from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from render_pptx import sha256_file  # noqa: E402
from visual_review import (  # noqa: E402
    VisualReviewError,
    load_visual_review,
    write_visual_review,
)


class VisualReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work = Path(self.temp_dir.name)
        self.deck = self.work / "deck.pptx"
        self.deck.write_bytes(b"deck revision")

    def write_review(self, **overrides) -> Path:
        value = {
            "schemaVersion": 1,
            "deckSha256": sha256_file(self.deck),
            "reviewer": "Copilot",
            "reviewedSlides": "all",
            "notes": "Reviewed the contact sheet and risk slides.",
        }
        value.update(overrides)
        path = self.work / "visual-review.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_review_is_bound_to_deck_revision_and_all_slides(self):
        review = load_visual_review(
            self.write_review(), self.deck, slide_count=3
        )
        self.assertEqual(review.reviewed_slides, {1, 2, 3})

        self.deck.write_bytes(b"changed")
        with self.assertRaises(VisualReviewError):
            load_visual_review(
                self.work / "visual-review.json", self.deck, slide_count=3
            )

    def test_partial_review_does_not_satisfy_completion(self):
        with self.assertRaisesRegex(VisualReviewError, "every slide"):
            load_visual_review(
                self.write_review(reviewedSlides=[1, 2]),
                self.deck,
                slide_count=3,
            )

    def test_writer_creates_revision_bound_evidence_without_overwrite(self):
        output = self.work / "created-review.json"
        write_visual_review(
            self.deck,
            output,
            reviewer="Copilot",
            notes="Reviewed every slide through the contact sheet.",
        )
        review = load_visual_review(output, self.deck, slide_count=1)
        self.assertEqual(review.reviewer, "Copilot")
        with self.assertRaises(FileExistsError):
            write_visual_review(
                self.deck,
                output,
                reviewer="Copilot",
                notes="Reviewed every slide through the contact sheet.",
            )


if __name__ == "__main__":
    unittest.main()
