#!/usr/bin/env python3
"""Materialize the unreviewed upper-respiratory-symptom research profile."""
from __future__ import annotations

from profile_support import (
    CREATED_AT, VERSION, base_graph_and_rules, completion_policy,
    default_refresh, entry, provenance, safety_rule, write_json,
)


PREFIX = "upper-respiratory"
RFE = "rfe.upper_respiratory_symptoms"
MRCM_REF = "mapping.snomed-mrcm.upper-respiratory-symptoms"
SNOMED = "http://snomed.info/sct"
SOURCES = [
    "source.nhs.sore-throat.2024",
    "source.nice.ng84.sore-throat.2025",
    "source.nice.ng79.sinusitis.2026",
    "source.nhs.allergic-rhinitis.2026",
]

G = {
    "safety": "group.upper-respiratory.immediate-safety",
    "throat": "group.upper-respiratory.throat",
    "nasal": "group.upper-respiratory.nasal-sinus",
    "allergy": "group.upper-respiratory.allergic",
    "voice": "group.upper-respiratory.voice-persistence",
    "context": "group.upper-respiratory.context",
}

CHARACTERIZE = ["intent.characterize_symptom"]
SAFETY = ["intent.screen_red_flags"]
RISK = ["intent.risk_assessment"]
DIFFERENTIATE = ["intent.differentiate_common_causes"]


def q(fid, display, vt, key, wording, score, reason, groups, intents, **kwargs):
    return entry(
        PREFIX, fid, display, vt, key, wording, score, reason, groups,
        intents=intents, **kwargs,
    )


