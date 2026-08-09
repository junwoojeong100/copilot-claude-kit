#!/usr/bin/env python3
"""Fast pre-QA lint for a demo-spec.json.

Runs render_demo's full structural / semantic / security validation, then checks the
interaction invariants that the browser QA (scripts/verify_demo.js) enforces.
This catches the common gotchas in under a second instead of a ~2 minute Puppeteer cycle.

The timing thresholds mirror the fixed Golden Runtime plus the waits in verify_demo.js.
Run this before rendering and before the browser QA:

    python3 -B scripts/lint_spec.py <demo-spec.json>
"""
from __future__ import annotations

import argparse
import html as html_lib
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render_demo  # noqa: E402

ORCH_SUMMARY_RE = re.compile(r"decision package|의사결정 패키지", re.IGNORECASE)
HANGUL_RE = re.compile(r"[가-힣]")
KOREAN_COPY_EXCEPTIONS = {
    "aca",
    "aks",
    "ai",
    "api",
    "app platform",
    "copilot",
    "crm",
    "devops",
    "erp",
    "esg",
    "ess",
    "finops",
    "foundry",
    "github advanced security",
    "github ai controls",
    "github copilot",
    "github ecosystem",
    "github",
    "kpi",
    "mes",
    "microsoft entra id",
    "microsoft foundry",
    "microsoft purview",
    "mlops",
    "oee",
    "pr",
    "scm",
    "soc",
    "aca · aks",
    "copilot · actions · advanced security",
}
DEFAULT_KOREAN_LANGUAGE_POLICY = {
    "mode": "korean-first-technical-english",
    "targetLatinRatio": 0.40,
    "maxLatinRatio": 0.55,
    "maxRouteLatinRatio": 0.75,
    "minAnalyzedCharacters": 80,
    "preserveOfficialTerms": True,
    "protectedTerms": [],
    "allowHighLatinRoutes": [],
}
EXECUTIVE_COPY_KEYS = {
    "action",
    "appName",
    "audience",
    "badge",
    "button",
    "complete",
    "controlEvidence",
    "crumb",
    "dangerLabel",
    "defaultRecommendation",
    "detail",
    "detailTitle",
    "differentiation",
    "explanation",
    "factorsHint",
    "factorsTitle",
    "feedHint",
    "feedTitle",
    "frame",
    "goodLabel",
    "hint",
    "impactsHint",
    "impactsTitle",
    "industry",
    "infrastructureLabel",
    "label",
    "leftLabel",
    "leversHint",
    "leversTitle",
    "message",
    "name",
    "note",
    "outcome",
    "owner",
    "question",
    "recommendationAfter",
    "recommendationBefore",
    "rightLabel",
    "running",
    "short",
    "sub",
    "subtitle",
    "successCriteria",
    "summary",
    "text",
    "timebox",
    "title",
    "toastText",
    "toastTitle",
    "warningLabel",
}
LATIN_RE = re.compile(r"[A-Za-z]")


def _reject_constant(value: str):
    raise render_demo.SpecError(f"non-finite JSON constant is not allowed: {value}")


def _is_korean_copy(value: object) -> bool:
    text = str(value or "").strip()
    return bool(HANGUL_RE.search(text)) or text.casefold() in KOREAN_COPY_EXCEPTIONS


def korean_copy_invariants(spec: dict) -> list[str]:
    """Return Korean-first copy problems for executive-facing navigation and hero text."""
    language = str(spec.get("meta", {}).get("language", "")).casefold()
    if language != "ko" and not language.startswith("ko-"):
        return []

    problems: list[str] = []
    for index, route in enumerate(spec.get("navigation", [])):
        for field in ("name", "short", "crumb"):
            value = route.get(field)
            if not _is_korean_copy(value):
                problems.append(
                    f"navigation[{index}].{field} must use Korean-first executive copy "
                    f"(official product names and common acronyms are allowed): {value!r}"
                )

    for route_id in render_demo.ROUTE_IDS:
        hero = spec.get(route_id, {}).get("hero", {})
        for field in ("title", "subtitle"):
            value = hero.get(field)
            if not _is_korean_copy(value):
                problems.append(
                    f"{route_id}.hero.{field} must use Korean-first executive copy "
                    f"(official product names and common acronyms are allowed): {value!r}"
                )
    return problems


