#!/usr/bin/env python3
"""Strengthen research-only chest-pain knowledge for clinician handoff."""
from __future__ import annotations

from copy import deepcopy

from profile_support import *


P = "chest-pain"
ROOT_FRAGMENT = "knowledge/generated/cardiovascular/chest-pain/chest-pain.json"
SOURCE_MANIFEST = "sources/manifests/primary-care-chest-pain-research.json"
COMPLETION = "policies/primary-care-chest-pain-completion.json"
SIMULATION_ROOT = ROOT / "simulation/patients/cardiovascular/chest-pain"
CLINICIAN_CONTEXT = "knowledge/shared/clinician-submission-context.json"
SOURCES = [
    "source.nice.cg95.chest-pain.2016",
    "source.nice.ng158.pe.2023",
    "source.nhs.chest-pain.2026",
    "source.nhs-england.aortic-dissection-sop.2024",
    "source.nhsggc.child-chest-pain.2024",
    "source.stom.mrcm.chest-pain.20260714",
]

GROUPS = {
    key: f"group.chest-pain.{key}"
    for key in (
        "routing", "course", "distribution", "coronary-detail",
        "respiratory", "aortic-detail", "thromboembolic-detail",
        "gastro-musculoskeletal", "medicine", "reproductive-child",
        "previous-care", "handoff",
    )
}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
D = ["intent.differentiate_common_causes"]
R = ["intent.risk_assessment"]


