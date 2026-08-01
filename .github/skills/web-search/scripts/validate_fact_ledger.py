#!/usr/bin/env python3
"""Validate and normalize the shared Web Search Fact Ledger contract."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import ipaddress
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse


ENTRY_KEYS = {
    "id",
    "type",
    "claim",
    "evidence",
    "sources",
    "basisIds",
    "assumptionOwner",
    "validationNeeded",
    "source",
    "publisher",
    "publishedOrUpdated",
    "accessed",
    "scopeOrStatus",
    "confidence",
    "status",
    "decisionRationale",
}
SOURCE_KEYS = {
    "title",
    "url",
    "publisher",
    "publishedOrUpdated",
    "accessed",
    "locator",
}
LEGACY_SOURCE_KEYS = {"title", "url", "locator"}
EXCLUDED_SOURCE_KEYS = {"title", "url", "reason", "accessed"}
ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_-]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    r"(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


class LedgerValidationError(ValueError):
    """Raised when a Fact Ledger violates schema or semantic constraints."""


def reject_unknown(value: dict[str, Any], allowed: set[str], path: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise LedgerValidationError(
            f"{path} contains unsupported field(s): {', '.join(unknown)}"
        )


def require_string(value: dict[str, Any], key: str, path: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item.strip():
        raise LedgerValidationError(f"{path}.{key} must be a non-empty string")
    return item.strip()


def parse_date(value: str, path: str) -> dt.date:
    if not DATE_PATTERN.fullmatch(value):
        raise LedgerValidationError(f"{path} must be YYYY-MM-DD")
    try:
        return dt.date.fromisoformat(value)
    except ValueError as error:
        raise LedgerValidationError(f"{path} must be a valid date") from error


def parse_timestamp(value: str) -> dt.datetime:
    if not TIMESTAMP_PATTERN.fullmatch(value):
        raise LedgerValidationError(
            "$.checkedAt must be a timezone-aware ISO 8601 timestamp"
        )
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise LedgerValidationError("$.checkedAt is not a valid timestamp") from error
    if parsed.utcoffset() is None:
        raise LedgerValidationError("$.checkedAt must include a timezone")
    return parsed


def canonical_public_url(value: str, path: str) -> str:
    try:
        parsed = urlparse(value)
        port = parsed.port
    except ValueError as error:
        raise LedgerValidationError(f"{path} must be a valid public HTTP(S) URL") from error
    scheme = parsed.scheme.casefold()
    host = parsed.hostname
    if scheme not in {"http", "https"} or not host or parsed.username or parsed.password:
        raise LedgerValidationError(f"{path} must be a public HTTP(S) URL")
    normalized_host = host.casefold().rstrip(".")
    if normalized_host == "localhost" or normalized_host.endswith(".local"):
        raise LedgerValidationError(f"{path} must not target a local host")
    numeric_labels = normalized_host.split(".")
    if numeric_labels and all(
        re.fullmatch(r"(?:0x[0-9a-f]+|[0-9]+)", label)
        for label in numeric_labels
    ):
        try:
            ipaddress.ip_address(normalized_host)
        except ValueError as error:
            raise LedgerValidationError(
                f"{path} must not use a non-canonical numeric host"
            ) from error
    try:
        address = ipaddress.ip_address(normalized_host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise LedgerValidationError(f"{path} must not target a private IP address")
    if parsed.fragment:
        raise LedgerValidationError(
            f"{path} must omit fragments; record the location in locator"
        )
    default_port = (scheme == "https" and port == 443) or (
        scheme == "http" and port == 80
    )
    rendered_host = f"[{normalized_host}]" if ":" in normalized_host else normalized_host
    netloc = rendered_host if port is None or default_port else f"{rendered_host}:{port}"
    return urlunparse((scheme, netloc, parsed.path or "/", "", parsed.query, ""))


def validate_source(
    source: Any,
    path: str,
    checked_date: dt.date,
) -> dict[str, Any]:
    if not isinstance(source, dict):
        raise LedgerValidationError(f"{path} must be an object")
    reject_unknown(source, SOURCE_KEYS, path)
    required = SOURCE_KEYS - {"locator"}
    missing = sorted(required - set(source))
    if missing:
        raise LedgerValidationError(f"{path} is missing: {', '.join(missing)}")
    normalized = copy.deepcopy(source)
    normalized["title"] = require_string(source, "title", path)
    normalized["publisher"] = require_string(source, "publisher", path)
    normalized["url"] = canonical_public_url(
        require_string(source, "url", path), f"{path}.url"
    )
    accessed = parse_date(require_string(source, "accessed", path), f"{path}.accessed")
    if accessed > checked_date:
        raise LedgerValidationError(f"{path}.accessed cannot be after checkedAt")
    published = require_string(source, "publishedOrUpdated", path)
    if published != "확인 불가":
        published_date = parse_date(published, f"{path}.publishedOrUpdated")
        if published_date > accessed:
            raise LedgerValidationError(
                f"{path}.publishedOrUpdated cannot be after accessed"
            )
    if "locator" in source:
        normalized["locator"] = require_string(source, "locator", path)
    return normalized


def legacy_source(entry: dict[str, Any], path: str) -> dict[str, Any] | None:
    source = entry.get("source")
    legacy_fields = {"source", "publisher", "publishedOrUpdated", "accessed"}
    present = legacy_fields & set(entry)
    if not present:
        return None
    if present != legacy_fields or not isinstance(source, dict):
        raise LedgerValidationError(
            f"{path} legacy provenance requires source, publisher, "
            "publishedOrUpdated, and accessed"
        )
    reject_unknown(source, LEGACY_SOURCE_KEYS, f"{path}.source")
    combined = {
        "title": require_string(source, "title", f"{path}.source"),
        "url": require_string(source, "url", f"{path}.source"),
        "publisher": require_string(entry, "publisher", path),
        "publishedOrUpdated": require_string(entry, "publishedOrUpdated", path),
        "accessed": require_string(entry, "accessed", path),
    }
    if "locator" in source:
        combined["locator"] = require_string(source, "locator", f"{path}.source")
    return combined


def normalized_sources(
    entry: dict[str, Any],
    path: str,
    checked_date: dt.date,
) -> list[dict[str, Any]]:
    values = entry.get("sources")
    if values is not None:
        if {"source", "publisher", "publishedOrUpdated", "accessed"} & set(entry):
            raise LedgerValidationError(
                f"{path} must not combine sources with legacy provenance fields"
            )
        if not isinstance(values, list) or not values:
            raise LedgerValidationError(f"{path}.sources must be a non-empty array")
        sources = [
            validate_source(source, f"{path}.sources[{index}]", checked_date)
            for index, source in enumerate(values)
        ]
    else:
        legacy = legacy_source(entry, path)
        sources = (
            [validate_source(legacy, f"{path}.source", checked_date)]
            if legacy is not None
            else []
        )
    urls = [source["url"] for source in sources]
    if len(urls) != len(set(urls)):
        raise LedgerValidationError(f"{path}.sources contains duplicate URLs")
    return sources


def validate_ledger(
    value: Any,
    *,
    now: dt.datetime | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LedgerValidationError("$ must be an object")
    reject_unknown(value, {"schemaVersion", "checkedAt", "facts", "excludedSources"}, "$")
    if type(value.get("schemaVersion")) is not int or value["schemaVersion"] != 1:
        raise LedgerValidationError("$.schemaVersion must be 1")
    checked_at = parse_timestamp(require_string(value, "checkedAt", "$"))
    current = now or dt.datetime.now(dt.timezone.utc)
    if current.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    if checked_at > current.astimezone(checked_at.tzinfo) + dt.timedelta(minutes=5):
        raise LedgerValidationError("$.checkedAt cannot be in the future")

    facts = value.get("facts")
    if not isinstance(facts, list) or not facts:
        raise LedgerValidationError("$.facts must be a non-empty array")

    normalized = copy.deepcopy(value)
    normalized_facts: list[dict[str, Any]] = []
    entries_by_id: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(facts):
        path = f"$.facts[{index}]"
        if not isinstance(entry, dict):
            raise LedgerValidationError(f"{path} must be an object")
        reject_unknown(entry, ENTRY_KEYS, path)
        entry_id = require_string(entry, "id", path)
        if not ID_PATTERN.fullmatch(entry_id):
            raise LedgerValidationError(
                f"{path}.id must start with A-Z and use A-Z, 0-9, _ or -"
            )
        if entry_id in entries_by_id:
            raise LedgerValidationError(f"Fact Ledger ID is duplicated: {entry_id}")
        entry_type = require_string(entry, "type", path)
        if entry_type not in {"Fact", "Inference", "Assumption"}:
            raise LedgerValidationError(f"{path}.type is invalid")
        require_string(entry, "claim", path)
        require_string(entry, "evidence", path)
        require_string(entry, "scopeOrStatus", path)
        confidence = require_string(entry, "confidence", path)
        if confidence not in {"High", "Medium", "Low"}:
            raise LedgerValidationError(f"{path}.confidence is invalid")
        for optional_string in (
            "assumptionOwner",
            "validationNeeded",
            "decisionRationale",
        ):
            if optional_string in entry:
                require_string(entry, optional_string, path)
        status = entry.get("status", "Accepted")
        if not isinstance(status, str):
            raise LedgerValidationError(f"{path}.status must be a string")
        if status not in {"Accepted", "Contested", "Rejected", "Unresolved"}:
            raise LedgerValidationError(f"{path}.status is invalid")
        if status != "Accepted":
            require_string(entry, "decisionRationale", path)

        sources = normalized_sources(entry, path, checked_at.date())
        basis_ids = entry.get("basisIds", [])
        if not isinstance(basis_ids, list) or not all(
            isinstance(item, str) and ID_PATTERN.fullmatch(item)
            for item in basis_ids
        ):
            raise LedgerValidationError(f"{path}.basisIds contains an invalid ID")
        if "basisIds" in entry and not basis_ids:
            raise LedgerValidationError(f"{path}.basisIds must not be empty")
        if len(basis_ids) != len(set(basis_ids)):
            raise LedgerValidationError(f"{path}.basisIds contains duplicates")
        if entry_type == "Fact" and not sources:
            raise LedgerValidationError(f"{path} Fact requires at least one source")
        if entry_type == "Inference" and not (basis_ids or sources):
            raise LedgerValidationError(
                f"{path} Inference requires basisIds or direct sources"
            )
        if entry_type == "Assumption":
            require_string(entry, "assumptionOwner", path)
            require_string(entry, "validationNeeded", path)

        normalized_entry = copy.deepcopy(entry)
        normalized_entry["status"] = status
        if sources:
            normalized_entry["sources"] = sources
        else:
            normalized_entry.pop("sources", None)
        for key in ("source", "publisher", "publishedOrUpdated", "accessed"):
            normalized_entry.pop(key, None)
        normalized_facts.append(normalized_entry)
        entries_by_id[entry_id] = normalized_entry

    for index, entry in enumerate(normalized_facts):
        path = f"$.facts[{index}]"
        for basis_id in entry.get("basisIds", []):
            if basis_id == entry["id"]:
                raise LedgerValidationError(f"{path}.basisIds must not reference itself")
            basis = entries_by_id.get(basis_id)
            if basis is None:
                raise LedgerValidationError(
                    f"{path}.basisIds references missing ID: {basis_id}"
                )
            if basis["type"] == "Assumption":
                raise LedgerValidationError(
                    f"{path}.basisIds must reference Fact or Inference entries"
                )
            if entry["status"] == "Accepted" and basis["status"] != "Accepted":
                raise LedgerValidationError(
                    f"{path} Accepted entry requires Accepted basis: {basis_id}"
                )

    graph = {
        entry["id"]: entry.get("basisIds", [])
        for entry in normalized_facts
        if entry.get("basisIds")
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(entry_id: str) -> None:
        if entry_id in visiting:
            raise LedgerValidationError(
                f"Fact Ledger basisIds contains a cycle at: {entry_id}"
            )
        if entry_id in visited:
            return
        visiting.add(entry_id)
        for basis_id in graph.get(entry_id, []):
            visit(basis_id)
        visiting.remove(entry_id)
        visited.add(entry_id)

    for entry_id in graph:
        visit(entry_id)

    excluded = value.get("excludedSources", [])
    if not isinstance(excluded, list):
        raise LedgerValidationError("$.excludedSources must be an array")
    normalized_excluded: list[dict[str, Any]] = []
    for index, source in enumerate(excluded):
        path = f"$.excludedSources[{index}]"
        if not isinstance(source, dict):
            raise LedgerValidationError(f"{path} must be an object")
        reject_unknown(source, EXCLUDED_SOURCE_KEYS, path)
        if set(source) != EXCLUDED_SOURCE_KEYS:
            raise LedgerValidationError(f"{path} must include title, url, reason, accessed")
        normalized_source = copy.deepcopy(source)
        normalized_source["title"] = require_string(source, "title", path)
        normalized_source["reason"] = require_string(source, "reason", path)
        normalized_source["url"] = canonical_public_url(
            require_string(source, "url", path), f"{path}.url"
        )
        accessed = parse_date(
            require_string(source, "accessed", path), f"{path}.accessed"
        )
        if accessed > checked_at.date():
            raise LedgerValidationError(f"{path}.accessed cannot be after checkedAt")
        normalized_excluded.append(normalized_source)

    normalized["facts"] = normalized_facts
    if excluded:
        normalized["excludedSources"] = normalized_excluded
    return normalized


def load_ledger(path: str | Path, *, now: dt.datetime | None = None) -> dict[str, Any]:
    source = Path(path).expanduser().resolve()

    def reject_constant(token: str):
        raise LedgerValidationError(f"Non-finite JSON number is invalid: {token}")

    try:
        value = json.loads(
            source.read_text(encoding="utf-8"),
            parse_constant=reject_constant,
        )
    except json.JSONDecodeError as error:
        raise LedgerValidationError(f"Fact Ledger is not valid JSON: {source}") from error
    return validate_ledger(value, now=now)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args(argv)
    try:
        normalized = load_ledger(args.ledger)
    except (OSError, LedgerValidationError) as error:
        print(f"Fact Ledger INVALID: {error}", file=sys.stderr)
        return 1
    print(
        "Fact Ledger PASS | "
        f"entries={len(normalized['facts'])} | "
        f"excluded={len(normalized.get('excludedSources', []))}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
