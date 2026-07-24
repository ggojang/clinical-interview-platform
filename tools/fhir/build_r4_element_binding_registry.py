#!/usr/bin/env python3
"""Build the offline registry of FHIR R4 resource element bindings.

This is a Build Time tool. Runtime code consumes only the checked-in registry
and never downloads FHIR definitions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]
SOURCE_URL = "https://hl7.org/fhir/R4/profiles-resources.json"
OUTPUT = ROOT / "mappings/fhir/r4/resource-element-bindings.json"
FHIR_VERSION = "4.0.1"


def _download() -> tuple[dict[str, Any], str]:
    with urlopen(SOURCE_URL, timeout=60) as response:
        payload = response.read()
    return json.loads(payload), hashlib.sha256(payload).hexdigest()


def build(bundle: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    resources = 0
    for item in bundle.get("entry", []):
        resource = item.get("resource", {})
        if (
            resource.get("resourceType") != "StructureDefinition"
            or resource.get("kind") != "resource"
            or resource.get("derivation") != "specialization"
        ):
            continue
        if resource.get("fhirVersion") != FHIR_VERSION:
            raise ValueError(
                f"{resource.get('type')}: unexpected FHIR version "
                f"{resource.get('fhirVersion')}"
            )
        resources += 1
        source = resource.get("url")
        for element in resource.get("snapshot", {}).get("element", []):
            binding = element.get("binding")
            if not binding:
                continue
            canonical = binding.get("valueSet")
            if not canonical:
                continue
            entries.append({
                "resource": resource["type"],
                "element_id": element["id"],
                "element_path": element["path"],
                "min": element.get("min"),
                "max": element.get("max"),
                "types": [
                    item["code"] for item in element.get("type", [])
                    if item.get("code")
                ],
                "binding": {
                    "strength": binding["strength"],
                    "value_set": canonical,
                    "description": binding.get("description"),
                },
                "structure_definition": source,
            })
    entries.sort(key=lambda row: (row["resource"], row["element_id"]))
    return {
        "id": "registry.fhir-r4-resource-element-bindings",
        "version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "fhir_version": FHIR_VERSION,
        "source": {
            "url": SOURCE_URL,
            "sha256": source_sha256,
            "retrieved_at": "2026-07-24",
        },
        "refresh": {
            "profile": "interoperability_standard",
            "interval_days": 7,
            "last_verified_at": "2026-07-24",
            "next_verification_at": "2026-07-31",
            "policy_id": "policy.knowledge-refresh",
        },
        "resource_count": resources,
        "binding_count": len(entries),
        "bindings": entries,
    }


def validate(registry: dict[str, Any]) -> None:
    if registry.get("fhir_version") != FHIR_VERSION:
        raise ValueError("FHIR registry must use R4 4.0.1")
    if registry.get("status") != "research_only":
        raise ValueError("FHIR registry must remain research_only")
    allowed_strengths = {"required", "extensible", "preferred", "example"}
    seen: set[str] = set()
    resources: set[str] = set()
    for row in registry.get("bindings", []):
        key = f"{row['resource']}::{row['element_id']}"
        if key in seen:
            raise ValueError(f"duplicate FHIR element binding: {key}")
        seen.add(key)
        resources.add(row["resource"])
        binding = row["binding"]
        if binding["strength"] not in allowed_strengths:
            raise ValueError(f"{key}: unsupported binding strength")
        if not binding["value_set"].startswith(("http://", "https://")):
            raise ValueError(f"{key}: invalid ValueSet canonical")
        if not row["structure_definition"].startswith("http://hl7.org/fhir/"):
            raise ValueError(f"{key}: non-HL7 base StructureDefinition")
    if registry.get("binding_count") != len(seen):
        raise ValueError("FHIR binding count does not match entries")
    if registry.get("resource_count") != len(resources):
        raise ValueError("FHIR resource count does not match entries")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    bundle, digest = _download()
    registry = build(bundle, digest)
    validate(registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {args.output}: {registry['resource_count']} resources, "
        f"{registry['binding_count']} bindings"
    )


if __name__ == "__main__":
    main()
