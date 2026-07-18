#!/usr/bin/env python3
"""Rebuild unreviewed dizziness and syncope knowledge for clinician handoff."""
from profile_support import *

P, RFE = "dizziness-syncope", "rfe.dizziness_syncope"
M, SN = "mapping.snomed-mrcm.dizziness-syncope", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-18T00:00:00Z"
SOURCES = [
    "source.nice.ng127.dizziness.2023", "source.nice.cg109.tloc.2023",
    "source.nhs.fainting.2023", "source.nhs.stroke-symptoms.2026",
    "source.nhs.head-injury.2025", "source.nhs.carbon-monoxide-poisoning.2025",
    "source.stom.mrcm.dizziness-syncope.20260714",
]
G = {key: f"group.dizziness_syncope.{key}" for key in (
    "routing", "safety", "course", "dizziness", "event", "recovery",
    "neurological", "hearing", "cardiovascular", "metabolic", "medicine",
    "reproductive", "child", "history", "handoff",
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
    branches = ["acute_continuous", "positional_head_movement", "postural_presyncope", "blackout_syncope", "hearing_or_headache", "medicine_metabolic", "child_proxy", "other_unclear"]
    e = [
        Q("symptom.dizziness.current", "Current Dizziness", "boolean", "current", "지금도 어지럼·빙빙 도는 느낌·쓰러질 듯함·균형 불안 중 하나가 있나요?", 320, "routing", C, terminology_binding={"system": SN, "code": "404640003"}),
        Q("symptom.syncope.occurred", "Transient Loss of Consciousness Occurred", "boolean", "syncope", "실제로 의식을 잃거나 주변 반응이 끊긴 적이 있었나요?", 319, "routing", C, terminology_binding={"system": SN, "code": "271594007"}),
        Q("dizziness_syncope.primary_group", "Primary Dizziness or Syncope Context", "coded", "primary-group", "가장 가까운 상황은 갑자기 계속되는 어지럼, 머리 위치에 따른 회전감, 일어설 때 쓰러질 듯함, 실제 실신, 청각·두통 동반, 약물·대사 관련, 소아 보호자 관찰, 또는 불분명 중 무엇인가요?", 318, "routing", C + D, allowed_values=branches),
        Q("symptom.duration", "Symptom Duration", "quantity", "duration", "첫 증상은 언제 시작했고 전체적으로 얼마나 지속됐나요?", 210, "course", C, reuse_existing=True),
        Q("dizziness_syncope.onset_date_time_place_activity_posture_and_speed", "Exact Onset Circumstances", "string", "onset", "처음 시작한 날짜·시간·장소, 당시 활동과 자세, 갑작스러웠는지 서서히였는지 알려주세요.", 209, "course", C),
        Q("dizziness_syncope.continuous_episodic_frequency_duration_and_trend", "Episode Pattern Frequency and Trend", "string", "pattern", "계속되는지 발작처럼 반복되는지, 횟수·한 번 지속시간·최근 빈도와 강도의 변화를 알려주세요.", 208, "course", C),
        Q("symptom.dizziness.presentation", "Patient-described Dizziness Type", "coded", "presentation", "빙빙 도는 회전감, 흔들리거나 균형이 안 맞음, 눈앞이 캄캄하며 쓰러질 듯함, 멍함 중 어디에 가깝나요?", 207, "dizziness", C, allowed_values=["vertigo", "imbalance", "presyncope", "nonspecific"]),
        Q("symptom.dizziness.severity", "Dizziness Severity", "coded", "severity", "현재 어지럼은 가벼움, 중간, 심함 중 어디에 가깝나요?", 206, "dizziness", C, allowed_values=["mild", "moderate", "severe"], terminology_binding={"system": SN, "focus_code": "404640003", "attribute_code": "246112005"}, mrcm_ref=M),
        Q("dizziness_syncope.patient_words_and_change_from_baseline", "Patient Description and Baseline Change", "string", "patient-words", "본인의 말로 어떤 느낌인지, 평소 균형·시력·청력·보행과 비교해 무엇이 달라졌는지 알려주세요.", 205, "dizziness", C),
        Q("dizziness_syncope.function_walking_selfcare_work_school_driving_and_falls", "Functional and Safety Impact", "string", "function", "걷기·씻기·식사·일·학업·운전이 얼마나 어려워졌고 넘어지거나 거의 넘어진 적이 있나요?", 204, "handoff", C + R),
        Q("dizziness_syncope.information_source_witness_reliability_video_and_conflict", "Information Source Witness and Reliability", "string", "source", "본인·보호자·목격자 중 누가 답하는지, 목격자 설명·영상·기록이 있는지, 기억이 불확실하거나 서로 다른 내용이 있는지 알려주세요.", 203, "handoff", R),
        Q("dizziness_syncope.patient_concern_goal_and_additional_comment", "Patient Concern Goal and Additional Comment", "string", "goal", "가장 걱정되는 점, 진료에서 확인하고 싶은 점과 질문에 없던 의견을 알려주세요.", 202, "handoff", R),

        Q("dizziness_syncope.current_unconscious_or_cannot_be_woken", "Current Unconsciousness or Cannot Be Woken", "boolean", "ongoing-unconscious", "현재 의식이 없거나 깨우기 어렵고 정상적으로 반응하지 못하나요?", 310, "safety", S, safety_relevant=True),
        Q("symptom.syncope.full_recovery", "Full Recovery after Event", "boolean", "full-recovery", "실신 뒤 의식·말·움직임이 평소 상태로 완전히 회복됐나요?", 309, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.dizziness.sudden_onset", "Sudden-onset Dizziness", "boolean", "sudden", "어지럼이 갑자기 시작했나요?", 308, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.neurological_deficit", "Focal Neurological Deficit", "boolean", "neuro-deficit", "새로 한쪽 얼굴·팔·다리 힘 빠짐/감각 저하, 말 어눌함, 복시, 삼킴 곤란이 있나요?", 307, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.new_gait_unsteadiness", "New Severe Gait Unsteadiness", "boolean", "gait-warning", "새로 혼자 서거나 걷기 어려울 정도로 중심을 못 잡나요?", 306, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.new_hearing_loss", "Sudden New Hearing Loss", "boolean", "hearing-warning", "갑자기 한쪽 또는 양쪽 청력이 뚜렷하게 떨어졌나요?", 305, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.nausea_or_vomiting", "Nausea or Vomiting", "boolean", "nausea-vomiting", "심한 메스꺼움이나 구토가 함께 있나요?", 304, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("dizziness_syncope.severe_chest_pain_or_breathlessness", "Severe Chest Pain or Breathlessness", "boolean", "severe-cardiorespiratory", "지금 심한 가슴통증·압박감 또는 말을 잇기 어려운 호흡곤란이 있나요?", 303, "safety", S, safety_relevant=True),
        Q("event.syncope.injury", "Injury during Event", "boolean", "injury", "쓰러지며 다친 곳이 있나요?", 302, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("dizziness_syncope.severe_head_injury_warning", "Severe Head Injury Warning", "boolean", "head-injury-warning", "머리를 다친 뒤 반복 구토·심한 두통·경련·한쪽 힘 빠짐·맑은 액체가 귀나 코에서 나옴이 있나요?", 301, "safety", S, safety_relevant=True),
        Q("dizziness_syncope.active_heavy_bleeding_or_black_stool", "Active Heavy Bleeding or Black Stool", "boolean", "bleeding-warning", "많은 출혈, 피를 토함, 검은 변·혈변이 있나요?", 300, "safety", S, safety_relevant=True),
        Q("dizziness_syncope.poisoning_overdose_or_carbon_monoxide_concern", "Poisoning Overdose or Carbon Monoxide Concern", "boolean", "poisoning-warning", "약물 과량·화학물질·밀폐공간 난방기 노출 또는 함께 있던 사람들의 두통·어지럼이 있나요?", 299, "safety", S, safety_relevant=True),
        Q("dizziness_syncope.pregnancy_postpartum_warning", "Pregnancy or Postpartum Warning", "boolean", "pregnancy-warning", "임신 중이거나 출산 후라면 많은 출혈·심한 복통·가슴통증·숨참·한쪽 다리 붓기·심한 두통이 있나요?", 298, "safety", S, safety_relevant=True),
        Q("dizziness_syncope.child_severe_warning", "Child Severe Warning Feature", "boolean", "child-warning", "소아라면 깨우기 어려움·경련·심한 호흡곤란·청색증·물을 못 마심·소변이 크게 줄었나요?", 297, "safety", S, safety_relevant=True),
        Q("symptom.chest_pain", "Chest Pain", "boolean", "chest-pain", "실신 전후 가슴통증이나 압박감이 있었나요?", 296, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("event.syncope.during_exertion", "Syncope during Exertion", "boolean", "during-exertion", "운동이나 힘든 활동을 하는 도중 의식을 잃었나요?", 295, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("event.syncope.while_supine", "Syncope while Supine", "boolean", "while-supine", "누워 있는 상태에서 의식을 잃었나요?", 294, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("family_history.sudden_cardiac_death_under_40", "Family Sudden Cardiac Death under 40", "boolean", "family-sudden-death", "가족 중 40세 이전 돌연사나 유전성 심장질환이 있나요?", 293, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("history.heart_failure", "Heart Failure History", "boolean", "heart-failure", "심부전 진단을 받은 적이 있나요?", 292, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.palpitations", "Palpitations", "boolean", "palpitations", "실신 직전 갑작스러운 두근거림이나 불규칙한 맥박 느낌이 있었나요?", 291, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("dizziness_syncope.unexplained_breathlessness_or_known_murmur_ecg_abnormality", "Breathlessness Murmur or ECG Abnormality", "boolean", "cardiac-warning", "새로운 원인 불명의 숨참, 심잡음, 또는 이전 심전도 이상을 들은 적이 있나요?", 290, "safety", S, safety_relevant=True),
        Q("event.syncope.lateral_tongue_bite", "Lateral Tongue Bite", "boolean", "lateral-tongue-bite", "실신 중 혀를 깨물었다면 혀 옆쪽이 다쳤나요?", 289, "safety", S, safety_relevant=True, reuse_existing=True),

        Q("symptom.dizziness.head_movement_trigger", "Head Movement Trigger", "boolean", "head-movement", "고개를 돌리거나 눕고 일어나거나 침대에서 돌아누울 때 짧게 빙빙 도나요?", 175, "dizziness", D, reuse_existing=True),
        Q("symptom.dizziness.postural_trigger", "Standing-related Trigger", "boolean", "postural-trigger", "누웠거나 앉았다 일어설 때 눈앞이 캄캄하고 어지러운가요?", 174, "dizziness", D, reuse_existing=True),
        Q("dizziness_syncope.position_head_movement_latency_duration_and_side", "Positional Trigger Detail", "string", "position-detail", "어떤 머리·몸 자세와 방향에서 몇 초 뒤 시작해 얼마나 지속되는지, 좌우 차이가 있는지 알려주세요.", 173, "dizziness", D),
        Q("dizziness_syncope.standing_heat_meal_exertion_cough_urination_pain_and_emotion_trigger", "Situational and Reflex Trigger Detail", "string", "trigger-detail", "오래 서기·더위·식사·운동·기침·배뇨·배변·통증·주사·공포와 관련이 있나요?", 172, "dizziness", D),
        Q("event.syncope.reflex_prodrome", "Warmth Sweating Nausea Prodrome", "boolean", "reflex-prodrome", "직전에 더워짐·식은땀·메스꺼움·시야 흐림 같은 경고가 있었나요?", 171, "event", D, reuse_existing=True),
        Q("event.syncope.no_prodrome", "No Prodrome", "boolean", "no-prodrome", "아무런 경고 없이 갑자기 의식을 잃었나요?", 170, "event", D, reuse_existing=True),
        Q("dizziness_syncope.visual_nystagmus_diplopia_photophobia_and_aura", "Visual and Eye Movement Features", "string", "visual", "눈이 떨린다는 관찰, 복시·시야 소실·빛 민감·번쩍임 같은 시각 증상이 있나요?", 169, "neurological", D),
        Q("dizziness_syncope.headache_neck_pain_migraine_history_and_relation", "Headache Neck Pain and Migraine Context", "string", "headache", "두통·목 통증의 시작과 어지럼의 관계, 반복 편두통 병력과 빛·소리 민감성이 있나요?", 168, "neurological", D),
        Q("symptom.hearing_change_or_tinnitus", "Hearing Change or Tinnitus", "boolean", "hearing-change", "청력 변화·이명·귀 먹먹함이 함께 있나요?", 167, "hearing", D, reuse_existing=True),
        Q("dizziness_syncope.hearing_side_onset_tinnitus_fullness_pain_and_discharge", "Hearing and Ear Detail", "string", "hearing-detail", "청력 변화의 좌우·시작 시점과 이명·귀 먹먹함·통증·분비물을 알려주세요.", 166, "hearing", D),

        Q("dizziness_syncope.event_count_frequency_previous_and_last_event", "Event Count and Recurrence", "string", "event-count", "의식소실이나 거의 쓰러질 뻔한 일이 총 몇 번이었고, 이전과 가장 최근 사건은 언제였나요?", 163, "event", C),
        Q("dizziness_syncope.event_before_symptoms_sequence_and_last_memory", "Pre-event Sequence and Last Memory", "string", "before-event", "직전 증상의 순서, 마지막으로 기억나는 것과 의식을 잃기 전까지의 시간을 알려주세요.", 162, "event", C),
        Q("dizziness_syncope.witness_appearance_colour_eyes_breathing_and_responsiveness", "Witnessed Appearance and Responsiveness", "string", "witness", "목격자가 본 얼굴색·눈이 열린/감긴 상태·호흡·소리·부름이나 자극에 대한 반응을 알려주세요.", 161, "event", C),
        Q("event.syncope.limb_jerking", "Limb Jerking", "boolean", "jerking", "몸이 뻣뻣해지거나 팔다리를 떤 움직임이 있었나요?", 160, "event", C, reuse_existing=True),
        Q("dizziness_syncope.movement_onset_body_part_symmetry_duration_and_head_turn", "Movement Detail", "string", "movement-detail", "움직임이 의식소실 전후 언제 시작했고, 어느 부위·좌우·지속시간과 머리 돌아감이 있었는지 알려주세요.", 159, "event", C),
        Q("dizziness_syncope.tongue_bite_tip_or_side_incontinence_and_foaming", "Tongue Bite Incontinence and Foaming", "string", "seizure-detail", "혀 깨묾의 위치(끝/옆), 소변·대변 실수, 침이나 거품이 있었나요?", 158, "event", C),
        Q("dizziness_syncope.loss_of_consciousness_duration_and_timing_method", "Loss of Consciousness Duration", "string", "loc-duration", "반응이 없던 시간과 누가 어떤 방법으로 시간을 확인했는지 알려주세요.", 157, "event", C),
        Q("event.syncope.post_event_confusion", "Post-event Confusion", "boolean", "post-confusion", "깨어난 뒤 혼란스럽거나 기억이 돌아오는 데 시간이 걸렸나요?", 156, "recovery", C, reuse_existing=True),
        Q("dizziness_syncope.recovery_time_weakness_speech_headache_sleep_and_baseline", "Recovery Course", "string", "recovery-detail", "완전히 평소로 돌아오는 데 걸린 시간과 이후 힘 빠짐·말 이상·두통·졸림·구토를 알려주세요.", 155, "recovery", C),
        Q("dizziness_syncope.injury_site_severity_bleeding_and_current_symptoms", "Injury Detail", "string", "injury-detail", "다친 부위·상처·출혈·통증 정도와 현재 남은 증상을 알려주세요.", 154, "recovery", R),

        Q("history.cardiac_disease", "Cardiac Disease History", "boolean", "cardiac-history", "부정맥·판막질환·심근병증·심근경색·선천성 심장질환 병력이 있나요?", 150, "cardiovascular", R, reuse_existing=True),
        Q("dizziness_syncope.cardiac_history_procedure_device_and_baseline_function", "Professional Cardiac History", "string", "cardiac-detail", "심장 진단·시술·수술·심박동기/제세동기, 평소 활동 가능 수준을 알려주세요.", 149, "cardiovascular", R),
        Q("dizziness_syncope.chest_pain_palpitations_dyspnea_relation_and_pain_nrs", "Cardiorespiratory Symptom Detail", "string", "cardiorespiratory-detail", "가슴통증·두근거림·숨참이 사건 전후 언제 생겼고 얼마나 지속됐는지 알려주세요.", 148, "cardiovascular", D),
        Q(
            "pain.nrs_score", "Pain NRS 0 to 10", "integer", "pain-nrs",
            "통증이 있다면 지금 또는 가장 심할 때를 0에서 10 사이 숫자로 알려주세요.",
            147, "cardiovascular", C, reuse_existing=True,
            fact_overrides={
                "minimum": 0,
                "maximum": 10,
                "scale": {
                    "type": "NRS", "minimum": 0, "maximum": 10,
                    "lower_anchor": "no_pain",
                    "upper_anchor": "worst_imaginable_pain",
                },
                "must_preserve_raw_score": True,
                "required_when_pain_applies": True,
            },
        ),
        Q("dizziness_syncope.family_inherited_cardiac_disease_seizure_and_unexplained_death", "Family Cardiac Neurological and Death History", "string", "family-detail", "가족의 부정맥·심근병증·유전성 심장질환·경련과 나이 어린 돌연사/원인불명 사망을 알려주세요.", 146, "cardiovascular", R),

        Q("history.diabetes", "Diabetes History", "boolean", "diabetes", "당뇨병이 있나요?", 143, "metabolic", R, reuse_existing=True),
        Q("dizziness_syncope.glucose_value_time_meal_relation_and_hypoglycemia_treatment", "Glucose and Meal Context", "string", "glucose", "당뇨가 있거나 혈당을 쟀다면 수치·측정시간·식사/약과의 관계, 저혈당 처치 후 변화를 알려주세요.", 142, "metabolic", R),
        Q("dizziness_syncope.food_fluid_intake_vomiting_diarrhea_fever_and_urine", "Hydration and Acute Illness Context", "string", "hydration", "최근 음식·수분 섭취, 구토·설사·발열과 소변량 변화를 알려주세요.", 141, "metabolic", D),
        Q("dizziness_syncope.bleeding_menses_stool_vomit_urine_donation_and_pallor", "Bleeding and Anaemia Context", "string", "bleeding", "많은 월경·기타 출혈, 혈변·검은 변·토혈·혈뇨·헌혈과 창백함이 있었나요?", 140, "metabolic", D + R),

        Q("dizziness_syncope.current_medicines_name_dose_schedule", "Current Medicines", "string", "medication", "현재 복용 중인 모든 약의 이름·용량·횟수를 알려주세요.", 137, "medicine", R),
        Q("dizziness_syncope.medicine_adherence_recent_change_diuretic_bp_glucose_qt_and_sedative", "Medicine Exposure and Changes", "string", "medicine-detail", "이뇨제·혈압약·혈당약·심장리듬 영향 약·수면진정제 등 최근 시작·중단·증량과 빠뜨린 복용을 알려주세요.", 136, "medicine", R),
        Q("dizziness_syncope.allergies_supplements_alcohol_caffeine_nicotine_and_substance", "Allergy Supplement and Substance Context", "string", "substance", "약물 알레르기, 영양제·한약, 술·카페인·담배/전자담배·기타 물질의 사용과 마지막 시점을 알려주세요.", 135, "medicine", R),
        Q("dizziness_syncope.heat_shift_work_sleep_deprivation_occupation_height_and_driving", "Occupational and Environmental Risk", "string", "occupation", "더위·교대근무·수면 부족과 고소·물·기계·운전 등 의식소실 시 위험한 직업/활동이 있나요?", 134, "medicine", R),

        Q("dizziness_syncope.pregnancy_possible_lmp_gestation_postpartum_and_bleeding", "Pregnancy and Postpartum Context", "string", "pregnancy", "해당되는 경우 임신 가능성·마지막 월경일·임신 주수·출산일/산후 기간과 출혈을 알려주세요.", 131, "reproductive", R),
        Q("dizziness_syncope.child_age_growth_feeding_fever_activity_and_proxy_observation", "Child Proxy and Development Context", "string", "child-detail", "소아라면 나이·성장/발달·식사·발열·활동 변화와 보호자가 본 사건 전후 모습을 알려주세요.", 130, "child", R),

        Q("dizziness_syncope.prior_similar_events_diagnoses_ed_visits_and_admissions", "Previous Events and Care", "string", "prior-events", "이전 유사 사건·진단, 응급실 방문·입원과 당시 경과를 알려주세요.", 127, "history", R),
        Q("dizziness_syncope.prior_exam_orthostatic_vitals_ecg_monitor_echo_labs_imaging_and_source", "Prior Examination and Tests", "string", "prior-tests", "누운/선 혈압·맥박, 심전도·홀터·심장초음파, 혈액/혈당, 청력·영상 검사 날짜·결과와 정보 출처를 알려주세요.", 126, "history", R),
        Q("dizziness_syncope.prior_treatment_hydration_position_manoeuvre_medicine_and_response", "Previous Management and Response", "string", "prior-treatment", "수분·자세 조절·재활/자세교정술·약물 변경 등 시도한 방법과 효과·부작용을 알려주세요.", 125, "history", R),
        Q("dizziness_syncope.neurological_ear_cardiac_metabolic_surgery_and_trauma_history", "Relevant Medical Surgical and Trauma History", "string", "medical-history", "뇌졸중·경련·편두통·귀질환·심장질환·당뇨, 최근 수술·감염·머리/목 외상 병력을 알려주세요.", 124, "history", R),
    ]
    rules = [
        safety_rule(P, "ongoing-unconscious", {"fact": "dizziness_syncope.current_unconscious_or_cannot_be_woken", "equals": True}, "emergency", 1000),
        safety_rule(P, "incomplete-recovery", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "symptom.syncope.full_recovery", "equals": False}]}, "emergency", 1000),
        safety_rule(P, "sudden-neurological-deficit", {"all": [{"fact": "symptom.dizziness.sudden_onset", "equals": True}, {"fact": "symptom.neurological_deficit", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "acute-vestibular-warning", {"all": [{"fact": "symptom.dizziness.sudden_onset", "equals": True}, {"fact": "symptom.new_gait_unsteadiness", "equals": True}, {"fact": "symptom.nausea_or_vomiting", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "severe-cardiorespiratory", {"fact": "dizziness_syncope.severe_chest_pain_or_breathlessness", "equals": True}, "emergency", 1000),
        safety_rule(P, "severe-head-injury", {"fact": "dizziness_syncope.severe_head_injury_warning", "equals": True}, "emergency", 1000),
        safety_rule(P, "poisoning-overdose-co", {"fact": "dizziness_syncope.poisoning_overdose_or_carbon_monoxide_concern", "equals": True}, "emergency", 1000),
        safety_rule(P, "sudden-new-deafness", {"all": [{"fact": "symptom.dizziness.sudden_onset", "equals": True}, {"fact": "symptom.new_hearing_loss", "equals": True}]}, "urgent", 900),
        safety_rule(P, "syncope-chest-pain", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "symptom.chest_pain", "equals": True}]}, "urgent", 900),
        safety_rule(P, "syncope-exertion", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "event.syncope.during_exertion", "equals": True}]}, "urgent", 900),
        safety_rule(P, "syncope-supine", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "event.syncope.while_supine", "equals": True}]}, "urgent", 900),
        safety_rule(P, "syncope-family-sudden-death", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "family_history.sudden_cardiac_death_under_40", "equals": True}]}, "urgent", 900),
        safety_rule(P, "syncope-heart-failure", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "history.heart_failure", "equals": True}]}, "urgent", 900),
        safety_rule(P, "syncope-palpitations", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "symptom.palpitations", "equals": True}]}, "urgent", 900),
        safety_rule(P, "syncope-cardiac-warning", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "dizziness_syncope.unexplained_breathlessness_or_known_murmur_ecg_abnormality", "equals": True}]}, "urgent", 900),
        safety_rule(P, "seizure-associated-feature", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "event.syncope.lateral_tongue_bite", "equals": True}]}, "urgent", 900),
        safety_rule(P, "syncope-injury", {"all": [{"fact": "symptom.syncope.occurred", "equals": True}, {"fact": "event.syncope.injury", "equals": True}]}, "urgent", 900),
        safety_rule(P, "active-bleeding", {"fact": "dizziness_syncope.active_heavy_bleeding_or_black_stool", "equals": True}, "urgent", 900),
        safety_rule(P, "pregnancy-postpartum-warning", {"fact": "dizziness_syncope.pregnancy_postpartum_warning", "equals": True}, "urgent", 900),
        safety_rule(P, "child-severe-warning", {"fact": "dizziness_syncope.child_severe_warning", "equals": True}, "urgent", 900),
    ]
    refresh = default_refresh(); refresh.update({"last_assessed_at": "2026-07-18", "next_monitor_at": "2026-07-19", "next_full_review_at": "2027-01-14"})
    return {"id": "knowledge.generated.neurological.dizziness-syncope", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-dizziness-syncope-research", "default_refresh": refresh, "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="symptom.dizziness.current", question_budget=86, source_refs=SOURCES)
    p["required_facts"]["routine"] = ["symptom.syncope.occurred", "dizziness_syncope.primary_group", "symptom.duration", "dizziness_syncope.onset_date_time_place_activity_posture_and_speed", "dizziness_syncope.continuous_episodic_frequency_duration_and_trend", "symptom.dizziness.presentation", "symptom.dizziness.severity", "dizziness_syncope.patient_words_and_change_from_baseline", "dizziness_syncope.function_walking_selfcare_work_school_driving_and_falls", "dizziness_syncope.current_medicines_name_dose_schedule", "dizziness_syncope.neurological_ear_cardiac_metabolic_surgery_and_trauma_history", "dizziness_syncope.prior_similar_events_diagnoses_ed_visits_and_admissions", "dizziness_syncope.prior_exam_orthostatic_vitals_ecg_monitor_echo_labs_imaging_and_source", "dizziness_syncope.prior_treatment_hydration_position_manoeuvre_medicine_and_response", "dizziness_syncope.information_source_witness_reliability_video_and_conflict", "dizziness_syncope.patient_concern_goal_and_additional_comment"]
    cases = {
        "acute_continuous": ["dizziness_syncope.visual_nystagmus_diplopia_photophobia_and_aura", "dizziness_syncope.headache_neck_pain_migraine_history_and_relation", "dizziness_syncope.food_fluid_intake_vomiting_diarrhea_fever_and_urine"],
        "positional_head_movement": ["symptom.dizziness.head_movement_trigger", "dizziness_syncope.position_head_movement_latency_duration_and_side", "symptom.hearing_change_or_tinnitus", "dizziness_syncope.hearing_side_onset_tinnitus_fullness_pain_and_discharge"],
        "postural_presyncope": ["symptom.dizziness.postural_trigger", "dizziness_syncope.standing_heat_meal_exertion_cough_urination_pain_and_emotion_trigger", "event.syncope.reflex_prodrome", "event.syncope.no_prodrome", "dizziness_syncope.food_fluid_intake_vomiting_diarrhea_fever_and_urine", "dizziness_syncope.bleeding_menses_stool_vomit_urine_donation_and_pallor"],
        "blackout_syncope": ["dizziness_syncope.event_count_frequency_previous_and_last_event", "dizziness_syncope.event_before_symptoms_sequence_and_last_memory", "dizziness_syncope.witness_appearance_colour_eyes_breathing_and_responsiveness", "event.syncope.limb_jerking", "dizziness_syncope.movement_onset_body_part_symmetry_duration_and_head_turn", "dizziness_syncope.tongue_bite_tip_or_side_incontinence_and_foaming", "dizziness_syncope.loss_of_consciousness_duration_and_timing_method", "event.syncope.post_event_confusion", "dizziness_syncope.recovery_time_weakness_speech_headache_sleep_and_baseline", "dizziness_syncope.injury_site_severity_bleeding_and_current_symptoms", "history.cardiac_disease", "dizziness_syncope.cardiac_history_procedure_device_and_baseline_function", "dizziness_syncope.chest_pain_palpitations_dyspnea_relation_and_pain_nrs", "pain.nrs_score", "dizziness_syncope.family_inherited_cardiac_disease_seizure_and_unexplained_death"],
        "hearing_or_headache": ["symptom.hearing_change_or_tinnitus", "dizziness_syncope.hearing_side_onset_tinnitus_fullness_pain_and_discharge", "dizziness_syncope.headache_neck_pain_migraine_history_and_relation", "dizziness_syncope.visual_nystagmus_diplopia_photophobia_and_aura"],
        "medicine_metabolic": ["history.diabetes", "dizziness_syncope.glucose_value_time_meal_relation_and_hypoglycemia_treatment", "dizziness_syncope.food_fluid_intake_vomiting_diarrhea_fever_and_urine", "dizziness_syncope.bleeding_menses_stool_vomit_urine_donation_and_pallor", "dizziness_syncope.medicine_adherence_recent_change_diuretic_bp_glucose_qt_and_sedative", "dizziness_syncope.allergies_supplements_alcohol_caffeine_nicotine_and_substance", "dizziness_syncope.heat_shift_work_sleep_deprivation_occupation_height_and_driving"],
        "child_proxy": ["dizziness_syncope.child_age_growth_feeding_fever_activity_and_proxy_observation", "dizziness_syncope.event_count_frequency_previous_and_last_event", "dizziness_syncope.witness_appearance_colour_eyes_breathing_and_responsiveness", "dizziness_syncope.recovery_time_weakness_speech_headache_sleep_and_baseline"],
        "other_unclear": ["dizziness_syncope.pregnancy_possible_lmp_gestation_postpartum_and_bleeding", "history.diabetes", "dizziness_syncope.food_fluid_intake_vomiting_diarrhea_fever_and_urine", "dizziness_syncope.medicine_adherence_recent_change_diuretic_bp_glucose_qt_and_sedative", "dizziness_syncope.heat_shift_work_sleep_deprivation_occupation_height_and_driving"],
    }
    p["conditional_required_facts"] = [{"selector_fact": "dizziness_syncope.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nice.ng127.dizziness.2023", "NICE", "Suspected neurological conditions — dizziness and vertigo", "NG127-updated-2023-10-02", "https://www.nice.org.uk/guidance/ng127/chapter/Recommendations-for-adults-aged-over-16", "nice_guidance", ["Sudden dizziness with focal neurological deficit, new unsteadiness or new deafness needs immediate assessment when a benign presentation or corrected hypoglycaemia does not account for it.", "Acute vestibular syndrome includes vertigo, nausea or vomiting and gait unsteadiness; head-movement, postural, hearing and headache context modifies assessment without assigning a diagnosis."]),
        ("source.nice.cg109.tloc.2023", "NICE", "Transient loss of consciousness in over 16s", "CG109-updated-2023-11-21", "https://www.nice.org.uk/guidance/cg109/chapter/Recommendations", "nice_guidance", ["Patient and witness accounts record circumstances, posture, prodrome, appearance, colour, eye state, movement and duration, tongue-bite site, injury, event duration, recovery confusion and unilateral weakness.", "Urgent cardiovascular context includes ECG abnormality, heart failure, exertional TLoC, young family sudden death, unexplained breathlessness and murmur; current medicines and previous event frequency are recorded.", "The interview does not diagnose a faint, epilepsy, arrhythmia or postural hypotension and does not select a test."]),
        ("source.nhs.fainting.2023", "NHS", "Fainting", "reviewed-2023-02-23", "https://www.nhs.uk/symptoms/fainting/", "public_health_guidance", ["Failure to wake promptly, incomplete recovery, speech or movement difficulty, chest pain, palpitations, seizure activity or exertional fainting are emergency warning features."]),
        ("source.nhs.stroke-symptoms.2026", "NHS", "Symptoms of a stroke", "current-2026", "https://www.nhs.uk/conditions/stroke/symptoms/", "public_health_guidance", ["Sudden unilateral face or arm weakness and speech difficulty are emergency warning features; confusion, dizziness and falling can also occur.", "The interview records warning features without diagnosing stroke."]),
        ("source.nhs.head-injury.2025", "NHS", "Head injury and concussion", "current-2026", "https://www.nhs.uk/conditions/head-injury-and-concussion/", "public_health_guidance", ["After head injury, failure to wake, seizure, weakness, repeated vomiting, severe persistent headache or clear fluid from the ears or nose are warning features requiring emergency assessment."]),
        ("source.nhs.carbon-monoxide-poisoning.2025", "NHS", "Carbon monoxide poisoning", "reviewed-2025-12-16", "https://www.nhs.uk/conditions/carbon-monoxide-poisoning/", "public_health_guidance", ["Headache, dizziness, nausea, weakness, tiredness and confusion that vary by location or affect co-occupants support immediate exposure assessment.", "Breathing difficulty, sudden confusion or loss of consciousness after possible exposure requires emergency help."]),
        ("source.stom.mrcm.dizziness-syncope.20260714", "Infoclinic", "STOM dizziness and syncope terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/404640003", "terminology_server", ["STOM confirmed active Dizziness and Syncope concepts; Finding site and Severity were allowed for Dizziness.", "The Syncope allowed-attribute query returned an empty collection, so no post-coordinated Syncope attribute is asserted; MRCM has no clinical-rule authority."]),
    ]
    verified_now = {"source.nhs.fainting.2023", "source.nhs.stroke-symptoms.2026", "source.nhs.head-injury.2025", "source.nhs.carbon-monoxide-poisoning.2025"}
    artifacts = []
    for sid, publisher, title, version, url, profile, assertions in defs:
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-18" if sid in verified_now else "2026-07-14", "monitor_result": "current_official_source_confirmed" if sid in verified_now else "not_due_existing_metadata_preserved", "assertions": assertions})
    research = {"id": "source-manifest.primary-care-dizziness-syncope-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.dizziness-syncope", "generated_clinical_knowledge", "knowledge/generated/neurological/dizziness-syncope/dizziness-syncope.json", True), ("source.mapping.dizziness-syncope", "terminology_mapping", "mappings/terminology/snomed-mrcm-dizziness-syncope.json", False), ("source.external.dizziness-syncope", "external_source_manifest", "sources/manifests/primary-care-dizziness-syncope-research.json", False), ("source.policy.dizziness-syncope", "runtime_policy", "policies/primary-care-dizziness-syncope-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-dizziness-syncope", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        key, level, condition = rule["id"].split("safety.")[1], rule["then"]["safety_level"], rule["when"]
        children = condition.get("all", [condition]); state = {x["fact"]: {"value": x.get("equals", True)} for x in children}
        out[f"DIZZINESS-SYNCOPE-{key.upper()}.json"] = {"id": f"DIZZINESS-SYNCOPE-{key.upper()}", "simulation_language": "ko", "persona": {"age": 9 if key == "child-severe-warning" else 24 + index * 3}, "initial_statement": {"ko": "어지럼 또는 실신이 있어 진료 전 문진을 합니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 35, "forbidden_assertions": ["diagnosis.stroke", "diagnosis.epilepsy", "diagnosis.arrhythmia", "diagnosis.bppv", "diagnosis.vasovagal_syncope"]}, "provenance": provenance(SOURCES)}
    policy = completion(f); always, base, branches = policy["required_facts"]["always"], policy["required_facts"]["routine"], policy["conditional_required_facts"][0]["cases"]
    by_id = {x["fact"]["id"]: x["fact"] for x in f["entries"]}
    def routine(branch):
        values = {}
        for fid in dict.fromkeys([*always, *base, *branches[branch]]):
            fact = by_id[fid]
            if fact["value_type"] == "boolean": value = False
            elif fact["value_type"] == "coded": value = fact.get("allowed_values", ["other_unclear"])[0]
            elif fact["value_type"] == "quantity": value = "2 weeks"
            else: value = "특이사항 없음"
            values[fid] = {"value": value}
        values["symptom.dizziness.current"] = {"value": True}; values["dizziness_syncope.primary_group"] = {"value": branch}; values["symptom.dizziness.severity"] = {"value": "moderate"}
        if "pain.nrs_score" in values: values["pain.nrs_score"] = {"value": 0}
        return values
    specs = [
        ("POSITIONAL", "positional_head_movement", 48, "침대에서 돌아누울 때 수초간 빙빙 돕니다.", {"symptom.dizziness.head_movement_trigger": {"value": True}, "dizziness_syncope.position_head_movement_latency_duration_and_side": {"value": "오른쪽으로 돌아누우면 2초 뒤 시작해 20초 지속"}}),
        ("POSTURAL-PRESYNCOPE", "postural_presyncope", 72, "일어설 때 눈앞이 캄캄하고 거의 쓰러질 듯합니다.", {"symptom.dizziness.postural_trigger": {"value": True}, "event.syncope.reflex_prodrome": {"value": True}}),
        ("BLACKOUT-WITNESS", "blackout_syncope", 37, "잠깐 의식을 잃은 사건을 목격자와 함께 정리합니다.", {"symptom.syncope.occurred": {"value": True}, "symptom.syncope.full_recovery": {"value": True}, "dizziness_syncope.information_source_witness_reliability_video_and_conflict": {"value": "환자와 배우자 목격 설명, 영상 없음"}}),
        ("HEARING-HEADACHE", "hearing_or_headache", 33, "반복 어지럼과 이명, 두통이 함께 있습니다.", {"symptom.hearing_change_or_tinnitus": {"value": True}, "dizziness_syncope.headache_neck_pain_migraine_history_and_relation": {"value": "어지럼 전 두통과 빛 민감"}}),
        ("MEDICINE-METABOLIC", "medicine_metabolic", 79, "혈압약 변경 뒤 어지럽고 식사도 줄었습니다.", {"dizziness_syncope.medicine_adherence_recent_change_diuretic_bp_glucose_qt_and_sedative": {"value": "3일 전 혈압약 증량"}, "dizziness_syncope.food_fluid_intake_vomiting_diarrhea_fever_and_urine": {"value": "식사 절반, 수분 섭취 감소"}}),
        ("CHILD-PROXY", "child_proxy", 11, "아이가 어지럽다고 해 보호자가 관찰 내용을 답합니다.", {"dizziness_syncope.information_source_witness_reliability_video_and_conflict": {"value": "보호자 관찰, 아이 본인 확인 필요"}, "dizziness_syncope.child_age_growth_feeding_fever_activity_and_proxy_observation": {"value": "11세, 성장 정상, 오늘 활동 감소"}}),
        ("MULTI-RFE-HEARING", "other_unclear", 58, "어지럼 외에 청력 저하도 별도 문진하고 싶습니다.", {"dizziness_syncope.patient_concern_goal_and_additional_comment": {"value": "청력 저하를 별도 RFE로 전달 요청"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine(branch); state.update(overrides)
        out[f"DIZZINESS-SYNCOPE-{key}.json"] = {"id": f"DIZZINESS-SYNCOPE-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": state, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 105, "forbidden_assertions": ["diagnosis.stroke", "diagnosis.epilepsy", "diagnosis.arrhythmia", "diagnosis.bppv"]}, "provenance": provenance(SOURCES)}
    absent = routine("other_unclear"); missing = "dizziness_syncope.prior_exam_orthostatic_vitals_ecg_monitor_echo_labs_imaging_and_source"; absent.pop(missing)
    out["DIZZINESS-SYNCOPE-REMOTE-DATA-ABSENT.json"] = {"id": "DIZZINESS-SYNCOPE-REMOTE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 83}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "보호자가 전화로 어지럼을 설명하며 이전 검사자료는 없습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {missing: "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 105, "forbidden_assertions": ["diagnosis.stroke", "diagnosis.arrhythmia"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Dizziness, Presyncope or Transient Loss of Consciousness", intents=[("intent.characterize_symptom", "Characterize Dizziness Type Onset Course Trigger Event and Recovery"), ("intent.screen_red_flags", "Screen Neurologic Vestibular Cardiovascular Injury Bleeding Toxic Pregnancy and Child Warning Features"), ("intent.differentiate_common_causes", "Describe Positional Postural Hearing Headache Reflex Metabolic and Medicine Context"), ("intent.risk_assessment", "Assess Witness Reliability Cardiac and Neurological History Medicines Tests Treatment Function and Patient Goals")])
    primary, research = source_docs()
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": "404640003", "display": "Dizziness (finding)", "concept_active": True}, {"code": "271594007", "display": "Syncope (finding)", "concept_active": True}], "dizziness_checks": [{"focus_code": "404640003", "attribute_code": "363698007", "allowed": True}, {"focus_code": "404640003", "attribute_code": "246112005", "allowed": True}], "syncope_checks": [], "unsupported_checks": [{"focus_code": "271594007", "reason": "STOM returned an empty allowed-attribute collection; no post-coordinated attribute binding is asserted."}], "validation": {"method": "build_time_live_mrcm_summary", "checked_at": "2026-07-14T00:00:00Z", "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "partial_provisional_pass"}, "dizziness_syncope_semantics": {"diagnosis_inferred": False, "stroke_diagnosed": False, "epilepsy_diagnosed": False, "arrhythmia_diagnosed": False, "bppv_diagnosed": False, "syncope_postcoordination_asserted": False, "test_selected_or_ordered": False, "runtime_terminology_query_required": False}, "provenance": provenance(["source.stom.mrcm.dizziness-syncope.20260714"])}
    docs = [("knowledge/base/primary-care-dizziness-syncope.json", graph), ("rules/base/primary-care-dizziness-syncope.json", rules), ("knowledge/generated/neurological/dizziness-syncope/dizziness-syncope.json", f), ("mappings/terminology/snomed-mrcm-dizziness-syncope.json", mapping), ("sources/manifests/primary-care-dizziness-syncope.json", primary), ("sources/manifests/primary-care-dizziness-syncope-research.json", research), ("policies/primary-care-dizziness-syncope-completion.json", completion(f))]
    for path, document in docs: write_json(path, document)
    for name, case in cases(f).items(): write_json("simulation/patients/neurological/dizziness-syncope/" + name, case)


if __name__ == "__main__": main()
