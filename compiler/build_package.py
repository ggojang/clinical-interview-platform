"""Deterministic Knowledge Package compiler for the Primary Care cough slice.

The compiler uses only versioned repository inputs. It never accesses the network
and never invents missing medical knowledge.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = ROOT / "knowledge/graph/primary-care-cough.json"
DEFAULT_RULES = ROOT / "rules/primary-care-cough.json"
DEFAULT_SOURCES = ROOT / "sources/manifests/primary-care-cough.json"
DEFAULT_COMPLETION_POLICY = ROOT / "policies/primary-care-cough-completion.json"
DEFAULT_OUTPUT = ROOT / "packages/generated/primary-care-cough-0.3.0.json"
PACKAGE_PROFILES = {
    "cough": {
        "graph": DEFAULT_GRAPH,
        "rules": DEFAULT_RULES,
        "sources": DEFAULT_SOURCES,
        "completion_policy": DEFAULT_COMPLETION_POLICY,
        "output": DEFAULT_OUTPUT,
        "package_id": "package.primary-care-cough",
        "package_version": "0.3.0",
        "rfe": "rfe.cough",
        "simulation_root": ROOT / "simulation/patients/respiratory",
        "simulation_glob": "*.json",
        "research_manifests": [ROOT / "sources/manifests/respiratory-cough-research.json"],
    },
    "fever": {
        "graph": ROOT / "knowledge/graph/primary-care-fever.json",
        "rules": ROOT / "rules/primary-care-fever.json",
        "sources": ROOT / "sources/manifests/primary-care-fever.json",
        "completion_policy": ROOT / "policies/primary-care-fever-completion.json",
        "output": ROOT / "packages/generated/primary-care-fever-0.1.0.json",
        "package_id": "package.primary-care-fever",
        "package_version": "0.1.0",
        "rfe": "rfe.fever",
        "simulation_root": ROOT / "simulation/patients/systemic/fever",
        "research_manifests": [ROOT / "sources/manifests/primary-care-fever-research.json"],
    },
    "dyspnea": {
        "graph": ROOT / "knowledge/graph/primary-care-dyspnea.json",
        "rules": ROOT / "rules/primary-care-dyspnea.json",
        "sources": ROOT / "sources/manifests/primary-care-dyspnea.json",
        "completion_policy": ROOT / "policies/primary-care-dyspnea-completion.json",
        "output": ROOT / "packages/generated/primary-care-dyspnea-0.1.0.json",
        "package_id": "package.primary-care-dyspnea",
        "package_version": "0.1.0",
        "rfe": "rfe.dyspnea",
        "simulation_root": ROOT / "simulation/patients/respiratory/dyspnea",
        "research_manifests": [ROOT / "sources/manifests/primary-care-dyspnea-research.json"],
    },
    "abdominal_pain": {
        "graph": ROOT / "knowledge/graph/primary-care-abdominal-pain.json",
        "rules": ROOT / "rules/primary-care-abdominal-pain.json",
        "sources": ROOT / "sources/manifests/primary-care-abdominal-pain.json",
        "completion_policy": ROOT / "policies/primary-care-abdominal-pain-completion.json",
        "output": ROOT / "packages/generated/primary-care-abdominal-pain-0.1.0.json",
        "package_id": "package.primary-care-abdominal-pain",
        "package_version": "0.1.0",
        "rfe": "rfe.abdominal_pain",
        "simulation_root": ROOT / "simulation/patients/gastrointestinal/abdominal-pain",
        "research_manifests": [ROOT / "sources/manifests/primary-care-abdominal-pain-research.json"],
    },
    "chest_pain": {
        "graph": ROOT / "knowledge/graph/primary-care-chest-pain.json",
        "rules": ROOT / "rules/primary-care-chest-pain.json",
        "sources": ROOT / "sources/manifests/primary-care-chest-pain.json",
        "completion_policy": ROOT / "policies/primary-care-chest-pain-completion.json",
        "output": ROOT / "packages/generated/primary-care-chest-pain-0.1.0.json",
        "package_id": "package.primary-care-chest-pain",
        "package_version": "0.1.0",
        "rfe": "rfe.chest_pain",
        "simulation_root": ROOT / "simulation/patients/cardiovascular/chest-pain",
        "research_manifests": [ROOT / "sources/manifests/primary-care-chest-pain-research.json"],
    },
}

ALLOWED_NODE_TYPES = {
    "EncounterContext", "ReasonForEncounter", "ClinicalIntent",
    "InterviewTarget", "Fact", "QuestionTemplate", "ClinicalGroup",
    "Hypothesis", "Simulation", "Coverage", "Mapping", "Guideline",
}
ALLOWED_RULE_TYPES = {
    "activation", "applicability", "requirement", "completion", "priority",
    "suppression", "conflict", "safety", "transition", "stop", "mapping",
}


class CompilationError(ValueError):
    """Raised when a package cannot be compiled without guessing."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CompilationError(f"{path.relative_to(ROOT)}: cannot load JSON: {exc}") from exc


