#!/usr/bin/env python3
"""Speaker-notes contract and PPTX analysis."""

from __future__ import annotations

import copy
import re
from pathlib import Path
from typing import Any

from pptx import Presentation


DEFAULT_KOREAN_POLICY = {
    "required": True,
    "authoringMode": "regenerate-from-scratch",
    "requiredSections": [
        "핵심 메시지",
        "발표 설명",
        "질문/전환",
        "출처/상태",
    ],
    "explanationSection": "발표 설명",
    "targetSeconds": 60,
    "minCharacters": 400,
    "maxCharacters": 750,
    "minExplanationCharacters": 240,
    "minExplanationSentences": 3,
}


class SpeakerNotesPolicyError(ValueError):
    """Raised when a speaker-notes policy is invalid."""


def normalize_policy(language: str, value: Any) -> dict[str, Any] | None:
    """Return a validated policy, applying Korean defaults when omitted."""
    is_korean = language.casefold() == "ko" or language.casefold().startswith("ko-")
    if value is None:
        return copy.deepcopy(DEFAULT_KOREAN_POLICY) if is_korean else None
    if not isinstance(value, dict):
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy must be an object or null"
        )
    allowed = set(DEFAULT_KOREAN_POLICY)
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy contains unsupported field(s): "
            + ", ".join(unknown)
        )
    policy = {**copy.deepcopy(DEFAULT_KOREAN_POLICY), **copy.deepcopy(value)}
    if not isinstance(policy["required"], bool):
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.required must be a boolean"
        )
    if policy["authoringMode"] != "regenerate-from-scratch":
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.authoringMode must be "
            "'regenerate-from-scratch'"
        )
    sections = policy["requiredSections"]
    if (
        not isinstance(sections, list)
        or not all(isinstance(section, str) and section.strip() for section in sections)
        or len(sections) != len(set(sections))
    ):
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.requiredSections must contain unique "
            "non-empty strings"
        )
    policy["requiredSections"] = [section.strip() for section in sections]
    explanation_section = policy["explanationSection"]
    if (
        not isinstance(explanation_section, str)
        or explanation_section.strip() not in policy["requiredSections"]
    ):
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.explanationSection must name one of "
            "requiredSections"
        )
    policy["explanationSection"] = explanation_section.strip()
    for key in (
        "minCharacters",
        "maxCharacters",
        "targetSeconds",
        "minExplanationCharacters",
        "minExplanationSentences",
    ):
        value = policy[key]
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise SpeakerNotesPolicyError(
                f"$.speakerNotesPolicy.{key} must be a positive integer"
            )
    if policy["maxCharacters"] < policy["minCharacters"]:
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.maxCharacters must be >= minCharacters"
        )
    return policy


def _notes_text(slide) -> str:
    try:
        value = slide.notes_slide.notes_text_frame.text
    except (AttributeError, ValueError):
        return ""
    return value.strip()


def _section_text(text: str, section: str) -> str:
    prefix = f"{section}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return ""


def _sentence_count(text: str) -> int:
    return len(re.findall(r"[.!?](?:\s|$)", text))


def analyze_deck(deck: Path, policy: dict[str, Any]) -> dict[str, Any]:
    """Inspect notes length and required section markers on every slide."""
    prs = Presentation(deck)
    slides: list[dict[str, Any]] = []
    missing_slides: list[int] = []
    short_slides: list[int] = []
    long_slides: list[int] = []
    section_gaps: list[dict[str, Any]] = []
    brief_explanation_slides: list[int] = []
    low_explanation_sentence_slides: list[int] = []
    for number, slide in enumerate(prs.slides, 1):
        text = _notes_text(slide)
        character_count = len(text)
        missing_sections = [
            section
            for section in policy["requiredSections"]
            if f"{section}:" not in text
        ]
        if not text:
            missing_slides.append(number)
        elif character_count < policy["minCharacters"]:
            short_slides.append(number)
        if character_count > policy["maxCharacters"]:
            long_slides.append(number)
        if missing_sections:
            section_gaps.append(
                {
                    "slide": number,
                    "missingSections": missing_sections,
                }
            )
        explanation = _section_text(text, policy["explanationSection"])
        explanation_characters = len(explanation)
        explanation_sentences = _sentence_count(explanation)
        if (
            explanation
            and explanation_characters < policy["minExplanationCharacters"]
        ):
            brief_explanation_slides.append(number)
        if (
            explanation
            and explanation_sentences < policy["minExplanationSentences"]
        ):
            low_explanation_sentence_slides.append(number)
        slides.append(
            {
                "slide": number,
                "characters": character_count,
                "missingSections": missing_sections,
                "explanationCharacters": explanation_characters,
                "explanationSentences": explanation_sentences,
            }
        )
    return {
        "required": policy["required"],
        "authoringMode": policy["authoringMode"],
        "requiredSections": policy["requiredSections"],
        "explanationSection": policy["explanationSection"],
        "minCharacters": policy["minCharacters"],
        "maxCharacters": policy["maxCharacters"],
        "targetSeconds": policy["targetSeconds"],
        "minExplanationCharacters": policy["minExplanationCharacters"],
        "minExplanationSentences": policy["minExplanationSentences"],
        "slides": slides,
        "missingSlides": missing_slides,
        "shortSlides": short_slides,
        "longSlides": long_slides,
        "sectionGaps": section_gaps,
        "briefExplanationSlides": brief_explanation_slides,
        "lowExplanationSentenceSlides": low_explanation_sentence_slides,
    }


def failures(report: dict[str, Any]) -> list[str]:
    if not report["required"]:
        return []
    problems: list[str] = []
    if report["missingSlides"]:
        problems.append(
            "Speaker notes are missing on slide(s): "
            + ", ".join(map(str, report["missingSlides"]))
        )
    if report["shortSlides"]:
        problems.append(
            "Speaker notes are shorter than "
            f"{report['minCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["shortSlides"]))
        )
    if report["longSlides"]:
        problems.append(
            "Speaker notes exceed "
            f"{report['maxCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["longSlides"]))
        )
    if report["sectionGaps"]:
        rendered = "; ".join(
            f"{item['slide']} ({', '.join(item['missingSections'])})"
            for item in report["sectionGaps"]
        )
        problems.append(
            "Speaker notes are missing required section(s): " + rendered
        )
    if report["briefExplanationSlides"]:
        problems.append(
            "Speaker note explanations are shorter than "
            f"{report['minExplanationCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["briefExplanationSlides"]))
        )
    if report["lowExplanationSentenceSlides"]:
        problems.append(
            "Speaker note explanations contain fewer than "
            f"{report['minExplanationSentences']} sentences on slide(s): "
            + ", ".join(map(str, report["lowExplanationSentenceSlides"]))
        )
    return problems
