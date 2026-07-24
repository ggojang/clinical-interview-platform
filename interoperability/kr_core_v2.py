"""Offline KR Core V2 profile and terminology-binding support.

Interview Runtime never downloads the KR Core package or queries STOM. This
module consumes a checked-in Build-Time registry containing canonical metadata
and profile constraints only.
"""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "policies/kr-core-v2-interoperability-overlay.json"
REGISTRY_PATH = (
    ROOT / "mappings/fhir/kr-core-v2/profile-element-bindings.json"
)
PACKAGE_NAME = "hl7.fhir.kr.core"
PACKAGE_VERSION = "2.0.0"
FHIR_VERSION = "4.0.1"
CANONICAL_BASE = "http://www.hl7korea.or.kr/fhir/krcore"
ALLOWED_STRENGTHS = {"required", "extensible", "preferred", "example"}


@lru_cache(maxsize=1)
def load_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    validate_documents(policy, registry)
    return policy, registry


def validate_documents(
    policy: dict[str, Any],
    registry: dict[str, Any],
) -> None:
    for document in (policy, registry):
        if document.get("status") != "research_only":
            raise ValueError(f"{document.get('id')}: must remain research_only")
        if document.get("review_status") != "unreviewed":
            raise ValueError(f"{document.get('id')}: must remain unreviewed")
    if policy.get("package") != f"{PACKAGE_NAME}#{PACKAGE_VERSION}":
        raise ValueError("KR Core policy package mismatch")
    package = registry.get("package", {})
    if package.get("name") != PACKAGE_NAME:
        raise ValueError("KR Core registry package mismatch")
    if package.get("version") != PACKAGE_VERSION:
        raise ValueError("KR Core registry version mismatch")
    if package.get("fhir_version") != FHIR_VERSION:
        raise ValueError("KR Core registry must use FHIR R4 4.0.1")
    profiles = registry.get("profiles", [])
    extensions = registry.get("extensions", [])
    profile_urls = {profile["url"] for profile in profiles}
    extension_urls = {extension["url"] for extension in extensions}
    if registry.get("profile_count") != len(profile_urls):
        raise ValueError("KR Core profile count mismatch")
    if registry.get("extension_count") != len(extension_urls):
        raise ValueError("KR Core extension count mismatch")
    if profile_urls & extension_urls:
        raise ValueError("KR Core profile and extension canonicals overlap")
    structure_urls = profile_urls | extension_urls
    if registry.get("structure_definition_count") != len(structure_urls):
        raise ValueError("KR Core StructureDefinition count mismatch")
    seen: set[tuple[str, str]] = set()
    binding_count = 0
    for row in registry.get("constraints", []):
        if row["profile_url"] not in structure_urls:
            raise ValueError(
                "KR Core constraint references unknown StructureDefinition"
            )
        key = (row["profile_url"], row["element_id"])
        if key in seen:
            raise ValueError(f"duplicate KR Core constraint: {key}")
        seen.add(key)
        binding = row.get("binding")
        if binding:
            binding_count += 1
            if binding["strength"] not in ALLOWED_STRENGTHS:
                raise ValueError(f"{key}: invalid KR Core binding strength")
            if not binding["value_set"].startswith(("http://", "https://")):
                raise ValueError(f"{key}: invalid KR Core ValueSet canonical")
    if registry.get("constraint_count") != len(seen):
        raise ValueError("KR Core constraint count mismatch")
    if registry.get("binding_count") != binding_count:
        raise ValueError("KR Core binding count mismatch")
    if registry.get("terminology_storage", {}).get(
        "duplicate_value_set_content"
    ) is not False:
        raise ValueError("KR Core terminology must remain an external reference")


def _profile_index(
    registry: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        profile["url"]: profile
        for profile in [
            *registry["profiles"],
            *registry.get("extensions", []),
        ]
    }


def _constraint_index(
    registry: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in registry["constraints"]:
        result.setdefault(row["profile_url"], []).append(row)
    return result


def profiles_for_resource(
    resource: str,
    *,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if registry is None:
        _, registry = load_documents()
    return [
        deepcopy(profile)
        for profile in registry["profiles"]
        if profile["resource"] == resource
    ]


def binding_for_profile_element(
    profile_url: str,
    element_path: str,
    *,
    element_id: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if registry is None:
        _, registry = load_documents()
    profile = _profile_index(registry).get(profile_url)
    if profile is None:
        raise ValueError(f"unknown KR Core V2 profile: {profile_url}")
    candidates = [
        row for row in _constraint_index(registry).get(profile_url, [])
        if row["element_path"] == element_path and row.get("binding")
        and (element_id is None or row["element_id"] == element_id)
    ]
    if not candidates:
        return None
    unique = {
        (row["binding"]["strength"], row["binding"]["value_set"])
        for row in candidates
    }
    if len(unique) != 1:
        raise ValueError(
            f"{profile_url}::{element_path}: sliced KR Core binding is "
            "ambiguous; select an element_id"
        )
    result = deepcopy(candidates[0])
    result["profile"] = deepcopy(profile)
    return result


def binding_for_selected_profiles(
    profile_urls: list[str],
    resource: str,
    element_path: str,
    *,
    element_id: str | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Resolve one compatible binding across explicitly selected profiles."""
    if registry is None:
        _, registry = load_documents()
    rows = []
    for profile_url in profile_urls:
        profile = _profile_index(registry).get(profile_url)
        if profile is None:
            raise ValueError(f"unknown KR Core V2 profile: {profile_url}")
        if profile["resource"] != resource:
            continue
        row = binding_for_profile_element(
            profile_url,
            element_path,
            element_id=element_id,
            registry=registry,
        )
        if row:
            rows.append(row)
    if not rows:
        return None
    unique = {
        (row["binding"]["strength"], row["binding"]["value_set"])
        for row in rows
    }
    if len(unique) != 1:
        raise ValueError(
            f"{resource}.{element_path}: selected KR Core profiles have "
            "incompatible bindings; split the projection"
        )
    result = deepcopy(rows[0])
    result["selected_profiles"] = [
        row["profile"]["url"] for row in rows
    ]
    return result


def projection_requirements(
    profile_url: str,
    *,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return constraints that must be checked before KR Core projection."""
    if registry is None:
        _, registry = load_documents()
    if profile_url not in _profile_index(registry):
        raise ValueError(f"unknown KR Core V2 profile: {profile_url}")
    return [
        deepcopy(row)
        for row in _constraint_index(registry).get(profile_url, [])
        if row["min"] and int(row["min"]) > 0
        or row["must_support"]
        or row["max"] == "0"
    ]
