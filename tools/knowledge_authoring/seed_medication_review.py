#!/usr/bin/env python3
"""Materialize the unreviewed medication-review research profile."""
from __future__ import annotations

import json
from pathlib import Path
from profile_support import normalize_source_monitoring


ROOT = Path(__file__).resolve().parents[2]
V = "0.1.0"
NOW = "2026-07-14T00:00:00Z"
MODES = ["chat", "face_to_face", "telephone", "video"]
SOURCES = [
    "source.nice.ng5.medicines-optimisation.2019",
    "source.nice.cg183.drug-allergy.2014",
    "source.nhs.poisoning.2025",
    "source.nhs.anticoagulant-bleeding.2024",
    "source.nhs.anaphylaxis.2026",
    "source.nhs.stevens-johnson.2026",
    "source.nhs.hypoglycaemia.2026",
    "source.nhs-england.opioid-respiratory-depression.2020",
]


def prov(refs=None):
    return {"created_by": {"type": "ai", "id": "codex-gpt5"}, "created_at": NOW,
            "source_refs": refs or SOURCES, "review_status": "unreviewed", "version": V}


def write(path, data):
    data = normalize_source_monitoring(data)
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


G = {
    "safety": "group.medication-review.immediate-safety",
    "reconcile": "group.medication-review.reconciliation",
    "use": "group.medication-review.actual-use",
    "benefit": "group.medication-review.benefit-harm",
    "monitor": "group.medication-review.monitoring-risk",
    "preference": "group.medication-review.preference-support",
}


def e(fid, display, vt, key, wording, score, reason, groups, *, allowed=None,
      safety=False, reuse=False, intents=None, terminology=None):
    fact = {"id": fid, "display": display, "value_type": vt}
    if allowed: fact["allowed_values"] = allowed
    if safety: fact["safety_relevant"] = True
    if terminology: fact["terminology_binding"] = terminology
    out = {
        "fact": fact,
        "target": {"id": f"target.medication-review.{key}", "display": display,
                   "intents": intents or ["intent.medication_reconciliation"]},
        "question": {"id": f"question.medication-review.{key}", "wording": wording,
                     "language": "ko", "mode": MODES},
        "priority": [{"branch": "any", "score": score, "reason": reason}],
        "supports": groups,
    }
    if reuse: out["reuse_existing"] = True
    return out


def rule(key, when, level, priority):
    return {"id": f"rule.medication-review.safety.{key}", "priority": priority,
            "when": when, "then": {"safety_level": level, "action": "human_handoff",
                                     "suppress_routine": True}}


