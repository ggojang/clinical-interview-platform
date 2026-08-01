#!/usr/bin/env python3
"""Materialize a research-only tobacco and nicotine counselling package."""
from profile_support import *


P, RFE = "tobacco-nicotine-counselling", "rfe.tobacco_nicotine_counselling"
M = "mapping.terminology.tobacco-nicotine-counselling"
ACQUIRED_AT = "2026-08-01T00:00:00Z"
SOURCES = [
    "source.nice.ng209.tobacco-dependence.current-20260801",
    "source.who.tobacco-cessation-guideline.2024",
    "source.cdc.tobacco-clinical-interventions.2024",
    "source.kr.nosmoke-guide.counselling.current-20260801",
    "source.stom.tobacco-nicotine.20260801",
]
G = {key: f"group.tobacco_nicotine.{key}" for key in (
    "goal", "identity", "safety", "pattern", "dependence", "quit", "exposure", "history", "handoff"
)}
I = [
    "intent.characterize_tobacco_nicotine_use",
    "intent.screen_tobacco_nicotine_safety",
    "intent.assess_tobacco_dependence_and_quit_history",
    "intent.prepare_tobacco_nicotine_handoff",
]


def Q(fact_id, display, value_type, key, wording, score, group, intent, **kwargs):
    return entry(P, fact_id, display, value_type, key, wording, score, key,
                 [G[group]], intents=[intent], **kwargs)


