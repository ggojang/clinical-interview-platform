#!/usr/bin/env python3
"""Strengthen research-only back-pain knowledge for clinician handoff."""
from __future__ import annotations

import json

from profile_support import ROOT, completion_policy, entry, provenance, write_json


P = "back-pain"
FRAGMENT = "knowledge/generated/musculoskeletal/back-pain/back-pain.json"
POLICY = "policies/primary-care-back-pain-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
SIM_ROOT = ROOT / "simulation/patients/musculoskeletal/back-pain"
SOURCES = [
    "source.nhs.back-pain.2026",
    "source.nice.ng59.back-pain.2020",
    "source.nice.ng127.cauda-equina.2025",
    "source.nice.ng12.back-pain.2026",
    "source.stom.mrcm.back-pain.20260714",
]
G = {key: f"group.back-pain.{key}" for key in (
    "routing", "course", "pain-detail", "neurological-detail",
    "systemic-detail", "risk-history", "investigation", "function",
    "handoff",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def q(
    fact_id: str,
    display: str,
    value_type: str,
    key: str,
    wording: str,
    score: int,
    group: str,
    intents: list[str],
    **kwargs,
) -> dict:
    return entry(
        P, fact_id, display, value_type, key, wording, score, key,
        [G[group]], intents=intents, **kwargs,
    )


def fragment() -> dict:
    doc = load(FRAGMENT)
    contexts = [
        "acute_mechanical", "radicular_or_neurological", "trauma_or_fracture_risk",
        "fever_infection_or_systemic", "night_rest_or_persistent",
        "urinary_abdominal_or_pelvic_context", "chronic_recurrent_or_followup",
        "pregnancy_or_postpartum", "child_or_proxy", "other_or_unclear",
    ]
    additions = [
        q("back_pain.primary_context", "Primary Back Pain Context", "coded", "primary-context", "가장 가까운 상황은 급성·동작 관련, 다리로 뻗침·신경 증상, 외상·골절 위험, 발열·감염·전신 증상, 밤·휴식·지속 통증, 소변·복부·골반 관련, 만성·반복·추적, 임신·산후, 소아·보호자 응답, 또는 불분명 중 무엇인가요?", 116, "routing", C + R, allowed_values=contexts),
        q("back_pain.patient_words_and_main_concern", "Patient Description and Main Concern", "string", "patient-words", "본인의 표현으로 통증을 설명하고 가장 불편하거나 걱정되는 점을 알려주세요.", 115, "pain-detail", C),
        q("back_pain.first_latest_onset_context_and_course", "First and Latest Back Pain Timeline", "string", "timeline", "처음과 가장 최근 통증의 날짜·시각, 당시 하던 일과 이후 좋아짐·악화·반복 양상을 알려주세요.", 114, "course", C + R),
        q("back_pain.episode_frequency_duration_baseline_and_between_state", "Episode Frequency Duration and Baseline", "string", "episode-course", "하루·주당 통증 횟수, 한 번 지속되는 시간, 통증 사이에 평소 상태로 돌아오는지와 이전의 통증 없는 기준 상태를 알려주세요.", 113, "course", C),
        q("back_pain.exact_site_laterality_surface_depth_and_radiation", "Exact Site Laterality Depth and Radiation", "string", "site-detail", "허리·등의 정확한 부위와 왼쪽·오른쪽·가운데, 피부 가까이 또는 깊은 느낌인지, 엉덩이·다리·가슴·배로 퍼지는 경로를 알려주세요.", 112, "pain-detail", C + R),
        q("back_pain.character_quality_and_patient_comparison", "Back Pain Character and Quality", "string", "character", "쑤심·찌름·타는 느낌·전기 오는 느낌·압박·당김 등 통증 양상과 이전 통증과 다른 점을 알려주세요.", 111, "pain-detail", C),
        q("back_pain.movement_posture_load_cough_strain_and_relief_pattern", "Movement Posture Load and Relief Pattern", "string", "mechanical-pattern", "허리 굽힘·폄·비틀기, 앉기·서기·걷기·눕기, 물건 들기, 기침·재채기·힘주기 중 무엇이 악화하거나 완화하며 변화까지 얼마나 걸리는지 알려주세요.", 110, "pain-detail", C + D),
        q("back_pain.day_night_rest_sleep_morning_stiffness_and_activity_pattern", "Day Night Rest Sleep and Stiffness Pattern", "string", "time-pattern", "낮·밤·휴식·수면·기상 후 중 언제 심한지, 아침 뻣뻣함이 지속되는 시간과 움직이면 좋아지는지 알려주세요.", 109, "course", C + R),
        q("back_pain.walk_transfer_stairs_sleep_work_selfcare_and_driving_impact", "Detailed Functional and Safety Impact", "string", "function-detail", "걷기·일어나기·계단·수면·씻기·옷입기·업무·운전에서 어려운 활동과 도움이나 보조기구가 필요한 정도를 알려주세요.", 108, "function", C + R),
        q("back_pain.leg_radiation_route_side_below_knee_and_timing", "Leg Radiation Route and Timing", "string", "radiation-detail", "다리로 통증이 뻗친다면 어느 쪽 엉덩이·허벅지·종아리·발까지 이어지는지와 허리 통증 전·후·동시에 시작했는지 알려주세요.", 107, "neurological-detail", C + R),
        q("back_pain.weakness_numbness_distribution_tasks_sequence_and_trend", "Weakness and Sensory Distribution", "string", "neurology-detail", "다리 힘 빠짐·저림·감각 저하가 있다면 정확한 부위, 계단·발뒤꿈치/발끝 걷기 등 어려운 동작, 시작 순서와 진행 양상을 알려주세요.", 106, "neurological-detail", C + S),
        q("back_pain.bladder_bowel_saddle_sexual_change_onset_and_baseline", "Cauda Equina Symptom Detail and Baseline", "string", "cauda-detail", "배뇨·배변·회음부 감각·성기능 변화가 있다면 평소와 달라진 내용, 시작 시각, 허리·다리 증상과의 순서를 알려주세요.", 105, "neurological-detail", S + R),
        q("back_pain.trauma_mechanism_height_force_date_and_immediate_function", "Trauma Mechanism and Immediate Function", "string", "trauma-detail", "외상이 있었다면 날짜·시각, 낙상 높이·충돌 방향·힘, 직후 걷거나 움직일 수 있었는지와 다른 부상을 알려주세요.", 104, "risk-history", S + R),
        q("back_pain.fever_temperature_systemic_state_infection_exposure_and_timeline", "Fever Systemic Illness and Infection Timeline", "string", "infection-detail", "발열이 있다면 최고 체온·측정방법·시각, 오한·전신 상태, 최근 감염·상처·치과/비뇨기 증상과 허리 통증의 시작 순서를 알려주세요.", 103, "systemic-detail", S + R),
        q("back_pain.recent_procedure_injection_device_wound_and_infection_context", "Procedure Device Wound and Infection Context", "string", "procedure-infection", "최근 수술·주사·척추 시술·카테터/기기, 피부 상처·감염 또는 입원이 있었다면 날짜와 통증 시작과의 관계를 알려주세요.", 102, "systemic-detail", R),
        q("back_pain.weight_change_night_rest_thoracic_and_systemic_timeline", "Persistent and Systemic Symptom Timeline", "string", "systemic-timeline", "체중 변화의 양·기간, 밤이나 휴식 때 통증, 윗등 통증과 식욕·피로·식은땀 등 전신 변화의 순서를 알려주세요.", 101, "systemic-detail", R),
        q("back_pain.cancer_history_type_treatment_date_status_and_followup", "Cancer History and Current Status", "string", "cancer-history", "암 병력이 있다면 종류·진단 시기·수술/항암/방사선 치료·현재 상태와 최근 추적 결과를 알려주세요.", 100, "risk-history", R),
        q("back_pain.immune_suppression_diabetes_infection_risk_and_timing", "Immune and Infection Risk Detail", "string", "immune-risk", "면역저하 질환·치료, 당뇨, 투석 등 감염 위험 병력과 약 이름·마지막 투여 시기를 알려주세요.", 99, "risk-history", R),
        q("back_pain.osteoporosis_steroid_frailty_fall_and_fracture_history", "Bone Fragility and Fracture Risk Detail", "string", "bone-risk", "골다공증·과거 골절, 장기 스테로이드의 이름·기간, 허약·최근 낙상과 작은 충격 뒤 통증 여부를 알려주세요.", 98, "risk-history", R),
        q("back_pain.anticoagulant_antiplatelet_bleeding_disorder_and_last_dose", "Antithrombotic and Bleeding Context", "string", "bleeding-risk", "항응고제·항혈소판제 사용이나 출혈 질환이 있다면 약 이름·용량·마지막 복용과 멍·출혈 변화를 알려주세요.", 97, "risk-history", R),
        q("back_pain.pregnancy_gestation_postpartum_delivery_anesthesia_and_complications", "Pregnancy and Postpartum Context", "string", "pregnancy-context", "해당되는 경우 임신 주수 또는 출산 후 기간, 분만 방식·마취, 출혈·발열·혈압 문제와 통증 시작 시점을 알려주세요.", 96, "risk-history", R),
        q("back_pain.urinary_abdominal_bowel_menstrual_and_pelvic_relation", "Urinary Abdominal Bowel and Pelvic Relation", "string", "visceral-context", "소변·혈뇨, 복통·구토·배변, 월경·질출혈·골반 증상과 허리·등 통증의 시간 관계를 알려주세요.", 95, "systemic-detail", D + R),
        q("back_pain.prior_episode_spine_diagnosis_surgery_injection_and_recovery", "Prior Spine Episode Procedure and Recovery", "string", "prior-history", "이전 같은 통증의 시기·진단, 척추 수술·주사·재활 여부, 당시 회복 정도와 이번에 달라진 점을 알려주세요.", 94, "risk-history", R),
        q("back_pain.medicine_analgesic_dose_timing_effect_adverse_effect_and_allergy", "Medication Treatment and Allergy Detail", "string", "medicine-detail", "현재 약과 이번 통증에 사용한 진통제·소염제·근이완제 등의 이름·용량·시각, 효과·부작용과 약물 알레르기를 알려주세요.", 93, "risk-history", R),
        q("back_pain.prior_examination_imaging_lab_date_result_source_and_pending", "Prior Examination Imaging and Laboratory Result", "string", "prior-tests", "이전 진찰, X선·CT·MRI, 혈액·소변 검사의 날짜·설명받은 결과·자료 출처와 아직 확인하지 못한 결과를 알려주세요.", 92, "investigation", R),
        q("back_pain.treatment_activity_heat_therapy_response_and_recurrence", "Treatment Attempt Response and Recurrence", "string", "treatment-response", "활동 조절·찜질·약·물리/운동치료 등 해본 방법, 시행 시기·횟수, 효과·부작용과 중단 뒤 재발 여부를 알려주세요.", 91, "investigation", C + R),
        q("back_pain.occupation_manual_handling_posture_vibration_ppe_and_work_change", "Occupation and Work Exposure Detail", "string", "occupation", "직업·가사·돌봄에서 물건 들기, 반복 굽힘·비틀기, 장시간 자세·진동·운전 노출과 업무 조정·보호구를 알려주세요.", 90, "function", R),
        q("back_pain.child_age_growth_fever_function_trauma_and_proxy_observation", "Child Back Pain and Proxy Observation", "string", "child-context", "소아라면 나이·성장, 발열·보행·놀이·수면 변화, 외상과 보호자가 직접 본 내용 및 아이의 표현을 구분해 알려주세요.", 89, "risk-history", C + R),
        q("back_pain.older_frailty_falls_mobility_cognition_and_caregiver_support", "Older Adult Frailty and Support Context", "string", "older-context", "고령자라면 평소 보행·낙상·골절·인지 상태, 최근 기능 저하, 보조기구와 보호자 도움을 알려주세요.", 88, "risk-history", R),
        q("back_pain.communication_language_hearing_cognition_and_accessibility", "Communication and Accessibility Needs", "string", "accessibility", "통역·청각·시각·인지·문해·디지털 사용 또는 자세 유지에 필요한 도움과 선호하는 응답 방법을 알려주세요.", 87, "handoff", R),
        q("back_pain.information_source_reliability_conflict_and_proxy", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자·목격자 중 누가 답하는지, 기록·영상·검사자료 유무와 기억이 불확실하거나 서로 다른 부분을 알려주세요.", 86, "handoff", R),
        q("back_pain.patient_goal_expected_help_and_additional_rfe", "Patient Goal Expected Help and Additional RFE", "string", "goal", "진료에서 확인하고 싶은 내용, 원하는 도움과 질문에 없던 다른 증상·의견 또는 별도 문진이 필요한 문제를 알려주세요.", 85, "handoff", C + R),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    for key, identifier in G.items():
        nodes[identifier] = {
            "id": identifier,
            "type": "ClinicalGroup",
            "display": key.replace("-", " ").title(),
        }
    doc["extra_nodes"] = list(nodes.values())
    doc["default_refresh"].update({
        "last_assessed_at": "2026-07-19",
        "next_monitor_at": "2026-07-21",
        "next_full_review_at": "2027-01-15",
    })
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc: dict) -> dict:
    result = completion_policy(
        prefix=P,
        fragment=doc,
        presentation_fact="symptom.back_pain.current",
        question_budget=85,
        source_refs=SOURCES,
    )
    result["required_facts"]["routine"] = [
        "back_pain.primary_context",
        "symptom.duration",
        "symptom.back_pain.location",
        "symptom.back_pain.onset",
        "symptom.back_pain.functional_impact",
        "back_pain.patient_words_and_main_concern",
        "back_pain.first_latest_onset_context_and_course",
        "back_pain.episode_frequency_duration_baseline_and_between_state",
        "back_pain.exact_site_laterality_surface_depth_and_radiation",
        "back_pain.character_quality_and_patient_comparison",
        "back_pain.movement_posture_load_cough_strain_and_relief_pattern",
        "back_pain.walk_transfer_stairs_sleep_work_selfcare_and_driving_impact",
        "back_pain.information_source_reliability_conflict_and_proxy",
        "back_pain.patient_goal_expected_help_and_additional_rfe",
    ]
    result["conditional_required_facts"] = [{
        "selector_fact": "back_pain.primary_context",
        "cases": {
            "acute_mechanical": [
                "event.mechanical_trigger",
                "back_pain.day_night_rest_sleep_morning_stiffness_and_activity_pattern",
                "back_pain.treatment_activity_heat_therapy_response_and_recurrence",
                "back_pain.occupation_manual_handling_posture_vibration_ppe_and_work_change",
            ],
            "radicular_or_neurological": [
                "symptom.radicular_leg_pain", "symptom.unilateral_leg_numbness",
                "symptom.unilateral_leg_weakness",
                "back_pain.leg_radiation_route_side_below_knee_and_timing",
                "back_pain.weakness_numbness_distribution_tasks_sequence_and_trend",
                "back_pain.bladder_bowel_saddle_sexual_change_onset_and_baseline",
            ],
            "trauma_or_fracture_risk": [
                "back_pain.trauma_mechanism_height_force_date_and_immediate_function",
                "history.osteoporosis_or_long_term_steroids",
                "back_pain.osteoporosis_steroid_frailty_fall_and_fracture_history",
                "back_pain.anticoagulant_antiplatelet_bleeding_disorder_and_last_dose",
                "back_pain.prior_examination_imaging_lab_date_result_source_and_pending",
            ],
            "fever_infection_or_systemic": [
                "back_pain.fever_temperature_systemic_state_infection_exposure_and_timeline",
                "back_pain.recent_procedure_injection_device_wound_and_infection_context",
                "back_pain.immune_suppression_diabetes_infection_risk_and_timing",
                "back_pain.prior_examination_imaging_lab_date_result_source_and_pending",
            ],
            "night_rest_or_persistent": [
                "symptom.back_pain.night_or_rest_pain", "symptom.unintentional_weight_loss",
                "history.malignancy", "symptom.back_pain.persistent",
                "back_pain.weight_change_night_rest_thoracic_and_systemic_timeline",
                "back_pain.cancer_history_type_treatment_date_status_and_followup",
                "back_pain.prior_examination_imaging_lab_date_result_source_and_pending",
            ],
            "urinary_abdominal_or_pelvic_context": [
                "symptom.urinary_symptoms",
                "back_pain.urinary_abdominal_bowel_menstrual_and_pelvic_relation",
                "back_pain.prior_examination_imaging_lab_date_result_source_and_pending",
            ],
            "chronic_recurrent_or_followup": [
                "symptom.back_pain.persistent",
                "back_pain.day_night_rest_sleep_morning_stiffness_and_activity_pattern",
                "back_pain.prior_episode_spine_diagnosis_surgery_injection_and_recovery",
                "back_pain.medicine_analgesic_dose_timing_effect_adverse_effect_and_allergy",
                "back_pain.prior_examination_imaging_lab_date_result_source_and_pending",
                "back_pain.treatment_activity_heat_therapy_response_and_recurrence",
            ],
            "pregnancy_or_postpartum": [
                "back_pain.pregnancy_gestation_postpartum_delivery_anesthesia_and_complications",
                "back_pain.urinary_abdominal_bowel_menstrual_and_pelvic_relation",
                "back_pain.medicine_analgesic_dose_timing_effect_adverse_effect_and_allergy",
            ],
            "child_or_proxy": [
                "back_pain.child_age_growth_fever_function_trauma_and_proxy_observation",
                "back_pain.information_source_reliability_conflict_and_proxy",
                "back_pain.communication_language_hearing_cognition_and_accessibility",
            ],
            "other_or_unclear": [
                "back_pain.day_night_rest_sleep_morning_stiffness_and_activity_pattern",
                "back_pain.urinary_abdominal_bowel_menstrual_and_pelvic_relation",
                "back_pain.prior_episode_spine_diagnosis_surgery_injection_and_recovery",
                "back_pain.medicine_analgesic_dose_timing_effect_adverse_effect_and_allergy",
                "back_pain.occupation_manual_handling_posture_vibration_ppe_and_work_change",
                "back_pain.communication_language_hearing_cognition_and_accessibility",
            ],
        },
    }]
    return result


def clinician(doc: dict) -> dict:
    result = load(CLINICIAN)
    ids = {item["fact"]["id"] for item in doc["entries"]}
    ids.update({"pain.frequency", "pain.nrs_score"})
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.back_pain"] = sorted(ids)
    return result


def routine_cases(doc: dict, completion: dict) -> dict[str, dict]:
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    always = completion["required_facts"]["always"]
    core = completion["required_facts"]["routine"]
    branches = completion["conditional_required_facts"][0]["cases"]
    forbidden = [
        "diagnosis.cauda_equina_syndrome", "diagnosis.spinal_infection",
        "diagnosis.spinal_malignancy", "diagnosis.vertebral_fracture",
        "recommendation.mri", "recommendation.xray", "recommendation.nsaid",
        "recommendation.surgery",
    ]

    def value(fid: str):
        fact = by_id[fid]
        if fact["value_type"] == "boolean":
            return False
        if fact["value_type"] == "coded":
            return fact.get("allowed_values", ["other_or_unclear"])[-1]
        if fact["value_type"] == "quantity":
            return {"amount": 3, "unit": "days"}
        return "특이사항 없음"

    def state(branch: str) -> dict:
        ids = dict.fromkeys([*always, *core, *branches[branch]])
        result = {fid: {"value": value(fid)} for fid in ids}
        result["symptom.back_pain.current"] = {"value": True}
        result["back_pain.primary_context"] = {"value": branch}
        result["pain.frequency"] = {"value": "daily"}
        result["pain.nrs_score"] = {"value": 5}
        return result

    specs = [
        ("ACUTE-MECHANICAL-HANDOFF", "acute_mechanical", 38, "물건을 옮긴 뒤 시작한 허리 통증을 진료 전에 정리합니다.", {}),
        ("RADICULAR-UNILATERAL-ROUTE", "radicular_or_neurological", 47, "허리에서 한쪽 다리로 뻗치는 통증과 저림의 경로를 정리합니다.", {"symptom.radicular_leg_pain": {"value": True}, "symptom.unilateral_leg_numbness": {"value": True}}),
        ("MINOR-TRAUMA-OLDER", "trauma_or_fracture_risk", 74, "작은 낙상 뒤 통증과 골절 위험 정보를 정리합니다.", {"history.osteoporosis_or_long_term_steroids": {"value": True}}),
        ("SYSTEMIC-CONTEXT-ROUTINE", "fever_infection_or_systemic", 55, "현재 응급 신호는 없지만 최근 시술과 감염 위험 맥락을 정리합니다.", {}),
        ("PERSISTENT-NIGHT-RESULT-SOURCE", "night_rest_or_persistent", 63, "지속되는 윗등 통증과 이전 검사 자료 출처를 정리합니다.", {"symptom.back_pain.persistent": {"value": True}, "symptom.back_pain.night_or_rest_pain": {"value": True}}),
        ("URINARY-PELVIC-RELATION", "urinary_abdominal_or_pelvic_context", 36, "허리 통증과 소변·골반 증상의 시간 관계를 정리합니다.", {"symptom.urinary_symptoms": {"value": True}}),
        ("CHRONIC-FOLLOWUP-TREATMENT", "chronic_recurrent_or_followup", 58, "반복되는 허리 통증의 이전 평가와 치료 반응을 정리합니다.", {"symptom.back_pain.persistent": {"value": True}}),
        ("PREGNANCY-POSTPARTUM", "pregnancy_or_postpartum", 31, "출산 후 허리 통증과 분만·마취·약물 맥락을 정리합니다.", {}),
        ("CHILD-PROXY", "child_or_proxy", 12, "보호자가 소아의 허리 통증과 보행·수면 변화를 대신 설명합니다.", {"back_pain.information_source_reliability_conflict_and_proxy": {"value": "보호자 대리, 아이 표현과 관찰을 구분함"}}),
        ("OLDER-ACCESSIBILITY", "other_or_unclear", 82, "고령자의 통증과 보행 보조·청각 지원 필요를 정리합니다.", {"back_pain.older_frailty_falls_mobility_cognition_and_caregiver_support": {"value": "보행기 사용, 보호자 도움"}, "back_pain.communication_language_hearing_cognition_and_accessibility": {"value": "청각 지원과 짧은 문장 필요"}}),
        ("MULTI-RFE-ADDITIONAL-COMMENT", "other_or_unclear", 49, "허리 통증 외에 별도 문진이 필요한 소화 증상도 전달합니다.", {"back_pain.patient_goal_expected_help_and_additional_rfe": {"value": "소화 증상을 별도 RFE로 문진 요청"}}),
        ("PAIN-NRS-REQUIRED", "acute_mechanical", 42, "현재 허리 통증의 빈도와 NRS 원점수를 필수로 기록합니다.", {"pain.frequency": {"value": "daily"}, "pain.nrs_score": {"value": 8}}),
    ]
    result = {}
    for key, branch, age, statement, overrides in specs:
        hidden = state(branch)
        hidden.update(overrides)
        expected = {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 85,
            "forbidden_assertions": forbidden,
        }
        if key == "PAIN-NRS-REQUIRED":
            expected["expected_known_facts"] = {"pain.nrs_score": 8}
        result[f"BACK-{key}.json"] = {
            "id": f"BACK-{key}",
            "simulation_language": "ko",
            "persona": {"age": age},
            "initial_statement": {"ko": statement},
            "hidden_state": hidden,
            "expected": expected,
            "provenance": provenance(SOURCES),
        }

    absent = state("chronic_recurrent_or_followup")
    missing = "back_pain.prior_examination_imaging_lab_date_result_source_and_pending"
    absent.pop(missing)
    result["BACK-DATA-ABSENT-PRIOR-RESULT.json"] = {
        "id": "BACK-DATA-ABSENT-PRIOR-RESULT",
        "simulation_language": "ko",
        "persona": {"age": 67},
        "encounter_context": {
            "care_setting": "primary_care",
            "encounter_type": "follow_up",
            "interview_initiator": "caregiver",
            "interview_mode": "telephone",
            "available_information": ["no_previous_records"],
            "time_constraint": "scheduled",
            "clinical_responsibility": "decision_support",
        },
        "initial_statement": {"ko": "보호자가 답하지만 이전 영상 결과지는 지금 확인할 수 없습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "asked-unknown"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 85,
            "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }
    declined = state("acute_mechanical")
    declined_fact = "back_pain.patient_words_and_main_concern"
    declined.pop(declined_fact)
    result["BACK-DATA-ABSENT-001.json"] = {
        "id": "BACK-DATA-ABSENT-001",
        "simulation_language": "ko",
        "persona": {"age": 39, "communication_style": "uncertain"},
        "initial_statement": {"ko": "급성 허리 통증 문진에서 한 항목은 답변하지 않겠습니다."},
        "hidden_state": declined,
        "response_behavior": {declined_fact: {"dataAbsentReason": "asked-declined"}},
        "expected": {
            "expected_data_absent_reasons": {declined_fact: "asked-declined"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 85,
            "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }
    return result


def main() -> None:
    doc = fragment()
    completion = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, completion)
    write_json(CLINICIAN, clinician(doc))
    for name, case in routine_cases(doc, completion).items():
        write_json(f"simulation/patients/musculoskeletal/back-pain/{name}", case)


if __name__ == "__main__":
    main()
