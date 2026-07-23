#!/usr/bin/env python3
"""Build complete local fallback CodeSystems for dynamic interview content."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from compiler.build_package import PACKAGE_PROFILES, compile_package
from interoperability.question_answer import (
    LOCAL_ANSWER,
    LOCAL_QUESTION,
    enrich_clinician_context,
)


OUTPUT = ROOT / "fhir/r4/codesystems"
CANONICAL = "https://ggojang.github.io/clinical-interview-platform/fhir"


def _base(identifier: str, url: str, title: str, description: str) -> dict[str, Any]:
    return {
        "resourceType": "CodeSystem",
        "id": identifier,
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/CodeSystem"],
            "tag": [
                {
                    "system": f"{CANONICAL}/CodeSystem/content-status",
                    "code": "research-only",
                    "display": "Research only",
                },
                {
                    "system": f"{CANONICAL}/CodeSystem/review-status",
                    "code": "unreviewed",
                    "display": "Unreviewed",
                },
            ],
        },
        "url": url,
        "version": "0.1.0",
        "name": "".join(part.title() for part in identifier.split("-")),
        "title": title,
        "status": "draft",
        "experimental": True,
        "date": "2026-07-23",
        "publisher": "Clinical Interview Knowledge Platform",
        "description": description,
        "caseSensitive": True,
        "valueSet": f"{CANONICAL}/ValueSet/{identifier}",
        "hierarchyMeaning": "is-a",
        "compositional": False,
        "versionNeeded": True,
        "content": "complete",
        "concept": [],
    }


def build() -> tuple[dict[str, Any], dict[str, Any]]:
    questions: dict[str, dict[str, str]] = {}
    answers: dict[str, dict[str, str]] = {}

    def add_question(
        code: str, display: str, fact_id: str
    ) -> None:
        candidate = {
            "code": code,
            "display": display,
            "definition": f"Local fallback code for the question collecting {fact_id}.",
        }
        previous = questions.setdefault(code, candidate)
        if previous != candidate:
            raise ValueError(f"conflicting local question code: {code}")

    def add_answer(
        code: str, display: str, fact_id: str, internal_value: str
    ) -> None:
        candidate = {
            "code": code,
            "display": display,
            "definition": f"Local fallback answer for {fact_id}: {internal_value}.",
        }
        previous = answers.setdefault(code, candidate)
        if previous != candidate:
            raise ValueError(f"conflicting local answer code: {code}")

    add_answer("boolean--yes", "yes", "boolean", "yes")
    add_answer("boolean--no", "no", "boolean", "no")

    for profile in PACKAGE_PROFILES:
        graph = compile_package(profile=profile)["knowledge_graph"]
        question_facts = {
            edge["from"]: edge["to"]
            for edge in graph["edges"]
            if edge.get("type") == "COLLECTS"
        }
        for node in graph["nodes"]:
            if node.get("type") == "QuestionTemplate":
                add_question(
                    node["id"], node["wording"], question_facts[node["id"]]
                )
            if node.get("type") != "Fact":
                continue
            absent = node.get("answer_semantic_binding", {}).get(
                "data_absent_reason_mappings", {}
            )
            for token in node.get("allowed_values", []):
                if token in absent:
                    continue
                add_answer(
                    f"{node['id']}--{token}",
                    token,
                    node["id"],
                    token,
                )
    context, _ = enrich_clinician_context(json.loads(
        (
            ROOT / "knowledge/shared/clinician-submission-context.json"
        ).read_text(encoding="utf-8")
    ))
    context_facts = {fact["id"]: fact for fact in context["facts"]}
    for question in context["questions"]:
        add_question(
            question["template_id"], question["wording"], question["fact_id"]
        )
        fact = context_facts[question["fact_id"]]
        absent = fact.get("answer_semantic_binding", {}).get(
            "data_absent_reason_mappings", {}
        )
        for token in fact.get("allowed_values", []):
            if token not in absent:
                add_answer(
                    f"{fact['id']}--{token}",
                    token,
                    fact["id"],
                    token,
                )
    question_system = _base(
        "clinical-interview-question",
        LOCAL_QUESTION,
        "Clinical Interview Question Codes",
        "Complete local fallback codes for dynamic research-only interview questions. "
        "A verified LOINC code is preferred when available.",
    )
    answer_system = _base(
        "clinical-interview-answer",
        LOCAL_ANSWER,
        "Clinical Interview Answer Codes",
        "Complete context-qualified local codes for coded dynamic interview "
        "answers. They remain available for round-trip identity even when a "
        "verified SNOMED CT equivalent also exists.",
    )
    question_system["concept"] = [questions[key] for key in sorted(questions)]
    question_system["count"] = len(question_system["concept"])
    answer_system["concept"] = [answers[key] for key in sorted(answers)]
    answer_system["count"] = len(answer_system["concept"])
    return question_system, answer_system


def validate(document: dict[str, Any]) -> None:
    if document.get("resourceType") != "CodeSystem":
        raise ValueError("not a CodeSystem")
    if document.get("status") != "draft" or document.get("experimental") is not True:
        raise ValueError("local CodeSystem must remain draft and experimental")
    codes = [concept["code"] for concept in document.get("concept", [])]
    if len(codes) != len(set(codes)) or document.get("count") != len(codes):
        raise ValueError("CodeSystem count or code uniqueness failure")
    if any(not code or any(char.isspace() for char in code) for code in codes):
        raise ValueError("CodeSystem codes must be non-empty and contain no whitespace")


def write() -> tuple[Path, Path]:
    question, answer = build()
    validate(question)
    validate(answer)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    question_path = OUTPUT / "clinical-interview-question.json"
    answer_path = OUTPUT / "clinical-interview-answer.json"
    question_path.write_text(
        json.dumps(question, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    answer_path.write_text(
        json.dumps(answer, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return question_path, answer_path


if __name__ == "__main__":
    for path in write():
        print(path.relative_to(ROOT))
