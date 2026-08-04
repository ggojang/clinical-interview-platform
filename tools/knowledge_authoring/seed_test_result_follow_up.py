#!/usr/bin/env python3
"""Materialize a purpose-specific test-result follow-up interview package."""
from profile_support import *

P, RFE = "test-result-follow-up", "rfe.test_result_follow_up"
ACQUIRED_AT = "2026-08-04T18:01:12Z"
SOURCES = [
    "source.hl7.fhir-r4.diagnosticreport",
    "source.hl7.fhir-r4.observation",
    "source.uscdi.v6.2025",
    "source.ahrq.follow-up-with-patients-tool6.2024",
    "source.ahrq.diagnostic-safety-current-state.2023",
    "source.acsqhc.pathology-information-communication-reporting.2026",
    "source.stom.test-result-follow-up.20260804",
    "policy.encounter-context-review",
]
G = {
    key: f"group.result.{key}"
    for key in ("goal", "safety", "identity", "content", "context", "handoff")
}
C = ["intent.characterize_result_follow_up"]
S = ["intent.screen_result_follow_up_safety"]
H = ["intent.prepare_result_clinician_handoff"]


def Q(
    fact_id,
    display,
    value_type,
    key,
    wording,
    score,
    groups,
    intents,
    **kwargs,
):
    return entry(
        P,
        fact_id,
        display,
        value_type,
        key,
        wording,
        score,
        key,
        groups,
        intents=intents,
        **kwargs,
    )


