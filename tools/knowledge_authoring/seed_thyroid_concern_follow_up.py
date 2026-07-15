#!/usr/bin/env python3
"""Materialize unreviewed thyroid symptom and follow-up interview knowledge."""
from profile_support import *

P, RFE, M, SN = "thyroid-concern-follow-up", "rfe.thyroid_concern_follow_up", "mapping.snomed-mrcm.thyroid-concern-follow-up", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = ["source.nice.ng145.thyroid.2025", "source.nhs.hyperthyroidism-complications.2026", "source.nhs.carbimazole-safety.2026", "source.stom.thyroid.20260715"]
G = {k: f"group.thyroid.{k}" for k in ("routing", "safety", "common", "hyper", "hypo", "treatment", "neck-eye")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("thyroid.primary_group", "Primary Thyroid Presentation", "coded", "primary-group", "이번 방문은 갑상선기능 항진 의심 증상, 저하 의심 증상, 항진증 추적, 저하증 추적, 목의 갑상선 비대·결절, 수술·방사성요오드 후 추적 중 무엇에 가깝나요?", 180, [G["routing"]], C, allowed_values=["suspected_hyperthyroid", "suspected_hypothyroid", "known_hyperthyroid_followup", "known_hypothyroid_followup", "thyroid_enlargement_or_nodule", "post_treatment_followup", "other_unclear"]),
        Q("thyroid.storm_pattern", "Possible Thyroid Storm", "boolean", "storm", "고열과 매우 빠르거나 불규칙한 맥박이 있으면서 심한 초조·혼란·의식저하 중 하나가 있나요?", 179, [G["safety"], G["hyper"]], S, safety_relevant=True),
        Q("thyroid.myxoedema_pattern", "Possible Myxoedema Emergency", "boolean", "myxoedema", "체온이 비정상적으로 낮고 심하게 졸리거나 혼란스러우며 숨이 느려지거나 깨우기 어려운가요?", 178, [G["safety"], G["hypo"]], S, safety_relevant=True),
        Q("thyroid.cardiopulmonary_instability", "Cardiopulmonary Instability", "boolean", "cardiopulmonary", "두근거림과 함께 지속되는 흉통·심한 호흡곤란·실신 또는 거의 쓰러질 것 같은 증상이 있나요?", 177, [G["safety"], G["hyper"]], S, safety_relevant=True),
        Q("thyroid.airway_or_swallowing_compromise", "Airway or Swallowing Compromise", "boolean", "airway", "목의 부기 때문에 숨쉬기 매우 어렵거나 침도 삼키기 힘든가요?", 176, [G["safety"], G["neck-eye"]], S, safety_relevant=True),
        Q("thyroid.antithyroid_fever_sore_throat_or_ulcers", "Antithyroid Drug Infection Warning", "boolean", "agranulocytosis", "카비마졸·메티마졸·프로필티오우라실을 복용 중이며 발열·심한 인후통·입안 궤양·감염 같은 심한 처짐이 있나요?", 175, [G["safety"], G["treatment"]], S, safety_relevant=True),
        Q("thyroid.antithyroid_liver_warning", "Antithyroid Drug Liver Warning", "boolean", "liver-warning", "항갑상선제를 복용 중이며 황달·짙은 소변·창백한 변·전신 가려움 또는 오른쪽 윗배 통증이 있나요?", 174, [G["safety"], G["treatment"]], S, safety_relevant=True),
        Q("thyroid.sudden_vision_loss_or_severe_eye_pain", "Vision-threatening Eye Symptoms", "boolean", "vision-warning", "갑자기 시력이 떨어지거나 색이 다르게 보이고, 심한 눈 통증 또는 빠르게 심해지는 복시가 있나요?", 173, [G["safety"], G["neck-eye"]], S, safety_relevant=True),
        Q("thyroid.rapid_neck_growth_hoarseness_or_dysphagia", "Rapid Thyroid Enlargement Warning", "boolean", "rapid-neck-growth", "목의 덩이·부기가 빠르게 커지거나 새로 지속되는 쉰목소리·삼킴곤란이 있나요?", 172, [G["safety"], G["neck-eye"]], S, safety_relevant=True),
        Q("thyroid.pregnancy_or_planning_with_treatment_risk", "Pregnancy with Thyroid Treatment Risk", "boolean", "pregnancy-treatment", "임신 중·수유 중·임신 계획이 있는데 항갑상선제·방사성요오드 치료 중이거나 갑상선약 조정이 필요한 상황인가요?", 171, [G["safety"], G["treatment"]], S, safety_relevant=True),
        Q("thyroid.severe_persistent_vomiting_and_dehydration", "Severe Vomiting and Dehydration", "boolean", "vomiting-dehydration", "심한 두근거림·떨림과 함께 계속 토해서 물을 못 마시고 소변이 크게 줄었나요?", 170, [G["safety"], G["hyper"]], S, safety_relevant=True),
        Q("thyroid.severe_bradycardia_with_syncope", "Severe Bradycardia with Syncope", "boolean", "bradycardia-syncope", "맥박이 매우 느리다고 들었거나 느껴지면서 실신·의식 혼란·심한 호흡곤란이 있나요?", 169, [G["safety"], G["hypo"]], S, safety_relevant=True),
        Q("thyroid.postoperative_neck_swelling_or_tetany", "Post-thyroid Surgery Emergency", "boolean", "postoperative", "최근 갑상선 수술 후 목이 빠르게 붓거나 숨쉬기 어렵고, 입 주위·손발 저림 또는 손이 심하게 오그라드나요?", 168, [G["safety"], G["treatment"]], S, safety_relevant=True),

        Q("thyroid.onset_duration_and_course", "Onset Duration and Course", "string", "onset", "증상이나 검사 이상을 처음 안 시기, 지속 기간과 좋아짐·악화·반복 경과를 알려주세요.", 155, [G["common"]], C),
        Q("thyroid.diagnosis_and_cause", "Thyroid Diagnosis and Cause", "string", "diagnosis", "진단받은 갑상선 질환과 원인(그레이브스병·하시모토갑상선염·결절·갑상선염 등), 진단 시기를 알려주세요.", 154, [G["common"]], R),
        Q("thyroid.current_symptom_priority", "Current Symptom Priority", "string", "priority", "현재 가장 불편하거나 의료진에게 우선 확인받고 싶은 증상은 무엇인가요?", 153, [G["common"]], C),
        Q("thyroid.weight_and_appetite_change", "Weight and Appetite Change", "string", "weight", "최근 체중과 식욕 변화의 양·기간, 의도한 변화인지 알려주세요.", 152, [G["common"]], C),
        Q("thyroid.heart_rate_rhythm_and_blood_pressure", "Heart Rate Rhythm and Blood Pressure", "string", "vitals", "최근 맥박수·규칙성·혈압 측정값과 측정 시각을 알려주세요.", 151, [G["common"]], R),
        Q("thyroid.temperature_heat_or_cold_intolerance", "Temperature Intolerance", "string", "temperature", "더위를 못 참음·땀이 많음 또는 추위를 심하게 탐·체온 저하가 있나요?", 150, [G["common"]], C),
        Q("thyroid.energy_sleep_and_function", "Energy Sleep and Function", "string", "function", "피로·기력·잠·업무·학업·일상 기능이 어떻게 달라졌나요?", 149, [G["common"]], C),
        Q("thyroid.bowel_habit_change", "Bowel Habit Change", "string", "bowel", "배변 횟수 증가·설사 또는 변비가 새로 생겼나요?", 148, [G["common"]], C),
        Q("thyroid.menstrual_fertility_and_sexual_change", "Menstrual Fertility and Sexual Change", "string", "reproductive", "해당되면 생리 주기·양, 임신 가능성·임신 계획·난임 또는 성기능 변화를 알려주세요.", 147, [G["common"]], R),
        Q("thyroid.neck_or_eye_pain_present", "Thyroid-related Pain Present", "boolean", "pain-present", "목 앞쪽이나 눈 주위에 현재 통증이 있나요?", 146, [G["common"], G["neck-eye"]], C),
        Q("thyroid.pain_nrs", "Thyroid-related Pain NRS", "integer", "pain-nrs", "[필수] 현재 목 또는 눈 통증을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 145, [G["common"], G["neck-eye"]], C),
        Q("thyroid.current_medicines_dose_and_schedule", "Current Thyroid Medicines", "string", "medicines", "갑상선약과 관련 약의 이름·용량·복용 횟수·복용 시간, 최근 변경일을 알려주세요.", 144, [G["common"], G["treatment"]], R),
        Q("thyroid.adherence_and_missed_doses", "Adherence and Missed Doses", "string", "adherence", "최근 빠뜨리거나 임의로 중단·증량한 횟수와 이유를 알려주세요.", 143, [G["common"], G["treatment"]], R),
        Q("thyroid.medicine_timing_interactions_and_biotin", "Medicine Timing Interactions and Biotin", "string", "interactions", "레보티록신 복용과 음식·철분·칼슘·제산제 간격, 비오틴 보충제와 다른 약·건강식품을 알려주세요.", 142, [G["common"], G["treatment"]], R),
        Q("thyroid.latest_tsh_ft4_ft3_results", "Latest Thyroid Function Tests", "string", "latest-labs", "최근 TSH·유리 T4·유리 T3 결과, 검사일과 검사실 기준범위를 알려주세요.", 141, [G["common"], G["treatment"]], R),
        Q("thyroid.test_trend_and_treatment_relation", "Thyroid Test Trend", "string", "lab-trend", "이전 검사와 비교한 추세, 약 변경 후 검사까지의 간격과 당시 증상을 알려주세요.", 140, [G["common"], G["treatment"]], R),
        Q("thyroid.antibody_imaging_and_pathology_results", "Antibody Imaging and Pathology", "string", "tests", "TPOAb·TRAb 등 항체, 초음파·핵의학검사·세침검사 결과와 날짜를 알려주세요.", 139, [G["common"], G["neck-eye"]], R),
        Q("thyroid.prior_treatments_and_procedures", "Prior Thyroid Treatments", "string", "prior-treatment", "과거 항갑상선제·방사성요오드·수술과 치료 시기·결과·합병증을 알려주세요.", 138, [G["common"], G["treatment"]], R),
        Q("thyroid.autoimmune_pituitary_cardiac_and_bone_history", "Relevant Comorbidity", "string", "comorbidity", "다른 자가면역질환, 뇌하수체·심장·골다공증·간질환 병력을 알려주세요.", 137, [G["common"]], R),
        Q("thyroid.family_history", "Thyroid Family History", "string", "family", "가족의 갑상선기능 이상·갑상선암·자가면역질환 병력을 알려주세요.", 136, [G["common"]], R),
        Q("thyroid.smoking_vaping_and_iodine_exposure", "Smoking and Iodine Exposure", "string", "exposure", "흡연·전자담배와 최근 조영제 검사, 요오드 함유 약·보충제·해조류 과다섭취를 알려주세요.", 135, [G["common"]], D),
        Q("thyroid.other_detail_or_patient_priority", "Other Thyroid Detail", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달하고 싶은 내용이나 걱정을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("thyroid.hyper_palpitations_tremor_and_anxiety", "Hyperthyroid Symptom Cluster", "string", "hyper-cluster", "두근거림·손떨림·초조·불안·과민함의 빈도와 심한 정도를 알려주세요.", 130, [G["hyper"]], C),
        Q("thyroid.hyper_muscle_weakness_and_exercise_tolerance", "Hyperthyroid Weakness", "string", "hyper-weakness", "허벅지·어깨 근력 저하, 계단·운동 능력 감소가 있나요?", 129, [G["hyper"]], C),
        Q("thyroid.hyper_skin_hair_and_nail_change", "Hyperthyroid Skin Hair Nail Change", "string", "hyper-skin", "피부가 덥고 축축함, 탈모·가려움·손발톱 변화가 있나요?", 128, [G["hyper"]], C),
        Q("thyroid.hyper_episode_triggers", "Thyrotoxicosis Triggers", "string", "hyper-triggers", "최근 감염·수술·출산·갑상선 외상·약 중단 또는 요오드 노출 뒤 증상이 악화됐나요?", 127, [G["hyper"]], R),

        Q("thyroid.hypo_cognitive_mood_and_slowness", "Hypothyroid Cognitive and Mood Change", "string", "hypo-cognition", "생각·말·움직임이 느려짐, 집중·기억 저하 또는 우울감이 있나요?", 130, [G["hypo"]], C),
        Q("thyroid.hypo_skin_hair_swelling_and_voice", "Hypothyroid Physical Change", "string", "hypo-physical", "피부 건조·탈모·얼굴이나 몸의 부기·쉰목소리가 있나요?", 129, [G["hypo"]], C),
        Q("thyroid.hypo_muscle_joint_and_cramp", "Hypothyroid Musculoskeletal Symptoms", "string", "hypo-muscle", "근육통·관절통·쥐·근력저하가 있나요?", 128, [G["hypo"]], C),
        Q("thyroid.hypo_snoring_breathing_and_daytime_sleepiness", "Hypothyroid Breathing and Sleep", "string", "hypo-sleep", "코골이·수면 중 호흡 문제·낮의 심한 졸림이 새로 생기거나 악화됐나요?", 127, [G["hypo"]], R),

        Q("thyroid.neck_size_site_growth_and_laterality", "Thyroid Enlargement Detail", "string", "neck-detail", "목 앞 부기·결절의 정확한 위치, 좌우, 크기와 성장 속도를 알려주세요.", 130, [G["neck-eye"]], C, terminology_binding={"system": SN, "code": "237495005"}, mrcm_ref=M),
        Q("thyroid.compressive_neck_symptoms", "Compressive Neck Symptoms", "string", "compression", "숨참·누울 때 압박감·삼킴곤란·기침·쉰목소리가 있나요?", 129, [G["neck-eye"]], R),
        Q("thyroid.eye_dryness_redness_bulging_and_diplopia", "Thyroid Eye Symptoms", "string", "eye-detail", "눈 건조·모래 낀 느낌·충혈·눈부심·돌출·눈꺼풀 변화·복시가 있나요?", 128, [G["neck-eye"]], R),
        Q("thyroid.eye_symptom_laterality_and_progression", "Thyroid Eye Laterality and Progression", "string", "eye-course", "눈 증상이 왼쪽·오른쪽·양쪽 중 어디이며 얼마나 빠르게 변했나요?", 127, [G["neck-eye"]], R),

        Q("thyroid.treatment_side_effects", "Thyroid Treatment Side Effects", "string", "side-effects", "발진·가려움·멍·출혈·감염·복통·황달 등 치료 후 생긴 증상을 알려주세요.", 130, [G["treatment"]], R),
        Q("thyroid.levothyroxine_response_and_overtreatment", "Levothyroxine Response", "string", "lt4-response", "레보티록신 복용 후 증상 변화와 두근거림·떨림·불면 같은 과치료 의심 증상이 있나요?", 129, [G["treatment"]], R),
        Q("thyroid.antithyroid_response_and_hypothyroid_shift", "Antithyroid Treatment Response", "string", "atd-response", "항갑상선제 후 증상 변화와 추위·피로·변비·체중증가 같은 저하 증상이 생겼나요?", 128, [G["treatment"]], R),
        Q("thyroid.followup_plan_and_specialist", "Follow-up Plan", "string", "followup-plan", "다음 혈액검사·초음파·내분비·안과 진료 일정과 의료진이 준 조정 기준을 알려주세요.", 127, [G["treatment"]], R),
    ]
    safety = [
        ("storm", "thyroid.storm_pattern", "emergency", 1000), ("myxoedema", "thyroid.myxoedema_pattern", "emergency", 1000),
        ("cardiopulmonary", "thyroid.cardiopulmonary_instability", "emergency", 1000), ("airway", "thyroid.airway_or_swallowing_compromise", "emergency", 1000),
        ("agranulocytosis", "thyroid.antithyroid_fever_sore_throat_or_ulcers", "urgent", 990), ("liver-warning", "thyroid.antithyroid_liver_warning", "urgent", 980),
        ("vision-warning", "thyroid.sudden_vision_loss_or_severe_eye_pain", "urgent", 990), ("rapid-neck-growth", "thyroid.rapid_neck_growth_hoarseness_or_dysphagia", "urgent", 980),
        ("pregnancy-treatment", "thyroid.pregnancy_or_planning_with_treatment_risk", "urgent", 970), ("vomiting-dehydration", "thyroid.severe_persistent_vomiting_and_dehydration", "urgent", 980),
        ("bradycardia-syncope", "thyroid.severe_bradycardia_with_syncope", "emergency", 1000), ("postoperative", "thyroid.postoperative_neck_swelling_or_tetany", "emergency", 1000),
    ]
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, priority) for key, fid, level, priority in safety]
    return {"id": "knowledge.generated.thyroid-concern-follow-up", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-thyroid-concern-follow-up-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="thyroid.primary_group", question_budget=65, source_refs=SOURCES)
    common = ["thyroid.onset_duration_and_course", "thyroid.diagnosis_and_cause", "thyroid.current_symptom_priority", "thyroid.weight_and_appetite_change", "thyroid.heart_rate_rhythm_and_blood_pressure", "thyroid.temperature_heat_or_cold_intolerance", "thyroid.energy_sleep_and_function", "thyroid.bowel_habit_change", "thyroid.menstrual_fertility_and_sexual_change", "thyroid.neck_or_eye_pain_present", "thyroid.current_medicines_dose_and_schedule", "thyroid.adherence_and_missed_doses", "thyroid.medicine_timing_interactions_and_biotin", "thyroid.latest_tsh_ft4_ft3_results", "thyroid.test_trend_and_treatment_relation", "thyroid.prior_treatments_and_procedures", "thyroid.other_detail_or_patient_priority"]
    cases = {
        "suspected_hyperthyroid": ["thyroid.hyper_palpitations_tremor_and_anxiety", "thyroid.hyper_muscle_weakness_and_exercise_tolerance", "thyroid.hyper_skin_hair_and_nail_change", "thyroid.hyper_episode_triggers"],
        "suspected_hypothyroid": ["thyroid.hypo_cognitive_mood_and_slowness", "thyroid.hypo_skin_hair_swelling_and_voice", "thyroid.hypo_muscle_joint_and_cramp", "thyroid.hypo_snoring_breathing_and_daytime_sleepiness"],
        "known_hyperthyroid_followup": ["thyroid.hyper_palpitations_tremor_and_anxiety", "thyroid.antibody_imaging_and_pathology_results", "thyroid.treatment_side_effects", "thyroid.antithyroid_response_and_hypothyroid_shift", "thyroid.followup_plan_and_specialist"],
        "known_hypothyroid_followup": ["thyroid.hypo_cognitive_mood_and_slowness", "thyroid.levothyroxine_response_and_overtreatment", "thyroid.followup_plan_and_specialist"],
        "thyroid_enlargement_or_nodule": ["thyroid.neck_size_site_growth_and_laterality", "thyroid.compressive_neck_symptoms", "thyroid.antibody_imaging_and_pathology_results", "thyroid.eye_dryness_redness_bulging_and_diplopia"],
        "post_treatment_followup": ["thyroid.treatment_side_effects", "thyroid.levothyroxine_response_and_overtreatment", "thyroid.antithyroid_response_and_hypothyroid_shift", "thyroid.followup_plan_and_specialist"],
        "other_unclear": ["thyroid.other_detail_or_patient_priority"],
    }
    policy["required_facts"]["routine"] = common
    policy["conditional_required_facts"] = [{"selector_fact": "thyroid.primary_group", "cases": cases}]
    return policy


