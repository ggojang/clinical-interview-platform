#!/usr/bin/env python3
"""Strengthen research-only hypertension follow-up clinician handoff knowledge."""
from __future__ import annotations

import json

import seed_hypertension_follow_up
from profile_support import ROOT, completion_policy, entry, provenance, write_json


P = "hypertension-follow-up"
FRAGMENT = "knowledge/generated/cardiovascular/hypertension-follow-up/hypertension-follow-up.json"
POLICY = "policies/primary-care-hypertension-follow-up-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
SOURCES = [
    "source.nice.ng136.hypertension.2026",
    "source.nice.ng133.pregnancy-hypertension.2023",
    "source.nhs.high-blood-pressure.2026",
    "source.stom.hypertension.20260714",
]
G = {key: f"group.hypertension-follow-up.{key}" for key in (
    "routing", "measurement-detail", "medicine-detail", "risk-detail",
    "monitoring-detail", "pregnancy-detail", "function", "handoff",
)}
C = ["intent.characterize_follow_up"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
F = ["intent.follow_up_support"]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def q(fact_id, display, value_type, key, wording, score, group, intents, **kwargs):
    return entry(
        P, fact_id, display, value_type, key, wording, score, key,
        [G[group]], intents=intents, **kwargs,
    )


def fragment() -> dict:
    doc = load(FRAGMENT)
    contexts = [
        "reading_or_home_log_review", "medicine_effect_or_adherence",
        "adverse_effect_or_postural_symptom", "risk_and_monitoring_review",
        "pregnancy_or_postpartum", "child_or_proxy", "result_or_plan_followup",
        "other_or_unclear",
    ]
    additions = [
        q("hypertension.primary_followup_context", "Primary Hypertension Follow-up Context", "coded", "primary-context", "이번 방문 목적은 혈압 수치·가정기록 확인, 약 효과·복용 확인, 부작용·기립 증상, 심혈관 위험·검사 확인, 임신·산후, 소아·보호자 응답, 결과·계획 추적, 또는 불분명 중 무엇에 가장 가깝나요?", 116, "routing", C + F, allowed_values=contexts),
        q("hypertension.patient_words_current_status_and_main_change", "Patient Description of Current Status", "string", "patient-words", "본인의 표현으로 최근 혈압 상태, 평소와 달라진 점과 가장 걱정되는 내용을 알려주세요.", 115, "handoff", C),
        q("hypertension.diagnosis_date_basis_target_and_followup_team", "Diagnosis, Target and Follow-up Team", "string", "diagnosis-context", "고혈압을 언제 어떤 측정이나 설명으로 진단받았고, 의료진과 정한 목표 혈압 및 현재 추적기관이 있다면 알려주세요.", 114, "handoff", C + F),
        q("hypertension.latest_reading_series_values_dates_times_and_context", "Recent Blood Pressure Series", "string", "reading-series", "최근 혈압값들을 날짜·시각별로 위/아래 숫자와 함께 적고, 각각 측정 전 활동·식사·카페인·흡연·증상 상황을 알려주세요.", 113, "measurement-detail", C + R),
        q("hypertension.measurement_arm_position_rest_cuff_device_and_repeats", "Blood Pressure Measurement Method", "string", "measurement-method", "측정한 팔, 자세, 휴식시간, 커프 크기·기기, 반복 횟수와 반복값 사이 간격을 알려주세요.", 112, "measurement-detail", C),
        q("hypertension.home_log_days_morning_evening_average_range_and_missing", "Home Blood Pressure Log Detail", "string", "home-log-detail", "가정혈압 기록이 있다면 측정한 날짜 수, 아침·저녁 횟수, 평균·최저·최고 범위와 빠진 날을 알려주세요.", 111, "measurement-detail", C + F),
        q("hypertension.baseline_variability_recent_trend_and_trigger_relation", "Blood Pressure Trend and Variability", "string", "trend", "평소 범위와 비교한 최근 상승·하락·변동 양상, 반복되는 시간대와 스트레스·통증·수면·운동과의 관계를 알려주세요.", 110, "measurement-detail", C + R),
        q("hypertension.high_or_low_reading_symptom_sequence_duration_and_recovery", "Reading-associated Symptom Sequence", "string", "symptom-sequence", "높거나 낮은 혈압과 함께 증상이 있었다면 수치와 증상 중 무엇이 먼저였는지, 지속시간·회복과 반복 여부를 알려주세요.", 109, "measurement-detail", C + S),
        q("hypertension.postural_symptom_position_timing_bp_pulse_fall_and_recovery", "Postural Symptom Detail", "string", "postural-detail", "자세를 바꿀 때 어지럼이 있다면 누움·앉음·서기 순서, 시작까지 시간, 당시 혈압·맥박, 넘어짐과 회복 과정을 알려주세요.", 108, "measurement-detail", C + R),
        q("hypertension.antihypertensive_name_strength_form_route_schedule_indication", "Structured Antihypertensive Regimen", "string", "medicine-regimen", "혈압약마다 제품명·성분명, 용량·제형, 복용 경로, 예정 시간·횟수와 처방 목적을 알려주세요.", 107, "medicine-detail", F),
        q("hypertension.actual_last_dose_timing_and_difference_from_prescription", "Actual Medicine Use and Last Dose", "string", "actual-use", "각 혈압약의 실제 복용 시간과 마지막 복용 시각, 처방대로 복용하지 않은 차이가 있다면 알려주세요.", 106, "medicine-detail", F + R),
        q("hypertension.missed_extra_or_late_dose_dates_reasons_and_action", "Dose Variance Detail", "string", "dose-variance", "최근 빠뜨림·추가복용·늦은 복용의 날짜·횟수·이유와 이후 어떻게 했는지 알려주세요.", 105, "medicine-detail", F + R),
        q("hypertension.access_cost_supply_schedule_memory_and_caregiver_barriers", "Medication Access and Adherence Barriers", "string", "adherence-barriers", "비용·재고·처방전·생활일정·기억·삼킴·보호자 도움 등 꾸준한 복용을 어렵게 하는 점이 있나요?", 104, "medicine-detail", F),
        q("hypertension.adverse_effect_onset_dose_relation_function_and_dechallenge", "Suspected Adverse-effect Timeline", "string", "adverse-effect-detail", "의심되는 부작용의 시작일, 약 복용·용량변경과의 순서, 일상 영향과 중단·재복용 때 변화를 알려주세요.", 103, "medicine-detail", C + F),
        q("hypertension.nonprescription_stimulant_hormone_supplement_timing_and_amount", "Other Product Exposure Detail", "string", "other-product-detail", "진통소염제·코막힘약·스테로이드·호르몬·각성제·한약·보충제·에너지음료를 사용한다면 이름·양·빈도·마지막 사용을 알려주세요.", 102, "medicine-detail", R),
        q("hypertension.cardiovascular_cerebrovascular_disease_event_date_status_and_treatment", "Cardiovascular Disease History Detail", "string", "cardiovascular-history", "심장·뇌·말초혈관 질환이 있다면 정확한 진단, 발생일·시술·입원과 현재 증상·치료 상태를 알려주세요.", 101, "risk-detail", R),
        q("hypertension.kidney_disease_albuminuria_stage_result_date_and_care_status", "Kidney Disease and Albuminuria Detail", "string", "kidney-history-detail", "신장질환·단백뇨가 있다면 진단명·단계, 최근 신장기능·소변검사 날짜와 설명받은 결과, 담당 진료를 알려주세요.", 100, "risk-detail", R + F),
        q("hypertension.diabetes_lipid_gout_and_vascular_risk_status", "Metabolic and Vascular Risk Context", "string", "metabolic-risk", "당뇨·이상지질혈증·통풍 등 관련 질환의 진단 시기, 최근 수치와 현재 치료 상태를 알려주세요.", 99, "risk-detail", R),
        q("hypertension.family_early_cardiovascular_kidney_hypertension_history", "Family Cardiovascular and Kidney History", "string", "family-risk", "가족의 고혈압, 젊은 나이의 심장·뇌혈관질환, 신장질환이 있다면 관계와 발병 나이를 알려주세요.", 98, "risk-detail", R),
        q("hypertension.sleep_snoring_apnoea_daytime_sleepiness_and_sleep_duration", "Sleep and Apnoea Context", "string", "sleep-detail", "평균 수면시간, 코골이·목격된 무호흡·아침 두통·낮 졸림과 교대근무 여부를 알려주세요.", 97, "risk-detail", R),
        q("hypertension.pregnancy_gestation_postpartum_obstetric_history_bp_proteinuria_and_plan", "Pregnancy and Postpartum Hypertension Detail", "string", "pregnancy-detail", "해당되는 경우 임신 주수 또는 출산 후 기간, 출산력·과거 임신 고혈압, 최근 혈압·소변 단백과 산과 진료 계획을 알려주세요.", 96, "pregnancy-detail", S + R),
        q("hypertension.laboratory_creatinine_egfr_electrolytes_urine_glucose_lipid_date_source", "Hypertension Laboratory Result Detail", "string", "laboratory-results", "최근 크레아티닌·eGFR, 전해질, 소변 단백, 혈당·당화혈색소, 지질 검사의 날짜·결과·결과 출처를 알려주세요.", 95, "monitoring-detail", F + R),
        q("hypertension.prior_ecg_and_clinical_test_result_date_source", "ECG and Clinical Test Result", "string", "clinical-tests", "심전도나 다른 심혈관 기능검사를 했다면 검사명·날짜·설명받은 결과와 자료 출처를 알려주세요.", 94, "monitoring-detail", F + R),
        q("hypertension.prior_cardiac_renal_vascular_imaging_date_result_and_source", "Cardiac Renal and Vascular Imaging", "string", "imaging-results", "심장·신장·혈관 영상검사를 했다면 검사명·날짜·설명받은 결과와 자료 출처를 알려주세요.", 93, "monitoring-detail", F + R),
        q("hypertension.eye_retinal_evaluation_date_result_and_source", "Eye and Retinal Evaluation", "string", "eye-evaluation", "고혈압과 관련해 눈 또는 망막 검사를 했다면 날짜·설명받은 결과와 자료 출처를 알려주세요.", 92, "monitoring-detail", F),
        q("hypertension.prior_treatment_change_response_bp_effect_and_adverse_effect", "Prior Treatment Response", "string", "treatment-response", "이전에 약·생활습관을 바꾼 시기, 이후 혈압 변화·증상 개선과 부작용을 알려주세요.", 91, "medicine-detail", C + F),
        q("hypertension.diet_salt_activity_weight_alcohol_tobacco_caffeine_and_change", "Lifestyle Pattern and Recent Change", "string", "lifestyle-detail", "식사·소금, 운동, 체중, 음주·흡연, 카페인 섭취량과 최근 바꾼 내용 및 지속 가능성을 알려주세요.", 90, "risk-detail", F + R),
        q("hypertension.function_sleep_work_driving_exercise_and_fall_impact", "Functional and Safety Impact", "string", "function-detail", "혈압·증상·약 때문에 수면, 운동, 업무·운전, 일상활동과 낙상 위험에 어떤 영향이 있는지 알려주세요.", 89, "function", C + R),
        q("hypertension.child_age_growth_birth_kidney_sleep_medicine_and_proxy_observation", "Child and Proxy Hypertension Context", "string", "child-context", "소아라면 나이·성장, 출생력, 신장·수면·복용약, 보호자가 직접 본 증상과 아이가 표현한 내용을 구분해 알려주세요.", 88, "risk-detail", C + R),
        q("hypertension.older_frailty_cognition_falls_self_management_and_support", "Older Adult Frailty and Support", "string", "older-context", "고령자라면 보행·낙상·인지·복약 자가관리의 최근 변화와 보조기구·보호자 지원을 알려주세요.", 87, "function", R),
        q("hypertension.information_source_measurement_record_reliability_and_conflict", "Information Source and Conflict", "string", "information-source", "누가 답하는지, 혈압계·기록·처방전·검사자료 유무, 기억이 불확실하거나 서로 다른 수치·복약 정보가 있는지 알려주세요.", 86, "handoff", R),
        q("hypertension.communication_language_hearing_vision_cognition_and_accessibility", "Communication and Accessibility Needs", "string", "accessibility", "선호 언어, 통역·청각·시각·인지·문해·디지털 사용에 필요한 도움과 선호하는 응답 방법을 알려주세요.", 85, "handoff", R),
        q("hypertension.patient_goal_expected_help_followup_plan_and_additional_rfe", "Patient Goal, Plan and Additional RFE", "string", "goal", "이번 진료에서 확인할 목표, 원하는 도움·다음 계획과 질문에 없던 다른 증상·의견 또는 별도 문진이 필요한 문제를 알려주세요.", 84, "handoff", C + F),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    for key, identifier in G.items():
        nodes[identifier] = {"id": identifier, "type": "ClinicalGroup", "display": key.replace("-", " ").title()}
    doc["extra_nodes"] = list(nodes.values())
    doc["default_refresh"].update({
        "last_assessed_at": "2026-07-20",
        "next_monitor_at": "2026-07-21",
        "next_full_review_at": "2027-01-16",
    })
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc: dict) -> dict:
    result = completion_policy(
        prefix=P, fragment=doc, presentation_fact="hypertension.follow_up.requested",
        question_budget=90, source_refs=SOURCES,
    )
    result["required_facts"]["routine"] = [
        "hypertension.primary_followup_context",
        "blood_pressure.latest_systolic", "blood_pressure.latest_diastolic",
        "blood_pressure.latest_measurement_time", "blood_pressure.measurement_setting",
        "hypertension.patient_words_current_status_and_main_change",
        "hypertension.diagnosis_date_basis_target_and_followup_team",
        "hypertension.latest_reading_series_values_dates_times_and_context",
        "hypertension.measurement_arm_position_rest_cuff_device_and_repeats",
        "hypertension.baseline_variability_recent_trend_and_trigger_relation",
        "hypertension.function_sleep_work_driving_exercise_and_fall_impact",
        "hypertension.information_source_measurement_record_reliability_and_conflict",
        "hypertension.patient_goal_expected_help_followup_plan_and_additional_rfe",
    ]
    result["conditional_required_facts"] = [{
        "selector_fact": "hypertension.primary_followup_context",
        "cases": {
            "reading_or_home_log_review": [
                "blood_pressure.repeated_after_rest", "blood_pressure.device_and_cuff_suitable",
                "blood_pressure.home_log_available", "blood_pressure.home_average_or_range",
                "hypertension.home_log_days_morning_evening_average_range_and_missing",
                "hypertension.high_or_low_reading_symptom_sequence_duration_and_recovery",
            ],
            "medicine_effect_or_adherence": [
                "medication.antihypertensive_current_list", "medication.missed_dose_frequency",
                "medication.recent_start_stop_dose_change", "medication.suspected_adverse_effects",
                "hypertension.antihypertensive_name_strength_form_route_schedule_indication",
                "hypertension.actual_last_dose_timing_and_difference_from_prescription",
                "hypertension.missed_extra_or_late_dose_dates_reasons_and_action",
                "hypertension.access_cost_supply_schedule_memory_and_caregiver_barriers",
                "hypertension.prior_treatment_change_response_bp_effect_and_adverse_effect",
            ],
            "adverse_effect_or_postural_symptom": [
                "symptom.postural_dizziness", "event.recent_fall",
                "medication.suspected_adverse_effects",
                "hypertension.postural_symptom_position_timing_bp_pulse_fall_and_recovery",
                "hypertension.adverse_effect_onset_dose_relation_function_and_dechallenge",
                "hypertension.actual_last_dose_timing_and_difference_from_prescription",
            ],
            "risk_and_monitoring_review": [
                "history.cardiovascular_or_cerebrovascular_disease", "history.kidney_impairment",
                "history.diabetes", "symptom.sleep_apnoea_features",
                "hypertension.cardiovascular_cerebrovascular_disease_event_date_status_and_treatment",
                "hypertension.kidney_disease_albuminuria_stage_result_date_and_care_status",
                "hypertension.diabetes_lipid_gout_and_vascular_risk_status",
                "hypertension.family_early_cardiovascular_kidney_hypertension_history",
                "hypertension.laboratory_creatinine_egfr_electrolytes_urine_glucose_lipid_date_source",
                "hypertension.prior_ecg_and_clinical_test_result_date_source",
                "hypertension.prior_cardiac_renal_vascular_imaging_date_result_and_source",
            ],
            "pregnancy_or_postpartum": [
                "patient.pregnant_or_postpartum", "blood_pressure.pregnancy_160_110_or_higher",
                "symptom.preeclampsia_warning_features",
                "hypertension.pregnancy_gestation_postpartum_obstetric_history_bp_proteinuria_and_plan",
                "hypertension.laboratory_creatinine_egfr_electrolytes_urine_glucose_lipid_date_source",
            ],
            "child_or_proxy": [
                "hypertension.child_age_growth_birth_kidney_sleep_medicine_and_proxy_observation",
                "hypertension.information_source_measurement_record_reliability_and_conflict",
                "hypertension.communication_language_hearing_vision_cognition_and_accessibility",
            ],
            "result_or_plan_followup": [
                "hypertension.monitoring_tests_due_or_known",
                "hypertension.laboratory_creatinine_egfr_electrolytes_urine_glucose_lipid_date_source",
                "hypertension.prior_ecg_and_clinical_test_result_date_source",
                "hypertension.prior_cardiac_renal_vascular_imaging_date_result_and_source",
                "hypertension.eye_retinal_evaluation_date_result_and_source",
                "hypertension.prior_treatment_change_response_bp_effect_and_adverse_effect",
            ],
            "other_or_unclear": [
                "medication.antihypertensive_current_list", "symptom.postural_dizziness",
                "hypertension.antihypertensive_name_strength_form_route_schedule_indication",
                "hypertension.nonprescription_stimulant_hormone_supplement_timing_and_amount",
                "hypertension.laboratory_creatinine_egfr_electrolytes_urine_glucose_lipid_date_source",
                "hypertension.diet_salt_activity_weight_alcohol_tobacco_caffeine_and_change",
                "hypertension.communication_language_hearing_vision_cognition_and_accessibility",
            ],
        },
    }]
    return result


def clinician(doc: dict) -> dict:
    result = load(CLINICIAN)
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.hypertension_follow_up"] = [
        "hypertension.primary_followup_context",
        "hypertension.patient_words_current_status_and_main_change",
        "hypertension.diagnosis_date_basis_target_and_followup_team",
        "hypertension.latest_reading_series_values_dates_times_and_context",
        "hypertension.measurement_arm_position_rest_cuff_device_and_repeats",
        "hypertension.baseline_variability_recent_trend_and_trigger_relation",
        "hypertension.high_or_low_reading_symptom_sequence_duration_and_recovery",
        "hypertension.antihypertensive_name_strength_form_route_schedule_indication",
        "hypertension.actual_last_dose_timing_and_difference_from_prescription",
        "hypertension.laboratory_creatinine_egfr_electrolytes_urine_glucose_lipid_date_source",
        "hypertension.prior_treatment_change_response_bp_effect_and_adverse_effect",
        "hypertension.diet_salt_activity_weight_alcohol_tobacco_caffeine_and_change",
        "hypertension.function_sleep_work_driving_exercise_and_fall_impact",
        "hypertension.information_source_measurement_record_reliability_and_conflict",
        "hypertension.communication_language_hearing_vision_cognition_and_accessibility",
        "hypertension.patient_goal_expected_help_followup_plan_and_additional_rfe",
    ]
    return result


