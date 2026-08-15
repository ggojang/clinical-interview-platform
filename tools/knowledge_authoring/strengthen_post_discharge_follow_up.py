#!/usr/bin/env python3
"""Split post-discharge wound-care and equipment handoff into atomic facts."""
from __future__ import annotations

import json

import seed_post_discharge_follow_up
from profile_support import ROOT, entry, write_json


P = "post-discharge-follow-up"
FRAGMENT = "knowledge/generated/follow-up/post-discharge/post-discharge-follow-up.json"
POLICY = "policies/primary-care-post-discharge-follow-up-completion.json"
RESEARCH = "sources/manifests/primary-care-post-discharge-follow-up-research.json"
MAPPING = "mappings/terminology/snomed-mrcm-post-discharge-follow-up.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
UPDATED = "2026-08-16T00:00:00Z"
VERSION = "0.2.0"
CMS_SOURCE = "source.cms.discharge-planning-checklist.20260816"
STOM_MONITOR = "source.stom.post-discharge-monitor.20260816"
SOURCES = [
    "source.ahrq.red-toolkit.current-20260731",
    CMS_SOURCE,
    "source.nice.ng27.transition-discharge.2015-current-20260731",
    STOM_MONITOR,
]
G = "group.post_discharge.plan"
I = ["intent.reconcile_post_discharge_plan"]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def provenance(source_refs: list[str]) -> dict:
    return {
        "created_by": {"type": "ai", "id": "codex-gpt5"},
        "created_at": UPDATED,
        "source_refs": source_refs,
        "review_status": "unreviewed",
        "version": VERSION,
    }


def q(fact_id: str, display: str, value_type: str, key: str, wording: str, score: int):
    return entry(
        P,
        fact_id,
        display,
        value_type,
        key,
        wording,
        score,
        key,
        [G],
        intents=I,
    )


