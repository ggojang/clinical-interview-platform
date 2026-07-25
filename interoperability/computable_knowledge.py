"""Build-Time validation for AU, openEHR and HL7 computable-knowledge references.

The internal Rule Graph remains authoritative. This module validates reference
metadata and emits package-level readiness metadata; it does not compile or
execute CQL, ELM, GDL2, PlanDefinition or CDS Hooks.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "policies/computable-knowledge-standards-overlay.json"
REGISTRY = ROOT / "mappings/interoperability/computable-knowledge-standards.json"
SOURCE_MANIFEST = (
    ROOT / "sources/manifests/computable-knowledge-standards-research.json"
)
SIMULATION = (
    ROOT / "simulation/workflows/computable-knowledge-standards-cases.json"
)
RULE_SCHEMA = ROOT / "schemas/rule-graph.schema.json"

EXPECTED_RULE_TYPES = {
    "activation",
    "applicability",
    "requirement",
    "completion",
    "priority",
    "suppression",
    "conflict",
    "safety",
    "transition",
    "stop",
    "mapping",
}
REQUIRED_FRAMEWORKS = {
    "hl7-au-base",
    "sparked-aucdi",
    "hl7-au-core",
    "aehrc-smart-health-checks",
    "openehr-ckm",
    "hl7-cpg",
    "hl7-cql",
    "hl7-fhir-clinical-reasoning",
    "hl7-cds-hooks",
    "openehr-gdl2",
}
FALSE_AUTHORITY_KEYS = {
    "clinical_question_authority",
    "clinical_safety_rule_authority",
    "question_priority_authority",
    "completion_rule_authority",
    "diagnosis_authority",
    "order_or_treatment_authority",
    "runtime_execution_authority",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_overlay_documents() -> dict[str, Any]:
    policy, registry, manifest, simulation, rule_schema = (
        load(POLICY),
        load(REGISTRY),
        load(SOURCE_MANIFEST),
        load(SIMULATION),
        load(RULE_SCHEMA),
    )
    errors: list[str] = []

    for label, document in (
        ("policy", policy),
        ("registry", registry),
        ("manifest", manifest),
    ):
        if document.get("status") != "research_only":
            errors.append(f"{label} must remain research_only")
        if document.get("review_status") != "unreviewed":
            errors.append(f"{label} must remain unreviewed")

    if policy.get("deployment_jurisdiction") != "KR":
        errors.append("deployment jurisdiction must remain KR")
    authority = policy.get("authority_boundary", {})
    for key in FALSE_AUTHORITY_KEYS:
        if authority.get(key) is not False:
            errors.append(f"external standards must not gain {key}")
    runtime = policy.get("runtime", {})
    for key in ("external_lookup", "external_compilation", "external_rule_interpretation"):
        if runtime.get(key) is not False:
            errors.append(f"Runtime boundary requires {key}=false")
    if runtime.get("executes_internal_compiled_rules_only") is not True:
        errors.append("Runtime must execute internal compiled rules only")
    if policy.get("fixed_questionnaires", {}).get("automatic_import") is not False:
        errors.append("fixed questionnaires must not be imported automatically")

    framework_ids = [item.get("id") for item in registry.get("frameworks", [])]
    if len(framework_ids) != len(set(framework_ids)):
        errors.append("framework ids must be unique")
    if set(framework_ids) != REQUIRED_FRAMEWORKS:
        errors.append(
            "framework registry mismatch: "
            f"missing={sorted(REQUIRED_FRAMEWORKS - set(framework_ids))}, "
            f"extra={sorted(set(framework_ids) - REQUIRED_FRAMEWORKS)}"
        )
    by_framework = {
        item["id"]: item
        for item in registry.get("frameworks", [])
        if item.get("id")
    }
    if by_framework.get("hl7-au-core", {}).get("adoption") != "reference_only":
        errors.append("AU Core must remain reference_only for Korean deployment")
    if by_framework.get("openehr-gdl2", {}).get("adoption") != "secondary_research":
        errors.append("GDL2 must remain secondary_research")
    if by_framework.get("hl7-cds-hooks", {}).get("adoption") != "external_adapter_only":
        errors.append("CDS Hooks must remain external_adapter_only")

    artifact_ids = {
        item.get("id") for item in manifest.get("artifacts", []) if item.get("id")
    }
    referenced_source_ids = {
        source_id
        for framework in registry.get("frameworks", [])
        for source_id in framework.get("source_ids", [])
    }
    if referenced_source_ids - artifact_ids:
        errors.append(
            "framework references unresolved sources: "
            f"{sorted(referenced_source_ids - artifact_ids)}"
        )
    for artifact in manifest.get("artifacts", []):
        if artifact.get("monitor_profile") != "interoperability_standard":
            errors.append(f"{artifact.get('id')}: wrong monitor profile")
        if artifact.get("monitor_interval_days") != 7:
            errors.append(f"{artifact.get('id')}: refresh must be weekly")
        if artifact.get("last_monitored_at") != "2026-07-25":
            errors.append(f"{artifact.get('id')}: last monitor date mismatch")
        if artifact.get("next_monitor_at") != "2026-08-01":
            errors.append(f"{artifact.get('id')}: next monitor date mismatch")
    gdl_source = next(
        (
            item
            for item in manifest.get("artifacts", [])
            if item.get("id") == "source.openehr.gdl2.2.0.0"
        ),
        {},
    )
    if gdl_source.get("specification_status") != "TRIAL":
        errors.append("GDL2 trial status must be explicit")

    projection_profiles = registry.get("rule_projection_profiles", [])
    mapped_rule_types = [item.get("rule_type") for item in projection_profiles]
    if len(mapped_rule_types) != len(set(mapped_rule_types)):
        errors.append("rule projection types must be unique")
    if set(mapped_rule_types) != EXPECTED_RULE_TYPES:
        errors.append("all Rule Graph types require a projection profile")
    if any(
        item.get("emission_status") != "metadata_only_not_emitted"
        for item in projection_profiles
    ):
        errors.append("unreviewed standards projections must not claim emission")
    schema_rule_types = set(
        rule_schema["properties"]["rules"]["items"]["properties"]["type"]["enum"]
    )
    if schema_rule_types != EXPECTED_RULE_TYPES:
        errors.append("projection profile rule types do not match Rule Graph schema")

    if simulation.get("contains_real_patient_data") is not False:
        errors.append("standards simulation must be synthetic")
    expected_tokens = {
        token
        for case in simulation.get("cases", [])
        for token in case.get("expected", [])
    }
    required_tokens = {
        "no_automatic_question",
        "kr_core_precedence_preserved",
        "no_fixed_questionnaire_import",
        "at_code_retained_as_local",
        "rule_graph_remains_authoritative",
        "definition_not_order",
        "secondary_research_only",
        "runtime_continues_with_compiled_package",
        "content_not_imported",
    }
    if not required_tokens <= expected_tokens:
        errors.append(
            "standards simulation boundary coverage incomplete: "
            f"{sorted(required_tokens - expected_tokens)}"
        )

    if errors:
        raise ValueError("; ".join(errors))
    return {
        "framework_count": len(framework_ids),
        "source_artifact_count": len(artifact_ids),
        "rule_projection_type_count": len(mapped_rule_types),
        "simulation_count": len(simulation.get("cases", [])),
    }


def build_package_computable_knowledge_coverage(
    rule_graph: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    validate_overlay_documents()
    registry = load(REGISTRY)
    profile_by_type = {
        item["rule_type"]: item for item in registry["rule_projection_profiles"]
    }
    encountered = sorted(
        {rule.get("type") for rule in rule_graph if rule.get("type")}
    )
    return {
        "id": "coverage.computable-knowledge-standards",
        "version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "contains_patient_responses": False,
        "deployment_jurisdiction": "KR",
        "source_of_truth": {
            "knowledge": "Knowledge Graph",
            "behavior": "Rule Graph",
            "runtime": "compiled Knowledge Package",
        },
        "authority": {
            "clinical": False,
            "safety": False,
            "priority": False,
            "completion": False,
            "diagnosis": False,
            "orders": False,
        },
        "runtime_external_lookup": False,
        "framework_ids": [item["id"] for item in registry["frameworks"]],
        "encountered_rule_types": encountered,
        "rule_projection_readiness": [
            {
                "rule_type": rule_type,
                "cql_role": profile_by_type[rule_type]["cql_role"],
                "fhir_clinical_reasoning_role": profile_by_type[rule_type][
                    "fhir_clinical_reasoning_role"
                ],
                "gdl2_role": profile_by_type[rule_type]["gdl2_role"],
                "emission_status": "metadata_only_not_emitted",
            }
            for rule_type in encountered
        ],
        "projection_outputs": {
            "cql_emitted": False,
            "elm_emitted": False,
            "fhir_library_emitted": False,
            "plan_definition_emitted": False,
            "activity_definition_emitted": False,
            "gdl2_emitted": False,
            "cds_hooks_dependency": False,
        },
        "fixed_questionnaire_automatic_mapping": False,
        "limitations": [
            "No CQL, ELM or GDL2 execution-engine conformance has been established.",
            "No PlanDefinition or ActivityDefinition is authorized to create an order.",
            "Australian and openEHR artifacts are structural references only in Korean deployment.",
        ],
    }


def validate_package_computable_knowledge(package: dict[str, Any]) -> None:
    overlay = package.get("computable_knowledge")
    if not isinstance(overlay, dict):
        raise ValueError("package missing computable-knowledge standards overlay")
    if overlay.get("status") != "research_only":
        raise ValueError("computable-knowledge overlay must remain research_only")
    if overlay.get("review_status") != "unreviewed":
        raise ValueError("computable-knowledge overlay must remain unreviewed")
    if overlay.get("deployment_jurisdiction") != "KR":
        raise ValueError("computable-knowledge deployment jurisdiction must remain KR")
    if overlay.get("runtime_external_lookup") is not False:
        raise ValueError("computable-knowledge overlay cannot add Runtime lookup")
    if overlay.get("source_of_truth", {}).get("behavior") != "Rule Graph":
        raise ValueError("Rule Graph must remain the behavior source of truth")
    if any(value is not False for value in overlay.get("authority", {}).values()):
        raise ValueError("computable-knowledge references cannot gain clinical authority")
    outputs = overlay.get("projection_outputs", {})
    if any(value is not False for value in outputs.values()):
        raise ValueError("unreviewed package cannot claim an emitted or Runtime projection")
    if overlay.get("fixed_questionnaire_automatic_mapping") is not False:
        raise ValueError("fixed questionnaire automatic mapping must remain disabled")
