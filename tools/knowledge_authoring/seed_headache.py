#!/usr/bin/env python3
"""Rebuild unreviewed headache knowledge for professional pre-visit handoff."""
from profile_support import *

P, RFE = "headache", "rfe.headache"
M, SN = "mapping.snomed-mrcm.headache", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-18T00:00:00Z"
SOURCES = [
    "source.nice.cg150.headache.2025",
    "source.nice.ng240.meningitis.2024",
    "source.nice.ng127.child-headache.2023",
    "source.nice.ng133.pregnancy-headache.2019",
    "source.nhs.headaches.2026",
    "source.stom.mrcm.headache.20260714",
]
G = {key: f"group.headache.{key}" for key in (
    "routing", "safety", "course", "pain", "associated", "neurological",
    "eye_autonomic", "systemic", "trigger", "medicine", "reproductive",
    "child", "history", "handoff",
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
    branches = [
        "sudden_or_acute_new", "recurrent_migraine_like", "pressure_or_tension_like",
        "unilateral_autonomic", "infection_or_systemic", "medicine_or_overuse",
        "pregnancy_or_postpartum", "child_or_proxy", "other_unclear",
    ]
    e = [
        Q("symptom.headache.current", "Current Headache", "boolean", "current", "지금도 머리·얼굴·목 위쪽의 통증이나 두통이 있나요?", 330, "routing", C, terminology_binding={"system": SN, "code": "25064002"}),
        Q("headache.primary_group", "Primary Headache Context", "coded", "primary-group", "가장 가까운 상황은 갑자기 생긴 새 두통, 반복되는 편두통 같은 양상, 압박·긴장 양상, 한쪽 눈·코 증상 동반, 감염·전신증상, 약물·진통제 관련, 임신·산후, 소아·보호자 관찰, 또는 불분명 중 무엇인가요?", 329, "routing", C + D, allowed_values=branches),
        Q("symptom.duration", "Headache Duration", "quantity", "duration", "두통은 언제부터 시작했고 전체적으로 얼마나 지속됐나요?", 220, "course", C, reuse_existing=True),
        Q("headache.onset_date_time_place_activity_and_speed", "Exact Onset Circumstances", "string", "onset", "처음 시작한 날짜·시간·장소와 당시 활동, 몇 초·분·시간에 걸쳐 심해졌는지 알려주세요.", 219, "course", C),
        Q("headache.first_worst_new_or_changed_from_usual", "First Worst New or Changed Headache", "string", "baseline-change", "처음 겪는 두통인지, 평생 가장 심한 두통인지, 평소 두통과 비교해 새롭거나 달라진 점이 있는지 알려주세요.", 218, "course", C + R),
        Q("symptom.headache.new_onset", "New-onset Headache", "boolean", "new-onset", "이번 두통이 처음 생겼거나 평소와 뚜렷하게 다른 새 두통인가요?", 304, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("headache.continuous_episodic_frequency_duration_and_trend", "Episode Pattern and Trend", "string", "pattern", "계속되는지 발작처럼 반복되는지, 한 번 지속시간·하루/주/월 횟수와 최근 빈도·강도 변화를 알려주세요.", 217, "course", C),
        Q("symptom.headache.location", "Headache Location", "string", "location", "통증이 있는 머리·얼굴·목 위쪽의 정확한 부위를 알려주세요.", 216, "pain", C, terminology_binding={"system": SN, "focus_code": "25064002", "attribute_code": "363698007"}, mrcm_ref=M),
        Q("headache.side_site_radiation_and_laterality", "Site Side and Radiation", "string", "site-detail", "왼쪽·오른쪽·양쪽 중 어디인지, 눈 주위·관자·뒤통수·얼굴·목 등 시작 부위와 퍼지는 방향을 알려주세요.", 215, "pain", C),
        Q("symptom.headache.quality", "Headache Quality", "coded", "quality", "욱신거림, 조이거나 압박함, 찌름·화끈거림, 묵직함 중 어디에 가깝나요? 보기와 다르면 본인의 표현으로 답해도 됩니다.", 214, "pain", C, allowed_values=["pulsating", "pressing_tightening", "sharp_burning", "dull_heavy", "other"]),
        Q("headache.current_nrs_peak_nrs_and_peak_time", "Current and Peak Pain Context", "string", "nrs-context", "현재 통증 점수와 가장 심했던 점수·시각이 다르면 함께 알려주세요.", 212, "pain", C),
        Q("symptom.headache.frequency_days_per_month", "Headache Days per Month", "integer", "monthly-frequency", "최근 한 달 중 두통이 있었던 날은 며칠인가요? 숫자로 알려주세요.", 211, "course", C, reuse_existing=True),
        Q("headache.activity_sleep_work_school_selfcare_and_driving_impact", "Functional and Safety Impact", "string", "function", "두통 때문에 일상활동·수면·일·학업·가사·돌봄·운전이 얼마나 줄었거나 중단됐나요?", 210, "handoff", C + R),
        Q("headache.patient_words_and_between_episode_baseline", "Patient Description and Baseline", "string", "patient-words", "본인의 말로 두통을 표현하고, 두통이 없을 때는 평소 상태로 완전히 돌아오는지 알려주세요.", 209, "handoff", C),

        Q("symptom.headache.maximum_within_5_minutes", "Maximum Intensity within Five Minutes", "boolean", "sudden-peak", "두통이 시작된 뒤 5분 안에 가장 심한 정도에 도달했나요?", 327, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.neurological_deficit", "New Focal Neurological Deficit", "boolean", "neuro-deficit", "새로 한쪽 얼굴·팔·다리 힘 빠짐/감각 저하, 말 어눌함, 삼킴 곤란이 있나요?", 326, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("headache.fever_neck_stiffness_altered_combination", "Fever Neck Stiffness and Altered Consciousness Combination", "boolean", "meningitis-combination", "두통과 함께 발열·목 경직·새로운 혼란 또는 의식 저하가 동시에 있나요?", 325, "safety", S, safety_relevant=True),
        Q("symptom.altered_consciousness_or_cognition", "Altered Consciousness or Cognition", "boolean", "altered-cognition", "새로 혼란스럽거나 성격·기억·판단이 달라졌거나 의식이 흐려진 적이 있나요?", 324, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("headache.current_unconscious_or_difficult_to_wake", "Current Unconsciousness or Difficult to Wake", "boolean", "ongoing-consciousness", "현재 의식이 없거나 깨우기 어렵고 정상적으로 반응하지 못하나요?", 324, "safety", S, safety_relevant=True),
        Q("symptom.fever", "Fever", "boolean", "fever", "발열이나 오한이 있나요?", 323, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.neck_stiffness", "Neck Stiffness", "boolean", "neck-stiffness", "고개를 숙이기 어려울 정도로 목이 뻣뻣하거나 심하게 아픈가요?", 322, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("headache.non_blanching_rash", "Non-blanching Rash", "boolean", "non-blanching-rash", "발열과 함께 유리컵으로 눌러도 사라지지 않는 붉거나 보라색 발진이 있나요?", 321, "safety", S, safety_relevant=True),
        Q("history.recent_head_trauma", "Recent Head Trauma", "boolean", "recent-trauma", "최근 3개월 안에 머리를 부딪치거나 다친 일이 있나요?", 320, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("headache.severe_head_injury_warning", "Severe Head Injury Warning", "boolean", "head-injury-warning", "머리를 다친 뒤 반복 구토·경련·한쪽 힘 빠짐·점점 심한 졸림·귀나 코의 맑은 액체가 있나요?", 319, "safety", S, safety_relevant=True),
        Q("symptom.painful_red_eye", "Painful Red Eye", "boolean", "painful-red-eye", "두통과 함께 한쪽 눈이 심하게 아프고 빨갛나요?", 318, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.visual_disturbance", "Visual Disturbance", "boolean", "visual-disturbance", "시야 흐림·무지개 테·겹쳐 보임·번쩍임·시야 일부 소실이 있나요?", 317, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("headache.sudden_one_eye_vision_loss", "Sudden Monocular Vision Loss", "boolean", "one-eye-loss", "한쪽 눈의 시력이 갑자기 떨어지거나 보이지 않게 됐나요?", 316, "safety", S, safety_relevant=True),
        Q("symptom.headache.worsening", "Progressively Worsening Headache", "boolean", "worsening", "두통이 계속 또는 빠르게 더 심해지고 있나요?", 315, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.unexplained_vomiting", "Unexplained Vomiting", "boolean", "unexplained-vomiting", "장염·임신 등 다른 이유로 설명되지 않는 구토가 있나요?", 314, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("patient.immunocompromised", "Immunocompromised State", "boolean", "immunocompromised", "항암치료·장기이식·고용량 면역억제제 등으로 면역이 크게 저하된 상태인가요?", 313, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("history.malignancy", "Malignancy History", "boolean", "malignancy", "암 진단이나 치료 병력이 있나요?", 312, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.headache.cough_or_valsalva_trigger", "Cough Valsalva or Sneeze Trigger", "boolean", "cough-trigger", "기침·재채기·힘주기·몸을 숙일 때 두통이 새로 생기거나 심해지나요?", 311, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.headache.exercise_trigger", "Exercise Trigger", "boolean", "exercise-trigger", "운동이나 힘든 활동 중 두통이 새로 생기거나 심해지나요?", 310, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.headache.postural", "Postural Headache", "boolean", "postural", "눕거나 일어서는 자세에 따라 두통이 뚜렷하게 달라지나요?", 309, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("headache.jaw_claudication_scalp_tenderness_or_new_vision_warning", "Jaw Scalp or Vision Warning", "boolean", "arteritis-warning", "씹을 때 턱이 아프거나 쉽게 피로하고, 두피가 아프거나 새 시력 변화가 있나요?", 308, "safety", S, safety_relevant=True),
        Q("headache.pregnancy_postpartum_severe_warning", "Pregnancy or Postpartum Severe Warning", "boolean", "pregnancy-warning", "임신 중이거나 출산 후라면 심한 두통과 함께 시야 문제·명치/갈비뼈 아래 심한 통증·구토·얼굴/손/발의 갑작스러운 붓기 중 하나가 있나요?", 307, "safety", S, safety_relevant=True),
        Q("headache.child_under12_warning", "Child under Twelve Headache Warning", "boolean", "child-warning", "12세 미만이라면 밤에 깨는/아침부터 있는/점점 심해지는 두통, 구토·휘청거림·축 처짐·의식 변화, 최근 5일 내 머리 외상 중 하나가 있나요?", 306, "safety", S, safety_relevant=True),
        Q("headache.poisoning_or_carbon_monoxide_concern", "Poisoning or Carbon Monoxide Concern", "boolean", "poisoning-warning", "약물 과량·화학물질·밀폐공간 난방기 노출 또는 함께 있던 사람들의 두통·어지럼·구역이 있나요?", 305, "safety", S, safety_relevant=True),

        Q("symptom.nausea_or_vomiting", "Nausea or Vomiting", "boolean", "nausea", "두통과 함께 메스꺼움이나 구토가 있나요?", 175, "associated", D, reuse_existing=True),
        Q("symptom.light_sensitivity", "Light Sensitivity", "boolean", "photophobia", "평소보다 빛이 불편하거나 어두운 곳을 찾게 되나요?", 174, "associated", D, reuse_existing=True),
        Q("symptom.sound_sensitivity", "Sound Sensitivity", "boolean", "phonophobia", "평소보다 소리가 불편한가요?", 173, "associated", D, reuse_existing=True),
        Q("symptom.aura_visual", "Visual Aura-like Symptom", "boolean", "visual-aura", "두통 전후 번쩍임·지그재그·점·시야 일부 가림이 있었나요?", 172, "neurological", D, reuse_existing=True),
        Q("symptom.aura_sensory", "Sensory Aura-like Symptom", "boolean", "sensory-aura", "두통 전후 저림·감각 이상이 서서히 퍼진 적이 있나요?", 171, "neurological", D, reuse_existing=True),
        Q("symptom.aura_speech", "Speech Aura-like Symptom", "boolean", "speech-aura", "두통 전후 말이 잘 나오지 않거나 말하기가 달라진 적이 있나요?", 170, "neurological", D, reuse_existing=True),
        Q("headache.aura_onset_progression_sequence_duration_reversibility_and_side", "Neurological Symptom Time Course", "string", "aura-detail", "시각·감각·말 증상이 있다면 갑자기/서서히 시작했는지, 순서·지속시간·좌우와 완전 회복 여부를 알려주세요.", 169, "neurological", D + R),
        Q("headache.double_vision_balance_motor_or_one_eye_symptom_relation", "Atypical Neurological Feature Detail", "string", "neuro-detail", "복시·균형 이상·힘 빠짐·한쪽 눈에만 생긴 시각 증상이 두통 전후 언제 나타났는지 알려주세요.", 168, "neurological", D + R),
        Q("headache.same_side_eye_nose_lid_sweat_pupil_features", "Same-side Autonomic Features", "string", "autonomic", "두통과 같은 쪽의 눈물·충혈·눈꺼풀 붓기/처짐, 코막힘·콧물, 얼굴 땀이나 동공 변화가 있나요?", 167, "eye_autonomic", D),
        Q("headache.restlessness_agitation_or_need_to_lie_still", "Behaviour during Headache", "coded", "behaviour", "두통 때 가만히 눕고 싶은지, 안절부절못하고 움직이게 되는지, 큰 차이가 없는지 알려주세요.", 166, "associated", D, allowed_values=["prefer_stillness", "restless_agitated", "no_clear_change"]),
        Q("headache.neck_jaw_scalp_sinus_dental_ear_features", "Head Neck Face and Ear Context", "string", "regional-associated", "목·턱·두피·코/부비동·치아·귀 통증이나 증상이 두통과 함께 있는지 알려주세요.", 165, "associated", D),
        Q("headache.menstrual_cycle_relation_and_pattern", "Menstrual Relationship", "string", "menstrual", "해당되는 경우 두통이 월경 시작 전후에 반복되는지와 주기 관계를 알려주세요.", 164, "reproductive", D),
        Q("headache.infection_fever_rash_sick_contact_and_recent_illness_detail", "Infection and Exposure Context", "string", "infection", "최근 감염·발열·발진·아픈 사람 접촉과 두통 시작의 순서를 알려주세요.", 163, "systemic", D),
        Q("headache.weight_appetite_night_sweat_and_systemic_change", "Systemic Change", "string", "systemic-change", "의도하지 않은 체중 감소·식욕 저하·야간발한·전신 상태 변화가 있나요?", 162, "systemic", D + R),
        Q("headache.sleep_hydration_meals_stress_screen_and_trigger_response", "Common Precipitants and Relief", "string", "triggers", "수면·수분·식사·스트레스·화면·날씨·냄새·활동 중 유발하거나 악화하는 것과 휴식 등 완화 요인을 알려주세요.", 161, "trigger", D),

        Q("medication.acute_headache_days_per_month", "Acute Headache Medicine Days per Month", "integer", "acute-med-days", "최근 3개월 동안 진통제·편두통 급성약을 한 달 평균 며칠 사용했나요? 숫자로 알려주세요.", 155, "medicine", D + R, reuse_existing=True),
        Q("headache.acute_medicine_name_dose_route_time_frequency_and_response", "Acute Medicine Detail", "string", "acute-medicine", "두통 때 쓴 처방약·일반약의 이름·용량·복용 시각·월 사용일수와 효과·부작용을 알려주세요.", 154, "medicine", R),
        Q("headache.preventive_medicine_adherence_change_response_and_adverse_effect", "Preventive Medicine Detail", "string", "preventive-medicine", "예방 목적으로 쓰는 약이 있다면 이름·용량·복용 규칙·빠뜨림·최근 변경·효과·부작용을 알려주세요.", 153, "medicine", R),
        Q("headache.allergy_otc_supplement_hormone_and_contraception", "Allergy OTC Supplement and Hormone Context", "string", "allergy-hormone", "약물 알레르기, 일반약·한약·영양제, 호르몬 치료·피임약 사용과 최근 변경을 알려주세요.", 152, "medicine", R),
        Q("headache.caffeine_alcohol_nicotine_substance_and_withdrawal", "Substance and Withdrawal Context", "string", "substance", "카페인·술·담배/전자담배·기타 물질의 양·빈도와 최근 급격한 중단 또는 증가를 알려주세요.", 151, "medicine", D + R),
        Q("headache.occupation_shift_heat_noise_chemical_and_co_exposure", "Occupational and Environmental Exposure", "string", "occupation", "직업·교대근무와 더위·소음·용제·화학물질·연소가스 노출, 함께 증상이 생긴 사람이 있는지 알려주세요.", 150, "medicine", R),

        Q("headache.pregnancy_possible_lmp_gestation_postpartum_and_lactation", "Pregnancy and Postpartum Context", "string", "pregnancy-context", "해당되는 경우 임신 가능성, 마지막 월경일·임신 주수, 출산일·산후 기간과 수유 여부를 알려주세요.", 145, "reproductive", R),
        Q("headache.obstetric_history_parity_outcomes_hypertension_and_complications", "Professional Obstetric History", "string", "obstetric-history", "임신·출산 횟수와 결과, 임신성 고혈압/전자간증·출혈·혈전 등 과거 및 현재 합병증을 알려주세요.", 144, "reproductive", R),
        Q("headache.pregnancy_postpartum_bp_value_time_device_and_upper_abdominal_edema", "Pregnancy Postpartum Measurements and Symptoms", "string", "pregnancy-detail", "임신·산후라면 최근 혈압 수치·측정 시각/기기, 명치나 갈비뼈 아래 통증·구토·갑작스러운 붓기를 알려주세요.", 143, "reproductive", R),
        Q("headache.child_age_development_growth_and_proxy_observation", "Child Development and Proxy Context", "string", "child-context", "소아라면 나이·발달·성장·평소 상태와 본인/보호자 중 누가 관찰하고 답하는지 알려주세요.", 140, "child", R),
        Q("headache.child_night_morning_school_play_vomiting_balance_and_eye_change", "Child Headache Functional Detail", "string", "child-detail", "밤에 깨거나 아침부터 아픈지, 학교·놀이·식사 변화, 구토·휘청거림·눈 위치나 시선 변화가 있는지 알려주세요.", 139, "child", C + R),

        Q("headache.prior_headache_pattern_diagnosis_ed_visit_admission_and_change", "Prior Headache and Acute Care History", "string", "prior-history", "이전 비슷한 두통의 양상·진단, 응급실 방문·입원 여부와 이번에 달라진 점을 알려주세요.", 135, "history", R),
        Q("headache.neurologic_eye_ent_sinus_dental_sleep_and_bp_history", "Relevant Medical History", "string", "medical-history", "뇌·신경·눈·귀코목·부비동·치과·수면·고혈압 관련 진단과 평소 상태를 알려주세요.", 134, "history", R),
        Q("headache.surgery_procedure_infection_trauma_cancer_and_immunity_history", "Surgical Procedure and Risk History", "string", "procedure-history", "최근 수술·마취·척추/경막 시술·감염·머리/목 외상, 암·면역저하 병력과 시점을 알려주세요.", 133, "history", R),
        Q("headache.family_headache_aneurysm_stroke_clotting_and_early_death", "Family Neurological and Vascular History", "string", "family-history", "가족의 반복 두통·뇌동맥류·뇌출혈/뇌졸중·혈전질환과 젊은 나이의 원인불명 사망을 알려주세요.", 132, "history", R),
        Q("headache.prior_bp_neurologic_fundus_visual_exam_and_source", "Prior Examination and Measurements", "string", "prior-exam", "이전에 측정한 혈압과 신경학적·안저·시력/시야 검사의 날짜·결과·정보 출처를 알려주세요.", 131, "history", R),
        Q("headache.prior_labs_imaging_lumbar_puncture_and_source", "Prior Tests", "string", "prior-tests", "관련 혈액검사·CT/MRI·기타 검사 날짜·결과와 직접 본 자료인지 들은 내용인지 알려주세요.", 130, "history", R),
        Q("headache.prior_nonmedicine_treatment_response_and_adverse_effect", "Previous Non-medicine Management", "string", "prior-treatment", "휴식·수분·수면 조절·물리치료 등 이전에 시도한 방법과 효과·악화·부작용을 알려주세요.", 129, "history", R),
        Q("headache.diary_frequency_duration_severity_trigger_medicine_and_menses", "Headache Diary Availability", "string", "diary", "두통 일지가 있다면 날짜·빈도·지속시간·NRS·동반증상·유발요인·복용약·월경 관계를 알려주세요.", 128, "history", R),
        Q("headache.information_source_proxy_reliability_and_conflict", "Information Source Reliability and Conflict", "string", "source", "본인·보호자 중 누가 답하는지, 기억이 불확실하거나 기록·다른 사람 설명과 충돌하는 내용이 있는지 알려주세요.", 127, "handoff", R),
        Q("headache.patient_concern_goal_expectation_and_additional_comment", "Patient Concern Goal and Additional Comment", "string", "goal", "가장 걱정되는 점, 진료에서 확인하고 싶은 점과 질문에 없던 의견을 알려주세요.", 126, "handoff", R),
    ]
    rules = [
        safety_rule(P, "ongoing-consciousness", {"fact": "headache.current_unconscious_or_difficult_to_wake", "equals": True}, "emergency", 1000),
        safety_rule(P, "sudden-peak", {"fact": "symptom.headache.maximum_within_5_minutes", "equals": True}, "emergency", 1000),
        safety_rule(P, "neurological-deficit", {"fact": "symptom.neurological_deficit", "equals": True}, "emergency", 1000),
        safety_rule(P, "meningitis-combination", {"fact": "headache.fever_neck_stiffness_altered_combination", "equals": True}, "emergency", 1000),
        safety_rule(P, "altered-consciousness", {"fact": "symptom.altered_consciousness_or_cognition", "equals": True}, "emergency", 1000),
        safety_rule(P, "fever-non-blanching-rash", {"all": [{"fact": "symptom.fever", "equals": True}, {"fact": "headache.non_blanching_rash", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "severe-head-injury", {"fact": "headache.severe_head_injury_warning", "equals": True}, "emergency", 1000),
        safety_rule(P, "poisoning-carbon-monoxide", {"fact": "headache.poisoning_or_carbon_monoxide_concern", "equals": True}, "emergency", 1000),
        safety_rule(P, "painful-red-eye-vision", {"all": [{"fact": "symptom.painful_red_eye", "equals": True}, {"fact": "symptom.visual_disturbance", "equals": True}]}, "urgent", 900),
        safety_rule(P, "sudden-one-eye-vision-loss", {"fact": "headache.sudden_one_eye_vision_loss", "equals": True}, "urgent", 900),
        safety_rule(P, "worsening-fever", {"all": [{"fact": "symptom.headache.worsening", "equals": True}, {"fact": "symptom.fever", "equals": True}]}, "urgent", 900),
        safety_rule(P, "recent-head-trauma", {"fact": "history.recent_head_trauma", "equals": True}, "urgent", 900),
        safety_rule(P, "new-immunocompromised", {"all": [{"fact": "symptom.headache.new_onset", "equals": True}, {"fact": "patient.immunocompromised", "equals": True}]}, "urgent", 900),
        safety_rule(P, "new-malignancy-history", {"all": [{"fact": "symptom.headache.new_onset", "equals": True}, {"fact": "history.malignancy", "equals": True}]}, "urgent", 900),
        safety_rule(P, "new-unexplained-vomiting", {"all": [{"fact": "symptom.headache.new_onset", "equals": True}, {"fact": "symptom.unexplained_vomiting", "equals": True}]}, "urgent", 900),
        safety_rule(P, "cough-valsalva-trigger", {"fact": "symptom.headache.cough_or_valsalva_trigger", "equals": True}, "urgent", 900),
        safety_rule(P, "exercise-trigger", {"fact": "symptom.headache.exercise_trigger", "equals": True}, "urgent", 900),
        safety_rule(P, "postural-headache", {"fact": "symptom.headache.postural", "equals": True}, "urgent", 900),
        safety_rule(P, "substantial-worsening", {"fact": "symptom.headache.worsening", "equals": True}, "urgent", 900),
        safety_rule(P, "jaw-scalp-vision-warning", {"fact": "headache.jaw_claudication_scalp_tenderness_or_new_vision_warning", "equals": True}, "urgent", 900),
        safety_rule(P, "pregnancy-postpartum-warning", {"fact": "headache.pregnancy_postpartum_severe_warning", "equals": True}, "urgent", 900),
        safety_rule(P, "child-under12-warning", {"fact": "headache.child_under12_warning", "equals": True}, "urgent", 900),
    ]
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-18", "next_monitor_at": "2026-07-19", "next_full_review_at": "2027-01-14"})
    return {
        "id": "knowledge.generated.neurological.headache", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-headache-research",
        "default_refresh": refresh,
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": e,
        "provenance": provenance(SOURCES),
    }


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="symptom.headache.current", question_budget=82, source_refs=SOURCES)
    p["required_facts"]["always"] = list(dict.fromkeys([*p["required_facts"]["always"], "pain.nrs_score"]))
    p["must_be_known_facts"] = ["pain.frequency", "pain.nrs_score"]
    p["required_facts"]["routine"] = [
        "headache.primary_group", "symptom.duration", "headache.onset_date_time_place_activity_and_speed",
        "headache.first_worst_new_or_changed_from_usual", "headache.continuous_episodic_frequency_duration_and_trend",
        "symptom.headache.location", "headache.side_site_radiation_and_laterality", "symptom.headache.quality",
        "headache.current_nrs_peak_nrs_and_peak_time", "symptom.headache.frequency_days_per_month",
        "headache.activity_sleep_work_school_selfcare_and_driving_impact", "headache.patient_words_and_between_episode_baseline",
        "headache.prior_headache_pattern_diagnosis_ed_visit_admission_and_change",
        "headache.neurologic_eye_ent_sinus_dental_sleep_and_bp_history",
        "headache.prior_bp_neurologic_fundus_visual_exam_and_source", "headache.prior_labs_imaging_lumbar_puncture_and_source",
        "headache.prior_nonmedicine_treatment_response_and_adverse_effect",
        "headache.information_source_proxy_reliability_and_conflict", "headache.patient_concern_goal_expectation_and_additional_comment",
    ]
    cases = {
        "sudden_or_acute_new": ["headache.aura_onset_progression_sequence_duration_reversibility_and_side", "headache.double_vision_balance_motor_or_one_eye_symptom_relation", "headache.infection_fever_rash_sick_contact_and_recent_illness_detail", "headache.surgery_procedure_infection_trauma_cancer_and_immunity_history"],
        "recurrent_migraine_like": ["symptom.nausea_or_vomiting", "symptom.light_sensitivity", "symptom.sound_sensitivity", "symptom.aura_visual", "symptom.aura_sensory", "symptom.aura_speech", "headache.aura_onset_progression_sequence_duration_reversibility_and_side", "headache.restlessness_agitation_or_need_to_lie_still", "headache.menstrual_cycle_relation_and_pattern", "headache.diary_frequency_duration_severity_trigger_medicine_and_menses"],
        "pressure_or_tension_like": ["headache.neck_jaw_scalp_sinus_dental_ear_features", "headache.sleep_hydration_meals_stress_screen_and_trigger_response", "headache.restlessness_agitation_or_need_to_lie_still"],
        "unilateral_autonomic": ["headache.same_side_eye_nose_lid_sweat_pupil_features", "headache.restlessness_agitation_or_need_to_lie_still", "headache.double_vision_balance_motor_or_one_eye_symptom_relation"],
        "infection_or_systemic": ["headache.infection_fever_rash_sick_contact_and_recent_illness_detail", "headache.weight_appetite_night_sweat_and_systemic_change", "headache.neck_jaw_scalp_sinus_dental_ear_features", "headache.surgery_procedure_infection_trauma_cancer_and_immunity_history"],
        "medicine_or_overuse": ["medication.acute_headache_days_per_month", "headache.acute_medicine_name_dose_route_time_frequency_and_response", "headache.preventive_medicine_adherence_change_response_and_adverse_effect", "headache.allergy_otc_supplement_hormone_and_contraception", "headache.caffeine_alcohol_nicotine_substance_and_withdrawal"],
        "pregnancy_or_postpartum": ["headache.pregnancy_possible_lmp_gestation_postpartum_and_lactation", "headache.obstetric_history_parity_outcomes_hypertension_and_complications", "headache.pregnancy_postpartum_bp_value_time_device_and_upper_abdominal_edema", "headache.allergy_otc_supplement_hormone_and_contraception"],
        "child_or_proxy": ["headache.child_age_development_growth_and_proxy_observation", "headache.child_night_morning_school_play_vomiting_balance_and_eye_change", "headache.information_source_proxy_reliability_and_conflict"],
        "other_unclear": ["headache.neck_jaw_scalp_sinus_dental_ear_features", "headache.sleep_hydration_meals_stress_screen_and_trigger_response", "headache.acute_medicine_name_dose_route_time_frequency_and_response", "headache.allergy_otc_supplement_hormone_and_contraception", "headache.caffeine_alcohol_nicotine_substance_and_withdrawal", "headache.occupation_shift_heat_noise_chemical_and_co_exposure", "headache.family_headache_aneurysm_stroke_clotting_and_early_death"],
    }
    p["conditional_required_facts"] = [{"selector_fact": "headache.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nice.cg150.headache.2025", "NICE", "Headaches in over 12s: diagnosis and management", "CG150-updated-2025-06-03", "https://www.nice.org.uk/guidance/cg150/chapter/recommendations", "nice_guidance", ["Assessment records sudden maximum intensity, neurological or consciousness change, trauma, cough/exercise/posture triggers, fever, eye and vision features, substantial change, immune status, malignancy and unexplained vomiting.", "A diary can preserve frequency, duration, severity, associated symptoms, medicines, precipitants and menstrual relationship; the interview does not assign a headache diagnosis."]),
        ("source.nice.ng240.meningitis.2024", "NICE", "Meningitis and meningococcal disease", "NG240-current-2026", "https://www.nice.org.uk/guidance/ng240/chapter/Recommendations", "nice_guidance", ["Headache with fever, neck stiffness and altered consciousness or cognition is a red-flag combination; a non-blanching rash is also a warning feature.", "The interview escalates reported features without diagnosing meningitis."]),
        ("source.nice.ng127.child-headache.2023", "NICE", "Suspected neurological conditions — headache in children under 12", "NG127-updated-2023-10-02", "https://www.nice.org.uk/guidance/ng127/chapter/Recommendations-for-children-aged-under-16", "nice_guidance", ["Under-12 same-day warning features include night waking, morning headache, progressive worsening, cough/sneeze/bending trigger, fever with meningism, vomiting, ataxia, altered consciousness or lethargy, recent head injury and eye-movement abnormality.", "The caregiver interview preserves age, proxy source, function and observed features without selecting a test."]),
        ("source.nice.ng133.pregnancy-headache.2019", "NICE", "Hypertension in pregnancy — severe headache warning symptoms", "NG133-amended-2019", "https://www.nice.org.uk/guidance/ng133/chapter/recommendations", "nice_guidance", ["During pregnancy, severe headache with visual problems, severe subcostal pain, vomiting or sudden face, hand or foot swelling needs immediate professional assessment.", "The interview records gestational or postpartum timing, obstetric history, symptoms and available blood pressure without diagnosing pre-eclampsia."]),
        ("source.nhs.headaches.2026", "NHS", "Headaches", "current-2026", "https://www.nhs.uk/symptoms/headaches/", "public_health_guidance", ["Sudden extremely painful headache, head injury, new weakness or speech change, vision loss, confusion or drowsiness are emergency warning features.", "Jaw pain on chewing, scalp tenderness and visual change are relevant urgent handoff features."]),
        ("source.stom.mrcm.headache.20260714", "Infoclinic", "STOM SNOMED CT lookup and MRCM allowed attributes for headache", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/25064002", "terminology_server", ["STOM confirmed the active Headache concept with Finding site and Severity permitted by the queried MRCM summary.", "MRCM constrains Build-Time terminology representation only and has no authority over clinical questions, priority or safety rules."]),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, assertions in defs:
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-18" if publisher == "NICE" else "2026-07-14", "monitor_result": "current_official_source_confirmed" if publisher == "NICE" else "not_due_existing_metadata_preserved", "assertions": assertions})
    research = {"id": "source-manifest.primary-care-headache-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.headache", "generated_clinical_knowledge", "knowledge/generated/neurological/headache/headache.json", True),
        ("source.mapping.headache", "terminology_mapping", "mappings/terminology/snomed-mrcm-headache.json", False),
        ("source.external.headache", "external_source_manifest", "sources/manifests/primary-care-headache-research.json", False),
        ("source.policy.headache", "runtime_policy", "policies/primary-care-headache-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-headache", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    forbidden = ["diagnosis.migraine", "diagnosis.cluster_headache", "diagnosis.meningitis", "diagnosis.subarachnoid_hemorrhage", "diagnosis.stroke", "diagnosis.glaucoma", "diagnosis.giant_cell_arteritis", "diagnosis.preeclampsia"]
    for index, rule in enumerate(f["safety_rules"]):
        key, level, condition = rule["id"].split("safety.")[1], rule["then"]["safety_level"], rule["when"]
        children = condition.get("all", [condition])
        state = {}
        for child in children:
            state[child["fact"]] = {"value": child.get("equals", "new_or_changed")}
        out[f"HEADACHE-{key.upper()}.json"] = {"id": f"HEADACHE-{key.upper()}", "simulation_language": "ko", "persona": {"age": 9 if key == "child-under12-warning" else 24 + index * 3}, "initial_statement": {"ko": "두통이 있어 진료 전 문진을 합니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 38, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}

    policy = completion(f)
    always, base, branches = policy["required_facts"]["always"], policy["required_facts"]["routine"], policy["conditional_required_facts"][0]["cases"]
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}

    def routine(branch):
        values = {}
        for fid in dict.fromkeys([*always, *base, *branches[branch]]):
            if fid in {"pain.frequency", "pain.nrs_score"}:
                values[fid] = {"value": "intermittent" if fid == "pain.frequency" else 4}
                continue
            fact = by_id[fid]
            if fact["value_type"] == "boolean": value = False
            elif fact["value_type"] == "coded": value = fact.get("allowed_values", ["other"])[0]
            elif fact["value_type"] == "integer": value = 4
            elif fact["value_type"] == "quantity": value = "2 weeks"
            else: value = "특이사항 없음"
            values[fid] = {"value": value}
        values["symptom.headache.current"] = {"value": True}
        values["headache.primary_group"] = {"value": branch}
        values["pain.nrs_score"] = {"value": 4}
        values["headache.first_worst_new_or_changed_from_usual"] = {"value": "no_change"}
        return values

    specs = [
        ("RECURRENT-AURA", "recurrent_migraine_like", 34, "반복되는 한쪽 두통과 빛 민감, 서서히 번지는 시각 증상을 정리합니다.", {"symptom.light_sensitivity": {"value": True}, "symptom.aura_visual": {"value": True}, "headache.aura_onset_progression_sequence_duration_reversibility_and_side": {"value": "10분에 걸쳐 퍼지고 30분 뒤 완전히 회복"}}),
        ("PRESSURE-WORK", "pressure_or_tension_like", 46, "업무 중 양쪽 머리를 조이는 두통이 반복됩니다.", {"symptom.headache.quality": {"value": "pressing_tightening"}, "headache.activity_sleep_work_school_selfcare_and_driving_impact": {"value": "업무 집중 저하, 운전 영향 없음"}}),
        ("AUTONOMIC", "unilateral_autonomic", 39, "한쪽 눈 주위 두통과 눈물·코막힘이 반복됩니다.", {"headache.same_side_eye_nose_lid_sweat_pupil_features": {"value": "오른쪽 눈물과 코막힘"}, "headache.restlessness_agitation_or_need_to_lie_still": {"value": "restless_agitated"}}),
        ("MEDICINE-DAYS", "medicine_or_overuse", 52, "진통제를 자주 사용하는 반복 두통을 진료 전에 정리합니다.", {"medication.acute_headache_days_per_month": {"value": 16}, "headache.acute_medicine_name_dose_route_time_frequency_and_response": {"value": "일반 진통제 제품명 확인 필요, 월 16일, 일시 호전"}}),
        ("PREGNANCY-ROUTINE", "pregnancy_or_postpartum", 31, "임신 중 평소와 비슷한 두통을 정리합니다.", {"headache.pregnancy_possible_lmp_gestation_postpartum_and_lactation": {"value": "임신 18주"}, "headache.obstetric_history_parity_outcomes_hypertension_and_complications": {"value": "G2P1, 과거 합병증 없음"}}),
        ("CHILD-PROXY", "child_or_proxy", 10, "보호자가 아이의 반복 두통을 관찰해 답합니다.", {"headache.child_age_development_growth_and_proxy_observation": {"value": "10세, 발달·성장 평소 수준, 보호자 관찰"}, "headache.information_source_proxy_reliability_and_conflict": {"value": "보호자 답변, 아이 본인 확인 필요"}}),
        ("MULTI-RFE-VISION", "other_unclear", 61, "두통 외에 시야 흐림도 별도 문진하고 싶습니다.", {"headache.patient_concern_goal_expectation_and_additional_comment": {"value": "시야 흐림을 별도 RFE로 전달 요청"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine(branch); state.update(overrides)
        out[f"HEADACHE-{key}.json"] = {"id": f"HEADACHE-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": state, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 100, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    absent = routine("other_unclear")
    missing = "headache.prior_labs_imaging_lumbar_puncture_and_source"
    absent.pop(missing)
    out["HEADACHE-REMOTE-DATA-ABSENT.json"] = {"id": "HEADACHE-REMOTE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 78}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "보호자가 고령자의 두통을 전화로 설명하며 이전 검사자료는 없습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {missing: "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 100, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Headache or Head Pain", intents=[("intent.characterize_symptom", "Characterize Headache Onset Course Site Quality NRS Pattern and Function"), ("intent.screen_red_flags", "Screen Neurologic Consciousness Infection Trauma Eye Systemic Pregnancy Child and Toxic Warning Features"), ("intent.differentiate_common_causes", "Describe Associated Neurological Autonomic Trigger Medicine Reproductive and Child Context"), ("intent.risk_assessment", "Assess History Medicines Prior Evaluation Treatment Source Reliability and Patient Goals")])
    primary, research = source_docs()
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concept": {"code": "25064002", "display": "Headache (finding)", "concept_active": True}, "checks": [{"attribute": {"code": "363698007", "display": "Finding site"}, "allowed": True}, {"attribute": {"code": "246112005", "display": "Severity"}, "allowed": True}], "validation": {"method": "build_time_live_mrcm_summary", "endpoint": "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/25064002", "checked_at": "2026-07-14T00:00:00Z", "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "headache_semantics": {"diagnosis_inferred": False, "migraine_diagnosed": False, "cluster_headache_diagnosed": False, "meningitis_diagnosed": False, "stroke_diagnosed": False, "glaucoma_diagnosed": False, "giant_cell_arteritis_diagnosed": False, "preeclampsia_diagnosed": False, "test_selected_or_ordered": False, "runtime_terminology_query_required": False}, "provenance": provenance(["source.stom.mrcm.headache.20260714"])}
    docs = [("knowledge/base/primary-care-headache.json", graph), ("rules/base/primary-care-headache.json", rules), ("knowledge/generated/neurological/headache/headache.json", f), ("mappings/terminology/snomed-mrcm-headache.json", mapping), ("sources/manifests/primary-care-headache.json", primary), ("sources/manifests/primary-care-headache-research.json", research), ("policies/primary-care-headache-completion.json", completion(f))]
    for path, document in docs: write_json(path, document)
    target = ROOT / "simulation/patients/neurological/headache"
    for old in target.glob("*.json"): old.unlink()
    for name, case in cases(f).items(): write_json("simulation/patients/neurological/headache/" + name, case)


if __name__ == "__main__":
    main()
