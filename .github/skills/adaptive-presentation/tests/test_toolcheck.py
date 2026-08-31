from __future__ import annotations

import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import toolcheck  # noqa: E402
import tooling  # noqa: E402


class ToolcheckTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parent / ".test-work"
        self.work_dir = root / self._testMethodName
        shutil.rmtree(self.work_dir, ignore_errors=True)
        self.work_dir.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.work_dir, True)

    def test_invalid_cache_is_ignored(self):
        cache = self.work_dir / "cache.json"
        cache.write_text("{broken", encoding="utf-8")
        self.assertIsNone(toolcheck.read_cache(cache))

    def test_strict_requirements_include_pillow(self):
        info = {
            "soffice": "/bin/soffice",
            "has_fitz": True,
            "has_PIL": False,
            "has_pptx": True,
        }
        self.assertEqual(toolcheck.missing_required(info), ["Pillow (PIL)"])

    def test_korean_font_can_be_required(self):
        info = {
            "soffice": "/bin/soffice",
            "has_fitz": True,
            "has_PIL": True,
            "has_pptx": True,
            "korean_fonts": [],
        }
        self.assertEqual(
            toolcheck.missing_required(info, require_korean_font=True),
            ["Korean font"],
        )

    def test_cache_is_bound_to_current_runtime(self):
        info = toolcheck.runtime_signature()
        self.assertTrue(toolcheck.cache_matches_runtime(info))
        changed = dict(info, python_executable="/different/python")
        self.assertFalse(toolcheck.cache_matches_runtime(changed))

    def test_path_containment_is_case_normalized(self):
        self.assertTrue(
            tooling.path_is_within(
                Path("/users/example/QA/deck.pptx"),
                Path("/Users/Example/qa"),
            )
        )

    def test_language_aware_font_resolution_is_deterministic(self):
        available = [
            "Arial",
            "Noto Sans KR",
            "Apple SD Gothic Neo",
            "Liberation Sans",
        ]
        self.assertEqual(
            toolcheck.select_font(available, language="ko-KR"),
            "Apple SD Gothic Neo",
        )
        self.assertEqual(
            toolcheck.select_font(reversed(available), language="ko-KR"),
            "Apple SD Gothic Neo",
        )
        self.assertEqual(
            toolcheck.select_font(available, language="en-US"),
            "Arial",
        )
        self.assertEqual(
            toolcheck.select_font(
                available,
                preferred=["Missing Font"],
                fallbacks=["liberation sans"],
                language="ko",
            ),
            "Liberation Sans",
        )

    def test_font_probe_surfaces_timeout_warning(self):
        with (
            patch.object(toolcheck.shutil, "which", return_value="/usr/bin/fc-list"),
            patch.object(
                toolcheck.subprocess,
                "run",
                side_effect=subprocess.TimeoutExpired("fc-list", 25),
            ),
            patch.object(toolcheck, "_font_directories", return_value=[]),
        ):
            info = toolcheck.enumerate_fonts()

        self.assertEqual(info["fonts"], [])
        self.assertTrue(
            any("fc-list probe failed" in warning for warning in info["warnings"])
        )

    def test_windows_font_directories_and_common_filenames(self):
        with (
            patch.object(toolcheck.sys, "platform", "win32"),
            patch.dict(
                os.environ,
                {
                    "WINDIR": r"C:\Windows",
                    "LOCALAPPDATA": r"C:\Users\Example\AppData\Local",
                },
                clear=False,
            ),
        ):
            directories = toolcheck._font_directories()

        self.assertIn(Path(r"C:\Windows") / "Fonts", directories)
        self.assertEqual(
            toolcheck._font_family_from_filename(Path("malgunbd.ttf")),
            "Malgun Gothic",
        )
        self.assertEqual(
            toolcheck._font_family_from_filename(Path("NotoSansKR-Regular.otf")),
            "Noto Sans KR",
        )

    def test_windows_registry_fonts_are_included(self):
        with (
            patch.object(toolcheck.shutil, "which", return_value=None),
            patch.object(toolcheck, "_font_directories", return_value=[]),
            patch.object(
                toolcheck,
                "_font_names_from_windows_registry",
                return_value=({"Segoe UI", "Aptos"}, []),
            ),
        ):
            info = toolcheck.enumerate_fonts()

        self.assertEqual(info["fonts"], ["Aptos", "Segoe UI"])
        self.assertIn("Windows font registry", info["sources"])


if __name__ == "__main__":
    unittest.main()
