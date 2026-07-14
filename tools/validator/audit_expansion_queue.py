#!/usr/bin/env python3
"""Audit every v0.2 grouped Primary Care expansion package against release gates."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "knowledge/catalog/planned-package-work-queue-v0.2.json"
CATALOG = ROOT / "knowledge/catalog/primary-care-rfe.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def package_index() -> dict[str, tuple[Path, dict[str, Any]]]:
    result = {}
    for path in (ROOT / "packages/generated").glob("*.json"):
        package = load(path)
        result[package["package_id"]] = (path, package)
    return result


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def audit_entry(
    queue_entry: dict[str, Any],
    catalog: dict[str, dict[str, Any]],
    packages: dict[str, tuple[Path, dict[str, Any]]],
) -> dict[str, Any]:
    rfe = queue_entry["rfe"]
    package_id = queue_entry.get("package_id")
    failures: list[str] = []
    check(queue_entry.get("state") == "implemented_unreviewed", "queue state is not implemented_unreviewed", failures)
    catalog_entry = catalog.get(rfe, {})
    check(catalog_entry.get("implementation_status") == "implemented", "catalog entry is not implemented", failures)
    check(catalog_entry.get("package_id") == package_id, "catalog package_id mismatch", failures)
    check(package_id in packages, "compiled package missing", failures)
    if package_id not in packages:
        return {"rfe": rfe, "package_id": package_id, "passed": False, "failures": failures}

    package_path, package = packages[package_id]
    check(package.get("release_state") == "draft", "package is not draft", failures)
    usage = package.get("usage_policy", {})
    check(usage.get("production_allowed") is False, "production is not explicitly disabled", failures)
    check(usage.get("unreviewed_knowledge_allowed") is True, "research use is not enabled", failures)
    check(set(usage.get("allowed_modes", [])) == {"research_test", "simulation"}, "allowed modes differ from research_test/simulation", failures)

    nodes = package.get("knowledge_graph", {}).get("nodes", [])
    facts = [node for node in nodes if node.get("type") == "Fact"]
    questions = [node for node in nodes if node.get("type") == "QuestionTemplate"]
    rules = package.get("rule_graph", {}).get("rules", [])
    check(bool(facts), "package has no Facts", failures)
    check(bool(questions), "package has no Questions", failures)
    check(all(node.get("status") == "research_only" for node in facts), "Fact status is not uniformly research_only", failures)
    check(all(node.get("provenance", {}).get("review_status") == "unreviewed" for node in facts), "Fact provenance is not uniformly unreviewed", failures)
    check(all(rule.get("provenance", {}).get("review_status") == "unreviewed" for rule in rules), "Rule provenance is not uniformly unreviewed", failures)

    fact_ids = {node["id"] for node in facts}
    question_index = package.get("indexes", {}).get("questions_by_fact", {})
    check(fact_ids == set(question_index), "Fact-to-Question coverage is incomplete", failures)
    coverage = package.get("coverage", {})
    check(coverage.get("total_facts") == len(facts), "coverage total_facts mismatch", failures)
    check(coverage.get("facts_with_questions") == len(facts), "coverage facts_with_questions mismatch", failures)
    check(coverage.get("total_safety_rules") == coverage.get("safety_rules_with_simulations"), "not all safety rules have simulations", failures)
    check(coverage.get("uncovered_safety_rules") == [], "uncovered safety rules remain", failures)
    check(coverage.get("data_absent_reason_simulations", 0) >= 1, "dataAbsentReason simulation missing", failures)

    simulations = package.get("simulations", [])
    check(len(simulations) == coverage.get("simulation_count"), "simulation count mismatch", failures)
    check(len(simulations) > coverage.get("total_safety_rules", 0), "positive/negative or absent-data simulation beyond safety cases is missing", failures)

    research_manifests = package.get("research_source_manifests", [])
    artifacts = [artifact for manifest in research_manifests for artifact in manifest.get("artifacts", [])]
    check(bool(artifacts), "authoritative research source artifacts missing", failures)
    check(any(artifact.get("monitor_profile") in {"clinical_guideline", "nice_guidance"} for artifact in artifacts), "clinical or NICE guideline source missing", failures)
    check(any(artifact.get("monitor_profile") == "terminology_server" for artifact in artifacts), "terminology source missing", failures)
    check(all(artifact.get("monitor_interval_days") in {1, 7, 30} for artifact in artifacts), "source refresh cadence is outside approved daily/weekly/monthly profiles", failures)
    check(all(artifact.get("next_monitor_at") for artifact in artifacts), "source next_monitor_at missing", failures)

    mapping_paths = [
        ROOT / artifact["path"]
        for artifact in package.get("source_manifest", {}).get("artifacts", [])
        if artifact.get("kind") == "terminology_mapping" and artifact.get("path")
    ]
    check(len(mapping_paths) == 1 and mapping_paths[0].exists(), "terminology mapping artifact missing", failures)
    if len(mapping_paths) == 1 and mapping_paths[0].exists():
        mapping = load(mapping_paths[0])
        check(mapping.get("validation", {}).get("clinical_rule_authority") is False, "MRCM incorrectly controls clinical rules", failures)
        check(mapping.get("review_status") == "unreviewed", "terminology mapping is not unreviewed", failures)

    slug = rfe.removeprefix("rfe.")
    public_root = ROOT / "docs/gpt/rfe" / slug
    for kind, count in (("facts", len(facts)), ("questions", len(questions))):
        path = public_root / f"{kind}.json"
        check(path.exists(), f"public {kind} resource missing", failures)
        if path.exists():
            document = load(path)
            check(document.get("count") == count, f"public {kind} count mismatch", failures)
            check(document.get("status") == "research_only", f"public {kind} status mismatch", failures)
            check(document.get("review_status") == "unreviewed", f"public {kind} review status mismatch", failures)
    rules_path = public_root / "rules.json"
    check(rules_path.exists(), "public rules resource missing", failures)
    if rules_path.exists():
        check(load(rules_path).get("count") == len(rules), "public rule count mismatch", failures)

    return {
        "rfe": rfe,
        "package_id": package_id,
        "package_path": str(package_path.relative_to(ROOT)),
        "fact_count": len(facts),
        "safety_rule_count": coverage.get("total_safety_rules"),
        "simulation_count": len(simulations),
        "source_artifact_count": len(artifacts),
        "passed": not failures,
        "failures": failures,
    }


def run() -> dict[str, Any]:
    queue = load(QUEUE)
    catalog = {entry["id"]: entry for entry in load(CATALOG)["entries"]}
    packages = package_index()
    results = [audit_entry(entry, catalog, packages) for entry in queue["order"]]
    queue_materialized = (
        queue.get("status") == "materialized_unreviewed"
        and all(entry.get("state") == "implemented_unreviewed" for entry in queue["order"])
    )
    return {
        "audit_id": "audit.primary-care-grouped-expansion-v0.2",
        "queue_id": queue["id"],
        "queue_version": queue["version"],
        "queue_status": queue.get("status"),
        "entry_count": len(results),
        "passed": queue_materialized and all(result["passed"] for result in results),
        "results": results,
    }


if __name__ == "__main__":
    report = run()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    sys.exit(0 if report["passed"] else 1)