def fragment() -> dict:
    doc = load(FRAGMENT)
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.pop("post_discharge.wound_or_device_plan", None)
    additions = [
        q(
            "post_discharge.wound_care_task_required",
            "Wound-care Task Required After Discharge",
            "boolean",
            "wound-care-required",
            "퇴원 후 집에서 직접 해야 하는 상처 관리 작업이 있나요?",
            206,
        ),
        q(
            "post_discharge.wound_care_task_description",
            "Wound-care Task Description",
            "string",
            "wound-care-task",
            "집에서 해야 하는 상처 관리 작업을 안내받은 표현대로 알려주세요. 예: 드레싱 교환",
            205,
        ),
        q(
            "post_discharge.wound_care_instructions_available",
            "Wound-care Instructions Available",
            "boolean",
            "wound-care-instructions",
            "상처 관리 방법을 적은 안내문이나 확인할 수 있는 설명이 있나요?",
            204,
        ),
        q(
            "post_discharge.wound_care_skill_difficulty",
            "Difficulty Performing Wound-care Task",
            "boolean",
            "wound-care-difficulty",
            "환자나 보호자가 안내받은 상처 관리 작업을 실제로 하는 데 어려움이 있나요?",
            203,
        ),
        q(
            "post_discharge.wound_care_help_contact_known",
            "Wound-care Help Contact Known",
            "boolean",
            "wound-care-contact",
            "상처 관리가 어렵거나 문제가 생겼을 때 연락할 곳을 알고 있나요?",
            202,
        ),
        q(
            "post_discharge.home_medical_device_or_equipment_required",
            "Home Medical Device or Equipment Required",
            "boolean",
            "home-equipment-required",
            "퇴원 후 집에서 사용해야 하는 의료기기나 장비가 있나요?",
            201,
        ),
        q(
            "post_discharge.home_medical_device_or_equipment_type",
            "Home Medical Device or Equipment Type",
            "string",
            "home-equipment-type",
            "집에서 사용해야 하는 의료기기나 장비의 이름 또는 종류를 알려주세요.",
            200,
        ),
        q(
            "post_discharge.home_medical_device_or_equipment_received",
            "Home Medical Device or Equipment Received",
            "boolean",
            "home-equipment-received",
            "필요한 의료기기나 장비를 실제로 받았나요?",
            199,
        ),
        q(
            "post_discharge.home_medical_device_or_equipment_use_training_received",
            "Home Medical Device or Equipment Use Training Received",
            "boolean",
            "home-equipment-training",
            "그 의료기기나 장비의 사용법을 직접 설명받거나 시범으로 확인했나요?",
            198,
        ),
        q(
            "post_discharge.home_medical_device_or_equipment_use_difficulty",
            "Difficulty Using Home Medical Device or Equipment",
            "boolean",
            "home-equipment-difficulty",
            "환자나 보호자가 그 의료기기나 장비를 실제로 사용하는 데 어려움이 있나요?",
            197,
        ),
        q(
            "post_discharge.home_medical_device_or_equipment_help_contact_known",
            "Home Medical Device or Equipment Help Contact Known",
            "boolean",
            "home-equipment-contact",
            "장비가 도착하지 않거나 사용 중 문제가 생겼을 때 연락할 곳을 알고 있나요?",
            196,
        ),
    ]
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())
    doc.update(
        {
            "version": VERSION,
            "lifecycle_status": "draft",
            "review_status": "unreviewed",
            "clinical_use_status": "limited",
            "clinical_use_policy_ref": "policies/draft-clinical-use-boundary.json",
            "usage_modes": ["research_test", "simulation", "clinician_supervised_pilot"],
            "updated_at": UPDATED,
        }
    )
    doc["default_refresh"].update(
        {
            "last_assessed_at": "2026-08-16",
            "next_monitor_at": "2026-08-17",
            "next_full_review_at": "2027-02-12",
        }
    )
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc: dict) -> dict:
    result = seed_post_discharge_follow_up.completion(doc)
    result["required_facts"]["always"] = list(
        dict.fromkeys(
            [
                *result["required_facts"]["always"],
                "post_discharge.wound_care_task_required",
                "post_discharge.home_medical_device_or_equipment_required",
            ]
        )
    )
    result["conditional_required_facts"].extend(
        [
            {
                "when": {"fact": "post_discharge.wound_care_task_required", "equals": True},
                "required_facts": [
                    "post_discharge.wound_care_task_description",
                    "post_discharge.wound_care_instructions_available",
                    "post_discharge.wound_care_skill_difficulty",
                    "post_discharge.wound_care_help_contact_known",
                ],
                "reason": "post_discharge_wound_care_handoff",
            },
            {
                "when": {
                    "fact": "post_discharge.home_medical_device_or_equipment_required",
                    "equals": True,
                },
                "required_facts": [
                    "post_discharge.home_medical_device_or_equipment_type",
                    "post_discharge.home_medical_device_or_equipment_received",
                    "post_discharge.home_medical_device_or_equipment_help_contact_known",
                ],
                "reason": "post_discharge_home_equipment_handoff",
            },
            {
                "when": {
                    "fact": "post_discharge.home_medical_device_or_equipment_received",
                    "equals": True,
                },
                "required_facts": [
                    "post_discharge.home_medical_device_or_equipment_use_training_received",
                    "post_discharge.home_medical_device_or_equipment_use_difficulty",
                ],
                "reason": "post_discharge_home_equipment_use_handoff",
            },
        ]
    )
    result["question_budget"] = {"routine": 50, "clarify": 10}
    result.update(
        {
            "version": VERSION,
            "lifecycle_status": "draft",
            "review_status": "unreviewed",
            "clinical_use_status": "limited",
            "clinical_use_policy_ref": "policies/draft-clinical-use-boundary.json",
            "updated_at": UPDATED,
        }
    )
    result["provenance"] = provenance(SOURCES)
    return result