def fragment():
    entries = [
        Q(
            "encounter.result_follow_up.goal",
            "Result Follow-up Goal",
            "coded",
            "goal",
            "오늘은 의료기관에서 검사결과를 확인하려는 것인가요, 검사결과의 판독·설명을 원하는 것인가요, 아니면 둘 다인가요?",
            240,
            [G["goal"]],
            C,
            allowed_values=[
                "institution_result_check",
                "interpretation_request",
                "both",
                "unknown",
            ],
        ),
        Q(
            "result.explicit_emergency_instruction",
            "Explicit Emergency Instruction",
            "boolean",
            "emergency-instruction",
            "의료기관에서 이 결과 때문에 지금 즉시 응급실로 가거나 119를 이용하라고 명확히 안내했나요?",
            239,
            [G["safety"]],
            S,
            safety_relevant=True,
        ),
        Q(
            "result.urgent_follow_up_instruction",
            "Explicit Urgent Follow-up Instruction",
            "boolean",
            "urgent-instruction",
            "의료기관에서 이 결과를 오늘 또는 매우 빠른 시일 안에 반드시 확인하라고 안내했나요?",
            238,
            [G["safety"]],
            S,
            safety_relevant=True,
        ),
        Q(
            "result.current_severe_symptom",
            "Current Severe Symptom",
            "boolean",
            "severe-current-symptom",
            "검사 이후 새로 생긴 심한 증상이 현재 있나요?",
            237,
            [G["safety"]],
            S,
            safety_relevant=True,
        ),
        Q(
            "result.rapidly_worsening_symptom",
            "Rapidly Worsening Symptom",
            "boolean",
            "rapidly-worsening-symptom",
            "검사 이후 증상이 빠르게 악화하고 있나요?",
            236,
            [G["safety"]],
            S,
            safety_relevant=True,
        ),
        Q(
            "result.abnormal_notice",
            "Abnormal Result Notice",
            "boolean",
            "abnormal-notice",
            "의료기관에서 결과가 비정상 또는 이상 소견이라고 통보했나요?",
            230,
            [G["safety"], G["context"]],
            H,
        ),
        Q(
            "result.new_concern",
            "New Concern Related to Result",
            "boolean",
            "new-concern",
            "검사결과와 관련해 새 증상이나 새로 걱정되는 변화가 있나요?",
            229,
            [G["safety"], G["context"]],
            H,
        ),
        Q(
            "result.related_symptoms",
            "Current Symptoms Related to Result",
            "string",
            "related-symptoms",
            "새 증상이나 변화가 있다면 무엇인지 알려주세요.",
            228,
            [G["safety"], G["context"]],
            H,
        ),
        Q(
            "result.related_symptom_onset",
            "Related Symptom Onset",
            "date_or_period",
            "related-symptom-onset",
            "그 증상이나 변화는 언제 시작되었나요?",
            227,
            [G["safety"], G["context"]],
            H,
        ),
        Q(
            "result.related_symptom_severity",
            "Related Symptom Severity",
            "string",
            "related-symptom-severity",
            "그 증상이나 변화의 현재 심한 정도를 알려주세요.",
            226,
            [G["safety"], G["context"]],
            H,
        ),
        Q(
            "result.patient_question",
            "Patient Question",
            "string",
            "patient-question",
            "이번 결과 확인에서 의료진에게 가장 확인하고 싶은 점은 무엇인가요?",
            220,
            [G["goal"], G["handoff"]],
            H,
        ),
        Q(
            "result.expected_outcome",
            "Expected Outcome",
            "string",
            "expected-outcome",
            "이번 결과 확인을 통해 원하는 도움은 무엇인가요?",
            219,
            [G["goal"], G["handoff"]],
            H,
        ),
        Q(
            "result.content.available",
            "Result Content Availability",
            "coded",
            "content-available",
            "실제 결과 내용은 현재 대화에 제공되어 있나요, 의료기관에만 있나요, 또는 현재 확인할 수 없나요?",
            210,
            [G["content"]],
            C,
            allowed_values=[
                "provided_in_conversation",
                "available_at_institution",
                "not_available",
                "unknown",
            ],
        ),
        Q(
            "result.test.category",
            "Test Category",
            "coded",
            "test-category",
            "확인하려는 것은 혈액·소변 등 검사, 영상검사, 병리검사, 시술·기능검사, 그 밖의 검사 중 무엇인가요?",
            209,
            [G["identity"]],
            H,
            allowed_values=[
                "laboratory",
                "diagnostic_imaging",
                "pathology",
                "procedure_or_function_test",
                "other",
                "unknown",
            ],
        ),
        Q(
            "result.test.name",
            "Test or Report Name",
            "coded_or_string",
            "test-name",
            "검사명 또는 보고서명을 원문에 적힌 그대로 알려주세요.",
            208,
            [G["identity"]],
            H,
        ),
        Q(
            "result.test.performed_at",
            "Clinically Relevant Test Time",
            "date_or_period",
            "performed-at",
            "검사를 시행한 날짜를 알려주세요.",
            207,
            [G["identity"]],
            H,
        ),
        Q(
            "result.report.issued_at",
            "Report Issued Time",
            "datetime",
            "issued-at",
            "결과 보고서가 발행된 날짜와 시각이 적혀 있다면 알려주세요.",
            206,
            [G["identity"]],
            H,
        ),
        Q(
            "result.report.status",
            "Report Status",
            "coded",
            "report-status",
            "보고서 상태가 예비, 최종, 수정 또는 취소 중 무엇으로 표시되어 있나요?",
            205,
            [G["identity"]],
            H,
            allowed_values=[
                "registered",
                "partial",
                "preliminary",
                "final",
                "amended",
                "corrected",
                "appended",
                "cancelled",
                "entered-in-error",
                "unknown",
            ],
        ),
        Q(
            "result.report.version_or_amendment",
            "Report Version or Amendment",
            "string",
            "report-version",
            "수정·정정된 보고서라면 버전, 정정 날짜 또는 변경되었다고 표시된 내용을 알려주세요.",
            204,
            [G["identity"]],
            H,
        ),
        Q(
            "result.performing_organization",
            "Performing Organization",
            "string_or_reference",
            "performing-organization",
            "검사를 시행하거나 보고서를 발행한 의료기관을 알려주세요.",
            203,
            [G["identity"]],
            H,
        ),
        Q(
            "result.test.clinical_reason",
            "Clinical Reason for Test",
            "string",
            "clinical-reason",
            "이 검사를 시행한 이유나 확인하려던 증상·질문을 알고 있다면 알려주세요.",
            202,
            [G["identity"], G["context"]],
            H,
        ),
        Q(
            "result.test_requester",
            "Test Requester",
            "string_or_reference",
            "ordering-clinician",
            "검사를 요청한 의료진이나 진료과가 보고서에 적혀 있다면 알려주세요.",
            201,
            [G["identity"], G["handoff"]],
            H,
        ),
        Q(
            "result.results_interpreter",
            "Result Interpreter",
            "string_or_reference",
            "results-interpreter",
            "결과를 판독한 의료진이나 부서가 적혀 있다면 알려주세요.",
            200,
            [G["identity"], G["handoff"]],
            H,
        ),
        Q(
            "result.report.source",
            "Result Information Source",
            "coded",
            "report-source",
            "현재 결과 정보는 본인 기억, 보호자 설명, 업로드 문서, 진료기록 또는 의료기관 포털 중 어디에서 확인한 것인가요?",
            199,
            [G["identity"], G["handoff"]],
            H,
            allowed_values=[
                "patient_report",
                "proxy_report",
                "uploaded_document",
                "clinical_record",
                "institution_portal",
                "unknown",
            ],
        ),
        Q(
            "result.report.readability",
            "Report Readability and Completeness",
            "coded",
            "report-readability",
            "제공된 보고서는 전체가 읽을 수 있나요, 일부만 보이나요, 읽기 어렵거나 제공되지 않았나요?",
            198,
            [G["content"]],
            H,
            allowed_values=[
                "complete_readable",
                "partial",
                "unreadable",
                "not_provided",
                "unknown",
            ],
        ),
        Q(
            "result.value.summary",
            "Reported Values or Findings",
            "string",
            "value-summary",
            "보고서에 적힌 수치 또는 소견을 원문 그대로 알려주세요.",
            190,
            [G["content"]],
            H,
        ),
        Q(
            "result.value.units",
            "Reported Result Units",
            "string",
            "value-units",
            "수치 옆에 적힌 단위를 원문 그대로 알려주세요.",
            189,
            [G["content"]],
            H,
        ),
        Q(
            "result.reference_range",
            "Reported Reference Range",
            "string",
            "reference-range",
            "보고서에 적힌 기준범위를 원문 그대로 알려주세요.",
            188,
            [G["content"]],
            H,
        ),
        Q(
            "result.reported_interpretation",
            "Reported Interpretation or Conclusion",
            "string",
            "reported-interpretation",
            "보고서의 판정·결론·Impression 항목에 적힌 내용을 원문 그대로 알려주세요.",
            187,
            [G["content"]],
            H,
        ),
        Q(
            "result.specimen_type",
            "Reported Specimen Type",
            "string",
            "specimen-type",
            "보고서에 검체 종류가 적혀 있다면 원문대로 알려주세요.",
            186,
            [G["content"]],
            H,
        ),
        Q(
            "result.specimen_collected_at",
            "Reported Specimen Collection Time",
            "datetime",
            "specimen-collected-at",
            "검체를 채취한 날짜와 시각이 적혀 있다면 알려주세요.",
            185,
            [G["content"]],
            H,
        ),
        Q(
            "result.body_site",
            "Reported Body Site",
            "string",
            "body-site",
            "검사한 신체 부위가 적혀 있다면 원문대로 알려주세요.",
            184,
            [G["content"]],
            H,
        ),
        Q(
            "result.method",
            "Reported Test Method",
            "string",
            "method",
            "검사 방법이 적혀 있다면 원문대로 알려주세요.",
            183,
            [G["content"]],
            H,
        ),
        Q(
            "result.device",
            "Reported Test Device",
            "string",
            "device",
            "검사에 사용한 장비가 적혀 있다면 원문대로 알려주세요.",
            182,
            [G["content"]],
            H,
        ),
        Q(
            "result.reported_limitation",
            "Reported Result Limitation",
            "string",
            "reported-limitation",
            "검체 상태, 판독 제한 또는 신뢰도 관련 주의문이 적혀 있다면 원문대로 알려주세요.",
            181,
            [G["content"], G["handoff"]],
            H,
        ),
        Q(
            "result.pending_components",
            "Pending Result Components",
            "string",
            "pending-components",
            "아직 나오지 않았다고 표시된 검사 항목이 있다면 그 항목을 알려주세요.",
            180,
            [G["content"], G["handoff"]],
            H,
        ),
        Q(
            "result.expected_completion_at",
            "Expected Result Completion Time",
            "date_or_period",
            "expected-completion",
            "남은 결과가 언제 나올 예정이라고 안내받았는지 알려주세요.",
            179,
            [G["content"], G["handoff"]],
            H,
        ),
        Q(
            "result.prior_result_available",
            "Prior Comparable Result Available",
            "boolean",
            "prior-result-available",
            "비교할 수 있는 이전 같은 검사결과가 있나요?",
            178,
            [G["context"]],
            H,
        ),
        Q(
            "result.prior_result_date",
            "Prior Comparable Result Date",
            "date_or_period",
            "prior-result-date",
            "이전 같은 검사를 시행한 때는 언제인가요?",
            177,
            [G["context"]],
            H,
        ),
        Q(
            "result.prior_result_summary",
            "Prior Comparable Result Summary",
            "string",
            "prior-result-summary",
            "이전 결과의 수치나 결론을 원문대로 알려주세요.",
            176,
            [G["context"]],
            H,
        ),
        Q(
            "result.reported_comparison",
            "Reported Comparison with Prior Result",
            "coded",
            "reported-comparison",
            "보고서에 이전 결과와 비교해 호전, 비슷, 악화 또는 변화라고 적혀 있나요? 보기에 없으면 직접 입력해 주세요.",
            175,
            [G["context"], G["handoff"]],
            H,
            allowed_values=[
                "improved",
                "similar",
                "worsened",
                "changed_unspecified",
                "not_compared",
                "unknown",
                "other",
            ],
        ),
        Q(
            "result.prior_explanation",
            "Prior Clinician Explanation",
            "string",
            "prior-explanation",
            "이 결과에 대해 의료진에게 이미 들은 설명이 있다면 그 내용을 알려주세요.",
            170,
            [G["context"], G["handoff"]],
            H,
        ),
        Q(
            "result.follow_up_plan",
            "Known Follow-up Plan",
            "string",
            "follow-up-plan",
            "재검, 진료 예약, 약 변경 또는 다른 진료과 방문 등 이미 안내받은 후속 계획이 있나요?",
            169,
            [G["context"], G["handoff"]],
            H,
        ),
        Q(
            "result.conflict",
            "Conflicting Result Information",
            "string",
            "result-conflict",
            "문서, 의료기관 안내와 본인이 이해한 내용이 서로 다르다면 각각 어떻게 다른지 알려주세요.",
            168,
            [G["content"], G["handoff"]],
            H,
        ),
        Q(
            "result.notification_received_at",
            "Result Notification Received Time",
            "datetime",
            "notification-received-at",
            "검사결과 또는 결과 안내를 처음 받은 날짜와 시각을 알려주세요.",
            167,
            [G["context"], G["handoff"]],
            H,
        ),
        Q(
            "result.notification_method",
            "Result Notification Method",
            "coded",
            "notification-method",
            "결과를 대면, 전화, 문자, 이메일, 환자 포털, 우편 또는 보호자를 통해 받았나요? 보기에 없으면 직접 입력해 주세요.",
            166,
            [G["context"], G["handoff"]],
            H,
            allowed_values=[
                "in_person",
                "telephone",
                "text_message",
                "email",
                "patient_portal",
                "letter",
                "caregiver",
                "other",
                "unknown",
            ],
        ),
        Q(
            "result.follow_up_responsible_party",
            "Responsible Follow-up Party",
            "string_or_reference",
            "follow-up-responsible-party",
            "이 결과를 확인하고 후속조치를 담당하기로 한 의료진이나 기관을 알려주세요.",
            165,
            [G["context"], G["handoff"]],
            H,
        ),
        Q(
            "result.follow_up_recommended_action",
            "Recommended Follow-up Action",
            "string",
            "follow-up-recommended-action",
            "결과와 관련해 안내받은 재검, 예약, 의뢰 또는 다른 후속조치를 알려주세요.",
            164,
            [G["context"], G["handoff"]],
            H,
        ),
        Q(
            "result.follow_up_due_at",
            "Follow-up Action Due Time",
            "date_or_period",
            "follow-up-due-at",
            "그 후속조치를 언제까지 하라고 안내받았나요?",
            163,
            [G["context"], G["handoff"]],
            H,
        ),
        Q(
            "result.follow_up_action_status",
            "Follow-up Action Status",
            "coded",
            "follow-up-action-status",
            "안내받은 후속조치는 아직 시작 전, 예약됨, 진행 중, 완료, 거절 또는 해당 없음 중 어디에 가깝나요? 보기에 없으면 직접 입력해 주세요.",
            162,
            [G["context"], G["handoff"]],
            H,
            allowed_values=[
                "not_started",
                "scheduled",
                "in_progress",
                "completed",
                "declined",
                "not_applicable",
                "unknown",
                "other",
            ],
        ),
        Q(
            "result.follow_up_barrier",
            "Follow-up Barrier",
            "string",
            "follow-up-barrier",
            "후속조치를 진행하기 어려운 이유가 있다면 알려주세요.",
            161,
            [G["context"], G["handoff"]],
            H,
        ),
        Q(
            "result.communication_support_need",
            "Result Communication Support Need",
            "string",
            "communication-support-need",
            "결과 안내를 이해하는 데 필요한 의사소통 지원이 있나요?",
            160,
            [G["context"], G["handoff"]],
            H,
        ),
        Q(
            "result.additional_comment",
            "Additional Result Follow-up Comment",
            "string",
            "additional-comment",
            "질문에 없지만 결과를 확인할 의료진에게 추가로 전달할 내용이 있나요?",
            90,
            [G["handoff"]],
            H,
        ),
    ]
    rules = [
        safety_rule(
            P,
            "explicit-emergency-instruction",
            {"fact": "result.explicit_emergency_instruction", "equals": True},
            "emergency",
            1000,
        ),
        safety_rule(
            P,
            "explicit-urgent-instruction",
            {"fact": "result.urgent_follow_up_instruction", "equals": True},
            "urgent",
            995,
        ),
        safety_rule(
            P,
            "severe-current-symptom",
            {"fact": "result.current_severe_symptom", "equals": True},
            "urgent",
            990,
        ),
        safety_rule(
            P,
            "rapidly-worsening-symptom",
            {"fact": "result.rapidly_worsening_symptom", "equals": True},
            "urgent",
            985,
        ),
    ]
    refresh = default_refresh()
    refresh.update(
        {
            "class": "stable_semantic",
            "last_assessed_at": "2026-07-25",
            "monitor_interval_days": 180,
            "full_review_interval_days": 365,
            "next_monitor_at": "2027-01-21",
            "next_full_review_at": "2027-07-25",
        }
    )
    return {
        "id": "knowledge.generated.test-result-follow-up",
        "version": VERSION,
        "status": "research_only",
        "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-test-result-follow-up-research",
        "default_refresh": refresh,
        "extra_nodes": [
            {"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]}
            for value in G.values()
        ],
        "group_hypothesis_edges": [],
        "safety_rules": rules,
        "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(fragment):
    safety = [
        "encounter.result_follow_up.goal",
        "result.explicit_emergency_instruction",
        "result.urgent_follow_up_instruction",
        "result.current_severe_symptom",
        "result.rapidly_worsening_symptom",
        "result.abnormal_notice",
        "result.new_concern",
        "result.patient_question",
        "result.expected_outcome",
    ]
    interpretation = [
        "result.content.available",
        "result.test.category",
        "result.test.name",
        "result.test.performed_at",
        "result.report.issued_at",
        "result.report.status",
        "result.report.version_or_amendment",
        "result.performing_organization",
        "result.test.clinical_reason",
            "result.test_requester",
        "result.results_interpreter",
        "result.report.source",
        "result.report.readability",
        "result.value.summary",
        "result.value.units",
        "result.reference_range",
        "result.reported_interpretation",
        "result.specimen_type",
        "result.specimen_collected_at",
        "result.body_site",
        "result.method",
        "result.device",
        "result.reported_limitation",
        "result.pending_components",
        "result.prior_result_available",
        "result.reported_comparison",
        "result.prior_explanation",
        "result.follow_up_plan",
        "result.conflict",
        "result.notification_received_at",
        "result.notification_method",
        "result.follow_up_responsible_party",
        "result.follow_up_recommended_action",
        "result.follow_up_due_at",
        "result.follow_up_action_status",
        "result.communication_support_need",
        "result.additional_comment",
    ]
    return {
        "id": "policy.primary-care-test-result-follow-up-completion",
        "version": VERSION,
        "status": "research_only",
        "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": safety, "routine": []},
        "conditional_required_facts": [
            {
                "selector_fact": "encounter.result_follow_up.goal",
                "cases": {
                    "institution_result_check": ["result.additional_comment"],
                    "interpretation_request": interpretation,
                    "both": interpretation,
                    "unknown": ["result.content.available", "result.additional_comment"],
                },
            },
            {
                "when": {"fact": "result.new_concern", "equals": True},
                "required_facts": [
                    "result.related_symptoms",
                    "result.related_symptom_onset",
                    "result.related_symptom_severity",
                ],
                "reason": "new_result_related_concern",
            },
            {
                "selector_fact": "result.report.status",
                "cases": {
                    "registered": ["result.expected_completion_at"],
                    "partial": ["result.expected_completion_at"],
                    "preliminary": ["result.expected_completion_at"],
                },
            },
            {
                "when": {"fact": "result.prior_result_available", "equals": True},
                "required_facts": [
                    "result.prior_result_date",
                    "result.prior_result_summary",
                ],
                "reason": "comparable_prior_result_available",
            },
            {
                "selector_fact": "result.follow_up_action_status",
                "cases": {
                    "not_started": ["result.follow_up_barrier"],
                    "in_progress": ["result.follow_up_barrier"],
                    "declined": ["result.follow_up_barrier"],
                    "unknown": ["result.follow_up_barrier"],
                },
            },
        ],
        "clarification_facts_by_rule": {},
        "question_budget": {"routine": 53, "clarify": 10},
        "upload_policy": {
            "institution_result_check": "never_request",
            "interpretation_request": "request_once_only_if_not_already_available",
            "both": "request_once_only_if_not_already_available",
            "unavailable_or_declined": "preserve_dataAbsentReason_and_do_not_repeat",
        },
        "provenance": provenance(SOURCES),
    }


def source_documents():
    artifacts = [
        {
            "id": "source.hl7.fhir-r4.diagnosticreport",
            "kind": "official_fhir_specification_metadata",
            "publisher": "HL7 International",
            "title": "FHIR R4 DiagnosticReport",
            "version": "4.0.1",
            "url": "https://hl7.org/fhir/R4/diagnosticreport.html",
            "language": "en",
            "digest": "metadata_only_existing_repository_reference",
            "license_status": "allowed",
            "complete": False,
            "monitor_profile": "interoperability_standard",
            "last_monitored_at": "2026-08-04",
            "monitor_result": "current_fhir_r4_4.0.1_no_version_change",
        },
        {
            "id": "source.hl7.fhir-r4.observation",
            "kind": "official_fhir_specification_metadata",
            "publisher": "HL7 International",
            "title": "FHIR R4 Observation",
            "version": "4.0.1",
            "url": "https://hl7.org/fhir/R4/observation.html",
            "language": "en",
            "digest": "metadata_only_existing_repository_reference",
            "license_status": "allowed",
            "complete": False,
            "monitor_profile": "interoperability_standard",
            "last_monitored_at": "2026-08-04",
            "monitor_result": "current_fhir_r4_4.0.1_no_version_change",
        },
        {
            "id": "source.uscdi.v6.2025",
            "kind": "official_interoperability_mapping_reference",
            "publisher": "ASTP/ONC",
            "title": "USCDI Version 6",
            "version": "v6",
            "url": "https://www.healthit.gov/isp/uscdi-data-class/diagnostic-imaging",
            "language": "en",
            "digest": "metadata_only_existing_repository_reference",
            "license_status": "allowed",
            "complete": False,
            "monitor_profile": "interoperability_standard",
            "last_monitored_at": "2026-08-04",
            "monitor_result": "current_v6_with_draft_v7_watch_no_baseline_promotion",
        },
        {
            "id": "source.ahrq.follow-up-with-patients-tool6.2024",
            "kind": "official_patient_safety_guidance_metadata",
            "publisher": "Agency for Healthcare Research and Quality",
            "title": "Health Literacy Universal Precautions Toolkit, Tool 6: Follow Up with Patients",
            "version": "reviewed-2024-02",
            "url": "https://www.ahrq.gov/health-literacy/improve/precautions/tool6.html",
            "language": "en",
            "digest": "follow_up_reason_responsibility_timing_action_plan_questions_and_communication_support_verified_2026-08-04",
            "license_status": "metadata_and_summary_only",
            "complete": False,
            "monitor_profile": "public_health_guidance",
            "last_monitored_at": "2026-08-04",
            "monitor_result": "current",
        },
        {
            "id": "source.ahrq.diagnostic-safety-current-state.2023",
            "kind": "official_diagnostic_safety_issue_brief_metadata",
            "publisher": "Agency for Healthcare Research and Quality",
            "title": "The Current State of Diagnostic Safety: Test Results Management and Closing the Loop",
            "version": "issue-brief-current-2026-08-04",
            "url": "https://www.ahrq.gov/diagnostic-safety/resources/issue-briefs/dxsafety-current-state3.html",
            "language": "en",
            "digest": "sent_received_acknowledged_acted_on_language_access_and_abnormal_result_follow_up_verified_2026-08-04",
            "license_status": "metadata_and_summary_only",
            "complete": False,
            "monitor_profile": "public_health_guidance",
            "last_monitored_at": "2026-08-04",
            "monitor_result": "current",
        },
        {
            "id": "source.acsqhc.pathology-information-communication-reporting.2026",
            "kind": "official_pathology_standard_metadata",
            "publisher": "Australian Commission on Safety and Quality in Health Care",
            "title": "Requirements for Information, Communication and Reporting, Sixth Edition",
            "version": "sixth-edition-2026",
            "url": "https://www.safetyandquality.gov.au/sites/default/files/2026-07/Requirements-for-Information-Communication-and-Reporting-sixth-edition-2026.pdf",
            "language": "en",
            "digest": "test_identity_result_units_interpretation_responsibility_and_communication_requirements_verified_2026-08-04",
            "license_status": "metadata_and_summary_only",
            "complete": False,
            "monitor_profile": "clinical_guideline",
            "last_monitored_at": "2026-08-04",
            "monitor_result": "current",
        },
        {
            "id": "source.stom.test-result-follow-up.20260804",
            "kind": "terminology_service_verification",
            "publisher": "STOM",
            "title": "FHIR R4 DiagnosticReport and Observation ValueSet verification",
            "version": "FHIR-R4-4.0.1-verified-20260804",
            "url": "http://localhost:8088/fhir",
            "language": "en",
            "digest": "diagnostic_report_status_and_observation_status_canonical_resources_discoverable",
            "license_status": "licensed_lookup_metadata_only",
            "complete": False,
            "monitor_profile": "terminology_server",
            "last_monitored_at": "2026-08-04",
            "monitor_result": "verified",
        },
    ]
    research = {
        "id": "source-manifest.primary-care-test-result-follow-up-research",
        "version": VERSION,
        "acquired_at": ACQUIRED_AT,
        "status": "research_only",
        "artifacts": artifacts,
        "provenance": provenance([item["id"] for item in artifacts]),
    }
    paths = [
        (
            "source.repository.foundation",
            "repository_specification",
            "FOUNDATION.md",
            True,
        ),
        (
            "source.generated.test-result-follow-up",
            "generated_clinical_knowledge",
            "knowledge/generated/follow-up/test-result/test-result-follow-up.json",
            True,
        ),
        (
            "source.external.test-result-follow-up",
            "external_source_manifest",
            "sources/manifests/primary-care-test-result-follow-up-research.json",
            False,
        ),
        (
            "source.policy.test-result-follow-up",
            "runtime_policy",
            "policies/primary-care-test-result-follow-up-completion.json",
            True,
        ),
    ]
    primary = {
        "id": "source-manifest.primary-care-test-result-follow-up",
        "version": VERSION,
        "acquired_at": ACQUIRED_AT,
        "artifacts": [
            {
                "id": identifier,
                "kind": kind,
                "publisher": "clinical-interview-platform",
                "version": VERSION,
                "language": "en",
                "path": path,
                "digest": "computed_at_build",
                "license_status": "allowed" if complete else "unknown",
                "complete": complete,
            }
            for identifier, kind, path, complete in paths
        ],
        "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"]),
    }
    return primary, research


