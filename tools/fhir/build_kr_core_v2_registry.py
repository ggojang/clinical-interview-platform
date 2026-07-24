#!/usr/bin/env python3
"""Build a compact KR Core V2 profile and terminology-binding registry.

The official NPM package is supplied as an input artifact. The generated
registry retains profile constraints and ValueSet canonical metadata, but does
not duplicate CodeSystem concepts or ValueSet expansions already served by
STOM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "mappings/fhir/kr-core-v2/profile-element-bindings.json"
PACKAGE_NAME = "hl7.fhir.kr.core"
PACKAGE_VERSION = "2.0.0"
FHIR_VERSION = "4.0.1"
CANONICAL_BASE = "http://www.hl7korea.or.kr/fhir/krcore"
SOURCE_URL = f"{CANONICAL_BASE}/STU2/package.tgz"
FHIR_PACKAGE_REGISTRY_URL = (
    "https://packages2.fhir.org/packages/hl7.fhir.kr.core/2.0.0"
)


def _read_package(
    package_tgz: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], str]:
    payload = package_tgz.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    with tarfile.open(package_tgz, mode="r:gz") as archive:
        members = {
            member.name: member
            for member in archive.getmembers()
            if member.isfile()
        }

        def read_json(name: str) -> dict[str, Any]:
            member = members.get(name)
            if member is None:
                raise ValueError(f"KR Core package is missing {name}")
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(f"cannot read {name}")
            return json.loads(stream.read())

        package = read_json("package/package.json")
        structures = [
            read_json(name)
            for name in sorted(members)
            if name.startswith("package/StructureDefinition-")
            and name.endswith(".json")
        ]
        value_sets = [
            read_json(name)
            for name in sorted(members)
            if name.startswith("package/ValueSet-") and name.endswith(".json")
        ]
    return package, structures, value_sets, digest


def _constraint_row(
    profile: dict[str, Any],
    element: dict[str, Any],
) -> dict[str, Any]:
    row = {
        "profile_id": profile["id"],
        "profile_url": profile["url"],
        "resource": profile["type"],
        "element_id": element["id"],
        "element_path": element["path"],
        "min": element.get("min"),
        "max": element.get("max"),
        "must_support": bool(element.get("mustSupport")),
    }
    if element.get("sliceName"):
        row["slice_name"] = element["sliceName"]
    types = [
        item["code"] for item in element.get("type", [])
        if item.get("code")
    ]
    if types:
        row["types"] = types
    binding = element.get("binding")
    if binding and binding.get("valueSet"):
        row["binding"] = {
            "strength": binding["strength"],
            "value_set": binding["valueSet"],
        }
        if binding.get("description"):
            row["binding"]["description"] = binding["description"]
    return row


def build(
    package: dict[str, Any],
    structures: list[dict[str, Any]],
    value_sets: list[dict[str, Any]],
    source_sha256: str,
) -> dict[str, Any]:
    if package.get("name") != PACKAGE_NAME:
        raise ValueError("unexpected KR Core package name")
    if package.get("version") != PACKAGE_VERSION:
        raise ValueError("unexpected KR Core package version")
    if package.get("fhirVersions") != [FHIR_VERSION]:
        raise ValueError("KR Core V2 must be based on FHIR R4 4.0.1")

    profiles = []
    extensions = []
    constraints = []
    for profile in structures:
        if profile.get("resourceType") != "StructureDefinition":
            continue
        if profile.get("derivation") != "constraint":
            continue
        if not profile.get("url", "").startswith(f"{CANONICAL_BASE}/"):
            raise ValueError(f"{profile.get('id')}: unexpected profile canonical")
        item = {
            "id": profile["id"],
            "url": profile["url"],
            "resource": profile["type"],
            "base_definition": profile["baseDefinition"],
            "status": profile.get("status"),
            "version": profile.get("version"),
        }
        if profile.get("kind") == "resource":
            profiles.append(item)
        elif (
            profile.get("kind") == "complex-type"
            and profile.get("type") == "Extension"
        ):
            extensions.append(item)
        else:
            continue
        for element in profile.get("snapshot", {}).get("element", []):
            constrained = (
                bool(element.get("binding", {}).get("valueSet"))
                or bool(element.get("mustSupport"))
                or int(element.get("min", 0)) > 0
                or element.get("max") == "0"
            )
            if constrained:
                constraints.append(_constraint_row(profile, element))

    profiles.sort(key=lambda row: row["url"])
    extensions.sort(key=lambda row: row["url"])
    constraints.sort(
        key=lambda row: (row["profile_url"], row["element_id"])
    )
    catalog = []
    for value_set in value_sets:
        url = value_set.get("url")
        if not url or not url.startswith(f"{CANONICAL_BASE}/ValueSet/"):
            raise ValueError(
                f"{value_set.get('id')}: unexpected ValueSet canonical"
            )
        catalog.append({
            "id": value_set["id"],
            "url": url,
            "version": value_set.get("version"),
            "status": value_set.get("status"),
            "title": value_set.get("title") or value_set.get("name"),
        })
    catalog.sort(key=lambda row: row["url"])

    referenced = sorted({
        row["binding"]["value_set"]
        for row in constraints
        if row.get("binding")
    })
    kr_referenced = [
        canonical for canonical in referenced
        if canonical.startswith(f"{CANONICAL_BASE}/ValueSet/")
    ]
    return {
        "id": "registry.kr-core-v2-profile-element-bindings",
        "version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "jurisdiction": "KR",
        "package": {
            "name": PACKAGE_NAME,
            "version": PACKAGE_VERSION,
            "fhir_version": FHIR_VERSION,
            "canonical": package["canonical"],
            "license": package.get("license"),
        },
        "source": {
            "url": SOURCE_URL,
            "fhir_package_registry_url": FHIR_PACKAGE_REGISTRY_URL,
            "sha256": source_sha256,
            "registry_digest_confirmed_at": "2026-07-24",
            "published_at": "2025-08-29",
            "retrieved_at": "2026-07-24",
        },
        "terminology_storage": {
            "mode": "canonical_reference_only",
            "service": "STOM FHIR R4",
            "base_url": "https://stom.infoclinic.co/fhir",
            "duplicate_value_set_content": False,
        },
        "refresh": {
            "profile": "interoperability_standard",
            "interval_days": 7,
            "last_verified_at": "2026-07-24",
            "next_verification_at": "2026-07-31",
            "policy_id": "policy.knowledge-refresh",
        },
        "profile_count": len(profiles),
        "extension_count": len(extensions),
        "structure_definition_count": len(profiles) + len(extensions),
        "constraint_count": len(constraints),
        "binding_count": sum(
            1 for row in constraints if row.get("binding")
        ),
        "referenced_value_set_count": len(referenced),
        "kr_core_referenced_value_set_count": len(kr_referenced),
        "defined_value_set_count": len(catalog),
        "profiles": profiles,
        "extensions": extensions,
        "constraints": constraints,
        "defined_value_sets": catalog,
        "referenced_value_sets": referenced,
    }


def validate(registry: dict[str, Any]) -> None:
    package = registry.get("package", {})
    if package.get("name") != PACKAGE_NAME:
        raise ValueError("invalid KR Core registry package name")
    if package.get("version") != PACKAGE_VERSION:
        raise ValueError("invalid KR Core registry version")
    if package.get("fhir_version") != FHIR_VERSION:
        raise ValueError("invalid KR Core FHIR version")
    if registry.get("status") != "research_only":
        raise ValueError("KR Core registry must remain research_only")
    if registry.get("review_status") != "unreviewed":
        raise ValueError("KR Core registry must remain unreviewed")
    if registry.get("profile_count") != len(registry.get("profiles", [])):
        raise ValueError("KR Core profile count mismatch")
    if registry.get("extension_count") != len(
        registry.get("extensions", [])
    ):
        raise ValueError("KR Core extension count mismatch")
    if registry.get("structure_definition_count") != (
        registry["profile_count"] + registry["extension_count"]
    ):
        raise ValueError("KR Core StructureDefinition count mismatch")
    if registry.get("constraint_count") != len(
        registry.get("constraints", [])
    ):
        raise ValueError("KR Core constraint count mismatch")
    seen: set[tuple[str, str]] = set()
    binding_count = 0
    allowed_strengths = {"required", "extensible", "preferred", "example"}
    structure_urls = {
        item["url"]
        for item in [
            *registry.get("profiles", []),
            *registry.get("extensions", []),
        ]
    }
    for row in registry.get("constraints", []):
        if row["profile_url"] not in structure_urls:
            raise ValueError("constraint references unknown StructureDefinition")
        key = (row["profile_url"], row["element_id"])
        if key in seen:
            raise ValueError(f"duplicate KR Core constraint: {key}")
        seen.add(key)
        binding = row.get("binding")
        if binding:
            binding_count += 1
            if binding["strength"] not in allowed_strengths:
                raise ValueError(f"{key}: unsupported binding strength")
            if not binding["value_set"].startswith(("http://", "https://")):
                raise ValueError(f"{key}: invalid ValueSet canonical")
    if registry.get("binding_count") != binding_count:
        raise ValueError("KR Core binding count mismatch")
    if registry.get("terminology_storage", {}).get(
        "duplicate_value_set_content"
    ) is not False:
        raise ValueError("KR Core terminology content must not be duplicated")
    for item in registry.get("defined_value_sets", []):
        if "compose" in item or "expansion" in item:
            raise ValueError("registry must retain canonical metadata only")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-tgz", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    package, structures, value_sets, digest = _read_package(args.package_tgz)
    registry = build(package, structures, value_sets, digest)
    validate(registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {args.output}: {registry['profile_count']} profiles, "
        f"{registry['extension_count']} extensions, "
        f"{registry['binding_count']} bindings, "
        f"{registry['defined_value_set_count']} ValueSet canonicals"
    )


if __name__ == "__main__":
    main()
