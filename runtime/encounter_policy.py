"""Deterministic encounter workflow and longitudinal context-review policy."""
from __future__ import annotations

from datetime import date
from typing import Any


DEFAULT_REVIEW_INTERVAL_DAYS = {
    "history.conditions": 365,
    "history.procedures": 365,
    "medication.current": 90,
    "allergy.current": 365,
    "history.family": 365,
    "occupation.current": 365,
    "social.alcohol": 365,
    "social.smoking": 365,
}

PREVENTIVE_IMMUNIZATION_INTERVAL_DAYS = 365
PREVENTIVE_IMMUNIZATION_ENCOUNTER_TYPES = {
    "preventive_visit",
    "annual_review",
    "vaccination",
}
PREVENTIVE_IMMUNIZATION_CARE_SETTINGS = {
    "health_checkup",
    "community_screening",
}

RESOLVED_CONTEXT_STATES = {
    "answered",
    "current_existing",
    "unknown",
    "declined",
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
    result_content_available: bool = False,
    abnormal_notice: bool = False,
    urgent_follow_up_instruction: bool = False,
    new_concern: bool = False,
) -> str:
    if abnormal_notice or urgent_follow_up_instruction or new_concern:
        return "continue_targeted_interview"
    if goal == "institution_result_check":
        return "ask_additional_request_then_complete"
    if goal in {"interpretation_request", "both"}:
        if result_content_available:
            return "interpret_provided_result"
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


def context_review_completion(
    *,
    due_groups: dict[str, dict[str, Any]],
    group_states: dict[str, str],
) -> dict[str, Any]:
    """Determine whether all due longitudinal groups have an explicit outcome."""
    unresolved = [
        group
        for group, review in due_groups.items()
        if review.get("due") and group_states.get(group) not in RESOLVED_CONTEXT_STATES
    ]
    deferred = [
        group for group in unresolved if group_states.get(group) == "deferred_safety"
    ]
    return {
        "complete": not unresolved,
        "unresolved_groups": unresolved,
        "safety_deferred_groups": deferred,
    }


def preventive_immunization_review_due(
    *,
    encounter_type: str,
    care_setting: str = "primary_care",
    as_of: date,
    last_confirmed_at: date | None,
    rfe_or_risk_relevant: bool = False,
    interval_days: int = PREVENTIVE_IMMUNIZATION_INTERVAL_DAYS,
) -> dict[str, Any]:
    """Review immunization history only when preventive context is activated.

    This interval controls history reconfirmation, never whether a vaccine is
    clinically due. Due status needs current age-, risk-, and jurisdiction-
    specific schedule knowledge.
    """
    activated = (
        encounter_type in PREVENTIVE_IMMUNIZATION_ENCOUNTER_TYPES
        or care_setting in PREVENTIVE_IMMUNIZATION_CARE_SETTINGS
        or rfe_or_risk_relevant
    )
    if not activated:
        return {
            "due": False,
            "activated": False,
            "reason": "not_activated",
            "interval_days": interval_days,
            "last_confirmed_at": (
                last_confirmed_at.isoformat() if last_confirmed_at else None
            ),
            "vaccine_due_status_inferred": False,
        }

    elapsed_days = (
        (as_of - last_confirmed_at).days if last_confirmed_at else None
    )
    due = last_confirmed_at is None or elapsed_days >= interval_days
    return {
        "due": due,
        "activated": True,
        "reason": (
            "never_confirmed" if last_confirmed_at is None
            else "interval_elapsed" if due
            else "recently_confirmed"
        ),
        "interval_days": interval_days,
        "last_confirmed_at": (
            last_confirmed_at.isoformat() if last_confirmed_at else None
        ),
        "elapsed_days": elapsed_days,
        "vaccine_due_status_inferred": False,
    }