def source_docs():
    defs = [
        ("source.nice.ng145.thyroid.2025", "NICE", "Thyroid disease: assessment and management", "NG145; updated-2023-10-12; reviewed-2025-10-03", "https://www.nice.org.uk/guidance/ng145/chapter/recommendations", "nice_guidance", ["Assessment should combine symptoms, thyroid function tests, medication and monitoring context; one symptom alone is not diagnostic.", "History should include biotin, pregnancy and fertility, treatment risks, thyroid enlargement compression, eye disease and test trends."]),
        ("source.nhs.hyperthyroidism-complications.2026", "NHS", "Overactive thyroid complications", "accessed-2026-07-15", "https://www.nhs.uk/conditions/overactive-thyroid-hyperthyroidism/complications/", "public_health_guidance", ["High temperature, rapid heartbeat, severe agitation or confusion and loss of consciousness may indicate thyroid storm; severe disease can involve atrial fibrillation, heart failure and vision-threatening eye disease."]),
        ("source.nhs.carbimazole-safety.2026", "NHS", "Side effects of carbimazole", "accessed-2026-07-15", "https://www.nhs.uk/medicines/carbimazole/side-effects-of-carbimazole/", "public_health_guidance", ["Fever, sore throat, mouth ulcers, severe tiredness or flu-like symptoms may indicate low white cells; jaundice or dark urine may indicate liver injury and require prompt advice."]),
        ("source.stom.thyroid.20260715", "Infoclinic", "STOM thyroid terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["FHIR lookup confirmed active concepts for hypothyroidism, hyperthyroidism, goiter, thyroid nodule, Graves disease, Hashimoto thyroiditis, thyroid disorder and thyrotoxicosis.", "MRCM supports provisional semantic binding and does not establish diagnosis or urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-15", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-thyroid-concern-follow-up-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.thyroid", "generated_clinical_knowledge", "knowledge/generated/endocrine/thyroid-concern-follow-up/thyroid-concern-follow-up.json", True), ("source.mapping.thyroid", "terminology_mapping", "mappings/terminology/snomed-mrcm-thyroid-concern-follow-up.json", False), ("source.external.thyroid", "external_source_manifest", "sources/manifests/primary-care-thyroid-concern-follow-up-research.json", False), ("source.policy.thyroid", "runtime_policy", "policies/primary-care-thyroid-concern-follow-up-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-thyroid-concern-follow-up", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level = rule["when"]["fact"], rule["then"]["safety_level"]
        key = rule["id"].split("safety.")[1]
        out[f"THYROID-{key.upper()}.json"] = {"id": f"THYROID-{key.upper()}", "simulation_language": "ko", "persona": {"age": 27 + i}, "initial_statement": {"ko": "갑상선 문제로 상담받고 싶어요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.thyroid_storm", "diagnosis.graves_disease", "diagnosis.thyroid_cancer"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["known_hypothyroid_followup"])
    by_id = {x["fact"]["id"]: x["fact"] for x in f["entries"]}
    hidden = {}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        elif fact["value_type"] == "integer": hidden[fid] = {"value": 0}
        else: hidden[fid] = {"value": "없음"}
    hidden["thyroid.primary_group"] = {"value": "known_hypothyroid_followup"}
    declined = "thyroid.medicine_timing_interactions_and_biotin"
    hidden.pop(declined)
    out["THYROID-HYPO-FOLLOWUP-DATA-ABSENT.json"] = {"id": "THYROID-HYPO-FOLLOWUP-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 46}, "initial_statement": {"ko": "갑상선 저하증 정기 진료예요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 65, "forbidden_assertions": ["diagnosis.dose_inadequate", "diagnosis.hashimoto"]}, "provenance": provenance(["source.nice.ng145.thyroid.2025", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Thyroid Concern or Follow-up", intents=[("intent.characterize_symptom", "Characterize Thyroid Symptoms"), ("intent.screen_red_flags", "Screen Thyroid and Treatment Emergencies"), ("intent.differentiate_common_causes", "Assess Hyperthyroid Hypothyroid and Structural Context"), ("intent.risk_assessment", "Assess Treatment Monitoring and Complication Risk")])
    primary, research = source_docs()
    concepts = [("40930008", "Hypothyroidism (disorder)", 0), ("34486009", "Hyperthyroidism (disorder)", 0), ("3716002", "Goiter (disorder)", 0), ("237495005", "Thyroid nodule (disorder)", 0), ("353295004", "Graves' disease (disorder)", 0), ("21983002", "Hashimoto thyroiditis (disorder)", 0), ("14304000", "Disorder of thyroid gland (disorder)", 0), ("90739004", "Thyrotoxicosis (disorder)", 0)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["363698007", "272741003", "246112005"], "laterality": {"reference_set": "723264001", "postcoordination_asserted": False, "reason": "Neck and eye laterality remain separate Facts until the selected anatomy is verified as lateralizable and MRCM-compatible."}, "validation": {"method": "build_time_live_fhir_lookup_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.thyroid.20260715"])}
    docs = [("knowledge/base/primary-care-thyroid-concern-follow-up.json", graph), ("rules/base/primary-care-thyroid-concern-follow-up.json", rules), ("knowledge/generated/endocrine/thyroid-concern-follow-up/thyroid-concern-follow-up.json", f), ("mappings/terminology/snomed-mrcm-thyroid-concern-follow-up.json", mapping), ("sources/manifests/primary-care-thyroid-concern-follow-up.json", primary), ("sources/manifests/primary-care-thyroid-concern-follow-up-research.json", research), ("policies/primary-care-thyroid-concern-follow-up-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/endocrine/thyroid-concern-follow-up/" + name, case)


if __name__ == "__main__": main()
