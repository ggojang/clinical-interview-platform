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
from interoperability.question_answer import enrich_clinician_context, load_documents


def run() -> dict[str, Any]:
    policy, registry = load_documents()
    rows = []
    totals: dict[str, int] = {}
    unique_questions: dict[str, dict[str, Any]] = {}
    unique_coded_answers: dict[str, bool] = {}
    unique_data_absent_answers: set[str] = set()
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
            answer = facts[question_facts[node["id"]]].get(
                "answer_semantic_binding", {}
            )
            fact = facts[question_facts[node["id"]]]
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

    def walk(items: list[dict[str, Any]]) -> None:
        for item in items:
            if item.get("type") in {"choice", "integer"}:
                fixed_items.append(item)
            walk(item.get("item", []))

    walk(fixed_questionnaire["item"])
    clinician_context, clinician_coverage = enrich_clinician_context(json.loads(
        (
            ROOT / "knowledge/shared/clinician-submission-context.json"
        ).read_text(encoding="utf-8")
    ))
    context_facts = {fact["id"]: fact for fact in clinician_context["facts"]}
    for question in clinician_context["questions"]:
        unique_questions.setdefault(question["template_id"], {
            "id": question["template_id"],
            "semantic_binding": question.get("semantic_binding", {}),
        })
        fact = context_facts[question["fact_id"]]
        answer = fact.get("answer_semantic_binding", {})
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
            "binding_policy": (
                "source-defined local question and answer codes are retained; "
                "no unverified LOINC or SNOMED equivalence is asserted"
            ),
        },
        "results": rows,
        "limitations": [
            "Counts are package occurrences; reusable Facts may appear in more than one package.",
            "A local code provides stable identity but does not imply external semantic equivalence.",
            "Composite questions remain local until split or a standard concept is verified.",
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