def sources() -> dict:
    doc = load(RESEARCH)
    artifacts = {item["id"]: item for item in doc["artifacts"]}
    artifacts["source.ahrq.red-toolkit.current-20260731"].update(
        {
            "version": "current-web-accessed-2026-08-16",
            "last_monitored_at": "2026-08-16",
            "next_monitor_at": "2026-08-23",
            "monitor_result": "current_official_toolkit_confirmed",
            "recommendation_change_detected": False,
            "assertions": [
                "Post-discharge handoff distinguishes required equipment, equipment receipt, use education, use difficulty and a help contact.",
                "The interview records patient or caregiver reports and does not certify safe device use or arrange equipment.",
            ],
        }
    )
    artifacts[CMS_SOURCE] = {
        "id": CMS_SOURCE,
        "kind": "official_discharge_planning_checklist_metadata",
        "publisher": "U.S. Centers for Medicare & Medicaid Services",
        "title": "Your Discharge Planning Checklist",
        "version": "official-pdf-accessed-2026-08-16",
        "url": "https://www.cms.gov/medicare/provider-enrollment-and-certification/qapi/downloads/qapi-discharge-planning-checklist.pdf",
        "language": "en",
        "digest": "metadata_and_targeted_summary_only",
        "license_status": "us_federal_publication_rights_reviewed_for_metadata_and_summary",
        "complete": False,
        "monitor_profile": "public_health_guidance",
        "last_monitored_at": "2026-08-16",
        "next_monitor_at": "2026-08-23",
        "monitor_result": "official_checklist_available",
        "recommendation_change_detected": False,
        "assertions": [
            "Discharge preparation includes identifying medical equipment, a contact for equipment questions and hands-on confirmation of special care tasks such as changing a bandage.",
            "Atomic interview facts preserve whether wound-care instructions exist, whether the task is difficult and whether a help contact is known.",
        ],
    }
    artifacts[STOM_MONITOR] = {
        "id": STOM_MONITOR,
        "kind": "terminology_service_monitor",
        "publisher": "STOM",
        "title": "Post-discharge atomic question terminology verification attempt",
        "version": "attempted-2026-08-16",
        "url": "http://localhost:8088/fhir",
        "language": "en",
        "digest": "no_response_cached",
        "license_status": "licensed_service_no_content_redistributed",
        "complete": False,
        "monitor_profile": "terminology_server",
        "last_monitored_at": "2026-08-16",
        "next_monitor_at": "2026-08-17",
        "monitor_result": "connection_refused_no_terminology_assertion",
        "recommendation_change_detected": False,
        "assertions": [
            "No exact or equivalent standard question mapping was asserted while the configured local terminology service was unavailable.",
            "All new contextual questions retain local question codes pending verified terminology review.",
        ],
    }
    doc.update(
        {
            "version": VERSION,
            "lifecycle_status": "draft",
            "review_status": "unreviewed",
            "clinical_use_status": "limited",
            "updated_at": UPDATED,
            "artifacts": list(artifacts.values()),
        }
    )
    doc["provenance"] = provenance([item["id"] for item in doc["artifacts"]])
    return doc


def mapping(doc: dict) -> dict:
    result = load(MAPPING)
    result.update(
        {
            "version": VERSION,
            "lifecycle_status": "draft",
            "review_status": "unreviewed",
            "clinical_use_status": "limited",
            "clinical_use_policy_ref": "policies/draft-clinical-use-boundary.json",
            "atomic_refactoring": {
                "retired_composite_facts": ["post_discharge.wound_or_device_plan"],
                "replacement_strategy": "atomic_local_questions_for_wound_care_and_home_equipment",
                "exact_mapping_for_new_contextual_questions": False,
                "question_code_remains_local": True,
            },
        }
    )
    result["question_mapping"].update(
        {
            "exact_standard_question_count": 0,
            "local_atomic_question_count": len(doc["entries"]),
            "compound_question_exact_mapping_allowed": False,
            "rationale": "The legacy composite was split before mapping. The configured STOM endpoint was unavailable, so contextual questions remain local without inferred equivalence.",
        }
    )
    result["validation"].update(
        {
            "method": "build_time_local_fhir_lookup_attempt",
            "checked_at": UPDATED,
            "result": "stom_connection_refused_local_questions_retained",
        }
    )
    result["provenance"] = provenance([STOM_MONITOR])
    return result


