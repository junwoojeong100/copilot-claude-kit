from __future__ import annotations

import sys
import tempfile
import unittest
import json
from argparse import Namespace
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import render_pptx  # noqa: E402
import toolcheck  # noqa: E402
import tooling  # noqa: E402
from pptx import Presentation  # noqa: E402
from pptx.util import Inches, Pt  # noqa: E402
from verify_deck import (  # noqa: E402
    audit_namespace,
    build_parser,
    claim_footer_failures,
    font_matches,
    prepare_output_dirs,
    resolve_contract,
    select_risk_slides,
    state_label_failures,
    unexpected_fonts,
    verify,
)


class VerifyDeckTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.work_dir = Path(self.temp_dir.name)

    def test_risk_selection_prioritizes_structural_findings(self):
        report = {
            "text_chars_per_slide": {"values": [100, 500, 200, 300]},
            "small_text_body_candidates": [{"slide": 3}],
            "small_text_label_candidates": [{"slide": 4}],
            "title_risks": [],
            "group_shapes": [],
            "unexpected_out_of_bounds": [{"slide": 1}],
        }
        self.assertEqual(select_risk_slides(report, 3), [1, 3, 2])

    def test_zero_text_decks_do_not_divide_by_zero(self):
        report = {
            "text_chars_per_slide": {"values": [0, 0]},
            "small_text_body_candidates": [],
            "small_text_label_candidates": [],
            "title_risks": [],
            "group_shapes": [],
            "unexpected_out_of_bounds": [],
        }
        self.assertEqual(select_risk_slides(report, 2), [1, 2])

    def test_strict_mode_enables_typography_failures(self):
        args = Namespace(
            deck=self.work_dir / "deck.pptx",
            expected_slides=5,
            allow_bleed="",
            bounds_tolerance=0.02,
            min_body_pt=13.0,
            min_title_pt=26.0,
            title_size_tolerance_pt=0.5,
            footer_top=6.9,
            min_small_text_chars=10,
            fail_small_text=False,
            allow_small_text="",
            allow_overlap="",
            allow_title_size="",
            require_sources="1,3-4",
            fail_unsized_runs=False,
            fail_title_risks=False,
            fail_title_consistency=False,
            fail_overlaps=False,
            strict=True,
        )
        namespace = audit_namespace(args, self.work_dir / "audit.json")
        self.assertTrue(namespace.fail_small_text)
        self.assertTrue(namespace.fail_title_risks)
        self.assertTrue(namespace.fail_title_consistency)
        self.assertTrue(namespace.fail_unsized_runs)
        self.assertTrue(namespace.fail_overlaps)
        self.assertEqual(namespace.require_sources, {1, 3, 4})

        args.allow_small_text = "2"
        namespace = audit_namespace(args, self.work_dir / "audit.json")
        self.assertEqual(namespace.allow_small_text, {2})
        self.assertTrue(namespace.fail_small_text)

        args.allow_overlap = "3"
        namespace = audit_namespace(args, self.work_dir / "audit.json")
        self.assertEqual(namespace.allow_overlap, {3})

        args.allow_title_size = "4"
        namespace = audit_namespace(args, self.work_dir / "audit.json")
        self.assertEqual(namespace.allow_title_size, {4})

    def test_risk_selection_prioritizes_rendered_overlap(self):
        report = {
            "text_chars_per_slide": {"values": [100, 100, 100]},
            "rendered_text_overlaps": [{"slide": 3}],
            "overlap_candidates": [{"slide": 2}],
        }
        self.assertEqual(select_risk_slides(report, 3), [3, 2, 1])

    def test_runner_clears_stale_qa_artifacts(self):
        detail = self.work_dir / "qa-detail"
        render_pptx.claim_output_dir(detail)
        stale = detail / "slide-99.jpg"
        stale.write_text("stale", encoding="utf-8")
        qa_dir, detail_dir = prepare_output_dirs(self.work_dir)
        self.assertTrue(qa_dir.is_dir())
        self.assertTrue(detail_dir.is_dir())
        self.assertFalse(stale.exists())

    def test_runner_refuses_unowned_qa_directory(self):
        qa_dir = self.work_dir / "qa"
        qa_dir.mkdir()
        unrelated = qa_dir / "notes.txt"
        unrelated.write_text("keep", encoding="utf-8")
        with self.assertRaises(RuntimeError):
            prepare_output_dirs(self.work_dir)
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")

    def test_runner_does_not_delete_deck_inside_managed_qa_directory(self):
        out = self.work_dir / "verify"
        qa_dir = out / "qa"
        qa_dir.mkdir(parents=True)
        deck = qa_dir / "deck.pptx"
        deck.write_bytes(b"preserve")
        args = build_parser().parse_args([str(deck), "--out", str(out)])
        with self.assertRaises(ValueError):
            verify(args)
        self.assertEqual(deck.read_bytes(), b"preserve")

    def test_runner_report_cannot_alias_input_deck(self):
        out = self.work_dir / "verify"
        out.mkdir()
        deck = self.work_dir / "deck.pptx"
        deck.write_bytes(b"preserve")
        (out / "verification-report.json").hardlink_to(deck)
        args = build_parser().parse_args([str(deck), "--out", str(out)])
        with self.assertRaises(ValueError):
            verify(args)
        self.assertEqual(deck.read_bytes(), b"preserve")

    def test_font_matching_tolerates_pdf_style_suffixes(self):
        self.assertTrue(
            font_matches(
                "Apple SD Gothic Neo",
                ["ABCDEE+AppleSDGothicNeo-Regular"],
            )
        )
        self.assertFalse(font_matches("Malgun Gothic", ["Aptos-Regular"]))
        self.assertFalse(font_matches("Arial", ["ABCDEF+ArialNarrow-Regular"]))
        self.assertTrue(font_matches("Arial", ["ABCDEF+Arial-BoldItalic"]))
        self.assertEqual(
            unexpected_fonts(
                ["Arial", "Malgun Gothic"],
                ["Arial-Bold", "Aptos", "Malgun Gothic"],
            ),
            ["Aptos"],
        )

    def test_claim_footer_requires_fact_ledger_ids(self):
        class Context:
            claim_ids_by_slide = {2: ["F-001", "F-002"]}

        failures, gaps = claim_footer_failures(
            {
                "footer_source_texts_by_slide": {
                    "2": ["Source: [F-001] Microsoft · Documentation"]
                }
            },
            Context(),
        )
        self.assertEqual(gaps, {"2": ["F-002"]})
        self.assertIn("F-002", failures[0])

    def test_without_deck_spec_defaults_remain_backward_compatible(self):
        args = build_parser().parse_args(
            ["deck.pptx", "--out", str(self.work_dir)]
        )
        self.assertIsNone(resolve_contract(args))
        self.assertEqual(args.min_body_pt, 13)
        self.assertEqual(args.min_title_pt, 26)
        self.assertIsNone(args.max_unmapped_text_spans)
        self.assertEqual(args.footer_top, 6.9)

    def test_state_labels_require_standalone_tokens(self):
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        shape = slide.shapes.add_textbox(
            Inches(1), Inches(1), Inches(4), Inches(1)
        )
        shape.text = "MEGA platform · PARTIAL GA"
        deck = self.work_dir / "state-label.pptx"
        prs.save(deck)

        class Context:
            spec = {
                "slides": [
                    {
                        "number": 1,
                        "stateLabels": ["GA"],
                    }
                ]
            }

        self.assertTrue(state_label_failures(deck, Context()))

    def test_runner_protects_visual_review_inside_managed_qa(self):
        out = self.work_dir / "verify"
        qa = out / "qa"
        qa.mkdir(parents=True)
        evidence = qa / "visual-review.json"
        evidence.write_text("{}", encoding="utf-8")
        deck = self.work_dir / "deck.pptx"
        deck.write_bytes(b"preserve")
        args = build_parser().parse_args(
            [
                str(deck),
                "--out",
                str(out),
                "--require-visual-review",
                "--visual-review",
                str(evidence),
            ]
        )
        with self.assertRaisesRegex(ValueError, "managed QA"):
            verify(args)
        self.assertTrue(evidence.exists())

    @unittest.skipUnless(
        tooling.resolve_soffice(),
        "LibreOffice is required for verifier integration",
    )
    def test_deck_spec_drives_end_to_end_verification(self):
        font = toolcheck.select_font(
            toolcheck.enumerate_fonts()["fonts"],
            language="en-US",
        )
        self.assertIsNotNone(font)
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        for text, top, height, size in (
            ("Decision title", 0.6, 0.8, 30),
            ("This body sentence provides enough evidence for the decision.", 2, 0.8, 15),
            ("GA", 5.8, 0.3, 11),
            ("Source: [F-001] Example · Official documentation", 6.95, 0.2, 8),
        ):
            shape = slide.shapes.add_textbox(
                Inches(0.8), Inches(top), Inches(11.5), Inches(height)
            )
            run = shape.text_frame.paragraphs[0].add_run()
            run.text = text
            run.font.size = Pt(size)
            run.font.name = font
        deck = self.work_dir / "contract-deck.pptx"
        prs.save(deck)

        ledger = {
            "schemaVersion": 1,
            "checkedAt": "2026-08-01T10:00:00+09:00",
            "facts": [
                {
                    "id": "F-001",
                    "type": "Fact",
                    "claim": "Official fact",
                    "evidence": "Official documentation",
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
        (self.work_dir / "fact-ledger.json").write_text(
            json.dumps(ledger), encoding="utf-8"
        )
        spec = {
            "schemaVersion": 1,
            "request": {
                "topic": "Decision",
                "audience": "Executive",
                "purpose": "Decision",
                "language": "en-US",
                "slideCount": 1,
            },
            "canvas": {
                "source": "default",
                "widthIn": 13.333,
                "heightIn": 7.5,
            },
            "templateProfile": None,
            "factLedger": "fact-ledger.json",
            "fontPolicy": {
                "selected": font,
                "fallbacks": [],
                "requireAvailable": True,
                "requireRenderedMatch": True,
            },
            "slides": [
                {
                    "number": 1,
                    "role": "evidence",
                    "title": "Decision title",
                    "claimIds": ["F-001"],
                    "stateLabels": ["GA"],
                }
            ],
            "qa": {
                "strict": True,
                "minBodyPt": 15,
                "minTitlePt": 26,
                "maxUnmappedTextSpans": 0,
                "failRenderedOverflow": True,
                "requireVisualReview": False,
                "exceptionManifest": None,
            },
        }
        spec_path = self.work_dir / "deck-spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        args = build_parser().parse_args(
            [
                str(deck),
                "--out",
                str(self.work_dir / "verify"),
                "--deck-spec",
                str(spec_path),
            ]
        )
        result = verify(args)
        self.assertTrue(result["passed"], result["audit_failures"])
        self.assertEqual(result["claim_id_gaps"], {})


if __name__ == "__main__":
    unittest.main()
