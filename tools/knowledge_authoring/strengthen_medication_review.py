#!/usr/bin/env python3
"""Strengthen research-only medication-review knowledge for clinician handoff."""
from __future__ import annotations

import seed_medication_review
from profile_support import *


P = "medication-review"
FRAGMENT = "knowledge/generated/medication/medication-review/medication-review.json"
POLICY = "policies/primary-care-medication-review-completion.json"
RESEARCH = "sources/manifests/primary-care-medication-review-research.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
SIM_ROOT = ROOT / "simulation/patients/medication/medication-review"
SOURCES = [
    "source.nice.ng5.medicines-optimisation.2019",
    "source.nice.cg183.drug-allergy.2014",
    "source.nhs.poisoning.2025",
    "source.nhs.anticoagulant-bleeding.2024",
    "source.nhs.anaphylaxis.2026",
    "source.nhs.stevens-johnson.2026",
    "source.nhs.hypoglycaemia.2026",
    "source.nhs-england.opioid-respiratory-depression.2020",
    "source.stom.mrcm.medication-review.20260714",
]
G = {key: f"group.medication-review.{key}" for key in (
    "immediate-safety", "reconciliation", "actual-use", "benefit-harm",
    "monitoring-risk", "preference-support", "structured-list",
    "source-verification", "adherence-support", "adverse-detail",
    "transition", "functional-safety", "clinician-handoff",
)}
RECONCILE = ["intent.medication_reconciliation"]
REVIEW = ["intent.medication_review"]
RISK = ["intent.risk_assessment"]
SAFETY = ["intent.screen_red_flags"]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def q(fid, display, vt, key, wording, score, group, intents, **kwargs):
    return entry(
        P, fid, display, vt, key, wording, score, key, [G[group]],
        intents=intents, **kwargs,
    )


