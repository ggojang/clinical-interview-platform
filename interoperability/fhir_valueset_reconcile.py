"""Reference-preserving FHIR R4 ValueSet reconciliation and derivation."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from typing import Any, Iterable


CANONICAL_BASE = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/ValueSet"
)
ORIGIN_EXTENSION = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "StructureDefinition/reference-valueset-origin"
)
VERIFICATION_SOURCE_EXTENSION = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "StructureDefinition/valueset-addition-verification-source"
)
VERIFIED_AT_EXTENSION = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "StructureDefinition/valueset-addition-verified-at"
)
LOCAL_CODE_SYSTEM_PREFIX = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/CodeSystem/"
)


class ValueSetReconciliationError(ValueError):
    """Raised when a reference or derived ValueSet cannot be handled safely."""


def canonical_with_version(resource: dict[str, Any]) -> str:
    canonical = resource.get("url")
    if not canonical:
        raise ValueSetReconciliationError("reference ValueSet requires url")
    version = resource.get("version")
    return f"{canonical}|{version}" if version else canonical


def _normalized_include(include: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key in ("system", "version"):
        if include.get(key) is not None:
            normalized[key] = include[key]
    normalized["valueSet"] = sorted(include.get("valueSet", []))
    normalized["concept"] = sorted({
        concept["code"]
        for concept in include.get("concept", [])
        if concept.get("code")
    })
    normalized["filter"] = sorted(
        (
            {
                "property": item.get("property"),
                "op": item.get("op"),
                "value": item.get("value"),
            }
            for item in include.get("filter", [])
        ),
        key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True),
    )
    return normalized


def normalized_membership_definition(resource: dict[str, Any]) -> dict[str, Any]:
    """Return order- and display-insensitive extensional/intensional content."""
    if resource.get("resourceType") != "ValueSet":
        raise ValueSetReconciliationError("resource is not a ValueSet")
    compose = resource.get("compose")
    if isinstance(compose, dict):
        include = sorted(
            (_normalized_include(item) for item in compose.get("include", [])),
            key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True),
        )
        exclude = sorted(
            (_normalized_include(item) for item in compose.get("exclude", [])),
            key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True),
        )
        return {
            "kind": "compose",
            "inactive": compose.get("inactive"),
            "lockedDate": compose.get("lockedDate"),
            "include": include,
            "exclude": exclude,
        }
    expansion = resource.get("expansion", {})
    contains_by_key = {
        (
            item.get("system"),
            item.get("version"),
            item.get("code"),
        ): {
            "system": item.get("system"),
            "version": item.get("version"),
            "code": item.get("code"),
        }
        for item in expansion.get("contains", [])
        if item.get("system") and item.get("code")
    }
    contains = sorted(
        contains_by_key.values(),
        key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True),
    )
    if contains:
        return {"kind": "expansion", "contains": contains}
    raise ValueSetReconciliationError(
        "ValueSet requires compose or a materialized expansion"
    )


def membership_fingerprint(resource: dict[str, Any]) -> str:
    normalized = normalized_membership_definition(resource)
    rendered = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return "sha256:" + hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def reconcile_reference(
    reference: dict[str, Any],
    candidates: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Decide whether to reuse or preserve-create a reference ValueSet.

    Canonical/version conflicts are never overwritten. A content-equivalent
    ValueSet with another canonical is reported as a duplicate-content
    candidate, but it cannot replace the requested reference identity.
    """
    if reference.get("resourceType") != "ValueSet":
        raise ValueSetReconciliationError("reference is not a ValueSet")
    if not reference.get("id") or not reference.get("url"):
        raise ValueSetReconciliationError("reference requires id and url")
    reference_fp = membership_fingerprint(reference)
    canonical = reference["url"]
    version = reference.get("version")
    exact_identity = [
        candidate
        for candidate in candidates
        if candidate.get("resourceType") == "ValueSet"
        and candidate.get("url") == canonical
        and candidate.get("version") == version
    ]
    if len(exact_identity) > 1:
        raise ValueSetReconciliationError(
            f"multiple ValueSets use canonical/version {canonical}|{version}"
        )
    if exact_identity:
        candidate = exact_identity[0]
        candidate_fp = membership_fingerprint(candidate)
        if candidate_fp != reference_fp:
            return {
                "action": "canonical_content_conflict",
                "reference_canonical": canonical_with_version(reference),
                "server_id": candidate.get("id"),
                "reference_membership_fingerprint": reference_fp,
                "server_membership_fingerprint": candidate_fp,
                "safe_to_write": False,
            }
        return {
            "action": "reuse_exact_reference",
            "reference_canonical": canonical_with_version(reference),
            "selected_canonical": canonical_with_version(candidate),
            "server_id": candidate.get("id"),
            "membership_fingerprint": reference_fp,
            "safe_to_write": False,
        }
    equivalent = []
    for candidate in candidates:
        if candidate.get("resourceType") != "ValueSet":
            continue
        try:
            if membership_fingerprint(candidate) == reference_fp:
                equivalent.append(candidate)
        except ValueSetReconciliationError:
            continue
    if equivalent:
        equivalent.sort(
            key=lambda item: (
                item.get("url", ""),
                item.get("version", ""),
                item.get("id", ""),
            )
        )
        return {
            "action": "create_reference_unchanged",
            "reference_canonical": canonical_with_version(reference),
            "membership_fingerprint": reference_fp,
            "equivalent_candidate_count": len(equivalent),
            "content_equivalent_candidates": [
                {
                    "canonical": canonical_with_version(item),
                    "server_id": item.get("id"),
                }
                for item in equivalent
            ],
            "semantic_identity_note": (
                "Membership is identical, but a different canonical is a "
                "different FHIR identity and cannot replace the reference."
            ),
            "safe_to_write": True,
            "resource": deepcopy(reference),
        }
    return {
        "action": "create_reference_unchanged",
        "reference_canonical": canonical_with_version(reference),
        "membership_fingerprint": reference_fp,
        "safe_to_write": True,
        "resource": deepcopy(reference),
    }


