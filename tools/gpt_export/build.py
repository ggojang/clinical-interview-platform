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
    return {
        "facts.json": envelope("FactCollection", deduplicate(facts)),
        "question-groups.json": envelope("QuestionCollection", deduplicate(questions)),
        "safety-rules.json": envelope("SafetyRuleCollection", deduplicate(rules)),
        "screening-kr.json": screening,
    }


def encoded(document: dict[str, Any]) -> bytes:
    return (json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def build(root: Path, output: Path) -> dict[str, Any]:
    resources = collect(root)
    output.mkdir(parents=True, exist_ok=True)
    manifest_resources = []
    for name, document in sorted(resources.items()):
        payload = encoded(document)
        (output / name).write_bytes(payload)
        manifest_resources.append({
            "name": name.removesuffix(".json"),
            "path": f"/gpt/{name}",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "count": document.get("count", len(document.get("question_groups", []))),
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