def require_provenance(obj: dict[str, Any], label: str) -> None:
    provenance = obj.get("provenance")
    if not isinstance(provenance, dict):
        raise CompilationError(f"{label}: missing provenance")
    for key in ("created_by", "created_at", "review_status", "version"):
        if key not in provenance:
            raise CompilationError(f"{label}: provenance missing {key}")


def validate_graph(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    require_provenance(graph, graph.get("id", "knowledge graph"))
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise CompilationError("knowledge graph: nodes and edges must be arrays")

    node_index: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_id = node.get("id")
        if not node_id or node_id in node_index:
            raise CompilationError(f"knowledge graph: duplicate or missing node id {node_id!r}")
        if node.get("type") not in ALLOWED_NODE_TYPES:
            raise CompilationError(f"{node_id}: unsupported node type {node.get('type')!r}")
        require_provenance(node, node_id)
        node_index[node_id] = node

    edge_ids: set[str] = set()
    for edge in edges:
        edge_id = edge.get("id")
        if not edge_id or edge_id in edge_ids:
            raise CompilationError(f"knowledge graph: duplicate or missing edge id {edge_id!r}")
        edge_ids.add(edge_id)
        if edge.get("from") not in node_index or edge.get("to") not in node_index:
            raise CompilationError(f"{edge_id}: unresolved edge reference")
        require_provenance(edge, edge_id)
        source = node_index[edge["from"]]
        target = node_index[edge["to"]]
        if source["type"] == "Hypothesis" and target["type"] == "QuestionTemplate":
            raise CompilationError(f"{edge_id}: Hypothesis must not generate QuestionTemplate")
    return node_index


def walk_values(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key, item
            yield from walk_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_values(item)


def validate_rules(
    rule_graph: dict[str, Any],
    node_index: dict[str, dict[str, Any]],
    production: bool,
) -> list[dict[str, Any]]:
    require_provenance(rule_graph, rule_graph.get("id", "rule graph"))
    rules = rule_graph.get("rules")
    if not isinstance(rules, list):
        raise CompilationError("rule graph: rules must be an array")

    rule_ids: set[str] = set()
    for rule in rules:
        rule_id = rule.get("id")
        if not rule_id or rule_id in rule_ids:
            raise CompilationError(f"rule graph: duplicate or missing rule id {rule_id!r}")
        rule_ids.add(rule_id)
        if rule.get("type") not in ALLOWED_RULE_TYPES:
            raise CompilationError(f"{rule_id}: unsupported rule type")
        require_provenance(rule, rule_id)
        for key, value in walk_values({"when": rule.get("when"), "then": rule.get("then")}):
            if key in {"fact", "target", "rfe"} and isinstance(value, str):
                if value not in node_index:
                    raise CompilationError(f"{rule_id}: unresolved {key} reference {value}")
            if key == "activate_intents" and isinstance(value, list):
                missing = [item for item in value if item not in node_index]
                if missing:
                    raise CompilationError(f"{rule_id}: unresolved intent references {missing}")
        if production and rule.get("type") == "safety":
            review = rule["provenance"].get("review_status")
            if review != "reviewed" or rule.get("status") != "enabled":
                raise CompilationError(
                    f"{rule_id}: production safety rule must be reviewed and enabled"
                )
    return sorted(rules, key=lambda item: (-item["priority"], item["id"]))


def validate_sources(manifest: dict[str, Any], production: bool) -> None:
    require_provenance(manifest, manifest.get("id", "source manifest"))
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise CompilationError("source manifest: artifacts must not be empty")
    for artifact in artifacts:
        for key in ("id", "kind", "version", "digest", "license_status"):
            if key not in artifact:
                raise CompilationError(f"source artifact missing {key}")
        if production and artifact["license_status"] not in {"allowed", "restricted"}:
            raise CompilationError(
                f"{artifact['id']}: production source license status is not acceptable"
            )
        if production and not artifact.get("complete", False):
            raise CompilationError(f"{artifact['id']}: production source is incomplete")


def path_digest(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.read_bytes())
    elif path.is_dir():
        for item in sorted(candidate for candidate in path.rglob("*") if candidate.is_file()):
            if "__pycache__" in item.parts:
                continue
            digest.update(str(item.relative_to(path)).encode("utf-8"))
            digest.update(b"\0")
            digest.update(item.read_bytes())
            digest.update(b"\0")
    else:
        raise CompilationError(f"source artifact path does not exist: {path}")
    return "sha256:" + digest.hexdigest()


def materialize_source_digests(manifest: dict[str, Any]) -> dict[str, Any]:
    resolved = deepcopy(manifest)
    for artifact in resolved["artifacts"]:
        source_path = ROOT / artifact["path"]
        artifact["digest"] = path_digest(source_path)
    return resolved


def simulation_metadata(
    simulation_root: Path, simulation_glob: str = "**/*.json"
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in sorted(simulation_root.glob(simulation_glob)):
        data = load_json(path)
        require_provenance(data, data.get("id", str(path.relative_to(ROOT))))
        result.append({
            "id": data["id"],
            "path": str(path.relative_to(ROOT)),
            "expected": data.get("expected", {}),
            "provenance": data["provenance"],
        })
    if not result:
        raise CompilationError("no JSON simulations available")
    return result


def build_indexes(
    node_index: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
) -> dict[str, Any]:
    questions: dict[str, dict[str, Any]] = {}
    target_facts: dict[str, list[str]] = {}
    intent_targets: dict[str, list[str]] = {}
    for edge in edges:
        if edge["type"] == "COLLECTS":
            q = node_index[edge["from"]]
            questions[edge["to"]] = {
                "template_id": q["id"],
                "wording": q["wording"],
                "language": q.get("language", "en"),
                "mode": q.get("mode", []),
            }
        elif edge["type"] == "REQUIRES":
            target_facts.setdefault(edge["from"], []).append(edge["to"])
        elif edge["type"] == "GENERATES":
            intent_targets.setdefault(edge["from"], []).append(edge["to"])
    return {
        "questions_by_fact": {key: questions[key] for key in sorted(questions)},
        "target_facts": {key: sorted(value) for key, value in sorted(target_facts.items())},
        "intent_targets": {key: sorted(value) for key, value in sorted(intent_targets.items())},
    }


def coverage(
    node_index: dict[str, dict[str, Any]],
    indexes: dict[str, Any],
    simulations: list[dict[str, Any]],
    rules: list[dict[str, Any]],
) -> dict[str, Any]:
    by_type: dict[str, int] = {}
    for node in node_index.values():
        by_type[node["type"]] = by_type.get(node["type"], 0) + 1
    fact_ids = {node["id"] for node in node_index.values() if node["type"] == "Fact"}
    question_facts = set(indexes["questions_by_fact"])
    target_ids = {node["id"] for node in node_index.values() if node["type"] == "InterviewTarget"}
    linked_targets = set(indexes["target_facts"])
    safety_rules = {rule["id"] for rule in rules if rule["type"] == "safety"}
    simulated_safety_rules = {
        rule_id
        for simulation in simulations
        for rule_id in simulation.get("expected", {}).get(
            "expected_triggered_rules_contains", []
        )
    }
    data_absent_simulations = sum(
        bool(simulation.get("expected", {}).get("expected_data_absent_reasons"))
        for simulation in simulations
    )
    return {
        "node_counts": dict(sorted(by_type.items())),
        "facts_with_questions": len(fact_ids & question_facts),
        "total_facts": len(fact_ids),
        "required_targets_linked_to_facts": len(target_ids & linked_targets),
        "total_targets": len(target_ids),
        "simulation_count": len(simulations),
        "total_safety_rules": len(safety_rules),
        "safety_rules_with_simulations": len(safety_rules & simulated_safety_rules),
        "uncovered_safety_rules": sorted(safety_rules - simulated_safety_rules),
        "data_absent_reason_simulations": data_absent_simulations,
        "reviewed_for_production": False,
        "known_gaps": [
            "External guideline artifacts are not cached or license-verified.",
            "Clinical and safety review is incomplete.",
            "Simulation set is below release coverage requirements.",
        ],
    }


def semantic_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def compile_package(
    graph_path: Path | None = None,
    rules_path: Path | None = None,
    sources_path: Path | None = None,
    production: bool = False,
    profile: str = "cough",
) -> dict[str, Any]:
    if profile not in PACKAGE_PROFILES:
        raise CompilationError(f"unknown package profile: {profile}")
    config = PACKAGE_PROFILES[profile]
    graph_path = graph_path or config["graph"]
    rules_path = rules_path or config["rules"]
    sources_path = sources_path or config["sources"]
    graph = load_json(graph_path)
    rule_graph = load_json(rules_path)
    sources = materialize_source_digests(load_json(sources_path))
    completion_policy = load_json(config["completion_policy"])
    node_index = validate_graph(graph)
    sorted_rules = validate_rules(rule_graph, node_index, production)
    validate_sources(sources, production)
    simulations = simulation_metadata(
        config["simulation_root"], config.get("simulation_glob", "**/*.json")
    )
    indexes = build_indexes(node_index, graph["edges"])
    all_fact_ids = {
        node_id for node_id, node in node_index.items() if node["type"] == "Fact"
    }
    for fact_ids in completion_policy.get("required_facts", {}).values():
        missing = set(fact_ids) - all_fact_ids
        if missing:
            raise CompilationError(f"completion policy has unresolved Facts: {sorted(missing)}")
    for rule_id, fact_ids in completion_policy.get("clarification_facts_by_rule", {}).items():
        if rule_id not in {rule["id"] for rule in sorted_rules}:
            raise CompilationError(f"completion policy has unresolved Rule: {rule_id}")
        missing = set(fact_ids) - all_fact_ids
        if missing:
            raise CompilationError(f"completion policy has unresolved Facts: {sorted(missing)}")

    package: dict[str, Any] = {
        "package_id": config["package_id"],
        "package_version": config["package_version"],
        "release_state": "draft",
        "usage_policy": {
            "allowed_modes": ["research_test", "simulation"],
            "production_allowed": False,
            "unreviewed_knowledge_allowed": True,
            "overdue_research_behavior": "allow_with_warning",
        },
        "scope": {
            "care_domain": "primary_care",
            "encounter_contexts": ["context.primary_care"],
            "reasons_for_encounter": [config["rfe"]],
            "production_enabled": production,
        },
        "knowledge_graph": graph,
        "rule_graph": {**rule_graph, "rules": sorted_rules},
        "indexes": indexes,
        "source_manifest": sources,
        "research_source_manifests": [
            load_json(path) for path in config["research_manifests"]
        ],
        "refresh_policy": load_json(ROOT / "policies/knowledge-refresh.json"),
        "interview_completion_policy": completion_policy,
        "simulations": simulations,
        "coverage": coverage(node_index, indexes, simulations, sorted_rules),
        "compatibility": {
            "runtime_min": "0.1.0",
            "runtime_max_tested": "0.1.0",
            "rule_language": "0.1.0",
            "clinical_memory_schema": "0.2.0",
        },
        "provenance": {
            "created_by": {"type": "compiler", "id": "compiler.build_package"},
            "created_at": os.environ.get("SOURCE_DATE_EPOCH_ISO", "2026-07-13T00:00:00Z"),
            "source_refs": [
                str(graph_path.relative_to(ROOT)),
                str(rules_path.relative_to(ROOT)),
                str(sources_path.relative_to(ROOT)),
            ],
            "review_status": "unreviewed",
            "version": "0.1.0",
        },
    }
    package["semantic_digest"] = semantic_digest(package)
    return package


def write_package(package: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(output)


def validate_package(package: dict[str, Any]) -> None:
    digest = package.get("semantic_digest")
    unsigned = {key: value for key, value in package.items() if key != "semantic_digest"}
    expected = semantic_digest(unsigned)
    if digest != expected:
        raise CompilationError("package semantic digest mismatch")
    graph = package.get("knowledge_graph")
    rules = package.get("rule_graph")
    if not isinstance(graph, dict) or not isinstance(rules, dict):
        raise CompilationError("package missing graph")
    node_index = validate_graph(graph)
    validate_rules(rules, node_index, bool(package.get("scope", {}).get("production_enabled")))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=sorted(PACKAGE_PROFILES), default="cough")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--production", action="store_true")
    parser.add_argument("--validate", type=Path)
    args = parser.parse_args()

    if args.validate:
        validate_package(load_json(args.validate.resolve()))
        print(f"PACKAGE VALID: {args.validate}")
        return

    package = compile_package(production=args.production, profile=args.profile)
    output = (args.output or PACKAGE_PROFILES[args.profile]["output"]).resolve()
    write_package(package, output)
    print(
        f"PACKAGE BUILT: {output} "
        f"({package['semantic_digest']}, "
        f"{package['coverage']['simulation_count']} simulations)"
    )


if __name__ == "__main__":
    main()
