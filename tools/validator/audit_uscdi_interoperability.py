#!/usr/bin/env python3
"""Audit USCDI v6 and USCDI+ overlays across every compiled package profile."""
from __future__ import annotations

import json
import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from compiler.build_package import PACKAGE_PROFILES, compile_package
from interoperability.uscdi import validate_overlay_documents


def run() -> dict:
    source = validate_overlay_documents()
    results = []
    passed = True
    for profile in PACKAGE_PROFILES:
        package = compile_package(profile=profile)
        overlay = package["interoperability_coverage"]
        failures = []
        if overlay["clinical_authority"] is not False:
            failures.append("overlay controls clinical behavior")
        if overlay["completion_authority"] is not False:
            failures.append("overlay controls completion")
        if overlay["jurisdiction"] != {"framework": "US", "deployment": "KR"}:
            failures.append("jurisdiction boundary mismatch")
        core = overlay["core"]
        if core["mapped_element_count"] > core["eligible_element_count"]:
            failures.append("mapped count exceeds eligible count")
        results.append({
            "profile": profile,
            "package_id": package["package_id"],
            "mapped_element_count": core["mapped_element_count"],
            "eligible_element_count": core["eligible_element_count"],
            "coverage_percent": core["coverage_percent"],
            "uscdi_plus_domains": [
                item["domain_id"] for item in overlay["uscdi_plus_domains"]
            ],
            "passed": not failures,
            "failures": failures,
        })
        passed = passed and not failures
    return {
        "id": "audit.uscdi-interoperability",
        "version": "0.1.0",
        "status": "research_only",
        "review_status": "unreviewed",
        "passed": passed,
        "package_count": len(results),
        "source_validation": source,
        "results": results,
        "limitations": [
            "This is mapping Coverage, not US certification or conformance.",
            "Unmapped record-only elements must not become patient questions.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    raise SystemExit(0 if report["passed"] else 1)
