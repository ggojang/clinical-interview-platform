#!/usr/bin/env python3
"""Probe approved STOM read-only terminology operations with synthetic terms."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


BASE_URL = "https://stom.infoclinic.co"


def request_json(
    path: str, *, query: dict[str, str | int] | None = None, body: dict | None = None
) -> dict | list:
    url = BASE_URL + quote(path, safe="/$")
    if query:
        url += "?" + urlencode(query)
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(
        url,
        data=payload,
        method="POST" if body is not None else "GET",
        headers={
            "Accept": "application/json, application/fhir+json",
            "Content-Type": "application/json",
            "User-Agent": "clinical-interview-platform-stom-probe/0.1",
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def parameter_value(parameters: dict, name: str) -> str | bool | None:
    for parameter in parameters.get("parameter", []):
        if parameter.get("name") != name:
            continue
        for key, value in parameter.items():
            if key.startswith("value"):
                return value
    return None


def probe() -> dict:
    capability = request_json("/fhir/metadata", query={"_format": "json"})
    mapping = request_json(
        "/map/SNOMEDCT/search",
        body={
            "q": "복부 통증",
            "semanticTags": ["finding", "disorder"],
            "state": "ACTIVE",
            "page": 1,
            "size": 5,
        },
    )
    candidates = mapping.get("hits", [])
    abdominal_pain = next(
        (item for item in candidates if item.get("conceptId") == "21522001"), None
    )
    if not abdominal_pain or not abdominal_pain.get("conceptActive"):
        raise RuntimeError("active SNOMED CT abdominal-pain candidate not returned")

    mrcm_attributes = request_json("/allow/attributes/SNOMEDCT/21522001")
    if not isinstance(mrcm_attributes, list):
        raise RuntimeError("SNOMED CT MRCM attribute response is not a list")
    mrcm_index = {item.get("id"): item for item in mrcm_attributes}
    for attribute_id in ("363698007", "246112005"):
        if attribute_id not in mrcm_index:
            raise RuntimeError(f"expected MRCM attribute missing: {attribute_id}")

    chest_lookup = request_json(
        "/fhir/CodeSystem/$lookup",
        query={
            "system": "http://snomed.info/sct",
            "code": "29857009",
            "_format": "json",
        },
    )
    if parameter_value(chest_lookup, "display") != "Chest pain (finding)":
        raise RuntimeError("SNOMED CT chest-pain lookup did not return expected display")
    chest_mrcm_attributes = request_json("/allow/attributes/SNOMEDCT/29857009")
    if not isinstance(chest_mrcm_attributes, list):
        raise RuntimeError("chest-pain MRCM attribute response is not a list")
    chest_mrcm_index = {item.get("id"): item for item in chest_mrcm_attributes}
    for attribute_id in ("363698007", "246112005"):
        if attribute_id not in chest_mrcm_index:
            raise RuntimeError(f"expected chest-pain MRCM attribute missing: {attribute_id}")

    headache_lookup = request_json(
        "/fhir/CodeSystem/$lookup",
        query={
            "system": "http://snomed.info/sct",
            "code": "25064002",
            "_format": "json",
        },
    )
    if parameter_value(headache_lookup, "display") != "Headache (finding)":
        raise RuntimeError("SNOMED CT headache lookup did not return expected display")
    headache_mrcm_attributes = request_json("/allow/attributes/SNOMEDCT/25064002")
    if not isinstance(headache_mrcm_attributes, list):
        raise RuntimeError("headache MRCM attribute response is not a list")
    headache_mrcm_index = {item.get("id"): item for item in headache_mrcm_attributes}
    for attribute_id in ("363698007", "246112005"):
        if attribute_id not in headache_mrcm_index:
            raise RuntimeError(f"expected headache MRCM attribute missing: {attribute_id}")

    dizziness_lookup = request_json(
        "/fhir/CodeSystem/$lookup",
        query={"system": "http://snomed.info/sct", "code": "404640003", "_format": "json"},
    )
    syncope_lookup = request_json(
        "/fhir/CodeSystem/$lookup",
        query={"system": "http://snomed.info/sct", "code": "271594007", "_format": "json"},
    )
    if parameter_value(dizziness_lookup, "display") != "Dizziness (finding)":
        raise RuntimeError("SNOMED CT dizziness lookup did not return expected display")
    if parameter_value(syncope_lookup, "display") != "Syncope (finding)":
        raise RuntimeError("SNOMED CT syncope lookup did not return expected display")
    dizziness_mrcm = request_json("/allow/attributes/SNOMEDCT/404640003")
    syncope_mrcm = request_json("/allow/attributes/SNOMEDCT/271594007")
    dizziness_mrcm_index = {item.get("id"): item for item in dizziness_mrcm}
    for attribute_id in ("363698007", "246112005"):
        if attribute_id not in dizziness_mrcm_index:
            raise RuntimeError(f"expected dizziness MRCM attribute missing: {attribute_id}")
    if syncope_mrcm != []:
        raise RuntimeError("expected empty Syncope MRCM result changed; reassess mapping")

    vomiting_lookup = request_json(
        "/fhir/CodeSystem/$lookup",
        query={"system": "http://snomed.info/sct", "code": "422400008", "_format": "json"},
    )
    diarrhea_lookup = request_json(
        "/fhir/CodeSystem/$lookup",
        query={"system": "http://snomed.info/sct", "code": "62315008", "_format": "json"},
    )
    if parameter_value(vomiting_lookup, "display") != "Vomiting (disorder)":
        raise RuntimeError("SNOMED CT vomiting lookup did not return expected display")
    if parameter_value(diarrhea_lookup, "display") != "Diarrhea (finding)":
        raise RuntimeError("SNOMED CT diarrhea lookup did not return expected display")
    vomiting_mrcm = request_json("/allow/attributes/SNOMEDCT/422400008")
    diarrhea_mrcm = request_json("/allow/attributes/SNOMEDCT/62315008")
    for label, attributes in (("vomiting", vomiting_mrcm), ("diarrhea", diarrhea_mrcm)):
        if not isinstance(attributes, list):
            raise RuntimeError(f"{label} MRCM attribute response is not a list")
        attribute_index = {item.get("id"): item for item in attributes}
        for attribute_id in ("363698007", "246112005"):
            if attribute_id not in attribute_index:
                raise RuntimeError(f"expected {label} MRCM attribute missing: {attribute_id}")

    urinary_concepts = {
        "49650001": "Dysuria (finding)",
        "162116003": "Increased frequency of urination (finding)",
        "75088002": "Urgent desire to urinate (finding)",
        "267064002": "Retention of urine (disorder)",
        "197927001": "Recurrent urinary tract infection (disorder)",
    }
    urinary_results = {}
    for code, expected_display in urinary_concepts.items():
        concept_lookup = request_json(
            "/fhir/CodeSystem/$lookup",
            query={"system": "http://snomed.info/sct", "code": code, "_format": "json"},
        )
        display = parameter_value(concept_lookup, "display")
        if display != expected_display:
            raise RuntimeError(f"SNOMED CT urinary lookup changed for {code}: {display!r}")
        attributes = request_json(f"/allow/attributes/SNOMEDCT/{code}")
        attribute_index = {item.get("id"): item for item in attributes}
        for attribute_id in ("363698007", "246112005"):
            if attribute_id not in attribute_index:
                raise RuntimeError(f"expected urinary MRCM attribute missing for {code}: {attribute_id}")
        urinary_results[code] = {
            "display": display,
            "version": parameter_value(concept_lookup, "version"),
            "attribute_count_returned": len(attributes),
        }

    fatigue_results = {}
    for code, expected_display in {
        "84229001": "Fatigue (finding)",
        "248274002": "Lack of energy (finding)",
    }.items():
        concept_lookup = request_json(
            "/fhir/CodeSystem/$lookup",
            query={"system": "http://snomed.info/sct", "code": code, "_format": "json"},
        )
        display = parameter_value(concept_lookup, "display")
        if display != expected_display:
            raise RuntimeError(f"SNOMED CT fatigue lookup changed for {code}: {display!r}")
        attributes = request_json(f"/allow/attributes/SNOMEDCT/{code}")
        attribute_index = {item.get("id"): item for item in attributes}
        for attribute_id in ("363698007", "246112005"):
            if attribute_id not in attribute_index:
                raise RuntimeError(f"expected fatigue MRCM attribute missing for {code}: {attribute_id}")
        fatigue_results[code] = {
            "display": display,
            "version": parameter_value(concept_lookup, "version"),
            "attribute_count_returned": len(attributes),
        }

    back_pain_results = {}
    for code, expected_display in {
        "161891005": "Backache (finding)",
        "279039007": "Low back pain (finding)",
        "23056005": "Sciatica (disorder)",
    }.items():
        concept_lookup = request_json(
            "/fhir/CodeSystem/$lookup",
            query={"system": "http://snomed.info/sct", "code": code, "_format": "json"},
        )
        display = parameter_value(concept_lookup, "display")
        if display != expected_display:
            raise RuntimeError(f"SNOMED CT back-pain lookup changed for {code}: {display!r}")
        attributes = request_json(f"/allow/attributes/SNOMEDCT/{code}")
        attribute_index = {item.get("id"): item for item in attributes}
        for attribute_id in ("363698007", "246112005"):
            if attribute_id not in attribute_index:
                raise RuntimeError(f"expected back-pain MRCM attribute missing for {code}: {attribute_id}")
        back_pain_results[code] = {
            "display": display,
            "version": parameter_value(concept_lookup, "version"),
            "attribute_count_returned": len(attributes),
        }

    skin_results = {}
    for code, expected_display in {
        "95324001": "Skin lesion (disorder)",
        "271807003": "Eruption of skin (disorder)",
        "418290006": "Itching (finding)",
    }.items():
        concept_lookup = request_json(
            "/fhir/CodeSystem/$lookup",
            query={"system": "http://snomed.info/sct", "code": code, "_format": "json"},
        )
        display = parameter_value(concept_lookup, "display")
        if display != expected_display:
            raise RuntimeError(f"SNOMED CT skin lookup changed for {code}: {display!r}")
        attributes = request_json(f"/allow/attributes/SNOMEDCT/{code}")
        attribute_index = {item.get("id"): item for item in attributes}
        for attribute_id in ("363698007", "246112005"):
            if attribute_id not in attribute_index:
                raise RuntimeError(f"expected skin MRCM attribute missing for {code}: {attribute_id}")
        skin_results[code] = {
            "display": display,
            "version": parameter_value(concept_lookup, "version"),
            "attribute_count_returned": len(attributes),
        }

    lookup = request_json(
        "/fhir/CodeSystem/$lookup",
        query={
            "system": "http://snomed.info/sct",
            "code": "49727002",
            "_format": "json",
        },
    )
    if parameter_value(lookup, "display") != "Cough (finding)":
        raise RuntimeError("SNOMED CT cough lookup did not return expected display")

    hira = request_json(
        "/hira/약제/search",
        query={"q": "암로디핀", "page": 1, "size": 3},
    )
    if not hira.get("items"):
        raise RuntimeError("HIRA amlodipine probe returned no candidates")

    return {
        "id": "probe.stom.read-only",
        "tested_at": datetime.now(timezone.utc).isoformat(),
        "contains_patient_data": False,
        "queries_are_synthetic_normalized_terms": True,
        "capability": {
            "fhir_version": capability.get("fhirVersion"),
            "software_version": capability.get("software", {}).get("version"),
        },
        "snomed_mapping": {
            "query": "복부 통증",
            "code": abdominal_pain["conceptId"],
            "display": abdominal_pain["fsn"],
            "active": abdominal_pain["conceptActive"],
        },
        "snomed_lookup": {
            "code": "49727002",
            "display": parameter_value(lookup, "display"),
            "version": parameter_value(lookup, "version"),
        },
        "snomed_mrcm": {
            "focus_code": "21522001",
            "verified_attribute_ids": ["246112005", "363698007"],
            "attribute_count_returned": len(mrcm_attributes),
            "clinical_rule_authority": False,
        },
        "chest_pain_snomed_mrcm": {
            "focus_code": "29857009",
            "display": parameter_value(chest_lookup, "display"),
            "version": parameter_value(chest_lookup, "version"),
            "verified_attribute_ids": ["246112005", "363698007"],
            "attribute_count_returned": len(chest_mrcm_attributes),
            "clinical_rule_authority": False,
        },
        "headache_snomed_mrcm": {
            "focus_code": "25064002",
            "display": parameter_value(headache_lookup, "display"),
            "version": parameter_value(headache_lookup, "version"),
            "verified_attribute_ids": ["246112005", "363698007"],
            "attribute_count_returned": len(headache_mrcm_attributes),
            "clinical_rule_authority": False,
        },
        "dizziness_syncope_snomed_mrcm": {
            "dizziness_focus_code": "404640003",
            "syncope_focus_code": "271594007",
            "dizziness_verified_attribute_ids": ["246112005", "363698007"],
            "dizziness_attribute_count_returned": len(dizziness_mrcm),
            "syncope_attribute_count_returned": len(syncope_mrcm),
            "syncope_postcoordination_asserted": False,
            "clinical_rule_authority": False,
        },
        "vomiting_diarrhea_snomed_mrcm": {
            "vomiting_focus_code": "422400008",
            "vomiting_display": parameter_value(vomiting_lookup, "display"),
            "vomiting_version": parameter_value(vomiting_lookup, "version"),
            "vomiting_attribute_count_returned": len(vomiting_mrcm),
            "diarrhea_focus_code": "62315008",
            "diarrhea_display": parameter_value(diarrhea_lookup, "display"),
            "diarrhea_version": parameter_value(diarrhea_lookup, "version"),
            "diarrhea_attribute_count_returned": len(diarrhea_mrcm),
            "verified_attribute_ids": ["246112005", "363698007"],
            "clinical_rule_authority": False,
        },
        "urinary_symptoms_snomed_mrcm": {
            "concepts": urinary_results,
            "verified_attribute_ids": ["246112005", "363698007"],
            "clinical_rule_authority": False,
        },
        "fatigue_snomed_mrcm": {
            "concepts": fatigue_results,
            "verified_attribute_ids": ["246112005", "363698007"],
            "clinical_rule_authority": False,
        },
        "back_pain_snomed_mrcm": {
            "concepts": back_pain_results,
            "verified_attribute_ids": ["246112005", "363698007"],
            "clinical_rule_authority": False,
        },
        "skin_complaint_snomed_mrcm": {
            "concepts": skin_results,
            "verified_attribute_ids": ["246112005", "363698007"],
            "clinical_rule_authority": False,
        },
        "hira_drug_search": {
            "query": "암로디핀",
            "candidate_count_returned": len(hira["items"]),
        },
        "status": "research_only",
        "review_status": "unreviewed",
    }


if __name__ == "__main__":
    print(json.dumps(probe(), ensure_ascii=False, indent=2, sort_keys=True))
