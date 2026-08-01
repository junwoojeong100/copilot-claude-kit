#!/usr/bin/env python3
"""Probe and cache the presentation toolchain, then reuse its stable inventory.

soffice(LibreOffice), PyMuPDF(fitz), Pillow, python-pptx, 그리고 폰트 인벤토리를 한 번 탐지해
${COPILOT_CACHE_DIR:-$HOME/.copilot/cache}/adaptive-presentation/{toolchain.json,fonts.txt}에
캐시한다. 캐시 hit에서도 실행 환경과 필수 도구는 빠르게 재확인하고, 비용이 큰 폰트 목록 탐색만
건너뛴다(--refresh로 강제 갱신).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Sequence

from tooling import resolve_soffice

FONT_PATTERNS = (
    r"Apple SD Gothic|Noto Sans CJK KR|Noto Sans KR|Malgun|맑은 고딕|"
    r"AppleGothic|Nanum(Gothic|Myeongjo)|나눔(고딕|명조)|"
    r"Source Han Sans K|Pretendard|Spoqa"
)
KOREAN_FONT_CANDIDATES = (
    "Noto Sans KR",
    "Noto Sans CJK KR",
    "Malgun Gothic",
    "Apple SD Gothic Neo",
    "Pretendard",
    "NanumGothic",
    "Source Han Sans K",
)
LATIN_FONT_CANDIDATES = (
    "Aptos",
    "Arial",
    "Noto Sans",
    "Liberation Sans",
    "DejaVu Sans",
    "Calibri",
)
FONT_FILE_FAMILIES = (
    ("applesdgothicneo", "Apple SD Gothic Neo"),
    ("notosanscjkkr", "Noto Sans CJK KR"),
    ("notosanskr", "Noto Sans KR"),
    ("sourcehansansk", "Source Han Sans K"),
    ("nanumgothic", "NanumGothic"),
    ("nanummyeongjo", "NanumMyeongjo"),
    ("pretendard", "Pretendard"),
    ("malgun", "Malgun Gothic"),
    ("aptos", "Aptos"),
    ("liberationsans", "Liberation Sans"),
    ("dejavusans", "DejaVu Sans"),
    ("calibri", "Calibri"),
    ("arial", "Arial"),
)
FONT_EXTENSIONS = {".otf", ".ttf", ".ttc", ".otc"}
CACHE_VERSION = 3
MODULES = ("fitz", "PIL", "pptx")


def cache_dir(override: str | None = None) -> Path:
    if override:
        return Path(override).expanduser()
    base = os.environ.get("COPILOT_CACHE_DIR") or str(Path.home() / ".copilot" / "cache")
    return Path(base) / "adaptive-presentation"


def runtime_signature() -> dict:
    info = {
        "cache_version": CACHE_VERSION,
        "python": sys.version.split()[0],
        "python_executable": str(Path(sys.executable).resolve()),
        "path_env": os.environ.get("PATH", ""),
        "soffice": resolve_soffice(),
    }
    warnings: list[str] = []
    for mod in MODULES:
        try:
            __import__(mod)
            info[f"has_{mod}"] = True
        except ImportError:
            info[f"has_{mod}"] = False
        except Exception as exc:
            info[f"has_{mod}"] = False
            warnings.append(
                f"module probe failed for {mod}: {type(exc).__name__}: {exc}"
            )
    info["runtime_probe_warnings"] = warnings
    return info


def _normalize_font_name(value: str) -> str:
    return " ".join(value.split()).casefold()


def _as_font_list(values: Sequence[str] | str | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        return [values]
    return [str(value) for value in values]


def _is_korean_language(language: str | None) -> bool:
    if not language:
        return False
    normalized = language.strip().replace("_", "-").casefold()
    return normalized == "ko" or normalized.startswith("ko-") or "korean" in normalized


def select_font(
    available_fonts: Iterable[str],
    preferred: Sequence[str] | str | None = None,
    fallbacks: Sequence[str] | str | None = None,
    language: str | None = None,
) -> str | None:
    """Select an installed font deterministically, honoring caller preferences."""
    installed: dict[str, str] = {}
    for value in sorted(
        {str(font).strip() for font in available_fonts if str(font).strip()},
        key=lambda item: (item.casefold(), item),
    ):
        installed.setdefault(_normalize_font_name(value), value)

    language_defaults = (
        KOREAN_FONT_CANDIDATES
        if _is_korean_language(language)
        else LATIN_FONT_CANDIDATES
    )
    candidates = (
        _as_font_list(preferred)
        + _as_font_list(fallbacks)
        + list(language_defaults)
    )
    seen: set[str] = set()
    for candidate in candidates:
        normalized = _normalize_font_name(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        if normalized in installed:
            return installed[normalized]
    return next(iter(installed.values()), None)


def _font_directories() -> list[Path]:
    if sys.platform == "win32":
        directories = []
        windir = os.environ.get("WINDIR")
        local_app_data = os.environ.get("LOCALAPPDATA")
        if windir:
            directories.append(Path(windir) / "Fonts")
        if local_app_data:
            directories.append(Path(local_app_data) / "Microsoft" / "Windows" / "Fonts")
        return directories
    if sys.platform == "darwin":
        return [
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path.home() / "Library" / "Fonts",
        ]
    return []


def _font_family_from_filename(path: Path) -> str | None:
    normalized = re.sub(r"[^a-z0-9]", "", path.stem.casefold())
    for prefix, family in FONT_FILE_FAMILIES:
        if normalized.startswith(prefix):
            return family
    return None


def _font_names_from_fc_list(output: str) -> set[str]:
    names: set[str] = set()
    for line in output.splitlines():
        value = line.strip()
        if not value:
            continue
        if ":" in value:
            fields = value.split(":")
            value = fields[1].strip() if len(fields) > 1 else value
        value = value.split("=", 1)[-1] if value.startswith("family=") else value
        for name in value.split(","):
            name = name.strip()
            if name:
                names.add(name)
    return names


def _font_names_from_windows_registry() -> tuple[set[str], list[str]]:
    if sys.platform != "win32":
        return set(), []
    try:
        import winreg
    except ImportError as exc:
        return set(), [f"Windows font registry probe failed: {exc}"]

    names: set[str] = set()
    warnings: list[str] = []
    registry_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
    for hive_name, hive in (
        ("HKLM", winreg.HKEY_LOCAL_MACHINE),
        ("HKCU", winreg.HKEY_CURRENT_USER),
    ):
        try:
            with winreg.OpenKey(hive, registry_path) as key:
                index = 0
                while True:
                    try:
                        display_name, _, _ = winreg.EnumValue(key, index)
                    except OSError:
                        break
                    index += 1
                    family = re.sub(r"\s+\([^)]*\)\s*$", "", display_name).strip()
                    if family:
                        names.add(family)
        except OSError as exc:
            warnings.append(f"Windows font registry probe failed for {hive_name}: {exc}")
    return names, warnings


def enumerate_fonts() -> dict:
    """Return sorted font names plus non-fatal probe warnings and sources."""
    fonts: set[str] = set()
    warnings: list[str] = []
    sources: list[str] = []

    fc = shutil.which("fc-list")
    if fc:
        try:
            result = subprocess.run(
                [fc, ":", "family"],
                capture_output=True,
                text=True,
                errors="replace",
                timeout=25,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            warnings.append(f"fc-list probe failed: {exc}")
        else:
            if result.returncode == 0:
                fonts.update(_font_names_from_fc_list(result.stdout))
                sources.append("fc-list")
            else:
                detail = result.stderr.strip() or f"exit status {result.returncode}"
                warnings.append(f"fc-list probe failed: {detail}")

    registry_fonts, registry_warnings = _font_names_from_windows_registry()
    if registry_fonts:
        fonts.update(registry_fonts)
        sources.append("Windows font registry")
    warnings.extend(registry_warnings)

    for directory in _font_directories():
        if not directory.is_dir():
            continue
        try:
            for path in directory.rglob("*"):
                if path.suffix.casefold() not in FONT_EXTENSIONS:
                    continue
                family = _font_family_from_filename(path)
                if family:
                    fonts.add(family)
        except OSError as exc:
            warnings.append(f"font directory probe failed for {directory}: {exc}")
        else:
            sources.append(str(directory))

    if not sources:
        warnings.append("No supported font enumeration source was available")
    if not fonts:
        warnings.append("No font names were discovered")
    return {
        "fonts": sorted(fonts, key=lambda item: (item.casefold(), item)),
        "warnings": warnings,
        "sources": sources,
    }


def probe() -> dict:
    info = runtime_signature()
    info["checked_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")

    font_info = enumerate_fonts()
    fonts = font_info["fonts"]
    info["font_names"] = fonts
    info["korean_fonts"] = [
        name for name in fonts if re.search(FONT_PATTERNS, name, re.I)
    ]
    info["selected_fonts"] = {
        "ko": select_font(fonts, language="ko"),
        "latin": select_font(fonts, language="en"),
    }
    info["font_probe_sources"] = font_info["sources"]
    info["probe_warnings"] = (
        info.get("runtime_probe_warnings", []) + font_info["warnings"]
    )
    return info


def is_fresh(path: Path, max_age_days: float) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < max_age_days * 86400


def read_cache(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def cache_matches_runtime(info: dict) -> bool:
    return all(
        info.get(key) == value
        for key, value in runtime_signature().items()
    )


def missing_required(info: dict, require_korean_font: bool = False) -> list[str]:
    checks = {
        "soffice": bool(info.get("soffice")),
        "PyMuPDF (fitz)": bool(info.get("has_fitz")),
        "Pillow (PIL)": bool(info.get("has_PIL")),
        "python-pptx": bool(info.get("has_pptx")),
    }
    missing = [name for name, available in checks.items() if not available]
    if require_korean_font and not info.get("korean_fonts"):
        missing.append("Korean font")
    return missing


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Probe/cache soffice, PyMuPDF, Pillow, python-pptx, and fonts."
    )
    ap.add_argument("--refresh", action="store_true", help="ignore cache and re-probe")
    ap.add_argument("--max-age-days", type=float, default=7.0)
    ap.add_argument("--cache-dir", help="override cache directory")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="nonzero exit if soffice, PyMuPDF, Pillow, or python-pptx is missing",
    )
    ap.add_argument(
        "--require-korean-font",
        action="store_true",
        help="with --strict, also fail when no Korean-capable font is found",
    )
    a = ap.parse_args()
    if not math.isfinite(a.max_age_days) or a.max_age_days < 0:
        ap.error("--max-age-days must be a finite non-negative number")

    cdir = cache_dir(a.cache_dir)
    cdir.mkdir(parents=True, exist_ok=True)
    tj, ft = cdir / "toolchain.json", cdir / "fonts.txt"

    cached = read_cache(tj) if not a.refresh and is_fresh(tj, a.max_age_days) else None
    if cached is not None and cache_matches_runtime(cached):
        info = cached
        if not ft.is_file():
            ft.write_text(
                "\n".join(info.get("font_names", info.get("korean_fonts", []))),
                encoding="utf-8",
            )
        hit = True
    else:
        info = probe()
        tj.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        ft.write_text(
            "\n".join(info.get("font_names", info.get("korean_fonts", []))),
            encoding="utf-8",
        )
        hit = False

    print(f"toolchain cache {'HIT' if hit else 'REFRESHED'}: {tj}")
    print(f"  soffice: {info.get('soffice') or 'MISSING'}")
    print(f"  PyMuPDF(fitz): {info.get('has_fitz')}  Pillow(PIL): {info.get('has_PIL')}  python-pptx: {info.get('has_pptx')}")
    print(f"  korean fonts: {', '.join(info.get('korean_fonts', [])) or 'NONE'}")
    selected = info.get("selected_fonts", {})
    print(f"  selected fonts: ko={selected.get('ko') or 'NONE'} latin={selected.get('latin') or 'NONE'}")
    for warning in info.get("probe_warnings", []):
        print(f"  warning: {warning}")

    missing = missing_required(info, a.require_korean_font)
    if missing:
        print(f"  missing required: {', '.join(missing)}")
    return 1 if (a.strict and missing) else 0


if __name__ == "__main__":
    sys.exit(main())
