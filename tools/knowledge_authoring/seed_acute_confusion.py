#!/usr/bin/env python3
"""Materialize a research-only acute-confusion interview package."""
from profile_support import *


P, RFE = "acute_confusion", "rfe.acute_confusion"
M = "mapping.terminology.acute-confusion"
ACQUIRED_AT = "2026-08-04T00:00:00Z"
SOURCES = [
    "source.nhs.sudden-confusion.20240528",
    "source.nice.cg103.delirium.2023",
    "source.acsqhc.delirium-standard.2021",
    "source.stom.acute-confusion.20260804",
]
G = {key: f"group.acute-confusion.{key}" for key in (
    "identity", "safety", "pattern", "context", "previous", "handoff",
)}
I = [
    "intent.characterize_acute_confusion",
    "intent.screen_acute_confusion_safety",
    "intent.assess_acute_confusion_context",
    "intent.prepare_acute_confusion_handoff",
]


def Q(fact_id, display, value_type, key, wording, score, group, intent, **kwargs):
    return entry(P, fact_id, display, value_type, key, wording, score, key,
                 [G[group]], intents=[intent], **kwargs)


def fragment():
    characterize, safety, assess, handoff = I
    entries = [
        Q("acute_confusion.presentation", "Main Acute Confusion Presentation", "coded_or_string", "presentation",
          "이번 문진의 주된 이유는 갑작스러운 혼란, 평소와 다른 행동, 주의력 저하, 지나친 졸림 중 무엇인가요? 보기에 없으면 직접 입력해 주세요.", 400, "identity", characterize,
          allowed_values=["sudden_confusion", "behavior_change", "inattention", "drowsiness", "fluctuating_change", "other"]),
        Q("acute_confusion.information_source", "Acute Confusion Information Source", "coded", "information-source",
          "현재 상태를 누가 답하고 있나요? 보기에 없으면 직접 입력해 주세요.", 399, "identity", characterize,
          allowed_values=["patient", "family_caregiver", "patient_and_caregiver", "clinician_or_record", "witness", "other"]),
        Q("acute_confusion.source_reliability", "Acute Confusion Source Reliability", "coded", "source-reliability",
          "답변의 신뢰도는 직접 관찰, 일부 불확실, 서로 상충, 확인할 사람 없음 중 어디에 가깝나요? 보기에 없으면 직접 입력해 주세요.", 398, "identity", characterize,
          allowed_values=["direct_reliable", "partly_reliable", "uncertain_memory", "conflicting_sources", "no_collateral_source", "other"]),
        Q("acute_confusion.baseline_informant", "Baseline Mental Status Informant", "string", "baseline-informant",
          "평소의 생각·말·행동 상태를 잘 아는 사람이나 기록이 있다면 알려주세요.", 397, "identity", characterize),

        Q("acute_confusion.current_reduced_consciousness", "Current Reduced Consciousness", "boolean", "reduced-consciousness",
          "지금 깨우기 매우 어렵거나 의식이 뚜렷하게 떨어져 있나요?", 1500, "safety", safety, safety_relevant=True),
        Q("acute_confusion.acute_change_from_baseline", "Acute Change From Baseline", "boolean", "acute-change-baseline",
          "평소 상태와 비교해 몇 시간 또는 며칠 사이 새로 혼란스러워졌나요?", 1499, "safety", safety, safety_relevant=True),
        Q("acute_confusion.new_one_sided_weakness", "New One-sided Weakness", "boolean", "one-sided-weakness",
          "새로 얼굴·팔·다리 한쪽에 힘이 빠졌나요?", 1498, "safety", safety, safety_relevant=True),
        Q("acute_confusion.new_speech_difficulty", "New Speech Difficulty", "boolean", "speech-difficulty",
          "새로 말이 어눌해졌거나 말을 이해하거나 표현하기 어려워졌나요?", 1497, "safety", safety, safety_relevant=True),
        Q("acute_confusion.current_or_recent_seizure", "Current or Recent Seizure", "boolean", "seizure",
          "지금 경련 중이거나 이번 혼란 직전에 경련으로 보이는 일이 있었나요?", 1496, "safety", safety, safety_relevant=True),
        Q("acute_confusion.recent_head_injury", "Recent Head Injury", "boolean", "head-injury",
          "혼란이 시작되기 전 머리를 부딪히거나 다친 일이 있었나요?", 1495, "safety", safety, safety_relevant=True),
        Q("acute_confusion.severe_breathing_difficulty", "Severe Breathing Difficulty", "boolean", "breathing-difficulty",
          "지금 숨쉬기 매우 어렵거나 문장으로 말하기 힘든가요?", 1494, "safety", safety, safety_relevant=True),
        Q("acute_confusion.current_chest_pain", "Current Chest Pain", "boolean", "chest-pain",
          "지금 가슴 통증이나 압박감이 있나요?", 1493, "safety", safety, safety_relevant=True),
        Q("acute_confusion.suspected_toxic_or_carbon_monoxide_exposure", "Suspected Toxic or Carbon Monoxide Exposure", "boolean", "toxic-exposure",
          "약물 과량, 독성 물질 또는 일산화탄소 노출 가능성이 있나요?", 1492, "safety", safety, safety_relevant=True),
        Q("acute_confusion.glucose_device_low_alert", "Glucose Device Low Alert", "boolean", "glucose-low-alert",
          "혈당계나 연속혈당측정기에서 저혈당 경고가 표시됐나요?", 1491, "safety", safety, safety_relevant=True),
        Q("acute_confusion.immediate_harm_danger", "Immediate Harm Danger", "boolean", "immediate-harm-danger",
          "지금 본인이나 다른 사람을 다치게 할 즉각적인 위험이 있나요?", 1490, "safety", safety, safety_relevant=True),

        Q("acute_confusion.first_onset", "First Onset of Mental Status Change", "date_or_period", "first-onset",
          "평소와 다른 변화가 처음 시작된 때는 언제인가요?", 380, "pattern", characterize),
        Q("acute_confusion.last_known_normal", "Last Known Usual Mental Status", "date_or_period", "last-known-normal",
          "마지막으로 평소 상태였다고 확실히 확인한 때는 언제인가요?", 379, "pattern", characterize),
        Q("acute_confusion.course", "Mental Status Change Course", "coded", "course",
          "변화가 좋아짐, 비슷함, 악화, 들쭉날쭉함 중 어디에 가깝나요? 보기에 없으면 직접 입력해 주세요.", 378, "pattern", characterize,
          allowed_values=["improving", "unchanged", "worsening", "fluctuating", "resolved", "uncertain", "other"]),
        Q("acute_confusion.fluctuation_timing", "Fluctuation Timing", "string", "fluctuation-timing",
          "상태가 좋아졌다 나빠진다면 어느 시간대에 어떻게 달라지는지 알려주세요.", 377, "pattern", characterize),
        Q("acute_confusion.attention_change", "Attention Change", "boolean", "attention-change",
          "평소보다 대화나 한 가지 일에 집중하기 어려워졌나요?", 376, "pattern", characterize),
        Q("acute_confusion.orientation_change", "Orientation Change", "string", "orientation-change",
          "사람·장소·시간을 평소와 다르게 혼동하는 부분이 있다면 알려주세요.", 375, "pattern", characterize),
        Q("acute_confusion.disorganized_thinking_or_speech", "Disorganized Thinking or Speech", "boolean", "disorganized-thinking",
          "평소와 달리 말의 흐름이나 생각이 앞뒤가 맞지 않나요?", 374, "pattern", characterize),
        Q("acute_confusion.hallucination_or_misperception", "Hallucination or Misperception", "boolean", "hallucination",
          "실제로 없는 것을 보거나 듣는 듯한 변화가 새로 있나요?", 373, "pattern", characterize),
        Q("acute_confusion.agitation_or_restlessness", "Agitation or Restlessness", "boolean", "agitation",
          "평소와 달리 몹시 초조하거나 가만히 있기 어려워졌나요?", 372, "pattern", characterize),
        Q("acute_confusion.drowsy_or_withdrawn", "Drowsy or Withdrawn Change", "boolean", "drowsy-withdrawn",
          "평소보다 지나치게 졸리거나 반응과 활동이 줄었나요?", 371, "pattern", characterize),
        Q("acute_confusion.sleep_wake_change", "Sleep Wake Pattern Change", "boolean", "sleep-wake-change",
          "최근 낮과 밤이 바뀌는 등 수면 시간대가 평소와 달라졌나요?", 370, "pattern", characterize),
        Q("acute_confusion.usual_cognition_and_function", "Usual Cognition and Function", "string", "usual-cognition-function",
          "변화 전 평소 기억력, 의사소통, 이동과 일상생활 상태를 알려주세요.", 369, "pattern", characterize),

        Q("acute_confusion.fever", "Current Fever", "boolean", "fever",
          "현재 열이 나나요?", 1489, "context", assess, safety_relevant=True),
        Q("acute_confusion.severe_illness_appearance", "Severe Illness Appearance", "boolean", "severe-illness-appearance",
          "현재 전신 상태가 심하게 나빠 보이나요?", 1488, "context", assess, safety_relevant=True),
        Q("acute_confusion.measured_temperature", "Measured Temperature", "quantity", "measured-temperature",
          "측정한 체온이 있다면 섭씨 수치를 알려주세요.", 349, "context", assess, unit="Cel"),
        Q("acute_confusion.infection_symptoms", "Recent Infection Symptoms", "string", "infection-symptoms",
          "최근 기침, 배뇨 불편, 상처, 설사 등 감염과 함께 나타난 증상이 있나요?", 348, "context", assess),
        Q("acute_confusion.current_pain", "Current Pain", "boolean", "current-pain",
          "현재 통증이 있나요?", 347, "context", assess),
        Q("acute_confusion.pain_nrs", "Pain Numeric Rating", "integer", "pain-nrs",
          "통증이 있다면 0점부터 10점 중 몇 점인가요?", 346, "context", assess, unit="{score}", minimum=0, maximum=10,
          terminology_binding={"system": "http://loinc.org", "code": "72514-3", "display": "Pain severity - 0-10 verbal numeric rating [Score] - Reported", "version": "2.82", "relation": "equivalent"}),
        Q("acute_confusion.fluid_intake", "Recent Fluid Intake", "string", "fluid-intake",
          "최근 물이나 음료를 평소만큼 마실 수 있었는지 알려주세요.", 345, "context", assess),
        Q("acute_confusion.food_intake", "Recent Food Intake", "string", "food-intake",
          "최근 식사량이 평소와 비교해 어떻게 달라졌는지 알려주세요.", 344, "context", assess),
        Q("acute_confusion.vomiting", "Recent Vomiting", "boolean", "vomiting",
          "최근 구토가 있었나요?", 343, "context", assess),
        Q("acute_confusion.diarrhea", "Recent Diarrhea", "boolean", "diarrhea",
          "최근 설사가 있었나요?", 342, "context", assess),
        Q("acute_confusion.urine_output_change", "Recent Urine Output Change", "string", "urine-output-change",
          "최근 소변량이 평소와 달라졌나요?", 341, "context", assess),
        Q("acute_confusion.urinary_retention", "Urinary Retention Difficulty", "boolean", "urinary-retention",
          "최근 소변이 마려운데도 보기 어려운 문제가 있나요?", 340, "context", assess),
        Q("acute_confusion.constipation", "Recent Constipation", "boolean", "constipation",
          "최근 평소보다 심한 변비가 있나요?", 339, "context", assess),
        Q("acute_confusion.recent_fall", "Recent Fall", "boolean", "recent-fall",
          "혼란 전후에 넘어지거나 거의 넘어질 뻔한 일이 있었나요?", 338, "context", assess),
        Q("acute_confusion.recent_surgery_or_hospitalization", "Recent Surgery or Hospitalization", "string", "recent-surgery-hospitalization",
          "최근 수술, 시술, 응급실 방문 또는 입원이 있었다면 시기를 알려주세요.", 337, "context", assess),
        Q("acute_confusion.environment_change", "Recent Environment Change", "string", "environment-change",
          "최근 입원, 시설 이동, 여행처럼 잠자리나 환경이 바뀐 일이 있나요?", 338, "context", assess),
        Q("acute_confusion.known_cognitive_impairment", "Known Cognitive Impairment", "string", "known-cognitive-impairment",
          "기존에 진단받거나 관찰된 기억력·인지기능 문제가 있나요?", 337, "context", assess),
        Q("acute_confusion.previous_delirium", "Previous Delirium or Acute Confusion", "string", "previous-delirium",
          "이전에도 갑작스러운 혼란이나 섬망을 겪은 적이 있다면 시기와 상황을 알려주세요.", 336, "context", assess),
        Q("acute_confusion.current_medicines", "Current Medicines", "string", "current-medicines",
          "현재 복용하는 처방약과 일반약을 이름·용량·복용법과 함께 알려주세요.", 335, "context", assess),
        Q("acute_confusion.recent_medicine_change", "Recent Medicine Change", "string", "medicine-change",
          "최근 시작, 중단 또는 용량·복용법이 바뀐 약과 변경 시점을 알려주세요.", 334, "context", assess),
        Q("acute_confusion.supplements_or_herbals", "Supplements or Herbals", "string", "supplements",
          "현재 복용하는 건강기능식품, 한약 또는 생약 제품이 있나요?", 333, "context", assess),
        Q("acute_confusion.alcohol_pattern_and_last_use", "Alcohol Pattern and Last Use", "string", "alcohol-pattern",
          "평소 음주 주종·양·빈도와 마지막 음주 시점을 알려주세요.", 332, "context", assess),
        Q("acute_confusion.recent_alcohol_reduction", "Recent Alcohol Reduction", "boolean", "alcohol-reduction",
          "최근 평소보다 음주량을 크게 줄이거나 갑자기 중단했나요?", 331, "context", assess),
        Q("acute_confusion.other_substance_exposure", "Other Substance Exposure", "string", "substance-exposure",
          "최근 대마, 각성제, 진정제 또는 다른 물질을 사용했거나 노출된 일이 있나요?", 330, "context", assess),
        Q("acute_confusion.relevant_conditions", "Relevant Medical Conditions", "string", "relevant-conditions",
          "당뇨, 뇌질환, 간·신장질환, 심장·폐질환 등 치료 중인 질환을 알려주세요.", 329, "context", assess),
        Q("acute_confusion.hearing_vision_aids", "Hearing and Vision Aids", "string", "hearing-vision-aids",
          "평소 안경, 보청기 또는 다른 감각 보조기기를 사용하는지와 현재 사용 가능 여부를 알려주세요.", 328, "context", assess),
        Q("acute_confusion.pregnancy_or_postpartum", "Pregnancy or Postpartum Context", "coded", "pregnancy-postpartum",
          "현재 임신 중이거나 출산 후 6주 이내인가요? 보기에 없으면 직접 입력해 주세요.", 327, "context", assess,
          allowed_values=["pregnant", "postpartum_6_weeks", "not_pregnant_or_postpartum", "not_applicable", "unknown"]),
        Q("acute_confusion.safe_supervision_available", "Safe Supervision Available", "boolean", "safe-supervision",
          "현재 곁에서 안전을 살피고 의료진에게 상태를 설명할 사람이 있나요?", 1488, "context", assess, safety_relevant=True),

        Q("acute_confusion.previous_assessment", "Previous Assessment", "string", "previous-assessment",
          "이번 변화로 이미 받은 진찰이나 상담이 있다면 시기와 내용을 알려주세요.", 300, "previous", assess),
        Q("acute_confusion.previous_tests", "Previous Tests", "string", "previous-tests",
          "이미 시행한 혈당, 혈액·소변검사, 영상검사 등이 있다면 검사명·시기·결과 출처를 알려주세요.", 299, "previous", assess),
        Q("acute_confusion.previous_response", "Response to Previous Care", "string", "previous-response",
          "이미 받은 처치나 환경 조정 후 상태가 어떻게 달라졌는지 알려주세요.", 298, "previous", assess),
        Q("acute_confusion.current_function_impact", "Current Function Impact", "string", "function-impact",
          "현재 식사, 화장실 이용, 이동, 의사소통과 자기 관리가 평소보다 어떻게 달라졌나요?", 297, "previous", assess),
        Q("acute_confusion.current_safety_concern", "Current Safety Concern", "string", "safety-concern",
          "낙상, 길 잃음, 기기 제거 등 지금 안전을 위해 특히 살펴야 할 행동이 있나요?", 296, "previous", assess),
        Q("acute_confusion.accessibility_need", "Accessibility Need", "string", "accessibility-need",
          "문진과 진료에 필요한 언어, 청각, 시각, 인지, 이동 또는 보호자 지원이 있나요?", 120, "handoff", handoff),
        Q("acute_confusion.patient_or_caregiver_concern", "Patient or Caregiver Concern", "string", "concern",
          "환자나 보호자가 현재 가장 걱정하는 점은 무엇인가요?", 110, "handoff", handoff),
        Q("acute_confusion.expected_help", "Expected Help", "string", "expected-help",
          "이번 진료에서 의료진에게 가장 받고 싶은 도움은 무엇인가요?", 109, "handoff", handoff),
        Q("acute_confusion.additional_comment", "Additional Comment", "string", "additional-comment",
          "질문에 없지만 의료진에게 추가로 전달할 내용이 있나요?", 100, "handoff", handoff),
    ]
    rules = [
        safety_rule(P, "reduced-consciousness", {"fact": "acute_confusion.current_reduced_consciousness", "equals": True}, "emergency", 1600),
        safety_rule(P, "acute-change", {"fact": "acute_confusion.acute_change_from_baseline", "equals": True}, "emergency", 1599),
        safety_rule(P, "focal-neurologic-change", {"any": [{"fact": "acute_confusion.new_one_sided_weakness", "equals": True}, {"fact": "acute_confusion.new_speech_difficulty", "equals": True}]}, "emergency", 1598),
        safety_rule(P, "seizure", {"fact": "acute_confusion.current_or_recent_seizure", "equals": True}, "emergency", 1597),
        safety_rule(P, "head-injury", {"fact": "acute_confusion.recent_head_injury", "equals": True}, "emergency", 1596),
        safety_rule(P, "cardiopulmonary", {"any": [{"fact": "acute_confusion.severe_breathing_difficulty", "equals": True}, {"fact": "acute_confusion.current_chest_pain", "equals": True}]}, "emergency", 1595),
        safety_rule(P, "toxic-exposure", {"fact": "acute_confusion.suspected_toxic_or_carbon_monoxide_exposure", "equals": True}, "emergency", 1594),
        safety_rule(P, "glucose-low-alert", {"fact": "acute_confusion.glucose_device_low_alert", "equals": True}, "emergency", 1593),
        safety_rule(P, "immediate-harm", {"fact": "acute_confusion.immediate_harm_danger", "equals": True}, "emergency", 1592),
        safety_rule(P, "severe-illness", {"any": [{"fact": "acute_confusion.fever", "equals": True}, {"fact": "acute_confusion.severe_illness_appearance", "equals": True}]}, "urgent", 1591),
        safety_rule(P, "no-safe-supervision", {"fact": "acute_confusion.safe_supervision_available", "equals": False}, "urgent", 1590),
    ]
    return {
        "id": "knowledge.generated.acute-confusion", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-acute-confusion-research",
        "default_refresh": {**default_refresh(), "last_assessed_at": "2026-08-04", "next_monitor_at": "2026-08-05", "next_full_review_at": "2027-01-31"},
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(document):
    safety_facts = []
    def collect(condition):
        if "fact" in condition and condition["fact"] not in safety_facts:
            safety_facts.append(condition["fact"])
        for operator in ("all", "any"):
            for child in condition.get(operator, []):
                collect(child)
    for rule in document["safety_rules"]:
        collect(rule["when"])
    all_facts = [item["fact"]["id"] for item in document["entries"]]
    return {
        "id": "policy.primary-care-acute-confusion-completion", "version": VERSION,
        "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": safety_facts, "routine": [fact for fact in all_facts if fact not in safety_facts]},
        "conditional_required_facts": [
            {"when": {"fact": "acute_confusion.current_pain", "equals": True}, "required_facts": ["acute_confusion.pain_nrs"]},
            {"when": {"fact": "acute_confusion.fever", "equals": True}, "required_facts": ["acute_confusion.measured_temperature"]},
        ],
        "clarification_facts_by_rule": {}, "question_budget": {"routine": 65, "clarify": 12},
        "provenance": provenance(SOURCES),
    }


