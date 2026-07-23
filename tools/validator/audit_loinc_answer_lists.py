#!/usr/bin/env python3
"""Audit the complete LOINC Answer List catalog and live STOM resolution."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.fhir_valueset_service import (  # noqa: E402
    DEFAULT_BASE_URL,
    FhirValueSetService,
)
from interoperability.loinc_answer_list_catalog import (  # noqa: E402
    LoincAnswerListCatalogError,
    validate_catalog,
)


DEFAULT_CATALOG = (
    ROOT / "sources" / "catalogs" / "loinc-answer-lists-stom.json"
)


def run(
    base_url: str,
    catalog_path: Path,
    *,
    workers: int = 32,
) -> dict:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    static = validate_catalog(catalog)
    service = FhirValueSetService(base_url)
    aggregate_members = service.list_loinc_answer_lists()
    live_codes = {item["code"] for item in aggregate_members}
    catalog_codes = {item["code"] for item in catalog["entries"]}
    expected_member_counts = {
        item["code"]: item["member_count"]
        for item in catalog["entries"]
    }

    def check(entry: dict) -> tuple[str, int | None, str | None]:
        try:
            resource = service.expand_loinc_answer_list(
                entry["code"],
                count=0,
            )
            return (
                entry["code"],
                resource["expansion"]["total"],
                None,
            )
        except Exception as exc:  # report every server failure in one audit
            return entry["code"], None, f"{type(exc).__name__}: {exc}"

    with ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        live_results = list(executor.map(check, catalog["entries"]))
    failures = [
        {
            "code": code,
            "observed_member_count": total,
            "error": error,
        }
        for code, total, error in live_results
        if error is not None
        or total != expected_member_counts[code]
    ]
    passed = (
        not failures
        and live_codes == catalog_codes
        and len(live_codes) == static["answer_list_count"]
    )
    return {
        "id": "audit.loinc-answer-lists",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if passed else "fail",
        "base_url": service.base_url,
        "catalog_path": str(catalog_path.relative_to(ROOT)),
        "catalog_answer_list_count": static["answer_list_count"],
        "catalog_membership_total": static["membership_total"],
        "live_aggregate_count": len(live_codes),
        "live_individual_expansion_checked": len(live_results),
        "live_individual_expansion_failures": len(failures),
        "failure_samples": failures[:20],
        "missing_from_live_aggregate": sorted(catalog_codes - live_codes),
        "missing_from_catalog": sorted(live_codes - catalog_codes),
        "aggregate_valueset_version": catalog.get(
            "aggregate_valueset_version"
        ),
        "loinc_codesystem_version": catalog.get(
            "loinc_codesystem_version"
        ),
        "version_alignment": catalog.get("version_alignment"),
        "version_warning": (
            "STOM aggregate ValueSet metadata is older than the observed "
            "LOINC CodeSystem version; preserve both versions in provenance."
            if catalog.get("version_alignment") != "aligned"
            else None
        ),
        "server_resources_created": 0,
        "runtime_dependency": False,
        "patient_data_transmitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workers", type=int, default=32)
    args = parser.parse_args()
    catalog_path = args.catalog
    if not catalog_path.is_absolute():
        catalog_path = ROOT / catalog_path
    try:
        report = run(
            args.base_url,
            catalog_path,
            workers=args.workers,
        )
    except (OSError, json.JSONDecodeError, LoincAnswerListCatalogError) as exc:
        report = {
            "id": "audit.loinc-answer-lists",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "status": "fail",
            "error": f"{type(exc).__name__}: {exc}",
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(output.relative_to(ROOT))
    else:
        print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