def clinician(result_policy: dict) -> dict:
    doc = load(CLINICIAN)
    minimum = doc["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]
    existing = minimum["rfe.post_discharge_follow_up"]
    minimum["rfe.post_discharge_follow_up"] = list(
        dict.fromkeys(
            [
                *existing,
                "post_discharge.wound_care_task_required",
                "post_discharge.home_medical_device_or_equipment_required",
            ]
        )
    )
    doc["version"] = "0.7.9"
    doc["provenance"]["version"] = "0.7.9"
    doc["updated_at"] = UPDATED
    return doc


def cases(doc: dict) -> dict[str, dict]:
    result = seed_post_discharge_follow_up.simulations(doc)
    for case in result.values():
        case["hidden_state"].update(
            {
                "post_discharge.wound_care_task_required": {"value": False},
                "post_discharge.home_medical_device_or_equipment_required": {"value": False},
            }
        )
        case["provenance"] = provenance(SOURCES)

    wound = seed_post_discharge_follow_up.routine_state()
    wound.update(
        {
            "post_discharge.wound_care_task_required": {"value": True},
            "post_discharge.wound_care_task_description": {"value": "복부 수술 부위 드레싱 교환"},
            "post_discharge.wound_care_instructions_available": {"value": True},
            "post_discharge.wound_care_skill_difficulty": {"value": True},
            "post_discharge.wound_care_help_contact_known": {"value": False},
            "post_discharge.home_medical_device_or_equipment_required": {"value": False},
        }
    )
    equipment = seed_post_discharge_follow_up.routine_state()
    equipment.update(
        {
            "post_discharge.wound_care_task_required": {"value": False},
            "post_discharge.home_medical_device_or_equipment_required": {"value": True},
            "post_discharge.home_medical_device_or_equipment_type": {"value": "재택 산소 장비"},
            "post_discharge.home_medical_device_or_equipment_received": {"value": False},
            "post_discharge.home_medical_device_or_equipment_help_contact_known": {"value": False},
        }
    )
    common = {
        "expected_safety_level": "routine",
        "expected_stop_reason": "required_targets_addressed_with_absent_data",
        "expected_max_turns": 64,
        "expected_clinician_handoff": True,
        "forbidden_assertions": [
            "diagnosis.post_discharge_complication",
            "recommendation.perform_wound_care",
            "recommendation.change_device_settings",
        ],
    }
    result["POST-DISCHARGE-WOUND-CARE-SKILL-GAP.json"] = {
        "id": "POST-DISCHARGE-WOUND-CARE-SKILL-GAP",
        "simulation_language": "ko",
        "persona": {"age": 79},
        "initial_statement": {"ko": "보호자가 수술 후 드레싱을 갈아야 하는데 실제로 하기가 어렵고 문의할 곳을 모르겠습니다."},
        "encounter_context": {
            "care_setting": "primary_care",
            "encounter_type": "follow_up",
            "interview_initiator": "caregiver",
            "interview_mode": "telephone",
            "available_information": ["partial_discharge_instructions"],
            "time_constraint": "scheduled",
            "clinical_responsibility": "follow_up_support",
        },
        "clinician_submission": True,
        "hidden_state": wound,
        "expected": {
            **common,
            "expected_selected_facts_contains": [
                "post_discharge.wound_care_task_description",
                "post_discharge.wound_care_instructions_available",
                "post_discharge.wound_care_skill_difficulty",
                "post_discharge.wound_care_help_contact_known",
            ],
        },
        "provenance": provenance(SOURCES),
    }
    result["POST-DISCHARGE-HOME-EQUIPMENT-NOT-RECEIVED.json"] = {
        "id": "POST-DISCHARGE-HOME-EQUIPMENT-NOT-RECEIVED",
        "simulation_language": "ko",
        "persona": {"age": 68},
        "initial_statement": {"ko": "퇴원 전에 집에서 쓸 산소 장비가 온다고 했는데 아직 받지 못했고 연락처도 모릅니다."},
        "encounter_context": {
            "care_setting": "telemedicine",
            "encounter_type": "follow_up",
            "interview_initiator": "patient",
            "interview_mode": "video",
            "available_information": ["discharge_summary"],
            "time_constraint": "scheduled",
            "clinical_responsibility": "follow_up_support",
        },
        "clinician_submission": True,
        "hidden_state": equipment,
        "expected": {
            **common,
            "expected_selected_facts_contains": [
                "post_discharge.home_medical_device_or_equipment_type",
                "post_discharge.home_medical_device_or_equipment_received",
                "post_discharge.home_medical_device_or_equipment_help_contact_known",
            ],
        },
        "provenance": provenance(SOURCES),
    }
    return result


def main() -> None:
    seed_post_discharge_follow_up.main()
    doc = fragment()
    result_policy = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, result_policy)
    write_json(RESEARCH, sources())
    write_json(MAPPING, mapping(doc))
    write_json(CLINICIAN, clinician(result_policy))
    for name, case in cases(doc).items():
        write_json(f"simulation/patients/follow-up/post-discharge/{name}", case)


if __name__ == "__main__":
    main()
