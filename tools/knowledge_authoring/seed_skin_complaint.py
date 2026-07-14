#!/usr/bin/env python3
"""Materialize the unreviewed skin-complaint research profile.

The compact declarations in this file are authoring inputs. The deterministic
Builder and Compiler remain the only path to runtime Knowledge Packages.
"""
from __future__ import annotations

import json
from pathlib import Path
from profile_support import normalize_source_monitoring


ROOT = Path(__file__).resolve().parents[2]
VERSION = "0.1.0"
CREATED = "2026-07-14T00:00:00Z"
MODES = ["chat", "face_to_face", "telephone", "video"]
SOURCE_REFS = [
    "source.nhs.anaphylaxis.2026",
    "source.nice.ng240.meningococcal-rash.2026",
    "source.nhs.stevens-johnson.2026",
    "source.nhs.cellulitis.2024",
    "source.nice.ng12.skin-cancer.2026",
]


def provenance(source_refs: list[str] | None = None) -> dict:
    return {
        "created_by": {"type": "ai", "id": "codex-gpt5"},
        "created_at": CREATED,
        "source_refs": source_refs or SOURCE_REFS,
        "review_status": "unreviewed",
        "version": VERSION,
    }


def write(path: str, document: dict) -> None:
    document = normalize_source_monitoring(document)
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def node(identifier: str, node_type: str, display: str, source: str) -> dict:
    return {
        "id": identifier, "type": node_type, "display": display,
        "version": VERSION, "status": "research_only",
        "provenance": provenance([source]),
    }


def entry(
    fact_id: str,
    display: str,
    value_type: str,
    target: str,
    wording: str,
    score: int,
    reason: str,
    groups: list[str],
    *,
    intents: list[str] | None = None,
    allowed: list[str] | None = None,
    safety: bool = False,
    reuse: bool = False,
    terminology: dict | None = None,
    mrcm: bool = False,
) -> dict:
    fact = {"id": fact_id, "display": display, "value_type": value_type}
    if allowed:
        fact["allowed_values"] = allowed
    if safety:
        fact["safety_relevant"] = True
    if terminology:
        fact["terminology_binding"] = terminology
    if mrcm:
        fact["mrcm_validation"] = {
            "ref": "mapping.snomed-mrcm.skin-complaint",
            "status": "provisional_pass",
        }
    item = {
        "fact": fact,
        "target": {
            "id": f"target.skin.{target}",
            "display": display,
            "intents": intents or ["intent.characterize_symptom"],
        },
        "question": {
            "id": f"question.skin.{target}", "wording": wording,
            "language": "ko", "mode": MODES,
        },
        "priority": [{"branch": "any", "score": score, "reason": reason}],
        "supports": groups,
    }
    if reuse:
        item["reuse_existing"] = True
    return item


def safety_rule(identifier: str, when: dict, level: str, priority: int) -> dict:
    return {
        "id": f"rule.skin.safety.{identifier}", "priority": priority,
        "when": when,
        "then": {
            "safety_level": level, "action": "human_handoff",
            "suppress_routine": True,
        },
    }


GROUPS = {
    "safety": "group.skin.immediate-safety",
    "character": "group.skin.characterization",
    "allergy": "group.skin.allergic-drug",
    "infection": "group.skin.infection",
    "lesion": "group.skin.lesion-warning",
    "context": "group.skin.exposure-context",
}


