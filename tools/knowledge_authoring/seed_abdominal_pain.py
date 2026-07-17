#!/usr/bin/env python3
"""Rebuild unreviewed abdominal-pain knowledge for clinician handoff."""
from profile_support import *

P, RFE = "abdominal_pain", "rfe.abdominal_pain"
M, SN = "mapping.snomed-mrcm.abdominal-pain", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-17T13:00:00Z"
SOURCES = [
    "source.nhs.stomach-ache.2023", "source.nice.ng126.ectopic-pregnancy.2026",
    "source.nice.ng12.abdominal-symptoms.2026", "source.acr.abdominal-pain.2026",
    "source.nice.ng104.pancreatitis", "source.nice.cg188.gallstone-disease",
    "source.nhs.abdominal-aortic-aneurysm.2025", "source.nhs.testicle-pain.2025",
    "source.nice.cg84.gastroenteritis-under-5",
    "source.stom.mrcm.abdominal-pain.20260714",
]
G = {key: f"group.abdominal_pain.{key}" for key in (
    "routing", "safety", "course", "site", "pain", "gastrointestinal",
    "urinary", "reproductive", "systemic", "exposure", "history",
    "treatment", "child", "handoff",
)}
C, S = ["intent.characterize_symptom"], ["intent.screen_red_flags"]
D, R = ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, group, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, [G[group]], intents=intents, **kwargs)


