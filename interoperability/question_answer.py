"""Build-time question and answer terminology bindings.

The repository model remains canonical. This module adds an interoperability
overlay and never changes interview priority, safety, routing, or completion.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
from typing import Any

from interoperability.fhir_r4_bindings import apply_element_bindings

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "policies/question-answer-terminology-binding.json"
REGISTRY_PATH = ROOT / "mappings/terminology/question-answer-bindings.json"

LOINC = "http://loinc.org"
SNOMED = "http://snomed.info/sct"
LOCAL_QUESTION = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "CodeSystem/clinical-interview-question"
)
LOCAL_ANSWER = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "CodeSystem/clinical-interview-answer"
)
VALUESET_BASE = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/ValueSet"
)


def load_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    validate_documents(policy, registry)
    return policy, registry


def validate_documents(policy: dict[str, Any], registry: dict[str, Any]) -> None:
    if policy.get("status") != "research_only":
        raise ValueError("question-answer terminology policy must remain research_only")
    if policy.get("review_status") != "unreviewed":
        raise ValueError("question-answer terminology policy must remain unreviewed")
    allowed_relations = set(policy["mapping_relations"])
    atomic_facts = set(registry["verified_atomic_question_fact_ids"])
    verification = registry["verification"]
    for fact_id, mappings in registry["question_mappings"].items():
        if not fact_id or not mappings:
            raise ValueError("question mapping requires a Fact id and mappings")
        for mapping in mappings:
            if mapping["relation"] not in allowed_relations:
                raise ValueError(f"{fact_id}: unsupported relation {mapping['relation']}")
            if mapping["system"] not in {LOINC, SNOMED}:
                raise ValueError(f"{fact_id}: unsupported standard system")
            if not mapping.get("code") or not mapping.get("display"):
                raise ValueError(f"{fact_id}: mapping requires code and display")
            if not 0 <= float(mapping["confidence"]) <= 1:
                raise ValueError(f"{fact_id}: invalid mapping confidence")
            if (
                mapping["relation"] in {"exact", "equivalent"}
                and fact_id not in atomic_facts
            ):
                raise ValueError(
                    f"{fact_id}: exact/equivalent mapping requires verified atomicity"
                )
    for mapping in registry["generic_snomed_answer_mappings"].values():
        if not mapping.get("code") or not mapping.get("display"):
            raise ValueError("generic SNOMED answer mapping is incomplete")
    if not verification.get("verified_at") or not verification.get("verification_source"):
        raise ValueError("terminology registry verification metadata is incomplete")


def answer_valueset_id(scope: str, semantic_name: str) -> str:
    """Return a deterministic FHIR id following the a-{scope}-{name} rule."""
    if scope not in {"sct", "loinc", "local", "mixed"}:
        raise ValueError(f"unsupported answer ValueSet scope: {scope}")
    slug = re.sub(r"[^a-z0-9]+", "-", semantic_name.lower()).strip("-")
    prefix = f"a-{scope}-"
    candidate = prefix + (slug or "answers")
    if len(candidate) <= 64:
        return candidate
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()[:10]
    return f"{candidate[:53].rstrip('-')}-{digest}"


def answer_valueset_url(identifier: str) -> str:
    return f"{VALUESET_BASE}/{identifier}"


def assess_question_atomicity(
    question: dict[str, Any],
    fact: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    """Classify mapping fitness without changing Runtime question behavior."""
    if fact["id"] in set(registry["verified_atomic_question_fact_ids"]):
        return {
            "status": "atomic_verified",
            "standard_mapping_eligible": True,
            "signals": ["verified_atomic_fact_registry"],
        }
    wording = str(question.get("wording") or question.get("display") or "")
    signals = []
    if "_and_" in fact["id"]:
        signals.append("fact_id_contains_and")
    separators = {
        "middle_dot_list": wording.count("·"),
        "comma_list": wording.count(",") + wording.count("，"),
        "and_conjunction": wording.count(" 및 ") + wording.count(" 그리고 "),
        "slash_list": wording.count("/"),
    }
    if sum(separators.values()) >= 2:
        signals.append("wording_contains_multiple_semantic_list_markers")
    if len(fact.get("allowed_values", [])) > 12:
        signals.append("large_multidimensional_answer_list")
    composite = bool(signals)
    return {
        "status": "composite_candidate" if composite else "atomic_candidate",
        "standard_mapping_eligible": False,
        "signals": signals,
    }


def _standard_mapping(
    internal_id: str,
    mapping: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    verification = registry["verification"]
    system = mapping["system"]
    return {
        "internal_object_identifier": internal_id,
        "system": system,
        "code": mapping["code"],
        "display": mapping["display"],
        "mapping_relation": mapping["relation"],
        "confidence": mapping["confidence"],
        "terminology_version": (
            verification["loinc_version"]
            if system == LOINC else verification["snomed_version"]
        ),
        "verification_source": verification["verification_source"],
        "verified_at": verification["verified_at"],
        "review_status": verification["review_status"],
        "selected_for_fhir_item_code": mapping["relation"] in {"exact", "equivalent"},
    }


def _inherited_snomed_mapping(
    fact: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any] | None:
    binding = fact.get("terminology_binding")
    if not isinstance(binding, dict) or binding.get("system") != SNOMED:
        return None
    code = binding.get("code") or binding.get("focus_code")
    if not code:
        return None
    return {
        "internal_object_identifier": fact["id"],
        "system": SNOMED,
        "code": code,
        "display": fact.get("display", fact["id"]),
        "mapping_relation": "related",
        "confidence": 0.5,
        "terminology_version": registry["verification"]["snomed_version"],
        "verification_source": "Fact.terminology_binding",
        "verified_at": None,
        "review_status": "unreviewed",
        "selected_for_fhir_item_code": False,
        "note": "Inherited as secondary question semantics; equivalence was not asserted.",
    }


def _question_binding(
    question: dict[str, Any],
    fact: dict[str, Any],
    policy: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    mappings = [
        _standard_mapping(fact["id"], mapping, registry)
        for mapping in registry["question_mappings"].get(fact["id"], [])
    ]
    if not any(mapping["system"] == SNOMED for mapping in mappings):
        inherited = _inherited_snomed_mapping(fact, registry)
        if inherited:
            mappings.append(inherited)
    compact_mappings = [{
        "system": mapping["system"],
        "code": mapping["code"],
        "mapping_relation": mapping["mapping_relation"],
    } for mapping in mappings]
    fhir_codes = [
            {
                "system": mapping["system"],
                "code": mapping["code"],
            }
            for mapping in mappings
            if mapping["selected_for_fhir_item_code"]
        ]
    result = {"standard_mappings": compact_mappings}
    if fhir_codes:
        result["fhir_standard_item_codes"] = fhir_codes
    return result


def _snomed_answer(
    fact_id: str,
    token: str,
    registry: dict[str, Any],
) -> dict[str, Any] | None:
    mapping = (
        registry["fact_specific_snomed_answer_mappings"]
        .get(fact_id, {})
        .get(token)
    )
    if mapping is None:
        mapping = registry["generic_snomed_answer_mappings"].get(token)
    if mapping is None:
        return None
    return {
        "system": SNOMED,
        "code": mapping["code"],
        "display": mapping["display"],
        "mapping_relation": mapping.get("relation", "equivalent"),
    }


def _answer_binding(
    fact: dict[str, Any],
    policy: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any] | None:
    value_type = fact.get("value_type")
    if value_type == "boolean":
        standard_id = answer_valueset_id("sct", "yes-no")
        local_id = answer_valueset_id("local", "yes-no")
        return {
            "strategy": "SNOMED_CT_coded_yes_no_with_local_fallback",
            "policy_id": policy["id"],
            "answer_value_set": answer_valueset_url(standard_id),
            "local_answer_value_set": answer_valueset_url(local_id),
            "fhir_item_type": "choice",
            "fhir_response_type": "valueCoding",
        }
    allowed_values = fact.get("allowed_values")
    if allowed_values:
        snomed_mappings = {}
        data_absent_mappings = {}
        for token in allowed_values:
            absent = registry["data_absent_tokens"].get(token)
            if absent:
                data_absent_mappings[token] = absent
                continue
            snomed = _snomed_answer(fact["id"], token, registry)
            if snomed:
                snomed_mappings[token] = snomed
        result = {
            "strategy": "SNOMED_CT_then_local_coded_fallback",
            "policy_id": policy["id"],
        }
        if snomed_mappings:
            result["snomed_mappings"] = snomed_mappings
        if data_absent_mappings:
            result["data_absent_reason_mappings"] = data_absent_mappings
        coded_values = [
            token for token in allowed_values
            if token not in data_absent_mappings
        ]
        answer_shape = "-".join(coded_values)
        local_id = answer_valueset_id(
            "local", f"{fact['id']}-{value_type}-{answer_shape}"
        )
        if coded_values and all(token in snomed_mappings for token in coded_values):
            preferred_id = answer_valueset_id(
                "sct", "-".join(sorted(coded_values))
            )
            result["value_set_strategy"] = "complete_SNOMED_CT"
        elif any(token in snomed_mappings for token in coded_values):
            preferred_id = answer_valueset_id(
                "mixed", f"{fact['id']}-{value_type}-{answer_shape}"
            )
            result["value_set_strategy"] = "complete_mixed_SNOMED_CT_and_local"
        else:
            preferred_id = local_id
            result["value_set_strategy"] = "complete_local"
        result["answer_value_set"] = answer_valueset_url(preferred_id)
        result["local_answer_value_set"] = answer_valueset_url(local_id)
        result["fhir_item_type"] = "choice"
        result["fhir_response_type"] = "valueCoding"
        return result
    return None


def enrich_graph(graph: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    policy, registry = load_documents()
    enriched = deepcopy(graph)
    nodes = {node["id"]: node for node in enriched["nodes"]}
    question_to_fact = {
        edge["from"]: edge["to"]
        for edge in enriched["edges"]
        if edge.get("type") == "COLLECTS"
    }
    for question_id, fact_id in question_to_fact.items():
        question = nodes[question_id]
        fact = nodes[fact_id]
        binding = _question_binding(
            question, fact, policy, registry
        )
        if binding["standard_mappings"]:
            question["semantic_binding"] = binding
        answer_binding = _answer_binding(fact, policy, registry)
        answer_binding, fhir_targets = apply_element_bindings(
            fact, answer_binding
        )
        if fhir_targets:
            fact["fhir_r4_element_bindings"] = fhir_targets
        if answer_binding:
            fact["answer_semantic_binding"] = answer_binding
    coverage = build_coverage(enriched)
    return enriched, {
        "policy_id": policy["id"],
        "policy_version": policy["version"],
        "registry_id": registry["id"],
        "registry_version": registry["version"],
        "status": "research_only",
        "review_status": "unreviewed",
        "runtime_terminology_lookup_required": False,
        "local_question_code_system": LOCAL_QUESTION,
        "local_question_code_is_template_id": True,
        "local_answer_code_system": LOCAL_ANSWER,
        "local_answer_code_pattern": "{fact_id}--{internal_value}",
        "primitive_answer_projection": policy["answer_binding"]["primitive_answers"],
        "boolean_snomed_semantic_equivalents": {
            "true": _snomed_answer("boolean", "yes", registry),
            "false": _snomed_answer("boolean", "no", registry),
        },
        "answer_value_set_naming_rule": "a-{sct|loinc|local|mixed}-{semantic-name}",
        "fhir_r4_element_binding_policy": (
            "policy.fhir-r4-element-terminology-binding"
        ),
        "answer_binding_precedence": (
            "target_FHIR_R4_element_then_SNOMED_CT_then_local"
        ),
        "coverage": coverage,
    }


def enrich_clinician_context(
    document: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Add the same bindings to reusable clinician-submission questions."""
    policy, registry = load_documents()
    enriched = deepcopy(document)
    facts = {fact["id"]: fact for fact in enriched["facts"]}
    for question in enriched["questions"]:
        fact = facts[question["fact_id"]]
        question_shape = {
            "id": question["template_id"],
            "wording": question["wording"],
        }
        binding = _question_binding(
            question_shape, fact, policy, registry
        )
        if binding["standard_mappings"]:
            question["semantic_binding"] = binding
        answer_binding = _answer_binding(fact, policy, registry)
        answer_binding, fhir_targets = apply_element_bindings(
            fact, answer_binding
        )
        if fhir_targets:
            fact["fhir_r4_element_bindings"] = fhir_targets
        if answer_binding:
            fact["answer_semantic_binding"] = answer_binding
    question_count = len(enriched["questions"])
    loinc_equivalent = 0
    loinc_non_equivalent = 0
    snomed_secondary = 0
    local_only = 0
    fhir_element_bound = 0
    fhir_element_candidates = 0
    for question in enriched["questions"]:
        mappings = question.get("semantic_binding", {}).get("standard_mappings", [])
        loinc = [item for item in mappings if item["system"] == LOINC]
        loinc_equivalent += any(
            item["mapping_relation"] in {"exact", "equivalent"} for item in loinc
        )
        loinc_non_equivalent += any(
            item["mapping_relation"] not in {"exact", "equivalent"} for item in loinc
        )
        snomed_secondary += any(item["system"] == SNOMED for item in mappings)
        local_only += not mappings
        fact = facts[question["fact_id"]]
        fhir_element_bound += bool(
            fact.get("answer_semantic_binding", {}).get("fhir_element_binding")
        )
        fhir_element_candidates += bool(
            fact.get("fhir_r4_element_bindings")
        )
    coverage = {
        "question_count": question_count,
        "question_loinc_exact_or_equivalent_count": loinc_equivalent,
        "question_loinc_partial_or_related_count": loinc_non_equivalent,
        "question_snomed_secondary_count": snomed_secondary,
        "question_local_code_count": question_count,
        "question_local_only_count": local_only,
        "question_loinc_exact_or_equivalent_percent": round(
            loinc_equivalent * 100 / question_count, 1
        ) if question_count else 0.0,
        "fhir_r4_element_bound_question_count": fhir_element_bound,
        "fhir_r4_element_candidate_question_count": fhir_element_candidates,
    }
    enriched["question_answer_terminology"] = {
        "policy_id": policy["id"],
        "registry_id": registry["id"],
        "status": "research_only",
        "review_status": "unreviewed",
        "local_question_code_system": LOCAL_QUESTION,
        "local_question_code_is_template_id": True,
        "local_answer_code_system": LOCAL_ANSWER,
        "local_answer_code_pattern": "{fact_id}--{internal_value}",
        "answer_value_set_naming_rule": "a-{sct|loinc|local|mixed}-{semantic-name}",
        "fhir_r4_element_binding_policy": (
            "policy.fhir-r4-element-terminology-binding"
        ),
        "answer_binding_precedence": (
            "target_FHIR_R4_element_then_SNOMED_CT_then_local"
        ),
        "coverage": coverage,
    }
    return enriched, coverage