def _policy(spec: dict) -> dict:
    value = spec.get("meta", {}).get("languagePolicy")
    return {**DEFAULT_KOREAN_LANGUAGE_POLICY, **(value or {})}


def _path_key(path: str) -> str:
    match = re.search(r"\.([A-Za-z][A-Za-z0-9]*)$", path)
    return match.group(1) if match else ""


def _visible_copy_strings(value: object, path: str = "$"):
    if isinstance(value, str):
        if (
            _path_key(path) in EXECUTIVE_COPY_KEYS
            and not path.startswith(("$.meta.research", "$.design"))
        ):
            yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _visible_copy_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _visible_copy_strings(child, f"{path}[{index}]")


def _plain_text(value: str) -> str:
    return html_lib.unescape(re.sub(r"<[^>]+>", " ", value))


def _neutralize_terms(text: str, terms: list[str]) -> str:
    neutralized = text
    for term in sorted(terms, key=len, reverse=True):
        neutralized = re.sub(
            re.escape(term),
            " ",
            neutralized,
            flags=re.IGNORECASE,
        )
    return neutralized


def _language_counts(
    items: list[tuple[str, str]],
    protected_terms: list[str],
) -> dict:
    text = " ".join(_plain_text(value) for _, value in items)
    raw_latin = len(LATIN_RE.findall(text))
    raw_hangul = len(HANGUL_RE.findall(text))
    raw_total = raw_latin + raw_hangul
    neutralized = _neutralize_terms(text, protected_terms)
    latin = len(LATIN_RE.findall(neutralized))
    hangul = len(HANGUL_RE.findall(neutralized))
    total = latin + hangul
    return {
        "rawLatinCharacters": raw_latin,
        "rawHangulCharacters": raw_hangul,
        "rawLatinRatio": raw_latin / raw_total if raw_total else 0.0,
        "latinCharacters": latin,
        "hangulCharacters": hangul,
        "analyzedCharacters": total,
        "latinRatio": latin / total if total else 0.0,
    }


def language_balance_report(spec: dict) -> dict | None:
    language = str(spec.get("meta", {}).get("language", "")).casefold()
    if language != "ko" and not language.startswith("ko-"):
        return None
    policy = _policy(spec)
    all_items = list(_visible_copy_strings(spec))
    overall = _language_counts(all_items, policy["protectedTerms"])
    routes = []
    allowed = set(policy["allowHighLatinRoutes"])
    for route_id in render_demo.ROUTE_IDS:
        route_items = list(
            _visible_copy_strings(spec.get(route_id, {}), f"$.{route_id}")
        )
        route_counts = _language_counts(route_items, policy["protectedTerms"])
        routes.append(
            {
                "route": route_id,
                **route_counts,
                "rawLatinRatio": round(route_counts["rawLatinRatio"], 4),
                "latinRatio": round(route_counts["latinRatio"], 4),
                "allowed": route_id in allowed,
            }
        )
    folded = " ".join(
        value
        for path, value in render_demo.iter_strings(spec)
        if not path.startswith("$.meta.languagePolicy")
    ).casefold()
    missing_terms = [
        term
        for term in policy["protectedTerms"]
        if term.casefold() not in folded
    ]
    return {
        "targetLatinRatio": policy["targetLatinRatio"],
        "maxLatinRatio": policy["maxLatinRatio"],
        "maxRouteLatinRatio": policy["maxRouteLatinRatio"],
        "minAnalyzedCharacters": policy["minAnalyzedCharacters"],
        "overall": {
            **overall,
            "rawLatinRatio": round(overall["rawLatinRatio"], 4),
            "latinRatio": round(overall["latinRatio"], 4),
        },
        "routes": routes,
        "missingProtectedTerms": missing_terms,
    }


def language_balance_invariants(spec: dict) -> list[str]:
    report = language_balance_report(spec)
    if report is None:
        return []
    problems: list[str] = []
    overall = report["overall"]
    if (
        overall["analyzedCharacters"] >= report["minAnalyzedCharacters"]
        and overall["latinRatio"] > report["maxLatinRatio"]
    ):
        problems.append(
            "Korean-first executive copy Latin-character ratio is too high: "
            "(protected official terms excluded) "
            f"{overall['latinRatio']:.1%} > {report['maxLatinRatio']:.1%} "
            f"(target {report['targetLatinRatio']:.1%})"
        )
    high_routes = [
        route["route"]
        for route in report["routes"]
        if route["analyzedCharacters"] >= report["minAnalyzedCharacters"]
        and route["latinRatio"] > report["maxRouteLatinRatio"]
        and not route["allowed"]
    ]
    if high_routes:
        problems.append(
            "Korean-first executive copy is too English-heavy on route(s): "
            + ", ".join(high_routes)
        )
    if report["missingProtectedTerms"]:
        problems.append(
            "Protected official service/feature term(s) are missing: "
            + ", ".join(report["missingProtectedTerms"])
        )
    return problems


