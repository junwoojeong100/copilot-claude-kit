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
        "질문",
        "핵심 메시지",
        "전환",
    ],
    "questionSection": "질문",
    "coreSection": "핵심 메시지",
    "transitionSection": "전환",
    "targetSeconds": 60,
    "minCharacters": 80,
    "maxCharacters": 600,
    "minQuestionCharacters": 20,
    "maxQuestionCharacters": 140,
    "maxQuestionSentences": 1,
    "minCoreCharacters": 30,
    "maxCoreCharacters": 260,
    "maxCoreSentences": 3,
    "maxTransitionCharacters": 180,
    "maxTransitionSentences": 1,
    "maxTotalSentences": 5,
    "requireQuestionFirst": True,
    "requireQuestionMark": True,
    "forbidSourceReferences": True,
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
    for key in ("questionSection", "coreSection", "transitionSection"):
        section = policy[key]
        if (
            not isinstance(section, str)
            or section.strip() not in policy["requiredSections"]
        ):
            raise SpeakerNotesPolicyError(
                f"$.speakerNotesPolicy.{key} must name one of requiredSections"
            )
        policy[key] = section.strip()
    for key in (
        "requireQuestionFirst",
        "requireQuestionMark",
        "forbidSourceReferences",
    ):
        if not isinstance(policy[key], bool):
            raise SpeakerNotesPolicyError(
                f"$.speakerNotesPolicy.{key} must be a boolean"
            )
    for key in (
        "minCharacters",
        "maxCharacters",
        "targetSeconds",
        "minQuestionCharacters",
        "maxQuestionCharacters",
        "maxQuestionSentences",
        "minCoreCharacters",
        "maxCoreCharacters",
        "maxCoreSentences",
        "maxTransitionCharacters",
        "maxTransitionSentences",
        "maxTotalSentences",
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
    if policy["maxQuestionCharacters"] < policy["minQuestionCharacters"]:
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.maxQuestionCharacters must be >= "
            "minQuestionCharacters"
        )
    if policy["maxCoreCharacters"] < policy["minCoreCharacters"]:
        raise SpeakerNotesPolicyError(
            "$.speakerNotesPolicy.maxCoreCharacters must be >= "
            "minCoreCharacters"
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


def _contains_source_reference(text: str) -> bool:
    return any(
        re.search(pattern, text, flags)
        for pattern, flags in (
            (r"^\s*(?:출처|source)\s*:", re.IGNORECASE | re.MULTILINE),
            (r"\[?F-\d{3,}\]?", re.IGNORECASE),
            (r"https?://", re.IGNORECASE),
        )
    )


def analyze_deck(
    deck: Path,
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Inspect notes length and required section markers on every slide."""
    prs = Presentation(deck)
    slides: list[dict[str, Any]] = []
    missing_slides: list[int] = []
    short_slides: list[int] = []
    long_slides: list[int] = []
    section_gaps: list[dict[str, Any]] = []
    question_not_first_slides: list[int] = []
    brief_question_slides: list[int] = []
    long_question_slides: list[int] = []
    multi_sentence_question_slides: list[int] = []
    question_mark_gaps: list[int] = []
    brief_core_slides: list[int] = []
    long_core_slides: list[int] = []
    multi_sentence_core_slides: list[int] = []
    long_transition_slides: list[int] = []
    multi_sentence_transition_slides: list[int] = []
    over_sentence_limit_slides: list[int] = []
    source_reference_slides: list[int] = []
    for number, slide in enumerate(prs.slides, 1):
        text = _notes_text(slide)
        character_count = len(text)
        total_sentences = _sentence_count(text)
        has_source_reference = _contains_source_reference(text)
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
        question = parsed_sections[policy["questionSection"]]
        question_characters = len(question)
        question_sentences = _sentence_count(question)
        question_first = text.startswith(f"{policy['questionSection']}:")
        has_question_mark = question.rstrip().endswith(("?", "？"))
        if text and policy["requireQuestionFirst"] and not question_first:
            question_not_first_slides.append(number)
        if question and question_characters < policy["minQuestionCharacters"]:
            brief_question_slides.append(number)
        if question_characters > policy["maxQuestionCharacters"]:
            long_question_slides.append(number)
        if question_sentences > policy["maxQuestionSentences"]:
            multi_sentence_question_slides.append(number)
        if question and policy["requireQuestionMark"] and not has_question_mark:
            question_mark_gaps.append(number)
        core = parsed_sections[policy["coreSection"]]
        core_characters = len(core)
        core_sentences = _sentence_count(core)
        if core and core_characters < policy["minCoreCharacters"]:
            brief_core_slides.append(number)
        if core_characters > policy["maxCoreCharacters"]:
            long_core_slides.append(number)
        if core_sentences > policy["maxCoreSentences"]:
            multi_sentence_core_slides.append(number)
        transition = parsed_sections[policy["transitionSection"]]
        transition_characters = len(transition)
        transition_sentences = _sentence_count(transition)
        if transition_characters > policy["maxTransitionCharacters"]:
            long_transition_slides.append(number)
        if transition_sentences > policy["maxTransitionSentences"]:
            multi_sentence_transition_slides.append(number)
        if total_sentences > policy["maxTotalSentences"]:
            over_sentence_limit_slides.append(number)
        if policy["forbidSourceReferences"] and has_source_reference:
            source_reference_slides.append(number)
        slides.append(
            {
                "slide": number,
                "characters": character_count,
                "sentences": total_sentences,
                "missingSections": missing_sections,
                "questionCharacters": question_characters,
                "questionSentences": question_sentences,
                "questionFirst": question_first,
                "hasQuestionMark": has_question_mark,
                "coreCharacters": core_characters,
                "coreSentences": core_sentences,
                "transitionCharacters": transition_characters,
                "transitionSentences": transition_sentences,
                "hasSourceReference": has_source_reference,
            }
        )
    return {
        "required": policy["required"],
        "authoringMode": policy["authoringMode"],
        "requiredSections": policy["requiredSections"],
        "questionSection": policy["questionSection"],
        "coreSection": policy["coreSection"],
        "transitionSection": policy["transitionSection"],
        "minCharacters": policy["minCharacters"],
        "maxCharacters": policy["maxCharacters"],
        "targetSeconds": policy["targetSeconds"],
        "minQuestionCharacters": policy["minQuestionCharacters"],
        "maxQuestionCharacters": policy["maxQuestionCharacters"],
        "maxQuestionSentences": policy["maxQuestionSentences"],
        "minCoreCharacters": policy["minCoreCharacters"],
        "maxCoreCharacters": policy["maxCoreCharacters"],
        "maxCoreSentences": policy["maxCoreSentences"],
        "maxTransitionCharacters": policy["maxTransitionCharacters"],
        "maxTransitionSentences": policy["maxTransitionSentences"],
        "maxTotalSentences": policy["maxTotalSentences"],
        "requireQuestionFirst": policy["requireQuestionFirst"],
        "requireQuestionMark": policy["requireQuestionMark"],
        "forbidSourceReferences": policy["forbidSourceReferences"],
        "slides": slides,
        "missingSlides": missing_slides,
        "shortSlides": short_slides,
        "longSlides": long_slides,
        "sectionGaps": section_gaps,
        "questionNotFirstSlides": question_not_first_slides,
        "briefQuestionSlides": brief_question_slides,
        "longQuestionSlides": long_question_slides,
        "multiSentenceQuestionSlides": multi_sentence_question_slides,
        "questionMarkGaps": question_mark_gaps,
        "briefCoreSlides": brief_core_slides,
        "longCoreSlides": long_core_slides,
        "multiSentenceCoreSlides": multi_sentence_core_slides,
        "longTransitionSlides": long_transition_slides,
        "multiSentenceTransitionSlides": multi_sentence_transition_slides,
        "overSentenceLimitSlides": over_sentence_limit_slides,
        "sourceReferenceSlides": source_reference_slides,
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
    if report["questionNotFirstSlides"]:
        problems.append(
            "Speaker notes do not start with the question section on slide(s): "
            + ", ".join(map(str, report["questionNotFirstSlides"]))
        )
    if report["briefQuestionSlides"]:
        problems.append(
            "Speaker note questions are shorter than "
            f"{report['minQuestionCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["briefQuestionSlides"]))
        )
    if report["longQuestionSlides"]:
        problems.append(
            "Speaker note questions exceed "
            f"{report['maxQuestionCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["longQuestionSlides"]))
        )
    if report["multiSentenceQuestionSlides"]:
        problems.append(
            "Speaker note questions contain more than "
            f"{report['maxQuestionSentences']} sentence(s) on slide(s): "
            + ", ".join(map(str, report["multiSentenceQuestionSlides"]))
        )
    if report["questionMarkGaps"]:
        problems.append(
            "Speaker note questions do not end with a question mark on slide(s): "
            + ", ".join(map(str, report["questionMarkGaps"]))
        )
    if report["briefCoreSlides"]:
        problems.append(
            "Speaker note core messages are shorter than "
            f"{report['minCoreCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["briefCoreSlides"]))
        )
    if report["longCoreSlides"]:
        problems.append(
            "Speaker note core messages exceed "
            f"{report['maxCoreCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["longCoreSlides"]))
        )
    if report["multiSentenceCoreSlides"]:
        problems.append(
            "Speaker note core messages contain more than "
            f"{report['maxCoreSentences']} sentence(s) on slide(s): "
            + ", ".join(map(str, report["multiSentenceCoreSlides"]))
        )
    if report["longTransitionSlides"]:
        problems.append(
            "Speaker note transitions exceed "
            f"{report['maxTransitionCharacters']} characters on slide(s): "
            + ", ".join(map(str, report["longTransitionSlides"]))
        )
    if report["multiSentenceTransitionSlides"]:
        problems.append(
            "Speaker note transitions contain more than "
            f"{report['maxTransitionSentences']} sentence(s) on slide(s): "
            + ", ".join(map(str, report["multiSentenceTransitionSlides"]))
        )
    if report["overSentenceLimitSlides"]:
        problems.append(
            "Speaker notes exceed "
            f"{report['maxTotalSentences']} total sentences on slide(s): "
            + ", ".join(map(str, report["overSentenceLimitSlides"]))
        )
    if report["sourceReferenceSlides"]:
        problems.append(
            "Speaker notes contain forbidden source references on slide(s): "
            + ", ".join(map(str, report["sourceReferenceSlides"]))
        )
    return problems
