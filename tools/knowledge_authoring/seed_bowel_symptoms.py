#!/usr/bin/env python3
"""Materialize the unreviewed grouped bowel-symptom research profile."""
from __future__ import annotations

from profile_support import VERSION, CREATED_AT, base_graph_and_rules, completion_policy, default_refresh, entry, provenance, safety_rule, write_json

PREFIX = "bowel-symptoms"
RFE = "rfe.bowel_symptoms"
MRCM_REF = "mapping.snomed-mrcm.bowel-symptoms"
SNOMED = "http://snomed.info/sct"
SOURCES = ["source.nhs.rectal-bleeding.2023", "source.nhs.stomach-ache.2023", "source.nice.ng12.colorectal.2026"]
G = {"safety": "group.bowel.immediate-safety", "habit": "group.bowel.habit-stool", "bleeding": "group.bowel.bleeding", "obstruction": "group.bowel.obstruction", "risk": "group.bowel.persistence-risk", "context": "group.bowel.context"}
C = ["intent.characterize_symptom"]; S = ["intent.screen_red_flags"]; R = ["intent.risk_assessment"]; D = ["intent.differentiate_common_causes"]


def q(fid, display, vt, key, wording, score, reason, groups, intents, **kwargs):
    return entry(PREFIX, fid, display, vt, key, wording, score, reason, groups, intents=intents, **kwargs)