def q(fid, display, value_type, key, wording, score, group, intents, **kwargs):
    fact_overrides = kwargs.pop("fact_overrides", None)
    result = entry(
        P, fid, display, value_type, key, wording, score, key,
        [GROUPS[group]], intents=intents, **kwargs,
    )
    if fact_overrides:
        result["fact"].update(fact_overrides)
    return result


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def strengthen_fragment():
    fragment = load_json(ROOT_FRAGMENT)
    branches = [
        "acute_or_recent", "exertional_recurrent", "pleuritic_respiratory",
        "positional_or_reproducible", "meal_or_swallow",
        "palpitations_or_collapse", "pregnancy_or_vte", "child_or_proxy",
        "other_unclear",
    ]
    additions = [
        q("chest_pain.primary_group", "Primary Chest Pain Context", "coded", "primary-group", "가장 가까운 상황은 지금/최근 급성 통증, 활동 때 반복, 숨·기침 관련, 자세·누름 관련, 식사·삼킴 관련, 두근거림·실신 관련, 임신·혈전 위험, 소아·보호자 관찰, 또는 불분명 중 무엇인가요?", 295, "routing", C + D, allowed_values=branches),
        q("chest_pain.exact_onset_date_time_activity_and_sequence", "Exact Onset and Sequence", "string", "exact-onset", "처음 통증이 시작한 날짜·시각, 당시 활동·자세·식사와 통증 및 동반 증상이 생긴 순서를 알려주세요.", 214, "course", C),
        q("chest_pain.last_episode_start_duration_and_time_since", "Last Episode Timing", "string", "last-episode", "가장 최근 통증은 언제 시작해 몇 분 지속됐고, 끝난 뒤 지금까지 얼마나 지났나요?", 213, "course", C + R),
        q("chest_pain.episode_count_frequency_recovery_and_trend", "Episode Frequency and Trend", "string", "episode-pattern", "총 횟수·하루/주당 빈도, 발작 사이 완전 회복 여부와 최근 더 잦아지거나 길어지거나 심해지는지 알려주세요.", 212, "course", C),
        q("chest_pain.patient_words_and_change_from_baseline", "Patient Description and Baseline Change", "string", "patient-words", "본인의 말로 어떤 불편감인지, 과거의 가슴 통증이나 평소 운동능력과 비교해 무엇이 달라졌는지 알려주세요.", 211, "handoff", C),
        q("chest_pain.exact_site_side_area_depth_and_tender_point", "Exact Site and Area", "string", "site-detail", "가슴의 왼쪽·오른쪽·가운데 중 어디인지, 한 점인지 넓은 부위인지, 피부·갈비뼈·가슴 깊은 곳 중 어디로 느끼는지 알려주세요.", 210, "distribution", C, terminology_binding={"system": "http://snomed.info/sct", "focus_code": "29857009", "attribute_code": "363698007"}, mrcm_ref="mapping.snomed-mrcm.chest-pain"),
        q("chest_pain.radiation_route_side_and_timing", "Radiation Detail", "string", "radiation-detail", "통증이 퍼진다면 어느 쪽 팔·어깨·목·턱·등·윗배로 어떤 순서와 시간 관계로 퍼지는지 알려주세요.", 209, "distribution", C),
        q("chest_pain.exertional_threshold_cold_emotion_and_change", "Exertional Threshold and Change", "string", "exertional-threshold", "걷기 거리·계단 수·운동 강도, 추위·감정 스트레스 중 언제 생기며 이전보다 더 적은 활동에도 생기는지 알려주세요.", 208, "coronary-detail", C + R),
        q("chest_pain.rest_nocturnal_or_minimal_exertion_escalation", "Rest or Minimal-exertion Escalation", "boolean", "rest-escalation", "최근 72시간 안에 쉬는 중·잠자는 중 또는 아주 적은 활동에도 새로 통증이 생기거나 더 자주·길게 반복되나요?", 319, "coronary-detail", S, safety_relevant=True),
        q("chest_pain.relief_time_rest_gtn_antacid_posture_and_recurrence", "Relief Detail", "string", "relief-detail", "중단·휴식·니트로글리세린·제산제·자세 변경 뒤 몇 분 만에 얼마나 좋아졌고 다시 생겼는지 알려주세요.", 207, "coronary-detail", C + R),
        q("chest_pain.activity_sleep_selfcare_work_and_driving_impact", "Functional and Safety Impact", "string", "function", "걷기·계단·수면·식사·씻기·일/학업·운전 중 중단하거나 도움받게 된 활동을 알려주세요.", 206, "handoff", C + R),
        q("chest_pain.associated_symptom_timing_and_recovery", "Associated Symptom Timing", "string", "associated-timing", "숨참·식은땀·메스꺼움·어지럼·두근거림·실신이 통증 전·중·후 언제 생겼고 얼마나 지속·회복됐는지 알려주세요.", 205, "coronary-detail", C),
        q("chest_pain.current_severe_breathlessness_cyanosis_or_consciousness_change", "Current Respiratory or Consciousness Warning", "boolean", "current-instability", "현재 말을 잇기 어려운 숨참, 창백하거나 파래짐, 깨우기 어려움 또는 새 심한 혼란이 있나요?", 340, "routing", S, safety_relevant=True),
        q("chest_pain.new_limb_cold_pale_weak_or_pulse_difference", "Possible Perfusion Deficit", "boolean", "perfusion-deficit", "통증과 함께 한쪽 팔·다리가 갑자기 차갑거나 창백해지거나 힘이 빠졌거나 맥박이 다르게 느껴지나요?", 334, "aortic-detail", S, safety_relevant=True),
        q("chest_pain.abrupt_severe_tearing_migrating_with_aortic_context", "Aortic High-risk Pattern", "boolean", "aortic-warning", "통증이 처음부터 매우 심하고 찢어지듯 등·배로 이동했으며, 대동맥질환·유전성 결합조직질환·가족력·최근 심장/대동맥 시술 중 하나가 있나요?", 333, "aortic-detail", S, safety_relevant=True),
        q("chest_pain.recent_chest_trauma_or_procedure_with_breathlessness", "Trauma or Procedure Respiratory Warning", "boolean", "trauma-procedure-warning", "최근 가슴 외상이나 중심정맥관·폐/흉부 시술 뒤 갑작스러운 흉통과 숨참이 생겼나요?", 332, "respiratory", S, safety_relevant=True),
        q("chest_pain.pregnancy_postpartum_vte_warning", "Pregnancy or Postpartum Warning", "boolean", "pregnancy-warning", "임신 중이거나 출산·유산·임신종결 후 6주 이내이며 흉통과 함께 갑작스러운 숨참·실신·피 섞인 기침·한쪽 다리 통증/부종 중 하나가 있나요?", 331, "reproductive-child", S, safety_relevant=True),
        q("chest_pain.child_exertional_syncope_or_family_sudden_death", "Child Cardiac Warning", "boolean", "child-warning", "소아·청소년이라면 운동 중 흉통과 실신이 함께 있었거나 가까운 가족의 젊은 나이 돌연사가 있나요?", 318, "reproductive-child", S, safety_relevant=True),
        q("chest_pain.respiratory_cough_sputum_fever_breathlessness_and_oxygen_context", "Respiratory Detail", "string", "respiratory-detail", "기침·가래 색/양·발열·숨참의 시작과 통증 관계, 측정한 산소포화도가 있다면 값·시각·기기를 알려주세요.", 180, "respiratory", D + R),
        q("chest_pain.vte_surgery_immobility_travel_cancer_prior_vte_hormone_context", "Detailed VTE Context", "string", "vte-detail", "최근 수술·외상·입원·3일 이상 거동 제한·장거리 이동, 암, 과거 혈전, 피임약/호르몬 사용의 시점을 알려주세요.", 179, "thromboembolic-detail", R),
        q("chest_pain.leg_side_site_swelling_pain_redness_and_onset", "Leg Symptom Detail", "string", "leg-detail", "다리 증상이 있다면 어느 쪽 어느 부위가 언제부터 붓고 아프거나 붉어졌는지 알려주세요.", 178, "thromboembolic-detail", C + R),
        q("chest_pain.pregnancy_lmp_gestation_postpartum_date_and_complications", "Pregnancy and Postpartum Context", "string", "pregnancy-context", "해당되는 경우 임신 가능성, 마지막 월경일·임신 주수, 출산/유산/임신종결 날짜와 고혈압·출혈·혈전 합병증을 알려주세요.", 177, "reproductive-child", R),
        q("chest_pain.meal_reflux_swallowing_bloating_and_vomit_relation", "Meal and Swallowing Context", "string", "meal-detail", "식사 전후·눕기·삼키기와의 관계, 속쓰림·신물·더부룩함·구토가 함께 있는지 알려주세요.", 176, "gastro-musculoskeletal", D),
        q("chest_pain.movement_breath_touch_injury_exercise_and_work_relation", "Movement and Chest Wall Context", "string", "movement-detail", "상체·팔 움직임, 깊은 숨, 눌렀을 때, 최근 운동·기침·외상·반복 작업과 같은 통증이 재현되는지 알려주세요.", 175, "gastro-musculoskeletal", D + R),
        q("chest_pain.skin_tenderness_rash_blister_and_side", "Skin and Rash Context", "string", "skin-detail", "아픈 부위 피부가 예민하거나 붉고, 한쪽 띠 모양 발진·물집이 생겼는지 알려주세요.", 174, "gastro-musculoskeletal", D),
        q("chest_pain.stress_panic_hyperventilation_and_symptom_sequence", "Stress and Hyperventilation Context", "string", "stress-detail", "스트레스·공포·과호흡과 통증·두근거림·손발 저림이 어떤 순서로 생겼는지 알려주세요. 이를 원인으로 단정하지 않습니다.", 173, "gastro-musculoskeletal", D),
        q("chest_pain.cardiovascular_history_procedure_device_and_baseline_function", "Detailed Cardiovascular History", "string", "cardiac-history", "협심증·심근경색·심부전·부정맥·판막/대동맥질환, 스텐트·우회술·심박동기와 평소 활동능력을 알려주세요.", 170, "previous-care", R),
        q("chest_pain.lipid_kidney_weight_vascular_and_family_sudden_death_context", "Cardiovascular Risk Detail", "string", "risk-detail", "고지혈증·신장질환·체중/비만·말초혈관질환과 가족의 조기 심혈관질환·대동맥질환·돌연사 나이를 알려주세요.", 169, "previous-care", R),
        q("chest_pain.current_medicines_dose_schedule_adherence_and_recent_change", "Current Medicines and Adherence", "string", "medicines", "처방약·일반약·한약·영양제의 이름·용량·횟수, 최근 시작/중단/변경과 실제 복용 여부를 알려주세요.", 168, "medicine", R),
        q("chest_pain.antiplatelet_anticoagulant_nitrate_and_allergy_context", "High-risk Medicines and Allergies", "string", "medicine-risk", "아스피린 등 항혈소판제·항응고제·니트로글리세린 사용과 약물/조영제 알레르기를 알려주세요.", 167, "medicine", R),
        q("chest_pain.cocaine_stimulant_vaping_alcohol_and_tobacco_exposure", "Substance and Stimulant Exposure", "string", "substance", "최근 코카인·각성제·에너지제품, 전자담배/담배, 음주와 증상의 시간 관계를 알려주세요.", 166, "medicine", R),
        q("chest_pain.pulmonary_gi_musculoskeletal_infection_and_anxiety_history", "Relevant Noncardiac History", "string", "other-history", "폐질환·기흉·폐렴, 역류/궤양, 흉벽·척추 질환, 최근 감염과 불안/공황 치료력을 알려주세요.", 165, "previous-care", R),
        q("chest_pain.prior_episode_ed_admission_diagnosis_and_difference", "Prior Episode and Care", "string", "prior-care", "비슷한 통증의 날짜·당시 응급실/입원 여부·설명받은 진단과 이번 증상의 차이를 알려주세요.", 162, "previous-care", R),
        q("chest_pain.prior_ecg_troponin_xray_ct_echo_stress_test_and_source", "Prior Tests and Results", "string", "prior-tests", "이전 심전도·트로포닌/혈액검사·흉부 X선·CT·심초음파·운동/기능검사의 날짜·결과·자료 출처를 알려주세요.", 161, "previous-care", R),
        q("chest_pain.reported_bp_pulse_oxygen_temperature_and_measurement_source", "Reported Observations", "string", "observations", "측정한 혈압·맥박·산소포화도·체온이 있다면 값·시각·기기·측정자를 알려주세요. 측정하지 않았다면 그대로 표시합니다.", 160, "previous-care", R),
        q("chest_pain.prior_treatment_name_dose_time_response_recurrence_and_adverse_effect", "Prior Treatment Response", "string", "treatment-response", "휴식·처방약·제산제·진통제 등 사용한 조치의 이름·용량·시각, 호전까지 걸린 시간·재발·부작용을 알려주세요.", 159, "previous-care", R),
        q("chest_pain.child_age_growth_activity_infection_and_proxy_context", "Child and Proxy Context", "string", "child-context", "소아라면 나이·성장/발달·운동 중 증상·최근 감염과 본인/보호자 중 누가 답하는지 알려주세요.", 156, "reproductive-child", R),
        q("chest_pain.occupation_heavy_lifting_repetition_cold_fume_and_safety_impact", "Occupational and Exposure Context", "string", "occupation", "중량물·반복동작·추위·분진/연기 노출과 운전·고소·기계 작업 안전에 미친 영향을 알려주세요.", 155, "handoff", R),
        q("chest_pain.information_source_witness_record_reliability_and_conflict", "Information Source and Reliability", "string", "information-source", "본인·보호자·목격자 중 누가 답하는지, 기록·검사파일이 있는지, 기억이 불확실하거나 설명이 서로 다른 부분을 알려주세요.", 154, "handoff", R),
        q("chest_pain.communication_accessibility_and_interpreter_need", "Communication and Accessibility", "string", "accessibility", "언어·청각·시각·인지·읽기·디지털 사용에 도움이 필요하거나 통역·보호자 지원이 필요한지 알려주세요.", 153, "handoff", R),
        q("chest_pain.patient_concern_goal_expectation_and_additional_comment", "Patient Concern Goal and Additional Comment", "string", "goal", "가장 걱정되는 점, 진료에서 확인하고 싶은 점과 질문에 없던 의견을 알려주세요.", 152, "handoff", R),
    ]
    existing = {item["fact"]["id"]: item for item in fragment["entries"]}
    existing.update({item["fact"]["id"]: item for item in additions})
    fragment["entries"] = list(existing.values())

    new_rules = [
        safety_rule(P, "current-instability", {"fact": "chest_pain.current_severe_breathlessness_cyanosis_or_consciousness_change", "equals": True}, "emergency", 1100),
        safety_rule(P, "perfusion-deficit", {"fact": "chest_pain.new_limb_cold_pale_weak_or_pulse_difference", "equals": True}, "emergency", 1080),
        safety_rule(P, "aortic-high-risk-pattern", {"fact": "chest_pain.abrupt_severe_tearing_migrating_with_aortic_context", "equals": True}, "emergency", 1070),
        safety_rule(P, "trauma-procedure-breathlessness", {"fact": "chest_pain.recent_chest_trauma_or_procedure_with_breathlessness", "equals": True}, "emergency", 1060),
        safety_rule(P, "pregnancy-postpartum-warning", {"fact": "chest_pain.pregnancy_postpartum_vte_warning", "equals": True}, "emergency", 1050),
        safety_rule(P, "rest-or-minimal-exertion-escalation", {"fact": "chest_pain.rest_nocturnal_or_minimal_exertion_escalation", "equals": True}, "urgent", 870),
        safety_rule(P, "child-exertional-or-family-warning", {"fact": "chest_pain.child_exertional_syncope_or_family_sudden_death", "equals": True}, "urgent", 860),
    ]
    rules = {item["id"]: item for item in fragment["safety_rules"]}
    rules.update({item["id"]: item for item in new_rules})
    fragment["safety_rules"] = sorted(
        rules.values(), key=lambda item: (-item["priority"], item["id"])
    )
    nodes = {item["id"]: item for item in fragment["extra_nodes"]}
    for key, identifier in GROUPS.items():
        nodes[identifier] = {
            "id": identifier, "type": "ClinicalGroup",
            "display": key.replace("-", " ").title(),
        }
    fragment["extra_nodes"] = list(nodes.values())
    fragment["default_refresh"].update({
        "last_assessed_at": "2026-07-18",
        "next_monitor_at": "2026-07-19",
        "next_full_review_at": "2027-01-14",
    })
    fragment["provenance"] = provenance(SOURCES)
    return fragment