def routine_state(goal):
    state = {
        "encounter.result_follow_up.goal": {"value": goal},
        "result.explicit_emergency_instruction": {"value": False},
        "result.urgent_follow_up_instruction": {"value": False},
        "result.current_severe_symptom": {"value": False},
        "result.rapidly_worsening_symptom": {"value": False},
        "result.abnormal_notice": {"value": False},
        "result.new_concern": {"value": False},
        "result.patient_question": {"value": "추가로 원하는 내용 없음"},
        "result.expected_outcome": {"value": "검사결과 확인"},
        "result.additional_comment": {"value": "없음"},
    }
    if goal in {"interpretation_request", "both"}:
        state.update(
            {
                "result.content.available": {"value": "provided_in_conversation"},
                "result.test.category": {"value": "laboratory"},
                "result.test.name": {"value": "검사명 원문"},
                "result.test.performed_at": {"value": "2026-07"},
                "result.report.issued_at": {"value": "2026-07"},
                "result.report.status": {"value": "final"},
                "result.report.version_or_amendment": {"value": "최종본"},
                "result.performing_organization": {"value": "합성 의료기관"},
                "result.test.clinical_reason": {"value": "합성 증상 평가"},
                "result.test_requester": {"value": "합성 일차의료 진료팀"},
                "result.results_interpreter": {"value": "합성 판독 부서"},
                "result.report.source": {"value": "uploaded_document"},
                "result.report.readability": {"value": "complete_readable"},
                "result.value.summary": {"value": "합성 결과값"},
                "result.value.units": {"value": "합성 단위"},
                "result.reference_range": {"value": "합성 기준범위"},
                "result.reported_interpretation": {"value": "합성 보고서 결론"},
                "result.specimen_type": {"value": "합성 혈액 검체"},
                "result.specimen_collected_at": {"value": "2026-07"},
                "result.body_site": {"value": "해당 없음"},
                "result.method": {"value": "보고서에 기재되지 않음"},
                "result.device": {"value": "보고서에 기재되지 않음"},
                "result.reported_limitation": {"value": "없음"},
                "result.pending_components": {"value": "없음"},
                "result.prior_result_available": {"value": False},
                "result.reported_comparison": {"value": "not_compared"},
                "result.prior_explanation": {"value": "아직 설명받지 않음"},
                "result.follow_up_plan": {"value": "담당 의료진 확인 예정"},
                "result.conflict": {"value": "없음"},
                "result.notification_received_at": {"value": "2026-07"},
                "result.notification_method": {"value": "patient_portal"},
                "result.follow_up_responsible_party": {"value": "합성 일차의료 진료팀"},
                "result.follow_up_recommended_action": {"value": "담당 의료진과 결과 검토"},
                "result.follow_up_due_at": {"value": "다음 예약일"},
                "result.follow_up_action_status": {"value": "scheduled"},
                "result.communication_support_need": {"value": "없음"},
            }
        )
    return state