def build_fragment():
    entries = [
        q("symptom.upper_respiratory.current", "Current Upper Respiratory Symptom", "boolean", "current", "지금도 목 통증, 코막힘·콧물, 재채기 또는 목소리 변화가 있나요?", 130, "confirm_presentation", [G["throat"], G["nasal"]], CHARACTERIZE),
        q("symptom.upper_respiratory.main_type", "Main Upper Respiratory Symptom", "coded", "main-type", "가장 불편한 것은 목 통증, 코막힘, 콧물, 재채기·가려움, 얼굴 통증, 쉰목소리 중 무엇인가요?", 105, "characterize_type", [G["throat"], G["nasal"]], CHARACTERIZE, allowed_values=["sore_throat", "nasal_obstruction", "nasal_discharge", "sneezing_itch", "facial_pain", "hoarseness", "other"]),
        q("symptom.duration", "Symptom Duration", "quantity", "duration", "증상은 언제부터 시작했나요?", 104, "characterize_duration", [G["context"]], CHARACTERIZE, reuse_existing=True),
        q("symptom.upper_respiratory.onset", "Upper Respiratory Symptom Onset", "coded", "onset", "갑자기 시작했나요, 서서히 시작했나요?", 103, "characterize_onset", [G["context"]], CHARACTERIZE, allowed_values=["sudden", "gradual", "unclear"]),
        q("symptom.upper_respiratory.severity", "Upper Respiratory Symptom Severity", "coded", "severity", "전체 불편은 가벼움, 중간, 심함 중 어디에 가깝나요?", 102, "characterize_severity", [G["context"]], CHARACTERIZE, allowed_values=["mild", "moderate", "severe"]),
        q("symptom.severe_breathing_or_stridor", "Severe Breathing Difficulty or Stridor", "boolean", "breathing-stridor", "숨쉬기 어렵거나 들이쉴 때 높은 소리가 나나요?", 129, "airway_gate", [G["safety"]], SAFETY, safety_relevant=True),
        q("symptom.unable_to_swallow_saliva_or_drooling", "Unable to Swallow Saliva or Drooling", "boolean", "drooling", "침도 삼키기 어려워 흘리거나 계속 뱉고 있나요?", 128, "airway_gate", [G["safety"], G["throat"]], SAFETY, safety_relevant=True),
        q("symptom.upper_respiratory.severe_rapid_worsening", "Severe and Rapidly Worsening Upper Respiratory Symptoms", "boolean", "rapid-worsening", "증상이 매우 심하면서 빠르게 악화하고 있나요?", 127, "rapid_deterioration_gate", [G["safety"]], SAFETY, safety_relevant=True),
        q("symptom.sudden_lip_tongue_or_throat_swelling", "Sudden Lip Tongue or Throat Swelling", "boolean", "allergic-swelling", "입술, 혀 또는 목이 갑자기 붓고 있나요?", 126, "anaphylaxis_gate", [G["safety"], G["allergy"]], SAFETY, safety_relevant=True),
        q("symptom.periorbital_swelling_or_displaced_eye", "Periorbital Swelling or Displaced Eye", "boolean", "orbital-swelling", "한쪽 눈 주위가 심하게 붓거나 눈이 앞으로 나오거나 위치가 달라 보이나요?", 125, "orbital_gate", [G["safety"], G["nasal"]], SAFETY, safety_relevant=True),
        q("symptom.double_vision_painful_eye_movement_or_reduced_vision", "Double Vision Painful Eye Movement or Reduced Vision", "boolean", "orbital-vision", "겹쳐 보이거나 눈을 움직일 때 아프거나 시력이 새로 떨어졌나요?", 124, "orbital_gate", [G["safety"], G["nasal"]], SAFETY, safety_relevant=True),
        q("symptom.sinus_intracranial_warning", "Sinus Intracranial Warning Feature", "boolean", "intracranial", "심한 이마 두통과 함께 목이 뻣뻣하거나 한쪽 팔다리 힘·말하기가 달라졌나요?", 123, "intracranial_gate", [G["safety"], G["nasal"]], SAFETY, safety_relevant=True),
        q("symptom.fever", "Fever", "boolean", "fever", "열이 나거나 몸이 뜨겁고 춥고 떨리나요?", 122, "infection_gate", [G["safety"], G["throat"], G["nasal"]], SAFETY, safety_relevant=True, reuse_existing=True),
        q("symptom.systemically_unwell", "Systemically Unwell", "boolean", "systemically-unwell", "평소와 달리 전신 상태가 몹시 나쁘고 기운이 없나요?", 121, "systemic_gate", [G["safety"]], SAFETY, safety_relevant=True),
        q("symptom.confusion", "New Confusion", "boolean", "confusion", "새로 혼란스럽거나 깨우기 어렵거나 평소와 다르게 반응하나요?", 120, "sepsis_gate", [G["safety"]], SAFETY, safety_relevant=True, reuse_existing=True),
        q("patient.immunocompromised", "Immunocompromised", "boolean", "immunocompromised", "면역을 낮추는 약을 사용하거나 면역이 약해지는 질환·치료를 받고 있나요?", 119, "complication_risk", [G["safety"], G["context"]], SAFETY + RISK, safety_relevant=True, reuse_existing=True),
        q("symptom.dehydration_or_unable_fluids", "Dehydration or Unable to Take Fluids", "boolean", "dehydration", "물을 충분히 마실 수 없거나 소변이 크게 줄고 진해졌나요?", 118, "dehydration_gate", [G["safety"], G["throat"]], SAFETY, safety_relevant=True),
        q("symptom.neck_swelling_trismus_or_muffled_voice", "Neck Swelling Trismus or Muffled Voice", "boolean", "deep-neck", "목 한쪽이 붓거나 입을 벌리기 어렵거나 목소리가 입에 무언가 문 듯 변했나요?", 117, "suppurative_complication_gate", [G["safety"], G["throat"]], SAFETY, safety_relevant=True),
        q("symptom.throat_pain", "Throat Pain", "coded", "throat-pain", "목 통증은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 98, "throat_characterization", [G["throat"]], CHARACTERIZE, allowed_values=["none", "mild", "moderate", "severe"], terminology_binding={"system": SNOMED, "focus_code": "162397003", "attribute_code": "246112005"}, mrcm_ref=MRCM_REF),
        q("symptom.painful_swallowing", "Painful Swallowing", "boolean", "painful-swallow", "음식이나 물을 삼킬 때 목이 아픈가요?", 97, "throat_characterization", [G["throat"]], CHARACTERIZE),
        q("observation.tonsillar_exudate_or_pus", "Tonsillar Exudate or Pus", "boolean", "tonsillar-exudate", "편도에 흰 점이나 고름처럼 보이는 것이 있나요? 보지 못했다면 모름으로 답해 주세요.", 91, "feverpain_context", [G["throat"]], DIFFERENTIATE),
        q("symptom.tender_anterior_neck_nodes", "Tender Anterior Neck Nodes", "boolean", "neck-nodes", "목 앞쪽 림프절이 붓고 누르면 아픈가요?", 90, "centor_context", [G["throat"]], DIFFERENTIATE),
        q("symptom.cough", "Cough", "boolean", "cough", "기침이 함께 있나요?", 89, "upper_respiratory_context", [G["throat"], G["nasal"]], DIFFERENTIATE, reuse_existing=True),
        q("symptom.nasal_obstruction", "Nasal Obstruction", "coded", "nasal-obstruction", "코막힘은 없음, 한쪽, 양쪽 중 무엇인가요?", 96, "nasal_characterization", [G["nasal"]], CHARACTERIZE, allowed_values=["none", "unilateral", "bilateral"], terminology_binding={"system": SNOMED, "code": "232209000"}),
        q("symptom.nasal_discharge", "Nasal Discharge", "coded", "nasal-discharge", "콧물은 없음, 맑음, 누렇거나 녹색, 피가 섞임 중 무엇인가요?", 95, "nasal_characterization", [G["nasal"]], CHARACTERIZE, allowed_values=["none", "clear", "discoloured", "blood_stained"], terminology_binding={"system": SNOMED, "code": "64531003"}),
        q("symptom.unilateral_purulent_nasal_discharge", "Unilateral Purulent Nasal Discharge", "boolean", "unilateral-discharge", "누렇거나 녹색 콧물이 주로 한쪽 코에서 나오나요?", 88, "sinus_context", [G["nasal"]], DIFFERENTIATE),
        q("symptom.facial_pain_or_pressure", "Facial Pain or Pressure", "coded", "facial-pain", "눈·볼·이마 주변 통증이나 압박은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 94, "sinus_context", [G["nasal"]], CHARACTERIZE, allowed_values=["none", "mild", "moderate", "severe"]),
        q("symptom.double_worsening_after_initial_improvement", "Worsening after Initial Improvement", "boolean", "double-worsening", "처음에는 나아지다가 다시 뚜렷하게 심해졌나요?", 87, "sinus_context", [G["nasal"]], DIFFERENTIATE),
        q("symptom.reduced_or_lost_smell", "Reduced or Lost Smell", "boolean", "smell", "후각이 줄거나 없어졌나요?", 86, "nasal_context", [G["nasal"]], DIFFERENTIATE),
        q("symptom.sneezing_or_itchy_nose", "Sneezing or Itchy Nose", "boolean", "sneezing-itch", "재채기가 반복되거나 코가 가려운가요?", 93, "allergic_context", [G["allergy"]], DIFFERENTIATE, terminology_binding={"system": SNOMED, "code": "76067001"}),
        q("symptom.itchy_red_watery_eyes", "Itchy Red Watery Eyes", "boolean", "itchy-eyes", "눈이 가렵고 붉거나 눈물이 나나요?", 85, "allergic_context", [G["allergy"]], DIFFERENTIATE),
        q("exposure.upper_respiratory_allergen", "Upper Respiratory Allergen Exposure", "string", "allergen", "꽃가루, 집먼지진드기, 동물, 곰팡이, 목재·밀가루 가루 또는 라텍스 접촉 뒤 심해지나요?", 84, "allergic_context", [G["allergy"], G["context"]], DIFFERENTIATE),
        q("symptom.hoarseness", "Hoarseness", "boolean", "hoarseness", "목소리가 쉬거나 평소와 달라졌나요?", 92, "voice_context", [G["voice"]], CHARACTERIZE, terminology_binding={"system": SNOMED, "code": "50219008"}),
        q("symptom.hoarseness_persistent_three_weeks", "Hoarseness Persistent Three Weeks", "boolean", "persistent-hoarseness", "쉰목소리가 3주 이상 계속되거나 점점 심해지나요?", 83, "persistent_voice_context", [G["voice"]], RISK),
        q("symptom.persistent_mouth_ulcer_or_neck_lump", "Persistent Mouth Ulcer or Neck Lump", "boolean", "persistent-lump-ulcer", "입안 궤양이나 입·목의 덩이가 3주 이상 지속되나요?", 82, "persistent_warning_context", [G["voice"], G["throat"]], RISK),
        q("symptom.upper_respiratory.recurrent", "Recurrent Upper Respiratory Symptoms", "boolean", "recurrent", "같은 증상이 자주 반복되나요?", 81, "recurrence_context", [G["context"]], RISK),
        q("exposure.sick_contact", "Sick Contact", "boolean", "sick-contact", "가족, 직장 또는 학교에 비슷한 증상이 있는 사람이 있나요?", 80, "infectious_context", [G["context"]], DIFFERENTIATE, reuse_existing=True),
        q("patient.smoking_or_inhaled_irritant", "Smoking or Inhaled Irritant Exposure", "boolean", "smoke-irritant", "흡연·전자담배를 하거나 연기·먼지·화학 자극에 노출되나요?", 79, "irritant_context", [G["context"], G["voice"]], RISK),
        q("treatment.upper_respiratory_self_care_response", "Upper Respiratory Self-care Response", "coded", "self-care", "수분 섭취, 가글, 일반 진통제·비강 세척·알레르기약 등을 사용했다면 좋아짐, 변화 없음, 악화 중 무엇인가요? 안 해봤다면 안 해봄으로 답해 주세요.", 78, "management_context", [G["context"]], RISK, allowed_values=["not_tried", "improved", "unchanged", "worsened"]),
    ]
    rules = [
        safety_rule(PREFIX, "breathing-stridor", {"fact": "symptom.severe_breathing_or_stridor", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "unable-swallow-drooling", {"fact": "symptom.unable_to_swallow_saliva_or_drooling", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "rapid-worsening", {"fact": "symptom.upper_respiratory.severe_rapid_worsening", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "allergic-swelling", {"fact": "symptom.sudden_lip_tongue_or_throat_swelling", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "orbital-complication", {"all": [{"fact": "symptom.periorbital_swelling_or_displaced_eye", "equals": True}, {"fact": "symptom.double_vision_painful_eye_movement_or_reduced_vision", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "intracranial-warning", {"fact": "symptom.sinus_intracranial_warning", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "confusion-systemic", {"all": [{"fact": "symptom.confusion", "equals": True}, {"fact": "symptom.fever", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "immunocompromised-fever", {"all": [{"fact": "patient.immunocompromised", "equals": True}, {"fact": "symptom.fever", "equals": True}]}, "urgent", 900),
        safety_rule(PREFIX, "dehydration", {"fact": "symptom.dehydration_or_unable_fluids", "equals": True}, "urgent", 900),
        safety_rule(PREFIX, "deep-neck-warning", {"fact": "symptom.neck_swelling_trismus_or_muffled_voice", "equals": True}, "urgent", 900),
    ]
    extra_nodes = [
        {"id": identifier, "type": "ClinicalGroup", "display": identifier.split(".")[-1].replace("-", " ").title()}
        for identifier in G.values()
    ] + [
        {"id": "hypothesis.upper-respiratory.immediate-safety", "type": "Hypothesis", "display": "Immediate Upper Airway Safety Warning Pattern"},
        {"id": "hypothesis.upper-respiratory.throat", "type": "Hypothesis", "display": "Throat Symptom Pattern"},
        {"id": "hypothesis.upper-respiratory.sinus", "type": "Hypothesis", "display": "Nasal and Sinus Symptom Pattern"},
        {"id": "hypothesis.upper-respiratory.allergic", "type": "Hypothesis", "display": "Allergic Upper Respiratory Pattern"},
        {"id": "hypothesis.upper-respiratory.persistence", "type": "Hypothesis", "display": "Persistent Voice or Lesion Warning Pattern"},
    ]
    group_edges = [
        [G["safety"], "hypothesis.upper-respiratory.immediate-safety"],
        [G["throat"], "hypothesis.upper-respiratory.throat"],
        [G["nasal"], "hypothesis.upper-respiratory.sinus"],
        [G["allergy"], "hypothesis.upper-respiratory.allergic"],
        [G["voice"], "hypothesis.upper-respiratory.persistence"],
    ]
    return {
        "id": "knowledge.generated.upper-respiratory-symptoms",
        "version": VERSION, "status": "research_only",
        "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-upper-respiratory-symptoms-research",
        "default_refresh": default_refresh(),
        "extra_nodes": extra_nodes, "group_hypothesis_edges": group_edges,
        "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def build_mrcm():
    concepts = [
        {"code": "162397003", "display": "Pain in throat (finding)", "attribute_count_returned": 20},
        {"code": "232209000", "display": "Nasal obstruction (disorder)", "attribute_count_returned": 22},
        {"code": "64531003", "display": "Nasal discharge (finding)", "attribute_count_returned": 0},
        {"code": "76067001", "display": "Sneezing (finding)", "attribute_count_returned": 20},
        {"code": "50219008", "display": "Hoarse (finding)", "attribute_count_returned": 20},
    ]
    supported = [item for item in concepts if item["attribute_count_returned"] > 0]
    checks = [
        {"focus_code": concept["code"], "attribute_code": attribute, "allowed": True}
        for concept in supported for attribute in ("363698007", "246112005")
    ]
    return {
        "id": MRCM_REF, "version": VERSION,
        "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SNOMED, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": concepts, "checks": checks,
        "unsupported_checks": [{"focus_code": "64531003", "reason": "STOM allowed-attribute endpoint returned an empty array; no post-coordination assertion made."}],
        "validation": {"method": "build_time_live_mrcm_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "partial_provisional_pass"},
        "provenance": provenance(["source.stom.mrcm.upper-respiratory.20260714"]),
    }


def build_sources():
    definitions = [
        ("source.nhs.sore-throat.2024", "NHS", "Sore throat", "reviewed-2024-04-08", "https://www.nhs.uk/symptoms/sore-throat/", "public_health_guidance", 7),
        ("source.nice.ng84.sore-throat.2025", "NICE", "Sore throat (acute): antimicrobial prescribing", "NG84-updated-2025", "https://www.nice.org.uk/guidance/ng84/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nice.ng79.sinusitis.2026", "NICE", "Sinusitis (acute): antimicrobial prescribing", "NG79-updated-2026", "https://www.nice.org.uk/guidance/ng79/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nhs.allergic-rhinitis.2026", "NHS", "Allergic rhinitis", "accessed-2026-07-14", "https://www.nhs.uk/conditions/allergic-rhinitis/", "public_health_guidance", 7),
        ("source.stom.mrcm.upper-respiratory.20260714", "Infoclinic", "STOM upper respiratory SNOMED CT lookup and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/162397003", "terminology_server", 30),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, days in definitions:
        artifacts.append({
            "id": sid,
            "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata",
            "publisher": publisher, "title": title, "version": version, "url": url,
            "language": "en",
            "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached",
            "license_status": "restricted" if publisher != "NHS" else "unknown",
            "complete": False, "monitor_profile": profile, "monitor_interval_days": days,
            "last_monitored_at": "2026-07-14",
            "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"),
            "assertions": ["Build-Time metadata only; Runtime does not browse this source and the generated clinical content remains unreviewed."],
        })
    research = {
        "id": "source-manifest.primary-care-upper-respiratory-symptoms-research",
        "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only",
        "artifacts": artifacts,
        "provenance": provenance([item[0] for item in definitions]),
    }
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.repository.context", "repository_specification", "docs/context", True),
        ("source.catalog.primary-care-rfe", "knowledge_catalog", "knowledge/catalog/primary-care-rfe.json", True),
        ("source.registry.shared-primary-care-facts", "fact_registry", "knowledge/shared/primary-care-facts.json", True),
        ("source.generated.primary-care-upper-respiratory", "generated_clinical_knowledge", "knowledge/generated/upper-respiratory/upper-respiratory-symptoms.json", True),
        ("source.mapping.snomed-mrcm.upper-respiratory", "terminology_mapping", "mappings/terminology/snomed-mrcm-upper-respiratory-symptoms.json", False),
        ("source.external.primary-care-upper-respiratory-research", "external_source_manifest", "sources/manifests/primary-care-upper-respiratory-symptoms-research.json", False),
        ("source.policy.primary-care-upper-respiratory-completion", "runtime_policy", "policies/primary-care-upper-respiratory-symptoms-completion.json", True),
    ]
    primary = {
        "id": "source-manifest.primary-care-upper-respiratory-symptoms",
        "version": VERSION, "acquired_at": CREATED_AT,
        "artifacts": [{
            "id": sid, "kind": kind, "publisher": "clinical-interview-platform",
            "version": VERSION, "language": "en", "path": path,
            "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown",
            "complete": complete,
        } for sid, kind, path, complete in paths],
        "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md", "sources/manifests/primary-care-upper-respiratory-symptoms-research.json"]),
    }
    return primary, research


def build_cases(fragment):
    true_map = {
        "breathing-stridor": ["symptom.severe_breathing_or_stridor"],
        "unable-swallow-drooling": ["symptom.unable_to_swallow_saliva_or_drooling"],
        "rapid-worsening": ["symptom.upper_respiratory.severe_rapid_worsening"],
        "allergic-swelling": ["symptom.sudden_lip_tongue_or_throat_swelling"],
        "orbital-complication": ["symptom.periorbital_swelling_or_displaced_eye", "symptom.double_vision_painful_eye_movement_or_reduced_vision"],
        "intracranial-warning": ["symptom.sinus_intracranial_warning"],
        "confusion-systemic": ["symptom.confusion", "symptom.fever"],
        "immunocompromised-fever": ["patient.immunocompromised", "symptom.fever"],
        "dehydration": ["symptom.dehydration_or_unable_fluids"],
        "deep-neck-warning": ["symptom.neck_swelling_trismus_or_muffled_voice"],
    }
    cases = {}
    for index, item in enumerate(fragment["safety_rules"], 1):
        key = item["id"].split("safety.", 1)[1]
        level = item["then"]["safety_level"]
        cases[f"UPPER-{key.upper()}-001.json"] = {
            "id": f"UPPER-{key.upper()}-001", "simulation_language": "ko",
            "persona": {"age": 30 + index},
            "initial_statement": {"ko": "목과 코가 불편해요."},
            "hidden_state": {fact_id: {"value": True} for fact_id in true_map[key]},
            "expected": {
                "expected_safety_level": level,
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [item["id"]],
                "expected_max_turns": 22,
                "forbidden_assertions": ["diagnosis.epiglottitis", "diagnosis.sinusitis", "recommendation.antibiotic"],
            },
            "provenance": provenance(SOURCES),
        }
    hidden = {}
    for item in fragment["entries"]:
        fact = item["fact"]
        fid = fact["id"]
        if fact["value_type"] == "boolean":
            hidden[fid] = {"value": fid == "symptom.upper_respiratory.current"}
        elif fact["value_type"] == "quantity":
            hidden[fid] = {"value": {"amount": 3, "unit": "days"}}
        elif fact["value_type"] == "coded":
            hidden[fid] = {"value": fact.get("allowed_values", ["none"])[0]}
        else:
            hidden[fid] = {"value": "없음"}
    declined = "exposure.upper_respiratory_allergen"
    hidden.pop(declined)
    cases["UPPER-DATA-ABSENT-001.json"] = {
        "id": "UPPER-DATA-ABSENT-001", "simulation_language": "ko",
        "persona": {"age": 37}, "initial_statement": {"ko": "코가 막히고 목이 조금 아파요."},
        "hidden_state": hidden,
        "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}},
        "expected": {
            "expected_data_absent_reasons": {declined: "asked-declined"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 40,
            "forbidden_assertions": ["diagnosis.common_cold", "recommendation.antibiotic"],
        },
        "provenance": provenance(["source.nice.ng84.sore-throat.2025", "specifications/clinical-memory.md"]),
    }
    return cases


def main():
    fragment = build_fragment()
    graph, rules = base_graph_and_rules(
        prefix=PREFIX, rfe=RFE, display="Upper Respiratory Symptoms",
        intents=[
            ("intent.characterize_symptom", "Characterize Symptom"),
            ("intent.screen_red_flags", "Screen Red Flags"),
            ("intent.differentiate_common_causes", "Differentiate Common Sources"),
            ("intent.risk_assessment", "Risk Assessment"),
        ],
    )
    primary, research = build_sources()
    policy = completion_policy(
        prefix="upper-respiratory-symptoms", fragment=fragment,
        presentation_fact="symptom.upper_respiratory.current", question_budget=40,
        source_refs=SOURCES,
    )
    for path, document in [
        ("knowledge/base/primary-care-upper-respiratory-symptoms.json", graph),
        ("rules/base/primary-care-upper-respiratory-symptoms.json", rules),
        ("knowledge/generated/upper-respiratory/upper-respiratory-symptoms.json", fragment),
        ("mappings/terminology/snomed-mrcm-upper-respiratory-symptoms.json", build_mrcm()),
        ("sources/manifests/primary-care-upper-respiratory-symptoms.json", primary),
        ("sources/manifests/primary-care-upper-respiratory-symptoms-research.json", research),
        ("policies/primary-care-upper-respiratory-symptoms-completion.json", policy),
    ]:
        write_json(path, document)
    for filename, case in build_cases(fragment).items():
        write_json(f"simulation/patients/upper-respiratory/{filename}", case)


if __name__ == "__main__":
    main()