def completion_policy_for(fragment):
    policy = completion_policy(
        prefix=P, fragment=fragment,
        presentation_fact="symptom.chest_pain.current",
        question_budget=72, source_refs=SOURCES,
    )
    policy["required_facts"]["always"].extend(
        ["pain.frequency", "pain.nrs_score"]
    )
    policy["required_facts"]["routine"] = [
        "chest_pain.primary_group",
        "symptom.duration",
        "chest_pain.exact_onset_date_time_activity_and_sequence",
        "chest_pain.last_episode_start_duration_and_time_since",
        "chest_pain.episode_count_frequency_recovery_and_trend",
        "symptom.chest_pain.location",
        "chest_pain.exact_site_side_area_depth_and_tender_point",
        "symptom.chest_pain.quality",
        "symptom.chest_pain.radiation",
        "chest_pain.radiation_route_side_and_timing",
        "chest_pain.patient_words_and_change_from_baseline",
        "chest_pain.activity_sleep_selfcare_work_and_driving_impact",
        "chest_pain.cardiovascular_history_procedure_device_and_baseline_function",
        "chest_pain.current_medicines_dose_schedule_adherence_and_recent_change",
        "chest_pain.antiplatelet_anticoagulant_nitrate_and_allergy_context",
        "chest_pain.prior_episode_ed_admission_diagnosis_and_difference",
        "chest_pain.prior_ecg_troponin_xray_ct_echo_stress_test_and_source",
        "chest_pain.prior_treatment_name_dose_time_response_recurrence_and_adverse_effect",
        "chest_pain.information_source_witness_record_reliability_and_conflict",
        "chest_pain.patient_concern_goal_expectation_and_additional_comment",
    ]
    branches = {
        "acute_or_recent": ["chest_pain.associated_symptom_timing_and_recovery", "chest_pain.reported_bp_pulse_oxygen_temperature_and_measurement_source", "chest_pain.lipid_kidney_weight_vascular_and_family_sudden_death_context"],
        "exertional_recurrent": ["symptom.chest_pain.exertional", "symptom.chest_pain.relieved_by_rest", "chest_pain.exertional_threshold_cold_emotion_and_change", "chest_pain.relief_time_rest_gtn_antacid_posture_and_recurrence", "chest_pain.lipid_kidney_weight_vascular_and_family_sudden_death_context"],
        "pleuritic_respiratory": ["symptom.chest_pain.pleuritic", "symptom.dyspnea", "symptom.hemoptysis", "symptom.fever", "chest_pain.respiratory_cough_sputum_fever_breathlessness_and_oxygen_context", "chest_pain.vte_surgery_immobility_travel_cancer_prior_vte_hormone_context", "chest_pain.leg_side_site_swelling_pain_redness_and_onset"],
        "positional_or_reproducible": ["symptom.chest_pain.positional", "symptom.chest_pain.reproducible", "chest_pain.movement_breath_touch_injury_exercise_and_work_relation", "chest_pain.skin_tenderness_rash_blister_and_side", "chest_pain.occupation_heavy_lifting_repetition_cold_fume_and_safety_impact"],
        "meal_or_swallow": ["chest_pain.meal_reflux_swallowing_bloating_and_vomit_relation", "chest_pain.relief_time_rest_gtn_antacid_posture_and_recurrence", "chest_pain.pulmonary_gi_musculoskeletal_infection_and_anxiety_history"],
        "palpitations_or_collapse": ["symptom.palpitations", "symptom.syncope", "chest_pain.associated_symptom_timing_and_recovery", "chest_pain.reported_bp_pulse_oxygen_temperature_and_measurement_source", "chest_pain.stress_panic_hyperventilation_and_symptom_sequence"],
        "pregnancy_or_vte": ["chest_pain.pregnancy_lmp_gestation_postpartum_date_and_complications", "chest_pain.vte_surgery_immobility_travel_cancer_prior_vte_hormone_context", "chest_pain.leg_side_site_swelling_pain_redness_and_onset", "chest_pain.reported_bp_pulse_oxygen_temperature_and_measurement_source"],
        "child_or_proxy": ["chest_pain.child_age_growth_activity_infection_and_proxy_context", "chest_pain.communication_accessibility_and_interpreter_need", "chest_pain.information_source_witness_record_reliability_and_conflict"],
        "other_unclear": ["chest_pain.respiratory_cough_sputum_fever_breathlessness_and_oxygen_context", "chest_pain.meal_reflux_swallowing_bloating_and_vomit_relation", "chest_pain.movement_breath_touch_injury_exercise_and_work_relation", "chest_pain.skin_tenderness_rash_blister_and_side", "chest_pain.stress_panic_hyperventilation_and_symptom_sequence", "chest_pain.pulmonary_gi_musculoskeletal_infection_and_anxiety_history", "chest_pain.cocaine_stimulant_vaping_alcohol_and_tobacco_exposure", "chest_pain.communication_accessibility_and_interpreter_need"],
    }
    policy["conditional_required_facts"] = [{
        "selector_fact": "chest_pain.primary_group", "cases": branches,
    }]
    policy["must_be_known_facts"] = ["pain.frequency", "pain.nrs_score"]
    return policy


