"""Create an auditable semantic/claim multi-coding record."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


SNOMED_SYSTEM = "http://snomed.info/sct"
CLAIM_SYSTEMS = {
    "diagnosis_kcd8": "http://www.hl7korea.or.kr/CodeSystem/kostat-kcd-8",
    "diagnosis_kcd9": "http://www.hl7korea.or.kr/CodeSystem/kostat-kcd-9",
    "procedure": "http://www.hl7korea.or.kr/CodeSystem/hira-edi-procedure",
    "medication": "http://www.hl7korea.or.kr/CodeSystem/hira-edi-medication",
    "material": "http://www.hl7korea.or.kr/CodeSystem/hira-edi-material",
}
RELATIONS = {"exact", "equivalent", "broader", "narrower", "related", "unresolved"}
ALLOWED_TRIGGERS = {
    "user_provided_exact_claim_code",
    "user_provided_claim_catalog_name",
    "user_requested_claim_code_verification",
    "uploaded_document_contains_explicit_claim_code_or_name",
    "user_provided_medication_product_name",
}


def _validate_coding(coding: dict[str, Any], expected_system: str) -> None:
    if coding.get("system") != expected_system:
        raise ValueError(f"unexpected coding system: {coding.get('system')!r}")
    if not isinstance(coding.get("code"), str) or not coding["code"].strip():
        raise ValueError("coding requires a non-empty code")


def build_semantic_claim_binding(
    *,
    domain: str,
    semantic_coding: dict[str, Any],
    claim_coding: dict[str, Any],
    mapping_relation: str,
    activation_trigger: str,
    verification_method: str,
    source_type: str,
) -> dict[str, Any]:
    """Preserve SNOMED CT and KCD/HIRA codings without collapsing either one."""
    if domain not in CLAIM_SYSTEMS:
        raise ValueError(f"unsupported claim domain: {domain}")
    if mapping_relation not in RELATIONS:
        raise ValueError(f"unsupported mapping relation: {mapping_relation}")
    if activation_trigger not in ALLOWED_TRIGGERS:
        raise ValueError("claim lookup was not activated by supplied claim information")
    _validate_coding(semantic_coding, SNOMED_SYSTEM)
    _validate_coding(claim_coding, CLAIM_SYSTEMS[domain])
    if mapping_relation in {"exact", "equivalent"} and verification_method in {
        "name_similarity_only", "unverified"
    }:
        raise ValueError("exact/equivalent mapping requires more than name similarity")
    return {
        "domain": domain,
        "semantic_coding": deepcopy(semantic_coding),
        "claim_coding": deepcopy(claim_coding),
        "mapping_relation": mapping_relation,
        "verification_method": verification_method,
        "activation_trigger": activation_trigger,
        "source_type": source_type,
        "preserve_both_codings": True,
        "single_codeable_concept_eligible": mapping_relation in {"exact", "equivalent"},
        "status": "research_only",
        "review_status": "unreviewed",
        "clinical_rule_authority": False,
    }
