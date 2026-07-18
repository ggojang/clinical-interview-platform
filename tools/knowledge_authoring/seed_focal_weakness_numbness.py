#!/usr/bin/env python3
"""Rebuild unreviewed focal weakness and numbness knowledge for clinician handoff."""
from profile_support import *

P, RFE = "focal-neurology", "rfe.focal_weakness_numbness"
M, SN = "mapping.snomed-mrcm.focal-weakness-numbness", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-18T07:34:26Z"
SOURCES = [
    "source.nice.ng127.adult-focal-neurology.2023",
    "source.nice.ng127.child-focal-neurology.2023",
    "source.nhs.stroke.2026",
    "source.stom.focal.20260714",
]
G = {key: f"group.focal-neurology.{key}" for key in (
    "routing", "safety", "course", "distribution", "motor", "sensory",
    "spine", "episodic", "systemic", "medicine", "reproductive", "child",
    "history", "handoff",
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
        "sudden_unilateral", "recurrent_transient", "progressive_symmetric",
        "progressive_single_limb", "spine_or_radicular", "distal_symmetric",
        "compression_or_position", "child_or_proxy", "other_unclear",
    ]
    e = [
        Q("symptom.focal_neurology.current", "Current Weakness or Sensory Change", "boolean", "current", "지금도 특정 부위의 힘 빠짐·감각 둔함·저림 중 하나가 있나요?", 340, "routing", C, safety_relevant=True),
        Q("focal_neurology.primary_group", "Primary Focal Neurology Context", "coded", "primary-group", "가장 가까운 상황은 갑작스러운 한쪽 증상, 짧게 반복되는 증상, 양쪽의 진행성 증상, 한 팔다리의 진행성 증상, 목·허리/뻗치는 통증 동반, 손발 끝 대칭 증상, 자세·압박 관련, 소아·보호자 관찰, 또는 불분명 중 무엇인가요?", 339, "routing", C + D, allowed_values=branches),
        Q("symptom.focal_neurology.main_type", "Main Focal Neurologic Symptom", "coded", "main-type", "주된 증상은 실제 힘 빠짐, 감각 둔함, 찌릿한 저림, 통증 때문에 못 움직임, 또는 혼합 중 무엇인가요?", 225, "routing", C, allowed_values=["weakness", "numbness", "tingling", "pain_limited", "mixed", "unclear"]),
        Q("symptom.duration", "Symptom Duration", "quantity", "duration", "첫 증상은 언제 시작했고 전체적으로 얼마나 지속됐나요?", 224, "course", C, reuse_existing=True),
        Q("focal_neurology.last_known_well_and_exact_onset_date_time_place_activity_posture", "Last Known Well and Exact Onset", "string", "onset", "마지막으로 정상임을 확인한 시각, 처음 발견한 날짜·시간·장소와 당시 활동·자세를 알려주세요.", 223, "course", C + R),
        Q("focal_neurology.onset_seconds_minutes_hours_and_symptom_sequence", "Onset Speed and Sequence", "string", "onset-speed", "수초·수분·수시간·수일 중 얼마나 빠르게 시작했고, 힘·감각·말·시야 등 어떤 증상이 어떤 순서로 생겼나요?", 222, "course", C),
        Q("focal_neurology.continuous_episodic_frequency_duration_recovery_and_trend", "Episode Pattern Recovery and Trend", "string", "pattern", "계속되는지 반복되는지, 횟수·한 번 지속시간·완전 회복 여부와 최근 호전/악화 추세를 알려주세요.", 221, "course", C),
        Q("symptom.focal_neurology.side", "Affected Side", "coded", "side", "왼쪽, 오른쪽, 양쪽, 번갈아 나타남 중 어디인가요?", 220, "distribution", C, allowed_values=["left", "right", "bilateral", "alternating", "variable", "unclear"]),
        Q("symptom.focal_neurology.region", "Affected Region", "coded", "region", "얼굴, 팔·손, 다리·발, 몸통, 회음부 또는 여러 부위 중 어디인가요?", 219, "distribution", C, allowed_values=["face", "arm_hand", "leg_foot", "trunk", "perineum", "multiple", "unclear"], terminology_binding={"system": SN, "focus_code": "44077006", "attribute_code": "363698007"}, mrcm_ref=M),
        Q("focal_neurology.exact_boundary_digits_joints_proximal_distal_and_spread", "Exact Distribution and Spread", "string", "distribution-detail", "정확한 경계, 손가락·발가락, 관절 위/아래, 몸 가까운/먼 쪽과 증상이 퍼지는 방향을 알려주세요.", 218, "distribution", C),
        Q("focal_neurology.patient_words_and_difference_from_baseline", "Patient Description and Baseline Change", "string", "patient-words", "본인의 표현으로 어떤 느낌인지, 평소 힘·감각·보행·손 사용과 비교해 무엇이 달라졌는지 알려주세요.", 217, "handoff", C),
        Q("focal_neurology.function_walk_transfer_stairs_handwriting_grip_selfcare_work_school_driving", "Functional and Safety Impact", "string", "function", "걷기·일어서기·계단·물건 잡기·글쓰기·식사·옷 입기·일/학업·운전 중 새로 어려워진 것을 알려주세요.", 216, "handoff", C + R),
        Q("focal_neurology.information_source_proxy_witness_reliability_record_and_conflict", "Information Source Reliability and Conflict", "string", "source", "본인·보호자·목격자 중 누가 답하는지, 기록이나 영상이 있는지, 기억이 불확실하거나 설명이 서로 다른지 알려주세요.", 215, "handoff", R),
        Q("focal_neurology.patient_concern_goal_expectation_and_additional_comment", "Patient Concern Goal and Additional Comment", "string", "goal", "가장 걱정되는 점, 진료에서 확인하고 싶은 점과 질문에 없던 의견을 알려주세요.", 214, "handoff", R),

        Q("symptom.focal_neurology.sudden_onset", "Sudden Onset", "boolean", "sudden", "증상이 수초에서 수분 사이 갑자기 시작했나요?", 338, "safety", S, safety_relevant=True),
        Q("symptom.focal_neurology.one_sided", "One-sided Symptom", "boolean", "one-sided", "얼굴이나 몸의 한쪽에만 새 증상이 있나요?", 337, "safety", S, safety_relevant=True),
        Q("symptom.face_droop", "Face Droop", "boolean", "face-droop", "웃을 때 한쪽 얼굴이나 입꼬리가 처지나요?", 336, "safety", S, safety_relevant=True),
        Q("symptom.arm_drift_or_cannot_raise", "Arm Drift or Cannot Raise", "boolean", "arm-drift", "두 팔을 들 때 한쪽 팔이 내려가거나 들 수 없나요?", 335, "safety", S, safety_relevant=True),
        Q("symptom.speech_or_language_disturbance", "Speech or Language Disturbance", "boolean", "speech", "말이 어눌하거나 단어가 나오지 않거나 다른 사람의 말을 이해하기 어렵나요?", 334, "safety", S, safety_relevant=True),
        Q("symptom.sudden_visual_loss_or_field_defect", "Sudden Visual Loss or Field Defect", "boolean", "vision", "시야가 갑자기 흐려지거나 한쪽 눈 또는 시야 일부가 보이지 않나요?", 333, "safety", S, safety_relevant=True),
        Q("symptom.sudden_gait_unsteadiness", "Sudden Gait Unsteadiness", "boolean", "gait", "갑자기 혼자 서거나 걷기 어렵거나 한쪽으로 넘어지나요?", 332, "safety", S, safety_relevant=True),
        Q("symptom.focal_neurology.resolved_within_24h", "Sudden Symptom Resolved within 24 Hours", "boolean", "resolved", "지난 24시간 안에 갑자기 생겼다가 사라진 한쪽 힘·감각·말·시야 증상이 있나요?", 331, "safety", S, safety_relevant=True),
        Q("focal_neurology.current_unconscious_confused_or_difficult_to_wake", "Current Consciousness Warning", "boolean", "consciousness", "현재 의식이 없거나 깨우기 어렵거나 새로 심하게 혼란스러운가요?", 330, "safety", S, safety_relevant=True),
        Q("focal_neurology.seizure_with_persistent_new_weakness_or_confusion", "Seizure with Persistent Deficit", "boolean", "seizure-warning", "경련이나 의식소실 뒤 새 힘 빠짐·말 이상·혼란이 계속되나요?", 329, "safety", S, safety_relevant=True),
        Q("symptom.dyspnea_at_rest_or_supine", "Breathlessness at Rest or Supine", "boolean", "breathing", "가만히 있거나 누우면 숨이 차거나 숨쉬는 힘이 약해진 느낌이 있나요?", 330, "safety", S, safety_relevant=True),
        Q("symptom.new_swallowing_impairment", "New Swallowing Impairment", "boolean", "swallowing", "새로 삼키기 어렵거나 물·음식에 자주 사레가 드나요?", 329, "safety", S, safety_relevant=True),
        Q("symptom.symmetric_progressive_weakness", "Rapid Symmetric Progressive Weakness", "boolean", "symmetric-progressive", "양쪽 팔다리 힘 또는 감각이 수시간에서 4주 사이 빠르게 나빠지나요?", 328, "safety", S, safety_relevant=True),
        Q("focal_neurology.neck_weakness_head_drop_or_voice_change", "Neck Bulbar Warning", "boolean", "neck-bulbar", "목 힘이 빠져 머리를 들기 어렵거나 목소리가 약해지거나 콧소리로 변했나요?", 325, "safety", S, safety_relevant=True),
        Q("symptom.severe_back_pain_radiating_leg", "Severe Back Pain Radiating to Leg", "boolean", "back-leg-pain", "심한 허리 통증이 한쪽 또는 양쪽 다리로 뻗치나요?", 324, "safety", S, safety_relevant=True),
        Q("symptom.new_bladder_bowel_or_sexual_dysfunction", "New Bladder Bowel or Sexual Dysfunction", "boolean", "bladder-bowel", "새로 소변이 안 나오거나 새거나, 대변 조절·성기능이 달라졌나요?", 323, "safety", S, safety_relevant=True),
        Q("symptom.perineal_or_saddle_numbness", "Saddle Numbness", "boolean", "saddle", "회음부·성기·엉덩이 안쪽·항문 주위 감각이 새로 둔해졌나요?", 322, "safety", S, safety_relevant=True),
        Q("symptom.single_limb_rapid_progression", "Rapid Single-limb Progression", "boolean", "single-progressive", "한쪽 팔다리 힘이 몇 시간에서 며칠 사이 빠르게 약해지나요?", 321, "safety", S, safety_relevant=True),
        Q("focal_neurology.recurrent_brief_fixed_sensory_under_two_minutes", "Recurrent Brief Fixed Sensory Pattern", "boolean", "brief-fixed", "같은 부위·같은 순서의 감각 이상이 2분 미만으로 반복되나요?", 320, "safety", S, safety_relevant=True),
        Q("focal_neurology.recent_head_spine_trauma_with_new_deficit", "Trauma with New Deficit", "boolean", "trauma-warning", "최근 머리·목·척추 외상 뒤 새 힘 빠짐·감각 저하·보행 이상이 생겼나요?", 319, "safety", S, safety_relevant=True),
        Q("focal_neurology.child_sudden_or_rapid_progressive_weakness", "Child Sudden or Rapid Progressive Weakness", "boolean", "child-weakness-warning", "소아라면 얼굴·팔다리 힘이 갑자기 빠졌거나 수시간~수일 사이 빠르게 나빠지나요?", 318, "safety", S, safety_relevant=True),
        Q("focal_neurology.child_tingling_with_weakness_bladder_bowel_or_gait", "Child Tingling with Motor or Autonomic Warning", "boolean", "child-tingling-warning", "소아라면 저림과 함께 힘 빠짐·새 보행 이상·배뇨/배변 변화가 있나요?", 317, "safety", S, safety_relevant=True),
        Q("focal_neurology.infant_hypotonia_feeding_breathing_or_consciousness_warning", "Infant Hypotonia Warning", "boolean", "infant-warning", "1세 미만 영아라면 갑자기 축 늘어짐과 함께 수유 곤란·호흡 곤란·발열·의식 변화가 있나요?", 316, "safety", S, safety_relevant=True),

        Q("symptom.objective_motor_task_loss", "Objective Motor Task Loss", "string", "motor-task", "컵 들기·단추 잠그기·열쇠 돌리기·글쓰기·발뒤꿈치/발끝 들기·계단·의자에서 일어나기 중 실제로 못 하게 된 동작을 알려주세요.", 185, "motor", C, terminology_binding={"system": SN, "code": "26544005"}),
        Q("focal_neurology.face_eye_closure_forehead_cheek_tongue_and_drooling", "Detailed Facial Motor Function", "string", "face-detail", "이마 주름·눈 감기·볼 부풀리기·혀 움직임·침 흘림 중 좌우 차이나 새 변화가 있나요?", 184, "motor", C),
        Q("focal_neurology.arm_leg_proximal_distal_grip_foot_drop_and_fatigability", "Detailed Limb Motor Pattern", "string", "motor-detail", "어깨·팔꿈치·손아귀·손가락, 엉덩이·무릎·발목·발가락 중 약한 부위와 반복할수록 더 약해지는지 알려주세요.", 183, "motor", C),
        Q("symptom.sensory_quality", "Sensory Quality", "coded", "sensory-quality", "완전 무감각, 바늘로 찌름, 화끈거림, 전기 느낌, 차갑거나 뜨거운 감각 변화 중 무엇인가요?", 182, "sensory", C, allowed_values=["numb", "pins_needles", "burning", "electric", "temperature_change", "mixed", "unclear"], terminology_binding={"system": SN, "code": "91019004"}),
        Q("focal_neurology.sensory_level_stocking_glove_patch_and_provocation", "Sensory Distribution Pattern", "string", "sensory-pattern", "몸통의 선 아래, 양말/장갑 모양, 특정 손가락·발가락, 작은 반점 중 어떤 분포인지와 만짐·압박 때 변화를 알려주세요.", 181, "sensory", C),
        Q("focal_neurology.balance_coordination_falls_and_dexterity", "Balance Coordination and Dexterity", "string", "coordination", "휘청거림·넘어짐·물건을 자주 떨어뜨림·손놀림 둔화·단추/젓가락 어려움이 있나요?", 180, "motor", C + R),
        Q("focal_neurology.headache_dizziness_vision_speech_swallowing_hearing_and_cognition_relation", "Associated Neurological Symptoms", "string", "associated-neuro", "두통·어지럼·시야·말·삼킴·청력·기억/혼란 증상이 언제 함께 생겼고 회복됐는지 알려주세요.", 179, "episodic", C + R),
        Q("focal_neurology.pain_present", "Associated Pain Present", "boolean", "pain-present", "목·허리·얼굴·팔다리 통증이 함께 있나요?", 178, "spine", C),
        Q("focal_neurology.pain_nrs", "Mandatory Associated Pain NRS", "integer", "pain-nrs", "[필수] 통증이 있다면 가장 심할 때의 통증을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 177, "spine", C, fact_overrides={"minimum": 0, "maximum": 10, "scale": {"type": "NRS", "minimum": 0, "maximum": 10, "lower_anchor": "no_pain", "upper_anchor": "worst_imaginable_pain"}, "must_preserve_raw_score": True, "required_when_pain_applies": True}),
        Q("focal_neurology.neck_back_pain_radiation_cough_movement_and_night_pattern", "Spine and Radiating Pain Detail", "string", "spine-detail", "목·허리 통증의 부위·퍼지는 방향과 기침·힘주기·움직임·밤/휴식 때 변화를 알려주세요.", 176, "spine", D),
        Q("focal_neurology.position_repetition_sleep_compression_tool_and_relief", "Position Repetition and Compression Context", "string", "compression", "수면 자세·팔꿈치/손목 압박·다리 꼬기·무거운 가방·반복 작업·진동공구와 관련되고 자세를 바꾸면 몇 분 안에 좋아지나요?", 175, "spine", D + R),
        Q("focal_neurology.episode_fixed_pattern_spread_duration_awareness_and_post_event", "Brief Episode Detail", "string", "episode-detail", "반복 증상의 시작 부위·퍼지는 순서·지속시간·의식/반응 변화와 이후 혼란·피로를 알려주세요.", 174, "episodic", D + R),
        Q("focal_neurology.gradual_reversible_five_to_sixty_minute_sensory_visual_headache_relation", "Gradual Reversible Sensory Pattern", "string", "gradual-pattern", "감각 증상이 5분 이상 서서히 퍼져 5~60분 지속 후 완전히 회복되는지, 시각 증상·두통과의 관계를 알려주세요.", 173, "episodic", D),
        Q("focal_neurology.blister_rash_fever_infection_tick_and_recent_illness", "Infection and Inflammatory Context", "string", "infection", "발진·물집·발열, 최근 감염·진드기/동물 노출과 신경 증상의 시간 관계를 알려주세요.", 170, "systemic", D + R),
        Q("focal_neurology.weight_loss_night_sweat_cancer_immunity_and_systemic_change", "Systemic Risk Context", "string", "systemic-risk", "체중 감소·야간발한·암·면역저하와 다른 전신 상태 변화가 있나요?", 169, "systemic", R),
        Q("focal_neurology.diabetes_thyroid_b12_kidney_celiac_nutrition_and_alcohol_context", "Metabolic Nutritional and Alcohol Context", "string", "metabolic", "당뇨·갑상선·비타민 B12·신장·셀리악병, 식사 제한·영양 상태와 음주량을 알려주세요.", 168, "systemic", R),
        Q("focal_neurology.current_medicines_dose_schedule_adherence_recent_change_and_neurotoxic_exposure", "Medicine and Treatment Exposure", "string", "medicine", "처방약·일반약·한약·영양제의 이름·용량·횟수, 최근 시작/중단/변경과 항암·진정·신경 영향 가능 치료를 알려주세요.", 165, "medicine", R),
        Q("focal_neurology.anticoagulant_antiplatelet_hormone_allergy_and_substance", "Bleeding Hormone Allergy and Substance Context", "string", "medicine-risk", "항응고제·항혈소판제·호르몬/피임약, 약물 알레르기와 술·담배·기타 물질 사용을 알려주세요.", 164, "medicine", R),
        Q("focal_neurology.occupation_repetition_vibration_posture_heavy_lifting_chemical_and_driving", "Occupational and Safety Exposure", "string", "occupation", "반복동작·진동·고정 자세·중량물·용제/금속 등 직업 노출과 운전·고소·기계 작업 안전 영향을 알려주세요.", 163, "medicine", R),
        Q("focal_neurology.pregnancy_possible_lmp_gestation_postpartum_and_complications", "Pregnancy and Postpartum Context", "string", "pregnancy", "해당되는 경우 임신 가능성, 마지막 월경일·임신 주수, 출산일·산후 기간과 고혈압·출혈·혈전 등 합병증을 알려주세요.", 160, "reproductive", R),
        Q("focal_neurology.child_age_development_regression_school_play_feeding_and_proxy", "Child Development and Proxy Context", "string", "child-context", "소아라면 나이·발달/운동 퇴행·학교/놀이·수유/식사 변화와 본인/보호자 중 누가 답하는지 알려주세요.", 157, "child", R),
        Q("focal_neurology.child_early_hand_preference_new_gait_backpack_crossed_legs_and_hyperventilation", "Child Pattern and Compression Context", "string", "child-detail", "소아라면 새 보행 이상·운동기능 퇴행·1세 전 한쪽 손 선호, 무거운 가방·다리 꼬기·과호흡과의 관계를 알려주세요.", 156, "child", D + R),
        Q("event.recent_injury_or_procedure", "Recent Injury or Procedure", "boolean", "injury", "최근 머리·목·척추·팔다리 외상, 수술·주사·카테터·치과 시술이 있었나요?", 153, "history", R, reuse_existing=True),
        Q("event.recent_infection_or_vaccination", "Recent Infection or Vaccination", "boolean", "infection-vaccination", "증상 전 수주 안에 감염이나 예방접종이 있었나요?", 152, "history", R, reuse_existing=True),
        Q("focal_neurology.prior_stroke_tia_seizure_migraine_neuropathy_spine_and_functional_diagnosis", "Relevant Neurological History", "string", "neuro-history", "과거 뇌졸중/TIA·경련·편두통·말초신경·뇌/척추 질환과 전문의가 진단한 기능성 신경장애가 있나요?", 151, "history", R),
        Q("focal_neurology.prior_episode_emergency_visit_admission_diagnosis_and_baseline_recovery", "Prior Episode and Acute Care", "string", "prior-episode", "이전 같은 증상의 날짜·양상·응급실/입원·진단과 평소 상태까지 회복했는지 알려주세요.", 150, "history", R),
        Q("focal_neurology.prior_neurologic_exam_strength_reflex_sensation_gait_and_source", "Prior Neurological Examination", "string", "prior-exam", "이전 근력·반사·감각·보행 검사 날짜·결과와 직접 본 기록인지 들은 내용인지 알려주세요.", 149, "history", R),
        Q("focal_neurology.prior_glucose_b12_thyroid_renal_imaging_emg_and_source", "Prior Tests and Source", "string", "prior-tests", "혈당·B12·갑상선·신장 검사, CT/MRI·신경전도/근전도 날짜·결과와 정보 출처를 알려주세요.", 148, "history", R),
        Q("focal_neurology.prior_treatment_splint_position_rehab_medicine_response_and_adverse_effect", "Previous Treatment and Response", "string", "prior-treatment", "자세 조절·부목·재활·약물 등 시도한 방법의 시작 시점·효과·악화·부작용을 알려주세요.", 147, "history", R),
        Q("focal_neurology.family_neuromuscular_neuropathy_stroke_clotting_and_early_death", "Family Neurological History", "string", "family-history", "가족의 근육/신경질환·뇌졸중·혈전질환과 젊은 나이의 원인불명 사망을 알려주세요.", 146, "history", R),
    ]
    rules = [
        safety_rule(P, "current-consciousness-warning", {"fact": "focal_neurology.current_unconscious_confused_or_difficult_to_wake", "equals": True}, "emergency", 1000),
        safety_rule(P, "sudden-unilateral", {"all": [{"fact": "symptom.focal_neurology.sudden_onset", "equals": True}, {"fact": "symptom.focal_neurology.one_sided", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "fast-face", {"fact": "symptom.face_droop", "equals": True}, "emergency", 1000),
        safety_rule(P, "fast-arm", {"fact": "symptom.arm_drift_or_cannot_raise", "equals": True}, "emergency", 1000),
        safety_rule(P, "fast-speech", {"fact": "symptom.speech_or_language_disturbance", "equals": True}, "emergency", 1000),
        safety_rule(P, "sudden-vision", {"all": [{"fact": "symptom.focal_neurology.sudden_onset", "equals": True}, {"fact": "symptom.sudden_visual_loss_or_field_defect", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "sudden-gait", {"all": [{"fact": "symptom.focal_neurology.sudden_onset", "equals": True}, {"fact": "symptom.sudden_gait_unsteadiness", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "resolved-within-24h", {"fact": "symptom.focal_neurology.resolved_within_24h", "equals": True}, "emergency", 1000),
        safety_rule(P, "seizure-persistent-deficit", {"fact": "focal_neurology.seizure_with_persistent_new_weakness_or_confusion", "equals": True}, "emergency", 1000),
        safety_rule(P, "trauma-new-deficit", {"fact": "focal_neurology.recent_head_spine_trauma_with_new_deficit", "equals": True}, "emergency", 1000),
        safety_rule(P, "rapid-symmetric", {"fact": "symptom.symmetric_progressive_weakness", "equals": True}, "emergency", 1000),
        safety_rule(P, "progressive-breathing", {"all": [{"fact": "symptom.symmetric_progressive_weakness", "equals": True}, {"fact": "symptom.dyspnea_at_rest_or_supine", "equals": True}]}, "emergency", 1010),
        safety_rule(P, "progressive-swallowing", {"all": [{"fact": "symptom.symmetric_progressive_weakness", "equals": True}, {"fact": "symptom.new_swallowing_impairment", "equals": True}]}, "emergency", 1010),
        safety_rule(P, "cauda-bladder", {"all": [{"fact": "symptom.severe_back_pain_radiating_leg", "equals": True}, {"fact": "symptom.new_bladder_bowel_or_sexual_dysfunction", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "cauda-saddle", {"all": [{"fact": "symptom.severe_back_pain_radiating_leg", "equals": True}, {"fact": "symptom.perineal_or_saddle_numbness", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "child-sudden-progressive", {"fact": "focal_neurology.child_sudden_or_rapid_progressive_weakness", "equals": True}, "emergency", 1000),
        safety_rule(P, "single-limb-progression", {"fact": "symptom.single_limb_rapid_progression", "equals": True}, "urgent", 900),
        safety_rule(P, "brief-fixed-sensory", {"fact": "focal_neurology.recurrent_brief_fixed_sensory_under_two_minutes", "equals": True}, "urgent", 900),
        safety_rule(P, "child-tingling-motor-autonomic", {"fact": "focal_neurology.child_tingling_with_weakness_bladder_bowel_or_gait", "equals": True}, "urgent", 900),
        safety_rule(P, "infant-hypotonia-warning", {"fact": "focal_neurology.infant_hypotonia_feeding_breathing_or_consciousness_warning", "equals": True}, "urgent", 900),
        safety_rule(P, "neck-bulbar-warning", {"all": [{"fact": "focal_neurology.neck_weakness_head_drop_or_voice_change", "equals": True}, {"fact": "symptom.new_swallowing_impairment", "equals": True}]}, "urgent", 900),
    ]
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-18", "next_monitor_at": "2026-07-19", "next_full_review_at": "2027-01-14"})
    return {"id": "knowledge.generated.focal-neurology", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-focal-weakness-numbness-research", "default_refresh": refresh, "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix="focal-weakness-numbness", fragment=f, presentation_fact="symptom.focal_neurology.current", question_budget=82, source_refs=SOURCES)
    p["required_facts"]["routine"] = [
        "focal_neurology.primary_group", "symptom.focal_neurology.main_type", "symptom.duration",
        "focal_neurology.last_known_well_and_exact_onset_date_time_place_activity_posture",
        "focal_neurology.onset_seconds_minutes_hours_and_symptom_sequence",
        "focal_neurology.continuous_episodic_frequency_duration_recovery_and_trend",
        "symptom.focal_neurology.side", "symptom.focal_neurology.region",
        "focal_neurology.exact_boundary_digits_joints_proximal_distal_and_spread",
        "focal_neurology.patient_words_and_difference_from_baseline",
        "focal_neurology.function_walk_transfer_stairs_handwriting_grip_selfcare_work_school_driving",
        "focal_neurology.prior_stroke_tia_seizure_migraine_neuropathy_spine_and_functional_diagnosis",
        "focal_neurology.prior_episode_emergency_visit_admission_diagnosis_and_baseline_recovery",
        "focal_neurology.prior_neurologic_exam_strength_reflex_sensation_gait_and_source",
        "focal_neurology.prior_glucose_b12_thyroid_renal_imaging_emg_and_source",
        "focal_neurology.prior_treatment_splint_position_rehab_medicine_response_and_adverse_effect",
        "focal_neurology.information_source_proxy_witness_reliability_record_and_conflict",
        "focal_neurology.patient_concern_goal_expectation_and_additional_comment",
    ]
    cases = {
        "sudden_unilateral": ["symptom.objective_motor_task_loss", "focal_neurology.face_eye_closure_forehead_cheek_tongue_and_drooling", "focal_neurology.arm_leg_proximal_distal_grip_foot_drop_and_fatigability", "focal_neurology.headache_dizziness_vision_speech_swallowing_hearing_and_cognition_relation", "focal_neurology.anticoagulant_antiplatelet_hormone_allergy_and_substance"],
        "recurrent_transient": ["focal_neurology.episode_fixed_pattern_spread_duration_awareness_and_post_event", "focal_neurology.gradual_reversible_five_to_sixty_minute_sensory_visual_headache_relation", "focal_neurology.headache_dizziness_vision_speech_swallowing_hearing_and_cognition_relation"],
        "progressive_symmetric": ["symptom.objective_motor_task_loss", "focal_neurology.arm_leg_proximal_distal_grip_foot_drop_and_fatigability", "focal_neurology.balance_coordination_falls_and_dexterity", "focal_neurology.diabetes_thyroid_b12_kidney_celiac_nutrition_and_alcohol_context", "focal_neurology.current_medicines_dose_schedule_adherence_recent_change_and_neurotoxic_exposure"],
        "progressive_single_limb": ["symptom.objective_motor_task_loss", "focal_neurology.arm_leg_proximal_distal_grip_foot_drop_and_fatigability", "focal_neurology.weight_loss_night_sweat_cancer_immunity_and_systemic_change", "focal_neurology.family_neuromuscular_neuropathy_stroke_clotting_and_early_death"],
        "spine_or_radicular": ["focal_neurology.pain_present", "focal_neurology.neck_back_pain_radiation_cough_movement_and_night_pattern", "focal_neurology.position_repetition_sleep_compression_tool_and_relief", "focal_neurology.balance_coordination_falls_and_dexterity"],
        "distal_symmetric": ["symptom.sensory_quality", "focal_neurology.sensory_level_stocking_glove_patch_and_provocation", "focal_neurology.diabetes_thyroid_b12_kidney_celiac_nutrition_and_alcohol_context", "focal_neurology.current_medicines_dose_schedule_adherence_recent_change_and_neurotoxic_exposure"],
        "compression_or_position": ["symptom.sensory_quality", "focal_neurology.sensory_level_stocking_glove_patch_and_provocation", "focal_neurology.position_repetition_sleep_compression_tool_and_relief", "focal_neurology.occupation_repetition_vibration_posture_heavy_lifting_chemical_and_driving"],
        "child_or_proxy": ["focal_neurology.child_age_development_regression_school_play_feeding_and_proxy", "focal_neurology.child_early_hand_preference_new_gait_backpack_crossed_legs_and_hyperventilation", "symptom.objective_motor_task_loss", "focal_neurology.information_source_proxy_witness_reliability_record_and_conflict"],
        "other_unclear": ["symptom.objective_motor_task_loss", "symptom.sensory_quality", "focal_neurology.sensory_level_stocking_glove_patch_and_provocation", "focal_neurology.balance_coordination_falls_and_dexterity", "focal_neurology.pain_present", "focal_neurology.blister_rash_fever_infection_tick_and_recent_illness", "focal_neurology.current_medicines_dose_schedule_adherence_recent_change_and_neurotoxic_exposure", "focal_neurology.occupation_repetition_vibration_posture_heavy_lifting_chemical_and_driving", "focal_neurology.pregnancy_possible_lmp_gestation_postpartum_and_complications"],
    }
    p["conditional_required_facts"] = [
        {"selector_fact": "focal_neurology.primary_group", "cases": cases},
        {"when": {"fact": "focal_neurology.pain_present", "equals": True}, "required_facts": ["focal_neurology.pain_nrs"], "reason": "associated_pain_requires_raw_nrs"},
    ]
    p["must_be_known_facts"] = ["focal_neurology.pain_nrs"]
    return p


def source_docs():
    defs = [
        ("source.nice.ng127.adult-focal-neurology.2023", "NICE", "Suspected neurological conditions — adult limb or facial weakness and sensory symptoms", "NG127-updated-2023-10-02", "https://www.nice.org.uk/guidance/ng127/chapter/Recommendations-for-adults-aged-over-16", "nice_guidance", ["Sudden restricted weakness or transient unilateral numbness requires stroke-pathway assessment; rapidly progressive symmetric weakness, bulbar or respiratory change and severe radiating back pain with bladder, bowel, sexual or saddle sensory change are time-sensitive.", "History distinguishes fixed brief sensory episodes, gradual reversible 5-to-60-minute sensory change, distal symmetric sensory change, compression, radicular and progressive patterns without assigning a diagnosis or selecting a test."]),
        ("source.nice.ng127.child-focal-neurology.2023", "NICE", "Suspected neurological conditions — child weakness and sensory symptoms", "NG127-updated-2023-10-02", "https://www.nice.org.uk/guidance/ng127/chapter/Recommendations-for-children-aged-under-16", "nice_guidance", ["Sudden or rapidly progressive child limb or facial weakness and new gait abnormality require immediate assessment; tingling with weakness, bladder or bowel dysfunction needs urgent neurological assessment.", "The child or proxy handoff records development, regression, feeding, breathing, function, compression context and source reliability without diagnosing a paediatric neurological disorder."]),
        ("source.nhs.stroke.2026", "NHS", "Symptoms of a stroke", "current-2026", "https://www.nhs.uk/conditions/stroke/symptoms/", "public_health_guidance", ["Sudden face weakness, arm weakness and speech difficulty are emergency warning features; sudden vision change, confusion, dizziness, falling and severe headache may also occur.", "Symptoms that stop still require emergency assessment; the interview does not diagnose stroke or TIA."]),
        ("source.stom.focal.20260714", "Infoclinic", "STOM focal neurology terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/26544005", "terminology_server", ["STOM confirmed Muscle weakness, Numbness and Paresthesia focus concepts with Finding site and Severity permitted in the queried MRCM summaries.", "MRCM is Build-Time terminology metadata only and has no authority over clinical questions, urgency or diagnosis."]),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, assertions in defs:
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-18" if publisher == "NICE" else "2026-07-14", "monitor_result": "current_official_source_confirmed" if publisher == "NICE" else "not_due_existing_metadata_preserved", "assertions": assertions})
    research = {"id": "source-manifest.primary-care-focal-weakness-numbness-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.focal", "generated_clinical_knowledge", "knowledge/generated/neurological/focal-weakness-numbness/focal-weakness-numbness.json", True), ("source.mapping.focal", "terminology_mapping", "mappings/terminology/snomed-mrcm-focal-weakness-numbness.json", False), ("source.external.focal", "external_source_manifest", "sources/manifests/primary-care-focal-weakness-numbness-research.json", False), ("source.policy.focal", "runtime_policy", "policies/primary-care-focal-weakness-numbness-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-focal-weakness-numbness", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    forbidden = ["diagnosis.stroke", "diagnosis.tia", "diagnosis.guillain_barre", "diagnosis.cauda_equina", "diagnosis.epilepsy", "diagnosis.migraine", "diagnosis.radiculopathy", "diagnosis.peripheral_neuropathy"]
    for index, rule in enumerate(f["safety_rules"]):
        key, level, condition = rule["id"].split("safety.")[1], rule["then"]["safety_level"], rule["when"]
        children = condition.get("all", [condition])
        state = {child["fact"]: {"value": child.get("equals", True)} for child in children}
        out[f"FOCAL-{key.upper()}.json"] = {"id": f"FOCAL-{key.upper()}", "simulation_language": "ko", "persona": {"age": 8 if "child" in key else (0 if "infant" in key else 24 + index * 3)}, "initial_statement": {"ko": "특정 부위의 힘 또는 감각 변화로 진료 전 문진을 합니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 42, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}

    policy = completion(f)
    always, base, branches = policy["required_facts"]["always"], policy["required_facts"]["routine"], policy["conditional_required_facts"][0]["cases"]
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}

    def routine(branch):
        values = {}
        for fid in dict.fromkeys([*always, *base, *branches[branch]]):
            fact = by_id[fid]
            if fact["value_type"] == "boolean": value = False
            elif fact["value_type"] == "coded": value = fact.get("allowed_values", ["unclear"])[-1]
            elif fact["value_type"] == "integer": value = 3
            elif fact["value_type"] == "quantity": value = "2 weeks"
            else: value = "특이사항 없음"
            values[fid] = {"value": value}
        values["symptom.focal_neurology.current"] = {"value": True}
        values["focal_neurology.primary_group"] = {"value": branch}
        return values

    specs = [
        ("TRANSIENT-GRADUAL", "recurrent_transient", 29, "손 저림이 서서히 퍼졌다가 완전히 회복되는 일이 반복됩니다.", {"focal_neurology.gradual_reversible_five_to_sixty_minute_sensory_visual_headache_relation": {"value": "10분에 걸쳐 퍼져 30분 후 회복, 두통 여부 확인 필요"}}),
        ("PROGRESSIVE-SYMMETRIC", "progressive_symmetric", 67, "양쪽 발끝 감각과 다리 힘이 서서히 달라졌습니다.", {"focal_neurology.sensory_level_stocking_glove_patch_and_provocation": {"value": "양쪽 발끝부터 양말 모양"}}),
        ("SINGLE-LIMB", "progressive_single_limb", 58, "오른손 힘이 며칠 동안 조금씩 약해졌습니다.", {"symptom.focal_neurology.side": {"value": "right"}, "symptom.objective_motor_task_loss": {"value": "컵과 열쇠를 놓침"}}),
        ("SPINE-PAIN-NRS", "spine_or_radicular", 44, "허리에서 다리로 뻗치는 통증과 저림이 있습니다.", {"focal_neurology.pain_present": {"value": True}, "focal_neurology.pain_nrs": {"value": 6}, "focal_neurology.neck_back_pain_radiation_cough_movement_and_night_pattern": {"value": "허리에서 오른쪽 종아리로 뻗침"}}),
        ("DISTAL-POLYPHARMACY", "distal_symmetric", 76, "여러 약을 복용하는 고령자의 양쪽 손발 저림을 정리합니다.", {"focal_neurology.current_medicines_dose_schedule_adherence_recent_change_and_neurotoxic_exposure": {"value": "처방전 목록 확인 필요, 최근 변경 여부 불확실"}}),
        ("OCCUPATIONAL-COMPRESSION", "compression_or_position", 41, "반복 작업 뒤 특정 손가락이 저립니다.", {"focal_neurology.position_repetition_sleep_compression_tool_and_relief": {"value": "손목 굽힌 작업 뒤 발생, 자세 변경 후 10분 내 호전"}}),
        ("CHILD-PROXY", "child_or_proxy", 11, "보호자가 아이의 간헐적 다리 저림을 설명합니다.", {"focal_neurology.child_age_development_regression_school_play_feeding_and_proxy": {"value": "11세, 퇴행 없음, 보호자 관찰"}, "focal_neurology.information_source_proxy_witness_reliability_record_and_conflict": {"value": "보호자 답변, 아이 본인 확인 필요"}}),
        ("PREGNANCY-MULTI-RFE", "other_unclear", 33, "임신 중 손 저림 외에 두통도 별도 문진하고 싶습니다.", {"focal_neurology.pregnancy_possible_lmp_gestation_postpartum_and_complications": {"value": "임신 24주, 알려진 합병증 없음"}, "focal_neurology.patient_concern_goal_expectation_and_additional_comment": {"value": "두통을 별도 RFE로 전달 요청"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine(branch); state.update(overrides)
        if state.get("focal_neurology.pain_present", {}).get("value") is True:
            state.setdefault("focal_neurology.pain_nrs", {"value": 6})
        expected = {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 105, "forbidden_assertions": forbidden}
        if key == "SPINE-PAIN-NRS": expected["expected_known_facts"] = {"focal_neurology.pain_nrs": 6}
        out[f"FOCAL-{key}.json"] = {"id": f"FOCAL-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": state, "expected": expected, "provenance": provenance(SOURCES)}
    absent = routine("other_unclear")
    missing = "focal_neurology.prior_glucose_b12_thyroid_renal_imaging_emg_and_source"
    absent.pop(missing)
    out["FOCAL-REMOTE-DATA-ABSENT.json"] = {"id": "FOCAL-REMOTE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 82}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "보호자가 고령자의 감각 변화를 설명하며 이전 검사자료는 없습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {missing: "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 105, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Focal Weakness, Numbness or Tingling", intents=[("intent.characterize_symptom", "Characterize Exact Onset Course Distribution Motor Sensory and Functional Change"), ("intent.screen_red_flags", "Screen Cerebrovascular Consciousness Neuromuscular Respiratory Bulbar Spinal Trauma and Paediatric Warning Features"), ("intent.differentiate_common_causes", "Describe Episodic Progressive Spine Distal Compression Systemic Medicine and Life-stage Context"), ("intent.risk_assessment", "Assess History Medicines Prior Evaluation Treatment Source Reliability and Patient Goals")])
    primary, research = source_docs()
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": code, "display": display, "concept_active": True} for code, display in [("26544005", "Muscle weakness (finding)"), ("44077006", "Numbness (finding)"), ("91019004", "Paresthesia (finding)")]], "checks": [{"focus_code": code, "attribute_code": attribute, "allowed": True} for code in ("26544005", "44077006", "91019004") for attribute in ("363698007", "246112005")], "laterality": {"reference_set": "723264001", "postcoordination_allowed_only_after_build_time_member_validation": True, "postcoordination_asserted": False}, "validation": {"method": "build_time_live_mrcm_summary", "checked_at": "2026-07-14T00:00:00Z", "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "focal_neurology_semantics": {"diagnosis_inferred": False, "stroke_diagnosed": False, "tia_diagnosed": False, "epilepsy_diagnosed": False, "migraine_diagnosed": False, "guillain_barre_diagnosed": False, "cauda_equina_diagnosed": False, "radiculopathy_diagnosed": False, "peripheral_neuropathy_diagnosed": False, "test_selected_or_ordered": False, "runtime_terminology_query_required": False}, "provenance": provenance(["source.stom.focal.20260714"])}
    docs = [("knowledge/base/primary-care-focal-weakness-numbness.json", graph), ("rules/base/primary-care-focal-weakness-numbness.json", rules), ("knowledge/generated/neurological/focal-weakness-numbness/focal-weakness-numbness.json", f), ("mappings/terminology/snomed-mrcm-focal-weakness-numbness.json", mapping), ("sources/manifests/primary-care-focal-weakness-numbness.json", primary), ("sources/manifests/primary-care-focal-weakness-numbness-research.json", research), ("policies/primary-care-focal-weakness-numbness-completion.json", completion(f))]
    for path, document in docs: write_json(path, document)
    target = ROOT / "simulation/patients/neurological/focal-weakness-numbness"
    for old in target.glob("*.json"): old.unlink()
    for name, case in cases(f).items(): write_json("simulation/patients/neurological/focal-weakness-numbness/" + name, case)


if __name__ == "__main__":
    main()