def fragment():
    doc = load(FRAGMENT)
    additions = [
        q("medication.list_source_last_reconciled_and_date", "Medication List Source and Reconciliation Date", "string", "list-source", "현재 약 목록은 본인 기억, 약 봉투·처방전, 의무기록, 보호자, 약국 중 무엇을 근거로 했고 마지막으로 의료진과 대조한 날짜는 언제인가요?", 111, "source-verification", RECONCILE + RISK),
        q("medication.list_conflict_unknown_and_verification_needed", "Medication Information Conflict and Verification Need", "string", "list-conflict", "약 이름·용량·복용법이 자료마다 다르거나 확인되지 않은 항목과 추가 확인이 필요한 약국·의료기관을 알려주세요.", 110, "source-verification", RECONCILE + RISK),
        q("medication.item_name_brand_generic_product_and_code", "Medicine Name Product and Code Detail", "string", "item-name", "각 약의 제품명과 성분명, 제조사·식별문자 또는 제공된 약제코드가 있으면 약별로 알려주세요.", 109, "structured-list", RECONCILE),
        q("medication.item_strength_formulation_and_unit", "Medicine Strength Formulation and Unit", "string", "item-strength", "각 약의 함량·단위와 정제, 캡슐, 액상, 흡입제, 주사, 패치 같은 제형을 약별로 알려주세요.", 108, "structured-list", RECONCILE),
        q("medication.item_dose_route_frequency_timing_and_prn", "Medicine Dose Route Frequency Timing and PRN", "string", "item-regimen", "각 약의 1회량, 투여경로, 하루·주당 횟수, 식전·식후·취침 전 같은 시간과 필요 시 복용 조건을 알려주세요.", 107, "structured-list", RECONCILE),
        q("medication.item_indication_start_date_prescriber_and_pharmacy", "Medicine Indication Start Date Prescriber and Pharmacy", "string", "item-context", "각 약을 사용하는 이유, 시작 시점, 처방한 의료기관·진료과와 조제 약국을 알고 있는 범위에서 알려주세요.", 106, "structured-list", RECONCILE),
        q("medication.last_actual_dose_by_item", "Last Actual Dose by Medicine", "string", "last-actual-dose", "최근 복용·투여한 시각이 중요한 약은 약별 마지막 실제 사용 시각을 알려주세요.", 96, "actual-use", RECONCILE + RISK),
        q("medication.stopped_held_expired_and_remaining_stock", "Stopped Held Expired Medicines and Remaining Stock", "string", "stopped-stock", "중단·보류했거나 유효기간이 지났지만 집에 남아 있는 약과 남은 수량, 중단 이유를 알려주세요.", 91, "reconciliation", RECONCILE + RISK),
        q("medication.unintentional_nonadherence_reason", "Unintentional Non-adherence Reason", "string", "unintentional-nonadherence", "깜빡함, 일정 변화, 복잡한 복용법, 삼킴·시력·손 사용·인지 문제 등 의도하지 않게 빠뜨리는 이유가 있나요?", 98, "adherence-support", RECONCILE + REVIEW),
        q("medication.adherence_aid_caregiver_and_administration_source", "Adherence Aid and Administration Support", "string", "adherence-support", "약 달력·약통·알람을 쓰는지, 누가 약을 준비·투여·확인하는지와 도움이 부족한 부분을 알려주세요.", 87, "adherence-support", RECONCILE + REVIEW),
        q("medication.swallowing_vision_dexterity_cognition_and_packaging", "Administration Accessibility Detail", "string", "accessibility", "알약 삼키기, 라벨 읽기, 포장 열기, 손으로 기구 조작하기, 용량 계산·기억하기 중 어려운 점을 알려주세요.", 86, "adherence-support", RECONCILE + REVIEW),
        q("medication.inhaler_injection_patch_device_technique_and_training", "Medicine Device Technique and Training", "string", "device-technique", "흡입기·주사·점안·패치 등 기구 사용법을 직접 확인받은 시점과 현재 사용 중 어려움·오류 의심을 알려주세요.", 85, "adherence-support", RECONCILE + REVIEW),
        q("allergy.drug_culprit_dose_route_onset_and_timing", "Drug Reaction Culprit Dose Route and Timing", "string", "allergy-timing", "약물 반응이 있었다면 원인 약, 당시 용량·투여경로, 복용 후 얼마 만에 어떤 순서로 시작했는지 알려주세요.", 105, "adverse-detail", REVIEW + RISK),
        q("allergy.drug_reaction_severity_treatment_outcome_and_reexposure", "Drug Reaction Severity Treatment Outcome and Re-exposure", "string", "allergy-outcome", "반응의 중증도, 응급치료·입원 여부, 회복 과정과 같은 약 또는 같은 계열을 다시 사용했을 때 반응을 알려주세요.", 104, "adverse-detail", REVIEW + RISK),
        q("allergy.drug_allergy_intolerance_or_uncertain_label", "Drug Allergy Intolerance or Uncertain Label", "coded", "allergy-label", "기록된 반응은 알레르기로 확인됨, 부작용·불내성, 가족력만 있음, 원인 불확실 중 어디에 해당하나요?", 97, "adverse-detail", REVIEW + RISK, allowed_values=["confirmed_allergy", "adverse_effect_or_intolerance", "family_history_only", "uncertain"]),
        q("medication.adverse_effect_onset_dose_relation_dechallenge_rechallenge", "Adverse Effect Temporal Relationship", "string", "adverse-timeline", "의심 부작용이 약 시작·증량 후 언제 생겼고 감량·중단 뒤 호전했는지, 다시 사용했을 때 재발했는지 알려주세요.", 103, "adverse-detail", REVIEW + RISK),
        q("medication.adverse_effect_severity_frequency_function_and_actions", "Adverse Effect Severity Frequency and Impact", "string", "adverse-impact", "의심 부작용의 빈도·중증도, 수면·식사·보행·운전·근무 영향과 이미 받은 조치를 알려주세요.", 102, "adverse-detail", REVIEW + RISK),
        q("medication.benefit_by_indication_target_and_time_course", "Benefit by Indication and Target", "string", "benefit-detail", "각 주요 약이 목표 증상·수치·기능에 얼마나 도움이 되었고 언제부터 효과가 나타났거나 줄었는지 알려주세요.", 88, "benefit-harm", REVIEW),
        q("medication.monitoring_test_name_last_date_result_trend_and_source", "Medicine Monitoring Test Result and Source", "string", "monitoring-result", "약과 관련해 받은 혈압·맥박·혈당, 혈액·소변검사, 심전도 또는 약물농도의 검사명, 최근 날짜·결과·추세와 자료 출처를 알려주세요.", 95, "monitoring-risk", REVIEW + RISK),
        q("medication.monitoring_target_due_date_and_unresolved_action", "Monitoring Target Due Date and Follow-up", "string", "monitoring-plan", "의료진이 정한 목표치·다음 검사 예정일과 결과 후 조치가 필요했지만 아직 확인하지 못한 항목이 있나요?", 90, "monitoring-risk", REVIEW + RISK),
        q("medication.renal_hepatic_function_date_result_and_dose_context", "Renal and Hepatic Function Result Context", "string", "organ-function", "최근 신장·간 기능검사의 날짜·결과와 그 결과로 용량을 조정하거나 약을 피하라는 설명을 들었는지 알려주세요.", 94, "monitoring-risk", REVIEW + RISK),
        q("medication.opioid_sedative_alcohol_sleep_apnoea_and_naloxone_context", "Opioid Sedative and Respiratory Risk Context", "string", "opioid-context", "마약성 진통제·수면제·진정제와 술을 함께 사용하는지, 수면무호흡·폐질환이 있는지, naloxone 교육·보유 여부를 알려주세요.", 101, "functional-safety", SAFETY + RISK),
        q("medication.drowsiness_confusion_dizziness_falls_driving_and_work", "Sedation Falls Driving and Work Impact", "string", "functional-safety", "약 사용 뒤 졸림·혼란·어지럼·휘청거림·낙상이 있었는지와 운전·기계조작·근무 안전에 미친 영향을 알려주세요.", 99, "functional-safety", REVIEW + RISK),
        q("medication.anticoagulant_indication_dose_last_dose_bleeding_and_monitoring", "Anticoagulant Regimen and Bleeding Context", "string", "anticoagulant-detail", "항응고제·항혈소판제를 사용한다면 이유, 약명·용량·마지막 복용, 멍·출혈과 관련 검사·다음 시술 계획을 알려주세요.", 100, "monitoring-risk", REVIEW + RISK),
        q("medication.diabetes_medicine_meal_pattern_glucose_and_hypoglycaemia", "Diabetes Medicine Meal and Hypoglycaemia Context", "string", "diabetes-detail", "인슐린·당뇨약을 사용한다면 식사와 투여 시각, 최근 혈당, 저혈당 횟수·대처와 도움 필요 여부를 알려주세요.", 100, "monitoring-risk", REVIEW + RISK),
        q("medication.care_transition_previous_current_discharge_list_conflict", "Care Transition Medication List Conflict", "string", "transition-conflict", "최근 입원·응급실·수술·전원 전 목록, 퇴원 목록과 현재 실제 복용 사이에 새로 시작·중단·변경되었거나 서로 다른 항목을 알려주세요.", 108, "transition", RECONCILE + RISK),
        q("medication.transition_change_reason_author_date_and_followup", "Care Transition Change Reason and Follow-up", "string", "transition-followup", "입퇴원 과정에서 누가 언제 어떤 이유로 약을 바꿨고, 어느 의료기관이 계속 처방·검사·추적하기로 했는지 알려주세요.", 96, "transition", RECONCILE + RISK),
        q("medication.supply_days_remaining_refill_access_and_storage", "Medicine Supply Refill Access and Storage", "string", "supply-detail", "약별 남은 일수, 다음 처방·조제 가능일, 비용·이동·품절 문제와 냉장·차광 등 보관 어려움을 알려주세요.", 84, "clinician-handoff", RECONCILE + REVIEW),
        q("medication.preference_tradeoff_change_request_and_constraints", "Medicine Preference Trade-off and Constraints", "string", "preference-detail", "효과, 부작용, 복용 횟수, 비용 중 무엇을 우선하며 바꾸거나 줄이고 싶은 약과 걱정되는 점을 알려주세요.", 83, "preference-support", REVIEW),
        q("medication.information_source_reliability_conflict_and_proxy", "Medication Information Source Reliability and Proxy", "string", "information-reliability", "본인·보호자 중 누가 답하는지, 기억의 확실성, 약 사진·처방전·퇴원서·검사자료 유무와 서로 맞지 않는 부분을 알려주세요.", 82, "clinician-handoff", RECONCILE + RISK),
        q("medication.clinician_handoff_unresolved_questions_and_additional_comment", "Clinician Handoff Questions and Additional Comment", "string", "handoff-goal", "진료 전에 의료진이 꼭 확인해야 할 미해결 약 문제, 가장 원하는 결정과 질문에 없던 의견을 알려주세요.", 81, "clinician-handoff", REVIEW),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    for key, identifier in G.items():
        nodes[identifier] = {
            "id": identifier, "type": "ClinicalGroup",
            "display": key.replace("-", " ").title(),
        }
    doc["extra_nodes"] = list(nodes.values())
    doc["default_refresh"].update({
        "last_assessed_at": "2026-07-19",
        "next_monitor_at": "2026-07-20",
        "next_full_review_at": "2027-01-15",
    })
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc):
    result = completion_policy(
        prefix=P, fragment=doc, presentation_fact="medication.review.requested",
        question_budget=75, source_refs=SOURCES,
    )
    result["required_facts"]["routine"] = [
        "medication.review.purpose",
        "medication.current_prescribed_list",
        "medication.current_otc_list",
        "medication.current_supplement_list",
        "medication.non_oral_products",
        "medication.actual_use_differs",
        "medication.recent_start_stop_dose_change",
        "allergy.drug_status",
        "allergy.drug_reaction_details",
        "medication.suspected_adverse_effects",
        "medication.monitoring_due_or_overdue",
        "medication.list_source_last_reconciled_and_date",
        "medication.list_conflict_unknown_and_verification_needed",
        "medication.information_source_reliability_conflict_and_proxy",
        "medication.clinician_handoff_unresolved_questions_and_additional_comment",
    ]
    result["conditional_required_facts"] = [{
        "selector_fact": "medication.review.purpose",
        "cases": {
            "reconcile": [
                "medication.item_name_brand_generic_product_and_code",
                "medication.item_strength_formulation_and_unit",
                "medication.item_dose_route_frequency_timing_and_prn",
                "medication.item_indication_start_date_prescriber_and_pharmacy",
                "medication.indications_known", "medication.last_actual_dose_by_item",
                "medication.duplicate_or_unknown_product",
                "medication.multiple_prescribers_or_pharmacies",
                "medication.stopped_held_expired_and_remaining_stock",
            ],
            "effectiveness": [
                "medication.perceived_benefit",
                "medication.benefit_by_indication_target_and_time_course",
                "medication.missed_dose_frequency",
                "medication.monitoring_test_name_last_date_result_trend_and_source",
                "medication.monitoring_target_due_date_and_unresolved_action",
                "medication.renal_hepatic_function_date_result_and_dose_context",
            ],
            "adverse_effect": [
                "medication.adverse_effect_onset_dose_relation_dechallenge_rechallenge",
                "medication.adverse_effect_severity_frequency_function_and_actions",
                "allergy.drug_culprit_dose_route_onset_and_timing",
                "allergy.drug_reaction_severity_treatment_outcome_and_reexposure",
                "allergy.drug_allergy_intolerance_or_uncertain_label",
                "medication.drowsiness_confusion_dizziness_falls_driving_and_work",
                "medication.opioid_sedative_alcohol_sleep_apnoea_and_naloxone_context",
            ],
            "instructions": [
                "medication.missed_dose_frequency",
                "medication.intentional_nonadherence_reason",
                "medication.unintentional_nonadherence_reason",
                "medication.administration_difficulty",
                "medication.adherence_aid_caregiver_and_administration_source",
                "medication.swallowing_vision_dexterity_cognition_and_packaging",
                "medication.inhaler_injection_patch_device_technique_and_training",
            ],
            "change_request": [
                "medication.perceived_benefit",
                "medication.intentional_nonadherence_reason",
                "medication.stopped_held_expired_and_remaining_stock",
                "medication.preference_tradeoff_change_request_and_constraints",
                "patient.pregnant_planning_or_breastfeeding",
                "history.kidney_impairment", "history.liver_impairment",
            ],
            "post_discharge": [
                "medication.recent_care_transition",
                "medication.care_transition_previous_current_discharge_list_conflict",
                "medication.transition_change_reason_author_date_and_followup",
                "medication.multiple_prescribers_or_pharmacies",
                "medication.last_actual_dose_by_item",
                "medication.supply_days_remaining_refill_access_and_storage",
            ],
            "other": [
                "medication.item_dose_route_frequency_timing_and_prn",
                "medication.missed_dose_frequency",
                "medication.unintentional_nonadherence_reason",
                "medication.perceived_benefit",
                "medication.adverse_effect_onset_dose_relation_dechallenge_rechallenge",
                "medication.monitoring_test_name_last_date_result_trend_and_source",
                "medication.supply_days_remaining_refill_access_and_storage",
                "medication.preference_tradeoff_change_request_and_constraints",
            ],
        },
    }]
    return result


