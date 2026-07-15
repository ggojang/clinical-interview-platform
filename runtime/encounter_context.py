"""Deterministic, diagnosis-independent Encounter Context normalization."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


ALLOWED = {
    "care_setting": {
        "primary_care", "emergency_department", "specialist_clinic",
        "telemedicine", "home_visit", "occupational_health",
        "health_checkup", "community_screening",
    },
    "encounter_type": {
        "new_encounter", "follow_up", "annual_review", "medication_review",
        "preventive_visit", "administrative_visit", "vaccination",
        "referral_consultation",
    },
    "interview_initiator": {
        "patient", "caregiver", "clinician", "health_system", "employer",
        "school", "public_health_program",
    },
    "interview_mode": {
        "face_to_face", "telephone", "video", "chat",
        "asynchronous_questionnaire", "ai_assisted_interview",
    },
    "time_constraint": {
        "emergency", "urgent", "routine", "scheduled", "screening",
        "self_paced",
    },
    "clinical_responsibility": {
        "independent_assessment", "shared_care", "referral_support",
        "follow_up_support", "decision_support", "education",
    },
}

DEFAULT = {
    "care_setting": "primary_care",
    "encounter_type": "new_encounter",
    "interview_initiator": "patient",
    "interview_mode": "chat",
    "available_information": ["no_previous_records"],
    "time_constraint": "routine",
    "clinical_responsibility": "decision_support",
}

REMOTE_MODES = {"telephone", "video", "chat", "asynchronous_questionnaire"}


def normalize_encounter_context(value: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a validated context plus observable Runtime constraints.

    Encounter Context changes interview behavior but never carries or infers a
    diagnosis. Unknown values fail closed so a misspelled care setting cannot
    silently select a different workflow.
    """
    raw = deepcopy(DEFAULT)
    if value:
        unknown = set(value) - set(DEFAULT)
        if unknown:
            raise ValueError(f"unknown Encounter Context fields: {sorted(unknown)}")
        raw.update(deepcopy(value))
    for field, allowed in ALLOWED.items():
        if raw[field] not in allowed:
            raise ValueError(f"unsupported Encounter Context {field}: {raw[field]!r}")
    information = raw["available_information"]
    if not isinstance(information, list) or not all(
        isinstance(item, str) and item.strip() for item in information
    ):
        raise ValueError("available_information must be a list of non-empty strings")

    emergency_context = (
        raw["care_setting"] == "emergency_department"
        or raw["time_constraint"] == "emergency"
    )
    urgent_context = raw["time_constraint"] == "urgent"
    remote = raw["interview_mode"] in REMOTE_MODES
    proxy = raw["interview_initiator"] == "caregiver"
    modifiers: list[str] = []
    candidate_intents: list[str] = []
    if emergency_context:
        modifiers.extend(["immediate_safety", "emergency_screening"])
        candidate_intents.append("intent.screen_red_flags")
    if raw["care_setting"] == "specialist_clinic" or raw["encounter_type"] == "follow_up":
        modifiers.extend(["treatment_response", "medication_adherence", "disease_progression"])
        candidate_intents.extend(["intent.characterize_follow_up", "intent.follow_up_support"])
    if raw["care_setting"] in {"health_checkup", "community_screening"} or raw["encounter_type"] == "preventive_visit":
        modifiers.extend(["prevention", "screening", "risk_assessment"])
        candidate_intents.extend(["intent.preventive_care", "intent.risk_assessment"])
    if raw["encounter_type"] == "medication_review":
        modifiers.extend(["medication_reconciliation", "adherence", "adverse_effects"])
        candidate_intents.extend(["intent.medication_review", "intent.follow_up_support"])

    raw.update({
        "context_version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "diagnosis_independent": True,
        "response_source": "proxy_report" if proxy else "patient_report",
        "source_attribution_required": True,
        "physical_examination_available": not remote,
        "remote_assessment_limitations_apply": remote,
        "safety_first": emergency_context or urgent_context,
        "question_budget_cap": 12 if emergency_context else 18 if urgent_context else None,
        "intent_modifiers": list(dict.fromkeys(modifiers)),
        "candidate_intents": list(dict.fromkeys(candidate_intents)),
    })
    return raw