def routine_cases(doc: dict, completion: dict) -> dict[str, dict]:
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    always = completion["required_facts"]["always"]
    core = completion["required_facts"]["routine"]
    branches = completion["conditional_required_facts"][0]["cases"]
    forbidden = [
        "diagnosis.hypertensive_emergency", "diagnosis.secondary_hypertension",
        "recommendation.change_dose", "recommendation.stop_medicine",
    ]

    def value(fid: str):
        fact = by_id[fid]
        if fact["value_type"] == "boolean":
            return False
        if fact["value_type"] == "integer":
            return 132 if "systolic" in fid else 82
        if fact["value_type"] == "coded":
            return fact.get("allowed_values", ["other_or_unclear"])[-1]
        return "특이사항 없음"

    def state(branch: str) -> dict:
        ids = dict.fromkeys([*always, *core, *branches[branch]])
        result = {fid: {"value": value(fid)} for fid in ids}
        result["hypertension.follow_up.requested"] = {"value": True}
        result["hypertension.primary_followup_context"] = {"value": branch}
        result["blood_pressure.latest_systolic"] = {"value": 132}
        result["blood_pressure.latest_diastolic"] = {"value": 82}
        return result

    specs = [
        ("HOME-LOG-REVIEW", "reading_or_home_log_review", 57, "가정혈압 기록의 추세와 측정방법을 진료 전에 정리합니다.", {}),
        ("MEDICINE-ADHERENCE", "medicine_effect_or_adherence", 63, "혈압약 실제 복용과 빠뜨린 이유, 치료 반응을 정리합니다.", {}),
        ("POSTURAL-ADVERSE-EFFECT", "adverse_effect_or_postural_symptom", 76, "약 변경 뒤 자세 변화 어지럼과 낙상 위험을 정리합니다.", {"symptom.postural_dizziness": {"value": True}}),
        ("RISK-MONITORING", "risk_and_monitoring_review", 68, "신장·심혈관 위험과 검사 결과 출처를 정리합니다.", {}),
        ("PREGNANCY-ROUTINE", "pregnancy_or_postpartum", 32, "임신 중 고혈압 추적과 산과 병력·검사 계획을 정리합니다.", {"patient.pregnant_or_postpartum": {"value": "pregnant"}}),
        ("CHILD-PROXY", "child_or_proxy", 12, "보호자가 소아의 혈압 기록과 성장·수면·복약 정보를 설명합니다.", {}),
        ("RESULT-PLAN-FOLLOWUP", "result_or_plan_followup", 61, "검사 결과를 해석 요청 없이 의료기관 추적용으로 정리합니다.", {}),
        ("OLDER-ACCESSIBILITY", "other_or_unclear", 84, "고령자의 복약 자가관리와 청각·보호자 지원을 정리합니다.", {"hypertension.older_frailty_cognition_falls_self_management_and_support": {"value": "복약 확인에 보호자 도움이 필요함"}}),
        ("MULTI-RFE-ADDITIONAL-COMMENT", "other_or_unclear", 55, "고혈압 추적 외 다른 증상은 별도 RFE로 보존합니다.", {"hypertension.patient_goal_expected_help_followup_plan_and_additional_rfe": {"value": "무릎 통증은 별도 문진 요청"}}),
        ("REMOTE-CONFLICT", "reading_or_home_log_review", 70, "전화 문진에서 기억한 혈압과 기록지 수치 충돌을 보존합니다.", {"hypertension.information_source_measurement_record_reliability_and_conflict": {"value": "본인 기억과 보호자 기록이 달라 의료진 확인 필요"}}),
        ("TYPO-CLARIFICATION", "medicine_effect_or_adherence", 49, "약 이름 오타가 의심되면 원문을 보존하고 재확인합니다.", {"hypertension.antihypertensive_name_strength_form_route_schedule_indication": {"value": "제품명 철자 불확실, 처방전 확인 필요"}}),
    ]
    output = {}
    for key, branch, age, statement, overrides in specs:
        hidden = state(branch)
        hidden.update(overrides)
        output[f"HTN-{key}.json"] = {
            "id": f"HTN-{key}", "simulation_language": "ko",
            "persona": {"age": age}, "initial_statement": {"ko": statement},
            "hidden_state": hidden,
            "expected": {
                "expected_safety_level": "routine",
                "expected_stop_reason": "all_required_targets_resolved",
                "expected_max_turns": 90, "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }

    absent = state("result_or_plan_followup")
    missing = "hypertension.prior_ecg_and_clinical_test_result_date_source"
    absent.pop(missing)
    output["HTN-DATA-ABSENT.json"] = {
        "id": "HTN-DATA-ABSENT", "simulation_language": "ko",
        "persona": {"age": 73},
        "encounter_context": {
            "care_setting": "primary_care", "encounter_type": "follow_up",
            "interview_initiator": "caregiver", "interview_mode": "telephone",
            "available_information": ["no_previous_records"],
            "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
        },
        "initial_statement": {"ko": "보호자가 답하지만 이전 심전도 결과는 지금 확인할 수 없습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "asked-unknown"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 90, "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }
    return output


def main() -> None:
    seed_hypertension_follow_up.main()
    doc = fragment()
    completion = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, completion)
    write_json(CLINICIAN, clinician(doc))
    for name, case in routine_cases(doc, completion).items():
        write_json(f"simulation/patients/cardiovascular/hypertension-follow-up/{name}", case)


if __name__ == "__main__":
    main()
