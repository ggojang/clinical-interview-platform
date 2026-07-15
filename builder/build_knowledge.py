"""Merge research-only knowledge fragments into canonical graph sources.

The Builder is deterministic. It reuses existing Facts only when a fragment
explicitly declares reuse_existing=true, and it never promotes review status.
"""
from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SHARED_FACTS = ROOT / "knowledge/shared/primary-care-facts.json"
PROFILES = {
    "cough": {
        "base_graph": ROOT / "knowledge/base/primary-care-cough.json",
        "base_rules": ROOT / "rules/base/primary-care-cough.json",
        "fragment_root": ROOT / "knowledge/generated/respiratory",
        "fragment_glob": "cough-expansion.json",
        "output_graph": ROOT / "knowledge/graph/primary-care-cough.json",
        "output_rules": ROOT / "rules/primary-care-cough.json",
        "version": "0.2.0",
    },
    "fever": {
        "base_graph": ROOT / "knowledge/base/primary-care-fever.json",
        "base_rules": ROOT / "rules/base/primary-care-fever.json",
        "fragment_root": ROOT / "knowledge/generated/systemic",
        "output_graph": ROOT / "knowledge/graph/primary-care-fever.json",
        "output_rules": ROOT / "rules/primary-care-fever.json",
        "version": "0.1.0",
    },
    "dyspnea": {
        "base_graph": ROOT / "knowledge/base/primary-care-dyspnea.json",
        "base_rules": ROOT / "rules/base/primary-care-dyspnea.json",
        "fragment_root": ROOT / "knowledge/generated/respiratory/dyspnea",
        "output_graph": ROOT / "knowledge/graph/primary-care-dyspnea.json",
        "output_rules": ROOT / "rules/primary-care-dyspnea.json",
        "version": "0.1.0",
    },
    "abdominal_pain": {
        "base_graph": ROOT / "knowledge/base/primary-care-abdominal-pain.json",
        "base_rules": ROOT / "rules/base/primary-care-abdominal-pain.json",
        "fragment_root": ROOT / "knowledge/generated/gastrointestinal/abdominal-pain",
        "output_graph": ROOT / "knowledge/graph/primary-care-abdominal-pain.json",
        "output_rules": ROOT / "rules/primary-care-abdominal-pain.json",
        "version": "0.1.0",
    },
    "chest_pain": {
        "base_graph": ROOT / "knowledge/base/primary-care-chest-pain.json",
        "base_rules": ROOT / "rules/base/primary-care-chest-pain.json",
        "fragment_root": ROOT / "knowledge/generated/cardiovascular/chest-pain",
        "output_graph": ROOT / "knowledge/graph/primary-care-chest-pain.json",
        "output_rules": ROOT / "rules/primary-care-chest-pain.json",
        "version": "0.1.0",
    },
    "headache": {
        "base_graph": ROOT / "knowledge/base/primary-care-headache.json",
        "base_rules": ROOT / "rules/base/primary-care-headache.json",
        "fragment_root": ROOT / "knowledge/generated/neurological/headache",
        "output_graph": ROOT / "knowledge/graph/primary-care-headache.json",
        "output_rules": ROOT / "rules/primary-care-headache.json",
        "version": "0.1.0",
    },
    "dizziness_syncope": {
        "base_graph": ROOT / "knowledge/base/primary-care-dizziness-syncope.json",
        "base_rules": ROOT / "rules/base/primary-care-dizziness-syncope.json",
        "fragment_root": ROOT / "knowledge/generated/neurological/dizziness-syncope",
        "output_graph": ROOT / "knowledge/graph/primary-care-dizziness-syncope.json",
        "output_rules": ROOT / "rules/primary-care-dizziness-syncope.json",
        "version": "0.1.0",
    },
    "vomiting_diarrhea": {
        "base_graph": ROOT / "knowledge/base/primary-care-vomiting-diarrhea.json",
        "base_rules": ROOT / "rules/base/primary-care-vomiting-diarrhea.json",
        "fragment_root": ROOT / "knowledge/generated/gastrointestinal/vomiting-diarrhea",
        "output_graph": ROOT / "knowledge/graph/primary-care-vomiting-diarrhea.json",
        "output_rules": ROOT / "rules/primary-care-vomiting-diarrhea.json",
        "version": "0.1.0",
    },
    "urinary_symptoms": {
        "base_graph": ROOT / "knowledge/base/primary-care-urinary-symptoms.json",
        "base_rules": ROOT / "rules/base/primary-care-urinary-symptoms.json",
        "fragment_root": ROOT / "knowledge/generated/genitourinary/urinary-symptoms",
        "output_graph": ROOT / "knowledge/graph/primary-care-urinary-symptoms.json",
        "output_rules": ROOT / "rules/primary-care-urinary-symptoms.json",
        "version": "0.1.0",
    },
    "fatigue": {
        "base_graph": ROOT / "knowledge/base/primary-care-fatigue.json",
        "base_rules": ROOT / "rules/base/primary-care-fatigue.json",
        "fragment_root": ROOT / "knowledge/generated/systemic/fatigue",
        "output_graph": ROOT / "knowledge/graph/primary-care-fatigue.json",
        "output_rules": ROOT / "rules/primary-care-fatigue.json",
        "version": "0.1.0",
    },
    "back_pain": {
        "base_graph": ROOT / "knowledge/base/primary-care-back-pain.json",
        "base_rules": ROOT / "rules/base/primary-care-back-pain.json",
        "fragment_root": ROOT / "knowledge/generated/musculoskeletal/back-pain",
        "output_graph": ROOT / "knowledge/graph/primary-care-back-pain.json",
        "output_rules": ROOT / "rules/primary-care-back-pain.json",
        "version": "0.1.0",
    },
    "skin_complaint": {
        "base_graph": ROOT / "knowledge/base/primary-care-skin-complaint.json",
        "base_rules": ROOT / "rules/base/primary-care-skin-complaint.json",
        "fragment_root": ROOT / "knowledge/generated/dermatological/skin-complaint",
        "output_graph": ROOT / "knowledge/graph/primary-care-skin-complaint.json",
        "output_rules": ROOT / "rules/primary-care-skin-complaint.json",
        "version": "0.1.0",
    },
    "medication_review": {
        "base_graph": ROOT / "knowledge/base/primary-care-medication-review.json",
        "base_rules": ROOT / "rules/base/primary-care-medication-review.json",
        "fragment_root": ROOT / "knowledge/generated/medication/medication-review",
        "output_graph": ROOT / "knowledge/graph/primary-care-medication-review.json",
        "output_rules": ROOT / "rules/primary-care-medication-review.json",
        "version": "0.1.0",
    },
    "upper_respiratory_symptoms": {
        "base_graph": ROOT / "knowledge/base/primary-care-upper-respiratory-symptoms.json",
        "base_rules": ROOT / "rules/base/primary-care-upper-respiratory-symptoms.json",
        "fragment_root": ROOT / "knowledge/generated/upper-respiratory",
        "output_graph": ROOT / "knowledge/graph/primary-care-upper-respiratory-symptoms.json",
        "output_rules": ROOT / "rules/primary-care-upper-respiratory-symptoms.json",
        "version": "0.1.0",
    },
    "palpitations": {
        "base_graph": ROOT / "knowledge/base/primary-care-palpitations.json",
        "base_rules": ROOT / "rules/base/primary-care-palpitations.json",
        "fragment_root": ROOT / "knowledge/generated/cardiovascular/palpitations",
        "output_graph": ROOT / "knowledge/graph/primary-care-palpitations.json",
        "output_rules": ROOT / "rules/primary-care-palpitations.json",
        "version": "0.1.0",
    },
    "bowel_symptoms": {
        "base_graph": ROOT / "knowledge/base/primary-care-bowel-symptoms.json",
        "base_rules": ROOT / "rules/base/primary-care-bowel-symptoms.json",
        "fragment_root": ROOT / "knowledge/generated/gastrointestinal/bowel-symptoms",
        "output_graph": ROOT / "knowledge/graph/primary-care-bowel-symptoms.json",
        "output_rules": ROOT / "rules/primary-care-bowel-symptoms.json",
        "version": "0.1.0",
    },
    "focal_weakness_numbness": {
        "base_graph": ROOT / "knowledge/base/primary-care-focal-weakness-numbness.json",
        "base_rules": ROOT / "rules/base/primary-care-focal-weakness-numbness.json",
        "fragment_root": ROOT / "knowledge/generated/neurological/focal-weakness-numbness",
        "output_graph": ROOT / "knowledge/graph/primary-care-focal-weakness-numbness.json",
        "output_rules": ROOT / "rules/primary-care-focal-weakness-numbness.json",
        "version": "0.1.0",
    },
    "joint_limb_complaint": {
        "base_graph": ROOT / "knowledge/base/primary-care-joint-limb.json",
        "base_rules": ROOT / "rules/base/primary-care-joint-limb.json",
        "fragment_root": ROOT / "knowledge/generated/musculoskeletal/joint-limb",
        "output_graph": ROOT / "knowledge/graph/primary-care-joint-limb.json",
        "output_rules": ROOT / "rules/primary-care-joint-limb.json", "version": "0.1.0",
    },
    "mental_health_sleep": {
        "base_graph": ROOT / "knowledge/base/primary-care-mental-health-sleep.json",
        "base_rules": ROOT / "rules/base/primary-care-mental-health-sleep.json",
        "fragment_root": ROOT / "knowledge/generated/mental-health/mental-health-sleep",
        "output_graph": ROOT / "knowledge/graph/primary-care-mental-health-sleep.json",
        "output_rules": ROOT / "rules/primary-care-mental-health-sleep.json", "version": "0.1.0",
    },
    "edema": {
        "base_graph": ROOT / "knowledge/base/primary-care-edema.json",
        "base_rules": ROOT / "rules/base/primary-care-edema.json",
        "fragment_root": ROOT / "knowledge/generated/cardiovascular/edema",
        "output_graph": ROOT / "knowledge/graph/primary-care-edema.json",
        "output_rules": ROOT / "rules/primary-care-edema.json", "version": "0.1.0",
    },
    "hypertension_follow_up": {
        "base_graph": ROOT / "knowledge/base/primary-care-hypertension-follow-up.json",
        "base_rules": ROOT / "rules/base/primary-care-hypertension-follow-up.json",
        "fragment_root": ROOT / "knowledge/generated/cardiovascular/hypertension-follow-up",
        "output_graph": ROOT / "knowledge/graph/primary-care-hypertension-follow-up.json",
        "output_rules": ROOT / "rules/primary-care-hypertension-follow-up.json",
        "version": "0.1.0",
    },
    "weight_constitutional_change": {
        "base_graph": ROOT / "knowledge/base/primary-care-weight-constitutional-change.json",
        "base_rules": ROOT / "rules/base/primary-care-weight-constitutional-change.json",
        "fragment_root": ROOT / "knowledge/generated/general/weight-constitutional-change",
        "output_graph": ROOT / "knowledge/graph/primary-care-weight-constitutional-change.json",
        "output_rules": ROOT / "rules/primary-care-weight-constitutional-change.json",
        "version": "0.1.0",
    },
    "reproductive_genital_symptoms": {
        "base_graph": ROOT / "knowledge/base/primary-care-reproductive-genital-symptoms.json",
        "base_rules": ROOT / "rules/base/primary-care-reproductive-genital-symptoms.json",
        "fragment_root": ROOT / "knowledge/generated/genitourinary/reproductive-genital-symptoms",
        "output_graph": ROOT / "knowledge/graph/primary-care-reproductive-genital-symptoms.json",
        "output_rules": ROOT / "rules/primary-care-reproductive-genital-symptoms.json",
        "version": "0.1.0",
    },
    "eye_symptoms": {
        "base_graph": ROOT / "knowledge/base/primary-care-eye-symptoms.json",
        "base_rules": ROOT / "rules/base/primary-care-eye-symptoms.json",
        "fragment_root": ROOT / "knowledge/generated/ophthalmic/eye-symptoms",
        "output_graph": ROOT / "knowledge/graph/primary-care-eye-symptoms.json",
        "output_rules": ROOT / "rules/primary-care-eye-symptoms.json",
        "version": "0.1.0",
    },
    "ear_hearing_symptoms": {
        "base_graph": ROOT / "knowledge/base/primary-care-ear-hearing-symptoms.json",
        "base_rules": ROOT / "rules/base/primary-care-ear-hearing-symptoms.json",
        "fragment_root": ROOT / "knowledge/generated/otologic/ear-hearing-symptoms",
        "output_graph": ROOT / "knowledge/graph/primary-care-ear-hearing-symptoms.json",
        "output_rules": ROOT / "rules/primary-care-ear-hearing-symptoms.json",
        "version": "0.1.0",
    },
    "diabetes_follow_up": {
        "base_graph": ROOT / "knowledge/base/primary-care-diabetes-follow-up.json",
        "base_rules": ROOT / "rules/base/primary-care-diabetes-follow-up.json",
        "fragment_root": ROOT / "knowledge/generated/endocrine/diabetes-follow-up",
        "output_graph": ROOT / "knowledge/graph/primary-care-diabetes-follow-up.json",
        "output_rules": ROOT / "rules/primary-care-diabetes-follow-up.json",
        "version": "0.1.0",
    },
    "oral_dental_symptoms": {
        "base_graph": ROOT / "knowledge/base/primary-care-oral-dental-symptoms.json",
        "base_rules": ROOT / "rules/base/primary-care-oral-dental-symptoms.json",
        "fragment_root": ROOT / "knowledge/generated/oral-dental/oral-dental-symptoms",
        "output_graph": ROOT / "knowledge/graph/primary-care-oral-dental-symptoms.json",
        "output_rules": ROOT / "rules/primary-care-oral-dental-symptoms.json",
        "version": "0.1.0",
    },
    "wound_minor_injury": {
        "base_graph": ROOT / "knowledge/base/primary-care-wound-minor-injury.json",
        "base_rules": ROOT / "rules/base/primary-care-wound-minor-injury.json",
        "fragment_root": ROOT / "knowledge/generated/injury/wound-minor-injury",
        "output_graph": ROOT / "knowledge/graph/primary-care-wound-minor-injury.json",
        "output_rules": ROOT / "rules/primary-care-wound-minor-injury.json",
        "version": "0.1.0",
    },
}