def update_sources():
    manifest = load_json(SOURCE_MANIFEST)
    artifacts = {
        item["id"]: item for item in manifest["artifacts"]
        if item["id"] != "source.nhs.pericarditis.chest-emergency.2023"
    }
    artifacts["source.nhs.chest-pain.2026"] = {
        "id": "source.nhs.chest-pain.2026",
        "kind": "public_health_guidance_metadata", "publisher": "NHS",
        "title": "Chest pain", "version": "reviewed-2023-08-08-accessed-2026-07-18",
        "url": "https://www.nhs.uk/symptoms/chest-pain/", "language": "en",
        "digest": "metadata_only_not_cached", "license_status": "unknown",
        "complete": False, "monitor_profile": "public_health_guidance",
        "last_monitored_at": "2026-07-18",
        "monitor_result": "current_official_source_confirmed",
        "assertions": [
            "Sudden persistent pressure or squeezing pain, radiation to an arm, neck, jaw, stomach or back, or chest pain with sweating, nausea, light-headedness or breathlessness requires emergency help.",
            "Intermittent or quickly resolved chest pain still warrants clinical assessment when the person remains concerned.",
            "Meal, movement, breathing, infection, rash and stress relationships are useful history features but do not establish a diagnosis.",
        ],
    }
    artifacts["source.nhsggc.child-chest-pain.2024"] = {
        "id": "source.nhsggc.child-chest-pain.2024",
        "kind": "clinical_referral_guidance_metadata", "publisher": "NHS GGC",
        "title": "Child with Chest Pain: Advice for Referrers",
        "version": "current-accessed-2026-07-18",
        "url": "https://www.clinicalguidelines.scot.nhs.uk/rhc-for-health-professionals/guidelines/primary-care-referral-guidelines/medical-paediatric-pre-referral-guidance/child-with-chest-pain-advice-for-referrers/",
        "language": "en", "digest": "metadata_only_not_cached",
        "license_status": "unknown", "complete": False,
        "monitor_profile": "clinical_guideline", "last_monitored_at": "2026-07-18",
        "monitor_result": "current_official_source_confirmed",
        "assertions": [
            "Paediatric chest pain is rarely due to serious pathology, but exertional pain, palpitations, chest pain with syncope, known cardiac disease, Kawasaki or connective-tissue history, and family sudden death or young-adult cardiac disease are referral features.",
            "The interview records age, exertional timing, associated symptoms, relevant history, family history and proxy source without diagnosing a cardiac condition or selecting a test.",
        ],
    }
    for identifier in (
        "source.nice.cg95.chest-pain.2016", "source.nice.ng158.pe.2023",
        "source.nhs-england.aortic-dissection-sop.2024",
    ):
        artifacts[identifier]["last_monitored_at"] = "2026-07-18"
        artifacts[identifier]["monitor_result"] = "current_official_source_confirmed"
    artifacts["source.stom.mrcm.chest-pain.20260714"]["monitor_result"] = "not_due_existing_metadata_preserved"
    manifest["artifacts"] = list(artifacts.values())
    manifest["provenance"] = provenance(SOURCES)
    return manifest