def sources():
    doc = load(RESEARCH)
    for artifact in doc["artifacts"]:
        if artifact["id"] == "source.nhs-england.opioid-respiratory-depression.2020":
            artifact.update({
                "title": "Risk of distress and death from inappropriate doses of naloxone in patients on long-term opioid or opiate treatment",
                "version": "NHS/PSA/W/2014/016-current-page-accessed-2026-07-19",
                "last_monitored_at": "2026-07-19",
                "monitor_result": "current_official_source_confirmed_no_replacement_identified",
                "assertions": [
                    "Long-term opioid or opiate treatment, reduced consciousness and dangerously shallow or slow breathing are retained as Build-Time medication-safety context.",
                    "The interview records opioid and sedative exposure and respiratory warning features but does not select or dose naloxone.",
                ],
            })
        else:
            artifact["monitor_result"] = "not_due_existing_metadata_preserved"
    doc["provenance"] = provenance(SOURCES)
    return doc


def clinician(doc):
    result = load(CLINICIAN)
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.medication_review"] = sorted(
        item["fact"]["id"] for item in doc["entries"]
    )
    return result


def condition_state(condition):
    result = {}
    for child in condition.get("all", [condition]):
        if "fact" in child:
            result[child["fact"]] = {
                "value": child.get("equals", child.get("in", [True])[0])
            }
    return result


