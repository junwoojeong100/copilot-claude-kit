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
        "전체 흐름",
        "구성 요소",
        "실제 예시",
        "검증 기준",
        "상태/조건",
        "질문/전환",
        "발표 한 문장",
        "출처",
    ],
    "explanationSection": "전체 흐름",
    "statusSection": "상태/조건",
    "exampleSection": "실제 예시",
    "validationSection": "검증 기준",
    "summarySection": "발표 한 문장",
    "targetSeconds": 180,
    "minCharacters": 1000,
    "maxCharacters": 2600,
    "minExplanationCharacters": 220,
    "minExplanationSentences": 3,
    "minStatusCharacters": 120,
    "minExampleCharacters": 100,
    "minValidationCharacters": 70,
    "minSummaryCharacters": 30,
    "maxSummaryCharacters": 180,
    "requireStateLabelsInStatusSection": True,
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
    status_section = policy["statusSection"]
    if (
        not isinstance(status_section, str)
        or status_section.strip() not in policy["requiredSections"]
    ):
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.statusSection must name one of "
            "requiredSections"
        )
    policy["statusSection"] = status_section.strip()
    for key in ("exampleSection", "validationSection", "summarySection"):
        section = policy[key]
        if (
            not isinstance(section, str)
            or section.strip() not in policy["requiredSections"]
        ):
            raise SpeakerNotesPolicyError(
                f"$.speakerNotesPolicy.{key} must name one of requiredSections"
            )
        policy[key] = section.strip()
    if not isinstance(policy["requireStateLabelsInStatusSection"], bool):
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.requireStateLabelsInStatusSection "
            "must be a boolean"
        )
    for key in (
        "minCharacters",
        "maxCharacters",
        "targetSeconds",
        "minExplanationCharacters",
        "minExplanationSentences",
        "minStatusCharacters",
        "minExampleCharacters",
        "minValidationCharacters",
        "minSummaryCharacters",
        "maxSummaryCharacters",
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
    if policy["maxSummaryCharacters"] < policy["minSummaryCharacters"]:
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.maxSummaryCharacters must be >= "
            "minSummaryCharacters"
        )
    return policy


def _notes_text(slide) -> str:
    try:
        value = slide.notes_slide.notes_text_frame.text
    except (AttributeError, ValueError):
        return ""
    return value.strip()


def _parse_sections(text: str, sections: list[str]) -> dict[str, str]:
    parsed = {section: [] for section in sections}
    ordered_sections = sorted(sections, key=len, reverse=True)
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        matched = next(
            (
                section
                for section in ordered_sections
                if stripped.startswith(f"{section}:")
            ),
            None,
        )
        if matched is not None:
            current = matched
            remainder = stripped[len(matched) + 1 :].strip()
            if remainder:
                parsed[current].append(remainder)
            continue
        if current is not None and stripped:
            parsed[current].append(stripped)
    return {
        section: "\n".join(lines).strip()
        for section, lines in parsed.items()
    }


def _sentence_count(text: str) -> int:
    return len(re.findall(r"[.!?](?:\s|$)", text))


def _contains_state_label(text: str, label: str) -> bool:
    normalized_text = " ".join(text.upper().split())
    normalized_label = " ".join(label.upper().split())
    if normalized_label == "GA":
        normalized_text = normalized_text.replace("PARTIAL GA", "")
        return re.search(r"(?<![A-Z])GA(?![A-Z])", normalized_text) is not None
    return normalized_label in normalized_text


