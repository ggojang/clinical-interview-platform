#!/usr/bin/env python3
"""Strengthen draft allergy follow-up and adrenaline autoinjector handoff."""
from __future__ import annotations

import json

import seed_allergy_concern
from profile_support import ROOT, completion_policy, entry, write_json


P = "allergy-concern"
FRAGMENT = "knowledge/generated/allergy/allergy-concern/allergy-concern.json"
POLICY = "policies/primary-care-allergy-concern-completion.json"
RESEARCH = "sources/manifests/primary-care-allergy-concern-research.json"
MAPPING = "mappings/terminology/snomed-mrcm-allergy-concern.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
CREATED = "2026-08-15T00:00:00Z"
UPDATED = "2026-08-15T00:00:00Z"
SOURCES = [
    "source.nice.ng258.anaphylaxis.2026",
    "source.mhra.adrenaline-autoinjector-safe-use.2023",
    "source.hl7.fhir-r4.allergyintolerance.4.0.1",
    "source.stom.allergy-follow-up.20260815",
]
G = {key: f"group.allergy.{key}" for key in (
    "routing", "common", "anaphylaxis-follow-up",
)}
C = ["intent.characterize_symptom"]
R = ["intent.risk_assessment"]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def provenance(source_refs: list[str]) -> dict:
    return {
        "created_by": {"type": "ai", "id": "codex-gpt5"},
        "created_at": CREATED,
        "source_refs": source_refs,
        "review_status": "unreviewed",
        "version": "0.2.0",
    }


def q(fact_id, display, value_type, key, wording, score, **kwargs):
    return entry(
        P, fact_id, display, value_type, key, wording, score, key,
        [G["anaphylaxis-follow-up"]], intents=R, **kwargs,
    )


def fragment() -> dict:
    doc = load(FRAGMENT)
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.pop("allergy.specialist_testing_and_emergency_plan", None)
    additions = [
        q("allergy.anaphylaxis_follow_up_context", "Anaphylaxis Follow-up Context", "boolean", "anaphylaxis-follow-up-context", "이미 회복한 심한 전신 알레르기 반응 뒤 자가주사기·행동계획·전문진료 준비 상태를 확인하려는 방문인가요?", 147),
        q("allergy.adrenaline_autoinjector_prescribed", "Adrenaline Autoinjector Prescribed", "boolean", "aai-prescribed", "의료진에게 아드레날린 자가주사기를 처방받은 적이 있나요?", 146),
        q("allergy.adrenaline_autoinjector_currently_available", "Adrenaline Autoinjector Currently Available", "boolean", "aai-available", "현재 바로 사용할 수 있는 아드레날린 자가주사기를 가지고 있나요?", 145),
        q("allergy.adrenaline_autoinjector_count_available", "Adrenaline Autoinjector Count Available", "integer", "aai-count", "현재 가지고 다니거나 바로 꺼낼 수 있는 아드레날린 자가주사기는 몇 개인가요?", 144, minimum=0),
        q("allergy.adrenaline_autoinjector_in_date_confirmed", "Adrenaline Autoinjector In-date Status Confirmed", "boolean", "aai-in-date", "현재 가진 자가주사기의 유효기간이 지나지 않았는지 확인했나요?", 143),
        q("allergy.adrenaline_autoinjector_earliest_expiry_date", "Earliest Adrenaline Autoinjector Expiry Date", "date_or_period", "aai-expiry", "가장 먼저 유효기간이 끝나는 자가주사기의 날짜를 알려주세요. 정확히 모르면 대략적인 시기나 모른다고 답해도 됩니다.", 142),
        q("allergy.adrenaline_autoinjector_device_name_or_brand", "Adrenaline Autoinjector Device Name or Brand", "string", "aai-device", "현재 처방받은 자가주사기의 제품명이나 기기 이름을 알려주세요. 보기에 없어도 자유롭게 입력할 수 있습니다.", 141),
        q("allergy.adrenaline_autoinjector_training_received", "Adrenaline Autoinjector Training Received", "boolean", "aai-training", "현재 처방된 기기의 사용법을 의료진에게 배우거나 연습용 기기로 연습한 적이 있나요?", 140),
        q("allergy.adrenaline_autoinjector_technique_confidence_or_gap", "Adrenaline Autoinjector Technique Confidence or Gap", "string", "aai-technique-gap", "자가주사기를 언제 어떻게 사용할지 본인이나 보호자가 어느 정도 알고 있으며, 다시 확인하고 싶은 부분은 무엇인가요?", 139),
        q("allergy.written_emergency_action_plan_available", "Written Allergy Emergency Action Plan Available", "boolean", "written-action-plan", "알레르기 반응이 생겼을 때 따를 서면 응급 행동계획을 가지고 있나요?", 138),
        q("allergy.specialist_allergy_referral_status", "Specialist Allergy Referral Status", "string", "specialist-referral", "알레르기 전문진료 의뢰 여부와 예약·진료 진행 상태를 알려주세요. 보기에 없어도 자유롭게 입력할 수 있습니다.", 137),
        q("allergy.specialist_allergy_testing_result", "Specialist Allergy Testing Result", "string", "specialist-testing-result", "전문진료에서 받은 검사와 설명받은 결과, 아직 기다리는 결과가 있다면 각각 알려주세요.", 136),
    ]
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    nodes[G["anaphylaxis-follow-up"]] = {
        "id": G["anaphylaxis-follow-up"],
        "type": "ClinicalGroup",
        "display": "Anaphylaxis Follow-up",
    }
    doc["extra_nodes"] = list(nodes.values())
    doc.update({
        "version": "0.2.0",
        "lifecycle_status": "draft",
        "review_status": "unreviewed",
        "clinical_use_status": "limited",
        "clinical_use_policy_ref": "policies/draft-clinical-use-boundary.json",
        "usage_modes": ["research_test", "simulation", "clinician_supervised_pilot"],
        "updated_at": UPDATED,
    })
    doc["default_refresh"].update({
        "last_assessed_at": "2026-08-15",
        "next_monitor_at": "2026-08-16",
        "next_full_review_at": "2027-02-11",
    })
    doc["provenance"] = provenance([
        *seed_allergy_concern.SOURCES,
        "source.mhra.adrenaline-autoinjector-safe-use.2023",
        "source.stom.allergy-follow-up.20260815",
    ])
    return doc


