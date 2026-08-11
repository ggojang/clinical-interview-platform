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
    LOCAL_ANSWER_DOMAIN,
    SNOMED,
    VALUESET_BASE,
    answer_valueset_id,
    answer_valueset_url,
    enrich_clinician_context,
    load_answer_domains,
)


OUTPUT = ROOT / "fhir/r4/valuesets/clinical-interview-answer-valuesets.json"
CANONICAL = "https://ggojang.github.io/clinical-interview-platform/fhir"
ARTIFACT_LIFECYCLE = f"{CANONICAL}/CodeSystem/artifact-lifecycle"
REPLACED_BY_EXTENSION = (
    f"{CANONICAL}/StructureDefinition/artifact-replaced-by"
)


def _valueset(
    identifier: str,
    title: str,
    description: str,
    concepts_by_system: dict[str, list[dict[str, str]]],
    *,
    content_status: str = "research-only",
    publication_status: str = "draft",
    replaced_by: str | None = None,
    resource_date: str = "2026-07-23",
) -> dict[str, Any]:
    includes = []
    for system in sorted(concepts_by_system):
        concepts = sorted(
            concepts_by_system[system],
            key=lambda item: (item["code"], item.get("display", "")),
        )
        includes.append({"system": system, "concept": concepts})
    tags = [
        {
            "system": f"{CANONICAL}/CodeSystem/content-status",
            "code": content_status,
            "display": (
                "Draft; limited use allowed"
                if content_status == "draft-limited-use"
                else (
                    "Retired compatibility artifact"
                    if content_status == "retired-compatibility"
                    else "Research only"
                )
            ),
        },
        {
            "system": f"{CANONICAL}/CodeSystem/review-status",
            "code": "unreviewed",
            "display": "Unreviewed",
        },
    ]
    extensions = []
    if publication_status == "retired":
        if not replaced_by:
            raise ValueError(f"{identifier}: retired ValueSet requires replaced_by")
        tags.append({
            "system": ARTIFACT_LIFECYCLE,
            "code": "retired",
            "display": "Retired; compatibility only",
        })
        extensions.append({
            "url": REPLACED_BY_EXTENSION,
            "valueCanonical": replaced_by,
        })
    resource = {
        "resourceType": "ValueSet",
        "id": identifier,
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/ValueSet"],
            "tag": tags,
        },
        "url": f"{VALUESET_BASE}/{identifier}",
        "version": "0.1.0",
        "name": "".join(part.title() for part in identifier.split("-")),
        "title": title,
        "status": publication_status,
        "experimental": True,
        "date": resource_date,
        "publisher": "Clinical Interview Knowledge Platform",
        "description": description,
        "immutable": publication_status == "retired",
        "compose": {"include": includes},
    }
    if extensions:
        resource["extension"] = extensions
    return resource


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

    domain_registry = load_answer_domains()
    migration_aliases: dict[
        str, tuple[dict[str, Any], list[dict[str, Any]]]
    ] = {}
    for domain_id, domain in domain_registry["domains"].items():
        concepts_by_system: dict[str, list[dict[str, str]]] = defaultdict(list)
        for concept in domain["concepts"]:
            concepts_by_system[concept.get("system", LOCAL_ANSWER_DOMAIN)].append({
                "code": concept["code"],
                "display": concept["display"],
            })
        add(_valueset(
            domain["value_set_id"],
            f"Reusable {domain_id.replace('-', ' ').title()} Answers",
            "Complete reusable atomic answer domain. Knowledge profiles may "
            "present a clinically relevant preferred subset, while open-choice "
            "input can retain an unlisted patient expression.",
            dict(concepts_by_system),
            content_status="draft-limited-use",
        ))
        aliases: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in domain.get("migration", {}).get("legacy_value_sets", []):
            aliases[item["fact_id"]].append(item)
        for fact_id, binding in domain.get("fact_bindings", {}).items():
            if binding.get("status") != "active_pilot" or fact_id not in aliases:
                continue
            migration_aliases[fact_id] = (domain, aliases[fact_id])

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
        migration = migration_aliases.get(fact_id)
        if migration:
            domain, aliases = migration
            replacement = answer_valueset_url(domain["value_set_id"])
            domain_binding = domain["fact_bindings"][fact_id]
            domain_concepts = {
                concept["code"]: concept for concept in domain["concepts"]
            }
            legacy_standard: dict[str, dict[str, str]] = {}
            for token, domain_code in domain_binding.get(
                "legacy_token_map", {}
            ).items():
                concept = domain_concepts.get(domain_code, {})
                if concept.get("system") == SNOMED:
                    legacy_standard[token] = {
                        "code": concept["code"],
                        "display": concept["display"],
                    }
            mapped = [
                token for token in coded_values if token in legacy_standard
            ]
            expected_aliases: dict[str, dict[str, list[dict[str, str]]]] = {
                local_id: {LOCAL_ANSWER: local_concepts},
            }
            if mapped and len(mapped) < len(coded_values):
                mixed_id = answer_valueset_id(
                    "mixed",
                    f"{fact_id}-{fact.get('value_type')}-{answer_shape}",
                )
                mixed_concepts: dict[
                    str, list[dict[str, str]]
                ] = defaultdict(list)
                for token in coded_values:
                    if token in legacy_standard:
                        mixed_concepts[SNOMED].append({
                            "code": legacy_standard[token]["code"],
                            "display": legacy_standard[token]["display"],
                        })
                    else:
                        mixed_concepts[LOCAL_ANSWER].append({
                            "code": f"{fact_id}--{token}",
                            "display": token,
                        })
                expected_aliases[mixed_id] = dict(mixed_concepts)
            elif mapped and len(mapped) == len(coded_values):
                standard_id = answer_valueset_id(
                    "sct", "-".join(sorted(coded_values))
                )
                expected_aliases[standard_id] = {
                    SNOMED: [
                        {
                            "code": legacy_standard[token]["code"],
                            "display": legacy_standard[token]["display"],
                        }
                        for token in coded_values
                    ]
                }
            for alias in aliases:
                alias_id = alias.get("id", "")
                if alias.get("status") != "retired":
                    raise ValueError(
                        f"{fact_id}: compatibility alias must be retired"
                    )
                concepts_by_system = expected_aliases.get(alias_id)
                if concepts_by_system is None:
                    raise ValueError(
                        f"{fact_id}: recorded legacy ValueSet id does not match "
                        "a deterministic former local or mixed ValueSet id: "
                        f"{alias_id}"
                    )
                add(_valueset(
                    alias_id,
                    f"Retired Answers for {fact_id}",
                    "Retired compatibility ValueSet for the former Fact-specific "
                    f"answer set of {fact_id}. Current content uses {replacement}.",
                    concepts_by_system,
                    content_status="retired-compatibility",
                    publication_status="retired",
                    replaced_by=replacement,
                    resource_date="2026-08-11",
                ))
            continue
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
        publication_status = resource.get("status")
        if publication_status not in {"draft", "retired"}:
            raise ValueError("answer ValueSets must be draft or retired")
        if resource.get("experimental") is not True:
            raise ValueError("answer ValueSets must remain experimental")
        lifecycle_codes = {
            tag.get("code")
            for tag in resource.get("meta", {}).get("tag", [])
            if tag.get("system") == ARTIFACT_LIFECYCLE
        }
        replacement_extensions = [
            extension
            for extension in resource.get("extension", [])
            if extension.get("url") == REPLACED_BY_EXTENSION
        ]
        if publication_status == "retired":
            if lifecycle_codes != {"retired"}:
                raise ValueError(
                    f"retired answer ValueSet lacks lifecycle tag: {identifier}"
                )
            if len(replacement_extensions) != 1 or not replacement_extensions[
                0
            ].get("valueCanonical"):
                raise ValueError(
                    f"retired answer ValueSet lacks replacement: {identifier}"
                )
        elif lifecycle_codes or replacement_extensions:
            raise ValueError(
                f"active answer ValueSet has retirement metadata: {identifier}"
            )
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
