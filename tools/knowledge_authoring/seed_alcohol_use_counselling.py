#!/usr/bin/env python3
"""Materialize a research-only alcohol use counselling package."""
from profile_support import *


P, RFE = "alcohol-use-counselling", "rfe.alcohol_use_counselling"
M = "mapping.terminology.alcohol-use-counselling"
ACQUIRED_AT = "2026-08-02T00:00:00Z"
SOURCES = [
    "source.kr.kdca.alcohol.current-20260615",
    "source.nice.cg115.alcohol-assessment.current-20260802",
    "source.nice.cg100.alcohol-withdrawal.current-20260802",
    "source.niaaa.core-alcohol.screen-assess.2025",
    "source.stom.alcohol-use.20260802",
]
G = {key: f"group.alcohol_use.{key}" for key in (
    "goal", "identity", "safety", "pattern", "dependence", "change", "impact", "history", "handoff"
)}
I = [
    "intent.characterize_alcohol_use",
    "intent.screen_alcohol_related_safety",
    "intent.assess_alcohol_change_and_withdrawal_history",
    "intent.prepare_alcohol_use_handoff",
]


def Q(fact_id, display, value_type, key, wording, score, group, intent, **kwargs):
    return entry(P, fact_id, display, value_type, key, wording, score, key,
                 [G[group]], intents=[intent], **kwargs)


