"""Versioned USCDI/USCDI+ mapping and Coverage helpers.

The overlay measures whether existing Facts can populate interoperability data
elements. It must not create questions, change completion, or trigger safety.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
CORE_MAPPING = ROOT / "mappings/interoperability/uscdi-v6-core.json"
PLUS_MAPPING = ROOT / "mappings/interoperability/uscdi-plus-domain-overlays.json"
POLICY = ROOT / "policies/uscdi-interoperability-overlay.json"
SOURCE_MANIFEST = ROOT / "sources/manifests/uscdi-interoperability-research.json"

ALLOWED_MAPPING_STATUSES = {
    "exact", "partial", "broader", "narrower", "contextual", "unmapped",
    "not_patient_collectable",
}
ALLOWED_COLLECTION_ROLES = {
    "patient_collectable", "patient_or_record", "record_or_provider",
    "output_generated",
}
STATUS_PRIORITY = {
    "exact": 5, "narrower": 4, "broader": 3, "partial": 2,
    "contextual": 1,
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _matches(selector: dict[str, Any], fact_id: str) -> bool:
    kind, value = selector["kind"], selector["value"]
    if kind == "exact":
        return fact_id == value
    if kind == "prefix":
        return fact_id.startswith(value)
    if kind == "regex":
        return re.search(value, fact_id) is not None
    raise ValueError(f"unsupported USCDI selector kind: {kind}")


def _matched_selectors(
    selectors: Iterable[dict[str, Any]], fact_ids: set[str]
) -> tuple[list[str], list[str]]:
    matched: set[str] = set()
    statuses: list[str] = []
    for selector in selectors:
        current = sorted(fact_id for fact_id in fact_ids if _matches(selector, fact_id))
        if current:
            matched.update(current)
            statuses.append(selector.get("mapping_status", "partial"))
    return sorted(matched), statuses


def validate_overlay_documents() -> dict[str, Any]:
    core, plus, policy, source = (
        load(CORE_MAPPING), load(PLUS_MAPPING), load(POLICY), load(SOURCE_MANIFEST)
    )
    errors: list[str] = []
    if core.get("status") != "research_only" or core.get("review_status") != "unreviewed":
        errors.append("USCDI core mapping must remain research_only/unreviewed")
    if plus.get("status") != "research_only" or plus.get("review_status") != "unreviewed":
        errors.append("USCDI+ mapping must remain research_only/unreviewed")
    if policy.get("authority_boundary", {}).get("clinical_question_authority") is not False:
        errors.append("USCDI overlay must not control clinical questions")
    if policy.get("authority_boundary", {}).get("clinical_safety_rule_authority") is not False:
        errors.append("USCDI overlay must not control clinical safety")
    if policy.get("jurisdiction", {}).get("deployment_jurisdiction") != "KR":
        errors.append("deployment jurisdiction must remain KR")
    ids: set[str] = set()
    for element in core.get("core_elements", []):
        element_id = element.get("id")
        if not element_id or element_id in ids:
            errors.append(f"duplicate or missing USCDI element id: {element_id!r}")
        ids.add(element_id)
        if element.get("collection_role") not in ALLOWED_COLLECTION_ROLES:
            errors.append(f"{element_id}: unsupported collection role")
        for selector in element.get("selectors", []):
            if selector.get("kind") not in {"exact", "prefix", "regex"}:
                errors.append(f"{element_id}: unsupported selector kind")
            if selector.get("mapping_status") not in ALLOWED_MAPPING_STATUSES:
                errors.append(f"{element_id}: unsupported mapping status")
            if selector.get("kind") == "regex":
                try:
                    re.compile(selector.get("value", ""))
                except re.error as exc:
                    errors.append(f"{element_id}: invalid regex: {exc}")
    domain_ids = [item.get("id") for item in plus.get("domains", [])]
    if len(domain_ids) != len(set(domain_ids)):
        errors.append("duplicate USCDI+ domain id")
    if not source.get("artifacts"):
        errors.append("USCDI source manifest has no artifacts")
    if errors:
        raise ValueError("; ".join(errors))
    return {
        "core_element_count": len(core["core_elements"]),
        "domain_count": len(plus["domains"]),
        "source_artifact_count": len(source["artifacts"]),
    }


def build_package_interoperability_coverage(
    *,
    profile: str,
    rfe: str,
    package_fact_ids: Iterable[str],
    clinician_context_fact_ids: Iterable[str],
    runtime_capabilities: Iterable[str] = ("dataAbsentReason",),
) -> dict[str, Any]:
    validate_overlay_documents()
    core, plus, policy = load(CORE_MAPPING), load(PLUS_MAPPING), load(POLICY)
    package_facts = set(package_fact_ids)
    context_facts = set(clinician_context_fact_ids)
    available = package_facts | context_facts
    core_results = []
    eligible_roles = {"patient_collectable", "patient_or_record"}
    for element in core["core_elements"]:
        matched, statuses = _matched_selectors(element.get("selectors", []), available)
        role = element["collection_role"]
        if role not in eligible_roles:
            status = "not_patient_collectable"
        elif statuses:
            status = max(statuses, key=lambda item: STATUS_PRIORITY.get(item, 0))
        else:
            status = "unmapped"
        core_results.append({
            "element_id": element["id"],
            "data_class": element["data_class"],
            "data_element": element["data_element"],
            "collection_role": role,
            "mapping_status": status,
            "matched_fact_ids": matched,
            **({"limitation": element["limitation"]} if element.get("limitation") else {}),
        })
    eligible = [item for item in core_results if item["collection_role"] in eligible_roles]
    mapped = [item for item in eligible if item["mapping_status"] != "unmapped"]

    domain_results = []
    capabilities = set(runtime_capabilities)
    for domain in plus["domains"]:
        applicable = "*" in domain["applicable_rfes"] or rfe in domain["applicable_rfes"]
        if not applicable:
            continue
        element_results = []
        for element in domain["elements"]:
            matched = sorted(set(element.get("fact_ids", [])) & available)
            selector_matches, _ = _matched_selectors(
                element.get("fact_selectors", []), available
            )
            matched = sorted(set(matched) | set(selector_matches))
            runtime_capability = element.get("runtime_capability")
            supported = bool(matched) or bool(runtime_capability in capabilities)
            element_results.append({
                "element_id": element["id"],
                "display": element["display"],
                "supported": supported,
                "matched_fact_ids": matched,
                **({"runtime_capability": runtime_capability} if runtime_capability else {}),
            })
        domain_results.append({
            "domain_id": domain["id"],
            "display": domain["display"],
            "maturity": domain["maturity"],
            "supported_elements": sum(item["supported"] for item in element_results),
            "total_elements": len(element_results),
            "unmapped_element_ids": [
                item["element_id"] for item in element_results if not item["supported"]
            ],
            "elements": element_results,
        })

    return {
        "id": f"coverage.interoperability.{profile}",
        "version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "clinical_authority": False,
        "completion_authority": False,
        "jurisdiction": {"framework": "US", "deployment": "KR"},
        "core": {
            "framework": "USCDI",
            "framework_version": core["framework"]["version"],
            "eligible_element_count": len(eligible),
            "mapped_element_count": len(mapped),
            "exact_element_count": sum(item["mapping_status"] == "exact" for item in eligible),
            "coverage_percent": round(100 * len(mapped) / len(eligible), 1) if eligible else 0.0,
            "unmapped_element_ids": [
                item["element_id"] for item in eligible if item["mapping_status"] == "unmapped"
            ],
            "non_patient_collectable_element_ids": [
                item["element_id"] for item in core_results
                if item["mapping_status"] == "not_patient_collectable"
            ],
            "elements": core_results,
        },
        "uscdi_plus_domains": domain_results,
        "policy_ref": str(POLICY.relative_to(ROOT)),
        "mapping_refs": [str(CORE_MAPPING.relative_to(ROOT)), str(PLUS_MAPPING.relative_to(ROOT))],
        "source_manifest_ref": str(SOURCE_MANIFEST.relative_to(ROOT)),
        "limitations": [
            "Coverage indicates candidate data-population capability, not US certification or conformance.",
            "A mapped Fact does not make the data element clinically required for this encounter.",
            "US-specific vocabularies and regulatory semantics do not replace Korean bindings or policy.",
        ],
        "provenance": {
            "created_by": {"type": "compiler", "id": "interoperability.uscdi"},
            "created_at": "2026-07-16T00:00:00Z",
            "source_refs": ["source.uscdi.v6.2025", "source.uscdi-plus.overview.2026"],
            "review_status": "unreviewed",
            "version": "0.1.0",
        },
    }
