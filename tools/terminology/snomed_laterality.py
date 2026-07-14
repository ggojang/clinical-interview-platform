"""Build validated SNOMED CT laterality expression candidates.

This module never decides clinical priority and never queries terminology at
interview Runtime. Callers must supply versioned MRCM and reference-set checks.
"""
from __future__ import annotations

from typing import Any


SNOMED_SYSTEM = "http://snomed.info/sct"
FINDING_SITE = "363698007"
LATERALITY = "272741003"
LATERALIZABLE_BODY_STRUCTURE_REFSET = "723264001"
SIDE = "182353008"
LATERALITY_CODES = {
    "left": "7771000",
    "right": "24028007",
    "bilateral": "51440002",
}


def _nested_site(site_code: str, laterality_code: str) -> str:
    return (
        f"{{ {FINDING_SITE} = ( {site_code} : "
        f"{LATERALITY} = {laterality_code} ) }}"
    )


def build_lateralized_finding(
    *,
    focus_code: str,
    finding_site_code: str,
    laterality: str,
    terminology_version: str,
    refset_member: bool,
    finding_site_attribute_allowed: bool,
    finding_sites_in_normal_form: int = 1,
    repeated_finding_sites_identical: bool = True,
    finding_site_already_lateralized: bool = False,
    membership_source: str = "STOM",
) -> dict[str, Any]:
    """Return a research-only nested Finding site/Laterality expression.

    Bilateral input is expanded into separate left and right role groups in the
    classifiable form, following SNOMED International transformation guidance.
    """
    if laterality not in LATERALITY_CODES:
        raise ValueError(f"unsupported laterality: {laterality}")
    if not focus_code.isdigit() or not finding_site_code.isdigit():
        raise ValueError("SNOMED CT concept identifiers must be numeric")
    if not terminology_version:
        raise ValueError("a versioned SNOMED CT edition is required")
    if not finding_site_attribute_allowed:
        raise ValueError("MRCM does not permit Finding site for the focus concept")
    if not refset_member:
        raise ValueError(
            "Finding site is not a verified member of the lateralizable body structure refset"
        )
    if finding_site_already_lateralized:
        raise ValueError("Finding site already states laterality; do not add it again")
    if finding_sites_in_normal_form < 1:
        raise ValueError("focus concept has no Finding site in its normal form")
    if finding_sites_in_normal_form > 1 and not repeated_finding_sites_identical:
        raise ValueError("multiple different Finding site values cannot be safely lateralized")

    input_code = LATERALITY_CODES[laterality]
    input_expression = f"{focus_code} : {LATERALITY} = {input_code}"
    if laterality == "bilateral":
        role_groups = [
            _nested_site(finding_site_code, LATERALITY_CODES["left"]),
            _nested_site(finding_site_code, LATERALITY_CODES["right"]),
        ]
    else:
        role_groups = [_nested_site(finding_site_code, input_code)]
    classifiable_expression = f"=== {focus_code} : " + ", ".join(role_groups)
    return {
        "system": SNOMED_SYSTEM,
        "version": terminology_version,
        "focus_code": focus_code,
        "finding_site": {
            "attribute_code": FINDING_SITE,
            "value_code": finding_site_code,
            "lateralizable_refset_id": LATERALIZABLE_BODY_STRUCTURE_REFSET,
            "refset_member": True,
            "membership_source": membership_source,
        },
        "laterality": {
            "attribute_code": LATERALITY,
            "value": laterality,
            "input_qualifier_code": input_code,
            "range_parent_code": SIDE,
        },
        "close_to_user_expression": input_expression,
        "classifiable_expression": classifiable_expression,
        "bilateral_expanded_to_left_and_right": laterality == "bilateral",
        "status": "research_only",
        "review_status": "unreviewed",
        "clinical_rule_authority": False,
    }