def fragment():
    characterize, safety, dependence, handoff = I
    entries = [
        Q("alcohol.consultation_goal", "Alcohol Consultation Goal", "coded", "goal",
          "이번 문진에서 음주 현황 확인, 줄이기, 끊기, 금주 유지 중 가장 원하는 도움은 무엇인가요?", 260, "goal", characterize,
          allowed_values=["use_review", "reduce", "stop", "maintain_abstinence", "health_effect_review", "unsure"]),
        Q("alcohol.information_source", "Alcohol Information Source", "coded", "information-source",
          "음주 정보를 누가 답하고 있나요?", 259, "identity", characterize,
          allowed_values=["patient", "caregiver", "patient_and_caregiver", "record", "unknown"]),
        Q("alcohol.source_reliability", "Alcohol Information Reliability", "coded", "source-reliability",
          "답변은 현재 음주를 잘 아는 내용인가요, 기억이 불확실하거나 다른 정보와 상충하나요?", 258, "identity", characterize,
          allowed_values=["reliable", "partly_reliable", "memory_uncertain", "conflicting_sources", "unknown"]),

        Q("alcohol.reduced_consciousness", "Current Reduced Consciousness", "boolean", "reduced-consciousness",
          "지금 술 또는 함께 복용한 물질 뒤 깨우기 어렵거나 의식이 뚜렷하게 떨어졌나요?", 1000, "safety", safety, safety_relevant=True),
        Q("alcohol.current_seizure", "Current or Recurrent Seizure", "boolean", "current-seizure",
          "지금 경련이 있거나 짧은 간격으로 다시 경련하고 있나요?", 999, "safety", safety, safety_relevant=True),
        Q("alcohol.severe_confusion_or_hallucination", "Severe Confusion or Hallucination", "boolean", "confusion-hallucination",
          "술을 줄이거나 끊은 뒤 심한 혼란, 환각 또는 통제하기 어려운 초조가 있나요?", 998, "safety", safety, safety_relevant=True),
        Q("alcohol.intentional_or_mixed_overdose", "Intentional or Mixed Overdose", "boolean", "mixed-overdose",
          "술과 약 또는 다른 물질을 함께 과량 복용했거나 일부러 해칠 목적으로 마신 상황인가요?", 997, "safety", safety, safety_relevant=True),
        Q("alcohol.immediate_self_or_other_harm", "Immediate Self or Other Harm Risk", "boolean", "self-other-harm",
          "지금 자신이나 다른 사람을 해칠 구체적인 계획, 행동 또는 즉각적인 위험이 있나요?", 996, "safety", safety, safety_relevant=True),
        Q("alcohol.current_withdrawal_warning", "Current Alcohol Withdrawal Warning Features", "coded", "withdrawal-warning",
          "최근 음주를 줄이거나 끊은 뒤 생긴 증상을 모두 선택하거나 직접 입력해 주세요.", 995, "safety", safety, safety_relevant=True,
          allowed_values=["none", "tremor", "sweating", "vomiting", "marked_anxiety_or_agitation", "hallucination", "confusion", "seizure"]),

        Q("patient.alcohol.use_status", "Alcohol Use Status", "coded", "use-status",
          "현재 음주, 과거 음주 후 금주, 평생 비음주 중 어디에 해당하나요?", 250, "pattern", characterize,
          allowed_values=["current", "former", "never"], reuse_existing=True),
        Q("patient.alcohol.beverage_types", "Alcoholic Beverage Types", "coded_or_string", "beverage-types",
          "현재 또는 과거에 마신 술 종류를 모두 선택하거나 직접 입력해 주세요.", 249, "pattern", characterize,
          allowed_values=["soju", "beer", "makgeolli", "wine", "spirits", "other"], reuse_existing=True),
        Q("patient.alcohol.frequency", "Alcohol Drinking Frequency", "string", "frequency",
          "평균적으로 술을 얼마나 자주 마시나요? 예: 주 2회, 월 1회, 거의 매일", 248, "pattern", characterize,
          reuse_existing=True,
          terminology_binding={"system": "http://loinc.org", "code": "68518-0", "display": "How often do you have a drink containing alcohol", "version": "2.82", "relation": "equivalent"}),
        Q("patient.alcohol.amount_per_occasion", "Alcohol Amount per Occasion", "string", "amount-per-occasion",
          "한 번 마실 때 보통 술 종류별로 얼마나 마시나요? 예: 소주 1병, 맥주 500 mL 2잔", 247, "pattern", characterize, reuse_existing=True),
        Q("alcohol.last_use_time", "Last Alcohol Use Time", "date_or_period", "last-use",
          "마지막으로 술을 마신 때는 언제인가요?", 246, "pattern", characterize,
          terminology_binding={"system": "http://loinc.org", "code": "74014-2", "display": "Last drank alcohol [Date and time]", "version": "2.82", "relation": "equivalent"}),
        Q("alcohol.total_use_duration", "Total Alcohol Use Duration", "date_or_period", "use-duration",
          "술을 규칙적으로 마신 총 기간은 얼마나 되나요? 중간에 금주한 기간이 있으면 제외해 주세요.", 245, "pattern", characterize),
        Q("alcohol.largest_amount_in_one_day", "Largest Alcohol Amount in One Day", "string", "largest-day-amount",
          "지난 1년 중 가장 많이 마신 날에는 술 종류별로 얼마나 마셨나요?", 244, "pattern", characterize),
        Q("alcohol.heavy_day_frequency", "Heavy Drinking Day Frequency", "string", "heavy-day-frequency",
          "평소보다 많이 마시는 날은 얼마나 자주 있나요?", 243, "pattern", characterize),
        Q("alcohol.usual_drinking_context", "Usual Drinking Context", "coded", "drinking-context",
          "주로 술을 마시는 상황을 모두 선택하거나 직접 입력해 주세요.", 242, "pattern", characterize,
          allowed_values=["with_meals", "social", "alone", "at_home", "work_gathering", "to_sleep", "to_relieve_symptoms", "other"]),
        Q("alcohol.recent_reduction_or_stop", "Recent Alcohol Reduction or Stop", "boolean", "recent-reduction-stop",
          "최근 평소 음주량을 크게 줄이거나 완전히 끊었나요?", 994, "safety", safety),

        Q("alcohol.craving", "Alcohol Craving", "boolean", "craving",
          "술을 강하게 마시고 싶은 갈망이 있나요?", 235, "dependence", dependence),
        Q("alcohol.control_difficulty", "Difficulty Controlling Alcohol Use", "boolean", "control-difficulty",
          "마시기 시작하면 계획한 양이나 시간에서 멈추기 어려운가요?", 234, "dependence", dependence),
        Q("alcohol.morning_use", "Morning Alcohol Use", "boolean", "morning-use",
          "아침에 술을 마시거나 불편한 증상을 줄이려고 술을 마시는 일이 있나요?", 233, "dependence", dependence),
        Q("alcohol.tolerance_change", "Alcohol Tolerance Change", "coded", "tolerance-change",
          "예전과 같은 효과를 느끼기 위해 필요한 술의 양이 어떻게 변했나요?", 232, "dependence", dependence,
          allowed_values=["increased", "unchanged", "decreased", "uncertain"]),
        Q("alcohol.prior_withdrawal_seizure", "Prior Alcohol Withdrawal Seizure", "boolean", "prior-withdrawal-seizure",
          "과거 음주를 줄이거나 끊은 뒤 경련한 적이 있나요?", 231, "dependence", dependence),
        Q("alcohol.prior_delirium_tremens", "Prior Delirium Tremens", "boolean", "prior-delirium",
          "과거 금주 과정에서 심한 혼란, 환각 또는 섬망으로 치료받은 적이 있나요?", 230, "dependence", dependence),
        Q("alcohol.prior_assisted_withdrawal", "Prior Medically Assisted Withdrawal", "boolean", "assisted-withdrawal",
          "과거 의료기관이나 전문서비스의 도움을 받아 금주 과정을 진행한 적이 있나요?", 229, "dependence", dependence),

        Q("alcohol.prior_change_attempt", "Prior Alcohol Change Attempt", "boolean", "prior-change-attempt",
          "술을 줄이거나 끊으려고 시도한 적이 있나요?", 225, "change", dependence),
        Q("alcohol.most_recent_change_attempt", "Most Recent Alcohol Change Attempt", "date_or_period", "recent-change-attempt",
          "가장 최근에 줄이거나 끊으려 한 때는 언제인가요?", 224, "change", dependence),
        Q("alcohol.longest_reduction_or_abstinence", "Longest Reduction or Abstinence", "date_or_period", "longest-change",
          "목표한 양 이하로 유지했거나 술을 마시지 않은 가장 긴 기간은 얼마나 되나요?", 223, "change", dependence),
        Q("alcohol.supports_tried", "Alcohol Change Supports Tried", "string", "supports-tried",
          "상담, 치료, 자조모임, 가족 지원 등 시도한 도움을 알려주세요.", 222, "change", dependence),
        Q("alcohol.support_response", "Response to Alcohol Change Supports", "string", "support-response",
          "시도한 도움의 효과는 어땠나요?", 221, "change", dependence),
        Q("alcohol.readiness", "Readiness to Change Alcohol Use", "coded", "readiness",
          "현재는 현황 확인, 줄이기 고려, 줄일 준비, 끊을 준비, 금주 유지 중 어디에 가장 가깝나요?", 220, "change", dependence,
          allowed_values=["review_only", "consider_reduce", "ready_to_reduce", "ready_to_stop", "maintain_abstinence", "unsure"]),
        Q("alcohol.target_date", "Alcohol Change Target Date", "date_or_period", "target-date",
          "줄이거나 끊을 목표 날짜가 있다면 언제인가요?", 219, "change", dependence),
        Q("alcohol.triggers", "Alcohol Use Triggers", "string", "triggers",
          "주로 마시게 되는 상황이나 유발 요인은 무엇인가요?", 218, "change", dependence),

        Q("alcohol.injury_or_hazardous_use", "Alcohol-related Injury or Hazardous Use", "coded", "injury-hazard",
          "음주와 관련해 있었던 상황을 모두 선택하거나 직접 입력해 주세요.", 210, "impact", handoff,
          allowed_values=["none", "fall_or_injury", "driving", "unsafe_work", "unprotected_sex", "violence_or_conflict", "other"]),
        Q("alcohol.role_or_relationship_impact", "Role or Relationship Impact", "string", "role-impact",
          "음주가 일, 학업, 돌봄 또는 관계에 미친 영향이 있나요?", 209, "impact", handoff),
        Q("alcohol.physical_health_context", "Physical Health Context", "string", "physical-health",
          "음주와 관련해 걱정되는 신체 증상이나 진단받은 건강 문제가 있나요?", 208, "impact", handoff),
        Q("alcohol.mental_health_sleep_context", "Mental Health and Sleep Context", "string", "mental-health-sleep",
          "기분, 불안 또는 수면이 음주 전후나 줄일 때 어떻게 달라지나요?", 207, "impact", handoff),
        Q("alcohol.other_substances_and_sedatives", "Other Substances and Sedatives", "string", "other-substances",
          "수면제·진정제·진통제 또는 다른 물질을 술과 함께 사용하나요?", 206, "history", handoff),
        Q("alcohol.pregnancy_or_postpartum_status", "Pregnancy or Postpartum Status", "coded", "pregnancy-postpartum",
          "현재 임신 중이거나 출산 후 1년 이내인가요?", 205, "history", handoff,
          allowed_values=["pregnant", "postpartum_within_one_year", "not_pregnant_or_postpartum", "not_applicable", "unknown"]),
        Q("alcohol.relevant_conditions", "Relevant Health Conditions", "string", "relevant-conditions",
          "치료 중인 질환이나 최근 건강 문제를 알려주세요.", 204, "history", handoff),
        Q("alcohol.current_medicines", "Current Medicines", "string", "current-medicines",
          "처방약, 일반약, 건강기능식품을 포함해 현재 복용 중인 것을 알려주세요.", 203, "history", handoff),
        Q("alcohol.allergies", "Known Allergies", "string", "allergies",
          "알고 있는 약물 또는 물질 알레르기가 있나요?", 202, "history", handoff),
        Q("alcohol.support_person", "Alcohol Change Support Person", "string", "support-person",
          "줄이거나 끊는 과정에서 도움을 줄 수 있는 사람이나 서비스가 있나요?", 201, "history", handoff),
        Q("alcohol.patient_concern", "Patient Concern", "string", "patient-concern",
          "음주와 관련해 가장 걱정되는 점은 무엇인가요?", 100, "handoff", handoff),
        Q("alcohol.expected_help", "Expected Help", "string", "expected-help",
          "이번 진료에서 의료진에게 가장 받고 싶은 도움은 무엇인가요?", 99, "handoff", handoff),
        Q("alcohol.additional_comment", "Additional Comment", "string", "additional-comment",
          "질문에 없지만 의료진에게 추가로 전달할 내용이 있나요?", 90, "handoff", handoff),
    ]
    rules = [
        safety_rule(P, "reduced-consciousness", {"fact": "alcohol.reduced_consciousness", "equals": True}, "emergency", 1200),
        safety_rule(P, "current-seizure", {"fact": "alcohol.current_seizure", "equals": True}, "emergency", 1199),
        safety_rule(P, "confusion-hallucination", {"fact": "alcohol.severe_confusion_or_hallucination", "equals": True}, "emergency", 1198),
        safety_rule(P, "mixed-overdose", {"fact": "alcohol.intentional_or_mixed_overdose", "equals": True}, "emergency", 1197),
        safety_rule(P, "self-other-harm", {"fact": "alcohol.immediate_self_or_other_harm", "equals": True}, "emergency", 1196),
        safety_rule(P, "withdrawal-warning", {"all": [
            {"fact": "alcohol.recent_reduction_or_stop", "equals": True},
            {"fact": "alcohol.current_withdrawal_warning", "in": ["tremor", "sweating", "vomiting", "marked_anxiety_or_agitation", "hallucination", "confusion", "seizure"]},
        ]}, "urgent", 1195),
    ]
    return {
        "id": "knowledge.generated.alcohol-use-counselling", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-alcohol-use-counselling-research",
        "default_refresh": {**default_refresh(), "last_assessed_at": "2026-08-02", "next_monitor_at": "2026-08-03", "next_full_review_at": "2027-01-29"},
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(document):
    safety = [item["fact"]["id"] for item in document["entries"] if item["fact"].get("safety_relevant")]
    core = [
        "alcohol.consultation_goal", "alcohol.information_source", "alcohol.source_reliability",
        "patient.alcohol.use_status", "alcohol.pregnancy_or_postpartum_status",
        "alcohol.relevant_conditions", "alcohol.current_medicines", "alcohol.allergies",
        "alcohol.patient_concern", "alcohol.expected_help", "alcohol.additional_comment",
    ]
    return {
        "id": "policy.primary-care-alcohol-use-counselling-completion", "version": VERSION,
        "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": safety + core, "routine": []},
        "conditional_required_facts": [
            {"when": {"fact": "patient.alcohol.use_status", "equals": "current"}, "required_facts": [
                "patient.alcohol.beverage_types", "patient.alcohol.frequency", "patient.alcohol.amount_per_occasion",
                "alcohol.last_use_time", "alcohol.total_use_duration", "alcohol.largest_amount_in_one_day",
                "alcohol.heavy_day_frequency", "alcohol.usual_drinking_context", "alcohol.recent_reduction_or_stop",
                "alcohol.craving", "alcohol.control_difficulty", "alcohol.morning_use", "alcohol.tolerance_change",
                "alcohol.prior_withdrawal_seizure", "alcohol.prior_delirium_tremens", "alcohol.prior_assisted_withdrawal",
                "alcohol.prior_change_attempt", "alcohol.readiness", "alcohol.target_date", "alcohol.triggers",
                "alcohol.injury_or_hazardous_use", "alcohol.role_or_relationship_impact", "alcohol.physical_health_context",
                "alcohol.mental_health_sleep_context", "alcohol.other_substances_and_sedatives", "alcohol.support_person"]},
            {"when": {"fact": "patient.alcohol.use_status", "equals": "former"}, "required_facts": [
                "patient.alcohol.beverage_types", "patient.alcohol.frequency", "patient.alcohol.amount_per_occasion",
                "alcohol.last_use_time", "alcohol.total_use_duration", "alcohol.prior_withdrawal_seizure",
                "alcohol.prior_delirium_tremens", "alcohol.prior_assisted_withdrawal", "alcohol.prior_change_attempt",
                "alcohol.readiness", "alcohol.triggers", "alcohol.support_person"]},
            {"when": {"fact": "alcohol.prior_change_attempt", "equals": True}, "required_facts": [
                "alcohol.most_recent_change_attempt", "alcohol.longest_reduction_or_abstinence",
                "alcohol.supports_tried", "alcohol.support_response"]},
        ],
        "clarification_facts_by_rule": {}, "question_budget": {"routine": 52, "clarify": 10},
        "provenance": provenance(SOURCES),
    }


