#!/usr/bin/env python3
"""Render a validated demo spec into a self-contained Golden Runtime HTML app."""

from __future__ import annotations

import argparse
import copy
import html as html_lib
import json
import math
import re
import sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse


REQUIRED_SECTIONS = [
    "meta",
    "design",
    "story",
    "navigation",
    "dashboard",
    "operations",
    "simulator",
    "improvement",
    "finance",
    "github",
    "foundry",
    "appPlatform",
    "notification",
]

ROUTE_IDS = [
    "dashboard",
    "operations",
    "simulator",
    "improvement",
    "finance",
    "github",
    "foundry",
    "appPlatform",
]

FIXED_DESIGN = {
    "archetype": "trusted-executive",
    "theme": "dark-dimmed",
    "density": "executive",
    "motion": "balanced",
    "visualMetaphor": "connected operating signals",
    "counterInfluence": "editorial clarity",
}
FIXED_CONCEPT_WORDS = ["clarity", "confidence", "continuity"]
FIXED_AVOID_PATTERNS = [
    "generic red-blue gradient",
    "oversized glass cards",
    "decorative 3D icons",
]
SEMANTIC_COLORS = {
    "brand",
    "accent",
    "info",
    "success",
    "warning",
    "danger",
    "violet",
}
STATUS_TONES = {"success", "warning", "danger", "info", "violet", "ok", "warn", "bad"}
SAFE_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
RUNTIME_ASSET_NAMES = ("shell.tmpl", "runtime.css", "runtime.js")
LANGUAGE_TAG_PATTERN = re.compile(
    r"^(?:"
    r"[A-Za-z]{2,3}(?:-[A-Za-z]{4})?(?:-(?:[A-Za-z]{2}|[0-9]{3}))?"
    r"|[A-Za-z]{4}"
    r"|[A-Za-z]{5,8}"
    r")(?:-(?:[A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*$"
)
ISO_TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)

UNSAFE_PATTERNS = [
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"\bon[a-z0-9_-]+\s*=", re.IGNORECASE),
]

RICH_TEXT_TAGS = {"b", "strong", "em", "code", "br", "div", "span"}
RICH_TEXT_CLASSES = {
    "message-stats",
    "message-stat-label",
    "message-stat-value",
}


def canonical_http_url(value: str) -> str | None:
    try:
        parsed = urlparse(value)
        port = parsed.port
    except ValueError:
        return None
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        return None
    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower()
    rendered_hostname = f"[{hostname}]" if ":" in hostname else hostname
    default_port = (scheme == "http" and port == 80) or (
        scheme == "https" and port == 443
    )
    netloc = (
        rendered_hostname
        if port is None or default_port
        else f"{rendered_hostname}:{port}"
    )
    return urlunparse(
        (scheme, netloc, parsed.path or "/", "", parsed.query, "")
    )


class SpecError(ValueError):
    """Raised when a demo spec violates the Golden Runtime contract."""


class RichTextSanitizer(HTMLParser):
    """Strictly allow the small rich-text subset used by the runtime."""

    def __init__(self, path: str):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.parts: list[str] = []
        self.stack: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        tag = tag.lower()
        if tag not in RICH_TEXT_TAGS:
            raise SpecError(f"{self.path} uses disallowed rich-text tag <{tag}>")
        rendered_attrs = ""
        if attrs:
            if tag not in {"div", "span"} or len(attrs) != 1 or attrs[0][0].lower() != "class":
                raise SpecError(f"{self.path} uses disallowed attribute on <{tag}>")
            classes = (attrs[0][1] or "").split()
            if not classes or any(value not in RICH_TEXT_CLASSES for value in classes):
                raise SpecError(f"{self.path} uses a disallowed rich-text class")
            rendered_attrs = f' class="{html_lib.escape(" ".join(classes), quote=True)}"'
        if tag == "br":
            self.parts.append("<br>")
            return
        self.parts.append(f"<{tag}{rendered_attrs}>")
        self.stack.append(tag)

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() != "br" or attrs:
            raise SpecError(f"{self.path} uses a disallowed self-closing tag")
        self.parts.append("<br>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "br" or not self.stack or self.stack[-1] != tag:
            raise SpecError(f"{self.path} contains malformed rich-text markup")
        self.stack.pop()
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(html_lib.escape(data, quote=False))

    def handle_comment(self, data: str) -> None:
        raise SpecError(f"{self.path} must not contain HTML comments")

    def handle_decl(self, decl: str) -> None:
        raise SpecError(f"{self.path} must not contain HTML declarations")

    def unknown_decl(self, data: str) -> None:
        raise SpecError(f"{self.path} contains unsupported markup")

    def result(self) -> str:
        if self.stack:
            raise SpecError(f"{self.path} contains unclosed rich-text markup")
        return "".join(self.parts)


def sanitize_rich_text(value: str, path: str) -> str:
    sanitizer = RichTextSanitizer(path)
    try:
        sanitizer.feed(value)
        sanitizer.close()
    except SpecError:
        raise
    except Exception as error:
        raise SpecError(f"{path} contains invalid rich text: {error}") from error
    return sanitizer.result()


def sanitize_rich_fields(spec: dict[str, Any]) -> dict[str, Any]:
    sanitized = copy.deepcopy(spec)

    def clean(container: Any, key: str, path: str) -> None:
        if isinstance(container, dict) and isinstance(container.get(key), str):
            container[key] = sanitize_rich_text(container[key], path)

    operations = sanitized.get("operations")
    action = operations.get("action") if isinstance(operations, dict) else None
    clean(action, "recommendationBefore", "$.operations.action.recommendationBefore")
    clean(action, "recommendationAfter", "$.operations.action.recommendationAfter")

    simulator = sanitized.get("simulator")
    if isinstance(simulator, dict):
        for index, rule in enumerate(simulator.get("recommendations") or []):
            clean(rule, "message", f"$.simulator.recommendations[{index}].message")
        clean(simulator, "defaultRecommendation", "$.simulator.defaultRecommendation")

    improvement = sanitized.get("improvement")
    action = improvement.get("action") if isinstance(improvement, dict) else None
    clean(action, "summaryBefore", "$.improvement.action.summaryBefore")
    clean(action, "summaryAfter", "$.improvement.action.summaryAfter")

    finance = sanitized.get("finance")
    clean(finance, "explanation", "$.finance.explanation")

    foundry = sanitized.get("foundry")
    if isinstance(foundry, dict):
        clean(foundry, "fallback", "$.foundry.fallback")
        for profile_index, profile in enumerate(foundry.get("profiles") or []):
            clean(profile, "intro", f"$.foundry.profiles[{profile_index}].intro")
            if isinstance(profile, dict):
                for qa_index, item in enumerate(profile.get("qa") or []):
                    clean(
                        item,
                        "answer",
                        f"$.foundry.profiles[{profile_index}].qa[{qa_index}].answer",
                    )
        orchestration = foundry.get("orchestration")
        clean(orchestration, "intro", "$.foundry.orchestration.intro")
        clean(orchestration, "summary", "$.foundry.orchestration.summary")

    return sanitized


def parse_args() -> argparse.Namespace:
    skill_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Compile a demo-spec JSON file into one self-contained HTML app."
    )
    parser.add_argument("--spec", type=Path, required=True, help="Customer demo spec JSON.")
    parser.add_argument("--output", type=Path, help="Output .html path.")
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=skill_root / "runtime",
        help="Directory containing shell.tmpl, runtime.css, and runtime.js.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the spec without writing HTML.",
    )
    return parser.parse_args()


