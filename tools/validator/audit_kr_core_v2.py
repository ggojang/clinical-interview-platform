#!/usr/bin/env python3
"""Audit KR Core V2 profile coverage and STOM canonical discovery."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.kr_core_v2 import load_documents, validate_documents


OUTPUT = ROOT / "coverage/kr-core-v2-interoperability-latest.json"


def _discover_value_set(
    base_url: str,
    canonical: str,
) -> dict[str, Any]:
    endpoint = (
        f"{base_url.rstrip('/')}/ValueSet?"
        f"{urlencode({'url': canonical, '_count': '2'})}"
    )
    with urlopen(endpoint, timeout=30) as response:
        bundle = json.load(response)
    entries = bundle.get("entry", [])
    return {
        "canonical": canonical,
        "found": bundle.get("total", len(entries)) > 0,
        "resource_ids": sorted({
            item.get("resource", {}).get("id")
            for item in entries
            if item.get("resource", {}).get("id")
        }),
    }


def run(base_url: str | None = None) -> dict[str, Any]:
    policy, registry = load_documents()
    validate_documents(policy, registry)
    resources: dict[str, int] = {}
    for profile in registry["profiles"]:
        resources[profile["resource"]] = resources.get(
            profile["resource"], 0
        ) + 1
    kr_canonicals = [
        item["url"] for item in registry["defined_value_sets"]
    ]
    terminology_results = []
    errors = []
    if base_url:
        for canonical in kr_canonicals:
            try:
                result = _discover_value_set(base_url, canonical)
                terminology_results.append(result)
                if not result["found"]:
                    errors.append(
                        f"STOM cannot discover KR Core ValueSet: {canonical}"
                    )
            except Exception as exc:
                errors.append(f"{canonical}: {exc}")
                terminology_results.append({
                    "canonical": canonical,
                    "found": False,
                    "error": str(exc),
                })
    profile_urls = {item["url"] for item in registry["profiles"]}
    report = {
        "id": "audit.kr-core-v2-interoperability",
        "version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "passed": not errors,
        "package": registry["package"],
        "policy_id": policy["id"],
        "source": registry["source"],
        "profile_count": registry["profile_count"],
        "extension_count": registry["extension_count"],
        "structure_definition_count": registry[
            "structure_definition_count"
        ],
        "profile_counts_by_resource": dict(sorted(resources.items())),
        "constraint_count": registry["constraint_count"],
        "binding_count": registry["binding_count"],
        "defined_value_set_count": registry["defined_value_set_count"],
        "kr_core_referenced_value_set_count": (
            registry["kr_core_referenced_value_set_count"]
        ),
        "questionnaire": {
            "profile_defined_in_kr_core_v2": any(
                item["resource"] in {"Questionnaire", "QuestionnaireResponse"}
                for item in registry["profiles"]
            ),
            "projection_policy": policy["scope"]["questionnaire"],
        },
        "terminology": {
            "storage_mode": registry["terminology_storage"]["mode"],
            "duplicate_value_set_content": (
                registry["terminology_storage"][
                    "duplicate_value_set_content"
                ]
            ),
            "service_checked": bool(base_url),
            "base_url": base_url,
            "canonical_count": len(kr_canonicals),
            "discoverable_count": sum(
                item["found"] for item in terminology_results
            ),
            "results": terminology_results,
        },
        "profile_urls": sorted(profile_urls),
        "errors": errors,
        "limitations": [
            "This report verifies profile metadata and canonical discovery; it is not a KR Core conformance certification.",
            "A KR Core profile is selected only when export context identifies the intended Korean resource profile.",
            "Must Support gaps are reported and are never filled with fabricated patient data.",
        ],
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = run(args.base_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