def policy(doc: dict) -> dict:
    result = completion_policy(
        prefix=P, fragment=doc, presentation_fact="allergy.primary_group",
        question_budget=72,
        source_refs=[*seed_allergy_concern.SOURCES, *SOURCES],
    )
    result["required_facts"]["routine"] = [
        "allergy.current_or_historical_episode",
        "allergy.suspected_trigger_and_latency",
        "allergy.symptom_sequence_and_systems",
        "allergy.treatment_and_response",
        "allergy.prior_similar_reaction",
        "allergy.known_allergies_and_avoidance",
        "allergy.current_medicines_and_risk_modifiers",
        "allergy.other_detail_or_patient_priority",
    ]
    branches = seed_allergy_concern.completion(doc)["conditional_required_facts"][0]["cases"]
    branches["acute_systemic"] = list(dict.fromkeys([
        *branches["acute_systemic"],
        "allergy.anaphylaxis_follow_up_context",
    ]))
    followup = [
        "allergy.adrenaline_autoinjector_prescribed",
        "allergy.written_emergency_action_plan_available",
        "allergy.specialist_allergy_referral_status",
        "allergy.specialist_allergy_testing_result",
        "allergy.asthma_cardiovascular_mast_cell_context",
        "allergy.pregnancy_age_and_care_context",
    ]
    result["conditional_required_facts"] = [
        {"selector_fact": "allergy.primary_group", "cases": branches},
        {
            "when": {
                "fact": "allergy.anaphylaxis_follow_up_context",
                "equals": True,
            },
            "required_facts": followup,
        },
        {
            "when": {
                "fact": "allergy.adrenaline_autoinjector_prescribed",
                "equals": True,
            },
            "required_facts": [
                "allergy.adrenaline_autoinjector_currently_available",
                "allergy.adrenaline_autoinjector_count_available",
                "allergy.adrenaline_autoinjector_in_date_confirmed",
                "allergy.adrenaline_autoinjector_earliest_expiry_date",
                "allergy.adrenaline_autoinjector_device_name_or_brand",
                "allergy.adrenaline_autoinjector_training_received",
                "allergy.adrenaline_autoinjector_technique_confidence_or_gap",
            ],
        },
    ]
    result.update({
        "version": "0.2.0",
        "lifecycle_status": "draft",
        "review_status": "unreviewed",
        "clinical_use_status": "limited",
        "clinical_use_policy_ref": "policies/draft-clinical-use-boundary.json",
        "updated_at": UPDATED,
    })
    result["provenance"] = provenance([*seed_allergy_concern.SOURCES, *SOURCES])
    return result


