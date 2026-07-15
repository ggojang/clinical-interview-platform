#!/usr/bin/env python3
"""Materialize unreviewed liver-function and chronic liver follow-up knowledge."""
from profile_support import *

P, RFE, M, SN = "liver-function-chronic-follow-up", "rfe.liver_function_chronic_follow_up", "mapping.snomed-mrcm.liver-function-chronic-follow-up", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = ["source.nice.ng50.cirrhosis.2023", "source.nice.ng49.nafld.2024", "source.nice.cg165.hepatitis-b", "source.stom.liver.20260715"]
G = {k: f"group.liver.{k}" for k in ("routing", "safety", "common", "cause", "complication", "treatment")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("liver.primary_group", "Primary Liver Presentation", "coded", "primary-group", "이번 방문은 간수치 이상, 지방간·대사성 간질환, 바이러스간염, 알코올 관련 간질환, 간경변 추적, 약물·보충제 관련 이상, 치료 후 추적 중 무엇에 가깝나요?", 180, [G["routing"]], C, allowed_values=["abnormal_liver_tests", "steatotic_metabolic_liver", "viral_hepatitis", "alcohol_related_liver", "cirrhosis_followup", "medicine_or_supplement_injury", "post_treatment_followup", "other_unclear"]),
        Q("liver.haematemesis_or_melena", "Variceal or Upper GI Bleeding", "boolean", "gi-bleed", "피를 토하거나 커피 찌꺼기 같은 구토, 검고 끈적한 타르변이 있나요?", 179, [G["safety"], G["complication"]], S, safety_relevant=True),
        Q("liver.new_confusion_or_reduced_consciousness", "Possible Hepatic Encephalopathy", "boolean", "encephalopathy", "새로 혼란스럽거나 말이 어눌해지고, 성격·수면이 갑자기 변하거나 깨우기 어려운가요?", 178, [G["safety"], G["complication"]], S, safety_relevant=True),
        Q("liver.ascites_with_fever_or_severe_pain", "Possible Spontaneous Bacterial Peritonitis", "boolean", "ascites-infection", "복수가 있거나 배가 불러온 상태에서 발열·오한·새로운 심한 복통·혼란이 있나요?", 177, [G["safety"], G["complication"]], S, safety_relevant=True),
        Q("liver.rapid_jaundice_with_systemic_illness", "Rapid Jaundice and Systemic Illness", "boolean", "rapid-jaundice", "황달이 빠르게 심해지면서 심한 처짐·구토·혼란·출혈 중 하나가 있나요?", 176, [G["safety"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "18165001"}, mrcm_ref=M),
        Q("liver.severe_right_upper_pain_fever_jaundice", "Biliary Sepsis Pattern", "boolean", "biliary-sepsis", "오른쪽 윗배의 심한 통증과 발열·오한·황달이 함께 있나요?", 175, [G["safety"]], S, safety_relevant=True),
        Q("liver.acetaminophen_or_toxic_overdose", "Potential Hepatotoxic Overdose", "boolean", "toxic-overdose", "아세트아미노펜 등 약을 권장량보다 많이 먹었거나 독성 물질을 복용한 가능성이 있나요?", 174, [G["safety"], G["treatment"]], S, safety_relevant=True),
        Q("liver.severe_bleeding_or_coagulopathy", "Severe Bleeding or Coagulopathy", "boolean", "coagulopathy", "압박해도 멈추지 않는 출혈, 많은 코피·잇몸출혈 또는 갑자기 커지는 멍이 있나요?", 173, [G["safety"], G["complication"]], S, safety_relevant=True),
        Q("liver.respiratory_distress_with_tense_ascites", "Respiratory Distress with Ascites", "boolean", "ascites-dyspnea", "배가 매우 팽팽하게 불러오면서 가만히 있어도 숨쉬기 어렵거나 누울 수 없나요?", 172, [G["safety"], G["complication"]], S, safety_relevant=True),
        Q("liver.severe_vomiting_dehydration_or_oliguria", "Dehydration or Kidney Deterioration", "boolean", "dehydration-oliguria", "계속 토하거나 설사해 물을 못 마시고 소변이 크게 줄며 어지럽거나 실신할 것 같은가요?", 171, [G["safety"]], S, safety_relevant=True),
        Q("liver.alcohol_withdrawal_severe_pattern", "Severe Alcohol Withdrawal", "boolean", "alcohol-withdrawal", "최근 술을 갑자기 줄이거나 끊은 뒤 심한 떨림·환각·경련·혼란이 있나요?", 170, [G["safety"], G["cause"]], S, safety_relevant=True),
        Q("liver.post_procedure_bleeding_or_infection", "Post Liver Procedure Complication", "boolean", "post-procedure", "최근 간생검·복수천자·내시경 치료 후 많은 출혈, 심한 복통·발열·어지럼이 있나요?", 169, [G["safety"], G["treatment"]], S, safety_relevant=True),
        Q("liver.urgent_abnormal_result_callback", "Urgent Liver Result Alert", "boolean", "urgent-result", "의료기관에서 간수치·빌리루빈·INR 등 결과 때문에 즉시 평가받으라고 연락받았나요?", 168, [G["safety"]], S, safety_relevant=True),

        Q("liver.onset_duration_and_course", "Onset Duration and Course", "string", "onset", "증상 또는 검사 이상을 처음 안 시기, 지속 기간과 경과를 알려주세요.", 155, [G["common"]], C),
        Q("liver.current_symptom_priority", "Current Symptom Priority", "string", "priority", "현재 가장 불편하거나 의료진에게 우선 확인받고 싶은 점은 무엇인가요?", 154, [G["common"]], C),
        Q("liver.diagnosis_cause_stage_and_date", "Liver Diagnosis Cause and Stage", "string", "diagnosis", "알고 있는 간질환의 진단명·원인·섬유화 또는 간경변 단계와 진단 시기를 알려주세요.", 153, [G["common"], G["cause"]], R, terminology_binding={"system": SN, "code": "328383001"}, mrcm_ref=M),
        Q("liver.latest_ast_alt_alp_ggt_and_reference", "Latest Liver Enzymes", "string", "enzymes", "최근 AST·ALT·ALP·GGT 수치, 검사일과 기준범위를 알려주세요.", 152, [G["common"]], R, terminology_binding={"system": SN, "code": "166643006"}, mrcm_ref=M),
        Q("liver.bilirubin_albumin_inr_and_platelets", "Liver Function and Portal Markers", "string", "function-tests", "총·직접 빌리루빈, 알부민, PT/INR, 혈소판 결과와 날짜를 알려주세요.", 151, [G["common"]], R),
        Q("liver.test_trend_and_baseline", "Liver Test Trend", "string", "trend", "이전 검사와 비교한 추세, 평소 기준값과 갑자기 변한 시점을 알려주세요.", 150, [G["common"]], R),
        Q("liver.jaundice_urine_stool_and_pruritus", "Jaundice Detail", "string", "jaundice-detail", "눈·피부 황달, 짙은 소변·창백한 변·가려움의 시작과 변화를 알려주세요.", 149, [G["common"]], C),
        Q("liver.abdominal_distension_edema_and_weight", "Ascites Oedema and Weight", "string", "fluid", "복부팽만·복수, 다리부종과 최근 체중·허리둘레 변화를 알려주세요.", 148, [G["common"], G["complication"]], C, terminology_binding={"system": SN, "code": "389026000"}, mrcm_ref=M),
        Q("liver.abdominal_pain_nausea_appetite_and_weight_loss", "Abdominal and Constitutional Symptoms", "string", "abdominal", "복통 위치·양상, 메스꺼움·식욕저하와 의도하지 않은 체중감소가 있나요?", 147, [G["common"]], C),
        Q("liver.fatigue_sleep_cognition_and_function", "Fatigue Cognition and Function", "string", "function", "피로·수면·집중·기억 변화와 일상 기능 저하를 알려주세요.", 146, [G["common"]], C),
        Q("liver.bleeding_bruising_and_stool_history", "Bleeding History", "string", "bleeding", "코피·잇몸출혈·멍, 구토혈·검은변·혈변과 과거 정맥류 출혈이 있었나요?", 145, [G["common"], G["complication"]], R),
        Q("liver.current_medicines_doses_and_adherence", "Current Medicines", "string", "medicines", "현재 처방약의 이름·용량·복용법, 최근 변경과 빠뜨린 복용을 알려주세요.", 144, [G["common"], G["treatment"]], R),
        Q("liver.otc_herbal_supplement_and_acetaminophen", "Potential Hepatotoxic Exposures", "string", "hepatotoxins", "진통제·감기약, 한약·보충제·다이어트제품과 아세트아미노펜 하루 복용량을 알려주세요.", 143, [G["common"], G["cause"]], R),
        Q("liver.alcohol_pattern_and_last_use", "Alcohol Pattern", "string", "alcohol", "술 종류·한 번 양·주당 횟수, 폭음과 마지막 음주 시각, 최근 감량·중단을 알려주세요.", 142, [G["common"], G["cause"]], R),
        Q("liver.metabolic_risk_weight_waist_diabetes_lipids", "Metabolic Risk", "string", "metabolic", "키·체중·허리둘레와 당뇨·고혈압·이상지질혈증·수면무호흡 상태를 알려주세요.", 141, [G["common"], G["cause"]], R),
        Q("liver.hepatitis_risk_vaccination_and_results", "Viral Hepatitis Context", "string", "hepatitis", "B·C형간염 검사·바이러스 수치, 예방접종과 혈액·주사·문신·성접촉·가족 노출 위험을 알려주세요.", 140, [G["common"], G["cause"]], R),
        Q("liver.autoimmune_metabolic_and_family_history", "Other Liver Causes and Family History", "string", "other-causes", "자가면역·철·구리 관련 질환과 가족의 간질환·간암 병력을 알려주세요.", 139, [G["common"], G["cause"]], R),
        Q("liver.pregnancy_status_and_plans", "Pregnancy Status and Plans", "string", "pregnancy", "임신 중·수유 중·임신 계획 여부와 관련 약물 상담을 알려주세요.", 138, [G["common"]], R),
        Q("liver.other_detail_or_patient_priority", "Other Liver Detail", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달하고 싶은 내용이나 걱정을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("liver.ultrasound_ct_mri_and_elastography", "Liver Imaging and Elastography", "string", "imaging", "초음파·CT·MRI와 탄성도검사 결과, 지방간·결절·비장비대·문맥 소견을 알려주세요.", 130, [G["cause"]], R),
        Q("liver.fibrosis_scores_and_biopsy", "Fibrosis Assessment", "string", "fibrosis", "FIB-4·ELF 등 섬유화 점수와 간생검 결과·날짜를 알려주세요.", 129, [G["cause"]], R),
        Q("liver.prior_decompensation_admissions_and_triggers", "Prior Decompensation", "string", "decompensation", "과거 복수·뇌증·정맥류 출혈·황달로 입원한 시기와 유발 요인을 알려주세요.", 128, [G["complication"]], R),
        Q("liver.encephalopathy_lactulose_and_bowel_target", "Encephalopathy Management", "string", "encephalopathy-management", "간성뇌증 병력, 락툴로오스·리팍시민 복용과 하루 목표 배변 횟수를 알려주세요.", 127, [G["complication"], G["treatment"]], R, terminology_binding={"system": SN, "code": "13920009"}, mrcm_ref=M),
        Q("liver.ascites_diuretics_paracentesis_and_sbp", "Ascites Management", "string", "ascites-management", "이뇨제·염분 제한, 복수천자 횟수·마지막 날짜와 자발성 세균성 복막염 병력을 알려주세요.", 126, [G["complication"], G["treatment"]], R),
        Q("liver.varices_endoscopy_beta_blocker_and_banding", "Varices Management", "string", "varices", "위내시경 정맥류 결과, 밴드결찰과 카르베딜롤·프로프라놀롤 복용·맥박·혈압을 알려주세요.", 125, [G["complication"], G["treatment"]], R),
        Q("liver.hcc_surveillance_ultrasound_afp", "HCC Surveillance", "string", "hcc-surveillance", "간암 감시 초음파·AFP의 마지막 날짜·결과와 다음 예약을 알려주세요.", 124, [G["complication"], G["treatment"]], R),
        Q("liver.antiviral_or_disease_specific_treatment", "Disease-specific Treatment", "string", "specific-treatment", "항바이러스제·면역억제제·대사질환 치료의 이름·기간·반응을 알려주세요.", 123, [G["treatment"]], R),
        Q("liver.transplant_evaluation_and_care_plan", "Transplant and Care Plan", "string", "transplant-plan", "간이식 평가 여부, 간 전문진료 일정과 악화 시 안내받은 기준을 알려주세요.", 122, [G["treatment"]], R),
    ]
    safety = [("gi-bleed", "liver.haematemesis_or_melena", "emergency", 1000), ("encephalopathy", "liver.new_confusion_or_reduced_consciousness", "emergency", 1000), ("ascites-infection", "liver.ascites_with_fever_or_severe_pain", "urgent", 990), ("rapid-jaundice", "liver.rapid_jaundice_with_systemic_illness", "urgent", 990), ("biliary-sepsis", "liver.severe_right_upper_pain_fever_jaundice", "urgent", 990), ("toxic-overdose", "liver.acetaminophen_or_toxic_overdose", "emergency", 1000), ("coagulopathy", "liver.severe_bleeding_or_coagulopathy", "emergency", 1000), ("ascites-dyspnea", "liver.respiratory_distress_with_tense_ascites", "emergency", 1000), ("dehydration-oliguria", "liver.severe_vomiting_dehydration_or_oliguria", "urgent", 980), ("alcohol-withdrawal", "liver.alcohol_withdrawal_severe_pattern", "emergency", 1000), ("post-procedure", "liver.post_procedure_bleeding_or_infection", "urgent", 980), ("urgent-result", "liver.urgent_abnormal_result_callback", "urgent", 990)]
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, priority) for key, fid, level, priority in safety]
    return {"id": "knowledge.generated.liver-function-chronic-follow-up", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-liver-function-chronic-follow-up-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="liver.primary_group", question_budget=62, source_refs=SOURCES)
    common = ["liver.onset_duration_and_course", "liver.current_symptom_priority", "liver.diagnosis_cause_stage_and_date", "liver.latest_ast_alt_alp_ggt_and_reference", "liver.bilirubin_albumin_inr_and_platelets", "liver.test_trend_and_baseline", "liver.jaundice_urine_stool_and_pruritus", "liver.abdominal_distension_edema_and_weight", "liver.abdominal_pain_nausea_appetite_and_weight_loss", "liver.fatigue_sleep_cognition_and_function", "liver.bleeding_bruising_and_stool_history", "liver.current_medicines_doses_and_adherence", "liver.otc_herbal_supplement_and_acetaminophen", "liver.alcohol_pattern_and_last_use", "liver.metabolic_risk_weight_waist_diabetes_lipids", "liver.other_detail_or_patient_priority"]
    cases = {"abnormal_liver_tests": ["liver.hepatitis_risk_vaccination_and_results", "liver.autoimmune_metabolic_and_family_history", "liver.ultrasound_ct_mri_and_elastography"], "steatotic_metabolic_liver": ["liver.metabolic_risk_weight_waist_diabetes_lipids", "liver.fibrosis_scores_and_biopsy", "liver.ultrasound_ct_mri_and_elastography"], "viral_hepatitis": ["liver.hepatitis_risk_vaccination_and_results", "liver.antiviral_or_disease_specific_treatment", "liver.hcc_surveillance_ultrasound_afp"], "alcohol_related_liver": ["liver.prior_decompensation_admissions_and_triggers", "liver.ultrasound_ct_mri_and_elastography"], "cirrhosis_followup": ["liver.prior_decompensation_admissions_and_triggers", "liver.encephalopathy_lactulose_and_bowel_target", "liver.ascites_diuretics_paracentesis_and_sbp", "liver.varices_endoscopy_beta_blocker_and_banding", "liver.hcc_surveillance_ultrasound_afp", "liver.transplant_evaluation_and_care_plan"], "medicine_or_supplement_injury": ["liver.otc_herbal_supplement_and_acetaminophen", "liver.pregnancy_status_and_plans"], "post_treatment_followup": ["liver.antiviral_or_disease_specific_treatment", "liver.ultrasound_ct_mri_and_elastography", "liver.hcc_surveillance_ultrasound_afp", "liver.transplant_evaluation_and_care_plan"], "other_unclear": ["liver.other_detail_or_patient_priority"]}
    p["required_facts"]["routine"], p["conditional_required_facts"] = common, [{"selector_fact": "liver.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [("source.nice.ng50.cirrhosis.2023", "NICE", "Cirrhosis in over 16s: assessment and management", "NG50; updated-2023-09-08", "https://www.nice.org.uk/guidance/ng50/chapter/Recommendations", "nice_guidance", ["Cirrhosis assessment includes cause, decompensation, varices, ascites, encephalopathy, medicines and hepatocellular carcinoma surveillance.", "Gastrointestinal bleeding, acute confusion, infected ascites and respiratory compromise require urgent escalation."]), ("source.nice.ng49.nafld.2024", "NICE", "Non-alcoholic fatty liver disease: assessment and management", "NG49; surveillance-2024", "https://www.nice.org.uk/guidance/ng49", "nice_guidance", ["Steatotic liver disease may be asymptomatic and requires metabolic risk, fibrosis assessment and imaging context rather than liver enzymes alone."]), ("source.nice.cg165.hepatitis-b", "NICE", "Chronic hepatitis B: diagnosis and management", "CG165", "https://www.nice.org.uk/Guidance/CG165/chapter/recommendations", "nice_guidance", ["Viral status, treatment, pregnancy, fibrosis, decompensation and HCC surveillance are relevant follow-up domains."]), ("source.stom.liver.20260715", "Infoclinic", "STOM liver terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["FHIR lookup confirmed active concepts for cirrhosis, liver steatosis, abnormal liver enzymes, jaundice, ascites, hepatic encephalopathy, chronic liver disease and portal hypertension.", "MRCM supports provisional semantic binding only and does not establish stage or urgency."])]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-15", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-liver-function-chronic-follow-up-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.liver", "generated_clinical_knowledge", "knowledge/generated/hepatology/liver-function-chronic-follow-up/liver-function-chronic-follow-up.json", True), ("source.mapping.liver", "terminology_mapping", "mappings/terminology/snomed-mrcm-liver-function-chronic-follow-up.json", False), ("source.external.liver", "external_source_manifest", "sources/manifests/primary-care-liver-function-chronic-follow-up-research.json", False), ("source.policy.liver", "runtime_policy", "policies/primary-care-liver-function-chronic-follow-up-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-liver-function-chronic-follow-up", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level, key = rule["when"]["fact"], rule["then"]["safety_level"], rule["id"].split("safety.")[1]
        out[f"LIVER-{key.upper()}.json"] = {"id": f"LIVER-{key.upper()}", "simulation_language": "ko", "persona": {"age": 30 + i}, "initial_statement": {"ko": "간수치와 간 건강이 걱정돼요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.cirrhosis", "diagnosis.hepatitis", "diagnosis.liver_cancer"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["cirrhosis_followup"])
    by_id, hidden = {x["fact"]["id"]: x["fact"] for x in f["entries"]}, {}
    for fid in required:
        fact = by_id[fid]
        hidden[fid] = {"value": False if fact["value_type"] == "boolean" else fact.get("allowed_values", ["unclear"])[-1] if fact["value_type"] == "coded" else 0 if fact["value_type"] == "integer" else "없음"}
    hidden["liver.primary_group"] = {"value": "cirrhosis_followup"}
    declined = "liver.hcc_surveillance_ultrasound_afp"
    hidden.pop(declined)
    out["LIVER-CIRRHOSIS-DATA-ABSENT.json"] = {"id": "LIVER-CIRRHOSIS-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 55}, "initial_statement": {"ko": "간경변 정기 진료예요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 62, "forbidden_assertions": ["diagnosis.decompensated_cirrhosis", "diagnosis.hcc"]}, "provenance": provenance(["source.nice.ng50.cirrhosis.2023", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Liver Function Concern or Chronic Liver Follow-up", intents=[("intent.characterize_symptom", "Characterize Liver Symptoms and Results"), ("intent.screen_red_flags", "Screen Acute Liver and Decompensation Emergencies"), ("intent.differentiate_common_causes", "Assess Metabolic Viral Alcohol and Medicine Context"), ("intent.risk_assessment", "Assess Fibrosis Complications and Surveillance")])
    primary, research = source_docs()
    concepts = [("19943007", "Cirrhosis of liver (disorder)", 0), ("197321007", "Steatosis of liver (disorder)", 0), ("166643006", "Liver enzymes outside reference range (finding)", 0), ("18165001", "Jaundice (finding)", 0), ("389026000", "Ascites (disorder)", 0), ("13920009", "Hepatic encephalopathy (disorder)", 0), ("328383001", "Chronic liver disease (disorder)", 0), ("34742003", "Portal hypertension (disorder)", 0)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["363698007", "246112005", "246454002"], "validation": {"method": "build_time_live_fhir_lookup_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.liver.20260715"])}
    docs = [("knowledge/base/primary-care-liver-function-chronic-follow-up.json", graph), ("rules/base/primary-care-liver-function-chronic-follow-up.json", rules), ("knowledge/generated/hepatology/liver-function-chronic-follow-up/liver-function-chronic-follow-up.json", f), ("mappings/terminology/snomed-mrcm-liver-function-chronic-follow-up.json", mapping), ("sources/manifests/primary-care-liver-function-chronic-follow-up.json", primary), ("sources/manifests/primary-care-liver-function-chronic-follow-up-research.json", research), ("policies/primary-care-liver-function-chronic-follow-up-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/hepatology/liver-function-chronic-follow-up/" + name, case)


if __name__ == "__main__": main()