def fragment():
    e = [
        Q("abdominal_pain.primary_group", "Primary Abdominal Pain Context", "coded", "primary-group", "이번 복통은 갑자기 시작하거나 매우 심한 경우, 윗배·식사 관련 또는 등으로 퍼짐, 오른쪽 아랫배나 한 부위에 국한, 아랫배·골반·임신 가능성과 관련, 옆구리·배뇨·사타구니 관련, 배변 변화·복부팽만 관련, 오래 지속·반복되며 체중·식욕 변화 동반, 수술·시술 뒤 발생, 소아 보호자 문진, 그 밖의 불분명한 경우 중 무엇에 가장 가깝나요?", 270, "routing", C, allowed_values=["acute_sudden_or_severe", "upper_meal_or_back", "right_lower_or_localized", "lower_pelvic_or_reproductive", "flank_urinary_or_groin", "bowel_change_or_distension", "chronic_recurrent_weight_or_appetite", "post_surgery_or_procedure", "infant_child_caregiver", "other_unclear"]),
        Q("abdominal_pain.collapse_shock_or_severe_weakness", "Collapse Shock or Severe Weakness", "boolean", "collapse-shock", "쓰러짐·실신, 깨우기 어려움, 차갑고 축축한 피부, 매우 창백함 또는 곧 쓰러질 듯한 상태가 있나요?", 269, "safety", S, safety_relevant=True),
        Q("symptom.abdominal_pain.onset", "Sudden Abdominal Pain Onset", "boolean", "sudden-onset", "통증이 갑자기 시작했나요?", 268, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.abdominal_pain.severity", "Abdominal Pain Severity", "coded", "severity", "복통은 가벼움·중간·심함 중 어느 정도인가요?", 267, "pain", S, safety_relevant=True, allowed_values=["mild", "moderate", "severe"], reuse_existing=True),
        Q("abdominal_pain.rigid_distended_rebound_or_unable_to_move", "Rigid Distended or Peritoneal Warning", "boolean", "rigid-rebound", "배가 단단하게 긴장되거나 빠르게 붓고, 손을 뗄 때 더 아프거나 통증 때문에 움직이기 매우 어렵나요?", 266, "safety", S, safety_relevant=True),
        Q("symptom.hematemesis", "Blood or Coffee Ground Vomit", "boolean", "hematemesis", "피를 토했거나 토사물이 커피 찌꺼기처럼 보이나요?", 265, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.bloody_or_black_stool", "Bloody or Black Stool", "boolean", "bloody-black-stool", "많은 피·혈괴가 섞인 변이나 검고 끈적한 변을 보았나요?", 264, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("abdominal_pain.repeated_green_or_feculent_vomit", "Green or Feculent Vomit", "boolean", "green-feculent-vomit", "초록색 구토를 반복하거나 토사물에서 대변 같은 냄새·내용물이 느껴지나요?", 263, "safety", S, safety_relevant=True),
        Q("symptom.unable_to_pass_stool_or_gas", "Unable to Pass Stool or Gas", "boolean", "obstruction", "배가 붓고 구토하면서 대변과 방귀가 전혀 나오지 않나요?", 262, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.unable_to_urinate", "Unable to Urinate", "boolean", "urinary-retention", "소변이 마려운데도 전혀 나오지 않으면서 아랫배가 아프거나 불러오나요?", 261, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.chest_pain", "Chest Pain", "boolean", "chest-pain", "복통과 함께 가슴 압박감·조임·통증이 있나요?", 260, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.dyspnea", "Breathing Difficulty", "severity", "dyspnea", "숨참은 없음·가벼움·중간·심함 중 어느 정도인가요?", 259, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("abdominal_pain.pregnancy_bleeding_shoulder_syncope_or_severe_unilateral_pain", "Pregnancy Warning Features", "boolean", "pregnancy-warning", "임신 가능성이 있거나 임신 중이며 질출혈, 어깨끝 통증, 실신 또는 한쪽의 심한 아랫배 통증이 있나요?", 258, "safety", S, safety_relevant=True),
        Q("abdominal_pain.acute_testicular_scrotal_or_groin_pain", "Acute Testicular Scrotal or Groin Pain", "boolean", "testicular-warning", "갑자기 시작한 고환·음낭·사타구니의 심한 통증이나 부종이 함께 있나요?", 257, "safety", S, safety_relevant=True),
        Q("abdominal_pain.severe_back_pain_pulsation_or_collapse", "Severe Back Pain Pulsation or Collapse", "boolean", "vascular-warning", "배와 등에 갑작스러운 심한 통증이 함께 있고 배에서 강한 박동이 느껴지거나 실신할 듯한가요?", 256, "safety", S, safety_relevant=True),
        Q("abdominal_pain.fever_with_severe_localized_or_rapid_worsening_pain", "Fever with Severe Localized Pain", "boolean", "fever-localized-warning", "발열·오한과 함께 한 부위 복통이 심하거나 빠르게 악화하고 있나요?", 255, "safety", S, safety_relevant=True),
        Q("abdominal_pain.recent_procedure_with_severe_pain_bleeding_or_fever", "Post Procedure Warning", "boolean", "post-procedure-warning", "최근 복부·골반 수술, 내시경·시술 뒤 통증이 심해지면서 출혈·발열·구토가 있나요?", 254, "safety", S, safety_relevant=True),
        Q("abdominal_pain.child_limp_bilious_vomit_distension_or_bloody_stool", "Child Abdominal Warning", "boolean", "child-warning", "소아라면 축 늘어짐·깨우기 어려움, 초록색 구토, 심한 복부팽만 또는 피 섞인 변이 있나요?", 253, "safety", S, safety_relevant=True),
    ]
    specs = [
        ("abdominal_pain.information_source_proxy_reliability_and_conflict", "Information Source and Reliability", "string", "information-source", "누가 답변하며 본인 느낌, 보호자 관찰, 측정값, 진료기록·검사결과 중 무엇에 근거하나요? 불확실하거나 서로 다른 정보도 알려주세요.", 240, "handoff", C),
        ("abdominal_pain.age_life_stage_anatomy_and_baseline", "Age Life Stage Anatomy and Baseline", "string", "age-baseline", "만 나이, 영유아·소아·고령·임신·산후 여부, 진료에 필요한 생식·비뇨기 해부학 정보와 평소 식사·배변·활동 상태를 알려주세요.", 239, "history", R),
        ("symptom.duration", "Abdominal Pain Duration", "quantity", "duration", "복통이 처음 시작된 뒤 지금까지의 기간을 알려주세요.", 238, "course", C),
        ("abdominal_pain.onset_date_time_activity_and_preceding_event", "Onset Date Time and Circumstance", "string", "onset-detail", "처음 시작한 날짜·시각과 당시 식사·배변·배뇨·운동·외상·성관계·수술·시술 등 상황을 알려주세요.", 237, "course", C),
        ("abdominal_pain.continuous_episodic_frequency_duration_and_trend", "Episode Pattern and Trend", "string", "episode-pattern", "계속 아픈지 반복되는지, 반복한다면 빈도·한 번의 지속시간·호전/악화 추세와 사이에 정상으로 돌아오는지 알려주세요.", 236, "course", C),
        ("symptom.abdominal_pain.location", "Abdominal Pain Location", "coded", "location", "통증이 가장 심한 곳은 윗배 중앙, 오른쪽 윗배, 왼쪽 윗배, 배꼽 주위, 오른쪽 아랫배, 왼쪽 아랫배, 아랫배 중앙·골반, 옆구리, 전반적·이동성 중 어디인가요?", 235, "site", C),
        ("abdominal_pain.side_exact_point_and_number_of_sites", "Side Exact Point and Number of Sites", "string", "site-detail", "오른쪽·왼쪽·양쪽 여부, 손가락 하나로 짚을 수 있는 가장 아픈 지점과 아픈 부위 수를 알려주세요.", 234, "site", C),
        ("abdominal_pain.radiation_and_migration_sequence", "Radiation and Migration", "string", "radiation", "통증이 등·어깨·가슴·옆구리·사타구니·고환 등으로 퍼지거나 처음 위치에서 다른 곳으로 이동했다면 순서와 시각을 알려주세요.", 233, "site", C),
        ("symptom.abdominal_pain.character", "Abdominal Pain Character", "coded", "character", "통증은 쥐어짜는 경련, 찌름, 타는 느낌, 둔함, 압박·팽만, 파도처럼 반복, 그 밖의 양상 중 무엇에 가깝나요?", 232, "pain", C),
        ("abdominal_pain.character_patient_words_and_change", "Pain in Patient Words", "string", "character-detail", "통증을 본인 표현으로 설명하고 시작 뒤 양상이 어떻게 변했는지 알려주세요.", 231, "pain", C),
        ("symptom.abdominal_pain.worsening", "Pain Worsening", "boolean", "worsening", "통증이 시간에 따라 점점 심해지고 있나요?", 230, "pain", C),
        ("symptom.abdominal_pain.touch_tenderness", "Pain on Touch", "boolean", "touch-tenderness", "배를 가볍게 만져도 많이 아픈가요?", 229, "pain", C),
        ("abdominal_pain.meal_food_fasting_and_appetite_relationship", "Meal and Food Relationship", "string", "meal-relation", "식사 전후·공복, 특정 음식·술과 통증의 관계, 식욕과 먹는 양의 변화를 알려주세요.", 228, "gastrointestinal", D),
        ("abdominal_pain.bowel_movement_flatus_and_stool_relationship", "Bowel Relationship", "string", "bowel-relation", "배변·방귀 전후 통증 변화와 마지막 배변·방귀 시각을 알려주세요.", 227, "gastrointestinal", D),
        ("abdominal_pain.urination_bladder_filling_and_flank_relationship", "Urinary Relationship", "string", "urinary-relation", "소변을 참거나 볼 때, 방광이 찰 때 통증 변화와 옆구리·사타구니로 퍼지는지 알려주세요.", 226, "urinary", D),
        ("abdominal_pain.movement_cough_breath_posture_and_sleep_relationship", "Movement Posture and Sleep Relationship", "string", "movement-relation", "걷기·기침·깊은숨·자세·누움·잠과 통증의 관계, 편해지는 자세를 알려주세요.", 225, "pain", D),
        ("abdominal_pain.menstrual_ovulation_sexual_and_pregnancy_relationship", "Menstrual Sexual and Pregnancy Relationship", "string", "reproductive-relation", "월경·배란·성관계·임신 가능성과 통증의 시간 관계를 해당되는 범위에서 알려주세요.", 224, "reproductive", R),
        ("symptom.vomiting", "Vomiting", "boolean", "vomiting", "메스꺼움이나 구토가 있나요?", 215, "gastrointestinal", D, True),
        ("abdominal_pain.nausea_vomit_count_content_blood_bile_and_relation", "Nausea and Vomit Detail", "string", "vomit-detail", "메스꺼움·구토의 시작, 최근 24시간 횟수, 내용물·색·피·초록색 여부와 통증·식사의 시간 관계를 알려주세요.", 214, "gastrointestinal", R),
        ("symptom.diarrhea", "Diarrhoea", "boolean", "diarrhea", "묽거나 물 같은 설사가 있나요?", 213, "gastrointestinal", D, True),
        ("symptom.constipation", "Constipation", "boolean", "constipation", "평소보다 변이 딱딱하거나 배변 횟수가 줄고 힘들어졌나요?", 212, "gastrointestinal", D, True),
        ("abdominal_pain.baseline_bowel_stool_frequency_consistency_blood_and_mucus", "Bowel and Stool Detail", "string", "stool-detail", "평소와 현재 배변 횟수·변 모양, 설사·변비, 피·검은변·점액·기름진 변과 마지막 배변을 알려주세요.", 211, "gastrointestinal", R),
        ("abdominal_pain.distension_bloating_hernia_bulge_and_abdominal_girth", "Distension Bloating or Bulge", "string", "distension", "배가 붓거나 팽팽함, 반복되는 더부룩함, 탈장처럼 튀어나오는 부위와 복부둘레 변화를 알려주세요.", 210, "gastrointestinal", R),
        ("symptom.urinary_symptoms", "Urinary Symptoms", "boolean", "urinary-symptoms", "소변볼 때 통증, 잦음·급함, 소변 변화가 있나요?", 209, "urinary", D, True),
        ("abdominal_pain.urine_frequency_urgency_dysuria_blood_color_and_volume", "Urinary Detail", "string", "urine-detail", "소변 횟수·급함·통증, 피·색·냄새·양 변화와 마지막 소변 시각을 알려주세요.", 208, "urinary", R),
        ("abdominal_pain.vaginal_bleeding_discharge_lmp_contraception_and_pregnancy_test", "Reproductive and Pregnancy Detail", "string", "pregnancy-detail", "해당된다면 마지막 월경일, 월경 주기, 피임법, 질출혈·분비물과 임신검사 날짜·결과를 알려주세요.", 207, "reproductive", R),
        ("pregnancy.possible", "Possible Pregnancy", "boolean", "pregnancy-possible", "임신 가능성이 있나요?", 206, "reproductive", R, True),
        ("symptom.missed_period", "Missed Period", "boolean", "missed-period", "예정된 월경이 늦었거나 건너뛰었나요?", 205, "reproductive", R, True),
        ("symptom.vaginal_bleeding_or_discharge", "Vaginal Bleeding or Discharge", "boolean", "vaginal-bleeding", "비정상 질출혈이나 분비물이 있나요?", 204, "reproductive", R, True),
        ("symptom.shoulder_tip_pain", "Shoulder Tip Pain", "boolean", "shoulder-tip", "어깨끝 통증이 함께 있나요?", 203, "reproductive", R, True),
        ("abdominal_pain.obstetric_history_gestation_postpartum_and_complications", "Obstetric History and Current Context", "string", "obstetric-history", "임신 중이면 주수, 출산·유산·임신종결 뒤라면 날짜와 출산력·이전 자궁외임신·주요 합병증을 알려주세요.", 202, "reproductive", R),
        ("abdominal_pain.testicular_scrotal_groin_symptoms_and_laterality", "Testicular Scrotal and Groin Detail", "string", "scrotal-detail", "해당된다면 고환·음낭·사타구니 통증·부종·덩이·위치 변화와 좌우를 알려주세요.", 201, "reproductive", R),
        ("symptom.fever", "Fever", "boolean", "fever", "측정된 발열이나 열감·오한이 있나요?", 200, "systemic", R, True),
        ("abdominal_pain.temperature_chills_sweats_and_systemic_state", "Temperature and Systemic State", "string", "systemic-detail", "최고 체온·측정 시각·부위·기기, 오한·식은땀·심한 처짐과 변화 추세를 알려주세요.", 199, "systemic", R),
        ("abdominal_pain.jaundice_dark_urine_pale_stool_or_pruritus", "Jaundice and Biliary Features", "string", "jaundice", "눈·피부가 노래짐, 진한 소변, 회색·흰색 변, 전신 가려움이 있나요? 시작 시각도 알려주세요.", 198, "systemic", D),
        ("abdominal_pain.appetite_early_satiety_weight_and_fatigue_change", "Appetite Weight and Fatigue", "string", "constitutional", "식욕저하·조기포만, 의도하지 않은 체중 변화, 피로와 시작 시점을 알려주세요.", 197, "systemic", R),
        ("symptom.unintentional_weight_loss", "Unintentional Weight Loss", "boolean", "weight-loss", "의도하지 않은 체중감소가 있나요?", 196, "systemic", R, True),
        ("symptom.persistent_bloating", "Persistent Bloating", "boolean", "persistent-bloating", "지속적이거나 자주 반복되는 복부팽만이 있나요?", 195, "gastrointestinal", R, True),
        ("symptom.early_satiety_or_appetite_loss", "Early Satiety or Appetite Loss", "boolean", "appetite-loss", "조금만 먹어도 금방 배부르거나 식욕이 줄었나요?", 194, "systemic", R, True),
        ("abdominal_pain.function_eating_sleep_mobility_work_school_and_selfcare", "Functional Impact", "string", "function", "통증이 식사·수면·걷기·화장실 이용·자가관리·직장·학교에 미치는 영향을 알려주세요.", 193, "handoff", R),
        ("abdominal_pain.gi_hepatobiliary_pancreatic_urinary_gyn_and_vascular_history", "Relevant Medical History", "string", "medical-history", "위궤양·염증성장질환·담석·간·췌장·신장결석·요로·부인과·혈관 질환과 진단 시기·현재 상태를 알려주세요.", 180, "history", R),
        ("history.abdominal_surgery", "Abdominal Surgery History", "boolean", "abdominal-surgery", "복부·골반 수술이나 주요 시술을 받은 적이 있나요?", 179, "history", R, True),
        ("abdominal_pain.surgery_procedure_date_reason_complications_stoma_or_device", "Surgery Procedure and Device Detail", "string", "surgery-detail", "복부·골반 수술·내시경·시술의 명칭·날짜·이유·합병증과 장루·배액관·영양관 여부를 알려주세요.", 178, "history", R),
        ("history.diabetes", "Diabetes", "boolean", "diabetes", "당뇨병이 있나요?", 177, "history", R, True),
        ("abdominal_pain.high_risk_conditions_immunosuppression_bleeding_and_frailty", "High Risk Conditions", "string", "high-risk-history", "면역저하·암치료·신장/부신질환, 출혈질환·항응고 치료, 고령·허약 등 관련 상태를 알려주세요.", 176, "history", R),
        ("abdominal_pain.current_medicines_nsaid_anticoagulant_steroid_glp1_and_changes", "Medicines and Recent Changes", "string", "medicines", "현재 약과 최근 시작·중단·증량한 소염진통제, 아스피린·항응고제, 스테로이드, GLP-1 계열 주사·변비약 등을 이름·용량·날짜와 함께 알려주세요.", 175, "history", R),
        ("abdominal_pain.medicine_food_allergies_and_reactions", "Allergies and Reactions", "string", "allergies", "약·음식·조영제 알레르기와 실제 나타난 반응을 알려주세요.", 174, "history", R),
        ("abdominal_pain.alcohol_smoking_substance_and_last_use", "Alcohol Tobacco and Substance Context", "string", "substance", "술 종류·양·빈도·마지막 음주, 흡연과 기타 물질 사용을 알려주세요.", 173, "exposure", R),
        ("abdominal_pain.food_water_sick_contact_travel_and_outbreak_context", "Food Water Travel and Contact", "string", "exposure-detail", "의심 음식·물·공동식사, 비슷하게 아픈 사람, 최근 여행지·날짜·수영·동물 노출을 알려주세요.", 172, "exposure", R),
        ("abdominal_pain.injury_heavy_exertion_occupation_and_safeguarding_context", "Injury Exertion Occupation and Safety", "string", "injury-context", "복부 외상·무거운 물건·격한 운동, 직업 노출과 안전·폭력 우려가 있다면 알려주세요.", 171, "exposure", R),
        ("abdominal_pain.child_age_weight_feeding_behavior_stool_urine_and_caregiver_observation", "Child Caregiver Detail", "string", "child-detail", "소아라면 정확한 나이·체중, 먹고 마신 양, 구토·변·소변 횟수, 보챔·처짐·걷기·잠과 보호자가 본 통증 위치를 알려주세요.", 170, "child", R),
        ("abdominal_pain.prior_similar_episodes_diagnoses_ed_visits_and_admissions", "Prior Episodes and Acute Care", "string", "prior-episodes", "이전 비슷한 통증의 시기·횟수, 당시 진단과 응급실·입원 경험을 알려주세요.", 160, "handoff", R),
        ("abdominal_pain.prior_assessment_labs_urine_stool_imaging_endoscopy_and_source", "Prior Assessment and Tests", "string", "prior-tests", "이번 통증 관련 진료, 혈액·소변·대변검사, 초음파·CT·MRI·내시경 결과가 있다면 날짜·기관·결과와 원본 또는 전달받은 설명을 알려주세요.", 159, "handoff", R),
        ("abdominal_pain.treatment_analgesic_antacid_antibiotic_bowel_action_and_response", "Treatment and Response", "string", "treatment-response", "진통제·제산제·항생제·변비약·금식·식이조절 등 시행한 조치의 이름·용량·시각과 효과·부작용을 알려주세요.", 158, "treatment", R),
        ("abdominal_pain.patient_concern_goal_and_additional_comment", "Patient Concern Goal and Other Detail", "string", "concern-goal", "가장 걱정되는 점, 의료진에게 원하는 도움과 질문에 없지만 전달할 내용을 알려주세요.", 157, "handoff", R),
    ]
    reused = {
        "symptom.vomiting", "symptom.diarrhea", "symptom.constipation",
        "symptom.urinary_symptoms", "pregnancy.possible", "symptom.missed_period",
        "symptom.vaginal_bleeding_or_discharge", "symptom.shoulder_tip_pain",
        "symptom.fever", "symptom.unintentional_weight_loss", "symptom.persistent_bloating",
        "symptom.early_satiety_or_appetite_loss", "history.abdominal_surgery", "history.diabetes",
    }
    coded_values = {
        "symptom.abdominal_pain.location": ["epigastric", "right_upper", "left_upper", "periumbilical", "right_lower", "left_lower", "suprapubic_or_pelvic", "flank", "generalized_or_migratory"],
        "symptom.abdominal_pain.character": ["cramping", "stabbing", "burning", "dull", "pressure_or_distension", "colicky", "other"],
    }
    for spec in specs:
        *base, reuse = spec if len(spec) == 9 else (*spec, False)
        item = Q(*base, reuse_existing=bool(reuse) or base[0] in reused)
        if base[0] in coded_values:
            item["fact"]["allowed_values"] = coded_values[base[0]]
        if base[0] == "symptom.abdominal_pain.location":
            item["fact"]["terminology_binding"] = {
                "system": SN, "focus_code": "21522001",
                "attribute_code": "363698007",
            }
            item["fact"]["mrcm_validation"] = {
                "ref": M, "status": "provisional_pass",
            }
        e.append(item)
    safety = [
        ("collapse-shock", "abdominal_pain.collapse_shock_or_severe_weakness", "emergency"),
        ("sudden-severe", "abdominal_pain.sudden_and_severe", "emergency"),
        ("rigid-rebound", "abdominal_pain.rigid_distended_rebound_or_unable_to_move", "emergency"),
        ("hematemesis", "symptom.hematemesis", "emergency"),
        ("bloody-black-stool", "symptom.bloody_or_black_stool", "emergency"),
        ("green-feculent-vomit", "abdominal_pain.repeated_green_or_feculent_vomit", "emergency"),
        ("obstruction", "symptom.unable_to_pass_stool_or_gas", "emergency"),
        ("urinary-retention", "symptom.unable_to_urinate", "emergency"),
        ("chest-pain", "symptom.chest_pain", "emergency"),
        ("pregnancy-warning", "abdominal_pain.pregnancy_bleeding_shoulder_syncope_or_severe_unilateral_pain", "emergency"),
        ("testicular-warning", "abdominal_pain.acute_testicular_scrotal_or_groin_pain", "emergency"),
        ("vascular-warning", "abdominal_pain.severe_back_pain_pulsation_or_collapse", "emergency"),
        ("child-warning", "abdominal_pain.child_limp_bilious_vomit_distension_or_bloody_stool", "emergency"),
        ("fever-localized-warning", "abdominal_pain.fever_with_severe_localized_or_rapid_worsening_pain", "urgent"),
        ("post-procedure-warning", "abdominal_pain.recent_procedure_with_severe_pain_bleeding_or_fever", "urgent"),
    ]
    # Preserve separate onset and severity Facts while evaluating the paired warning.
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, 1000 if level == "emergency" else 960) for key, fid, level in safety if key != "sudden-severe"]
    rules.append(safety_rule(P, "sudden-severe", {"all": [{"fact": "symptom.abdominal_pain.onset", "equals": True}, {"fact": "symptom.abdominal_pain.severity", "equals": "severe"}]}, "emergency", 1000))
    rules.append(safety_rule(P, "severe-dyspnea", {"fact": "symptom.dyspnea", "equals": "severe"}, "emergency", 1000))
    refresh = default_refresh(); refresh.update({"last_assessed_at": "2026-07-17", "next_monitor_at": "2026-07-18", "next_full_review_at": "2027-01-13"})
    return {"id": "knowledge.generated.gastrointestinal.abdominal-pain", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-abdominal-pain-research", "default_refresh": refresh, "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="abdominal_pain.primary_group", question_budget=84, source_refs=SOURCES)
    common = {
        "abdominal_pain.information_source_proxy_reliability_and_conflict", "abdominal_pain.age_life_stage_anatomy_and_baseline", "symptom.duration",
        "abdominal_pain.onset_date_time_activity_and_preceding_event", "abdominal_pain.continuous_episodic_frequency_duration_and_trend",
        "symptom.abdominal_pain.location", "abdominal_pain.side_exact_point_and_number_of_sites", "abdominal_pain.radiation_and_migration_sequence",
        "symptom.abdominal_pain.character", "abdominal_pain.character_patient_words_and_change", "symptom.abdominal_pain.worsening",
        "symptom.abdominal_pain.touch_tenderness", "abdominal_pain.function_eating_sleep_mobility_work_school_and_selfcare",
        "abdominal_pain.gi_hepatobiliary_pancreatic_urinary_gyn_and_vascular_history", "abdominal_pain.current_medicines_nsaid_anticoagulant_steroid_glp1_and_changes",
        "abdominal_pain.medicine_food_allergies_and_reactions", "abdominal_pain.prior_similar_episodes_diagnoses_ed_visits_and_admissions",
        "abdominal_pain.prior_assessment_labs_urine_stool_imaging_endoscopy_and_source", "abdominal_pain.treatment_analgesic_antacid_antibiotic_bowel_action_and_response",
        "abdominal_pain.patient_concern_goal_and_additional_comment",
    }
    p["required_facts"]["routine"] = sorted(common)
    cases = {
        "acute_sudden_or_severe": ["abdominal_pain.movement_cough_breath_posture_and_sleep_relationship", "symptom.vomiting", "abdominal_pain.nausea_vomit_count_content_blood_bile_and_relation", "symptom.fever", "abdominal_pain.temperature_chills_sweats_and_systemic_state"],
        "upper_meal_or_back": ["abdominal_pain.meal_food_fasting_and_appetite_relationship", "abdominal_pain.jaundice_dark_urine_pale_stool_or_pruritus", "abdominal_pain.alcohol_smoking_substance_and_last_use", "abdominal_pain.nausea_vomit_count_content_blood_bile_and_relation"],
        "right_lower_or_localized": ["symptom.fever", "abdominal_pain.temperature_chills_sweats_and_systemic_state", "abdominal_pain.bowel_movement_flatus_and_stool_relationship", "abdominal_pain.movement_cough_breath_posture_and_sleep_relationship"],
        "lower_pelvic_or_reproductive": ["abdominal_pain.menstrual_ovulation_sexual_and_pregnancy_relationship", "abdominal_pain.vaginal_bleeding_discharge_lmp_contraception_and_pregnancy_test", "pregnancy.possible", "symptom.missed_period", "symptom.vaginal_bleeding_or_discharge", "symptom.shoulder_tip_pain", "abdominal_pain.obstetric_history_gestation_postpartum_and_complications", "abdominal_pain.testicular_scrotal_groin_symptoms_and_laterality"],
        "flank_urinary_or_groin": ["symptom.urinary_symptoms", "abdominal_pain.urination_bladder_filling_and_flank_relationship", "abdominal_pain.urine_frequency_urgency_dysuria_blood_color_and_volume", "abdominal_pain.testicular_scrotal_groin_symptoms_and_laterality"],
        "bowel_change_or_distension": ["symptom.diarrhea", "symptom.constipation", "abdominal_pain.baseline_bowel_stool_frequency_consistency_blood_and_mucus", "abdominal_pain.bowel_movement_flatus_and_stool_relationship", "abdominal_pain.distension_bloating_hernia_bulge_and_abdominal_girth"],
        "chronic_recurrent_weight_or_appetite": ["abdominal_pain.appetite_early_satiety_weight_and_fatigue_change", "symptom.unintentional_weight_loss", "symptom.persistent_bloating", "symptom.early_satiety_or_appetite_loss", "abdominal_pain.baseline_bowel_stool_frequency_consistency_blood_and_mucus"],
        "post_surgery_or_procedure": ["history.abdominal_surgery", "abdominal_pain.surgery_procedure_date_reason_complications_stoma_or_device", "symptom.fever", "abdominal_pain.temperature_chills_sweats_and_systemic_state"],
        "infant_child_caregiver": ["abdominal_pain.child_age_weight_feeding_behavior_stool_urine_and_caregiver_observation", "symptom.vomiting", "symptom.diarrhea", "symptom.constipation"],
        "other_unclear": ["abdominal_pain.food_water_sick_contact_travel_and_outbreak_context", "abdominal_pain.injury_heavy_exertion_occupation_and_safeguarding_context", "abdominal_pain.high_risk_conditions_immunosuppression_bleeding_and_frailty", "history.diabetes"],
    }
    p["conditional_required_facts"] = [{"selector_fact": "abdominal_pain.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nhs.stomach-ache.2023", "NHS", "Stomach ache", "reviewed-2023-05-26", "https://www.nhs.uk/symptoms/stomach-ache/", "public_health_guidance", ["Sudden or severe pain, marked tenderness, gastrointestinal bleeding, urinary retention, bowel obstruction features, breathing difficulty, chest pain and collapse are warning features."]),
        ("source.nice.ng126.ectopic-pregnancy.2026", "NICE", "Ectopic pregnancy and miscarriage", "NG126-updated-2026-06-17", "https://www.nice.org.uk/guidance/ng126/chapter/symptoms-and-signs-of-ectopic-pregnancy-and-initial-assessment", "nice_guidance", ["Pregnancy-related history includes abdominal or pelvic pain, missed period, bleeding, gastrointestinal or urinary symptoms, dizziness, syncope, shoulder-tip pain and rectal pressure.", "Haemodynamic instability or significant concern about pain or bleeding requires emergency assessment; the interview does not diagnose ectopic pregnancy."]),
        ("source.nice.ng12.abdominal-symptoms.2026", "NICE", "Suspected cancer recognition and referral — abdominal symptoms", "NG12-updated-2026-04-15", "https://www.nice.org.uk/guidance/ng12/chapter/Recommended-actions-organised-by-symptom-and-findings-of-primary-care-investigations", "nice_guidance", ["Persistent abdominal pain, distension, early satiety, appetite loss, weight loss, rectal bleeding, bowel or urinary change and age context support clinician assessment without assigning cancer."]),
        ("source.acr.abdominal-pain.2026", "American College of Radiology", "ACR Appropriateness Criteria: Acute Nonlocalized Abdominal Pain", "finalized-2026", "https://gravitas.acr.org/ACPortal/TopicNarrativePdf?topicId=125", "clinical_guideline", ["Pain localization, fever, recent surgery and localized versus nonlocalized presentation affect downstream imaging consideration.", "The package records imaging context but does not select or order imaging."]),
        ("source.nice.ng104.pancreatitis", "NICE", "Pancreatitis", "NG104-updated-2020-12-16", "https://www.nice.org.uk/guidance/ng104/chapter/Recommendations", "nice_guidance", ["Sudden upper abdominal pain, nausea, vomiting, tenderness, fever, pulse, gallstone history, alcohol and medication context are relevant; diagnosis requires clinical tests.", "Chronic or recurrent upper abdominal pain and prior CT, ultrasound or endoscopy findings are relevant handoff information."]),
        ("source.nice.cg188.gallstone-disease", "NICE", "Gallstone disease: diagnosis and management", "CG188-current-2026", "https://www.nice.org.uk/guidance/cg188/chapter/recommendations", "nice_guidance", ["Unresponsive abdominal or gastrointestinal symptoms, food triggers, liver tests and ultrasound history are relevant to clinician review.", "The interview does not diagnose gallstones or order investigations."]),
        ("source.nhs.abdominal-aortic-aneurysm.2025", "NHS", "Abdominal aortic aneurysm", "reviewed-2025", "https://www.nhs.uk/conditions/abdominal-aortic-aneurysm/", "public_health_guidance", ["Sudden severe abdominal or back pain requires immediate emergency help; recurrent pain or an abdominal pulsation also needs clinician assessment.", "The interview records warning symptoms and does not diagnose an aneurysm."]),
        ("source.nhs.testicle-pain.2025", "NHS", "Testicle pain", "reviewed-2025-06-26", "https://www.nhs.uk/symptoms/testicle-pain/", "public_health_guidance", ["Sudden severe testicular pain, or testicular pain with nausea, vomiting or abdominal pain, requires immediate emergency assessment.", "The interview records site, laterality and associated symptoms without diagnosing testicular torsion."]),
        ("source.nice.cg84.gastroenteritis-under-5", "NICE", "Diarrhoea and vomiting caused by gastroenteritis in under 5s", "CG84-current-2026", "https://www.nice.org.uk/guidance/cg84/chapter/Recommendations", "nice_guidance", ["In young children, altered responsiveness, blood or mucus in stool, bilious green vomit, severe or localised abdominal pain, abdominal distension and rebound tenderness are warning features.", "The caregiver interview records feeding, urine, stool, behaviour and warning features without assigning a diagnosis."]),
        ("source.stom.mrcm.abdominal-pain.20260714", "Infoclinic", "STOM abdominal pain terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/21522001", "terminology_server", ["Build-time MRCM verification allowed Finding site and Severity for abdominal pain.", "MRCM constrains terminology representation only and does not create clinical rules."]),
    ]
    verified_now = {"source.nice.ng126.ectopic-pregnancy.2026", "source.nice.ng12.abdominal-symptoms.2026", "source.acr.abdominal-pain.2026", "source.nice.ng104.pancreatitis", "source.nice.cg188.gallstone-disease", "source.nhs.abdominal-aortic-aneurysm.2025", "source.nhs.testicle-pain.2025", "source.nice.cg84.gastroenteritis-under-5"}
    artifacts = []
    for sid, publisher, title, version, url, profile, assertions in defs:
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "Infoclinic", "American College of Radiology"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-17" if sid in verified_now else "2026-07-14", "monitor_result": "current_official_source_confirmed" if sid in verified_now else "not_due_existing_metadata_preserved", "assertions": assertions})
    research = {"id": "source-manifest.primary-care-abdominal-pain-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.abdominal-pain", "generated_clinical_knowledge", "knowledge/generated/gastrointestinal/abdominal-pain/abdominal-pain.json", True), ("source.mapping.abdominal-pain", "terminology_mapping", "mappings/terminology/snomed-mrcm-abdominal-pain.json", False), ("source.external.abdominal-pain", "external_source_manifest", "sources/manifests/primary-care-abdominal-pain-research.json", False), ("source.policy.abdominal-pain", "runtime_policy", "policies/primary-care-abdominal-pain-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-abdominal-pain", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        key, level, condition = rule["id"].split("safety.")[1], rule["then"]["safety_level"], rule["when"]
        children = condition.get("all", [condition]); state = {child["fact"]: {"value": child.get("equals", True)} for child in children}
        out[f"ABDOMINAL-{key.upper()}.json"] = {"id": f"ABDOMINAL-{key.upper()}", "simulation_language": "ko", "persona": {"age": 5 if key == "child-warning" else 24 + index * 3}, "initial_statement": {"ko": "복통이 있어 진료 전 문진을 합니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 25, "forbidden_assertions": ["diagnosis.appendicitis", "diagnosis.ectopic_pregnancy", "diagnosis.pancreatitis", "diagnosis.gallstone"]}, "provenance": provenance(SOURCES)}
    policy, by_id = completion(f), {item["fact"]["id"]: item["fact"] for item in f["entries"]}
    def routine(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"][branch])
        values = {}
        for fid in required:
            fact = by_id[fid]
            if fact["value_type"] == "boolean": value = False
            elif fact["value_type"] == "integer": value = 0
            elif fact["value_type"] == "coded": value = fact.get("allowed_values", ["other_unclear"])[0]
            elif fact["value_type"] == "quantity": value = "3 days"
            elif fact["value_type"] == "severity": value = "none"
            else: value = "특이사항 없음"
            values[fid] = {"value": value}
        values["abdominal_pain.primary_group"] = {"value": branch}; values["symptom.abdominal_pain.severity"] = {"value": "mild"}; values["pain.nrs_score"] = {"value": 3}; values["pain.frequency"] = {"value": "less_than_daily"}
        return values
    specs = [
        ("UPPER-MEAL-BACK", "upper_meal_or_back", 48, "식후 윗배 통증이 등으로 퍼집니다.", {"abdominal_pain.meal_food_fasting_and_appetite_relationship": {"value": "기름진 식사 1시간 뒤 악화"}}),
        ("LOWER-PELVIC", "lower_pelvic_or_reproductive", 31, "아랫배 통증과 월경 관련 정보를 함께 전달합니다.", {"pregnancy.possible": {"value": False}, "abdominal_pain.vaginal_bleeding_discharge_lmp_contraception_and_pregnancy_test": {"value": "마지막 월경 2주 전, 비정상 출혈 없음"}}),
        ("BOWEL-DISTENSION", "bowel_change_or_distension", 56, "복부팽만과 변비가 반복됩니다.", {"symptom.constipation": {"value": True}, "abdominal_pain.baseline_bowel_stool_frequency_consistency_blood_and_mucus": {"value": "평소 매일, 최근 3일간 딱딱한 변 1회"}}),
        ("CHILD-PROXY", "infant_child_caregiver", 7, "아이의 배가 아파 보호자가 관찰 내용을 답합니다.", {"abdominal_pain.child_age_weight_feeding_behavior_stool_urine_and_caregiver_observation": {"value": "7세, 24kg, 물과 죽 섭취, 소변 5회, 배꼽 주위를 가리킴"}}),
        ("POST-SURGERY", "post_surgery_or_procedure", 63, "복부수술 뒤 반복되는 통증을 정리합니다.", {"history.abdominal_surgery": {"value": True}, "abdominal_pain.surgery_procedure_date_reason_complications_stoma_or_device": {"value": "담낭절제술 2년 전, 합병증 없음"}}),
        ("MULTI-RFE-URINARY", "other_unclear", 42, "복통 외에 배뇨 불편도 별도 문진하고 싶습니다.", {"abdominal_pain.patient_concern_goal_and_additional_comment": {"value": "복통 외 반복되는 배뇨 불편을 별도 RFE로 전달 요청"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine(branch); state.update(overrides)
        out[f"ABDOMINAL-{key}.json"] = {"id": f"ABDOMINAL-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": state, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 90, "forbidden_assertions": ["diagnosis.appendicitis", "diagnosis.pancreatitis"]}, "provenance": provenance(SOURCES)}
    absent = routine("chronic_recurrent_weight_or_appetite"); missing = "abdominal_pain.prior_assessment_labs_urine_stool_imaging_endoscopy_and_source"; absent.pop(missing)
    out["ABDOMINAL-REMOTE-DATA-ABSENT.json"] = {"id": "ABDOMINAL-REMOTE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 74}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "보호자가 전화로 반복 복통을 설명합니다. 검사자료는 없습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {missing: "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 90, "forbidden_assertions": ["diagnosis.cancer"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Abdominal or Pelvic Pain", intents=[("intent.characterize_symptom", "Characterize Onset Site Radiation NRS Character Course Triggers and Functional Impact"), ("intent.screen_red_flags", "Screen Shock Acute Abdomen Bleeding Obstruction Urinary Pregnancy Testicular Vascular Procedure and Child Warning Features"), ("intent.differentiate_common_causes", "Localize Gastrointestinal Urinary Reproductive Systemic and Exposure Features"), ("intent.risk_assessment", "Assess Life Stage Anatomy History Surgery Medicines Tests Treatment and Patient Goals")])
    primary, research = source_docs()
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": "21522001", "display": "Abdominal pain (finding)", "concept_active": True}], "verified_attribute_ids": ["363698007", "246112005"], "validation": {"method": "build_time_live_mrcm_summary", "checked_at": "2026-07-14T00:00:00Z", "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "abdominal_pain_semantics": {"diagnosis_inferred": False, "appendicitis_score_calculated": False, "ectopic_pregnancy_diagnosed": False, "pancreatitis_diagnosed": False, "imaging_selected_or_ordered": False, "runtime_terminology_query_required": False}, "provenance": provenance(["source.stom.mrcm.abdominal-pain.20260714"])}
    docs = [("knowledge/base/primary-care-abdominal-pain.json", graph), ("rules/base/primary-care-abdominal-pain.json", rules), ("knowledge/generated/gastrointestinal/abdominal-pain/abdominal-pain.json", f), ("mappings/terminology/snomed-mrcm-abdominal-pain.json", mapping), ("sources/manifests/primary-care-abdominal-pain.json", primary), ("sources/manifests/primary-care-abdominal-pain-research.json", research), ("policies/primary-care-abdominal-pain-completion.json", completion(f))]
    for path, document in docs: write_json(path, document)
    for name, case in cases(f).items(): write_json("simulation/patients/gastrointestinal/abdominal-pain/" + name, case)


if __name__ == "__main__":
    main()