def build_fragment():
    e = [
        q("symptom.bowel.current", "Current Bowel Symptom", "boolean", "current", "지금도 변비, 배변 습관 변화, 항문 출혈 또는 혈변이 있나요?", 130, "confirm_presentation", [G["habit"], G["bleeding"]], C),
        q("symptom.bowel.main_type", "Main Bowel Symptom", "coded", "main-type", "가장 불편한 것은 변비, 묽거나 잦은 변, 가는 변, 잔변감, 항문 출혈, 혈변 중 무엇인가요?", 111, "group_branch", [G["habit"], G["bleeding"]], C, allowed_values=["constipation", "loose_frequent", "narrow_stool", "incomplete_emptying", "rectal_bleeding", "blood_mixed_stool", "other"]),
        q("symptom.duration", "Symptom Duration", "quantity", "duration", "이 변화는 언제부터 시작했나요?", 110, "duration", [G["habit"]], C, reuse_existing=True),
        q("symptom.bowel.sudden_or_gradual", "Bowel Symptom Onset", "coded", "onset", "갑자기 시작했나요, 서서히 시작했나요?", 109, "onset", [G["habit"]], C, allowed_values=["sudden", "gradual", "unclear"]),
        q("symptom.rectal_bleeding_nonstop", "Non-stop Rectal Bleeding", "boolean", "bleeding-nonstop", "지금 항문 출혈이 멈추지 않고 계속되나요?", 129, "hemorrhage_gate", [G["safety"], G["bleeding"]], S, safety_relevant=True),
        q("symptom.rectal_bleeding_large_volume_or_clots", "Large-volume Rectal Bleeding or Clots", "boolean", "large-bleeding", "변기 물이 붉어질 만큼 피가 많거나 큰 피떡이 나오나요?", 128, "hemorrhage_gate", [G["safety"], G["bleeding"]], S, safety_relevant=True),
        q("symptom.collapse_or_severe_faintness", "Collapse or Severe Faintness", "boolean", "collapse", "출혈과 함께 쓰러졌거나 식은땀, 심한 어지럼, 거의 실신할 느낌이 있나요?", 127, "shock_gate", [G["safety"], G["bleeding"]], S, safety_relevant=True),
        q("symptom.sudden_severe_abdominal_pain", "Sudden Severe Abdominal Pain", "boolean", "severe-pain", "배가 갑자기 매우 심하게 아프거나 만지기 힘들 만큼 아픈가요?", 126, "acute_abdomen_gate", [G["safety"], G["obstruction"]], S, safety_relevant=True),
        q("symptom.unable_to_pass_stool_or_flatus", "Unable to Pass Stool or Flatus", "boolean", "obstipation", "대변뿐 아니라 방귀도 전혀 나오지 않나요?", 125, "obstruction_gate", [G["safety"], G["obstruction"]], S, safety_relevant=True),
        q("symptom.abdominal_distension", "Abdominal Distension", "boolean", "distension", "배가 평소보다 많이 붓고 팽팽해졌나요?", 124, "obstruction_gate", [G["safety"], G["obstruction"]], S, safety_relevant=True),
        q("symptom.repeated_vomiting", "Repeated Vomiting", "boolean", "vomiting", "계속 토하거나 물도 마시기 어려운가요?", 123, "obstruction_gate", [G["safety"], G["obstruction"]], S, safety_relevant=True),
        q("symptom.black_tarry_stool", "Black Tarry Stool", "boolean", "black-stool", "변이 검고 끈적하며 타르처럼 보이나요? 철분제나 검은 음식 때문인지 확실하지 않아도 예로 답해 주세요.", 122, "gi_bleeding_gate", [G["safety"], G["bleeding"]], S, safety_relevant=True),
        q("symptom.bloody_diarrhea", "Bloody Diarrhoea", "boolean", "bloody-diarrhea", "묽은 변이나 설사에 피가 섞여 나오나요?", 121, "urgent_bleeding_gate", [G["safety"], G["bleeding"]], S, safety_relevant=True),
        q("symptom.fever", "Fever", "boolean", "fever", "열이 나거나 춥고 떨리나요?", 120, "infection_context", [G["safety"], G["context"]], S, safety_relevant=True, reuse_existing=True),
        q("symptom.systemically_unwell", "Systemically Unwell", "boolean", "systemically-unwell", "전신 상태가 몹시 나쁘거나 혼란스럽고 기운이 없나요?", 119, "systemic_gate", [G["safety"]], S, safety_relevant=True),
        q("symptom.bowel.frequency", "Bowel Movement Frequency", "string", "frequency", "평소와 지금은 각각 며칠에 몇 번 배변하나요?", 105, "habit_characterization", [G["habit"]], C),
        q("symptom.stool_form", "Stool Form", "coded", "stool-form", "변 모양은 딱딱한 알갱이, 단단한 덩어리, 보통, 무른 변, 물 같은 변 중 무엇에 가깝나요?", 104, "stool_characterization", [G["habit"]], C, allowed_values=["hard_pellets", "hard_lumpy", "formed", "loose", "watery", "variable", "unclear"]),
        q("symptom.straining", "Straining", "boolean", "straining", "배변할 때 평소보다 심하게 힘을 줘야 하나요?", 98, "constipation_context", [G["habit"]], C, terminology_binding={"system": SNOMED, "code": "14760008"}),
        q("symptom.incomplete_evacuations", "Incomplete Evacuation", "boolean", "incomplete", "배변 후에도 변이 남은 느낌이 있나요?", 97, "constipation_context", [G["habit"]], C),
        q("symptom.manual_maneuver_for_defecation", "Manual Manoeuvre for Defecation", "boolean", "manual-maneuver", "대변을 보기 위해 손으로 눌러 돕거나 직접 꺼내야 한 적이 있나요?", 86, "constipation_severity", [G["habit"]], R),
        q("symptom.narrow_stool", "Narrow Stool", "boolean", "narrow-stool", "변이 전보다 계속 가늘어졌나요?", 96, "change_context", [G["habit"], G["risk"]], R, terminology_binding={"system": SNOMED, "code": "88111009"}, mrcm_ref=MRCM_REF),
        q("symptom.mucus_in_stool", "Mucus in Stool", "boolean", "mucus", "변에 점액이나 끈적한 것이 섞이나요?", 85, "inflammatory_context", [G["habit"], G["bleeding"]], D),
        q("symptom.abdominal_pain", "Abdominal Pain", "boolean", "abdominal-pain", "복통이나 반복되는 배 경련이 있나요?", 95, "associated_context", [G["habit"], G["risk"]], C, reuse_existing=True),
        q("symptom.bloating", "Bloating", "boolean", "bloating", "배가 더부룩하거나 가스가 많이 차나요?", 84, "associated_context", [G["habit"]], D),
        q("symptom.rectal_pain_or_itch", "Rectal Pain or Itch", "boolean", "rectal-pain", "배변할 때 항문이 아프거나 평소 가렵고 불편한가요?", 94, "bleeding_source_context", [G["bleeding"]], D),
        q("symptom.blood_appearance", "Blood Appearance", "coded", "blood-appearance", "피는 휴지에 묻음, 변 겉에 선홍색, 변에 섞인 붉은 피, 검붉은 피 중 무엇인가요?", 103, "bleeding_characterization", [G["bleeding"]], C, allowed_values=["paper_only", "bright_surface", "mixed_red", "dark_red", "unclear"], terminology_binding={"system": SNOMED, "code": "12063002"}, mrcm_ref=MRCM_REF),
        q("symptom.rectal_bleeding.recurrent_or_persistent", "Recurrent or Persistent Rectal Bleeding", "boolean", "persistent-bleeding", "출혈이 반복되거나 3주 이상 지속되나요?", 102, "persistence_risk", [G["bleeding"], G["risk"]], R),
        q("symptom.unintentional_weight_loss", "Unintentional Weight Loss", "boolean", "weight-loss", "최근 일부러 빼지 않았는데 체중이 줄었나요?", 101, "colorectal_risk", [G["risk"]], R, reuse_existing=True),
        q("symptom.anemia_or_fatigue_features", "Anaemia or Fatigue Features", "boolean", "anemia", "평소보다 많이 피곤하거나 숨이 차고 창백하다는 말을 듣나요?", 100, "colorectal_risk", [G["risk"]], R),
        q("observation.abdominal_or_rectal_mass_known", "Known Abdominal or Rectal Mass", "boolean", "mass", "배나 항문 안쪽에 덩이가 만져지거나 의료진에게 덩이가 있다고 들었나요?", 99, "colorectal_risk", [G["risk"]], R),
        q("family.colorectal_cancer_or_polyps", "Family Colorectal Cancer or Polyps", "boolean", "family-history", "부모·형제자매·자녀 중 대장암이나 진행성 대장용종을 진단받은 사람이 있나요?", 83, "risk_context", [G["risk"]], R),
        q("history.inflammatory_bowel_disease", "Inflammatory Bowel Disease History", "boolean", "ibd", "궤양성 대장염이나 크론병을 진단받은 적이 있나요?", 82, "risk_context", [G["risk"]], R),
        q("medication.bowel_relevant", "Bowel-relevant Medication", "string", "medication", "철분제, 진통제·마약성 진통제, 항콜린제, 완하제, 항응고제·아스피린 등 관련 약을 복용하나요?", 81, "medication_context", [G["context"], G["bleeding"]], R),
        q("lifestyle.fibre_fluid_activity_change", "Fibre Fluid or Activity Change", "string", "lifestyle", "최근 식이섬유, 수분 섭취, 활동량 또는 생활환경이 달라졌나요?", 80, "common_context", [G["context"]], D),
        q("history.abdominal_or_bowel_surgery", "Abdominal or Bowel Surgery History", "boolean", "surgery", "복부나 장 수술을 받은 적이 있나요?", 79, "obstruction_risk", [G["context"], G["obstruction"]], R),
    ]
    rules = [
        safety_rule(PREFIX, "nonstop-bleeding", {"fact": "symptom.rectal_bleeding_nonstop", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "large-bleeding", {"fact": "symptom.rectal_bleeding_large_volume_or_clots", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "bleeding-collapse", {"fact": "symptom.collapse_or_severe_faintness", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "acute-abdomen", {"fact": "symptom.sudden_severe_abdominal_pain", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "obstruction", {"all": [{"fact": "symptom.unable_to_pass_stool_or_flatus", "equals": True}, {"fact": "symptom.abdominal_distension", "equals": True}, {"fact": "symptom.repeated_vomiting", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "black-tarry-stool", {"fact": "symptom.black_tarry_stool", "equals": True}, "urgent", 900),
        safety_rule(PREFIX, "bloody-diarrhea", {"fact": "symptom.bloody_diarrhea", "equals": True}, "urgent", 900),
        safety_rule(PREFIX, "systemic-inflammation", {"all": [{"fact": "symptom.fever", "equals": True}, {"fact": "symptom.systemically_unwell", "equals": True}]}, "urgent", 900),
        safety_rule(PREFIX, "persistent-bleeding-weight-loss", {"all": [{"fact": "symptom.rectal_bleeding.recurrent_or_persistent", "equals": True}, {"fact": "symptom.unintentional_weight_loss", "equals": True}]}, "urgent", 850),
    ]
    extra = [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1].replace("-", " ").title()} for v in G.values()] + [{"id": "hypothesis.bowel.immediate-safety", "type": "Hypothesis", "display": "Immediate Bowel Safety Pattern"}, {"id": "hypothesis.bowel.habit", "type": "Hypothesis", "display": "Changed Bowel Habit Pattern"}, {"id": "hypothesis.bowel.bleeding-risk", "type": "Hypothesis", "display": "Bowel Bleeding and Persistence Pattern"}]
    return {"id": "knowledge.generated.bowel-symptoms", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-bowel-symptoms-research", "default_refresh": default_refresh(), "extra_nodes": extra, "group_hypothesis_edges": [[G["safety"], "hypothesis.bowel.immediate-safety"], [G["habit"], "hypothesis.bowel.habit"], [G["bleeding"], "hypothesis.bowel.bleeding-risk"]], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def build_mrcm():
    concepts = [{"code": "14760008", "display": "Constipation (finding)", "attribute_count_returned": 0}, {"code": "12063002", "display": "Rectal hemorrhage (disorder)", "attribute_count_returned": 22}, {"code": "405729008", "display": "Hematochezia (finding)", "attribute_count_returned": 20}, {"code": "88111009", "display": "Altered bowel function (finding)", "attribute_count_returned": 20}]
    return {"id": MRCM_REF, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SNOMED, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": concepts, "checks": [{"focus_code": c["code"], "attribute_code": a, "allowed": True} for c in concepts if c["attribute_count_returned"] for a in ("363698007", "246112005")], "unsupported_checks": [{"focus_code": "14760008", "reason": "STOM allowed-attribute endpoint returned an empty array; no post-coordination assertion made."}], "validation": {"method": "build_time_live_mrcm_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "partial_provisional_pass"}, "provenance": provenance(["source.stom.mrcm.bowel.20260714"])}


def build_sources():
    defs = [("source.nhs.rectal-bleeding.2023", "NHS", "Bleeding from the bottom", "reviewed-2023-04-12", "https://www.nhs.uk/symptoms/bleeding-from-the-bottom-rectal-bleeding/", "public_health_guidance", 7), ("source.nhs.stomach-ache.2023", "NHS", "Stomach ache", "reviewed-2023-05-26", "https://www.nhs.uk/symptoms/stomach-ache/", "public_health_guidance", 7), ("source.nice.ng12.colorectal.2026", "NICE", "Suspected cancer: colorectal recommendations", "NG12-updated-2026-04-15", "https://www.nice.org.uk/guidance/ng12/chapter/Recommendations-organised-by-site-of-cancer", "clinical_guideline", 1), ("source.stom.mrcm.bowel.20260714", "Infoclinic", "STOM bowel SNOMED CT lookup and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/12063002", "terminology_server", 30)]
    artifacts = [{"id": sid, "kind": "terminology_mrcm_query_summary" if p == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": ver, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if p == "terminology_server" else "metadata_only_not_cached", "license_status": "unknown", "complete": False, "monitor_profile": p, "monitor_interval_days": days, "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"), "assertions": ["Build-Time metadata only; Runtime does not browse this source and generated clinical content remains unreviewed."]} for sid, pub, title, ver, url, p, days in defs]
    research = {"id": "source-manifest.primary-care-bowel-symptoms-research", "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([d[0] for d in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.repository.context", "repository_specification", "docs/context", True), ("source.catalog.primary-care-rfe", "knowledge_catalog", "knowledge/catalog/primary-care-rfe.json", True), ("source.registry.shared-primary-care-facts", "fact_registry", "knowledge/shared/primary-care-facts.json", True), ("source.generated.primary-care-bowel", "generated_clinical_knowledge", "knowledge/generated/gastrointestinal/bowel-symptoms/bowel-symptoms.json", True), ("source.mapping.snomed-mrcm.bowel", "terminology_mapping", "mappings/terminology/snomed-mrcm-bowel-symptoms.json", False), ("source.external.primary-care-bowel-research", "external_source_manifest", "sources/manifests/primary-care-bowel-symptoms-research.json", False), ("source.policy.primary-care-bowel-completion", "runtime_policy", "policies/primary-care-bowel-symptoms-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-bowel-symptoms", "version": VERSION, "acquired_at": CREATED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md", "sources/manifests/primary-care-bowel-symptoms-research.json"])}
    return primary, research


def build_cases(fragment):
    true_map = {"nonstop-bleeding": ["symptom.rectal_bleeding_nonstop"], "large-bleeding": ["symptom.rectal_bleeding_large_volume_or_clots"], "bleeding-collapse": ["symptom.collapse_or_severe_faintness"], "acute-abdomen": ["symptom.sudden_severe_abdominal_pain"], "obstruction": ["symptom.unable_to_pass_stool_or_flatus", "symptom.abdominal_distension", "symptom.repeated_vomiting"], "black-tarry-stool": ["symptom.black_tarry_stool"], "bloody-diarrhea": ["symptom.bloody_diarrhea"], "systemic-inflammation": ["symptom.fever", "symptom.systemically_unwell"], "persistent-bleeding-weight-loss": ["symptom.rectal_bleeding.recurrent_or_persistent", "symptom.unintentional_weight_loss"]}
    cases = {}
    for i, rule in enumerate(fragment["safety_rules"], 1):
        key = rule["id"].split("safety.", 1)[1]; level = rule["then"]["safety_level"]
        cases[f"BOWEL-{key.upper()}-001.json"] = {"id": f"BOWEL-{key.upper()}-001", "simulation_language": "ko", "persona": {"age": 35 + i}, "initial_statement": {"ko": "배변이 달라졌어요."}, "hidden_state": {fid: {"value": True} for fid in true_map[key]}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 25, "forbidden_assertions": ["diagnosis.colorectal_cancer", "diagnosis.bowel_obstruction", "recommendation.laxative"]}, "provenance": provenance(SOURCES)}
    hidden = {}
    for item in fragment["entries"]:
        f = item["fact"]; fid = f["id"]
        if f["value_type"] == "boolean": hidden[fid] = {"value": fid == "symptom.bowel.current"}
        elif f["value_type"] == "quantity": hidden[fid] = {"value": {"amount": 5, "unit": "days"}}
        elif f["value_type"] == "coded": hidden[fid] = {"value": f.get("allowed_values", ["unclear"])[-1]}
        else: hidden[fid] = {"value": "없음"}
    declined = "family.colorectal_cancer_or_polyps"; hidden.pop(declined)
    cases["BOWEL-DATA-ABSENT-001.json"] = {"id": "BOWEL-DATA-ABSENT-001", "simulation_language": "ko", "persona": {"age": 48}, "initial_statement": {"ko": "변비가 생겼어요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-declined"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 37, "forbidden_assertions": ["diagnosis.colorectal_cancer", "recommendation.colonoscopy"]}, "provenance": provenance(["source.nice.ng12.colorectal.2026", "specifications/clinical-memory.md"])}
    return cases


def main():
    fragment = build_fragment(); graph, rules = base_graph_and_rules(prefix=PREFIX, rfe=RFE, display="Bowel Symptoms", intents=[("intent.characterize_symptom", "Characterize Symptom"), ("intent.screen_red_flags", "Screen Red Flags"), ("intent.differentiate_common_causes", "Differentiate Common Sources"), ("intent.risk_assessment", "Risk Assessment")]); primary, research = build_sources(); policy = completion_policy(prefix=PREFIX, fragment=fragment, presentation_fact="symptom.bowel.current", question_budget=37, source_refs=SOURCES)
    for path, doc in [("knowledge/base/primary-care-bowel-symptoms.json", graph), ("rules/base/primary-care-bowel-symptoms.json", rules), ("knowledge/generated/gastrointestinal/bowel-symptoms/bowel-symptoms.json", fragment), ("mappings/terminology/snomed-mrcm-bowel-symptoms.json", build_mrcm()), ("sources/manifests/primary-care-bowel-symptoms.json", primary), ("sources/manifests/primary-care-bowel-symptoms-research.json", research), ("policies/primary-care-bowel-symptoms-completion.json", policy)]: write_json(path, doc)
    for filename, case in build_cases(fragment).items(): write_json(f"simulation/patients/gastrointestinal/bowel-symptoms/{filename}", case)


if __name__ == "__main__": main()
