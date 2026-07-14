"""Reusable helpers for compact research-only Knowledge Package authoring seeds."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.1.0"
CREATED_AT = "2026-07-14T00:00:00Z"
QUESTION_MODES = ["chat", "face_to_face", "telephone", "video"]


def provenance(source_refs: list[str]) -> dict[str, Any]:
    return {
        "created_by": {"type": "ai", "id": "codex-gpt5"},
        "created_at": CREATED_AT,
        "source_refs": source_refs,
        "review_status": "unreviewed",
        "version": VERSION,
    }


def write_json(path: str, document: dict[str, Any]) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def default_refresh() -> dict[str, Any]:
    return {
        "class": "clinical_guideline",
        "last_assessed_at": "2026-07-14",
        "monitor_interval_days": 1,
        "full_review_interval_days": 180,
        "next_monitor_at": "2026-07-15",
        "next_full_review_at": "2027-01-10",
        "policy_id": "policy.knowledge-refresh",
        "overdue_behavior": {
            "production": "exclude_or_require_review",
            "research_test": "allow_with_warning",
        },
    }


def entry(
    prefix: str,
    fact_id: str,
    display: str,
    value_type: str,
    key: str,
    wording: str,
    score: int,
    reason: str,
    groups: list[str],
    *,
    intents: list[str],
    allowed_values: list[str] | None = None,
    safety_relevant: bool = False,
    reuse_existing: bool = False,
    terminology_binding: dict[str, Any] | None = None,
    mrcm_ref: str | None = None,
    mrcm_status: str = "provisional_pass",
) -> dict[str, Any]:
    fact: dict[str, Any] = {
        "id": fact_id,
        "display": display,
        "value_type": value_type,
    }
    if allowed_values:
        fact["allowed_values"] = allowed_values
    if safety_relevant:
        fact["safety_relevant"] = True
    if terminology_binding:
        fact["terminology_binding"] = terminology_binding
    if mrcm_ref:
        fact["mrcm_validation"] = {"ref": mrcm_ref, "status": mrcm_status}
    result: dict[str, Any] = {
        "fact": fact,
        "target": {
            "id": f"target.{prefix}.{key}",
            "display": display,
            "intents": intents,
        },
        "question": {
            "id": f"question.{prefix}.{key}",
            "wording": wording,
            "language": "ko",
            "mode": QUESTION_MODES,
        },
        "priority": [{"branch": "any", "score": score, "reason": reason}],
        "supports": groups,
    }
    if reuse_existing:
        result["reuse_existing"] = True
    return result


def safety_rule(
    prefix: str,
    key: str,
    condition: dict[str, Any],
    level: str,
    priority: int,
) -> dict[str, Any]:
    return {
        "id": f"rule.{prefix}.safety.{key}",
        "priority": priority,
        "when": condition,
        "then": {
            "safety_level": level,
            "action": "human_handoff",
            "suppress_routine": True,
        },
    }


def base_graph_and_rules(
    *,
    prefix: str,
    rfe: str,
    display: str,
    intents: list[tuple[str, str]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    nodes = [
        {
            "id": "context.primary_care", "type": "EncounterContext",
            "display": "Primary Care", "version": VERSION,
            "status": "research_only",
            "provenance": provenance(["docs/context/002-encounter-context.md"]),
        },
        {
            "id": rfe, "type": "ReasonForEncounter", "display": display,
            "version": VERSION, "status": "research_only",
            "provenance": provenance(["knowledge/catalog/primary-care-rfe.json"]),
        },
    ]
    nodes.extend({
        "id": identifier, "type": "ClinicalIntent", "display": intent_display,
        "version": VERSION, "status": "research_only",
        "provenance": provenance(["docs/context/001-clinical-intent.md"]),
    } for identifier, intent_display in intents)
    edges = [{
        "id": f"edge.{prefix}.000", "type": "ACTIVATES",
        "from": "context.primary_care", "to": intents[0][0],
        "version": VERSION,
        "provenance": provenance(["docs/context/002-encounter-context.md"]),
    }]
    edges.extend({
        "id": f"edge.{prefix}.{index:03d}", "type": "SUGGESTS",
        "from": rfe, "to": identifier, "version": VERSION,
        "provenance": provenance(["docs/context/001-clinical-intent.md"]),
    } for index, (identifier, _) in enumerate(intents, 1))
    graph = {
        "id": f"knowledge.primary-care-{prefix}", "version": VERSION,
        "nodes": nodes, "edges": edges,
        "provenance": provenance(["knowledge/catalog/primary-care-rfe.json"]),
    }
    rules = {
        "id": f"rules.primary-care-{prefix}", "version": VERSION,
        "rules": [{
            "id": f"rule.activate.{prefix}", "type": "activation", "priority": 100,
            "when": {"rfe": rfe},
            "then": {"activate_intents": [item[0] for item in intents]},
            "version": VERSION, "status": "research_only",
            "provenance": provenance(["specifications/reasoning-loop.md"]),
        }],
        "provenance": provenance(["specifications/reasoning-loop.md"]),
    }
    return graph, rules


def completion_policy(
    *, prefix: str, fragment: dict[str, Any], presentation_fact: str,
    question_budget: int, source_refs: list[str],
) -> dict[str, Any]:
    safety_facts: list[str] = []
    def collect(condition: dict[str, Any]) -> None:
        if "fact" in condition and condition["fact"] not in safety_facts:
            safety_facts.append(condition["fact"])
        for child in condition.get("all", []):
            collect(child)
    for item in fragment["safety_rules"]:
        collect(item["when"])
    fact_ids = [item["fact"]["id"] for item in fragment["entries"]]
    always = [presentation_fact, *[item for item in safety_facts if item != presentation_fact]]
    return {
        "id": f"policy.primary-care-{prefix}-completion", "version": VERSION,
        "status": "research_only",
        "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {
            "always": always,
            "routine": [item for item in fact_ids if item not in always],
        },
        "clarification_facts_by_rule": {},
        "question_budget": {"routine": question_budget, "clarify": 12},
        "provenance": provenance(source_refs),
    }
