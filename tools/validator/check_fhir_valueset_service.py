#!/usr/bin/env python3
"""Check the configured STOM FHIR ValueSet service without mutating it."""
from __future__ import annotations

import argparse
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


PROBE_URL = (
    "http://terminology.hl7.org/ValueSet/"
    "yes-no-unknown-not-applicable"
)
PROBE_SYSTEM = "http://terminology.hl7.org/CodeSystem/v2-0532"


def run(base_url: str) -> dict:
    service = FhirValueSetService(base_url)
    capabilities = service.valueset_capabilities()
    required_interactions = {"read", "search-type"}
    required_operations = {"$expand", "$validate-code"}
    missing_interactions = sorted(
        required_interactions - set(capabilities["interactions"])
    )
    missing_operations = sorted(
        required_operations - set(capabilities["operations"])
    )
    matches = service.search_by_canonical(PROBE_URL, count=1)
    expanded = service.expand(PROBE_URL, count=20)
    contains = expanded.get("expansion", {}).get("contains", [])
    valid_yes = service.validate_code(
        PROBE_URL,
        system=PROBE_SYSTEM,
        code="Y",
    )
    invalid_code = service.validate_code(
        PROBE_URL,
        system=PROBE_SYSTEM,
        code="NOT-A-CODE",
    )
    passed = (
        not missing_interactions
        and not missing_operations
        and len(matches) == 1
        and any(
            item.get("system") == PROBE_SYSTEM and item.get("code") == "Y"
            for item in contains
        )
        and valid_yes["result"] is True
        and invalid_code["result"] is False
    )
    return {
        "id": "stom-fhir-valueset-service-check",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if passed else "fail",
        "base_url": service.base_url,
        "read_only_check": True,
        "capability": capabilities,
        "required_capability_gaps": {
            "interactions": missing_interactions,
            "operations": missing_operations,
        },
        "probe": {
            "canonical_url": PROBE_URL,
            "search_match_count": len(matches),
            "expansion_contains_count": len(contains),
            "valid_code_result": valid_yes["result"],
            "invalid_code_result": invalid_code["result"],
        },
        "runtime_terminology_lookup_required": False,
        "patient_data_transmitted": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.base_url)
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