def sources() -> dict:
    doc = load(RESEARCH)
    for artifact in doc["artifacts"]:
        if artifact["id"] == "source.nice.ng258.anaphylaxis.2026":
            artifact.update({
                "version": "NG258-published-2026-05-27-reviewed-2026-06-04-accessed-2026-08-15",
                "last_monitored_at": "2026-08-15",
                "next_monitor_at": "2026-08-22",
                "monitor_result": "current_official_guidance_and_public_information_confirmed",
                "recommendation_change_detected": False,
                "assertions": [
                    "After emergency treatment, handoff preserves the suspected trigger, reaction course, treatment response, specialist referral and written information or action-plan status.",
                    "People at ongoing risk should have two adrenaline autoinjectors and know when and how to use them; the interview records preparedness without prescribing or replacing training.",
                ],
            })
    additions = [
        {
            "id": "source.mhra.adrenaline-autoinjector-safe-use.2023",
            "kind": "official_medicines_safety_guidance",
            "publisher": "UK Medicines and Healthcare products Regulatory Agency",
            "title": "Adrenaline auto-injectors: reminder for prescribers to support safe and effective use",
            "version": "published-2023-06-19-accessed-2026-08-15",
            "url": "https://www.gov.uk/drug-safety-update/adrenaline-auto-injectors-reminder-for-prescribers-to-support-safe-and-effective-use",
            "language": "en",
            "digest": "metadata_and_targeted_safety_summary_only",
            "license_status": "open_government_licence_v3",
            "complete": False,
            "monitor_profile": "medicine_safety_guidance",
            "last_monitored_at": "2026-08-15",
            "next_monitor_at": "2026-08-16",
            "monitor_result": "current_official_safety_update_confirmed",
            "recommendation_change_detected": False,
            "assertions": [
                "Preparedness review distinguishes carrying two in-date devices, expiry replacement, prescribed-device training and technique confidence.",
                "The package only records current readiness and gaps for clinician handoff; it does not prescribe, replace device-specific instruction or delay emergency care.",
            ],
        },
        {
            "id": "source.stom.allergy-follow-up.20260815",
            "kind": "terminology_service_verification",
            "publisher": "Infoclinic",
            "title": "STOM adrenaline autoinjector and allergy-referral terminology verification",
            "version": "SNOMEDCT-20260801",
            "url": "http://localhost:8088/fhir",
            "language": "en",
            "digest": "snomed_468846009_306111000_verified",
            "license_status": "licensed_lookup_metadata_only",
            "complete": False,
            "monitor_profile": "terminology_server",
            "last_monitored_at": "2026-08-15",
            "next_monitor_at": "2026-09-14",
            "monitor_result": "verified_active_related_concepts",
            "recommendation_change_detected": False,
            "assertions": [
                "STOM returned active SNOMED CT concepts for Epinephrine autoinjector (physical object) and Referral to clinical allergy service (procedure).",
                "Preparedness, possession, expiry, training and referral-status questions remain local because these related concepts are not exact equivalents of the contextual questions.",
            ],
        },
    ]
    artifacts = {artifact["id"]: artifact for artifact in doc["artifacts"]}
    artifacts.update({artifact["id"]: artifact for artifact in additions})
    doc["artifacts"] = list(artifacts.values())
    doc.update({
        "version": "0.2.0",
        "lifecycle_status": "draft",
        "review_status": "unreviewed",
        "clinical_use_status": "limited",
        "updated_at": UPDATED,
    })
    doc["provenance"] = provenance([item["id"] for item in doc["artifacts"]])
    return doc