def cases(doc, completion):
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    forbidden = [
        "diagnosis.drug_poisoning", "diagnosis.drug_allergy",
        "recommendation.stop_medication", "recommendation.change_dose",
        "recommendation.naloxone_dose",
    ]
    result = {}
    for index, rule in enumerate(doc["safety_rules"]):
        key = rule["id"].split("safety.", 1)[1]
        level = rule["then"]["safety_level"]
        result[f"MED-{key.upper()}.json"] = {
            "id": f"MED-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 35 + index * 4},
            "initial_statement": {"ko": "복용약 검토 중 즉시 확인할 증상이 있습니다."},
            "hidden_state": condition_state(rule["when"]),
            "expected": {
                "expected_safety_level": level,
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [rule["id"]],
                "expected_max_turns": 25, "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }
    always = completion["required_facts"]["always"]
    base = completion["required_facts"]["routine"]
    branches = completion["conditional_required_facts"][0]["cases"]

    def value(fid):
        fact = by_id[fid]
        if fact["value_type"] == "boolean":
            return False
        if fact["value_type"] == "coded":
            return fact.get("allowed_values", ["other"])[-1]
        return "특이사항 없음"

    def routine(branch):
        ids = dict.fromkeys([*always, *base, *branches[branch]])
        state = {fid: {"value": value(fid)} for fid in ids}
        state["medication.review.requested"] = {"value": True}
        state["medication.review.purpose"] = {"value": branch}
        return state

    specs = [
        ("RECONCILIATION-FIRST", "reconcile", 54, "약 봉투와 실제 복용이 달라 전체 약 목록을 대조합니다.", {}),
        ("EFFECTIVENESS-MONITORING", "effectiveness", 67, "약 효과와 최근 검사 결과를 진료 전에 정리합니다.", {}),
        ("ADVERSE-EFFECT-TIMELINE", "adverse_effect", 46, "새 약 뒤 생긴 불편의 시간 관계를 정리합니다.", {}),
        ("DEVICE-ACCESSIBILITY", "instructions", 78, "흡입기와 약 포장 사용이 어려워 보호자와 답합니다.", {"medication.adherence_aid_caregiver_and_administration_source": {"value": "딸이 약통 준비와 흡입기 사용을 확인함"}}),
        ("CHANGE-PREFERENCE", "change_request", 59, "효과와 부작용 사이에서 바꾸고 싶은 약을 상담하려 합니다.", {}),
        ("POST-DISCHARGE-CONFLICT", "post_discharge", 72, "퇴원약과 기존 약 목록이 달라 의료진에게 전달합니다.", {"medication.care_transition_previous_current_discharge_list_conflict": {"value": "퇴원서와 집의 약 봉투 용량이 다름"}}),
        ("REMOTE-PROXY-UNCERTAIN", "other", 84, "전화로 보호자가 답하며 약 이름 일부는 확실하지 않습니다.", {"medication.information_source_reliability_conflict_and_proxy": {"value": "보호자 대리, 약 봉투 일부만 확인됨"}}),
        ("POLYPHARMACY-FALL-WORK", "adverse_effect", 76, "여러 약 복용 후 졸림과 낙상·운전 영향을 정리합니다.", {"medication.drowsiness_confusion_dizziness_falls_driving_and_work": {"value": "졸림과 한 차례 낙상, 현재 운전하지 않음"}}),
        ("PREGNANCY-BREASTFEEDING-CHANGE", "change_request", 32, "임신·수유 가능성을 포함해 약 변경 상담 내용을 정리합니다.", {"patient.pregnant_planning_or_breastfeeding": {"value": True}}),
        ("MULTI-RFE-ADDITIONAL-COMMENT", "other", 63, "복용약 외에 배변 문제도 별도 문진하고 싶습니다.", {"medication.clinician_handoff_unresolved_questions_and_additional_comment": {"value": "배변 변화를 별도 RFE로 전달 요청"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine(branch)
        state.update(overrides)
        result[f"MED-{key}.json"] = {
            "id": f"MED-{key}", "simulation_language": "ko",
            "persona": {"age": age}, "initial_statement": {"ko": statement},
            "hidden_state": state,
            "expected": {
                "expected_safety_level": "routine",
                "expected_stop_reason": "all_required_targets_resolved",
                "expected_max_turns": 65, "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }
    absent = routine("reconcile")
    missing = "medication.list_conflict_unknown_and_verification_needed"
    absent.pop(missing)
    result["MED-DATA-ABSENT-SOURCE.json"] = {
        "id": "MED-DATA-ABSENT-SOURCE", "simulation_language": "ko",
        "persona": {"age": 81},
        "encounter_context": {
            "care_setting": "primary_care", "encounter_type": "medication_review",
            "interview_initiator": "caregiver", "interview_mode": "telephone",
            "available_information": ["no_previous_records"],
            "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
        },
        "initial_statement": {"ko": "보호자가 전화로 답하며 처방 차이는 확인할 자료가 없습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "not-performed"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "not-performed"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 65, "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }
    return result


def main():
    seed_medication_review.main()
    doc = fragment()
    completion = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, completion)
    write_json(RESEARCH, sources())
    write_json(CLINICIAN, clinician(doc))
    for old in SIM_ROOT.glob("*.json"):
        old.unlink()
    for name, case in cases(doc, completion).items():
        write_json(f"simulation/patients/medication/medication-review/{name}", case)


if __name__ == "__main__":
    main()