def build_coverage(graph: dict[str, Any]) -> dict[str, Any]:
    questions = [
        node for node in graph["nodes"] if node.get("type") == "QuestionTemplate"
    ]
    facts = {
        node["id"]: node for node in graph["nodes"] if node.get("type") == "Fact"
    }
    question_facts = {
        edge["from"]: edge["to"]
        for edge in graph["edges"]
        if edge.get("type") == "COLLECTS"
    }
    loinc_equivalent = 0
    loinc_non_equivalent = 0
    snomed_secondary = 0
    local_only = 0
    coded_answer_values = 0
    snomed_answer_values = 0
    local_answer_values = 0
    data_absent_values = 0
    primitive_answer_questions = 0
    boolean_answer_questions = 0
    fhir_element_bound_questions = 0
    fhir_element_candidate_questions = 0
    for question in questions:
        mappings = question.get("semantic_binding", {}).get("standard_mappings", [])
        loinc = [item for item in mappings if item["system"] == LOINC]
        snomed = [item for item in mappings if item["system"] == SNOMED]
        loinc_equivalent += any(
            item["mapping_relation"] in {"exact", "equivalent"} for item in loinc
        )
        loinc_non_equivalent += any(
            item["mapping_relation"] not in {"exact", "equivalent"} for item in loinc
        )
        snomed_secondary += bool(snomed)
        local_only += not mappings
        fact = facts[question_facts[question["id"]]]
        answer = fact.get("answer_semantic_binding", {})
        fhir_targets = fact.get("fhir_r4_element_bindings", [])
        fhir_element_bound_questions += bool(
            answer.get("fhir_element_binding")
        )
        fhir_element_candidate_questions += bool(fhir_targets)
        if fact.get("value_type") == "boolean":
            boolean_answer_questions += 1
        elif not fact.get("allowed_values"):
            primitive_answer_questions += 1
        else:
            absent = answer.get("data_absent_reason_mappings", {})
            snomed = answer.get("snomed_mappings", {})
            for token in fact.get("allowed_values", []):
                if token in absent:
                    data_absent_values += 1
                    continue
                coded_answer_values += 1
                local_answer_values += 1
                snomed_answer_values += token in snomed
    total = len(questions)
    return {
        "question_count": total,
        "question_loinc_exact_or_equivalent_count": loinc_equivalent,
        "question_loinc_partial_or_related_count": loinc_non_equivalent,
        "question_snomed_secondary_count": snomed_secondary,
        "question_local_code_count": total,
        "question_local_only_count": local_only,
        "question_loinc_exact_or_equivalent_percent": round(
            loinc_equivalent * 100 / total, 1
        ) if total else 0.0,
        "coded_answer_value_count": coded_answer_values,
        "coded_answer_snomed_count": snomed_answer_values,
        "coded_answer_local_fallback_count": local_answer_values,
        "coded_answer_snomed_percent": round(
            snomed_answer_values * 100 / coded_answer_values, 1
        ) if coded_answer_values else 0.0,
        "data_absent_option_count": data_absent_values,
        "boolean_primitive_question_count": boolean_answer_questions,
        "other_primitive_question_count": primitive_answer_questions,
        "fhir_r4_element_bound_question_count": fhir_element_bound_questions,
        "fhir_r4_element_candidate_question_count": (
            fhir_element_candidate_questions
        ),
    }
