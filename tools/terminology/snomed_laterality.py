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


def _lookup_parameter(document: dict[str, Any], name: str) -> Any:
    for parameter in document.get("parameter", []):
        if parameter.get("name") == name:
            for key, value in parameter.items():
                if key.startswith("value"):
                    return value
        if parameter.get("name") == "property":
            parts = parameter.get("part", [])
            property_code = next((
                part.get("valueCode") for part in parts
                if part.get("name") == "code"
            ), None)
            if property_code != name:
                continue
            for part in parts:
                if part.get("name") != "value":
                    continue
                for key, value in part.items():
                    if key.startswith("value"):
                        return value
    return None


def assess_lateralizable_site(
    *,
    finding_site_code: str,
    membership_response: dict[str, Any],
    lookup_response: dict[str, Any],
    finding_site_attribute_allowed: bool,
    expected_terminology_version: str | None = None,
) -> dict[str, Any]:
    """Combine refset membership, active-concept lookup, edition and MRCM checks.

    STOM's RefsetMemberViewDTO ``referencedComponentActive`` field is retained
    as service evidence but is not treated as the authoritative concept-active
    result. Active status comes from the versioned FHIR CodeSystem lookup.
    """
    if not finding_site_code.isdigit():
        raise ValueError("SNOMED CT finding-site identifier must be numeric")
    rows = [
        row for row in membership_response.get("content", [])
        if str(row.get("refset", {}).get("id")) == LATERALIZABLE_BODY_STRUCTURE_REFSET
        and str(row.get("referencedComponent", {}).get("id")) == finding_site_code
    ]
    lookup_code = str(_lookup_parameter(lookup_response, "code") or finding_site_code)
    display = _lookup_parameter(lookup_response, "display")
    version = _lookup_parameter(lookup_response, "version")
    inactive = _lookup_parameter(lookup_response, "inactive")
    lookup_matches = lookup_code == finding_site_code
    lookup_active = bool(display and version and inactive is False and lookup_matches)
    version_matches = bool(version) and (
        expected_terminology_version is None or version == expected_terminology_version
    )
    eligible = bool(
        rows and lookup_active and version_matches and finding_site_attribute_allowed
    )
    return {
        "finding_site_code": finding_site_code,
        "refset_id": LATERALIZABLE_BODY_STRUCTURE_REFSET,
        "membership_row_present": bool(rows),
        "membership_row_count": len(rows),
        "member_view_referenced_component_active_values": sorted({
            row.get("referencedComponentActive") for row in rows
        }, key=str),
        "member_view_active_field_is_authoritative": False,
        "lookup_display": display,
        "lookup_active": lookup_active,
        "terminology_version": version,
        "terminology_version_matches": version_matches,
        "mrcm_finding_site_attribute_allowed": finding_site_attribute_allowed,
        "laterality_question_eligible": eligible,
        "fallback": None if eligible else "preserve_separate_site_and_laterality_facts",
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