class BuildError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    temporary.replace(path)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def add_node(
    nodes: dict[str, dict[str, Any]],
    node: dict[str, Any],
    provenance: dict[str, Any],
    fragment: dict[str, Any],
    allow_existing: bool = False,
) -> None:
    node_id = node["id"]
    if node_id in nodes:
        if allow_existing:
            if nodes[node_id]["type"] != node["type"]:
                raise BuildError(f"{node_id}: reuse type mismatch")
            return
        raise BuildError(f"{node_id}: duplicate node")
    nodes[node_id] = {
        **deepcopy(node),
        "version": fragment["version"],
        "status": "research_only",
        "usage_modes": fragment["usage_modes"],
        "source_manifest": fragment["source_manifest"],
        "provenance": deepcopy(provenance),
    }


def add_edge(
    edges: dict[str, dict[str, Any]],
    edge_type: str,
    source: str,
    target: str,
    provenance: dict[str, Any],
    fragment: dict[str, Any],
) -> None:
    edge_id = f"edge.generated.{slug(source)}.{edge_type.lower()}.{slug(target)}"
    if edge_id in edges:
        return
    edges[edge_id] = {
        "id": edge_id,
        "type": edge_type,
        "from": source,
        "to": target,
        "version": fragment["version"],
        "status": "research_only",
        "usage_modes": fragment["usage_modes"],
        "provenance": deepcopy(provenance),
    }