def source_documents():
    artifacts = [
        {"id": SOURCES[0], "kind": "official_public_health_guidance_metadata", "publisher": "NHS", "title": "Sudden confusion (delirium)", "version": "reviewed-2024-05-28", "url": "https://www.nhs.uk/symptoms/confusion/", "language": "en", "digest": "sudden_confusion_immediate_help_features_causes_medicines_and_caregiver_support_verified_2026-08-04", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-04", "monitor_result": "current"},
        {"id": SOURCES[1], "kind": "official_clinical_guideline_metadata", "publisher": "NICE", "title": "Delirium: prevention, diagnosis and management in hospital and long-term care", "version": "CG103-amended-2023", "url": "https://www.nice.org.uk/guidance/cg103/chapter/Recommendations", "language": "en", "digest": "acute_fluctuating_change_attention_cognition_perception_behavior_mobility_appetite_sleep_and_4at_boundary_verified_2026-08-04", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "nice_guidance", "last_monitored_at": "2026-08-04", "monitor_result": "current"},
        {"id": SOURCES[2], "kind": "official_clinical_care_standard_metadata", "publisher": "Australian Commission on Safety and Quality in Health Care", "title": "Delirium Clinical Care Standard (revised 2021)", "version": "2021-page-updated-2026-04-30", "url": "https://www.safetyandquality.gov.au/clinical-care-standards/delirium", "language": "en", "digest": "baseline_collateral_history_medicine_pain_hydration_nutrition_function_falls_sensory_and_transition_context_verified_2026-08-04", "license_status": "CC_BY_NC_ND_metadata_and_summary_only", "complete": False, "monitor_profile": "clinical_guideline", "last_monitored_at": "2026-08-04", "monitor_result": "current"},
        {"id": SOURCES[3], "kind": "terminology_service_verification", "publisher": "STOM", "title": "Acute confusion terminology verification", "version": "LOINC-2.82_SNOMEDCT-observed-20260801", "url": "http://localhost:8088/fhir", "language": "en", "digest": "snomed_2776000_62476001_loinc_95813-2_54632-5_54628-3_54629-1_54630-9_and_72514-3_verified", "license_status": "licensed_lookup_metadata_only", "complete": False, "monitor_profile": "terminology_server", "last_monitored_at": "2026-08-04", "monitor_result": "verified_active_baseline_change_observed"},
    ]
    research = {"id": "source-manifest.primary-care-acute-confusion-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance(SOURCES)}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.acute-confusion", "generated_clinical_knowledge", "knowledge/generated/neurology/acute-confusion/acute-confusion.json", True),
        ("source.mapping.acute-confusion", "terminology_mapping", "mappings/terminology/snomed-mrcm-acute-confusion.json", False),
        ("source.external.acute-confusion", "external_source_manifest", "sources/manifests/primary-care-acute-confusion-research.json", False),
        ("source.policy.acute-confusion", "runtime_policy", "policies/primary-care-acute-confusion-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-acute-confusion", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def routine_state():
    values = {}
    true_facts = {"acute_confusion.attention_change", "acute_confusion.sleep_wake_change"}
    for item in fragment()["entries"]:
        fact = item["fact"]
        fid, value_type = fact["id"], fact["value_type"]
        if value_type == "boolean":
            value = fid in true_facts
        elif value_type == "integer":
            value = 0
        elif value_type == "quantity":
            value = "36.8"
        elif value_type == "date_or_period":
            value = "3일 전"
        elif value_type in {"coded", "coded_or_string"}:
            value = fact.get("allowed_values", ["other"])[0]
        else:
            value = "없음"
        values[fid] = {"value": value}
    values.update({
        "acute_confusion.presentation": {"value": "fluctuating_change"},
        "acute_confusion.information_source": {"value": "family_caregiver"},
        "acute_confusion.source_reliability": {"value": "direct_reliable"},
        "acute_confusion.baseline_informant": {"value": "함께 사는 가족"},
        "acute_confusion.acute_change_from_baseline": {"value": False},
        "acute_confusion.first_onset": {"value": "3일 전부터 의심"},
        "acute_confusion.last_known_normal": {"value": "4일 전 저녁"},
        "acute_confusion.course": {"value": "fluctuating"},
        "acute_confusion.fluctuation_timing": {"value": "저녁에 더 산만함"},
        "acute_confusion.usual_cognition_and_function": {"value": "평소 독립적인 일상생활"},
        "acute_confusion.fluid_intake": {"value": "평소와 비슷"},
        "acute_confusion.food_intake": {"value": "평소와 비슷"},
        "acute_confusion.current_medicines": {"value": "합성 약물 목록은 의료진에게 제시 예정"},
        "acute_confusion.safe_supervision_available": {"value": True},
        "acute_confusion.current_function_impact": {"value": "가족의 확인이 필요"},
        "acute_confusion.accessibility_need": {"value": "보호자 대리와 짧은 문장"},
        "acute_confusion.patient_or_caregiver_concern": {"value": "평소와 다른 집중력"},
        "acute_confusion.expected_help": {"value": "변화 시점과 약물 목록 전달"},
        "acute_confusion.additional_comment": {"value": "없음"},
    })
    return values


def case(identifier, updates, level, rule, initial="갑자기 평소와 다른 혼란이 생겼습니다."):
    state = routine_state()
    for fact, value in updates.items():
        state[fact] = {"value": value}
    return {"id": identifier, "simulation_language": "ko", "persona": {"age": 74}, "initial_statement": {"ko": initial}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule], "expected_max_turns": 24, "forbidden_assertions": ["diagnosis.delirium", "diagnosis.stroke", "recommendation.medication_change"]}, "provenance": provenance(SOURCES)}


