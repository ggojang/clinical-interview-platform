#!/usr/bin/env python3
"""Strengthen research-only joint and limb complaint clinician handoff."""
from __future__ import annotations

import json

import seed_joint_limb_complaint
from profile_support import ROOT, completion_policy, entry, write_json


P = "joint-limb"
FRAGMENT = "knowledge/generated/musculoskeletal/joint-limb/joint-limb.json"
POLICY = "policies/primary-care-joint-limb-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
RESEARCH = "sources/manifests/primary-care-joint-limb-research.json"
CREATED = "2026-07-21T00:00:00Z"
SOURCES = [
    "source.nhs.joint-pain.2026", "source.nhs.septic-arthritis.2023",
    "source.nice.ng38.fracture.2025", "source.nice.ng226.osteoarthritis.2022",
    "source.nice.ng100.rheumatoid-arthritis.2020",
    "source.nice.ng158.venous-thromboembolism.2023",
    "source.nice.ng12.skeletal-soft-tissue.2026",
    "source.stom.joint-limb.20260714",
]
G = {key: f"group.joint-limb.{key}" for key in (
    "routing", "site-course", "pain-detail", "trauma-detail",
    "inflammatory-detail", "neurovascular-detail", "exposure-detail",
    "history-detail", "treatment-detail", "life-stage", "function-detail",
    "handoff",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]


def provenance(source_refs: list[str]) -> dict:
    return {
        "created_by": {"type": "ai", "id": "codex-gpt5"},
        "created_at": CREATED, "source_refs": source_refs,
        "review_status": "unreviewed", "version": "0.1.0",
    }


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
        "acute_injury", "hot_swollen_single_joint", "mechanical_or_overuse",
        "multiple_or_inflammatory_joints", "calf_or_circulatory",
        "child_or_proxy", "pregnancy_or_postpartum",
        "followup_or_result_review", "other_or_unclear",
    ]
    additions = [
        q("joint_limb.primary_context", "Primary Joint or Limb Context", "coded", "primary-context", "가장 가까운 상황은 급성 외상, 뜨겁고 붓는 한 관절, 반복 사용·기계적 문제, 여러 관절·염증 양상, 종아리·순환 문제, 소아·보호자 응답, 임신·산후, 추적·결과 확인, 또는 불분명 중 무엇인가요?", 132, "routing", C + R, allowed_values=contexts),
        q("joint_limb.patient_words_first_change_and_main_concern", "Patient Description and Main Concern", "string", "patient-words", "본인의 표현으로 처음 알아차린 변화, 지금 가장 불편한 점과 가장 걱정되는 점을 알려주세요.", 116, "site-course", C),
        q("joint_limb.exact_structure_site_side_surface_depth_and_distribution", "Exact Structure Site and Distribution", "string", "site-detail", "정확한 관절·뼈·근육·힘줄 부위, 좌우, 앞뒤·안쪽/바깥쪽·표면/깊이와 한 곳인지 여러 곳인지 알려주세요.", 115, "site-course", C + R, terminology_binding={"system": "http://snomed.info/sct", "focus_code": "57676002", "attribute_code": "363698007"}, mrcm_ref="mapping.snomed-mrcm.joint-limb"),
        q("joint_limb.first_latest_date_time_activity_speed_course_and_baseline", "Detailed Joint or Limb Timeline", "string", "timeline", "처음과 가장 최근 증상의 날짜·시각, 당시 활동, 갑작스럽거나 서서히 시작한 속도, 호전·악화·반복 과정과 평소 상태에서 달라진 점을 알려주세요.", 114, "site-course", C + R),
        q("joint_limb.episode_frequency_duration_flare_recovery_and_between_state", "Episode Pattern and Between-state", "string", "episode-pattern", "간헐적이라면 하루·주당 횟수, 한 번 지속시간, 악화 기간과 회복 양상, 증상 사이에 완전히 정상으로 돌아오는지 알려주세요.", 113, "site-course", C),
        q("joint_limb.pain_exact_site_radiation_character_timing_and_pattern", "Detailed Pain Pattern", "string", "pain-pattern", "통증의 정확한 시작 부위와 퍼지는 방향, 쑤심·찌름·타는 듯함·전기 오는 느낌 등 양상, 지속/간헐 여부와 하루 중 변화를 알려주세요.", 112, "pain-detail", C + R),
        q("joint_limb.swelling_onset_extent_measurement_progression_and_symmetry", "Swelling Detail", "string", "swelling-detail", "붓기의 시작 시점, 범위·둘레 측정값, 빠르게 커지는지, 반대쪽과 차이와 눌렀을 때 변화를 알려주세요.", 111, "inflammatory-detail", C + S),
        q("joint_limb.warmth_redness_colour_tenderness_and_sequence", "Inflammatory Appearance Sequence", "string", "inflammatory-appearance", "열감·붉음 또는 다른 색 변화·압통이 있다면 통증·붓기와 비교한 시작 순서와 진행을 알려주세요.", 110, "inflammatory-detail", C + S),
        q("joint_limb.stiffness_after_rest_morning_duration_and_improvement", "Detailed Stiffness Pattern", "string", "stiffness-detail", "기상 후 또는 오래 쉰 뒤 뻣뻣함의 지속시간, 움직이면 풀리는지와 하루 중 변화를 알려주세요.", 109, "inflammatory-detail", C + D),
        q("joint_limb.active_passive_motion_task_limit_and_comparison", "Movement and Task Limitation", "string", "movement-detail", "스스로 움직일 때와 도움받아 움직일 때 제한되는 방향·각도, 통증이나 걸림과 반대쪽 비교를 알려주세요.", 108, "function-detail", C + R),
        q("joint_limb.click_catch_lock_give_way_pop_and_timing", "Mechanical Symptom Detail", "string", "mechanical-detail", "딸깍거림·마찰감·걸림·잠김·휘청임·뚝 소리가 있다면 어느 동작에서 언제 생기고 통증·붓기와 어떤 순서인지 알려주세요.", 107, "site-course", C + D),
        q("joint_limb.trauma_exact_time_place_activity_mechanism_force_direction_and_position", "Structured Injury Mechanism", "string", "trauma-detail", "다쳤다면 정확한 날짜·시각·장소·활동, 넘어짐 높이·충돌·비틀림·압궤 등 힘의 크기·방향과 당시 자세를 알려주세요.", 106, "trauma-detail", C + S),
        q("joint_limb.trauma_immediate_pain_pop_swelling_bruising_and_function", "Immediate Post-injury Features", "string", "postinjury-detail", "다친 직후 통증·소리·붓기·멍이 생긴 시점과 바로 걷거나 팔다리를 사용할 수 있었는지 알려주세요.", 105, "trauma-detail", C + S),
        q("joint_limb.weight_bearing_steps_grip_lift_and_current_change", "Weight-bearing and Limb Use", "string", "weight-bearing", "직후와 현재 각각 몇 걸음 가능한지, 서기·계단 또는 잡기·들기·밀기 같은 동작이 어느 정도 가능한지 알려주세요.", 104, "function-detail", C + S),
        q("joint_limb.wound_contamination_bite_foreign_body_bleeding_and_tetanus_record", "Wound and Contamination Context", "string", "wound-detail", "상처가 있다면 깊이·출혈·흙/물 오염·물림·이물질, 세척·처치와 파상풍 접종 기록을 알려주세요.", 103, "trauma-detail", C + S),
        q("joint_limb.numbness_tingling_weakness_exact_boundary_and_progression", "Neurological Symptom Distribution", "string", "neuro-detail", "저림·감각저하·힘 빠짐이 있다면 손가락·발가락까지 정확한 경계, 시작 순서와 퍼지거나 악화하는지 알려주세요.", 102, "neurovascular-detail", C + S),
        q("joint_limb.distal_colour_temperature_capillary_change_and_patient_observation", "Distal Circulation Observation", "string", "circulation-detail", "손가락·발가락의 색·온도·붓기와 눌렀다 뗀 뒤 색이 돌아오는 모습이 반대쪽과 다른지, 누가 어떻게 확인했는지 알려주세요.", 101, "neurovascular-detail", C + S),
        q("joint_limb.acute_unilateral_calf_or_thigh_swelling_pain_and_colour", "Acute Unilateral Leg Warning Features", "boolean", "acute-unilateral-leg", "한쪽 종아리나 허벅지에 새로 통증·붓기·색 변화가 생겼나요?", 129, "neurovascular-detail", S, safety_relevant=True),
        q("joint_limb.leg_and_chest_breathlessness_haemoptysis_syncope_sequence", "Leg and Cardiopulmonary Symptom Sequence", "string", "leg-cardiopulmonary-sequence", "한쪽 다리 변화와 흉통·숨참·객혈·실신이 있다면 각각의 시작 시각과 순서를 알려주세요.", 100, "neurovascular-detail", C + S),
        q("joint_limb.infection_skin_wound_dental_urinary_procedure_and_injection_timeline", "Infection and Procedure Timeline", "string", "infection-timeline", "최근 피부상처·감염, 치과·비뇨기 감염, 관절 주사·수술·시술이 있었다면 날짜와 관절 증상까지의 간격을 알려주세요.", 99, "inflammatory-detail", D + R),
        q("joint_limb.prosthesis_implant_hardware_site_date_and_recent_problem", "Joint Prosthesis or Hardware Context", "string", "implant-context", "인공관절·금속판·나사 등 삽입물이 있다면 부위·수술일과 최근 상처·통증·기능 변화가 있었는지 알려주세요.", 98, "history-detail", R),
        q("joint_limb.temperature_chills_malaise_sweats_rash_weight_and_sequence", "Systemic Symptom Timeline", "string", "systemic-timeline", "체온값·오한·몸살감·식은땀·발진·피로·체중 변화가 있다면 관절 증상 전후의 시작 순서를 알려주세요.", 97, "inflammatory-detail", C + S),
        q("joint_limb.multijoint_exact_count_small_large_symmetry_and_migration", "Multi-joint Distribution", "string", "multijoint-detail", "여러 관절이라면 정확한 개수, 손·발 작은 관절과 큰 관절, 좌우 대칭 여부와 한 관절에서 다른 곳으로 옮겨가는지 알려주세요.", 96, "inflammatory-detail", C + D),
        q("joint_limb.eye_skin_nail_mouth_bowel_urinary_and_genital_context", "Associated Extra-articular Context", "string", "associated-context", "눈 충혈·통증, 건선 같은 피부·손발톱 변화, 입안 궤양, 설사·혈변, 배뇨통·분비물이 있다면 시작 순서를 알려주세요.", 95, "inflammatory-detail", D + R),
        q("joint_limb.previous_episode_diagnosis_injury_surgery_injection_and_rehabilitation", "Previous Joint or Limb History", "string", "previous-history", "같은 부위의 이전 증상·외상·진단, 수술·주사·재활치료의 날짜와 당시 회복 정도를 알려주세요.", 94, "history-detail", R),
        q("joint_limb.inflammatory_gout_psoriasis_detail_and_current_status", "Inflammatory Disease History Detail", "string", "inflammatory-history-detail", "류마티스질환·통풍·건선 진단명이 있다면 진단 시기, 침범 관절, 최근 악화와 현재 치료 상태를 알려주세요.", 93, "history-detail", R),
        q("joint_limb.diabetes_bleeding_vascular_neurologic_cancer_and_bone_health_history", "Relevant Medical Risk History", "string", "medical-risk-history", "당뇨·출혈질환·혈관·신경질환, 암·골다공증·골절 병력이 있다면 진단명·시기와 현재 상태를 알려주세요.", 92, "history-detail", R),
        q("joint_limb.medicine_product_dose_route_schedule_indication_change_and_last_use", "Structured Medicine Timeline", "string", "medicine-timeline", "처방약·일반약·주사·한약·보충제마다 제품/성분명, 용량·경로·목적, 복용 일정·최근 변경일과 마지막 사용을 알려주세요.", 91, "treatment-detail", R),
        q("joint_limb.anticoagulant_steroid_immunosuppressant_and_antibiotic_timeline", "High-risk Medicine Timeline", "string", "high-risk-medicine", "항응고제·스테로이드·면역억제제·항생제를 사용한다면 이름·용량·시작/변경일, 마지막 사용과 증상 시작의 관계를 알려주세요.", 90, "treatment-detail", R),
        q("joint_limb.analgesic_rest_ice_support_exercise_therapy_response_and_adverse_effect", "Treatment Attempt and Response", "string", "treatment-detail", "진통제·휴식·냉/온찜질·보호대·운동·물리치료마다 시행 시점·횟수, 효과 지속시간과 부작용을 알려주세요.", 89, "treatment-detail", C + R),
        q("joint_limb.occupation_repetition_load_posture_vibration_ergonomics_and_ppe", "Occupational Exposure Detail", "string", "occupation-detail", "직업에서 반복 동작·중량물·자세·진동·장시간 서기/앉기와 작업대·도구·보호구, 쉬는 날과 증상 차이를 알려주세요.", 88, "exposure-detail", D + R),
        q("joint_limb.sport_hobby_training_change_surface_footwear_and_equipment", "Sport and Activity Exposure", "string", "sport-detail", "운동·취미 종류, 최근 거리·강도·기술 변화, 바닥·신발·장비와 증상 시작의 시간관계를 알려주세요.", 87, "exposure-detail", D + R),
        q("joint_limb.family_inflammatory_gout_psoriasis_clot_bone_and_joint_history", "Relevant Family History", "string", "family-history", "가족의 염증성 관절질환·통풍·건선·혈전·유전성 뼈/관절질환이 있다면 관계·진단명·진단 나이를 알려주세요.", 86, "history-detail", R),
        q("joint_limb.pregnancy_gestation_postpartum_lactation_hormone_and_mobility_context", "Pregnancy and Postpartum Context", "string", "pregnancy-context", "해당되는 경우 임신 주수·출산 후 기간·수유, 피임/호르몬 사용, 활동 감소와 관절·다리 증상의 시간관계를 알려주세요.", 85, "life-stage", R),
        q("joint_limb.child_age_growth_limp_activity_fever_rash_and_proxy_observation", "Child and Proxy Joint Context", "string", "child-context", "소아라면 나이·성장, 절뚝거림·보행 거부·놀이 변화, 열·발진과 보호자가 직접 본 내용 및 아이가 표현한 증상을 구분해 알려주세요.", 84, "life-stage", C + S),
        q("joint_limb.older_frailty_falls_baseline_mobility_aid_cognition_and_support", "Older Adult Mobility Context", "string", "older-context", "고령자라면 허약·낙상, 평소 보행·이동보조기, 인지 변화와 현재 이동·돌봄 지원이 어떻게 달라졌는지 알려주세요.", 83, "life-stage", R),
        q("falls.falls_and_near_falls_last_twelve_months", "Falls in Last Twelve Months", "string", "fall-history", "지난 12개월 실제 낙상과 넘어질 뻔한 일이 각각 몇 번이었고 가장 최근은 언제였나요?", 82, "function-detail", R, reuse_existing=True),
        q("falls.baseline_mobility_and_recent_functional_change", "Baseline Mobility", "string", "baseline-mobility", "증상 전 평소 보행·균형·독립 수준과 현재 달라진 점을 알려주세요.", 81, "function-detail", R, reuse_existing=True),
        q("joint_limb.prior_exam_clinical_test_laboratory_and_imaging_date_result_source_pending", "Prior Examination and Test Provenance", "string", "prior-tests", "이전 진찰, 기능검사·혈액검사, X선·초음파·CT·MRI 결과가 있다면 검사명·부위·날짜, 설명받은 결과, 자료 출처와 미확인 결과를 알려주세요.", 80, "history-detail", R),
        q("joint_limb.walking_stairs_transfer_selfcare_work_sleep_driving_and_sport_impact", "Detailed Functional Impact", "string", "function-impact-detail", "걷기·계단·일어나기·씻기·옷입기·업무/등교·수면·운전·운동에 미치는 영향과 도움 필요 정도를 알려주세요.", 79, "function-detail", C + R),
        q("joint_limb.communication_language_hearing_vision_cognition_literacy_and_accessibility", "Communication and Accessibility Needs", "string", "accessibility", "선호 언어, 통역·청각·시각·인지·문해·디지털 사용과 측정·사진·응답에 필요한 도움을 알려주세요.", 78, "handoff", R),
        q("joint_limb.information_source_record_image_witness_reliability_conflict_and_proxy", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자 중 누가 답하는지, 사진·영상·측정·약 목록·검사자료 유무와 기억이 불확실하거나 자료가 서로 다른 부분을 알려주세요.", 77, "handoff", R),
        q("joint_limb.patient_goal_expected_help_and_additional_rfe", "Patient Goal and Additional RFE", "string", "goal", "진료에서 확인하고 싶은 내용, 원하는 도움과 질문에 없던 의견 또는 별도 문진이 필요한 다른 문제를 알려주세요.", 76, "handoff", C + R),
        q("joint_limb.unexplained_increasing_lump_or_bone_swelling", "Unexplained Increasing Lump or Bone Swelling", "boolean", "increasing-lump", "원인을 모르는 덩이·뼈 부위 붓기가 계속 커지거나 지속되나요?", 75, "history-detail", R, safety_relevant=True),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    for key, identifier in G.items():
        nodes[identifier] = {"id": identifier, "type": "ClinicalGroup", "display": key.replace("-", " ").title()}
    doc["extra_nodes"] = list(nodes.values())
    new_rules = [
        {"id": "rule.joint-limb.safety.unilateral-leg-chest-pain", "priority": 1000, "when": {"all": [{"fact": "joint_limb.acute_unilateral_calf_or_thigh_swelling_pain_and_colour", "equals": True}, {"fact": "symptom.chest_pain", "equals": True}]}, "then": {"safety_level": "emergency", "action": "human_handoff", "suppress_routine": True}},
        {"id": "rule.joint-limb.safety.unilateral-leg-severe-dyspnea", "priority": 1000, "when": {"all": [{"fact": "joint_limb.acute_unilateral_calf_or_thigh_swelling_pain_and_colour", "equals": True}, {"fact": "symptom.severe_dyspnea", "equals": True}]}, "then": {"safety_level": "emergency", "action": "human_handoff", "suppress_routine": True}},
    ]
    rules = {item["id"]: item for item in doc["safety_rules"]}
    rules.update({item["id"]: item for item in new_rules})
    doc["safety_rules"] = list(rules.values())
    doc["default_refresh"].update({"last_assessed_at": "2026-07-21", "next_monitor_at": "2026-07-22", "next_full_review_at": "2027-01-17"})
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc: dict) -> dict:
    result = completion_policy(prefix=P, fragment=doc, presentation_fact="symptom.joint_limb.current", question_budget=96, source_refs=SOURCES)
    result["required_facts"]["routine"] = [
        "joint_limb.primary_context", "symptom.duration", "symptom.joint_limb.main_type",
        "symptom.joint_limb.location", "symptom.joint_limb.side", "symptom.joint_limb.onset",
        "symptom.joint_limb.pain_severity", "symptom.joint_limb.range_of_motion",
        "symptom.joint_limb.functional_impact",
        "joint_limb.patient_words_first_change_and_main_concern",
        "joint_limb.exact_structure_site_side_surface_depth_and_distribution",
        "joint_limb.first_latest_date_time_activity_speed_course_and_baseline",
        "joint_limb.episode_frequency_duration_flare_recovery_and_between_state",
        "joint_limb.walking_stairs_transfer_selfcare_work_sleep_driving_and_sport_impact",
        "joint_limb.information_source_record_image_witness_reliability_conflict_and_proxy",
        "joint_limb.patient_goal_expected_help_and_additional_rfe",
    ]
    result["conditional_required_facts"] = [{"selector_fact": "joint_limb.primary_context", "cases": {
        "acute_injury": ["event.joint_limb.recent_injury", "joint_limb.trauma_exact_time_place_activity_mechanism_force_direction_and_position", "joint_limb.trauma_immediate_pain_pop_swelling_bruising_and_function", "joint_limb.weight_bearing_steps_grip_lift_and_current_change", "joint_limb.wound_contamination_bite_foreign_body_bleeding_and_tetanus_record", "joint_limb.numbness_tingling_weakness_exact_boundary_and_progression", "joint_limb.distal_colour_temperature_capillary_change_and_patient_observation"],
        "hot_swollen_single_joint": ["symptom.hot_swollen_joint", "symptom.sudden_severe_single_joint", "joint_limb.swelling_onset_extent_measurement_progression_and_symmetry", "joint_limb.warmth_redness_colour_tenderness_and_sequence", "joint_limb.temperature_chills_malaise_sweats_rash_weight_and_sequence", "joint_limb.infection_skin_wound_dental_urinary_procedure_and_injection_timeline", "joint_limb.prosthesis_implant_hardware_site_date_and_recent_problem"],
        "mechanical_or_overuse": ["symptom.joint_limb.activity_relation", "symptom.joint_limb.locking_or_giving_way", "joint_limb.pain_exact_site_radiation_character_timing_and_pattern", "joint_limb.active_passive_motion_task_limit_and_comparison", "joint_limb.click_catch_lock_give_way_pop_and_timing", "joint_limb.occupation_repetition_load_posture_vibration_ergonomics_and_ppe", "joint_limb.sport_hobby_training_change_surface_footwear_and_equipment", "joint_limb.analgesic_rest_ice_support_exercise_therapy_response_and_adverse_effect"],
        "multiple_or_inflammatory_joints": ["symptom.joint_limb.number_of_joints", "symptom.joint_limb.morning_stiffness", "joint_limb.multijoint_exact_count_small_large_symmetry_and_migration", "joint_limb.stiffness_after_rest_morning_duration_and_improvement", "joint_limb.eye_skin_nail_mouth_bowel_urinary_and_genital_context", "joint_limb.inflammatory_gout_psoriasis_detail_and_current_status", "joint_limb.family_inflammatory_gout_psoriasis_clot_bone_and_joint_history"],
        "calf_or_circulatory": ["joint_limb.acute_unilateral_calf_or_thigh_swelling_pain_and_colour", "joint_limb.swelling_onset_extent_measurement_progression_and_symmetry", "joint_limb.leg_and_chest_breathlessness_haemoptysis_syncope_sequence", "joint_limb.distal_colour_temperature_capillary_change_and_patient_observation", "joint_limb.pregnancy_gestation_postpartum_lactation_hormone_and_mobility_context", "joint_limb.anticoagulant_steroid_immunosuppressant_and_antibiotic_timeline"],
        "child_or_proxy": ["joint_limb.child_age_growth_limp_activity_fever_rash_and_proxy_observation", "joint_limb.information_source_record_image_witness_reliability_conflict_and_proxy", "joint_limb.communication_language_hearing_vision_cognition_literacy_and_accessibility", "falls.baseline_mobility_and_recent_functional_change"],
        "pregnancy_or_postpartum": ["joint_limb.pregnancy_gestation_postpartum_lactation_hormone_and_mobility_context", "joint_limb.acute_unilateral_calf_or_thigh_swelling_pain_and_colour", "joint_limb.medicine_product_dose_route_schedule_indication_change_and_last_use", "joint_limb.walking_stairs_transfer_selfcare_work_sleep_driving_and_sport_impact"],
        "followup_or_result_review": ["joint_limb.previous_episode_diagnosis_injury_surgery_injection_and_rehabilitation", "joint_limb.prior_exam_clinical_test_laboratory_and_imaging_date_result_source_pending", "joint_limb.medicine_product_dose_route_schedule_indication_change_and_last_use", "joint_limb.analgesic_rest_ice_support_exercise_therapy_response_and_adverse_effect", "falls.baseline_mobility_and_recent_functional_change"],
        "other_or_unclear": ["joint_limb.pain_exact_site_radiation_character_timing_and_pattern", "joint_limb.previous_episode_diagnosis_injury_surgery_injection_and_rehabilitation", "joint_limb.diabetes_bleeding_vascular_neurologic_cancer_and_bone_health_history", "joint_limb.unexplained_increasing_lump_or_bone_swelling", "joint_limb.older_frailty_falls_baseline_mobility_aid_cognition_and_support", "falls.falls_and_near_falls_last_twelve_months", "falls.baseline_mobility_and_recent_functional_change", "joint_limb.communication_language_hearing_vision_cognition_literacy_and_accessibility"],
    }}]
    result["provenance"] = provenance(SOURCES)
    return result


def sources() -> dict:
    doc = load(RESEARCH)
    additions = [
        {"id": "source.nice.ng100.rheumatoid-arthritis.2020", "kind": "clinical_guideline_metadata", "publisher": "NICE", "title": "Rheumatoid arthritis in adults: management", "version": "NG100-updated-2020-accessed-2026-07-21", "url": "https://www.nice.org.uk/guidance/ng100/chapter/recommendations", "language": "en", "digest": "metadata_only_not_cached", "license_status": "restricted", "complete": False, "monitor_profile": "nice_guidance", "monitor_interval_days": 7, "last_monitored_at": "2026-07-21", "next_monitor_at": "2026-07-28", "assertions": ["History preserves duration, exact joint count, small-joint involvement, symmetry, morning stiffness and functional baseline; Runtime does not infer rheumatoid arthritis or calculate disease activity."]},
        {"id": "source.nice.ng158.venous-thromboembolism.2023", "kind": "clinical_guideline_metadata", "publisher": "NICE", "title": "Venous thromboembolic diseases: diagnosis, management and thrombophilia testing", "version": "NG158-updated-2023-accessed-2026-07-21", "url": "https://www.nice.org.uk/guidance/ng158/chapter/recommendations", "language": "en", "digest": "metadata_only_not_cached", "license_status": "restricted", "complete": False, "monitor_profile": "nice_guidance", "monitor_interval_days": 7, "last_monitored_at": "2026-07-21", "next_monitor_at": "2026-07-28", "assertions": ["Acute unilateral leg pain or swelling is recorded with chest pain, breathlessness, haemoptysis, syncope and recent immobility, surgery, trauma, pregnancy, puerperium or hormone exposure.", "Runtime does not calculate Wells or diagnose DVT or pulmonary embolism; combined leg and cardiopulmonary warning features trigger emergency handoff."]},
        {"id": "source.nice.ng12.skeletal-soft-tissue.2026", "kind": "clinical_guideline_metadata", "publisher": "NICE", "title": "Suspected cancer: skeletal and soft-tissue symptoms", "version": "NG12-updated-2026-accessed-2026-07-21", "url": "https://www.nice.org.uk/guidance/ng12/chapter/recommendations-organised-by-site-of-cancer", "language": "en", "digest": "metadata_only_not_cached", "license_status": "restricted", "complete": False, "monitor_profile": "nice_guidance", "monitor_interval_days": 7, "last_monitored_at": "2026-07-21", "next_monitor_at": "2026-07-28", "assertions": ["Persistent unexplained bone pain or swelling in children and an unexplained increasing soft-tissue lump are preserved for clinician review; Runtime does not infer malignancy or choose testing."]},
    ]
    for artifact in doc["artifacts"]:
        if artifact["id"] != "source.stom.joint-limb.20260714":
            artifact["last_monitored_at"] = "2026-07-21"
            artifact["monitor_result"] = "current_official_source_confirmed_no_replacement_identified"
    artifacts = {item["id"]: item for item in doc["artifacts"]}
    artifacts.update({item["id"]: item for item in additions})
    doc["artifacts"] = list(artifacts.values())
    doc["updated_at"] = CREATED
    doc["provenance"] = provenance([item["id"] for item in doc["artifacts"]])
    return doc


def clinician(doc: dict) -> dict:
    result = load(CLINICIAN)
    ids = {item["fact"]["id"] for item in doc["entries"]}
    ids.update({"pain.frequency", "pain.nrs_score"})
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.joint_limb_complaint"] = sorted(ids)
    return result


def condition_state(condition: dict) -> dict[str, dict]:
    result = {}
    if "fact" in condition:
        result[condition["fact"]] = {"value": condition.get("equals", True)}
    for child in condition.get("all", []):
        result.update(condition_state(child))
    return result


def routine_cases(doc: dict, completion: dict) -> dict[str, dict]:
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    always = completion["required_facts"]["always"]
    core = completion["required_facts"]["routine"]
    branches = completion["conditional_required_facts"][0]["cases"]
    forbidden = ["diagnosis.fracture", "diagnosis.septic_arthritis", "diagnosis.rheumatoid_arthritis", "diagnosis.deep_vein_thrombosis", "diagnosis.cancer", "recommendation.start_treatment"]

    def value(fid):
        fact = by_id[fid]
        if fact["value_type"] == "boolean": return False
        if fact["value_type"] == "integer": return 4
        if fact["value_type"] == "quantity": return {"amount": 3, "unit": "weeks"}
        if fact["value_type"] == "coded": return fact.get("allowed_values", ["unclear"])[-1]
        return "특이사항 없음"

    def state(branch):
        ids = dict.fromkeys([*always, *core, *branches[branch]])
        result = {fid: {"value": value(fid)} for fid in ids}
        result["symptom.joint_limb.current"] = {"value": True}
        result["joint_limb.primary_context"] = {"value": branch}
        result["symptom.joint_limb.main_type"] = {"value": "other"}
        result["symptom.joint_limb.pain_severity"] = {"value": "none"}
        return result

    specs = [
        ("ACUTE-SPORT-INJURY", "acute_injury", 29, "운동 중 발목을 접질린 뒤 통증과 사용 제한을 진료 전에 정리합니다.", {}),
        ("HOT-SWOLLEN-ROUTINE", "hot_swollen_single_joint", 47, "한 관절의 갑작스러운 통증·붓기와 전신 증상 순서를 정리합니다.", {}),
        ("MECHANICAL-OCCUPATION", "mechanical_or_overuse", 38, "반복 작업과 어깨 통증의 동작·기능·치료 반응을 정리합니다.", {}),
        ("MULTIJOINT-INFLAMMATORY", "multiple_or_inflammatory_joints", 55, "여러 손 관절의 분포·뻣뻣함·기능 변화를 정리합니다.", {}),
        ("CALF-CIRCULATORY-ROUTINE", "calf_or_circulatory", 61, "편측 종아리 증상과 심폐 증상·위험 노출의 순서를 정리합니다.", {}),
        ("CHILD-PROXY", "child_or_proxy", 8, "보호자가 소아의 절뚝거림과 활동·전신 변화를 관찰한 내용을 구분해 전달합니다.", {}),
        ("PREGNANCY-POSTPARTUM", "pregnancy_or_postpartum", 34, "산후 관절·다리 증상과 활동·약물·기능 변화를 정리합니다.", {}),
        ("FOLLOWUP-RESULT-SOURCE", "followup_or_result_review", 66, "이전 영상·검사 결과와 치료 반응, 자료 출처를 추적 진료에 전달합니다.", {}),
        ("OLDER-FALL-ACCESSIBILITY", "other_or_unclear", 84, "고령자의 낙상·평소 이동과 접근성·돌봄 변화를 정리합니다.", {"falls.falls_and_near_falls_last_twelve_months": {"value": "지난 1년 1회 낙상"}}),
        ("PAIN-NRS-REQUIRED", "mechanical_or_overuse", 41, "관절 통증이 있으면 통증 빈도와 원점수 NRS를 필수 기록합니다.", {"symptom.joint_limb.pain_severity": {"value": "moderate"}, "pain.frequency": {"value": "daily"}, "pain.nrs_score": {"value": 5}}),
        ("MULTI-RFE-ADDITIONAL-COMMENT", "other_or_unclear", 50, "관절 문제 외 흉부 불편은 별도 RFE로 보존합니다.", {"joint_limb.patient_goal_expected_help_and_additional_rfe": {"value": "가끔 두근거림은 별도 문진 요청"}}),
        ("REMOTE-UNCLEAR-IMAGE", "other_or_unclear", 58, "원격 사진으로 확인할 수 없는 구조·색 변화는 음성으로 간주하지 않습니다.", {}),
    ]
    result = {}
    for key, branch, age, statement, overrides in specs:
        hidden = state(branch); hidden.update(overrides)
        expected = {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 100, "forbidden_assertions": forbidden}
        if key == "PAIN-NRS-REQUIRED": expected["expected_known_facts"] = {"pain.nrs_score": 5}
        case = {"id": f"JOINT-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": hidden, "expected": expected, "provenance": provenance(SOURCES)}
        if key == "CHILD-PROXY": case["encounter_context"] = {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "face_to_face", "available_information": ["caregiver_report"], "time_constraint": "routine", "clinical_responsibility": "decision_support"}
        if key == "REMOTE-UNCLEAR-IMAGE": case["encounter_context"] = {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "patient", "interview_mode": "video", "available_information": ["image_unreadable"], "time_constraint": "self_paced", "clinical_responsibility": "decision_support"}
        result[f"JOINT-{key}.json"] = case

    missing = "joint_limb.prior_exam_clinical_test_laboratory_and_imaging_date_result_source_pending"
    absent = state("followup_or_result_review"); absent.pop(missing)
    result["JOINT-RESULT-DATA-ABSENT.json"] = {"id": "JOINT-RESULT-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 63}, "initial_statement": {"ko": "검사를 했지만 결과 원문과 날짜를 잘 모르겠습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {missing: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 100, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}

    unclear = state("other_or_unclear")
    declined = "joint_limb.information_source_record_image_witness_reliability_conflict_and_proxy"
    unclear.pop(declined)
    result["JOINT-DATA-ABSENT.json"] = {"id": "JOINT-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 52}, "initial_statement": {"ko": "무릎이 서서히 아픈데 일부 정보는 답하고 싶지 않습니다."}, "hidden_state": unclear, "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-declined"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 100, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}

    rules = {item["id"]: item for item in doc["safety_rules"]}
    for key, rule_id in {"CALF-CHEST-PAIN": "rule.joint-limb.safety.unilateral-leg-chest-pain", "CALF-SEVERE-DYSPNEA": "rule.joint-limb.safety.unilateral-leg-severe-dyspnea"}.items():
        rule = rules[rule_id]
        result[f"JOINT-{key}.json"] = {"id": f"JOINT-{key}", "simulation_language": "ko", "persona": {"age": 57}, "initial_statement": {"ko": "한쪽 다리가 붓고 아픈데 심폐 경고 증상도 있습니다."}, "hidden_state": condition_state(rule["when"]), "expected": {"expected_safety_level": "emergency", "expected_safety_action": "human_handoff", "expected_stop_reason": "emergency_escalation", "expected_triggered_rules_contains": [rule_id], "expected_max_turns": 45, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    return result


def main() -> None:
    seed_joint_limb_complaint.main()
    doc = fragment(); completion = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, completion)
    write_json(RESEARCH, sources())
    write_json(CLINICIAN, clinician(doc))
    for path in (ROOT / "simulation/patients/musculoskeletal/joint-limb").glob("JOINT-*.json"):
        case = json.loads(path.read_text(encoding="utf-8"))
        if case.get("expected", {}).get("expected_max_turns") == 25:
            case["expected"]["expected_max_turns"] = 35
            write_json(str(path.relative_to(ROOT)), case)
    for name, case in routine_cases(doc, completion).items():
        write_json(f"simulation/patients/musculoskeletal/joint-limb/{name}", case)


if __name__ == "__main__":
    main()
