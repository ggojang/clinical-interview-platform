#!/usr/bin/env python3
"""Materialize a research-only swallowing-difficulty interview package."""
from profile_support import *


P, RFE = "swallowing-difficulty", "rfe.swallowing_difficulty"
M = "mapping.terminology.swallowing-difficulty"
ACQUIRED_AT = "2026-08-03T00:00:00Z"
SOURCES = [
    "source.nhs.dysphagia.20230502",
    "source.nice.ng12.dysphagia.2025",
    "source.asha.adult-dysphagia.20260803",
    "source.rcslt.eating-drinking-swallowing.2024",
    "source.stom.swallowing-difficulty.20260803",
]
G = {key: f"group.swallowing.{key}" for key in (
    "identity", "safety", "pattern", "oropharyngeal", "oesophageal",
    "nutrition", "context", "handoff",
)}
I = [
    "intent.characterize_swallowing_difficulty",
    "intent.screen_swallowing_safety",
    "intent.assess_swallowing_impact_and_context",
    "intent.prepare_swallowing_handoff",
]


def Q(fact_id, display, value_type, key, wording, score, group, intent, **kwargs):
    return entry(P, fact_id, display, value_type, key, wording, score, key,
                 [G[group]], intents=[intent], **kwargs)


def fragment():
    characterize, safety, assess, handoff = I
    entries = [
        Q("swallow.presentation", "Main Swallowing Presentation", "coded_or_string", "presentation",
          "가장 주된 불편은 삼키기 시작하기 어려움, 음식 걸림, 삼킬 때 통증, 기침·사레, 음식 역류 중 무엇인가요? 보기에 없으면 직접 입력해 주세요.", 300, "identity", characterize,
          allowed_values=["difficulty_starting", "food_sticking", "painful_swallowing", "coughing_or_choking", "regurgitation", "follow_up", "other"]),
        Q("swallow.information_source", "Swallowing Information Source", "coded", "information-source",
          "삼킴 상태를 누가 답하고 있나요?", 299, "identity", characterize,
          allowed_values=["patient", "caregiver", "patient_and_caregiver", "record", "unknown"]),
        Q("swallow.source_reliability", "Swallowing Information Reliability", "coded", "source-reliability",
          "답변은 최근 식사·음료 상황을 잘 반영하나요, 기억이 불확실하거나 다른 사람·기록과 상충하나요?", 298, "identity", characterize,
          allowed_values=["reliable", "partly_reliable", "memory_uncertain", "conflicting_sources", "unknown"]),

        Q("swallow.current_cannot_breathe_or_speak", "Current Complete Airway Obstruction", "boolean", "airway-obstruction",
          "지금 음식이나 물질이 막혀 숨을 쉬거나 말을 할 수 없나요?", 1200, "safety", safety, safety_relevant=True),
        Q("swallow.current_reduced_consciousness", "Current Reduced Consciousness", "boolean", "reduced-consciousness",
          "지금 깨우기 어렵거나 의식이 뚜렷하게 떨어져 있나요?", 1199, "safety", safety, safety_relevant=True),
        Q("swallow.current_blue_colour", "Current Blue Colour", "boolean", "blue-colour",
          "지금 입술이나 얼굴이 파랗게 보이나요?", 1198, "safety", safety, safety_relevant=True),
        Q("swallow.sudden_new_difficulty", "Sudden New Swallowing Difficulty", "boolean", "sudden-new-difficulty",
          "삼키기 어려움이 갑자기 새로 시작됐나요?", 1197, "safety", safety, safety_relevant=True),
        Q("swallow.sudden_focal_neurologic_change", "Sudden Focal Neurologic Change", "boolean", "sudden-neurologic-change",
          "같은 때 갑자기 한쪽 얼굴·팔·다리 힘이 빠지거나 말이 어눌해졌나요?", 1196, "safety", safety, safety_relevant=True),
        Q("swallow.unable_to_swallow_saliva", "Unable to Swallow Saliva", "boolean", "unable-swallow-saliva",
          "현재 침도 삼키지 못해 흘리거나 계속 뱉고 있나요?", 1195, "safety", safety, safety_relevant=True),
        Q("swallow.suspected_food_bolus", "Suspected Food Bolus", "boolean", "suspected-food-bolus",
          "음식이나 다른 물질이 목 또는 가슴에 걸린 채 내려가지 않는 느낌인가요?", 1194, "safety", safety, safety_relevant=True),
        Q("swallow.unable_to_swallow_liquids_current", "Unable to Swallow Liquids Currently", "boolean", "unable-liquids-current",
          "현재 물도 전혀 삼킬 수 없나요?", 1193, "safety", safety, safety_relevant=True),
        Q("swallow.current_severe_breathlessness_after_swallow", "Severe Breathlessness after Swallowing", "boolean", "severe-breathlessness-after-swallow",
          "삼킨 뒤 지금 말하기 어려울 정도로 심하게 숨이 차나요?", 1192, "safety", safety, safety_relevant=True),
        Q("swallow.unable_to_keep_fluids", "Unable to Maintain Fluid Intake", "boolean", "unable-maintain-fluids",
          "삼킴 문제 때문에 하루 동안 필요한 물을 거의 마시지 못했나요?", 1191, "safety", safety, safety_relevant=True),
        Q("swallow.markedly_reduced_urine", "Markedly Reduced Urine", "boolean", "markedly-reduced-urine",
          "평소보다 소변이 뚜렷하게 줄었나요?", 1190, "safety", safety, safety_relevant=True),

        Q("swallow.first_onset", "First Swallowing Difficulty Onset", "date_or_period", "first-onset",
          "삼킴 문제가 처음 시작된 때는 언제인가요?", 280, "pattern", characterize),
        Q("swallow.latest_episode", "Latest Swallowing Difficulty Episode", "date_or_period", "latest-episode",
          "가장 최근에 문제가 있었던 때는 언제인가요?", 279, "pattern", characterize),
        Q("swallow.course", "Swallowing Difficulty Course", "coded", "course",
          "처음보다 좋아짐, 비슷함, 점점 심해짐, 들쭉날쭉함 중 어디에 가깝나요?", 278, "pattern", characterize,
          allowed_values=["improving", "unchanged", "progressive", "fluctuating", "resolved", "uncertain"]),
        Q("swallow.frequency", "Swallowing Difficulty Frequency", "string", "frequency",
          "삼킬 때 불편한 빈도를 알려주세요. 예: 매 끼니, 하루 한 번, 가끔", 277, "pattern", characterize),
        Q("swallow.difficulty_initiating", "Difficulty Initiating Swallow", "boolean", "difficulty-initiating",
          "음식이나 물을 입에서 목으로 넘기기 시작하기 어렵나요?", 276, "oropharyngeal", characterize),
        Q("swallow.perceived_sticking_location", "Perceived Food Sticking Location", "coded_or_string", "sticking-location",
          "걸리는 느낌이 있다면 입안, 목, 가슴 중 어디인가요? 보기에 없으면 직접 입력해 주세요.", 275, "oesophageal", characterize,
          allowed_values=["mouth", "throat", "neck", "upper_chest", "mid_chest", "lower_chest", "uncertain", "other"]),
        Q("swallow.solid_food_difficulty_last_7_days", "Solid Food Swallowing Difficulty in Last 7 Days", "boolean", "solid-last-seven",
          "최근 7일 동안 고형식을 삼키기 어려웠나요?", 274, "pattern", characterize),
        Q("swallow.soft_food_difficulty_last_7_days", "Soft Food Swallowing Difficulty in Last 7 Days", "boolean", "soft-last-seven",
          "최근 7일 동안 부드럽거나 으깬 음식을 삼키기 어려웠나요?", 273, "pattern", characterize),
        Q("swallow.liquid_difficulty_last_7_days", "Liquid Swallowing Difficulty in Last 7 Days", "boolean", "liquid-last-seven",
          "최근 7일 동안 물 같은 액체를 삼키기 어려웠나요?", 272, "pattern", characterize),
        Q("swallow.painful_swallowing", "Painful Swallowing", "boolean", "painful-swallowing",
          "삼킬 때 통증이 있나요?", 271, "pattern", characterize),
        Q("swallow.pain_location", "Swallowing Pain Location", "string", "pain-location",
          "삼킬 때 아픈 위치를 알려주세요.", 270, "pattern", characterize),
        Q("swallow.pain_nrs", "Swallowing Pain Numeric Rating", "integer", "pain-nrs",
          "삼킬 때 통증이 있다면 0점부터 10점 중 몇 점인가요?", 269, "pattern", characterize,
          unit="{score}", minimum=0, maximum=10,
          terminology_binding={"system": "http://loinc.org", "code": "72514-3", "display": "Pain severity - 0-10 verbal numeric rating [Score] - Reported", "version": "2.82", "relation": "equivalent"}),

        Q("swallow.chewing_difficulty", "Chewing Difficulty", "boolean", "chewing-difficulty",
          "씹거나 음식 덩어리를 만들기 어렵나요?", 250, "oropharyngeal", assess),
        Q("swallow.oral_residue_or_leakage", "Oral Residue or Leakage", "boolean", "oral-residue-leakage",
          "삼킨 뒤 음식이 입안에 남거나 입 밖으로 새나요?", 249, "oropharyngeal", assess),
        Q("swallow.nasal_regurgitation", "Nasal Regurgitation", "boolean", "nasal-regurgitation",
          "삼킬 때 음식이나 물이 코로 나오나요?", 248, "oropharyngeal", assess),
        Q("swallow.cough_during_or_after", "Cough during or after Swallow", "boolean", "cough-during-after",
          "먹거나 마시는 중 또는 직후에 기침하나요?", 247, "oropharyngeal", assess),
        Q("swallow.choking_episode", "Choking Episode", "boolean", "choking-episode",
          "먹거나 마실 때 사레가 들리거나 숨길이 막힌 적이 있나요?", 246, "oropharyngeal", assess),
        Q("swallow.wet_voice_after", "Wet Voice after Swallow", "boolean", "wet-voice-after",
          "먹거나 마신 뒤 목소리가 젖은 듯 가래 끓는 소리로 변하나요?", 245, "oropharyngeal", assess),
        Q("swallow.breathing_change_after", "Breathing Change after Swallow", "boolean", "breathing-change-after",
          "먹거나 마신 뒤 숨이 차거나 호흡 소리가 달라지나요?", 244, "oropharyngeal", assess),
        Q("swallow.regurgitation", "Regurgitation after Swallow", "boolean", "regurgitation",
          "삼킨 음식이나 물이 다시 입이나 코로 올라오나요?", 243, "oesophageal", assess),
        Q("swallow.reflux_or_heartburn", "Reflux or Heartburn", "boolean", "reflux-heartburn",
          "속쓰림이나 신물이 올라오는 증상이 함께 있나요?", 242, "oesophageal", assess),
        Q("swallow.meal_related_chest_discomfort", "Meal-related Chest Discomfort", "boolean", "meal-chest-discomfort",
          "삼키거나 식사할 때 가슴 불편감이 생기나요?", 241, "oesophageal", assess),

        Q("swallow.meal_duration", "Meal Duration", "string", "meal-duration",
          "한 끼를 먹는 데 보통 얼마나 걸리며 예전보다 길어졌나요?", 225, "nutrition", assess),
        Q("swallow.fatigue_during_meal", "Fatigue during Meal", "boolean", "meal-fatigue",
          "식사 도중 지쳐서 쉬거나 끝내지 못하나요?", 224, "nutrition", assess),
        Q("swallow.food_or_drink_avoidance", "Food or Drink Avoidance", "string", "food-avoidance",
          "삼키기 어려워 피하는 음식·음료나 바꾼 질감이 있나요?", 223, "nutrition", assess),
        Q("swallow.intake_reduction", "Food Intake Reduction", "coded", "intake-reduction",
          "평소보다 먹는 양은 어떻게 달라졌나요?", 222, "nutrition", assess,
          allowed_values=["none", "slightly_reduced", "markedly_reduced", "almost_none", "uncertain"]),
        Q("swallow.unintentional_weight_change", "Unintentional Weight Change", "string", "weight-change",
          "의도하지 않은 체중 변화가 있다면 양과 기간을 알려주세요.", 221, "nutrition", assess),
        Q("swallow.recurrent_chest_infection", "Recurrent Chest Infection", "boolean", "recurrent-chest-infection",
          "삼킴 문제가 생긴 뒤 흉부 감염이나 폐렴을 반복해서 진료받았나요?", 220, "nutrition", assess),
        Q("swallow.daily_function_and_social_impact", "Daily and Social Impact", "string", "function-social-impact",
          "삼킴 문제로 약 복용, 외식, 직장·학교, 수면 또는 사람들과 식사하는 데 어떤 영향이 있나요?", 219, "nutrition", assess),

        Q("swallow.neurologic_history", "Neurologic History", "string", "neurologic-history",
          "뇌졸중, 신경계 질환, 근력 저하 등 삼킴에 영향을 줄 수 있는 병력이 있나요?", 205, "context", assess),
        Q("swallow.head_neck_surgery_or_radiation", "Head or Neck Surgery or Radiation", "string", "head-neck-treatment",
          "머리·목 수술, 방사선치료, 기관삽관 또는 기관절개 이력이 있나요?", 204, "context", assess),
        Q("swallow.oesophageal_or_reflux_history", "Oesophageal or Reflux History", "string", "oesophageal-history",
          "식도 질환, 역류, 협착 또는 관련 시술 이력이 있나요?", 203, "context", assess),
        Q("swallow.oral_dental_context", "Oral and Dental Context", "string", "oral-dental-context",
          "치아, 틀니, 입안 통증·건조 또는 씹기 문제가 있나요?", 202, "context", assess),
        Q("swallow.respiratory_history", "Respiratory History", "string", "respiratory-history",
          "폐질환이나 반복되는 흉부 감염 이력이 있나요?", 201, "context", assess),
        Q("swallow.cognition_frailty_posture", "Cognition Frailty and Posture Context", "string", "cognition-frailty-posture",
          "주의력·인지, 전반적 쇠약, 식사 자세 때문에 삼키기 어려운 점이 있나요?", 200, "context", assess),
        Q("swallow.feeding_tube_or_airway_device", "Feeding Tube or Airway Device", "string", "feeding-airway-device",
          "비위관·위루관 같은 영양관이나 기관절개관을 사용하나요?", 199, "context", assess),
        Q("swallow.current_medicines", "Current Medicines", "string", "current-medicines",
          "현재 복용하는 처방약, 일반약, 건강기능식품과 삼키기 어려운 제형이 있나요?", 198, "context", assess),
        Q("swallow.allergies", "Known Allergies", "string", "allergies",
          "알고 있는 약물 또는 물질 알레르기가 있나요?", 197, "context", assess),
        Q("swallow.previous_assessment_or_test", "Previous Swallowing Assessment or Test", "string", "previous-assessment",
          "이 문제로 진찰, 내시경, 조영검사, 연하검사 등을 받은 적과 결과를 알려주세요.", 196, "context", assess),
        Q("swallow.previous_strategy_or_treatment", "Previous Strategy or Treatment", "string", "previous-strategy",
          "전에 안내받은 식이 질감, 자세, 연하치료 또는 치료가 있다면 알려주세요.", 195, "context", assess),
        Q("swallow.previous_response", "Response to Previous Strategy", "string", "previous-response",
          "이전 안내나 치료 후 좋아진 점과 남은 문제를 알려주세요.", 194, "context", assess),
        Q("swallow.feeding_assistance", "Feeding Assistance", "string", "feeding-assistance",
          "식사 준비, 자세 잡기, 먹기 또는 약 복용에 다른 사람의 도움이 필요한가요?", 193, "context", assess),
        Q("swallow.accessibility_need", "Accessibility Need", "string", "accessibility-need",
          "청각·시각·인지·의사소통·이동 측면에서 문진이나 진료에 필요한 지원이 있나요?", 192, "context", assess),

        Q("swallow.patient_concern", "Patient Swallowing Concern", "string", "patient-concern",
          "삼킴 문제와 관련해 가장 걱정되는 점은 무엇인가요?", 100, "handoff", handoff),
        Q("swallow.expected_help", "Expected Help", "string", "expected-help",
          "이번 진료에서 의료진에게 가장 받고 싶은 도움은 무엇인가요?", 99, "handoff", handoff),
        Q("swallow.additional_comment", "Additional Comment", "string", "additional-comment",
          "질문에 없지만 의료진에게 추가로 전달할 내용이 있나요?", 90, "handoff", handoff),
    ]
    rules = [
        safety_rule(P, "complete-airway-obstruction", {"fact": "swallow.current_cannot_breathe_or_speak", "equals": True}, "emergency", 1300),
        safety_rule(P, "reduced-consciousness", {"fact": "swallow.current_reduced_consciousness", "equals": True}, "emergency", 1299),
        safety_rule(P, "blue-colour", {"fact": "swallow.current_blue_colour", "equals": True}, "emergency", 1298),
        safety_rule(P, "sudden-neurologic-change", {"all": [{"fact": "swallow.sudden_new_difficulty", "equals": True}, {"fact": "swallow.sudden_focal_neurologic_change", "equals": True}]}, "emergency", 1297),
        safety_rule(P, "unable-swallow-saliva", {"fact": "swallow.unable_to_swallow_saliva", "equals": True}, "urgent", 1296),
        safety_rule(P, "food-bolus-unable-liquids", {"all": [{"fact": "swallow.suspected_food_bolus", "equals": True}, {"fact": "swallow.unable_to_swallow_liquids_current", "equals": True}]}, "urgent", 1295),
        safety_rule(P, "severe-breathlessness-after-swallow", {"fact": "swallow.current_severe_breathlessness_after_swallow", "equals": True}, "emergency", 1294),
        safety_rule(P, "fluid-intake-dehydration", {"all": [{"fact": "swallow.unable_to_keep_fluids", "equals": True}, {"fact": "swallow.markedly_reduced_urine", "equals": True}]}, "urgent", 1293),
    ]
    return {
        "id": "knowledge.generated.swallowing-difficulty", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-swallowing-difficulty-research",
        "default_refresh": {**default_refresh(), "last_assessed_at": "2026-08-03", "next_monitor_at": "2026-08-04", "next_full_review_at": "2027-01-30"},
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(document):
    safety = [item["fact"]["id"] for item in document["entries"] if item["fact"].get("safety_relevant")]
    core = [
        "swallow.presentation", "swallow.information_source", "swallow.source_reliability",
        "swallow.first_onset", "swallow.latest_episode", "swallow.course", "swallow.frequency",
        "swallow.difficulty_initiating", "swallow.perceived_sticking_location",
        "swallow.solid_food_difficulty_last_7_days", "swallow.soft_food_difficulty_last_7_days",
        "swallow.liquid_difficulty_last_7_days", "swallow.painful_swallowing",
        "swallow.cough_during_or_after", "swallow.choking_episode", "swallow.wet_voice_after",
        "swallow.breathing_change_after", "swallow.regurgitation", "swallow.intake_reduction",
        "swallow.unintentional_weight_change", "swallow.recurrent_chest_infection",
        "swallow.daily_function_and_social_impact", "swallow.neurologic_history",
        "swallow.head_neck_surgery_or_radiation", "swallow.oesophageal_or_reflux_history",
        "swallow.current_medicines", "swallow.allergies", "swallow.previous_assessment_or_test",
        "swallow.previous_strategy_or_treatment", "swallow.previous_response",
        "swallow.feeding_assistance", "swallow.accessibility_need", "swallow.patient_concern",
        "swallow.expected_help", "swallow.additional_comment",
    ]
    return {
        "id": "policy.primary-care-swallowing-difficulty-completion", "version": VERSION,
        "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": safety + core, "routine": []},
        "conditional_required_facts": [
            {"when": {"fact": "swallow.painful_swallowing", "equals": True}, "required_facts": ["swallow.pain_location", "swallow.pain_nrs"]},
            {"when": {"fact": "swallow.difficulty_initiating", "equals": True}, "required_facts": ["swallow.chewing_difficulty", "swallow.oral_residue_or_leakage", "swallow.nasal_regurgitation"]},
            {"when": {"fact": "swallow.intake_reduction", "in": ["slightly_reduced", "markedly_reduced", "almost_none"]}, "required_facts": ["swallow.meal_duration", "swallow.fatigue_during_meal", "swallow.food_or_drink_avoidance"]},
        ],
        "clarification_facts_by_rule": {}, "question_budget": {"routine": 64, "clarify": 10},
        "provenance": provenance(SOURCES),
    }