def fragment():
    entries = [
        e("medication.review.requested", "Medication Review Requested", "boolean", "requested", "복용 중인 약을 확인하고 안전성·효과·불편을 함께 검토하려는 방문이 맞나요?", 130, "confirm_encounter", [G["reconcile"]], terminology={"system": "http://snomed.info/sct", "code": "182836005"}),
        e("medication.review.purpose", "Medication Review Purpose", "coded", "purpose", "주된 목적은 약 목록 확인, 효과 확인, 부작용 상담, 복용법 질문, 약을 줄이거나 바꾸는 상담, 퇴원 후 대조 중 무엇인가요?", 105, "review_purpose", [G["reconcile"], G["preference"]], allowed=["reconcile", "effectiveness", "adverse_effect", "instructions", "change_request", "post_discharge", "other"]),
        e("medication.current_prescribed_list", "Current Prescribed Medicines", "string", "prescribed-list", "현재 처방받아 실제 사용하는 약의 이름, 함량, 제형, 1회 용량, 복용 시간과 횟수를 알려주세요. 모르면 약 봉투나 사진 내용을 그대로 적어도 됩니다.", 104, "reconcile_prescribed", [G["reconcile"]]),
        e("medication.current_otc_list", "Current Over-the-counter Medicines", "string", "otc-list", "진통제, 감기약, 위장약처럼 처방 없이 사서 쓰는 약이 있나요?", 101, "reconcile_otc", [G["reconcile"]]),
        e("medication.current_supplement_list", "Current Supplements and Complementary Medicines", "string", "supplement-list", "건강기능식품, 한약, 비타민 또는 허브 제품을 사용하나요?", 100, "reconcile_supplements", [G["reconcile"]]),
        e("medication.non_oral_products", "Injections Inhalers Topicals and As-needed Medicines", "string", "nonoral-list", "주사, 흡입기, 패치, 안약, 연고, 좌약 또는 필요할 때만 쓰는 약도 있나요?", 99, "reconcile_nonoral", [G["reconcile"]]),
        e("medication.indications_known", "Medicine Indications Known", "coded", "indications", "각 약을 왜 사용하는지 모두 앎, 일부만 앎, 모름 중 어디에 해당하나요?", 94, "indication_understanding", [G["reconcile"], G["preference"]], allowed=["all_known", "partly_known", "unknown"]),
        e("medication.actual_use_differs", "Actual Use Differs from Label", "boolean", "actual-use", "처방전이나 약 봉투의 지시와 다르게 복용하는 약이 있나요?", 103, "reconciliation_discrepancy", [G["reconcile"], G["use"]]),
        e("medication.recent_start_stop_dose_change", "Recent Medicine Start Stop or Dose Change", "string", "recent-change", "최근 시작·중단·용량 변경한 약과 변경 이유, 변경한 날짜를 알려주세요.", 98, "recent_change", [G["reconcile"], G["monitor"]]),
        e("medication.last_dose_critical_or_infrequent", "Last Dose of Infrequent or Critical Medicine", "string", "last-dose", "주 1회·월 1회 약, 주사 또는 꼭 시간을 맞춰야 하는 약의 마지막 투여 시각을 알고 있나요?", 88, "last_dose", [G["reconcile"]]),
        e("medication.duplicate_or_unknown_product", "Duplicate or Unidentified Medicine", "boolean", "duplicate-unknown", "같은 성분일 수 있는 약을 여러 곳에서 받았거나 이름을 알 수 없는 약이 있나요?", 97, "duplication_risk", [G["reconcile"], G["monitor"]]),
        e("medication.multiple_prescribers_or_pharmacies", "Multiple Prescribers or Pharmacies", "boolean", "multiple-sources", "여러 의료기관이나 약국에서 서로 다른 약을 받고 있나요?", 87, "coordination_context", [G["reconcile"]]),
        e("allergy.drug_status", "Drug Allergy Status", "coded", "allergy-status", "약물 알레르기는 있음, 알려진 것 없음, 확인할 수 없음 중 무엇인가요?", 102, "allergy_reconciliation", [G["reconcile"], G["safety"]], allowed=["known", "none_known", "unable_to_ascertain"]),
        e("allergy.drug_reaction_details", "Drug Allergy Reaction Details", "string", "allergy-details", "알레르기가 있다면 약 이름, 증상과 심한 정도, 발생 시기를 알려주세요.", 96, "allergy_documentation", [G["reconcile"], G["safety"]]),
        e("medication.missed_dose_frequency", "Missed Dose Frequency", "coded", "missed-doses", "최근 한 달 동안 약을 빼먹은 정도는 없음, 드물게, 주 1회 이상, 거의 매일 중 무엇인가요?", 93, "adherence", [G["use"]], allowed=["none", "rare", "weekly_or_more", "almost_daily"]),
        e("medication.intentional_nonadherence_reason", "Intentional Non-adherence Reason", "string", "intentional-nonadherence", "효과 걱정, 부작용, 약이 너무 많음, 비용, 개인 신념 때문에 일부러 줄이거나 거른 약이 있나요?", 86, "adherence_reason", [G["use"], G["preference"]]),
        e("medication.administration_difficulty", "Medicine Administration Difficulty", "string", "administration-difficulty", "삼키기, 포장 열기, 흡입기·주사 사용, 용량 재기 또는 시간 기억에 어려움이 있나요?", 85, "administration_support", [G["use"], G["preference"]]),
        e("medication.access_or_cost_problem", "Medicine Access or Cost Problem", "boolean", "access-cost", "처방 갱신, 약 구하기, 비용 또는 이동 문제로 약을 못 쓴 적이 있나요?", 84, "access_support", [G["use"], G["preference"]]),
        e("medication.perceived_benefit", "Perceived Medicine Benefit", "coded", "benefit", "현재 약의 효과는 좋음, 일부 효과, 효과 없음, 판단 어려움 중 어디에 가깝나요?", 83, "effectiveness", [G["benefit"]], allowed=["good", "partial", "none", "uncertain"], intents=["intent.medication_review"]),
        e("medication.suspected_adverse_effects", "Suspected Adverse Effects", "string", "adverse-effects", "약을 시작하거나 바꾼 뒤 새로 생긴 불편이나 부작용이 있나요? 증상과 시작 시점을 알려주세요.", 95, "adverse_effect", [G["benefit"], G["safety"]], intents=["intent.medication_review", "intent.screen_red_flags"]),
        e("medication.monitoring_due_or_overdue", "Medicine Monitoring Due or Overdue", "boolean", "monitoring", "혈액검사, 혈압·혈당, 심전도 또는 약물 농도처럼 약 때문에 정기 확인할 검사가 밀렸나요?", 82, "monitoring", [G["monitor"]], intents=["intent.risk_assessment"]),
        e("medication.recent_care_transition", "Recent Care Transition", "boolean", "care-transition", "최근 퇴원, 응급실 방문, 요양시설 이동 또는 다른 병원 진료 후 약 목록이 바뀌었나요?", 92, "reconciliation_transition", [G["reconcile"]]),
        e("patient.pregnant_planning_or_breastfeeding", "Pregnant Planning Pregnancy or Breastfeeding", "boolean", "pregnancy", "현재 임신 중이거나 임신을 계획하거나 수유 중인가요?", 91, "pregnancy_review", [G["monitor"]], intents=["intent.risk_assessment"]),
        e("history.kidney_impairment", "Kidney Impairment", "boolean", "kidney", "신장 기능 저하, 투석 또는 최근 신장검사 이상을 들은 적이 있나요?", 90, "dose_risk", [G["monitor"]], intents=["intent.risk_assessment"]),
        e("history.liver_impairment", "Liver Impairment", "boolean", "liver", "간질환, 황달 또는 최근 간기능검사 이상을 들은 적이 있나요?", 89, "dose_risk", [G["monitor"]], intents=["intent.risk_assessment"]),
        e("medication.patient_priority_or_question", "Patient Medication Priority or Question", "string", "priority-question", "약 검토에서 가장 해결하고 싶은 질문이나 목표는 무엇인가요?", 80, "shared_decision", [G["preference"]], intents=["intent.medication_review"]),
        e("medication.possible_poisoning_or_extra_dose", "Possible Poisoning or Extra Dose", "boolean", "poisoning", "약을 정해진 양보다 많이 먹었거나 잘못된 약을 먹었을 가능성이 있나요?", 129, "poisoning_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
        e("mental_health.intentional_overdose_or_self_harm", "Intentional Overdose or Self-harm", "boolean", "intentional-overdose", "자해할 의도로 약을 복용했거나 지금 약으로 자신을 해칠 생각·계획이 있나요?", 128, "self_harm_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
        e("symptom.throat_or_tongue_swelling", "Throat or Tongue Swelling after Medicine", "boolean", "airway-swelling", "약을 사용한 뒤 입술, 혀 또는 목이 갑자기 붓거나 삼키기 어려운가요?", 127, "anaphylaxis_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
        e("symptom.severe_breathing_difficulty", "Severe Breathing Difficulty after Medicine", "boolean", "breathing", "약을 사용한 뒤 숨이 매우 차거나 쌕쌕거리고 말하기 어려운가요?", 126, "anaphylaxis_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
        e("symptom.unresponsive_or_slow_breathing", "Unresponsive or Slow Breathing", "boolean", "slow-breathing", "깨우기 어렵거나 의식이 없고, 호흡이 매우 느리거나 얕은가요?", 125, "opioid_toxicity_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
        e("symptom.severe_active_bleeding", "Severe or Uncontrolled Bleeding", "boolean", "severe-bleeding", "피가 멈추지 않거나 피를 토함, 검은 변·혈변, 혈뇨, 머리를 다친 뒤 심한 두통 같은 증상이 있나요?", 124, "bleeding_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
        e("medication.anticoagulant_current", "Current Anticoagulant", "boolean", "anticoagulant", "와파린, 아픽사반, 리바록사반 같은 항응고제를 복용하나요?", 123, "bleeding_context", [G["safety"], G["reconcile"]], safety=True, intents=["intent.screen_red_flags"]),
        e("symptom.severe_hypoglycaemia", "Severe Hypoglycaemia", "boolean", "hypoglycaemia", "당뇨약 사용 중 의식이 흐리거나 경련·실신이 있거나 안전하게 삼킬 수 없는 저혈당이 의심되나요?", 122, "hypoglycaemia_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
        e("symptom.drug_related_blistering_mucosal_rash", "Blistering or Mucosal Rash after Medicine", "boolean", "severe-rash", "새 약 뒤 피부가 아프게 물집·박리되거나 입·눈·성기 점막이 헐었나요?", 121, "severe_skin_reaction_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
        e("medication.abrupt_stop_with_withdrawal", "Abrupt Stop with Significant Withdrawal", "boolean", "withdrawal", "의존이나 금단을 일으킬 수 있는 약을 갑자기 끊은 뒤 심한 떨림, 혼란, 경련 또는 견디기 어려운 증상이 있나요?", 120, "withdrawal_gate", [G["safety"]], safety=True, intents=["intent.screen_red_flags"]),
    ]
    rules = [
        rule("possible-poisoning", {"fact": "medication.possible_poisoning_or_extra_dose", "equals": True}, "emergency", 1000),
        rule("intentional-overdose", {"fact": "mental_health.intentional_overdose_or_self_harm", "equals": True}, "emergency", 1000),
        rule("airway-swelling", {"fact": "symptom.throat_or_tongue_swelling", "equals": True}, "emergency", 1000),
        rule("breathing", {"fact": "symptom.severe_breathing_difficulty", "equals": True}, "emergency", 1000),
        rule("unresponsive-slow-breathing", {"fact": "symptom.unresponsive_or_slow_breathing", "equals": True}, "emergency", 1000),
        rule("anticoagulant-bleeding", {"all": [{"fact": "symptom.severe_active_bleeding", "equals": True}, {"fact": "medication.anticoagulant_current", "equals": True}]}, "emergency", 1000),
        rule("severe-hypoglycaemia", {"fact": "symptom.severe_hypoglycaemia", "equals": True}, "emergency", 1000),
        rule("blistering-mucosal-rash", {"fact": "symptom.drug_related_blistering_mucosal_rash", "equals": True}, "emergency", 1000),
        rule("severe-withdrawal", {"fact": "medication.abrupt_stop_with_withdrawal", "equals": True}, "urgent", 900),
    ]
    extras = [{"id": x, "type": "ClinicalGroup", "display": x.split(".")[-1].replace("-", " ").title()} for x in G.values()]
    extras += [{"id": f"hypothesis.medication-review.{x}", "type": "Hypothesis", "display": y} for x, y in [
        ("immediate-safety", "Immediate Medicine Safety Warning Pattern"),
        ("reconciliation", "Medication Reconciliation Discrepancy Pattern"),
        ("benefit-harm", "Medicine Benefit and Harm Pattern"),
        ("support", "Medicine Use Support Need Pattern")]]
    edges = [[G["safety"], "hypothesis.medication-review.immediate-safety"], [G["reconcile"], "hypothesis.medication-review.reconciliation"], [G["benefit"], "hypothesis.medication-review.benefit-harm"], [G["preference"], "hypothesis.medication-review.support"]]
    refresh = {"class": "clinical_guideline", "last_assessed_at": "2026-07-14", "monitor_interval_days": 1,
               "full_review_interval_days": 180, "next_monitor_at": "2026-07-15", "next_full_review_at": "2027-01-10",
               "policy_id": "policy.knowledge-refresh", "overdue_behavior": {"production": "exclude_or_require_review", "research_test": "allow_with_warning"}}
    return {"id": "knowledge.generated.medication-review", "version": V, "status": "research_only",
            "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-medication-review-research",
            "default_refresh": refresh, "extra_nodes": extras, "group_hypothesis_edges": edges,
            "safety_rules": rules, "entries": entries, "provenance": prov()}


def base():
    def n(i, t, d, s): return {"id": i, "type": t, "display": d, "version": V, "status": "research_only", "provenance": prov([s])}
    ns = [n("context.primary_care", "EncounterContext", "Primary Care", "docs/context/002-encounter-context.md"),
          n("rfe.medication_review", "ReasonForEncounter", "Medication Review", "knowledge/catalog/primary-care-rfe.json"),
          n("intent.medication_reconciliation", "ClinicalIntent", "Medication Reconciliation", "docs/context/001-clinical-intent.md"),
          n("intent.medication_review", "ClinicalIntent", "Medication Benefit and Harm Review", "docs/context/001-clinical-intent.md"),
          n("intent.screen_red_flags", "ClinicalIntent", "Screen Red Flags", "docs/context/001-clinical-intent.md"),
          n("intent.risk_assessment", "ClinicalIntent", "Risk Assessment", "docs/context/001-clinical-intent.md")]
    targets = ["intent.medication_reconciliation", "intent.medication_review", "intent.screen_red_flags", "intent.risk_assessment"]
    es = [{"id": f"edge.medication-review.{i:03d}", "type": "SUGGESTS", "from": "rfe.medication_review", "to": t,
           "version": V, "provenance": prov(["docs/context/001-clinical-intent.md"])} for i, t in enumerate(targets, 1)]
    es.insert(0, {"id": "edge.medication-review.000", "type": "ACTIVATES", "from": "context.primary_care", "to": "intent.medication_reconciliation", "version": V, "provenance": prov(["docs/context/002-encounter-context.md"])})
    graph = {"id": "knowledge.primary-care-medication-review", "version": V, "nodes": ns, "edges": es, "provenance": prov(["knowledge/catalog/primary-care-rfe.json"])}
    rules = {"id": "rules.primary-care-medication-review", "version": V, "rules": [{"id": "rule.activate.medication-review", "type": "activation", "priority": 100, "when": {"rfe": "rfe.medication_review"}, "then": {"activate_intents": targets}, "version": V, "status": "research_only", "provenance": prov(["specifications/reasoning-loop.md"])}], "provenance": prov(["specifications/reasoning-loop.md"])}
    return graph, rules


def mrcm():
    return {"id": "mapping.snomed-mrcm.medication-review", "version": V, "status": "research_only", "review_status": "unreviewed",
            "terminology": {"system": "http://snomed.info/sct", "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
            "focus_concepts": [{"code": "182836005", "display": "Review of medication (procedure)"}], "checks": [],
            "validation": {"method": "build_time_live_mrcm_summary", "checked_at": NOW, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass", "attribute_count_returned": 24},
            "provenance": prov(["source.stom.mrcm.medication-review.20260714"])}


def manifests():
    source_defs = [
        ("source.nice.ng5.medicines-optimisation.2019", "NICE", "Medicines optimisation: reconciliation and medication review", "https://www.nice.org.uk/guidance/ng5/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nice.cg183.drug-allergy.2014", "NICE", "Drug allergy: diagnosis and management", "https://www.nice.org.uk/guidance/cg183/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nhs.poisoning.2025", "NHS", "Poisoning", "https://www.nhs.uk/conditions/poisoning/", "public_health_guidance", 7),
        ("source.nhs.anticoagulant-bleeding.2024", "NHS", "Anticoagulant medicines: side effects", "https://www.nhs.uk/medicines/anticoagulants/side-effects/", "public_health_guidance", 7),
        ("source.nhs.anaphylaxis.2026", "NHS", "Anaphylaxis", "https://www.nhs.uk/conditions/anaphylaxis/", "public_health_guidance", 7),
        ("source.nhs.stevens-johnson.2026", "NHS", "Stevens-Johnson syndrome", "https://www.nhs.uk/conditions/stevens-johnson-syndrome/", "public_health_guidance", 7),
        ("source.nhs.hypoglycaemia.2026", "NHS", "Low blood sugar (hypoglycaemia)", "https://www.nhs.uk/conditions/low-blood-sugar-hypoglycaemia/", "public_health_guidance", 7),
        ("source.nhs-england.opioid-respiratory-depression.2020", "NHS England", "Opioid respiratory depression safety alert", "https://www.england.nhs.uk/2014/11/risk-distress-death-inappropriate-doses-naloxone-patients-long-term-opioid-opiate-treatment/", "clinical_guideline", 1),
        ("source.stom.mrcm.medication-review.20260714", "Infoclinic", "STOM SNOMED CT medication review lookup and MRCM summary", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/182836005", "terminology_server", 30),
    ]
    arts = []
    for sid, pub, title, url, profile, days in source_defs:
        arts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata",
                     "publisher": pub, "title": title, "version": "accessed-2026-07-14", "url": url, "language": "en",
                     "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached",
                     "license_status": "restricted" if pub != "NHS" else "unknown", "complete": False,
                     "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-14",
                     "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"),
                     "assertions": ["Used only as Build-Time source metadata; runtime does not query this source and generated content remains unreviewed."]})
    research = {"id": "source-manifest.primary-care-medication-review-research", "version": V, "acquired_at": NOW, "status": "research_only", "artifacts": arts, "provenance": prov([x[0] for x in source_defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.repository.context", "repository_specification", "docs/context", True),
             ("source.catalog.primary-care-rfe", "knowledge_catalog", "knowledge/catalog/primary-care-rfe.json", True), ("source.registry.shared-primary-care-facts", "fact_registry", "knowledge/shared/primary-care-facts.json", True),
             ("source.generated.primary-care-medication-review", "generated_clinical_knowledge", "knowledge/generated/medication/medication-review/medication-review.json", True),
             ("source.mapping.snomed-mrcm.medication-review", "terminology_mapping", "mappings/terminology/snomed-mrcm-medication-review.json", False),
             ("source.external.primary-care-medication-review-research", "external_source_manifest", "sources/manifests/primary-care-medication-review-research.json", False),
             ("source.policy.primary-care-medication-review-completion", "runtime_policy", "policies/primary-care-medication-review-completion.json", True)]
    items = [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": V, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths]
    primary = {"id": "source-manifest.primary-care-medication-review", "version": V, "acquired_at": NOW, "artifacts": items, "provenance": prov(["FOUNDATION.md", "PROJECT_CONTEXT.md", "sources/manifests/primary-care-medication-review-research.json"])}
    return primary, research


def policy_and_cases(f):
    safety = []
    def collect(c):
        if "fact" in c and c["fact"] not in safety: safety.append(c["fact"])
        for child in c.get("all", []): collect(child)
    for r in f["safety_rules"]: collect(r["when"])
    ids = [x["fact"]["id"] for x in f["entries"]]
    always = ["medication.review.requested", *safety]
    policy = {"id": "policy.primary-care-medication-review-completion", "version": V, "status": "research_only",
              "addressed_fact_states": ["known", "unknown", "not_applicable"], "required_facts": {"always": always, "routine": [x for x in ids if x not in always]},
              "clarification_facts_by_rule": {}, "question_budget": {"routine": 40, "clarify": 12}, "provenance": prov()}
    true_map = {
        "possible-poisoning": ["medication.possible_poisoning_or_extra_dose"], "intentional-overdose": ["mental_health.intentional_overdose_or_self_harm"],
        "airway-swelling": ["symptom.throat_or_tongue_swelling"], "breathing": ["symptom.severe_breathing_difficulty"],
        "unresponsive-slow-breathing": ["symptom.unresponsive_or_slow_breathing"], "anticoagulant-bleeding": ["symptom.severe_active_bleeding", "medication.anticoagulant_current"],
        "severe-hypoglycaemia": ["symptom.severe_hypoglycaemia"], "blistering-mucosal-rash": ["symptom.drug_related_blistering_mucosal_rash"],
        "severe-withdrawal": ["medication.abrupt_stop_with_withdrawal"]}
    cases = {}
    for i, r in enumerate(f["safety_rules"], 1):
        key = r["id"].split("safety.", 1)[1]; level = r["then"]["safety_level"]
        cases[f"MED-{key.upper()}-001.json"] = {"id": f"MED-{key.upper()}-001", "simulation_language": "ko", "persona": {"age": 40+i},
            "initial_statement": {"ko": "복용약을 검토하고 싶어요."}, "hidden_state": {x: {"value": True} for x in true_map[key]},
            "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation",
                         "expected_triggered_rules_contains": [r["id"]], "expected_max_turns": 20, "forbidden_assertions": ["diagnosis.drug_poisoning", "recommendation.stop_medication"]},
            "provenance": prov()}
    hidden = {}
    for x in f["entries"]:
        fact=x["fact"]; fid=fact["id"]; vt=fact["value_type"]
        hidden[fid]={"value": (fid=="medication.review.requested") if vt=="boolean" else (fact.get("allowed_values", ["none"])[0] if vt=="coded" else "없음")}
    declined="medication.intentional_nonadherence_reason"; hidden.pop(declined)
    cases["MED-DATA-ABSENT-001.json"]={"id":"MED-DATA-ABSENT-001","simulation_language":"ko","persona":{"age":62},"initial_statement":{"ko":"복용약을 검토하고 싶어요."},"hidden_state":hidden,
        "response_behavior":{declined:{"dataAbsentReason":"asked-declined"}},"expected":{"expected_data_absent_reasons":{declined:"asked-declined"},"expected_safety_level":"routine","expected_stop_reason":"required_targets_addressed_with_absent_data","expected_max_turns":40,"forbidden_assertions":["recommendation.stop_medication"]},"provenance":prov(["source.nice.ng5.medicines-optimisation.2019","specifications/clinical-memory.md"])}
    return policy, cases


def main():
    f=fragment(); graph,rules=base(); primary,research=manifests(); policy,cases=policy_and_cases(f)
    for path,data in [("knowledge/base/primary-care-medication-review.json",graph),("rules/base/primary-care-medication-review.json",rules),
        ("knowledge/generated/medication/medication-review/medication-review.json",f),("mappings/terminology/snomed-mrcm-medication-review.json",mrcm()),
        ("sources/manifests/primary-care-medication-review.json",primary),("sources/manifests/primary-care-medication-review-research.json",research),
        ("policies/primary-care-medication-review-completion.json",policy)]: write(path,data)
    for name,case in cases.items(): write("simulation/patients/medication/medication-review/"+name,case)


if __name__ == "__main__": main()
