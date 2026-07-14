#!/usr/bin/env python3
"""Materialize unreviewed weight and constitutional-change knowledge."""
from profile_support import *

P = "weight-constitutional-change"
RFE = "rfe.weight_constitutional_change"
M = "mapping.snomed-mrcm.weight-constitutional-change"
SN = "http://snomed.info/sct"
SOURCES = [
    "source.nhs.unintentional-weight-loss.2025",
    "source.nhs.night-sweats.2023",
    "source.nice.ng12.constitutional.2026",
    "source.nice.cg32.nutrition.2017",
    "source.nice.ng127.weakness.2023",
]
G = {key: f"group.weight-constitutional.{key}" for key in (
    "change-measurement", "neurological-safety", "acute-systemic-safety",
    "nutrition", "night-sweats", "associated-symptoms", "metabolic",
    "background", "function",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups,
                 intents=intents, **kwargs)


def fragment():
    entries = [
        Q("constitutional.primary_concern", "Primary Weight or Constitutional Concern", "coded", "primary-concern", "가장 주된 변화는 의도하지 않은 체중 감소, 의도한 체중 감소, 체중 증가, 야간 발한, 전신 쇠약 중 무엇인가요?", 130, [G["change-measurement"]], C, allowed_values=["unintentional_weight_loss", "intentional_weight_loss", "weight_gain", "night_sweats", "generalized_weakness", "multiple", "other"], terminology_binding={"system": SN, "focus_codes": ["89362005", "262286000", "42984000", "13791008"]}, mrcm_ref=M, mrcm_status="partial_provisional_pass"),
        Q("constitutional.change_duration", "Duration of Constitutional Change", "string", "duration", "그 변화는 언제부터 시작됐나요?", 115, [G["change-measurement"]], C),
        Q("weight.change_intentionality", "Weight Change Intentionality", "coded", "intentionality", "식사나 운동을 일부러 바꿔 생긴 변화인가요, 의도하지 않았나요, 확실하지 않나요?", 114, [G["change-measurement"]], C, allowed_values=["intentional", "unintentional", "mixed", "uncertain"]),
        Q("weight.current_kg", "Current Weight in Kilograms", "integer", "current-weight", "현재 체중은 몇 kg인가요?", 113, [G["change-measurement"], G["nutrition"]], C),
        Q("weight.previous_kg_and_date", "Previous Weight and Date", "string", "previous-weight", "변화 전 체중과 그 체중을 확인한 시점을 알려주세요.", 112, [G["change-measurement"], G["nutrition"]], C),
        Q("weight.change_amount_or_percent", "Weight Change Amount or Percentage", "string", "change-amount", "총 몇 kg 또는 체중의 몇 퍼센트 정도 변했나요?", 111, [G["change-measurement"], G["nutrition"]], C),
        Q("weight.change_trajectory", "Weight Change Trajectory", "coded", "trajectory", "변화는 계속 진행 중, 안정됨, 다시 회복 중, 오르내림 중 무엇인가요?", 105, [G["change-measurement"]], C, allowed_values=["progressing", "stable", "recovering", "fluctuating", "uncertain"]),
        Q("symptom.generalized_weakness", "Generalized Weakness", "boolean", "generalized-weakness", "온몸에 힘이 빠지는 전신 쇠약이 있나요?", 129, [G["neurological-safety"], G["function"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "13791008"}),
        Q("symptom.sudden_focal_weakness_or_speech_change", "Sudden Focal Weakness or Speech Change", "boolean", "focal-weakness", "갑자기 한쪽 얼굴·팔·다리에 힘이 빠지거나 말이 어눌하거나 이해하기 어려워졌나요?", 128, [G["neurological-safety"]], S, safety_relevant=True),
        Q("symptom.rapidly_progressive_symmetric_weakness", "Rapidly Progressive Symmetric Weakness", "boolean", "progressive-symmetric", "수시간에서 수일 사이 양쪽 팔·다리 힘이 빠르게 약해지거나 위쪽으로 번지나요?", 127, [G["neurological-safety"]], S, safety_relevant=True),
        Q("symptom.weakness_swallowing_or_voice_change", "Weakness with Swallowing or Voice Change", "boolean", "bulbar", "힘 빠짐과 함께 삼키기 어렵거나 사레, 목소리 변화가 있나요?", 126, [G["neurological-safety"]], S, safety_relevant=True),
        Q("symptom.breathlessness_at_rest_or_lying", "Breathlessness at Rest or Lying", "boolean", "rest-breathlessness", "가만히 있거나 누워 있을 때도 숨이 차나요?", 125, [G["neurological-safety"], G["acute-systemic-safety"]], S, safety_relevant=True),
        Q("symptom.new_confusion_or_collapse", "New Confusion or Collapse", "boolean", "confusion-collapse", "새로 혼란하거나 깨우기 어렵거나 쓰러졌나요?", 124, [G["acute-systemic-safety"]], S, safety_relevant=True),
        Q("symptom.chest_pain", "Chest Pain", "boolean", "chest-pain", "전신 쇠약이나 체중 변화와 함께 지금 가슴 통증이나 압박감이 있나요?", 123, [G["acute-systemic-safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("symptom.severe_dyspnea", "Severe Shortness of Breath", "boolean", "severe-dyspnea", "숨이 매우 차서 말하거나 움직이기 어려운가요?", 122, [G["acute-systemic-safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("weight.rapid_gain_with_edema", "Rapid Weight Gain with Edema", "boolean", "rapid-gain-edema", "며칠 사이 체중이 빠르게 늘면서 발·다리·배나 얼굴이 붓나요?", 121, [G["acute-systemic-safety"], G["change-measurement"]], S, safety_relevant=True),
        Q("nutrition.unable_to_keep_fluids_or_severe_dehydration", "Unable to Keep Fluids or Severe Dehydration", "boolean", "dehydration", "물을 마셔도 계속 토하거나 소변이 거의 없고 입이 매우 마르는 등 심한 탈수 징후가 있나요?", 120, [G["acute-systemic-safety"], G["nutrition"]], S, safety_relevant=True),
        Q("nutrition.little_or_no_intake_over_five_days", "Little or No Intake over Five Days", "boolean", "low-intake-five-days", "5일 넘게 거의 먹지 못했거나 앞으로도 먹기 어려울 것 같나요?", 119, [G["nutrition"]], S, safety_relevant=True),
        Q("symptom.high_fever_or_systemically_very_unwell", "High Fever or Systemically Very Unwell", "boolean", "high-fever-unwell", "높은 열, 심한 오한 또는 매우 아픈 느낌이 있나요?", 118, [G["acute-systemic-safety"], G["night-sweats"]], S, safety_relevant=True),
        Q("symptom.night_sweats", "Night Sweats", "boolean", "night-sweats", "잘 때 방이 덥지 않은데도 땀이 많이 나나요?", 110, [G["night-sweats"]], C, terminology_binding={"system": SN, "code": "42984000"}),
        Q("symptom.drenching_night_sweats", "Drenching Night Sweats", "boolean", "drenching", "잠옷이나 침구를 갈아야 할 정도로 흠뻑 젖나요?", 109, [G["night-sweats"]], C),
        Q("symptom.night_sweat_frequency", "Night Sweat Frequency", "string", "night-sweat-frequency", "일주일에 몇 번이고, 잠을 깨우며, 얼마나 지속됐나요?", 108, [G["night-sweats"]], C),
        Q("environment.sleep_heat_or_bedding", "Sleep Heat or Bedding Context", "boolean", "sleep-environment", "방 온도, 두꺼운 이불이나 잠옷 때문에 더웠을 가능성이 있나요?", 86, [G["night-sweats"], G["background"]], D),
        Q("symptom.appetite_change", "Appetite Change", "coded", "appetite", "식욕은 감소, 변화 없음, 증가 중 무엇인가요?", 104, [G["nutrition"], G["metabolic"]], R, allowed_values=["decreased", "unchanged", "increased", "variable", "uncertain"]),
        Q("symptom.persistent_cough_or_breathlessness", "Persistent Cough or Breathlessness", "boolean", "cough-breathlessness", "3주 이상 지속되는 기침이나 평소보다 숨참이 있나요?", 103, [G["associated-symptoms"]], R),
        Q("symptom.unexplained_lymph_node_or_mass", "Unexplained Lymph Node or Mass", "boolean", "node-mass", "목, 겨드랑이, 사타구니에 원인 없이 커진 멍울이나 다른 덩이가 있나요?", 102, [G["associated-symptoms"]], R),
        Q("symptom.persistent_diarrhea_or_bowel_change", "Persistent Diarrhea or Bowel Change", "boolean", "bowel-change", "지속되는 설사, 변비 또는 배변 습관 변화가 있나요?", 101, [G["associated-symptoms"], G["nutrition"]], R),
        Q("symptom.visible_or_suspected_blood_loss", "Visible or Suspected Blood Loss", "boolean", "blood-loss", "혈변·검은 변, 혈뇨, 비정상 출혈 또는 반복되는 출혈이 있나요?", 117, [G["acute-systemic-safety"], G["associated-symptoms"]], S, safety_relevant=True),
        Q("symptom.persistent_or_localizing_pain", "Persistent or Localizing Pain", "string", "persistent-pain", "계속되거나 점점 심해지는 통증이 있다면 위치와 양상을 알려주세요.", 100, [G["associated-symptoms"]], R),
        Q("symptom.thirst_and_frequent_urination", "Thirst and Frequent Urination", "boolean", "thirst-polyuria", "갈증이 심하고 물을 많이 마시며 소변을 자주 보나요?", 99, [G["metabolic"]], R),
        Q("symptom.heat_intolerance_palpitations_or_tremor", "Heat Intolerance Palpitations or Tremor", "boolean", "thyroid-like", "더위를 못 견디거나 두근거림, 손떨림, 땀 증가가 있나요?", 98, [G["metabolic"]], R),
        Q("symptom.cold_intolerance_constipation_or_dry_skin", "Cold Intolerance Constipation or Dry Skin", "boolean", "cold-pattern", "추위를 유난히 타거나 변비, 피부 건조, 움직임 둔화가 있나요?", 97, [G["metabolic"]], R),
        Q("exposure.infection_contact_or_travel", "Infection Contact or Travel", "string", "infection-exposure", "최근 감염 환자 접촉, 결핵 노출, 해외여행 또는 동물 관련 노출이 있었나요?", 96, [G["background"], G["night-sweats"]], R),
        Q("history.cancer_immunosuppression_or_chronic_disease", "Cancer Immunosuppression or Chronic Disease", "string", "medical-history", "암, 면역저하, 당뇨, 갑상선, 심장·폐·신장·간·장 질환 병력이 있나요?", 95, [G["background"]], R),
        Q("medication.substance_or_recent_change", "Medication Substance or Recent Change", "string", "medication-substance", "최근 시작·중단·용량 변경한 약, 보충제, 술 또는 약물이 있나요?", 94, [G["background"], G["night-sweats"]], R),
        Q("mental_health.mood_stress_or_eating_concern", "Mood Stress or Eating Concern", "string", "mood-eating", "우울·불안·스트레스, 체중이나 체형에 대한 걱정, 일부러 식사를 제한하거나 폭식·구토한 일이 있나요?", 93, [G["background"], G["nutrition"]], R),
        Q("constitutional.functional_impact", "Constitutional Functional Impact", "coded", "functional-impact", "걷기, 일, 식사, 씻기 같은 일상 영향은 없음, 가벼움, 중간, 심함 중 무엇인가요?", 92, [G["function"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("constitutional.patient_priority_or_comment", "Patient Priority or Comment", "string", "patient-priority", "이 변화와 관련해 가장 걱정되거나 꼭 전달하고 싶은 내용은 무엇인가요?", 85, [G["function"], G["background"]], C),
    ]
    rules = [
        safety_rule(P, "sudden-focal-weakness", {"fact": "symptom.sudden_focal_weakness_or_speech_change", "equals": True}, "emergency", 1000),
        safety_rule(P, "progressive-symmetric-weakness", {"fact": "symptom.rapidly_progressive_symmetric_weakness", "equals": True}, "emergency", 1000),
        safety_rule(P, "weakness-bulbar", {"all": [{"fact": "symptom.generalized_weakness", "equals": True}, {"fact": "symptom.weakness_swallowing_or_voice_change", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "weakness-rest-breathlessness", {"all": [{"fact": "symptom.generalized_weakness", "equals": True}, {"fact": "symptom.breathlessness_at_rest_or_lying", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "confusion-collapse", {"fact": "symptom.new_confusion_or_collapse", "equals": True}, "emergency", 1000),
        safety_rule(P, "weakness-chest-pain", {"all": [{"fact": "symptom.generalized_weakness", "equals": True}, {"fact": "symptom.chest_pain", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "rapid-gain-severe-dyspnea", {"all": [{"fact": "weight.rapid_gain_with_edema", "equals": True}, {"fact": "symptom.severe_dyspnea", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "severe-dehydration", {"fact": "nutrition.unable_to_keep_fluids_or_severe_dehydration", "equals": True}, "urgent", 900),
        safety_rule(P, "low-intake-five-days", {"fact": "nutrition.little_or_no_intake_over_five_days", "equals": True}, "urgent", 880),
        safety_rule(P, "fever-blood-loss", {"all": [{"fact": "symptom.high_fever_or_systemically_very_unwell", "equals": True}, {"fact": "symptom.visible_or_suspected_blood_loss", "equals": True}]}, "urgent", 870),
    ]
    return {
        "id": "knowledge.generated.weight-constitutional-change", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-weight-constitutional-change-research",
        "default_refresh": default_refresh(),
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def source_docs():
    definitions = [
        ("source.nhs.unintentional-weight-loss.2025", "NHS", "Unintentional weight loss", "reviewed-2025-07-28", "https://www.nhs.uk/symptoms/unintentional-weight-loss/", "public_health_guidance", 7),
        ("source.nhs.night-sweats.2023", "NHS", "Night sweats", "reviewed-2023-11-09", "https://www.nhs.uk/symptoms/night-sweats/", "public_health_guidance", 7),
        ("source.nice.ng12.constitutional.2026", "NICE", "Suspected cancer: recognition and referral — constitutional symptoms", "NG12-updated-2026", "https://www.nice.org.uk/guidance/ng12/chapter/Recommended-actions-organised-by-symptom-and-findings-of-primary-care-investigations", "clinical_guideline", 1),
        ("source.nice.cg32.nutrition.2017", "NICE", "Nutrition support for adults", "CG32-updated-2017", "https://www.nice.org.uk/guidance/cg32/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nice.ng127.weakness.2023", "NICE", "Suspected neurological conditions — weakness", "NG127-updated-2023", "https://www.nice.org.uk/guidance/ng127/chapter/Recommendations-for-adults-aged-over-16", "clinical_guideline", 1),
        ("source.stom.weight-constitutional.20260714", "Infoclinic", "STOM weight and constitutional symptom terminology", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/42984000", "terminology_server", 30),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, days in definitions:
        artifacts.append({
            "id": sid, "kind": "terminology_mrcm_query_summary" if days == 30 else "clinical_guidance_metadata",
            "publisher": publisher, "title": title, "version": version, "url": url, "language": "en",
            "digest": "live_response_summary_not_raw_cache" if days == 30 else "metadata_only_not_cached",
            "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown", "complete": False,
            "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-14",
            "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"),
            "assertions": ["Build-Time source only; Runtime does not browse it; generated content remains unreviewed."],
        })
    research = {"id": "source-manifest.primary-care-weight-constitutional-change-research", "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([item[0] for item in definitions])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.weight-constitutional", "generated_clinical_knowledge", "knowledge/generated/general/weight-constitutional-change/weight-constitutional-change.json", True),
        ("source.mapping.weight-constitutional", "terminology_mapping", "mappings/terminology/snomed-mrcm-weight-constitutional-change.json", False),
        ("source.external.weight-constitutional", "external_source_manifest", "sources/manifests/primary-care-weight-constitutional-change-research.json", False),
        ("source.policy.weight-constitutional", "runtime_policy", "policies/primary-care-weight-constitutional-change-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-weight-constitutional-change", "version": VERSION, "acquired_at": CREATED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(fragment_document):
    trigger_map = {
        "sudden-focal-weakness": ["symptom.sudden_focal_weakness_or_speech_change"],
        "progressive-symmetric-weakness": ["symptom.rapidly_progressive_symmetric_weakness"],
        "weakness-bulbar": ["symptom.generalized_weakness", "symptom.weakness_swallowing_or_voice_change"],
        "weakness-rest-breathlessness": ["symptom.generalized_weakness", "symptom.breathlessness_at_rest_or_lying"],
        "confusion-collapse": ["symptom.new_confusion_or_collapse"],
        "weakness-chest-pain": ["symptom.generalized_weakness", "symptom.chest_pain"],
        "rapid-gain-severe-dyspnea": ["weight.rapid_gain_with_edema", "symptom.severe_dyspnea"],
        "severe-dehydration": ["nutrition.unable_to_keep_fluids_or_severe_dehydration"],
        "low-intake-five-days": ["nutrition.little_or_no_intake_over_five_days"],
        "fever-blood-loss": ["symptom.high_fever_or_systemically_very_unwell", "symptom.visible_or_suspected_blood_loss"],
    }
    output = {}
    for index, rule in enumerate(fragment_document["safety_rules"], 1):
        key = rule["id"].split("safety.", 1)[1]
        level = rule["then"]["safety_level"]
        output[f"CONST-{key.upper()}.json"] = {
            "id": f"CONST-{key.upper()}", "simulation_language": "ko", "persona": {"age": 35 + index},
            "initial_statement": {"ko": "최근 체중이 줄고 온몸에 힘이 없어요."},
            "hidden_state": {fact_id: {"value": True} for fact_id in trigger_map[key]},
            "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 28, "forbidden_assertions": ["diagnosis.cancer", "diagnosis.stroke", "recommendation.start_nutrition_support"]},
            "provenance": provenance(SOURCES),
        }
    hidden = {}
    for item in fragment_document["entries"]:
        fact = item["fact"]
        fid = fact["id"]
        if fact["value_type"] == "boolean":
            hidden[fid] = {"value": False}
        elif fact["value_type"] == "integer":
            hidden[fid] = {"value": 65}
        elif fact["value_type"] == "coded":
            hidden[fid] = {"value": fact.get("allowed_values", ["other"])[-1]}
        else:
            hidden[fid] = {"value": "없음"}
    hidden["constitutional.primary_concern"] = {"value": "unintentional_weight_loss"}
    declined = "mental_health.mood_stress_or_eating_concern"
    hidden.pop(declined)
    output["CONST-DATA-ABSENT.json"] = {
        "id": "CONST-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 52},
        "initial_statement": {"ko": "이유 없이 체중이 조금 줄었어요."}, "hidden_state": hidden,
        "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}},
        "expected": {"expected_data_absent_reasons": {declined: "asked-declined"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.malignancy", "recommendation.start_medication"]},
        "provenance": provenance(["source.nhs.unintentional-weight-loss.2025", "specifications/clinical-memory.md"]),
    }
    return output


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Weight or Constitutional Change", intents=[("intent.characterize_symptom", "Characterize Symptom"), ("intent.screen_red_flags", "Screen Red Flags"), ("intent.differentiate_common_causes", "Differentiate Common Sources"), ("intent.risk_assessment", "Risk Assessment")])
    primary, research = source_docs()
    concepts = [("89362005", "Weight loss (finding)", 0), ("262286000", "Weight increased (finding)", 20), ("42984000", "Night sweats (finding)", 20), ("13791008", "Asthenia (finding)", 20)]
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": [{"code": code, "display": display, "attribute_count_returned": count} for code, display, count in concepts],
        "checks": [{"focus_code": code, "attribute_code": attribute, "allowed": True} for code in ("262286000", "42984000", "13791008") for attribute in ("363698007", "246112005")],
        "unsupported_checks": [{"focus_code": "89362005", "reason": "STOM_allowed_attribute_response_empty"}],
        "validation": {"method": "build_time_live_mrcm_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "partial_provisional_pass"},
        "provenance": provenance(["source.stom.weight-constitutional.20260714"]),
    }
    documents = [
        ("knowledge/base/primary-care-weight-constitutional-change.json", graph),
        ("rules/base/primary-care-weight-constitutional-change.json", rules),
        ("knowledge/generated/general/weight-constitutional-change/weight-constitutional-change.json", generated),
        ("mappings/terminology/snomed-mrcm-weight-constitutional-change.json", mapping),
        ("sources/manifests/primary-care-weight-constitutional-change.json", primary),
        ("sources/manifests/primary-care-weight-constitutional-change-research.json", research),
        ("policies/primary-care-weight-constitutional-change-completion.json", completion_policy(prefix=P, fragment=generated, presentation_fact="constitutional.primary_concern", question_budget=40, source_refs=SOURCES)),
    ]
    for path, document in documents:
        write_json(path, document)
    for name, case in cases(generated).items():
        write_json("simulation/patients/general/weight-constitutional-change/" + name, case)


if __name__ == "__main__":
    main()