def qa_invariants(spec: dict) -> list[str]:
    """Return a list of QA-invariant problems (empty means all satisfied)."""
    problems: list[str] = []

    ops = spec.get("operations", {}).get("action", {})
    if ops.get("recommendationBefore") == ops.get("recommendationAfter"):
        problems.append(
            "operations.action.recommendationBefore equals recommendationAfter: the re-optimize "
            "action will not visibly change the recommendation."
        )

    orchestration = spec.get("foundry", {}).get("orchestration", {})
    if not ORCH_SUMMARY_RE.search(str(orchestration.get("summary", ""))):
        problems.append(
            "foundry.orchestration.summary must contain '의사결정 패키지' (or 'decision package'): "
            "browser QA checks the chat log for that phrase after orchestration runs."
        )

    app_platform = spec.get("appPlatform", {})
    cards = app_platform.get("cards", [])
    final_score = app_platform.get("evaluation", {}).get("finalScore")
    if cards and final_score is not None:
        try:
            visible_score = float(cards[0].get("value"))
            final_numeric = float(final_score)
        except (TypeError, ValueError):
            pass
        else:
            if (
                math.isfinite(visible_score)
                and math.isfinite(final_numeric)
                and math.isclose(visible_score, final_numeric, rel_tol=0, abs_tol=1e-9)
            ):
                problems.append(
                    "appPlatform.cards[0].value equals evaluation.finalScore: the projected "
                    "remediation score will not visibly differ from the assessed score."
                )
    gaps = app_platform.get("evaluation", {}).get("gaps", [])
    if gaps and not any(
        gap.get("status", {}).get("tone") in {"warning", "danger", "warn", "bad"}
        for gap in gaps
    ):
        problems.append(
            "appPlatform.evaluation.gaps must include at least one unresolved gap: "
            "assessment should discover work instead of presenting an all-pass result."
        )

    output = spec.get("simulator", {}).get("output", {})
    good = output.get("goodThreshold")
    warn = output.get("warningThreshold")
    if isinstance(good, (int, float)) and isinstance(warn, (int, float)) and not good > warn:
        problems.append(
            "simulator.output.goodThreshold must be greater than warningThreshold: the runtime "
            "treats a HIGH output as good/green, so frame the output as a positive score."
        )

    problems.extend(korean_copy_invariants(spec))
    problems.extend(language_balance_invariants(spec))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="Fast pre-QA lint for a demo-spec.json.")
    parser.add_argument("spec", type=Path, help="Path to demo-spec.json")
    args = parser.parse_args()

    try:
        with args.spec.open(encoding="utf-8") as stream:
            spec = json.load(stream, parse_constant=_reject_constant)
    except (OSError, ValueError, render_demo.SpecError) as error:
        print(f"[lint] cannot read spec: {error}")
        return 2
    if not isinstance(spec, dict):
        print("[lint] top-level JSON must be an object")
        return 2

    # 1) Full structural / semantic / security validation (same as render_demo --validate-only).
    try:
        spec = render_demo.sanitize_rich_fields(spec)
        render_demo.validate_spec(spec)
    except render_demo.SpecError as error:
        print(f"[lint] STRUCTURE: {error}")
        return 1

    # 2) Interaction / timing invariants enforced by the browser QA.
    problems = qa_invariants(spec)
    if problems:
        print("[lint] QA-invariant problems:")
        for item in problems:
            print(f"  - {item}")
        return 1

    balance = language_balance_report(spec)
    suffix = ""
    if balance is not None:
        suffix = (
            " | executive-copy Latin ratio="
            f"{balance['overall']['latinRatio']:.1%} "
            f"(target {balance['targetLatinRatio']:.1%}, "
            f"raw {balance['overall']['rawLatinRatio']:.1%})"
        )
    print("[lint] OK — structure valid and QA invariants satisfied." + suffix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