def analyze_deck(
    deck: Path,
    policy: dict[str, Any],
    *,
    state_labels_by_slide: dict[int, list[str]] | None = None,
) -> dict[str, Any]:
    """Inspect notes length and required section markers on every slide."""
    prs = Presentation(deck)
    slides: list[dict[str, Any]] = []
    missing_slides: list[int] = []
    short_slides: list[int] = []
    long_slides: list[int] = []
    section_gaps: list[dict[str, Any]] = []
    brief_explanation_slides: list[int] = []
    low_explanation_sentence_slides: list[int] = []
    brief_status_slides: list[int] = []
    state_summary_gaps: list[dict[str, Any]] = []
    brief_example_slides: list[int] = []
    brief_validation_slides: list[int] = []
    brief_summary_slides: list[int] = []
    long_summary_slides: list[int] = []
    for number, slide in enumerate(prs.slides, 1):
        text = _notes_text(slide)
        character_count = len(text)
        parsed_sections = _parse_sections(text, policy["requiredSections"])
        missing_sections = [
            section
            for section in policy["requiredSections"]
            if not parsed_sections[section]
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
        explanation = parsed_sections[policy["explanationSection"]]
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
        status_summary = parsed_sections[policy["statusSection"]]
        status_characters = len(status_summary)
        if status_summary and status_characters < policy["minStatusCharacters"]:
            brief_status_slides.append(number)
        expected_state_labels = (
            state_labels_by_slide.get(number, [])
            if state_labels_by_slide is not None
            else []
        )
        missing_state_labels = []
        if policy["requireStateLabelsInStatusSection"]:
            missing_state_labels = [
                label
                for label in expected_state_labels
                if not _contains_state_label(status_summary, label)
            ]
        if missing_state_labels:
            state_summary_gaps.append(
                {
                    "slide": number,
                    "missingStateLabels": missing_state_labels,
                }
            )
        example = parsed_sections[policy["exampleSection"]]
        example_characters = len(example)
        if example and example_characters < policy["minExampleCharacters"]:
            brief_example_slides.append(number)
        validation = parsed_sections[policy["validationSection"]]
        validation_characters = len(validation)
        if (
            validation
            and validation_characters < policy["minValidationCharacters"]
        ):
            brief_validation_slides.append(number)
        summary = parsed_sections[policy["summarySection"]]
        summary_characters = len(summary)
        if summary and summary_characters < policy["minSummaryCharacters"]:
            brief_summary_slides.append(number)
        if summary_characters > policy["maxSummaryCharacters"]:
            long_summary_slides.append(number)
        slides.append(
            {
                "slide": number,
                "characters": character_count,
                "missingSections": missing_sections,
                "explanationCharacters": explanation_characters,
                "explanationSentences": explanation_sentences,
                "statusCharacters": status_characters,
                "missingStateLabels": missing_state_labels,
                "exampleCharacters": example_characters,
                "validationCharacters": validation_characters,
                "summaryCharacters": summary_characters,
            }
        )
    return {
        "required": policy["required"],
        "authoringMode": policy["authoringMode"],
        "requiredSections": policy["requiredSections"],
        "explanationSection": policy["explanationSection"],
        "statusSection": policy["statusSection"],
        "exampleSection": policy["exampleSection"],
        "validationSection": policy["validationSection"],
        "summarySection": policy["summarySection"],
        "minCharacters": policy["minCharacters"],
        "maxCharacters": policy["maxCharacters"],
        "targetSeconds": policy["targetSeconds"],
        "minExplanationCharacters": policy["minExplanationCharacters"],
        "minExplanationSentences": policy["minExplanationSentences"],
        "minStatusCharacters": policy["minStatusCharacters"],
        "minExampleCharacters": policy["minExampleCharacters"],
        "minValidationCharacters": policy["minValidationCharacters"],
        "minSummaryCharacters": policy["minSummaryCharacters"],
        "maxSummaryCharacters": policy["maxSummaryCharacters"],
        "requireStateLabelsInStatusSection": policy[
            "requireStateLabelsInStatusSection"
        ],
        "slides": slides,
        "missingSlides": missing_slides,
        "shortSlides": short_slides,
        "longSlides": long_slides,
        "sectionGaps": section_gaps,
        "briefExplanationSlides": brief_explanation_slides,
        "lowExplanationSentenceSlides": low_explanation_sentence_slides,
        "briefStatusSlides": brief_status_slides,
        "stateSummaryGaps": state_summary_gaps,
        "briefExampleSlides": brief_example_slides,
        "briefValidationSlides": brief_validation_slides,
        "briefSummarySlides": brief_summary_slides,
        "longSummarySlides": long_summary_slides,
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
    if report["briefStatusSlides"]:
        problems.append(
            "Speaker note status/condition summaries are shorter than "
            f"{report['minStatusCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["briefStatusSlides"]))
        )
    if report["stateSummaryGaps"]:
        rendered = "; ".join(
            f"{item['slide']} ({', '.join(item['missingStateLabels'])})"
            for item in report["stateSummaryGaps"]
        )
        problems.append(
            "Speaker note status/condition summaries are missing slide state "
            "label(s): " + rendered
        )
    if report["briefExampleSlides"]:
        problems.append(
            "Speaker note examples are shorter than "
            f"{report['minExampleCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["briefExampleSlides"]))
        )
    if report["briefValidationSlides"]:
        problems.append(
            "Speaker note validation criteria are shorter than "
            f"{report['minValidationCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["briefValidationSlides"]))
        )
    if report["briefSummarySlides"]:
        problems.append(
            "Speaker note presenter summaries are shorter than "
            f"{report['minSummaryCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["briefSummarySlides"]))
        )
    if report["longSummarySlides"]:
        problems.append(
            "Speaker note presenter summaries exceed "
            f"{report['maxSummaryCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["longSummarySlides"]))
        )
    return problems
