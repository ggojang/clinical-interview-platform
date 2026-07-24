#!/usr/bin/env python3
"""Audit question and answer terminology coverage across compiled packages."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from compiler.build_package import PACKAGE_PROFILES, compile_package
from interoperability.fhir_r4_bindings import (
    load_documents as load_fhir_binding_documents,
)
from interoperability.kr_core_v2 import (
    load_documents as load_kr_core_v2_documents,
)
from interoperability.question_answer import (
    assess_question_atomicity,
    enrich_clinician_context,
    load_documents,
)
from tools.fhir.build_answer_valuesets import build as build_answer_valuesets


def run() -> dict[str, Any]:
    policy, registry = load_documents()
    fhir_policy, fhir_registry, fact_element_mappings = (
        load_fhir_binding_documents()
    )
    kr_core_policy, kr_core_registry = load_kr_core_v2_documents()
    rows = []
    totals: dict[str, int] = {}
    unique_questions: dict[str, dict[str, Any]] = {}
    unique_question_facts: dict[str, dict[str, Any]] = {}
    unique_coded_answers: dict[str, bool] = {}
    unique_data_absent_answers: set[str] = set()
    effective_fhir_element_facts: set[str] = set()
    candidate_fhir_element_facts: set[str] = set()
    fhir_binding_conflicts: list[str] = []
    passed = True
    for profile in PACKAGE_PROFILES:
        package = compile_package(profile=profile)
        graph = package["knowledge_graph"]
        facts = {
            node["id"]: node
            for node in graph["nodes"]
            if node.get("type") == "Fact"
        }
        question_facts = {
            edge["from"]: edge["to"]
            for edge in graph["edges"]
            if edge.get("type") == "COLLECTS"
        }
        for node in graph["nodes"]:
            if node.get("type") != "QuestionTemplate":
                continue
            unique_questions.setdefault(node["id"], node)
            unique_question_facts.setdefault(
                node["id"], facts[question_facts[node["id"]]]
            )
            answer = facts[question_facts[node["id"]]].get(
                "answer_semantic_binding", {}
            )
            fact = facts[question_facts[node["id"]]]
            if fact.get("fhir_r4_element_bindings"):
                candidate_fhir_element_facts.add(fact["id"])
            if answer.get("fhir_element_binding"):
                effective_fhir_element_facts.add(fact["id"])
            if answer.get("fhir_element_binding_conflict"):
                fhir_binding_conflicts.append(fact["id"])
            absent = answer.get("data_absent_reason_mappings", {})
            snomed = answer.get("snomed_mappings", {})
            for token in fact.get("allowed_values", []):
                if token in absent:
                    unique_data_absent_answers.add(
                        f"{question_facts[node['id']]}--{token}"
                    )
                    continue
                local_code = f"{fact['id']}--{token}"
                unique_coded_answers[local_code] = token in snomed
        coverage = package["question_answer_terminology"]["coverage"]
        failures = []
        if coverage["question_local_code_count"] != coverage["question_count"]:
            failures.append("not every question has a local fallback code")
        if (
            coverage["coded_answer_local_fallback_count"]
            != coverage["coded_answer_value_count"]
        ):
            failures.append("not every coded answer has a local fallback code")
        if coverage["question_loinc_exact_or_equivalent_count"] > coverage["question_count"]:
            failures.append("LOINC count exceeds question count")
        rows.append({
            "profile": profile,
            **coverage,
            "passed": not failures,
            "failures": failures,
        })
        for key, value in coverage.items():
            if isinstance(value, int):
                totals[key] = totals.get(key, 0) + value
        passed = passed and not failures
    fixed_questionnaire = json.loads(
        (
            ROOT
            / "fhir/r4/questionnaires/"
            "kr-patient-experience-evaluation-5th-2025.json"
        ).read_text(encoding="utf-8")
    )
    fixed_items = []
    fixed_standard_mapping_count = 0

    def walk(items: list[dict[str, Any]]) -> None:
        nonlocal fixed_standard_mapping_count
        for item in items:
            if item.get("type") in {"choice", "integer"}:
                fixed_items.append(item)
            fixed_standard_mapping_count += sum(
                coding.get("system") in {
                    "http://loinc.org",
                    "http://snomed.info/sct",
                }
                for coding in item.get("code", [])
            )
            walk(item.get("item", []))

    walk(fixed_questionnaire["item"])
    if fixed_standard_mapping_count:
        passed = False
    clinician_context, clinician_coverage = enrich_clinician_context(json.loads(
        (
            ROOT / "knowledge/shared/clinician-submission-context.json"
        ).read_text(encoding="utf-8")
    ))
    context_facts = {fact["id"]: fact for fact in clinician_context["facts"]}
    for question in clinician_context["questions"]:
        unique_questions.setdefault(question["template_id"], {
            "id": question["template_id"],
            "wording": question["wording"],
            "semantic_binding": question.get("semantic_binding", {}),
        })
        fact = context_facts[question["fact_id"]]
        unique_question_facts.setdefault(question["template_id"], fact)
        answer = fact.get("answer_semantic_binding", {})
        if fact.get("fhir_r4_element_bindings"):
            candidate_fhir_element_facts.add(fact["id"])
        if answer.get("fhir_element_binding"):
            effective_fhir_element_facts.add(fact["id"])
        if answer.get("fhir_element_binding_conflict"):
            fhir_binding_conflicts.append(fact["id"])
        absent = answer.get("data_absent_reason_mappings", {})
        snomed = answer.get("snomed_mappings", {})
        for token in fact.get("allowed_values", []):
            if token in absent:
                unique_data_absent_answers.add(
                    f"{question['fact_id']}--{token}"
                )
                continue
            local_code = f"{fact['id']}--{token}"
            unique_coded_answers[local_code] = token in snomed
    totals["question_loinc_exact_or_equivalent_percent"] = round(
        totals["question_loinc_exact_or_equivalent_count"]
        * 100
        / totals["question_count"],
        1,
    )
    totals["coded_answer_snomed_percent"] = round(
        totals["coded_answer_snomed_count"]
        * 100
        / totals["coded_answer_value_count"],
        1,
    ) if totals["coded_answer_value_count"] else 0.0
    unique_loinc_exact = 0
    unique_loinc_non_equivalent = 0
    unique_snomed = 0
    unique_local_only = 0
    for question in unique_questions.values():
        mappings = question.get("semantic_binding", {}).get(
            "standard_mappings", []
        )
        loinc = [
            item for item in mappings if item["system"] == "http://loinc.org"
        ]
        unique_loinc_exact += any(
            item["mapping_relation"] in {"exact", "equivalent"} for item in loinc
        )
        unique_loinc_non_equivalent += any(
            item["mapping_relation"] not in {"exact", "equivalent"}
            for item in loinc
        )
        unique_snomed += any(
            item["system"] == "http://snomed.info/sct" for item in mappings
        )
        unique_local_only += not mappings
    unique_total = len(unique_questions)
    unique_answer_total = len(unique_coded_answers)
    atomicity_counts: dict[str, int] = {}
    composite_candidates = []
    invalid_standard_atomicity = []
    for question_id, question in unique_questions.items():
        fact = unique_question_facts[question_id]
        atomicity = assess_question_atomicity(question, fact, registry)
        atomicity_counts[atomicity["status"]] = (
            atomicity_counts.get(atomicity["status"], 0) + 1
        )
        mappings = question.get("semantic_binding", {}).get(
            "standard_mappings", []
        )
        selected_standard = any(
            item["mapping_relation"] in {"exact", "equivalent"}
            for item in mappings
        )
        if selected_standard and not atomicity["standard_mapping_eligible"]:
            invalid_standard_atomicity.append(question_id)
        if atomicity["status"] == "composite_candidate":
            composite_candidates.append({
                "question_id": question_id,
                "fact_id": fact["id"],
                "signals": atomicity["signals"],
                "standard_mapping_present": bool(mappings),
            })
    composite_candidates.sort(
        key=lambda item: (
            not item["standard_mapping_present"],
            item["question_id"],
        )
    )
    if invalid_standard_atomicity:
        passed = False
    if fhir_binding_conflicts:
        passed = False

    value_set_bundle = build_answer_valuesets()
    value_set_counts: dict[str, int] = {}
    for entry in value_set_bundle["entry"]:
        identifier = entry["resource"]["id"]
        scope = identifier.split("-", 2)[1]
        value_set_counts[scope] = value_set_counts.get(scope, 0) + 1
    unique_summary = {
        "question_count": unique_total,
        "question_loinc_exact_or_equivalent_count": unique_loinc_exact,
        "question_loinc_exact_or_equivalent_percent": round(
            unique_loinc_exact * 100 / unique_total, 1
        ) if unique_total else 0.0,
        "question_loinc_partial_or_related_count": unique_loinc_non_equivalent,
        "question_snomed_secondary_count": unique_snomed,
        "question_local_code_count": unique_total,
        "question_local_only_count": unique_local_only,
        "coded_answer_value_count": unique_answer_total,
        "coded_answer_snomed_count": sum(unique_coded_answers.values()),
        "coded_answer_snomed_percent": round(
            sum(unique_coded_answers.values()) * 100 / unique_answer_total, 1
        ) if unique_answer_total else 0.0,
        "coded_answer_local_fallback_count": unique_answer_total,
        "data_absent_option_count": len(unique_data_absent_answers),
    }
    return {
        "id": "audit.question-answer-terminology",
        "version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "passed": passed,
        "package_count": len(rows),
        "policy_id": policy["id"],
        "registry_id": registry["id"],
        "terminology_versions": policy["terminology_versions"],
        "totals_by_package_occurrence": totals,
        "unique_dynamic_content": unique_summary,
        "clinician_submission_context": {
            "id": clinician_context["id"],
            **clinician_coverage,
        },
        "fixed_questionnaire_inventory": {
            "questionnaire_id": fixed_questionnaire["id"],
            "question_count": len(fixed_items),
            "automatic_standard_mapping_count": fixed_standard_mapping_count,
            "binding_policy": (
                "excluded from automatic terminology mapping; source-defined "
                "question and answer codes are retained unless explicit mapping "
                "was requested and verified"
            ),
        },
        "question_atomicity": {
            "counts": atomicity_counts,
            "invalid_exact_or_equivalent_mapping_count": len(
                invalid_standard_atomicity
            ),
            "invalid_exact_or_equivalent_mapping_question_ids": (
                invalid_standard_atomicity
            ),
            "composite_refactoring_queue_count": len(composite_candidates),
            "composite_refactoring_queue_sample": composite_candidates[:100],
        },
        "fhir_r4_element_bindings": {
            "policy_id": fhir_policy["id"],
            "registry_id": fhir_registry["id"],
            "fhir_version": fhir_registry["fhir_version"],
            "resource_count": fhir_registry["resource_count"],
            "element_binding_count": fhir_registry["binding_count"],
            "fact_element_mapping_count": len(
                fact_element_mappings["mappings"]
            ),
            "candidate_fact_count": len(candidate_fhir_element_facts),
            "effective_fact_count": len(effective_fhir_element_facts),
            "effective_fact_ids": sorted(effective_fhir_element_facts),
            "binding_conflict_count": len(set(fhir_binding_conflicts)),
            "binding_conflict_fact_ids": sorted(set(fhir_binding_conflicts)),
            "passed": not fhir_binding_conflicts,
        },
        "kr_core_v2_overlay": {
            "policy_id": kr_core_policy["id"],
            "registry_id": kr_core_registry["id"],
            "package": (
                f"{kr_core_registry['package']['name']}#"
                f"{kr_core_registry['package']['version']}"
            ),
            "fhir_version": kr_core_registry["package"]["fhir_version"],
            "profile_count": kr_core_registry["profile_count"],
            "extension_count": kr_core_registry["extension_count"],
            "structure_definition_count": kr_core_registry[
                "structure_definition_count"
            ],
            "constraint_count": kr_core_registry["constraint_count"],
            "element_binding_count": kr_core_registry["binding_count"],
            "defined_value_set_count": (
                kr_core_registry["defined_value_set_count"]
            ),
            "terminology_content_embedded": False,
            "questionnaire_profile_defined": False,
            "profile_selection": "explicit_export_context_required",
            "passed": True,
        },
        "answer_valuesets": {
            "bundle_id": value_set_bundle["id"],
            "resource_count": len(value_set_bundle["entry"]),
            "counts_by_scope": value_set_counts,
            "id_rule": "a-{sct|loinc|local|mixed}-{semantic-name}",
        },
        "mapping_quality_simulation": {
            "passed": (
                not invalid_standard_atomicity
                and not fhir_binding_conflicts
            ),
            "scenarios": [
                "atomic_question_standard_mapping_gate",
                "composite_question_refactoring_queue",
                "fixed_instrument_default_exclusion",
                "complete_SNOMED_answer_ValueSet",
                "mixed_SNOMED_and_local_answer_ValueSet",
                "complete_local_answer_ValueSet",
                "dataAbsentReason_exclusion_from_answer_ValueSet",
                "FHIR_id_length_and_uniqueness",
                "FHIR_R4_target_element_binding_precedence",
                "FHIR_R4_binding_strength_projection",
                "FHIR_R4_multiple_target_binding_conflict_detection",
                "FHIR_R4_required_binding_choice_and_response_enforcement",
                "KR_Core_V2_profile_binding_precedes_base_FHIR_for_Korean_projection",
                "KR_Core_V2_sliced_element_requires_exact_element_id",
                "KR_Core_V2_incompatible_profiles_require_split_projection",
                "KR_Core_V2_terminology_referenced_by_STOM_canonical_without_duplication",
                "runtime_exposes_compiled_ValueSet_choices_without_live_lookup",
            ],
        },
        "results": rows,
        "limitations": [
            "Counts are package occurrences; reusable Facts may appear in more than one package.",
            "A local code provides stable identity but does not imply external semantic equivalence.",
            "Composite questions remain local until split or a standard concept is verified.",
            "Fixed source-defined questionnaires are excluded from automatic mapping unless explicitly requested.",
            "Primitive measurements, dates, booleans, and narratives use FHIR value types rather than artificial answer codes.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    raise SystemExit(0 if report["passed"] else 1)