def simulations():
    cases = {}
    routine = routine_state()
    cases["ACUTE-CONFUSION-UNCERTAIN-REMOTE-PROXY.json"] = {"id": "ACUTE-CONFUSION-UNCERTAIN-REMOTE-PROXY", "simulation_language": "ko", "persona": {"age": 79}, "encounter_context": {"care_setting": "telemedicine", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "video", "available_information": ["caregiver_report"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "어머니가 저녁에 산만해 보여 대신 답하지만 갑작스러운 변화인지는 확실하지 않습니다."}, "hidden_state": routine, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"acute_confusion.information_source": "family_caregiver"}, "expected_max_turns": 65, "forbidden_assertions": ["diagnosis.delirium", "diagnosis.dementia"]}, "provenance": provenance(SOURCES)}
    absent = routine_state()
    absent.pop("acute_confusion.last_known_normal")
    absent.pop("acute_confusion.previous_tests")
    behavior = {"acute_confusion.last_known_normal": {"dataAbsentReason": "asked-unknown"}, "acute_confusion.previous_tests": {"dataAbsentReason": "asked-declined"}}
    cases["ACUTE-CONFUSION-CONFLICT-DATA-ABSENT.json"] = {"id": "ACUTE-CONFUSION-CONFLICT-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 68}, "initial_statement": {"ko": "가족끼리 시작 시점이 다르고 검사 내용은 답하지 않겠습니다."}, "hidden_state": absent, "response_behavior": behavior, "expected": {"expected_data_absent_reasons": {key: value["dataAbsentReason"] for key, value in behavior.items()}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 65, "forbidden_assertions": ["acute_confusion.previous_tests.none"]}, "provenance": provenance(SOURCES)}
    cases["ACUTE-CONFUSION-REDUCED-CONSCIOUSNESS.json"] = case("ACUTE-CONFUSION-REDUCED-CONSCIOUSNESS", {"acute_confusion.current_reduced_consciousness": True}, "emergency", "rule.acute_confusion.safety.reduced-consciousness")
    cases["ACUTE-CONFUSION-ACUTE-CHANGE.json"] = case("ACUTE-CONFUSION-ACUTE-CHANGE", {"acute_confusion.acute_change_from_baseline": True}, "emergency", "rule.acute_confusion.safety.acute-change")
    cases["ACUTE-CONFUSION-FOCAL-NEUROLOGIC.json"] = case("ACUTE-CONFUSION-FOCAL-NEUROLOGIC", {"acute_confusion.new_one_sided_weakness": True}, "emergency", "rule.acute_confusion.safety.focal-neurologic-change")
    cases["ACUTE-CONFUSION-SEIZURE.json"] = case("ACUTE-CONFUSION-SEIZURE", {"acute_confusion.current_or_recent_seizure": True}, "emergency", "rule.acute_confusion.safety.seizure")
    cases["ACUTE-CONFUSION-HEAD-INJURY.json"] = case("ACUTE-CONFUSION-HEAD-INJURY", {"acute_confusion.recent_head_injury": True}, "emergency", "rule.acute_confusion.safety.head-injury")
    cases["ACUTE-CONFUSION-CARDIOPULMONARY.json"] = case("ACUTE-CONFUSION-CARDIOPULMONARY", {"acute_confusion.severe_breathing_difficulty": True}, "emergency", "rule.acute_confusion.safety.cardiopulmonary")
    cases["ACUTE-CONFUSION-TOXIC-EXPOSURE.json"] = case("ACUTE-CONFUSION-TOXIC-EXPOSURE", {"acute_confusion.suspected_toxic_or_carbon_monoxide_exposure": True}, "emergency", "rule.acute_confusion.safety.toxic-exposure", "같은 방에 있던 두 사람이 함께 혼란스럽고 머리가 아픕니다.")
    cases["ACUTE-CONFUSION-GLUCOSE-LOW-ALERT.json"] = case("ACUTE-CONFUSION-GLUCOSE-LOW-ALERT", {"acute_confusion.glucose_device_low_alert": True}, "emergency", "rule.acute_confusion.safety.glucose-low-alert")
    cases["ACUTE-CONFUSION-IMMEDIATE-HARM.json"] = case("ACUTE-CONFUSION-IMMEDIATE-HARM", {"acute_confusion.immediate_harm_danger": True}, "emergency", "rule.acute_confusion.safety.immediate-harm")
    cases["ACUTE-CONFUSION-SEVERE-ILLNESS.json"] = case("ACUTE-CONFUSION-SEVERE-ILLNESS", {"acute_confusion.severe_illness_appearance": True}, "urgent", "rule.acute_confusion.safety.severe-illness")
    cases["ACUTE-CONFUSION-NO-SUPERVISION.json"] = case("ACUTE-CONFUSION-NO-SUPERVISION", {"acute_confusion.safe_supervision_available": False}, "urgent", "rule.acute_confusion.safety.no-safe-supervision")
    multi = routine_state()
    multi["acute_confusion.current_pain"] = {"value": True}
    multi["acute_confusion.pain_nrs"] = {"value": 4}
    cases["ACUTE-CONFUSION-MULTI-RFE-PAIN-ACCESSIBILITY.json"] = {"id": "ACUTE-CONFUSION-MULTI-RFE-PAIN-ACCESSIBILITY", "simulation_language": "ko", "persona": {"age": 82}, "initial_statement": {"ko": "혼란 여부가 걱정되고 허리 통증도 있으며 보청기를 사용합니다."}, "hidden_state": multi, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"acute_confusion.current_pain": True, "acute_confusion.pain_nrs": 4}, "expected_max_turns": 65, "forbidden_assertions": ["diagnosis.delirium", "diagnosis.fracture"]}, "provenance": provenance(SOURCES)}
    return cases