def safety_state(condition):
    state = {}
    children = condition.get("all", [condition])
    for child in children:
        if "fact" not in child:
            continue
        value = child.get("equals")
        if value is None:
            value = child.get("in", [True])[0]
        state[child["fact"]] = {"value": value}
    return state


def simulations(fragment, policy):
    by_id = {item["fact"]["id"]: item["fact"] for item in fragment["entries"]}
    forbidden = [
        "diagnosis.acute_coronary_syndrome", "diagnosis.myocardial_infarction",
        "diagnosis.pulmonary_embolism", "diagnosis.aortic_dissection",
        "diagnosis.pneumothorax", "diagnosis.pericarditis",
        "diagnosis.panic_attack",
    ]
    out = {}
    for index, rule in enumerate(fragment["safety_rules"]):
        key = rule["id"].split("safety.", 1)[1]
        state = safety_state(rule["when"])
        out[f"CHEST-{key.upper()}.json"] = {
            "id": f"CHEST-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 16 if "child" in key else 35 + index * 2},
            "initial_statement": {"ko": "가슴 통증 때문에 진료 전 문진을 시작합니다."},
            "hidden_state": state,
            "expected": {
                "expected_safety_level": rule["then"]["safety_level"],
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{rule['then']['safety_level']}_escalation",
                "expected_triggered_rules_contains": [rule["id"]],
                "expected_max_turns": 45, "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }

    always = policy["required_facts"]["always"]
    routine = policy["required_facts"]["routine"]
    branches = policy["conditional_required_facts"][0]["cases"]

    def value_for(fid):
        if fid == "pain.frequency": return "daily"
        if fid == "pain.nrs_score": return 3
        fact = by_id[fid]
        if fact["value_type"] == "boolean": return False
        if fact["value_type"] == "coded": return fact.get("allowed_values", ["unclear"])[-1]
        if fact["value_type"] == "integer": return 3
        if fact["value_type"] == "quantity": return "2 weeks"
        if fact["value_type"] == "severity": return "mild"
        return "특이사항 없음"

    def routine_state(branch):
        values = {
            fid: {"value": value_for(fid)}
            for fid in dict.fromkeys([*always, *routine, *branches[branch]])
        }
        values["symptom.chest_pain.current"] = {"value": False}
        values["symptom.chest_pain.within_last_72_hours"] = {"value": False}
        values["chest_pain.primary_group"] = {"value": branch}
        values["pain.nrs_score"] = {"value": 3}
        values["pain.frequency"] = {"value": "daily"}
        return values

    specs = [
        ("ACUTE-RESOLVED", "acute_or_recent", 54, "어제 잠깐 가슴이 불편했지만 지금은 괜찮습니다.", {}),
        ("EXERTIONAL-RECURRENT", "exertional_recurrent", 63, "계단을 오를 때 반복되는 가슴 불편을 정리하고 싶습니다.", {"symptom.chest_pain.exertional": {"value": True}, "symptom.chest_pain.relieved_by_rest": {"value": True}}),
        ("PLEURITIC-RESPIRATORY", "pleuritic_respiratory", 39, "숨을 깊이 들이쉴 때 가슴이 아프지만 심한 숨참은 없습니다.", {"symptom.chest_pain.pleuritic": {"value": True}, "symptom.dyspnea": {"value": "mild"}}),
        ("POSITIONAL-REMOTE", "positional_or_reproducible", 46, "원격 문진으로 움직일 때 재현되는 가슴 통증을 정리합니다.", {"symptom.chest_pain.reproducible": {"value": True}}),
        ("MEAL-SWALLOW", "meal_or_swallow", 44, "식후에 반복되는 가슴 불편이 있습니다.", {}),
        ("PALPITATION-HISTORY", "palpitations_or_collapse", 52, "두근거림과 함께했던 가슴 불편의 과거 기록을 정리합니다.", {"symptom.palpitations": {"value": True}}),
        ("PREGNANCY-MULTI-RFE", "pregnancy_or_vte", 32, "임신 중 가슴 불편 외에 다리 증상도 별도 문진하고 싶습니다.", {"chest_pain.pregnancy_lmp_gestation_postpartum_date_and_complications": {"value": "임신 22주, 기록 확인 필요"}, "chest_pain.patient_concern_goal_expectation_and_additional_comment": {"value": "다리 증상을 별도 RFE로 전달 요청"}}),
        ("CHILD-PROXY", "child_or_proxy", 12, "보호자가 아이의 간헐적 가슴 불편을 설명합니다.", {"chest_pain.child_age_growth_activity_infection_and_proxy_context": {"value": "12세, 보호자 답변, 아이 본인 확인 필요"}}),
        ("UNCLEAR-ACCESSIBILITY", "other_unclear", 77, "청각 지원이 필요한 고령자의 불분명한 가슴 불편을 정리합니다.", {"chest_pain.communication_accessibility_and_interpreter_need": {"value": "청각 지원과 보호자 확인 필요"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine_state(branch)
        state.update(overrides)
        out[f"CHEST-{key}.json"] = {
            "id": f"CHEST-{key}", "simulation_language": "ko",
            "persona": {"age": age},
            "initial_statement": {"ko": statement}, "hidden_state": state,
            "expected": {
                "expected_safety_level": "routine",
                "expected_stop_reason": "all_required_targets_resolved",
                "expected_known_facts": {"pain.nrs_score": 3},
                "expected_max_turns": 100, "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }
    absent = routine_state("other_unclear")
    missing = "chest_pain.prior_ecg_troponin_xray_ct_echo_stress_test_and_source"
    absent.pop(missing)
    out["CHEST-DATA-ABSENT-REMOTE.json"] = {
        "id": "CHEST-DATA-ABSENT-REMOTE", "simulation_language": "ko",
        "persona": {"age": 81},
        "encounter_context": {
            "care_setting": "primary_care", "encounter_type": "new_encounter",
            "interview_initiator": "caregiver", "interview_mode": "telephone",
            "available_information": ["no_previous_records"],
            "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
        },
        "initial_statement": {"ko": "보호자가 가슴 불편을 설명하지만 이전 검사자료는 없습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "not-performed"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "not-performed"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 100, "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }
    return out


def update_clinician_context(fragment):
    document = load_json(CLINICIAN_CONTEXT)
    additional = document["completion"]["clinician_rfe_minimum"][
        "additional_required_facts_by_rfe"
    ]
    additional["rfe.chest_pain"] = sorted({
        *(item["fact"]["id"] for item in fragment["entries"]),
        "pain.frequency", "pain.nrs_score",
    })
    return document


def main():
    fragment = strengthen_fragment()
    policy = completion_policy_for(fragment)
    write_json(ROOT_FRAGMENT, fragment)
    write_json(COMPLETION, policy)
    write_json(SOURCE_MANIFEST, update_sources())
    write_json(CLINICIAN_CONTEXT, update_clinician_context(fragment))
    for old in SIMULATION_ROOT.glob("*.json"):
        old.unlink()
    for name, case in simulations(fragment, policy).items():
        write_json(f"simulation/patients/cardiovascular/chest-pain/{name}", case)


if __name__ == "__main__":
    main()
