#!/usr/bin/env python3
"""Materialize a research-only post-discharge transition follow-up package."""
from profile_support import *


P, RFE = "post-discharge-follow-up", "rfe.post_discharge_follow_up"
M = "mapping.terminology.post-discharge-follow-up"
ACQUIRED_AT = "2026-07-31T00:00:00Z"
SOURCES = [
    "source.nice.ng27.transition-discharge.2015-current-20260731",
    "source.ahrq.red-toolkit.current-20260731",
    "source.who.medication-safety-transitions.2019",
    "source.stom.post-discharge.20260731",
]
G = {key: f"group.post_discharge.{key}" for key in (
    "goal", "identity", "safety", "course", "medication", "plan", "support", "handoff"
)}
I = [
    "intent.characterize_post_discharge_transition",
    "intent.screen_post_discharge_safety",
    "intent.reconcile_post_discharge_plan",
    "intent.prepare_post_discharge_handoff",
]


def Q(fact_id, display, value_type, key, wording, score, group, intent, **kwargs):
    return entry(P, fact_id, display, value_type, key, wording, score, key,
                 [G[group]], intents=[intent], **kwargs)


def fragment():
    characterize, safety, reconcile, handoff = I
    entries = [
        Q("post_discharge.follow_up_goal", "Post-discharge Follow-up Goal", "coded", "goal",
          "이번 퇴원 후 확인에서 가장 필요한 것은 증상 변화 확인, 약 확인, 검사·예약 확인, 돌봄·기능 확인 중 무엇인가요?", 250, "goal", characterize,
          allowed_values=["symptom_review", "medication_review", "results_or_appointments", "care_or_function", "combined", "unknown"]),
        Q("post_discharge.discharge_date", "Hospital Discharge Date", "date_or_period", "discharge-date",
          "병원에서 퇴원한 날짜는 언제인가요?", 249, "identity", characterize),
        Q("post_discharge.hospital", "Discharging Hospital", "string", "hospital",
          "어느 의료기관에서 퇴원했나요?", 248, "identity", characterize),
        Q("post_discharge.service", "Discharging Service", "string", "service",
          "입원했던 진료과 또는 병동을 알고 있다면 알려주세요.", 247, "identity", characterize),
        Q("post_discharge.information_source", "Information Source", "coded", "information-source",
          "퇴원 후 정보를 누가 답하고 있나요?", 246, "identity", characterize,
          allowed_values=["patient", "caregiver", "patient_and_caregiver", "record", "unknown"]),
        Q("post_discharge.source_reliability", "Source Reliability", "coded", "source-reliability",
          "답변 내용은 퇴원서류와 확인한 내용인가요, 주로 기억에 따른 내용인가요?", 245, "identity", characterize,
          allowed_values=["document_confirmed", "partly_document_confirmed", "memory_only", "conflicting_sources", "unknown"]),
        Q("post_discharge.discharge_summary_available", "Discharge Summary Availability", "coded", "summary-available",
          "퇴원요약지나 퇴원안내서는 현재 확인할 수 있나요?", 244, "identity", characterize,
          allowed_values=["available_complete", "available_partial", "not_available", "unreadable", "unknown"]),
        Q("post_discharge.admission_reason_reported", "Reported Admission Reason", "string", "admission-reason",
          "입원하게 된 주된 이유를 안내받은 표현 그대로 알려주세요.", 243, "identity", characterize),
        Q("post_discharge.major_treatment_or_procedure", "Major Inpatient Treatment or Procedure", "string", "major-treatment",
          "입원 중 받은 주요 수술·시술·치료가 있다면 알려주세요.", 242, "identity", characterize),

        Q("post_discharge.emergency_return_instruction_received", "Emergency Return Instruction Received", "boolean", "emergency-instruction-received",
          "퇴원할 때 특정 변화가 생기면 즉시 응급실로 가거나 119를 이용하라는 안내를 받았나요?", 240, "plan", reconcile),
        Q("post_discharge.instructed_warning_feature_present", "Instructed Warning Feature Present", "boolean", "instructed-warning-present",
          "퇴원할 때 즉시 진료받으라고 안내받은 변화가 지금 있나요?", 1000, "safety", safety, safety_relevant=True),
        Q("post_discharge.severe_breathing_difficulty", "Severe Breathing Difficulty", "boolean", "severe-breathing",
          "지금 숨쉬기가 매우 어렵거나 말을 이어가기 힘든가요?", 999, "safety", safety, safety_relevant=True),
        Q("post_discharge.new_severe_chest_pain", "New Severe Chest Pain", "boolean", "severe-chest-pain",
          "퇴원 후 새로 생긴 심한 가슴 통증이 지금 있나요?", 998, "safety", safety, safety_relevant=True),
        Q("post_discharge.collapse_or_reduced_consciousness", "Collapse or Reduced Consciousness", "boolean", "collapse-consciousness",
          "퇴원 후 쓰러졌거나 깨우기 어렵고 의식이 평소보다 뚜렷하게 떨어진 적이 있나요?", 997, "safety", safety, safety_relevant=True),
        Q("post_discharge.new_focal_neurologic_change", "New Focal Neurologic Change", "boolean", "focal-neurologic-change",
          "퇴원 후 한쪽 힘 빠짐, 얼굴 처짐 또는 갑작스러운 말하기 어려움이 새로 생겼나요?", 996, "safety", safety, safety_relevant=True),
        Q("post_discharge.uncontrolled_bleeding", "Uncontrolled Bleeding", "boolean", "uncontrolled-bleeding",
          "현재 눌러도 멈추지 않는 출혈이나 많은 양의 피가 보이나요?", 995, "safety", safety, safety_relevant=True),
        Q("post_discharge.rapid_deterioration", "Rapid Clinical Deterioration", "boolean", "rapid-deterioration",
          "퇴원 후 전반적인 상태가 빠르게 나빠지고 있나요?", 994, "safety", safety, safety_relevant=True),
        Q("post_discharge.essential_medicine_unavailable", "Essential Medicine Unavailable", "boolean", "essential-medicine-unavailable",
          "퇴원 시 반드시 계속 복용하라고 한 약을 구하지 못해 현재 복용할 수 없는 상태인가요?", 993, "safety", safety, safety_relevant=True),

        Q("post_discharge.overall_course", "Overall Course Since Discharge", "coded", "overall-course",
          "퇴원할 때와 비교해 전반적인 상태는 좋아짐, 비슷함, 나빠짐 중 어느 쪽인가요?", 230, "course", handoff,
          allowed_values=["improving", "unchanged", "worsening", "fluctuating", "unknown"]),
        Q("post_discharge.new_or_worsened_symptom_present", "New or Worsened Symptom Present", "boolean", "new-symptom-present",
          "퇴원 후 새로 생기거나 더 심해진 증상이 있나요?", 229, "course", handoff),
        Q("post_discharge.new_or_worsened_symptom", "New or Worsened Symptom", "string", "new-symptom",
          "새로 생기거나 더 심해진 증상을 하나씩 알려주세요.", 228, "course", handoff),
        Q("post_discharge.symptom_onset", "Post-discharge Symptom Onset", "date_or_period", "symptom-onset",
          "그 변화는 퇴원 후 언제 시작되었나요?", 227, "course", handoff),
        Q("post_discharge.current_pain_present", "Current Pain Present", "boolean", "current-pain-present",
          "현재 통증이 있나요?", 226, "course", handoff),
        Q("post_discharge.pain_nrs", "Current Pain NRS", "integer", "pain-nrs",
          "현재 통증은 0점부터 10점 중 몇 점인가요?", 225, "course", handoff,
          minimum=0, maximum=10),
        Q("post_discharge.function_change", "Function Compared with Discharge", "coded", "function-change",
          "걷기, 씻기, 옷 입기, 식사 같은 일상 기능은 퇴원할 때보다 좋아졌나요, 비슷한가요, 나빠졌나요?", 226, "course", handoff,
          allowed_values=["improving", "unchanged", "worsening", "dependent", "unknown"]),
        Q("post_discharge.oral_intake", "Oral Intake", "coded", "oral-intake",
          "음식과 물을 먹고 마시는 양은 평소와 비교해 어떤가요?", 225, "course", handoff,
          allowed_values=["usual", "reduced", "minimal_or_none", "tube_or_assisted", "unknown"]),
        Q("post_discharge.urine_change", "Urine Output Change", "coded", "urine-change",
          "소변 양이나 횟수가 퇴원 후 평소보다 줄었나요?", 224, "course", handoff,
          allowed_values=["no_change", "reduced", "markedly_reduced", "unable_to_assess", "unknown"]),

        Q("post_discharge.discharge_medicine_list_available", "Discharge Medicine List Available", "boolean", "medicine-list-available",
          "퇴원약 목록이나 처방전을 현재 확인할 수 있나요?", 220, "medication", reconcile),
        Q("post_discharge.actual_current_medicines", "Actual Current Medicines", "string", "actual-current-medicines",
          "퇴원 후 실제로 복용 중인 약을 처방약, 일반약, 건강기능식품을 포함해 알려주세요.", 219, "medication", reconcile),
        Q("post_discharge.medicine_changes_understood", "Medicine Changes Understood", "coded", "medicine-changes-understood",
          "입원 전과 비교해 시작·중단·용량 변경된 약을 본인이나 보호자가 알고 있나요?", 218, "medication", reconcile,
          allowed_values=["understood", "partly_understood", "not_understood", "no_changes_reported", "unknown"]),
        Q("post_discharge.medicine_discrepancy", "Medicine List Discrepancy", "string", "medicine-discrepancy",
          "퇴원서류의 약 목록과 실제 복용이 다르다면 어떤 약이 어떻게 다른가요?", 217, "medication", reconcile),
        Q("post_discharge.medicine_access_problem", "Medicine Access Problem", "string", "medicine-access",
          "비용, 재고, 처방, 이동 문제로 구하지 못한 퇴원약이 있나요?", 216, "medication", reconcile),
        Q("post_discharge.suspected_medicine_effect", "Suspected Medicine Effect", "string", "suspected-medicine-effect",
          "퇴원 후 약을 복용하면서 새로 생겼다고 생각되는 불편감이 있나요?", 215, "medication", reconcile),
        Q("post_discharge.medicine_instruction_conflict", "Medicine Instruction Conflict", "string", "medicine-instruction-conflict",
          "병원, 기존 처방기관, 약국의 복용 안내가 서로 다르다면 각각 어떻게 안내받았나요?", 214, "medication", reconcile),

        Q("post_discharge.pending_tests_present", "Pending Tests or Results Present", "boolean", "pending-tests-present",
          "퇴원할 때 아직 결과가 나오지 않았다고 들은 검사나 조직검사가 있나요?", 211, "plan", reconcile),
        Q("post_discharge.pending_tests", "Pending Tests or Results", "string", "pending-tests",
          "결과가 남아 있는 검사나 조직검사를 알려주세요.", 210, "plan", reconcile),
        Q("post_discharge.pending_result_owner", "Pending Result Follow-up Owner", "string", "pending-result-owner",
          "미결 검사결과를 누가 언제 확인해 주기로 했나요?", 209, "plan", reconcile),
        Q("post_discharge.follow_up_appointment_present", "Follow-up Appointment Present", "boolean", "follow-up-appointment-present",
          "예약된 외래, 검사, 방문간호 또는 재활 일정이 있나요?", 208, "plan", reconcile),
        Q("post_discharge.follow_up_appointments", "Follow-up Appointments", "string", "follow-up-appointments",
          "예약된 일정의 종류와 날짜를 알려주세요.", 207, "plan", reconcile),
        Q("post_discharge.appointment_access_barrier", "Appointment Access Barrier", "string", "appointment-barrier",
          "예약에 참석하기 어려운 교통, 비용, 언어, 돌봄 또는 디지털 접근 문제가 있나요?", 207, "plan", reconcile),
        Q("post_discharge.wound_or_device_plan", "Wound or Device Plan", "string", "wound-device-plan",
          "상처, 배액관, 도뇨관, 산소 또는 다른 기기가 있다면 현재 관리 방법과 문제를 알려주세요.", 206, "plan", reconcile),
        Q("post_discharge.home_service_or_equipment", "Home Service or Equipment", "string", "home-service-equipment",
          "퇴원 후 제공받기로 한 방문간호, 재활, 돌봄서비스 또는 의료장비가 예정대로 준비됐나요?", 205, "support", reconcile),
        Q("post_discharge.caregiver_support", "Caregiver Support", "coded", "caregiver-support",
          "집에서 필요한 도움을 줄 사람이 실제로 가능한가요?", 204, "support", reconcile,
          allowed_values=["available_sufficient", "available_insufficient", "not_available", "not_needed", "unknown"]),
        Q("post_discharge.contact_for_problem", "Post-discharge Contact", "coded", "problem-contact",
          "퇴원 후 문제가 생겼을 때 연락할 의료기관이나 담당자를 알고 있나요?", 203, "support", reconcile,
          allowed_values=["known_and_reachable", "known_not_reachable", "not_known", "unknown"]),
        Q("post_discharge.plan_understanding", "Discharge Plan Understanding", "coded", "plan-understanding",
          "환자나 보호자가 퇴원 후 해야 할 일과 주의할 변화를 어느 정도 이해하고 있나요?", 202, "support", reconcile,
          allowed_values=["understood", "partly_understood", "not_understood", "conflicting_information", "unknown"]),
        Q("post_discharge.patient_concern", "Patient or Caregiver Concern", "string", "patient-concern",
          "퇴원 후 가장 걱정되는 한 가지는 무엇인가요?", 100, "handoff", handoff),
        Q("post_discharge.expected_help", "Expected Help", "string", "expected-help",
          "이번 진료에서 의료진에게 가장 받고 싶은 도움은 무엇인가요?", 99, "handoff", handoff),
        Q("post_discharge.additional_comment", "Additional Comment", "string", "additional-comment",
          "질문에 없지만 의료진에게 추가로 전달할 내용이 있나요?", 90, "handoff", handoff),
    ]
    rules = [
        safety_rule(P, "instructed-warning-present", {"fact": "post_discharge.instructed_warning_feature_present", "equals": True}, "emergency", 1200),
        safety_rule(P, "severe-breathing", {"fact": "post_discharge.severe_breathing_difficulty", "equals": True}, "emergency", 1199),
        safety_rule(P, "severe-chest-pain", {"fact": "post_discharge.new_severe_chest_pain", "equals": True}, "emergency", 1198),
        safety_rule(P, "collapse-consciousness", {"fact": "post_discharge.collapse_or_reduced_consciousness", "equals": True}, "emergency", 1197),
        safety_rule(P, "focal-neurologic-change", {"fact": "post_discharge.new_focal_neurologic_change", "equals": True}, "emergency", 1196),
        safety_rule(P, "uncontrolled-bleeding", {"fact": "post_discharge.uncontrolled_bleeding", "equals": True}, "emergency", 1195),
        safety_rule(P, "rapid-deterioration", {"fact": "post_discharge.rapid_deterioration", "equals": True}, "urgent", 1194),
        safety_rule(P, "essential-medicine-unavailable", {"fact": "post_discharge.essential_medicine_unavailable", "equals": True}, "urgent", 1193),
    ]
    return {
        "id": "knowledge.generated.post-discharge-follow-up", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-post-discharge-follow-up-research",
        "default_refresh": {**default_refresh(), "last_assessed_at": "2026-07-31", "next_monitor_at": "2026-08-01", "next_full_review_at": "2027-01-27"},
        "terminology_reference": {
            "record_title": {"system": "http://loinc.org", "code": "11544-4", "display": "Hospital discharge follow-up Narrative", "version": "2.82", "relation": "record_title_not_question_exact"},
            "discharge_event": {"system": "http://snomed.info/sct", "code": "308283009", "display": "Discharge from hospital (procedure)", "version": "http://snomed.info/sct/900000000000207008/version/20260701", "relation": "context_event"},
        },
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(document):
    core = [
        "post_discharge.follow_up_goal", "post_discharge.discharge_date",
        "post_discharge.hospital", "post_discharge.information_source",
        "post_discharge.source_reliability", "post_discharge.discharge_summary_available",
        "post_discharge.admission_reason_reported",
        "post_discharge.emergency_return_instruction_received",
        "post_discharge.overall_course",
        "post_discharge.new_or_worsened_symptom_present",
        "post_discharge.discharge_medicine_list_available",
        "post_discharge.actual_current_medicines", "post_discharge.medicine_changes_understood",
        "post_discharge.pending_tests_present",
        "post_discharge.follow_up_appointment_present", "post_discharge.caregiver_support",
        "post_discharge.contact_for_problem", "post_discharge.plan_understanding",
        "post_discharge.patient_concern", "post_discharge.expected_help",
        "post_discharge.additional_comment",
    ]
    safety = [item["fact"]["id"] for item in document["entries"] if item["fact"].get("safety_relevant")]
    return {
        "id": "policy.primary-care-post-discharge-follow-up-completion", "version": VERSION,
        "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": safety + core, "routine": []},
        "conditional_required_facts": [
            {"when": {"fact": "post_discharge.discharge_summary_available", "in": ["available_partial", "not_available", "unreadable", "unknown"]}, "required_facts": ["post_discharge.service", "post_discharge.major_treatment_or_procedure"], "reason": "incomplete_discharge_document_context"},
            {"when": {"fact": "post_discharge.new_or_worsened_symptom_present", "equals": True}, "required_facts": ["post_discharge.new_or_worsened_symptom", "post_discharge.symptom_onset", "post_discharge.current_pain_present", "post_discharge.function_change", "post_discharge.oral_intake", "post_discharge.urine_change"], "reason": "new_or_worsened_post_discharge_symptom"},
            {"when": {"fact": "post_discharge.current_pain_present", "equals": True}, "required_facts": ["post_discharge.pain_nrs"], "reason": "current_pain_severity"},
            {"when": {"fact": "post_discharge.discharge_medicine_list_available", "equals": True}, "required_facts": ["post_discharge.medicine_discrepancy", "post_discharge.medicine_access_problem", "post_discharge.suspected_medicine_effect", "post_discharge.medicine_instruction_conflict"], "reason": "medication_reconciliation"},
            {"when": {"fact": "post_discharge.pending_tests_present", "equals": True}, "required_facts": ["post_discharge.pending_tests", "post_discharge.pending_result_owner"], "reason": "pending_result_handoff"},
            {"when": {"fact": "post_discharge.follow_up_appointment_present", "equals": True}, "required_facts": ["post_discharge.follow_up_appointments", "post_discharge.appointment_access_barrier"], "reason": "appointment_feasibility"},
        ],
        "clarification_facts_by_rule": {}, "question_budget": {"routine": 40, "clarify": 10},
        "provenance": provenance(SOURCES),
    }


