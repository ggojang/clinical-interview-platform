#!/usr/bin/env python3
"""Rebuild unreviewed fever knowledge for clinician pre-visit handoff."""
from profile_support import *

P, RFE = "fever", "rfe.fever"
M, SN = "mapping.snomed-mrcm.fever", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-16T10:00:00Z"
SOURCES = [
    "source.nice.ng253.sepsis-adults.2025",
    "source.nice.ng254.sepsis-under16.2025",
    "source.nice.ng255.sepsis-pregnancy.2026",
    "source.nice.ng240.meningitis.2024",
    "source.cdc.yellow-book.post-travel-fever.2026",
    "source.nhs.fever-adults.2023",
    "source.nhs.fever-children.2026",
    "source.stom.fever.20260716",
]
G = {key: f"group.fever.{key}" for key in (
    "routing", "safety", "character", "respiratory", "urinary",
    "gastrointestinal", "neurological", "skin_joint", "reproductive",
    "exposure", "risk", "followup", "function",
)}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("fever.primary_group", "Primary Fever Context", "coded", "primary-group", "이번 발열·열감은 현재 급성 발열, 반복·주기적 발열, 오래 지속되는 발열, 여행·특정 노출 후 발열, 시술·수술·기구·치료 후 발열, 면역저하·고위험 상태의 발열, 검사·치료 후 추적, 체온은 재지 않았지만 열감이 있는 경우 중 무엇에 가장 가깝나요?", 240, [G["routing"]], C, allowed_values=["acute_current_fever", "recurrent_or_periodic_fever", "persistent_or_prolonged_fever", "post_travel_or_specific_exposure", "post_procedure_device_or_treatment", "immunocompromised_or_high_risk", "test_or_treatment_followup", "feverish_not_measured", "other_unclear"]),
        Q("fever.reduced_consciousness_or_new_confusion", "Reduced Consciousness or New Confusion", "boolean", "reduced-consciousness", "새로 혼란스럽거나 깨우기 어렵고 평소와 다른 행동·의식 저하가 있나요?", 239, [G["safety"], G["neurological"]], S, safety_relevant=True),
        Q("fever.severe_breathing_cyanosis_or_new_high_oxygen_need", "Severe Respiratory Warning", "boolean", "severe-breathing", "숨을 매우 힘들게 쉬거나 입술·혀가 파래지고, 말을 잇기 어렵거나 평소보다 많은 산소가 필요한가요?", 238, [G["safety"], G["respiratory"]], S, safety_relevant=True),
        Q("fever.collapse_mottled_ashen_or_shock_features", "Collapse or Circulatory Warning", "boolean", "shock-warning", "쓰러짐·실신, 차갑고 축축한 피부, 회색빛·얼룩덜룩한 피부, 매우 빠른 맥박 또는 심한 어지럼이 있나요?", 237, [G["safety"]], S, safety_relevant=True),
        Q("symptom.non_blanching_rash", "Non-blanching or Purpuric Rash", "boolean", "non-blanching-rash", "눌러도 옅어지지 않는 붉거나 자주색 점·멍 같은 발진이 새로 생겼나요?", 236, [G["safety"], G["skin_joint"]], S, safety_relevant=True, reuse_existing=True),
        Q("fever.meningitis_warning_combination", "Meningitis Warning Combination", "boolean", "meningitis-warning", "심한 두통과 목 경직이 있으면서 혼란·심한 졸림 또는 빛을 보기 힘든 증상이 함께 있나요?", 235, [G["safety"], G["neurological"]], S, safety_relevant=True),
        Q("fever.new_seizure_or_focal_neurologic_deficit", "Seizure or Focal Neurologic Warning", "boolean", "seizure-neurology", "처음 발생한 경련, 한쪽 힘 빠짐·감각 저하, 새 말하기 장애 또는 갑작스러운 신경학적 변화가 있나요?", 234, [G["safety"], G["neurological"]], S, safety_relevant=True),
        Q("fever.no_urine_or_severe_dehydration", "Severe Dehydration Warning", "boolean", "severe-dehydration", "12시간 이상 소변을 거의 보지 못했거나 물을 마시지 못하고 계속 토하며 입이 매우 마르고 심하게 처지나요?", 233, [G["safety"], G["gastrointestinal"]], S, safety_relevant=True),
        Q("fever.recent_anticancer_or_neutropenia_risk", "Neutropenic Sepsis Risk", "boolean", "neutropenia-risk", "최근 30일 이내 전신 항암치료를 받았거나 의료진에게 호중구감소·심한 면역억제 위험이 있다고 들은 상태에서 열이 나나요?", 232, [G["safety"], G["risk"]], S, safety_relevant=True),
        Q("fever.young_infant_temperature_warning", "Young Infant Fever Warning", "boolean", "young-infant-warning", "생후 3개월 미만인데 38℃ 이상이거나 열이 의심되거나, 생후 3~6개월인데 39℃ 이상이거나 평소와 다르게 많이 처지나요?", 231, [G["safety"], G["risk"]], S, safety_relevant=True),
        Q("fever.pregnancy_postpartum_severe_infection_warning", "Pregnancy or Postpartum Infection Warning", "boolean", "pregnancy-warning", "임신 중이거나 출산·유산·임신종결 후 6주 이내이며, 발열과 함께 심한 처짐·숨참·혼란·심한 복통·악취 나는 분비물 또는 상처 악화가 있나요?", 230, [G["safety"], G["reproductive"]], S, safety_relevant=True),
        Q("fever.travel_with_bleeding_altered_mental_state_or_instability", "High-consequence Travel Fever Warning", "boolean", "travel-warning", "최근 해외 체류 뒤 발열과 함께 원인 모를 출혈·자주색 발진, 의식 변화, 심한 숨참 또는 쓰러질 듯한 상태가 있나요?", 229, [G["safety"], G["exposure"]], S, safety_relevant=True),
        Q("fever.post_procedure_device_wound_severe_infection", "Post-procedure or Device Infection Warning", "boolean", "procedure-infection", "최근 수술·시술·분만 또는 카테터·주사관 주변에 심한 통증·붉음·고름·상처 벌어짐이 있고 발열·오한·전신 악화가 있나요?", 228, [G["safety"], G["risk"]], S, safety_relevant=True),

        Q("fever.information_source_proxy_and_reliability", "Information Source and Reliability", "string", "information-source", "누가 답변하며 본인 측정, 보호자 관찰, 체온계 기록, 사진, 검사결과 중 무엇에 근거하나요? 확실하지 않거나 서로 다른 정보도 알려주세요.", 210, [G["routing"]], C),
        Q("fever.age_life_stage_and_baseline", "Age and Life Stage", "string", "age-life-stage", "만 나이 또는 생후 개월 수, 임신·산후 여부와 평소 건강·기능 상태를 알려주세요.", 209, [G["risk"]], R),
        Q("symptom.duration", "Fever Duration", "quantity", "duration", "처음 열감이나 측정된 발열이 시작된 날짜·시각과 지금까지의 기간을 알려주세요.", 208, [G["character"]], C, reuse_existing=True),
        Q("observation.body_temperature", "Measured Body Temperature", "quantity", "temperature", "측정한 체온이 있다면 가장 최근 값과 최고·최저값을 ℃로 알려주세요. 측정하지 않았다면 그렇게 알려주세요.", 207, [G["character"]], C, reuse_existing=True),
        Q("fever.measurement_site_device_time_and_circumstance", "Temperature Measurement Context", "string", "measurement-context", "체온을 언제, 귀·입·겨드랑이·이마·직장 중 어디에서 어떤 체온계로 측정했으며 해열제 전후 중 언제였나요?", 206, [G["character"]], C),
        Q("fever.current_status_peak_trend_and_pattern", "Fever Course and Pattern", "string", "course-pattern", "지금도 열이 있는지, 계속·간헐·매일 특정 시간·주기적 반복인지와 최고점·호전·악화 추세를 알려주세요.", 205, [G["character"]], C),
        Q("symptom.chills", "Chills Sweats or Rigors", "boolean", "chills", "오한, 이를 부딪칠 정도의 심한 떨림 또는 식은땀·밤땀이 있나요?", 204, [G["character"]], C, reuse_existing=True, terminology_binding={"system": SN, "code": "248456009"}, mrcm_ref=M),
        Q("fever.chills_sweats_timing_and_severity", "Chills and Sweats Detail", "string", "chills-detail", "오한·심한 떨림·땀의 시작 시각, 빈도, 지속시간과 체온 변화와의 관계를 알려주세요.", 203, [G["character"]], C),
        Q("fever.antipyretic_name_dose_time_and_temperature_response", "Antipyretic Use and Response", "string", "antipyretic-response", "아세트아미노펜·이부프로펜 등 해열제를 먹었다면 이름·용량·복용 시각과 전후 체온·증상 변화를 알려주세요.", 202, [G["followup"]], R),
        Q("fever.fluid_intake_urine_frequency_and_color", "Hydration and Urine", "string", "hydration", "평소 대비 마신 양, 마지막 소변 시각, 소변 횟수·양·색과 입 마름·어지럼을 알려주세요.", 201, [G["character"], G["gastrointestinal"]], R),
        Q("fever.acute_functional_decline_eating_drinking_mobility", "Acute Functional Decline", "string", "functional-decline", "식사·수분 섭취, 걷기, 일상생활, 수면과 돌봄 필요가 평소보다 어떻게 달라졌나요?", 200, [G["function"]], R),
        Q("symptom.systemically_unwell", "Systemically Unwell", "boolean", "systemic-unwellness", "열과 함께 평소와 달리 전반적으로 매우 아프거나 처진 상태인가요?", 199, [G["function"], G["safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("fever.pain_present", "Pain Present with Fever", "boolean", "pain-present", "열과 함께 통증이 있나요?", 199, [G["character"]], C),
        Q("fever.pain_nrs", "Fever-associated Pain NRS", "integer", "pain-nrs", "[필수] 통증이 있다면 현재 통증을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 198, [G["character"]], C),
        Q("fever.pain_site_character_and_course", "Pain Site and Character", "string", "pain-detail", "통증의 정확한 부위, 양상, 시작·지속시간, 움직임·호흡·식사·배뇨와의 관계를 알려주세요.", 197, [G["character"]], C),

        Q("symptom.cough", "Cough", "boolean", "cough", "기침이 있나요?", 180, [G["respiratory"]], D, reuse_existing=True),
        Q("fever.respiratory_nasal_throat_sputum_and_chest_features", "Respiratory and ENT Features", "string", "respiratory-detail", "콧물·코막힘·인후통·기침·가래·흉통·숨참의 시작, 심한 정도와 가래 색·피 여부를 알려주세요.", 179, [G["respiratory"]], D),
        Q("symptom.sore_throat", "Sore Throat", "boolean", "sore-throat", "목 통증이나 삼키기 어려움이 있나요?", 178, [G["respiratory"]], D, reuse_existing=True),
        Q("symptom.dyspnea", "Breathing Difficulty", "severity", "dyspnea", "숨참이 있다면 없음·가벼움·중간·심함 중 어느 정도이며 안정 시에도 있나요?", 177, [G["respiratory"]], D, reuse_existing=True),
        Q("symptom.urinary_symptoms", "Urinary Symptoms", "boolean", "urinary", "배뇨통, 빈뇨·절박뇨, 탁하거나 피 섞인 소변 또는 소변 냄새 변화가 있나요?", 174, [G["urinary"]], D, reuse_existing=True),
        Q("fever.flank_pelvic_or_genital_urinary_features", "Upper Urinary or Genital Features", "string", "urinary-detail", "옆구리·허리·아랫배 통증, 소변 문제, 생식기 분비물·통증과 시작 시점을 알려주세요.", 173, [G["urinary"], G["reproductive"]], D),
        Q("symptom.vomiting", "Vomiting", "boolean", "vomiting", "구토가 있나요?", 170, [G["gastrointestinal"]], D, reuse_existing=True),
        Q("symptom.diarrhea", "Diarrhea", "boolean", "diarrhea", "설사나 평소와 다른 묽은 변이 있나요?", 169, [G["gastrointestinal"]], D, reuse_existing=True),
        Q("symptom.abdominal_pain", "Abdominal Pain", "boolean", "abdominal-pain", "복통이 있나요?", 168, [G["gastrointestinal"]], D, reuse_existing=True),
        Q("fever.gastrointestinal_stool_blood_jaundice_and_intake", "Gastrointestinal Detail", "string", "gastrointestinal-detail", "구토·설사의 횟수와 혈액, 복통 위치, 황달, 식욕·섭취 변화와 최근 음식 노출을 알려주세요.", 167, [G["gastrointestinal"]], D),
        Q("symptom.headache", "Headache", "boolean", "headache", "새 두통이 있나요?", 164, [G["neurological"]], D, reuse_existing=True),
        Q("symptom.neck_stiffness", "Neck Stiffness", "boolean", "neck-stiffness", "목이 평소와 다르게 뻣뻣하거나 움직이기 어렵나요?", 163, [G["neurological"]], D, reuse_existing=True),
        Q("fever.neurologic_eye_ear_and_behavior_features", "Neurologic Sensory and Behavior Features", "string", "neurologic-detail", "두통·목 경직·빛 불편·눈 통증, 귀 통증, 어지럼, 혼란·행동 변화가 있으면 시작과 경과를 알려주세요.", 162, [G["neurological"]], D),
        Q("symptom.skin_infection_features", "Skin or Wound Infection Features", "boolean", "skin-infection", "붉고 뜨겁고 아픈 피부, 상처·고름 또는 빠르게 번지는 부위가 있나요?", 159, [G["skin_joint"]], D, reuse_existing=True),
        Q("fever.rash_wound_joint_or_localized_swelling_detail", "Skin Joint and Wound Detail", "string", "skin-joint-detail", "발진·물집·상처·피부 붉음, 관절 통증·부기, 국소 멍울의 위치·범위·사진 유무와 진행을 알려주세요.", 158, [G["skin_joint"]], D),
        Q("fever.pregnancy_postpartum_lactation_and_reproductive_source", "Pregnancy and Postpartum Context", "string", "reproductive-context", "임신 주수, 출산·유산·임신종결 날짜, 수유 여부와 골반통·분비물·유방·상처 증상을 알려주세요.", 155, [G["reproductive"]], R),

        Q("exposure.sick_contact", "Sick Contact or Cluster", "boolean", "sick-contact", "가족·학교·직장·시설에서 비슷하게 아픈 사람이나 알려진 유행이 있나요?", 150, [G["exposure"]], R, reuse_existing=True),
        Q("fever.travel_destinations_dates_onset_and_healthcare", "Travel Itinerary and Timing", "string", "travel-itinerary", "최근 1년 내 국내외 여행·체류 지역과 출입국 날짜, 여행 중·귀국 후 증상 시작 시점과 현지 진료·약 복용을 알려주세요.", 149, [G["exposure"]], R),
        Q("fever.insect_tick_animal_bite_scratch_or_contact", "Vector and Animal Exposure", "string", "vector-animal", "모기·진드기 등 벌레물림, 동물 물림·긁힘·사체·분비물 접촉과 날짜·지역을 알려주세요.", 148, [G["exposure"]], R),
        Q("fever.food_water_freshwater_and_group_meal_exposure", "Food Water and Environmental Exposure", "string", "food-water", "날음식·덜 익힌 음식·비살균 유제품·의심되는 물, 계곡·강·호수·온천, 단체식사와 함께 아픈 사람을 알려주세요.", 147, [G["exposure"]], R),
        Q("fever.sexual_sharps_tattoo_piercing_or_blood_exposure", "Sexual and Blood Exposure", "string", "sexual-blood", "답변 가능한 범위에서 최근 새 성접촉, 주사침·혈액, 문신·피어싱 등 감염 관련 노출과 날짜를 알려주세요.", 146, [G["exposure"]], R),
        Q("fever.occupation_healthcare_laboratory_animal_or_crowding_exposure", "Occupational and Congregate Exposure", "string", "occupation-exposure", "의료·돌봄·실험실·축산·동물·식품 관련 업무, 군대·기숙사·교정시설·보호시설 등 집단생활 노출이 있나요?", 145, [G["exposure"]], R),

        Q("patient.immunocompromised", "Immunocompromised State", "boolean", "immunocompromised", "면역을 약화시키는 질환이나 치료가 있나요?", 140, [G["risk"]], R, reuse_existing=True),
        Q("fever.immunosuppression_cancer_transplant_hiv_asplenia_and_last_treatment", "Immune Risk Detail", "string", "immune-detail", "암·항암치료, 이식, HIV, 비장 없음, 면역결핍, 스테로이드·생물학제제 등 면역억제 치료의 이름과 마지막 투여일을 알려주세요.", 139, [G["risk"]], R),
        Q("fever.chronic_conditions_frailty_and_baseline_vulnerability", "Chronic Conditions and Frailty", "string", "chronic-risk", "당뇨, 심장·폐·신장·간·신경 질환, 허약·거동 제한 등 중증 감염 위험이나 증상 표현에 영향을 줄 상태를 알려주세요.", 138, [G["risk"]], R),
        Q("fever.recent_surgery_procedure_delivery_dental_work_wound_or_device", "Recent Procedure and Device Context", "string", "procedure-device", "최근 6주 내 수술·시술·분만·치과치료·상처와 카테터·투석관·중심정맥관·인공관절 등 기구의 종류·날짜·부위를 알려주세요.", 137, [G["risk"]], R),
        Q("fever.vaccination_infection_history_and_previous_similar_episodes", "Vaccination and Infection History", "string", "vaccination-history", "최근 예방접종과 독감·COVID-19·폐렴구균·수막구균 등 접종력, 최근 감염·입원·내성균 및 이전 비슷한 발열을 알려주세요.", 136, [G["risk"]], R),
        Q("fever.current_medicines_antibiotics_antipyretics_and_recent_changes", "Medicines and Antibiotics", "string", "medicines", "현재 약·보충제, 최근 시작·중단·변경한 약, 최근 반복 항생제와 해열제의 이름·용량·복용 시각을 알려주세요.", 135, [G["risk"], G["followup"]], R),
        Q("fever.medicine_allergies_and_adverse_reactions", "Medicine Allergies", "string", "medicine-allergies", "항생제·해열제 등 약물 알레르기와 발생한 반응을 알려주세요.", 134, [G["risk"]], R),
        Q("fever.prior_tests_results_cultures_and_imaging", "Prior Tests and Results", "string", "prior-tests", "이번 발열로 시행한 혈액·소변·호흡기검사·배양·영상의 날짜와 수치·결과, 원본 유무를 알려주세요.", 130, [G["followup"]], R),
        Q("fever.treatment_antibiotic_start_response_and_adverse_effect", "Treatment and Response", "string", "treatment-response", "수액·해열제·항생제 등 치료의 시작일·용량·순응도, 체온·증상 반응과 부작용을 알려주세요.", 129, [G["followup"]], R),
        Q("fever.prior_clinical_assessment_diagnosis_and_followup_plan", "Prior Assessment and Plan", "string", "prior-assessment", "이미 진료받았다면 의료기관·날짜, 들은 설명, 재진·검사·격리 지시와 악화 시 계획을 알려주세요.", 128, [G["followup"]], R),
        Q("fever.patient_concern_goal_and_other_detail", "Patient Concern and Goal", "string", "patient-goal", "질문에 없지만 의료진에게 꼭 전달할 내용, 가장 걱정하는 점과 이번 진료에서 원하는 것을 알려주세요.", 120, [G["function"], G["routing"]], C),
    ]
    safety = [
        ("reduced-consciousness", "fever.reduced_consciousness_or_new_confusion", "emergency"),
        ("severe-breathing", "fever.severe_breathing_cyanosis_or_new_high_oxygen_need", "emergency"),
        ("shock-warning", "fever.collapse_mottled_ashen_or_shock_features", "emergency"),
        ("non-blanching-rash", "symptom.non_blanching_rash", "emergency"),
        ("meningitis-warning", "fever.meningitis_warning_combination", "emergency"),
        ("seizure-neurology", "fever.new_seizure_or_focal_neurologic_deficit", "emergency"),
        ("severe-dehydration", "fever.no_urine_or_severe_dehydration", "urgent"),
        ("neutropenia-risk", "fever.recent_anticancer_or_neutropenia_risk", "urgent"),
        ("young-infant-warning", "fever.young_infant_temperature_warning", "urgent"),
        ("pregnancy-warning", "fever.pregnancy_postpartum_severe_infection_warning", "urgent"),
        ("travel-warning", "fever.travel_with_bleeding_altered_mental_state_or_instability", "emergency"),
        ("procedure-infection", "fever.post_procedure_device_wound_severe_infection", "urgent"),
    ]
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-16", "next_monitor_at": "2026-07-17", "next_full_review_at": "2027-01-12"})
    return {
        "id": "knowledge.generated.systemic.fever", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-fever-research",
        "default_refresh": refresh,
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [],
        "safety_rules": [safety_rule(P, key, {"fact": fact, "equals": True}, level, 1000 if level == "emergency" else 990) for key, fact, level in safety],
        "entries": e, "provenance": provenance(SOURCES),
    }


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="fever.primary_group", question_budget=72, source_refs=SOURCES)
    common = {
        "fever.information_source_proxy_and_reliability", "fever.age_life_stage_and_baseline",
        "symptom.duration", "observation.body_temperature", "fever.measurement_site_device_time_and_circumstance",
        "fever.current_status_peak_trend_and_pattern", "symptom.chills", "fever.chills_sweats_timing_and_severity",
        "fever.antipyretic_name_dose_time_and_temperature_response", "fever.fluid_intake_urine_frequency_and_color",
        "fever.acute_functional_decline_eating_drinking_mobility", "symptom.systemically_unwell", "fever.pain_present",
        "fever.pain_site_character_and_course", "fever.chronic_conditions_frailty_and_baseline_vulnerability",
        "fever.vaccination_infection_history_and_previous_similar_episodes",
        "fever.current_medicines_antibiotics_antipyretics_and_recent_changes",
        "fever.medicine_allergies_and_adverse_reactions", "fever.prior_tests_results_cultures_and_imaging",
        "fever.treatment_antibiotic_start_response_and_adverse_effect",
        "fever.prior_clinical_assessment_diagnosis_and_followup_plan", "fever.patient_concern_goal_and_other_detail",
    }
    policy["required_facts"]["routine"] = sorted(common)
    branches = {
        "acute_current_fever": ["symptom.cough", "fever.respiratory_nasal_throat_sputum_and_chest_features", "symptom.sore_throat", "symptom.dyspnea", "symptom.urinary_symptoms", "fever.flank_pelvic_or_genital_urinary_features", "symptom.vomiting", "symptom.diarrhea", "symptom.abdominal_pain", "fever.gastrointestinal_stool_blood_jaundice_and_intake", "symptom.headache", "symptom.neck_stiffness", "fever.neurologic_eye_ear_and_behavior_features", "symptom.skin_infection_features", "fever.rash_wound_joint_or_localized_swelling_detail", "exposure.sick_contact"],
        "recurrent_or_periodic_fever": ["fever.current_status_peak_trend_and_pattern", "fever.vaccination_infection_history_and_previous_similar_episodes", "fever.chronic_conditions_frailty_and_baseline_vulnerability", "fever.immunosuppression_cancer_transplant_hiv_asplenia_and_last_treatment", "fever.occupation_healthcare_laboratory_animal_or_crowding_exposure"],
        "persistent_or_prolonged_fever": ["fever.current_status_peak_trend_and_pattern", "fever.travel_destinations_dates_onset_and_healthcare", "fever.occupation_healthcare_laboratory_animal_or_crowding_exposure", "fever.sexual_sharps_tattoo_piercing_or_blood_exposure", "fever.immunosuppression_cancer_transplant_hiv_asplenia_and_last_treatment"],
        "post_travel_or_specific_exposure": ["fever.travel_destinations_dates_onset_and_healthcare", "fever.insect_tick_animal_bite_scratch_or_contact", "fever.food_water_freshwater_and_group_meal_exposure", "fever.sexual_sharps_tattoo_piercing_or_blood_exposure", "fever.occupation_healthcare_laboratory_animal_or_crowding_exposure", "exposure.sick_contact"],
        "post_procedure_device_or_treatment": ["fever.recent_surgery_procedure_delivery_dental_work_wound_or_device", "symptom.skin_infection_features", "fever.rash_wound_joint_or_localized_swelling_detail", "fever.current_medicines_antibiotics_antipyretics_and_recent_changes"],
        "immunocompromised_or_high_risk": ["patient.immunocompromised", "fever.immunosuppression_cancer_transplant_hiv_asplenia_and_last_treatment", "fever.recent_surgery_procedure_delivery_dental_work_wound_or_device", "fever.occupation_healthcare_laboratory_animal_or_crowding_exposure"],
        "test_or_treatment_followup": ["fever.prior_tests_results_cultures_and_imaging", "fever.treatment_antibiotic_start_response_and_adverse_effect", "fever.prior_clinical_assessment_diagnosis_and_followup_plan"],
        "feverish_not_measured": ["observation.body_temperature", "fever.measurement_site_device_time_and_circumstance", "fever.current_status_peak_trend_and_pattern", "exposure.sick_contact"],
        "other_unclear": [],
    }
    policy["conditional_required_facts"] = [{"selector_fact": "fever.primary_group", "cases": branches}]
    return policy


def source_docs():
    defs = [
        ("source.nice.ng253.sepsis-adults.2025", "NICE", "Suspected sepsis in people aged 16 or over", "NG253-published-2025-11-19", "https://www.nice.org.uk/guidance/ng253", "clinical_guideline", ["Assessment considers non-localised severe illness, patient or carer concern, behaviour, circulation, respiration, immune impairment, recent invasive procedure, indwelling devices and repeated antibiotics.", "Runtime records history and patient-reported features but does not calculate NEWS2."]),
        ("source.nice.ng254.sepsis-under16.2025", "NICE", "Suspected sepsis in under 16s", "NG254-published-2025-11-19", "https://www.nice.org.uk/guidance/ng254", "clinical_guideline", ["Paediatric assessment is age-specific and uses caregiver history, examination and age-banded physiological criteria.", "The interview captures age, caregiver observation, feeding, urine, breathing, skin and neurological warning features without reproducing a professional score."]),
        ("source.nice.ng255.sepsis-pregnancy.2026", "NICE", "Suspected sepsis in pregnant or recently pregnant people", "NG255-reviewed-2026-03-05", "https://www.nice.org.uk/guidance/ng255", "clinical_guideline", ["Pregnancy and recent-pregnancy sepsis assessment uses a distinct pathway.", "The interview records gestation or outcome date, possible obstetric source and systemic warning features but does not calculate MEWS."]),
        ("source.nice.ng240.meningitis.2024", "NICE", "Bacterial meningitis and meningococcal disease", "NG240-published-2024-03-19", "https://www.nice.org.uk/guidance/ng240/chapter/Recommendations", "clinical_guideline", ["Fever, headache, neck stiffness and altered consciousness or cognition form the adult red-flag combination; antipyretics may obscure fever.", "Non-blanching rash, rapid deterioration and neurological features require emergency assessment, while absence of the full combination does not exclude disease."]),
        ("source.cdc.yellow-book.post-travel-fever.2026", "CDC", "Post-Travel Evaluation of the Ill Traveler", "Yellow-Book-2026", "https://www.cdc.gov/yellow-book/hcp/post-travel-evaluation/post-travel-evaluation-of-the-ill-traveler.html", "clinical_guideline", ["Returned-traveller fever history includes itinerary, timing, care abroad, vaccination and prophylaxis, medicines, food and water, vectors, animals, freshwater, sexual and sharps exposure.", "Respiratory distress, haemodynamic instability, altered mental state, bleeding or possible high-consequence infection requires prompt triage."]),
        ("source.nhs.fever-adults.2023", "NHS", "High temperature in adults", "reviewed-2023-05-24-review-due", "https://www.nhs.uk/symptoms/fever-in-adults/", "public_health_guidance", ["38°C or more is commonly considered fever, but hot, cold or shivery symptoms can occur below that measurement.", "Measurement context, hydration, urine and failure to improve inform history; this overdue-review page does not control safety rules."]),
        ("source.nhs.fever-children.2026", "NHS", "High temperature in children", "accessed-2026-07-16", "https://www.nhs.uk/symptoms/fever-in-children/", "public_health_guidance", ["Urgent assessment is advised for infants under 3 months with 38°C or more or suspected fever, and ages 3 to 6 months with 39°C or more or suspected fever.", "Caregiver concern, rash, first febrile seizure, poor intake, altered behaviour and fever lasting 5 days are relevant handoff items."]),
        ("source.stom.fever.20260716", "Infoclinic", "STOM fever terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/386661006", "terminology_server", ["Build-time STOM search confirmed active Fever 386661006, Shivering or rigors 248456009 and Hypothermia 386689009.", "MRCM returned Finding site and Severity for all three. LOINC 8310-5 is the quantitative body-temperature binding; MRCM does not create clinical rules."]),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, assertions in defs:
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-16", "monitor_result": "official_page_available_review_due" if sid == "source.nhs.fever-adults.2023" else "current_official_source_confirmed", "assertions": assertions})
    research = {"id": "source-manifest.primary-care-fever-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.fever", "generated_clinical_knowledge", "knowledge/generated/systemic/fever.json", True),
        ("source.mapping.fever", "terminology_mapping", "mappings/terminology/snomed-mrcm-fever.json", False),
        ("source.external.fever", "external_source_manifest", "sources/manifests/primary-care-fever-research.json", False),
        ("source.policy.fever", "runtime_policy", "policies/primary-care-fever-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-fever", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        fact_id, level = rule["when"]["fact"], rule["then"]["safety_level"]
        key = rule["id"].split("safety.")[1]
        out[f"FEVER-{key.upper()}.json"] = {
            "id": f"FEVER-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 1 if key == "young-infant-warning" else 20 + index * 5},
            "initial_statement": {"ko": "열이 나고 상태가 좋지 않아요."},
            "hidden_state": {fact_id: {"value": True}},
            "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 15, "forbidden_assertions": ["diagnosis.sepsis", "diagnosis.meningitis", "diagnosis.malaria"]},
            "provenance": provenance(SOURCES),
        }
    policy = completion(f)
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}
    def routine(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"][branch])
        values = {}
        for fact_id in required:
            fact = by_id[fact_id]
            if fact["value_type"] == "boolean":
                value = False
            elif fact["value_type"] == "integer":
                value = 0
            elif fact["value_type"] == "coded":
                value = fact.get("allowed_values", ["other_unclear"])[0]
            elif fact["value_type"] == "quantity":
                value = "1 day" if fact_id == "symptom.duration" else "38.0 °C"
            else:
                value = "없음"
            values[fact_id] = {"value": value}
        values["fever.primary_group"] = {"value": branch}
        values["symptom.dyspnea"] = {"value": "none"}
        return values
    adult = routine("acute_current_fever")
    adult["observation.body_temperature"] = {"value": "39.1 °C"}
    adult["symptom.duration"] = {"value": "2 days"}
    adult["symptom.cough"] = {"value": True}
    out["FEVER-ROUTINE-ADULT-RESPIRATORY.json"] = {"id": "FEVER-ROUTINE-ADULT-RESPIRATORY", "simulation_language": "ko", "persona": {"age": 34}, "initial_statement": {"ko": "이틀째 39.1도 열과 기침이 있어 진료 전 문진을 합니다."}, "hidden_state": adult, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.influenza", "diagnosis.pneumonia"]}, "provenance": provenance(SOURCES)}
    pain = routine("acute_current_fever")
    pain["fever.pain_present"] = {"value": True}
    pain["fever.pain_nrs"] = {"value": 7}
    pain["pain.frequency"] = {"value": "daily"}
    out["FEVER-PAIN-MANDATORY-NRS.json"] = {"id": "FEVER-PAIN-MANDATORY-NRS", "simulation_language": "ko", "persona": {"age": 45}, "initial_statement": {"ko": "열과 통증이 같이 있습니다."}, "hidden_state": pain, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"fever.pain_nrs": 7}, "expected_max_turns": 75}, "provenance": provenance(SOURCES)}
    absent = routine("feverish_not_measured")
    absent.pop("observation.body_temperature")
    out["FEVER-TEMPERATURE-DATA-ABSENT.json"] = {"id": "FEVER-TEMPERATURE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 29}, "initial_statement": {"ko": "열감은 있지만 체온계가 없어서 재지 못했습니다."}, "hidden_state": absent, "response_behavior": {"observation.body_temperature": {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {"observation.body_temperature": "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.fever_confirmed"]}, "provenance": provenance(SOURCES)}
    child = routine("acute_current_fever")
    child["fever.information_source_proxy_and_reliability"] = {"value": "보호자가 체온계 기록을 보며 답변"}
    child["fever.age_life_stage_and_baseline"] = {"value": "8세, 평소 건강"}
    out["FEVER-CHILD-CAREGIVER-REMOTE.json"] = {"id": "FEVER-CHILD-CAREGIVER-REMOTE", "simulation_language": "ko", "persona": {"age": 8}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "video", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "아이 열에 대해 보호자가 영상으로 답합니다."}, "hidden_state": child, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.pediatric_sepsis"]}, "provenance": provenance(SOURCES)}
    travel = routine("post_travel_or_specific_exposure")
    travel["fever.travel_destinations_dates_onset_and_healthcare"] = {"value": "2026-07-10 동남아시아에서 귀국, 귀국 3일 뒤 발열 시작"}
    out["FEVER-POST-TRAVEL-CLINICIAN-HANDOFF.json"] = {"id": "FEVER-POST-TRAVEL-CLINICIAN-HANDOFF", "simulation_language": "ko", "persona": {"age": 38}, "initial_statement": {"ko": "해외여행 후 열이 생겼습니다."}, "hidden_state": travel, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"fever.travel_destinations_dates_onset_and_healthcare": "2026-07-10 동남아시아에서 귀국, 귀국 3일 뒤 발열 시작"}, "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.malaria", "diagnosis.dengue"]}, "provenance": provenance(SOURCES)}
    extra = routine("test_or_treatment_followup")
    extra["fever.patient_concern_goal_and_other_detail"] = {"value": "발열 추적 외에 회사 제출용 진료확인서 문의도 전달 요청"}
    out["FEVER-UNRELATED-ADDITIONAL-COMMENT.json"] = {"id": "FEVER-UNRELATED-ADDITIONAL-COMMENT", "simulation_language": "ko", "persona": {"age": 52}, "initial_statement": {"ko": "열 치료 후 추적과 다른 요청이 있습니다."}, "hidden_state": extra, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"fever.patient_concern_goal_and_other_detail": "발열 추적 외에 회사 제출용 진료확인서 문의도 전달 요청"}, "expected_max_turns": 75}, "provenance": provenance(SOURCES)}
    multi = routine("acute_current_fever")
    multi["fever.patient_concern_goal_and_other_detail"] = {"value": "발열 외에 왼쪽 유방 통증도 별도 문진 요청"}
    out["FEVER-MULTI-RFE-BREAST-PAIN.json"] = {"id": "FEVER-MULTI-RFE-BREAST-PAIN", "simulation_language": "ko", "persona": {"age": 43}, "initial_statement": {"ko": "열이 나고 왼쪽 유방도 아픕니다."}, "hidden_state": multi, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.mastitis"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Fever or Feeling Feverish", intents=[
        ("intent.characterize_symptom", "Characterize Measured or Subjective Fever Course and Severity"),
        ("intent.screen_red_flags", "Screen Sepsis Meningitis Respiratory Neurologic Dehydration and Vulnerable-host Warning Features"),
        ("intent.differentiate_common_causes", "Localize Respiratory Urinary Gastrointestinal Neurological Skin Reproductive and Exposure Context"),
        ("intent.risk_assessment", "Assess Age Pregnancy Immune Travel Procedure Device Medicine Test Treatment Function and Patient Goals"),
    ])
    primary, research = source_docs()
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": [{"code": "386661006", "display": "Fever (finding)", "concept_active": True, "attribute_count_returned": 20}, {"code": "248456009", "display": "Shivering or rigors (finding)", "concept_active": True, "attribute_count_returned": 20}, {"code": "386689009", "display": "Hypothermia (finding)", "concept_active": True, "attribute_count_returned": 20}],
        "verified_attribute_ids": ["363698007", "246112005"],
        "quantitative_observation_binding": {"system": "http://loinc.org", "code": "8310-5", "display": "Body temperature", "runtime_inference": False},
        "validation": {"method": "build_time_live_search_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "fever_semantics": {"infection_inferred": False, "sepsis_score_calculated": False, "news2_or_mews_calculated": False, "temperature_threshold_alone_diagnoses_infection": False, "runtime_terminology_query_required": False},
        "provenance": provenance(["source.stom.fever.20260716"]),
    }
    documents = [
        ("knowledge/base/primary-care-fever.json", graph),
        ("rules/base/primary-care-fever.json", rules),
        ("knowledge/generated/systemic/fever.json", f),
        ("mappings/terminology/snomed-mrcm-fever.json", mapping),
        ("sources/manifests/primary-care-fever.json", primary),
        ("sources/manifests/primary-care-fever-research.json", research),
        ("policies/primary-care-fever-completion.json", completion(f)),
    ]
    for path, document in documents:
        write_json(path, document)
    for name, case in cases(f).items():
        write_json("simulation/patients/systemic/fever/" + name, case)


if __name__ == "__main__":
    main()
