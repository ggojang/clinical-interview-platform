#!/usr/bin/env python3
"""Rebuild unreviewed fatigue knowledge for professional pre-visit handoff."""
from profile_support import *

P, RFE = "fatigue", "rfe.fatigue"
M, SN = "mapping.snomed-mrcm.fatigue", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-18T00:00:00Z"
SOURCES = [
    "source.nhs.tiredness-fatigue.2023", "source.nice.ng206.mecfs.2021",
    "source.nice.ng12.fatigue.2026", "source.nice.ng222.depression.2026",
    "source.nhs.sleep-apnoea.2025", "source.nice.ng194.postnatal-care",
    "source.nhs.stroke-symptoms.2026", "source.nhs.carbon-monoxide-poisoning.2025",
    "source.nhs.vomiting-blood.2025", "source.nhs.fainting.2023",
    "source.nhs.chest-pain.2026", "source.nice.ng253.sepsis-adult",
    "source.nice.ng254.sepsis-under-16",
    "source.stom.mrcm.fatigue.20260714",
]
G = {key: f"group.fatigue.{key}" for key in (
    "routing", "safety", "course", "function", "sleep", "post_exertional",
    "mood", "systemic", "cardiopulmonary", "metabolic", "reproductive",
    "medicine", "history", "child", "handoff",
)}
C, S = ["intent.characterize_symptom"], ["intent.screen_red_flags"]
D, R = ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, group, intents, **kwargs):
    fact_overrides = kwargs.pop("fact_overrides", None)
    item = entry(
        P, fid, display, value_type, key, wording, score, key, [G[group]],
        intents=intents, **kwargs,
    )
    if fact_overrides:
        item["fact"].update(fact_overrides)
    return item


