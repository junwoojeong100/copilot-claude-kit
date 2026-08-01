#!/usr/bin/env python3
"""Finding-level QA exception manifests for adaptive presentations."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ExceptionManifestError(ValueError):
    """Raised when a QA exception manifest is invalid or stale."""


@dataclass(frozen=True)
class ExceptionManifest:
    path: Path
    reasons: dict[str, str]


def finding_id(detector: str, finding: dict[str, Any]) -> str:
    identity = {
        key: value
        for key, value in finding.items()
        if key not in {"allowed", "findingId", "exceptionReason"}
    }
    payload = json.dumps(
        {"detector": detector, "finding": identity},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"{detector}:{hashlib.sha256(payload).hexdigest()[:16]}"


def annotate(
    detector: str,
    finding: dict[str, Any],
    *,
    allowed_finding_ids: set[str] | None = None,
    slide_allowed: bool = False,
) -> dict[str, Any]:
    identifier = finding_id(detector, finding)
    finding["findingId"] = identifier
    finding["allowed"] = slide_allowed or identifier in (allowed_finding_ids or set())
    return finding


def load_exception_manifest(path: Path | None) -> ExceptionManifest | None:
    if path is None:
        return None
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    try:
        value = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ExceptionManifestError(
            f"QA exception manifest is not valid JSON: {resolved}"
        ) from error
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise ExceptionManifestError("QA exception manifest schemaVersion must be 1")
    unknown = sorted(set(value) - {"schemaVersion", "exceptions"})
    if unknown:
        raise ExceptionManifestError(
            "QA exception manifest contains unsupported fields: "
            + ", ".join(unknown)
        )
    exceptions = value.get("exceptions")
    if not isinstance(exceptions, list):
        raise ExceptionManifestError("QA exception manifest exceptions must be an array")
    reasons: dict[str, str] = {}
    for index, item in enumerate(exceptions):
        if not isinstance(item, dict):
            raise ExceptionManifestError(f"exceptions[{index}] must be an object")
        item_unknown = sorted(set(item) - {"findingId", "reason"})
        if item_unknown:
            raise ExceptionManifestError(
                f"exceptions[{index}] contains unsupported fields: "
                + ", ".join(item_unknown)
            )
        identifier = item.get("findingId")
        reason = item.get("reason")
        if not isinstance(identifier, str) or not identifier.strip():
            raise ExceptionManifestError(
                f"exceptions[{index}].findingId must be a non-empty string"
            )
        if not isinstance(reason, str) or len(reason.strip()) < 12:
            raise ExceptionManifestError(
                f"exceptions[{index}].reason must explain the reviewed exception"
            )
        if identifier in reasons:
            raise ExceptionManifestError(
                f"Duplicate QA exception findingId: {identifier}"
            )
        reasons[identifier] = reason.strip()
    return ExceptionManifest(path=resolved, reasons=reasons)


def apply_reasons(
    findings: list[dict[str, Any]],
    manifest: ExceptionManifest | None,
) -> set[str]:
    if manifest is None:
        return set()
    used: set[str] = set()
    for finding in findings:
        identifier = finding.get("findingId")
        if identifier in manifest.reasons:
            finding["allowed"] = True
            finding["exceptionReason"] = manifest.reasons[identifier]
            used.add(identifier)
    return used


def reject_stale_exceptions(
    manifest: ExceptionManifest | None,
    used_ids: set[str],
) -> None:
    if manifest is None:
        return
    stale = sorted(set(manifest.reasons) - used_ids)
    if stale:
        raise ExceptionManifestError(
            "QA exception manifest contains stale or unused finding IDs: "
            + ", ".join(stale)
        )
