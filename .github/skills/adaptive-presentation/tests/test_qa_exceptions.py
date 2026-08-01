from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import qa_exceptions  # noqa: E402


class QaExceptionTests(unittest.TestCase):
    def test_finding_ids_are_stable_and_ignore_runtime_annotations(self):
        finding = {"slide": 2, "shape": "Chart 1", "allowed": False}
        first = qa_exceptions.finding_id("unsupported_text_object", finding)
        finding["findingId"] = first
        finding["exceptionReason"] = "Reviewed in the rendered slide."
        self.assertEqual(
            first,
            qa_exceptions.finding_id("unsupported_text_object", finding),
        )

    def test_manifest_requires_rationale_and_rejects_stale_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "exceptions.json"
            path.write_text(
                json.dumps(
                    {
                        "schemaVersion": 1,
                        "exceptions": [
                            {
                                "findingId": "rendered_overflow:abc",
                                "reason": "Reviewed at full-slide scale and accepted.",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            manifest = qa_exceptions.load_exception_manifest(path)
            with self.assertRaises(qa_exceptions.ExceptionManifestError):
                qa_exceptions.reject_stale_exceptions(manifest, set())

    def test_apply_reasons_is_finding_scoped(self):
        findings = [
            {"findingId": "a", "allowed": False},
            {"findingId": "b", "allowed": False},
        ]
        manifest = qa_exceptions.ExceptionManifest(
            Path("exceptions.json"),
            {"a": "Reviewed finding A at full-slide scale."},
        )
        used = qa_exceptions.apply_reasons(findings, manifest)
        self.assertEqual(used, {"a"})
        self.assertTrue(findings[0]["allowed"])
        self.assertFalse(findings[1]["allowed"])


if __name__ == "__main__":
    unittest.main()
