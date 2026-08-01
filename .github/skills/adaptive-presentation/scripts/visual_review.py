#!/usr/bin/env python3
"""Validate human/agent visual-review evidence for a rendered deck revision."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from pptx import Presentation

from render_pptx import sha256_file


class VisualReviewError(ValueError):
    """Raised when visual-review evidence is missing, stale, or incomplete."""


@dataclass(frozen=True)
class VisualReview:
    path: Path
    reviewed_slides: set[int]
    reviewer: str
    notes: str


def load_visual_review(
    path: Path,
    deck: Path,
    *,
    slide_count: int,
) -> VisualReview:
    resolved = path.expanduser().resolve()
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    try:
        value = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise VisualReviewError(
            f"Visual-review evidence is not valid JSON: {resolved}"
        ) from error
    if not isinstance(value, dict) or value.get("schemaVersion") != 1:
        raise VisualReviewError("Visual-review schemaVersion must be 1")
    unknown = sorted(
        set(value)
        - {"schemaVersion", "deckSha256", "reviewer", "reviewedSlides", "notes"}
    )
    if unknown:
        raise VisualReviewError(
            "Visual-review contains unsupported fields: " + ", ".join(unknown)
        )
    if value.get("deckSha256") != sha256_file(deck):
        raise VisualReviewError(
            "Visual-review evidence does not match the current PPTX revision"
        )
    reviewer = value.get("reviewer")
    notes = value.get("notes")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise VisualReviewError("Visual-review reviewer must be a non-empty string")
    if not isinstance(notes, str) or len(notes.strip()) < 12:
        raise VisualReviewError("Visual-review notes must record the review outcome")
    slides = value.get("reviewedSlides")
    if slides == "all":
        reviewed = set(range(1, slide_count + 1))
    elif isinstance(slides, list) and all(
        isinstance(slide, int) and not isinstance(slide, bool) for slide in slides
    ):
        reviewed = set(slides)
    else:
        raise VisualReviewError(
            "Visual-review reviewedSlides must be 'all' or an integer array"
        )
    invalid = sorted(
        slide for slide in reviewed if slide < 1 or slide > slide_count
    )
    if invalid:
        raise VisualReviewError(
            f"Visual-review slides out of range 1-{slide_count}: {invalid}"
        )
    if reviewed != set(range(1, slide_count + 1)):
        raise VisualReviewError(
            "Visual-review evidence must cover every slide through contact sheets "
            "or full-slide inspection"
        )
    return VisualReview(
        path=resolved,
        reviewed_slides=reviewed,
        reviewer=reviewer.strip(),
        notes=notes.strip(),
    )


def write_visual_review(
    deck: Path,
    output: Path,
    *,
    reviewer: str,
    notes: str,
) -> Path:
    resolved_deck = deck.expanduser().resolve()
    if not resolved_deck.is_file():
        raise FileNotFoundError(resolved_deck)
    resolved_output = output.expanduser().resolve()
    if resolved_output.exists() or resolved_output.is_symlink():
        raise FileExistsError(
            f"Refusing to overwrite visual-review evidence: {resolved_output}"
        )
    if len(reviewer.strip()) < 1 or len(notes.strip()) < 12:
        raise VisualReviewError("Reviewer and meaningful review notes are required")
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    value = {
        "schemaVersion": 1,
        "deckSha256": sha256_file(resolved_deck),
        "reviewer": reviewer.strip(),
        "reviewedSlides": "all",
        "notes": notes.strip(),
    }
    resolved_output.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return resolved_output


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or validate revision-bound visual-review evidence."
    )
    subparsers = parser.add_subparsers(dest="action", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("deck", type=Path)
    create.add_argument("--out", type=Path, required=True)
    create.add_argument("--reviewer", required=True)
    create.add_argument("--notes", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("deck", type=Path)
    validate.add_argument("evidence", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.action == "create":
        output = write_visual_review(
            args.deck,
            args.out,
            reviewer=args.reviewer,
            notes=args.notes,
        )
        print(output)
        return 0
    slide_count = len(Presentation(args.deck).slides)
    review = load_visual_review(
        args.evidence,
        args.deck.expanduser().resolve(),
        slide_count=slide_count,
    )
    print(
        f"Visual review PASS | reviewer={review.reviewer} | "
        f"slides={len(review.reviewed_slides)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, FileExistsError, OSError, VisualReviewError) as error:
        print(f"visual_review.py: {error}", file=sys.stderr)
        raise SystemExit(2)
