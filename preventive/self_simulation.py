"""Deterministic exploratory simulations for preventive questionnaire coverage."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any
import json

from preventive.national_screening import NationalScreeningSession


DEFAULT_CASES = Path(__file__).resolve().parents[1] / "simulation/preventive/kr-national-screening-cases.json"


def run(path: Path | str = DEFAULT_CASES) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        cases = json.load(handle)["cases"]
    results = []
    candidate_gaps: dict[str, dict[str, Any]] = {}
    for case in cases:
        session = NationalScreeningSession(case["id"], case["patient_context"])
        eligible = set(session.eligible_group_ids())
        expected = set(case["expected_groups"])
        missing_groups = sorted(expected - eligible)
        unexpected_groups = sorted(eligible - expected)
        for observation in case.get("unmodeled_observations", []):
            candidate_gaps.setdefault(observation["candidate_fact_id"], deepcopy(observation))
        results.append({
            "case_id": case["id"],
            "passed": not missing_groups and not unexpected_groups,
            "eligible_groups": sorted(eligible),
            "missing_groups": missing_groups,
            "unexpected_groups": unexpected_groups,
        })
    return {
        "status": "research_only",
        "review_status": "unreviewed",
        "case_count": len(results),
        "passed": all(item["passed"] for item in results),
        "results": results,
        "candidate_fact_gaps": sorted(candidate_gaps.values(), key=lambda item: item["candidate_fact_id"]),
    }
