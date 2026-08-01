from __future__ import annotations

import copy
import contextlib
import datetime as dt
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import validate_fact_ledger as validator  # noqa: E402


NOW = dt.datetime(2026, 8, 1, 8, 0, tzinfo=dt.timezone.utc)


class FactLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = json.loads(
            (SKILL_ROOT / "examples" / "fact-ledger.example.json").read_text(
                encoding="utf-8"
            )
        )

    def test_example_validates_and_preserves_type_specific_entries(self):
        normalized = validator.validate_ledger(
            copy.deepcopy(self.example),
            now=NOW,
        )

        entries = {entry["id"]: entry for entry in normalized["facts"]}
        self.assertEqual(entries["F-001"]["sources"][0]["publisher"], "Microsoft")
        self.assertEqual(entries["I-001"]["basisIds"], ["F-001", "F-002"])
        self.assertNotIn("sources", entries["A-001"])
        self.assertEqual(entries["A-001"]["status"], "Unresolved")

    def test_legacy_single_source_is_normalized(self):
        ledger = {
            "schemaVersion": 1,
            "checkedAt": "2026-08-01T16:00:00+09:00",
            "facts": [
                {
                    "id": "F-001",
                    "type": "Fact",
                    "claim": "Claim",
                    "evidence": "Evidence",
                    "source": {
                        "title": "Document",
                        "url": "https://example.com/doc",
                    },
                    "publisher": "Example",
                    "publishedOrUpdated": "2026-07-31",
                    "accessed": "2026-08-01",
                    "scopeOrStatus": "Global",
                    "confidence": "High",
                }
            ],
        }

        normalized = validator.validate_ledger(ledger, now=NOW)

        self.assertEqual(
            normalized["facts"][0]["sources"][0]["url"],
            "https://example.com/doc",
        )
        self.assertNotIn("source", normalized["facts"][0])

    def test_duplicate_ids_and_missing_basis_are_rejected(self):
        duplicate = copy.deepcopy(self.example)
        duplicate["facts"][1]["id"] = "F-001"
        with self.assertRaisesRegex(validator.LedgerValidationError, "duplicated"):
            validator.validate_ledger(duplicate, now=NOW)

        missing_basis = copy.deepcopy(self.example)
        missing_basis["facts"][2]["basisIds"] = ["F-404"]
        with self.assertRaisesRegex(validator.LedgerValidationError, "missing ID"):
            validator.validate_ledger(missing_basis, now=NOW)

    def test_nonaccepted_status_requires_rationale(self):
        ledger = copy.deepcopy(self.example)
        del ledger["facts"][3]["decisionRationale"]
        with self.assertRaisesRegex(
            validator.LedgerValidationError,
            "decisionRationale",
        ):
            validator.validate_ledger(ledger, now=NOW)

        invalid_optional = copy.deepcopy(self.example)
        invalid_optional["facts"][0]["decisionRationale"] = 123
        with self.assertRaisesRegex(
            validator.LedgerValidationError,
            "decisionRationale",
        ):
            validator.validate_ledger(invalid_optional, now=NOW)

        invalid_status = copy.deepcopy(self.example)
        invalid_status["facts"][0]["status"] = []
        with self.assertRaisesRegex(validator.LedgerValidationError, "status"):
            validator.validate_ledger(invalid_status, now=NOW)

    def test_basis_cycles_and_nonaccepted_basis_are_rejected(self):
        cycle = copy.deepcopy(self.example)
        cycle["facts"][2]["basisIds"] = ["I-002"]
        cycle["facts"].insert(
            3,
            {
                "id": "I-002",
                "type": "Inference",
                "claim": "Cyclic inference",
                "evidence": "Cycle",
                "basisIds": ["I-001"],
                "scopeOrStatus": "Test",
                "confidence": "Low",
                "status": "Accepted",
            },
        )
        with self.assertRaisesRegex(validator.LedgerValidationError, "cycle"):
            validator.validate_ledger(cycle, now=NOW)

        rejected_basis = copy.deepcopy(self.example)
        rejected_basis["facts"][0]["status"] = "Rejected"
        rejected_basis["facts"][0]["decisionRationale"] = "Source was superseded."
        with self.assertRaisesRegex(
            validator.LedgerValidationError,
            "requires Accepted basis",
        ):
            validator.validate_ledger(rejected_basis, now=NOW)

    def test_new_and_legacy_provenance_cannot_be_mixed(self):
        ledger = copy.deepcopy(self.example)
        ledger["facts"][0]["source"] = {
            "title": "Duplicate",
            "url": "https://example.com/duplicate",
        }
        ledger["facts"][0]["publisher"] = "Example"
        ledger["facts"][0]["publishedOrUpdated"] = "확인 불가"
        ledger["facts"][0]["accessed"] = "2026-08-01"
        with self.assertRaisesRegex(validator.LedgerValidationError, "must not combine"):
            validator.validate_ledger(ledger, now=NOW)

    def test_private_urls_and_future_timestamps_are_rejected(self):
        private = copy.deepcopy(self.example)
        private["facts"][0]["sources"][0]["url"] = "http://127.0.0.1/source"
        with self.assertRaisesRegex(validator.LedgerValidationError, "private"):
            validator.validate_ledger(private, now=NOW)

        for encoded_loopback in ("http://127.1/source", "http://2130706433/source"):
            encoded = copy.deepcopy(self.example)
            encoded["facts"][0]["sources"][0]["url"] = encoded_loopback
            with self.subTest(url=encoded_loopback):
                with self.assertRaisesRegex(
                    validator.LedgerValidationError,
                    "numeric host",
                ):
                    validator.validate_ledger(encoded, now=NOW)

        future = copy.deepcopy(self.example)
        future["checkedAt"] = "2027-01-01T00:00:00Z"
        with self.assertRaisesRegex(validator.LedgerValidationError, "future"):
            validator.validate_ledger(future, now=NOW)

    def test_cli_reports_valid_ledger(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fact-ledger.json"
            path.write_text(json.dumps(self.example), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(validator.main([str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
