#!/usr/bin/env python3
"""Materialize the unreviewed grouped palpitations research profile."""
from __future__ import annotations

from profile_support import (
    CREATED_AT, VERSION, base_graph_and_rules, completion_policy,
    default_refresh, entry, provenance, safety_rule, write_json,
)

PREFIX = "palpitations"
RFE = "rfe.palpitations"
MRCM_REF = "mapping.snomed-mrcm.palpitations"
SNOMED = "http://snomed.info/sct"
SOURCES = [
    "source.nhs.heart-palpitations.2026",
    "source.nice.ng196.atrial-fibrillation.2021",
    "source.nice.cg109.blackouts.2023",
]
G = {
    "safety": "group.palpitations.immediate-safety",
    "rhythm": "group.palpitations.rhythm-characterization",
    "associated": "group.palpitations.associated-symptoms",
    "trigger": "group.palpitations.triggers-context",
    "risk": "group.palpitations.cardiac-risk",
}
CHARACTERIZE = ["intent.characterize_symptom"]
SAFETY = ["intent.screen_red_flags"]
RISK = ["intent.risk_assessment"]
DIFFERENTIATE = ["intent.differentiate_common_causes"]


def q(fid, display, vt, key, wording, score, reason, groups, intents, **kwargs):
    return entry(PREFIX, fid, display, vt, key, wording, score, reason, groups,
                 intents=intents, **kwargs)