def priority_when(branch: str, target: str) -> dict[str, Any]:
    result: dict[str, Any] = {"target_state": {target: "active"}}
    if branch == "acute":
        result["duration_class"] = "acute"
    elif branch == "persistent":
        result["duration_class"] = {"in": ["subacute", "chronic"]}
    elif branch != "any":
        raise BuildError(f"unsupported priority branch: {branch}")
    return result


def merge_fragment(
    graph: dict[str, Any],
    rule_graph: dict[str, Any],
    fragment: dict[str, Any],
    shared_facts: dict[str, dict[str, Any]] | None = None,
    output_version: str = "0.2.0",
) -> dict[str, int]:
    if fragment.get("status") != "research_only":
        raise BuildError(f"{fragment.get('id')}: generated fragment must be research_only")
    if set(fragment.get("usage_modes", [])) - {"research_test", "simulation"}:
        raise BuildError(f"{fragment.get('id')}: generated fragment has forbidden usage mode")
    provenance = fragment.get("provenance", {})
    if provenance.get("review_status") != "unreviewed":
        raise BuildError(f"{fragment.get('id')}: generated fragment must be unreviewed")
    manifest_ids = {
        load(path).get("id")
        for path in (ROOT / "sources/manifests").glob("*.json")
    }
    if fragment.get("source_manifest") not in manifest_ids:
        raise BuildError(
            f"{fragment.get('id')}: unresolved Source Manifest "
            f"{fragment.get('source_manifest')!r}"
        )

    nodes = {node["id"]: node for node in graph["nodes"]}
    edges = {edge["id"]: edge for edge in graph["edges"]}
    rules = {rule["id"]: rule for rule in rule_graph["rules"]}
    before = (len(nodes), len(edges), len(rules))

    for extra in fragment.get("extra_nodes", []):
        add_node(nodes, extra, provenance, fragment, allow_existing=True)

    for source, target in fragment.get("group_hypothesis_edges", []):
        if source not in nodes or target not in nodes:
            raise BuildError(f"unresolved group-hypothesis edge: {source} -> {target}")
        add_edge(edges, "SUPPORTS", source, target, provenance, fragment)

    for safety in fragment.get("safety_rules", []):
        rule_id = safety["id"]
        if rule_id in rules:
            raise BuildError(f"duplicate generated rule: {rule_id}")
        rules[rule_id] = {
            "id": rule_id,
            "type": "safety",
            "priority": safety["priority"],
            "when": deepcopy(safety["when"]),
            "then": deepcopy(safety["then"]),
            "version": fragment["version"],
            "status": "research_only",
            "usage_modes": fragment["usage_modes"],
            "refresh": {
                "class": "safety_critical",
                "last_assessed_at": "2026-07-14",
                "next_monitor_at": "2026-07-15",
                "next_full_review_at": "2026-10-12",
                "policy_id": "policy.knowledge-refresh"
            },
            "provenance": deepcopy(provenance),
        }

    for entry in fragment.get("entries", []):
        fact = entry["fact"]
        refresh = fact.get("refresh", fragment.get("default_refresh", {}))
        for key in (
            "class", "last_assessed_at", "next_monitor_at",
            "next_full_review_at", "policy_id",
        ):
            if key not in refresh:
                raise BuildError(f"{fact.get('id')}: refresh metadata missing {key}")
        if not entry.get("question", {}).get("wording"):
            raise BuildError(f"{fact.get('id')}: Question Template is required")
        fact_node = {
            "id": fact["id"],
            "type": "Fact",
            "display": fact["display"],
            "description": fact.get("description", ""),
            "value_type": fact["value_type"],
            "extraction_cues": fact.get("extraction_cues", []),
            "safety_relevant": fact.get("safety_relevant", False),
            "refresh": refresh,
        }
        if fact.get("allowed_values") is not None:
            fact_node["allowed_values"] = fact["allowed_values"]
        for key in ("terminology_binding", "mrcm_validation"):
            if fact.get(key) is not None:
                fact_node[key] = deepcopy(fact[key])
        if (
            entry.get("reuse_existing")
            and fact["id"] not in nodes
            and shared_facts
            and fact["id"] in shared_facts
        ):
            nodes[fact["id"]] = deepcopy(shared_facts[fact["id"]])
        add_node(
            nodes, fact_node, provenance, fragment,
            allow_existing=bool(entry.get("reuse_existing")),
        )

        target = entry["target"]
        target_node = {
            "id": target["id"],
            "type": "InterviewTarget",
            "display": target["display"],
            "required_facts": [fact["id"]],
        }
        add_node(nodes, target_node, provenance, fragment)

        question = entry["question"]
        question_node = {
            "id": question["id"],
            "type": "QuestionTemplate",
            "display": question["wording"],
            "wording": question["wording"],
            "collects": fact["id"],
            "language": question["language"],
            "mode": question["mode"],
        }
        add_node(nodes, question_node, provenance, fragment)

        for intent in target["intents"]:
            if intent not in nodes:
                raise BuildError(f"{target['id']}: unresolved intent {intent}")
            add_edge(edges, "GENERATES", intent, target["id"], provenance, fragment)
        add_edge(edges, "REQUIRES", target["id"], fact["id"], provenance, fragment)
        add_edge(edges, "COLLECTS", question["id"], fact["id"], provenance, fragment)
        for group in entry.get("supports", []):
            if group not in nodes:
                raise BuildError(f"{fact['id']}: unresolved group {group}")
            add_edge(edges, "SUPPORTS", fact["id"], group, provenance, fragment)

        for priority in entry.get("priority", []):
            rule_id = (
                f"rule.generated.priority.{priority['branch']}."
                f"{target['id'].split('.')[-1]}"
            )
            if rule_id in rules:
                raise BuildError(f"duplicate generated rule: {rule_id}")
            rules[rule_id] = {
                "id": rule_id,
                "type": "priority",
                "priority": priority["score"],
                "when": priority_when(priority["branch"], target["id"]),
                "then": {
                    "target": target["id"],
                    "reason": priority["reason"],
                },
                "version": fragment["version"],
                "status": "research_only",
                "usage_modes": fragment["usage_modes"],
                "refresh": refresh,
                "provenance": deepcopy(provenance),
            }

        completion_id = f"rule.generated.complete.{target['id'].split('.')[-1]}"
        rules[completion_id] = {
            "id": completion_id,
            "type": "completion",
            "priority": 50,
            "when": {"target": target["id"], "facts_resolved": "all_required"},
            "then": {"target_state": "satisfied"},
            "version": fragment["version"],
            "status": "research_only",
            "usage_modes": fragment["usage_modes"],
            "refresh": refresh,
            "provenance": deepcopy(provenance),
        }

    graph["nodes"] = sorted(nodes.values(), key=lambda item: item["id"])
    graph["edges"] = sorted(edges.values(), key=lambda item: item["id"])
    rule_graph["rules"] = sorted(rules.values(), key=lambda item: item["id"])
    graph["version"] = output_version
    rule_graph["version"] = output_version
    after = (len(nodes), len(edges), len(rules))
    return {
        "nodes_added": after[0] - before[0],
        "edges_added": after[1] - before[1],
        "rules_added": after[2] - before[2],
    }


