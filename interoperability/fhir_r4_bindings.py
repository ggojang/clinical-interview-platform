"""Offline application of FHIR R4 resource element terminology bindings."""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "policies/fhir-r4-element-terminology-binding.json"
REGISTRY_PATH = ROOT / "mappings/fhir/r4/resource-element-bindings.json"
FACT_MAPPINGS_PATH = ROOT / "mappings/fhir/r4/fact-element-mappings.json"
FHIR_VERSION = "4.0.1"
LOCAL_ANSWER = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "CodeSystem/clinical-interview-answer"
)
ACTIVATING_RELATIONS = {"exact", "equivalent"}
ALLOWED_STRENGTHS = {"required", "extensible", "preferred", "example"}


@lru_cache(maxsize=1)
def load_documents() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    mappings = json.loads(FACT_MAPPINGS_PATH.read_text(encoding="utf-8"))
    validate_documents(policy, registry, mappings)
    return policy, registry, mappings


def _registry_index(registry: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    index: dict[str, list[dict[str, Any]]] = {}
    for row in registry["bindings"]:
        index.setdefault(row["element_path"], []).append(row)
    return index


@lru_cache(maxsize=1)
def _cached_registry_index() -> dict[str, list[dict[str, Any]]]:
    _, registry, _ = load_documents()
    return _registry_index(registry)


def validate_documents(
    policy: dict[str, Any],
    registry: dict[str, Any],
    mappings: dict[str, Any],
) -> None:
    for document in (policy, registry, mappings):
        if document.get("status") != "research_only":
            raise ValueError(f"{document.get('id')}: must remain research_only")
        if document.get("review_status") != "unreviewed":
            raise ValueError(f"{document.get('id')}: must remain unreviewed")
        if document.get("fhir_version") != FHIR_VERSION:
            raise ValueError(f"{document.get('id')}: must use FHIR R4 4.0.1")
    index = _registry_index(registry)
    seen: set[tuple[str, str]] = set()
    for mapping in mappings["mappings"]:
        key = (mapping["fact_id"], mapping["element_path"])
        if key in seen:
            raise ValueError(f"duplicate Fact to FHIR mapping: {key}")
        seen.add(key)
        if mapping["mapping_relation"] not in {
            "exact", "equivalent", "partial", "related", "candidate"
        }:
            raise ValueError(f"{key}: unsupported mapping relation")
        candidates = [
            row for row in index.get(mapping["element_path"], [])
            if row["resource"] == mapping["resource"]
        ]
        if not candidates:
            raise ValueError(f"{key}: target element is absent from R4 registry")
        bindings = {
            (row["binding"]["strength"], row["binding"]["value_set"])
            for row in candidates
        }
        if len(bindings) != 1:
            raise ValueError(f"{key}: target element binding is ambiguous")
        for token, coding in mapping.get("answer_code_mappings", {}).items():
            if not token or not coding.get("system") or not coding.get("code"):
                raise ValueError(f"{key}: incomplete answer coding for {token}")


def binding_for_element(
    element_path: str,
    *,
    resource: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if registry is None:
        candidates = [
            row for row in _cached_registry_index().get(element_path, [])
            if resource is None or row["resource"] == resource
        ]
    else:
        candidates = [
            row for row in _registry_index(registry).get(element_path, [])
            if resource is None or row["resource"] == resource
        ]
    if not candidates:
        return None
    unique = {
        (row["binding"]["strength"], row["binding"]["value_set"])
        for row in candidates
    }
    if len(unique) != 1:
        raise ValueError(f"{element_path}: ambiguous FHIR element binding")
    return deepcopy(candidates[0])


def fact_target_mappings(
    fact: dict[str, Any],
    mappings: dict[str, Any],
) -> list[dict[str, Any]]:
    explicit = [
        deepcopy(row) for row in mappings["mappings"]
        if row["fact_id"] == fact["id"]
    ]
    explicit_paths = {row["element_path"] for row in explicit}
    for target in fact.get("fhir_r4_targets", []):
        if not isinstance(target, str) or target in explicit_paths:
            continue
        explicit.append({
            "fact_id": fact["id"],
            "resource": target.split(".", 1)[0],
            "element_path": target,
            "mapping_relation": "candidate",
            "projection_role": "candidate",
            "provenance": {
                "source": "Fact.fhir_r4_targets",
                "review_status": "unreviewed",
            },
        })
    return explicit


def apply_element_bindings(
    fact: dict[str, Any],
    generic_answer_binding: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Return the effective answer binding and all discovered FHIR targets."""
    policy, registry, mappings = load_documents()
    discovered: list[dict[str, Any]] = []
    activating: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for mapping in fact_target_mappings(fact, mappings):
        target = binding_for_element(
            mapping["element_path"],
            resource=mapping["resource"],
            registry=registry,
        )
        if target is None:
            discovered.append({
                **mapping,
                "binding_status": "target_has_no_bound_valueset",
            })
            continue
        summary = {
            "resource": mapping["resource"],
            "element_path": mapping["element_path"],
            "mapping_relation": mapping["mapping_relation"],
            "projection_role": mapping.get("projection_role"),
            "binding_strength": target["binding"]["strength"],
            "value_set": target["binding"]["value_set"],
            "fhir_version": FHIR_VERSION,
            "structure_definition": target["structure_definition"],
            "binding_status": (
                "effective_candidate"
                if mapping["mapping_relation"] in ACTIVATING_RELATIONS
                else "annotation_only"
            ),
        }
        if mapping.get("answer_code_mappings"):
            summary["answer_code_mappings"] = deepcopy(
                mapping["answer_code_mappings"]
            )
        discovered.append(summary)
        if mapping["mapping_relation"] in ACTIVATING_RELATIONS:
            activating.append((mapping, target))
    if not activating:
        return deepcopy(generic_answer_binding), discovered
    unique = {
        (target["binding"]["strength"], target["binding"]["value_set"])
        for _, target in activating
    }
    if len(unique) != 1:
        return {
            **(deepcopy(generic_answer_binding) or {}),
            "fhir_element_binding_conflict": {
                "status": "projection_split_required",
                "targets": discovered,
            },
        }, discovered
    mapping, target = activating[0]
    strength = target["binding"]["strength"]
    if strength not in ALLOWED_STRENGTHS:
        raise ValueError(f"unsupported FHIR binding strength: {strength}")
    strength_rule = policy["binding_strength_rules"][strength]
    if strength == "required" and fact.get("allowed_values"):
        absent = set(
            (generic_answer_binding or {})
            .get("data_absent_reason_mappings", {})
        )
        expected = set(fact["allowed_values"]) - absent
        mapped = set(mapping.get("answer_code_mappings", {}))
        missing = sorted(expected - mapped)
        if missing:
            raise ValueError(
                f"{fact['id']}: required FHIR element binding has no "
                f"answer coding for {', '.join(missing)}"
            )
    effective = deepcopy(generic_answer_binding) or {}
    if effective.get("answer_value_set"):
        effective["generic_answer_value_set"] = effective["answer_value_set"]
    effective.update({
        "strategy": "FHIR_R4_element_binding_then_generic_SNOMED_CT_and_local",
        "value_set_strategy": "fhir_r4_element_binding",
        "answer_value_set": target["binding"]["value_set"],
        "fhir_item_type": strength_rule["questionnaire_item_type"],
        "fhir_response_type": "valueCoding",
        "fhir_element_binding": {
            "resource": mapping["resource"],
            "element_path": mapping["element_path"],
            "mapping_relation": mapping["mapping_relation"],
            "strength": strength,
            "value_set": target["binding"]["value_set"],
            "allow_outside_code": strength_rule["allow_outside_code"],
            "fhir_version": FHIR_VERSION,
            "structure_definition": target["structure_definition"],
        },
    })
    if mapping.get("answer_code_mappings"):
        effective["fhir_bound_answer_mappings"] = deepcopy(
            mapping["answer_code_mappings"]
        )
    return effective, discovered


def questionnaire_item_projection(fact: dict[str, Any]) -> dict[str, Any]:
    """Project compiled answer-binding metadata onto a Questionnaire item."""
    binding = fact.get("answer_semantic_binding", {})
    result: dict[str, Any] = {}
    if binding.get("fhir_item_type"):
        result["type"] = binding["fhir_item_type"]
    if binding.get("answer_value_set"):
        result["answerValueSet"] = binding["answer_value_set"]
    if binding.get("fhir_element_binding"):
        result["_targetElementBinding"] = deepcopy(
            binding["fhir_element_binding"]
        )
    return result


def questionnaire_response_answer_projection(
    fact: dict[str, Any],
    internal_value: str,
) -> dict[str, Any]:
    """Project one compiled coded answer without conflating absent data."""
    binding = fact.get("answer_semantic_binding", {})
    absent = binding.get("data_absent_reason_mappings", {}).get(internal_value)
    if absent:
        return {"dataAbsentReason": absent}
    coding = binding.get("fhir_bound_answer_mappings", {}).get(internal_value)
    if coding:
        return {"valueCoding": deepcopy(coding)}
    element_binding = binding.get("fhir_element_binding", {})
    if element_binding.get("strength") == "required":
        raise ValueError(
            f"{fact['id']}: {internal_value!r} cannot be projected outside "
            f"required ValueSet {element_binding.get('value_set')}"
        )
    coding = binding.get("snomed_mappings", {}).get(internal_value)
    if coding:
        return {
            "valueCoding": {
                key: coding[key]
                for key in ("system", "code", "display")
                if key in coding
            }
        }
    if internal_value not in fact.get("allowed_values", []):
        return {"valueString": str(internal_value)}
    return {
        "valueCoding": {
            "system": LOCAL_ANSWER,
            "code": f"{fact['id']}--{internal_value}",
            "display": internal_value,
        }
    }
