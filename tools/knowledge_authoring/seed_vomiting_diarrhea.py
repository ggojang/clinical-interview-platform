#!/usr/bin/env python3
"""Rebuild unreviewed vomiting/diarrhoea knowledge for clinician handoff."""
from profile_support import *

P, RFE = "vomiting_diarrhea", "rfe.vomiting_diarrhea"
M, SN = "mapping.snomed-mrcm.vomiting-diarrhea", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-17T12:00:00Z"
SOURCES = [
    "source.nhs.diarrhoea-vomiting.2026", "source.nhs.dehydration.2026",
    "source.cdc.food-poisoning.2025", "source.cdc.yellow-book.travelers-diarrhea.2026",
    "source.cdc.c-diff.2026", "source.nice.cg84.gastroenteritis-under-5",
    "source.nice.ng12.vomiting-diarrhea.2026",
    "source.stom.mrcm.vomiting-diarrhea.20260714",
]
G = {key: f"group.vomiting_diarrhea.{key}" for key in (
    "routing", "safety", "course", "vomit", "stool", "pain", "hydration",
    "exposure", "child", "pregnancy", "history", "treatment", "handoff",
)}
C, S = ["intent.characterize_symptom"], ["intent.screen_red_flags"]
D, R = ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, group, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, [G[group]], intents=intents, **kwargs)