def build(profile: str = "cough") -> dict[str, Any]:
    if profile not in PROFILES:
        raise BuildError(f"unknown build profile: {profile}")
    config = PROFILES[profile]
    graph = load(config["base_graph"])
    rule_graph = load(config["base_rules"])
    shared_facts = {
        node["id"]: node for node in load(SHARED_FACTS).get("facts", [])
    } if SHARED_FACTS.exists() else {}
    reports = []
    fragment_paths = sorted(
        config["fragment_root"].rglob(config.get("fragment_glob", "*.json"))
    )
    if not fragment_paths:
        raise BuildError("no generated knowledge fragments")
    for path in fragment_paths:
        fragment = load(path)
        report = merge_fragment(
            graph, rule_graph, fragment, shared_facts, config["version"]
        )
        reports.append({
            "fragment": str(path.relative_to(ROOT)),
            **report,
        })
    write(config["output_graph"], graph)
    write(config["output_rules"], rule_graph)
    return {
        "builder_id": "builder.build_knowledge",
        "version": "0.1.0",
        "profile": profile,
        "fragments": reports,
        "graph": {
            "nodes": len(graph["nodes"]),
            "edges": len(graph["edges"]),
            "version": graph["version"],
        },
        "rules": {
            "count": len(rule_graph["rules"]),
            "version": rule_graph["version"],
        },
        "review_status": "unreviewed",
        "usage_modes": ["research_test", "simulation"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--profile", choices=sorted(PROFILES), default="cough")
    args = parser.parse_args()
    report = build(args.profile)
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.report:
        write(args.report.resolve(), report)
    print(rendered, end="")


if __name__ == "__main__":
    main()
