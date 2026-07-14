"""Projections of the internal screening response.

The internal response remains the source of truth. Report, API, and FHIR are
separate projections and do not alter the captured Facts.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


DAR_EXTENSION = "http://hl7.org/fhir/StructureDefinition/data-absent-reason"


def to_report(response: dict[str, Any], template_id: str = "KR-NHIS-2026") -> dict[str, Any]:
    sections: dict[str, list[dict[str, Any]]] = {}
    for answer in response.get("answers", {}).values():
        group = answer["question_id"].rsplit(".", 1)[0]
        sections.setdefault(group, []).append({
            "field": answer["fact_id"],
            "value": deepcopy(answer.get("value")),
            "dataAbsentReason": deepcopy(answer.get("dataAbsentReason")),
            "raw_input": answer.get("raw_input"),
        })
    return {
        "report_template": template_id,
        "template_version": "0.1.0-research",
        "jurisdiction": "KR",
        "session_id": response["session_id"],
        "official_entitlement": response["official_entitlement"],
        "sections": sections,
        "disclaimer": "Research projection; official submission mapping requires receiving-system conformance approval.",
    }


def to_api_payload(response: dict[str, Any]) -> dict[str, Any]:
    return {
        "api_version": "v1-research",
        "event_type": "national_health_screening.response",
        "idempotency_key": response["session_id"],
        "subject": deepcopy(response.get("patient_context", {})),
        "eligibility": {
            "official_status": response["official_entitlement"],
            "candidate_groups": deepcopy(response["eligible_question_groups"]),
        },
        "consent": deepcopy(response["consent_decisions"]),
        "questionnaire_response": deepcopy(response["answers"]),
        "knowledge": {
            "version": response["knowledge_version"],
            "status": response["knowledge_status"],
            "review_status": response["review_status"],
        },
    }


def _fhir_answer(answer: dict[str, Any]) -> dict[str, Any]:
    value = answer.get("value")
    if isinstance(value, bool):
        return {"valueBoolean": value}
    if isinstance(value, int):
        return {"valueInteger": value}
    if isinstance(value, float):
        return {"valueDecimal": value}
    return {"valueString": str(value)}


def to_fhir_bundle(response: dict[str, Any]) -> dict[str, Any]:
    patient_context = response.get("patient_context", {})
    patient: dict[str, Any] = {
        "resourceType": "Patient",
        "id": f"patient-{response['session_id']}",
    }
    if patient_context.get("administrative_gender") in {"male", "female", "other", "unknown"}:
        patient["gender"] = patient_context["administrative_gender"]
    if patient_context.get("birth_date"):
        patient["birthDate"] = patient_context["birth_date"]

    qr_items = []
    for answer in response.get("answers", {}).values():
        item: dict[str, Any] = {
            "linkId": answer["question_id"],
            "text": answer["fact_id"],
        }
        if answer.get("dataAbsentReason"):
            item["extension"] = [{
                "url": DAR_EXTENSION,
                "valueCode": answer["dataAbsentReason"]["code"],
            }]
        else:
            item["answer"] = [_fhir_answer(answer)]
        qr_items.append(item)

    questionnaire_response = {
        "resourceType": "QuestionnaireResponse",
        "id": f"qr-{response['session_id']}",
        "questionnaire": "https://infoclinic.co/fhir/Questionnaire/kr-national-health-screening-research",
        "status": "completed" if response.get("status") == "completed" else "in-progress",
        "subject": {"reference": f"Patient/{patient['id']}"},
        "item": qr_items,
    }
    consent_entries = []
    for index, decision in enumerate(response.get("consents", []), 1):
        lifecycle = decision.get("lifecycle_status")
        if lifecycle == "withdrawn":
            fhir_status = "inactive"
        elif decision["decision"] == "accepted":
            fhir_status = "active"
        else:
            fhir_status = "rejected"
        consent_entries.append({
            "resource": {
                "resourceType": "Consent",
                "id": f"consent-{response['session_id']}-{index}",
                "status": fhir_status,
                "scope": {"coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/consentscope",
                    "code": "patient-privacy",
                }]},
                "category": [{"coding": [{
                    "system": "https://infoclinic.co/codesystem/consent-category",
                    "code": "questionnaire-participation",
                }]}],
                "patient": {"reference": f"Patient/{patient['id']}"},
                "dateTime": decision["captured_at"],
                "sourceReference": {"display": decision["raw_input"]},
                "policyRule": {"coding": [{
                    "system": decision["policy"]["uri"],
                    "code": decision["policy"]["version"],
                }]},
                "provision": {
                    "type": "permit" if decision["decision"] == "accepted" else "deny",
                    "purpose": [{
                        "system": "https://infoclinic.co/codesystem/consent-purpose",
                        "code": decision["purpose"],
                    }],
                    "class": [{
                        "system": "https://infoclinic.co/codesystem/consent-scope",
                        "code": decision["scope"],
                    }],
                },
            }
        })
    return {
        "resourceType": "Bundle",
        "type": "collection",
        "meta": {"tag": [{
            "system": "https://infoclinic.co/codesystem/knowledge-status",
            "code": "research-only",
        }]},
        "entry": [
            {"resource": patient},
            {"resource": questionnaire_response},
            *consent_entries,
        ],
    }
