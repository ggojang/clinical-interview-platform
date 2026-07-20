#!/usr/bin/env python3
"""Strengthen research-only weight and constitutional-change clinician handoff."""
from __future__ import annotations

import json

import seed_weight_constitutional_change
from profile_support import ROOT, completion_policy, entry, write_json


P = "weight-constitutional-change"
FRAGMENT = "knowledge/generated/general/weight-constitutional-change/weight-constitutional-change.json"
POLICY = "policies/primary-care-weight-constitutional-change-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
PAIN = "knowledge/shared/hira-pain-assessment.json"
RESEARCH = "sources/manifests/primary-care-weight-constitutional-change-research.json"
CREATED = "2026-07-20T00:00:00Z"
SOURCES = [
    "source.nhs.unintentional-weight-loss.2025", "source.nhs.night-sweats.2023",
    "source.nice.ng12.constitutional.2026", "source.nice.cg32.nutrition.2017",
    "source.nice.ng127.weakness.2023", "source.nice.ng69.eating-disorders.2020",
    "source.cdc.tuberculosis-symptoms.2025",
]
G = {key: f"group.weight-constitutional.{key}" for key in (
    "routing", "measurement-detail", "course-detail", "nutrition-detail",
    "weakness-detail", "systemic-detail", "medicine-detail", "eating-behaviour",
    "life-stage", "history-detail", "function-detail", "handoff",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]


def provenance(source_refs: list[str]) -> dict:
    return {"created_by": {"type": "ai", "id": "codex-gpt5"}, "created_at": CREATED, "source_refs": source_refs, "review_status": "unreviewed", "version": "0.1.0"}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def q(fact_id, display, value_type, key, wording, score, group, intents, **kwargs):
    return entry(P, fact_id, display, value_type, key, wording, score, key, [G[group]], intents=intents, **kwargs)


def fragment() -> dict:
    doc = load(FRAGMENT)
    contexts = ["unintentional_weight_loss", "intentional_weight_loss", "weight_gain_or_fluid_change", "night_sweats_or_fever", "generalized_weakness_or_function_loss", "eating_or_intake_concern", "child_or_proxy", "pregnancy_or_postpartum", "followup_or_result_review", "multiple_or_unclear"]
    additions = [
        q("constitutional.primary_context", "Primary Constitutional Context", "coded", "primary-context", "가장 가까운 상황은 의도하지 않은 체중 감소, 의도한 체중 감소, 체중 증가·체액 변화, 야간 발한·열, 전신 쇠약·기능 저하, 식사·섭식 문제, 소아·보호자 응답, 임신·산후, 추적·결과 확인, 또는 여러 변화·불분명 중 무엇인가요?", 132, "routing", C + R, allowed_values=contexts),
        q("constitutional.patient_words_first_change_and_main_concern", "Patient Description and Main Concern", "string", "patient-words", "본인의 표현으로 처음 알아차린 변화, 현재 가장 불편한 점과 가장 걱정되는 점을 알려주세요.", 116, "course-detail", C),
        q("constitutional.first_latest_date_context_sequence_and_baseline", "Detailed Constitutional Timeline", "string", "timeline", "처음과 가장 최근 변화의 날짜·시각, 당시 상황, 증상이 생긴 순서와 평소 상태에서 달라진 점을 알려주세요.", 115, "course-detail", C + R),
        q("weight.usual_current_low_high_date_scale_clothing_and_source", "Weight Measurement Provenance", "string", "weight-provenance", "평소·현재·최근 최저/최고 체중, 각 측정 날짜·시각, 체중계·옷·식사/배변 조건과 직접 측정인지 추정인지 알려주세요.", 114, "measurement-detail", C + R),
        q("weight.height_date_method_and_reported_bmi_source", "Height and Reported BMI Provenance", "string", "height-bmi", "키의 값·측정일·방법과 이미 제공받은 BMI가 있다면 값·날짜·자료 출처를 알려주세요. 이 문진은 BMI를 새로 계산하지 않습니다.", 113, "measurement-detail", C + R),
        q("weight.weekly_monthly_rate_percent_period_and_calculation_source", "Weight Change Rate and Source", "string", "rate", "주·월별 변화량, 총 변화율과 기간을 알고 있다면 값과 누가 어떻게 계산했는지 알려주세요.", 112, "measurement-detail", C + R),
        q("weight.fluid_edema_diuresis_bowel_dialysis_and_measurement_context", "Fluid and Measurement Context", "string", "fluid-context", "부종·탈수, 소변량, 변비/설사, 투석, 생리 또는 식사 전후처럼 체중값에 영향을 줄 수 있는 변화와 측정 시점을 알려주세요.", 111, "measurement-detail", C + R),
        q("constitutional.weakness_fatigue_sleepiness_and_loss_of_strength_distinction", "Weakness Fatigue and Sleepiness Distinction", "string", "weakness-distinction", "힘이 빠짐이 실제 근력 저하, 쉽게 지침, 졸림 중 무엇에 가까운지와 각각의 시작 순서를 알려주세요.", 110, "weakness-detail", C + R),
        q("constitutional.strength_tasks_distribution_progression_recovery_and_falls", "Strength Task Loss and Falls", "string", "strength-tasks", "의자에서 일어나기·계단·걷기·물건 들기·머리 빗기 같은 동작 변화, 좌우·몸통 분포, 진행·회복과 넘어짐을 알려주세요.", 109, "weakness-detail", C + S),
        q("nutrition.meal_frequency_portion_food_groups_intake_change_and_duration", "Detailed Nutritional Intake", "string", "intake-detail", "평소와 현재 하루 식사·간식 횟수, 대략적인 양과 음식 종류, 실제 섭취 감소 정도와 지속기간을 알려주세요.", 108, "nutrition-detail", C + R),
        q("nutrition.chewing_dental_swallowing_pain_choking_and_food_sticking", "Chewing and Swallowing Detail", "string", "swallow-detail", "치아·입안 문제, 씹기나 삼킬 때 통증, 음식 걸림·사레·기침, 고형식과 물 중 어느 쪽이 어려운지 알려주세요.", 107, "nutrition-detail", C + S),
        q("nutrition.cannot_swallow_liquids_saliva_or_repeated_choking", "Unable to Swallow or Repeated Choking", "boolean", "swallow-warning", "현재 물이나 침도 삼키기 어렵거나 반복해서 심하게 사레가 드나요?", 131, "nutrition-detail", S, safety_relevant=True),
        q("nutrition.nausea_vomiting_early_satiety_reflux_abdominal_and_meal_relation", "Upper Gastrointestinal and Meal Context", "string", "upper-gi", "메스꺼움·구토·조기 포만·속쓰림·복통이 있다면 횟수, 내용, 식사와의 관계와 시작 순서를 알려주세요.", 106, "nutrition-detail", C + R),
        q("nutrition.stool_frequency_form_fat_blood_diarrhea_constipation_and_loss", "Bowel and Nutrient Loss Detail", "string", "bowel-detail", "배변 횟수·형태, 기름지거나 뜨는 변, 설사·변비·혈변/검은 변과 체중 변화 전후 관계를 알려주세요.", 105, "nutrition-detail", C + R),
        q("constitutional.fever_temperature_chills_night_sweat_dates_frequency_and_environment", "Fever and Night Sweat Timeline", "string", "fever-sweat-detail", "체온값·측정 시각, 오한, 야간 발한의 빈도·지속·침구 교체 여부와 방 온도, 체중 변화와의 순서를 알려주세요.", 104, "systemic-detail", C + R),
        q("constitutional.cough_dyspnea_chest_pain_blood_and_symptom_sequence", "Respiratory and Chest Symptom Sequence", "string", "respiratory-sequence", "기침·가래·객혈·숨참·흉통이 있다면 시작 순서, 지속기간, 활동·수면 영향과 현재 상태를 알려주세요.", 103, "systemic-detail", C + S),
        q("constitutional.pain_present", "Pain Present with Constitutional Change", "boolean", "pain-present", "체중·전신상태 변화와 함께 현재 또는 반복되는 통증이 있나요?", 103, "systemic-detail", C + R),
        q("constitutional.pain_site_frequency_character_night_function_and_weight_relation", "Pain Detail with Constitutional Change", "string", "pain-detail", "통증이 있다면 정확한 부위·빈도·양상·야간/활동 영향과 체중 변화 전후 관계를 알려주세요.", 102, "systemic-detail", C + R),
        q("constitutional.node_mass_bleeding_skin_change_and_timeline", "Mass Bleeding and Skin Change Timeline", "string", "mass-bleeding-detail", "멍울·덩이, 혈변·검은 변·혈뇨·비정상 출혈, 멍·창백·황달·피부 변화가 있다면 부위·양·시작 순서를 알려주세요.", 101, "systemic-detail", C + S),
        q("constitutional.medicine_product_dose_route_indication_start_change_last_use_and_effect", "Structured Medicine and Substance Timeline", "string", "medicine-timeline", "처방약·일반약·주사·호르몬·한약·보충제마다 제품/성분명, 용량·경로·목적, 시작/변경일, 마지막 사용과 체중·식욕 변화의 시간관계를 알려주세요.", 100, "medicine-detail", D + R),
        q("constitutional.restriction_binge_vomit_laxative_diuretic_exercise_and_water_loading", "Eating and Compensatory Behaviours", "string", "eating-behaviour", "식사 제한·금식, 통제하기 어려운 폭식, 일부러 구토, 하제·이뇨제·다이어트약, 과도한 운동·물 섭취가 있다면 빈도와 최근 시점을 알려주세요.", 99, "eating-behaviour", C + S),
        q("constitutional.purging_with_fainting_chest_pain_or_severe_weakness", "Purging with Physical Instability", "boolean", "purging-warning", "구토·하제·이뇨제 사용 또는 심한 식사 제한과 함께 실신, 가슴 통증·심한 두근거림 또는 서 있기 어려운 쇠약이 있나요?", 130, "eating-behaviour", S, safety_relevant=True),
        q("constitutional.body_image_weight_goal_fear_and_family_observation", "Body Image and Weight Goal Context", "string", "body-image", "원하는 체중, 체중 증가에 대한 두려움·체형 걱정과 본인 또는 가족이 관찰한 식사행동 변화를 알려주세요.", 98, "eating-behaviour", C + R),
        q("constitutional.current_self_harm_or_suicide_danger", "Current Self-harm or Suicide Danger", "boolean", "self-harm-warning", "현재 자신을 해치거나 죽고 싶은 생각이 구체적이고, 곧 행동할 위험이 있나요?", 133, "eating-behaviour", S, safety_relevant=True),
        q("nutrition.food_access_cost_preparation_support_dentition_and_preferences", "Food Access and Eating Support", "string", "food-access", "음식 비용·구입·조리, 혼자 식사, 치아/의치, 도움 제공자와 종교·문화·알레르기·선호로 먹기 어려운 점을 알려주세요.", 97, "nutrition-detail", R),
        q("constitutional.alcohol_nicotine_caffeine_recreational_substance_and_last_use", "Alcohol Tobacco Caffeine and Substance Context", "string", "substance-detail", "술·담배/니코틴·카페인/에너지음료·기타 물질의 종류, 양·빈도와 마지막 사용 및 최근 변화를 알려주세요.", 96, "medicine-detail", R),
        q("constitutional.contact_travel_tb_occupation_animal_and_environment_timeline", "Infection Travel and Occupational Exposure", "string", "exposure-detail", "감염·결핵 접촉, 여행·거주지, 직업상 분진/석면·화학물질, 동물 노출의 날짜와 증상 시작 관계를 알려주세요.", 95, "history-detail", R),
        q("constitutional.medical_surgical_dental_history_stage_treatment_and_status", "Relevant Medical Surgical and Dental History", "string", "history-detail", "암·감염·내분비·당뇨·심폐·신장·간·장·신경·정신·치과 질환과 수술의 정확한 진단, 시기·치료·현재 상태를 알려주세요.", 94, "history-detail", R),
        q("constitutional.family_weight_endocrine_cancer_gi_and_eating_history", "Relevant Family History", "string", "family-history", "가족의 비슷한 체중 변화, 내분비·당뇨·암·소화기 질환 또는 섭식문제가 있다면 관계·진단명·진단 나이를 알려주세요.", 93, "history-detail", R),
        q("constitutional.pregnancy_gestation_postpartum_lactation_menstrual_puberty_and_growth", "Pregnancy Reproductive and Puberty Context", "string", "pregnancy-context", "해당되는 경우 임신 주수·출산 후 기간·수유, 월경 변화·폐경, 청소년의 사춘기·성장 변화와 체중 변화의 관계를 알려주세요.", 92, "life-stage", R),
        q("constitutional.child_age_height_weight_dates_growth_intake_activity_and_proxy", "Child Growth and Proxy Context", "string", "child-context", "소아라면 나이, 날짜가 있는 키·체중 원값과 측정 출처, 성장·사춘기, 섭취·활동 변화와 보호자가 직접 본 내용을 알려주세요.", 91, "life-stage", C + R),
        q("constitutional.older_frailty_muscle_dentition_swallowing_cognition_and_support", "Older Adult Frailty and Support Context", "string", "older-context", "고령자라면 근육·보행·낙상, 치아·삼킴, 인지·우울, 쇼핑·조리·식사와 보호자 지원의 변화를 알려주세요.", 90, "life-stage", R),
        q("constitutional.prior_exam_vitals_labs_imaging_endoscopy_date_result_source_and_pending", "Prior Examination and Test Provenance", "string", "prior-tests", "이전 진찰·활력징후, 혈액/소변/대변검사, 영상·내시경 결과가 있다면 날짜, 설명받은 결과, 자료 출처와 아직 확인하지 못한 결과를 알려주세요.", 89, "history-detail", R),
        q("constitutional.diet_exercise_medicine_counselling_response_and_adverse_effect", "Previous Intervention and Response", "string", "treatment-response", "식사·운동 변화, 영양보충, 약물·상담 등 시행한 방법의 시작일·빈도, 체중/기능 반응과 부작용을 알려주세요.", 88, "history-detail", C + R),
        q("constitutional.eating_mobility_sleep_work_school_selfcare_driving_and_fall_impact", "Detailed Functional and Safety Impact", "string", "function-detail", "식사·걷기·수면·업무/등교·씻기·옷입기·운전과 낙상 위험에 어떤 영향이 있는지 알려주세요.", 87, "function-detail", C + R),
        q("constitutional.communication_language_hearing_vision_cognition_literacy_and_accessibility", "Communication and Accessibility Needs", "string", "accessibility", "통역·청각·시각·인지·문해·디지털 사용 또는 체중 측정에 필요한 도움과 선호하는 응답 방법을 알려주세요.", 86, "handoff", R),
        q("constitutional.information_source_measurement_record_reliability_conflict_and_proxy", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자 중 누가 답하는지, 체중계·건강앱·의무기록·약 목록 유무와 기억이 불확실하거나 자료가 서로 다른 부분을 알려주세요.", 85, "handoff", R),
        q("constitutional.patient_goal_expected_help_and_additional_rfe", "Patient Goal and Additional RFE", "string", "goal", "진료에서 확인하고 싶은 내용, 원하는 도움과 질문에 없던 의견 또는 별도 문진이 필요한 다른 문제를 알려주세요.", 84, "handoff", C + R),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}; entries.update({item["fact"]["id"]: item for item in additions}); doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    for key, identifier in G.items(): nodes[identifier] = {"id": identifier, "type": "ClinicalGroup", "display": key.replace("-", " ").title()}
    doc["extra_nodes"] = list(nodes.values())
    new_rules = [
        {"id": "rule.weight-constitutional-change.safety.current-self-harm-danger", "priority": 1000, "when": {"fact": "constitutional.current_self_harm_or_suicide_danger", "equals": True}, "then": {"safety_level": "emergency", "action": "human_handoff", "suppress_routine": True}},
        {"id": "rule.weight-constitutional-change.safety.cannot-swallow-liquids", "priority": 930, "when": {"fact": "nutrition.cannot_swallow_liquids_saliva_or_repeated_choking", "equals": True}, "then": {"safety_level": "urgent", "action": "human_handoff", "suppress_routine": True}},
        {"id": "rule.weight-constitutional-change.safety.purging-physical-instability", "priority": 1000, "when": {"fact": "constitutional.purging_with_fainting_chest_pain_or_severe_weakness", "equals": True}, "then": {"safety_level": "emergency", "action": "human_handoff", "suppress_routine": True}},
        {"id": "rule.weight-constitutional-change.safety.unintentional-loss-mass", "priority": 900, "when": {"all": [{"fact": "weight.change_intentionality", "equals": "unintentional"}, {"fact": "symptom.unexplained_lymph_node_or_mass", "equals": True}]}, "then": {"safety_level": "urgent", "action": "human_handoff", "suppress_routine": True}},
        {"id": "rule.weight-constitutional-change.safety.unintentional-loss-bleeding", "priority": 900, "when": {"all": [{"fact": "weight.change_intentionality", "equals": "unintentional"}, {"fact": "symptom.visible_or_suspected_blood_loss", "equals": True}]}, "then": {"safety_level": "urgent", "action": "human_handoff", "suppress_routine": True}},
    ]
    rules = {item["id"]: item for item in doc["safety_rules"]}; rules.update({item["id"]: item for item in new_rules}); doc["safety_rules"] = list(rules.values())
    doc["default_refresh"].update({"last_assessed_at": "2026-07-20", "next_monitor_at": "2026-07-21", "next_full_review_at": "2027-01-16"}); doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc: dict) -> dict:
    result = completion_policy(prefix=P, fragment=doc, presentation_fact="constitutional.primary_concern", question_budget=92, source_refs=SOURCES)
    result["required_facts"]["routine"] = ["constitutional.primary_context", "constitutional.change_duration", "weight.change_intentionality", "weight.current_kg", "weight.previous_kg_and_date", "weight.change_trajectory", "mental_health.mood_stress_or_eating_concern", "constitutional.patient_words_first_change_and_main_concern", "constitutional.first_latest_date_context_sequence_and_baseline", "weight.usual_current_low_high_date_scale_clothing_and_source", "weight.weekly_monthly_rate_percent_period_and_calculation_source", "constitutional.weakness_fatigue_sleepiness_and_loss_of_strength_distinction", "constitutional.eating_mobility_sleep_work_school_selfcare_driving_and_fall_impact", "constitutional.information_source_measurement_record_reliability_conflict_and_proxy", "constitutional.patient_goal_expected_help_and_additional_rfe"]
    result["conditional_required_facts"] = [{"selector_fact": "constitutional.primary_context", "cases": {
        "unintentional_weight_loss": ["symptom.appetite_change", "nutrition.meal_frequency_portion_food_groups_intake_change_and_duration", "nutrition.chewing_dental_swallowing_pain_choking_and_food_sticking", "nutrition.nausea_vomiting_early_satiety_reflux_abdominal_and_meal_relation", "nutrition.stool_frequency_form_fat_blood_diarrhea_constipation_and_loss", "constitutional.node_mass_bleeding_skin_change_and_timeline", "constitutional.medical_surgical_dental_history_stage_treatment_and_status", "constitutional.prior_exam_vitals_labs_imaging_endoscopy_date_result_source_and_pending"],
        "intentional_weight_loss": ["constitutional.body_image_weight_goal_fear_and_family_observation", "constitutional.diet_exercise_medicine_counselling_response_and_adverse_effect", "constitutional.medicine_product_dose_route_indication_start_change_last_use_and_effect", "constitutional.eating_mobility_sleep_work_school_selfcare_driving_and_fall_impact"],
        "weight_gain_or_fluid_change": ["weight.rapid_gain_with_edema", "weight.fluid_edema_diuresis_bowel_dialysis_and_measurement_context", "constitutional.medicine_product_dose_route_indication_start_change_last_use_and_effect", "constitutional.pregnancy_gestation_postpartum_lactation_menstrual_puberty_and_growth", "constitutional.prior_exam_vitals_labs_imaging_endoscopy_date_result_source_and_pending"],
        "night_sweats_or_fever": ["symptom.night_sweats", "symptom.drenching_night_sweats", "symptom.night_sweat_frequency", "environment.sleep_heat_or_bedding", "constitutional.fever_temperature_chills_night_sweat_dates_frequency_and_environment", "constitutional.cough_dyspnea_chest_pain_blood_and_symptom_sequence", "constitutional.contact_travel_tb_occupation_animal_and_environment_timeline", "constitutional.node_mass_bleeding_skin_change_and_timeline"],
        "generalized_weakness_or_function_loss": ["symptom.generalized_weakness", "constitutional.strength_tasks_distribution_progression_recovery_and_falls", "constitutional.cough_dyspnea_chest_pain_blood_and_symptom_sequence", "constitutional.medical_surgical_dental_history_stage_treatment_and_status", "constitutional.medicine_product_dose_route_indication_start_change_last_use_and_effect", "constitutional.prior_exam_vitals_labs_imaging_endoscopy_date_result_source_and_pending"],
        "eating_or_intake_concern": ["nutrition.meal_frequency_portion_food_groups_intake_change_and_duration", "constitutional.restriction_binge_vomit_laxative_diuretic_exercise_and_water_loading", "constitutional.body_image_weight_goal_fear_and_family_observation", "mental_health.mood_stress_or_eating_concern", "constitutional.alcohol_nicotine_caffeine_recreational_substance_and_last_use", "nutrition.food_access_cost_preparation_support_dentition_and_preferences", "constitutional.prior_exam_vitals_labs_imaging_endoscopy_date_result_source_and_pending"],
        "child_or_proxy": ["constitutional.child_age_height_weight_dates_growth_intake_activity_and_proxy", "constitutional.information_source_measurement_record_reliability_conflict_and_proxy", "constitutional.communication_language_hearing_vision_cognition_literacy_and_accessibility"],
        "pregnancy_or_postpartum": ["constitutional.pregnancy_gestation_postpartum_lactation_menstrual_puberty_and_growth", "nutrition.meal_frequency_portion_food_groups_intake_change_and_duration", "constitutional.medicine_product_dose_route_indication_start_change_last_use_and_effect", "constitutional.prior_exam_vitals_labs_imaging_endoscopy_date_result_source_and_pending"],
        "followup_or_result_review": ["constitutional.prior_exam_vitals_labs_imaging_endoscopy_date_result_source_and_pending", "constitutional.diet_exercise_medicine_counselling_response_and_adverse_effect", "weight.usual_current_low_high_date_scale_clothing_and_source", "constitutional.medicine_product_dose_route_indication_start_change_last_use_and_effect"],
        "multiple_or_unclear": ["weight.height_date_method_and_reported_bmi_source", "weight.fluid_edema_diuresis_bowel_dialysis_and_measurement_context", "constitutional.pain_present", "constitutional.pain_site_frequency_character_night_function_and_weight_relation", "constitutional.medical_surgical_dental_history_stage_treatment_and_status", "constitutional.older_frailty_muscle_dentition_swallowing_cognition_and_support", "constitutional.communication_language_hearing_vision_cognition_literacy_and_accessibility"],
    }}]
    result["provenance"] = provenance(SOURCES)
    return result


def sources() -> dict:
    doc = load(RESEARCH)
    additions = [
        {"id": "source.nice.ng69.eating-disorders.2020", "kind": "clinical_guideline_metadata", "publisher": "NICE", "title": "Eating disorders: recognition and treatment", "version": "NG69-updated-2020-accessed-2026-07-20", "url": "https://www.nice.org.uk/guidance/ng69/chapter/recommendations", "language": "en", "digest": "metadata_only_not_cached", "license_status": "restricted", "complete": False, "monitor_profile": "nice_guidance", "monitor_interval_days": 7, "last_monitored_at": "2026-07-20", "next_monitor_at": "2026-07-27", "assertions": ["Assessment records rapid weight loss, restriction, bingeing, vomiting, laxative or diuretic use, excessive exercise, physical compromise, mental-health comorbidity, substance use and current self-harm or suicide risk without using a screening score as sole authority.", "Severe dehydration, severe malnutrition, organ-failure warning features or physical instability need acute medical assessment; BMI alone must not determine treatment or admission."]},
        {"id": "source.cdc.tuberculosis-symptoms.2025", "kind": "public_health_guidance_metadata", "publisher": "CDC", "title": "Signs and Symptoms of Tuberculosis", "version": "published-2025-01-17-accessed-2026-07-20", "url": "https://www.cdc.gov/tb/signs-symptoms/index.html", "language": "en", "digest": "metadata_only_not_cached", "license_status": "unknown", "complete": False, "monitor_profile": "public_health_guidance", "monitor_interval_days": 7, "last_monitored_at": "2026-07-20", "next_monitor_at": "2026-07-27", "assertions": ["Weight loss, poor appetite, weakness or fatigue, fever, chills and night sweats are recorded with cough, chest pain or haemoptysis and exposure timing; Runtime does not infer tuberculosis."]},
    ]
    artifacts = {item["id"]: item for item in doc["artifacts"]}; artifacts.update({item["id"]: item for item in additions}); doc["artifacts"] = list(artifacts.values()); doc["updated_at"] = CREATED; doc["provenance"] = provenance([item["id"] for item in doc["artifacts"]])
    return doc


def clinician(doc: dict) -> dict:
    result = load(CLINICIAN); ids = {item["fact"]["id"] for item in doc["entries"]}; ids.update({"pain.frequency", "pain.nrs_score"}); result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.weight_constitutional_change"] = sorted(ids); return result


def pain_module() -> dict:
    result = load(PAIN)
    result["profile_bindings"]["weight_constitutional_change"] = {
        "activation": "when",
        "when": {"fact": "constitutional.pain_present", "equals": True},
    }
    return result


def condition_state(condition: dict) -> dict[str, dict]:
    result = {}
    if "fact" in condition: result[condition["fact"]] = {"value": condition.get("equals", True)}
    for child in condition.get("all", []): result.update(condition_state(child))
    return result


def routine_cases(doc: dict, completion: dict) -> dict[str, dict]:
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}; always = completion["required_facts"]["always"]; core = completion["required_facts"]["routine"]; branches = completion["conditional_required_facts"][0]["cases"]
    forbidden = ["diagnosis.cancer", "diagnosis.tuberculosis", "diagnosis.eating_disorder", "diagnosis.thyroid_disease", "recommendation.start_nutrition_support"]
    def value(fid):
        fact = by_id[fid]
        if fact["value_type"] == "boolean": return False
        if fact["value_type"] == "integer": return 65
        if fact["value_type"] == "quantity": return {"amount": 4, "unit": "weeks"}
        if fact["value_type"] == "coded": return fact.get("allowed_values", ["uncertain"])[-1]
        return "특이사항 없음"
    def state(branch):
        ids = dict.fromkeys([*always, *core, *branches[branch]]); result = {fid: {"value": value(fid)} for fid in ids}; result["constitutional.primary_concern"] = {"value": "multiple"}; result["constitutional.primary_context"] = {"value": branch}; result["weight.change_intentionality"] = {"value": "uncertain"}; return result
    specs = [
        ("UNINTENTIONAL-MEASURED", "unintentional_weight_loss", 54, "의도하지 않은 체중 감소의 측정값과 섭취·동반증상을 진료 전에 정리합니다.", {"weight.change_intentionality": {"value": "unintentional"}}),
        ("INTENTIONAL-FOLLOWUP", "intentional_weight_loss", 43, "의도한 체중 변화의 방법·속도·기능과 부작용을 정리합니다.", {"weight.change_intentionality": {"value": "intentional"}}),
        ("GAIN-FLUID-CONTEXT", "weight_gain_or_fluid_change", 68, "체중 증가가 체액·부종 및 측정 조건과 어떻게 겹치는지 기록합니다.", {}),
        ("NIGHT-SWEAT-EXPOSURE", "night_sweats_or_fever", 46, "야간 발한·열과 기침·노출의 순서를 기록하되 원인을 진단하지 않습니다.", {}),
        ("WEAKNESS-TASKS", "generalized_weakness_or_function_loss", 72, "피로와 실제 근력 저하를 구분하고 구체적인 동작 변화를 기록합니다.", {}),
        ("EATING-BEHAVIOUR-SENSITIVE", "eating_or_intake_concern", 19, "식사 제한과 보상행동을 낙인 없이 민감하게 기록합니다.", {}),
        ("CHILD-PROXY-GROWTH", "child_or_proxy", 9, "보호자가 날짜와 출처가 있는 성장 측정 원값으로 답합니다.", {}),
        ("PREGNANCY-POSTPARTUM", "pregnancy_or_postpartum", 31, "임신·산후의 체중·섭취·수유 및 약물 맥락을 기록합니다.", {}),
        ("FOLLOWUP-RESULT-SOURCE", "followup_or_result_review", 63, "이전 검사결과를 재요구하지 않고 날짜·결과·출처와 미확인 여부를 기록합니다.", {}),
        ("OLDER-ACCESSIBILITY", "multiple_or_unclear", 84, "고령자의 근육·치아·삼킴·돌봄과 접근성 요구를 기록합니다.", {}),
        ("MULTI-RFE-ADDITIONAL", "multiple_or_unclear", 49, "체중 변화 외 다른 증상은 별도 RFE로 보존합니다.", {"constitutional.patient_goal_expected_help_and_additional_rfe": {"value": "체중 변화 외 반복되는 두통도 별도 문진 요청"}}),
        ("PAIN-NRS-REQUIRED", "multiple_or_unclear", 57, "통증이 동반되면 빈도와 NRS 원점수를 필수 기록합니다.", {"constitutional.pain_present": {"value": True}, "constitutional.pain_site_frequency_character_night_function_and_weight_relation": {"value": "매일 밤 허리 통증"}, "pain.frequency": {"value": "daily"}, "pain.nrs_score": {"value": 7}}),
        ("MEASUREMENT-CONFLICT", "unintentional_weight_loss", 38, "가정 체중계와 의료기관 기록이 다르면 충돌을 보존합니다.", {"constitutional.information_source_measurement_record_reliability_conflict_and_proxy": {"value": "가정 62.4kg, 병원 64.0kg로 측정 조건이 달라 상충"}}),
        ("MEDICINE-TIMELINE", "intentional_weight_loss", 51, "약물과 체중·식욕 변화의 시간관계를 구조화하되 인과를 단정하지 않습니다.", {}),
        ("FOOD-ACCESS", "eating_or_intake_concern", 76, "음식 접근·조리·치아와 돌봄 장벽을 의료인에게 전달합니다.", {}),
    ]
    result = {}
    for key, branch, age, statement, overrides in specs:
        hidden = state(branch); hidden.update(overrides); expected = {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 105, "forbidden_assertions": forbidden}
        if key == "PAIN-NRS-REQUIRED": expected["expected_known_facts"] = {"pain.nrs_score": 7}
        result[f"CONST-{key}.json"] = {"id": f"CONST-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": hidden, "expected": expected, "provenance": provenance(SOURCES)}
    missing = "weight.usual_current_low_high_date_scale_clothing_and_source"; absent = state("unintentional_weight_loss"); absent.pop(missing)
    result["CONST-MEASUREMENT-DATA-ABSENT.json"] = {"id": "CONST-MEASUREMENT-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 59}, "initial_statement": {"ko": "옷이 헐렁해졌지만 체중을 직접 재지 못했습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {missing: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 105, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    rules = {item["id"]: item for item in doc["safety_rules"]}
    for key, rule_id in {"SELF-HARM-DANGER": "rule.weight-constitutional-change.safety.current-self-harm-danger", "CANNOT-SWALLOW": "rule.weight-constitutional-change.safety.cannot-swallow-liquids", "PURGING-INSTABILITY": "rule.weight-constitutional-change.safety.purging-physical-instability", "UNINTENTIONAL-MASS": "rule.weight-constitutional-change.safety.unintentional-loss-mass", "UNINTENTIONAL-BLEEDING": "rule.weight-constitutional-change.safety.unintentional-loss-bleeding"}.items():
        rule = rules[rule_id]; level = rule["then"]["safety_level"]
        result[f"CONST-{key}.json"] = {"id": f"CONST-{key}", "simulation_language": "ko", "persona": {"age": 48}, "initial_statement": {"ko": "체중 변화와 함께 시간민감한 위험 신호가 있어 안전평가를 진행합니다."}, "hidden_state": condition_state(rule["when"]), "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule_id], "expected_max_turns": 45, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    return result


def main() -> None:
    seed_weight_constitutional_change.main(); doc = fragment(); completion = policy(doc); write_json(FRAGMENT, doc); write_json(POLICY, completion); write_json(RESEARCH, sources()); write_json(PAIN, pain_module()); write_json(CLINICIAN, clinician(doc))
    for name, case in routine_cases(doc, completion).items(): write_json(f"simulation/patients/general/weight-constitutional-change/{name}", case)


if __name__ == "__main__": main()
