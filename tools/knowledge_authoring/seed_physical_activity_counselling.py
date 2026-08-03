#!/usr/bin/env python3
"""Materialize a research-only physical activity counselling package."""
from profile_support import *


P, RFE = "physical-activity-counselling", "rfe.physical_activity_counselling"
M = "mapping.terminology.physical-activity-counselling"
ACQUIRED_AT = "2026-08-02T13:29:57Z"
SOURCES = [
    "source.kr.kdca.physical-activity.20260727",
    "source.kr.kdca.exercise.20260515",
    "source.who.physical-activity-sedentary.2020",
    "source.hhs.physical-activity-guidelines.current-20251119",
    "source.stom.physical-activity.20260802",
]
G = {key: f"group.physical_activity.{key}" for key in (
    "goal", "identity", "safety", "pattern", "symptoms", "context", "change", "handoff"
)}
I = [
    "intent.characterize_physical_activity",
    "intent.screen_activity_related_safety",
    "intent.assess_activity_capacity_and_context",
    "intent.prepare_physical_activity_handoff",
]


def Q(fact_id, display, value_type, key, wording, score, group, intent, **kwargs):
    return entry(P, fact_id, display, value_type, key, wording, score, key,
                 [G[group]], intents=[intent], **kwargs)


def fragment():
    characterize, safety, capacity, handoff = I
    entries = [
        Q("activity.consultation_goal", "Physical Activity Consultation Goal", "coded", "goal",
          "이번 문진에서 활동량 확인, 안전하게 시작하기, 늘리기, 다시 시작하기, 현재 수준 유지 중 가장 원하는 도움은 무엇인가요?", 260, "goal", characterize,
          allowed_values=["review", "safe_start", "increase", "return_after_break", "maintain", "unsure"]),
        Q("activity.information_source", "Physical Activity Information Source", "coded", "information-source",
          "신체활동 정보를 누가 답하고 있나요?", 259, "identity", characterize,
          allowed_values=["patient", "caregiver", "patient_and_caregiver", "device_or_record", "unknown"]),
        Q("activity.source_reliability", "Physical Activity Information Reliability", "coded", "source-reliability",
          "답변은 평소 활동을 잘 반영하나요, 기억이 불확실하거나 기기·다른 사람의 정보와 상충하나요?", 258, "identity", characterize,
          allowed_values=["reliable", "partly_reliable", "memory_uncertain", "conflicting_sources", "unknown"]),

        Q("activity.current_chest_pressure", "Current Chest Pressure", "boolean", "current-chest-pressure",
          "지금 가슴을 누르거나 조이는 심한 불편감이 있나요?", 1000, "safety", safety, safety_relevant=True),
        Q("activity.current_severe_breathlessness_at_rest", "Current Severe Breathlessness at Rest", "boolean", "current-severe-breathlessness",
          "지금 쉬고 있어도 말하기 어렵거나 매우 심하게 숨이 차나요?", 999, "safety", safety, safety_relevant=True),
        Q("activity.current_reduced_consciousness", "Current Reduced Consciousness", "boolean", "current-reduced-consciousness",
          "지금 깨우기 어렵거나 의식이 뚜렷하게 떨어져 있나요?", 998, "safety", safety, safety_relevant=True),
        Q("activity.exertional_syncope", "Syncope During or Immediately after Activity", "boolean", "exertional-syncope",
          "신체활동 중이나 직후에 실제로 의식을 잃은 적이 있나요?", 997, "safety", safety, safety_relevant=True),
        Q("activity.current_severe_injury_or_inability", "Current Severe Activity-related Injury", "boolean", "current-severe-injury",
          "활동 중 다친 뒤 현재 심한 변형이 있거나 해당 부위로 서거나 움직일 수 없나요?", 996, "safety", safety, safety_relevant=True),

        Q("physical_activity.current_level", "Current Physical Activity Level", "coded", "current-level",
          "현재 전반적인 신체활동 수준은 어디에 가장 가깝나요?", 250, "pattern", characterize,
          allowed_values=["inactive", "light_only", "some_moderate", "regular_moderate", "regular_vigorous", "variable"]),
        Q("physical_activity.types", "Physical Activity Types", "coded_or_string", "types",
          "현재 하는 신체활동 종류를 모두 선택하거나 보기에 없으면 직접 입력해 주세요.", 249, "pattern", characterize,
          allowed_values=["walking_or_transport", "aerobic_recreation", "muscle_strengthening", "balance", "flexibility", "work_or_household", "sport", "other"]),
        Q("physical_activity.contexts", "Physical Activity Contexts", "coded_or_string", "contexts",
          "주로 활동하는 상황을 모두 선택하거나 보기에 없으면 직접 입력해 주세요.", 248, "pattern", characterize,
          allowed_values=["leisure", "transport", "occupation", "household_or_caregiving", "school", "rehabilitation", "other"]),
        Q("physical_activity.moderate_strenuous_days_last_7", "Moderate to Strenuous Activity Days in Last 7 Days", "integer", "active-days-last-seven",
          "최근 7일 동안 빠르게 걷기처럼 숨이 약간 차는 정도 이상의 활동을 한 날은 며칠인가요?", 247, "pattern", characterize,
          terminology_binding={"system": "http://loinc.org", "code": "68515-6", "display": "How many days of moderate to strenuous exercise, like a brisk walk, did you do in the last 7 days [SAMHSA]", "version": "2.82", "relation": "equivalent"}),
        Q("physical_activity.minutes_per_active_day", "Minutes per Moderate to Strenuous Activity Day", "integer", "minutes-per-active-day",
          "그런 활동을 한 날에는 평균 몇 분 정도 했나요?", 246, "pattern", characterize,
          terminology_binding={"system": "http://loinc.org", "code": "68516-4", "display": "On those days that you engage in moderate to strenuous exercise, how many minutes, on average, do you exercise", "version": "2.82", "relation": "equivalent"}),
        Q("physical_activity.muscle_strengthening_frequency", "Muscle Strengthening Frequency", "string", "muscle-strength-frequency",
          "근력 강화 활동은 얼마나 자주 하나요? 예: 주 2일, 월 1회", 245, "pattern", characterize,
          terminology_binding={"system": "http://loinc.org", "code": "82291-6", "display": "Frequency of muscle-strengthening physical activity", "version": "2.82", "relation": "equivalent"}),
        Q("physical_activity.balance_frequency", "Balance Activity Frequency", "string", "balance-frequency",
          "균형 운동이나 넘어짐 예방 활동은 얼마나 자주 하나요?", 244, "pattern", characterize),
        Q("physical_activity.sedentary_time_per_day", "Sedentary Time per Day", "string", "sedentary-time",
          "잠자는 시간을 제외하고 하루에 앉거나 누워 지내는 시간은 보통 얼마나 되나요?", 243, "pattern", characterize),
        Q("physical_activity.sedentary_break_pattern", "Sedentary Break Pattern", "coded", "sedentary-breaks",
          "오래 앉아 있을 때 일어나 움직이는 빈도는 어느 정도인가요?", 242, "pattern", characterize,
          allowed_values=["at_least_hourly", "several_times_daily", "once_daily", "rarely", "varies"]),
        Q("physical_activity.pattern_duration", "Duration of Current Activity Pattern", "date_or_period", "pattern-duration",
          "현재와 비슷한 활동 수준이 이어진 기간은 얼마나 되나요?", 241, "pattern", characterize),
        Q("physical_activity.change_from_baseline", "Change from Usual Activity", "coded", "change-from-baseline",
          "평소와 비교한 최근 활동량 변화는 어떤가요?", 240, "pattern", characterize,
          allowed_values=["much_less", "slightly_less", "unchanged", "slightly_more", "much_more", "variable"]),
        Q("physical_activity.measurement_method", "Activity Measurement Method", "coded_or_string", "measurement-method",
          "활동량은 주로 기억, 기록지, 휴대전화·웨어러블 중 무엇으로 확인하나요? 보기에 없으면 직접 입력해 주세요.", 239, "pattern", characterize,
          allowed_values=["recall", "written_log", "phone", "wearable", "caregiver_report", "other"]),

        Q("activity.exertional_chest_discomfort_history", "Exertional Chest Discomfort History", "boolean", "exertional-chest-history",
          "활동 중이나 직후에 가슴 불편감이 생긴 적이 있나요?", 230, "symptoms", capacity),
        Q("activity.exertional_breathlessness", "Exertional Breathlessness", "coded", "exertional-breathlessness",
          "활동할 때 숨찬 정도는 예상한 활동 강도와 비교해 어떤가요?", 229, "symptoms", capacity,
          allowed_values=["none", "expected", "more_than_expected", "stops_activity", "occurs_at_rest", "uncertain"]),
        Q("activity.exertional_dizziness_or_near_syncope", "Exertional Dizziness or Near Syncope", "boolean", "exertional-dizziness",
          "활동 중이나 직후에 어지럽거나 쓰러질 것 같은 느낌이 있나요?", 228, "symptoms", capacity),
        Q("activity.exertional_palpitations", "Exertional Palpitations", "boolean", "exertional-palpitations",
          "활동 중이나 직후에 두근거림이 생기나요?", 227, "symptoms", capacity),
        Q("activity.pain_or_stiffness_limit", "Pain or Stiffness Limiting Activity", "string", "pain-stiffness-limit",
          "통증이나 뻣뻣함 때문에 제한되는 활동과 부위를 알려주세요.", 226, "symptoms", capacity),
        Q("activity.fatigue_or_recovery", "Fatigue and Recovery after Activity", "string", "fatigue-recovery",
          "활동 뒤 피로와 회복 시간은 어느 정도인가요?", 225, "symptoms", capacity),
        Q("activity.falls_or_balance_concern", "Falls or Balance Concern", "boolean", "falls-balance",
          "활동할 때 넘어짐이나 균형 문제를 걱정하나요?", 224, "symptoms", capacity),
        Q("activity.daily_function_limit", "Daily Function Limitation", "string", "daily-function-limit",
          "걷기, 계단, 집안일, 직장·학교 또는 돌봄 중 제한되는 활동이 있나요?", 223, "symptoms", capacity),

        Q("activity.mobility_aid", "Mobility Aid", "string", "mobility-aid",
          "지팡이, 보행기, 휠체어, 보조기 등 사용하는 이동 보조도구가 있나요?", 215, "context", capacity),
        Q("activity.cardiopulmonary_history", "Cardiopulmonary History Relevant to Activity", "string", "cardiopulmonary-history",
          "운동 계획에 참고할 심장·폐 질환이나 관련 진료 이력이 있나요?", 214, "context", capacity),
        Q("activity.musculoskeletal_neurologic_history", "Musculoskeletal or Neurologic History Relevant to Activity", "string", "musculoskeletal-neurologic-history",
          "활동에 영향을 주는 근골격계 또는 신경계 질환·손상 이력이 있나요?", 213, "context", capacity),
        Q("activity.metabolic_health_context", "Metabolic Health Context", "string", "metabolic-context",
          "당뇨병, 저혈당, 체중 변화 등 활동 계획에 참고할 건강 문제가 있나요?", 212, "context", capacity),
        Q("activity.pregnancy_or_postpartum_status", "Pregnancy or Postpartum Status", "coded", "pregnancy-postpartum",
          "현재 임신 중이거나 출산 후 1년 이내인가요?", 211, "context", capacity,
          allowed_values=["pregnant", "postpartum_within_one_year", "not_pregnant_or_postpartum", "not_applicable", "unknown"]),
        Q("activity.disability_or_accessibility_need", "Disability or Accessibility Need", "string", "accessibility-need",
          "활동을 위해 필요한 장애·감각·인지·의사소통 또는 접근성 지원이 있나요?", 210, "context", capacity),
        Q("activity.current_medicines", "Current Medicines Relevant to Activity", "string", "current-medicines",
          "처방약, 일반약, 건강기능식품 중 활동 전후 증상이나 안전에 영향을 줄 수 있는 복용물이 있나요?", 209, "context", capacity),
        Q("activity.allergies", "Known Allergies", "string", "allergies",
          "알고 있는 약물 또는 물질 알레르기가 있나요?", 208, "context", capacity),
        Q("activity.prior_professional_restriction", "Prior Professional Activity Restriction", "string", "prior-restriction",
          "의료진이나 재활 전문가가 권한 활동 제한 또는 주의사항이 있나요?", 207, "context", capacity),
        Q("activity.prior_injury_or_rehabilitation", "Prior Activity Injury or Rehabilitation", "string", "prior-injury-rehab",
          "운동 관련 부상이나 재활 치료를 받은 적과 그 반응을 알려주세요.", 206, "context", capacity),
        Q("activity.environment_or_equipment_barrier", "Environment or Equipment Barrier", "string", "environment-barrier",
          "장소, 비용, 날씨·공기질, 안전, 장비 등 활동을 어렵게 하는 환경 요인이 있나요?", 205, "context", capacity),
        Q("activity.occupation_or_caregiving_demand", "Occupation or Caregiving Activity Demand", "string", "occupation-demand",
          "직업·학업·가사·돌봄에서 반복하거나 힘을 쓰는 활동을 알려주세요.", 204, "context", capacity),

        Q("activity.previous_change_attempt", "Previous Physical Activity Change Attempt", "boolean", "previous-attempt",
          "활동량을 늘리거나 운동을 다시 시작하려고 시도한 적이 있나요?", 190, "change", handoff),
        Q("activity.previous_attempt_detail", "Previous Activity Attempt Detail", "string", "attempt-detail",
          "가장 최근 시도한 활동과 기간을 알려주세요.", 189, "change", handoff),
        Q("activity.previous_attempt_response", "Response to Previous Activity Attempt", "string", "attempt-response",
          "그 시도에서 도움이 된 점, 불편했던 점 또는 중단 이유는 무엇인가요?", 188, "change", handoff),
        Q("activity.preferred_activity", "Preferred Physical Activity", "string", "preferred-activity",
          "선호하거나 현실적으로 할 수 있다고 생각하는 활동은 무엇인가요?", 187, "change", handoff),
        Q("activity.personal_barriers", "Personal Barriers to Physical Activity", "string", "personal-barriers",
          "시간, 동기, 피로, 통증, 자신감 등 개인적으로 가장 큰 방해 요인은 무엇인가요?", 186, "change", handoff),
        Q("activity.support_available", "Physical Activity Support Available", "string", "support-available",
          "함께하거나 도와줄 사람, 프로그램 또는 서비스가 있나요?", 185, "change", handoff),
        Q("activity.readiness", "Readiness to Change Physical Activity", "coded", "readiness",
          "현재는 현황 확인, 시작 고려, 곧 시작, 이미 실천, 유지 중 어디에 가장 가깝나요?", 184, "change", handoff,
          allowed_values=["review_only", "considering", "ready_to_start", "already_active", "maintaining", "unsure"]),
        Q("activity.patient_concern", "Patient Physical Activity Concern", "string", "patient-concern",
          "신체활동과 관련해 가장 걱정되는 점은 무엇인가요?", 100, "handoff", handoff),
        Q("activity.expected_help", "Expected Help", "string", "expected-help",
          "이번 진료에서 의료진에게 가장 받고 싶은 도움은 무엇인가요?", 99, "handoff", handoff),
        Q("activity.additional_comment", "Additional Comment", "string", "additional-comment",
          "질문에 없지만 의료진에게 추가로 전달할 내용이 있나요?", 90, "handoff", handoff),
    ]
    rules = [
        safety_rule(P, "current-chest-pressure", {"fact": "activity.current_chest_pressure", "equals": True}, "emergency", 1200),
        safety_rule(P, "current-severe-breathlessness", {"fact": "activity.current_severe_breathlessness_at_rest", "equals": True}, "emergency", 1199),
        safety_rule(P, "current-reduced-consciousness", {"fact": "activity.current_reduced_consciousness", "equals": True}, "emergency", 1198),
        safety_rule(P, "exertional-syncope", {"fact": "activity.exertional_syncope", "equals": True}, "urgent", 1197),
        safety_rule(P, "current-severe-injury", {"fact": "activity.current_severe_injury_or_inability", "equals": True}, "urgent", 1196),
    ]
    return {
        "id": "knowledge.generated.physical-activity-counselling", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-physical-activity-counselling-research",
        "default_refresh": {**default_refresh(), "last_assessed_at": "2026-08-02", "next_monitor_at": "2026-08-03", "next_full_review_at": "2027-01-29"},
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(document):
    safety = [item["fact"]["id"] for item in document["entries"] if item["fact"].get("safety_relevant")]
    core = [
        "activity.consultation_goal", "activity.information_source", "activity.source_reliability",
        "physical_activity.current_level", "physical_activity.types", "physical_activity.contexts",
        "physical_activity.moderate_strenuous_days_last_7", "physical_activity.minutes_per_active_day",
        "physical_activity.muscle_strengthening_frequency", "physical_activity.sedentary_time_per_day",
        "physical_activity.pattern_duration", "physical_activity.change_from_baseline",
        "activity.daily_function_limit", "activity.pregnancy_or_postpartum_status",
        "activity.current_medicines", "activity.allergies", "activity.patient_concern",
        "activity.expected_help", "activity.additional_comment",
    ]
    return {
        "id": "policy.primary-care-physical-activity-counselling-completion", "version": VERSION,
        "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": safety + core, "routine": []},
        "conditional_required_facts": [
            {"when": {"fact": "activity.previous_change_attempt", "equals": True}, "required_facts": [
                "activity.previous_attempt_detail", "activity.previous_attempt_response"]},
            {"when": {"fact": "physical_activity.current_level", "in": ["inactive", "light_only"]}, "required_facts": [
                "activity.exertional_chest_discomfort_history", "activity.exertional_breathlessness",
                "activity.exertional_dizziness_or_near_syncope", "activity.exertional_palpitations",
                "activity.pain_or_stiffness_limit", "activity.falls_or_balance_concern",
                "activity.mobility_aid",
                "activity.cardiopulmonary_history", "activity.musculoskeletal_neurologic_history",
                "activity.metabolic_health_context", "activity.disability_or_accessibility_need",
                "activity.prior_professional_restriction", "activity.preferred_activity",
                "activity.personal_barriers", "activity.support_available", "activity.readiness"]},
        ],
        "clarification_facts_by_rule": {}, "question_budget": {"routine": 52, "clarify": 10},
        "provenance": provenance(SOURCES),
    }