def source_documents():
    artifacts = [
        {"id": SOURCES[0], "kind": "official_clinical_guideline_metadata", "publisher": "NICE", "title": "Transition between inpatient hospital settings and community or care home settings for adults with social care needs", "version": "NG27", "url": "https://www.nice.org.uk/guidance/ng27", "language": "en", "digest": "official_metadata_and_recommendations_verified_2026-07-31", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "nice_guidance", "last_monitored_at": "2026-07-31", "monitor_result": "current_no_revision_notice"},
        {"id": SOURCES[1], "kind": "official_patient_safety_toolkit_metadata", "publisher": "AHRQ", "title": "Re-Engineered Discharge (RED) Toolkit", "version": "current-web-2026-07-31", "url": "https://www.ahrq.gov/patient-safety/settings/hospital/red/toolkit/index.html", "language": "en", "digest": "official_metadata_and_selected_components_verified_2026-07-31", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-07-31", "monitor_result": "current"},
        {"id": SOURCES[2], "kind": "official_patient_safety_report_metadata", "publisher": "World Health Organization", "title": "Medication safety in transitions of care", "version": "WHO/UHC/SDS/2019.9", "url": "https://www.who.int/publications/i/item/WHO-UHC-SDS-2019.9", "language": "en", "digest": "official_metadata_verified_2026-07-31", "license_status": "metadata_only_review_required", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-07-31", "monitor_result": "current_publication"},
        {"id": SOURCES[3], "kind": "terminology_service_verification", "publisher": "STOM", "title": "Post-discharge terminology verification", "version": "LOINC-2.82_SNOMEDCT-20260701", "url": "http://localhost:8088/fhir", "language": "en", "digest": "loinc-11544-4_and_snomed-308283009_lookup_verified", "license_status": "licensed_lookup_metadata_only", "complete": False, "monitor_profile": "terminology_server", "last_monitored_at": "2026-07-31", "monitor_result": "verified_active"},
    ]
    research = {"id": "source-manifest.primary-care-post-discharge-follow-up-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance(SOURCES)}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.post-discharge-follow-up", "generated_clinical_knowledge", "knowledge/generated/follow-up/post-discharge/post-discharge-follow-up.json", True),
        ("source.mapping.post-discharge-follow-up", "terminology_mapping", "mappings/terminology/snomed-mrcm-post-discharge-follow-up.json", False),
        ("source.external.post-discharge-follow-up", "external_source_manifest", "sources/manifests/primary-care-post-discharge-follow-up-research.json", False),
        ("source.policy.post-discharge-follow-up", "runtime_policy", "policies/primary-care-post-discharge-follow-up-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-post-discharge-follow-up", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def routine_state():
    return {
        "post_discharge.follow_up_goal": {"value": "combined"},
        "post_discharge.discharge_date": {"value": "2026-07-29"},
        "post_discharge.hospital": {"value": "합성 의료기관"},
        "post_discharge.service": {"value": "합성 진료과"},
        "post_discharge.information_source": {"value": "patient"},
        "post_discharge.source_reliability": {"value": "document_confirmed"},
        "post_discharge.discharge_summary_available": {"value": "available_complete"},
        "post_discharge.admission_reason_reported": {"value": "퇴원요약지에 적힌 합성 입원 사유"},
        "post_discharge.major_treatment_or_procedure": {"value": "입원 중 시행한 합성 치료"},
        "post_discharge.emergency_return_instruction_received": {"value": True},
        "post_discharge.instructed_warning_feature_present": {"value": False},
        "post_discharge.severe_breathing_difficulty": {"value": False},
        "post_discharge.new_severe_chest_pain": {"value": False},
        "post_discharge.collapse_or_reduced_consciousness": {"value": False},
        "post_discharge.new_focal_neurologic_change": {"value": False},
        "post_discharge.uncontrolled_bleeding": {"value": False},
        "post_discharge.rapid_deterioration": {"value": False},
        "post_discharge.essential_medicine_unavailable": {"value": False},
        "post_discharge.overall_course": {"value": "improving"},
        "post_discharge.new_or_worsened_symptom_present": {"value": False},
        "post_discharge.current_pain_present": {"value": False},
        "post_discharge.discharge_medicine_list_available": {"value": True},
        "post_discharge.actual_current_medicines": {"value": "퇴원약 목록과 동일"},
        "post_discharge.medicine_changes_understood": {"value": "understood"},
        "post_discharge.medicine_discrepancy": {"value": "없음"},
        "post_discharge.medicine_access_problem": {"value": "없음"},
        "post_discharge.suspected_medicine_effect": {"value": "없음"},
        "post_discharge.medicine_instruction_conflict": {"value": "없음"},
        "post_discharge.pending_tests_present": {"value": False},
        "post_discharge.follow_up_appointment_present": {"value": True},
        "post_discharge.follow_up_appointments": {"value": "일주일 뒤 외래"},
        "post_discharge.appointment_access_barrier": {"value": "없음"},
        "post_discharge.caregiver_support": {"value": "available_sufficient"},
        "post_discharge.contact_for_problem": {"value": "known_and_reachable"},
        "post_discharge.plan_understanding": {"value": "understood"},
        "post_discharge.patient_concern": {"value": "회복 경과"},
        "post_discharge.expected_help": {"value": "퇴원계획 확인"},
        "post_discharge.additional_comment": {"value": "없음"},
    }


def simulations(document):
    cases = {}
    cases["POST-DISCHARGE-ROUTINE-DOCUMENT-CONFIRMED.json"] = {"id": "POST-DISCHARGE-ROUTINE-DOCUMENT-CONFIRMED", "simulation_language": "ko", "persona": {"age": 58}, "initial_statement": {"ko": "이틀 전 퇴원해서 외래 전 문진을 작성합니다."}, "hidden_state": routine_state(), "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.readmission_required", "recommendation.change_medicine"]}, "provenance": provenance(SOURCES)}
    for key, fact, level in [
        ("INSTRUCTED-WARNING", "post_discharge.instructed_warning_feature_present", "emergency"),
        ("SEVERE-BREATHING", "post_discharge.severe_breathing_difficulty", "emergency"),
        ("SEVERE-CHEST-PAIN", "post_discharge.new_severe_chest_pain", "emergency"),
        ("COLLAPSE", "post_discharge.collapse_or_reduced_consciousness", "emergency"),
        ("FOCAL-NEUROLOGY", "post_discharge.new_focal_neurologic_change", "emergency"),
        ("UNCONTROLLED-BLEEDING", "post_discharge.uncontrolled_bleeding", "emergency"),
        ("RAPID-DETERIORATION", "post_discharge.rapid_deterioration", "urgent"),
        ("ESSENTIAL-MEDICINE-UNAVAILABLE", "post_discharge.essential_medicine_unavailable", "urgent"),
    ]:
        state = routine_state(); state[fact] = {"value": True}
        rule = {item["when"]["fact"]: item["id"] for item in document["safety_rules"]}[fact]
        cases[f"POST-DISCHARGE-{key}.json"] = {"id": f"POST-DISCHARGE-{key}", "simulation_language": "ko", "persona": {"age": 67}, "initial_statement": {"ko": "퇴원 후 상태 변화가 있어 확인이 필요합니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule], "expected_max_turns": 16, "forbidden_assertions": ["diagnosis.post_discharge_complication"]}, "provenance": provenance(SOURCES)}
    conflict = routine_state(); conflict.update({"post_discharge.information_source": {"value": "patient_and_caregiver"}, "post_discharge.source_reliability": {"value": "conflicting_sources"}, "post_discharge.medicine_discrepancy": {"value": "퇴원지에는 중단, 기존 약봉투에는 계속 복용으로 상충"}, "post_discharge.medicine_instruction_conflict": {"value": "병원과 기존 의원 안내가 다름"}})
    cases["POST-DISCHARGE-PROXY-MEDICINE-CONFLICT.json"] = {"id": "POST-DISCHARGE-PROXY-MEDICINE-CONFLICT", "simulation_language": "ko", "persona": {"age": 81}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "follow_up", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["discharge_summary"], "time_constraint": "scheduled", "clinical_responsibility": "follow_up_support"}, "initial_statement": {"ko": "어머니 퇴원약이 달라 보여 보호자가 전화로 답합니다."}, "hidden_state": conflict, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"post_discharge.medicine_discrepancy": "퇴원지에는 중단, 기존 약봉투에는 계속 복용으로 상충"}, "expected_max_turns": 40, "forbidden_assertions": ["recommendation.stop_medicine", "silent_conflict_overwrite"]}, "provenance": provenance(SOURCES)}
    absent = routine_state(); absent.pop("post_discharge.pending_tests_present"); absent.pop("post_discharge.follow_up_appointment_present")
    behavior = {"post_discharge.pending_tests_present": {"dataAbsentReason": "asked-unknown"}, "post_discharge.follow_up_appointment_present": {"dataAbsentReason": "asked-unknown"}}
    cases["POST-DISCHARGE-MISSING-DOCUMENT-DATA-ABSENT.json"] = {"id": "POST-DISCHARGE-MISSING-DOCUMENT-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 49}, "initial_statement": {"ko": "퇴원서류를 잃어버려 미결 검사와 예약을 모르겠습니다."}, "hidden_state": absent, "response_behavior": behavior, "expected": {"expected_data_absent_reasons": {k: v["dataAbsentReason"] for k, v in behavior.items()}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 40, "forbidden_assertions": ["pending_results_none", "appointments_none"]}, "provenance": provenance(SOURCES)}
    multi = routine_state(); multi["post_discharge.additional_comment"] = {"value": "퇴원 추적 외에 새 두통도 별도 문진 요청"}
    cases["POST-DISCHARGE-MULTI-RFE-HEADACHE.json"] = {"id": "POST-DISCHARGE-MULTI-RFE-HEADACHE", "simulation_language": "ko", "persona": {"age": 44}, "initial_statement": {"ko": "퇴원 후 확인과 새로 생긴 두통 상담도 원합니다."}, "hidden_state": multi, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"post_discharge.additional_comment": "퇴원 추적 외에 새 두통도 별도 문진 요청"}, "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.migraine", "merge_rfe.silently"]}, "provenance": provenance(SOURCES)}
    return cases


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Post-discharge Follow-up", intents=[
        (I[0], "Characterize Post-discharge Transition"),
        (I[1], "Screen Post-discharge Safety"),
        (I[2], "Reconcile Discharge Medicines Plans and Support"),
        (I[3], "Prepare Post-discharge Clinician Handoff"),
    ])
    primary, research = source_documents()
    mapping = {
        "id": M,
        "version": VERSION,
        "status": "research_only",
        "review_status": "unreviewed",
        "terminology": {
            "source": "STOM localhost:8088/fhir",
            "loinc_version": "2.82",
            "snomed_ct_version": "http://snomed.info/sct/900000000000207008/version/20260701",
        },
        "verified_loinc_record_titles": [
            {
                "code": "11544-4",
                "display": "Hospital discharge follow-up Narrative",
                "relation": "record_title_not_question_exact",
                "version": "2.82",
            }
        ],
        "verified_snomed_context_concepts": [
            {
                "code": "308283009",
                "display": "Discharge from hospital (procedure)",
                "relation": "context_event",
                "active": True,
            }
        ],
        "question_mapping": {
            "exact_standard_question_count": 0,
            "local_atomic_question_count": len(generated["entries"]),
            "compound_question_exact_mapping_allowed": False,
            "rationale": "The verified LOINC code is a record title, not an exact match for any individual answer-bearing question.",
        },
        "validation": {
            "method": "build_time_local_fhir_lookup",
            "checked_at": ACQUIRED_AT,
            "raw_response_cached": False,
            "clinical_rule_authority": False,
            "question_equivalence_inferred": False,
            "result": "provisional_pass",
        },
        "provenance": provenance(["source.stom.post-discharge.20260731"]),
    }
    for path, document in [
        ("knowledge/base/primary-care-post-discharge-follow-up.json", graph),
        ("rules/base/primary-care-post-discharge-follow-up.json", rules),
        ("knowledge/generated/follow-up/post-discharge/post-discharge-follow-up.json", generated),
        ("mappings/terminology/snomed-mrcm-post-discharge-follow-up.json", mapping),
        ("sources/manifests/primary-care-post-discharge-follow-up.json", primary),
        ("sources/manifests/primary-care-post-discharge-follow-up-research.json", research),
        ("policies/primary-care-post-discharge-follow-up-completion.json", completion(generated)),
    ]:
        write_json(path, document)
    for filename, case in simulations(generated).items():
        write_json(f"simulation/patients/follow-up/post-discharge/{filename}", case)


if __name__ == "__main__":
    main()