def mapping() -> dict:
    doc = load(MAPPING)
    concepts = {item["code"]: item for item in doc["focus_concepts"]}
    concepts.update({
        "468846009": {
            "code": "468846009",
            "display": "Epinephrine autoinjector (physical object)",
            "concept_active": True,
            "mapping_status": "active_related_candidate_returned",
        },
        "306111000": {
            "code": "306111000",
            "display": "Referral to clinical allergy service (procedure)",
            "concept_active": True,
            "mapping_status": "active_related_candidate_returned",
        },
    })
    doc.update({
        "version": "0.2.0",
        "lifecycle_status": "draft",
        "review_status": "unreviewed",
        "clinical_use_status": "limited",
        "clinical_use_policy_ref": "policies/draft-clinical-use-boundary.json",
        "focus_concepts": list(concepts.values()),
        "terminology": {
            "system": "http://snomed.info/sct",
            "version": "http://snomed.info/sct/900000000000207008/version/20260801",
            "source": "STOM localhost:8088/fhir",
        },
        "related_concept_candidates": [
            {"code": "468846009", "display": "Epinephrine autoinjector (physical object)", "relation": "related_not_exact"},
            {"code": "306111000", "display": "Referral to clinical allergy service (procedure)", "relation": "related_not_exact"},
        ],
        "atomic_refactoring": {
            "retired_composite_facts": ["allergy.specialist_testing_and_emergency_plan"],
            "replacement_strategy": "atomic_local_questions_with_related_standard_concepts_only",
            "exact_mapping_for_new_contextual_questions": False,
            "question_code_remains_local": True,
        },
        "validation": {
            "method": "build_time_live_stom_filter_search",
            "checked_at": UPDATED,
            "raw_response_cached": False,
            "complete_mrcm_snapshot": False,
            "clinical_rule_authority": False,
            "result": "related_concepts_verified_contextual_questions_remain_local",
        },
    })
    doc["provenance"] = provenance(["source.stom.allergy-follow-up.20260815"])
    return doc


