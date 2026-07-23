#!/usr/bin/env python3
"""Audit server reuse and duplicate content for project answer ValueSets."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.fhir_valueset_reconcile import (  # noqa: E402
    ValueSetReconciliationError,
    membership_fingerprint,
    reconcile_reference,
)
from interoperability.fhir_valueset_service import (  # noqa: E402
    DEFAULT_BASE_URL,
    FhirValueSetService,
)
from tools.fhir.build_answer_valuesets import build, validate  # noqa: E402


def run(base_url: str) -> dict:
    service = FhirValueSetService(base_url)
    catalog_summary = service.list_valuesets()
    bundle = build()
    validate(bundle)
    resources = [entry["resource"] for entry in bundle["entry"]]
    decisions = [
        reconcile_reference(
            resource,
            service.search_by_canonical(
                resource["url"],
                version=resource.get("version"),
                count=2,
            ),
        )
        for resource in resources
    ]
    counts = Counter(item["action"] for item in decisions)
    project_by_fingerprint: dict[str, list[str]] = defaultdict(list)
    for resource in resources:
        project_by_fingerprint[membership_fingerprint(resource)].append(
            resource["url"]
        )
    duplicate_groups = [
        sorted(canonicals)
        for canonicals in project_by_fingerprint.values()
        if len(canonicals) > 1
    ]
    passed = (
        counts.get("canonical_content_conflict", 0) == 0
        and counts.get("create_reference_unchanged", 0) == 0
        and sum(counts.values()) == len(resources)
    )
    return {
        "id": "audit.reference-valuesets",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if passed else "fail",
        "base_url": base_url.rstrip("/"),
        "server_valueset_count": len(catalog_summary),
        "server_type_search_returns_full_content": all(
            bool(resource.get("compose") or resource.get("expansion"))
            for resource in catalog_summary
        ),
        "comparison_method": (
            "canonical_full_resource_search_plus_local_membership_fingerprint"
        ),
        "project_valueset_count": len(resources),
        "decision_counts": dict(sorted(counts.items())),
        "project_content_duplicate_group_count": len(duplicate_groups),
        "project_content_duplicate_samples": duplicate_groups[:10],
        "reference_mutation_performed": False,
        "runtime_dependency": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = run(args.base_url)
    except ValueSetReconciliationError as exc:
        report = {
            "id": "audit.reference-valuesets",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "status": "fail",
            "base_url": args.base_url.rstrip("/"),
            "error": str(exc),
        }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        try:
            print(output.relative_to(ROOT))
        except ValueError:
            print(output)
    else:
        print(rendered, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
