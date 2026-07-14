#!/usr/bin/env python3
"""Build deterministic public GPT resources from repository knowledge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


VERSION = "0.4.4"
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
        "items": [compact(item) for item in items],
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
    aggregate_questions = envelope("QuestionCollection", deduplicate(questions))
    aggregate_rules = envelope("SafetyRuleCollection", deduplicate(rules))
    for document in (aggregate_facts, aggregate_questions, aggregate_rules):
        document["items"] = [compact(item) for item in document["items"]]
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
    return resources


def encoded(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def build(root: Path, output: Path) -> dict[str, Any]:
    resources = collect(root)
    encounter_policy = sanitize(
        load_json(root / "policies" / "encounter-context-review.json")
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
                len(document.get("entries", document.get("question_groups", []))),
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
                        "implementation_status", "package_id",
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
                "preserve_server_version_and_mapping_provenance",
            ],
            "fallback": "preserve_free_text_and_continue_with_compiled_knowledge",
        },
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