def fragment():
    characterize, safety, dependence, handoff = I
    entries = [
        Q("tobacco.consultation_goal", "Tobacco or Nicotine Consultation Goal", "coded", "goal",
          "이번 문진에서 사용 현황 확인, 줄이기, 끊기, 재사용 예방 중 가장 원하는 도움은 무엇인가요?", 260, "goal", characterize,
          allowed_values=["use_review", "reduce", "quit", "prevent_relapse", "exposure_review", "unsure"]),
        Q("tobacco.information_source", "Information Source", "coded", "information-source",
          "흡연·니코틴 사용 정보를 누가 답하고 있나요?", 259, "identity", characterize,
          allowed_values=["patient", "caregiver", "patient_and_caregiver", "record", "unknown"]),
        Q("tobacco.source_reliability", "Source Reliability", "coded", "source-reliability",
          "답변은 본인의 현재 사용을 잘 아는 내용인가요, 기억이 불확실하거나 다른 정보와 상충하나요?", 258, "identity", characterize,
          allowed_values=["reliable", "partly_reliable", "memory_uncertain", "conflicting_sources", "unknown"]),

        Q("tobacco.severe_chest_pain", "Current Severe Chest Pain", "boolean", "severe-chest-pain",
          "지금 심한 가슴 통증이나 압박감이 있나요?", 1000, "safety", safety, safety_relevant=True),
        Q("tobacco.severe_breathing_difficulty", "Current Severe Breathing Difficulty", "boolean", "severe-breathing",
          "지금 숨쉬기가 매우 어렵거나 말을 이어가기 힘든가요?", 999, "safety", safety, safety_relevant=True),
        Q("tobacco.collapse_or_reduced_consciousness", "Collapse or Reduced Consciousness", "boolean", "collapse-consciousness",
          "니코틴 제품 사용이나 노출 뒤 쓰러졌거나 깨우기 어렵고 의식이 뚜렷하게 떨어졌나요?", 998, "safety", safety, safety_relevant=True),
        Q("tobacco.suspected_acute_nicotine_exposure", "Suspected Acute Nicotine Exposure", "boolean", "acute-nicotine-exposure",
          "니코틴 액상이나 제품을 삼켰거나 피부·눈에 많이 묻은 급성 노출이 있나요?", 997, "safety", safety, safety_relevant=True),

        Q("patient.smoking.status", "Tobacco Smoking Status", "coded", "smoking-status",
          "일반담배 또는 가열담배를 포함한 현재 흡연 상태는 어떻게 되나요?", 250, "pattern", characterize,
          allowed_values=["current", "former", "never"], reuse_existing=True),
        Q("patient.smoking.product_types", "Tobacco or Nicotine Product Types", "coded", "product-types",
          "현재 또는 과거에 사용한 담배·니코틴 제품을 모두 선택하거나 직접 입력해 주세요.", 249, "pattern", characterize,
          allowed_values=["combustible_cigarette", "heated_tobacco", "electronic_cigarette", "cigar_or_pipe", "smokeless_tobacco", "other"], reuse_existing=True),
        Q("tobacco.last_use_time", "Last Tobacco or Nicotine Use Time", "date_or_period", "last-use",
          "담배나 니코틴 제품을 마지막으로 사용한 때는 언제인가요?", 248, "pattern", characterize),
        Q("patient.smoking.cigarettes_per_day", "Combustible Cigarettes per Day", "quantity", "cigarettes-per-day",
          "일반담배는 보통 하루 몇 개비 피우나요?", 247, "pattern", characterize, unit="{cigarette}/d", reuse_existing=True),
        Q("patient.smoking.duration_years", "Smoking Duration", "quantity", "smoking-duration",
          "일반담배 또는 가열담배를 사용한 총 기간은 몇 년 정도인가요?", 246, "pattern", characterize, unit="a", reuse_existing=True),
        Q("tobacco.heated_tobacco_amount", "Heated Tobacco Amount", "string", "heated-amount",
          "가열담배는 제품명과 하루 또는 일주일 사용량을 알려주세요.", 245, "pattern", characterize),
        Q("tobacco.electronic_cigarette_status", "Electronic Cigarette Status", "coded", "electronic-status",
          "전자담배는 현재 매일, 가끔, 금연을 위해 사용 중, 과거 사용, 사용한 적 없음 중 어디에 해당하나요?", 245, "pattern", characterize,
          allowed_values=["current_daily", "current_occasional", "trying_to_quit", "former", "never"],
          terminology_binding={"system": "http://loinc.org", "code": "105045-9", "display": "Electronic cigarette status", "version": "2.82", "relation": "equivalent"}),
        Q("tobacco.electronic_cigarette_nicotine_content", "Electronic Cigarette Nicotine Content", "coded", "electronic-nicotine",
          "사용하는 전자담배 액상이나 카트리지에 니코틴이 들어 있나요?", 244, "pattern", characterize,
          allowed_values=["nicotine", "non_nicotine", "mixed_or_varies", "unknown"]),
        Q("tobacco.electronic_cigarette_amount", "Electronic Cigarette Amount", "string", "electronic-amount",
          "전자담배는 제품명과 하루 또는 일주일 사용량을 알려주세요.", 243, "pattern", characterize),
        Q("tobacco.smokeless_tobacco_amount", "Smokeless Tobacco Amount", "string", "smokeless-amount",
          "씹는 담배·스누스·코담배 같은 무연담배의 종류와 사용량을 알려주세요.", 242, "pattern", characterize),

        Q("tobacco.age_at_first_regular_use", "Age at First Regular Use", "integer", "first-regular-age",
          "담배나 니코틴 제품을 규칙적으로 사용하기 시작한 나이는 몇 살인가요?", 235, "dependence", dependence, minimum=0, maximum=120),
        Q("tobacco.time_to_first_use_after_waking", "Time to First Use After Waking", "coded", "time-to-first-use",
          "잠에서 깬 뒤 첫 담배나 니코틴 제품을 사용하기까지 보통 얼마나 걸리나요?", 234, "dependence", dependence,
          allowed_values=["within_5_minutes", "6_to_30_minutes", "31_to_60_minutes", "after_60_minutes", "not_applicable"]),
        Q("tobacco.wakes_to_use", "Wakes to Use Tobacco or Nicotine", "boolean", "wakes-to-use",
          "담배나 니코틴 제품을 사용하려고 밤에 깨는 일이 있나요?", 233, "dependence", dependence),
        Q("tobacco.craving_or_withdrawal", "Craving or Withdrawal", "string", "craving-withdrawal",
          "사용하지 못할 때 생기는 갈망이나 초조함 같은 불편을 알려주세요.", 232, "dependence", dependence),

        Q("tobacco.prior_quit_attempt", "Prior Quit Attempt", "boolean", "prior-attempt",
          "담배나 니코틴 제품을 끊으려고 시도한 적이 있나요?", 225, "quit", dependence),
        Q("tobacco.quit_attempt_count", "Quit Attempt Count", "integer", "attempt-count",
          "끊으려 한 시도는 지금까지 대략 몇 번인가요?", 224, "quit", dependence, minimum=0, maximum=999),
        Q("tobacco.most_recent_quit_attempt", "Most Recent Quit Attempt", "date_or_period", "recent-attempt",
          "가장 최근에 끊으려 한 때는 언제인가요?", 223, "quit", dependence),
        Q("tobacco.longest_abstinence", "Longest Abstinence", "date_or_period", "longest-abstinence",
          "가장 오래 사용하지 않았던 기간은 얼마나 되나요?", 222, "quit", dependence),
        Q("tobacco.quit_supports_tried", "Quit Supports Tried", "string", "supports-tried",
          "상담, 금연클리닉, 약이나 니코틴 대체제품 등 시도한 도움을 알려주세요.", 221, "quit", dependence),
        Q("tobacco.quit_support_response", "Response to Quit Supports", "string", "support-response",
          "시도한 금연 도움의 효과와 불편 또는 부작용은 어땠나요?", 220, "quit", dependence),
        Q("patient.smoking.quit_timing", "Quit Timing", "date_or_period", "quit-timing",
          "흡연을 중단했다면 언제부터 사용하지 않았나요?", 219, "quit", dependence, reuse_existing=True),
        Q("tobacco.readiness", "Readiness to Change", "coded", "readiness",
          "현재는 계속 사용, 줄이기, 끊을 준비, 금연 유지 중 어디에 가장 가깝나요?", 218, "quit", dependence,
          allowed_values=["continue", "consider_reduce", "ready_to_reduce", "ready_to_quit", "maintain_abstinence", "unsure"]),
        Q("tobacco.target_date", "Target Quit or Reduction Date", "date_or_period", "target-date",
          "줄이거나 끊을 목표 날짜가 있다면 언제인가요?", 217, "quit", dependence),
        Q("tobacco.triggers", "Tobacco or Nicotine Use Triggers", "string", "triggers",
          "주로 사용하게 되는 상황이나 유발 요인은 무엇인가요?", 216, "quit", dependence),

        Q("tobacco.home_secondhand_exposure", "Home Secondhand Exposure", "boolean", "home-exposure",
          "집 안이나 차 안에서 다른 사람의 담배 연기 또는 전자담배 에어로졸에 노출되나요?", 210, "exposure", handoff),
        Q("tobacco.work_secondhand_exposure", "Work Secondhand Exposure", "boolean", "work-exposure",
          "직장이나 자주 머무는 장소에서 담배 연기 또는 전자담배 에어로졸에 노출되나요?", 209, "exposure", handoff),
        Q("tobacco.pregnancy_or_postpartum_status", "Pregnancy or Postpartum Status", "coded", "pregnancy-postpartum",
          "현재 임신 중이거나 출산 후 1년 이내인가요?", 208, "history", handoff,
          allowed_values=["pregnant", "postpartum_within_one_year", "not_pregnant_or_postpartum", "not_applicable", "unknown"]),
        Q("tobacco.relevant_conditions", "Relevant Health Conditions", "string", "relevant-conditions",
          "치료 중인 질환이나 최근 건강 문제를 알려주세요.", 205, "history", handoff),
        Q("tobacco.current_medicines", "Current Medicines", "string", "current-medicines",
          "처방약, 일반약, 건강기능식품을 포함해 현재 복용 중인 것을 알려주세요.", 204, "history", handoff),
        Q("tobacco.allergies", "Known Allergies", "string", "allergies",
          "알고 있는 약물 또는 물질 알레르기가 있나요?", 203, "history", handoff),
        Q("tobacco.patient_concern", "Patient Concern", "string", "patient-concern",
          "담배·니코틴 사용과 관련해 가장 걱정되는 점은 무엇인가요?", 100, "handoff", handoff),
        Q("tobacco.expected_help", "Expected Help", "string", "expected-help",
          "이번 진료에서 의료진에게 가장 받고 싶은 도움은 무엇인가요?", 99, "handoff", handoff),
        Q("tobacco.additional_comment", "Additional Comment", "string", "additional-comment",
          "질문에 없지만 의료진에게 추가로 전달할 내용이 있나요?", 90, "handoff", handoff),
    ]
    rules = [
        safety_rule(P, "severe-chest-pain", {"fact": "tobacco.severe_chest_pain", "equals": True}, "emergency", 1200),
        safety_rule(P, "severe-breathing", {"fact": "tobacco.severe_breathing_difficulty", "equals": True}, "emergency", 1199),
        safety_rule(P, "collapse-consciousness", {"fact": "tobacco.collapse_or_reduced_consciousness", "equals": True}, "emergency", 1198),
        safety_rule(P, "acute-nicotine-exposure", {"fact": "tobacco.suspected_acute_nicotine_exposure", "equals": True}, "urgent", 1197),
    ]
    return {
        "id": "knowledge.generated.tobacco-nicotine-counselling", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-tobacco-nicotine-counselling-research",
        "default_refresh": {**default_refresh(), "last_assessed_at": "2026-08-01", "next_monitor_at": "2026-08-02", "next_full_review_at": "2027-01-28"},
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(document):
    safety = [item["fact"]["id"] for item in document["entries"] if item["fact"].get("safety_relevant")]
    core = [
        "tobacco.consultation_goal", "tobacco.information_source", "tobacco.source_reliability",
        "patient.smoking.status", "patient.smoking.product_types", "tobacco.last_use_time",
        "tobacco.home_secondhand_exposure", "tobacco.work_secondhand_exposure",
        "tobacco.pregnancy_or_postpartum_status", "tobacco.relevant_conditions",
        "tobacco.current_medicines", "tobacco.allergies", "tobacco.patient_concern",
        "tobacco.expected_help", "tobacco.additional_comment",
    ]
    return {
        "id": "policy.primary-care-tobacco-nicotine-counselling-completion", "version": VERSION,
        "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": safety + core, "routine": []},
        "conditional_required_facts": [
            {"selector_fact": "patient.smoking.product_types", "cases": {
                "combustible_cigarette": ["patient.smoking.cigarettes_per_day", "patient.smoking.duration_years"],
                "heated_tobacco": ["patient.smoking.duration_years", "tobacco.heated_tobacco_amount"],
                "electronic_cigarette": ["tobacco.electronic_cigarette_status", "tobacco.electronic_cigarette_nicotine_content", "tobacco.electronic_cigarette_amount"],
                "smokeless_tobacco": ["tobacco.smokeless_tobacco_amount"],
                "cigar_or_pipe": [], "other": []}, "default": []},
            {"when": {"fact": "patient.smoking.status", "equals": "current"}, "required_facts": [
                "tobacco.age_at_first_regular_use", "tobacco.time_to_first_use_after_waking", "tobacco.wakes_to_use",
                "tobacco.craving_or_withdrawal", "tobacco.prior_quit_attempt", "tobacco.readiness", "tobacco.target_date", "tobacco.triggers"]},
            {"when": {"fact": "patient.smoking.status", "equals": "former"}, "required_facts": ["patient.smoking.quit_timing", "tobacco.prior_quit_attempt", "tobacco.readiness", "tobacco.triggers"]},
            {"when": {"fact": "tobacco.prior_quit_attempt", "equals": True}, "required_facts": [
                "tobacco.quit_attempt_count", "tobacco.most_recent_quit_attempt", "tobacco.longest_abstinence",
                "tobacco.quit_supports_tried", "tobacco.quit_support_response"]},
        ],
        "clarification_facts_by_rule": {}, "question_budget": {"routine": 45, "clarify": 10},
        "provenance": provenance(SOURCES),
    }


