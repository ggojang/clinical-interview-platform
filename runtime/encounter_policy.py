"""Deterministic encounter workflow and longitudinal context-review policy."""
from __future__ import annotations

from datetime import date
from typing import Any


DEFAULT_REVIEW_INTERVAL_DAYS = {
    "history.conditions": 365,
    "medication.current": 90,
    "history.family": 365,
    "social.alcohol": 365,
    "social.smoking": 365,
}


def classify_result_follow_up_goal(text: str) -> str:
    low = text.lower()
    interpretation = any(cue in low for cue in (
        "판독", "해석", "설명해", "무슨 뜻", "봐 주세요", "봐주세요",
        "interpret", "explain this result", "review this report",
    ))
    institution_check = any(cue in low for cue in (
        "결과 확인하러", "결과 들으러", "병원에서 결과", "의료기관에서 결과",
        "결과가 나왔다고", "check my result at the hospital", "get my results",
    ))
    if interpretation and institution_check:
        return "both"
    if interpretation:
        return "interpretation_request"
    if institution_check:
        return "institution_result_check"
    return "unknown"


def result_follow_up_action(
    goal: str,
    *,
    result_content_requested: bool = False,
    abnormal_notice: bool = False,
    new_concern: bool = False,
) -> str:
    if abnormal_notice or new_concern:
        return "continue_targeted_interview"
    if goal == "institution_result_check":
        return "ask_additional_request_then_complete"
    if goal in {"interpretation_request", "both"}:
        return (
            "await_or_interpret_provided_result"
            if result_content_requested
            else "request_result_content_once"
        )
    return "clarify_result_follow_up_goal"


def context_review_due(
    *,
    is_first_encounter: bool,
    as_of: date,
    last_confirmed: dict[str, date | None],
    intervals: dict[str, int] | None = None,
) -> dict[str, dict[str, Any]]:
    policy = intervals or DEFAULT_REVIEW_INTERVAL_DAYS
    due: dict[str, dict[str, Any]] = {}
    for fact_group, interval_days in policy.items():
        confirmed_at = last_confirmed.get(fact_group)
        elapsed_days = (as_of - confirmed_at).days if confirmed_at else None
        should_review = (
            is_first_encounter
            or confirmed_at is None
            or elapsed_days is not None and elapsed_days >= interval_days
        )
        due[fact_group] = {
            "due": should_review,
            "interval_days": interval_days,
            "last_confirmed_at": confirmed_at.isoformat() if confirmed_at else None,
            "elapsed_days": elapsed_days,
            "reason": (
                "first_encounter" if is_first_encounter
                else "never_confirmed" if confirmed_at is None
                else "interval_elapsed" if should_review
                else "recently_confirmed"
            ),
        }
    return due