def require_mapping(parent: dict[str, Any], key: str, path: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise SpecError(f"{path}.{key} must be an object")
    return value


def require_list(
    parent: dict[str, Any],
    key: str,
    path: str,
    *,
    minimum: int = 1,
) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list) or len(value) < minimum:
        raise SpecError(f"{path}.{key} must be an array with at least {minimum} item(s)")
    return value


def require_string(parent: dict[str, Any], key: str, path: str) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SpecError(f"{path}.{key} must be a non-empty string")
    return value


def require_number(parent: dict[str, Any], key: str, path: str) -> float:
    value = parent.get(key)
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
    ):
        raise SpecError(f"{path}.{key} must be a finite number")
    return float(value)


def optional_integer(
    parent: dict[str, Any],
    key: str,
    path: str,
    *,
    minimum: int = 0,
    maximum: int = 10,
) -> int | None:
    value = parent.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise SpecError(f"{path}.{key} must be an integer between {minimum} and {maximum}")
    return value


def require_boolean(parent: dict[str, Any], key: str, path: str) -> bool:
    value = parent.get(key)
    if not isinstance(value, bool):
        raise SpecError(f"{path}.{key} must be a boolean")
    return value


def require_string_list(
    parent: dict[str, Any],
    key: str,
    path: str,
    *,
    minimum: int = 1,
) -> list[str]:
    values = require_list(parent, key, path, minimum=minimum)
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise SpecError(f"{path}.{key} must contain non-empty strings")
    return values


def validate_hero(section: dict[str, Any], path: str) -> None:
    hero = require_mapping(section, "hero", path)
    if "actionHtml" in hero:
        raise SpecError(f"{path}.hero.actionHtml is runtime-owned and must not be supplied")
    require_string(hero, "title", f"{path}.hero")
    require_string(hero, "subtitle", f"{path}.hero")
    require_string(hero, "icon", f"{path}.hero")
    badge = hero.get("badge")
    if badge is not None:
        if not isinstance(badge, dict):
            raise SpecError(f"{path}.hero.badge must be an object")
        require_string(badge, "label", f"{path}.hero.badge")
        validate_tone(require_string(badge, "tone", f"{path}.hero.badge"), f"{path}.hero.badge.tone")


def validate_semantic_color(value: str, path: str) -> None:
    if value not in SEMANTIC_COLORS:
        raise SpecError(f"{path} must be one of: {', '.join(sorted(SEMANTIC_COLORS))}")


def validate_tone(value: str, path: str) -> None:
    if value not in STATUS_TONES:
        raise SpecError(f"{path} must be a supported status tone")


def validate_safe_id(value: str, path: str) -> None:
    if not SAFE_ID_PATTERN.fullmatch(value):
        raise SpecError(f"{path} must start with a letter and contain only letters, digits, '_' or '-'")


def validate_kpis(section: dict[str, Any], path: str) -> None:
    kpis = require_list(section, "kpis", path, minimum=4)
    if len(kpis) != 4:
        raise SpecError(f"{path}.kpis must contain exactly 4 KPI items")
    for index, item in enumerate(kpis):
        if not isinstance(item, dict):
            raise SpecError(f"{path}.kpis[{index}] must be an object")
        item_path = f"{path}.kpis[{index}]"
        require_string(item, "label", item_path)
        require_string(item, "icon", item_path)
        require_number(item, "value", item_path)
        require_string(item, "delta", item_path)
        direction = require_string(item, "direction", item_path)
        if direction not in {"up", "down", "warning"}:
            raise SpecError(f"{item_path}.direction must be 'up', 'down', or 'warning'")
        color = require_string(item, "color", item_path)
        validate_semantic_color(color, f"{item_path}.color")
        optional_integer(item, "decimals", item_path, maximum=6)
        series = require_list(item, "series", item_path, minimum=2)
        if not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            for value in series
        ):
            raise SpecError(f"{item_path}.series must contain only finite numbers")
        tick = item.get("tick")
        if tick is not None:
            if not isinstance(tick, dict):
                raise SpecError(f"{item_path}.tick must be an object")
            require_number(tick, "min", f"{item_path}.tick")
            require_number(tick, "max", f"{item_path}.tick")
            if tick["min"] > tick["max"]:
                raise SpecError(f"{item_path}.tick.min must not exceed max")
            floor = tick.get("floor")
            ceiling = tick.get("ceiling")
            if floor is not None:
                require_number(tick, "floor", f"{item_path}.tick")
            if ceiling is not None:
                require_number(tick, "ceiling", f"{item_path}.tick")
            if floor is not None and ceiling is not None and floor > ceiling:
                raise SpecError(f"{item_path}.tick.floor must not exceed ceiling")


def validate_table(table: dict[str, Any], path: str, *, minimum_rows: int = 3) -> None:
    require_string(table, "title", path)
    require_string(table, "hint", path)
    headers = require_list(table, "headers", path, minimum=2)
    rows = require_list(table, "rows", path, minimum=minimum_rows)
    if not all(isinstance(header, str) and header for header in headers):
        raise SpecError(f"{path}.headers must contain non-empty strings")
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise SpecError(f"{path}.rows[{index}] must be an object")
        cells = require_list(row, "cells", f"{path}.rows[{index}]", minimum=1)
        if not all(
            isinstance(cell, (str, int, float))
            and not isinstance(cell, bool)
            and (not isinstance(cell, float) or math.isfinite(cell))
            for cell in cells
        ):
            raise SpecError(f"{path}.rows[{index}].cells contains unsupported values")
        require_string(row, "detail", f"{path}.rows[{index}]")
        status = row.get("status")
        if status is not None:
            if not isinstance(status, dict):
                raise SpecError(f"{path}.rows[{index}].status must be an object")
            require_string(status, "label", f"{path}.rows[{index}].status")
            tone = require_string(status, "tone", f"{path}.rows[{index}].status")
            validate_tone(tone, f"{path}.rows[{index}].status.tone")
        expected_cells = len(headers) - (1 if status is not None else 0)
        if len(cells) != expected_cells:
            raise SpecError(
                f"{path}.rows[{index}].cells must contain exactly {expected_cells} value(s) "
                "to match the table headers"
            )


def validate_named_items(
    items: list[Any],
    path: str,
    required_strings: list[str],
    required_numbers: list[str] | None = None,
) -> None:
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise SpecError(f"{path}[{index}] must be an object")
        item_path = f"{path}[{index}]"
        for key in required_strings:
            require_string(item, key, item_path)
        for key in required_numbers or []:
            require_number(item, key, item_path)