def source_documents():
    artifacts = [
        {"id": SOURCES[0], "kind": "official_korean_public_health_guidance_metadata", "publisher": "Korea Disease Control and Prevention Agency", "title": "Alcohol consumption", "version": "updated-2026-06-15", "url": "https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=5297", "language": "ko", "digest": "official_pattern_standard_drink_withdrawal_and_support_sections_verified_2026-08-02", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-02", "monitor_result": "current"},
        {"id": SOURCES[1], "kind": "official_clinical_guideline_metadata", "publisher": "NICE", "title": "Alcohol-use disorders: diagnosis, assessment and management of harmful drinking and alcohol dependence", "version": "CG115-current-2014-10-21", "url": "https://www.nice.org.uk/guidance/cg115/chapter/Recommendations", "language": "en", "digest": "official_assessment_risk_comorbidity_previous_treatment_and_goal_recommendations_verified_2026-08-02", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "nice_guidance", "last_monitored_at": "2026-08-02", "monitor_result": "current"},
        {"id": SOURCES[2], "kind": "official_clinical_guideline_metadata", "publisher": "NICE", "title": "Alcohol-use disorders: diagnosis and management of physical complications", "version": "CG100-current-2017-04-12", "url": "https://www.nice.org.uk/guidance/cg100/chapter/Recommendations", "language": "en", "digest": "official_acute_withdrawal_seizure_delirium_and_vulnerability_recommendations_verified_2026-08-02", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "nice_guidance", "last_monitored_at": "2026-08-02", "monitor_result": "current"},
        {"id": SOURCES[3], "kind": "official_clinical_resource_metadata", "publisher": "NIAAA", "title": "Core Resource on Alcohol: Screen and Assess", "version": "2025-recertification", "url": "https://www.niaaa.nih.gov/health-professionals-communities/core-resource-on-alcohol/screen-and-assess-use-quick-effective-methods", "language": "en", "digest": "official_frequency_quantity_heavy_day_assessment_and_withdrawal_context_verified_2026-08-02", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-02", "monitor_result": "current"},
        {"id": SOURCES[4], "kind": "terminology_service_verification", "publisher": "STOM", "title": "Alcohol-use question terminology verification", "version": "LOINC-2.82_SNOMEDCT-20260701", "url": "http://localhost:8088/fhir", "language": "en", "digest": "loinc_68518-0_11287-0_74013-4_74014-2_72109-2_72110-0_75626-2_verified", "license_status": "licensed_lookup_metadata_only", "complete": False, "monitor_profile": "terminology_server", "last_monitored_at": "2026-08-02", "monitor_result": "verified_active"},
    ]
    research = {"id": "source-manifest.primary-care-alcohol-use-counselling-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance(SOURCES)}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.alcohol-use-counselling", "generated_clinical_knowledge", "knowledge/generated/preventive/alcohol-use-counselling/alcohol-use-counselling.json", True),
        ("source.mapping.alcohol-use-counselling", "terminology_mapping", "mappings/terminology/snomed-mrcm-alcohol-use-counselling.json", False),
        ("source.external.alcohol-use-counselling", "external_source_manifest", "sources/manifests/primary-care-alcohol-use-counselling-research.json", False),
        ("source.policy.alcohol-use-counselling", "runtime_policy", "policies/primary-care-alcohol-use-counselling-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-alcohol-use-counselling", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def routine_state():
    return {
        "alcohol.consultation_goal": {"value": "reduce"}, "alcohol.information_source": {"value": "patient"},
        "alcohol.source_reliability": {"value": "reliable"}, "alcohol.reduced_consciousness": {"value": False},
        "alcohol.current_seizure": {"value": False}, "alcohol.severe_confusion_or_hallucination": {"value": False},
        "alcohol.intentional_or_mixed_overdose": {"value": False}, "alcohol.immediate_self_or_other_harm": {"value": False},
        "alcohol.current_withdrawal_warning": {"value": "none"}, "patient.alcohol.use_status": {"value": "current"},
        "patient.alcohol.beverage_types": {"value": "soju,beer"}, "patient.alcohol.frequency": {"value": "주 3회"},
        "patient.alcohol.amount_per_occasion": {"value": "소주 1병 또는 맥주 500 mL 2잔"},
        "alcohol.last_use_time": {"value": "어젯밤"}, "alcohol.total_use_duration": {"value": "15년"},
        "alcohol.largest_amount_in_one_day": {"value": "소주 2병"}, "alcohol.heavy_day_frequency": {"value": "월 2회"},
        "alcohol.usual_drinking_context": {"value": "social"}, "alcohol.recent_reduction_or_stop": {"value": False},
        "alcohol.craving": {"value": True}, "alcohol.control_difficulty": {"value": True},
        "alcohol.morning_use": {"value": False}, "alcohol.tolerance_change": {"value": "increased"},
        "alcohol.prior_withdrawal_seizure": {"value": False}, "alcohol.prior_delirium_tremens": {"value": False},
        "alcohol.prior_assisted_withdrawal": {"value": False}, "alcohol.prior_change_attempt": {"value": True},
        "alcohol.most_recent_change_attempt": {"value": "3개월 전"}, "alcohol.longest_reduction_or_abstinence": {"value": "4주"},
        "alcohol.supports_tried": {"value": "가족 도움"}, "alcohol.support_response": {"value": "4주간 줄였음"},
        "alcohol.readiness": {"value": "ready_to_reduce"}, "alcohol.target_date": {"value": "다음 주"},
        "alcohol.triggers": {"value": "업무 스트레스"}, "alcohol.injury_or_hazardous_use": {"value": "none"},
        "alcohol.role_or_relationship_impact": {"value": "아침 지각"}, "alcohol.physical_health_context": {"value": "혈압 걱정"},
        "alcohol.mental_health_sleep_context": {"value": "잠들려고 마심"}, "alcohol.other_substances_and_sedatives": {"value": "없음"},
        "alcohol.pregnancy_or_postpartum_status": {"value": "not_applicable"}, "alcohol.relevant_conditions": {"value": "고혈압"},
        "alcohol.current_medicines": {"value": "암로디핀"}, "alcohol.allergies": {"value": "없음"},
        "alcohol.support_person": {"value": "배우자"}, "alcohol.patient_concern": {"value": "점점 양이 늘어남"},
        "alcohol.expected_help": {"value": "안전하게 줄이는 계획 상담"}, "alcohol.additional_comment": {"value": "없음"},
    }


def simulations(document):
    cases = {}
    cases["ALCOHOL-VAGUE-REMOTE-FIRST-VISIT.json"] = {"id": "ALCOHOL-VAGUE-REMOTE-FIRST-VISIT", "simulation_language": "ko", "persona": {"age": 46}, "encounter_context": {"care_setting": "telemedicine", "encounter_type": "new_encounter", "interview_initiator": "patient", "interview_mode": "video", "available_information": [], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "술은 그냥 가끔 마시는데 요즘 양이 늘어난 것 같아 확인하고 싶어요."}, "hidden_state": routine_state(), "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"patient.alcohol.frequency": "주 3회", "patient.alcohol.amount_per_occasion": "소주 1병 또는 맥주 500 mL 2잔"}, "expected_max_turns": 52, "forbidden_assertions": ["diagnosis.alcohol_use_disorder", "recommendation.medication"]}, "provenance": provenance(SOURCES)}
    former = routine_state(); former.update({"alcohol.consultation_goal": {"value": "maintain_abstinence"}, "patient.alcohol.use_status": {"value": "former"}, "alcohol.last_use_time": {"value": "9개월 전"}, "alcohol.readiness": {"value": "maintain_abstinence"}})
    cases["ALCOHOL-FORMER-ABSTINENCE-MAINTENANCE.json"] = {"id": "ALCOHOL-FORMER-ABSTINENCE-MAINTENANCE", "simulation_language": "ko", "persona": {"age": 58}, "initial_statement": {"ko": "9개월째 금주 중인데 유지 상담을 받고 싶습니다."}, "hidden_state": former, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 52, "forbidden_assertions": ["diagnosis.remission"]}, "provenance": provenance(SOURCES)}
    pregnant = routine_state(); pregnant.update({"alcohol.pregnancy_or_postpartum_status": {"value": "pregnant"}, "alcohol.consultation_goal": {"value": "stop"}})
    cases["ALCOHOL-PREGNANCY-CURRENT-USE.json"] = {"id": "ALCOHOL-PREGNANCY-CURRENT-USE", "simulation_language": "ko", "persona": {"age": 32}, "initial_statement": {"ko": "임신 중인데 술을 끊는 상담이 필요합니다."}, "hidden_state": pregnant, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"alcohol.pregnancy_or_postpartum_status": "pregnant"}, "expected_max_turns": 52, "forbidden_assertions": ["recommendation.safe_alcohol_amount_in_pregnancy"]}, "provenance": provenance(SOURCES)}
    absent = routine_state(); absent.pop("patient.alcohol.amount_per_occasion"); absent.pop("alcohol.prior_withdrawal_seizure")
    behavior = {"patient.alcohol.amount_per_occasion": {"dataAbsentReason": "asked-unknown"}, "alcohol.prior_withdrawal_seizure": {"dataAbsentReason": "asked-declined"}}
    cases["ALCOHOL-VAGUE-DATA-ABSENT.json"] = {"id": "ALCOHOL-VAGUE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 51}, "initial_statement": {"ko": "양은 들쭉날쭉해서 모르겠고 과거 금단 이야기는 답하고 싶지 않습니다."}, "hidden_state": absent, "response_behavior": behavior, "expected": {"expected_data_absent_reasons": {k: v["dataAbsentReason"] for k, v in behavior.items()}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 52, "forbidden_assertions": ["alcohol_amount.zero"]}, "provenance": provenance(SOURCES)}
    for key, fact, level in [
        ("REDUCED-CONSCIOUSNESS", "alcohol.reduced_consciousness", "emergency"),
        ("CURRENT-SEIZURE", "alcohol.current_seizure", "emergency"),
        ("CONFUSION-HALLUCINATION", "alcohol.severe_confusion_or_hallucination", "emergency"),
        ("MIXED-OVERDOSE", "alcohol.intentional_or_mixed_overdose", "emergency"),
        ("SELF-OTHER-HARM", "alcohol.immediate_self_or_other_harm", "emergency"),
    ]:
        state = routine_state(); state[fact] = {"value": True}
        rule = {item["when"].get("fact"): item["id"] for item in document["safety_rules"] if item["when"].get("fact")}.get(fact)
        cases[f"ALCOHOL-{key}.json"] = {"id": f"ALCOHOL-{key}", "simulation_language": "ko", "persona": {"age": 44}, "initial_statement": {"ko": "음주와 관련해 지금 급한 증상이 있습니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule], "expected_max_turns": 12, "forbidden_assertions": ["diagnosis.alcohol_poisoning", "diagnosis.alcohol_withdrawal"]}, "provenance": provenance(SOURCES)}
    withdrawal = routine_state(); withdrawal.update({"alcohol.recent_reduction_or_stop": {"value": True}, "alcohol.current_withdrawal_warning": {"value": "tremor"}})
    withdrawal_rule = next(item["id"] for item in document["safety_rules"] if item["id"].endswith("withdrawal-warning"))
    cases["ALCOHOL-RECENT-REDUCTION-WITHDRAWAL.json"] = {"id": "ALCOHOL-RECENT-REDUCTION-WITHDRAWAL", "simulation_language": "ko", "persona": {"age": 61}, "initial_statement": {"ko": "어제부터 술을 확 줄였는데 손이 떨립니다."}, "hidden_state": withdrawal, "expected": {"expected_safety_level": "urgent", "expected_safety_action": "human_handoff", "expected_stop_reason": "urgent_escalation", "expected_triggered_rules_contains": [withdrawal_rule], "expected_max_turns": 14, "forbidden_assertions": ["diagnosis.alcohol_withdrawal"]}, "provenance": provenance(SOURCES)}
    return cases


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Alcohol Use Counselling", intents=[
        (I[0], "Characterize Alcohol Use"), (I[1], "Screen Alcohol-related Safety"),
        (I[2], "Assess Change and Withdrawal History"), (I[3], "Prepare Alcohol Use Handoff")])
    primary, research = source_documents()
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"source": "STOM localhost:8088/fhir", "loinc_version": "2.82", "snomed_ct_version": "http://snomed.info/sct/900000000000207008/version/20260701"},
        "verified_loinc_questions": [
            {"fact_id": "patient.alcohol.frequency", "code": "68518-0", "display": "How often do you have a drink containing alcohol", "relation": "equivalent"},
            {"fact_id": "alcohol.last_use_time", "code": "74014-2", "display": "Last drank alcohol [Date and time]", "relation": "equivalent"},
            {"fact_id": "patient.alcohol.amount_per_occasion", "code": "11287-0", "display": "Alcoholic drinks per drinking day - Reported", "relation": "partial"}],
        "verified_instrument_references_excluded_from_dynamic_mapping": [
            {"code": "72109-2", "display": "Alcohol Use Disorder Identification Test - Consumption [AUDIT-C]"},
            {"code": "72110-0", "display": "Alcohol Use Disorder Identification Test [AUDIT]"},
            {"code": "75626-2", "display": "Total score [AUDIT-C]"}],
        "atomicity": {"answer_bearing_questions": len(generated["entries"]), "compound_exact_mapping_allowed": False, "beverage_and_context_checklists_are_single_multi_select_dimensions": True},
        "validation": {"method": "build_time_local_fhir_lookup", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "provenance": provenance([SOURCES[4]])}
    for path, document in [
        ("knowledge/base/primary-care-alcohol-use-counselling.json", graph),
        ("rules/base/primary-care-alcohol-use-counselling.json", rules),
        ("knowledge/generated/preventive/alcohol-use-counselling/alcohol-use-counselling.json", generated),
        ("mappings/terminology/snomed-mrcm-alcohol-use-counselling.json", mapping),
        ("sources/manifests/primary-care-alcohol-use-counselling.json", primary),
        ("sources/manifests/primary-care-alcohol-use-counselling-research.json", research),
        ("policies/primary-care-alcohol-use-counselling-completion.json", completion(generated)),
    ]:
        write_json(path, document)
    for filename, case in simulations(generated).items():
        write_json(f"simulation/patients/preventive/alcohol-use-counselling/{filename}", case)


if __name__ == "__main__":
    main()
