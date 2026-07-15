#!/usr/bin/env python3
"""Materialize unreviewed anaemia concern and follow-up interview knowledge."""
from profile_support import *

P, RFE, M, SN = "anemia-concern-follow-up", "rfe.anemia_concern_follow_up", "mapping.snomed-mrcm.anemia-concern-follow-up", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = ["source.bsg.ida.2021", "source.nice.ng12.anemia.2026", "source.who.ferritin.2020", "source.stom.anemia.20260715"]
G = {k: f"group.anemia.{k}" for k in ("routing", "safety", "common", "bleeding", "nutrition", "chronic", "treatment")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("anemia.primary_group", "Primary Anaemia Presentation", "coded", "primary-group", "이번 방문은 빈혈 의심 증상, 혈액검사상 빈혈, 철결핍빈혈, 비타민 B12·엽산 관련 빈혈, 만성질환·신장질환 관련 빈혈, 출혈 관련 빈혈, 치료 후 추적 중 무엇에 가깝나요?", 180, [G["routing"]], C, allowed_values=["suspected_symptomatic", "abnormal_blood_result", "iron_deficiency", "b12_folate_or_macrocytic", "chronic_disease_or_renal", "bleeding_related", "treatment_followup", "other_unclear"]),
        Q("anemia.chest_pain_rest_dyspnea_or_syncope", "Cardiopulmonary Instability with Anaemia", "boolean", "cardiopulmonary", "심한 쇠약과 함께 가만히 있어도 흉통·호흡곤란이 있거나 실신했나요?", 179, [G["safety"]], S, safety_relevant=True),
        Q("anemia.active_upper_gi_bleeding", "Active Upper Gastrointestinal Bleeding", "boolean", "upper-gi-bleed", "피를 토하거나 커피 찌꺼기 같은 구토, 검고 끈적한 타르변이 현재 있나요?", 178, [G["safety"], G["bleeding"]], S, safety_relevant=True),
        Q("anemia.active_lower_gi_bleeding_with_instability", "Active Lower Gastrointestinal Bleeding", "boolean", "lower-gi-bleed", "많은 혈변이 계속되면서 어지럼·식은땀·실신할 것 같은 느낌이 있나요?", 177, [G["safety"], G["bleeding"]], S, safety_relevant=True),
        Q("anemia.heavy_vaginal_bleeding_with_instability", "Heavy Vaginal Bleeding with Instability", "boolean", "vaginal-bleed", "질 출혈이 매우 많아 패드를 한 시간마다 갈 정도이거나 큰 혈덩이가 나오면서 어지럼·실신 느낌이 있나요?", 176, [G["safety"], G["bleeding"]], S, safety_relevant=True),
        Q("anemia.pregnancy_or_postpartum_bleeding", "Pregnancy or Postpartum Bleeding", "boolean", "pregnancy-bleed", "임신 중이거나 출산·유산 후인데 많은 출혈, 심한 복통, 어지럼·실신이 있나요?", 175, [G["safety"], G["bleeding"]], S, safety_relevant=True),
        Q("anemia.confusion_or_new_neurologic_deficit", "Neurologic Instability", "boolean", "neurologic", "새로운 혼란·의식저하, 한쪽 마비·말하기 어려움 또는 걷기 힘든 심한 균형 문제가 있나요?", 174, [G["safety"]], S, safety_relevant=True),
        Q("anemia.known_critical_or_rapidly_falling_hemoglobin", "Critical or Rapidly Falling Haemoglobin", "boolean", "critical-hb", "의료기관에서 혈색소가 매우 낮거나 빠르게 떨어져 즉시 평가가 필요하다고 안내받았나요?", 173, [G["safety"]], S, safety_relevant=True),
        Q("anemia.transfusion_reaction_pattern", "Possible Transfusion Reaction", "boolean", "transfusion-reaction", "수혈 중이거나 직후에 숨참·흉통·고열·오한·허리통증·붉거나 짙은 소변이 생겼나요?", 172, [G["safety"], G["treatment"]], S, safety_relevant=True),
        Q("anemia.hemolysis_pattern", "Possible Acute Haemolysis", "boolean", "hemolysis", "갑자기 눈·피부가 노래지고 소변이 콜라색으로 짙어지면서 심한 쇠약·복통·등통증이 있나요?", 171, [G["safety"]], S, safety_relevant=True),
        Q("anemia.unexplained_bleeding_bruising_and_fever", "Possible Marrow or Haematologic Warning", "boolean", "bleeding-fever", "원인 모를 멍·점상출혈·코피·잇몸출혈과 함께 지속 발열·반복 감염·심한 피로 중 하나가 있나요?", 170, [G["safety"]], S, safety_relevant=True),
        Q("anemia.anticoagulant_with_new_bleeding", "Bleeding while Anticoagulated", "boolean", "anticoagulant-bleed", "항응고제·항혈소판제를 복용 중이며 새로 생긴 지속 출혈이나 큰 멍, 혈뇨·혈변이 있나요?", 169, [G["safety"], G["bleeding"]], S, safety_relevant=True),
        Q("anemia.severe_infection_or_sepsis_pattern", "Severe Infection with Cytopenia Concern", "boolean", "severe-infection", "항암·면역억제 치료 중이거나 백혈구 감소를 들었는데 고열·오한·혼란·심한 처짐이 있나요?", 168, [G["safety"]], S, safety_relevant=True),

        Q("anemia.onset_duration_and_course", "Onset Duration and Course", "string", "onset", "증상 또는 검사 이상을 처음 안 시기, 지속 기간과 악화·호전·반복 경과를 알려주세요.", 155, [G["common"]], C),
        Q("anemia.current_symptom_priority", "Current Symptom Priority", "string", "priority", "현재 가장 불편하거나 의료진에게 우선 확인받고 싶은 증상은 무엇인가요?", 154, [G["common"]], C),
        Q("anemia.fatigue_weakness_and_function", "Fatigue Weakness and Function", "string", "fatigue", "피로·기력저하가 업무·학업·운동·일상활동을 얼마나 방해하나요?", 153, [G["common"]], C),
        Q("anemia.exertional_dyspnea_palpitations_and_dizziness", "Exertional Symptoms", "string", "exertional", "걷기·계단에서 숨참·두근거림·어지럼이 생기는 정도와 이전 대비 변화를 알려주세요.", 152, [G["common"]], C),
        Q("anemia.headache_cognition_and_sleep", "Headache Cognition and Sleep", "string", "cognition", "두통·집중력저하·졸림·수면 변화가 있나요?", 151, [G["common"]], C),
        Q("anemia.pallor_cold_hands_and_orthostasis", "Pallor and Orthostatic Symptoms", "string", "pallor", "창백함·손발 차가움, 일어설 때 어지럼 또는 맥박이 빨라지는 느낌이 있나요?", 150, [G["common"]], C),
        Q("anemia.pica_restless_legs_and_nail_hair_change", "Iron-deficiency-associated Symptoms", "string", "pica", "얼음·흙 등을 먹고 싶은 느낌, 하지불안, 손발톱·탈모·혀 통증 변화가 있나요?", 149, [G["common"], G["nutrition"]], D),
        Q("anemia.latest_cbc_and_reference_range", "Latest Complete Blood Count", "string", "cbc", "최근 혈색소·헤마토크릿·적혈구·MCV·MCH·RDW 수치, 검사일과 기준범위를 알려주세요.", 148, [G["common"]], R, terminology_binding={"system": SN, "code": "165397008"}, mrcm_ref=M),
        Q("anemia.cbc_trend_and_prior_baseline", "CBC Trend", "string", "cbc-trend", "이전 혈액검사와 비교해 혈색소·MCV가 어떻게 변했고 평소 기준값은 얼마였나요?", 147, [G["common"]], R),
        Q("anemia.white_cells_platelets_and_other_cytopenias", "Other Blood Cell Lines", "string", "other-lines", "백혈구·호중구·혈소판 이상도 함께 있었나요? 결과와 추세를 알려주세요.", 146, [G["common"]], R),
        Q("anemia.ferritin_iron_tsat_tibc_and_inflammation", "Iron Studies and Inflammation", "string", "iron-studies", "페리틴·혈청철·트랜스페린포화도·TIBC와 CRP 등 염증 수치, 검사일을 알려주세요.", 145, [G["common"], G["nutrition"]], R),
        Q("anemia.reticulocyte_bilirubin_ldh_haptoglobin", "Reticulocyte and Haemolysis Tests", "string", "hemolysis-tests", "망상적혈구·빌리루빈·LDH·합토글로빈 등 용혈 관련 결과가 있나요?", 144, [G["common"]], R),
        Q("anemia.b12_folate_and_related_tests", "B12 Folate and Related Tests", "string", "b12-folate-tests", "비타민 B12·엽산과 관련 추가검사 결과, 검사일을 알려주세요.", 143, [G["common"], G["nutrition"]], R),
        Q("anemia.current_medicines_and_supplements", "Current Medicines and Supplements", "string", "medicines", "현재 복용약 전체와 철분·B12·엽산·건강보조제의 제품명·용량·복용법을 알려주세요.", 142, [G["common"]], R),
        Q("anemia.nsaid_antiplatelet_anticoagulant_use", "Bleeding-risk Medicines", "string", "bleeding-medicines", "진통소염제·아스피린·항혈소판제·항응고제의 이름, 복용 빈도와 시작 시기를 알려주세요.", 141, [G["common"], G["bleeding"]], R),
        Q("anemia.past_anemia_transfusion_and_blood_disorder", "Past Anaemia and Transfusion History", "string", "past-history", "과거 빈혈 유형·치료·수혈, 혈액질환 또는 비슷한 재발 병력을 알려주세요.", 140, [G["common"]], R),
        Q("anemia.family_history_and_ancestry_context", "Family and Haemoglobinopathy Context", "string", "family", "가족의 빈혈·혈색소질환·출혈질환과 관련해 의료진에게 필요한 가족 배경을 알려주세요.", 139, [G["common"]], R),
        Q("anemia.pregnancy_postpartum_and_lactation", "Pregnancy Postpartum and Lactation", "string", "pregnancy", "현재 임신·수유 여부, 임신 주수 또는 출산·유산 시기와 출혈량을 알려주세요.", 138, [G["common"], G["bleeding"]], R),
        Q("anemia.other_detail_or_patient_priority", "Other Anaemia Detail", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달하고 싶은 내용이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("anemia.menstrual_pattern_and_heavy_bleeding", "Menstrual Blood Loss", "string", "menstrual", "해당되면 생리 주기·기간, 가장 많은 날 패드·탐폰 교체 횟수, 큰 혈덩이·샘·야간 교체 여부를 알려주세요.", 130, [G["bleeding"]], R),
        Q("anemia.gi_bleeding_and_bowel_change", "Gastrointestinal Bleeding and Bowel Change", "string", "gi-bleeding", "검은변·혈변·구토혈, 배변 습관 변화·복통·체중감소가 있나요?", 129, [G["bleeding"]], R),
        Q("anemia.urinary_nasal_dental_and_other_bleeding", "Other Bleeding Sources", "string", "other-bleeding", "혈뇨·코피·잇몸출혈·멍, 상처 후 오래가는 출혈이 있나요?", 128, [G["bleeding"]], R),
        Q("anemia.blood_donation_surgery_trauma_and_procedures", "Blood Loss Events", "string", "blood-loss-events", "헌혈 빈도와 최근 수술·외상·출산·시술로 인한 출혈을 알려주세요.", 127, [G["bleeding"]], R),

        Q("anemia.dietary_iron_b12_folate_intake", "Dietary Intake", "string", "diet", "육류·생선·달걀·콩·채소 등 철분·B12·엽산 공급 식품과 제한식·채식 여부를 알려주세요.", 130, [G["nutrition"]], D),
        Q("anemia.appetite_weight_and_food_security", "Nutrition Adequacy", "string", "nutrition", "식욕·체중 변화, 식사량과 충분한 음식을 지속적으로 구할 수 있는지 알려주세요.", 129, [G["nutrition"]], R),
        Q("anemia.malabsorption_gi_surgery_and_coeliac_context", "Malabsorption and GI Surgery", "string", "malabsorption", "셀리악병·염증성장질환·만성설사, 위·장 절제 또는 비만수술 병력이 있나요?", 128, [G["nutrition"]], R),

        Q("anemia.chronic_kidney_inflammation_cancer_and_infection", "Chronic Disease Context", "string", "chronic-disease", "만성신장질환·염증성질환·감염·암·심부전·간질환이 있나요?", 130, [G["chronic"]], R),
        Q("anemia.renal_dialysis_and_esa_history", "Renal and ESA Treatment", "string", "renal-treatment", "신장기능·투석 상태와 조혈자극제 투여 여부·일정을 알려주세요.", 129, [G["chronic"], G["treatment"]], R),
        Q("anemia.endocrine_liver_and_bone_marrow_context", "Other Systemic Causes", "string", "systemic", "갑상선·간질환, 골수질환 또는 항암·방사선 치료 병력이 있나요?", 128, [G["chronic"]], R),

        Q("anemia.oral_iron_regimen_adherence_and_tolerance", "Oral Iron Treatment", "string", "oral-iron", "경구 철분 제품·원소철 용량·복용 간격, 빠뜨린 횟수와 변비·복통·메스꺼움 등 부작용을 알려주세요.", 130, [G["treatment"]], R),
        Q("anemia.iv_iron_details_and_reaction", "Intravenous Iron Treatment", "string", "iv-iron", "정맥 철분 제품·총 투여량·날짜와 주입 반응을 알려주세요.", 129, [G["treatment"]], R),
        Q("anemia.b12_folate_treatment_details", "B12 and Folate Treatment", "string", "vitamin-treatment", "B12 주사·경구약과 엽산 용량·기간·복용완료 여부를 알려주세요.", 128, [G["treatment"]], R),
        Q("anemia.treatment_response_and_followup_labs", "Treatment Response", "string", "response", "치료 후 증상과 혈색소·페리틴이 얼마나 변했고 언제 재검할 예정인가요?", 127, [G["treatment"]], R),
        Q("anemia.fit_endoscopy_coeliac_and_gynaecologic_workup", "Cause Investigation", "string", "investigation", "FIT·위내시경·대장내시경·셀리악검사·산부인과 검사 결과와 예정 검사를 알려주세요.", 126, [G["treatment"], G["bleeding"]], R),
        Q("anemia.specialist_referral_and_safety_net", "Referral and Safety Net", "string", "referral", "혈액내과·소화기·산부인과·신장 진료 일정과 악화 시 안내받은 기준을 알려주세요.", 125, [G["treatment"]], R),
    ]
    safety = [
        ("cardiopulmonary", "anemia.chest_pain_rest_dyspnea_or_syncope", "emergency", 1000), ("upper-gi-bleed", "anemia.active_upper_gi_bleeding", "emergency", 1000),
        ("lower-gi-bleed", "anemia.active_lower_gi_bleeding_with_instability", "emergency", 1000), ("vaginal-bleed", "anemia.heavy_vaginal_bleeding_with_instability", "emergency", 1000),
        ("pregnancy-bleed", "anemia.pregnancy_or_postpartum_bleeding", "emergency", 1000), ("neurologic", "anemia.confusion_or_new_neurologic_deficit", "emergency", 1000),
        ("critical-hb", "anemia.known_critical_or_rapidly_falling_hemoglobin", "urgent", 990), ("transfusion-reaction", "anemia.transfusion_reaction_pattern", "emergency", 1000),
        ("hemolysis", "anemia.hemolysis_pattern", "urgent", 980), ("bleeding-fever", "anemia.unexplained_bleeding_bruising_and_fever", "urgent", 980),
        ("anticoagulant-bleed", "anemia.anticoagulant_with_new_bleeding", "urgent", 980), ("severe-infection", "anemia.severe_infection_or_sepsis_pattern", "emergency", 1000),
    ]
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, priority) for key, fid, level, priority in safety]
    return {"id": "knowledge.generated.anemia-concern-follow-up", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-anemia-concern-follow-up-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="anemia.primary_group", question_budget=65, source_refs=SOURCES)
    common = ["anemia.onset_duration_and_course", "anemia.current_symptom_priority", "anemia.fatigue_weakness_and_function", "anemia.exertional_dyspnea_palpitations_and_dizziness", "anemia.pallor_cold_hands_and_orthostasis", "anemia.latest_cbc_and_reference_range", "anemia.cbc_trend_and_prior_baseline", "anemia.white_cells_platelets_and_other_cytopenias", "anemia.ferritin_iron_tsat_tibc_and_inflammation", "anemia.current_medicines_and_supplements", "anemia.nsaid_antiplatelet_anticoagulant_use", "anemia.past_anemia_transfusion_and_blood_disorder", "anemia.pregnancy_postpartum_and_lactation", "anemia.other_detail_or_patient_priority"]
    cases = {"suspected_symptomatic": ["anemia.headache_cognition_and_sleep", "anemia.pica_restless_legs_and_nail_hair_change", "anemia.dietary_iron_b12_folate_intake"], "abnormal_blood_result": ["anemia.reticulocyte_bilirubin_ldh_haptoglobin", "anemia.b12_folate_and_related_tests", "anemia.family_history_and_ancestry_context"], "iron_deficiency": ["anemia.menstrual_pattern_and_heavy_bleeding", "anemia.gi_bleeding_and_bowel_change", "anemia.urinary_nasal_dental_and_other_bleeding", "anemia.blood_donation_surgery_trauma_and_procedures", "anemia.dietary_iron_b12_folate_intake", "anemia.malabsorption_gi_surgery_and_coeliac_context", "anemia.fit_endoscopy_coeliac_and_gynaecologic_workup"], "b12_folate_or_macrocytic": ["anemia.b12_folate_and_related_tests", "anemia.dietary_iron_b12_folate_intake", "anemia.malabsorption_gi_surgery_and_coeliac_context", "anemia.b12_folate_treatment_details"], "chronic_disease_or_renal": ["anemia.chronic_kidney_inflammation_cancer_and_infection", "anemia.renal_dialysis_and_esa_history", "anemia.endocrine_liver_and_bone_marrow_context"], "bleeding_related": ["anemia.menstrual_pattern_and_heavy_bleeding", "anemia.gi_bleeding_and_bowel_change", "anemia.urinary_nasal_dental_and_other_bleeding", "anemia.blood_donation_surgery_trauma_and_procedures"], "treatment_followup": ["anemia.oral_iron_regimen_adherence_and_tolerance", "anemia.iv_iron_details_and_reaction", "anemia.b12_folate_treatment_details", "anemia.treatment_response_and_followup_labs", "anemia.fit_endoscopy_coeliac_and_gynaecologic_workup", "anemia.specialist_referral_and_safety_net"], "other_unclear": ["anemia.other_detail_or_patient_priority"]}
    p["required_facts"]["routine"], p["conditional_required_facts"] = common, [{"selector_fact": "anemia.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.bsg.ida.2021", "British Society of Gastroenterology", "Guidelines for management of iron deficiency anaemia in adults", "Gut-2021-325210", "https://pmc.ncbi.nlm.nih.gov/articles/PMC8515119/", "clinical_guideline", ["History should seek overt blood loss including menstruation and epistaxis, blood donation, inadequate diet, NSAID use and previous gastrointestinal resection or bypass.", "Evaluation and treatment response require iron studies, coeliac and gastrointestinal context, medication and follow-up information; this package does not diagnose the cause."]),
        ("source.nice.ng12.anemia.2026", "NICE", "Suspected cancer: anaemia-related recommendations", "NG12; updated-2026-04-15", "https://www.nice.org.uk/guidance/ng12/chapter/Recommendations-organised-by-site-of-cancer", "nice_guidance", ["Iron-deficiency anaemia and selected age or symptom combinations require FIT or referral consideration; pallor, persistent fatigue, fever, infection, bruising, bleeding and petechiae can warrant urgent blood count assessment."]),
        ("source.who.ferritin.2020", "WHO", "Guideline on ferritin concentrations to assess iron status", "ISBN-978-92-4-000012-4", "https://www.who.int/publications/i/item/9789240000124", "public_health_guidance", ["Ferritin is an iron-store marker whose interpretation must consider infection and inflammation; raw result, reference context and inflammatory markers should be preserved."]),
        ("source.stom.anemia.20260715", "Infoclinic", "STOM anaemia terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["FHIR lookup confirmed active concepts for anaemia, iron-deficiency anaemia, macrocytic anaemia, B12- and folate-deficiency megaloblastic anaemia, blood-loss anaemia, chronic-disease anaemia and low haemoglobin.", "MRCM supports provisional semantic binding only and does not establish cause or urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-15", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-anemia-concern-follow-up-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.anemia", "generated_clinical_knowledge", "knowledge/generated/hematology/anemia-concern-follow-up/anemia-concern-follow-up.json", True), ("source.mapping.anemia", "terminology_mapping", "mappings/terminology/snomed-mrcm-anemia-concern-follow-up.json", False), ("source.external.anemia", "external_source_manifest", "sources/manifests/primary-care-anemia-concern-follow-up-research.json", False), ("source.policy.anemia", "runtime_policy", "policies/primary-care-anemia-concern-follow-up-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-anemia-concern-follow-up", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level, key = rule["when"]["fact"], rule["then"]["safety_level"], rule["id"].split("safety.")[1]
        out[f"ANEMIA-{key.upper()}.json"] = {"id": f"ANEMIA-{key.upper()}", "simulation_language": "ko", "persona": {"age": 24 + i}, "initial_statement": {"ko": "빈혈이 걱정돼서 왔어요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.iron_deficiency", "diagnosis.cancer", "diagnosis.leukaemia"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["iron_deficiency"])
    by_id, hidden = {x["fact"]["id"]: x["fact"] for x in f["entries"]}, {}
    for fid in required:
        fact = by_id[fid]
        hidden[fid] = {"value": False if fact["value_type"] == "boolean" else fact.get("allowed_values", ["unclear"])[-1] if fact["value_type"] == "coded" else 0 if fact["value_type"] == "integer" else "없음"}
    hidden["anemia.primary_group"] = {"value": "iron_deficiency"}
    declined = "anemia.dietary_iron_b12_folate_intake"
    hidden.pop(declined)
    out["ANEMIA-IRON-DEFICIENCY-DATA-ABSENT.json"] = {"id": "ANEMIA-IRON-DEFICIENCY-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 39}, "initial_statement": {"ko": "검사에서 철결핍빈혈이라고 들었어요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 65, "forbidden_assertions": ["diagnosis.gastrointestinal_cancer", "diagnosis.menorrhagia"]}, "provenance": provenance(["source.bsg.ida.2021", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Anaemia Concern or Follow-up", intents=[("intent.characterize_symptom", "Characterize Anaemia Symptoms and Results"), ("intent.screen_red_flags", "Screen Bleeding and Physiologic Instability"), ("intent.differentiate_common_causes", "Assess Blood Loss Nutrition and Chronic Disease Context"), ("intent.risk_assessment", "Assess Investigation and Treatment Response")])
    primary, research = source_docs()
    concepts = [("271737000", "Anemia (disorder)", 0), ("87522002", "Iron deficiency anemia (disorder)", 0), ("83414005", "Macrocytic anemia (disorder)", 0), ("49472006", "Megaloblastic anemia due to vitamin B12 deficiency (disorder)", 0), ("85649008", "Megaloblastic anemia due to folate deficiency (disorder)", 0), ("413532003", "Anemia due to blood loss (disorder)", 0), ("234347009", "Anemia of chronic disorder (disorder)", 0), ("165397008", "Hemoglobin below reference range (finding)", 0)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["246112005", "246454002", "363714003"], "validation": {"method": "build_time_live_fhir_lookup_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.anemia.20260715"])}
    docs = [("knowledge/base/primary-care-anemia-concern-follow-up.json", graph), ("rules/base/primary-care-anemia-concern-follow-up.json", rules), ("knowledge/generated/hematology/anemia-concern-follow-up/anemia-concern-follow-up.json", f), ("mappings/terminology/snomed-mrcm-anemia-concern-follow-up.json", mapping), ("sources/manifests/primary-care-anemia-concern-follow-up.json", primary), ("sources/manifests/primary-care-anemia-concern-follow-up-research.json", research), ("policies/primary-care-anemia-concern-follow-up-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/hematology/anemia-concern-follow-up/" + name, case)


if __name__ == "__main__": main()