def fragment():
    e = [
        Q("vomiting_diarrhea.primary_group", "Primary Vomiting or Diarrhoea Context", "coded", "primary-group", "이번 문제는 구토가 주된 경우, 설사가 주된 경우, 둘 다 있는 경우, 반복·지속되는 경우, 여행·음식 노출 뒤 발생, 항생제·의료기관 이용 뒤 발생, 임신·산후 관련, 영유아·소아 보호자 문진, 기존 질환·약물 추적, 그 밖의 불분명한 경우 중 무엇에 가장 가깝나요?", 260, "routing", C, allowed_values=["vomiting_predominant", "diarrhea_predominant", "both_acute", "persistent_or_recurrent", "travel_food_or_cluster", "post_antibiotic_or_healthcare", "pregnancy_postpartum", "infant_child_caregiver", "condition_or_medicine_followup", "other_unclear"]),
        Q("symptom.vomiting_diarrhea.presentation", "Presentation", "coded", "presentation", "구토만, 설사만, 구토와 설사 모두 중 어느 것인가요?", 259, "routing", C, allowed_values=["vomiting_only", "diarrhea_only", "both"], reuse_existing=True),
        Q("vomiting_diarrhea.collapse_shock_or_unresponsive", "Collapse Shock or Unresponsive", "boolean", "collapse", "쓰러짐·실신, 깨우기 어려움, 심한 혼란, 차갑고 얼룩진 피부 또는 매우 축 늘어진 상태가 있나요?", 258, "safety", S, safety_relevant=True),
        Q("symptom.hematemesis", "Blood or Coffee Ground Vomit", "boolean", "hematemesis", "피를 토했거나 토사물이 커피 찌꺼기처럼 보이나요?", 257, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.green_vomit", "Green Bilious Vomit", "boolean", "green-vomit", "토사물이 분명한 초록색인가요?", 256, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("exposure.possible_poisoning", "Possible Poisoning", "boolean", "poisoning", "약·세제·농약·화학물질·독버섯 등 독성 물질을 잘못 먹었을 가능성이 있나요?", 255, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.sudden_severe_abdominal_pain", "Sudden Severe Abdominal Pain", "boolean", "severe-pain", "배가 갑자기 매우 심하게 아프거나 단단하게 붓고 만지기 힘든가요?", 254, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("vomiting_diarrhea.black_stool_or_large_rectal_bleeding", "Black Stool or Large Rectal Bleeding", "boolean", "major-stool-bleeding", "검고 끈적한 변을 보았거나 많은 피·혈괴가 항문으로 나왔나요?", 253, "safety", S, safety_relevant=True),
        Q("symptom.confusion", "Confusion", "boolean", "confusion", "새로 혼란스럽거나 반응이 평소와 다른가요?", 252, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.dyspnea", "Breathing Difficulty", "severity", "dyspnea", "숨참은 없음·가벼움·중간·심함 중 어느 정도인가요?", 251, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("vomiting_diarrhea.neck_stiffness_rash_or_severe_headache", "Neurologic or Rash Warning", "boolean", "neuro-warning", "심한 두통과 목이 뻣뻣함, 빛에 심하게 예민함, 눌러도 사라지지 않는 붉거나 보라색 발진이 있나요?", 250, "safety", S, safety_relevant=True),
        Q("vomiting_diarrhea.child_bilious_vomit_distension_or_severe_local_pain", "Child Bilious Vomit or Acute Abdomen Warning", "boolean", "child-abdomen-warning", "소아라면 초록색 구토, 심한 국소 복통, 배가 심하게 붓거나 만지면 크게 아파하나요?", 249, "safety", S, safety_relevant=True),
        Q("vomiting_diarrhea.pregnancy_postpartum_bleeding_severe_pain_or_collapse", "Pregnancy Postpartum Warning", "boolean", "pregnancy-warning", "임신 중이거나 출산·유산·임신종결 뒤이며 질출혈, 한쪽 또는 심한 복통, 어깨끝 통증, 실신이 함께 있나요?", 248, "safety", S, safety_relevant=True),
        Q("symptom.bloody_diarrhea", "Bloody Diarrhoea", "boolean", "bloody-diarrhea", "묽은 변에 선명한 피나 피 섞인 점액이 있나요?", 247, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.unable_to_keep_fluids", "Unable to Keep Fluids", "boolean", "unable-fluids", "물을 조금씩 마셔도 계속 토해서 거의 유지할 수 없나요?", 246, "safety", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.dehydration_signs", "Dehydration Symptoms", "boolean", "dehydration", "심한 갈증·입마름, 일어설 때 어지럼, 눈물이 안 남, 눈이 들어가 보임 등 탈수 증상이 있나요?", 245, "hydration", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.reduced_urine_output", "Reduced Urine Output", "boolean", "reduced-urine", "소변이 평소보다 크게 줄었거나 매우 진하고, 영유아라면 젖은 기저귀 수가 줄었나요?", 244, "hydration", S, safety_relevant=True, reuse_existing=True),
        Q("vomiting_diarrhea.rapid_worsening_or_high_risk_dehydration", "Rapid Worsening or High Risk Dehydration", "boolean", "high-risk-dehydration", "영유아·고령·허약·면역저하 상태에서 빠르게 처지거나 수분 섭취와 소변량이 계속 줄고 있나요?", 243, "safety", S, safety_relevant=True),
        Q("symptom.vomiting_over_two_days", "Vomiting Over Two Days", "boolean", "vomiting-persistent", "성인 기준 구토가 2일을 넘겨 계속되나요?", 242, "course", S, safety_relevant=True, reuse_existing=True),
        Q("symptom.diarrhea_over_seven_days", "Diarrhoea Over Seven Days", "boolean", "diarrhea-persistent", "설사가 7일을 넘겨 계속되나요?", 241, "course", S, safety_relevant=True, reuse_existing=True),
    ]
    specs = [
        ("vomiting_diarrhea.information_source_proxy_reliability_and_conflict", "Information Source and Reliability", "string", "information-source", "누가 답변하며 본인 느낌, 보호자 관찰, 체온·체중 기록, 검사결과 중 무엇에 근거하나요? 불확실하거나 서로 다른 정보도 알려주세요.", 230, "handoff", C),
        ("vomiting_diarrhea.age_life_stage_baseline_and_frailty", "Age Life Stage and Baseline", "string", "age-baseline", "만 나이, 영유아·소아·고령·임신·산후 여부와 평소 식사·배변·활동·인지 상태를 알려주세요.", 229, "history", R),
        ("symptom.duration", "Overall Duration", "quantity", "duration", "처음 증상이 시작된 뒤 지금까지의 기간을 알려주세요.", 228, "course", C),
        ("vomiting_diarrhea.onset_date_time_first_symptom_and_speed", "Onset Detail", "string", "onset-detail", "시작 날짜·시각, 구토·설사·통증 중 무엇이 먼저였고 갑자기 또는 서서히 시작했는지 알려주세요.", 227, "course", C),
        ("vomiting_diarrhea.continuous_episodic_frequency_trend_and_baseline", "Course and Trend", "string", "course-trend", "계속되는지 반복되는지, 빈도·한 번의 지속시간·호전/악화 추세와 사이에 정상으로 돌아오는지 알려주세요.", 226, "course", C),
        ("symptom.vomiting.present", "Vomiting Present", "boolean", "vomiting-present", "구토가 있나요?", 225, "vomit", C),
        ("symptom.vomiting.count_24h", "Vomiting Count 24 Hours", "integer", "vomiting-count", "최근 24시간 구토 횟수는 몇 회인가요?", 224, "vomit", C),
        ("symptom.vomiting.severity", "Vomiting Severity", "severity", "vomiting-severity", "구토는 가벼움·중간·심함 중 어느 정도인가요?", 223, "vomit", C),
        ("vomiting_diarrhea.vomit_timing_meal_relation_volume_and_content", "Vomit Timing Volume and Content", "string", "vomit-detail", "구토 시각과 식사·약 복용과의 관계, 대략적인 양, 음식물·맑은 액체·담즙 같은 내용물을 알려주세요.", 222, "vomit", C),
        ("vomiting_diarrhea.projectile_effortless_regurgitation_and_retching", "Vomiting Mechanism Description", "string", "vomit-mechanism", "분수처럼 뿜는지, 구역질 뒤 토하는지, 힘들이지 않고 음식이 올라오는지와 메스꺼움·헛구역질을 알려주세요.", 221, "vomit", D),
        ("vomiting_diarrhea.vomit_blood_color_amount_and_coffee_ground_detail", "Vomit Blood Detail", "string", "vomit-blood-detail", "피 또는 커피 찌꺼기 같은 구토가 있다면 색·양·횟수와 마지막 시각을 알려주세요.", 220, "vomit", R),
        ("symptom.diarrhea.present", "Diarrhoea Present", "boolean", "diarrhea-present", "묽거나 물 같은 설사가 있나요?", 219, "stool", C),
        ("symptom.diarrhea.count_24h", "Stool Count 24 Hours", "integer", "stool-count", "최근 24시간 묽은 변 횟수는 몇 회인가요?", 218, "stool", C),
        ("symptom.diarrhea.severity", "Diarrhoea Severity", "severity", "diarrhea-severity", "설사는 가벼움·중간·심함 중 어느 정도인가요?", 217, "stool", C),
        ("vomiting_diarrhea.baseline_bowel_pattern_and_current_consistency", "Baseline and Current Stool", "string", "stool-baseline", "평소 배변 횟수·모양과 비교해 현재 변이 물 같음·묽음·기름짐·그 밖의 형태 중 어떻게 달라졌나요?", 216, "stool", C),
        ("vomiting_diarrhea.stool_blood_mucus_black_color_amount_and_photo_source", "Stool Blood and Mucus Detail", "string", "stool-blood-detail", "피·점액·검은 변이 있다면 색·양·횟수와 사진·검사자료 등 정보 출처를 알려주세요.", 215, "stool", R),
        ("vomiting_diarrhea.nocturnal_urgency_incontinence_or_tenesmus", "Nocturnal Urgency Incontinence or Tenesmus", "string", "stool-pattern", "밤에 자다가 설사하는지, 참기 어려운 급박감·실금·보고 나도 남은 느낌이나 통증이 있는지 알려주세요.", 214, "stool", D),
        ("vomiting_diarrhea.abdominal_pain_present", "Abdominal Pain Present", "boolean", "pain-present", "복통이나 반복되는 배 경련이 있나요?", 213, "pain", C),
        ("vomiting_diarrhea.abdominal_pain_nrs", "Abdominal Pain NRS", "integer", "pain-nrs", "[필수] 복통이 있다면 현재 통증을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 212, "pain", C),
        ("vomiting_diarrhea.pain_site_radiation_character_timing_and_relations", "Abdominal Pain Detail", "string", "pain-detail", "복통의 정확한 부위·퍼지는 곳·양상·지속시간과 식사·배변·구토·움직임과의 관계를 알려주세요.", 211, "pain", C),
        ("symptom.persistent_abdominal_or_back_pain", "Persistent Abdominal or Back Pain", "boolean", "persistent-pain", "복통이나 등 통증이 지속되거나 반복되나요?", 210, "pain", R),
        ("vomiting_diarrhea.abdominal_distension_flatus_and_bowel_change", "Distension and Flatus", "string", "distension", "배가 붓는 정도, 방귀·대변이 나오는지, 평소보다 배가 단단하거나 커졌는지 알려주세요.", 209, "pain", D),
        ("vomiting_diarrhea.oral_intake_type_amount_last_kept_down_and_thirst", "Oral Intake and Thirst", "string", "oral-intake", "최근 마신 물·수분보충액·모유·분유와 먹은 음식의 종류·양, 마지막으로 토하지 않고 유지한 시각과 갈증을 알려주세요.", 208, "hydration", R),
        ("vomiting_diarrhea.last_urine_time_frequency_color_and_diaper_count", "Urine and Diaper Detail", "string", "urine-detail", "마지막 소변 시각, 최근 횟수·양·색과 영유아라면 24시간 젖은 기저귀 수를 알려주세요.", 207, "hydration", R),
        ("vomiting_diarrhea.weight_before_current_change_and_measurement_source", "Weight Change and Source", "string", "weight", "증상 전후 체중과 측정 날짜·기기, 의도하지 않은 체중감소가 있다면 그 양을 알려주세요.", 206, "hydration", R),
        ("symptom.unintentional_weight_loss", "Unintentional Weight Loss", "boolean", "weight-loss", "의도하지 않은 체중감소가 있나요?", 205, "history", R),
        ("symptom.fever", "Fever", "boolean", "fever", "측정된 발열이나 열감·오한이 있나요?", 204, "history", R),
        ("vomiting_diarrhea.temperature_value_site_device_time_and_trend", "Temperature Context", "string", "temperature", "체온을 쟀다면 최고값·측정 시각·부위·기기와 변화 추세를 알려주세요.", 203, "history", R),
        ("vomiting_diarrhea.associated_headache_rash_respiratory_urinary_or_jaundice", "Associated System Symptoms", "string", "associated", "두통·발진·기침·숨참·소변통·옆구리통증·피부나 눈의 황달 등 함께 있는 증상을 알려주세요.", 202, "history", D),
        ("vomiting_diarrhea.eating_drinking_sleep_work_school_selfcare_impact", "Functional Impact", "string", "function", "먹기·마시기·수면·화장실 이용·자가관리·직장·학교에 어느 정도 영향을 주는지 알려주세요.", 201, "handoff", R),
        ("exposure.sick_contact_gastrointestinal", "Gastrointestinal Sick Contact", "boolean", "sick-contact", "주변에 비슷한 구토·설사를 하는 사람이 있나요?", 190, "exposure", D),
        ("exposure.suspect_food_or_water", "Suspect Food or Water", "boolean", "food-water", "증상 전 의심되는 음식·물·공동식사가 있나요?", 189, "exposure", D),
        ("vomiting_diarrhea.food_water_meal_place_preparation_and_cluster_detail", "Food Water and Cluster Detail", "string", "food-detail", "먹은 음식·물, 장소·조리상태·시각과 함께 먹은 사람 중 아픈 사람의 수와 증상 시작 시각을 알려주세요.", 188, "exposure", R),
        ("exposure.recent_international_travel", "Recent International Travel", "boolean", "travel", "최근 해외여행이나 해외 체류가 있었나요?", 187, "exposure", R),
        ("vomiting_diarrhea.travel_destination_dates_food_water_healthcare_and_onset", "Travel Detail", "string", "travel-detail", "여행지·출발/귀국일, 현지 음식·물·수영·동물·의료기관 노출과 증상 시작일을 알려주세요.", 186, "exposure", R),
        ("vomiting_diarrhea.childcare_care_facility_healthcare_animal_or_freshwater_exposure", "Institutional Animal or Freshwater Exposure", "string", "other-exposure", "어린이집·학교·요양시설·의료기관, 동물 접촉, 수영장·계곡·호수 노출과 날짜를 알려주세요.", 185, "exposure", R),
        ("medication.recent_antibiotics", "Recent Antibiotics", "boolean", "recent-antibiotics", "최근 항생제를 복용하거나 주사로 맞았나요?", 184, "treatment", R),
        ("vomiting_diarrhea.antibiotic_name_route_start_stop_and_diarrhea_relation", "Antibiotic Detail", "string", "antibiotic-detail", "항생제 이름·투여경로·시작/종료일과 설사 시작 시각의 관계를 알려주세요.", 183, "treatment", R),
        ("vomiting_diarrhea.current_medicines_recent_changes_laxative_glp1_metformin_and_supplements", "Medicines and Recent Changes", "string", "medicines", "현재 약과 최근 시작·증량·중단한 약, 변비약·메트포르민·GLP-1 계열 주사·건강기능식품이 있다면 이름·용량·날짜를 알려주세요.", 182, "treatment", R),
        ("vomiting_diarrhea.medicine_food_allergies_and_reactions", "Allergies and Reactions", "string", "allergies", "약·음식 알레르기와 실제 나타난 반응을 알려주세요.", 181, "history", R),
        ("vomiting_diarrhea.gi_conditions_surgery_stoma_feeding_tube_and_baseline", "GI History Surgery and Devices", "string", "gi-history", "염증성장질환·셀리악병·흡수장애·간담췌 질환, 복부수술, 장루·영양관과 평소 상태를 알려주세요.", 180, "history", R),
        ("vomiting_diarrhea.diabetes_kidney_adrenal_immunocompromise_and_frailty", "High Risk Conditions", "string", "high-risk-history", "당뇨·신장·부신 질환, 암치료·이식·면역억제, 허약·영양실조 등 탈수 위험을 높일 수 있는 상태를 알려주세요.", 179, "history", R),
        ("patient.immunocompromised", "Immunocompromised", "boolean", "immunocompromised", "면역저하 상태인가요?", 178, "history", R),
        ("patient.age_65_or_older", "Age 65 or Older", "boolean", "older-age", "만 65세 이상인가요?", 177, "history", R),
        ("pregnancy.possible", "Possible Pregnancy", "boolean", "pregnancy-possible", "임신 가능성이 있나요?", 176, "pregnancy", R),
        ("vomiting_diarrhea.pregnancy_gestation_lmp_postpartum_date_feeding_and_obstetric_symptoms", "Pregnancy and Postpartum Detail", "string", "pregnancy-detail", "임신 주수·마지막 월경일 또는 출산·유산·임신종결 날짜, 수유 여부와 질출혈·골반통 등 산과 증상을 알려주세요.", 175, "pregnancy", R),
        ("vomiting_diarrhea.child_age_weight_birth_history_feeding_and_baseline", "Child Baseline", "string", "child-baseline", "소아의 정확한 나이·현재/평소 체중, 미숙아·저체중 출생 여부, 모유·분유·이유식과 평소 활동을 알려주세요.", 174, "child", R),
        ("vomiting_diarrhea.child_responsiveness_tears_fontanelle_skin_color_and_extremities", "Child Dehydration Observation", "string", "child-observation", "아이의 반응·보챔·처짐, 눈물, 눈·숨구멍이 들어가 보임, 피부색·손발 온도 변화를 보호자가 관찰한 대로 알려주세요.", 173, "child", R),
        ("vomiting_diarrhea.child_stool_vomit_counts_feeding_and_diapers_24h", "Child 24 Hour Intake Output", "string", "child-intake-output", "최근 24시간 구토·설사 횟수, 먹인 수분·모유·분유의 양과 젖은 기저귀 수를 알려주세요.", 172, "child", R),
        ("vomiting_diarrhea.prior_similar_episodes_previous_diagnosis_and_admissions", "Prior Episodes", "string", "prior-episodes", "이전 비슷한 증상의 횟수·시기, 들은 진단과 응급실·입원 경험을 알려주세요.", 160, "handoff", R),
        ("vomiting_diarrhea.prior_assessment_tests_results_and_source", "Prior Assessment and Tests", "string", "prior-tests", "이번 증상으로 이미 진료·검사를 받았다면 날짜·기관, 혈액·대변·영상 결과와 원본 또는 전달받은 설명을 알려주세요.", 159, "handoff", R),
        ("vomiting_diarrhea.oral_rehydration_antiemetic_antidiarrheal_antibiotic_and_response", "Treatment and Response", "string", "treatment-response", "수분보충액·구토약·지사제·항생제 등 시행한 조치의 이름·용량·시각과 효과·부작용을 알려주세요.", 158, "treatment", R),
        ("vomiting_diarrhea.patient_concern_goal_and_additional_comment", "Patient Concern Goal and Other Detail", "string", "concern-goal", "가장 걱정되는 점, 의료진에게 원하는 도움과 질문에 없지만 전달할 내용을 알려주세요.", 157, "handoff", R),
    ]
    reused = {
        "symptom.persistent_abdominal_or_back_pain", "symptom.unintentional_weight_loss",
        "symptom.fever", "exposure.sick_contact_gastrointestinal",
        "exposure.suspect_food_or_water", "exposure.recent_international_travel",
        "medication.recent_antibiotics", "patient.immunocompromised",
        "patient.age_65_or_older", "pregnancy.possible",
    }
    for spec in specs:
        item = Q(*spec, reuse_existing=spec[0] in reused)
        # The deterministic research runtime parses enumerated coded answers;
        # generic free-standing ``severity`` values have no common parser.
        if spec[2] == "severity":
            item["fact"]["value_type"] = "coded"
            item["fact"]["allowed_values"] = ["mild", "moderate", "severe"]
        e.append(item)
    safety = [
        ("collapse", "vomiting_diarrhea.collapse_shock_or_unresponsive", "emergency"),
        ("hematemesis", "symptom.hematemesis", "emergency"),
        ("green-vomit", "symptom.green_vomit", "emergency"),
        ("poisoning", "exposure.possible_poisoning", "emergency"),
        ("severe-pain", "symptom.sudden_severe_abdominal_pain", "emergency"),
        ("major-stool-bleeding", "vomiting_diarrhea.black_stool_or_large_rectal_bleeding", "emergency"),
        ("confusion", "symptom.confusion", "emergency"),
        ("neuro-warning", "vomiting_diarrhea.neck_stiffness_rash_or_severe_headache", "emergency"),
        ("child-abdomen-warning", "vomiting_diarrhea.child_bilious_vomit_distension_or_severe_local_pain", "emergency"),
        ("pregnancy-warning", "vomiting_diarrhea.pregnancy_postpartum_bleeding_severe_pain_or_collapse", "emergency"),
        ("bloody-diarrhea", "symptom.bloody_diarrhea", "urgent"),
        ("unable-fluids", "symptom.unable_to_keep_fluids", "urgent"),
        ("high-risk-dehydration", "vomiting_diarrhea.rapid_worsening_or_high_risk_dehydration", "urgent"),
        ("vomiting-persistent", "symptom.vomiting_over_two_days", "urgent"),
        ("diarrhea-persistent", "symptom.diarrhea_over_seven_days", "urgent"),
    ]
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, 1000 if level == "emergency" else 950) for key, fid, level in safety]
    rules.append(safety_rule(P, "dehydration-low-urine", {"all": [{"fact": "symptom.dehydration_signs", "equals": True}, {"fact": "symptom.reduced_urine_output", "equals": True}]}, "urgent", 960))
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-17", "next_monitor_at": "2026-07-18", "next_full_review_at": "2027-01-13"})
    return {"id": "knowledge.generated.gastrointestinal.vomiting-diarrhea", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-vomiting-diarrhea-research", "default_refresh": refresh, "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="vomiting_diarrhea.primary_group", question_budget=80, source_refs=SOURCES)
    common = {
        "vomiting_diarrhea.information_source_proxy_reliability_and_conflict", "vomiting_diarrhea.age_life_stage_baseline_and_frailty", "symptom.duration",
        "vomiting_diarrhea.onset_date_time_first_symptom_and_speed", "vomiting_diarrhea.continuous_episodic_frequency_trend_and_baseline",
        "symptom.vomiting.present", "symptom.vomiting.count_24h", "symptom.diarrhea.present", "symptom.diarrhea.count_24h",
        "vomiting_diarrhea.abdominal_pain_present", "vomiting_diarrhea.oral_intake_type_amount_last_kept_down_and_thirst",
        "vomiting_diarrhea.last_urine_time_frequency_color_and_diaper_count", "symptom.fever", "vomiting_diarrhea.eating_drinking_sleep_work_school_selfcare_impact",
        "vomiting_diarrhea.current_medicines_recent_changes_laxative_glp1_metformin_and_supplements", "vomiting_diarrhea.medicine_food_allergies_and_reactions",
        "vomiting_diarrhea.prior_similar_episodes_previous_diagnosis_and_admissions", "vomiting_diarrhea.prior_assessment_tests_results_and_source",
        "vomiting_diarrhea.oral_rehydration_antiemetic_antidiarrheal_antibiotic_and_response", "vomiting_diarrhea.patient_concern_goal_and_additional_comment",
    }
    p["required_facts"]["routine"] = sorted(common)
    cases = {
        "vomiting_predominant": ["symptom.vomiting.severity", "vomiting_diarrhea.vomit_timing_meal_relation_volume_and_content", "vomiting_diarrhea.projectile_effortless_regurgitation_and_retching", "vomiting_diarrhea.vomit_blood_color_amount_and_coffee_ground_detail"],
        "diarrhea_predominant": ["symptom.diarrhea.severity", "vomiting_diarrhea.baseline_bowel_pattern_and_current_consistency", "vomiting_diarrhea.stool_blood_mucus_black_color_amount_and_photo_source", "vomiting_diarrhea.nocturnal_urgency_incontinence_or_tenesmus"],
        "both_acute": ["symptom.vomiting.severity", "symptom.diarrhea.severity", "vomiting_diarrhea.vomit_timing_meal_relation_volume_and_content", "vomiting_diarrhea.baseline_bowel_pattern_and_current_consistency"],
        "persistent_or_recurrent": ["symptom.persistent_abdominal_or_back_pain", "symptom.unintentional_weight_loss", "vomiting_diarrhea.gi_conditions_surgery_stoma_feeding_tube_and_baseline", "vomiting_diarrhea.weight_before_current_change_and_measurement_source"],
        "travel_food_or_cluster": ["exposure.sick_contact_gastrointestinal", "exposure.suspect_food_or_water", "vomiting_diarrhea.food_water_meal_place_preparation_and_cluster_detail", "exposure.recent_international_travel", "vomiting_diarrhea.travel_destination_dates_food_water_healthcare_and_onset", "vomiting_diarrhea.childcare_care_facility_healthcare_animal_or_freshwater_exposure"],
        "post_antibiotic_or_healthcare": ["medication.recent_antibiotics", "vomiting_diarrhea.antibiotic_name_route_start_stop_and_diarrhea_relation", "vomiting_diarrhea.childcare_care_facility_healthcare_animal_or_freshwater_exposure", "vomiting_diarrhea.gi_conditions_surgery_stoma_feeding_tube_and_baseline"],
        "pregnancy_postpartum": ["pregnancy.possible", "vomiting_diarrhea.pregnancy_gestation_lmp_postpartum_date_feeding_and_obstetric_symptoms", "vomiting_diarrhea.weight_before_current_change_and_measurement_source"],
        "infant_child_caregiver": ["vomiting_diarrhea.child_age_weight_birth_history_feeding_and_baseline", "vomiting_diarrhea.child_responsiveness_tears_fontanelle_skin_color_and_extremities", "vomiting_diarrhea.child_stool_vomit_counts_feeding_and_diapers_24h"],
        "condition_or_medicine_followup": ["vomiting_diarrhea.gi_conditions_surgery_stoma_feeding_tube_and_baseline", "vomiting_diarrhea.diabetes_kidney_adrenal_immunocompromise_and_frailty", "medication.recent_antibiotics", "vomiting_diarrhea.antibiotic_name_route_start_stop_and_diarrhea_relation"],
        "other_unclear": ["vomiting_diarrhea.associated_headache_rash_respiratory_urinary_or_jaundice", "vomiting_diarrhea.abdominal_distension_flatus_and_bowel_change", "vomiting_diarrhea.diabetes_kidney_adrenal_immunocompromise_and_frailty"],
    }
    p["conditional_required_facts"] = [{"selector_fact": "vomiting_diarrhea.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nhs.diarrhoea-vomiting.2026", "NHS", "Diarrhoea and vomiting", "accessed-2026-07-17", "https://www.nhs.uk/symptoms/diarrhoea-and-vomiting/", "public_health_guidance", ["Blood or coffee-ground vomit, green vomit, suspected poisoning, sudden severe abdominal pain, confusion and severe breathing difficulty are warning features.", "Inability to keep fluid down, blood in stool, prolonged vomiting or diarrhoea and dehydration require timely clinical review."]),
        ("source.nhs.dehydration.2026", "NHS", "Dehydration", "accessed-2026-07-17", "https://www.nhs.uk/conditions/dehydration/", "public_health_guidance", ["Thirst, dark or reduced urine, dry mouth, dizziness, reduced alertness and fewer wet nappies support dehydration assessment."]),
        ("source.cdc.food-poisoning.2025", "CDC", "Food Safety Signs and Symptoms", "updated-2025-11-24", "https://www.cdc.gov/food-safety/signs-symptoms/index.html", "public_health_guidance", ["Food, water, shared meal, symptom timing, bloody diarrhoea, fever, frequent vomiting and dehydration are relevant history; exposure does not establish an organism."]),
        ("source.cdc.yellow-book.travelers-diarrhea.2026", "CDC", "Travelers' Diarrhea", "Yellow-Book-2026-updated-2026-03-24", "https://www.cdc.gov/yellow-book/hcp/preparing-international-travelers/travelers-diarrhea.html", "clinical_guideline", ["Destination, travel dates, food and water exposure, incubation, onset, stool frequency, blood, fever, pain and persistence support returned-traveller handoff.", "The package does not infer a pathogen or recommend empiric antimicrobial treatment."]),
        ("source.cdc.c-diff.2026", "CDC", "About C. diff", "updated-2026-05", "https://www.cdc.gov/c-diff/about/index.html", "public_health_guidance", ["Antibiotic name, route, start and stop dates and relation to diarrhoea are relevant because risk is increased during antibiotics and after completion.", "The interview does not diagnose C. difficile infection."]),
        ("source.nice.cg84.gastroenteritis-under-5", "NICE", "Diarrhoea and vomiting caused by gastroenteritis in under 5s", "CG84-2009-current-2026", "https://www.nice.org.uk/guidance/cg84/chapter/Recommendations", "clinical_guideline", ["Caregiver history includes sudden stool or vomiting change, contacts, food or water, travel, counts in 24 hours, intake, urine, responsiveness and dehydration risk.", "Green vomit, blood or mucus, severe or localized pain, distension, altered consciousness, neck stiffness, rash and respiratory difficulty can indicate an alternative serious condition."]),
        ("source.nice.ng12.vomiting-diarrhea.2026", "NICE", "Suspected cancer recognition and referral", "NG12-updated-2026", "https://www.nice.org.uk/guidance/ng12/chapter/Recommended-actions-organised-by-symptom-and-findings-of-primary-care-investigations", "nice_guidance", ["Persistent unexplained symptoms, weight loss, abdominal or back pain and age-dependent context should be available to the clinician without assigning cancer."]),
        ("source.stom.mrcm.vomiting-diarrhea.20260714", "Infoclinic", "STOM vomiting and diarrhoea terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/422400008", "terminology_server", ["Build-time verification confirmed active vomiting and diarrhoea focus concepts and allowed Finding site and Severity attributes.", "MRCM is terminology metadata and does not create questions, diagnosis or safety rules."]),
    ]
    artifacts = []
    verified_now = {
        "source.cdc.yellow-book.travelers-diarrhea.2026",
        "source.cdc.c-diff.2026",
        "source.nice.cg84.gastroenteritis-under-5",
    }
    for sid, publisher, title, version, url, profile, assertions in defs:
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "allowed", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-17" if sid in verified_now else "2026-07-14", "monitor_result": "current_official_source_confirmed" if sid in verified_now else "not_due_existing_metadata_preserved", "assertions": assertions})
    research = {"id": "source-manifest.primary-care-vomiting-diarrhea-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.vomiting-diarrhea", "generated_clinical_knowledge", "knowledge/generated/gastrointestinal/vomiting-diarrhea/vomiting-diarrhea.json", True),
        ("source.mapping.vomiting-diarrhea", "terminology_mapping", "mappings/terminology/snomed-mrcm-vomiting-diarrhea.json", False),
        ("source.external.vomiting-diarrhea", "external_source_manifest", "sources/manifests/primary-care-vomiting-diarrhea-research.json", False),
        ("source.policy.vomiting-diarrhea", "runtime_policy", "policies/primary-care-vomiting-diarrhea-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-vomiting-diarrhea", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        key = rule["id"].split("safety.")[1]
        condition, level = rule["when"], rule["then"]["safety_level"]
        children = condition.get("all", [condition])
        state = {child["fact"]: {"value": child.get("equals", True)} for child in children}
        out[f"VOMITING-DIARRHEA-{key.upper()}.json"] = {"id": f"VOMITING-DIARRHEA-{key.upper()}", "simulation_language": "ko", "persona": {"age": 4 if key == "child-abdomen-warning" else 25 + index * 3}, "initial_statement": {"ko": "구토나 설사로 진료 전 문진을 합니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 22, "forbidden_assertions": ["diagnosis.gastroenteritis", "diagnosis.food_poisoning", "diagnosis.c_difficile"]}, "provenance": provenance(SOURCES)}
    policy, by_id = completion(f), {item["fact"]["id"]: item["fact"] for item in f["entries"]}
    def routine(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"][branch])
        values = {}
        for fid in required:
            fact = by_id[fid]
            if fact["value_type"] == "boolean": value = False
            elif fact["value_type"] == "integer": value = 0
            elif fact["value_type"] == "coded": value = fact.get("allowed_values", ["other_unclear"])[0]
            elif fact["value_type"] == "quantity": value = "2 days"
            elif fact["value_type"] == "severity": value = "mild"
            else: value = "특이사항 없음"
            values[fid] = {"value": value}
        values["vomiting_diarrhea.primary_group"] = {"value": branch}
        values["symptom.vomiting_diarrhea.presentation"] = {"value": "both"}
        return values
    routine_specs = [
        ("TRAVEL-FOOD-CLUSTER", "travel_food_or_cluster", 32, "해외여행 뒤 설사가 시작되어 노출 내용을 정리합니다.", {"exposure.recent_international_travel": {"value": True}, "vomiting_diarrhea.travel_destination_dates_food_water_healthcare_and_onset": {"value": "태국 7월 1~8일, 귀국 다음 날 물설사 시작"}}),
        ("POST-ANTIBIOTIC", "post_antibiotic_or_healthcare", 71, "항생제를 먹은 뒤 설사가 생겼습니다.", {"medication.recent_antibiotics": {"value": True}, "vomiting_diarrhea.antibiotic_name_route_start_stop_and_diarrhea_relation": {"value": "경구 항생제 7일 복용, 종료 3일 뒤 설사 시작"}}),
        ("CHILD-PROXY", "infant_child_caregiver", 2, "두 살 아이의 구토와 설사를 보호자가 답합니다.", {"vomiting_diarrhea.child_stool_vomit_counts_feeding_and_diapers_24h": {"value": "구토 2회, 묽은 변 4회, 젖은 기저귀 5개"}}),
        ("PREGNANCY", "pregnancy_postpartum", 29, "임신 중 구토가 있어 산과 정보를 함께 전달합니다.", {"pregnancy.possible": {"value": True}, "vomiting_diarrhea.pregnancy_gestation_lmp_postpartum_date_feeding_and_obstetric_symptoms": {"value": "임신 11주, 질출혈·골반통 없음"}}),
        ("MULTI-RFE-HEADACHE", "other_unclear", 38, "설사와 두통이 함께 있어 둘 다 전달하고 싶습니다.", {"vomiting_diarrhea.associated_headache_rash_respiratory_urinary_or_jaundice": {"value": "두통이 별도 문제로 반복되어 추가 문진 요청"}}),
    ]
    for key, branch, age, statement, overrides in routine_specs:
        state = routine(branch); state.update(overrides)
        out[f"VOMITING-DIARRHEA-{key}.json"] = {"id": f"VOMITING-DIARRHEA-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": state, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 85, "forbidden_assertions": ["diagnosis.gastroenteritis", "diagnosis.travelers_diarrhea"]}, "provenance": provenance(SOURCES)}
    absent = routine("vomiting_predominant")
    missing = "vomiting_diarrhea.prior_assessment_tests_results_and_source"; absent.pop(missing)
    out["VOMITING-DIARRHEA-REMOTE-DATA-ABSENT.json"] = {"id": "VOMITING-DIARRHEA-REMOTE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 66}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "patient", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "전화로 구토 문진을 합니다. 검사자료는 없습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {missing: "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 85, "forbidden_assertions": ["diagnosis.gastroenteritis"]}, "provenance": provenance(SOURCES)}
    pain = routine("both_acute"); pain["vomiting_diarrhea.abdominal_pain_present"] = {"value": True}; pain["vomiting_diarrhea.abdominal_pain_nrs"] = {"value": 5}; pain["pain.frequency"] = {"value": "less_than_daily"}
    out["VOMITING-DIARRHEA-PAIN-NRS.json"] = {"id": "VOMITING-DIARRHEA-PAIN-NRS", "simulation_language": "ko", "persona": {"age": 44}, "initial_statement": {"ko": "구토와 설사, 복통이 있습니다."}, "hidden_state": pain, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"vomiting_diarrhea.abdominal_pain_nrs": 5}, "expected_max_turns": 85, "forbidden_assertions": ["diagnosis.gastroenteritis"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Vomiting or Diarrhoea", intents=[("intent.characterize_symptom", "Characterize Vomiting Diarrhoea Pain Hydration Course and Functional Impact"), ("intent.screen_red_flags", "Screen Bleeding Bilious Vomit Poisoning Acute Abdomen Neurologic Dehydration Pregnancy and Child Warning Features"), ("intent.differentiate_common_causes", "Localize Vomit Stool Exposure Medicine Travel and Associated Features"), ("intent.risk_assessment", "Assess Life Stage Comorbidity Medicine Exposure Prior Tests Treatment Response and Patient Goals")])
    primary, research = source_docs()
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": "422400008", "display": "Vomiting (disorder)", "concept_active": True}, {"code": "62315008", "display": "Diarrhea (finding)", "concept_active": True}], "verified_attribute_ids": ["363698007", "246112005"], "validation": {"method": "build_time_live_mrcm_summary", "checked_at": "2026-07-14T00:00:00Z", "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "vomiting_diarrhea_semantics": {"diagnosis_inferred": False, "infectious_organism_inferred": False, "dehydration_score_calculated": False, "c_difficile_diagnosed": False, "runtime_terminology_query_required": False}, "provenance": provenance(["source.stom.mrcm.vomiting-diarrhea.20260714"])}
    documents = [("knowledge/base/primary-care-vomiting-diarrhea.json", graph), ("rules/base/primary-care-vomiting-diarrhea.json", rules), ("knowledge/generated/gastrointestinal/vomiting-diarrhea/vomiting-diarrhea.json", f), ("mappings/terminology/snomed-mrcm-vomiting-diarrhea.json", mapping), ("sources/manifests/primary-care-vomiting-diarrhea.json", primary), ("sources/manifests/primary-care-vomiting-diarrhea-research.json", research), ("policies/primary-care-vomiting-diarrhea-completion.json", completion(f))]
    for path, document in documents: write_json(path, document)
    for name, case in cases(f).items(): write_json("simulation/patients/gastrointestinal/vomiting-diarrhea/" + name, case)


if __name__ == "__main__":
    main()
