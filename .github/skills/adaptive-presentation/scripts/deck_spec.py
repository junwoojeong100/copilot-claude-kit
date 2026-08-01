#!/usr/bin/env python3
"""Validate the machine-readable contract for an adaptive presentation deck."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tooling import paths_collide

WEB_SEARCH_SCRIPTS = (
    Path(__file__).resolve().parents[2] / "web-search" / "scripts"
)
sys.path.insert(0, str(WEB_SEARCH_SCRIPTS))
import validate_fact_ledger as fact_ledger_validator  # noqa: E402


STATE_LABELS = {"GA", "PARTIAL GA", "PREVIEW", "ASSUMPTION", "DEMO DATA"}
LANGUAGE_PATTERN = re.compile(
    r"^(?:[A-Za-z]{2,3})(?:-[A-Za-z0-9]{2,8})*$"
)


class DeckSpecError(ValueError):
    """Raised when a deck specification is structurally or semantically invalid."""


def reject_unknown(
    value: dict[str, Any],
    allowed: set[str],
    path: str,
) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise DeckSpecError(
            f"{path} contains unsupported field(s): " + ", ".join(unknown)
        )


@dataclass(frozen=True)
class DeckSpecContext:
    path: Path
    spec: dict[str, Any]
    fact_ledger_path: Path | None
    fact_ledger: dict[str, Any] | None
    template_profile_path: Path | None
    template_profile: dict[str, Any] | None

    @property
    def required_source_slides(self) -> set[int]:
        return {
            int(slide["number"])
            for slide in self.spec["slides"]
            if slide["claimIds"]
        }

    @property
    def claim_ids_by_slide(self) -> dict[int, list[str]]:
        return {
            int(slide["number"]): list(slide["claimIds"])
            for slide in self.spec["slides"]
            if slide["claimIds"]
        }


def require_object(parent: dict[str, Any], key: str, path: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise DeckSpecError(f"{path}.{key} must be an object")
    return value


def require_string(parent: dict[str, Any], key: str, path: str) -> str:
    value = parent.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DeckSpecError(f"{path}.{key} must be a non-empty string")
    return value


def require_bool(parent: dict[str, Any], key: str, path: str) -> bool:
    value = parent.get(key)
    if not isinstance(value, bool):
        raise DeckSpecError(f"{path}.{key} must be a boolean")
    return value


def require_positive_number(parent: dict[str, Any], key: str, path: str) -> float:
    value = parent.get(key)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise DeckSpecError(f"{path}.{key} must be a finite positive number")
    return float(value)


def require_string_list(
    parent: dict[str, Any],
    key: str,
    path: str,
) -> list[str]:
    values = parent.get(key)
    if not isinstance(values, list):
        raise DeckSpecError(f"{path}.{key} must be an array")
    if not all(isinstance(value, str) and value.strip() for value in values):
        raise DeckSpecError(f"{path}.{key} must contain non-empty strings")
    if len(values) != len(set(values)):
        raise DeckSpecError(f"{path}.{key} must not contain duplicates")
    return values


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    try:
        value = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise DeckSpecError(f"{label} is not valid JSON: {resolved}") from error
    if not isinstance(value, dict):
        raise DeckSpecError(f"{label} must contain a top-level object: {resolved}")
    return value


def resolve_optional_file(
    spec_path: Path,
    spec: dict[str, Any],
    key: str,
    label: str,
) -> tuple[Path | None, dict[str, Any] | None]:
    value = spec.get(key)
    if value is None:
        return None, None
    if not isinstance(value, str) or not value.strip():
        raise DeckSpecError(f"$.{key} must be a non-empty path or null")
    resolved = (spec_path.parent / value).expanduser().resolve()
    return resolved, load_json_object(resolved, label)


def validate_fact_ledger(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    try:
        normalized = fact_ledger_validator.validate_ledger(ledger)
    except fact_ledger_validator.LedgerValidationError as error:
        raise DeckSpecError(f"Fact Ledger is invalid: {error}") from error
    return {fact["id"]: fact for fact in normalized["facts"]}


def validate_template_profile(
    profile: dict[str, Any],
    canvas: dict[str, Any],
) -> None:
    if profile.get("schemaVersion") != 1:
        raise DeckSpecError("Template profile schemaVersion must be 1")
    width = require_positive_number(profile, "widthIn", "Template profile")
    height = require_positive_number(profile, "heightIn", "Template profile")
    if (
        abs(width - float(canvas["widthIn"])) > 0.01
        or abs(height - float(canvas["heightIn"])) > 0.01
    ):
        raise DeckSpecError(
            "Deck canvas must match the referenced template profile dimensions"
        )


def validate_spec(
    spec: dict[str, Any],
    *,
    spec_path: Path,
) -> DeckSpecContext:
    if spec.get("schemaVersion") != 1:
        raise DeckSpecError("$.schemaVersion must be 1")
    reject_unknown(
        spec,
        {
            "schemaVersion",
            "request",
            "canvas",
            "templateProfile",
            "factLedger",
            "fontPolicy",
            "slides",
            "qa",
        },
        "$",
    )

    request = require_object(spec, "request", "$")
    reject_unknown(
        request,
        {"topic", "audience", "purpose", "language", "slideCount", "output"},
        "$.request",
    )
    for key in ("topic", "audience", "purpose"):
        require_string(request, key, "$.request")
    language = require_string(request, "language", "$.request")
    if not LANGUAGE_PATTERN.fullmatch(language):
        raise DeckSpecError("$.request.language must be a BCP-47-like language tag")
    slide_count = request.get("slideCount")
    if isinstance(slide_count, bool) or not isinstance(slide_count, int) or slide_count < 1:
        raise DeckSpecError("$.request.slideCount must be a positive integer")

    canvas = require_object(spec, "canvas", "$")
    reject_unknown(canvas, {"source", "widthIn", "heightIn"}, "$.canvas")
    source = require_string(canvas, "source", "$.canvas")
    if source not in {"default", "template", "custom"}:
        raise DeckSpecError("$.canvas.source must be default, template, or custom")
    canvas["widthIn"] = require_positive_number(canvas, "widthIn", "$.canvas")
    canvas["heightIn"] = require_positive_number(canvas, "heightIn", "$.canvas")
    if source == "default" and (
        abs(canvas["widthIn"] - 13.333) > 0.01
        or abs(canvas["heightIn"] - 7.5) > 0.01
    ):
        raise DeckSpecError(
            "$.canvas.source 'default' requires the canonical 13.333x7.5 canvas"
        )

    font_policy = require_object(spec, "fontPolicy", "$")
    reject_unknown(
        font_policy,
        {"selected", "fallbacks", "requireAvailable", "requireRenderedMatch"},
        "$.fontPolicy",
    )
    require_string(font_policy, "selected", "$.fontPolicy")
    require_string_list(font_policy, "fallbacks", "$.fontPolicy")
    require_bool(font_policy, "requireAvailable", "$.fontPolicy")
    require_bool(font_policy, "requireRenderedMatch", "$.fontPolicy")

    slides = spec.get("slides")
    if not isinstance(slides, list) or len(slides) != slide_count:
        raise DeckSpecError(
            "$.slides must contain exactly request.slideCount slide entries"
        )
    for index, slide in enumerate(slides, 1):
        path = f"$.slides[{index - 1}]"
        if not isinstance(slide, dict):
            raise DeckSpecError(f"{path} must be an object")
        reject_unknown(
            slide,
            {"number", "role", "title", "claimIds", "stateLabels"},
            path,
        )
        if slide.get("number") != index:
            raise DeckSpecError("$.slides numbers must be consecutive and start at 1")
        require_string(slide, "role", path)
        require_string(slide, "title", path)
        require_string_list(slide, "claimIds", path)
        states = require_string_list(slide, "stateLabels", path)
        unsupported_states = set(states) - STATE_LABELS
        if unsupported_states:
            raise DeckSpecError(
                f"{path}.stateLabels contains unsupported values: "
                + ", ".join(sorted(unsupported_states))
            )

    qa = require_object(spec, "qa", "$")
    reject_unknown(
        qa,
        {
            "strict",
            "minBodyPt",
            "minTitlePt",
            "maxUnmappedTextSpans",
            "failRenderedOverflow",
            "requireVisualReview",
            "exceptionManifest",
        },
        "$.qa",
    )
    require_bool(qa, "strict", "$.qa")
    qa["minBodyPt"] = require_positive_number(qa, "minBodyPt", "$.qa")
    qa["minTitlePt"] = require_positive_number(qa, "minTitlePt", "$.qa")
    max_unmapped = qa.get("maxUnmappedTextSpans")
    if (
        isinstance(max_unmapped, bool)
        or not isinstance(max_unmapped, int)
        or max_unmapped < 0
    ):
        raise DeckSpecError("$.qa.maxUnmappedTextSpans must be a non-negative integer")
    require_bool(qa, "failRenderedOverflow", "$.qa")
    require_bool(qa, "requireVisualReview", "$.qa")
    exception_manifest = qa.get("exceptionManifest")
    if exception_manifest is not None and (
        not isinstance(exception_manifest, str) or not exception_manifest.strip()
    ):
        raise DeckSpecError("$.qa.exceptionManifest must be a path or null")

    ledger_path, ledger = resolve_optional_file(
        spec_path, spec, "factLedger", "Fact Ledger"
    )
    ledger_index = validate_fact_ledger(ledger) if ledger is not None else {}
    referenced_claims = {
        claim_id for slide in slides for claim_id in slide["claimIds"]
    }
    if referenced_claims and ledger is None:
        raise DeckSpecError(
            "$.factLedger is required when any slide references claimIds"
        )
    missing_claims = sorted(referenced_claims - set(ledger_index))
    if missing_claims:
        raise DeckSpecError(
            "Slide claimIds are missing from the Fact Ledger: "
            + ", ".join(missing_claims)
        )
    non_fact_claims = sorted(
        claim_id
        for claim_id in referenced_claims
        if ledger_index[claim_id]["type"] != "Fact"
    )
    if non_fact_claims:
        raise DeckSpecError(
            "Slide claimIds must reference Fact entries: "
            + ", ".join(non_fact_claims)
        )
    non_accepted_claims = sorted(
        claim_id
        for claim_id in referenced_claims
        if ledger_index[claim_id]["status"] != "Accepted"
    )
    if non_accepted_claims:
        raise DeckSpecError(
            "Slide claimIds must reference Accepted Fact entries: "
            + ", ".join(non_accepted_claims)
        )

    profile_path, profile = resolve_optional_file(
        spec_path, spec, "templateProfile", "Template profile"
    )
    if source == "template" and profile is None:
        raise DeckSpecError(
            "$.templateProfile is required when $.canvas.source is template"
        )
    if profile is not None:
        validate_template_profile(profile, canvas)

    if ledger_path is not None and paths_collide(spec_path, ledger_path):
        raise DeckSpecError("Deck spec and Fact Ledger must be different files")
    if profile_path is not None and paths_collide(spec_path, profile_path):
        raise DeckSpecError("Deck spec and template profile must be different files")

    return DeckSpecContext(
        path=spec_path,
        spec=spec,
        fact_ledger_path=ledger_path,
        fact_ledger=ledger,
        template_profile_path=profile_path,
        template_profile=profile,
    )


def load_deck_spec(path: Path) -> DeckSpecContext:
    resolved = path.expanduser().resolve()
    return validate_spec(
        load_json_object(resolved, "Deck spec"),
        spec_path=resolved,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an adaptive-presentation deck-spec JSON file."
    )
    parser.add_argument("spec", type=Path)
    parser.add_argument("--json", action="store_true", help="Print a JSON summary")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    context = load_deck_spec(args.spec)
    summary = {
        "spec": str(context.path),
        "slides": context.spec["request"]["slideCount"],
        "requiredSourceSlides": sorted(context.required_source_slides),
        "templateProfile": context.template_profile is not None,
        "valid": True,
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(
            "Deck spec PASS | "
            f"slides={summary['slides']} | "
            f"sources={','.join(map(str, summary['requiredSourceSlides'])) or 'none'}"
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DeckSpecError, FileNotFoundError, OSError) as error:
        print(f"deck_spec.py: {error}", file=sys.stderr)
        raise SystemExit(2)