def source_documents():
    artifacts = [
        {"id": SOURCES[0], "kind": "official_clinical_guideline_metadata", "publisher": "NICE", "title": "Tobacco: preventing uptake, promoting quitting and treating dependence", "version": "NG209-current-2025-02-04", "url": "https://www.nice.org.uk/guidance/ng209", "language": "en", "digest": "official_recommendations_verified_2026-08-01", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "nice_guidance", "last_monitored_at": "2026-08-01", "monitor_result": "current"},
        {"id": SOURCES[1], "kind": "official_clinical_guideline_metadata", "publisher": "World Health Organization", "title": "WHO clinical treatment guideline for tobacco cessation in adults", "version": "2024-07-02", "url": "https://www.who.int/publications/i/item/9789240096431", "language": "en", "digest": "official_metadata_and_recommendations_verified_2026-08-01", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-01", "monitor_result": "current"},
        {"id": SOURCES[2], "kind": "official_public_health_guidance_metadata", "publisher": "CDC", "title": "Clinical Interventions to Treat Tobacco Use and Dependence Among Adults", "version": "2024-05-15", "url": "https://www.cdc.gov/tobacco/hcp/patient-care-settings/clinical.html", "language": "en", "digest": "official_guidance_verified_2026-08-01", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-01", "monitor_result": "current"},
        {"id": SOURCES[3], "kind": "official_korean_counselling_service_metadata", "publisher": "Korea Health Promotion Institute", "title": "National No Smoking Guide counselling and nicotine dependence assessment", "version": "current-web-2026-08-01", "url": "https://www.nosmokeguide.go.kr/helpness/counsel", "language": "ko", "digest": "official_counselling_and_assessment_pages_verified_2026-08-01", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-01", "monitor_result": "current"},
        {"id": SOURCES[4], "kind": "terminology_service_verification", "publisher": "STOM", "title": "Tobacco and nicotine terminology verification", "version": "LOINC-2.82_SNOMEDCT-20260701", "url": "http://localhost:8088/fhir", "language": "en", "digest": "loinc_72166-2_67741-9_8663-7_88028-6_105045-9_LL2201-3_LL6587-1_and_snomed_smoking_statuses_verified", "license_status": "licensed_lookup_metadata_only", "complete": False, "monitor_profile": "terminology_server", "last_monitored_at": "2026-08-01", "monitor_result": "verified_active"},
    ]
    research = {"id": "source-manifest.primary-care-tobacco-nicotine-counselling-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance(SOURCES)}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.tobacco-nicotine-counselling", "generated_clinical_knowledge", "knowledge/generated/preventive/tobacco-nicotine-counselling/tobacco-nicotine-counselling.json", True),
        ("source.mapping.tobacco-nicotine-counselling", "terminology_mapping", "mappings/terminology/snomed-mrcm-tobacco-nicotine-counselling.json", False),
        ("source.external.tobacco-nicotine-counselling", "external_source_manifest", "sources/manifests/primary-care-tobacco-nicotine-counselling-research.json", False),
        ("source.policy.tobacco-nicotine-counselling", "runtime_policy", "policies/primary-care-tobacco-nicotine-counselling-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-tobacco-nicotine-counselling", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def routine_state():
    return {
        "tobacco.consultation_goal": {"value": "quit"}, "tobacco.information_source": {"value": "patient"},
        "tobacco.source_reliability": {"value": "reliable"}, "tobacco.severe_chest_pain": {"value": False},
        "tobacco.severe_breathing_difficulty": {"value": False}, "tobacco.collapse_or_reduced_consciousness": {"value": False},
        "tobacco.suspected_acute_nicotine_exposure": {"value": False}, "patient.smoking.status": {"value": "current"},
        "patient.smoking.product_types": {"value": "combustible_cigarette,electronic_cigarette"},
        "tobacco.last_use_time": {"value": "오늘 아침"}, "patient.smoking.cigarettes_per_day": {"value": 10},
        "patient.smoking.duration_years": {"value": 18}, "tobacco.electronic_cigarette_status": {"value": "current_occasional"},
        "tobacco.electronic_cigarette_nicotine_content": {"value": "nicotine"}, "tobacco.electronic_cigarette_amount": {"value": "주 2~3회"},
        "tobacco.age_at_first_regular_use": {"value": 24}, "tobacco.time_to_first_use_after_waking": {"value": "31_to_60_minutes"},
        "tobacco.wakes_to_use": {"value": False}, "tobacco.craving_or_withdrawal": {"value": "오후에 갈망"},
        "tobacco.prior_quit_attempt": {"value": True}, "tobacco.quit_attempt_count": {"value": 2},
        "tobacco.most_recent_quit_attempt": {"value": "6개월 전"}, "tobacco.longest_abstinence": {"value": "3개월"},
        "tobacco.quit_supports_tried": {"value": "상담"}, "tobacco.quit_support_response": {"value": "도움됐으나 재사용"},
        "tobacco.readiness": {"value": "ready_to_quit"}, "tobacco.target_date": {"value": "2주 이내"},
        "tobacco.triggers": {"value": "업무 스트레스"}, "tobacco.home_secondhand_exposure": {"value": False},
        "tobacco.work_secondhand_exposure": {"value": True}, "tobacco.pregnancy_or_postpartum_status": {"value": "not_applicable"},
        "tobacco.relevant_conditions": {"value": "없음"}, "tobacco.current_medicines": {"value": "없음"},
        "tobacco.allergies": {"value": "없음"}, "tobacco.patient_concern": {"value": "의존"},
        "tobacco.expected_help": {"value": "금연계획 상담"}, "tobacco.additional_comment": {"value": "없음"},
    }


def simulations(document):
    cases = {}
    cases["TOBACCO-DUAL-USE-REMOTE-FIRST-VISIT.json"] = {"id": "TOBACCO-DUAL-USE-REMOTE-FIRST-VISIT", "simulation_language": "ko", "persona": {"age": 42}, "encounter_context": {"care_setting": "telemedicine", "encounter_type": "new_encounter", "interview_initiator": "patient", "interview_mode": "video", "available_information": [], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "담배는 가끔 피고 전자담배도 조금 써요. 끊고 싶습니다."}, "hidden_state": routine_state(), "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"patient.smoking.cigarettes_per_day": {"amount": 10, "unit": "{cigarette}/d"}, "tobacco.electronic_cigarette_status": "current_occasional"}, "expected_max_turns": 45, "forbidden_assertions": ["diagnosis.nicotine_dependence", "recommendation.prescribe_medicine"]}, "provenance": provenance(SOURCES)}
    former = routine_state(); former.update({"tobacco.consultation_goal": {"value": "prevent_relapse"}, "patient.smoking.status": {"value": "former"}, "patient.smoking.product_types": {"value": "combustible_cigarette"}, "patient.smoking.quit_timing": {"value": "8개월 전"}, "tobacco.readiness": {"value": "maintain_abstinence"}})
    cases["TOBACCO-FORMER-RELAPSE-PREVENTION.json"] = {"id": "TOBACCO-FORMER-RELAPSE-PREVENTION", "simulation_language": "ko", "persona": {"age": 55}, "initial_statement": {"ko": "금연 8개월째인데 다시 피울까 걱정됩니다."}, "hidden_state": former, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 45, "forbidden_assertions": ["diagnosis.relapse"]}, "provenance": provenance(SOURCES)}
    pregnant = routine_state(); pregnant.update({"patient.smoking.product_types": {"value": "electronic_cigarette"}, "tobacco.pregnancy_or_postpartum_status": {"value": "pregnant"}, "tobacco.electronic_cigarette_status": {"value": "current_daily"}})
    cases["TOBACCO-PREGNANCY-ELECTRONIC-CIGARETTE.json"] = {"id": "TOBACCO-PREGNANCY-ELECTRONIC-CIGARETTE", "simulation_language": "ko", "persona": {"age": 31}, "initial_statement": {"ko": "임신 중인데 전자담배를 매일 사용합니다."}, "hidden_state": pregnant, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"tobacco.pregnancy_or_postpartum_status": "pregnant"}, "expected_max_turns": 45, "forbidden_assertions": ["recommendation.medication_safe_in_pregnancy"]}, "provenance": provenance(SOURCES)}
    absent = routine_state(); absent.pop("patient.smoking.cigarettes_per_day"); absent.pop("tobacco.quit_attempt_count")
    behavior = {"patient.smoking.cigarettes_per_day": {"dataAbsentReason": "asked-unknown"}, "tobacco.quit_attempt_count": {"dataAbsentReason": "asked-declined"}}
    cases["TOBACCO-VAGUE-DATA-ABSENT.json"] = {"id": "TOBACCO-VAGUE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 47}, "initial_statement": {"ko": "피는 양은 들쭉날쭉하고 금연 시도 횟수는 말하고 싶지 않아요."}, "hidden_state": absent, "response_behavior": behavior, "expected": {"expected_data_absent_reasons": {k: v["dataAbsentReason"] for k, v in behavior.items()}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 45, "forbidden_assertions": ["smoking_amount.zero"]}, "provenance": provenance(SOURCES)}
    for key, fact, level in [
        ("SEVERE-CHEST-PAIN", "tobacco.severe_chest_pain", "emergency"),
        ("SEVERE-BREATHING", "tobacco.severe_breathing_difficulty", "emergency"),
        ("COLLAPSE", "tobacco.collapse_or_reduced_consciousness", "emergency"),
        ("ACUTE-NICOTINE-EXPOSURE", "tobacco.suspected_acute_nicotine_exposure", "urgent"),
    ]:
        state = routine_state(); state[fact] = {"value": True}
        rule = {item["when"]["fact"]: item["id"] for item in document["safety_rules"]}[fact]
        cases[f"TOBACCO-{key}.json"] = {"id": f"TOBACCO-{key}", "simulation_language": "ko", "persona": {"age": 38}, "initial_statement": {"ko": "담배나 니코틴 제품 사용 뒤 급성 증상이 있습니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule], "expected_max_turns": 12, "forbidden_assertions": ["diagnosis.nicotine_poisoning"]}, "provenance": provenance(SOURCES)}
    return cases


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Tobacco and Nicotine Counselling", intents=[
        (I[0], "Characterize Tobacco and Nicotine Use"), (I[1], "Screen Tobacco and Nicotine Safety"),
        (I[2], "Assess Dependence and Quit History"), (I[3], "Prepare Tobacco and Nicotine Handoff")])
    primary, research = source_documents()
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"source": "STOM localhost:8088/fhir", "loinc_version": "2.82", "snomed_ct_version": "http://snomed.info/sct/900000000000207008/version/20260701"},
        "verified_loinc_questions": [
            {"fact_id": "patient.smoking.status", "code": "72166-2", "display": "Tobacco smoking status", "relation": "equivalent"},
            {"fact_id": "patient.smoking.duration_years", "code": "67741-9", "display": "Smoking tobacco use duration", "relation": "equivalent"},
            {"fact_id": "tobacco.electronic_cigarette_status", "code": "105045-9", "display": "Electronic cigarette status", "relation": "equivalent"}],
        "verified_official_answer_lists": [
            {"id": "LL2201-3", "title": "Smoking Status", "scope": "official_loinc_answer_list", "preserve_original": True},
            {"id": "LL6587-1", "title": "Electronic cigarette user", "scope": "official_loinc_answer_list", "preserve_original": True}],
        "verified_snomed_answers": [
            {"code": "449868002", "display": "Smokes tobacco daily (finding)", "active": True},
            {"code": "428041000124106", "display": "Occasional tobacco smoker (finding)", "active": True},
            {"code": "8517006", "display": "Ex-smoker (finding)", "active": True},
            {"code": "266919005", "display": "Never smoked tobacco (finding)", "active": True}],
        "atomicity": {"answer_bearing_questions": len(generated["entries"]), "compound_exact_mapping_allowed": False, "product_checklist_is_single_multi_select_dimension": True},
        "validation": {"method": "build_time_local_fhir_lookup", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "provenance": provenance([SOURCES[4]])}
    for path, document in [
        ("knowledge/base/primary-care-tobacco-nicotine-counselling.json", graph),
        ("rules/base/primary-care-tobacco-nicotine-counselling.json", rules),
        ("knowledge/generated/preventive/tobacco-nicotine-counselling/tobacco-nicotine-counselling.json", generated),
        ("mappings/terminology/snomed-mrcm-tobacco-nicotine-counselling.json", mapping),
        ("sources/manifests/primary-care-tobacco-nicotine-counselling.json", primary),
        ("sources/manifests/primary-care-tobacco-nicotine-counselling-research.json", research),
        ("policies/primary-care-tobacco-nicotine-counselling-completion.json", completion(generated)),
    ]:
        write_json(path, document)
    for filename, case in simulations(generated).items():
        write_json(f"simulation/patients/preventive/tobacco-nicotine-counselling/{filename}", case)


if __name__ == "__main__":
    main()
