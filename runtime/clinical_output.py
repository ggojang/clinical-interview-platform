"""Draft clinician note and FHIR projections for a completed adaptive interview.

The Knowledge Graph and compiled JSON packages remain the clinical source of
truth.  This module projects the in-memory conversation only after completion;
it never writes patient answers to disk and never promotes model output to
reviewed Knowledge.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
QUESTION_SYSTEM = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "CodeSystem/clinical-interview-question"
)
FACT_SYSTEM = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "CodeSystem/clinical-interview-fact"
)
SNOMED_SYSTEM = "http://snomed.info/sct"
YES_CODING = {"system": SNOMED_SYSTEM, "code": "373066001", "display": "Yes"}
NO_CODING = {"system": SNOMED_SYSTEM, "code": "373067005", "display": "No"}
DATA_ABSENT_REASON_URL = "http://hl7.org/fhir/StructureDefinition/data-absent-reason"
DATA_ABSENT_REASON_SYSTEM = (
    "http://terminology.hl7.org/CodeSystem/data-absent-reason"
)


def build_completed_clinical_outputs(
    *,
    session_id: str,
    reason_for_encounter: str,
    conversation: list[dict[str, str]],
    repository_root: Path = REPOSITORY_ROOT,
) -> dict[str, Any]:
    """Return a chart-style handoff plus draft R4 Questionnaire/QR/extraction.

    Values are patient-reported unless otherwise stated.  Standard codes are
    emitted only when the compiled source declares them; stable local codes are
    retained as the explicit fallback.
    """
    source = _source_index(reason_for_encounter, repository_root)
    responses = _response_rows(conversation, source)
    questionnaire = _questionnaire(session_id, reason_for_encounter, responses)
    questionnaire_response = _questionnaire_response(
        session_id, questionnaire, responses
    )
    extraction = _extraction_bundle(
        session_id, reason_for_encounter, responses
    )
    return {
        "clinical_handoff": _chart_note(reason_for_encounter, responses),
        "questionnaire": questionnaire,
        "questionnaire_response": questionnaire_response,
        "sdc_extraction": {
            "status": "draft_projection",
            "method": "completed_conversation_to_compiled_fact_projection",
            "review_required": True,
            "standard_codes_only_when_declared_by_compiled_knowledge": True,
            "bundle": extraction,
        },
    }


def _source_index(
    reason_for_encounter: str, repository_root: Path
) -> dict[str, dict[str, Any]]:
    slug = reason_for_encounter.removeprefix("rfe.")
    root = repository_root / "docs/gpt"
    question_document = json.loads(
        (root / "rfe" / slug / "questions.json").read_text(encoding="utf-8")
    )
    fact_document = json.loads(
        (root / "rfe" / slug / "facts.json").read_text(encoding="utf-8")
    )
    common_fact_document = json.loads(
        (root / "common-facts.json").read_text(encoding="utf-8")
    )
    context_document = json.loads(
        (root / "clinician-submission-context.json").read_text(encoding="utf-8")
    )
    questions = {
        item["id"]: deepcopy(item)
        for item in question_document.get("items", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for item in context_document.get("questions", []):
        template_id = item.get("template_id")
        if not isinstance(template_id, str):
            continue
        questions[template_id] = {
            **deepcopy(item),
            "id": template_id,
            "collects": item.get("fact_id"),
            "language": "ko",
            "type": "QuestionTemplate",
        }
    facts = {
        item["id"]: deepcopy(item)
        for document in (fact_document, common_fact_document)
        for item in document.get("items", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    return {"questions": questions, "facts": facts}


def _response_rows(
    conversation: list[dict[str, str]], source: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, item in enumerate(conversation[:-1]):
        if item.get("role") != "assistant":
            continue
        following = conversation[index + 1]
        if following.get("role") != "user":
            continue
        message = str(item.get("content", ""))
        question_ref = re.search(r"(?im)^\s*(?:\[)?Q(\d+)(?:\])?[.)：:]?", message)
        source_ids = re.findall(r"question\.[A-Za-z0-9_.-]+", message)
        source_id = next(
            (candidate for candidate in reversed(source_ids) if candidate in source["questions"]),
            source_ids[-1] if source_ids else None,
        )
        if question_ref is None or source_id is None:
            continue
        question = source["questions"].get(source_id, {"id": source_id})
        fact_id = question.get("collects") or question.get("fact_id")
        fact = source["facts"].get(fact_id, {"id": fact_id})
        raw_answer = str(following.get("content", "")).strip()
        display_answer = _visible_answer(message, raw_answer)
        rows.append({
            "question_ref": f"Q{question_ref.group(1)}",
            "question_id": source_id,
            "question": deepcopy(question),
            "fact_id": fact_id,
            "fact": deepcopy(fact),
            "raw_answer": raw_answer,
            "display_answer": display_answer,
            "data_absent_reason": _data_absent_reason(display_answer),
        })
    return rows


def _visible_answer(message: str, raw_answer: str) -> str:
    numeric = re.fullmatch(r"\s*(\d{1,2})(?:[.)])?\s*", raw_answer)
    if numeric is None:
        return raw_answer
    selected = numeric.group(1)
    for line in message.splitlines():
        option = re.fullmatch(r"\s*`?(\d{1,2})(?:[.)])?\s+(.+?)`?\s*", line)
        if option is not None and option.group(1) == selected:
            return option.group(2).strip().strip("*`")
    return raw_answer


def _data_absent_reason(answer: str) -> str | None:
    normalized = re.sub(r"\s+", "", answer.casefold())
    if normalized in {"잘모르겠음", "모름", "unknown"}:
        return "unknown"
    if normalized in {"답변하지않음", "응답거부", "declined"}:
        return "asked-declined"
    return None


def _questionnaire(
    session_id: str,
    reason_for_encounter: str,
    responses: list[dict[str, Any]],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for row in responses:
        question = row["question"]
        fact = row["fact"]
        item_type = _questionnaire_type(fact)
        item: dict[str, Any] = {
            "linkId": row["question_ref"],
            "text": _question_text(question, row["question_id"]),
            "type": item_type,
            "code": _question_codes(question, row["question_id"]),
            "extension": [{
                "url": (
                    "https://ggojang.github.io/clinical-interview-platform/fhir/"
                    "StructureDefinition/collected-fact-id"
                ),
                "valueString": row["fact_id"] or "unresolved",
            }],
        }
        answer_value_set = fact.get("answer_semantic_binding", {}).get(
            "answer_value_set"
        )
        if isinstance(answer_value_set, str) and item_type in {"choice", "open-choice"}:
            item["answerValueSet"] = answer_value_set
        items.append(item)
    return {
        "resourceType": "Questionnaire",
        "id": f"ciai-{session_id[:8]}",
        "url": (
            "https://ggojang.github.io/clinical-interview-platform/fhir/"
            f"Questionnaire/ciai-{session_id[:8]}"
        ),
        "version": "0.1.0",
        "status": "draft",
        "experimental": True,
        "title": f"Completed adaptive interview: {reason_for_encounter}",
        "subjectType": ["Patient"],
        "item": items,
    }


def _question_text(question: dict[str, Any], fallback: str) -> str:
    value = question.get("wording") or question.get("text")
    if isinstance(value, dict):
        value = value.get("ko") or value.get("en")
    return str(value or fallback)


def _question_codes(question: dict[str, Any], question_id: str) -> list[dict[str, Any]]:
    bindings = question.get("semantic_binding", {})
    declared = bindings.get("fhir_standard_item_codes", []) if isinstance(bindings, dict) else []
    codes = [
        {
            key: item[key]
            for key in ("system", "version", "code", "display")
            if key in item
        }
        for item in declared
        if isinstance(item, dict) and item.get("system") and item.get("code")
    ]
    if codes:
        return codes
    return [{"system": QUESTION_SYSTEM, "code": question_id}]


def _questionnaire_type(fact: dict[str, Any]) -> str:
    value_type = fact.get("value_type")
    if value_type == "boolean":
        return "choice"
    if value_type == "coded":
        return "open-choice"
    if value_type == "integer":
        return "integer"
    if value_type in {"decimal", "number"}:
        return "decimal"
    return "string"


def _questionnaire_response(
    session_id: str,
    questionnaire: dict[str, Any],
    responses: list[dict[str, Any]],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    for row, questionnaire_item in zip(responses, questionnaire["item"]):
        absent = row["data_absent_reason"]
        if absent:
            answer = {"extension": [{
                "url": DATA_ABSENT_REASON_URL,
                "valueCode": absent,
            }]}
        else:
            answer = _fhir_answer(row, questionnaire_item["type"])
        items.append({
            "linkId": row["question_ref"],
            "text": questionnaire_item["text"],
            "answer": [answer],
        })
    return {
        "resourceType": "QuestionnaireResponse",
        "id": f"ciai-response-{session_id[:8]}",
        "questionnaire": f"{questionnaire['url']}|{questionnaire['version']}",
        "status": "completed",
        "subject": {"reference": "Patient/subject"},
        "encounter": {"reference": "Encounter/interview"},
        "item": items,
    }


def _fhir_answer(row: dict[str, Any], item_type: str) -> dict[str, Any]:
    answer = row["display_answer"]
    normalized = re.sub(r"\s+", "", answer.casefold())
    if item_type == "choice":
        if normalized in {"예", "네", "yes", "y", "있음", "있어요"}:
            return {"valueCoding": deepcopy(YES_CODING)}
        if normalized in {"아니오", "아니요", "no", "n", "없음", "없어요"}:
            return {"valueCoding": deepcopy(NO_CODING)}
        return {"valueString": answer}
    if item_type == "integer" and re.fullmatch(r"-?\d+", answer):
        return {"valueInteger": int(answer)}
    if item_type == "decimal" and re.fullmatch(r"-?\d+(?:\.\d+)?", answer):
        return {"valueDecimal": float(answer)}
    return {"valueString": answer}


def _chart_note(
    reason_for_encounter: str, responses: list[dict[str, Any]]
) -> dict[str, Any]:
    sections: dict[str, list[dict[str, Any]]] = {
        "History of Present Illness": [],
        "Past Medical History": [],
        "Past Surgical History": [],
        "Medications": [],
        "Allergies": [],
        "Family History": [],
        "Social History": [],
        "Patient Concern / Expectation": [],
        "Additional Information": [],
    }
    missing: list[dict[str, str]] = []
    for row in responses:
        field = _chart_field(row["fact_id"], row["fact"])
        section = _chart_section(row["fact_id"])
        entry = {
            "field": field,
            "value": row["display_answer"],
            "fact_id": row["fact_id"],
            "question_id": row["question_id"],
            "source": "patient_report",
        }
        if row["data_absent_reason"]:
            entry["dataAbsentReason"] = row["data_absent_reason"]
            missing.append({
                "field": field,
                "dataAbsentReason": row["data_absent_reason"],
            })
        sections[section].append(entry)
    sections = {key: value for key, value in sections.items() if value}
    chief = reason_for_encounter.removeprefix("rfe.").replace("_", " / ")
    note_lines = [f"Chief Complaint: {chief}"]
    for section, entries in sections.items():
        note_lines.append(f"\n{section}:")
        note_lines.extend(f"- {item['field']}: {item['value']}" for item in entries)
    return {
        "format": "clinical_chart_note",
        "language": "English medical headings; patient-reported values preserved",
        "chief_complaint": chief,
        "sections": sections,
        "unconfirmed_or_absent": missing,
        "chart_note_text": "\n".join(note_lines),
        "diagnosis_inferred": False,
        "clinician_review_required": True,
    }


def _chart_section(fact_id: str | None) -> str:
    fact_id = fact_id or ""
    if fact_id.startswith("history.condition"):
        return "Past Medical History"
    if fact_id.startswith("history.procedure"):
        return "Past Surgical History"
    if fact_id.startswith("medication"):
        return "Medications"
    if fact_id.startswith("allergy"):
        return "Allergies"
    if fact_id.startswith("history.family"):
        return "Family History"
    if fact_id.startswith(("patient.smoking", "patient.alcohol", "occupation")):
        return "Social History"
    if "concern" in fact_id or "expectation" in fact_id:
        return "Patient Concern / Expectation"
    if "additional" in fact_id or fact_id.startswith("interview.final"):
        return "Additional Information"
    return "History of Present Illness"


def _chart_field(fact_id: str | None, fact: dict[str, Any]) -> str:
    fact_id = fact_id or "Unresolved fact"
    low = fact_id.casefold()
    labels = (
        (("onset",), "Onset"),
        (("severity", "nrs"), "Severity"),
        (("character", "presentation", "quality"), "Characteristic"),
        (("frequency",), "Frequency"),
        (("duration",), "Duration"),
        (("location", "site", "laterality"), "Location"),
        (("course", "trajectory", "trend"), "Course"),
        (("trigger", "aggravat"), "Trigger / Aggravating factor"),
        (("relief", "alleviat"), "Relieving factor"),
        (("impact", "function"), "Functional impact"),
    )
    for tokens, label in labels:
        if any(token in low for token in tokens):
            return label
    display = fact.get("display")
    return str(display) if isinstance(display, str) and display else fact_id


def _extraction_bundle(
    session_id: str,
    reason_for_encounter: str,
    responses: list[dict[str, Any]],
) -> dict[str, Any]:
    entries: list[dict[str, Any]] = [
        {"resource": {
            "resourceType": "Patient",
            "id": "subject",
            "meta": {"tag": [{"system": FACT_SYSTEM, "code": "synthetic-or-ephemeral"}]},
        }},
        {"resource": {
            "resourceType": "Encounter",
            "id": "interview",
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory",
            },
            "subject": {"reference": "Patient/subject"},
            "reasonCode": [{"coding": [{
                "system": FACT_SYSTEM,
                "code": reason_for_encounter,
            }]}],
        }},
    ]
    patient = entries[0]["resource"]
    for row in responses:
        if row["data_absent_reason"]:
            continue
        fact_id = row["fact_id"] or "unresolved"
        value = row["display_answer"]
        if fact_id == "patient.sex_for_clinical_care":
            normalized = value.casefold()
            if "female" in normalized or "여성" in value:
                patient["gender"] = "female"
            elif "male" in normalized or "남성" in value:
                patient["gender"] = "male"
            continue
        resource = _resource_for_fact(session_id, len(entries), row)
        entries.append({"resource": resource})
    return {
        "resourceType": "Bundle",
        "id": f"ciai-extraction-{session_id[:8]}",
        "type": "collection",
        "entry": entries,
    }


def _resource_for_fact(
    session_id: str, index: int, row: dict[str, Any]
) -> dict[str, Any]:
    fact_id = row["fact_id"] or "unresolved"
    value = row["display_answer"]
    fact = row["fact"]
    identifier = f"extracted-{session_id[:8]}-{index}"
    code = {"coding": _fact_codes(fact_id, fact), "text": value}
    common = {"id": identifier, "subject": {"reference": "Patient/subject"}}
    if fact_id.startswith("history.condition"):
        return {"resourceType": "Condition", **common, "code": code}
    if fact_id.startswith("history.procedure"):
        return {"resourceType": "Procedure", **common, "status": "unknown", "code": code}
    if fact_id.startswith("medication"):
        return {
            "resourceType": "MedicationStatement", **common,
            "status": "unknown", "medicationCodeableConcept": code,
        }
    if fact_id.startswith("allergy"):
        return {"resourceType": "AllergyIntolerance", **common, "code": code}
    if fact_id.startswith("history.family"):
        return {
            "resourceType": "FamilyMemberHistory", "id": identifier,
            "status": "completed", "patient": {"reference": "Patient/subject"},
            "condition": [{"code": code}],
        }
    observation = {
        "resourceType": "Observation", **common, "status": "final",
        "category": [{"coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "survey",
            "display": "Survey",
        }]}],
        "code": {"coding": _fact_codes(fact_id, fact)},
        "encounter": {"reference": "Encounter/interview"},
    }
    encoded = _fhir_answer(row, _questionnaire_type(fact))
    if "valueCoding" in encoded:
        observation["valueCodeableConcept"] = {
            "coding": [encoded["valueCoding"]]
        }
    elif "valueInteger" in encoded:
        observation["valueInteger"] = encoded["valueInteger"]
    elif "valueDecimal" in encoded:
        observation["valueQuantity"] = {"value": encoded["valueDecimal"]}
    else:
        observation["valueString"] = value
    return observation


def _fact_codes(fact_id: str, fact: dict[str, Any]) -> list[dict[str, Any]]:
    declared = fact.get("standard_mappings", [])
    codes = [
        {
            key: item[key]
            for key in ("system", "version", "code", "display")
            if key in item
        }
        for item in declared
        if isinstance(item, dict)
        and item.get("mapping_relation") in {"exact", "equivalent"}
        and item.get("system")
        and item.get("code")
    ]
    codes.append({"system": FACT_SYSTEM, "code": fact_id})
    return codes
