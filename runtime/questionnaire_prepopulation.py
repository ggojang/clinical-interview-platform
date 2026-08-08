"""FHIR R4 QuestionnaireResponse prepopulation from verified atomic Facts."""
from __future__ import annotations

from copy import deepcopy
import json
from typing import Any


PROVENANCE_EXTENSION = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "StructureDefinition/questionnaire-prepopulation-provenance"
)
AUTOMATIC_RELATIONS = {"exact", "equivalent"}


def _walk_items(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        link_id = item.get("linkId")
        if not link_id:
            raise ValueError("every Questionnaire item requires linkId")
        if link_id in result:
            raise ValueError(f"duplicate Questionnaire linkId: {link_id}")
        result[link_id] = item
        result.update(_walk_items(item.get("item", [])))
    return result


def _answer(item: dict[str, Any], value: Any) -> dict[str, Any] | None:
    item_type = item.get("type")
    if item_type == "boolean" and isinstance(value, bool):
        return {"valueBoolean": value}
    if item_type == "integer" and isinstance(value, int) and not isinstance(value, bool):
        return {"valueInteger": value}
    if item_type == "decimal" and isinstance(value, (int, float)) and not isinstance(value, bool):
        return {"valueDecimal": value}
    if item_type in {"date", "dateTime", "time"} and isinstance(value, str):
        suffix = {"date": "Date", "dateTime": "DateTime", "time": "Time"}[item_type]
        return {f"value{suffix}": value}
    if item_type in {"string", "text", "url"} and isinstance(value, str):
        suffix = {"string": "String", "text": "String", "url": "Uri"}[item_type]
        return {f"value{suffix}": value}
    if item_type in {"choice", "open-choice"} and isinstance(value, dict):
        if value.get("system") and value.get("code"):
            coding = {
                key: deepcopy(value[key])
                for key in ("system", "version", "code", "display")
                if key in value
            }
            return {"valueCoding": coding}
    if item_type == "quantity" and isinstance(value, dict) and "value" in value:
        quantity = {
            key: deepcopy(value[key])
            for key in ("value", "unit", "system", "code")
            if key in value
        }
        return {"valueQuantity": quantity}
    return None


def prefill_questionnaire_response(
    questionnaire: dict[str, Any],
    facts: dict[str, dict[str, Any]],
    mapping: dict[str, Any],
    *,
    response_id: str = "prefill-preview",
) -> dict[str, Any]:
    """Return an in-progress QR preview and an auditable prepopulation report.

    Only exact/equivalent entries are automatic. Compound targets require every
    declared atomic source Fact to be known. The source Questionnaire is never
    modified and the caller must obtain user review before completion.
    """
    if questionnaire.get("resourceType") != "Questionnaire":
        raise ValueError("FHIR R4 Questionnaire is required")
    canonical = questionnaire.get("url")
    if not canonical:
        raise ValueError("Questionnaire canonical url is required")
    item_index = _walk_items(questionnaire.get("item", []))
    mapping_version = mapping.get("version")
    if not mapping_version or not mapping.get("provenance"):
        raise ValueError("mapping version and provenance are required")

    qr_items: list[dict[str, Any]] = []
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    seen_targets: set[str] = set()
    for entry in mapping.get("entries", []):
        target = entry.get("target_link_id")
        relation = entry.get("relation")
        source_ids = entry.get("source_fact_ids", [])
        if not target or target in seen_targets:
            raise ValueError("mapping target_link_id must be present and unique")
        seen_targets.add(target)
        if target not in item_index:
            raise ValueError(f"mapping target linkId not found: {target}")
        if relation not in AUTOMATIC_RELATIONS:
            skipped.append({"target_link_id": target, "reason": "relation_not_automatic"})
            continue
        if not source_ids:
            raise ValueError(f"mapping source_fact_ids missing for {target}")
        if any(facts.get(fact_id, {}).get("status") != "known" for fact_id in source_ids):
            skipped.append({"target_link_id": target, "reason": "source_fact_not_known"})
            continue
        value_fact_id = entry.get("value_fact_id", source_ids[0])
        if value_fact_id not in source_ids:
            raise ValueError("value_fact_id must be one of source_fact_ids")
        encoded = _answer(item_index[target], facts[value_fact_id].get("value"))
        if encoded is None:
            skipped.append({"target_link_id": target, "reason": "value_type_not_safe"})
            continue
        provenance = {
            "mapping_id": mapping.get("id"),
            "mapping_version": mapping_version,
            "relation": relation,
            "source_fact_ids": source_ids,
        }
        qr_items.append({
            "linkId": target,
            "answer": [encoded],
            "extension": [{
                "url": PROVENANCE_EXTENSION,
                "valueString": json.dumps(
                    provenance, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                ),
            }],
        })
        applied.append({"target_link_id": target, **provenance})

    questionnaire_ref = canonical
    if questionnaire.get("version"):
        questionnaire_ref += f"|{questionnaire['version']}"
    response = {
        "resourceType": "QuestionnaireResponse",
        "id": response_id,
        "questionnaire": questionnaire_ref,
        "status": "in-progress",
        "item": qr_items,
    }
    return {
        "questionnaire_response": response,
        "prepopulation_report": {
            "mapping_id": mapping.get("id"),
            "mapping_version": mapping_version,
            "requires_user_review": True,
            "automatic_completed_status": False,
            "applied": applied,
            "skipped": skipped,
        },
    }
