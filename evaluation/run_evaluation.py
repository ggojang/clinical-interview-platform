"""Execute package simulations and emit a reproducible evaluation report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.package import DEFAULT_PACKAGE, load_package
from runtime.session import InterviewSession
from runtime.simulator import PatientSimulator


def evaluate_case(case_path: Path, package_path: Path) -> dict[str, Any]:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    simulator = PatientSimulator(case)
    session = InterviewSession(
        case["id"],
        package_path=package_path,
        encounter_context=case.get("encounter_context"),
    )
    utterance = simulator.initial(case.get("simulation_language", "en"))
    selected_facts: list[str] = []

    state: dict[str, Any] = {}
    for _ in range(session.max_turns):
        state = session.process(utterance)
        question = state["selected_question"]
        if question is None:
            break
        selected_facts.append(question["fact_id"])
        utterance = simulator.answer(question["fact_id"])

    expected = case.get("expected", {})
    failures: list[str] = []
    preferred = expected.get("preferred_pattern")
    if preferred and preferred not in state.get("active_patterns", []):
        failures.append(f"preferred pattern not active: {preferred}")
    expected_safety = expected.get("expected_safety_level")
    actual_safety = state.get("safety_status", {}).get("level")
    if expected_safety and actual_safety != expected_safety:
        failures.append(
            f"safety level mismatch: expected {expected_safety}, got {actual_safety}"
        )
    expected_stop = expected.get("expected_stop_reason")
    if expected_stop and state.get("stop_reason") != expected_stop:
        failures.append(
            f"stop reason mismatch: expected {expected_stop}, got {state.get('stop_reason')}"
        )
    expected_action = expected.get("expected_safety_action")
    actual_action = state.get("safety_status", {}).get("action")
    if expected_action and actual_action != expected_action:
        failures.append(
            f"safety action mismatch: expected {expected_action}, got {actual_action}"
        )
    triggered_rules = state.get("safety_status", {}).get("triggered_rules", [])
    for rule_id in expected.get("expected_triggered_rules_contains", []):
        if rule_id not in triggered_rules:
            failures.append(f"expected safety Rule was not triggered: {rule_id}")
    for fact_id in expected.get("expected_selected_facts_contains", []):
        if fact_id not in selected_facts:
            failures.append(f"expected Fact was not selected: {fact_id}")
    for fact_id, expected_value in expected.get("expected_known_facts", {}).items():
        record = state.get("facts", {}).get(fact_id, {})
        if record.get("status") != "known" or record.get("value") != expected_value:
            failures.append(
                f"expected known Fact mismatch: {fact_id}={expected_value!r}"
            )
    for fact_id, expected_reason in expected.get(
        "expected_data_absent_reasons", {}
    ).items():
        record = state.get("facts", {}).get(fact_id, {})
        actual_reason = record.get("dataAbsentReason", {}).get("code")
        if actual_reason != expected_reason or record.get("value") is not None:
            failures.append(
                f"dataAbsentReason mismatch: {fact_id} expected {expected_reason!r}, "
                f"got {actual_reason!r}"
            )

    max_turns = expected.get("expected_max_turns")
    if max_turns is not None and state.get("turn", 0) > max_turns:
        failures.append(
            f"turn budget exceeded: expected <= {max_turns}, got {state.get('turn', 0)}"
        )

    serialized = json.dumps(state, ensure_ascii=False)
    for forbidden in expected.get("forbidden_assertions", []):
        if forbidden in serialized:
            failures.append(f"forbidden assertion present: {forbidden}")

    repeated = {
        fact_id: selected_facts.count(fact_id)
        for fact_id in set(selected_facts)
        if selected_facts.count(fact_id) > 1
    }
    mandatory = set(
        session.package.get("interview_completion_policy", {})
        .get("must_be_known_facts", [])
    )
    disallowed_repetitions = {
        fact_id: count for fact_id, count in repeated.items()
        if fact_id not in mandatory or count > 2
    }
    if disallowed_repetitions:
        failures.append("equivalent fact question repeated")

    return {
        "case_id": case["id"],
        "passed": not failures,
        "failures": failures,
        "turns": state.get("turn", 0),
        "selected_facts": selected_facts,
        "safety_level": actual_safety,
        "safety_action": actual_action,
        "triggered_rules": triggered_rules,
        "stop_reason": state.get("stop_reason"),
        "known_fact_count": sum(
            record.get("status") == "known"
            for record in state.get("facts", {}).values()
        ),
        "data_absent_fact_count": len(state.get("data_absent_facts", {})),
        "completion_status": state.get("completion_status"),
        "package": state.get("package"),
        "encounter_context": state.get("patient_context"),
    }


def run(package_path: Path = DEFAULT_PACKAGE) -> dict[str, Any]:
    package = load_package(package_path)
    case_paths = [ROOT / item["path"] for item in package.get("simulations", [])]
    results = [
        evaluate_case(path, package_path)
        for path in case_paths
    ]
    return {
        "evaluation_id": "evaluation." + package["package_id"].removeprefix("package."),
        "version": "0.1.0",
        "package_id": package["package_id"],
        "package_version": package["package_version"],
        "semantic_digest": package["semantic_digest"],
        "case_count": len(results),
        "passed": all(item["passed"] for item in results),
        "results": results,
        "provenance": {
            "created_by": {"type": "runtime", "id": "evaluation.run_evaluation"},
            "created_at": "2026-07-14T00:00:00Z",
            "source_refs": [str(path.relative_to(ROOT)) for path in case_paths],
            "review_status": "unreviewed",
            "version": "0.1.0",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.package.resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