def source_documents():
    artifacts = [
        {"id": SOURCES[0], "kind": "official_korean_public_health_guidance_metadata", "publisher": "Korea Disease Control and Prevention Agency", "title": "Physical activity: what you need to know", "version": "updated-2026-07-27", "url": "https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=6251", "language": "ko", "digest": "official_activity_types_intensity_frequency_duration_sedentary_life_stage_and_safety_sections_verified_2026-08-02", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-02", "monitor_result": "current"},
        {"id": SOURCES[1], "kind": "official_korean_public_health_guidance_metadata", "publisher": "Korea Disease Control and Prevention Agency", "title": "Exercise", "version": "updated-2026-05-15", "url": "https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=5293", "language": "ko", "digest": "official_activity_definition_intensity_types_and_individual_adjustment_verified_2026-08-02", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-02", "monitor_result": "current"},
        {"id": SOURCES[2], "kind": "official_guideline_metadata", "publisher": "World Health Organization", "title": "WHO guidelines on physical activity and sedentary behaviour", "version": "2020-11-25", "url": "https://www.who.int/publications/i/item/9789240015128", "language": "en", "digest": "official_frequency_intensity_duration_sedentary_pregnancy_disability_chronic_condition_recommendations_verified_2026-08-02", "license_status": "metadata_and_summary_only_CC_BY_NC_SA_3_IGO", "complete": False, "monitor_profile": "clinical_guideline", "last_monitored_at": "2026-08-02", "monitor_result": "current"},
        {"id": SOURCES[3], "kind": "official_guideline_metadata", "publisher": "US Department of Health and Human Services", "title": "Physical Activity Guidelines for Americans current guidelines", "version": "second-edition-current-page-updated-2025-11-19", "url": "https://odphp.health.gov/our-work/nutrition-physical-activity/physical-activity-guidelines/current-guidelines", "language": "en", "digest": "official_move_more_sit_less_aerobic_strengthening_life_stage_and_chronic_condition_guidance_verified_2026-08-02", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "clinical_guideline", "last_monitored_at": "2026-08-02", "monitor_result": "current"},
        {"id": SOURCES[4], "kind": "terminology_service_verification", "publisher": "STOM", "title": "Physical activity question terminology verification", "version": "LOINC-2.82_SNOMEDCT-20260701", "url": "http://localhost:8088/fhir", "language": "en", "digest": "loinc_89574-8_68515-6_68516-4_82290-8_82291-6_55423-8_verified", "license_status": "licensed_lookup_metadata_only", "complete": False, "monitor_profile": "terminology_server", "last_monitored_at": "2026-08-02", "monitor_result": "verified_active"},
    ]
    research = {"id": "source-manifest.primary-care-physical-activity-counselling-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance(SOURCES)}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.physical-activity-counselling", "generated_clinical_knowledge", "knowledge/generated/preventive/physical-activity-counselling/physical-activity-counselling.json", True),
        ("source.mapping.physical-activity-counselling", "terminology_mapping", "mappings/terminology/snomed-mrcm-physical-activity-counselling.json", False),
        ("source.external.physical-activity-counselling", "external_source_manifest", "sources/manifests/primary-care-physical-activity-counselling-research.json", False),
        ("source.policy.physical-activity-counselling", "runtime_policy", "policies/primary-care-physical-activity-counselling-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-physical-activity-counselling", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def routine_state():
    return {
        "activity.consultation_goal": {"value": "safe_start"}, "activity.information_source": {"value": "patient"},
        "activity.source_reliability": {"value": "reliable"}, "activity.current_chest_pressure": {"value": False},
        "activity.current_severe_breathlessness_at_rest": {"value": False}, "activity.current_reduced_consciousness": {"value": False},
        "activity.exertional_syncope": {"value": False}, "activity.current_severe_injury_or_inability": {"value": False},
        "physical_activity.current_level": {"value": "light_only"}, "physical_activity.types": {"value": "walking_or_transport"},
        "physical_activity.contexts": {"value": "transport"}, "physical_activity.moderate_strenuous_days_last_7": {"value": 1},
        "physical_activity.minutes_per_active_day": {"value": 20}, "physical_activity.muscle_strengthening_frequency": {"value": "하지 않음"},
        "physical_activity.balance_frequency": {"value": "하지 않음"}, "physical_activity.sedentary_time_per_day": {"value": "하루 9시간"},
        "physical_activity.sedentary_break_pattern": {"value": "rarely"}, "physical_activity.pattern_duration": {"value": "2년"},
        "physical_activity.change_from_baseline": {"value": "slightly_less"}, "physical_activity.measurement_method": {"value": "recall"},
        "activity.exertional_chest_discomfort_history": {"value": False}, "activity.exertional_breathlessness": {"value": "expected"},
        "activity.exertional_dizziness_or_near_syncope": {"value": False}, "activity.exertional_palpitations": {"value": False},
        "activity.pain_or_stiffness_limit": {"value": "무릎 뻣뻣함으로 계단이 불편함"}, "activity.fatigue_or_recovery": {"value": "30분 이내 회복"},
        "activity.falls_or_balance_concern": {"value": False}, "activity.daily_function_limit": {"value": "계단 두 층에서 쉬어야 함"},
        "activity.mobility_aid": {"value": "없음"}, "activity.cardiopulmonary_history": {"value": "고혈압"},
        "activity.musculoskeletal_neurologic_history": {"value": "무릎 골관절염"}, "activity.metabolic_health_context": {"value": "과체중"},
        "activity.pregnancy_or_postpartum_status": {"value": "not_applicable"}, "activity.disability_or_accessibility_need": {"value": "없음"},
        "activity.current_medicines": {"value": "암로디핀"}, "activity.allergies": {"value": "없음"},
        "activity.prior_professional_restriction": {"value": "없음"}, "activity.prior_injury_or_rehabilitation": {"value": "없음"},
        "activity.environment_or_equipment_barrier": {"value": "퇴근이 늦음"}, "activity.occupation_or_caregiving_demand": {"value": "사무직"},
        "activity.previous_change_attempt": {"value": True}, "activity.previous_attempt_detail": {"value": "3개월 전 걷기 2주"},
        "activity.previous_attempt_response": {"value": "야근으로 중단"}, "activity.preferred_activity": {"value": "저녁 걷기"},
        "activity.personal_barriers": {"value": "시간 부족"}, "activity.support_available": {"value": "배우자와 함께 가능"},
        "activity.readiness": {"value": "ready_to_start"}, "activity.patient_concern": {"value": "무릎을 악화시키지 않고 시작하고 싶음"},
        "activity.expected_help": {"value": "현재 상태에 맞는 활동 상담"}, "activity.additional_comment": {"value": "없음"},
    }


def simulations(document):
    cases = {}
    cases["ACTIVITY-VAGUE-REMOTE-FIRST-VISIT.json"] = {"id": "ACTIVITY-VAGUE-REMOTE-FIRST-VISIT", "simulation_language": "ko", "persona": {"age": 54}, "encounter_context": {"care_setting": "telemedicine", "encounter_type": "new_encounter", "interview_initiator": "patient", "interview_mode": "video", "available_information": [], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "운동을 좀 해야 할 것 같은데 뭘 확인해야 하나요?"}, "hidden_state": routine_state(), "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"physical_activity.moderate_strenuous_days_last_7": 1, "physical_activity.minutes_per_active_day": 20}, "expected_max_turns": 52, "forbidden_assertions": ["diagnosis.exercise_intolerance", "recommendation.exercise_prescription"]}, "provenance": provenance(SOURCES)}
    absent = routine_state(); absent.pop("physical_activity.minutes_per_active_day"); absent.pop("activity.cardiopulmonary_history")
    behavior = {"physical_activity.minutes_per_active_day": {"dataAbsentReason": "asked-unknown"}, "activity.cardiopulmonary_history": {"dataAbsentReason": "asked-declined"}}
    cases["ACTIVITY-VAGUE-DATA-ABSENT.json"] = {"id": "ACTIVITY-VAGUE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 43}, "initial_statement": {"ko": "활동 시간은 잘 모르겠고 일부 병력은 답하고 싶지 않습니다."}, "hidden_state": absent, "response_behavior": behavior, "expected": {"expected_data_absent_reasons": {k: v["dataAbsentReason"] for k, v in behavior.items()}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 52, "forbidden_assertions": ["physical_activity.minutes_per_active_day.zero"]}, "provenance": provenance(SOURCES)}
    older = routine_state(); older.update({"physical_activity.balance_frequency": {"value": "주 2회"}, "activity.falls_or_balance_concern": {"value": True}, "activity.mobility_aid": {"value": "지팡이"}})
    cases["ACTIVITY-OLDER-ADULT-FALL-CONCERN.json"] = {"id": "ACTIVITY-OLDER-ADULT-FALL-CONCERN", "simulation_language": "ko", "persona": {"age": 78}, "initial_statement": {"ko": "넘어질까 걱정되지만 활동을 늘리고 싶습니다."}, "hidden_state": older, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"activity.falls_or_balance_concern": True}, "expected_max_turns": 52, "forbidden_assertions": ["diagnosis.fall_risk"]}, "provenance": provenance(SOURCES)}
    pregnant = routine_state(); pregnant["activity.pregnancy_or_postpartum_status"] = {"value": "pregnant"}
    cases["ACTIVITY-PREGNANCY-CONSULTATION.json"] = {"id": "ACTIVITY-PREGNANCY-CONSULTATION", "simulation_language": "ko", "persona": {"age": 33}, "initial_statement": {"ko": "임신 중 활동 상담을 받고 싶어요."}, "hidden_state": pregnant, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"activity.pregnancy_or_postpartum_status": "pregnant"}, "expected_max_turns": 52, "forbidden_assertions": ["recommendation.universal_pregnancy_exercise_plan"]}, "provenance": provenance(SOURCES)}
    accessibility = routine_state(); accessibility.update({"activity.disability_or_accessibility_need": {"value": "청각 안내와 휠체어 접근 공간 필요"}, "activity.mobility_aid": {"value": "휠체어"}})
    cases["ACTIVITY-ACCESSIBILITY-REMOTE.json"] = {"id": "ACTIVITY-ACCESSIBILITY-REMOTE", "simulation_language": "ko", "persona": {"age": 39}, "initial_statement": {"ko": "휠체어를 사용하며 접근 가능한 활동을 찾고 싶습니다."}, "hidden_state": accessibility, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"activity.mobility_aid": "휠체어"}, "expected_max_turns": 52, "forbidden_assertions": ["diagnosis.disability"]}, "provenance": provenance(SOURCES)}
    for key, fact, level in [
        ("CURRENT-CHEST-PRESSURE", "activity.current_chest_pressure", "emergency"),
        ("CURRENT-SEVERE-BREATHLESSNESS", "activity.current_severe_breathlessness_at_rest", "emergency"),
        ("CURRENT-REDUCED-CONSCIOUSNESS", "activity.current_reduced_consciousness", "emergency"),
        ("EXERTIONAL-SYNCOPE", "activity.exertional_syncope", "urgent"),
        ("CURRENT-SEVERE-INJURY", "activity.current_severe_injury_or_inability", "urgent"),
    ]:
        state = routine_state(); state[fact] = {"value": True}
        rule = {item["when"].get("fact"): item["id"] for item in document["safety_rules"] if item["when"].get("fact")}.get(fact)
        cases[f"ACTIVITY-{key}.json"] = {"id": f"ACTIVITY-{key}", "simulation_language": "ko", "persona": {"age": 57}, "initial_statement": {"ko": "신체활동과 관련해 지금 확인이 필요한 증상이 있습니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule], "expected_max_turns": 12, "forbidden_assertions": ["diagnosis.cardiac_event", "recommendation.exercise_prescription"]}, "provenance": provenance(SOURCES)}
    return cases


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Physical Activity Counselling", intents=[
        (I[0], "Characterize Physical Activity"), (I[1], "Screen Activity-related Safety"),
        (I[2], "Assess Activity Capacity and Context"), (I[3], "Prepare Physical Activity Handoff")])
    primary, research = source_documents()
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"source": "STOM localhost:8088/fhir", "loinc_version": "2.82", "snomed_ct_version": "http://snomed.info/sct/900000000000207008/version/20260701"},
        "verified_loinc_questions": [
            {"fact_id": "physical_activity.moderate_strenuous_days_last_7", "code": "68515-6", "display": "How many days of moderate to strenuous exercise, like a brisk walk, did you do in the last 7 days [SAMHSA]", "relation": "equivalent"},
            {"fact_id": "physical_activity.minutes_per_active_day", "code": "68516-4", "display": "On those days that you engage in moderate to strenuous exercise, how many minutes, on average, do you exercise", "relation": "equivalent"},
            {"fact_id": "physical_activity.muscle_strengthening_frequency", "code": "82291-6", "display": "Frequency of muscle-strengthening physical activity", "relation": "equivalent"}],
        "verified_panel_references_excluded_from_item_mapping": [
            {"code": "89574-8", "display": "Exercise Vital Sign (EVS)"},
            {"code": "82290-8", "display": "Frequency of moderate to vigorous aerobic physical activity"}],
        "verified_related_measurement_not_mapped": [{"code": "55423-8", "display": "Number of steps in unspecified time Pedometer", "reason": "no_atomic_step_count_question_in_this_package"}],
        "atomicity": {"answer_bearing_questions": len(generated["entries"]), "compound_exact_mapping_allowed": False, "multi_select_type_and_context_questions_remain_local": True},
        "validation": {"method": "build_time_local_fhir_lookup", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "provenance": provenance([SOURCES[4]])}
    for path, document in [
        ("knowledge/base/primary-care-physical-activity-counselling.json", graph),
        ("rules/base/primary-care-physical-activity-counselling.json", rules),
        ("knowledge/generated/preventive/physical-activity-counselling/physical-activity-counselling.json", generated),
        ("mappings/terminology/snomed-mrcm-physical-activity-counselling.json", mapping),
        ("sources/manifests/primary-care-physical-activity-counselling.json", primary),
        ("sources/manifests/primary-care-physical-activity-counselling-research.json", research),
        ("policies/primary-care-physical-activity-counselling-completion.json", completion(generated)),
    ]:
        write_json(path, document)
    for filename, case in simulations(generated).items():
        write_json(f"simulation/patients/preventive/physical-activity-counselling/{filename}", case)


if __name__ == "__main__":
    main()