def source_documents():
    artifacts = [
        {"id": SOURCES[0], "kind": "official_public_health_guidance_metadata", "publisher": "NHS", "title": "Dysphagia (swallowing problems)", "version": "reviewed-2023-05-02", "url": "https://www.nhs.uk/symptoms/swallowing-problems-dysphagia/", "language": "en", "digest": "official_symptoms_choking_sticking_wet_voice_weight_dehydration_recurrent_infection_and_urgent_advice_verified_2026-08-03", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[1], "kind": "official_clinical_guideline_metadata", "publisher": "NICE", "title": "Suspected cancer: recognition and referral - dysphagia recommendations", "version": "NG12-amended-2025", "url": "https://www.nice.org.uk/guidance/ng12/chapter/recommendations-organised-by-site-of-cancer", "language": "en", "digest": "official_dysphagia_time_sensitive_referral_signal_verified_2026-08-03_without_korean_pathway_projection", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "nice_guidance", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[2], "kind": "professional_clinical_guidance_metadata", "publisher": "American Speech-Language-Hearing Association", "title": "Adult Dysphagia Practice Portal", "version": "retrieved-2026-08-03", "url": "https://www.asha.org/Practice-Portal/Clinical-Topics/Adult-Dysphagia/", "language": "en", "digest": "professional_oral_pharyngeal_oesophageal_symptoms_intake_airway_function_context_and_assessment_boundaries_verified_2026-08-03", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "clinical_guideline", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[3], "kind": "professional_clinical_guidance_metadata", "publisher": "Royal College of Speech and Language Therapists", "title": "Eating, drinking and swallowing guidance", "version": "updated-guidance-2024", "url": "https://www.rcslt.org/members/clinical-guidance/eating-drinking-and-swallowing/eating-drinking-and-swallowing-guidance/", "language": "en", "digest": "professional_person_context_environment_and_multidisciplinary_guidance_verified_2026-08-03", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "clinical_guideline", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[4], "kind": "terminology_service_verification", "publisher": "STOM", "title": "Swallowing difficulty terminology verification", "version": "LOINC-2.82_SNOMEDCT-observed-20260801", "url": "http://localhost:8088/fhir", "language": "en", "digest": "loinc_70367-8_70368-6_70369-4_54860-2_54861-0_72514-3_and_snomed_40739000_verified", "license_status": "licensed_lookup_metadata_only", "complete": False, "monitor_profile": "terminology_server", "last_monitored_at": "2026-08-03", "monitor_result": "verified_active_baseline_change_observed"},
    ]
    research = {"id": "source-manifest.primary-care-swallowing-difficulty-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance(SOURCES)}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.swallowing-difficulty", "generated_clinical_knowledge", "knowledge/generated/gastrointestinal/swallowing-difficulty/swallowing-difficulty.json", True),
        ("source.mapping.swallowing-difficulty", "terminology_mapping", "mappings/terminology/snomed-mrcm-swallowing-difficulty.json", False),
        ("source.external.swallowing-difficulty", "external_source_manifest", "sources/manifests/primary-care-swallowing-difficulty-research.json", False),
        ("source.policy.swallowing-difficulty", "runtime_policy", "policies/primary-care-swallowing-difficulty-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-swallowing-difficulty", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def routine_state():
    return {
        "swallow.presentation": {"value": "food_sticking"}, "swallow.information_source": {"value": "patient"},
        "swallow.source_reliability": {"value": "reliable"}, "swallow.current_cannot_breathe_or_speak": {"value": False},
        "swallow.current_reduced_consciousness": {"value": False}, "swallow.current_blue_colour": {"value": False},
        "swallow.sudden_new_difficulty": {"value": False}, "swallow.sudden_focal_neurologic_change": {"value": False},
        "swallow.unable_to_swallow_saliva": {"value": False}, "swallow.suspected_food_bolus": {"value": False},
        "swallow.unable_to_swallow_liquids_current": {"value": False}, "swallow.current_severe_breathlessness_after_swallow": {"value": False},
        "swallow.unable_to_keep_fluids": {"value": False}, "swallow.markedly_reduced_urine": {"value": False},
        "swallow.first_onset": {"value": "3주 전"}, "swallow.latest_episode": {"value": "오늘 아침"},
        "swallow.course": {"value": "unchanged"}, "swallow.frequency": {"value": "하루 한두 번"},
        "swallow.difficulty_initiating": {"value": False}, "swallow.perceived_sticking_location": {"value": "mid_chest"},
        "swallow.solid_food_difficulty_last_7_days": {"value": True}, "swallow.soft_food_difficulty_last_7_days": {"value": False},
        "swallow.liquid_difficulty_last_7_days": {"value": False}, "swallow.painful_swallowing": {"value": False},
        "swallow.pain_location": {"value": "not_applicable"}, "swallow.pain_nrs": {"value": 0},
        "swallow.chewing_difficulty": {"value": False}, "swallow.oral_residue_or_leakage": {"value": False},
        "swallow.nasal_regurgitation": {"value": False}, "swallow.cough_during_or_after": {"value": False},
        "swallow.choking_episode": {"value": False}, "swallow.wet_voice_after": {"value": False},
        "swallow.breathing_change_after": {"value": False}, "swallow.regurgitation": {"value": False},
        "swallow.reflux_or_heartburn": {"value": True}, "swallow.meal_related_chest_discomfort": {"value": False},
        "swallow.meal_duration": {"value": "20분, 변화 없음"}, "swallow.fatigue_during_meal": {"value": False},
        "swallow.food_or_drink_avoidance": {"value": "마른 고기"}, "swallow.intake_reduction": {"value": "slightly_reduced"},
        "swallow.unintentional_weight_change": {"value": "없음"}, "swallow.recurrent_chest_infection": {"value": False},
        "swallow.daily_function_and_social_impact": {"value": "물을 곁들여 천천히 먹음"},
        "swallow.neurologic_history": {"value": "없음"}, "swallow.head_neck_surgery_or_radiation": {"value": "없음"},
        "swallow.oesophageal_or_reflux_history": {"value": "역류 증상"}, "swallow.oral_dental_context": {"value": "없음"},
        "swallow.respiratory_history": {"value": "없음"}, "swallow.cognition_frailty_posture": {"value": "없음"},
        "swallow.feeding_tube_or_airway_device": {"value": "없음"}, "swallow.current_medicines": {"value": "암로디핀"},
        "swallow.allergies": {"value": "없음"}, "swallow.previous_assessment_or_test": {"value": "없음"},
        "swallow.previous_strategy_or_treatment": {"value": "물과 함께 먹음"}, "swallow.previous_response": {"value": "조금 도움"},
        "swallow.feeding_assistance": {"value": "필요 없음"}, "swallow.accessibility_need": {"value": "없음"},
        "swallow.patient_concern": {"value": "점점 심해질까 걱정"}, "swallow.expected_help": {"value": "원인 평가에 필요한 정보 전달"},
        "swallow.additional_comment": {"value": "없음"},
    }


def simulations(document):
    cases = {}
    cases["SWALLOW-VAGUE-REMOTE-FIRST-VISIT.json"] = {"id": "SWALLOW-VAGUE-REMOTE-FIRST-VISIT", "simulation_language": "ko", "persona": {"age": 58}, "encounter_context": {"care_setting": "telemedicine", "encounter_type": "new_encounter", "interview_initiator": "patient", "interview_mode": "video", "available_information": [], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "요즘 음식이 잘 안 넘어가고 가슴에 걸리는 느낌이 있습니다."}, "hidden_state": routine_state(), "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"swallow.solid_food_difficulty_last_7_days": True, "swallow.liquid_difficulty_last_7_days": False}, "expected_max_turns": 64, "forbidden_assertions": ["diagnosis.oesophageal_cancer", "recommendation.endoscopy"]}, "provenance": provenance(SOURCES)}
    absent = routine_state(); absent.pop("swallow.latest_episode"); absent.pop("swallow.previous_assessment_or_test")
    behavior = {"swallow.latest_episode": {"dataAbsentReason": "asked-unknown"}, "swallow.previous_assessment_or_test": {"dataAbsentReason": "asked-declined"}}
    cases["SWALLOW-CONFLICT-DATA-ABSENT.json"] = {"id": "SWALLOW-CONFLICT-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 47}, "initial_statement": {"ko": "언제 마지막이었는지는 모르겠고 검사 이야기는 답하지 않겠습니다."}, "hidden_state": absent, "response_behavior": behavior, "expected": {"expected_data_absent_reasons": {k: v["dataAbsentReason"] for k, v in behavior.items()}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 64, "forbidden_assertions": ["swallow.latest_episode.never"]}, "provenance": provenance(SOURCES)}
    proxy = routine_state(); proxy.update({"swallow.information_source": {"value": "caregiver"}, "swallow.source_reliability": {"value": "partly_reliable"}, "swallow.difficulty_initiating": {"value": True}, "swallow.cough_during_or_after": {"value": True}, "swallow.wet_voice_after": {"value": True}, "swallow.feeding_assistance": {"value": "식사 자세와 속도 도움 필요"}, "swallow.accessibility_need": {"value": "인지 지원과 보호자 동행"}})
    cases["SWALLOW-OLDER-PROXY-ACCESSIBILITY.json"] = {"id": "SWALLOW-OLDER-PROXY-ACCESSIBILITY", "simulation_language": "ko", "persona": {"age": 82}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "follow_up", "interview_initiator": "caregiver", "interview_mode": "chat", "available_information": ["caregiver_report"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "어머니가 식사할 때 기침하고 목소리가 젖은 것처럼 들립니다."}, "hidden_state": proxy, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"swallow.information_source": "caregiver", "swallow.wet_voice_after": True}, "expected_max_turns": 64, "forbidden_assertions": ["diagnosis.aspiration"]}, "provenance": provenance(SOURCES)}
    safety_cases = [
        ("AIRWAY-OBSTRUCTION", {"swallow.current_cannot_breathe_or_speak": True}, "emergency", "rule.swallowing-difficulty.safety.complete-airway-obstruction"),
        ("REDUCED-CONSCIOUSNESS", {"swallow.current_reduced_consciousness": True}, "emergency", "rule.swallowing-difficulty.safety.reduced-consciousness"),
        ("BLUE-COLOUR", {"swallow.current_blue_colour": True}, "emergency", "rule.swallowing-difficulty.safety.blue-colour"),
        ("SUDDEN-NEUROLOGIC", {"swallow.sudden_new_difficulty": True, "swallow.sudden_focal_neurologic_change": True}, "emergency", "rule.swallowing-difficulty.safety.sudden-neurologic-change"),
        ("UNABLE-SALIVA", {"swallow.unable_to_swallow_saliva": True}, "urgent", "rule.swallowing-difficulty.safety.unable-swallow-saliva"),
        ("FOOD-BOLUS", {"swallow.suspected_food_bolus": True, "swallow.unable_to_swallow_liquids_current": True}, "urgent", "rule.swallowing-difficulty.safety.food-bolus-unable-liquids"),
        ("SEVERE-BREATHLESSNESS", {"swallow.current_severe_breathlessness_after_swallow": True}, "emergency", "rule.swallowing-difficulty.safety.severe-breathlessness-after-swallow"),
        ("DEHYDRATION", {"swallow.unable_to_keep_fluids": True, "swallow.markedly_reduced_urine": True}, "urgent", "rule.swallowing-difficulty.safety.fluid-intake-dehydration"),
    ]
    for key, updates, level, rule in safety_cases:
        state = routine_state()
        for fact, value in updates.items(): state[fact] = {"value": value}
        cases[f"SWALLOW-{key}.json"] = {"id": f"SWALLOW-{key}", "simulation_language": "ko", "persona": {"age": 61}, "initial_statement": {"ko": "삼키는 중 지금 확인이 필요한 문제가 생겼습니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule], "expected_max_turns": 16, "forbidden_assertions": ["diagnosis.stroke", "diagnosis.food_bolus", "recommendation.diet_texture"]}, "provenance": provenance(SOURCES)}
    follow = routine_state(); follow.update({"swallow.head_neck_surgery_or_radiation": {"value": "후두 수술 후"}, "swallow.previous_assessment_or_test": {"value": "연하검사 결과는 첨부 기록에 있으나 세부 내용 모름"}, "swallow.previous_strategy_or_treatment": {"value": "연하치료 중"}, "swallow.accessibility_need": {"value": "말하기 대신 문자 응답"}})
    cases["SWALLOW-SPECIALTY-FOLLOWUP-ACCESS.json"] = {"id": "SWALLOW-SPECIALTY-FOLLOWUP-ACCESS", "simulation_language": "ko", "persona": {"age": 66}, "encounter_context": {"care_setting": "specialist_clinic", "encounter_type": "follow_up", "interview_initiator": "patient", "interview_mode": "chat", "available_information": ["synthetic_report"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "수술 후 삼킴 재진인데 음성 대신 문자로 답하고 싶습니다."}, "hidden_state": follow, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"swallow.accessibility_need": "말하기 대신 문자 응답"}, "expected_max_turns": 64, "forbidden_assertions": ["interpretation.swallow_study"]}, "provenance": provenance(SOURCES)}
    return cases


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Swallowing Difficulty", intents=[
        (I[0], "Characterize Swallowing Difficulty"), (I[1], "Screen Swallowing Safety"),
        (I[2], "Assess Swallowing Impact and Context"), (I[3], "Prepare Swallowing Handoff")])
    primary, research = source_documents()
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"source": "STOM localhost:8088/fhir", "loinc_version": "2.82", "snomed_ct_observed_version": "http://snomed.info/sct/900000000000207008/version/20260801", "repository_mapping_baseline": "http://snomed.info/sct/900000000000207008/version/20260701"},
        "verified_focus_concept": {"code": "40739000", "display": "Dysphagia (disorder)", "active": True, "use": "rfe_indexing_only_not_diagnosis"},
        "verified_related_loinc_questions": [
            {"fact_id": "swallow.solid_food_difficulty_last_7_days", "code": "70367-8", "display": "I have difficulty swallowing solid foods in the past 7 days [FACIT]", "relation": "related", "exact_mapping_excluded_reason": "source_defined_instrument_item_and_answer_semantics_not_adopted"},
            {"fact_id": "swallow.soft_food_difficulty_last_7_days", "code": "70368-6", "display": "I have difficulty swallowing soft or mashed foods in the past 7 days [FACIT]", "relation": "related", "exact_mapping_excluded_reason": "source_defined_instrument_item_and_answer_semantics_not_adopted"},
            {"fact_id": "swallow.liquid_difficulty_last_7_days", "code": "70369-4", "display": "I have difficulty swallowing liquids in the past 7 days [FACIT]", "relation": "related", "exact_mapping_excluded_reason": "source_defined_instrument_item_and_answer_semantics_not_adopted"},
        ],
        "verified_composite_loinc_references_excluded_from_exact_mapping": [
            {"code": "54860-2", "display": "Coughing or choking during meals or when swallowing medications in last 7 days [MDSv3]"},
            {"code": "54861-0", "display": "Complaints of difficulty or pain with swallowing in last 7 days [MDSv3]"},
        ],
        "verified_exact_question": {"fact_id": "swallow.pain_nrs", "code": "72514-3", "display": "Pain severity - 0-10 verbal numeric rating [Score] - Reported", "relation": "equivalent"},
        "atomicity": {"answer_bearing_questions": len(generated["entries"]), "compound_exact_mapping_allowed": False, "source_defined_instrument_mapping_requires_explicit_instruction": True},
        "validation": {"method": "build_time_local_fhir_lookup", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "clinical_rule_authority": False, "result": "provisional_pass_with_snomed_baseline_change_trigger"},
        "provenance": provenance([SOURCES[4]])}
    for path, document in [
        ("knowledge/base/primary-care-swallowing-difficulty.json", graph),
        ("rules/base/primary-care-swallowing-difficulty.json", rules),
        ("knowledge/generated/gastrointestinal/swallowing-difficulty/swallowing-difficulty.json", generated),
        ("mappings/terminology/snomed-mrcm-swallowing-difficulty.json", mapping),
        ("sources/manifests/primary-care-swallowing-difficulty.json", primary),
        ("sources/manifests/primary-care-swallowing-difficulty-research.json", research),
        ("policies/primary-care-swallowing-difficulty-completion.json", completion(generated)),
    ]:
        write_json(path, document)
    for filename, case in simulations(generated).items():
        write_json(f"simulation/patients/gastrointestinal/swallowing-difficulty/{filename}", case)


if __name__ == "__main__":
    main()
