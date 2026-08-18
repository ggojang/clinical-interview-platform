"""Deterministic presentation metadata for adaptive interview questions.

These shortcuts are not clinical answer codes and must never be exported as a
Questionnaire ``answerOption`` or included in an answer ValueSet.  They only
make an otherwise free-text question easier to answer.  The Runtime owns this
contract so every client presents the same choices without asking an LLM to
invent them.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


PRESENTATION_CONTRACT_VERSION = "0.1.0"


_FACT_SUGGESTIONS: dict[str, list[dict[str, str]]] = {
    "symptom.duration": [
        {
            "input": "1",
            "display_ko": "오늘부터",
            "answer_text": "1일",
        },
        {
            "input": "2",
            "display_ko": "3일 정도",
            "answer_text": "3일",
        },
        {
            "input": "3",
            "display_ko": "1주일 정도",
            "answer_text": "1주",
        },
        {
            "input": "4",
            "display_ko": "1개월 정도",
            "answer_text": "1개월",
        },
    ],
}


DATA_ABSENT_ACTIONS = [
    {
        "input": "5",
        "display_ko": "잘 모르겠음",
        "dataAbsentReason": "asked-unknown",
        "answer_text": "잘 모르겠습니다",
    },
    {
        "input": "6",
        "display_ko": "답변하지 않음",
        "dataAbsentReason": "asked-declined",
        "answer_text": "답변하지 않음",
    },
]


def display_suggestions(fact_id: str) -> list[dict[str, str]]:
    """Return input-only shortcuts for a Fact, never coded answer options."""
    return deepcopy(_FACT_SUGGESTIONS.get(fact_id, []))


def resolve_presentation_input(
    fact_id: str,
    answer: str,
) -> dict[str, Any] | None:
    """Resolve a shortcut label/number without confusing it with a code."""
    normalized = answer.strip().lower().rstrip(".!?")
    suggestions = display_suggestions(fact_id)
    for suggestion in suggestions:
        aliases = {
            suggestion["input"].lower(),
            suggestion["display_ko"].lower(),
            suggestion["answer_text"].lower(),
        }
        if normalized in aliases:
            return {
                "kind": "display_suggestion",
                "answer_text": suggestion["answer_text"],
            }
    # Inputs 5 and 6 are reserved only in the shortcut presentation.  Treating
    # them globally would corrupt legitimate numeric answers such as NRS 5.
    for action in DATA_ABSENT_ACTIONS if suggestions else []:
        aliases = {
            action["input"].lower(),
            action["display_ko"].lower(),
            action["answer_text"].lower(),
        }
        if normalized in aliases:
            return {
                "kind": "data_absent",
                "answer_text": action["answer_text"],
                "dataAbsentReason": action["dataAbsentReason"],
            }
    return None