def clinician(result_policy: dict) -> dict:
    doc = load(CLINICIAN)
    minimum = doc["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]
    minimum["rfe.allergy_concern"] = list(result_policy["required_facts"]["routine"])
    doc["version"] = "0.7.8"
    doc["provenance"]["version"] = "0.7.8"
    doc["updated_at"] = UPDATED
    return doc


def cases(doc: dict, result_policy: dict) -> dict[str, dict]:
    facts = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    branches = result_policy["conditional_required_facts"][0]["cases"]
    followup = result_policy["conditional_required_facts"][1]["required_facts"]
    prescribed = result_policy["conditional_required_facts"][2]["required_facts"]

    def default_value(fact_id: str):
        fact = facts[fact_id]
        if fact["value_type"] == "boolean":
            return False
        if fact["value_type"] == "integer":
            return 0
        if fact["value_type"] == "coded":
            return fact.get("allowed_values", ["other"])[-1]
        return "특이사항 없음"

    ids = dict.fromkeys([
        *result_policy["required_facts"]["always"],
        *result_policy["required_facts"]["routine"],
        *branches["acute_systemic"],
        *followup,
        *prescribed,
    ])
    base = {fact_id: {"value": default_value(fact_id)} for fact_id in ids}
    base.update({
        "allergy.primary_group": {"value": "acute_systemic"},
        "allergy.current_or_historical_episode": {"value": "historical"},
        "allergy.anaphylaxis_follow_up_context": {"value": True},
        "allergy.adrenaline_autoinjector_prescribed": {"value": True},
    })
    forbidden = [
        "diagnosis.anaphylaxis_confirmed",
        "recommendation.prescribe_adrenaline_autoinjector",
        "recommendation.replace_device_specific_training",
        "recommendation.change_allergy_treatment",
    ]
    prepared = {key: dict(value) for key, value in base.items()}
    prepared.update({
        "allergy.adrenaline_autoinjector_currently_available": {"value": True},
        "allergy.adrenaline_autoinjector_count_available": {"value": 2},
        "allergy.adrenaline_autoinjector_in_date_confirmed": {"value": True},
        "allergy.adrenaline_autoinjector_earliest_expiry_date": {"value": "2027-03"},
        "allergy.adrenaline_autoinjector_device_name_or_brand": {"value": "처방 기기명은 사진으로 확인 가능"},
        "allergy.adrenaline_autoinjector_training_received": {"value": True},
        "allergy.adrenaline_autoinjector_technique_confidence_or_gap": {"value": "본인과 배우자가 연습용 기기로 교육받음"},
        "allergy.written_emergency_action_plan_available": {"value": True},
        "allergy.specialist_allergy_referral_status": {"value": "전문진료 완료, 정기 추적 예정"},
        "allergy.specialist_allergy_testing_result": {"value": "검사 결과지는 있으며 진료 시 제출 예정"},
    })
    gap = {key: dict(value) for key, value in base.items()}
    gap.update({
        "allergy.adrenaline_autoinjector_currently_available": {"value": True},
        "allergy.adrenaline_autoinjector_count_available": {"value": 1},
        "allergy.adrenaline_autoinjector_in_date_confirmed": {"value": False},
        "allergy.adrenaline_autoinjector_device_name_or_brand": {"value": "제품명은 사진 확인 필요"},
        "allergy.adrenaline_autoinjector_training_received": {"value": False},
        "allergy.adrenaline_autoinjector_technique_confidence_or_gap": {"value": "언제 사용하고 두 번째 기기를 어떻게 준비하는지 확인 필요"},
        "allergy.written_emergency_action_plan_available": {"value": False},
        "allergy.specialist_allergy_referral_status": {"value": "의뢰 여부 확인 필요"},
        "allergy.specialist_allergy_testing_result": {"value": "검사받았는지 기억이 불확실함"},
    })
    gap.pop("allergy.adrenaline_autoinjector_earliest_expiry_date")
    common_expected = {
        "expected_safety_level": "routine",
        "expected_max_turns": 72,
        "expected_clinician_handoff": True,
        "forbidden_assertions": forbidden,
    }
    return {
        "ALLERGY-AAI-PREPAREDNESS-FOLLOWUP.json": {
            "id": "ALLERGY-AAI-PREPAREDNESS-FOLLOWUP",
            "simulation_language": "ko",
            "persona": {"age": 38},
            "initial_statement": {"ko": "이전에 심한 알레르기 반응으로 치료받아 자가주사기와 후속관리 상태를 진료 전에 정리하고 싶어요."},
            "hidden_state": prepared,
            "encounter_context": {
                "care_setting": "specialist_clinic", "encounter_type": "follow_up",
                "interview_initiator": "patient", "interview_mode": "chat",
                "available_information": ["patient_device_report", "prior_discharge_document"],
                "time_constraint": "scheduled", "clinical_responsibility": "follow_up_support",
            },
            "clinician_submission": True,
            "expected": {
                **common_expected,
                "expected_stop_reason": "required_targets_addressed_with_absent_data",
                "expected_selected_facts_contains": [
                    "allergy.adrenaline_autoinjector_count_available",
                    "allergy.adrenaline_autoinjector_in_date_confirmed",
                    "allergy.adrenaline_autoinjector_training_received",
                    "allergy.written_emergency_action_plan_available",
                    "allergy.specialist_allergy_referral_status",
                ],
            },
            "provenance": provenance(SOURCES),
        },
        "ALLERGY-AAI-EXPIRY-TRAINING-GAPS.json": {
            "id": "ALLERGY-AAI-EXPIRY-TRAINING-GAPS",
            "simulation_language": "ko",
            "persona": {"age": 67},
            "initial_statement": {"ko": "예전에 응급실 치료 후 자가주사기를 받았지만 한 개만 있고 유효기간과 사용법을 잘 모르겠습니다."},
            "hidden_state": gap,
            "response_behavior": {
                "allergy.adrenaline_autoinjector_earliest_expiry_date": {"dataAbsentReason": "asked-unknown"},
            },
            "encounter_context": {
                "care_setting": "telemedicine", "encounter_type": "follow_up",
                "interview_initiator": "patient", "interview_mode": "video",
                "available_information": ["no_previous_records"],
                "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
            },
            "clinician_submission": True,
            "expected": {
                **common_expected,
                "expected_stop_reason": "required_targets_addressed_with_absent_data",
                "expected_data_absent_reasons": {
                    "allergy.adrenaline_autoinjector_earliest_expiry_date": "asked-unknown",
                },
                "expected_selected_facts_contains": [
                    "allergy.adrenaline_autoinjector_count_available",
                    "allergy.adrenaline_autoinjector_in_date_confirmed",
                    "allergy.adrenaline_autoinjector_training_received",
                    "allergy.written_emergency_action_plan_available",
                ],
            },
            "provenance": provenance(SOURCES),
        },
    }


def main() -> None:
    seed_allergy_concern.main()
    doc = fragment()
    result_policy = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, result_policy)
    write_json(RESEARCH, sources())
    write_json(MAPPING, mapping())
    write_json(CLINICIAN, clinician(result_policy))
    for name, case in cases(doc, result_policy).items():
        write_json(f"simulation/patients/allergy/allergy-concern/{name}", case)


if __name__ == "__main__":
    main()