def build_fragment() -> dict:
    snomed = "http://snomed.info/sct"
    entries = [
        entry("symptom.skin_complaint.current", "Current Skin Complaint", "boolean", "current", "지금도 피부 발진, 가려움, 반점, 물집, 상처 또는 피부 병변이 있나요?", 130, "confirm_presentation", [GROUPS["character"]], terminology={"system": snomed, "code": "95324001"}),
        entry("symptom.skin_complaint.main_type", "Main Skin Complaint Type", "coded", "main-type", "가장 주된 문제는 발진·반점, 가려움, 통증·부기, 물집·벗겨짐, 상처·궤양, 점·혹 중 무엇인가요?", 105, "characterize_type", [GROUPS["character"]], allowed=["rash_spots", "itch", "pain_swelling", "blister_peeling", "wound_ulcer", "mole_lump", "other"]),
        entry("symptom.duration", "Symptom Duration", "quantity", "duration", "피부 문제는 언제부터 시작했나요?", 104, "characterize_duration", [GROUPS["character"]], reuse=True),
        entry("symptom.skin_complaint.onset", "Skin Complaint Onset", "coded", "onset", "갑자기 시작했나요, 서서히 시작했나요?", 103, "characterize_onset", [GROUPS["character"]], allowed=["sudden", "gradual", "unclear"]),
        entry("symptom.skin_complaint.location", "Skin Complaint Location", "string", "location", "처음 생긴 곳과 지금 영향을 받은 신체 부위를 알려주세요.", 102, "characterize_location", [GROUPS["character"]], terminology={"system": snomed, "focus_code": "95324001", "attribute_code": "363698007"}, mrcm=True),
        entry("symptom.skin_complaint.distribution", "Skin Complaint Distribution", "coded", "distribution", "한 곳, 몸 한쪽, 양쪽 대칭, 여러 곳, 전신 중 어느 형태인가요?", 101, "characterize_distribution", [GROUPS["character"]], allowed=["single", "unilateral", "bilateral_symmetric", "multiple", "generalized"]),
        entry("symptom.skin_complaint.appearance", "Skin Complaint Appearance", "coded", "appearance", "편평한 반점, 솟은 발진, 진물·딱지, 고름, 물집, 갈라짐·벗겨짐, 점·혹 중 가장 가까운 모양은 무엇인가요?", 100, "characterize_appearance", [GROUPS["character"]], allowed=["flat_patch", "raised", "oozing_crusted", "pustular", "blister", "cracked_peeling", "mole_lump", "other"]),
        entry("symptom.skin_complaint.itch", "Itch", "coded", "itch", "가려움은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 94, "characterize_itch", [GROUPS["character"]], allowed=["none", "mild", "moderate", "severe"], terminology={"system": snomed, "code": "418290006"}),
        entry("symptom.skin_complaint.pain", "Skin Pain", "coded", "pain", "피부 통증은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 99, "characterize_pain", [GROUPS["character"], GROUPS["infection"]], allowed=["none", "mild", "moderate", "severe"]),
        entry("symptom.skin_complaint.rapid_spread", "Rapidly Spreading Skin Change", "boolean", "rapid-spread", "발진이나 붉은 부위가 몇 시간에서 하루 사이 빠르게 퍼지고 있나요?", 126, "rapid_progression_gate", [GROUPS["safety"], GROUPS["infection"]], safety=True),
        entry("symptom.non_blanching_rash", "Non-blanching Petechial or Purpuric Rash", "boolean", "non-blanching", "붉거나 보라색인 점·반점을 투명한 컵으로 눌러도 색이 옅어지지 않나요?", 129, "meningococcal_gate", [GROUPS["safety"]], safety=True),
        entry("symptom.throat_or_tongue_swelling", "Sudden Throat or Tongue Swelling", "boolean", "airway-swelling", "입술, 입안, 혀 또는 목이 갑자기 붓거나 삼키기 어려운가요?", 129, "anaphylaxis_gate", [GROUPS["safety"], GROUPS["allergy"]], safety=True),
        entry("symptom.severe_breathing_difficulty", "Severe Breathing Difficulty with Skin Complaint", "boolean", "breathing", "숨이 매우 차거나 쌕쌕거리고, 목이 조이거나 말하기 어려운가요?", 128, "anaphylaxis_gate", [GROUPS["safety"], GROUPS["allergy"]], safety=True),
        entry("symptom.collapse_or_unresponsiveness", "Collapse or Unresponsiveness", "boolean", "collapse", "갑자기 심하게 어지럽거나 쓰러졌거나, 깨우기 어렵거나 반응이 둔한가요?", 127, "shock_gate", [GROUPS["safety"]], safety=True),
        entry("symptom.skin_blistering_or_peeling", "Widespread Blistering or Peeling", "boolean", "blister-peeling", "피부에 통증 있는 물집이 넓게 생기거나 피부가 벗겨지고 있나요?", 125, "severe_skin_reaction_gate", [GROUPS["safety"], GROUPS["allergy"]], safety=True),
        entry("symptom.mucosal_sores", "Mouth or Genital Mucosal Sores", "boolean", "mucosal", "입술·입안·목 또는 성기 주변에 아픈 물집이나 헐은 곳이 있나요?", 124, "mucosal_gate", [GROUPS["safety"], GROUPS["allergy"]], safety=True),
        entry("symptom.eye_pain_or_vision_change", "Eye Pain or Vision Change", "boolean", "eye", "눈이 아프거나 충혈되고, 빛이 아프거나 시야가 달라졌나요?", 123, "ocular_gate", [GROUPS["safety"], GROUPS["allergy"]], safety=True),
        entry("symptom.fever", "Fever", "boolean", "fever", "열이 나거나 몸이 뜨겁고 춥고 떨리나요?", 122, "infection_gate", [GROUPS["safety"], GROUPS["infection"]], safety=True, reuse=True),
        entry("symptom.systemically_unwell", "Systemically Unwell", "boolean", "unwell", "평소와 달리 전신 상태가 나쁘고 몹시 기운이 없나요?", 121, "infection_gate", [GROUPS["safety"], GROUPS["infection"]], safety=True),
        entry("symptom.confusion", "New Confusion", "boolean", "confusion", "새로 혼란스럽거나 평소와 다르게 횡설수설하나요?", 120, "sepsis_gate", [GROUPS["safety"], GROUPS["infection"]], safety=True, reuse=True),
        entry("symptom.skin_hot_painful_swollen", "Hot Painful Swollen Skin", "boolean", "hot-swollen", "해당 피부가 뜨겁고 아프며 부어 있나요?", 119, "cellulitis_gate", [GROUPS["safety"], GROUPS["infection"]], safety=True),
        entry("symptom.skin_pain_out_of_proportion", "Severe Pain Out of Proportion", "boolean", "severe-pain", "보이는 피부 변화에 비해 통증이 매우 심하거나 빠르게 악화하나요?", 118, "deep_infection_gate", [GROUPS["safety"], GROUPS["infection"]], safety=True),
        entry("medication.new_recent", "Recently Started Medicine", "boolean", "new-medicine", "최근 8주 안에 새 약을 시작했거나 용량을 바꿨나요?", 117, "drug_reaction_context", [GROUPS["safety"], GROUPS["allergy"]], safety=True),
        entry("exposure.new_food_sting_product", "New Food Sting or Product Exposure", "string", "allergen-exposure", "직전에 먹은 음식, 벌레·벌 쏘임, 새 화장품·세제·염색약·장갑처럼 의심되는 노출이 있나요?", 89, "allergy_contact_context", [GROUPS["allergy"], GROUPS["context"]]),
        entry("event.recent_infection", "Recent Infection", "boolean", "recent-infection", "피부 문제가 생기기 전 감기, 인후통, 설사 같은 감염 증상이 있었나요?", 88, "infection_context", [GROUPS["allergy"], GROUPS["infection"]]),
        entry("event.skin_break_bite_wound", "Skin Break Bite or Wound", "boolean", "skin-break", "그 부위에 상처, 갈라짐, 벌레 물림, 수술 또는 주사가 있었나요?", 87, "infection_entry_context", [GROUPS["infection"], GROUPS["context"]]),
        entry("exposure.close_contact_similar_rash", "Close Contact with Similar Rash", "boolean", "contact", "가족·동거인·직장·학교에서 비슷한 발진이나 가려움이 있는 사람이 있나요?", 82, "transmission_context", [GROUPS["context"]]),
        entry("symptom.skin_complaint.recurrent", "Recurrent Skin Complaint", "boolean", "recurrent", "같은 피부 문제가 이전에도 반복됐나요?", 81, "recurrence_context", [GROUPS["context"]]),
        entry("patient.immunocompromised", "Immunocompromised", "boolean", "immunocompromise", "면역을 낮추는 약을 사용하거나 면역이 약해지는 질환·치료를 받고 있나요?", 116, "infection_safety_context", [GROUPS["safety"], GROUPS["infection"]], safety=True, reuse=True, intents=["intent.risk_assessment", "intent.screen_red_flags"]),
        entry("history.diabetes_or_poor_circulation", "Diabetes or Poor Circulation", "boolean", "diabetes-circulation", "당뇨병, 다리 혈액순환 문제 또는 림프부종이 있나요?", 80, "infection_risk_context", [GROUPS["infection"]], intents=["intent.risk_assessment"]),
        entry("symptom.pigmented_lesion_change_size", "Pigmented Lesion Change in Size", "boolean", "lesion-size-change", "점이나 색소 병변이 새로 생겼거나 크기가 변했나요?", 93, "melanoma_context", [GROUPS["lesion"]], intents=["intent.risk_assessment"]),
        entry("symptom.pigmented_lesion_irregular_shape", "Pigmented Lesion Irregular Shape", "boolean", "lesion-shape", "점이나 병변의 모양 또는 경계가 불규칙한가요?", 92, "melanoma_context", [GROUPS["lesion"]], intents=["intent.risk_assessment"]),
        entry("symptom.pigmented_lesion_irregular_colour", "Pigmented Lesion Irregular Colour", "boolean", "lesion-colour", "한 병변 안에 색이 고르지 않거나 여러 색이 섞여 있나요?", 91, "melanoma_context", [GROUPS["lesion"]], intents=["intent.risk_assessment"]),
        entry("symptom.skin_lesion_diameter_7mm_or_more", "Skin Lesion Diameter 7 mm or More", "boolean", "lesion-diameter", "병변의 가장 긴 지름이 약 7mm 이상인가요?", 90, "melanoma_context", [GROUPS["lesion"]], intents=["intent.risk_assessment"]),
        entry("symptom.skin_lesion_oozing_bleeding_nonhealing", "Oozing Bleeding or Non-healing Lesion", "boolean", "lesion-nonhealing", "병변에서 진물·피가 나거나 헐어서 3주 이상 낫지 않나요?", 89, "skin_cancer_context", [GROUPS["lesion"]], intents=["intent.risk_assessment"]),
        entry("symptom.skin_complaint.functional_impact", "Skin Complaint Functional Impact", "coded", "function", "피부 문제 때문에 잠, 일상 활동 또는 업무가 얼마나 방해되나요? 없음, 가벼움, 중간, 심함으로 답해 주세요.", 78, "functional_impact", [GROUPS["character"]], allowed=["none", "mild", "moderate", "severe"], intents=["intent.risk_assessment"]),
    ]
    emergency = 1000
    urgent = 900
    rules = [
        safety_rule("airway-swelling", {"fact": "symptom.throat_or_tongue_swelling", "equals": True}, "emergency", emergency),
        safety_rule("breathing", {"fact": "symptom.severe_breathing_difficulty", "equals": True}, "emergency", emergency),
        safety_rule("collapse", {"fact": "symptom.collapse_or_unresponsiveness", "equals": True}, "emergency", emergency),
        safety_rule("non-blanching-rapid", {"all": [{"fact": "symptom.non_blanching_rash", "equals": True}, {"fact": "symptom.skin_complaint.rapid_spread", "equals": True}]}, "emergency", emergency),
        safety_rule("non-blanching-systemic", {"all": [{"fact": "symptom.non_blanching_rash", "equals": True}, {"fact": "symptom.fever", "equals": True}]}, "emergency", emergency),
        safety_rule("blistering-mucosal", {"all": [{"fact": "symptom.skin_blistering_or_peeling", "equals": True}, {"fact": "symptom.mucosal_sores", "equals": True}]}, "emergency", emergency),
        safety_rule("confusion-systemic", {"all": [{"fact": "symptom.confusion", "equals": True}, {"fact": "symptom.systemically_unwell", "equals": True}]}, "emergency", emergency),
        safety_rule("cellulitis-systemic", {"all": [{"fact": "symptom.skin_hot_painful_swollen", "equals": True}, {"fact": "symptom.fever", "equals": True}]}, "urgent", urgent),
        safety_rule("rapid-severe-pain", {"all": [{"fact": "symptom.skin_complaint.rapid_spread", "equals": True}, {"fact": "symptom.skin_pain_out_of_proportion", "equals": True}]}, "urgent", urgent),
        safety_rule("fever-immunocompromised", {"all": [{"fact": "symptom.fever", "equals": True}, {"fact": "patient.immunocompromised", "equals": True}]}, "urgent", urgent),
    ]
    extra = [
        {"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1].replace("-", " ").title()}
        for value in GROUPS.values()
    ] + [
        {"id": "hypothesis.skin.immediate-safety", "type": "Hypothesis", "display": "Immediate Skin Safety Warning Pattern"},
        {"id": "hypothesis.skin.allergic-drug", "type": "Hypothesis", "display": "Allergic or Drug Reaction Pattern"},
        {"id": "hypothesis.skin.infection", "type": "Hypothesis", "display": "Skin Infection Warning Pattern"},
        {"id": "hypothesis.skin.lesion-warning", "type": "Hypothesis", "display": "Concerning Skin Lesion Pattern"},
    ]
    edges = [
        [GROUPS["safety"], "hypothesis.skin.immediate-safety"],
        [GROUPS["allergy"], "hypothesis.skin.allergic-drug"],
        [GROUPS["infection"], "hypothesis.skin.infection"],
        [GROUPS["lesion"], "hypothesis.skin.lesion-warning"],
    ]
    return {
        "id": "knowledge.generated.dermatological.skin-complaint",
        "version": VERSION, "status": "research_only",
        "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-skin-complaint-research",
        "default_refresh": {
            "class": "clinical_guideline", "last_assessed_at": "2026-07-14",
            "monitor_interval_days": 1, "full_review_interval_days": 180,
            "next_monitor_at": "2026-07-15", "next_full_review_at": "2027-01-10",
            "policy_id": "policy.knowledge-refresh",
            "overdue_behavior": {"production": "exclude_or_require_review", "research_test": "allow_with_warning"},
        },
        "extra_nodes": extra, "group_hypothesis_edges": edges,
        "safety_rules": rules, "entries": entries,
        "provenance": provenance(),
    }


def build_base() -> tuple[dict, dict]:
    source_context = "docs/context/002-encounter-context.md"
    source_intent = "docs/context/001-clinical-intent.md"
    nodes = [
        node("context.primary_care", "EncounterContext", "Primary Care", source_context),
        node("rfe.skin_complaint", "ReasonForEncounter", "Skin Complaint", "knowledge/catalog/primary-care-rfe.json"),
        node("intent.characterize_symptom", "ClinicalIntent", "Characterize Symptom", source_intent),
        node("intent.screen_red_flags", "ClinicalIntent", "Screen Red Flags", source_intent),
        node("intent.differentiate_common_causes", "ClinicalIntent", "Differentiate Common Sources", source_intent),
        node("intent.risk_assessment", "ClinicalIntent", "Risk Assessment", source_intent),
    ]
    edge_data = [
        ("ACTIVATES", "context.primary_care", "intent.characterize_symptom", source_context),
        ("SUGGESTS", "rfe.skin_complaint", "intent.characterize_symptom", source_intent),
        ("SUGGESTS", "rfe.skin_complaint", "intent.screen_red_flags", source_intent),
        ("SUGGESTS", "rfe.skin_complaint", "intent.differentiate_common_causes", source_intent),
        ("SUGGESTS", "rfe.skin_complaint", "intent.risk_assessment", source_intent),
    ]
    edges = [{
        "id": f"edge.skin.{index:03d}", "type": kind, "from": start, "to": end,
        "version": VERSION, "provenance": provenance([source]),
    } for index, (kind, start, end, source) in enumerate(edge_data, 1)]
    graph = {
        "id": "knowledge.primary-care-skin-complaint", "version": VERSION,
        "nodes": nodes, "edges": edges,
        "provenance": provenance(["knowledge/catalog/primary-care-rfe.json"]),
    }
    rules = {
        "id": "rules.primary-care-skin-complaint", "version": VERSION,
        "rules": [{
            "id": "rule.activate.skin-complaint", "type": "activation", "priority": 100,
            "when": {"rfe": "rfe.skin_complaint"},
            "then": {"activate_intents": ["intent.characterize_symptom", "intent.screen_red_flags", "intent.differentiate_common_causes", "intent.risk_assessment"]},
            "version": VERSION, "status": "research_only",
            "provenance": provenance(["specifications/reasoning-loop.md"]),
        }],
        "provenance": provenance(["specifications/reasoning-loop.md"]),
    }
    return graph, rules


def build_mrcm() -> dict:
    concepts = [
        {"code": "95324001", "display": "Skin lesion (disorder)"},
        {"code": "271807003", "display": "Eruption of skin (disorder)"},
        {"code": "418290006", "display": "Itching (finding)"},
    ]
    checks = [
        {"focus_code": concept["code"], "attribute_code": attribute, "allowed": True}
        for concept in concepts for attribute in ("363698007", "246112005")
    ]
    return {
        "id": "mapping.snomed-mrcm.skin-complaint", "version": VERSION,
        "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": "http://snomed.info/sct", "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": concepts, "checks": checks,
        "validation": {"method": "build_time_live_mrcm_summary", "checked_at": CREATED, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "provenance": provenance(["source.stom.mrcm.skin-complaint.20260714"]),
    }


def build_sources() -> tuple[dict, dict]:
    research_artifacts = [
        {
            "id": "source.nhs.anaphylaxis.2026", "kind": "public_health_guidance_metadata",
            "publisher": "NHS", "title": "Anaphylaxis", "version": "accessed-2026-07-14",
            "url": "https://www.nhs.uk/conditions/anaphylaxis/", "language": "en",
            "digest": "metadata_only_not_cached", "license_status": "unknown", "complete": False,
            "monitor_profile": "public_health_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-07-21",
            "assertions": [
                "Sudden swelling of the lips, mouth, throat or tongue, breathing difficulty, severe dizziness, collapse or unresponsiveness requires emergency response.",
                "A raised itchy rash may accompany anaphylaxis but is neither required nor sufficient for diagnosis.",
            ],
        },
        {
            "id": "source.nice.ng240.meningococcal-rash.2026", "kind": "clinical_guideline_metadata",
            "publisher": "NICE", "title": "Meningitis and meningococcal disease: recognition, diagnosis and management",
            "version": "NG240-updated-2026", "url": "https://www.nice.org.uk/guidance/ng240/chapter/Recommendations",
            "language": "en", "digest": "metadata_only_not_cached", "license_status": "restricted", "complete": False,
            "monitor_profile": "clinical_guideline", "monitor_interval_days": 1,
            "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-07-15",
            "assertions": [
                "Haemorrhagic non-blanching purpura, a rapidly spreading non-blanching rash, or a non-blanching rash with meningitis features requires emergency hospital transfer.",
                "Rash may be harder to see on brown, black or tanned skin and absence of rash does not exclude meningococcal disease.",
            ],
        },
        {
            "id": "source.nhs.stevens-johnson.2026", "kind": "public_health_guidance_metadata",
            "publisher": "NHS", "title": "Stevens-Johnson syndrome", "version": "accessed-2026-07-14",
            "url": "https://www.nhs.uk/conditions/stevens-johnson-syndrome/", "language": "en",
            "digest": "metadata_only_not_cached", "license_status": "unknown", "complete": False,
            "monitor_profile": "public_health_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-07-21",
            "assertions": [
                "A spreading painful, blistering or peeling rash after an infection or new medicine, especially with mouth, eye, airway or genital involvement, requires emergency assessment.",
                "The interview identifies severe-reaction warning features and does not diagnose Stevens-Johnson syndrome.",
            ],
        },
        {
            "id": "source.nhs.cellulitis.2024", "kind": "public_health_guidance_metadata",
            "publisher": "NHS", "title": "Cellulitis", "version": "reviewed-2024-04-18",
            "url": "https://www.nhs.uk/conditions/cellulitis/", "language": "en",
            "digest": "metadata_only_not_cached", "license_status": "unknown", "complete": False,
            "monitor_profile": "public_health_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-07-21",
            "assertions": [
                "Painful, hot and swollen skin needs urgent clinical assessment.",
                "Systemic illness, purple patches, rapid breathing or heartbeat, dizziness, confusion, cold clammy skin or unresponsiveness can indicate life-threatening complications.",
            ],
        },
        {
            "id": "source.nice.ng12.skin-cancer.2026", "kind": "clinical_guideline_metadata",
            "publisher": "NICE", "title": "Suspected cancer: recognition and referral — skin cancers",
            "version": "NG12-updated-2026", "url": "https://www.nice.org.uk/guidance/ng12/chapter/Recommendations-organised-by-site-of-cancer",
            "language": "en", "digest": "metadata_only_not_cached", "license_status": "restricted", "complete": False,
            "monitor_profile": "clinical_guideline", "monitor_interval_days": 1,
            "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-07-15",
            "assertions": [
                "The weighted seven-point checklist includes change in size, irregular shape, irregular colour, diameter of 7 mm or more, inflammation, oozing and change in sensation.",
                "Suspicious pigmented or non-pigmented lesions require clinician assessment; questionnaire features do not diagnose skin cancer.",
            ],
        },
        {
            "id": "source.stom.mrcm.skin-complaint.20260714", "kind": "terminology_mrcm_query_summary",
            "publisher": "Infoclinic", "title": "STOM SNOMED CT lookup and MRCM allowed attributes for skin complaint",
            "version": "SNOMEDCT-20260701", "url": "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/95324001",
            "language": "en", "digest": "live_response_summary_not_raw_cache", "license_status": "restricted", "complete": False,
            "monitor_profile": "terminology_server", "monitor_interval_days": 30,
            "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-08-13",
            "assertions": [
                "STOM confirmed active Skin lesion, Eruption of skin and Itching concepts.",
                "Finding site and Severity were allowed for the selected concepts.",
                "MRCM validates terminology modeling only and does not control clinical questions, diagnoses, priority or safety.",
            ],
        },
    ]
    research = {
        "id": "source-manifest.primary-care-skin-complaint-research", "version": VERSION,
        "acquired_at": CREATED, "status": "research_only", "artifacts": research_artifacts,
        "provenance": provenance([item["id"] for item in research_artifacts]),
    }
    artifacts = [
        ("source.repository.foundation", "repository_specification", "clinical-interview-platform", "0.2-draft", "en", "FOUNDATION.md", True),
        ("source.repository.context", "repository_specification", "clinical-interview-platform", "0.2-draft", "en", "docs/context", True),
        ("source.catalog.primary-care-rfe", "knowledge_catalog", "clinical-interview-platform", VERSION, "en", "knowledge/catalog/primary-care-rfe.json", True),
        ("source.registry.shared-primary-care-facts", "fact_registry", "clinical-interview-platform", "0.2.0", "en", "knowledge/shared/primary-care-facts.json", True),
        ("source.generated.primary-care-skin-complaint", "generated_clinical_knowledge", "clinical-interview-platform", VERSION, "ko", "knowledge/generated/dermatological/skin-complaint/skin-complaint.json", True),
        ("source.mapping.snomed-mrcm.skin-complaint", "terminology_mapping", "clinical-interview-platform", VERSION, "en", "mappings/terminology/snomed-mrcm-skin-complaint.json", False),
        ("source.external.primary-care-skin-complaint-research", "external_source_manifest", "clinical-interview-platform", VERSION, "en", "sources/manifests/primary-care-skin-complaint-research.json", False),
        ("source.policy.primary-care-skin-complaint-completion", "runtime_policy", "clinical-interview-platform", VERSION, "en", "policies/primary-care-skin-complaint-completion.json", True),
    ]
    primary_items = []
    for identifier, kind, publisher, version, language, path, complete in artifacts:
        item = {
            "id": identifier, "kind": kind, "publisher": publisher, "version": version,
            "language": language, "path": path, "digest": "computed_at_build",
            "license_status": "allowed" if complete else ("unknown" if "external" in identifier else "allowed"),
            "complete": complete,
        }
        if identifier == "source.generated.primary-care-skin-complaint":
            item["usage_modes"] = ["research_test", "simulation"]
        primary_items.append(item)
    primary = {
        "id": "source-manifest.primary-care-skin-complaint", "version": VERSION,
        "acquired_at": CREATED, "artifacts": primary_items,
        "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md", "sources/manifests/primary-care-skin-complaint-research.json"]),
    }
    return primary, research


def build_policy(fragment: dict) -> dict:
    safety_facts: list[str] = []
    for rule in fragment["safety_rules"]:
        def collect(condition: dict) -> None:
            if "fact" in condition and condition["fact"] not in safety_facts:
                safety_facts.append(condition["fact"])
            for key in ("all", "any"):
                for child in condition.get(key, []):
                    collect(child)
        collect(rule["when"])
    fact_ids = [item["fact"]["id"] for item in fragment["entries"]]
    always = ["symptom.skin_complaint.current", *safety_facts]
    routine = [identifier for identifier in fact_ids if identifier not in always]
    return {
        "id": "policy.primary-care-skin-complaint-completion", "version": VERSION,
        "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": always, "routine": routine},
        "clarification_facts_by_rule": {}, "question_budget": {"routine": 40, "clarify": 12},
        "provenance": provenance(),
    }


def build_simulations(fragment: dict) -> dict[str, dict]:
    cases: dict[str, dict] = {}
    source_by_rule = {
        "airway-swelling": "source.nhs.anaphylaxis.2026",
        "breathing": "source.nhs.anaphylaxis.2026",
        "collapse": "source.nhs.anaphylaxis.2026",
        "non-blanching-rapid": "source.nice.ng240.meningococcal-rash.2026",
        "non-blanching-systemic": "source.nice.ng240.meningococcal-rash.2026",
        "blistering-mucosal": "source.nhs.stevens-johnson.2026",
        "confusion-systemic": "source.nhs.cellulitis.2024",
        "cellulitis-systemic": "source.nhs.cellulitis.2024",
        "rapid-severe-pain": "source.nhs.cellulitis.2024",
        "fever-immunocompromised": "source.nhs.cellulitis.2024",
    }
    true_facts = {
        "airway-swelling": ["symptom.throat_or_tongue_swelling"],
        "breathing": ["symptom.severe_breathing_difficulty"],
        "collapse": ["symptom.collapse_or_unresponsiveness"],
        "non-blanching-rapid": ["symptom.non_blanching_rash", "symptom.skin_complaint.rapid_spread"],
        "non-blanching-systemic": ["symptom.non_blanching_rash", "symptom.fever"],
        "blistering-mucosal": ["symptom.skin_blistering_or_peeling", "symptom.mucosal_sores"],
        "confusion-systemic": ["symptom.confusion", "symptom.systemically_unwell"],
        "cellulitis-systemic": ["symptom.skin_hot_painful_swollen", "symptom.fever"],
        "rapid-severe-pain": ["symptom.skin_complaint.rapid_spread", "symptom.skin_pain_out_of_proportion"],
        "fever-immunocompromised": ["symptom.fever", "patient.immunocompromised"],
    }
    for index, rule in enumerate(fragment["safety_rules"], 1):
        short = rule["id"].removeprefix("rule.skin.safety.")
        level = rule["then"]["safety_level"]
        cases[f"SKIN-{short.upper()}-001.json"] = {
            "id": f"SKIN-{short.upper()}-001", "simulation_language": "ko",
            "persona": {"age": 40 + index},
            "initial_statement": {"ko": "피부에 이상이 생겼어요."},
            "hidden_state": {identifier: {"value": True} for identifier in true_facts[short]},
            "expected": {
                "expected_safety_level": level, "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [rule["id"]],
                "expected_max_turns": 25,
                "forbidden_assertions": ["diagnosis.anaphylaxis", "diagnosis.meningococcal_disease", "diagnosis.stevens_johnson_syndrome"],
            },
            "provenance": provenance([source_by_rule[short]]),
        }
    hidden: dict[str, dict] = {}
    for item in fragment["entries"]:
        fact = item["fact"]
        identifier = fact["id"]
        if fact["value_type"] == "boolean":
            hidden[identifier] = {"value": identifier == "symptom.skin_complaint.current"}
        elif fact["value_type"] == "quantity":
            hidden[identifier] = {"value": {"amount": 2, "unit": "days"}}
        elif fact["value_type"] == "coded":
            hidden[identifier] = {"value": fact.get("allowed_values", ["other"])[0]}
        else:
            hidden[identifier] = {"value": "팔 한 곳"}
    declined = "exposure.new_food_sting_product"
    hidden.pop(declined, None)
    cases["SKIN-DATA-ABSENT-001.json"] = {
        "id": "SKIN-DATA-ABSENT-001", "simulation_language": "ko",
        "persona": {"age": 34, "communication_style": "declines_exposure_detail"},
        "initial_statement": {"ko": "팔에 가벼운 발진이 생겼어요."},
        "hidden_state": hidden,
        "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}},
        "expected": {
            "expected_data_absent_reasons": {declined: "asked-declined"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 40,
            "forbidden_assertions": ["diagnosis.contact_dermatitis"],
        },
        "provenance": provenance(["source.nice.ng12.skin-cancer.2026", "specifications/clinical-memory.md"]),
    }
    return cases


def main() -> None:
    graph, rules = build_base()
    fragment = build_fragment()
    write("knowledge/base/primary-care-skin-complaint.json", graph)
    write("rules/base/primary-care-skin-complaint.json", rules)
    write("knowledge/generated/dermatological/skin-complaint/skin-complaint.json", fragment)
    write("mappings/terminology/snomed-mrcm-skin-complaint.json", build_mrcm())
    primary_sources, research_sources = build_sources()
    write("sources/manifests/primary-care-skin-complaint.json", primary_sources)
    write("sources/manifests/primary-care-skin-complaint-research.json", research_sources)
    write("policies/primary-care-skin-complaint-completion.json", build_policy(fragment))
    for filename, case in build_simulations(fragment).items():
        write(f"simulation/patients/dermatological/skin-complaint/{filename}", case)


if __name__ == "__main__":
    main()
