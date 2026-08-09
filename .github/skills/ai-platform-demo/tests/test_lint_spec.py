from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
BASE = SKILL_ROOT / "examples" / "precision-manufacturing.example.json"


def run_lint(spec_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / "lint_spec.py"), str(spec_path)],
        capture_output=True,
        text=True,
    )


def write_temp(spec: dict, directory: str) -> Path:
    path = Path(directory) / "spec.json"
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


class LintSpecTests(unittest.TestCase):
    def test_base_example_passes(self):
        result = run_lint(BASE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_qa_invariant_violations_are_caught(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        spec["operations"]["action"]["recommendationAfter"] = spec["operations"]["action"]["recommendationBefore"]
        spec["foundry"]["orchestration"]["summary"] = "자율 대응을 완료했습니다."
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("recommendationBefore", result.stdout)
        self.assertIn("의사결정 패키지", result.stdout)

    def test_numeric_noop_app_platform_score_is_caught(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        spec["appPlatform"]["evaluation"]["initialScore"] = 90.0
        spec["appPlatform"]["evaluation"]["finalScore"] = 90
        spec["appPlatform"]["cards"][0]["value"] = "90.0"
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("finalScore", result.stdout)

    def test_all_pass_app_platform_assessment_is_caught(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        for gap in spec["appPlatform"]["evaluation"]["gaps"]:
            gap["status"]["tone"] = "success"
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("unresolved gap", result.stdout)

    def test_english_only_korean_navigation_is_caught(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        spec["navigation"][0].update(
            name="Executive Cockpit",
            short="Overview",
            crumb="Global Overview",
        )
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Korean-first executive copy", result.stdout)
        self.assertIn("navigation[0].name", result.stdout)

    def test_korean_language_balance_policy_is_enforced(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        spec["meta"]["languagePolicy"]["targetLatinRatio"] = 0.05
        spec["meta"]["languagePolicy"]["maxLatinRatio"] = 0.10
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Latin-character ratio", result.stdout)

    def test_missing_protected_official_term_is_caught(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        spec["meta"]["languagePolicy"]["protectedTerms"].append(
            "Nonexistent Official Feature"
        )
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Protected official service/feature", result.stdout)

    def test_structural_error_is_caught(self):
        spec = json.loads(BASE.read_text(encoding="utf-8"))
        spec["navigation"] = spec["navigation"][:7]  # break the runtime data contract
        with tempfile.TemporaryDirectory() as directory:
            result = run_lint(write_temp(spec, directory))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("STRUCTURE", result.stdout)


if __name__ == "__main__":
    unittest.main()
