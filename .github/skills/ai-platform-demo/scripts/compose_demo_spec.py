#!/usr/bin/env python3
"""Compose a customer demo spec from a validated base, industry packs, and overlay."""

from __future__ import annotations

import argparse
import copy
import html as html_lib
import json
import math
import re
import sys
import unicodedata
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import render_demo


DELETE_MARKER = {"$delete": True}
REPLACE_KEY = "$replace"
PLACEHOLDER_PATTERN = re.compile(r"__[A-Z][A-Z0-9_-]*__")
ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
FACT_LEDGER_KEYS = {"schemaVersion", "checkedAt", "facts"}
FACT_KEYS = {
    "id",
    "type",
    "claim",
    "evidence",
    "source",
    "publisher",
    "publishedOrUpdated",
    "accessed",
    "scopeOrStatus",
    "confidence",
}
SOURCE_KEYS = {"title", "url"}


class ComposeError(ValueError):
    """Raised when composition metadata or layers are invalid."""


class VisibleTextParser(HTMLParser):
    """Extract rendered text while preserving adjacency across inline tags."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag.lower() in {"br", "div", "p", "li"}:
            self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"div", "p", "li"}:
            self.parts.append(" ")


def parse_args() -> argparse.Namespace:
    skill_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Compose and validate a customer demo spec without fixing customer design."
    )
    parser.add_argument(
        "--base",
        type=Path,
        default=skill_root / "examples" / "precision-manufacturing.example.json",
        help="Complete validated base spec.",
    )
    parser.add_argument(
        "--pack",
        type=Path,
        action="append",
        default=[],
        help="Industry pack. May be provided multiple times.",
    )
    parser.add_argument("--customer", type=Path, required=True, help="Customer overlay.")
    parser.add_argument(
        "--fact-ledger",
        type=Path,
        help="Machine-readable web-search fact-ledger.json used as research source of truth.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Composed demo-spec.json.")
    parser.add_argument("--html-output", type=Path, help="Optional rendered HTML output.")
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=skill_root / "runtime",
        help="Golden Runtime directory for --html-output.",
    )
    parser.add_argument(
        "--max-research-age-hours",
        type=float,
        default=24.0,
        help="Maximum age of live research metadata.",
    )
    parser.add_argument(
        "--allow-stale-research",
        action="store_true",
        help="Allow stale research only for repository examples and tests.",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)

    def reject_constant(value: str):
        raise ComposeError(f"Non-finite JSON number is not allowed: {value}")

    with resolved.open(encoding="utf-8") as stream:
        return json.load(stream, parse_constant=reject_constant)


def deep_merge(base: Any, overlay: Any) -> Any:
    if overlay == DELETE_MARKER:
        return DELETE_MARKER
    if isinstance(overlay, dict) and set(overlay) == {REPLACE_KEY}:
        return copy.deepcopy(overlay[REPLACE_KEY])
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = copy.deepcopy(base)
        for key, value in overlay.items():
            result = deep_merge(merged.get(key), value)
            if result == DELETE_MARKER:
                merged.pop(key, None)
            else:
                merged[key] = result
        return merged
    return copy.deepcopy(overlay)


def path_exists(value: Any, path: str) -> bool:
    current = value
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return False
        current = current[segment]
    return True


def get_path(value: Any, path: str) -> Any:
    current = value
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            raise ComposeError(f"Missing path: {path}")
        current = current[segment]
    return current


def set_path(value: dict[str, Any], path: str, replacement: Any) -> None:
    segments = path.split(".")
    current = value
    for segment in segments[:-1]:
        child = current.get(segment)
        if not isinstance(child, dict):
            child = {}
            current[segment] = child
        current = child
    current[segments[-1]] = copy.deepcopy(replacement)


def meaningful(value: Any) -> bool:
    if isinstance(value, (dict, list, str)):
        return bool(value)
    return value is not None


def validate_customer_design(customer_spec: dict[str, Any]) -> None:
    design = customer_spec.get("design")
    if design is None:
        return
    if not isinstance(design, dict) or set(design) != {"tokens"}:
        raise ComposeError(
            "Customer overlay design may define only the optional 'tokens' object"
        )
    tokens = design.get("tokens")
    if not isinstance(tokens, dict):
        raise ComposeError("Customer overlay design.tokens must be an object")
    unsupported = set(tokens) - render_demo.ALLOWED_DESIGN_TOKENS
    if unsupported:
        raise ComposeError(
            "Customer overlay design.tokens supports only: "
            + ", ".join(sorted(render_demo.ALLOWED_DESIGN_TOKENS))
        )
    for key, value in tokens.items():
        if (
            not isinstance(value, str)
            or not render_demo.HEX_COLOR_PATTERN.fullmatch(value)
        ):
            raise ComposeError(
                f"Customer overlay design.tokens.{key} must be a six-digit hex color"
            )


def apply_customer_layer(
    composed: dict[str, Any],
    customer_spec: dict[str, Any],
    required_paths: list[str],
) -> dict[str, Any]:
    validate_customer_design(customer_spec)
    merged = deep_merge(composed, customer_spec)
    for section in ["meta", "story"]:
        merged[section] = copy.deepcopy(customer_spec[section])
    for path in required_paths:
        replacement = deep_merge(None, get_path(customer_spec, path))
        if replacement == DELETE_MARKER:
            raise ComposeError(f"Customer-required path cannot be deleted: {path}")
        set_path(merged, path, replacement)
    return merged


def iter_strings(value: Any, path: str = "$"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from iter_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_strings(child, f"{path}[{index}]")


def visible_text(value: str) -> str:
    parser = VisibleTextParser()
    parser.feed(value)
    parser.close()
    normalized = unicodedata.normalize("NFKC", "".join(parser.parts))
    return re.sub(r"\s+", " ", normalized).strip()


def term_matches(value: str, term: str) -> bool:
    text = visible_text(value)
    normalized_term = unicodedata.normalize("NFKC", html_lib.unescape(term)).strip()
    if re.fullmatch(r"[A-Z0-9]{2,5}", normalized_term):
        pattern = re.compile(
            rf"(?<![A-Za-z0-9]){re.escape(normalized_term)}(?![A-Za-z0-9])",
            re.IGNORECASE,
        )
        return bool(pattern.search(text))
    return normalized_term.casefold() in text.casefold()


def validate_pack(
    document: Any,
    source: Path,
) -> tuple[dict[str, Any], list[str], list[str], dict[str, Any]]:
    if not isinstance(document, dict):
        raise ComposeError(f"{source}: pack must be an object")
    metadata = document.get("_pack")
    spec = document.get("spec")
    if not isinstance(metadata, dict) or not isinstance(spec, dict):
        raise ComposeError(f"{source}: pack requires _pack and spec objects")
    for key in ["id", "name"]:
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ComposeError(f"{source}: _pack.{key} must be a non-empty string")
    forbidden = {"meta", "design", "story"} & set(spec)
    if forbidden:
        raise ComposeError(
            f"{source}: Industry Pack must not define customer-owned section(s): "
            + ", ".join(sorted(forbidden))
        )
    if REPLACE_KEY in spec or "$delete" in spec:
        raise ComposeError(f"{source}: merge directives are not allowed at pack spec root")
    required_paths = metadata.get("requiredCustomerPaths", [])
    if not isinstance(required_paths, list) or not all(
        isinstance(path, str) and path.strip() for path in required_paths
    ):
        raise ComposeError(f"{source}: _pack.requiredCustomerPaths must contain strings")
    forbid_terms = metadata.get("forbidOutputTerms", [])
    if not isinstance(forbid_terms, list) or not all(
        isinstance(term, str) and term for term in forbid_terms
    ):
        raise ComposeError(f"{source}: _pack.forbidOutputTerms must contain strings")
    return spec, required_paths, forbid_terms, metadata


def parse_checked_at(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ComposeError("_customer.research.checkedAt must be ISO 8601") from error
    if parsed.tzinfo is None:
        raise ComposeError("_customer.research.checkedAt must include a timezone")
    return parsed.astimezone(timezone.utc)


def canonical_source_url(value: str) -> str | None:
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
    path = parsed.path or "/"
    return urlunparse((scheme, netloc, path, "", parsed.query, ""))


def fact_ledger_research(
    document: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if (
        not isinstance(document, dict)
        or set(document) != FACT_LEDGER_KEYS
        or type(document.get("schemaVersion")) is not int
        or document["schemaVersion"] != 1
    ):
        raise ComposeError("Fact Ledger requires schemaVersion 1")
    checked_at = document.get("checkedAt")
    if not isinstance(checked_at, str) or not ISO_TIMESTAMP_PATTERN.fullmatch(
        checked_at
    ):
        raise ComposeError(
            "Fact Ledger checkedAt must be a timezone-aware ISO 8601 timestamp"
        )
    parse_checked_at(checked_at)
    facts = document.get("facts")
    if not isinstance(facts, list) or not facts:
        raise ComposeError("Fact Ledger facts must be a non-empty array")

    required_strings = (
        "id",
        "type",
        "claim",
        "evidence",
        "publisher",
        "publishedOrUpdated",
        "accessed",
        "scopeOrStatus",
        "confidence",
    )
    seen_ids: set[str] = set()
    sources_by_url: dict[str, dict[str, Any]] = {}
    for index, fact in enumerate(facts):
        path = f"Fact Ledger facts[{index}]"
        if not isinstance(fact, dict) or set(fact) != FACT_KEYS:
            raise ComposeError(f"{path} must match the Fact Ledger schema")
        for key in required_strings:
            value = fact.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ComposeError(f"{path}.{key} must be a non-empty string")
        if fact["type"] not in {"Fact", "Inference", "Assumption"}:
            raise ComposeError(f"{path}.type is invalid")
        if fact["confidence"] not in {"High", "Medium", "Low"}:
            raise ComposeError(f"{path}.confidence is invalid")
        if fact["id"] in seen_ids:
            raise ComposeError(f"Fact Ledger ID is duplicated: {fact['id']}")
        seen_ids.add(fact["id"])
        if not ISO_DATE_PATTERN.fullmatch(fact["accessed"]):
            raise ComposeError(f"{path}.accessed must be YYYY-MM-DD")
        try:
            date.fromisoformat(fact["accessed"])
        except ValueError as error:
            raise ComposeError(f"{path}.accessed must be YYYY-MM-DD") from error
        published_or_updated = fact["publishedOrUpdated"]
        if published_or_updated != "확인 불가":
            if not ISO_DATE_PATTERN.fullmatch(published_or_updated):
                raise ComposeError(
                    f"{path}.publishedOrUpdated must be YYYY-MM-DD or 확인 불가"
                )
            try:
                date.fromisoformat(published_or_updated)
            except ValueError as error:
                raise ComposeError(
                    f"{path}.publishedOrUpdated must be YYYY-MM-DD or 확인 불가"
                ) from error

        source = fact.get("source")
        if not isinstance(source, dict) or set(source) != SOURCE_KEYS:
            raise ComposeError(f"{path}.source must match the Fact Ledger schema")
        title = source.get("title")
        source_url = source.get("url")
        if not isinstance(title, str) or not title.strip():
            raise ComposeError(f"{path}.source.title must be a non-empty string")
        if not isinstance(source_url, str):
            raise ComposeError(f"{path}.source.url must be an HTTP(S) URL")
        canonical_url = canonical_source_url(source_url)
        if canonical_url is None:
            raise ComposeError(f"{path}.source.url must be an HTTP(S) URL")
        if fact["type"] != "Fact":
            continue
        if canonical_url not in sources_by_url:
            sources_by_url[canonical_url] = {
                "title": title.strip(),
                "url": canonical_url,
                "publisher": fact["publisher"].strip(),
                "ledgerIds": [],
            }
        sources_by_url[canonical_url]["ledgerIds"].append(fact["id"])

    if len(sources_by_url) < 2:
        raise ComposeError(
            "AI demo Fact Ledger requires at least two unique canonical Fact sources"
        )
    source_urls = list(sources_by_url)
    research = {
        "mode": "live",
        "checkedAt": checked_at,
        "sourceUrls": source_urls,
        "ledgerIds": sorted(seen_ids),
    }
    provenance = {
        "checkedAt": checked_at,
        "ledgerIds": sorted(seen_ids),
        "sources": list(sources_by_url.values()),
    }
    return research, provenance


def apply_fact_ledger(
    customer_document: Any,
    fact_ledger: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(customer_document, dict):
        raise ComposeError("Customer overlay must be an object")
    metadata = customer_document.get("_customer")
    if not isinstance(metadata, dict):
        raise ComposeError("Customer overlay requires an _customer object")
    research, provenance = fact_ledger_research(fact_ledger)
    existing = metadata.get("research")
    if existing is not None:
        if not isinstance(existing, dict):
            raise ComposeError("_customer.research must be an object")
        existing_checked_at = existing.get("checkedAt")
        existing_urls = existing.get("sourceUrls")
        if not isinstance(existing_checked_at, str) or not isinstance(
            existing_urls, list
        ):
            raise ComposeError(
                "Existing _customer.research must match the supplied Fact Ledger"
            )
        try:
            existing_checked = parse_checked_at(existing_checked_at)
        except ComposeError as error:
            raise ComposeError(
                "Existing _customer.research must match the supplied Fact Ledger"
            ) from error
        canonical_existing = [
            canonical_source_url(value) if isinstance(value, str) else None
            for value in existing_urls
        ]
        if (
            existing_checked != parse_checked_at(research["checkedAt"])
            or None in canonical_existing
            or set(canonical_existing) != set(research["sourceUrls"])
        ):
            raise ComposeError(
                "Existing _customer.research does not match the supplied Fact Ledger"
            )
    updated = copy.deepcopy(customer_document)
    updated["_customer"]["research"] = research
    return updated, provenance


def research_provenance(research: dict[str, Any]) -> dict[str, Any]:
    return {
        "checkedAt": research["checkedAt"],
        "sources": [
            {"url": canonical_source_url(url)}
            for url in research["sourceUrls"]
        ],
    }


def validate_customer(
    document: Any,
    required_paths: list[str],
    *,
    allow_stale: bool,
    max_age_hours: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(document, dict):
        raise ComposeError("Customer overlay must be an object")
    metadata = document.get("_customer")
    spec = document.get("spec")
    if not isinstance(metadata, dict) or not isinstance(spec, dict):
        raise ComposeError("Customer overlay requires _customer and spec objects")
    for section in ["meta", "story"]:
        if not isinstance(spec.get(section), dict):
            raise ComposeError(f"Customer overlay must own the full '{section}' section")
    validate_customer_design(spec)

    research = metadata.get("research")
    if not isinstance(research, dict) or research.get("mode") != "live":
        raise ComposeError("_customer.research.mode must be 'live'")
    checked_at_raw = research.get("checkedAt")
    if not isinstance(checked_at_raw, str):
        raise ComposeError("_customer.research.checkedAt is required")
    checked_at = parse_checked_at(checked_at_raw)
    sources = research.get("sourceUrls")
    if not isinstance(sources, list):
        raise ComposeError("_customer.research.sourceUrls must be an array")
    if not all(isinstance(url, str) for url in sources):
        raise ComposeError("Customer research sources must be valid HTTP(S) URL strings")
    canonical_sources = [canonical_source_url(url) for url in sources]
    if any(url is None for url in canonical_sources):
        raise ComposeError("Customer research sources must be valid HTTP(S) URL strings")
    unique_sources = sorted(set(canonical_sources))
    if len(unique_sources) < 2:
        raise ComposeError("Customer overlay requires at least two unique HTTP(S) sources")
    now = datetime.now(timezone.utc)
    age_hours = (now - checked_at).total_seconds() / 3600
    if age_hours < -0.25:
        raise ComposeError("Research timestamp is unexpectedly in the future")
    if not allow_stale:
        if age_hours > max_age_hours:
            raise ComposeError(
                f"Live research is {age_hours:.1f} hours old; maximum is {max_age_hours:.1f}"
            )

    missing_paths = []
    for path in required_paths:
        if not path_exists(spec, path):
            missing_paths.append(path)
            continue
        resolved = deep_merge(None, get_path(spec, path))
        if resolved == DELETE_MARKER or not meaningful(resolved):
            missing_paths.append(path)
    if missing_paths:
        raise ComposeError(
            "Customer overlay is missing high-impact path(s): "
            + ", ".join(sorted(set(missing_paths)))
        )
    forbid_terms = metadata.get("forbidTerms", [])
    if not isinstance(forbid_terms, list) or not all(
        isinstance(term, str) and term for term in forbid_terms
    ):
        raise ComposeError("_customer.forbidTerms must contain non-empty strings")
    return spec, metadata


def stale_research_allowed(customer_path: Path, skill_root: Path) -> bool:
    resolved = customer_path.expanduser().resolve()
    return any(
        resolved.is_relative_to((skill_root / directory).resolve())
        for directory in ("examples", "tests")
    )


def check_output_leaks(spec: dict[str, Any], forbid_terms: list[str]) -> None:
    for path, value in iter_strings(spec):
        for term in forbid_terms:
            if term_matches(value, term):
                raise ComposeError(f"Forbidden base/example term leaked into {path}: {term}")
        placeholder = PLACEHOLDER_PATTERN.search(visible_text(value))
        if placeholder:
            raise ComposeError(f"Unresolved placeholder in {path}: {placeholder.group(0)}")


def validate_output_paths(
    output: Path,
    html_output: Path | None,
    input_paths: set[Path],
) -> None:
    if output.suffix.lower() != ".json":
        raise ComposeError("--output must use the .json extension")
    if any(render_demo.paths_collide(output, path) for path in input_paths):
        raise ComposeError("--output must not overwrite a base, pack, or customer input")
    if html_output is None:
        return
    if html_output.suffix.lower() != ".html":
        raise ComposeError("--html-output must use the .html extension")
    if any(render_demo.paths_collide(html_output, path) for path in input_paths):
        raise ComposeError("--html-output must not overwrite an input")
    if render_demo.paths_collide(html_output, output):
        raise ComposeError("--html-output must not overwrite the spec output")


def main() -> int:
    args = parse_args()
    if not math.isfinite(args.max_research_age_hours) or args.max_research_age_hours <= 0:
        raise ComposeError("--max-research-age-hours must be a finite number greater than zero")
    skill_root = Path(__file__).resolve().parents[1]
    customer_path = args.customer.expanduser().resolve()
    if args.allow_stale_research and not stale_research_allowed(customer_path, skill_root):
        raise ComposeError(
            "--allow-stale-research is restricted to repository examples and tests"
        )
    base = load_json(args.base)
    if not isinstance(base, dict):
        raise ComposeError("Base spec must be an object")
    composed = copy.deepcopy(base)
    required_paths: list[str] = []
    pack_forbid_terms: list[str] = []
    pack_summaries = []

    for pack_path in args.pack:
        pack_document = load_json(pack_path)
        pack_spec, pack_required, pack_forbid, metadata = validate_pack(
            pack_document,
            pack_path,
        )
        composed = deep_merge(composed, pack_spec)
        required_paths.extend(pack_required)
        pack_forbid_terms.extend(pack_forbid)
        pack_summaries.append(
            {
                "id": metadata["id"],
                "name": metadata["name"],
            }
        )

    customer_document = load_json(customer_path)
    ledger_provenance = None
    if args.fact_ledger is not None:
        customer_document, ledger_provenance = apply_fact_ledger(
            customer_document,
            load_json(args.fact_ledger),
        )
    customer_spec, customer_metadata = validate_customer(
        customer_document,
        required_paths,
        allow_stale=args.allow_stale_research,
        max_age_hours=args.max_research_age_hours,
    )
    composed = apply_customer_layer(composed, customer_spec, required_paths)
    provenance = ledger_provenance or research_provenance(
        customer_metadata["research"]
    )
    composed["meta"]["research"] = provenance
    composed = render_demo.sanitize_rich_fields(composed)
    check_output_leaks(
        composed,
        pack_forbid_terms + customer_metadata.get("forbidTerms", []),
    )
    render_demo.validate_spec(composed)

    output = args.output.expanduser().resolve()
    input_paths = {
        args.base.expanduser().resolve(),
        customer_path,
        *(path.expanduser().resolve() for path in args.pack),
        *render_demo.runtime_input_paths(args.runtime_dir),
    }
    if args.fact_ledger is not None:
        input_paths.add(args.fact_ledger.expanduser().resolve())
    html_output = args.html_output.expanduser().resolve() if args.html_output else None
    validate_output_paths(output, html_output, input_paths)
    rendered_html = (
        render_demo.render(composed, args.runtime_dir) if html_output is not None else None
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(composed, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )

    summary: dict[str, Any] = {
        "base": str(args.base.expanduser().resolve()),
        "packs": pack_summaries,
        "customer": composed["meta"]["customer"],
        "archetype": composed["design"]["archetype"],
        "researchCheckedAt": customer_metadata["research"]["checkedAt"],
        "researchSources": [
            source["url"] for source in provenance["sources"]
        ],
        "researchLedgerIds": customer_metadata["research"].get("ledgerIds", []),
        "routes": len(composed["story"].get("routeScope", composed["navigation"])),
        "dataRoutes": len(composed["navigation"]),
        "agents": len(composed["foundry"]["profiles"]),
        "specOutput": str(output),
        "specBytes": output.stat().st_size,
    }

    if html_output is not None:
        html_output.parent.mkdir(parents=True, exist_ok=True)
        html_output.write_text(rendered_html, encoding="utf-8")
        summary.update(
            {
                "htmlOutput": str(html_output),
                "htmlBytes": html_output.stat().st_size,
            }
        )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        ComposeError,
        FileNotFoundError,
        json.JSONDecodeError,
        render_demo.SpecError,
        RuntimeError,
    ) as error:
        print(f"compose_demo_spec.py: {error}", file=sys.stderr)
        raise SystemExit(2)
