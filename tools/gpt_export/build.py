#!/usr/bin/env python3
"""Build deterministic public GPT resources from repository knowledge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


VERSION = "1.22.5"
GENERATED_AT = "2026-07-14T00:00:00Z"
PRIVATE_KEYS = {
    "raw_text", "raw_input", "patient_response", "patient_responses",
    "questionnaire_response", "conversation", "transcript", "evidence",
}
COMPACT_DROP_KEYS = {
    "provenance", "refresh", "source_manifest", "usage_modes", "version",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: sanitize(item)
            for key, item in sorted(value.items())
            if key.lower() not in PRIVATE_KEYS
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def quality(item: dict[str, Any]) -> tuple[int, int]:
    """Prefer the richest duplicate and then use stable JSON ordering."""
    encoded = json.dumps(item, ensure_ascii=False, sort_keys=True)
    return len(item), len(encoded)


def deduplicate(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for item in items:
        identifier = item.get("id")
        if not identifier:
            continue
        clean = sanitize(item)
        if identifier not in selected or quality(clean) > quality(selected[identifier]):
            selected[identifier] = clean
    return [selected[key] for key in sorted(selected)]


def envelope(resource_type: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "resource_type": resource_type,
        "version": VERSION,
        "status": "research_only",
        "review_status": "unreviewed",
        "usage_modes": ["research_test", "simulation"],
        "contains_patient_responses": False,
        "generated_at": GENERATED_AT,
        "count": len(items),
        "items": items,
    }


def compact(value: Any) -> Any:
    """Remove repeated build metadata while preserving runtime semantics."""
    if isinstance(value, dict):
        return {
            key: compact(item)
            for key, item in sorted(value.items())
            if key not in COMPACT_DROP_KEYS and key.lower() not in PRIVATE_KEYS
        }
    if isinstance(value, list):
        return [compact(item) for item in value]
    return value


def compact_fact_index(item: dict[str, Any]) -> dict[str, Any]:
    """Keep the legacy aggregate as discovery metadata, not a knowledge payload."""
    # Korean labels for shared Facts remain in common-facts.json. Omitting the
    # duplicate label here keeps this legacy cross-RFE discovery index bounded.
    keys = ("id", "value_type")
    result = {key: item[key] for key in keys if key in item}
    if item.get("safety_relevant") is True:
        result["safety_relevant"] = True
    return result


def compact_safety_rule_index(item: dict[str, Any]) -> dict[str, Any]:
    """Keep executable safety essentials without repeated collection metadata."""
    return {
        key: compact(item[key])
        for key in ("id", "when", "then")
        if key in item
    }


def package_knowledge_sources(package: dict[str, Any]) -> list[dict[str, Any]]:
    """Expose compact source identity once per RFE resource without full provenance."""
    keys = (
        "id", "kind", "publisher", "title", "version", "url", "complete",
        "license_status", "last_monitored_at", "monitor_interval_days",
    )
    selected: dict[str, dict[str, Any]] = {}
    for manifest in package.get("research_source_manifests", []):
        for artifact in manifest.get("artifacts", []):
            source_id = artifact.get("id")
            if source_id:
                selected[source_id] = {
                    key: artifact[key] for key in keys if key in artifact
                }
    return [selected[key] for key in sorted(selected)]


def number_answer_options(
    labels: list[str], *, include_unknown: bool = True, include_decline: bool = True
) -> list[dict[str, Any]]:
    """Assign unique display numbers within one question.

    The fixed 1/2/3/5 shortcut is valid only for the exact
    yes/no/unknown/decline set. Enumerated questions continue numbering after
    their domain choices so unknown and decline cannot collide with them.
    """
    if labels == ["예", "아니오"] and include_unknown and include_decline:
        return [
            {"number": 1, "label": "예", "code": "yes"},
            {"number": 2, "label": "아니오", "code": "no"},
            {"number": 3, "label": "잘 모르겠음", "code": "unknown"},
            {"number": 5, "label": "답변하지 않음", "code": "decline"},
        ]
    options = [
        {"number": index, "label": label, "code": "domain_choice"}
        for index, label in enumerate(labels, start=1)
    ]
    next_number = len(options) + 1
    if include_unknown:
        options.append({"number": next_number, "label": "잘 모르겠음", "code": "unknown"})
        next_number += 1
    if include_decline:
        options.append({"number": next_number, "label": "답변하지 않음", "code": "decline"})
    return options


def rfe_resource(
    resource_type: str,
    rfe_id: str,
    package: dict[str, Any],
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    compact_items = [compact(item) for item in items]
    if resource_type == "ReasonForEncounterRuleCollection":
        # The envelope carries the review status for every compiled rule.
        # Keep rule type and executable semantics, but omit repeated status text.
        compact_items = [
            {key: value for key, value in item.items() if key != "status"}
            for item in compact_items
        ]
    return {
        "resource_type": resource_type,
        "version": VERSION,
        "status": "research_only",
        "review_status": "unreviewed",
        "usage_modes": ["research_test", "simulation"],
        "contains_patient_responses": False,
        "generated_at": GENERATED_AT,
        "reason_for_encounter": rfe_id,
        "encounter_contexts": package.get("scope", {}).get("encounter_contexts", []),
        "package_id": package.get("package_id"),
        "package_version": package.get("package_version"),
        "knowledge_sources": package_knowledge_sources(package),
        "knowledge_source_status": {
            "status": "research_only",
            "review_status": "unreviewed",
            "clinical_sources_are_compiled_not_queried_live": True,
        },
        "count": len(items),
        "items": compact_items,
    }


def collect_rfe_resources(root: Path) -> dict[str, dict[str, Any]]:
    resources: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "packages" / "generated").glob("*.json")):
        package = load_json(path)
        reasons = package.get("scope", {}).get("reasons_for_encounter", [])
        if len(reasons) != 1:
            continue
        rfe_id = reasons[0]
        slug = rfe_id.removeprefix("rfe.")
        nodes = package.get("knowledge_graph", {}).get("nodes", [])
        facts = [node for node in nodes if node.get("type") == "Fact"]
        questions = [node for node in nodes if node.get("type") == "QuestionTemplate"]
        rules = package.get("rule_graph", {}).get("rules", [])
        resources[f"rfe/{slug}/facts.json"] = rfe_resource(
            "ReasonForEncounterFactCollection", rfe_id, package, facts
        )
        resources[f"rfe/{slug}/questions.json"] = rfe_resource(
            "ReasonForEncounterQuestionCollection", rfe_id, package, questions
        )
        resources[f"rfe/{slug}/rules.json"] = rfe_resource(
            "ReasonForEncounterRuleCollection", rfe_id, package, rules
        )
    return resources


def collect_patient_experience_questionnaire(root: Path) -> dict[str, dict[str, Any]]:
    """Split the FHIR Questionnaire into Action-safe workflow and section payloads."""
    path = (
        root / "fhir/r4/questionnaires/"
        "kr-patient-experience-evaluation-5th-2025.json"
    )
    questionnaire = load_json(path)
    if questionnaire.get("resourceType") != "Questionnaire":
        raise RuntimeError("patient-experience source is not a FHIR Questionnaire")
    sections = questionnaire.get("item", [])
    if len(sections) != 8:
        raise RuntimeError("patient-experience Questionnaire must contain 8 sections")
    resources: dict[str, dict[str, Any]] = {}
    section_index = []
    total_questions = 0
    for number, section in enumerate(sections, 1):
        question_count = sum(
            item.get("type") not in {"display", "group"}
            for item in section.get("item", [])
        )
        total_questions += question_count
        section_path = (
            "questionnaires/patient-experience-5th-2025/"
            f"sections/{number}.json"
        )
        section_index.append({
            "number": number,
            "linkId": section["linkId"],
            "title": section.get("text"),
            "question_count": question_count,
            "path": f"/gpt/{section_path}",
        })
        resources[section_path] = {
            "resource_type": "QuestionnaireSection",
            "version": VERSION,
            "status": "research_only",
            "review_status": "unreviewed",
            "contains_patient_responses": False,
            "reason_for_encounter": "rfe.patient_experience_evaluation",
            "required_workflow_state": "activation_confirmed",
            "if_activation_not_confirmed": {
                "do_not_present_section_items": True,
                "required_question_ko": "환자경험평가 설문을 작성하시겠습니까?",
                "required_options": {
                    "1": "예",
                    "2": "아니오",
                    "3": "잘 모르겠음",
                    "4": "답변하지 않음",
                },
            },
            "questionnaire": questionnaire["url"],
            "questionnaire_version": questionnaire.get("version"),
            "section_number": number,
            "section_count": len(sections),
            "question_count": question_count,
            "item": compact(section),
        }
    if total_questions != 26:
        raise RuntimeError(
            f"patient-experience Questionnaire must contain 26 questions, got {total_questions}"
        )
    metadata_path = "questionnaires/patient-experience-5th-2025/metadata.json"
    resources[metadata_path] = {
        "resource_type": "QuestionnaireChatbotWorkflow",
        "version": VERSION,
        "status": "research_only",
        "review_status": "unreviewed",
        "contains_patient_responses": False,
        "reason_for_encounter": "rfe.patient_experience_evaluation",
        "activation_aliases_ko": [
            "환자경험평가", "환자 경험 평가", "입원 경험 설문",
            "입원 환자경험 설문", "5차 환자경험평가", "환자경험 설문",
        ],
        "activation_gate": {
            "workflow_state": "awaiting_activation_confirmation",
            "assistant_directive_ko": "설명 다음에는 아래 시작 확인 질문만 제시하십시오. 사용자가 예라고 답하기 전에는 섹션 문항을 제시하지 마십시오.",
            "required_next_question_ko": "환자경험평가 설문을 작성하시겠습니까?",
            "required_options": {
                "1": "예",
                "2": "아니오",
                "3": "잘 모르겠음",
                "4": "답변하지 않음",
            },
            "section_loading_precondition": "affirmative_activation_answer",
            "on_affirmative": "retrieve_uploaded_knowledge_file_and_present_section_1_q01_immediately_without_reconfirmation",
            "preferred_runtime_source": "patient-experience-evaluation-5th-2025-chatbot.md",
            "fallback_runtime_operation": "getPatientExperienceQuestionnaireSection(sectionId=1)",
        },
        "questionnaire": {
            "id": questionnaire["id"],
            "url": questionnaire["url"],
            "version": questionnaire.get("version"),
            "title": questionnaire.get("title"),
            "language": questionnaire.get("language"),
            "fhir_version": "4.0.1",
            "source_status": questionnaire.get("status"),
            "experimental": questionnaire.get("experimental"),
        },
        "section_count": len(sections),
        "question_count": total_questions,
        "sections": section_index,
        "loading_policy": {
            "load_metadata_after_rfe_mapping": True,
            "load_one_section_at_a_time": True,
            "never_send_answers_to_knowledge_action": True,
        },
        "presentation_policy": {
            "language": "ko",
            "activation_behavior": "after_optional_explanation_ask_only_whether_user_wants_to_complete_then_start_first_item_immediately",
            "activation_prompt_ko": "환자경험평가 설문을 작성하시겠습니까?",
            "activation_options": {
                "1": "예",
                "2": "아니오",
                "3": "잘 모르겠음",
                "4": "답변하지 않음",
            },
            "opening_screen_and_explanation_allowed": True,
            "activation_prompt_is_final_actionable_question_before_start": True,
            "affirmative_answer_enters_first_item_without_reconfirmation": True,
            "display_only_source_answer_options": True,
            "do_not_append_unknown_or_decline_options": True,
            "ask_one_question_at_a_time": True,
            "preserve_source_option_codes": True,
            "show_section_transition": True,
            "do_not_inject_clinical_history_or_screening_questions": True,
            "accept_free_text_for_additional_comments": True,
        },
        "answer_policy": {
            "choice": "store QuestionnaireResponse answer.valueCoding from selected source option",
            "integer": "store QuestionnaireResponse answer.valueInteger within declared minValue and maxValue",
            "unknown": "retain unanswered state with dataAbsentReason=asked-unknown",
            "decline": "retain unanswered state with dataAbsentReason=asked-declined",
            "edit_reference": "E{positive_integer}",
        },
        "completion_policy": {
            "after_last_question": "show section summary and explicit completion handoff",
            "before_confirmation_status": "in-progress",
            "confirmed_status": "completed",
            "stopped_status": "stopped",
            "corrected_after_completion_status": "amended",
            "completion_confirmation_is_not_consent": True,
        },
    }
    return resources


def collect(root: Path) -> dict[str, dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    questions: list[dict[str, Any]] = []
    rules: list[dict[str, Any]] = []
    screening: dict[str, Any] | None = None
    terminology_source = sanitize(
        load_json(root / "sources" / "manifests" / "stom-terminology.json")
    )

    for path in sorted((root / "knowledge").rglob("*.json")):
        document = load_json(path)
        if not isinstance(document, dict):
            continue
        if path.name == "kr-national-health-screening-2026.json":
            screening = sanitize(document)
        for node in document.get("nodes", []):
            if not isinstance(node, dict):
                continue
            if node.get("type") == "Fact":
                facts.append(node)
            elif node.get("type") == "QuestionTemplate":
                questions.append(node)
        for fact in document.get("facts", []):
            if isinstance(fact, dict):
                facts.append(fact)
        for group in document.get("question_groups", []):
            if isinstance(group, dict):
                questions.append({**group, "type": "QuestionGroup"})
        for entry in document.get("entries", []):
            if not isinstance(entry, dict) or not entry.get("question"):
                continue
            fact = entry.get("fact")
            target = entry.get("target")
            question = entry.get("question")
            fact_id = fact.get("id") if isinstance(fact, dict) else fact
            target_id = target.get("id") if isinstance(target, dict) else target
            if isinstance(question, dict):
                text = question.get("wording") or question.get("display")
                question_id = question.get("id")
            else:
                text = question
                question_id = None
            generated_id = question_id or f"generated.question.{target_id or fact_id or 'unknown'}"
            questions.append({
                "id": generated_id,
                "type": "QuestionTemplate",
                "fact_id": fact_id,
                "target_id": target_id,
                "text": text,
                "priority": entry.get("priority"),
                "supports": entry.get("supports", []),
                "status": document.get("status", "research_only"),
                "provenance": document.get("provenance", {}),
            })
        for rule in document.get("safety_rules", []):
            if isinstance(rule, dict):
                rules.append({
                    **rule,
                    "status": document.get("status", "research_only"),
                    "provenance": document.get("provenance", {}),
                })

    for path in sorted((root / "rules").rglob("*.json")):
        document = load_json(path)
        if not isinstance(document, dict):
            continue
        for rule in document.get("rules", []):
            if isinstance(rule, dict):
                rules.append(rule)

    if screening is None:
        raise RuntimeError("Korean screening knowledge is missing")
    if screening.get("status") != "research_only" or screening.get("review_status") != "unreviewed":
        raise RuntimeError("Screening knowledge must remain research_only/unreviewed")

    screening["contains_patient_responses"] = False
    catalog = sanitize(load_json(root / "knowledge" / "catalog" / "primary-care-rfe.json"))
    catalog["resource_type"] = "ReasonForEncounterCatalog"
    catalog["review_status"] = "unreviewed"
    catalog["usage_modes"] = ["research_test", "simulation"]
    catalog["contains_patient_responses"] = False
    shared_facts = load_json(root / "knowledge" / "shared" / "primary-care-facts.json")
    workflow_facts = load_json(
        root / "knowledge" / "shared" / "encounter-workflow-facts.json"
    )
    common_facts = envelope(
        "CommonInterviewFactCollection",
        deduplicate(
            shared_facts.get("facts", []) + workflow_facts.get("facts", [])
        ),
    )
    common_facts["items"] = [compact(item) for item in common_facts["items"]]
    aggregate_facts = envelope("FactCollection", deduplicate(facts))
    # Keep the legacy aggregate as a compact group index. Complete
    # QuestionTemplates are served from Reason-for-Encounter resources.
    aggregate_questions = envelope(
        "QuestionGroupCollection",
        deduplicate([
            question for question in questions
            if question.get("type") == "QuestionGroup"
        ]),
    )
    # Keep this backward-compatible aggregate small and semantically precise.
    # Full routing and priority Rules remain available in each RFE bundle.
    aggregate_rules = envelope(
        "SafetyRuleCollection",
        deduplicate([rule for rule in rules if rule.get("type") == "safety"]),
    )
    aggregate_facts["items"] = [
        compact_fact_index(item) for item in aggregate_facts["items"]
    ]
    aggregate_facts["payload_role"] = "legacy_discovery_index"
    aggregate_facts["complete_fact_payloads"] = "/gpt/rfe/{rfe}/facts.json"
    aggregate_questions["items"] = [compact(item) for item in aggregate_questions["items"]]
    aggregate_rules["items"] = [
        compact_safety_rule_index(item) for item in aggregate_rules["items"]
    ]
    aggregate_rules["payload_role"] = "legacy_cross_rfe_safety_index"
    aggregate_rules["complete_rule_payloads"] = "/gpt/rfe/{rfe}/rules.json"
    resources = {
        "common-facts.json": common_facts,
        "reason-for-encounters.json": catalog,
        "facts.json": aggregate_facts,
        "question-groups.json": aggregate_questions,
        "safety-rules.json": aggregate_rules,
        "screening-kr.json": screening,
        "terminology-source.json": terminology_source,
    }
    resources.update(collect_rfe_resources(root))
    resources.update(collect_patient_experience_questionnaire(root))
    return resources


def encoded(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def build(root: Path, output: Path) -> dict[str, Any]:
    resources = collect(root)
    encounter_policy = sanitize(
        load_json(root / "policies" / "encounter-context-review.json")
    )
    snomed_laterality_policy = sanitize(
        load_json(root / "policies" / "snomed-postcoordination-laterality.json")
    )
    korean_claim_policy = sanitize(
        load_json(root / "policies" / "korean-claim-code-binding.json")
    )
    output.mkdir(parents=True, exist_ok=True)
    manifest_resources = []
    for name, document in sorted(resources.items()):
        payload = encoded(document)
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        manifest_resources.append({
            "name": name.removesuffix(".json").replace("/", "-"),
            "path": f"/gpt/{name}",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "count": document.get(
                "count",
                document.get(
                    "question_count",
                    len(document.get("entries", document.get("question_groups", []))),
                ),
            ),
        })
    manifest = {
        "id": "clinical-interview-platform.gpt-manifest",
        "version": VERSION,
        "generated_at": GENERATED_AT,
        "status": "research_only",
        "review_status": "unreviewed",
        "contains_patient_responses": False,
        "interview_entry": {
            "type": "reason_for_encounter",
            "required_before": [
                "demographics", "medical_history", "health_screening", "routine_questions"
            ],
            "first_question_ko": "오늘 어떤 이유로 오셨나요? 불편한 증상이나 상담받고 싶은 내용을 자유롭게 말씀해 주세요.",
            "use_first_message_when_present": True,
            "confirm_only_when_ambiguous": True,
            "catalog": [
                {
                    key: entry[key]
                    for key in (
                        "id", "display", "display_ko", "aliases",
                        "implementation_status", "package_id", "questionnaire_id",
                        "activation_mode", "activation_prompt_ko",
                    )
                    if key in entry
                }
                for entry in resources["reason-for-encounters.json"]["entries"]
            ],
        },
        "additional_comment_policy": {
            "fact_id": "interview.additional_comment",
            "do_not_force_map_to_current_question": True,
            "current_question_remains_unanswered": True,
            "reassess_safety": True,
            "resolve_when_safe_and_within_scope": True,
            "resolution_includes_service_improvement": True,
            "report_resolved_and_unresolved_separately": True,
            "never_publish_raw_response": True,
        },
        "patient_experience_questionnaire_policy": resources[
            "questionnaires/patient-experience-5th-2025/metadata.json"
        ],
        "numbering_policy": {
            "display_question_sequence": False,
            "question_tracking": "stable_question_id",
            "numeric_input_reserved_for": "current_question_answer_options",
            "option_numbers_must_be_unique_within_question": True,
            "do_not_combine_independently_numbered_lists": True,
            "numeric_reply_scope": "immediately_preceding_question",
            "binary_question_only_codes": {
                "1": "yes",
                "2": "no",
                "3": "unknown",
                "5": "decline",
            },
            "enumerated_question_rule": {
                "domain_choices": "number_sequentially_from_1",
                "unknown": "next_number_after_last_domain_choice",
                "decline": "next_number_after_unknown",
                "none_of_the_above_is_domain_choice": True,
                "never_append_fixed_3_or_5": True,
            },
            "pre_send_validation": "all_displayed_option_numbers_are_unique",
        },
        "question_choice_semantic_alignment_policy": encounter_policy[
            "question_choice_semantic_alignment"
        ],
        "result_follow_up_policy": encounter_policy["result_follow_up"],
        "uploaded_clinical_material_policy": encounter_policy[
            "uploaded_clinical_material"
        ],
        "completion_handoff_policy": encounter_policy["completion_handoff"],
        "answer_revision_policy": encounter_policy["answer_revision"],
        "answer_understanding_clarification_policy": encounter_policy[
            "answer_understanding_clarification"
        ],
        "test_access_limit_notice_policy": encounter_policy[
            "test_access_limit_notice"
        ],
        "response_provenance_display_policy": encounter_policy[
            "response_provenance_display"
        ],
        "off_path_recovery_policy": encounter_policy["off_path_recovery"],
        "terminology_lookup_policy": {
            "status": "research_only",
            "review_status": "unreviewed",
            "source_id": "source.stom.fhir-r4-terminology-server",
            "action_schema_url": (
                "https://ggojang.github.io/clinical-interview-platform/"
                "gpt/stom-openapi.yaml"
            ),
            "runtime_use": "optional_semantic_alignment_only",
            "clinical_rule_selection_from_live_terminology": False,
            "send_raw_patient_response": False,
            "send_direct_identifiers": False,
            "send_only_minimal_normalized_term_or_code": True,
            "mapping_flow": [
                "normalize_korean_or_english_free_text_locally",
                "search_up_to_five_active_candidates",
                "select_or_ask_when_ambiguous",
                "verify_selected_code_with_fhir_lookup",
                "verify_finding_site_membership_in_723264001_before_laterality",
                "preserve_server_version_and_mapping_provenance",
            ],
            "fallback": "preserve_free_text_and_continue_with_compiled_knowledge",
        },
        "snomed_laterality_postcoordination_policy": snomed_laterality_policy,
        "korean_claim_code_binding_policy": korean_claim_policy,
        "longitudinal_context_review_policy": encounter_policy[
            "longitudinal_context_review"
        ],
        "preferred_loading": {
            "catalog_operation": "getReasonForEncounters",
            "common_operation": "getCommonInterviewFacts",
            "rfe_operations": [
                "getReasonForEncounterRules",
                "getReasonForEncounterQuestions",
                "getReasonForEncounterFacts",
            ],
            "questionnaire_operations": [
                "getPatientExperienceQuestionnaire",
                "getPatientExperienceQuestionnaireSection",
            ],
            "aggregate_resources_are_backward_compatible": True,
        },
        "resources": manifest_resources,
    }
    (output / "manifest.json").write_bytes(encoded(manifest))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="docs/gpt")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    manifest = build(root, output)
    print(f"Built {len(manifest['resources'])} public GPT resources in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
