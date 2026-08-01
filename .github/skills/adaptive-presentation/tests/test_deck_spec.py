from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import deck_spec  # noqa: E402


BASE = {
    "schemaVersion": 1,
    "request": {
        "topic": "AI 운영 전략",
        "audience": "CIO",
        "purpose": "의사결정",
        "language": "ko-KR",
        "slideCount": 2,
    },
    "canvas": {
        "source": "default",
        "widthIn": 13.333,
        "heightIn": 7.5,
    },
    "templateProfile": None,
    "factLedger": "fact-ledger.json",
    "fontPolicy": {
        "selected": "Noto Sans CJK KR",
        "fallbacks": ["Malgun Gothic"],
        "requireAvailable": True,
        "requireRenderedMatch": True,
    },
    "slides": [
        {
            "number": 1,
            "role": "cover",
            "title": "결론",
            "claimIds": [],
            "stateLabels": [],
        },
        {
            "number": 2,
            "role": "evidence",
            "title": "공식 근거",
            "claimIds": ["F-001"],
            "stateLabels": ["GA"],
        },
    ],
    "qa": {
        "strict": True,
        "minBodyPt": 15,
        "minTitlePt": 26,
        "maxUnmappedTextSpans": 0,
        "failRenderedOverflow": True,
        "requireVisualReview": True,
        "exceptionManifest": None,
    },
}


LEDGER = {
    "schemaVersion": 1,
    "checkedAt": "2026-08-01T10:00:00+09:00",
    "facts": [
        {
            "id": "F-001",
            "type": "Fact",
            "claim": "공식 사실",
            "evidence": "공식 문서",
            "source": {
                "title": "Official documentation",
                "url": "https://example.com/docs",
            },
            "publisher": "Example",
            "publishedOrUpdated": "2026-08-01",
            "accessed": "2026-08-01",
            "scopeOrStatus": "GA",
            "confidence": "High",
        }
    ],
}


class DeckSpecTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work = Path(self.temp_dir.name)
        (self.work / "fact-ledger.json").write_text(
            json.dumps(LEDGER), encoding="utf-8"
        )

    def write_spec(self, value: dict) -> Path:
        path = self.work / "deck-spec.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_valid_spec_derives_source_slides_and_claim_ids(self):
        context = deck_spec.load_deck_spec(self.write_spec(copy.deepcopy(BASE)))
        self.assertEqual(context.required_source_slides, {2})
        self.assertEqual(context.claim_ids_by_slide, {2: ["F-001"]})

    def test_slide_count_and_sequence_are_authoritative(self):
        value = copy.deepcopy(BASE)
        value["slides"][1]["number"] = 3
        with self.assertRaises(deck_spec.DeckSpecError):
            deck_spec.load_deck_spec(self.write_spec(value))

    def test_claim_ids_require_matching_fact_ledger_entries(self):
        value = copy.deepcopy(BASE)
        value["slides"][1]["claimIds"] = ["F-404"]
        with self.assertRaisesRegex(deck_spec.DeckSpecError, "missing"):
            deck_spec.load_deck_spec(self.write_spec(value))

    def test_slide_claim_ids_must_reference_fact_entries(self):
        ledger = copy.deepcopy(LEDGER)
        ledger["facts"].append(
            {
                "id": "I-001",
                "type": "Inference",
                "claim": "Derived conclusion",
                "evidence": "Derived from F-001",
                "basisIds": ["F-001"],
                "scopeOrStatus": "Decision",
                "confidence": "Medium",
                "status": "Accepted",
            }
        )
        (self.work / "fact-ledger.json").write_text(
            json.dumps(ledger), encoding="utf-8"
        )
        value = copy.deepcopy(BASE)
        value["slides"][1]["claimIds"] = ["I-001"]
        with self.assertRaisesRegex(deck_spec.DeckSpecError, "Fact entries"):
            deck_spec.load_deck_spec(self.write_spec(value))

    def test_slide_claim_ids_must_reference_accepted_facts(self):
        ledger = copy.deepcopy(LEDGER)
        ledger["facts"][0]["status"] = "Rejected"
        ledger["facts"][0]["decisionRationale"] = "Superseded source."
        (self.work / "fact-ledger.json").write_text(
            json.dumps(ledger), encoding="utf-8"
        )
        with self.assertRaisesRegex(deck_spec.DeckSpecError, "Accepted Fact"):
            deck_spec.load_deck_spec(self.write_spec(copy.deepcopy(BASE)))

    def test_fact_ledger_requires_complete_shared_contract(self):
        ledger = copy.deepcopy(LEDGER)
        del ledger["facts"][0]["claim"]
        (self.work / "fact-ledger.json").write_text(
            json.dumps(ledger), encoding="utf-8"
        )
        with self.assertRaisesRegex(deck_spec.DeckSpecError, "claim"):
            deck_spec.load_deck_spec(self.write_spec(copy.deepcopy(BASE)))

    def test_template_canvas_requires_matching_profile(self):
        profile = {
            "schemaVersion": 1,
            "widthIn": 10,
            "heightIn": 7.5,
        }
        (self.work / "template-profile.json").write_text(
            json.dumps(profile), encoding="utf-8"
        )
        value = copy.deepcopy(BASE)
        value["canvas"]["source"] = "template"
        value["templateProfile"] = "template-profile.json"
        with self.assertRaisesRegex(deck_spec.DeckSpecError, "dimensions"):
            deck_spec.load_deck_spec(self.write_spec(value))

    def test_nonfinite_or_boolean_numeric_fields_are_rejected(self):
        for invalid in (True, float("inf"), 0):
            value = copy.deepcopy(BASE)
            value["qa"]["minBodyPt"] = invalid
            with self.subTest(invalid=invalid):
                with self.assertRaises(deck_spec.DeckSpecError):
                    deck_spec.load_deck_spec(self.write_spec(value))

    def test_default_canvas_cannot_silently_accept_four_by_three(self):
        value = copy.deepcopy(BASE)
        value["canvas"].update(widthIn=10, heightIn=7.5)
        with self.assertRaisesRegex(deck_spec.DeckSpecError, "canonical"):
            deck_spec.load_deck_spec(self.write_spec(value))


if __name__ == "__main__":
    unittest.main()