def queue_document(document):
    return {
        "id": "queue.primary-care-knowledge-package-expansion-v0.14", "version": "0.14.0",
        "status": "materialized_unreviewed", "content_status": "materialized_unreviewed", "review_status": "unreviewed",
        "grouping_principle": "A sudden mental-status or behaviour change is a time-sensitive Reason for Encounter and must not be forced into a chronic memory or cognitive-concern route.",
        "order": [{"rfe": RFE, "package_id": "package.primary-care-acute-confusion", "priority": 1, "state": "implemented_unreviewed", "coverage_goal": ["baseline informant source reliability onset last-known-usual course and fluctuation", "atomic consciousness focal-neurologic seizure injury cardiopulmonary toxic glucose and harm warning features", "attention orientation thought perception activity sleep and usual cognitive-functional comparison", "medicine infection hydration nutrition pain elimination alcohol substance environment sensory and prior-delirium context", "previous assessment tests response function supervision accessibility concern and expected help"]}],
        "definition_of_done": ["official NHS NICE Australian Commission and STOM source manifests with refresh metadata", "sudden confusion routes independently from chronic memory concern", "clinician handoff Facts and no unverified CAM instrument equivalence", "routine proxy remote accessibility conflict dataAbsentReason multi-RFE and every safety-rule simulation", "privacy validator build unit all-simulation terminology ValueSet and Coverage gates pass"],
        "constraints": ["Do not diagnose delirium dementia stroke infection intoxication or another cause.", "Do not administer or score CAM 4AT or another source-defined instrument without explicit adoption and licensing review.", "Do not recommend tests medicines or treatment during collection.", "Keep content unreviewed and research_only pending clinical and Korean service review."],
        "provenance": provenance(["knowledge/catalog/primary-care-rfe.json", "PROJECT_CONTEXT.md", "sources/manifests/primary-care-acute-confusion-research.json"]),
    }


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Acute Confusion", intents=[
        (I[0], "Characterize Acute Confusion"), (I[1], "Screen Acute Confusion Safety"),
        (I[2], "Assess Acute Confusion Context"), (I[3], "Prepare Acute Confusion Handoff")])
    primary, research = source_documents()
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"source": "STOM localhost:8088/fhir", "loinc_version": "2.82", "snomed_ct_observed_version": "http://snomed.info/sct/900000000000207008/version/20260801", "repository_mapping_baseline": "http://snomed.info/sct/900000000000207008/version/20260701"},
        "verified_focus_concept": {"code": "2776000", "display": "Delirium (disorder)", "active": True, "use": "rfe_indexing_reference_only_not_patient_diagnosis"},
        "verified_related_concepts": [{"code": "62476001", "display": "Disorientated (finding)", "active": True}],
        "verified_exact_questions": [{"fact_id": "acute_confusion.pain_nrs", "code": "72514-3", "display": "Pain severity - 0-10 verbal numeric rating [Score] - Reported", "relation": "equivalent"}],
        "verified_reference_not_used": [
            {"code": "95813-2", "display": "Is there evidence of an acute change in mental status from the patient's baseline during assessment period [CAM.CMS]", "reason": "source_defined_CAM_CMS_item_not_automatically_adopted"},
            {"code": "54632-5", "display": "Acute onset mental status change [CAM.CMS]", "reason": "source_defined_CAM_CMS_item_not_automatically_adopted"},
            {"code": "54628-3", "display": "Inattention in last 7 days [CAM.CMS]", "reason": "instrument_time_window_and_answer_semantics_not_adopted"},
            {"code": "54629-1", "display": "Disorganized thinking in last 7 days [CAM.CMS]", "reason": "instrument_time_window_and_answer_semantics_not_adopted"},
            {"code": "54630-9", "display": "Altered level of consciousness in last 7 days [CAM.CMS]", "reason": "instrument_answer_list_not_adopted"},
        ],
        "atomicity": {"answer_bearing_questions": len(generated["entries"]), "compound_exact_mapping_allowed": False, "source_defined_fixed_questionnaire_excluded": True},
        "validation": {"method": "build_time_local_fhir_lookup", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "clinical_rule_authority": False, "result": "provisional_pass_with_snomed_baseline_change_trigger"},
        "provenance": provenance([SOURCES[3]])}
    for path, document in [
        ("knowledge/base/primary-care-acute-confusion.json", graph),
        ("rules/base/primary-care-acute-confusion.json", rules),
        ("knowledge/generated/neurology/acute-confusion/acute-confusion.json", generated),
        ("mappings/terminology/snomed-mrcm-acute-confusion.json", mapping),
        ("sources/manifests/primary-care-acute-confusion.json", primary),
        ("sources/manifests/primary-care-acute-confusion-research.json", research),
        ("policies/primary-care-acute-confusion-completion.json", completion(generated)),
        ("knowledge/catalog/planned-package-work-queue-v0.14.json", queue_document(generated)),
    ]:
        write_json(path, document)
    for filename, scenario in simulations().items():
        write_json(f"simulation/patients/neurology/acute-confusion/{filename}", scenario)


if __name__ == "__main__":
    main()
