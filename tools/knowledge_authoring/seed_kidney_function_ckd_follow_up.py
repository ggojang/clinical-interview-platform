#!/usr/bin/env python3
"""Materialize unreviewed kidney-function and CKD follow-up interview knowledge."""
from profile_support import *

P, RFE, M, SN = "kidney-function-ckd-follow-up", "rfe.kidney_function_ckd_follow_up", "mapping.snomed-mrcm.kidney-function-ckd-follow-up", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-31T00:00:00Z"
SOURCES = ["source.nice.ng203.ckd.2025", "source.nice.ng148.aki.2024", "source.kdigo.ckd.2024", "source.stom.kidney.20260715"]
G = {k: f"group.kidney.{k}" for k in ("routing", "safety", "common", "results", "cause", "dialysis", "transplant")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    fact_overrides = kwargs.pop("fact_overrides", None)
    result = entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)
    if fact_overrides:
        result["fact"].update(fact_overrides)
    return result


def fragment():
    e = [
        Q("kidney.primary_group", "Primary Kidney Presentation", "coded", "primary-group", "이번 방문은 신장기능 검사 이상, 만성콩팥병 추적, 갑작스러운 신장기능 변화, 단백뇨·혈뇨, 투석 관리, 신장이식 후 관리, 구조적 신장·요로질환 중 무엇에 가깝나요?", 180, [G["routing"]], C, allowed_values=["abnormal_kidney_result", "known_ckd_followup", "acute_kidney_change", "proteinuria_or_hematuria", "dialysis_followup", "kidney_transplant_followup", "structural_or_hereditary", "other_unclear"]),
        Q("kidney.anuria_or_severe_oliguria", "Anuria or Severe Oliguria", "boolean", "anuria", "소변이 거의 또는 전혀 나오지 않으면서 몸이 붓거나 심하게 처지고 아픈가요?", 179, [G["safety"]], S, safety_relevant=True),
        Q("kidney.pulmonary_edema_pattern", "Possible Pulmonary Oedema", "boolean", "pulmonary-edema", "갑자기 심하게 숨차고 누우면 더 힘들거나 거품 섞인 가래·빠르게 심해지는 전신 부종이 있나요?", 178, [G["safety"]], S, safety_relevant=True),
        Q("kidney.hyperkalemia_instability_pattern", "Possible Hyperkalaemic Instability", "boolean", "hyperkalemia", "칼륨이 높다고 들었거나 신장질환이 있으면서 갑작스러운 심한 근력저하·두근거림·실신이 있나요?", 177, [G["safety"]], S, safety_relevant=True),
        Q("kidney.uremic_neurologic_pattern", "Possible Uraemic Neurologic Emergency", "boolean", "uremic-neurologic", "새로운 혼란·의식저하·경련 또는 깨우기 어려운 심한 졸림이 있나요?", 176, [G["safety"]], S, safety_relevant=True),
        Q("kidney.hypertensive_emergency_pattern", "Possible Hypertensive Emergency", "boolean", "hypertensive-emergency", "혈압이 매우 높으면서 흉통·심한 호흡곤란·시력 변화·새 신경증상·의식 혼란이 있나요?", 175, [G["safety"]], S, safety_relevant=True),
        Q("kidney.severe_dehydration_with_reduced_urine", "Severe Dehydration with Reduced Urine", "boolean", "dehydration", "계속되는 구토·설사·고열 뒤 물을 못 마시고 소변이 크게 줄며 어지럽거나 실신할 것 같은가요?", 174, [G["safety"]], S, safety_relevant=True),
        Q("kidney.dialysis_access_uncontrolled_bleeding", "Dialysis Access Bleeding", "boolean", "access-bleeding", "투석 혈관이나 카테터에서 압박해도 피가 계속 많이 나나요?", 173, [G["safety"], G["dialysis"]], S, safety_relevant=True),
        Q("kidney.dialysis_access_infection_or_failure", "Dialysis Access Infection or Failure", "boolean", "access-infection", "투석 혈관·카테터 부위가 붉고 뜨겁고 아프면서 발열·오한이 있거나, 평소 만져지던 진동이 갑자기 사라졌나요?", 172, [G["safety"], G["dialysis"]], S, safety_relevant=True),
        Q("kidney.peritoneal_dialysis_peritonitis_pattern", "Peritoneal Dialysis Peritonitis Pattern", "boolean", "pd-peritonitis", "복막투석 중 배액이 흐리거나 복통·발열·오한이 있나요?", 171, [G["safety"], G["dialysis"]], S, safety_relevant=True),
        Q("kidney.transplant_graft_warning", "Kidney Transplant Warning", "boolean", "transplant-warning", "신장이식 후 발열·오한, 이식 신장 부위 통증, 소변 감소 또는 갑작스러운 부종·체중증가가 있나요?", 170, [G["safety"], G["transplant"]], S, safety_relevant=True),
        Q("kidney.flank_pain_fever_and_systemic_illness", "Upper Urinary Infection Warning", "boolean", "flank-fever", "옆구리 통증과 고열·오한·구토가 함께 있고 심하게 처지거나 혼란스러운가요?", 169, [G["safety"]], S, safety_relevant=True),
        Q("kidney.known_severe_aki_or_urgent_lab_callback", "Urgent Kidney Laboratory Alert", "boolean", "urgent-lab", "의료기관에서 크레아티닌·칼륨·산증 등 결과 때문에 즉시 평가받으라고 연락받았나요?", 168, [G["safety"], G["results"]], S, safety_relevant=True),

        Q("kidney.onset_duration_and_course", "Onset Duration and Course", "string", "onset", "증상 또는 검사 이상을 처음 안 시기, 지속 기간과 악화·호전 경과를 알려주세요.", 155, [G["common"]], C),
        Q("kidney.current_symptom_priority", "Current Symptom Priority", "string", "priority", "현재 가장 불편하거나 의료진에게 우선 확인받고 싶은 점은 무엇인가요?", 154, [G["common"]], C),
        Q("kidney.ckd_cause_stage_and_diagnosis_date", "CKD Cause Stage and Diagnosis", "string", "diagnosis", "알고 있는 신장질환 원인, CKD G·A 단계와 진단 시기를 알려주세요.", 153, [G["common"], G["cause"]], R, terminology_binding={"system": SN, "code": "709044004"}, mrcm_ref=M),
        Q("kidney.latest_serum_creatinine_result", "Latest Serum Creatinine Result", "string", "latest-creatinine", "가장 최근 혈청 또는 혈장 크레아티닌 결과값과 단위를 알려주세요. 보기에 없으면 직접 입력해 주세요.", 152, [G["common"], G["results"]], R),
        Q("kidney.latest_egfr_result", "Latest eGFR Result", "string", "latest-egfr", "가장 최근 eGFR 결과값과 단위를 알려주세요. 계산식을 모르면 결과값만 입력해도 됩니다.", 151, [G["common"], G["results"]], R),
        Q("kidney.latest_kidney_result_date", "Latest Kidney Result Date", "date_or_period", "latest-result-date", "가장 최근 신장기능 검사를 시행한 날짜를 알려주세요. 정확한 날짜를 모르면 대략적인 시점을 입력해도 됩니다.", 150, [G["common"], G["results"]], R),
        Q("kidney.egfr_creatinine_trend_and_baseline", "Kidney Function Trend", "string", "trend", "이전 크레아티닌·eGFR과 비교한 변화, 평소 기준값과 변화 속도를 알려주세요.", 151, [G["common"], G["results"]], R),
        Q("kidney.latest_urine_acr_result", "Latest Urine Albumin Creatinine Ratio", "string", "latest-urine-acr", "가장 최근 소변 알부민-크레아티닌비(ACR) 결과값과 단위를 알려주세요. 보기에 없으면 직접 입력해 주세요.", 149, [G["common"], G["results"]], R),
        Q("kidney.latest_urine_pcr_result", "Latest Urine Protein Creatinine Ratio", "string", "latest-urine-pcr", "소변 단백-크레아티닌비(PCR)를 검사했다면 가장 최근 결과값과 단위를 알려주세요. 보기에 없으면 직접 입력해 주세요.", 148, [G["common"], G["results"]], R),
        Q("kidney.urine_protein_specimen_context", "Urine Protein Specimen Context", "coded_or_string", "urine-protein-specimen", "소변 단백 검체는 어떤 방식으로 채취했나요? 1 첫 아침 소변, 2 수시뇨, 3 시간 지정 채뇨, 4 24시간 소변, 5 기타. 보기에 없으면 직접 입력해 주세요.", 147, [G["common"], G["results"]], R, allowed_values=["first_morning", "random_spot", "timed", "twenty_four_hour", "other"]),
        Q("kidney.urinalysis_blood_protein_and_sediment", "Urinalysis Detail", "string", "urinalysis", "소변검사의 단백·잠혈·적혈구·백혈구·원주 결과를 알려주세요.", 149, [G["common"], G["results"]], R),
        Q("kidney.electrolytes_bicarbonate_urea_and_albumin", "Electrolytes and Metabolic Results", "string", "metabolic", "칼륨·나트륨·중탄산염·요소질소·칼슘·인·알부민 결과와 날짜를 알려주세요.", 148, [G["common"], G["results"]], R),
        Q("kidney.cbc_iron_pth_and_vitamin_d", "CKD Complication Tests", "string", "complication-tests", "혈색소·철분, PTH·비타민D 등 빈혈·뼈대사 관련 결과를 알려주세요.", 147, [G["common"], G["results"]], R),
        Q("kidney.urine_volume_frequency_and_nocturia", "Urine Volume and Pattern", "string", "urine-pattern", "하루 소변량, 횟수·야간뇨와 최근 증가·감소를 알려주세요.", 146, [G["common"]], C),
        Q("kidney.edema_weight_and_fluid_change", "Oedema Weight and Fluid Change", "string", "fluid", "발·다리·얼굴 부종, 최근 체중 변화와 하루 수분 섭취량을 알려주세요.", 145, [G["common"]], C),
        Q("kidney.dyspnea_severity", "Dyspnea Severity", "coded", "dyspnea-severity", "현재 숨참은 없음, 가벼움, 중간, 심함 중 어디에 가깝나요?", 144, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("kidney.fatigue_lethargy_severity", "Fatigue or Lethargy Severity", "coded", "fatigue-severity", "현재 피로하거나 기운이 없는 정도는 없음, 가벼움, 중간, 심함 중 어디에 가깝나요?", 144, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("kidney.nausea_severity", "Nausea Severity", "coded", "nausea-severity", "현재 메스꺼움은 없음, 가벼움, 중간, 심함 중 어디에 가깝나요?", 144, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("kidney.reduced_appetite_severity", "Reduced Appetite Severity", "coded", "appetite-severity", "현재 식욕 저하는 없음, 가벼움, 중간, 심함 중 어디에 가깝나요?", 144, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("kidney.pruritus_severity", "Pruritus Severity", "coded", "pruritus-severity", "현재 가려움은 없음, 가벼움, 중간, 심함 중 어디에 가깝나요?", 144, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("kidney.muscle_cramps_severity", "Muscle Cramps Severity", "coded", "cramps-severity", "현재 근육 경련이나 쥐는 없음, 가벼움, 중간, 심함 중 어디에 가깝나요?", 144, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("kidney.sleep_disturbance_severity", "Sleep Disturbance Severity", "coded", "sleep-severity", "현재 수면 방해는 없음, 가벼움, 중간, 심함 중 어디에 가깝나요?", 144, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("pain.nrs_score", "Pain NRS 0 to 10", "integer", "pain-nrs", "현재 통증을 0에서 10 사이 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 144, [G["common"]], C, fact_overrides={"minimum": 0, "maximum": 10, "scale": {"type": "NRS", "minimum": 0, "maximum": 10, "lower_anchor": "no_pain", "upper_anchor": "worst_imaginable_pain"}, "must_preserve_raw_score": True, "required_when_pain_applies": True}, reuse_existing=True),
        Q("kidney.daily_activity_impact", "Daily Activity Impact", "coded", "activity-impact", "신장질환이나 관련 증상이 일상 활동에 미치는 영향은 없음, 가벼움, 중간, 심함 중 어디에 가깝나요?", 144, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("kidney.home_and_clinic_blood_pressure", "Blood Pressure", "string", "blood-pressure", "가정·진료실 혈압과 맥박, 측정 날짜·자세와 최근 추세를 알려주세요.", 143, [G["common"]], R),
        Q("kidney.current_medicines_doses_and_adherence", "Current Medicines and Adherence", "string", "medicines", "현재 처방약의 이름·용량·복용법, 최근 변경과 빠뜨린 복용을 알려주세요.", 142, [G["common"]], R),
        Q("kidney.acei_arb_sglt2_diuretic_and_mra", "Kidney-protective and Volume Medicines", "string", "renal-medicines", "ACE억제제·ARB·SGLT2억제제·이뇨제·미네랄코르티코이드길항제 사용과 시작·증량일을 알려주세요.", 141, [G["common"]], R),
        Q("kidney.nsaid_otc_herbal_and_contrast_exposure", "Nephrotoxin Exposure", "string", "nephrotoxins", "진통소염제, 감기약·제산제, 한약·보충제와 최근 조영제 검사를 알려주세요.", 140, [G["common"], G["cause"]], R),
        Q("kidney.recent_illness_intake_and_medication_holds", "Intercurrent Illness and Medicine Holds", "string", "illness", "최근 구토·설사·발열·식사·수분 감소와 그동안 중단하거나 계속 먹은 약을 알려주세요.", 139, [G["common"], G["cause"]], R),
        Q("kidney.diabetes_hypertension_cardiovascular_and_gout", "Major CKD Comorbidities", "string", "comorbidity", "당뇨·고혈압·심장혈관질환·통풍과 최근 조절 상태를 알려주세요.", 138, [G["common"], G["cause"]], R),
        Q("kidney.family_history_and_hereditary_disease", "Family and Hereditary Kidney History", "string", "family", "가족의 신부전·투석·이식·다낭신 등 유전성 신장질환 병력을 알려주세요.", 137, [G["common"], G["cause"]], R),
        Q("kidney.pregnancy_status_and_plans", "Pregnancy Status and Plans", "string", "pregnancy", "임신 중·수유 중·임신 계획 여부와 관련 약물 상담 내용을 알려주세요.", 136, [G["common"]], R),
        Q("kidney.diet_salt_protein_potassium_and_phosphate", "Kidney Diet", "string", "diet", "소금·단백질·칼륨·인 섭취와 의료진이 정한 식이·수분 제한을 알려주세요.", 135, [G["common"]], R),
        Q("kidney.smoking_alcohol_activity_and_weight", "Lifestyle and Weight", "string", "lifestyle", "흡연·음주·운동, 키·체중과 최근 체중변화를 알려주세요.", 134, [G["common"]], R),
        Q("kidney.other_detail_or_patient_priority", "Other Kidney Detail", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달하고 싶은 내용이나 걱정을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("kidney.prior_aki_dates_causes_and_recovery", "Prior Acute Kidney Injury", "string", "prior-aki", "과거 급성신손상의 날짜·원인·단계, 투석 여부와 회복 후 기준 신장기능을 알려주세요.", 130, [G["cause"]], R, terminology_binding={"system": SN, "code": "14669001"}, mrcm_ref=M),
        Q("kidney.stones_obstruction_prostate_and_infections", "Structural and Obstructive History", "string", "structural", "신장결석·요로폐쇄·전립선비대·반복 요로감염 병력을 알려주세요.", 129, [G["cause"]], R),
        Q("kidney.autoimmune_systemic_and_glomerular_disease", "Systemic and Glomerular Disease", "string", "systemic", "루푸스·혈관염·사구체질환·다발골수종 등 신장에 영향을 줄 수 있는 병력이 있나요?", 128, [G["cause"]], R),
        Q("kidney.ultrasound_biopsy_and_kidney_imaging", "Kidney Imaging and Biopsy", "string", "imaging", "신장 초음파·CT·조직검사 결과, 신장 크기·낭종·폐쇄 여부를 알려주세요.", 127, [G["cause"], G["results"]], R),
        Q("kidney.kfre_and_referral_plan", "Kidney Failure Risk and Referral", "string", "risk-plan", "신부전 위험도(KFRE)를 안내받았거나 신장내과 의뢰·재의뢰 기준이 정해졌나요?", 126, [G["cause"]], R),

        Q("kidney.dialysis_modality_schedule_and_last_session", "Dialysis Modality and Schedule", "string", "dialysis-schedule", "혈액·복막투석 방식, 정규 일정과 마지막 투석 완료 여부를 알려주세요.", 130, [G["dialysis"]], R, terminology_binding={"system": SN, "code": "265764009"}, mrcm_ref=M),
        Q("kidney.dialysis_access_type_and_condition", "Dialysis Access", "string", "dialysis-access", "동정맥루·인조혈관·카테터 위치와 통증·발적·분비물·진동 변화를 알려주세요.", 129, [G["dialysis"]], R),
        Q("kidney.dialysis_weight_bp_cramps_and_recovery", "Dialysis Tolerance", "string", "dialysis-tolerance", "투석 전후 체중·혈압, 저혈압·쥐·흉통·회복 시간과 목표 건체중을 알려주세요.", 128, [G["dialysis"]], R),
        Q("kidney.missed_or_shortened_dialysis", "Missed Dialysis", "string", "missed-dialysis", "최근 빠뜨리거나 일찍 끝낸 투석과 이유, 이후 증상을 알려주세요.", 127, [G["dialysis"]], R),

        Q("kidney.transplant_date_donor_and_baseline_function", "Kidney Transplant Context", "string", "transplant", "이식 날짜·기증자 유형, 평소 크레아티닌과 과거 거부반응을 알려주세요.", 130, [G["transplant"]], R, terminology_binding={"system": SN, "code": "70536003"}, mrcm_ref=M),
        Q("kidney.immunosuppression_levels_and_adherence", "Transplant Immunosuppression", "string", "immunosuppression", "면역억제제 이름·용량·복용시각, 빠뜨린 복용과 최근 약물농도를 알려주세요.", 129, [G["transplant"]], R),
        Q("kidney.transplant_infection_rejection_and_followup", "Transplant Follow-up", "string", "transplant-followup", "최근 감염·거부반응·입원, 이식팀 검사와 다음 진료 일정을 알려주세요.", 128, [G["transplant"]], R),
    ]
    safety = [("anuria", "kidney.anuria_or_severe_oliguria", "urgent", 990), ("pulmonary-edema", "kidney.pulmonary_edema_pattern", "emergency", 1000), ("hyperkalemia", "kidney.hyperkalemia_instability_pattern", "emergency", 1000), ("uremic-neurologic", "kidney.uremic_neurologic_pattern", "emergency", 1000), ("hypertensive-emergency", "kidney.hypertensive_emergency_pattern", "emergency", 1000), ("dehydration", "kidney.severe_dehydration_with_reduced_urine", "urgent", 980), ("access-bleeding", "kidney.dialysis_access_uncontrolled_bleeding", "emergency", 1000), ("access-infection", "kidney.dialysis_access_infection_or_failure", "urgent", 980), ("pd-peritonitis", "kidney.peritoneal_dialysis_peritonitis_pattern", "urgent", 990), ("transplant-warning", "kidney.transplant_graft_warning", "urgent", 990), ("flank-fever", "kidney.flank_pain_fever_and_systemic_illness", "urgent", 980), ("urgent-lab", "kidney.known_severe_aki_or_urgent_lab_callback", "urgent", 990)]
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, priority) for key, fid, level, priority in safety]
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-31", "next_monitor_at": "2026-08-01", "next_full_review_at": "2027-01-27"})
    return {"id": "knowledge.generated.kidney-function-ckd-follow-up", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-kidney-function-ckd-follow-up-research", "default_refresh": refresh, "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="kidney.primary_group", question_budget=65, source_refs=SOURCES)
    common = ["kidney.onset_duration_and_course", "kidney.current_symptom_priority", "kidney.ckd_cause_stage_and_diagnosis_date", "kidney.latest_serum_creatinine_result", "kidney.latest_egfr_result", "kidney.latest_kidney_result_date", "kidney.egfr_creatinine_trend_and_baseline", "kidney.latest_urine_acr_result", "kidney.urine_protein_specimen_context", "kidney.urinalysis_blood_protein_and_sediment", "kidney.electrolytes_bicarbonate_urea_and_albumin", "kidney.urine_volume_frequency_and_nocturia", "kidney.edema_weight_and_fluid_change", "kidney.dyspnea_severity", "kidney.fatigue_lethargy_severity", "kidney.nausea_severity", "kidney.reduced_appetite_severity", "kidney.pruritus_severity", "kidney.muscle_cramps_severity", "kidney.sleep_disturbance_severity", "pain.nrs_score", "kidney.daily_activity_impact", "kidney.home_and_clinic_blood_pressure", "kidney.current_medicines_doses_and_adherence", "kidney.nsaid_otc_herbal_and_contrast_exposure", "kidney.recent_illness_intake_and_medication_holds", "kidney.diabetes_hypertension_cardiovascular_and_gout", "kidney.other_detail_or_patient_priority"]
    cases = {"abnormal_kidney_result": ["kidney.cbc_iron_pth_and_vitamin_d", "kidney.ultrasound_biopsy_and_kidney_imaging", "kidney.prior_aki_dates_causes_and_recovery"], "known_ckd_followup": ["kidney.acei_arb_sglt2_diuretic_and_mra", "kidney.family_history_and_hereditary_disease", "kidney.diet_salt_protein_potassium_and_phosphate", "kidney.kfre_and_referral_plan"], "acute_kidney_change": ["kidney.prior_aki_dates_causes_and_recovery", "kidney.stones_obstruction_prostate_and_infections", "kidney.ultrasound_biopsy_and_kidney_imaging"], "proteinuria_or_hematuria": ["kidney.latest_urine_pcr_result", "kidney.autoimmune_systemic_and_glomerular_disease", "kidney.stones_obstruction_prostate_and_infections", "kidney.ultrasound_biopsy_and_kidney_imaging"], "dialysis_followup": ["kidney.dialysis_modality_schedule_and_last_session", "kidney.dialysis_access_type_and_condition", "kidney.dialysis_weight_bp_cramps_and_recovery", "kidney.missed_or_shortened_dialysis"], "kidney_transplant_followup": ["kidney.transplant_date_donor_and_baseline_function", "kidney.immunosuppression_levels_and_adherence", "kidney.transplant_infection_rejection_and_followup"], "structural_or_hereditary": ["kidney.family_history_and_hereditary_disease", "kidney.stones_obstruction_prostate_and_infections", "kidney.ultrasound_biopsy_and_kidney_imaging"], "other_unclear": ["kidney.other_detail_or_patient_priority"]}
    p["required_facts"]["routine"], p["conditional_required_facts"] = common, [{"selector_fact": "kidney.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nice.ng203.ckd.2025", "NICE", "Chronic kidney disease: assessment and management", "NG203; last updated 2021-11-24", "https://www.nice.org.uk/guidance/ng203", "nice_guidance", "sha256:42a54199347c47ffa3d8eafc278c04346a00d1fdd1b92267521f862b18a8160b", "2026-07-28", "current_official_source_confirmed_metadata_corrected", ["CKD assessment uses eGFR and urine ACR together, trends, cause, progression risk, medicines, comorbidity and individualized monitoring.", "Urgent complications include hyperkalaemia, severe uraemia, acidosis and fluid overload; this package captures warning features and does not calculate diagnosis or treatment eligibility."]),
        ("source.nice.ng148.aki.2024", "NICE", "Acute kidney injury: prevention, detection and management", "NG148; last updated 2024-10-16", "https://www.nice.org.uk/guidance/ng148", "nice_guidance", "sha256:b2195742417512dab1ff07ddafa2cd4d24c3d85e5bdaecfb683174f91141ab8e", "2026-07-28", "current_official_source_confirmed", ["Acute illness, oliguria, dehydration, nephrotoxic medicines and recent contrast are relevant to acute kidney injury risk and escalation."]),
        ("source.kdigo.ckd.2024", "KDIGO", "2024 CKD evaluation and management guideline", "Kidney International 105 (Suppl 4S), S117-S314", "https://kdigo.org/wp-content/uploads/2024/03/KDIGO-2024-CKD-Guideline.pdf", "clinical_guideline", "sha256:b18db280f7dc889a1a99447b779c0312cd536f939a5180b38894a5d68e4410c0", "2026-07-31", "current_official_source_confirmed_no_clinical_change", ["CKD evaluation and follow-up require cause, GFR, albuminuria, progression, complications, cardiovascular risk, medicines and kidney replacement therapy planning.", "Practice Point 2.1.1 supports recording albuminuria and GFR as distinct monitored measures rather than collapsing them into an unstructured combined response.", "KDIGO Practice Point 5.2.2.1 supports asking people with progressive CKD about uremic symptoms at each consultation using a standardized validated symptom assessment tool."]),
        ("source.stom.kidney.20260715", "Infoclinic", "STOM kidney terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", "live_response_summary_not_raw_cache", "2026-07-15", "current_official_source_confirmed", ["FHIR lookup confirmed active concepts for CKD, acute kidney injury, proteinuria, haematuria, CKD stage 5, kidney transplant and renal dialysis.", "MRCM supports provisional semantic binding only and does not establish stage or urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": digest, "license_status": "restricted" if pub in {"NICE", "Infoclinic", "KDIGO"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": last_monitored, "monitor_result": monitor_result, "assertions": assertions} for i, pub, title, version, url, profile, digest, last_monitored, monitor_result, assertions in defs]
    research = {"id": "source-manifest.primary-care-kidney-function-ckd-follow-up-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.kidney", "generated_clinical_knowledge", "knowledge/generated/renal/kidney-function-ckd-follow-up/kidney-function-ckd-follow-up.json", True), ("source.mapping.kidney", "terminology_mapping", "mappings/terminology/snomed-mrcm-kidney-function-ckd-follow-up.json", False), ("source.external.kidney", "external_source_manifest", "sources/manifests/primary-care-kidney-function-ckd-follow-up-research.json", False), ("source.policy.kidney", "runtime_policy", "policies/primary-care-kidney-function-ckd-follow-up-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-kidney-function-ckd-follow-up", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level, key = rule["when"]["fact"], rule["then"]["safety_level"], rule["id"].split("safety.")[1]
        out[f"KIDNEY-{key.upper()}.json"] = {"id": f"KIDNEY-{key.upper()}", "simulation_language": "ko", "persona": {"age": 31 + i}, "initial_statement": {"ko": "신장기능이 걱정돼서 왔어요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.aki", "diagnosis.ckd_progression", "diagnosis.hyperkalemia"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["known_ckd_followup"])
    by_id, hidden = {x["fact"]["id"]: x["fact"] for x in f["entries"]}, {}
    for fid in required:
        fact = by_id[fid]
        hidden[fid] = {"value": False if fact["value_type"] == "boolean" else fact.get("allowed_values", ["unclear"])[-1] if fact["value_type"] == "coded" else 0 if fact["value_type"] == "integer" else "없음"}
    hidden["kidney.primary_group"] = {"value": "known_ckd_followup"}
    for fid in (
        "kidney.dyspnea_severity", "kidney.fatigue_lethargy_severity",
        "kidney.nausea_severity", "kidney.reduced_appetite_severity",
        "kidney.pruritus_severity", "kidney.muscle_cramps_severity",
        "kidney.sleep_disturbance_severity", "kidney.daily_activity_impact",
    ):
        hidden[fid] = {"value": "none"}
    declined = "kidney.diet_salt_protein_potassium_and_phosphate"
    hidden.pop(declined)
    out["KIDNEY-CKD-DATA-ABSENT.json"] = {"id": "KIDNEY-CKD-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 58}, "initial_statement": {"ko": "만성콩팥병 정기 진료예요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 65, "forbidden_assertions": ["diagnosis.ckd_stage", "diagnosis.dialysis_needed"]}, "provenance": provenance(["source.nice.ng203.ckd.2025", "specifications/clinical-memory.md"])}
    handoff = {fid: dict(value) for fid, value in hidden.items()}
    handoff.update({
        "kidney.onset_duration_and_course": {"value": "3년 전 진단 후 정기 추적 중이며 최근 급격한 악화는 없음"},
        "kidney.current_symptom_priority": {"value": "최근 오후 피로가 진료에 전달되길 원함"},
        "kidney.ckd_cause_stage_and_diagnosis_date": {"value": "고혈압 관련 CKD G3b A2로 3년 전 안내받음"},
        "kidney.latest_serum_creatinine_result": {"value": "1.6 mg/dL"},
        "kidney.latest_egfr_result": {"value": "42 mL/min/1.73m2"},
        "kidney.latest_kidney_result_date": {"value": "2026-07-20"},
        "kidney.egfr_creatinine_trend_and_baseline": {"value": "지난 1년 eGFR 40~44로 큰 변화 없음"},
        "kidney.latest_urine_acr_result": {"value": "120 mg/g"},
        "kidney.urine_protein_specimen_context": {"value": "first_morning"},
        "kidney.urinalysis_blood_protein_and_sediment": {"value": "단백 양성, 혈뇨나 원주는 없다고 들음"},
        "kidney.electrolytes_bicarbonate_urea_and_albumin": {"value": "같은 날 칼륨 4.6 mmol/L, 중탄산염 24 mmol/L, 알부민 정상"},
        "kidney.urine_volume_frequency_and_nocturia": {"value": "소변량 변화 없음, 야간뇨 1회"},
        "kidney.edema_weight_and_fluid_change": {"value": "부종 없고 최근 체중 변화 없음"},
        "kidney.fatigue_lethargy_severity": {"value": "mild"},
        "kidney.daily_activity_impact": {"value": "mild"},
        "kidney.home_and_clinic_blood_pressure": {"value": "가정혈압 최근 평균 128/76 mmHg"},
        "kidney.current_medicines_doses_and_adherence": {"value": "처방약을 매일 복용하며 최근 누락 없음"},
        "kidney.nsaid_otc_herbal_and_contrast_exposure": {"value": "진통소염제·한약·보충제 복용 및 최근 조영제 검사 없음"},
        "kidney.recent_illness_intake_and_medication_holds": {"value": "최근 구토·설사·발열이나 식사·수분 감소 없음"},
        "kidney.diabetes_hypertension_cardiovascular_and_gout": {"value": "고혈압 치료 중, 당뇨·심혈관질환·통풍 없음"},
        "kidney.acei_arb_sglt2_diuretic_and_mra": {"value": "ARB 복용 중이며 최근 용량 변경 없음"},
        "kidney.family_history_and_hereditary_disease": {"value": "가족의 투석·이식·유전성 신장질환 병력 없음"},
        "kidney.kfre_and_referral_plan": {"value": "신장내과 정기 추적 중이며 다음 진료에서 위험도를 확인할 예정"},
        "kidney.other_detail_or_patient_priority": {"value": "검사 추세와 피로가 연관될 수 있는지 의료진에게 확인하고 싶음"},
    })
    out["KIDNEY-CKD-CLINICIAN-HANDOFF.json"] = {
        "id": "KIDNEY-CKD-CLINICIAN-HANDOFF",
        "simulation_language": "ko",
        "clinician_submission": True,
        "encounter_context": {
            "care_setting": "specialist_clinic", "encounter_type": "follow_up",
            "interview_initiator": "patient", "interview_mode": "chat",
            "available_information": ["synthetic_patient_reported_results"],
            "time_constraint": "routine", "clinical_responsibility": "decision_support",
        },
        "persona": {"age": 62},
        "initial_statement": {"ko": "만성콩팥병 정기 진료 전에 최근 검사와 증상을 정리하려고 합니다."},
        "hidden_state": handoff,
        "response_behavior": {
            "encounter.context_review_state": {
                "response_text": "최근 확인했고 바뀐 내용이 없습니다"
            }
        },
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_clinician_handoff": True,
            "expected_known_facts": {
                "kidney.primary_group": "known_ckd_followup",
                "kidney.fatigue_lethargy_severity": "mild",
                "pain.nrs_score": 0,
                "kidney.daily_activity_impact": "mild",
            },
            "expected_selected_facts_contains": [
                "kidney.latest_serum_creatinine_result",
                "kidney.latest_egfr_result",
                "kidney.latest_kidney_result_date",
                "kidney.latest_urine_acr_result",
                "kidney.urine_protein_specimen_context",
            ],
            "expected_selected_facts_excludes": [
                "kidney.latest_creatinine_egfr_and_reference",
                "kidney.urine_acr_pcr_and_collection_context",
                "history.condition.current", "history.procedure.past",
                "medication.current", "allergy.current", "history.family",
                "occupation.current", "patient.smoking.status",
                "patient.smoking.exposure_detail", "patient.alcohol.pattern",
            ],
            "expected_max_turns": 60,
            "forbidden_assertions": ["diagnosis.ckd_progression", "diagnosis.uremia", "recommendation.change_medication"],
        },
        "provenance": provenance(["source.kdigo.ckd.2024", "source.nice.ng203.ckd.2025", "specifications/clinical-memory.md"]),
    }
    lab_handoff = {fid: dict(value) for fid, value in handoff.items()}
    lab_handoff.update({
        "kidney.primary_group": {"value": "proteinuria_or_hematuria"},
        "kidney.latest_urine_pcr_result": {"value": "310 mg/g"},
        "kidney.autoimmune_systemic_and_glomerular_disease": {"value": "알고 있는 자가면역질환이나 사구체질환 없음"},
        "kidney.stones_obstruction_prostate_and_infections": {"value": "결석·요로폐쇄·반복 요로감염 병력 없음"},
        "kidney.ultrasound_biopsy_and_kidney_imaging": {"value": "최근 초음파에서 폐쇄는 없다고 들음"},
    })
    out["KIDNEY-LAB-ATOMIC-HANDOFF.json"] = {
        "id": "KIDNEY-LAB-ATOMIC-HANDOFF",
        "simulation_language": "ko",
        "clinician_submission": True,
        "encounter_context": {
            "care_setting": "specialist_clinic", "encounter_type": "follow_up",
            "interview_initiator": "patient", "interview_mode": "chat",
            "available_information": ["synthetic_scanned_lab_summary"],
            "time_constraint": "routine", "clinical_responsibility": "decision_support",
        },
        "persona": {"age": 59},
        "initial_statement": {"ko": "콩팥 추적 진료 전에 크레아티닌, eGFR, 소변 ACR과 PCR 결과를 구분해 전달하고 싶어요."},
        "hidden_state": lab_handoff,
        "response_behavior": {
            "encounter.context_review_state": {
                "response_text": "최근 확인했고 바뀐 내용이 없습니다"
            }
        },
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_clinician_handoff": True,
            "expected_selected_facts_contains": [
                "kidney.latest_serum_creatinine_result",
                "kidney.latest_egfr_result",
                "kidney.latest_kidney_result_date",
                "kidney.latest_urine_acr_result",
                "kidney.latest_urine_pcr_result",
                "kidney.urine_protein_specimen_context",
            ],
            "expected_selected_facts_excludes": [
                "kidney.latest_creatinine_egfr_and_reference",
                "kidney.urine_acr_pcr_and_collection_context",
            ],
            "expected_max_turns": 62,
            "forbidden_assertions": [
                "diagnosis.ckd_progression", "diagnosis.glomerulonephritis",
                "recommendation.change_medication",
            ],
        },
        "provenance": provenance([
            "source.kdigo.ckd.2024",
            "source.stom.fhir-r4-terminology-server",
            "specifications/clinical-memory.md",
        ]),
    }
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Kidney Function Concern or CKD Follow-up", intents=[("intent.characterize_symptom", "Characterize Kidney Function and Symptoms"), ("intent.screen_red_flags", "Screen Acute Kidney and Treatment Emergencies"), ("intent.differentiate_common_causes", "Assess Cause Medication and Structural Context"), ("intent.risk_assessment", "Assess Progression Complications and Kidney Replacement Care")])
    primary, research = source_docs()
    concepts = [("709044004", "Chronic kidney disease (disorder)", 0), ("14669001", "Acute kidney injury (disorder)", 0), ("29738008", "Proteinuria (finding)", 0), ("34436003", "Blood in urine (finding)", 0), ("433146000", "Chronic kidney disease stage 5 (disorder)", 0), ("70536003", "Transplant of kidney (procedure)", 0), ("265764009", "Renal dialysis (procedure)", 0)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["363698007", "116676008", "246112005"], "validation": {"method": "build_time_live_fhir_lookup_and_mrcm_summary", "checked_at": "2026-07-15T00:00:00Z", "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.kidney.20260715"])}
    docs = [("knowledge/base/primary-care-kidney-function-ckd-follow-up.json", graph), ("rules/base/primary-care-kidney-function-ckd-follow-up.json", rules), ("knowledge/generated/renal/kidney-function-ckd-follow-up/kidney-function-ckd-follow-up.json", f), ("mappings/terminology/snomed-mrcm-kidney-function-ckd-follow-up.json", mapping), ("sources/manifests/primary-care-kidney-function-ckd-follow-up.json", primary), ("sources/manifests/primary-care-kidney-function-ckd-follow-up-research.json", research), ("policies/primary-care-kidney-function-ckd-follow-up-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/renal/kidney-function-ckd-follow-up/" + name, case)


if __name__ == "__main__": main()