def simulations(fragment):
    result = {}
    base = routine_state("institution_result_check")
    result["RESULT-INSTITUTION-CHECK-MINIMAL.json"] = {
        "id": "RESULT-INSTITUTION-CHECK-MINIMAL",
        "simulation_language": "ko",
        "persona": {"age": 54},
        "initial_statement": {"ko": "검사 결과 확인하러 왔어요."},
        "hidden_state": base,
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 12,
            "forbidden_assertions": [
                "result_upload_required",
                "diagnosis.normal_result",
                "diagnosis.abnormal_result",
            ],
        },
        "provenance": provenance(SOURCES),
    }
    interpreted = routine_state("interpretation_request")
    result["RESULT-INTERPRET-UPLOADED-LAB.json"] = {
        "id": "RESULT-INTERPRET-UPLOADED-LAB",
        "simulation_language": "ko",
        "persona": {"age": 41},
        "initial_statement": {"ko": "올린 검사결과의 내용을 설명받고 싶어요."},
        "hidden_state": interpreted,
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 53,
            "forbidden_assertions": [
                "repeat_upload_request",
                "diagnosis.inferred_from_report",
            ],
        },
        "provenance": provenance(SOURCES),
    }
    for key, fact, level in (
        (
            "EMERGENCY-INSTRUCTION",
            "result.explicit_emergency_instruction",
            "emergency",
        ),
        ("URGENT-INSTRUCTION", "result.urgent_follow_up_instruction", "urgent"),
        (
            "SEVERE-CURRENT-SYMPTOM",
            "result.current_severe_symptom",
            "urgent",
        ),
        (
            "RAPIDLY-WORSENING-SYMPTOM",
            "result.rapidly_worsening_symptom",
            "urgent",
        ),
    ):
        state = routine_state("institution_result_check")
        state[fact] = {"value": True}
        rule_key = {
            "result.explicit_emergency_instruction": "explicit-emergency-instruction",
            "result.urgent_follow_up_instruction": "explicit-urgent-instruction",
            "result.current_severe_symptom": "severe-current-symptom",
            "result.rapidly_worsening_symptom": "rapidly-worsening-symptom",
        }[fact]
        result[f"RESULT-{key}.json"] = {
            "id": f"RESULT-{key}",
            "simulation_language": "ko",
            "persona": {"age": 63},
            "initial_statement": {"ko": "검사결과 때문에 빠른 확인 안내를 받았습니다."},
            "hidden_state": state,
            "expected": {
                "expected_safety_level": level,
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [
                    f"rule.{P}.safety.{rule_key}"
                ],
                "expected_max_turns": 8,
                "forbidden_assertions": ["diagnosis.result_based_emergency"],
            },
            "provenance": provenance(SOURCES),
        }
    absent = routine_state("interpretation_request")
    for fact in (
        "result.content.available",
        "result.test.name",
        "result.report.status",
        "result.value.summary",
    ):
        absent.pop(fact, None)
    absent_responses = {
        "result.content.available": {"dataAbsentReason": "asked-unknown"},
        "result.test.name": {"dataAbsentReason": "asked-unknown"},
        "result.report.status": {"dataAbsentReason": "asked-unknown"},
        "result.value.summary": {"dataAbsentReason": "not-performed"},
    }
    result["RESULT-DATA-ABSENT-NO-REPEAT.json"] = {
        "id": "RESULT-DATA-ABSENT-NO-REPEAT",
        "simulation_language": "ko",
        "persona": {"age": 72},
        "initial_statement": {"ko": "결과를 설명받고 싶은데 자료는 지금 없어요."},
        "hidden_state": absent,
        "response_behavior": absent_responses,
        "expected": {
            "expected_data_absent_reasons": {
                key: value["dataAbsentReason"]
                for key, value in absent_responses.items()
            },
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 53,
            "forbidden_assertions": ["repeat_upload_request", "diagnosis.normal_result"],
        },
        "provenance": provenance(SOURCES),
    }
    proxy = routine_state("interpretation_request")
    proxy["result.report.source"] = {"value": "proxy_report"}
    proxy["result.conflict"] = {
        "value": "보호자 설명과 수정된 최종 보고서의 결론이 다름"
    }
    result["RESULT-PROXY-AMENDED-CONFLICT.json"] = {
        "id": "RESULT-PROXY-AMENDED-CONFLICT",
        "simulation_language": "ko",
        "persona": {"age": 80},
        "encounter_context": {
            "care_setting": "primary_care",
            "encounter_type": "follow_up",
            "interview_initiator": "caregiver",
            "interview_mode": "telephone",
            "available_information": ["referral_letter"],
            "time_constraint": "scheduled",
            "clinical_responsibility": "follow_up_support",
        },
        "initial_statement": {"ko": "보호자가 수정된 검사결과 확인을 대신합니다."},
        "hidden_state": proxy,
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 53,
            "forbidden_assertions": ["silent_conflict_overwrite", "diagnosis.inferred"],
        },
        "provenance": provenance(SOURCES),
    }
    multi = routine_state("institution_result_check")
    multi["result.new_concern"] = {"value": True}
    multi["result.related_symptoms"] = {"value": "새 가슴 통증이 있어 별도 문진 필요"}
    multi["result.related_symptom_onset"] = {"value": "오늘"}
    multi["result.related_symptom_severity"] = {"value": "현재 중간 정도"}
    multi["result.additional_comment"] = {"value": "검사결과 외에 흉통 문진도 원함"}
    result["RESULT-MULTI-RFE-CHEST-PAIN.json"] = {
        "id": "RESULT-MULTI-RFE-CHEST-PAIN",
        "simulation_language": "ko",
        "persona": {"age": 58},
        "initial_statement": {"ko": "검사결과 확인과 새로 생긴 가슴 통증 문진을 원합니다."},
        "hidden_state": multi,
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_known_facts": {
                "result.related_symptoms": "새 가슴 통증이 있어 별도 문진 필요"
            },
            "expected_max_turns": 16,
            "forbidden_assertions": ["diagnosis.acute_coronary_syndrome"],
        },
        "provenance": provenance(SOURCES),
    }
    pending = routine_state("interpretation_request")
    pending.update(
        {
            "result.report.status": {"value": "preliminary"},
            "result.pending_components": {"value": "합성 병리 추가 판독"},
            "result.expected_completion_at": {"value": "약 1주 후"},
            "result.report.source": {"value": "proxy_report"},
            "result.notification_method": {"value": "caregiver"},
            "result.communication_support_need": {"value": "짧은 문장과 보호자 대리"},
        }
    )
    result["RESULT-PENDING-PATHOLOGY-PROXY-REMOTE.json"] = {
        "id": "RESULT-PENDING-PATHOLOGY-PROXY-REMOTE",
        "simulation_language": "ko",
        "persona": {"age": 76},
        "encounter_context": {
            "care_setting": "telemedicine",
            "encounter_type": "follow_up",
            "interview_initiator": "caregiver",
            "interview_mode": "video",
            "available_information": ["partial_report"],
            "time_constraint": "scheduled",
            "clinical_responsibility": "follow_up_support",
        },
        "initial_statement": {"ko": "보호자가 아직 일부만 나온 병리결과를 대신 확인합니다."},
        "hidden_state": pending,
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_known_facts": {
                "result.report.status": "preliminary",
                "result.expected_completion_at": "약 1주 후",
                "result.communication_support_need": "짧은 문장과 보호자 대리",
            },
            "expected_max_turns": 53,
            "forbidden_assertions": [
                "diagnosis.final_pathology",
                "result.pending_components.completed",
            ],
        },
        "provenance": provenance(SOURCES),
    }
    compared = routine_state("interpretation_request")
    compared.update(
        {
            "result.prior_result_available": {"value": True},
            "result.prior_result_date": {"value": "약 6개월 전"},
            "result.prior_result_summary": {"value": "합성 이전 결과"},
            "result.reported_comparison": {"value": "changed_unspecified"},
        }
    )
    result["RESULT-PRIOR-COMPARISON-PRESERVED.json"] = {
        "id": "RESULT-PRIOR-COMPARISON-PRESERVED",
        "simulation_language": "ko",
        "persona": {"age": 59},
        "initial_statement": {"ko": "이번 보고서에 이전 검사와 달라졌다고 적혀 있어 비교해서 전달하고 싶습니다."},
        "hidden_state": compared,
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_known_facts": {
                "result.prior_result_available": True,
                "result.reported_comparison": "changed_unspecified",
            },
            "expected_max_turns": 53,
            "forbidden_assertions": ["diagnosis.trend_interpretation"],
        },
        "provenance": provenance(SOURCES),
    }
    barrier = routine_state("interpretation_request")
    barrier.update(
        {
            "result.follow_up_action_status": {"value": "not_started"},
            "result.follow_up_barrier": {"value": "예약 방법을 몰라 아직 진행하지 못함"},
            "result.follow_up_due_at": {"value": "이번 주 안"},
        }
    )
    result["RESULT-FOLLOW-UP-BARRIER-UNRESOLVED.json"] = {
        "id": "RESULT-FOLLOW-UP-BARRIER-UNRESOLVED",
        "simulation_language": "ko",
        "persona": {"age": 67},
        "initial_statement": {"ko": "후속 진료 안내를 받았지만 예약을 아직 못했습니다."},
        "hidden_state": barrier,
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_known_facts": {
                "result.follow_up_action_status": "not_started",
                "result.follow_up_barrier": "예약 방법을 몰라 아직 진행하지 못함",
            },
            "expected_max_turns": 53,
            "forbidden_assertions": [
                "recommendation.booked_automatically",
                "diagnosis.result_interpretation",
            ],
        },
        "provenance": provenance(SOURCES),
    }
    return result


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(
        prefix=P,
        rfe=RFE,
        display="Test Result Follow-up",
        intents=[
            (
                "intent.characterize_result_follow_up",
                "Clarify Result Follow-up Goal",
            ),
            (
                "intent.screen_result_follow_up_safety",
                "Screen Explicit Result Follow-up Safety Instructions",
            ),
            (
                "intent.prepare_result_clinician_handoff",
                "Prepare Result Identity Content Source and Follow-up Handoff",
            ),
        ],
    )
    primary, research = source_documents()
    documents = [
        ("knowledge/base/primary-care-test-result-follow-up.json", graph),
        ("rules/base/primary-care-test-result-follow-up.json", rules),
        (
            "knowledge/generated/follow-up/test-result/test-result-follow-up.json",
            generated,
        ),
        ("sources/manifests/primary-care-test-result-follow-up.json", primary),
        (
            "sources/manifests/primary-care-test-result-follow-up-research.json",
            research,
        ),
        (
            "policies/primary-care-test-result-follow-up-completion.json",
            completion(generated),
        ),
    ]
    for path, document in documents:
        write_json(path, document)
    for filename, case in simulations(generated).items():
        write_json(
            f"simulation/patients/follow-up/test-result/{filename}",
            case,
        )


if __name__ == "__main__":
    main()
