#!/usr/bin/env python3
"""Strengthen research-only edema knowledge for clinician pre-visit handoff."""
from __future__ import annotations

import json

import seed_edema
from profile_support import ROOT, completion_policy, entry, provenance, write_json


P = "edema"
FRAGMENT = "knowledge/generated/cardiovascular/edema/edema.json"
POLICY = "policies/primary-care-edema-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
PAIN = "knowledge/shared/hira-pain-assessment.json"
SIM_ROOT = ROOT / "simulation/patients/cardiovascular/edema"
SOURCES = [
    "source.nhs.edema.2026",
    "source.nice.ng158.vte.2023",
    "source.nice.ng106.heart-failure.2025",
    "source.stom.edema.20260714",
]
G = {key: f"group.edema.{key}" for key in (
    "routing", "course", "measurement", "local-detail", "cardiopulmonary-detail",
    "thromboembolic-detail", "systemic-detail", "pregnancy-detail",
    "history-treatment", "function", "handoff",
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
        "acute_unilateral_leg", "bilateral_dependent_leg", "generalized_or_fluid_change",
        "face_or_upper_body", "local_inflammatory_or_wound", "pregnancy_or_postpartum",
        "medicine_related", "chronic_venous_or_lymphatic", "child_or_proxy",
        "followup_or_result_review", "other_or_unclear",
    ]
    additions = [
        q("edema.primary_context", "Primary Edema Context", "coded", "primary-context", "가장 가까운 상황은 갑작스러운 한쪽 다리 부종, 양쪽 다리·자세 관련, 전신·체액 변화, 얼굴·상체, 국소 염증·상처, 임신·산후, 약물 관련, 만성 정맥·림프, 소아·보호자 응답, 추적·결과 확인, 또는 불분명 중 무엇인가요?", 117, "routing", C + R, allowed_values=contexts),
        q("edema.patient_words_first_noticed_change_and_main_concern", "Patient Description and Main Concern", "string", "patient-words", "본인의 표현으로 어디가 어떻게 붓는지, 처음 알아차린 변화와 가장 불편하거나 걱정되는 점을 알려주세요.", 116, "course", C),
        q("edema.first_latest_onset_exact_time_context_and_progression", "First and Latest Edema Timeline", "string", "timeline", "처음과 가장 최근 붓기의 날짜·시각, 당시 하던 일과 이후 퍼짐·호전·악화·반복 양상을 알려주세요.", 115, "course", C + R),
        q("edema.daily_episode_duration_baseline_and_between_state", "Edema Frequency Duration and Baseline", "string", "episode-course", "매일 또는 간헐적인지, 한 번 지속되는 시간, 사이에 완전히 빠지는지와 평소 기준 상태를 알려주세요.", 114, "course", C),
        q("edema.exact_site_side_extent_sequence_and_asymmetry", "Exact Site Side Extent and Sequence", "string", "distribution-detail", "발가락·발등·발목·종아리·허벅지·손·얼굴·배 등 정확한 부위, 좌우 차이와 어느 부위부터 어떤 순서로 퍼졌는지 알려주세요.", 113, "local-detail", C + R),
        q("edema.circumference_landmark_time_device_and_side_comparison", "Circumference Measurement Provenance", "string", "circumference", "둘레를 쟀다면 측정 부위의 기준점, 좌우 cm 값, 측정 시각·도구와 같은 조건에서 잰 것인지 알려주세요.", 112, "measurement", C + R),
        q("edema.weight_date_time_scale_trend_and_dry_baseline", "Weight Measurement and Trend", "string", "weight-trend", "최근 체중의 날짜·시각·체중계, 며칠간 변화량과 평소 붓기 없을 때 기준 체중을 알려주세요.", 111, "measurement", C + R),
        q("edema.pitting_observation_method_depth_duration_and_recovery", "Pitting Observation Detail", "string", "pitting-detail", "눌러 본 경우 어느 부위를 얼마 동안 눌렀고 자국의 깊이·지속시간과 다시 돌아오는 시간을 알려주세요. 확인하지 않았다면 확인하지 않았다고 답해 주세요.", 110, "measurement", C),
        q("edema.pain_nrs", "Edema-associated Pain NRS", "integer", "pain-nrs", "[필수] 부은 부위에 통증이 있다면 가장 심할 때 통증을 0부터 10까지 숫자로 알려주세요.", 109, "local-detail", C + S),
        q("edema.pain_tenderness_heaviness_tightness_and_movement_relation", "Pain Tenderness Heaviness and Tightness", "string", "local-sensation", "통증·압통·무거움·당김·팽팽함이 있다면 정확한 부위, 걷기·관절 움직임·만지기와의 관계를 알려주세요.", 108, "local-detail", C + R),
        q("edema.skin_colour_temperature_texture_wound_drainage_and_timeline", "Skin Wound and Drainage Detail", "string", "skin-detail", "피부색·열감·광택·단단함·가려움·상처·진물 변화와 붓기 전후 시작 시점을 알려주세요.", 107, "local-detail", C + S),
        q("edema.dyspnea_chest_symptom_order_rest_exertion_sleep_and_recovery", "Cardiopulmonary Symptom Sequence and Recovery", "string", "cardiopulmonary-sequence", "숨참·흉통·기침·실신감이 있다면 붓기 전·중·후 순서, 안정·운동·수면 영향과 회복 과정을 알려주세요.", 106, "cardiopulmonary-detail", C + S),
        q("edema.orthopnea_pillow_count_nocturnal_awaking_and_baseline_change", "Orthopnea and Nocturnal Dyspnea Detail", "string", "orthopnea-detail", "누울 때 숨참, 사용하는 베개 수, 밤에 숨차서 깨는 횟수와 평소 수면 상태에서 달라진 시점을 알려주세요.", 105, "cardiopulmonary-detail", C + R),
        q("edema.pulse_bp_oxygen_temperature_time_device_position_and_source", "Relevant Measurement Provenance", "string", "vital-measurements", "확인한 혈압·맥박·산소포화도·체온이 있다면 값, 날짜·시각, 자세·기기와 누가 측정했는지 알려주세요.", 104, "measurement", R),
        q("edema.unilateral_leg_onset_route_size_change_skin_and_function", "Unilateral Leg Swelling Detail", "string", "unilateral-detail", "한쪽 다리만 붓는다면 시작 시각, 발에서 위로 퍼지는지, 좌우 크기 차이, 피부 변화와 걷기 영향을 알려주세요.", 103, "thromboembolic-detail", C + S),
        q("edema.immobility_surgery_cast_travel_date_duration_and_mobility_return", "Immobility Surgery and Travel Timeline", "string", "immobility-detail", "수술·입원·깁스·침상안정·장거리 이동이 있었다면 날짜, 움직이지 못한 시간과 평소 활동으로 돌아온 시점을 알려주세요.", 102, "thromboembolic-detail", R),
        q("edema.vte_cancer_hormone_pregnancy_family_and_anticoagulant_context", "Thromboembolic Risk History Detail", "string", "vte-risk-detail", "본인·가족의 혈전 병력, 암 치료, 피임약·호르몬, 임신·산후와 항응고제 이름·용량·마지막 복용을 알려주세요.", 101, "thromboembolic-detail", R),
        q("edema.urine_output_frequency_appearance_intake_and_baseline_change", "Urine Output and Intake Detail", "string", "urine-detail", "소변 횟수·대략적인 양·색·거품 변화, 물 섭취량과 평소 기준에서 달라진 시점을 알려주세요.", 100, "systemic-detail", C + R),
        q("edema.abdominal_girth_appetite_nausea_jaundice_and_bowel_context", "Abdominal and Hepatic Context", "string", "abdominal-detail", "배 둘레·팽만, 식욕·메스꺼움, 피부/눈 노래짐과 배변 변화가 있다면 시작 순서를 알려주세요.", 99, "systemic-detail", D + R),
        q("edema.heart_kidney_liver_venous_lymphatic_diagnosis_stage_and_status", "Relevant Disease History and Current Status", "string", "disease-history", "심장·신장·간·정맥·림프 질환의 정확한 진단명·진단 시기·현재 단계와 담당 진료 상태를 알려주세요.", 98, "history-treatment", R),
        q("edema.prior_node_surgery_radiation_infection_or_limb_procedure", "Lymphatic and Limb Procedure History", "string", "procedure-history", "림프절 수술·방사선 치료, 정맥/혈관 시술, 감염·외상·관절수술이 있었다면 부위·시기와 붓기 시작과의 관계를 알려주세요.", 97, "history-treatment", R),
        q("edema.medicine_name_dose_start_change_last_use_and_temporal_relation", "Medicine Exposure Timeline", "string", "medicine-detail", "처방약·일반약·호르몬·보충제의 이름·용량·시작/변경일·마지막 사용과 붓기 시작 시점의 관계를 알려주세요.", 96, "history-treatment", D + R),
        q("edema.salt_fluid_alcohol_activity_heat_and_posture_change", "Diet Fluid Activity Heat and Posture Context", "string", "lifestyle-detail", "최근 소금·수분·술 섭취, 활동량, 더위, 오래 서기·앉기와 붓기의 시간 관계를 알려주세요.", 95, "systemic-detail", D),
        q("edema.pregnancy_gestation_postpartum_delivery_bp_proteinuria_and_warning_timeline", "Pregnancy and Postpartum Detail", "string", "pregnancy-context", "해당되는 경우 임신 주수 또는 출산 후 기간, 분만일·방식, 혈압·소변 단백 설명과 두통·시야·윗배 통증의 시작 순서를 알려주세요.", 94, "pregnancy-detail", S + R),
        q("edema.prior_episode_trigger_diagnosis_resolution_and_current_difference", "Prior Edema Episode and Recovery", "string", "prior-episode", "이전 붓기의 시기·유발 상황·진단, 가라앉기까지 걸린 시간과 이번에 달라진 점을 알려주세요.", 93, "history-treatment", C + R),
        q("edema.prior_exam_ecg_echo_ultrasound_imaging_lab_date_result_and_source", "Prior Examination Imaging and Laboratory Results", "string", "prior-tests", "이전 진찰, ECG·심초음파·혈관초음파·영상, 신장·간·단백·소변 검사의 날짜·설명받은 결과·자료 출처와 미확인 결과를 알려주세요.", 92, "history-treatment", R),
        q("edema.elevation_compression_diuretic_skin_care_response_and_adverse_effect", "Treatment Attempt and Response", "string", "treatment-response", "다리 올리기·압박·처방 이뇨제·피부관리 등 이미 시행한 방법, 시기·횟수·효과·부작용을 알려주세요.", 91, "history-treatment", C + R),
        q("edema.walking_footwear_hand_use_sleep_work_selfcare_and_fall_impact", "Detailed Functional and Safety Impact", "string", "function-detail", "걷기·신발·손 사용·수면·업무·씻기·옷입기와 낙상 위험에 어떤 영향이 있는지 알려주세요.", 90, "function", C + R),
        q("edema.child_age_growth_nephrotic_infection_function_and_proxy_observation", "Child Edema and Proxy Observation", "string", "child-context", "소아라면 나이·성장, 눈 주위·소변·감염·활동 변화와 보호자가 직접 본 내용 및 아이의 표현을 구분해 알려주세요.", 89, "history-treatment", C + R),
        q("edema.older_frailty_mobility_falls_cognition_and_caregiver_support", "Older Adult Frailty and Support Context", "string", "older-context", "고령자라면 평소 보행·낙상·인지·자가관리, 최근 기능 변화와 보조기구·보호자 도움을 알려주세요.", 88, "function", R),
        q("edema.communication_language_hearing_cognition_and_accessibility", "Communication and Accessibility Needs", "string", "accessibility", "통역·청각·시각·인지·문해·디지털 사용 또는 자세 유지에 필요한 도움과 선호하는 응답 방법을 알려주세요.", 87, "handoff", R),
        q("edema.information_source_reliability_conflict_and_proxy", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자 중 누가 답하는지, 체중·둘레·활력·검사 기록 유무와 기억이 불확실하거나 자료가 서로 다른 부분을 알려주세요.", 86, "handoff", R),
        q("edema.patient_goal_expected_help_and_additional_rfe", "Patient Goal Expected Help and Additional RFE", "string", "goal", "진료에서 확인하고 싶은 내용, 원하는 도움과 질문에 없던 다른 증상·의견 또는 별도 문진이 필요한 문제를 알려주세요.", 85, "handoff", C + R),
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
        presentation_fact="symptom.edema.current",
        question_budget=85,
        source_refs=SOURCES,
    )
    result["required_facts"]["routine"] = [
        "edema.primary_context", "symptom.duration", "symptom.edema.location",
        "symptom.edema.laterality", "symptom.edema.severity", "symptom.edema.pain",
        "symptom.edema.functional_impact",
        "edema.patient_words_first_noticed_change_and_main_concern",
        "edema.first_latest_onset_exact_time_context_and_progression",
        "edema.daily_episode_duration_baseline_and_between_state",
        "edema.exact_site_side_extent_sequence_and_asymmetry",
        "edema.walking_footwear_hand_use_sleep_work_selfcare_and_fall_impact",
        "edema.information_source_reliability_conflict_and_proxy",
        "edema.patient_goal_expected_help_and_additional_rfe",
    ]
    result["conditional_required_facts"] = [{
        "selector_fact": "edema.primary_context",
        "cases": {
            "acute_unilateral_leg": [
                "symptom.unilateral_leg_pain_swelling", "symptom.edema.red_or_hot",
                "edema.unilateral_leg_onset_route_size_change_skin_and_function",
                "edema.circumference_landmark_time_device_and_side_comparison",
                "edema.immobility_surgery_cast_travel_date_duration_and_mobility_return",
                "edema.vte_cancer_hormone_pregnancy_family_and_anticoagulant_context",
            ],
            "bilateral_dependent_leg": [
                "symptom.edema.time_pattern", "symptom.edema.pitting",
                "edema.pitting_observation_method_depth_duration_and_recovery",
                "edema.weight_date_time_scale_trend_and_dry_baseline",
                "edema.salt_fluid_alcohol_activity_heat_and_posture_change",
                "edema.elevation_compression_diuretic_skin_care_response_and_adverse_effect",
            ],
            "generalized_or_fluid_change": [
                "symptom.markedly_reduced_urine", "symptom.rapid_weight_gain",
                "symptom.abdominal_swelling_or_ascites", "symptom.dyspnea_on_exertion",
                "symptom.orthopnea", "symptom.paroxysmal_nocturnal_dyspnea",
                "edema.weight_date_time_scale_trend_and_dry_baseline",
                "edema.urine_output_frequency_appearance_intake_and_baseline_change",
                "edema.orthopnea_pillow_count_nocturnal_awaking_and_baseline_change",
                "edema.pulse_bp_oxygen_temperature_time_device_position_and_source",
            ],
            "face_or_upper_body": [
                "symptom.sudden_face_tongue_throat_swelling",
                "edema.exact_site_side_extent_sequence_and_asymmetry",
                "edema.skin_colour_temperature_texture_wound_drainage_and_timeline",
                "edema.urine_output_frequency_appearance_intake_and_baseline_change",
                "edema.prior_node_surgery_radiation_infection_or_limb_procedure",
            ],
            "local_inflammatory_or_wound": [
                "symptom.edema.red_or_hot", "symptom.fever",
                "symptom.edema.skin_change_or_wound",
                "event.edema.injury_bite_or_local_trigger",
                "edema.skin_colour_temperature_texture_wound_drainage_and_timeline",
                "edema.pain_tenderness_heaviness_tightness_and_movement_relation",
            ],
            "pregnancy_or_postpartum": [
                "patient.pregnant_or_postpartum", "symptom.preeclampsia_warning_features",
                "edema.pregnancy_gestation_postpartum_delivery_bp_proteinuria_and_warning_timeline",
                "edema.pulse_bp_oxygen_temperature_time_device_position_and_source",
                "edema.urine_output_frequency_appearance_intake_and_baseline_change",
            ],
            "medicine_related": [
                "medication.edema_relevant",
                "edema.medicine_name_dose_start_change_last_use_and_temporal_relation",
                "edema.heart_kidney_liver_venous_lymphatic_diagnosis_stage_and_status",
                "edema.prior_episode_trigger_diagnosis_resolution_and_current_difference",
            ],
            "chronic_venous_or_lymphatic": [
                "symptom.edema.pitting", "symptom.edema.skin_change_or_wound",
                "edema.skin_colour_temperature_texture_wound_drainage_and_timeline",
                "edema.heart_kidney_liver_venous_lymphatic_diagnosis_stage_and_status",
                "edema.prior_node_surgery_radiation_infection_or_limb_procedure",
                "edema.prior_exam_ecg_echo_ultrasound_imaging_lab_date_result_and_source",
                "edema.elevation_compression_diuretic_skin_care_response_and_adverse_effect",
            ],
            "child_or_proxy": [
                "edema.child_age_growth_nephrotic_infection_function_and_proxy_observation",
                "edema.information_source_reliability_conflict_and_proxy",
                "edema.communication_language_hearing_cognition_and_accessibility",
            ],
            "followup_or_result_review": [
                "edema.prior_episode_trigger_diagnosis_resolution_and_current_difference",
                "edema.prior_exam_ecg_echo_ultrasound_imaging_lab_date_result_and_source",
                "edema.elevation_compression_diuretic_skin_care_response_and_adverse_effect",
                "edema.weight_date_time_scale_trend_and_dry_baseline",
            ],
            "other_or_unclear": [
                "edema.pitting_observation_method_depth_duration_and_recovery",
                "edema.weight_date_time_scale_trend_and_dry_baseline",
                "edema.dyspnea_chest_symptom_order_rest_exertion_sleep_and_recovery",
                "edema.urine_output_frequency_appearance_intake_and_baseline_change",
                "edema.heart_kidney_liver_venous_lymphatic_diagnosis_stage_and_status",
                "edema.medicine_name_dose_start_change_last_use_and_temporal_relation",
                "edema.communication_language_hearing_cognition_and_accessibility",
            ],
        },
    }]
    return result


def clinician(doc: dict) -> dict:
    result = load(CLINICIAN)
    ids = {item["fact"]["id"] for item in doc["entries"]}
    ids.update({"pain.frequency", "edema.pain_nrs"})
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.edema"] = sorted(ids)
    return result


def routine_cases(doc: dict, completion: dict) -> dict[str, dict]:
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    always = completion["required_facts"]["always"]
    core = completion["required_facts"]["routine"]
    branches = completion["conditional_required_facts"][0]["cases"]
    forbidden = [
        "diagnosis.deep_vein_thrombosis", "diagnosis.heart_failure",
        "diagnosis.nephrotic_syndrome", "diagnosis.cirrhosis",
        "recommendation.diuretic", "recommendation.anticoagulant",
        "recommendation.compression_stocking",
    ]

    def value(fid: str):
        fact = by_id[fid]
        if fact["value_type"] == "boolean":
            return False
        if fact["value_type"] == "coded":
            return fact.get("allowed_values", ["other_or_unclear"])[-1]
        if fact["value_type"] == "quantity":
            return {"amount": 4, "unit": "days"}
        return "특이사항 없음"

    def state(branch: str) -> dict:
        ids = dict.fromkeys([*always, *core, *branches[branch]])
        result = {fid: {"value": value(fid)} for fid in ids}
        result["symptom.edema.current"] = {"value": True}
        result["edema.primary_context"] = {"value": branch}
        result["symptom.edema.severity"] = {"value": "moderate"}
        result["symptom.edema.pain"] = {"value": "none"}
        return result

    specs = [
        ("UNILATERAL-NO-RED-FLAG", "acute_unilateral_leg", 46, "한쪽 다리 붓기의 시작과 좌우 차이, 이동·수술 위험 맥락을 정리합니다.", {"symptom.unilateral_leg_pain_swelling": {"value": False}}),
        ("BILATERAL-DEPENDENT-MEASURED", "bilateral_dependent_leg", 59, "저녁에 심해지는 양쪽 발목 붓기와 둘레·체중 기록을 정리합니다.", {"symptom.edema.laterality": {"value": "bilateral"}}),
        ("GENERALIZED-FLUID-CONTEXT", "generalized_or_fluid_change", 68, "전신 붓기와 체중·소변·호흡 변화를 진료 전에 정리합니다.", {"symptom.edema.location": {"value": "generalized"}}),
        ("FACE-UPPER-BODY", "face_or_upper_body", 34, "얼굴 붓기의 범위와 피부·소변·시술 맥락을 정리합니다.", {"symptom.edema.location": {"value": "face"}}),
        ("LOCAL-WOUND-NO-FEVER", "local_inflammatory_or_wound", 41, "상처 주변 국소 붓기와 피부 변화·통증을 정리합니다.", {"symptom.edema.skin_change_or_wound": {"value": True}}),
        ("PREGNANCY-ROUTINE", "pregnancy_or_postpartum", 31, "임신 중 붓기와 혈압·소변·경고 증상 시점을 정리합니다.", {"patient.pregnant_or_postpartum": {"value": "pregnant"}}),
        ("MEDICINE-TIMING", "medicine_related", 54, "최근 약 변경과 붓기의 시간 관계를 정리합니다.", {}),
        ("CHRONIC-LYMPHATIC", "chronic_venous_or_lymphatic", 63, "만성 부종의 피부·시술·검사와 기존 관리 반응을 정리합니다.", {}),
        ("CHILD-PROXY", "child_or_proxy", 9, "보호자가 소아의 눈 주위 붓기와 소변·활동 변화를 설명합니다.", {"edema.information_source_reliability_conflict_and_proxy": {"value": "보호자 대리, 직접 관찰과 아이 표현을 구분함"}}),
        ("FOLLOWUP-RESULT-SOURCE", "followup_or_result_review", 72, "부종 추적에서 이전 검사 결과와 자료 출처를 정리합니다.", {}),
        ("OLDER-ACCESSIBILITY", "other_or_unclear", 84, "고령자의 보행·낙상·청각 지원과 보호자 정보를 정리합니다.", {"edema.older_frailty_mobility_falls_cognition_and_caregiver_support": {"value": "보행 보조와 보호자 도움 필요"}, "edema.communication_language_hearing_cognition_and_accessibility": {"value": "청각 지원과 짧은 질문 필요"}}),
        ("MULTI-RFE-ADDITIONAL-COMMENT", "other_or_unclear", 50, "붓기 외에 별도 문진이 필요한 호흡 증상도 전달합니다.", {"edema.patient_goal_expected_help_and_additional_rfe": {"value": "호흡 증상을 별도 RFE로 문진 요청"}}),
        ("PAIN-NRS-REQUIRED", "local_inflammatory_or_wound", 45, "통증이 동반된 부종에서 빈도와 NRS 원점수를 필수 기록합니다.", {"symptom.edema.pain": {"value": "moderate"}, "pain.frequency": {"value": "daily"}, "edema.pain_nrs": {"value": 6}}),
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
            expected["expected_known_facts"] = {"edema.pain_nrs": 6}
        result[f"EDEMA-{key}.json"] = {
            "id": f"EDEMA-{key}", "simulation_language": "ko",
            "persona": {"age": age}, "initial_statement": {"ko": statement},
            "hidden_state": hidden, "expected": expected,
            "provenance": provenance(SOURCES),
        }

    absent = state("followup_or_result_review")
    missing = "edema.prior_exam_ecg_echo_ultrasound_imaging_lab_date_result_and_source"
    absent.pop(missing)
    result["EDEMA-DATA-ABSENT.json"] = {
        "id": "EDEMA-DATA-ABSENT", "simulation_language": "ko",
        "persona": {"age": 70},
        "encounter_context": {
            "care_setting": "primary_care", "encounter_type": "follow_up",
            "interview_initiator": "caregiver", "interview_mode": "telephone",
            "available_information": ["no_previous_records"],
            "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
        },
        "initial_statement": {"ko": "보호자가 답하지만 이전 검사 결과지는 지금 확인할 수 없습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "asked-unknown"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 85, "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }
    return result


def main() -> None:
    seed_edema.main()
    doc = fragment()
    completion = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, completion)
    write_json(CLINICIAN, clinician(doc))
    pain = load(PAIN)
    pain["profile_bindings"]["edema"]["existing_nrs_fact"] = "edema.pain_nrs"
    write_json(PAIN, pain)
    for name, case in routine_cases(doc, completion).items():
        write_json(f"simulation/patients/cardiovascular/edema/{name}", case)


if __name__ == "__main__":
    main()
