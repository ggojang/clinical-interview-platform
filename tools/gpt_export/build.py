#!/usr/bin/env python3
"""Build deterministic public GPT resources from repository knowledge."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


VERSION = "0.1.0"
GENERATED_AT = "2026-07-14T00:00:00Z"
PRIVATE_KEYS = {
    "raw_text", "raw_input", "patient_response", "patient_responses",
    "questionnaire_response", "conversation", "transcript", "evidence",
}
COMPACT_DROP_KEYS = {
    "provenance", "refresh", "source_manifest", "usage_modes", "version",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: sanitize(item)
            for key, item in sorted(value.items())
            if key.lower() not in PRIVATE_KEYS
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def quality(item: dict[str, Any]) -> tuple[int, int]:
    """Prefer the richest duplicate and then use stable JSON ordering."""
    encoded = json.dumps(item, ensure_ascii=False, sort_keys=True)
    return len(item), len(encoded)


def deduplicate(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: dict[str, dict[str, Any]] = {}
    for item in items:
        identifier = item.get("id")
        if not identifier:
            continue
        clean = sanitize(item)
        if identifier not in selected or quality(clean) > quality(selected[identifier]):
            selected[identifier] = clean
    return [selected[key] for key in sorted(selected)]


def envelope(resource_type: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "resource_type": resource_type,
        "version": VERSION,
        "status": "research_only",
        "review_status": "unreviewed",
        "usage_modes": ["research_test", "simulation"],
        "contains_patient_responses": False,
        "generated_at": GENERATED_AT,
        "count": len(items),
        "items": items,
    }


def compact(value: Any) -> Any:
    """Remove repeated build metadata while preserving runtime semantics."""
    if isinstance(value, dict):
        return {
            key: compact(item)
            for key, item in sorted(value.items())
            if key not in COMPACT_DROP_KEYS and key.lower() not in PRIVATE_KEYS
        }
    if isinstance(value, list):
        return [compact(item) for item in value]
    return value


def rfe_resource(
    resource_type: str,
    rfe_id: str,
    package: dict[str, Any],
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "resource_type": resource_type,
        "version": VERSION,
        "status": "research_only",
        "review_status": "unreviewed",
        "usage_modes": ["research_test", "simulation"],
        "contains_patient_responses": False,
        "generated_at": GENERATED_AT,
        "reason_for_encounter": rfe_id,
        "encounter_contexts": package.get("scope", {}).get("encounter_contexts", []),
        "package_id": package.get("package_id"),
        "package_version": package.get("package_version"),
        "count": len(items),
        "items": [compact(item) for item in items],
    }


def collect_rfe_resources(root: Path) -> dict[str, dict[str, Any]]:
    resources: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "packages" / "generated").glob("*.json")):
        package = load_json(path)
        reasons = package.get("scope", {}).get("reasons_for_encounter", [])
        if len(reasons) != 1:
            continue
        rfe_id = reasons[0]
        slug = rfe_id.removeprefix("rfe.")
        nodes = package.get("knowledge_graph", {}).get("nodes", [])
        facts = [node for node in nodes if node.get("type") == "Fact"]
        questions = [node for node in nodes if node.get("type") == "QuestionTemplate"]
        rules = package.get("rule_graph", {}).get("rules", [])
        resources[f"rfe/{slug}/facts.json"] = rfe_resource(
            "ReasonForEncounterFactCollection", rfe_id, package, facts
        )
        resources[f"rfe/{slug}/questions.json"] = rfe_resource(
            "ReasonForEncounterQuestionCollection", rfe_id, package, questions
        )
        resources[f"rfe/{slug}/rules.json"] = rfe_resource(
            "ReasonForEncounterRuleCollection", rfe_id, package, rules
        )
    return resources


def collect(root: Path) -> dict[str, dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    questions: list[dict[str, Any]] = []
    rules: list[dict[str, Any]] = []
    screening: dict[str, Any] | None = None

    for path in sorted((root / "knowledge").rglob("*.json")):
        document = load_json(path)
        if not isinstance(document, dict):
            continue
        if path.name == "kr-national-health-screening-2026.json":
            screening = sanitize(document)
        for node in document.get("nodes", []):
            if not isinstance(node, dict):
                continue
            if node.get("type") == "Fact":
                facts.append(node)
            elif node.get("type") == "QuestionTemplate":
                questions.append(node)
        for fact in document.get("facts", []):
            if isinstance(fact, dict):
                facts.append(fact)
        for group in document.get("question_groups", []):
            if isinstance(group, dict):
                questions.append({**group, "type": "QuestionGroup"})
        for entry in document.get("entries", []):
            if not isinstance(entry, dict) or not entry.get("question"):
                continue
            questions.append({
                "id": f"generated.question.{entry.get('target', entry.get('fact', 'unknown'))}",
                "type": "QuestionTemplate",
                "fact_id": entry.get("fact"),
                "target_id": entry.get("target"),
                "text": entry.get("question"),
                "priority": entry.get("priority"),
                "supports": entry.get("supports", []),
                "status": document.get("status", "research_only"),
                "provenance": document.get("provenance", {}),
            })
        for rule in document.get("safety_rules", []):
            if isinstance(rule, dict):
                rules.append({
                    **rule,
                    "status": document.get("status", "research_only"),
                    "provenance": document.get("provenance", {}),
                })

    for path in sorted((root / "rules").rglob("*.json")):
        document = load_json(path)
        if not isinstance(document, dict):
            continue
        for rule in document.get("rules", []):
            if isinstance(rule, dict):
                rules.append(rule)

    if screening is None:
        raise RuntimeError("Korean screening knowledge is missing")
    if screening.get("status") != "research_only" or screening.get("review_status") != "unreviewed":
        raise RuntimeError("Screening knowledge must remain research_only/unreviewed")

    screening["contains_patient_responses"] = False
    catalog = sanitize(load_json(root / "knowledge" / "catalog" / "primary-care-rfe.json"))
    catalog["resource_type"] = "ReasonForEncounterCatalog"
    catalog["review_status"] = "unreviewed"
    catalog["usage_modes"] = ["research_test", "simulation"]
    catalog["contains_patient_responses"] = False
    resources = {
        "reason-for-encounters.json": catalog,
        "facts.json": envelope("FactCollection", deduplicate(facts)),
        "question-groups.json": envelope("QuestionCollection", deduplicate(questions)),
        "safety-rules.json": envelope("SafetyRuleCollection", deduplicate(rules)),
        "screening-kr.json": screening,
    }
    resources.update(collect_rfe_resources(root))
    return resources


def encoded(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def build(root: Path, output: Path) -> dict[str, Any]:
    resources = collect(root)
    output.mkdir(parents=True, exist_ok=True)
    manifest_resources = []
    for name, document in sorted(resources.items()):
        payload = encoded(document)
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        manifest_resources.append({
            "name": name.removesuffix(".json").replace("/", "-"),
            "path": f"/gpt/{name}",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "count": document.get(
                "count",
                len(document.get("entries", document.get("question_groups", []))),
            ),
        })
    manifest = {
        "id": "clinical-interview-platform.gpt-manifest",
        "version": VERSION,
        "generated_at": GENERATED_AT,
        "status": "research_only",
        "review_status": "unreviewed",
        "contains_patient_responses": False,
        "resources": manifest_resources,
    }
    (output / "manifest.json").write_bytes(encoded(manifest))
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="docs/gpt")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    manifest = build(root, output)
    print(f"Built {len(manifest['resources'])} public GPT resources in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