def validate_buyer_next_step(value: Any, path: str) -> None:
    if not isinstance(value, dict):
        raise SpecError(f"{path} must be an object")
    for key in ["action", "owner", "timebox", "successCriteria"]:
        require_string(value, key, path)


def validate_sales_contract(
    section: dict[str, Any],
    path: str,
    *,
    required_services: tuple[str, ...],
) -> None:
    sales = require_mapping(section, "sales", path)
    require_string(sales, "executiveQuestion", f"{path}.sales")
    require_string(sales, "enabledBusinessOutcome", f"{path}.sales")
    business_kpis = require_list(sales, "businessKpis", f"{path}.sales", minimum=2)
    if len(business_kpis) != 2:
        raise SpecError(f"{path}.sales.businessKpis must contain exactly 2 items")
    validate_named_items(
        business_kpis,
        f"{path}.sales.businessKpis",
        ["label", "value", "detail"],
    )
    capabilities = require_list(
        sales,
        "differentiatedCapabilities",
        f"{path}.sales",
        minimum=3,
    )
    validate_named_items(
        capabilities,
        f"{path}.sales.differentiatedCapabilities",
        ["title", "detail"],
    )
    controls = require_list(sales, "controlEvidence", f"{path}.sales", minimum=3)
    services: list[str] = []
    for index, control in enumerate(controls):
        control_path = f"{path}.sales.controlEvidence[{index}]"
        if not isinstance(control, dict):
            raise SpecError(f"{control_path} must be an object")
        services.append(require_string(control, "service", control_path))
        require_string(control, "control", control_path)
        require_string(control, "evidence", control_path)
        status = require_mapping(control, "status", control_path)
        require_string(status, "label", f"{control_path}.status")
        validate_tone(
            require_string(status, "tone", f"{control_path}.status"),
            f"{control_path}.status.tone",
        )
    service_text = " ".join(services).casefold()
    missing_services = [
        service for service in required_services if service.casefold() not in service_text
    ]
    if missing_services:
        raise SpecError(
            f"{path}.sales.controlEvidence must include: "
            + ", ".join(missing_services)
        )
    validate_buyer_next_step(
        require_mapping(sales, "buyerNextStep", f"{path}.sales"),
        f"{path}.sales.buyerNextStep",
    )


def validate_guided_journeys(story: dict[str, Any]) -> None:
    journeys = require_list(story, "guidedJourneys", "$.story", minimum=2)
    journey_ids: list[str] = []
    for index, journey in enumerate(journeys):
        journey_path = f"$.story.guidedJourneys[{index}]"
        if not isinstance(journey, dict):
            raise SpecError(f"{journey_path} must be an object")
        journey_id = require_string(journey, "id", journey_path)
        validate_safe_id(journey_id, f"{journey_path}.id")
        journey_ids.append(journey_id)
        for key in ["label", "audience"]:
            require_string(journey, key, journey_path)
        routes = require_list(journey, "routes", journey_path, minimum=4)
        if len(routes) > 6 or len(routes) != len(set(routes)):
            raise SpecError(
                f"{journey_path}.routes must contain 4-6 unique route IDs"
            )
        if routes[0] != "dashboard" or not all(route in ROUTE_IDS for route in routes):
            raise SpecError(
                f"{journey_path}.routes must start with dashboard and use fixed route IDs"
            )
        bridges = require_string_list(journey, "bridges", journey_path, minimum=3)
        if len(bridges) != len(routes) - 1:
            raise SpecError(
                f"{journey_path}.bridges must contain one bridge per route transition"
            )
        validate_buyer_next_step(
            require_mapping(journey, "finalAction", journey_path),
            f"{journey_path}.finalAction",
        )
    if len(journey_ids) != len(set(journey_ids)):
        raise SpecError("$.story.guidedJourneys IDs must be unique")
    default_journey_id = require_string(story, "defaultJourneyId", "$.story")
    if default_journey_id not in journey_ids:
        raise SpecError("$.story.defaultJourneyId must reference a guided journey")


def validate_scenario_trace(story: dict[str, Any]) -> None:
    scenario = require_mapping(story, "scenarioTrace", "$.story")
    for key in ["id", "title"]:
        require_string(scenario, key, "$.story.scenarioTrace")
    steps = require_list(scenario, "steps", "$.story.scenarioTrace", minimum=4)
    if len(steps) != 4:
        raise SpecError("$.story.scenarioTrace.steps must contain exactly 4 items")
    routes: list[str] = []
    for index, step in enumerate(steps):
        step_path = f"$.story.scenarioTrace.steps[{index}]"
        if not isinstance(step, dict):
            raise SpecError(f"{step_path} must be an object")
        routes.append(require_string(step, "route", step_path))
        for key in ["label", "owner", "timestamp"]:
            require_string(step, key, step_path)
        status = require_mapping(step, "status", step_path)
        require_string(status, "label", f"{step_path}.status")
        validate_tone(
            require_string(status, "tone", f"{step_path}.status"),
            f"{step_path}.status.tone",
        )
    if routes[0] not in ROUTE_IDS[:5] or routes[1:] != ["foundry", "github", "appPlatform"]:
        raise SpecError(
            "$.story.scenarioTrace must connect one business route to "
            "foundry, github, and appPlatform in that order"
        )