def build_fragment():
    entries = [
        q("symptom.palpitations.current", "Current Palpitations", "boolean", "current", "지금도 가슴이 두근거리거나 심장이 빠르거나 불규칙하게 뛰는 느낌이 있나요?", 130, "confirm_current_state", [G["safety"], G["rhythm"]], CHARACTERIZE, safety_relevant=True, terminology_binding={"system": SNOMED, "code": "80313002"}, mrcm_ref=MRCM_REF),
        q("symptom.chest_pain", "Chest Pain", "boolean", "chest-pain", "두근거림과 함께 가슴 통증이나 압박감이 있나요?", 129, "emergency_gate", [G["safety"], G["associated"]], SAFETY, safety_relevant=True, reuse_existing=True),
        q("symptom.severe_dyspnea", "Severe Shortness of Breath", "boolean", "severe-dyspnea", "숨이 매우 차서 문장을 말하기 어렵거나 가만히 있어도 숨쉬기 힘든가요?", 128, "emergency_gate", [G["safety"], G["associated"]], SAFETY, safety_relevant=True),
        q("symptom.syncope", "Syncope", "boolean", "syncope", "두근거리는 동안 쓰러지거나 의식을 잃은 적이 있나요?", 127, "emergency_gate", [G["safety"], G["associated"]], SAFETY, safety_relevant=True, reuse_existing=True),
        q("symptom.presyncope", "Presyncope", "boolean", "presyncope", "두근거릴 때 쓰러질 것 같거나 눈앞이 캄캄하고 심하게 어지러운가요?", 126, "emergency_gate", [G["safety"], G["associated"]], SAFETY, safety_relevant=True),
        q("symptom.palpitations.persistent_not_settling", "Persistent Palpitations Not Settling", "boolean", "not-settling", "현재 두근거림이 몇 분 이상 계속되며 가라앉지 않나요?", 125, "persistent_episode_gate", [G["safety"], G["rhythm"]], SAFETY, safety_relevant=True),
        q("symptom.new_focal_neurologic_deficit", "New Focal Neurologic Deficit", "boolean", "neurologic-deficit", "새로 한쪽 얼굴·팔·다리에 힘이 빠지거나 말이 어눌해졌나요?", 124, "stroke_gate", [G["safety"], G["associated"]], SAFETY, safety_relevant=True, reuse_existing=True),
        q("symptom.syncope_during_exertion", "Syncope During Exertion", "boolean", "exertional-syncope", "운동하는 도중 두근거림과 함께 의식을 잃었나요?", 123, "urgent_cardiac_gate", [G["safety"], G["risk"]], SAFETY, safety_relevant=True),
        q("history.known_heart_disease", "Known Heart Disease", "boolean", "heart-disease", "부정맥, 심부전, 심근경색, 심장판막질환 또는 선천성 심장질환을 진단받은 적이 있나요?", 122, "cardiac_risk", [G["safety"], G["risk"]], SAFETY + RISK, safety_relevant=True),
        q("symptom.palpitations.worsening_or_frequent", "Worsening or Frequent Palpitations", "boolean", "worsening-frequent", "두근거림이 최근 더 자주 생기거나 더 오래 지속되거나 심해졌나요?", 116, "urgent_review_context", [G["safety"], G["rhythm"]], RISK, safety_relevant=True),
        q("family.sudden_cardiac_death_under_40", "Family Sudden Cardiac Death Under 40", "boolean", "family-sudden-death", "가족 중 40세 전에 원인 모르게 갑자기 사망했거나 유전성 심장질환을 진단받은 사람이 있나요?", 115, "inherited_risk", [G["safety"], G["risk"]], RISK, safety_relevant=True),
        q("symptom.duration", "Symptom Duration", "quantity", "duration", "처음 두근거림을 느낀 것은 언제부터인가요?", 110, "characterize_duration", [G["rhythm"]], CHARACTERIZE, reuse_existing=True),
        q("symptom.palpitations.episode_duration", "Palpitation Episode Duration", "coded", "episode-duration", "한 번 시작하면 보통 얼마나 지속되나요?", 109, "monitoring_context", [G["rhythm"]], CHARACTERIZE, allowed_values=["seconds", "under_5_minutes", "5_to_30_minutes", "30_minutes_to_24_hours", "over_24_hours", "continuous", "unclear"]),
        q("symptom.palpitations.frequency", "Palpitation Frequency", "coded", "frequency", "두근거림은 얼마나 자주 생기나요?", 108, "monitoring_context", [G["rhythm"]], CHARACTERIZE, allowed_values=["single_episode", "less_than_weekly", "weekly", "daily", "multiple_daily", "continuous", "unclear"]),
        q("symptom.palpitations.onset_offset", "Palpitation Onset and Offset", "coded", "onset-offset", "두근거림이 갑자기 시작하고 갑자기 끝나나요, 서서히 변하나요?", 107, "rhythm_characterization", [G["rhythm"]], CHARACTERIZE, allowed_values=["sudden_both", "sudden_onset", "gradual", "variable", "unclear"]),
        q("symptom.palpitations.sensation", "Palpitation Sensation", "coded", "sensation", "느낌은 매우 빠름, 불규칙함, 건너뜀·툭 떨어짐, 세게 뜀 중 무엇에 가깝나요?", 106, "rhythm_characterization", [G["rhythm"]], CHARACTERIZE, allowed_values=["rapid", "irregular", "skipped_extra", "pounding", "mixed", "unclear"]),
        q("observation.pulse_rate_during_episode", "Pulse Rate During Episode", "quantity", "pulse-rate", "증상 중 맥박이나 기기 심박수를 측정했다면 분당 몇 회였나요? 측정하지 않았다면 모름으로 답해 주세요.", 105, "objective_context", [G["rhythm"]], CHARACTERIZE, terminology_binding={"system": SNOMED, "focus_code": "3424008"}, mrcm_ref=MRCM_REF),
        q("observation.pulse_regular_during_episode", "Pulse Regularity During Episode", "coded", "pulse-regularity", "증상 중 맥박은 규칙적, 불규칙, 확인 못함 중 무엇인가요?", 104, "af_detection_context", [G["rhythm"]], CHARACTERIZE, allowed_values=["regular", "irregular", "not_checked", "unclear"]),
        q("symptom.dyspnea", "Shortness of Breath", "boolean", "dyspnea", "두근거릴 때 숨이 차나요?", 103, "associated_symptom", [G["associated"]], CHARACTERIZE, reuse_existing=True),
        q("symptom.dizziness", "Dizziness", "boolean", "dizziness", "두근거릴 때 어지럽거나 휘청거리나요?", 102, "associated_symptom", [G["associated"]], CHARACTERIZE, reuse_existing=True),
        q("symptom.fatigue", "Fatigue", "boolean", "fatigue", "평소보다 쉽게 피곤하거나 운동 능력이 줄었나요?", 91, "associated_context", [G["associated"]], DIFFERENTIATE, reuse_existing=True),
        q("symptom.sweating_or_tremor", "Sweating or Tremor", "boolean", "sweating-tremor", "두근거릴 때 식은땀이나 손 떨림이 있나요?", 90, "associated_context", [G["associated"]], DIFFERENTIATE),
        q("symptom.fever", "Fever", "boolean", "fever", "열이 나거나 최근 감염 증상이 있나요?", 89, "reversible_context", [G["associated"], G["trigger"]], DIFFERENTIATE, reuse_existing=True),
        q("symptom.weight_loss_heat_intolerance", "Weight Loss or Heat Intolerance", "boolean", "thyroid-features", "이유 없는 체중 감소, 더위를 못 견딤, 땀 증가가 있나요?", 88, "thyroid_context", [G["associated"]], DIFFERENTIATE),
        q("symptom.bleeding_or_anemia_features", "Bleeding or Anaemia Features", "boolean", "anemia-features", "최근 출혈, 검은 변·혈변, 생리량 증가, 창백함 또는 심한 피로가 있나요?", 87, "anemia_context", [G["associated"]], DIFFERENTIATE),
        q("trigger.palpitations.exertion", "Exertional Trigger", "boolean", "exertion-trigger", "운동하거나 계단을 오를 때 주로 생기나요?", 99, "trigger_characterization", [G["trigger"], G["risk"]], CHARACTERIZE),
        q("trigger.palpitations.postural", "Postural Trigger", "boolean", "postural-trigger", "앉거나 누웠다가 일어설 때 주로 생기나요?", 86, "trigger_characterization", [G["trigger"]], DIFFERENTIATE),
        q("trigger.palpitations.stress_or_panic", "Stress or Panic Trigger", "boolean", "stress-trigger", "불안, 스트레스 또는 공포감이 심할 때 주로 생기나요?", 85, "trigger_characterization", [G["trigger"]], DIFFERENTIATE),
        q("exposure.caffeine_or_energy_drinks", "Caffeine or Energy Drink Exposure", "string", "caffeine", "커피, 차, 에너지음료를 하루에 얼마나 마시나요?", 84, "trigger_context", [G["trigger"]], DIFFERENTIATE),
        q("exposure.alcohol_nicotine_recreational_stimulant", "Alcohol Nicotine or Stimulant Exposure", "string", "stimulants", "최근 음주, 흡연·전자담배, 코카인·암페타민 같은 각성제 사용과 관련이 있나요?", 83, "trigger_context", [G["trigger"], G["risk"]], RISK),
        q("medication.recent_change_palpitations", "Recent Medication Change Relevant to Palpitations", "string", "medication-change", "최근 시작하거나 용량이 바뀐 처방약, 감기약·비충혈제거제, 흡입제, 갑상선약 또는 보충제가 있나요?", 82, "medication_context", [G["trigger"]], RISK),
        q("history.thyroid_disease", "Thyroid Disease History", "boolean", "thyroid-history", "갑상선 질환을 진단받은 적이 있나요?", 81, "medical_context", [G["risk"]], RISK),
        q("history.anemia", "Anaemia History", "boolean", "anemia-history", "빈혈을 진단받은 적이 있나요?", 80, "medical_context", [G["risk"]], RISK),
        q("patient.pregnant_or_postpartum", "Pregnant or Postpartum", "coded", "pregnancy", "현재 임신 중이거나 출산 후 6주 이내인가요? 해당되지 않으면 해당 없음으로 답해 주세요.", 79, "physiologic_context", [G["risk"]], RISK, allowed_values=["pregnant", "postpartum_6_weeks", "not_applicable", "unclear"]),
        q("investigation.ecg_or_device_record_available", "ECG or Device Record Available", "boolean", "record-available", "증상 중 기록된 심전도, 스마트워치 리듬 또는 맥박 기록이 있나요?", 78, "diagnostic_context", [G["rhythm"]], RISK),
        q("symptom.palpitations.functional_impact", "Functional Impact of Palpitations", "coded", "impact", "두근거림이 일상이나 수면에 미치는 영향은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 77, "impact_context", [G["rhythm"]], CHARACTERIZE, allowed_values=["none", "mild", "moderate", "severe"]),
    ]
    rules = [
        safety_rule(PREFIX, "current-chest-pain", {"all": [{"fact": "symptom.palpitations.current", "equals": True}, {"fact": "symptom.chest_pain", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "current-severe-dyspnea", {"all": [{"fact": "symptom.palpitations.current", "equals": True}, {"fact": "symptom.severe_dyspnea", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "current-syncope-presyncope", {"all": [{"fact": "symptom.palpitations.current", "equals": True}, {"fact": "symptom.presyncope", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "palpitations-syncope", {"fact": "symptom.syncope", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "current-not-settling", {"all": [{"fact": "symptom.palpitations.current", "equals": True}, {"fact": "symptom.palpitations.persistent_not_settling", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "neurologic-deficit", {"fact": "symptom.new_focal_neurologic_deficit", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "exertional-syncope", {"fact": "symptom.syncope_during_exertion", "equals": True}, "urgent", 900),
        safety_rule(PREFIX, "heart-disease-worsening", {"all": [{"fact": "history.known_heart_disease", "equals": True}, {"fact": "symptom.palpitations.worsening_or_frequent", "equals": True}]}, "urgent", 900),
        safety_rule(PREFIX, "family-sudden-death", {"fact": "family.sudden_cardiac_death_under_40", "equals": True}, "urgent", 900),
    ]
    extra_nodes = [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1].replace("-", " ").title()} for v in G.values()] + [
        {"id": "hypothesis.palpitations.immediate-safety", "type": "Hypothesis", "display": "Immediate Cardiac Safety Warning Pattern"},
        {"id": "hypothesis.palpitations.arrhythmia", "type": "Hypothesis", "display": "Possible Rhythm Disturbance Pattern"},
        {"id": "hypothesis.palpitations.reversible-trigger", "type": "Hypothesis", "display": "Possible Reversible Trigger Pattern"},
    ]
    return {
        "id": "knowledge.generated.palpitations", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-palpitations-research",
        "default_refresh": default_refresh(), "extra_nodes": extra_nodes,
        "group_hypothesis_edges": [[G["safety"], "hypothesis.palpitations.immediate-safety"], [G["rhythm"], "hypothesis.palpitations.arrhythmia"], [G["trigger"], "hypothesis.palpitations.reversible-trigger"]],
        "safety_rules": rules, "entries": entries, "provenance": provenance(SOURCES),
    }


def build_mrcm():
    return {
        "id": MRCM_REF, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SNOMED, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": [
            {"code": "80313002", "display": "Palpitations (finding)", "attribute_count_returned": 20},
            {"code": "3424008", "display": "Tachycardia (finding)", "attribute_count_returned": 20},
        ],
        "checks": [{"focus_code": code, "attribute_code": attr, "allowed": True} for code in ("80313002", "3424008") for attr in ("363698007", "246112005")],
        "validation": {"method": "build_time_live_mrcm_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "provenance": provenance(["source.stom.mrcm.palpitations.20260714"]),
    }


def build_sources():
    definitions = [
        ("source.nhs.heart-palpitations.2026", "NHS", "Heart palpitations", "reviewed-2026-03-17", "https://www.nhs.uk/symptoms/heart-palpitations/", "public_health_guidance", 7),
        ("source.nice.ng196.atrial-fibrillation.2021", "NICE", "Atrial fibrillation: diagnosis and management", "NG196-updated-2021-06-30", "https://www.nice.org.uk/guidance/ng196/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nice.cg109.blackouts.2023", "NICE", "Transient loss of consciousness in over 16s", "CG109-updated-2023", "https://www.nice.org.uk/guidance/cg109/chapter/Recommendations", "clinical_guideline", 1),
        ("source.stom.mrcm.palpitations.20260714", "Infoclinic", "STOM palpitations SNOMED CT lookup and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/80313002", "terminology_server", 30),
    ]
    artifacts = [{
        "id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata",
        "publisher": publisher, "title": title, "version": version, "url": url, "language": "en",
        "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached",
        "license_status": "restricted" if publisher != "NHS" else "unknown", "complete": False,
        "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-14",
        "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"),
        "assertions": ["Build-Time metadata only; Runtime does not browse this source and generated clinical content remains unreviewed."],
    } for sid, publisher, title, version, url, profile, days in definitions]
    research = {"id": "source-manifest.primary-care-palpitations-research", "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in definitions])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.repository.context", "repository_specification", "docs/context", True),
        ("source.catalog.primary-care-rfe", "knowledge_catalog", "knowledge/catalog/primary-care-rfe.json", True),
        ("source.registry.shared-primary-care-facts", "fact_registry", "knowledge/shared/primary-care-facts.json", True),
        ("source.generated.primary-care-palpitations", "generated_clinical_knowledge", "knowledge/generated/cardiovascular/palpitations/palpitations.json", True),
        ("source.mapping.snomed-mrcm.palpitations", "terminology_mapping", "mappings/terminology/snomed-mrcm-palpitations.json", False),
        ("source.external.primary-care-palpitations-research", "external_source_manifest", "sources/manifests/primary-care-palpitations-research.json", False),
        ("source.policy.primary-care-palpitations-completion", "runtime_policy", "policies/primary-care-palpitations-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-palpitations", "version": VERSION, "acquired_at": CREATED_AT,
               "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths],
               "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md", "sources/manifests/primary-care-palpitations-research.json"])}
    return primary, research


def build_cases(fragment):
    true_map = {
        "current-chest-pain": ["symptom.palpitations.current", "symptom.chest_pain"],
        "current-severe-dyspnea": ["symptom.palpitations.current", "symptom.severe_dyspnea"],
        "current-syncope-presyncope": ["symptom.palpitations.current", "symptom.presyncope"],
        "palpitations-syncope": ["symptom.syncope"],
        "current-not-settling": ["symptom.palpitations.current", "symptom.palpitations.persistent_not_settling"],
        "neurologic-deficit": ["symptom.new_focal_neurologic_deficit"],
        "exertional-syncope": ["symptom.syncope_during_exertion"],
        "heart-disease-worsening": ["history.known_heart_disease", "symptom.palpitations.worsening_or_frequent"],
        "family-sudden-death": ["family.sudden_cardiac_death_under_40"],
    }
    cases = {}
    for index, rule in enumerate(fragment["safety_rules"], 1):
        key = rule["id"].split("safety.", 1)[1]
        level = rule["then"]["safety_level"]
        cases[f"PALP-{key.upper()}-001.json"] = {
            "id": f"PALP-{key.upper()}-001", "simulation_language": "ko", "persona": {"age": 30 + index},
            "initial_statement": {"ko": "가슴이 두근거려요."}, "hidden_state": {fid: {"value": True} for fid in true_map[key]},
            "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 24, "forbidden_assertions": ["diagnosis.atrial_fibrillation", "diagnosis.supraventricular_tachycardia", "recommendation.antiarrhythmic"]},
            "provenance": provenance(SOURCES),
        }
    hidden = {}
    for item in fragment["entries"]:
        fact = item["fact"]; fid = fact["id"]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": fid == "symptom.palpitations.current"}
        elif fact["value_type"] == "quantity": hidden[fid] = {"value": {"amount": 3, "unit": "days"}}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        else: hidden[fid] = {"value": "없음"}
    declined = "exposure.alcohol_nicotine_recreational_stimulant"; hidden.pop(declined)
    not_measured = "observation.pulse_rate_during_episode"; hidden.pop(not_measured)
    cases["PALP-DATA-ABSENT-001.json"] = {
        "id": "PALP-DATA-ABSENT-001", "simulation_language": "ko", "persona": {"age": 44},
        "initial_statement": {"ko": "가끔 심장이 두근거려요."}, "hidden_state": hidden,
        "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}, not_measured: {"dataAbsentReason": "asked-unknown"}},
        "expected": {"expected_data_absent_reasons": {declined: "asked-declined", not_measured: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 38, "forbidden_assertions": ["diagnosis.atrial_fibrillation", "recommendation.beta_blocker"]},
        "provenance": provenance(["source.nice.ng196.atrial-fibrillation.2021", "specifications/clinical-memory.md"]),
    }
    return cases


def main():
    fragment = build_fragment()
    graph, rules = base_graph_and_rules(prefix=PREFIX, rfe=RFE, display="Palpitations", intents=[
        ("intent.characterize_symptom", "Characterize Symptom"), ("intent.screen_red_flags", "Screen Red Flags"),
        ("intent.differentiate_common_causes", "Differentiate Common Sources"), ("intent.risk_assessment", "Risk Assessment")])
    primary, research = build_sources()
    policy = completion_policy(prefix=PREFIX, fragment=fragment, presentation_fact="symptom.palpitations.current", question_budget=38, source_refs=SOURCES)
    for path, document in [
        ("knowledge/base/primary-care-palpitations.json", graph), ("rules/base/primary-care-palpitations.json", rules),
        ("knowledge/generated/cardiovascular/palpitations/palpitations.json", fragment), ("mappings/terminology/snomed-mrcm-palpitations.json", build_mrcm()),
        ("sources/manifests/primary-care-palpitations.json", primary), ("sources/manifests/primary-care-palpitations-research.json", research),
        ("policies/primary-care-palpitations-completion.json", policy),
    ]: write_json(path, document)
    for filename, case in build_cases(fragment).items(): write_json(f"simulation/patients/cardiovascular/palpitations/{filename}", case)


if __name__ == "__main__":
    main()
