#!/usr/bin/env python3
"""Build reusable FHIR R4 answer ValueSets for dynamic interview content."""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from compiler.build_package import PACKAGE_PROFILES, compile_package
from interoperability.question_answer import (
    LOCAL_ANSWER,
    SNOMED,
    VALUESET_BASE,
    answer_valueset_id,
    enrich_clinician_context,
)


OUTPUT = ROOT / "fhir/r4/valuesets/clinical-interview-answer-valuesets.json"
CANONICAL = "https://ggojang.github.io/clinical-interview-platform/fhir"


def _valueset(
    identifier: str,
    title: str,
    description: str,
    concepts_by_system: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    includes = []
    for system in sorted(concepts_by_system):
        concepts = sorted(
            concepts_by_system[system],
            key=lambda item: (item["code"], item.get("display", "")),
        )
        includes.append({"system": system, "concept": concepts})
    return {
        "resourceType": "ValueSet",
        "id": identifier,
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/ValueSet"],
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
        "url": f"{VALUESET_BASE}/{identifier}",
        "version": "0.1.0",
        "name": "".join(part.title() for part in identifier.split("-")),
        "title": title,
        "status": "draft",
        "experimental": True,
        "date": "2026-07-23",
        "publisher": "Clinical Interview Knowledge Platform",
        "description": description,
        "immutable": False,
        "compose": {"include": includes},
    }


def _all_enriched_facts() -> list[dict[str, Any]]:
    facts: dict[tuple[str, str, tuple[str, ...]], dict[str, Any]] = {}

    def add(fact: dict[str, Any]) -> None:
        key = (
            fact["id"],
            str(fact.get("value_type")),
            tuple(fact.get("allowed_values", [])),
        )
        facts.setdefault(key, fact)

    for profile in PACKAGE_PROFILES:
        graph = compile_package(profile=profile)["knowledge_graph"]
        for node in graph["nodes"]:
            if node.get("type") == "Fact":
                add(node)
    context, _ = enrich_clinician_context(json.loads(
        (
            ROOT / "knowledge/shared/clinician-submission-context.json"
        ).read_text(encoding="utf-8")
    ))
    for fact in context["facts"]:
        add(fact)
    return [facts[key] for key in sorted(facts)]


def build() -> dict[str, Any]:
    resources: dict[str, dict[str, Any]] = {}

    def add(resource: dict[str, Any]) -> None:
        identifier = resource["id"]
        previous = resources.setdefault(identifier, resource)
        if previous != resource:
            raise ValueError(f"conflicting answer ValueSet id: {identifier}")

    yes_no_sct = answer_valueset_id("sct", "yes-no")
    add(_valueset(
        yes_no_sct,
        "SNOMED CT Yes No Answers",
        "Verified SNOMED CT answers for a coded yes/no interview item.",
        {
            SNOMED: [
                {"code": "373066001", "display": "Yes"},
                {"code": "373067005", "display": "No"},
            ]
        },
    ))
    yes_no_local = answer_valueset_id("local", "yes-no")
    add(_valueset(
        yes_no_local,
        "Local Yes No Answers",
        "Local fallback answers for a coded yes/no interview item.",
        {
            LOCAL_ANSWER: [
                {"code": "boolean--yes", "display": "yes"},
                {"code": "boolean--no", "display": "no"},
            ]
        },
    ))

    for fact in _all_enriched_facts():
        fact_id = fact["id"]
        allowed_values = fact.get("allowed_values")
        if not allowed_values:
            continue
        binding = fact.get("answer_semantic_binding", {})
        absent = binding.get("data_absent_reason_mappings", {})
        snomed = binding.get("snomed_mappings", {})
        coded_values = [token for token in allowed_values if token not in absent]
        if not coded_values:
            continue

        answer_shape = "-".join(coded_values)
        local_id = answer_valueset_id(
            "local",
            f"{fact_id}-{fact.get('value_type')}-{answer_shape}",
        )
        local_concepts = [
            {
                "code": f"{fact_id}--{token}",
                "display": token,
            }
            for token in coded_values
        ]
        add(_valueset(
            local_id,
            f"Local Answers for {fact_id}",
            "Complete local fallback answer set for the dynamic interview Fact "
            f"{fact_id}.",
            {LOCAL_ANSWER: local_concepts},
        ))

        mapped = [token for token in coded_values if token in snomed]
        if len(mapped) == len(coded_values):
            standard_id = answer_valueset_id(
                "sct", "-".join(sorted(coded_values))
            )
            add(_valueset(
                standard_id,
                "SNOMED CT Answers " + " ".join(sorted(coded_values)),
                "Complete verified SNOMED CT answer set shared by compatible "
                "dynamic interview questions.",
                {
                    SNOMED: [
                        {
                            "code": snomed[token]["code"],
                            "display": snomed[token]["display"],
                        }
                        for token in coded_values
                    ]
                },
            ))
        elif mapped:
            mixed_id = answer_valueset_id(
                "mixed",
                f"{fact_id}-{fact.get('value_type')}-{answer_shape}",
            )
            by_system: dict[str, list[dict[str, str]]] = defaultdict(list)
            for token in coded_values:
                if token in snomed:
                    by_system[SNOMED].append({
                        "code": snomed[token]["code"],
                        "display": snomed[token]["display"],
                    })
                else:
                    by_system[LOCAL_ANSWER].append({
                        "code": f"{fact_id}--{token}",
                        "display": token,
                    })
            add(_valueset(
                mixed_id,
                f"Mixed Standard and Local Answers for {fact_id}",
                "Complete answer set using verified SNOMED CT concepts where "
                "available and context-qualified local codes otherwise.",
                dict(by_system),
            ))

    bundle = {
        "resourceType": "Bundle",
        "id": "clinical-interview-answer-valuesets",
        "type": "collection",
        "timestamp": "2026-07-23T00:00:00Z",
        "entry": [
            {
                "fullUrl": resource["url"],
                "resource": resource,
            }
            for _, resource in sorted(resources.items())
        ],
    }
    return bundle


def validate(bundle: dict[str, Any]) -> None:
    if bundle.get("resourceType") != "Bundle" or bundle.get("type") != "collection":
        raise ValueError("answer ValueSets must be emitted as a collection Bundle")
    ids = []
    urls = []
    for entry in bundle.get("entry", []):
        resource = entry.get("resource", {})
        if resource.get("resourceType") != "ValueSet":
            raise ValueError("Bundle contains a non-ValueSet resource")
        identifier = resource.get("id", "")
        if not identifier.startswith(("a-sct-", "a-loinc-", "a-local-", "a-mixed-")):
            raise ValueError(f"invalid answer ValueSet id: {identifier}")
        if len(identifier) > 64:
            raise ValueError(f"FHIR id exceeds 64 characters: {identifier}")
        if resource.get("status") != "draft" or resource.get("experimental") is not True:
            raise ValueError("answer ValueSets must remain draft and experimental")
        if entry.get("fullUrl") != resource.get("url"):
            raise ValueError(f"fullUrl mismatch: {identifier}")
        includes = resource.get("compose", {}).get("include", [])
        if not includes or any(not include.get("concept") for include in includes):
            raise ValueError(f"empty answer ValueSet: {identifier}")
        ids.append(identifier)
        urls.append(resource["url"])
    if len(ids) != len(set(ids)) or len(urls) != len(set(urls)):
        raise ValueError("duplicate answer ValueSet id or canonical URL")


def write() -> Path:
    bundle = build()
    validate(bundle)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return OUTPUT


if __name__ == "__main__":
    path = write()
    print(path.relative_to(ROOT))
