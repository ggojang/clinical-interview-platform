#!/usr/bin/env python3
"""Materialize unreviewed dyspepsia, heartburn and reflux interview knowledge."""
from profile_support import *

P = "dyspepsia-reflux"
RFE = "rfe.dyspepsia_reflux"
M = "mapping.snomed-mrcm.dyspepsia-reflux"
SN = "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = ["source.nice.cg184.dyspepsia.2019", "source.nice.ng12.upper-gi.2026", "source.stom.dyspepsia-reflux.20260715"]
G = {k: f"group.dyspepsia.{k}" for k in ("routing", "safety", "common", "reflux", "dyspepsia", "nausea", "follow-up")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("dyspepsia.primary_group", "Primary Upper Gastrointestinal Presentation", "coded", "primary-group", "가장 주된 불편은 가슴쓰림·신물 역류, 명치 통증·화끈거림, 식후 더부룩함·조기포만, 메스꺼움·트림·복부팽만, 기존 역류·궤양 추적 중 무엇에 가깝나요?", 180, [G["routing"]], C, allowed_values=["heartburn_reflux", "epigastric_pain_burning", "postprandial_fullness_early_satiety", "nausea_belching_bloating", "known_gord_or_ulcer_followup", "other_unclear"]),
        Q("dyspepsia.haematemesis_or_coffee_ground_vomit", "Haematemesis or Coffee-ground Vomit", "boolean", "haematemesis", "피를 토했거나 토사물이 검붉은색·커피 찌꺼기처럼 보이나요?", 179, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.melena_with_collapse_or_weakness", "Melena with Collapse or Weakness", "boolean", "melena-collapse", "검고 끈적한 타르변을 보면서 실신·심한 어지럼·식은땀·기운 빠짐이 있나요?", 178, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.cardiac_pattern_chest_discomfort", "Possible Cardiac Chest Discomfort", "boolean", "cardiac-pattern", "가슴 압박감이나 명치 불편이 운동 중 생기거나 숨참·식은땀·메스꺼움, 팔·턱·등으로 퍼지는 통증과 함께 있나요?", 177, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.sudden_severe_pain_or_rigidity", "Sudden Severe Upper Abdominal Pain or Rigidity", "boolean", "sudden-severe", "갑자기 시작된 매우 심한 윗배 통증이 계속되거나 배가 딱딱해지고 움직이기 힘든가요?", 176, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.food_impaction_or_airway_problem", "Food Impaction or Airway Problem", "boolean", "food-impaction", "음식이 목이나 가슴에 완전히 걸려 침도 삼키기 어렵거나 숨쉬기 힘든가요?", 175, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.persistent_vomiting_or_dehydration", "Persistent Vomiting or Dehydration", "boolean", "vomiting-dehydration", "계속 토해서 물도 못 마시거나 소변이 크게 줄고 심하게 처지나요?", 174, [G["safety"], G["nausea"]], S, safety_relevant=True),
        Q("dyspepsia.progressive_dysphagia", "Progressive Dysphagia", "boolean", "progressive-dysphagia", "음식이나 물이 삼키기 어렵고 점점 심해지거나 자주 걸리나요?", 173, [G["safety"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "40739000"}, mrcm_ref=M),
        Q("dyspepsia.unexplained_weight_loss_or_appetite_loss", "Unexplained Weight or Appetite Loss", "boolean", "weight-loss", "의도하지 않은 체중감소나 지속적인 식욕저하가 있나요?", 172, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.jaundice_or_biliary_warning", "Jaundice or Biliary Warning", "boolean", "jaundice", "눈·피부가 노래지거나 소변이 짙어지고 변이 회색·흰색에 가까워졌나요?", 171, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.upper_abdominal_mass_or_progressive_distension", "Upper Abdominal Mass or Progressive Distension", "boolean", "upper-mass", "윗배에서 덩이가 만져지거나 원인 없이 배가 계속 불러오나요?", 170, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.fever_with_severe_upper_abdominal_pain", "Fever with Severe Upper Abdominal Pain", "boolean", "fever-severe-pain", "심한 윗배 통증과 함께 발열·오한·심한 처짐이 있나요?", 169, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.known_anemia_or_bleeding_symptoms", "Known Anemia or Bleeding Symptoms", "boolean", "anemia-bleeding", "최근 빈혈 또는 낮은 혈색소를 들었거나 창백함·숨참·두근거림이 새로 생겼나요?", 168, [G["safety"]], S, safety_relevant=True),
        Q("dyspepsia.pregnancy_with_severe_persistent_vomiting", "Pregnancy with Severe Persistent Vomiting", "boolean", "pregnancy-vomiting", "임신 중이거나 가능성이 있으면서 심한 구토로 음식·물을 유지하기 어렵나요?", 167, [G["safety"], G["nausea"]], S, safety_relevant=True),

        Q("dyspepsia.onset_duration_and_frequency", "Onset Duration and Frequency", "string", "onset", "증상이 처음 시작된 시기, 지속 기간과 하루·주당 발생 횟수를 알려주세요.", 155, [G["common"]], C),
        Q("dyspepsia.course_and_episode_duration", "Course and Episode Duration", "string", "course", "한 번 생기면 얼마나 지속되고, 좋아짐·그대로·악화·반복 중 어떤 경과인가요?", 154, [G["common"]], C),
        Q("dyspepsia.exact_location_and_radiation", "Exact Location and Radiation", "string", "location", "불편한 곳이 명치·가슴뼈 뒤·오른쪽 윗배 등 어디이며 등·어깨·팔·턱으로 퍼지나요?", 153, [G["common"]], C, terminology_binding={"system": SN, "code": "79922009"}, mrcm_ref=M),
        Q("dyspepsia.pain_nrs", "Upper Abdominal Pain NRS", "integer", "pain-nrs", "[필수] 현재 통증 또는 화끈거림을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 152, [G["common"]], C),
        Q("dyspepsia.quality", "Symptom Quality", "string", "quality", "화끈거림·쓰림·쥐어짜는 느낌·압박감·묵직함·찌르는 느낌 중 어떻게 느껴지나요?", 151, [G["common"]], C),
        Q("dyspepsia.meal_relationship", "Relationship to Meals", "string", "meal-relation", "공복·식전·식후 중 언제 생기며 특정 음식이나 과식과 관련되나요?", 150, [G["common"]], C),
        Q("dyspepsia.posture_nocturnal_and_exertional_relationship", "Postural Nocturnal and Exertional Relationship", "string", "context", "눕기·숙이기·밤·수면 중 또는 걷기·계단·운동할 때 생기거나 심해지나요?", 149, [G["common"]], D),
        Q("dyspepsia.relief_and_self_treatment_response", "Relief and Self-treatment Response", "string", "relief", "음식·자세 변화·제산제·위산억제제 또는 휴식으로 좋아지나요? 복용한 제품과 효과를 알려주세요.", 148, [G["common"]], D),
        Q("dyspepsia.nausea_vomiting_characteristics", "Nausea and Vomiting Characteristics", "string", "nausea-vomiting", "메스꺼움·구토의 횟수와 양, 음식물·담즙·피 여부를 알려주세요.", 147, [G["common"], G["nausea"]], C, terminology_binding={"system": SN, "code": "422587007"}, mrcm_ref=M),
        Q("dyspepsia.bowel_stool_and_bleeding_change", "Bowel and Stool Change", "string", "stool", "검은변·혈변 외에도 설사·변비·창백한 변 등 배변 변화가 있나요?", 146, [G["common"]], R),
        Q("dyspepsia.appetite_weight_and_nutrition", "Appetite Weight and Nutrition", "string", "nutrition", "식욕과 최근 체중 변화, 먹는 양 감소 또는 영양 섭취 어려움을 알려주세요.", 145, [G["common"]], R),
        Q("dyspepsia.impact_on_sleep_work_and_intake", "Functional Impact", "string", "impact", "증상 때문에 수면·식사·일·일상활동이 얼마나 방해받나요?", 144, [G["common"]], C),
        Q("dyspepsia.trigger_foods_alcohol_coffee_and_smoking", "Food Alcohol Coffee and Smoking Triggers", "string", "triggers", "관련 있다고 느끼는 음식, 술·커피·초콜릿·기름진 음식과 흡연·전자담배 사용을 알려주세요.", 143, [G["common"]], D),
        Q("dyspepsia.current_medicines_and_dyspepsia_risk", "Medicines that May Affect Dyspepsia", "string", "medicines", "현재 복용약 전체와 진통소염제·아스피린·스테로이드·골다공증약·철분·혈압약을 알려주세요.", 142, [G["common"]], R),
        Q("dyspepsia.anticoagulant_antiplatelet_and_bleeding_history", "Bleeding Risk Medicines and History", "string", "bleeding-risk", "항응고제·항혈소판제 복용, 위장관 출혈·위궤양 병력이 있나요?", 141, [G["common"]], R),
        Q("dyspepsia.past_gastrointestinal_biliary_pancreatic_and_cardiac_history", "Relevant Past Medical History", "string", "history", "역류·식도염·위궤양, 담석·췌장질환, 심장질환과 관련 수술력을 알려주세요.", 140, [G["common"]], R),
        Q("dyspepsia.family_history_upper_gi_cancer", "Upper Gastrointestinal Cancer Family History", "string", "family-history", "가족 중 식도암·위암 등 상부위장관 암을 진단받은 사람이 있나요? 관계와 진단 연령을 알려주세요.", 139, [G["common"]], R),
        Q("dyspepsia.pregnancy_status", "Pregnancy Status", "coded", "pregnancy", "임신 중이거나 임신 가능성이 있나요?", 138, [G["common"]], R, allowed_values=["pregnant", "possibly_pregnant", "not_pregnant", "not_applicable", "unclear"]),
        Q("dyspepsia.other_detail_or_patient_priority", "Other Detail or Patient Priority", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달하고 싶은 내용이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("dyspepsia.heartburn_and_acid_regurgitation", "Heartburn and Acid Regurgitation", "string", "heartburn", "가슴뼈 뒤 화끈거림, 신물·쓴물이 목이나 입까지 올라오는 증상의 빈도와 시점을 알려주세요.", 130, [G["reflux"]], C),
        Q("dyspepsia.nocturnal_reflux_and_sleep_position", "Nocturnal Reflux and Sleep Position", "string", "nocturnal-reflux", "밤에 역류로 깨거나 기침·질식 느낌이 있나요? 취침 전 식사 시간과 머리를 높여 자는지도 알려주세요.", 129, [G["reflux"]], C),
        Q("dyspepsia.extraoesophageal_symptoms", "Extraoesophageal Symptoms", "string", "extraoesophageal", "지속되는 기침·쉰목소리·목 이물감·천식 악화 또는 치아 산 부식 지적이 있나요?", 128, [G["reflux"]], D),
        Q("dyspepsia.dysphagia_solids_liquids_and_progression", "Dysphagia Detail", "string", "dysphagia-detail", "삼키기 어렵다면 고형식·물 중 무엇부터인지, 통증·걸림 위치·진행 속도와 체중변화를 알려주세요.", 127, [G["reflux"]], R),

        Q("dyspepsia.postprandial_fullness", "Postprandial Fullness", "string", "fullness", "식후 불편할 정도의 포만감이 얼마나 자주, 얼마나 오래 지속되나요?", 130, [G["dyspepsia"]], C),
        Q("dyspepsia.early_satiety", "Early Satiety", "string", "early-satiety", "평소 양보다 적게 먹어도 빨리 배불러 식사를 끝내나요? 시작 시기와 빈도를 알려주세요.", 129, [G["dyspepsia"]], C),
        Q("dyspepsia.bloating_belching_and_gas", "Bloating Belching and Gas", "string", "bloating", "윗배 팽만·트림·가스가 식사 전후로 어떻게 나타나나요?", 128, [G["dyspepsia"], G["nausea"]], C),
        Q("dyspepsia.epigastric_burning_or_pain_pattern", "Epigastric Burning or Pain Pattern", "string", "epigastric-pattern", "명치 통증·화끈거림이 식사와 어떤 관계이며 밤에 깨우거나 등으로 퍼지나요?", 127, [G["dyspepsia"]], C),

        Q("dyspepsia.vomiting_frequency_timing_and_contents", "Vomiting Frequency Timing and Contents", "string", "vomiting-detail", "구토가 언제 얼마나 자주 생기며 먹은 음식·담즙·대변 냄새 같은 내용물 특징이 있나요?", 130, [G["nausea"]], C),
        Q("dyspepsia.hydration_urine_and_dizziness", "Hydration Urine and Dizziness", "string", "hydration", "물을 마실 수 있는지, 소변 횟수·색 변화와 일어설 때 어지럼이 있는지 알려주세요.", 129, [G["nausea"]], R),
        Q("dyspepsia.headache_neurologic_or_infectious_context", "Neurologic or Infectious Context for Nausea", "string", "nausea-context", "심한 두통·목 경직·신경 증상, 발열·설사 또는 주변의 비슷한 증상이 있나요?", 128, [G["nausea"]], D),

        Q("dyspepsia.prior_endoscopy_date_and_findings", "Prior Endoscopy Findings", "string", "endoscopy", "이전에 받은 위내시경 날짜와 식도염·궤양·바렛식도·협착·탈장·조직검사 결과를 알려주세요.", 130, [G["follow-up"]], R),
        Q("dyspepsia.h_pylori_test_type_date_and_result", "H. pylori Test History", "string", "hp-test", "헬리코박터 검사의 종류·날짜·결과와 검사 전 위산억제제 중단 여부를 알려주세요.", 129, [G["follow-up"]], R),
        Q("dyspepsia.h_pylori_treatment_adherence_and_confirmation", "H. pylori Treatment and Confirmation", "string", "hp-treatment", "제균치료 약·기간·복용완료 여부, 부작용과 치료 후 음성 확인검사 결과를 알려주세요.", 128, [G["follow-up"]], R),
        Q("dyspepsia.ppi_h2ra_name_dose_timing_adherence", "Acid Suppression Treatment Detail", "string", "acid-treatment", "PPI·H2 차단제·제산제의 제품명·용량·복용 시점·기간, 빠뜨린 횟수를 알려주세요.", 127, [G["follow-up"]], R),
        Q("dyspepsia.treatment_response_recurrence_and_side_effects", "Treatment Response Recurrence and Adverse Effects", "string", "treatment-response", "치료 후 좋아진 정도, 중단·감량 후 재발과 부작용을 알려주세요.", 126, [G["follow-up"]], R),
        Q("dyspepsia.prior_antibiotic_exposure_and_allergy", "Antibiotic Exposure and Allergy", "string", "antibiotic-history", "페니실린 알레르기와 최근 사용한 클래리스로마이신·메트로니다졸·퀴놀론 등 항생제를 알려주세요.", 125, [G["follow-up"]], R),
        Q("dyspepsia.planned_tests_referrals_and_followup", "Planned Tests Referrals and Follow-up", "string", "planned-care", "예정된 내시경·검사·전문진료와 이전 의료진이 정한 추적 시기를 알려주세요.", 124, [G["follow-up"]], R),
    ]
    rules = [
        safety_rule(P, "haematemesis", {"fact": "dyspepsia.haematemesis_or_coffee_ground_vomit", "equals": True}, "emergency", 1000),
        safety_rule(P, "melena-collapse", {"fact": "dyspepsia.melena_with_collapse_or_weakness", "equals": True}, "emergency", 1000),
        safety_rule(P, "cardiac-pattern", {"fact": "dyspepsia.cardiac_pattern_chest_discomfort", "equals": True}, "emergency", 1000),
        safety_rule(P, "sudden-severe", {"fact": "dyspepsia.sudden_severe_pain_or_rigidity", "equals": True}, "emergency", 1000),
        safety_rule(P, "food-impaction", {"fact": "dyspepsia.food_impaction_or_airway_problem", "equals": True}, "emergency", 1000),
        safety_rule(P, "vomiting-dehydration", {"fact": "dyspepsia.persistent_vomiting_or_dehydration", "equals": True}, "urgent", 980),
        safety_rule(P, "progressive-dysphagia", {"fact": "dyspepsia.progressive_dysphagia", "equals": True}, "urgent", 980),
        safety_rule(P, "weight-loss", {"fact": "dyspepsia.unexplained_weight_loss_or_appetite_loss", "equals": True}, "urgent", 970),
        safety_rule(P, "jaundice", {"fact": "dyspepsia.jaundice_or_biliary_warning", "equals": True}, "urgent", 980),
        safety_rule(P, "upper-mass", {"fact": "dyspepsia.upper_abdominal_mass_or_progressive_distension", "equals": True}, "urgent", 970),
        safety_rule(P, "fever-severe-pain", {"fact": "dyspepsia.fever_with_severe_upper_abdominal_pain", "equals": True}, "urgent", 980),
        safety_rule(P, "anemia-bleeding", {"fact": "dyspepsia.known_anemia_or_bleeding_symptoms", "equals": True}, "urgent", 960),
        safety_rule(P, "pregnancy-vomiting", {"fact": "dyspepsia.pregnancy_with_severe_persistent_vomiting", "equals": True}, "urgent", 970),
    ]
    return {"id": "knowledge.generated.dyspepsia-reflux", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-dyspepsia-reflux-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="dyspepsia.primary_group", question_budget=62, source_refs=SOURCES)
    common = ["dyspepsia.onset_duration_and_frequency", "dyspepsia.course_and_episode_duration", "dyspepsia.exact_location_and_radiation", "dyspepsia.pain_nrs", "dyspepsia.quality", "dyspepsia.meal_relationship", "dyspepsia.posture_nocturnal_and_exertional_relationship", "dyspepsia.relief_and_self_treatment_response", "dyspepsia.nausea_vomiting_characteristics", "dyspepsia.bowel_stool_and_bleeding_change", "dyspepsia.appetite_weight_and_nutrition", "dyspepsia.impact_on_sleep_work_and_intake", "dyspepsia.current_medicines_and_dyspepsia_risk", "dyspepsia.anticoagulant_antiplatelet_and_bleeding_history", "dyspepsia.past_gastrointestinal_biliary_pancreatic_and_cardiac_history", "dyspepsia.other_detail_or_patient_priority"]
    cases = {
        "heartburn_reflux": ["dyspepsia.heartburn_and_acid_regurgitation", "dyspepsia.nocturnal_reflux_and_sleep_position", "dyspepsia.extraoesophageal_symptoms", "dyspepsia.dysphagia_solids_liquids_and_progression"],
        "epigastric_pain_burning": ["dyspepsia.epigastric_burning_or_pain_pattern", "dyspepsia.h_pylori_test_type_date_and_result", "dyspepsia.prior_endoscopy_date_and_findings"],
        "postprandial_fullness_early_satiety": ["dyspepsia.postprandial_fullness", "dyspepsia.early_satiety", "dyspepsia.bloating_belching_and_gas"],
        "nausea_belching_bloating": ["dyspepsia.bloating_belching_and_gas", "dyspepsia.vomiting_frequency_timing_and_contents", "dyspepsia.hydration_urine_and_dizziness", "dyspepsia.headache_neurologic_or_infectious_context"],
        "known_gord_or_ulcer_followup": ["dyspepsia.prior_endoscopy_date_and_findings", "dyspepsia.h_pylori_test_type_date_and_result", "dyspepsia.h_pylori_treatment_adherence_and_confirmation", "dyspepsia.ppi_h2ra_name_dose_timing_adherence", "dyspepsia.treatment_response_recurrence_and_side_effects", "dyspepsia.prior_antibiotic_exposure_and_allergy", "dyspepsia.planned_tests_referrals_and_followup"],
        "other_unclear": ["dyspepsia.other_detail_or_patient_priority"],
    }
    policy["required_facts"]["routine"] = common
    policy["conditional_required_facts"] = [{"selector_fact": "dyspepsia.primary_group", "cases": cases}]
    return policy


def source_docs():
    defs = [
        ("source.nice.cg184.dyspepsia.2019", "NICE", "Gastro-oesophageal reflux disease and dyspepsia in adults", "CG184; updated-2019-10-18", "https://www.nice.org.uk/guidance/cg184/chapter/Recommendations", "nice_guidance", ["Broad dyspepsia includes recurrent epigastric pain, heartburn or acid regurgitation with or without bloating, nausea or vomiting.", "Significant acute gastrointestinal bleeding requires same-day specialist referral; medication, cardiac and biliary causes, H. pylori testing, acid suppression and treatment response are relevant history domains."]),
        ("source.nice.ng12.upper-gi.2026", "NICE", "Suspected cancer: upper gastrointestinal tract", "NG12; updated-2026-04-15", "https://www.nice.org.uk/guidance/ng12/chapter/Recommendations-organised-by-site-of-cancer", "nice_guidance", ["Dysphagia and age-risk combinations involving weight loss, upper abdominal pain, reflux or dyspepsia require referral consideration.", "This research package captures alarm features and does not diagnose cancer or autonomously determine eligibility."]),
        ("source.stom.dyspepsia-reflux.20260715", "Infoclinic", "STOM dyspepsia and reflux terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["FHIR lookup confirmed active concepts for indigestion, nonulcer dyspepsia, epigastric pain, gastroesophageal reflux disease, dysphagia and nausea.", "MRCM results support provisional semantic binding only and do not establish clinical urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-15", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-dyspepsia-reflux-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.dyspepsia-reflux", "generated_clinical_knowledge", "knowledge/generated/gastrointestinal/dyspepsia-reflux/dyspepsia-reflux.json", True), ("source.mapping.dyspepsia-reflux", "terminology_mapping", "mappings/terminology/snomed-mrcm-dyspepsia-reflux.json", False), ("source.external.dyspepsia-reflux", "external_source_manifest", "sources/manifests/primary-care-dyspepsia-reflux-research.json", False), ("source.policy.dyspepsia-reflux", "runtime_policy", "policies/primary-care-dyspepsia-reflux-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-dyspepsia-reflux", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level = rule["when"]["fact"], rule["then"]["safety_level"]
        key = rule["id"].split("safety.")[1]
        out[f"DYSPEPSIA-{key.upper()}.json"] = {"id": f"DYSPEPSIA-{key.upper()}", "simulation_language": "ko", "persona": {"age": 30 + i}, "initial_statement": {"ko": "속이 쓰리고 명치가 불편해요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.gastric_cancer", "diagnosis.peptic_ulcer", "diagnosis.gord"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["heartburn_reflux"])
    by_id = {x["fact"]["id"]: x["fact"] for x in f["entries"]}
    hidden = {}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        elif fact["value_type"] == "integer": hidden[fid] = {"value": 2}
        else: hidden[fid] = {"value": "없음"}
    hidden["dyspepsia.primary_group"] = {"value": "heartburn_reflux"}
    declined = "dyspepsia.extraoesophageal_symptoms"
    hidden.pop(declined)
    out["DYSPEPSIA-REFLUX-DATA-ABSENT.json"] = {"id": "DYSPEPSIA-REFLUX-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 41}, "initial_statement": {"ko": "식후에 신물이 올라와요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 62, "forbidden_assertions": ["diagnosis.gord", "diagnosis.cancer"]}, "provenance": provenance(["source.nice.cg184.dyspepsia.2019", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Dyspepsia, Heartburn or Reflux", intents=[("intent.characterize_symptom", "Characterize Upper Gastrointestinal Symptoms"), ("intent.screen_red_flags", "Screen Immediate and Urgent Features"), ("intent.differentiate_common_causes", "Assess Gastrointestinal and Non-gastrointestinal Context"), ("intent.risk_assessment", "Assess Investigation and Follow-up Risk")])
    primary, research = source_docs()
    concepts = [("162031009", "Indigestion (finding)", 0), ("3696007", "Nonulcer dyspepsia (disorder)", 0), ("79922009", "Epigastric pain (finding)", 0), ("235595009", "Gastroesophageal reflux disease (disorder)", 0), ("40739000", "Dysphagia (disorder)", 0), ("422587007", "Nausea (finding)", 0)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["363698007", "246112005", "246456000"], "validation": {"method": "build_time_live_fhir_lookup_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.dyspepsia-reflux.20260715"])}
    docs = [("knowledge/base/primary-care-dyspepsia-reflux.json", graph), ("rules/base/primary-care-dyspepsia-reflux.json", rules), ("knowledge/generated/gastrointestinal/dyspepsia-reflux/dyspepsia-reflux.json", f), ("mappings/terminology/snomed-mrcm-dyspepsia-reflux.json", mapping), ("sources/manifests/primary-care-dyspepsia-reflux.json", primary), ("sources/manifests/primary-care-dyspepsia-reflux-research.json", research), ("policies/primary-care-dyspepsia-reflux-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/gastrointestinal/dyspepsia-reflux/" + name, case)


if __name__ == "__main__": main()
