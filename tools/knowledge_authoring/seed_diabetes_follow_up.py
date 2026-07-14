#!/usr/bin/env python3
"""Materialize unreviewed diabetes follow-up knowledge."""
from profile_support import *

P = "diabetes-follow-up"
RFE = "rfe.diabetes_follow_up"
M = "mapping.snomed-mrcm.diabetes-follow-up"
SN = "http://snomed.info/sct"
SOURCES = [
    "source.ada.soc2026.glycemic-goals", "source.ada.soc2026.ckd",
    "source.ada.soc2026.retina-neuropathy-foot", "source.nice.ng28.diabetes-type2.2026",
    "source.nice.ng17.diabetes-type1", "source.nice.ng19.diabetic-foot.2025",
    "source.nhs.dka.2026", "source.nhs.hypoglycaemia.2026",
    "source.stom.diabetes.20260714",
]
G = {k: f"group.diabetes-follow-up.{k}" for k in (
    "routing", "acute-safety", "glycemic-review", "medication-hypoglycemia",
    "kidney-eye-foot", "cardiovascular", "self-management", "type1-insulin",
)}
C, S, R, F = ["intent.characterize_follow_up"], ["intent.screen_red_flags"], ["intent.risk_assessment"], ["intent.follow_up_support"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("diabetes.follow_up.requested", "Diabetes Follow-up Requested", "boolean", "requested", "당뇨병 또는 혈당 관리 추적을 위해 방문한 것이 맞나요?", 130, [G["routing"]], C, terminology_binding={"system": SN, "code": "73211009"}, mrcm_ref=M),
        Q("diabetes.type_or_context", "Diabetes Type or Context", "coded", "type-context", "알고 있는 당뇨병 유형은 1형, 2형, 임신성, 기타·불확실 중 무엇인가요?", 129, [G["routing"]], C, allowed_values=["type1", "type2", "gestational_or_pregnancy", "other", "unclear"]),
        Q("diabetes.primary_follow_up_focus", "Primary Diabetes Follow-up Focus", "coded", "primary-focus", "이번 방문의 주된 목적은 혈당 조절 확인, 약물·저혈당, 합병증 점검, 기기·교육, 기타 중 무엇인가요?", 128, [G["routing"]], C, allowed_values=["glycemic_control", "medication_hypoglycemia", "complication_screening", "device_education", "other_unclear"]),

        Q("diabetes.current_severe_hypoglycemia", "Current Severe Hypoglycemia", "boolean", "current-severe-hypoglycemia", "지금 저혈당이 의심되면서 의식이 흐리거나 경련, 삼키기 어려움, 다른 사람 도움 없이는 회복하기 어려운 상태인가요?", 127, [G["acute-safety"], G["medication-hypoglycemia"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "302866003"}, mrcm_ref=M),
        Q("diabetes.current_glucose_below_54_or_persistent_below_70", "Current Clinically Important Hypoglycemia", "boolean", "current-low-glucose", "현재 혈당이 54 mg/dL 미만이거나, 70 mg/dL 미만이면서 당 섭취 후에도 계속 낮나요?", 126, [G["acute-safety"], G["medication-hypoglycemia"]], S, safety_relevant=True),
        Q("diabetes.dka_symptom_cluster", "Diabetic Ketoacidosis Symptom Cluster", "boolean", "dka-symptoms", "심한 갈증·잦은 소변과 함께 메스꺼움·구토, 복통, 깊거나 빠른 호흡, 과일 냄새 같은 숨, 심한 졸림·혼란이 있나요?", 125, [G["acute-safety"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "111556005"}, mrcm_ref=M),
        Q("diabetes.moderate_large_ketones_or_high_ketone", "Moderate or Large Ketones", "boolean", "high-ketones", "혈액 케톤이 높다고 나오거나 소변 케톤이 중등도·대량으로 나왔나요?", 124, [G["acute-safety"], G["type1-insulin"]], S, safety_relevant=True),
        Q("diabetes.repeated_vomiting_or_cannot_keep_fluids", "Repeated Vomiting or Unable to Keep Fluids", "boolean", "vomiting-dehydration", "반복해서 토하거나 물을 마셔도 유지할 수 없나요?", 123, [G["acute-safety"]], S, safety_relevant=True),
        Q("diabetes.marked_hyperglycemia_with_confusion_or_dehydration", "Marked Hyperglycemia with Confusion or Dehydration", "boolean", "hyperglycemic-crisis", "혈당이 매우 높으면서 심한 탈수, 기운 없음, 졸림·혼란 또는 의식 변화가 있나요?", 122, [G["acute-safety"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "80394007"}, mrcm_ref=M),
        Q("diabetes.suspected_insulin_delivery_interruption", "Suspected Insulin Delivery Interruption", "boolean", "insulin-interruption", "인슐린 주사를 여러 번 거르거나 펌프·주입세트 이상으로 인슐린 공급이 중단됐나요?", 121, [G["acute-safety"], G["type1-insulin"]], S, safety_relevant=True),
        Q("diabetes.sglt2_use_with_dka_symptoms", "SGLT2 Inhibitor Use with DKA Symptoms", "boolean", "sglt2-dka", "SGLT2 억제제 계열 당뇨약을 복용하면서 혈당 수치와 상관없이 케톤산증 의심 증상이 있나요?", 120, [G["acute-safety"], G["medication-hypoglycemia"]], S, safety_relevant=True),
        Q("diabetes.foot_ulcer_with_sepsis_ischaemia_deep_infection_or_gangrene", "Limb-threatening Diabetic Foot Features", "boolean", "limb-threatening-foot", "발 상처·궤양과 함께 고열·패혈증 의심, 발이 창백하거나 검게 변함, 깊은 감염·뼈 노출 또는 괴저가 있나요?", 119, [G["acute-safety"], G["kidney-eye-foot"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "371087003"}, mrcm_ref=M),
        Q("diabetes.active_foot_ulcer_infection_or_unexplained_hot_swollen_foot", "Active Diabetic Foot Problem", "boolean", "active-foot-problem", "새 발 궤양·물집·감염, 이유 없이 붉고 뜨겁고 부은 발 또는 낫지 않는 상처가 있나요?", 118, [G["acute-safety"], G["kidney-eye-foot"]], S, safety_relevant=True),
        Q("diabetes.pregnant_or_planning_pregnancy", "Pregnancy or Pregnancy Planning", "coded", "pregnancy-context", "현재 임신 중이거나 임신을 계획하고 있나요?", 117, [G["acute-safety"], G["self-management"]], R, allowed_values=["pregnant", "planning", "not_applicable", "unclear"]),

        Q("diabetes.latest_hba1c_value", "Latest HbA1c Value", "string", "latest-hba1c", "가장 최근 당화혈색소(HbA1c) 수치와 단위를 알려주세요.", 116, [G["glycemic-review"]], C),
        Q("diabetes.latest_hba1c_date", "Latest HbA1c Date", "string", "hba1c-date", "그 당화혈색소 검사는 언제 했나요?", 115, [G["glycemic-review"]], C),
        Q("diabetes.individualized_glycemic_goal_known", "Individualized Glycemic Goal", "string", "glycemic-goal", "의료진과 합의한 개인별 당화혈색소 또는 혈당 목표가 있나요?", 108, [G["glycemic-review"]], F),
        Q("diabetes.home_glucose_or_cgm_summary", "Home Glucose or CGM Summary", "string", "glucose-summary", "최근 공복·식후 혈당 범위나 연속혈당측정기의 평균·목표범위시간을 알려주세요.", 114, [G["glycemic-review"]], C),
        Q("diabetes.glucose_pattern_high_low_or_variable", "Glucose Pattern", "coded", "glucose-pattern", "최근 혈당 양상은 대체로 높음, 낮음, 변동이 큼, 목표 범위, 자료 없음 중 무엇인가요?", 113, [G["glycemic-review"]], C, allowed_values=["mostly_high", "mostly_low", "high_variability", "mostly_in_target", "no_data", "unclear"]),
        Q("diabetes.hyperglycemia_symptoms", "Hyperglycemia Symptoms", "boolean", "hyperglycemia-symptoms", "최근 갈증, 소변 증가, 흐린 시야, 피로 또는 설명되지 않는 체중 감소가 있나요?", 112, [G["glycemic-review"]], R),
        Q("diabetes.recent_illness_steroid_or_major_routine_change", "Factors Affecting Recent Glucose", "string", "recent-glucose-context", "최근 감염·질병, 스테로이드 사용, 식사·활동·체중 변화처럼 혈당에 영향을 줄 일이 있었나요?", 107, [G["glycemic-review"], G["self-management"]], R),
        Q("diabetes.monitoring_method_and_frequency", "Glucose Monitoring Method and Frequency", "string", "monitoring-method", "자가혈당계·연속혈당측정기 사용 여부와 실제 측정 빈도를 알려주세요.", 106, [G["glycemic-review"], G["type1-insulin"]], F),
        Q("diabetes.monitoring_supply_or_device_problem", "Monitoring Supply or Device Problem", "string", "device-problem", "시험지·센서 비용이나 공급, 기기 정확도·알람·피부 문제 등 사용 장벽이 있나요?", 92, [G["glycemic-review"], G["type1-insulin"]], F),

        Q("medication.diabetes_current_list", "Current Diabetes Medicines", "string", "medicine-list", "현재 당뇨약·인슐린 이름, 용량, 하루 횟수와 실제 사용 방법을 알려주세요.", 111, [G["medication-hypoglycemia"]], F),
        Q("medication.missed_dose_frequency", "Missed Dose Frequency", "coded", "missed-doses", "최근 한 달 동안 당뇨약이나 인슐린을 빼먹은 정도는 없음, 드물게, 주 1회 이상, 거의 매일 중 무엇인가요?", 110, [G["medication-hypoglycemia"]], F, allowed_values=["none", "rare", "weekly_or_more", "almost_daily"], reuse_existing=True),
        Q("medication.recent_start_stop_dose_change", "Recent Diabetes Medicine Change", "string", "recent-change", "최근 당뇨약·인슐린을 시작·중단·증량·감량한 내용과 시점이 있나요?", 105, [G["medication-hypoglycemia"]], F, reuse_existing=True),
        Q("medication.suspected_adverse_effects", "Suspected Diabetes Medicine Adverse Effects", "string", "adverse-effects", "메스꺼움·설사, 탈수, 생식기 감염, 부종, 체중 변화 등 약과 관련 있다고 생각하는 불편이 있나요?", 104, [G["medication-hypoglycemia"]], F, reuse_existing=True),
        Q("diabetes.hypoglycemia_frequency_and_timing", "Hypoglycemia Frequency and Timing", "string", "hypoglycemia-frequency", "최근 저혈당 또는 70 mg/dL 미만이 얼마나 자주, 주로 언제 발생했나요?", 109, [G["medication-hypoglycemia"]], R),
        Q("diabetes.severe_hypoglycemia_needing_assistance_history", "Severe Hypoglycemia Requiring Assistance", "boolean", "severe-hypoglycemia-history", "최근 다른 사람의 도움, 글루카곤, 응급진료가 필요했던 심한 저혈당이 있었나요?", 108, [G["medication-hypoglycemia"]], R),
        Q("diabetes.impaired_hypoglycemia_awareness", "Impaired Hypoglycemia Awareness", "boolean", "hypoglycemia-awareness", "혈당이 많이 낮아질 때까지 떨림·식은땀·허기 같은 경고 증상을 잘 느끼지 못하나요?", 107, [G["medication-hypoglycemia"]], R),
        Q("diabetes.hypoglycemia_treatment_and_glucagon_access", "Hypoglycemia Treatment and Glucagon Access", "string", "hypoglycemia-preparedness", "빠른 당 섭취 방법을 알고 준비해 두었는지, 필요하면 글루카곤과 사용 가능한 보호자가 있는지 알려주세요.", 96, [G["medication-hypoglycemia"], G["self-management"]], F),
        Q("diabetes.insulin_regimen_delivery_site_and_technique", "Insulin Regimen Delivery Site and Technique", "string", "insulin-technique", "인슐린 사용 중이면 주사·펌프 방식, 주입 부위 교대와 피부 멍울·누출 문제가 있나요?", 103, [G["type1-insulin"], G["medication-hypoglycemia"]], F),
        Q("diabetes.sick_day_and_ketone_plan_known", "Sick-day and Ketone Plan", "coded", "sick-day-plan", "아플 때 약·인슐린, 수분, 혈당·케톤 확인과 연락 기준을 적은 계획을 알고 있나요?", 102, [G["type1-insulin"], G["self-management"]], F, allowed_values=["known_and_available", "partly_known", "not_known", "not_applicable", "unclear"]),

        Q("diabetes.latest_egfr_creatinine_and_date", "Latest Kidney Function", "string", "kidney-function", "최근 크레아티닌·eGFR 결과와 검사 날짜를 알려주세요.", 101, [G["kidney-eye-foot"]], R),
        Q("diabetes.latest_uacr_albuminuria_and_date", "Latest Urine Albumin Assessment", "string", "albuminuria", "최근 소변 알부민/크레아티닌비(UACR) 또는 단백뇨 결과와 검사 날짜를 알려주세요.", 100, [G["kidney-eye-foot"]], R),
        Q("diabetes.rapid_kidney_decline_or_increasing_albuminuria_known", "Rapid Kidney Decline or Rising Albuminuria", "boolean", "kidney-progression", "신장기능이 빠르게 떨어지거나 소변 단백이 계속 증가한다는 말을 들었나요?", 99, [G["kidney-eye-foot"]], R),
        Q("diabetes.retinal_screening_date_and_result", "Retinal Screening Date and Result", "string", "retinal-screening", "최근 당뇨망막검사·안저검사 날짜와 결과, 다음 일정이 있나요?", 100, [G["kidney-eye-foot"]], R),
        Q("diabetes.new_vision_change", "New Vision Change", "boolean", "vision-change", "최근 갑작스럽거나 새로 생긴 시력 저하·시야 변화가 있나요?", 105, [G["kidney-eye-foot"]], R),
        Q("diabetes.foot_numbness_burning_pain_or_sensation_loss", "Foot Neuropathy Symptoms", "boolean", "foot-neuropathy", "발의 저림·화끈거림·통증, 감각 둔화 또는 상처를 잘 못 느끼는 증상이 있나요?", 99, [G["kidney-eye-foot"]], R),
        Q("diabetes.foot_exam_date_and_risk_result", "Foot Examination and Risk Result", "string", "foot-exam", "최근 발 피부·변형·감각·맥박 검사를 언제 받았고 위험도 결과는 어땠나요?", 98, [G["kidney-eye-foot"]], R),
        Q("diabetes.prior_foot_ulcer_amputation_or_charcot", "Prior Foot Ulcer Amputation or Charcot Foot", "boolean", "foot-history", "과거 발 궤양, 절단, 샤르코 발 또는 발 혈관 시술 병력이 있나요?", 97, [G["kidney-eye-foot"]], R),
        Q("diabetes.daily_foot_check_and_footwear", "Daily Foot Check and Footwear", "string", "foot-self-care", "매일 발을 확인하는지, 맞지 않는 신발·맨발 보행·굳은살 자가 제거 같은 위험이 있는지 알려주세요.", 91, [G["kidney-eye-foot"], G["self-management"]], F),
        Q("diabetes.dental_periodontal_or_recurrent_infection", "Dental or Recurrent Infection Concern", "string", "infection-screen", "잇몸 출혈·치주질환, 반복되는 피부·요로·생식기 감염 같은 문제가 있나요?", 87, [G["kidney-eye-foot"]], R),

        Q("diabetes.blood_pressure_recent", "Recent Blood Pressure", "string", "blood-pressure", "최근 혈압 또는 가정혈압 범위를 알려주세요.", 95, [G["cardiovascular"]], R),
        Q("diabetes.lipid_result_and_statin_use", "Lipid Result and Statin Use", "string", "lipid-statin", "최근 콜레스테롤 검사 결과와 스타틴 등 지질약 복용 여부를 알려주세요.", 94, [G["cardiovascular"]], R),
        Q("history.cardiovascular_or_cerebrovascular_disease", "Cardiovascular or Cerebrovascular Disease", "boolean", "cvd-history", "심근경색·협심증·심부전·뇌졸중 또는 말초혈관질환 병력이 있나요?", 93, [G["cardiovascular"]], R, reuse_existing=True),
        Q("lifestyle.tobacco_current", "Current Tobacco Use", "coded", "tobacco", "현재 담배나 전자담배를 사용하나요?", 92, [G["cardiovascular"], G["self-management"]], R, allowed_values=["never", "former", "current", "unknown"], reuse_existing=True),
        Q("diabetes.weight_bmi_and_recent_change", "Weight BMI and Recent Change", "string", "weight-bmi", "현재 키·체중 또는 BMI와 최근 체중 변화를 알려주세요.", 90, [G["cardiovascular"], G["self-management"]], R),
        Q("diabetes.food_pattern_and_carbohydrate_management", "Food Pattern and Carbohydrate Management", "string", "food-pattern", "평소 식사 시간·양, 탄수화물·단 음료 섭취와 조절하기 어려운 점이 있나요?", 89, [G["self-management"]], F),
        Q("lifestyle.physical_activity", "Physical Activity", "string", "activity", "최근 일주일의 걷기·유산소·근력운동 횟수와 시간을 알려주세요.", 88, [G["self-management"]], F, reuse_existing=True),
        Q("diabetes.alcohol_and_hypoglycemia_context", "Alcohol and Hypoglycemia Context", "string", "alcohol", "술은 일주일에 며칠, 한 번에 얼마나 마시며 음주 후 저혈당 경험이 있나요?", 86, [G["self-management"]], R),
        Q("diabetes.education_health_literacy_or_cost_barrier", "Education or Access Barrier", "string", "access-barrier", "약·검사·기기 비용, 교육 이해, 식품·주거·돌봄·진료 접근 문제로 관리가 어려운 점이 있나요?", 85, [G["self-management"]], F),
        Q("diabetes.vaccination_and_preventive_care_review", "Vaccination and Preventive Care Review", "string", "preventive-review", "예방접종과 연령·성별에 맞는 일반 건강검진을 최근에 확인했나요?", 84, [G["self-management"]], F),
        Q("diabetes.patient_goal_or_question", "Patient Goal or Question", "string", "patient-goal", "이번 추적관리에서 가장 확인하거나 개선하고 싶은 점은 무엇인가요?", 83, [G["routing"], G["self-management"]], F),
    ]
    dka = {"fact": "diabetes.dka_symptom_cluster", "equals": True}
    rules = [
        safety_rule(P, "current-severe-hypoglycemia", {"fact": "diabetes.current_severe_hypoglycemia", "equals": True}, "emergency", 1000),
        safety_rule(P, "persistent-current-hypoglycemia", {"fact": "diabetes.current_glucose_below_54_or_persistent_below_70", "equals": True}, "urgent", 960),
        safety_rule(P, "dka-symptoms-ketones", {"all": [dka, {"fact": "diabetes.moderate_large_ketones_or_high_ketone", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "dka-symptoms-vomiting", {"all": [dka, {"fact": "diabetes.repeated_vomiting_or_cannot_keep_fluids", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "hyperglycemic-crisis", {"fact": "diabetes.marked_hyperglycemia_with_confusion_or_dehydration", "equals": True}, "emergency", 1000),
        safety_rule(P, "insulin-interruption-dka", {"all": [{"fact": "diabetes.suspected_insulin_delivery_interruption", "equals": True}, dka]}, "emergency", 1000),
        safety_rule(P, "sglt2-dka", {"fact": "diabetes.sglt2_use_with_dka_symptoms", "equals": True}, "emergency", 1000),
        safety_rule(P, "limb-threatening-foot", {"fact": "diabetes.foot_ulcer_with_sepsis_ischaemia_deep_infection_or_gangrene", "equals": True}, "emergency", 1000),
        safety_rule(P, "active-foot-problem", {"fact": "diabetes.active_foot_ulcer_infection_or_unexplained_hot_swollen_foot", "equals": True}, "urgent", 940),
        safety_rule(P, "recent-severe-hypoglycemia", {"fact": "diabetes.severe_hypoglycemia_needing_assistance_history", "equals": True}, "urgent", 900),
        safety_rule(P, "new-vision-change", {"fact": "diabetes.new_vision_change", "equals": True}, "urgent", 900),
    ]
    return {"id": "knowledge.generated.diabetes-follow-up", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-diabetes-follow-up-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="diabetes.follow_up.requested", question_budget=38, source_refs=SOURCES)
    p["required_facts"]["routine"] = [
        "diabetes.type_or_context", "diabetes.primary_follow_up_focus",
        "diabetes.latest_hba1c_value", "diabetes.latest_hba1c_date",
        "diabetes.home_glucose_or_cgm_summary", "diabetes.glucose_pattern_high_low_or_variable",
        "medication.diabetes_current_list", "medication.missed_dose_frequency",
        "diabetes.hypoglycemia_frequency_and_timing",
        "diabetes.latest_egfr_creatinine_and_date", "diabetes.latest_uacr_albuminuria_and_date",
        "diabetes.retinal_screening_date_and_result", "diabetes.foot_numbness_burning_pain_or_sensation_loss",
        "diabetes.foot_exam_date_and_risk_result", "history.cardiovascular_or_cerebrovascular_disease",
        "diabetes.blood_pressure_recent", "diabetes.patient_goal_or_question",
    ]
    type1 = ["diabetes.insulin_regimen_delivery_site_and_technique", "diabetes.sick_day_and_ketone_plan_known"]
    focus = {
        "glycemic_control": ["diabetes.individualized_glycemic_goal_known", "diabetes.hyperglycemia_symptoms", "diabetes.recent_illness_steroid_or_major_routine_change", "diabetes.monitoring_method_and_frequency", "diabetes.monitoring_supply_or_device_problem"],
        "medication_hypoglycemia": ["medication.recent_start_stop_dose_change", "medication.suspected_adverse_effects", "diabetes.impaired_hypoglycemia_awareness", "diabetes.hypoglycemia_treatment_and_glucagon_access", "diabetes.insulin_regimen_delivery_site_and_technique"],
        "complication_screening": ["diabetes.rapid_kidney_decline_or_increasing_albuminuria_known", "diabetes.prior_foot_ulcer_amputation_or_charcot", "diabetes.daily_foot_check_and_footwear", "diabetes.dental_periodontal_or_recurrent_infection", "diabetes.lipid_result_and_statin_use"],
        "device_education": ["diabetes.monitoring_method_and_frequency", "diabetes.monitoring_supply_or_device_problem", "diabetes.sick_day_and_ketone_plan_known", "diabetes.education_health_literacy_or_cost_barrier"],
        "other_unclear": [],
    }
    p["conditional_required_facts"] = [
        {"selector_fact": "diabetes.type_or_context", "cases": {"type1": type1, "type2": [], "gestational_or_pregnancy": [], "other": [], "unclear": []}},
        {"selector_fact": "diabetes.primary_follow_up_focus", "cases": focus},
    ]
    return p


def source_docs():
    defs = [
        ("source.ada.soc2026.glycemic-goals", "American Diabetes Association", "Glycemic Goals, Hypoglycemia, and Hyperglycemic Crises: Standards of Care in Diabetes—2026", "2026", "https://diabetesjournals.org/care/article/49/Supplement_1/S132/163927/", "clinical_guideline", 1),
        ("source.ada.soc2026.ckd", "American Diabetes Association", "Chronic Kidney Disease and Risk Management: Standards of Care in Diabetes—2026", "2026", "https://diabetesjournals.org/care/article/49/Supplement_1/S246/163914/", "clinical_guideline", 1),
        ("source.ada.soc2026.retina-neuropathy-foot", "American Diabetes Association", "Retinopathy, Neuropathy, and Foot Care: Standards of Care in Diabetes—2026", "2026", "https://diabetesjournals.org/care/article/49/Supplement_1/S261/163919/", "clinical_guideline", 1),
        ("source.nice.ng28.diabetes-type2.2026", "NICE", "Type 2 diabetes in adults: management", "NG28-updated-2026-02-18", "https://www.nice.org.uk/guidance/ng28", "clinical_guideline", 1),
        ("source.nice.ng17.diabetes-type1", "NICE", "Type 1 diabetes in adults: diagnosis and management", "NG17", "https://www.nice.org.uk/guidance/ng17/chapter/recommendations", "clinical_guideline", 1),
        ("source.nice.ng19.diabetic-foot.2025", "NICE", "Diabetic foot problems: prevention and management", "NG19-reviewed-2025-07-03", "https://www.nice.org.uk/guidance/ng19/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nhs.dka.2026", "NHS", "Diabetic ketoacidosis", "accessed-2026-07-14", "https://www.nhs.uk/conditions/diabetic-ketoacidosis/", "public_health_guidance", 7),
        ("source.nhs.hypoglycaemia.2026", "NHS", "Low blood sugar (hypoglycaemia)", "accessed-2026-07-14", "https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/", "public_health_guidance", 7),
        ("source.stom.diabetes.20260714", "Infoclinic", "STOM diabetes terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", 30),
    ]
    arts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": ver, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "American Diabetes Association", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"), "assertions": ["Build-Time only; Runtime does not browse; content remains unreviewed."]} for i, pub, title, ver, url, profile, days in defs]
    research = {"id": "source-manifest.primary-care-diabetes-follow-up-research", "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only", "artifacts": arts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.diabetes-follow-up", "generated_clinical_knowledge", "knowledge/generated/endocrine/diabetes-follow-up/diabetes-follow-up.json", True), ("source.mapping.diabetes-follow-up", "terminology_mapping", "mappings/terminology/snomed-mrcm-diabetes-follow-up.json", False), ("source.external.diabetes-follow-up", "external_source_manifest", "sources/manifests/primary-care-diabetes-follow-up-research.json", False), ("source.policy.diabetes-follow-up", "runtime_policy", "policies/primary-care-diabetes-follow-up-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-diabetes-follow-up", "version": VERSION, "acquired_at": CREATED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    def satisfy(c, h):
        if "all" in c:
            for x in c["all"]: satisfy(x, h)
        elif "equals" in c: h[c["fact"]] = {"value": c["equals"]}
        elif "in" in c: h[c["fact"]] = {"value": c["in"][0]}
    for i, rule in enumerate(f["safety_rules"]):
        hidden = {}; satisfy(rule["when"], hidden); key = rule["id"].split("safety.")[1]; level = rule["then"]["safety_level"]
        out[f"DM-{key.upper()}.json"] = {"id": f"DM-{key.upper()}", "simulation_language": "ko", "persona": {"age": 31 + i}, "initial_statement": {"ko": "당뇨병 정기 진료를 받으러 왔어요."}, "hidden_state": hidden, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 35, "forbidden_assertions": ["diagnosis.diabetic_ketoacidosis", "diagnosis.hyperosmolar_state", "recommendation.change_insulin_dose"]}, "provenance": provenance(SOURCES)}
    policy = completion(f); required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["type2"])
    by_id = {x["fact"]["id"]: x["fact"] for x in f["entries"]}; hidden = {}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": fid == "diabetes.follow_up.requested"}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        else: hidden[fid] = {"value": "없음"}
    hidden["diabetes.type_or_context"] = {"value": "type2"}; hidden["diabetes.primary_follow_up_focus"] = {"value": "glycemic_control"}
    declined = "medication.diabetes_current_list"; hidden.pop(declined)
    out["DM-TYPE2-DATA-ABSENT.json"] = {"id": "DM-TYPE2-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 57}, "initial_statement": {"ko": "2형 당뇨 정기 검진을 받으러 왔어요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-declined"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.controlled_diabetes", "recommendation.change_medication"]}, "provenance": provenance(["source.nice.ng28.diabetes-type2.2026", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment(); graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Diabetes Follow-up", intents=[("intent.characterize_follow_up", "Characterize Follow-up"), ("intent.screen_red_flags", "Screen Red Flags"), ("intent.risk_assessment", "Risk Assessment"), ("intent.follow_up_support", "Follow-up Support")]); primary, research = source_docs()
    concepts = [("73211009", "Diabetes mellitus (disorder)"), ("46635009", "Diabetes mellitus type 1 (disorder)"), ("44054006", "Diabetes mellitus type 2 (disorder)"), ("302866003", "Hypoglycemia (disorder)"), ("80394007", "Hyperglycemia (disorder)"), ("111556005", "Ketoacidosis without coma due to diabetes mellitus (disorder)"), ("371087003", "Ulcer of foot due to diabetes mellitus (disorder)")]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": 22} for c, d in concepts], "checks": [{"focus_code": c, "query": "mapping_support_and_mrcm", "allowed": True} for c, _ in concepts], "validation": {"method": "build_time_live_mapping_and_mrcm_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.diabetes.20260714"])}
    docs = [("knowledge/base/primary-care-diabetes-follow-up.json", graph), ("rules/base/primary-care-diabetes-follow-up.json", rules), ("knowledge/generated/endocrine/diabetes-follow-up/diabetes-follow-up.json", f), ("mappings/terminology/snomed-mrcm-diabetes-follow-up.json", mapping), ("sources/manifests/primary-care-diabetes-follow-up.json", primary), ("sources/manifests/primary-care-diabetes-follow-up-research.json", research), ("policies/primary-care-diabetes-follow-up-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/endocrine/diabetes-follow-up/" + name, case)


if __name__ == "__main__": main()
