#!/usr/bin/env python3
"""Materialize unreviewed gait, falls-risk and post-fall knowledge."""
from profile_support import *

P, RFE = "gait-falls-concern", "rfe.gait_falls_concern"
M, SN = "mapping.snomed-mrcm.gait-falls-concern", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-16T00:00:00Z"
SOURCES = ["source.nice.ng249.2025", "source.cdc.steadi.2025", "source.nice.ng232.2025", "source.stom.gait-falls.20260716"]
G = {k: f"group.falls.{k}" for k in ("routing", "safety", "event", "gait", "contributors", "function")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("falls.primary_group", "Primary Gait or Falls Presentation", "coded", "primary-group", "이번 방문은 최근 한 번 넘어진 뒤 평가, 반복 낙상, 넘어지지는 않았지만 보행·균형 변화, 넘어질까 두려움·아찔한 순간, 낙상 손상 추적, 기존 신경·이동장애 추적 중 무엇에 가깝나요?", 195, [G["routing"]], C, allowed_values=["recent_single_fall", "recurrent_falls", "gait_balance_change_without_fall", "fear_or_near_falls", "post_fall_injury_followup", "known_mobility_condition_followup", "other_unclear"]),
        Q("falls.current_unable_to_stand_or_walk_after_fall", "Unable to Stand or Walk after Fall", "boolean", "unable-walk", "넘어진 뒤 지금 체중을 싣거나 서거나 걷지 못하나요?", 194, [G["safety"]], S, safety_relevant=True),
        Q("falls.major_bleeding_deformity_or_open_fracture", "Major Injury Warning", "boolean", "major-injury", "지혈되지 않는 심한 출혈, 뼈가 보이는 상처, 팔다리 변형 또는 고관절·골반 골절이 의심되는 심한 통증이 있나요?", 193, [G["safety"]], S, safety_relevant=True),
        Q("falls.head_injury_reduced_consciousness_vomiting_or_seizure", "Serious Head Injury Warning", "boolean", "head-warning", "머리를 부딪힌 뒤 깨우기 어렵거나 의식이 흐림, 반복 구토, 경련 또는 점점 심해지는 두통이 있나요?", 192, [G["safety"]], S, safety_relevant=True),
        Q("falls.head_impact_with_anticoagulant_or_bleeding_risk", "Head Impact with Bleeding Risk", "boolean", "head-anticoagulant", "머리를 부딪혔고 항응고제·일부 항혈소판제를 복용하거나 출혈·응고 질환이 있나요?", 191, [G["safety"], G["contributors"]], S, safety_relevant=True),
        Q("falls.new_focal_neurologic_deficit_or_severe_ataxia", "Acute Neurologic Warning", "boolean", "neuro-warning", "새로 한쪽 힘 빠짐·감각저하·말 또는 시야 변화, 얼굴 처짐, 갑자기 걷기 어려운 심한 균형장애가 있나요?", 190, [G["safety"]], S, safety_relevant=True),
        Q("falls.syncope_chest_pain_palpitations_or_breathlessness", "Cardiovascular Fall Warning", "boolean", "cardiac-warning", "넘어지기 직전 또는 현재 실신, 흉통, 심한 두근거림이나 숨참이 있나요?", 189, [G["safety"], G["event"]], S, safety_relevant=True),
        Q("falls.spinal_injury_with_weakness_numbness_or_sphincter_change", "Possible Spinal Injury Warning", "boolean", "spinal-warning", "목·등·허리를 다친 뒤 새 팔다리 마비·저림, 회음부 감각저하 또는 소변·대변 조절 변화가 있나요?", 188, [G["safety"]], S, safety_relevant=True),
        Q("falls.acute_confusion_fever_or_severe_illness", "Acute Illness or Delirium Warning", "boolean", "acute-illness", "갑자기 평소와 다르게 혼란스럽거나 고열·심한 쇠약과 함께 잇따라 넘어졌나요?", 187, [G["safety"], G["contributors"]], S, safety_relevant=True),
        Q("falls.prolonged_time_on_floor_or_cold_exposure", "Prolonged Time on Floor", "boolean", "long-lie", "넘어진 뒤 오래 일어나지 못했거나 구조를 요청하지 못해 추위·탈수·압박 손상이 걱정되나요?", 186, [G["safety"], G["event"]], S, safety_relevant=True),
        Q("falls.possible_hypoglycemia_overdose_or_intoxication", "Metabolic or Toxic Fall Warning", "boolean", "metabolic-toxic", "저혈당이 의심되거나 약물 과량, 술·중독물질 영향 속에서 넘어지고 아직 평소 상태가 아닌가요?", 185, [G["safety"], G["contributors"]], S, safety_relevant=True),
        Q("falls.pregnancy_fall_with_bleeding_pain_or_reduced_movement", "Pregnancy Fall Warning", "boolean", "pregnancy-warning", "임신 중 넘어졌고 질출혈·복통·양수 같은 분비물 또는 평소보다 태동 감소가 있나요?", 184, [G["safety"]], S, safety_relevant=True),
        Q("falls.repeated_falls_with_acute_deterioration", "Repeated Falls with Acute Deterioration", "boolean", "repeated-acute", "오늘 여러 번 넘어졌거나 짧은 기간에 급격히 늘면서 매번 평소 상태로 회복되지 않나요?", 183, [G["safety"], G["event"]], S, safety_relevant=True),
        Q("falls.safeguarding_assault_or_unsafe_home_concern", "Safeguarding Concern", "boolean", "safeguarding", "누군가 밀거나 다치게 했을 가능성, 돌봄 방임 또는 집에 돌아가면 안전하지 않을 우려가 있나요?", 182, [G["safety"], G["function"]], S, safety_relevant=True),

        Q("falls.information_source_witness_and_reliability", "Information Source and Witness", "string", "witness", "내용은 본인 기억, 목격자·보호자 설명, 영상·기기 기록 중 무엇에 근거하며 목격자와 연락할 수 있나요?", 170, [G["event"]], C),
        Q("falls.event_date_time_place_activity_and_posture", "Fall Circumstances", "string", "circumstances", "넘어진 날짜·시각·장소, 당시 하던 일과 앉음·섬·걸음 등 자세를 알려주세요.", 169, [G["event"]], C),
        Q("falls.mechanism_direction_height_and_surface", "Fall Mechanism", "string", "mechanism", "미끄러짐·걸림·균형 상실·다리 풀림 중 무엇 같았나요? 넘어진 방향, 계단·높이, 바닥 상태도 알려주세요.", 168, [G["event"]], C),
        Q("falls.prodrome_dizziness_vision_nausea_or_weakness", "Symptoms Before Fall", "string", "prodrome", "직전 어지럼, 시야 흐림, 식은땀, 메스꺼움, 갑작스러운 힘 빠짐 또는 아무 예고가 없었는지 알려주세요.", 167, [G["event"]], C),
        Q("falls.loss_of_consciousness_amnesia_and_recovery", "Awareness and Recovery", "string", "awareness", "의식을 잃었거나 사건 전후 기억 공백이 있었나요? 평소 상태로 돌아오는 데 얼마나 걸렸나요?", 166, [G["event"]], C, terminology_binding={"system": SN, "code": "419045004"}, mrcm_ref=M),
        Q("falls.head_impact_and_landed_body_sites", "Impact Sites", "string", "impact-sites", "머리를 부딪혔는지와 바닥에 먼저 닿거나 다친 신체 부위, 왼쪽·오른쪽을 알려주세요.", 165, [G["event"]], C),
        Q("falls.assistance_to_rise_and_floor_time", "Ability to Rise and Floor Time", "string", "rise-floor-time", "스스로 일어났나요, 도움이 필요했나요? 바닥에 있었던 시간과 도움을 부른 방법을 알려주세요.", 164, [G["event"], G["function"]], C),
        Q("falls.current_injury_sites_swelling_bruising_and_function", "Current Injury Details", "string", "injury-detail", "현재 아픈·붓거나 멍든·출혈하는 부위와 움직임 또는 체중 부하 제한을 알려주세요.", 163, [G["event"]], C),
        Q("falls.current_injury_pain_present", "Current Injury Pain Present", "boolean", "pain-present", "낙상이나 보행 문제와 관련된 현재 통증이 있나요?", 162, [G["event"]], C),
        Q("falls.current_injury_pain_nrs", "Current Injury Pain NRS", "integer", "pain-nrs", "[필수] 현재 통증을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 161, [G["event"]], C),
        Q("falls.falls_and_near_falls_last_twelve_months", "Falls in Last Twelve Months", "string", "fall-history", "지난 12개월 동안 실제 낙상과 넘어질 뻔한 일이 각각 몇 번이었고 가장 최근은 언제였나요?", 160, [G["event"], G["gait"]], R, terminology_binding={"system": SN, "code": "161898004"}, mrcm_ref=M),
        Q("falls.prior_fall_injuries_treatment_and_fractures", "Prior Fall Injuries", "string", "prior-injuries", "이전 낙상으로 골절·머리 손상·응급실 방문·입원·수술을 받은 적과 날짜를 알려주세요.", 159, [G["event"]], R),

        Q("falls.gait_balance_onset_course_and_variability", "Gait Change Course", "string", "gait-course", "걷기·균형 변화가 언제 시작되어 갑자기인지 서서히인지, 지속·악화·변동 여부를 알려주세요.", 158, [G["gait"]], C, terminology_binding={"system": SN, "code": "22325002"}, mrcm_ref=M),
        Q("falls.gait_pattern_and_laterality", "Gait Pattern and Laterality", "string", "gait-pattern", "종종걸음·발 끌림·보폭 넓어짐·한쪽 쏠림·발이 붙는 느낌·발 처짐 중 무엇이며 어느 쪽인지 알려주세요.", 157, [G["gait"]], C),
        Q("falls.triggers_turning_stairs_darkness_and_dual_task", "Gait Triggers", "string", "gait-triggers", "일어나기, 방향 전환, 계단, 울퉁불퉁한 길, 어두운 곳, 말하거나 물건을 들고 걸을 때 더 불안한가요?", 156, [G["gait"]], D),
        Q("falls.walking_distance_speed_endurance_and_rest", "Walking Capacity", "string", "walking-capacity", "도움 없이 걸을 수 있는 거리·시간, 속도와 쉬어야 하는 이유가 이전과 어떻게 달라졌나요?", 155, [G["gait"], G["function"]], R),
        Q("falls.mobility_aid_type_fit_and_use", "Mobility Aid Use", "string", "mobility-aid", "지팡이·보행기·휠체어 등 보조기구 종류, 사용 시기, 맞춤 점검 여부와 실제 사용 문제를 알려주세요.", 154, [G["gait"], G["function"]], R),
        Q("falls.transfers_standing_chair_and_stairs", "Transfers and Stairs", "string", "transfers", "침대·의자·변기에서 일어나기, 오래 서기와 계단 이용에 손잡이 또는 사람 도움이 필요한가요?", 153, [G["gait"], G["function"]], R),
        Q("falls.fear_confidence_and_activity_restriction", "Concern about Falling", "string", "fear", "넘어질까 걱정되는 정도와 그 때문에 외출·운동·목욕·일상활동을 줄였는지 알려주세요.", 152, [G["gait"], G["function"]], R, terminology_binding={"system": SN, "code": "129839007"}, mrcm_ref=M),
        Q("falls.baseline_mobility_and_recent_functional_change", "Baseline Mobility", "string", "baseline", "문제 전 평소 보행·균형·독립 수준과 현재 달라진 점을 알려주세요.", 151, [G["gait"], G["function"]], R),
        Q("falls.prior_gait_balance_assessment_and_therapy", "Previous Gait Assessment", "string", "prior-assessment", "이전에 보행·균형 검사, 기립혈압, 재활·물리·작업치료 또는 낙상예방 교육을 받은 결과를 알려주세요.", 150, [G["gait"]], R),

        Q("falls.orthostatic_symptoms_and_lying_standing_bp", "Orthostatic Context", "string", "orthostatic", "누웠다·앉았다 일어날 때 어지럽거나 쓰러질 듯한가요? 가능하면 누운·선 혈압과 측정 시각을 알려주세요.", 149, [G["contributors"]], D),
        Q("falls.cardiac_history_and_rhythm_evaluation", "Cardiac Context", "string", "cardiac-context", "부정맥·심장질환·실신 병력과 최근 심전도·심장검사 결과를 알려주세요.", 148, [G["contributors"]], D),
        Q("falls.weakness_stiffness_tremor_numbness_and_coordination", "Neurologic and Musculoskeletal Symptoms", "string", "neuro-msk", "근력 저하·경직·떨림·저림·감각 둔함·협응 저하 또는 관절 통증이 있나요? 부위와 좌우를 알려주세요.", 147, [G["contributors"]], D),
        Q("falls.vertigo_hearing_and_vestibular_features", "Vestibular and Hearing Context", "string", "vestibular", "빙글 도는 어지럼, 머리 움직임과의 관계, 귀 먹먹함·이명·청력 변화를 알려주세요.", 146, [G["contributors"]], D),
        Q("falls.vision_change_glasses_and_last_eye_check", "Vision Context", "string", "vision", "시력·복시·시야 문제, 안경 사용과 최근 안과·시력검사 결과를 알려주세요.", 145, [G["contributors"]], D),
        Q("falls.foot_pain_numbness_deformity_and_footwear", "Feet and Footwear", "string", "feet-footwear", "발 통증·저림·상처·변형과 평소 신발·슬리퍼의 맞음과 미끄러짐을 알려주세요.", 144, [G["contributors"]], D),
        Q("falls.cognition_mood_delirium_and_attention_change", "Cognition and Mood", "string", "cognition-mood", "최근 기억·집중·판단·기분 변화 또는 갑작스러운 혼란이 있었는지 보호자 관찰과 함께 알려주세요.", 143, [G["contributors"]], D),
        Q("falls.urinary_urgency_nocturia_and_continence", "Continence Context", "string", "continence", "급하게 소변을 보러 가거나 밤중 배뇨, 실금 때문에 서두르다 불안정해지는 일이 있나요?", 142, [G["contributors"]], D),
        Q("falls.diet_fluids_weight_loss_and_frailty_context", "Nutrition and Frailty Context", "string", "nutrition", "식사·수분 섭취, 최근 체중 감소, 근력·활동 감소와 전반적인 쇠약 변화를 알려주세요.", 141, [G["contributors"]], R),
        Q("falls.current_medicines_doses_and_adherence", "Current Medicines", "string", "medicines", "처방약·일반약·한약·보충제의 이름·용량·횟수와 실제 복용 방법을 알려주세요.", 140, [G["contributors"]], R),
        Q("falls.sedating_bp_glucose_and_recent_medicine_changes", "Fall-related Medicine Context", "string", "medicine-risk", "수면·진정제, 정신건강약, 혈압약·이뇨제, 혈당약과 최근 시작·중단·증량·누락 여부를 알려주세요.", 139, [G["contributors"]], R),
        Q("falls.alcohol_substance_and_intoxication_context", "Alcohol and Substance Context", "string", "substance", "음주 빈도·양·마지막 음주와 대마·진정물질 등 사용이 낙상 시점과 관련 있었는지 알려주세요.", 138, [G["contributors"]], D),
        Q("falls.long_term_conditions_and_previous_neurologic_disease", "Relevant Conditions", "string", "conditions", "뇌졸중·파킨슨병·치매·당뇨·관절질환·골다공증·전정질환 등 보행과 골절 위험에 관련된 진단을 알려주세요.", 137, [G["contributors"]], R),
        Q("falls.osteoporosis_fragility_fracture_and_bone_health", "Bone Health", "string", "bone-health", "골다공증·작은 충격 골절, 골밀도검사와 뼈 건강 치료 이력을 알려주세요.", 136, [G["contributors"]], R),

        Q("falls.home_hazards_lighting_rugs_bathroom_and_stairs", "Home Hazards", "string", "home-hazards", "집의 조명, 전선·카펫, 미끄러운 욕실, 문턱·계단·손잡이 등 넘어질 위험과 개선 여부를 알려주세요.", 130, [G["function"]], R),
        Q("falls.living_arrangement_support_and_alarm", "Support and Emergency Access", "string", "support", "혼자 사는지, 일상 도움을 주는 사람과 비상호출기·전화 접근, 넘어졌을 때 도움받는 계획을 알려주세요.", 129, [G["function"]], R),
        Q("falls.adl_bathing_toileting_dressing_and_meals", "Activities of Daily Living", "string", "adl", "목욕·화장실·옷 입기·식사 준비·약 관리에 어느 정도 도움이 필요한가요?", 128, [G["function"]], R),
        Q("falls.driving_work_heights_and_community_mobility", "Driving and Occupational Safety", "string", "driving-work", "운전, 고소·기계 작업, 통근·장보기 등에서 보행 문제가 안전과 역할에 미친 영향을 알려주세요.", 127, [G["function"]], R),
        Q("falls.patient_goal_priority_and_other_detail", "Patient Goal and Other Detail", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달할 내용, 가장 걱정되는 점과 진료에서 원하는 도움을 알려주세요.", 80, [G["routing"], G["function"]], C),
    ]
    safety = [
        ("unable-walk", "falls.current_unable_to_stand_or_walk_after_fall", "emergency"),
        ("major-injury", "falls.major_bleeding_deformity_or_open_fracture", "emergency"),
        ("head-warning", "falls.head_injury_reduced_consciousness_vomiting_or_seizure", "emergency"),
        ("head-anticoagulant", "falls.head_impact_with_anticoagulant_or_bleeding_risk", "urgent"),
        ("neuro-warning", "falls.new_focal_neurologic_deficit_or_severe_ataxia", "emergency"),
        ("cardiac-warning", "falls.syncope_chest_pain_palpitations_or_breathlessness", "emergency"),
        ("spinal-warning", "falls.spinal_injury_with_weakness_numbness_or_sphincter_change", "emergency"),
        ("acute-illness", "falls.acute_confusion_fever_or_severe_illness", "urgent"),
        ("long-lie", "falls.prolonged_time_on_floor_or_cold_exposure", "urgent"),
        ("metabolic-toxic", "falls.possible_hypoglycemia_overdose_or_intoxication", "emergency"),
        ("pregnancy-warning", "falls.pregnancy_fall_with_bleeding_pain_or_reduced_movement", "emergency"),
        ("repeated-acute", "falls.repeated_falls_with_acute_deterioration", "urgent"),
        ("safeguarding", "falls.safeguarding_assault_or_unsafe_home_concern", "urgent"),
    ]
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, 1000 if level == "emergency" else 990) for key, fid, level in safety]
    return {"id": "knowledge.generated.gait-falls-concern", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-gait-falls-concern-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="falls.primary_group", question_budget=78, source_refs=SOURCES)
    common = ["falls.information_source_witness_and_reliability", "falls.event_date_time_place_activity_and_posture", "falls.mechanism_direction_height_and_surface", "falls.prodrome_dizziness_vision_nausea_or_weakness", "falls.loss_of_consciousness_amnesia_and_recovery", "falls.head_impact_and_landed_body_sites", "falls.assistance_to_rise_and_floor_time", "falls.current_injury_sites_swelling_bruising_and_function", "falls.current_injury_pain_present", "falls.current_injury_pain_nrs", "falls.falls_and_near_falls_last_twelve_months", "falls.gait_balance_onset_course_and_variability", "falls.gait_pattern_and_laterality", "falls.walking_distance_speed_endurance_and_rest", "falls.mobility_aid_type_fit_and_use", "falls.fear_confidence_and_activity_restriction", "falls.baseline_mobility_and_recent_functional_change", "falls.orthostatic_symptoms_and_lying_standing_bp", "falls.weakness_stiffness_tremor_numbness_and_coordination", "falls.vertigo_hearing_and_vestibular_features", "falls.vision_change_glasses_and_last_eye_check", "falls.foot_pain_numbness_deformity_and_footwear", "falls.current_medicines_doses_and_adherence", "falls.sedating_bp_glucose_and_recent_medicine_changes", "falls.long_term_conditions_and_previous_neurologic_disease", "falls.home_hazards_lighting_rugs_bathroom_and_stairs", "falls.living_arrangement_support_and_alarm", "falls.patient_goal_priority_and_other_detail"]
    cases = {
        "recent_single_fall": ["falls.prior_fall_injuries_treatment_and_fractures", "falls.cardiac_history_and_rhythm_evaluation", "falls.osteoporosis_fragility_fracture_and_bone_health"],
        "recurrent_falls": ["falls.prior_fall_injuries_treatment_and_fractures", "falls.triggers_turning_stairs_darkness_and_dual_task", "falls.transfers_standing_chair_and_stairs", "falls.cognition_mood_delirium_and_attention_change", "falls.urinary_urgency_nocturia_and_continence", "falls.diet_fluids_weight_loss_and_frailty_context", "falls.alcohol_substance_and_intoxication_context", "falls.osteoporosis_fragility_fracture_and_bone_health", "falls.adl_bathing_toileting_dressing_and_meals"],
        "gait_balance_change_without_fall": ["falls.triggers_turning_stairs_darkness_and_dual_task", "falls.transfers_standing_chair_and_stairs", "falls.prior_gait_balance_assessment_and_therapy", "falls.cardiac_history_and_rhythm_evaluation", "falls.cognition_mood_delirium_and_attention_change", "falls.adl_bathing_toileting_dressing_and_meals", "falls.driving_work_heights_and_community_mobility"],
        "fear_or_near_falls": ["falls.triggers_turning_stairs_darkness_and_dual_task", "falls.transfers_standing_chair_and_stairs", "falls.prior_gait_balance_assessment_and_therapy", "falls.adl_bathing_toileting_dressing_and_meals"],
        "post_fall_injury_followup": ["falls.prior_fall_injuries_treatment_and_fractures", "falls.osteoporosis_fragility_fracture_and_bone_health", "falls.adl_bathing_toileting_dressing_and_meals", "falls.driving_work_heights_and_community_mobility"],
        "known_mobility_condition_followup": ["falls.triggers_turning_stairs_darkness_and_dual_task", "falls.transfers_standing_chair_and_stairs", "falls.prior_gait_balance_assessment_and_therapy", "falls.cognition_mood_delirium_and_attention_change", "falls.diet_fluids_weight_loss_and_frailty_context", "falls.adl_bathing_toileting_dressing_and_meals", "falls.driving_work_heights_and_community_mobility"],
        "other_unclear": ["falls.patient_goal_priority_and_other_detail"],
    }
    p["required_facts"]["routine"], p["conditional_required_facts"] = common, [{"selector_fact": "falls.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nice.ng249.2025", "NICE", "Falls: assessment and prevention in older people and in people 50 and over at higher risk", "NG249; updated-2025-05", "https://www.nice.org.uk/guidance/ng249", "nice_guidance", ["A comprehensive falls assessment may include alcohol, lying and standing blood pressure, cognition and mood, diet and weight loss, dizziness, feet and footwear, function and concern about falling, gait and strength, hearing, long-term conditions, medicines, neurology, osteoporosis, continence and vision.", "People with injury requiring treatment, loss of consciousness, inability to rise independently or two or more falls in a year need comprehensive assessment; this package records those features without calculating a predictive score."]),
        ("source.cdc.steadi.2025", "CDC", "STEADI algorithm for fall risk screening, assessment, and intervention", "official-web-2025", "https://www.cdc.gov/steadi/", "public_health_guidance", ["Primary-care screening asks about a fall in the past year, unsteadiness and worry about falling, followed by assessment of modifiable risk factors.", "STEADI applies to community-dwelling adults 65 years and older; its age scope is not generalized into a diagnosis or universal risk threshold."]),
        ("source.nice.ng232.2025", "NICE", "Head injury: assessment and early management", "NG232; updated-2025-03", "https://www.nice.org.uk/guidance/ng232", "nice_guidance", ["After head injury, altered consciousness, focal deficit, seizure, persistent headache, vomiting, amnesia and anticoagulant or qualifying antiplatelet treatment are relevant urgent assessment features."]),
        ("source.stom.gait-falls.20260716", "Infoclinic", "STOM gait and falls terminology lookup", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["FHIR lookup confirmed active abnormal-gait, falls, increased-risk-for-falls, loss-of-consciousness and syncope concepts in the 20260701 international edition.", "Terminology and MRCM support semantic binding only and do not calculate risk or determine urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-16", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-gait-falls-concern-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.gait-falls", "generated_clinical_knowledge", "knowledge/generated/neurology/gait-falls-concern/gait-falls-concern.json", True), ("source.mapping.gait-falls", "terminology_mapping", "mappings/terminology/snomed-mrcm-gait-falls-concern.json", False), ("source.external.gait-falls", "external_source_manifest", "sources/manifests/primary-care-gait-falls-concern-research.json", False), ("source.policy.gait-falls", "runtime_policy", "policies/primary-care-gait-falls-concern-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-gait-falls-concern", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level, key = rule["when"]["fact"], rule["then"]["safety_level"], rule["id"].split("safety.")[1]
        out[f"FALLS-{key.upper()}.json"] = {"id": f"FALLS-{key.upper()}", "simulation_language": "ko", "persona": {"age": 35 + i}, "initial_statement": {"ko": "넘어졌거나 걷기가 불안해요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 45, "forbidden_assertions": ["diagnosis.stroke", "diagnosis.syncope", "diagnosis.fracture"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    by_id = {x["fact"]["id"]: x["fact"] for x in f["entries"]}

    def routine_hidden(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"][branch])
        values = {}
        for fid in required:
            fact = by_id[fid]
            values[fid] = {"value": False if fact["value_type"] == "boolean" else 0 if fact["value_type"] == "integer" else fact.get("allowed_values", ["없음"])[0] if fact["value_type"] == "coded" else "없음"}
        values["falls.primary_group"] = {"value": branch}
        return values

    recurrent = routine_hidden("recurrent_falls")
    recurrent["falls.falls_and_near_falls_last_twelve_months"] = {"value": "지난 1년 2회 낙상, 최근 3주 전; 넘어질 뻔한 일 주 1회"}
    recurrent["falls.current_injury_pain_nrs"] = {"value": 0}
    out["FALLS-RECURRENT-COMPREHENSIVE-ROUTINE.json"] = {"id": "FALLS-RECURRENT-COMPREHENSIVE-ROUTINE", "simulation_language": "ko", "persona": {"age": 74}, "initial_statement": {"ko": "최근 자꾸 넘어져서 진료 전 문진을 작성합니다."}, "hidden_state": recurrent, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"falls.current_injury_pain_nrs": 0}, "expected_max_turns": 82, "forbidden_assertions": ["diagnosis.high_fall_risk", "diagnosis.parkinson_disease"]}, "provenance": provenance(SOURCES)}

    ambiguous = routine_hidden("recent_single_fall")
    ambiguous.pop("falls.information_source_witness_and_reliability")
    ambiguous.pop("falls.assistance_to_rise_and_floor_time")
    out["FALLS-AMBIGUOUS-UNWITNESSED-DATA-ABSENT.json"] = {"id": "FALLS-AMBIGUOUS-UNWITNESSED-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 68}, "initial_statement": {"ko": "혼자 있다 넘어졌는데 자세한 상황은 잘 모르겠어요."}, "hidden_state": ambiguous, "response_behavior": {"falls.information_source_witness_and_reliability": {"dataAbsentReason": "asked-unknown"}, "falls.assistance_to_rise_and_floor_time": {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {"falls.information_source_witness_and_reliability": "asked-unknown", "falls.assistance_to_rise_and_floor_time": "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 82, "forbidden_assertions": ["diagnosis.syncope", "diagnosis.mechanical_fall"]}, "provenance": provenance(SOURCES)}

    boundary = routine_hidden("fear_or_near_falls")
    boundary["falls.falls_and_near_falls_last_twelve_months"] = {"value": "실제 낙상 0회, 지난달 두 번 휘청거림"}
    out["FALLS-BOUNDARY-NEAR-FALL-NO-INJURY.json"] = {"id": "FALLS-BOUNDARY-NEAR-FALL-NO-INJURY", "simulation_language": "ko", "persona": {"age": 61}, "initial_statement": {"ko": "넘어지지는 않았지만 자꾸 휘청거려요."}, "hidden_state": boundary, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_selected_facts_contains": ["falls.fear_confidence_and_activity_restriction"], "expected_max_turns": 82, "forbidden_assertions": ["diagnosis.fall", "diagnosis.high_fall_risk"]}, "provenance": provenance(SOURCES)}

    proxy = routine_hidden("known_mobility_condition_followup")
    proxy["falls.information_source_witness_and_reliability"] = {"value": "보호자가 영상통화로 답변하며 최근 보행을 직접 관찰함"}
    out["FALLS-PROXY-REMOTE-MOBILITY-FOLLOWUP.json"] = {"id": "FALLS-PROXY-REMOTE-MOBILITY-FOLLOWUP", "simulation_language": "ko", "persona": {"age": 79}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "follow_up", "interview_initiator": "caregiver", "interview_mode": "video", "available_information": ["previous_clinical_memory", "medication_history"], "time_constraint": "scheduled", "clinical_responsibility": "follow_up_support"}, "initial_statement": {"ko": "어머니 보행 상태를 보호자가 대신 설명합니다."}, "hidden_state": proxy, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"falls.information_source_witness_and_reliability": "보호자가 영상통화로 답변하며 최근 보행을 직접 관찰함"}, "expected_max_turns": 82, "forbidden_assertions": ["diagnosis.dementia"]}, "provenance": provenance(SOURCES)}

    additional = routine_hidden("post_fall_injury_followup")
    additional["falls.patient_goal_priority_and_other_detail"] = {"value": "질문과 별개로 현관 조명 수리 지원도 문의하고 싶음"}
    out["FALLS-UNRELATED-ADDITIONAL-COMMENT.json"] = {"id": "FALLS-UNRELATED-ADDITIONAL-COMMENT", "simulation_language": "ko", "persona": {"age": 70}, "initial_statement": {"ko": "낙상 후 진료와 다른 의견도 남기고 싶어요."}, "hidden_state": additional, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"falls.patient_goal_priority_and_other_detail": "질문과 별개로 현관 조명 수리 지원도 문의하고 싶음"}, "expected_max_turns": 82, "forbidden_assertions": ["diagnosis.unsafe_home"]}, "provenance": provenance(SOURCES)}

    multi = routine_hidden("gait_balance_change_without_fall")
    multi["falls.patient_goal_priority_and_other_detail"] = {"value": "보행 변화 외에 새로 생긴 손 떨림도 별도 평가받고 싶음"}
    out["FALLS-MULTI-RFE-TREMOR.json"] = {"id": "FALLS-MULTI-RFE-TREMOR", "simulation_language": "ko", "persona": {"age": 57}, "initial_statement": {"ko": "걸음이 불안하고 손도 떨려요."}, "hidden_state": multi, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"falls.patient_goal_priority_and_other_detail": "보행 변화 외에 새로 생긴 손 떨림도 별도 평가받고 싶음"}, "expected_max_turns": 82, "forbidden_assertions": ["diagnosis.parkinson_disease"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Gait, Falls Risk or Post-fall Concern", intents=[("intent.characterize_symptom", "Characterize Fall Event and Gait Change"), ("intent.screen_red_flags", "Screen Injury Neurological Cardiovascular and Safeguarding Risk"), ("intent.differentiate_common_causes", "Assess Modifiable Multisystem Contributors"), ("intent.risk_assessment", "Assess Baseline Mobility Function and Support")])
    primary, research = source_docs()
    concepts = [("22325002", "Abnormal gait (finding)"), ("161898004", "Falls (finding)"), ("129839007", "At increased risk for falls (finding)"), ("419045004", "Loss of consciousness (finding)"), ("271594007", "Syncope (finding)")]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": 0} for c, d in concepts], "verified_attribute_ids": ["246112005", "363714003", "363698007", "272741003"], "validation": {"method": "build_time_live_fhir_lookup_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "event_semantics": {"diagnosis_inferred": False, "predictive_fall_risk_score_calculated": False, "laterality_postcoordination_asserted": False}, "provenance": provenance(["source.stom.gait-falls.20260716"])}
    docs = [("knowledge/base/primary-care-gait-falls-concern.json", graph), ("rules/base/primary-care-gait-falls-concern.json", rules), ("knowledge/generated/neurology/gait-falls-concern/gait-falls-concern.json", f), ("mappings/terminology/snomed-mrcm-gait-falls-concern.json", mapping), ("sources/manifests/primary-care-gait-falls-concern.json", primary), ("sources/manifests/primary-care-gait-falls-concern-research.json", research), ("policies/primary-care-gait-falls-concern-completion.json", completion(f))]
    for path, doc in docs:
        write_json(path, doc)
    for name, case in cases(f).items():
        write_json("simulation/patients/neurology/gait-falls-concern/" + name, case)


if __name__ == "__main__":
    main()