def iter_strings(value: Any, path: str = "$"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from iter_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_strings(child, f"{path}[{index}]")


def validate_spec(spec: dict[str, Any]) -> None:
    missing = [section for section in REQUIRED_SECTIONS if section not in spec]
    if missing:
        raise SpecError(f"Missing required top-level section(s): {', '.join(missing)}")

    meta = require_mapping(spec, "meta", "$")
    for key in [
        "customer",
        "industry",
        "audience",
        "appName",
        "initials",
        "language",
        "infrastructureLabel",
        "demoNote",
    ]:
        require_string(meta, key, "$.meta")
    if len(meta["initials"]) > 4:
        raise SpecError("$.meta.initials must be 1-4 characters")
    if not LANGUAGE_TAG_PATTERN.fullmatch(meta["language"]):
        raise SpecError("$.meta.language must be a supported BCP 47 language tag")
    research = require_mapping(meta, "research", "$.meta")
    checked_at = require_string(research, "checkedAt", "$.meta.research")
    if not ISO_TIMESTAMP_PATTERN.fullmatch(checked_at):
        raise SpecError(
            "$.meta.research.checkedAt must be a timezone-aware ISO 8601 timestamp"
        )
    try:
        parsed_checked_at = datetime.fromisoformat(
            checked_at.replace("Z", "+00:00")
        )
    except ValueError as error:
        raise SpecError(
            "$.meta.research.checkedAt must be a timezone-aware ISO 8601 timestamp"
        ) from error
    if parsed_checked_at.tzinfo is None:
        raise SpecError("$.meta.research.checkedAt must include a timezone")
    if "ledgerIds" in research:
        ledger_ids = require_list(
            research, "ledgerIds", "$.meta.research", minimum=1
        )
        if not all(
            isinstance(ledger_id, str) and ledger_id
            for ledger_id in ledger_ids
        ):
            raise SpecError(
                "$.meta.research.ledgerIds must contain non-empty strings"
            )
    sources = require_list(research, "sources", "$.meta.research", minimum=2)
    canonical_sources: set[str] = set()
    for index, source in enumerate(sources):
        source_path = f"$.meta.research.sources[{index}]"
        if not isinstance(source, dict):
            raise SpecError(f"{source_path} must be an object")
        url = require_string(source, "url", source_path)
        canonical_url = canonical_http_url(url)
        if canonical_url is None:
            raise SpecError(f"{source_path}.url must be an HTTP(S) URL")
        canonical_sources.add(canonical_url)
        for optional in ("title", "publisher"):
            if optional in source:
                require_string(source, optional, source_path)
        if "ledgerIds" in source:
            ledger_ids = require_list(source, "ledgerIds", source_path, minimum=1)
            if not all(
                isinstance(ledger_id, str) and ledger_id
                for ledger_id in ledger_ids
            ):
                raise SpecError(
                    f"{source_path}.ledgerIds must contain non-empty strings"
                )
    if len(canonical_sources) < 2:
        raise SpecError(
            "$.meta.research.sources must contain at least two unique "
            "canonical HTTP(S) URLs"
        )

    design = require_mapping(spec, "design", "$")
    for key, expected in FIXED_DESIGN.items():
        actual = require_string(design, key, "$.design")
        if actual != expected:
            raise SpecError(
                f"$.design.{key} must be '{expected}'; the Golden Runtime design is fixed"
            )
    concept_words = require_list(design, "conceptWords", "$.design", minimum=3)
    if concept_words != FIXED_CONCEPT_WORDS:
        raise SpecError("$.design.conceptWords must match the fixed Golden Runtime marker")
    tokens = require_mapping(design, "tokens", "$.design")
    if tokens:
        raise SpecError(
            "$.design.tokens must be empty; runtime/runtime.css is the only visual-token source"
        )
    avoid = require_list(design, "avoid", "$.design", minimum=3)
    if avoid != FIXED_AVOID_PATTERNS:
        raise SpecError("$.design.avoid must match the fixed Golden Runtime marker")

    story = require_mapping(spec, "story", "$")
    require_string(story, "frame", "$.story")
    require_string(story, "climax", "$.story")
    audience_messages = require_list(story, "audienceMessages", "$.story", minimum=2)
    validate_named_items(
        audience_messages,
        "$.story.audienceMessages",
        ["audience", "message"],
    )
    validate_guided_journeys(story)
    validate_scenario_trace(story)
    route_scope = story.get("routeScope", ROUTE_IDS)
    if "routeScope" in story:
        route_scope = require_list(story, "routeScope", "$.story", minimum=8)
    if route_scope != ROUTE_IDS:
        raise SpecError(
            "$.story.routeScope must contain all 8 route IDs in canonical order"
        )

    navigation = require_list(spec, "navigation", "$", minimum=8)
    nav_ids = [item.get("id") if isinstance(item, dict) else None for item in navigation]
    if nav_ids != ROUTE_IDS:
        raise SpecError(
            "$.navigation IDs must match the fixed route order: "
            + ", ".join(ROUTE_IDS)
        )
    for index, route in enumerate(navigation):
        route_path = f"$.navigation[{index}]"
        require_string(route, "name", route_path)
        require_string(route, "short", route_path)
        require_string(route, "icon", route_path)

    dashboard = require_mapping(spec, "dashboard", "$")
    validate_hero(dashboard, "$.dashboard")
    validate_kpis(dashboard, "$.dashboard")
    primary_action = require_mapping(dashboard, "primaryAction", "$.dashboard")
    for key in ["label", "targetRoute", "toastTitle", "toastText", "icon"]:
        require_string(primary_action, key, "$.dashboard.primaryAction")
    if (
        primary_action["targetRoute"] not in ROUTE_IDS
        or primary_action["targetRoute"] == "dashboard"
    ):
        raise SpecError(
            "$.dashboard.primaryAction.targetRoute must reference another fixed route"
        )
    stream = require_mapping(dashboard, "stream", "$.dashboard")
    for key in ["title", "label", "color"]:
        require_string(stream, key, "$.dashboard.stream")
    validate_semantic_color(stream["color"], "$.dashboard.stream.color")
    stream_values = require_list(stream, "values", "$.dashboard.stream", minimum=2)
    if not all(
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        for value in stream_values
    ):
        raise SpecError("$.dashboard.stream.values must contain finite numbers")
    for key in ["min", "max"]:
        require_number(stream, key, "$.dashboard.stream")
    if stream["min"] >= stream["max"]:
        raise SpecError("$.dashboard.stream.min must be lower than max")
    stream_tick = require_mapping(stream, "tick", "$.dashboard.stream")
    require_number(stream_tick, "min", "$.dashboard.stream.tick")
    require_number(stream_tick, "max", "$.dashboard.stream.tick")
    if stream_tick["min"] > stream_tick["max"]:
        raise SpecError("$.dashboard.stream.tick.min must not exceed max")
    require_string(dashboard, "feedTitle", "$.dashboard")
    require_string(dashboard, "feedHint", "$.dashboard")
    feed = require_list(dashboard, "feed", "$.dashboard", minimum=4)
    validate_named_items(
        feed,
        "$.dashboard.feed",
        ["icon", "title", "text"],
    )
    cards = require_mapping(dashboard, "cards", "$.dashboard")
    require_string(cards, "title", "$.dashboard.cards")
    require_string(cards, "hint", "$.dashboard.cards")
    card_items = require_list(cards, "items", "$.dashboard.cards", minimum=3)
    validate_named_items(
        card_items,
        "$.dashboard.cards.items",
        ["name", "value", "sub", "detail"],
    )
    validate_table(
        require_mapping(dashboard, "table", "$.dashboard"),
        "$.dashboard.table",
    )
    learning_loop = require_mapping(dashboard, "learningLoop", "$.dashboard")
    for key in ["label", "unit", "note"]:
        require_string(learning_loop, key, "$.dashboard.learningLoop")
    require_number(learning_loop, "value", "$.dashboard.learningLoop")

    operations = require_mapping(spec, "operations", "$")
    validate_hero(operations, "$.operations")
    validate_kpis(operations, "$.operations")
    flow = require_mapping(operations, "flow", "$.operations")
    for key in ["title", "hint", "moverLabel"]:
        require_string(flow, key, "$.operations.flow")
    nodes = require_list(flow, "nodes", "$.operations.flow", minimum=4)
    if len(nodes) > 7:
        raise SpecError("$.operations.flow.nodes supports at most 7 nodes")
    validate_named_items(
        nodes,
        "$.operations.flow.nodes",
        ["name", "subtitle", "metric", "status", "detail"],
    )
    require_string_list(
        flow,
        "events",
        "$.operations.flow",
        minimum=len(nodes),
    )
    action = require_mapping(operations, "action", "$.operations")
    for key in [
        "button",
        "running",
        "complete",
        "runningEvent",
        "completeEvent",
        "recommendationLabel",
        "recommendationBefore",
        "recommendationAfter",
        "toastTitle",
        "toastText",
        "toastIcon",
    ]:
        require_string(action, key, "$.operations.action")
    require_number(action, "durationMs", "$.operations.action")
    if not 0 < action["durationMs"] <= 15000:
        raise SpecError("$.operations.action.durationMs must be between 0 and 15000")
    kpi_updates = require_mapping(action, "kpiUpdates", "$.operations.action")
    for key, value in kpi_updates.items():
        if (
            not str(key).isdigit()
            or not 0 <= int(key) < len(operations["kpis"])
            or not isinstance(value, (int, float))
            or isinstance(value, bool)
            or not math.isfinite(value)
        ):
            raise SpecError(
                "$.operations.action.kpiUpdates must map valid KPI indexes to finite numbers"
            )
    validate_table(
        require_mapping(operations, "table", "$.operations"),
        "$.operations.table",
    )

    simulator = require_mapping(spec, "simulator", "$")
    validate_hero(simulator, "$.simulator")
    require_string(simulator, "inputsTitle", "$.simulator")
    require_string(simulator, "inputsHint", "$.simulator")
    inputs = require_list(simulator, "inputs", "$.simulator", minimum=2)
    input_ids = []
    for index, item in enumerate(inputs):
        item_path = f"$.simulator.inputs[{index}]"
        input_id = require_string(item, "id", item_path)
        validate_safe_id(input_id, f"{item_path}.id")
        input_ids.append(input_id)
        require_string(item, "label", item_path)
        if not isinstance(item.get("unit"), str):
            raise SpecError(f"{item_path}.unit must be a string")
        for key in ["min", "max", "step", "value", "optimum", "weight"]:
            require_number(item, key, item_path)
        if item["min"] >= item["max"]:
            raise SpecError(f"{item_path}.min must be lower than max")
        if item["step"] <= 0:
            raise SpecError(f"{item_path}.step must be greater than zero")
        if not item["min"] <= item["value"] <= item["max"]:
            raise SpecError(f"{item_path}.value must be within min and max")
        if not item["min"] <= item["optimum"] <= item["max"]:
            raise SpecError(f"{item_path}.optimum must be within min and max")
        if item["weight"] < 0:
            raise SpecError(f"{item_path}.weight must not be negative")
        optional_integer(item, "decimals", item_path, maximum=6)
    if len(input_ids) != len(set(input_ids)):
        raise SpecError("$.simulator.inputs IDs must be unique")
    output = require_mapping(simulator, "output", "$.simulator")
    for key in [
        "label",
        "unit",
        "goodLabel",
        "warningLabel",
        "dangerLabel",
    ]:
        require_string(output, key, "$.simulator.output")
    for key in ["base", "min", "max", "goodThreshold", "warningThreshold"]:
        require_number(output, key, "$.simulator.output")
    optional_integer(output, "decimals", "$.simulator.output", maximum=6)
    if output["min"] >= output["max"]:
        raise SpecError("$.simulator.output.min must be lower than max")
    for key in ["base", "goodThreshold", "warningThreshold"]:
        if not output["min"] <= output[key] <= output["max"]:
            raise SpecError(f"$.simulator.output.{key} must be within min and max")
    if output["goodThreshold"] <= output["warningThreshold"]:
        raise SpecError(
            "$.simulator.output.goodThreshold must be greater than warningThreshold"
        )
    secondary = require_list(simulator, "secondary", "$.simulator", minimum=3)
    for index, metric in enumerate(secondary):
        metric_path = f"$.simulator.secondary[{index}]"
        if not isinstance(metric, dict):
            raise SpecError(f"{metric_path} must be an object")
        require_string(metric, "label", metric_path)
        if not isinstance(metric.get("unit"), str):
            raise SpecError(f"{metric_path}.unit must be a string")
        require_number(metric, "base", metric_path)
        optional_integer(metric, "decimals", metric_path, maximum=6)
        weights = require_mapping(metric, "weights", metric_path)
        if set(weights) != set(input_ids):
            raise SpecError(
                f"{metric_path}.weights must contain exactly the simulator input IDs"
            )
        for input_id, weight in weights.items():
            if input_id not in input_ids:
                raise SpecError(f"{metric_path}.weights references unknown input {input_id}")
            if (
                not isinstance(weight, (int, float))
                or isinstance(weight, bool)
                or not math.isfinite(weight)
            ):
                raise SpecError(f"{metric_path}.weights must contain finite numbers")
    recommendations = require_list(
        simulator,
        "recommendations",
        "$.simulator",
        minimum=1,
    )
    for index, rule in enumerate(recommendations):
        rule_path = f"$.simulator.recommendations[{index}]"
        if not isinstance(rule, dict):
            raise SpecError(f"{rule_path} must be an object")
        input_id = require_string(rule, "inputId", rule_path)
        if input_id not in input_ids:
            raise SpecError(f"{rule_path}.inputId references unknown input")
        operator = require_string(rule, "operator", rule_path)
        if operator not in {">", "<", "abs>", "default"}:
            raise SpecError(f"{rule_path}.operator is unsupported")
        require_number(rule, "threshold", rule_path)
        require_string(rule, "message", rule_path)
    default_indexes = [
        index for index, rule in enumerate(recommendations) if rule.get("operator") == "default"
    ]
    if default_indexes != [len(recommendations) - 1]:
        raise SpecError(
            "$.simulator.recommendations must contain exactly one default rule, as the last item"
        )
    require_string(simulator, "defaultRecommendation", "$.simulator")
    histogram = require_mapping(simulator, "histogram", "$.simulator")
    for key in ["title", "hint", "leftLabel", "centerLabel", "rightLabel"]:
        require_string(histogram, key, "$.simulator.histogram")
    validate_table(
        require_mapping(simulator, "history", "$.simulator"),
        "$.simulator.history",
    )

    improvement = require_mapping(spec, "improvement", "$")
    validate_hero(improvement, "$.improvement")
    validate_kpis(improvement, "$.improvement")
    for key in [
        "stepsTitle",
        "stepsHint",
        "factorsTitle",
        "factorsHint",
        "impactsTitle",
        "impactsHint",
    ]:
        require_string(improvement, key, "$.improvement")
    steps_data = require_list(improvement, "steps", "$.improvement", minimum=5)
    validate_named_items(steps_data, "$.improvement.steps", ["title", "text"])
    factors = require_list(improvement, "factors", "$.improvement", minimum=4)
    validate_named_items(
        factors,
        "$.improvement.factors",
        ["label", "value", "color"],
        ["width"],
    )
    for index, factor in enumerate(factors):
        validate_semantic_color(
            factor["color"],
            f"$.improvement.factors[{index}].color",
        )
        if not 0 <= factor["width"] <= 100:
            raise SpecError(f"$.improvement.factors[{index}].width must be between 0 and 100")
    impacts = require_list(improvement, "impacts", "$.improvement", minimum=4)
    validate_named_items(
        impacts,
        "$.improvement.impacts",
        ["label", "value", "sub", "detail"],
    )
    board = require_mapping(improvement, "board", "$.improvement")
    require_string(board, "title", "$.improvement.board")
    require_string(board, "hint", "$.improvement.board")
    columns = require_list(board, "columns", "$.improvement.board", minimum=3)
    if len(columns) != 3:
        raise SpecError("$.improvement.board.columns must contain exactly 3 columns")
    for index, column in enumerate(columns):
        column_path = f"$.improvement.board.columns[{index}]"
        if not isinstance(column, dict):
            raise SpecError(f"{column_path} must be an object")
        require_string(column, "name", column_path)
        items = require_list(column, "items", column_path, minimum=1)
        validate_named_items(
            items,
            f"{column_path}.items",
            ["text", "title", "detail"],
        )
    improvement_action = require_mapping(improvement, "action", "$.improvement")
    for key in [
        "button",
        "running",
        "complete",
        "summaryBefore",
        "summaryAfter",
        "toastTitle",
        "toastText",
        "toastIcon",
    ]:
        require_string(improvement_action, key, "$.improvement.action")
    require_number(improvement_action, "durationMs", "$.improvement.action")
    if not 0 < improvement_action["durationMs"] <= 15000:
        raise SpecError("$.improvement.action.durationMs must be between 0 and 15000")
    require_boolean(improvement_action, "autoRun", "$.improvement.action")

    finance = require_mapping(spec, "finance", "$")
    validate_hero(finance, "$.finance")
    require_string(finance, "leversTitle", "$.finance")
    require_string(finance, "leversHint", "$.finance")
    require_string(finance, "explanation", "$.finance")
    levers = require_list(finance, "levers", "$.finance", minimum=3)
    lever_ids = []
    for index, lever in enumerate(levers):
        lever_path = f"$.finance.levers[{index}]"
        if not isinstance(lever, dict):
            raise SpecError(f"{lever_path} must be an object")
        lever_id = require_string(lever, "id", lever_path)
        validate_safe_id(lever_id, f"{lever_path}.id")
        lever_ids.append(lever_id)
        require_string(lever, "label", lever_path)
        if not isinstance(lever.get("unit"), str):
            raise SpecError(f"{lever_path}.unit must be a string")
        for key in ["min", "max", "step", "value"]:
            require_number(lever, key, lever_path)
        if lever["min"] >= lever["max"]:
            raise SpecError(f"{lever_path}.min must be lower than max")
        if lever["step"] <= 0:
            raise SpecError(f"{lever_path}.step must be greater than zero")
        if not lever["min"] <= lever["value"] <= lever["max"]:
            raise SpecError(f"{lever_path}.value must be within min and max")
        optional_integer(lever, "decimals", lever_path, maximum=6)
    if len(lever_ids) != len(set(lever_ids)):
        raise SpecError("$.finance.levers IDs must be unique")
    margin = require_mapping(finance, "margin", "$.finance")
    for key in [
        "label",
        "unit",
        "note",
        "goodLabel",
        "warningLabel",
        "lowLabel",
    ]:
        require_string(margin, key, "$.finance.margin")
    for key in ["base", "goodThreshold", "warningThreshold"]:
        require_number(margin, key, "$.finance.margin")
    optional_integer(margin, "decimals", "$.finance.margin", maximum=6)
    if margin["goodThreshold"] <= margin["warningThreshold"]:
        raise SpecError("$.finance.margin.goodThreshold must be greater than warningThreshold")
    margin_impacts = require_mapping(margin, "impacts", "$.finance.margin")
    for lever_id, impact in margin_impacts.items():
        if (
            lever_id not in lever_ids
            or not isinstance(impact, (int, float))
            or isinstance(impact, bool)
            or not math.isfinite(impact)
        ):
            raise SpecError("$.finance.margin.impacts is invalid")
    summary_metrics = require_list(finance, "summaryMetrics", "$.finance", minimum=3)
    for index, metric in enumerate(summary_metrics):
        metric_path = f"$.finance.summaryMetrics[{index}]"
        if not isinstance(metric, dict):
            raise SpecError(f"{metric_path} must be an object")
        require_string(metric, "label", metric_path)
        if not isinstance(metric.get("unit"), str):
            raise SpecError(f"{metric_path}.unit must be a string")
        require_number(metric, "base", metric_path)
        optional_integer(metric, "decimals", metric_path, maximum=6)
        impacts = require_mapping(metric, "impacts", metric_path)
        for lever_id, impact in impacts.items():
            if (
                lever_id not in lever_ids
                or not isinstance(impact, (int, float))
                or isinstance(impact, bool)
                or not math.isfinite(impact)
            ):
                raise SpecError(f"{metric_path}.impacts is invalid")
    composition = require_mapping(finance, "composition", "$.finance")
    for key in ["title", "hint", "centerLabel"]:
        require_string(composition, key, "$.finance.composition")
    segments = require_list(composition, "segments", "$.finance.composition", minimum=4)
    if len(segments) != 4:
        raise SpecError("$.finance.composition.segments must contain exactly 4 items")
    for index, segment in enumerate(segments):
        segment_path = f"$.finance.composition.segments[{index}]"
        if not isinstance(segment, dict):
            raise SpecError(f"{segment_path} must be an object")
        require_string(segment, "label", segment_path)
        color = require_string(segment, "color", segment_path)
        validate_semantic_color(color, f"{segment_path}.color")
        require_number(segment, "base", segment_path)
        impacts = require_mapping(segment, "impacts", segment_path)
        for lever_id, impact in impacts.items():
            if (
                lever_id not in lever_ids
                or not isinstance(impact, (int, float))
                or isinstance(impact, bool)
                or not math.isfinite(impact)
            ):
                raise SpecError(f"{segment_path}.impacts is invalid")
    center_segment = composition.get("centerSegment", 1)
    if (
        isinstance(center_segment, bool)
        or not isinstance(center_segment, int)
        or not 0 <= center_segment < len(segments)
    ):
        raise SpecError("$.finance.composition.centerSegment must reference a segment index")
    validate_table(
        require_mapping(finance, "watchlist", "$.finance"),
        "$.finance.watchlist",
    )

    github = require_mapping(spec, "github", "$")
    validate_hero(github, "$.github")
    validate_kpis(github, "$.github")
    validate_sales_contract(
        github,
        "$.github",
        required_services=("GitHub AI Controls", "GitHub Advanced Security"),
    )
    for key in ["stepsTitle", "stepsHint", "issuesTitle", "issuesHint"]:
        require_string(github, key, "$.github")
    require_string_list(github, "issueHeaders", "$.github", minimum=5)
    github_steps = require_list(github, "steps", "$.github", minimum=5)
    validate_named_items(github_steps, "$.github.steps", ["title", "text"])
    issues = require_list(github, "issues", "$.github", minimum=3)
    issue_risk_modes: list[bool] = []
    for index, issue in enumerate(issues):
        issue_path = f"$.github.issues[{index}]"
        for key in ["id", "title", "product", "type", "risk", "context"]:
            require_string(issue, key, issue_path)
        issue_risk_modes.append(require_boolean(issue, "highRisk", issue_path))
        diff_lines = require_list(issue, "diffLines", issue_path, minimum=2)
        validate_named_items(diff_lines, f"{issue_path}.diffLines", ["type", "text"])
        status = require_mapping(issue, "status", issue_path)
        require_string(status, "label", f"{issue_path}.status")
        tone = require_string(status, "tone", f"{issue_path}.status")
        validate_tone(tone, f"{issue_path}.status.tone")
        for line_index, line in enumerate(diff_lines):
            if line["type"] not in {"add", "delete", "comment", "keyword"}:
                raise SpecError(
                    f"{issue_path}.diffLines[{line_index}].type is unsupported"
                )
    if not any(issue_risk_modes) or all(issue_risk_modes):
        raise SpecError(
            "$.github.issues must include at least one autonomous and one high-risk issue"
        )
    github_action = require_mapping(github, "action", "$.github")
    for key in [
        "button",
        "running",
        "complete",
        "readyLabel",
        "humanLedLabel",
        "notCreated",
        "humanRequired",
        "awaiting",
        "agentRunning",
        "policyChecks",
        "planReady",
        "prReady",
        "humanImplementation",
        "checksPassed",
        "humanResult",
        "prResult",
        "planStatus",
        "prStatus",
        "humanToastTitle",
        "humanToastText",
        "prToastTitle",
        "prToastText",
    ]:
        require_string(github_action, key, "$.github.action")
    require_number(github_action, "prBase", "$.github.action")
    require_number(github_action, "durationMs", "$.github.action")
    if not 0 < github_action["durationMs"] <= 15000:
        raise SpecError("$.github.action.durationMs must be between 0 and 15000")

    foundry = require_mapping(spec, "foundry", "$")
    validate_hero(foundry, "$.foundry")
    validate_kpis(foundry, "$.foundry")
    validate_sales_contract(
        foundry,
        "$.foundry",
        required_services=(
            "Microsoft Entra",
            "Microsoft Purview",
            "Azure AI Content Safety",
        ),
    )
    require_string(foundry, "decisionPreviewTitle", "$.foundry")
    for key in [
        "listTitle",
        "listHint",
        "governedLabel",
        "placeholder",
        "sendLabel",
        "fallback",
    ]:
        require_string(foundry, key, "$.foundry")
    profiles = require_list(foundry, "profiles", "$.foundry", minimum=5)
    if len(profiles) > 7:
        raise SpecError("$.foundry.profiles supports at most 7 agents")
    profile_names = []
    for index, profile in enumerate(profiles):
        profile_path = f"$.foundry.profiles[{index}]"
        profile_names.append(require_string(profile, "name", profile_path))
        require_string(profile, "icon", profile_path)
        require_string(profile, "subtitle", profile_path)
        require_string(profile, "intro", profile_path)
        qa = require_list(profile, "qa", profile_path, minimum=3)
        for qa_index, item in enumerate(qa):
            item_path = f"{profile_path}.qa[{qa_index}]"
            require_string(item, "question", item_path)
            require_string(item, "answer", item_path)
    if len(profile_names) != len(set(profile_names)):
        raise SpecError("$.foundry.profiles names must be unique")
    orchestration = require_mapping(foundry, "orchestration", "$.foundry")
    for key in [
        "title",
        "button",
        "running",
        "complete",
        "coreLabel",
        "intro",
        "summary",
        "toastTitle",
        "toastText",
    ]:
        require_string(orchestration, key, "$.foundry.orchestration")
    stages = require_list(orchestration, "stages", "$.foundry.orchestration", minimum=3)
    for index, stage in enumerate(stages):
        stage_path = f"$.foundry.orchestration.stages[{index}]"
        if not isinstance(stage, dict):
            raise SpecError(f"{stage_path} must be an object")
        agent_index = stage.get("agentIndex")
        if not isinstance(agent_index, int) or not 0 <= agent_index < len(profiles):
            raise SpecError(
                f"$.foundry.orchestration.stages[{index}].agentIndex is out of range"
            )
        for key in ["icon", "name", "text"]:
            require_string(stage, key, stage_path)

    app_platform = require_mapping(spec, "appPlatform", "$")
    validate_hero(app_platform, "$.appPlatform")
    validate_sales_contract(
        app_platform,
        "$.appPlatform",
        required_services=("Microsoft Entra", "Microsoft Defender"),
    )
    cards = require_list(app_platform, "cards", "$.appPlatform", minimum=3)
    if len(cards) != 3:
        raise SpecError("$.appPlatform.cards must contain exactly 3 items")
    validate_named_items(
        cards,
        "$.appPlatform.cards",
        ["icon", "title", "value", "sub", "detail"],
    )
    validate_table(
        require_mapping(app_platform, "controls", "$.appPlatform"),
        "$.appPlatform.controls",
        minimum_rows=5,
    )
    validate_table(
        require_mapping(app_platform, "memories", "$.appPlatform"),
        "$.appPlatform.memories",
    )
    platform_loop = require_mapping(app_platform, "learningLoop", "$.appPlatform")
    require_string(platform_loop, "title", "$.appPlatform.learningLoop")
    require_string(platform_loop, "hint", "$.appPlatform.learningLoop")
    platform_steps = require_list(
        platform_loop,
        "steps",
        "$.appPlatform.learningLoop",
        minimum=4,
    )
    if len(platform_steps) != 4:
        raise SpecError("$.appPlatform.learningLoop.steps must contain exactly 4 items")
    validate_named_items(
        platform_steps,
        "$.appPlatform.learningLoop.steps",
        ["icon", "title", "sub", "detail"],
    )
    evaluation = require_mapping(app_platform, "evaluation", "$.appPlatform")
    for key in [
        "title",
        "hint",
        "button",
        "running",
        "complete",
        "toastTitle",
        "toastText",
        "planButton",
        "planning",
        "planComplete",
        "projectedLabel",
        "planBlockedTitle",
        "planBlockedText",
        "planToastTitle",
        "planToastText",
    ]:
        require_string(evaluation, key, "$.appPlatform.evaluation")
    require_number(evaluation, "initialScore", "$.appPlatform.evaluation")
    require_number(evaluation, "finalScore", "$.appPlatform.evaluation")
    try:
        visible_initial_score = float(cards[0]["value"])
    except (TypeError, ValueError) as error:
        raise SpecError(
            "$.appPlatform.cards[0].value must be a numeric display string"
        ) from error
    if (
        not math.isfinite(visible_initial_score)
        or not math.isclose(
            visible_initial_score,
            float(evaluation["initialScore"]),
            rel_tol=0,
            abs_tol=1e-9,
        )
    ):
        raise SpecError(
            "$.appPlatform.cards[0].value must equal evaluation.initialScore"
        )
    if math.isclose(
        float(evaluation["initialScore"]),
        float(evaluation["finalScore"]),
        rel_tol=0,
        abs_tol=1e-9,
    ):
        raise SpecError(
            "$.appPlatform.evaluation.finalScore must differ from initialScore"
        )
    require_string_list(
        evaluation,
        "readyLines",
        "$.appPlatform.evaluation",
        minimum=3,
    )
    require_string_list(
        evaluation,
        "runLines",
        "$.appPlatform.evaluation",
        minimum=4,
    )
    require_string_list(
        evaluation,
        "remediationLines",
        "$.appPlatform.evaluation",
        minimum=4,
    )
    gaps = require_list(
        evaluation,
        "gaps",
        "$.appPlatform.evaluation",
        minimum=2,
    )
    unresolved_gaps = 0
    for index, gap in enumerate(gaps):
        gap_path = f"$.appPlatform.evaluation.gaps[{index}]"
        if not isinstance(gap, dict):
            raise SpecError(f"{gap_path} must be an object")
        for key in ["title", "detail", "owner", "effort"]:
            require_string(gap, key, gap_path)
        status = require_mapping(gap, "status", gap_path)
        require_string(status, "label", f"{gap_path}.status")
        tone = require_string(status, "tone", f"{gap_path}.status")
        validate_tone(tone, f"{gap_path}.status.tone")
        if tone in {"warning", "danger", "warn", "bad"}:
            unresolved_gaps += 1
    if unresolved_gaps < 1:
        raise SpecError(
            "$.appPlatform.evaluation.gaps must include at least one unresolved gap"
        )

    notification = require_mapping(spec, "notification", "$")
    for key in ["title", "text", "icon"]:
        require_string(notification, key, "$.notification")
    ambient = spec.get("ambientNotifications")
    if ambient is not None:
        if not isinstance(ambient, list):
            raise SpecError("$.ambientNotifications must be an array")
        validate_named_items(
            ambient,
            "$.ambientNotifications",
            ["title", "text", "icon"],
        )
    ambient_interval = spec.get("ambientIntervalMs")
    if ambient_interval is not None:
        require_number(spec, "ambientIntervalMs", "$")
        if ambient_interval <= 0:
            raise SpecError("$.ambientIntervalMs must be greater than zero")

    for path, value in iter_strings(spec):
        for pattern in UNSAFE_PATTERNS:
            if pattern.search(value):
                raise SpecError(f"Unsafe HTML/JavaScript pattern in {path}")


def read_text(path: Path) -> str:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    return resolved.read_text(encoding="utf-8")


def paths_collide(first: Path, second: Path) -> bool:
    first_resolved = first.expanduser().resolve()
    second_resolved = second.expanduser().resolve()
    if str(first_resolved).casefold() == str(second_resolved).casefold():
        return True
    try:
        return first_resolved.exists() and second_resolved.exists() and first_resolved.samefile(second_resolved)
    except OSError:
        return False


def runtime_input_paths(runtime_dir: Path) -> set[Path]:
    runtime = runtime_dir.expanduser().resolve()
    return {runtime / name for name in RUNTIME_ASSET_NAMES}


def safe_json_for_script(spec: dict[str, Any]) -> str:
    encoded = json.dumps(
        spec,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    )
    return (
        encoded.replace("</", "<\\/")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def render(spec: dict[str, Any], runtime_dir: Path) -> str:
    runtime = runtime_dir.expanduser().resolve()
    shell = read_text(runtime / "shell.tmpl")
    css = read_text(runtime / "runtime.css")
    javascript = read_text(runtime / "runtime.js")
    language = spec["meta"]["language"].casefold()
    is_korean = language == "ko" or language.startswith("ko-")
    canvas_match = re.search(r"--canvas:\s*(#[0-9a-fA-F]{6})\s*;", css)
    if canvas_match is None:
        raise RuntimeError("Runtime CSS must define --canvas as a six-digit hex color")
    replacements = {
        "{{LANG}}": html_lib.escape(spec["meta"]["language"], quote=True),
        "{{TITLE}}": html_lib.escape(
            (
                f'{spec["meta"]["appName"]} | 임원용 AI 운영 데모'
                if is_korean
                else f'{spec["meta"]["appName"]} | Executive AI Operations Demo'
            ),
            quote=False,
        ),
        "{{NAV_SECTION_LABEL}}": "통합 운영 현황" if is_korean else "Operations Intelligence",
        "{{EXECUTIVE_WORKSPACE_LABEL}}": "임원용 · 시연 환경" if is_korean else "Executive · Demo workspace",
        "{{DEMO_DATA_LABEL}}": "시연 데이터" if is_korean else "DEMO DATA",
        "{{NOTIFICATION_ARIA_LABEL}}": "시연 알림" if is_korean else "Demo notifications",
        "{{RUNTIME_CSS}}": css,
        "{{THEME_COLOR}}": canvas_match.group(1),
        "{{DEMO_SPEC_JSON}}": safe_json_for_script(spec),
        "{{RUNTIME_JS}}": javascript,
    }
    html = shell
    for placeholder, value in replacements.items():
        if placeholder not in html:
            raise RuntimeError(f"Runtime shell placeholder missing: {placeholder}")
        html = html.replace(placeholder, value)
    return html


def main() -> int:
    args = parse_args()
    spec_path = args.spec.expanduser().resolve()
    if not spec_path.is_file():
        raise FileNotFoundError(spec_path)
    def reject_constant(value: str):
        raise SpecError(f"Non-finite JSON number is not allowed: {value}")

    with spec_path.open(encoding="utf-8") as stream:
        spec = json.load(stream, parse_constant=reject_constant)
    if not isinstance(spec, dict):
        raise SpecError("Top-level JSON value must be an object")
    spec = sanitize_rich_fields(spec)
    validate_spec(spec)

    summary = {
        "spec": str(spec_path),
        "customer": spec["meta"]["customer"],
        "archetype": spec["design"]["archetype"],
        "routes": len(spec["story"].get("routeScope", spec["navigation"])),
        "dataRoutes": len(spec["navigation"]),
        "agents": len(spec["foundry"]["profiles"]),
        "valid": True,
    }

    if args.validate_only:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    if args.output is None:
        raise SpecError("--output is required unless --validate-only is used")
    output = args.output.expanduser().resolve()
    if paths_collide(output, spec_path):
        raise SpecError("--output must not overwrite the input spec")
    if any(paths_collide(output, path) for path in runtime_input_paths(args.runtime_dir)):
        raise SpecError("--output must not overwrite or alias a runtime asset")
    if output.suffix.lower() != ".html":
        raise SpecError("--output must use the .html extension")
    output.parent.mkdir(parents=True, exist_ok=True)
    html = render(spec, args.runtime_dir)
    output.write_text(html, encoding="utf-8")
    summary.update({"output": str(output), "bytes": output.stat().st_size})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, json.JSONDecodeError, SpecError, RuntimeError) as error:
        print(f"render_demo.py: {error}", file=sys.stderr)
        raise SystemExit(2)
