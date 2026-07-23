#!/usr/bin/env python3
"""Build the complete official LOINC Answer List reference catalog from STOM."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.fhir_valueset_service import (  # noqa: E402
    DEFAULT_BASE_URL,
    LOINC_ANSWER_LIST_AGGREGATE_URL,
    LOINC_ANSWER_LIST_CANONICAL_PREFIX,
    LOINC_SYSTEM_URL,
    FhirValueSetService,
)
from interoperability.loinc_answer_list_catalog import (  # noqa: E402
    validate_catalog,
)


DEFAULT_OUTPUT = (
    ROOT / "sources" / "catalogs" / "loinc-answer-lists-stom.json"
)


def build(
    service: FhirValueSetService,
    *,
    checked_at: str,
    workers: int = 32,
) -> dict:
    observed_at = datetime.fromisoformat(checked_at.replace("Z", "+00:00"))
    next_monitor_at = (observed_at + timedelta(days=30)).date().isoformat()
    aggregate = service.read_valueset("loinc-answer-lists")
    members = service.list_loinc_answer_lists()
    lookup = service.lookup_codesystem_code(
        LOINC_SYSTEM_URL,
        code="LL2201-3",
    )

    def resolve(member: dict) -> dict:
        code = member["code"]
        expansion = service.expand_loinc_answer_list(code, count=0)
        return {
            "code": code,
            "canonical": LOINC_ANSWER_LIST_CANONICAL_PREFIX + code,
            "display": member.get("display"),
            "member_count": expansion["expansion"]["total"],
            "resolution": "stom_dynamic_expand",
        }

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        entries = list(executor.map(resolve, members))
    entries.sort(key=lambda item: item["code"])
    catalog = {
        "id": "catalog.loinc-answer-lists",
        "version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "purpose": (
            "Complete Build-Time reference index of official LOINC LL "
            "Answer Lists resolvable through STOM."
        ),
        "aggregate_canonical": LOINC_ANSWER_LIST_AGGREGATE_URL,
        "aggregate_resource_id": aggregate.get("id"),
        "aggregate_valueset_version": aggregate.get("version"),
        "loinc_codesystem_version": lookup.get("version"),
        "version_alignment": (
            "aligned"
            if aggregate.get("version") == lookup.get("version")
            else "metadata_mismatch"
        ),
        "registration_mode": "reference_catalog_and_dynamic_resolution",
        "server_resources_created": 0,
        "runtime_dependency": False,
        "total": len(entries),
        "membership_total": sum(item["member_count"] for item in entries),
        "entries": entries,
        "refresh": {
            "class": "terminology_mapping",
            "source_monitor_profile": "terminology_server",
            "monitor_interval_days": 30,
            "last_monitored_at": checked_at[:10],
            "next_monitor_at": next_monitor_at,
            "immediate_review_triggers": [
                "LOINC release changes",
                "aggregate membership changes",
                "individual expansion failure",
                "aggregate and CodeSystem version mismatch changes",
            ],
        },
        "provenance": {
            "created_by": {"type": "ai", "id": "codex-gpt5"},
            "created_at": checked_at,
            "source_endpoint": service.base_url,
            "source_refs": [
                f"{service.base_url}/ValueSet/loinc-answer-lists",
                (
                    f"{service.base_url}/ValueSet/$expand"
                    "?url=http://loinc.org/vs/ll"
                ),
                "https://loinc.org/fhir/",
                "https://loinc.org/answer-file/",
            ],
            "contains_raw_patient_text": False,
            "review_status": "unreviewed",
        },
    }
    validate_catalog(catalog)
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--checked-at")
    args = parser.parse_args()
    checked_at = args.checked_at or datetime.now(timezone.utc).isoformat()
    catalog = build(
        FhirValueSetService(args.base_url),
        checked_at=checked_at,
        workers=args.workers,
    )
    output = args.output
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(output.relative_to(ROOT)),
                "answer_list_count": catalog["total"],
                "membership_total": catalog["membership_total"],
                "version_alignment": catalog["version_alignment"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