def fragment():
    groups = [
        "sudden_acute", "sleep_daytime", "post_exertional", "mood_stress",
        "systemic_weight_infection", "cardiopulmonary_bleeding",
        "endocrine_metabolic", "pregnancy_postpartum", "medicine_substance",
        "child_adolescent", "other_unclear",
    ]
    e = [
        Q("symptom.fatigue.current", "Current Fatigue or Lack of Energy", "boolean", "current", "지금도 평소와 다른 피로감·기운 없음·쉽게 지침이 계속되나요?", 300, "routing", C, terminology_binding={"system": SN, "code": "84229001"}),
        Q("fatigue.primary_group", "Primary Fatigue Context", "coded", "primary-group", "현재 피로와 가장 관련 있어 보이는 상황은 무엇인가요? 갑작스러운 변화, 수면·졸림, 활동 후 악화, 기분·스트레스, 감염·체중 변화, 숨참·출혈, 대사 증상, 임신·산후, 약물·물질, 소아·청소년, 또는 불분명 중에서 알려주세요.", 295, "routing", C + D, allowed_values=groups),
        Q("symptom.duration", "Fatigue Duration", "quantity", "duration", "피로는 언제부터 시작했고 얼마나 지속됐나요?", 190, "course", C, reuse_existing=True),
        Q("fatigue.onset_date_time_and_preceding_event", "Exact Onset and Preceding Event", "string", "onset-detail", "처음 시작한 날짜·시간과 당시 하던 일, 직전 감염·수술·출산·약 변경·과로 같은 계기를 알려주세요.", 189, "course", C),
        Q("fatigue.continuous_episodic_daily_pattern_and_trend", "Pattern Frequency and Trend", "string", "pattern", "계속 피곤한지 간헐적인지, 하루 중 심한 시간, 반복 빈도·한 번 지속시간과 좋아지거나 악화되는 추세를 알려주세요.", 188, "course", C),
        Q("symptom.fatigue.severity", "Fatigue Severity", "coded", "severity", "현재 피로는 가벼움, 중간, 심함 중 어디에 가깝나요?", 187, "course", C, allowed_values=["mild", "moderate", "severe"], terminology_binding={"system": SN, "focus_code": "84229001", "attribute_code": "246112005"}, mrcm_ref=M),
        Q("fatigue.physical_mental_sleepiness_or_weakness_description", "Patient Description of Fatigue", "string", "quality", "몸이 무거움·근력 저하·정신적 소진·졸림·의욕 저하 중 무엇에 가깝고, 본인의 표현으로는 어떤 느낌인가요?", 186, "course", C),
        Q("fatigue.rest_sleep_activity_and_meal_response", "Response to Rest Sleep Activity and Meals", "string", "response", "휴식·수면·가벼운 활동·식사 후 어떻게 달라지고, 악화시키거나 완화하는 것이 있나요?", 185, "course", C),
        Q("fatigue.function_work_school_selfcare_mobility_and_driving", "Functional Impact", "string", "function", "피로 때문에 일·학업·가사·씻기·식사·걷기·운전·돌봄이 이전보다 얼마나 줄었나요?", 184, "function", C + R),
        Q("fatigue.baseline_activity_change_good_bad_days_and_falls", "Baseline Change and Good or Bad Days", "string", "baseline-change", "피로 전 활동 수준과 비교한 변화, 좋은 날·나쁜 날의 차이, 넘어짐이나 보조 필요 여부를 알려주세요.", 183, "function", C + R),
        Q("fatigue.information_source_proxy_reliability_and_conflict", "Information Source Reliability and Conflict", "string", "source", "답변자가 본인인지 보호자인지, 기억이 불확실하거나 기록과 다른 내용이 있는지 알려주세요.", 182, "handoff", R),
        Q("fatigue.patient_concern_goal_and_additional_comment", "Patient Concern Goal and Additional Comment", "string", "goal", "가장 걱정되는 점, 진료에서 확인하고 싶은 점과 질문에 없던 의견을 알려주세요.", 181, "handoff", R),

        Q("mental_health.suicidal_ideation", "Suicidal Ideation", "boolean", "suicidal-ideation", "최근 죽고 싶거나 스스로를 해치고 싶다는 생각이 있었나요?", 280, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("mental_health.suicidal_intent_or_plan", "Suicidal Intent or Plan", "boolean", "suicidal-plan", "지금 스스로를 해칠 구체적인 계획·준비·의도가 있나요?", 279, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("fatigue.unable_to_wake_or_maintain_consciousness", "Unable to Wake or Maintain Consciousness", "boolean", "consciousness", "깨우기 어렵거나 깨어 있지 못하고 의식이 흐려지는 일이 있나요?", 278, "safety", S, safety_relevant=True),
        Q("symptom.confusion", "New Confusion", "boolean", "confusion", "갑자기 혼란스럽거나 사람·장소·시간을 알아보기 어려워졌나요?", 277, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.new_unilateral_weakness", "New Unilateral Weakness", "boolean", "unilateral-weakness", "갑자기 한쪽 얼굴·팔·다리에 힘이 빠지거나 말이 어눌해졌나요?", 276, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.dyspnea", "Breathlessness Severity", "coded", "dyspnea", "숨참은 없나요, 가벼운가요, 중간인가요, 쉬고 있어도 심한가요?", 275, "safety", S, allowed_values=["none", "mild", "moderate", "severe"], safety_relevant=True, reuse_existing=True),
        Q("symptom.chest_pain", "Chest Pain", "boolean", "chest-pain", "가슴 통증이나 압박감이 있나요?", 274, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.syncope", "Syncope", "boolean", "syncope", "실신했거나 거의 쓰러질 듯했던 일이 있나요?", 273, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.black_or_bloody_stool", "Black or Bloody Stool", "boolean", "gi-bleeding", "검은 변이나 피가 섞인 변이 있었나요?", 272, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("fatigue.active_heavy_bleeding_or_vomiting_blood", "Active Heavy Bleeding or Haematemesis", "boolean", "heavy-bleeding", "지금 멈추지 않는 많은 출혈이나 피를 토하는 증상이 있나요?", 271, "safety", S, safety_relevant=True),
        Q("symptom.fever", "Fever", "boolean", "fever", "현재 발열이나 오한이 있나요?", 270, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("patient.immunocompromised", "Immunocompromised State", "boolean", "immunocompromised", "항암치료·장기이식·고용량 면역억제제 등으로 면역이 크게 저하된 상태인가요?", 269, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("fatigue.pregnancy_postpartum_warning", "Pregnancy or Postpartum Warning Feature", "boolean", "pregnancy-warning", "임신 중이거나 출산 후라면 심한 출혈·가슴통증·숨참·한쪽 다리 붓기·심한 두통·발열이 있나요?", 268, "safety", S, safety_relevant=True),
        Q("fatigue.poisoning_overdose_or_carbon_monoxide_concern", "Poisoning Overdose or Carbon Monoxide Concern", "boolean", "poisoning", "약물 과량복용, 화학물질 노출, 난방기 사용 뒤 함께 있던 사람들의 두통·어지럼·피로 등 중독 가능성이 있나요?", 267, "safety", S, safety_relevant=True),
        Q("fatigue.child_severe_warning", "Child Severe Warning Feature", "boolean", "child-warning", "소아라면 깨우기 어려움·경련·심한 호흡곤란·물을 못 마심·소변이 크게 줄음·축 늘어짐이 있나요?", 266, "safety", S, safety_relevant=True),
        Q("fatigue.rapidly_worsening_weakness_or_inability_to_walk", "Rapidly Worsening Weakness or Inability to Walk", "boolean", "rapid-weakness", "근력 저하가 빠르게 악화되거나 혼자 서거나 걷기 어려워졌나요?", 265, "safety", S, safety_relevant=True),

        Q("sleep.hours_per_night", "Sleep Duration in Hours", "integer", "sleep-hours", "평균적으로 하루에 실제로 자는 시간은 몇 시간인가요? 숫자로 알려주세요.", 160, "sleep", D, reuse_existing=True),
        Q("sleep.insomnia", "Insomnia", "boolean", "insomnia", "잠들기 어렵거나 자주 깨거나 너무 일찍 깨나요?", 159, "sleep", D, reuse_existing=True),
        Q("sleep.snoring_gasping_or_choking", "Snoring Gasping or Choking", "boolean", "sleep-breathing", "코골이와 함께 숨이 멎거나 헐떡이고 컥컥거린다는 말을 들었나요?", 158, "sleep", D, reuse_existing=True),
        Q("symptom.unrefreshing_sleep", "Unrefreshing Sleep", "boolean", "unrefreshing-sleep", "충분히 자도 개운하지 않고 일어날 때부터 지쳐 있나요?", 157, "sleep", D, reuse_existing=True),
        Q("fatigue.sleep_schedule_latency_awakenings_quality_and_environment", "Sleep Schedule and Quality Detail", "string", "sleep-detail", "취침·기상 시각, 잠드는 데 걸리는 시간, 깨는 횟수, 수면 환경과 수면의 질을 알려주세요.", 156, "sleep", D),
        Q("fatigue.daytime_sleepiness_naps_unintentional_sleep_and_driving_risk", "Daytime Sleepiness and Safety", "string", "daytime-sleepiness", "낮잠·참기 어려운 졸림·의도치 않게 잠듦이 있고 운전이나 작업 중 위험했던 적이 있나요?", 155, "sleep", D + R),
        Q("fatigue.shift_work_caregiving_screens_caffeine_and_sleep_medicine", "Sleep Context and Exposures", "string", "sleep-context", "교대근무·야간돌봄·화면 사용·카페인·수면제·음주가 수면에 미치는 영향을 알려주세요.", 154, "sleep", D),

        Q("symptom.post_exertional_malaise", "Post-exertional Symptom Exacerbation", "boolean", "post-exertional", "적은 신체·정신·사회 활동 뒤에도 피로와 다른 증상이 지나치게 심해지나요?", 150, "post_exertional", D, reuse_existing=True),
        Q("symptom.post_exertional_delayed_or_prolonged", "Delayed or Prolonged Recovery", "boolean", "post-exertional-recovery", "활동 뒤 악화가 수시간 또는 다음 날 늦게 시작하거나 며칠 이상 지속되나요?", 149, "post_exertional", D, reuse_existing=True),
        Q("symptom.cognitive_difficulty", "Cognitive Difficulty", "boolean", "cognitive", "집중·기억·단어 찾기·생각 정리가 이전보다 어려워졌나요?", 148, "post_exertional", D, reuse_existing=True),
        Q("fatigue.activity_trigger_delay_duration_recovery_and_energy_limit", "Activity Trigger and Recovery Detail", "string", "activity-recovery", "어떤 활동이 악화를 유발하고, 몇 시간 뒤 시작해 얼마나 지속되며 이전 수준으로 회복하는 데 얼마나 걸리나요?", 147, "post_exertional", D),
        Q("fatigue.orthostatic_dizziness_palpitations_and_standing_effect", "Orthostatic Symptoms", "string", "orthostatic", "눕거나 앉았다 일어설 때 어지럼·두근거림·시야 흐림이 생기고 다시 누우면 좋아지나요?", 146, "post_exertional", D),
        Q("fatigue.pain_headache_sore_throat_lymph_and_flu_like_features", "Pain and Flu-like Features", "string", "associated-pain", "근육·관절통, 두통, 인후통, 목의 림프절 불편, 몸살 같은 증상이 함께 있나요?", 145, "post_exertional", D),

        Q("mental_health.low_mood", "Low Mood", "boolean", "low-mood", "최근 대부분의 날에 우울하거나 가라앉은 기분이 있었나요?", 142, "mood", D, reuse_existing=True),
        Q("mental_health.anhedonia", "Loss of Interest or Pleasure", "boolean", "anhedonia", "평소 즐기던 일에 흥미나 즐거움이 줄었나요?", 141, "mood", D, reuse_existing=True),
        Q("fatigue.anxiety_stress_bereavement_trauma_loneliness_and_support", "Psychosocial Context and Support", "string", "psychosocial", "불안·스트레스·상실·외상·고립·돌봄 부담과 도움을 받을 사람이나 지지체계를 알려주세요.", 140, "mood", D + R),
        Q("fatigue.mood_duration_function_prior_care_and_treatment_response", "Mood Course and Prior Care", "string", "mood-course", "기분 변화의 기간·일상 영향, 과거 정신건강 문제와 상담·약물 치료 및 반응을 알려주세요.", 139, "mood", D + R),

        Q("symptom.unintentional_weight_loss", "Unintentional Weight Loss", "boolean", "weight-loss", "의도하지 않은 체중 감소가 있나요?", 136, "systemic", D, reuse_existing=True),
        Q("symptom.appetite_loss", "Appetite Loss", "boolean", "appetite-loss", "식욕이 줄었거나 빨리 배부른가요?", 135, "systemic", D, reuse_existing=True),
        Q("symptom.cough", "Cough", "boolean", "cough", "기침이 계속되나요?", 134, "systemic", D, reuse_existing=True),
        Q("history.recent_infection", "Recent Infection", "boolean", "recent-infection", "최근 감염이나 감염 후 회복 중인 일이 있었나요?", 133, "systemic", D, reuse_existing=True),
        Q("fatigue.night_sweats_chills_measured_temperature_and_recurrent_fever", "Systemic Temperature Features", "string", "temperature-detail", "식은땀으로 옷을 갈아입을 정도의 야간발한, 오한, 반복 발열과 측정한 최고 체온·시간을 알려주세요.", 132, "systemic", D),
        Q("fatigue.recent_infection_covid_travel_sick_contact_and_exposure_timing", "Infection Travel and Contact Context", "string", "infection-context", "최근 감염·코로나19, 여행, 아픈 사람·동물·오염된 음식이나 물과 접촉한 시기와 증상 순서를 알려주세요.", 131, "systemic", D),
        Q("fatigue.lump_lymph_node_persistent_pain_rash_or_skin_change", "Lump Nodes Pain or Skin Change", "string", "systemic-other", "새 멍울·림프절, 지속 통증, 발진·황달·피부 변화가 있나요?", 130, "systemic", D),
        Q("patient.age_40_or_older", "Age 40 or Older", "boolean", "age-context", "만 40세 이상인가요?", 129, "systemic", R, reuse_existing=True),
        Q("patient.ever_smoked", "Ever Smoked", "boolean", "smoking-history", "현재 또는 과거에 흡연한 적이 있나요?", 128, "systemic", R, reuse_existing=True),
        Q("exposure.asbestos", "Asbestos Exposure", "boolean", "asbestos", "직업이나 환경에서 석면에 노출된 적이 있나요?", 127, "systemic", R, reuse_existing=True),

        Q("fatigue.palpitations_dizziness_exertional_dyspnea_pallor_and_exercise_tolerance", "Cardiopulmonary and Pallor Detail", "string", "cardiopulmonary", "두근거림·어지럼·창백함·활동 시 숨참과 이전보다 줄어든 운동 가능 거리를 알려주세요.", 124, "cardiopulmonary", D),
        Q("fatigue.bleeding_menses_gi_urine_bruising_donation_and_recent_loss", "Bleeding History", "string", "bleeding-history", "월경량 증가, 코피·잇몸출혈·멍, 혈뇨·혈변, 헌혈·수술·출산 등 최근 혈액 손실이 있었나요?", 123, "cardiopulmonary", D + R),
        Q("fatigue.chest_pain_character_radiation_trigger_duration_and_nrs_context", "Chest Pain Detail", "string", "chest-pain-detail", "가슴 통증이 있다면 위치·양상·퍼지는 곳·유발 상황·지속시간을 알려주세요.", 122, "cardiopulmonary", D),
        Q("pain.nrs_score", "Pain NRS 0 to 10", "integer", "pain-nrs", "통증이 있다면 지금 또는 가장 심할 때를 0에서 10 사이 숫자로 알려주세요.", 121, "cardiopulmonary", C, fact_overrides={"minimum": 0, "maximum": 10, "scale": {"type": "NRS", "minimum": 0, "maximum": 10, "lower_anchor": "no_pain", "upper_anchor": "worst_imaginable_pain"}, "must_preserve_raw_score": True, "required_when_pain_applies": True}, reuse_existing=True),
        Q("fatigue.edema_orthopnea_nocturnal_breathlessness_and_weight_gain", "Fluid and Positional Breathing Features", "string", "fluid-breathing", "다리 붓기·갑작스러운 체중 증가, 누우면 숨참, 밤에 숨이 차서 깨는 증상이 있나요?", 120, "cardiopulmonary", D),

        Q("symptom.thirst_and_polyuria", "Thirst and Polyuria", "boolean", "thirst-polyuria", "갈증이 심하고 소변량이나 야간 소변 횟수가 늘었나요?", 117, "metabolic", D, reuse_existing=True),
        Q("fatigue.weight_heat_cold_sweat_tremor_bowel_skin_hair_and_neck_change", "Endocrine-like Symptom Context", "string", "endocrine-context", "체중·더위/추위 민감성·땀·떨림·배변·피부·머리카락·목 앞쪽의 변화를 알려주세요.", 116, "metabolic", D),
        Q("fatigue.hunger_blurred_vision_recurrent_infection_and_wound_healing", "Metabolic Associated Features", "string", "metabolic-features", "심한 허기·시야 흐림·반복 감염·상처 회복 지연이 있나요?", 115, "metabolic", D),
        Q("fatigue.diet_restriction_intake_hydration_weight_height_and_measurement_source", "Nutrition Hydration and Measurements", "string", "nutrition", "식사 제한·최근 섭취량·수분 섭취와 키·현재 체중·변화량·측정 시점을 알려주세요.", 114, "metabolic", R),

        Q("fatigue.pregnancy_possible_lmp_gestation_postpartum_and_lactation", "Pregnancy and Postpartum Context", "string", "pregnancy-context", "해당되는 경우 임신 가능성, 마지막 월경일·임신 주수, 출산일·산후 기간과 수유 여부를 알려주세요.", 111, "reproductive", R),
        Q("fatigue.obstetric_history_delivery_bleeding_hypertension_infection_and_complications", "Professional Obstetric Context", "string", "obstetric-history", "임신·출산 횟수와 결과, 최근 분만 방식, 출혈·고혈압·감염·혈전 등 합병증을 알려주세요.", 110, "reproductive", R),

        Q("medication.possible_fatigue_contributor", "Possible Medicine-related Fatigue", "boolean", "medicine-contributor", "복용약이나 치료를 시작·중단·변경한 뒤 피로가 시작되거나 심해졌나요?", 107, "medicine", D, reuse_existing=True),
        Q("fatigue.current_medicines_dose_schedule_adherence_changes_supplements_and_allergies", "Complete Medicine and Allergy Context", "string", "medicine-detail", "처방약·일반약·한약·영양제의 이름·용량·횟수·복용 여부·최근 변경과 약물 알레르기를 알려주세요.", 106, "medicine", R),
        Q("fatigue.alcohol_caffeine_nicotine_recreational_substance_and_last_use", "Alcohol Caffeine Nicotine and Substance Use", "string", "substance", "술·카페인·담배/전자담배·기타 물질의 종류·양·빈도와 마지막 사용 시점을 알려주세요.", 105, "medicine", R),
        Q("fatigue.recent_treatment_surgery_hospitalization_vaccination_and_response", "Recent Treatment Procedure and Vaccination", "string", "recent-treatment", "최근 수술·입원·항암/방사선·감염 치료·예방접종의 날짜와 이후 변화가 있었나요?", 104, "medicine", R),

        Q("fatigue.chronic_conditions_prior_fatigue_surgery_and_family_history", "Relevant Medical Surgical and Family History", "string", "history", "심장·폐·혈액·갑상선·당뇨·신장·간·자가면역·암·정신건강 질환, 수술력, 이전 유사 피로와 가족력을 알려주세요.", 101, "history", R),
        Q("fatigue.previous_examination_labs_imaging_sleep_test_dates_results_and_source", "Prior Assessment and Test Results", "string", "prior-tests", "이 문제로 받은 진찰·혈액/소변검사·영상·수면검사의 날짜·결과와 정보 출처를 알려주세요. 받지 않았다면 받지 않았다고 답할 수 있습니다.", 100, "history", R),
        Q("fatigue.prior_treatment_rest_sleep_diet_activity_medicine_and_response", "Prior Management and Response", "string", "prior-response", "휴식·수면 조절·식사·활동 조절·약물 등 시도한 방법과 효과·부작용을 알려주세요.", 99, "history", R),
        Q("fatigue.occupation_shift_caregiving_heat_chemical_infection_and_co_exposure", "Occupation and Environmental Exposure", "string", "occupation-exposure", "직업·교대근무·돌봄 부담과 열·화학물질·감염·일산화탄소 가능 노출을 알려주세요.", 98, "history", R),

        Q("fatigue.child_age_growth_school_play_feeding_sleep_and_proxy_observation", "Child and Adolescent Proxy Detail", "string", "child-detail", "소아·청소년이라면 나이·성장/체중 변화·등교·놀이·운동·식사·수면과 보호자가 본 활력 변화를 알려주세요.", 95, "child", R),
    ]
    rules = [
        safety_rule(P, "suicide-intent", {"fact": "mental_health.suicidal_intent_or_plan", "equals": True}, "emergency", 1000),
        safety_rule(P, "cannot-maintain-consciousness", {"fact": "fatigue.unable_to_wake_or_maintain_consciousness", "equals": True}, "emergency", 1000),
        safety_rule(P, "confusion", {"fact": "symptom.confusion", "equals": True}, "emergency", 1000),
        safety_rule(P, "unilateral-weakness", {"fact": "symptom.new_unilateral_weakness", "equals": True}, "emergency", 1000),
        safety_rule(P, "severe-dyspnea", {"fact": "symptom.dyspnea", "equals": "severe"}, "emergency", 1000),
        safety_rule(P, "poisoning-overdose-co", {"fact": "fatigue.poisoning_overdose_or_carbon_monoxide_concern", "equals": True}, "emergency", 1000),
        safety_rule(P, "active-heavy-bleeding", {"fact": "fatigue.active_heavy_bleeding_or_vomiting_blood", "equals": True}, "emergency", 1000),
        safety_rule(P, "chest-pain-syncope", {"all": [{"fact": "symptom.chest_pain", "equals": True}, {"fact": "symptom.syncope", "equals": True}]}, "urgent", 900),
        safety_rule(P, "gastrointestinal-bleeding", {"fact": "symptom.black_or_bloody_stool", "equals": True}, "urgent", 900),
        safety_rule(P, "fever-immunocompromised", {"all": [{"fact": "symptom.fever", "equals": True}, {"fact": "patient.immunocompromised", "equals": True}]}, "urgent", 900),
        safety_rule(P, "pregnancy-postpartum-warning", {"fact": "fatigue.pregnancy_postpartum_warning", "equals": True}, "urgent", 900),
        safety_rule(P, "child-severe-warning", {"fact": "fatigue.child_severe_warning", "equals": True}, "urgent", 900),
        safety_rule(P, "rapidly-worsening-weakness", {"fact": "fatigue.rapidly_worsening_weakness_or_inability_to_walk", "equals": True}, "urgent", 900),
    ]
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-18", "next_monitor_at": "2026-07-19", "next_full_review_at": "2027-01-14"})
    return {"id": "knowledge.generated.systemic.fatigue", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-fatigue-research", "default_refresh": refresh, "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="symptom.fatigue.current", question_budget=78, source_refs=SOURCES)
    p["required_facts"]["routine"] = [
        "fatigue.primary_group", "symptom.duration", "fatigue.onset_date_time_and_preceding_event",
        "fatigue.continuous_episodic_daily_pattern_and_trend", "symptom.fatigue.severity",
        "fatigue.physical_mental_sleepiness_or_weakness_description", "fatigue.rest_sleep_activity_and_meal_response",
        "fatigue.function_work_school_selfcare_mobility_and_driving", "fatigue.baseline_activity_change_good_bad_days_and_falls",
        "fatigue.current_medicines_dose_schedule_adherence_changes_supplements_and_allergies",
        "fatigue.chronic_conditions_prior_fatigue_surgery_and_family_history",
        "fatigue.previous_examination_labs_imaging_sleep_test_dates_results_and_source",
        "fatigue.prior_treatment_rest_sleep_diet_activity_medicine_and_response",
        "fatigue.information_source_proxy_reliability_and_conflict", "fatigue.patient_concern_goal_and_additional_comment",
    ]
    cases = {
        "sudden_acute": ["history.recent_infection", "fatigue.recent_infection_covid_travel_sick_contact_and_exposure_timing", "fatigue.bleeding_menses_gi_urine_bruising_donation_and_recent_loss"],
        "sleep_daytime": ["sleep.hours_per_night", "sleep.insomnia", "sleep.snoring_gasping_or_choking", "symptom.unrefreshing_sleep", "fatigue.sleep_schedule_latency_awakenings_quality_and_environment", "fatigue.daytime_sleepiness_naps_unintentional_sleep_and_driving_risk", "fatigue.shift_work_caregiving_screens_caffeine_and_sleep_medicine"],
        "post_exertional": ["symptom.post_exertional_malaise", "symptom.post_exertional_delayed_or_prolonged", "symptom.cognitive_difficulty", "fatigue.activity_trigger_delay_duration_recovery_and_energy_limit", "fatigue.orthostatic_dizziness_palpitations_and_standing_effect", "fatigue.pain_headache_sore_throat_lymph_and_flu_like_features"],
        "mood_stress": ["mental_health.low_mood", "mental_health.anhedonia", "fatigue.anxiety_stress_bereavement_trauma_loneliness_and_support", "fatigue.mood_duration_function_prior_care_and_treatment_response", "fatigue.alcohol_caffeine_nicotine_recreational_substance_and_last_use"],
        "systemic_weight_infection": ["symptom.unintentional_weight_loss", "symptom.appetite_loss", "symptom.cough", "history.recent_infection", "fatigue.night_sweats_chills_measured_temperature_and_recurrent_fever", "fatigue.recent_infection_covid_travel_sick_contact_and_exposure_timing", "fatigue.lump_lymph_node_persistent_pain_rash_or_skin_change", "patient.age_40_or_older", "patient.ever_smoked", "exposure.asbestos"],
        "cardiopulmonary_bleeding": ["fatigue.palpitations_dizziness_exertional_dyspnea_pallor_and_exercise_tolerance", "fatigue.bleeding_menses_gi_urine_bruising_donation_and_recent_loss", "fatigue.chest_pain_character_radiation_trigger_duration_and_nrs_context", "pain.nrs_score", "fatigue.edema_orthopnea_nocturnal_breathlessness_and_weight_gain"],
        "endocrine_metabolic": ["symptom.thirst_and_polyuria", "fatigue.weight_heat_cold_sweat_tremor_bowel_skin_hair_and_neck_change", "fatigue.hunger_blurred_vision_recurrent_infection_and_wound_healing", "fatigue.diet_restriction_intake_hydration_weight_height_and_measurement_source"],
        "pregnancy_postpartum": ["fatigue.pregnancy_possible_lmp_gestation_postpartum_and_lactation", "fatigue.obstetric_history_delivery_bleeding_hypertension_infection_and_complications", "fatigue.bleeding_menses_gi_urine_bruising_donation_and_recent_loss"],
        "medicine_substance": ["medication.possible_fatigue_contributor", "fatigue.alcohol_caffeine_nicotine_recreational_substance_and_last_use", "fatigue.recent_treatment_surgery_hospitalization_vaccination_and_response", "fatigue.occupation_shift_caregiving_heat_chemical_infection_and_co_exposure"],
        "child_adolescent": ["fatigue.child_age_growth_school_play_feeding_sleep_and_proxy_observation", "sleep.hours_per_night", "symptom.unrefreshing_sleep", "history.recent_infection", "mental_health.low_mood", "mental_health.anhedonia"],
        "other_unclear": ["fatigue.occupation_shift_caregiving_heat_chemical_infection_and_co_exposure", "fatigue.diet_restriction_intake_hydration_weight_height_and_measurement_source", "medication.possible_fatigue_contributor", "history.recent_infection"],
    }
    p["conditional_required_facts"] = [{"selector_fact": "fatigue.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nhs.tiredness-fatigue.2023", "NHS", "Tiredness and fatigue", "reviewed-2023-06-02", "https://www.nhs.uk/symptoms/tiredness-and-fatigue/", "public_health_guidance", ["Persistent unexplained fatigue, functional impact, weight loss, mood change or sleep-related gasping warrant clinical assessment.", "Sleep, lifestyle, stress, hormonal change, illness, treatment, medicines, palpitations, dyspnoea, pallor, thirst and urinary frequency are relevant contexts without establishing a diagnosis."]),
        ("source.nice.ng206.mecfs.2021", "NICE", "ME/CFS: diagnosis and management", "NG206-reviewed-2025-01-24", "https://www.nice.org.uk/guidance/ng206/chapter/recommendations", "nice_guidance", ["Assessment records specific onset, debilitating fatigue, activity reduction, post-exertional symptom exacerbation including delay and duration, unrefreshing sleep and cognitive difficulty.", "Medical, mental-health and social context and alternative explanations require clinician assessment; the interview does not diagnose ME/CFS."]),
        ("source.nice.ng12.fatigue.2026", "NICE", "Suspected cancer: recognition and referral — fatigue", "NG12-updated-2026", "https://www.nice.org.uk/guidance/ng12/chapter/Recommended-actions-organised-by-symptom-and-findings-of-primary-care-investigations", "nice_guidance", ["Persistent fatigue with age, smoking, asbestos exposure, cough, dyspnoea, chest pain, weight loss or appetite loss can require clinician investigation.", "The interview records these features without diagnosing cancer or selecting a test."]),
        ("source.nice.ng222.depression.2026", "NICE", "Depression in adults: treatment and management", "NG222-reviewed-2026", "https://www.nice.org.uk/guidance/ng222/chapter/Recommendations", "nice_guidance", ["Assessment includes function, sleep, diet, activity, stressful events, relationships, living conditions, prescribed and illicit drugs, alcohol, employment, loneliness and prior treatment response.", "People with depressive symptoms are asked directly about suicidal ideation and intent; considerable immediate risk requires urgent specialist help."]),
        ("source.nhs.sleep-apnoea.2025", "NHS", "Sleep apnoea", "current-2026", "https://www.nhs.uk/conditions/sleep-apnoea/", "public_health_guidance", ["Observed breathing pauses, gasping or choking, loud snoring, repeated waking, morning headache, daytime tiredness and impaired concentration are relevant handoff features.", "Uncontrolled excessive sleepiness can create driving and occupational safety risk; the interview does not diagnose sleep apnoea."]),
        ("source.nice.ng194.postnatal-care", "NICE", "Postnatal care", "NG194-current-2026", "https://www.nice.org.uk/guidance/ng194/chapter/recommendations", "nice_guidance", ["Postnatal heavy bleeding, infection features, leg swelling or tenderness with breathlessness, chest pain and persistent severe headache require prompt clinical assessment.", "The fatigue interview records postpartum timing and obstetric context without diagnosing a complication."]),
        ("source.nhs.stroke-symptoms.2026", "NHS", "Symptoms of a stroke", "current-2026", "https://www.nhs.uk/conditions/stroke/symptoms/", "public_health_guidance", ["Sudden facial or unilateral arm weakness and speech difficulty are emergency warning features; confusion can also occur.", "The interview records reported warning features and does not diagnose stroke."]),
        ("source.nhs.carbon-monoxide-poisoning.2025", "NHS", "Carbon monoxide poisoning", "reviewed-2025-12-16", "https://www.nhs.uk/conditions/carbon-monoxide-poisoning/", "public_health_guidance", ["Headache, dizziness, nausea, weakness, tiredness, confusion, chest pain and breathlessness that vary by location or affect co-occupants support immediate exposure assessment.", "Breathing difficulty, sudden confusion, loss of consciousness, marked weakness or chest pain after possible exposure require emergency help."]),
        ("source.nhs.vomiting-blood.2025", "NHS", "Vomiting blood", "reviewed-2025-08-18", "https://www.nhs.uk/symptoms/vomiting-blood/", "public_health_guidance", ["Vomiting blood with confusion, faintness, rapid breathing, clammy pallor, abdominal pain or black stool requires emergency assessment.", "The interview records bleeding features without assigning a bleeding source."]),
        ("source.nhs.fainting.2023", "NHS", "Fainting", "reviewed-2023-02-23", "https://www.nhs.uk/symptoms/fainting/", "public_health_guidance", ["Failure to wake promptly, incomplete recovery, speech or movement difficulty, chest pain, palpitations, seizure activity or exertional fainting are emergency warning features."]),
        ("source.nhs.chest-pain.2026", "NHS", "Chest pain", "current-2026", "https://www.nhs.uk/symptoms/chest-pain/", "public_health_guidance", ["Persistent sudden pressure-like chest discomfort, radiation, or chest pain with sweating, nausea, light-headedness or breathlessness requires emergency help.", "The interview records pain character and a raw NRS without diagnosing a cardiac condition."]),
        ("source.nice.ng253.sepsis-adult", "NICE", "Suspected sepsis in people aged 16 or over", "NG253-current-2026", "https://www.nice.org.uk/guidance/ng253/chapter/evaluating-risk", "nice_guidance", ["New altered mental state, acute functional deterioration, impaired immunity, recent procedures, respiratory change and reduced urine are risk-context features in suspected infection.", "The interview does not calculate NEWS2 or diagnose sepsis."]),
        ("source.nice.ng254.sepsis-under-16", "NICE", "Suspected sepsis in under 16s", "NG254-current-2026", "https://www.nice.org.uk/guidance/ng254/chapter/Evaluating-risk-level", "nice_guidance", ["Child or young-person warning context includes altered behaviour or mental state, acute functional decline, immune impairment, respiratory change and reduced urine.", "The caregiver interview records observable warning features without calculating a score or diagnosing sepsis."]),
        ("source.stom.mrcm.fatigue.20260714", "Infoclinic", "STOM SNOMED CT lookup and MRCM allowed attributes for fatigue", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/84229001", "terminology_server", ["STOM confirmed active Fatigue and Lack of energy concepts with Finding site and Severity allowed.", "MRCM constrains terminology representation only and does not create questions, diagnoses, priority or safety rules."]),
    ]
    verified_now = {"source.nhs.sleep-apnoea.2025", "source.nice.ng194.postnatal-care", "source.nhs.stroke-symptoms.2026", "source.nhs.carbon-monoxide-poisoning.2025", "source.nhs.vomiting-blood.2025", "source.nhs.fainting.2023", "source.nhs.chest-pain.2026", "source.nice.ng253.sepsis-adult", "source.nice.ng254.sepsis-under-16"}
    artifacts = []
    for sid, publisher, title, version, url, profile, assertions in defs:
        old_date = "2026-07-14"
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-18" if sid in verified_now else old_date, "monitor_result": "current_official_source_confirmed" if sid in verified_now else "not_due_existing_metadata_preserved", "assertions": assertions})
    research = {"id": "source-manifest.primary-care-fatigue-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.fatigue", "generated_clinical_knowledge", "knowledge/generated/systemic/fatigue/fatigue.json", True), ("source.mapping.fatigue", "terminology_mapping", "mappings/terminology/snomed-mrcm-fatigue.json", False), ("source.external.fatigue", "external_source_manifest", "sources/manifests/primary-care-fatigue-research.json", False), ("source.policy.fatigue", "runtime_policy", "policies/primary-care-fatigue-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-fatigue", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        key, level, condition = rule["id"].split("safety.")[1], rule["then"]["safety_level"], rule["when"]
        children = condition.get("all", [condition])
        state = {child["fact"]: {"value": child.get("equals", True)} for child in children}
        out[f"FATIGUE-{key.upper()}.json"] = {"id": f"FATIGUE-{key.upper()}", "simulation_language": "ko", "persona": {"age": 13 if key == "child-severe-warning" else 22 + index * 4}, "initial_statement": {"ko": "피로와 기력 저하로 진료 전 문진을 합니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 30, "forbidden_assertions": ["diagnosis.anemia", "diagnosis.diabetes", "diagnosis.depression", "diagnosis.mecfs", "diagnosis.cancer"]}, "provenance": provenance(SOURCES)}

    policy = completion(f)
    always = policy["required_facts"]["always"]
    base = policy["required_facts"]["routine"]
    branch_cases = policy["conditional_required_facts"][0]["cases"]
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}

    def routine(branch):
        values = {}
        for fid in dict.fromkeys([*always, *base, *branch_cases[branch]]):
            fact = by_id[fid]
            if fact["value_type"] == "boolean": value = False
            elif fact["value_type"] == "coded": value = fact.get("allowed_values", ["other_unclear"])[0]
            elif fact["value_type"] == "integer": value = 7
            elif fact["value_type"] == "quantity": value = "3 weeks"
            else: value = "특이사항 없음"
            values[fid] = {"value": value}
        values["symptom.fatigue.current"] = {"value": True}
        values["fatigue.primary_group"] = {"value": branch}
        values["symptom.fatigue.severity"] = {"value": "moderate"}
        if "pain.nrs_score" in values: values["pain.nrs_score"] = {"value": 2}
        return values

    specs = [
        ("SLEEP-SHIFT", "sleep_daytime", 38, "야간 교대근무 뒤 낮 졸림과 피로가 심합니다.", {"sleep.hours_per_night": {"value": 5}, "fatigue.daytime_sleepiness_naps_unintentional_sleep_and_driving_risk": {"value": "퇴근 운전 중 졸려 운전을 피하고 있음"}}),
        ("POST-EXERTIONAL", "post_exertional", 35, "가벼운 활동 다음 날 피로와 집중 저하가 심해집니다.", {"symptom.post_exertional_malaise": {"value": True}, "symptom.post_exertional_delayed_or_prolonged": {"value": True}, "symptom.cognitive_difficulty": {"value": True}}),
        ("MOOD-STRESS", "mood_stress", 47, "가족 돌봄과 스트레스 뒤 피로가 계속됩니다.", {"mental_health.low_mood": {"value": True}, "fatigue.anxiety_stress_bereavement_trauma_loneliness_and_support": {"value": "부모 돌봄 부담, 배우자 지원 있음"}}),
        ("SYSTEMIC-WEIGHT", "systemic_weight_infection", 62, "피로와 식욕 저하, 체중 감소가 있습니다.", {"symptom.unintentional_weight_loss": {"value": True}, "symptom.appetite_loss": {"value": True}, "patient.age_40_or_older": {"value": True}}),
        ("PREGNANCY-POSTPARTUM", "pregnancy_postpartum", 32, "출산 후 피로가 심해 진료 전에 정리합니다.", {"fatigue.pregnancy_possible_lmp_gestation_postpartum_and_lactation": {"value": "출산 6주, 수유 중"}, "fatigue.obstetric_history_delivery_bleeding_hypertension_infection_and_complications": {"value": "1회 질식분만, 알려진 합병증 없음"}}),
        ("MEDICATION-POLYPHARMACY", "medicine_substance", 74, "약이 여러 개이고 최근 더 피곤해졌습니다.", {"medication.possible_fatigue_contributor": {"value": True}, "fatigue.current_medicines_dose_schedule_adherence_changes_supplements_and_allergies": {"value": "최근 복용약 1개 증량, 목록은 처방전에서 확인 필요"}}),
        ("CHILD-PROXY", "child_adolescent", 12, "아이가 쉽게 지쳐 보호자가 관찰 내용을 답합니다.", {"fatigue.child_age_growth_school_play_feeding_sleep_and_proxy_observation": {"value": "12세, 최근 결석 2일, 식사와 수면은 유지"}, "fatigue.information_source_proxy_reliability_and_conflict": {"value": "보호자 관찰, 아이 본인 확인 필요"}}),
        ("MULTI-RFE-DIZZINESS", "other_unclear", 55, "피로 외에 반복되는 어지럼도 따로 문진하고 싶습니다.", {"fatigue.patient_concern_goal_and_additional_comment": {"value": "반복 어지럼을 별도 RFE로 전달 요청"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine(branch); state.update(overrides)
        out[f"FATIGUE-{key}.json"] = {"id": f"FATIGUE-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": state, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 95, "forbidden_assertions": ["diagnosis.anemia", "diagnosis.diabetes", "diagnosis.depression", "diagnosis.mecfs", "diagnosis.cancer"]}, "provenance": provenance(SOURCES)}
    absent = routine("other_unclear")
    missing = "fatigue.previous_examination_labs_imaging_sleep_test_dates_results_and_source"
    absent.pop(missing)
    out["FATIGUE-REMOTE-DATA-ABSENT.json"] = {"id": "FATIGUE-REMOTE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 81}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "보호자가 전화로 고령자의 피로를 설명하며 이전 검사자료는 없습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {missing: "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 95, "forbidden_assertions": ["diagnosis.anemia", "diagnosis.cancer"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Fatigue or Lack of Energy", intents=[("intent.characterize_symptom", "Characterize Onset Course Quality Severity Function and Recovery"), ("intent.screen_red_flags", "Screen Neurologic Cardiopulmonary Bleeding Infection Mental Health Toxic and Life Stage Warning Features"), ("intent.differentiate_common_causes", "Describe Sleep Activity Mood Systemic Metabolic Reproductive Medicine and Exposure Context"), ("intent.risk_assessment", "Assess History Medicines Tests Treatment Source Reliability and Patient Goals")])
    primary, research = source_docs()
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": "84229001", "display": "Fatigue (finding)", "concept_active": True}, {"code": "248274002", "display": "Lack of energy (finding)", "concept_active": True}], "verified_attribute_ids": ["363698007", "246112005"], "validation": {"method": "build_time_live_mrcm_summary", "checked_at": "2026-07-14T00:00:00Z", "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "fatigue_semantics": {"diagnosis_inferred": False, "mecfs_diagnosed": False, "depression_diagnosed": False, "anemia_diagnosed": False, "diabetes_diagnosed": False, "cancer_diagnosed": False, "test_selected_or_ordered": False, "runtime_terminology_query_required": False}, "provenance": provenance(["source.stom.mrcm.fatigue.20260714"])}
    docs = [("knowledge/base/primary-care-fatigue.json", graph), ("rules/base/primary-care-fatigue.json", rules), ("knowledge/generated/systemic/fatigue/fatigue.json", f), ("mappings/terminology/snomed-mrcm-fatigue.json", mapping), ("sources/manifests/primary-care-fatigue.json", primary), ("sources/manifests/primary-care-fatigue-research.json", research), ("policies/primary-care-fatigue-completion.json", completion(f))]
    for path, document in docs: write_json(path, document)
    for name, case in cases(f).items(): write_json("simulation/patients/systemic/fatigue/" + name, case)


if __name__ == "__main__":
    main()