def _extended_id(semantic_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", semantic_name.lower()).strip("-")
    candidate = "a-extended-" + (slug or "answers")
    if len(candidate) <= 64:
        return candidate
    digest = hashlib.sha256(candidate.encode("utf-8")).hexdigest()[:10]
    return f"{candidate[:53].rstrip('-')}-{digest}"


def build_extended_valueset(
    reference: dict[str, Any],
    additions: list[dict[str, Any]],
    *,
    semantic_name: str,
    title: str,
    description: str,
    version: str = "0.1.0",
    date: str,
    allow_local_codes: bool = False,
) -> dict[str, Any]:
    """Build a distinct ValueSet importing an untouched reference ValueSet."""
    reference_snapshot = deepcopy(reference)
    reference_canonical = canonical_with_version(reference)
    if not additions:
        raise ValueSetReconciliationError(
            "an extended ValueSet requires at least one additional code"
        )
    by_system: dict[tuple[str, str | None], dict[str, dict[str, str]]] = {}
    for addition in additions:
        system = addition.get("system")
        code = addition.get("code")
        if not system or not code:
            raise ValueSetReconciliationError(
                "every extension code requires system and code"
            )
        if (
            system.startswith(LOCAL_CODE_SYSTEM_PREFIX)
            and not allow_local_codes
        ):
            raise ValueSetReconciliationError(
                "local extension codes require explicit allow_local_codes"
            )
        if not addition.get("verification_source"):
            raise ValueSetReconciliationError(
                f"{system}|{code}: verification_source is required"
            )
        key = (system, addition.get("version"))
        by_system.setdefault(key, {})[code] = {
            "code": code,
            **(
                {"display": addition["display"]}
                if addition.get("display")
                else {}
            ),
            "extension": [
                {
                    "url": VERIFICATION_SOURCE_EXTENSION,
                    "valueString": addition["verification_source"],
                },
                *(
                    [{
                        "url": VERIFIED_AT_EXTENSION,
                        "valueDateTime": addition["verified_at"],
                    }]
                    if addition.get("verified_at")
                    else []
                ),
            ],
        }
    identifier = _extended_id(semantic_name)
    includes: list[dict[str, Any]] = [{"valueSet": [reference_canonical]}]
    for (system, system_version), concepts in sorted(
        by_system.items(),
        key=lambda item: (item[0][0], item[0][1] or ""),
    ):
        include: dict[str, Any] = {
            "system": system,
            "concept": [concepts[code] for code in sorted(concepts)],
        }
        if system_version:
            include["version"] = system_version
        includes.append(include)
    derived = {
        "resourceType": "ValueSet",
        "id": identifier,
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/ValueSet"],
            "tag": [
                {
                    "system": (
                        "https://ggojang.github.io/"
                        "clinical-interview-platform/fhir/"
                        "CodeSystem/content-status"
                    ),
                    "code": "research-only",
                    "display": "Research only",
                },
                {
                    "system": (
                        "https://ggojang.github.io/"
                        "clinical-interview-platform/fhir/"
                        "CodeSystem/review-status"
                    ),
                    "code": "unreviewed",
                    "display": "Unreviewed",
                },
            ],
        },
        "extension": [{
            "url": ORIGIN_EXTENSION,
            "valueCanonical": reference_canonical,
        }],
        "url": f"{CANONICAL_BASE}/{identifier}",
        "version": version,
        "name": "".join(part.title() for part in identifier.split("-")),
        "title": title,
        "status": "draft",
        "experimental": True,
        "date": date,
        "publisher": "Clinical Interview Knowledge Platform",
        "description": description,
        "immutable": False,
        "purpose": (
            "Application-specific extension of an unchanged reference "
            f"ValueSet: {reference_canonical}"
        ),
        "compose": {"include": includes},
    }
    if reference != reference_snapshot:
        raise AssertionError("reference ValueSet was mutated")
    return derived
