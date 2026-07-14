#!/usr/bin/env python3
"""Materialize unreviewed grouped ear and hearing symptom knowledge."""
from profile_support import *

P = "ear-hearing-symptoms"
RFE = "rfe.ear_hearing_symptoms"
M = "mapping.snomed-mrcm.ear-hearing-symptoms"
SN = "http://snomed.info/sct"
SOURCES = [
    "source.nice.hearing-loss-ng98", "source.nice.tinnitus-ng155",
    "source.nhs.ear-infections.2025", "source.nhs.hearing-loss.2025",
    "source.nhs.mastoiditis.2025", "source.uhsussex.sudden-hearing-change.2025",
    "source.stom.ear-hearing.20260714",
]
G = {k: f"group.ear.{k}" for k in (
    "routing", "shared-safety", "common", "pain-infection",
    "hearing-change", "discharge-trauma", "tinnitus",
)}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("ear.primary_symptom_group", "Primary Ear or Hearing Symptom Group", "coded", "primary-group", "가장 불편한 증상은 귀 통증·감염 증상, 청력 변화, 귀 분비물·외상, 이명 중 무엇인가요?", 130, [G["routing"]], C, allowed_values=["ear_pain_infection", "hearing_change", "discharge_trauma", "tinnitus", "other_unclear"]),
        Q("ear.sudden_hearing_loss_within_72h", "Sudden Hearing Loss within 72 Hours", "boolean", "sudden-hearing-loss", "청력이 3일 이내에 갑자기 떨어졌나요?", 129, [G["shared-safety"], G["hearing-change"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "79471008"}, mrcm_ref=M),
        Q("ear.rapidly_worsening_hearing_4_to_90_days", "Rapidly Worsening Hearing over 4 to 90 Days", "boolean", "rapid-hearing-decline", "청력이 4일에서 3개월 사이에 빠르게 나빠지고 있나요?", 128, [G["shared-safety"], G["hearing-change"]], S, safety_relevant=True),
        Q("symptom.new_focal_neurological_deficit", "New Focal Neurological Deficit", "boolean", "neurological-deficit", "얼굴 처짐, 한쪽 힘 빠짐·감각 저하, 말이 어눌함 같은 증상이 새로 생겼나요?", 127, [G["shared-safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("ear.acute_uncontrolled_vertigo_or_inability_to_stand", "Acute Uncontrolled Vertigo or Inability to Stand", "boolean", "uncontrolled-vertigo", "심한 회전성 어지럼 때문에 서거나 걷기 어렵거나 계속 토하나요?", 126, [G["shared-safety"]], S, safety_relevant=True),
        Q("ear.postauricular_redness_swelling_tenderness_or_protrusion", "Postauricular Mastoid Warning Features", "boolean", "mastoid-warning", "귀 뒤가 붉고 붓거나 심하게 아프고, 귀가 바깥으로 밀려나 보이나요?", 125, [G["shared-safety"], G["pain-infection"]], S, safety_relevant=True),
        Q("ear.severe_systemic_illness_or_high_fever", "Severe Systemic Illness or High Fever", "boolean", "systemic-illness", "고열이 있거나 오한·처짐 등으로 전신 상태가 매우 나쁜가요?", 124, [G["shared-safety"]], S, safety_relevant=True),
        Q("ear.diabetes_or_immunosuppression_with_severe_pain_or_discharge", "High-risk Host with Severe Ear Pain or Discharge", "boolean", "high-risk-host", "당뇨나 면역저하가 있으면서 귀 통증이 심하거나 분비물이 나오나요?", 123, [G["shared-safety"]], S, safety_relevant=True),
        Q("ear.head_injury_or_penetrating_trauma", "Head Injury or Penetrating Ear Trauma", "boolean", "major-trauma", "머리를 다쳤거나 날카로운 물체가 귀 안을 찌른 뒤 증상이 생겼나요?", 122, [G["shared-safety"], G["discharge-trauma"]], S, safety_relevant=True),
        Q("ear.clear_or_bloody_discharge_after_head_injury", "Clear or Bloody Ear Discharge after Head Injury", "boolean", "post-trauma-discharge", "머리를 다친 뒤 귀에서 맑은 물이나 피가 나오나요?", 121, [G["shared-safety"], G["discharge-trauma"]], S, safety_relevant=True),
        Q("ear.button_battery_or_sharp_foreign_body", "Button Battery or Sharp Ear Foreign Body", "boolean", "dangerous-foreign-body", "단추형 건전지나 날카로운 물체가 귀 안에 들어갔거나 들어간 것으로 의심되나요?", 120, [G["shared-safety"], G["discharge-trauma"]], S, safety_relevant=True),
        Q("ear.tinnitus_with_immediate_self_harm_risk", "Tinnitus with Immediate Self-harm Risk", "boolean", "tinnitus-self-harm", "이명 때문에 지금 자신을 해칠 생각이나 안전을 지키기 어렵다는 느낌이 있나요?", 119, [G["shared-safety"], G["tinnitus"]], S, safety_relevant=True),
        Q("ear.pulsatile_tinnitus_with_neurological_or_visual_symptoms", "Pulsatile Tinnitus with Neurological or Visual Symptoms", "boolean", "pulsatile-neuro", "맥박에 맞춰 들리는 소리와 함께 새 신경 증상이나 시야 변화가 있나요?", 118, [G["shared-safety"], G["tinnitus"]], S, safety_relevant=True),

        Q("ear.symptom_duration", "Ear Symptom Duration", "string", "duration", "증상은 언제 시작됐고 계속되는지 반복되는지 알려주세요.", 112, [G["common"]], C),
        Q("ear.onset_and_progression", "Ear Symptom Onset and Progression", "coded", "onset-progression", "갑자기 또는 서서히 시작했고, 좋아짐·같음·악화 중 어느 쪽인가요?", 111, [G["common"]], C, allowed_values=["sudden_improving", "sudden_same", "sudden_worsening", "gradual_improving", "gradual_same", "gradual_worsening", "unclear"]),
        Q("ear.laterality", "Ear Laterality", "coded", "laterality", "왼쪽 귀, 오른쪽 귀, 양쪽 귀 중 어디인가요?", 110, [G["common"]], C, allowed_values=["left", "right", "bilateral", "unclear"], mrcm_ref=M),
        Q("ear.pain_severity", "Ear Pain Severity", "coded", "pain-severity", "귀 통증은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 109, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"], terminology_binding={"system": SN, "code": "301354004"}, mrcm_ref=M),
        Q("ear.hearing_function_impact", "Hearing Function Impact", "coded", "hearing-impact", "대화나 전화·TV 소리를 듣는 데 영향이 없음, 약간, 많이, 거의 못 들음 중 어느 정도인가요?", 108, [G["common"], G["hearing-change"]], C, allowed_values=["none", "mild", "major", "near_complete", "unclear"], terminology_binding={"system": SN, "code": "15188001"}, mrcm_ref=M),
        Q("ear.fever_or_systemic_symptoms", "Fever or Systemic Symptoms", "string", "fever-systemic", "열, 오한, 몸살, 구토 또는 전신 쇠약이 함께 있나요?", 103, [G["common"]], R),
        Q("ear.prior_disease_surgery_or_recurrent_episode", "Prior Ear Disease Surgery or Recurrence", "string", "prior-history", "중이염·고막천공·난청·메니에르병, 귀 수술 또는 비슷한 증상 병력이 있나요?", 99, [G["common"]], R),
        Q("ear.current_treatment_device_or_hearing_aid", "Current Ear Treatment or Hearing Device", "string", "treatment-device", "사용 중인 귀약·항생제·보청기·인공와우와 최근 변화가 있나요?", 98, [G["common"]], R),
        Q("ear.recent_uri_water_flight_noise_or_medication", "Recent Ear-related Exposures", "string", "recent-context", "최근 감기, 수영·물놀이, 비행·잠수, 큰 소음, 새 약 복용이 있었나요?", 97, [G["common"]], R),
        Q("ear.other_detail_or_patient_priority", "Other Ear Detail or Patient Priority", "string", "other-detail", "질문에 없지만 꼭 전달하고 싶은 증상이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("ear.pain_location", "Ear Pain Location", "coded", "pain-location", "통증은 귓속, 귓구멍 입구, 귓바퀴, 귀 뒤 중 어디가 가장 심한가요?", 107, [G["pain-infection"]], C, allowed_values=["deep_inside", "canal_entrance", "pinna", "behind_ear", "referred_or_unclear"]),
        Q("ear.pinna_movement_or_tragus_tenderness", "Pinna Movement or Tragus Tenderness", "boolean", "tragus-tenderness", "귓바퀴를 당기거나 귓구멍 앞 돌기를 누르면 더 아픈가요?", 106, [G["pain-infection"]], D),
        Q("ear.itching_or_canal_skin_change", "Ear Itching or Canal Skin Change", "boolean", "itching-skin", "귀가 가렵거나 귓구멍 피부가 붓고 벗겨지나요?", 105, [G["pain-infection"]], D),
        Q("ear.pressure_fullness_or_popping", "Ear Pressure Fullness or Popping", "boolean", "pressure-fullness", "귀가 먹먹하거나 꽉 찬 느낌, 딸깍거림이 있나요?", 104, [G["pain-infection"]], D),
        Q("ear.uri_sore_throat_dental_or_jaw_pain", "URI Throat Dental or Jaw Symptoms", "string", "referred-pain-context", "콧물·코막힘·목 통증, 치통 또는 씹을 때 턱 통증이 함께 있나요?", 96, [G["pain-infection"]], D),
        Q("ear.rash_or_vesicles_around_ear", "Rash or Vesicles around Ear", "boolean", "rash-vesicles", "귀나 얼굴 주변에 발진이나 물집이 있나요?", 95, [G["pain-infection"]], R),

        Q("ear.hearing_change_pattern", "Hearing Change Pattern", "coded", "hearing-pattern", "청력 변화는 갑작스러운 소실, 빠른 악화, 서서히 악화, 들쭉날쭉함 중 무엇인가요?", 107, [G["hearing-change"]], C, allowed_values=["sudden_loss", "rapid_decline", "gradual_decline", "fluctuating", "unclear"]),
        Q("ear.asymmetric_hearing_change", "Asymmetric Hearing Change", "boolean", "asymmetric-hearing", "한쪽 귀가 다른 쪽보다 확실히 덜 들리나요?", 106, [G["hearing-change"]], R),
        Q("ear.associated_tinnitus_vertigo_or_fullness", "Hearing Loss with Tinnitus Vertigo or Fullness", "string", "hearing-associated", "청력 변화와 함께 이명, 회전성 어지럼 또는 귀 먹먹함이 있나요?", 105, [G["hearing-change"]], D),
        Q("ear.noise_exposure_or_acoustic_trauma", "Noise Exposure or Acoustic Trauma", "string", "noise-exposure", "최근 폭발음·공연·기계음 또는 장기간 큰 소음에 노출됐나요?", 104, [G["hearing-change"]], R),
        Q("ear.possible_ototoxic_medication", "Possible Ototoxic Medication Context", "string", "ototoxic-medication", "최근 시작·증량한 약이나 항암제·주사 항생제 등 청력에 영향을 줄 수 있는 치료가 있나요?", 94, [G["hearing-change"]], R),

        Q("ear.discharge_character", "Ear Discharge Character", "coded", "discharge-character", "분비물은 맑은 물, 고름·끈적한 액, 피, 귀지 같은 물질 중 무엇인가요?", 107, [G["discharge-trauma"]], C, allowed_values=["clear_watery", "purulent_sticky", "bloody", "wax_like", "other_unclear"], terminology_binding={"system": SN, "code": "300132001"}, mrcm_ref=M),
        Q("ear.discharge_amount_odor_and_duration", "Ear Discharge Amount Odor and Duration", "string", "discharge-detail", "분비물의 양·냄새와 언제부터 얼마나 자주 나오는지 알려주세요.", 106, [G["discharge-trauma"]], C),
        Q("ear.instrument_cotton_bud_or_foreign_body", "Ear Instrument or Foreign Body", "string", "instrument-foreign-body", "면봉·귀이개·이어폰 등으로 귀를 건드렸거나 다른 물체가 들어갔나요?", 105, [G["discharge-trauma"]], R),
        Q("ear.water_pressure_or_barotrauma_exposure", "Water Pressure or Barotrauma Exposure", "string", "water-pressure", "수영·잠수·비행 또는 큰 압력 변화 뒤 증상이 시작됐나요?", 104, [G["discharge-trauma"]], R),
        Q("ear.suspected_perforation_or_sudden_pain_relief", "Suspected Tympanic Membrane Perforation", "boolean", "perforation-clue", "갑자기 심하게 아픈 뒤 통증이 줄면서 분비물이나 청력 저하가 생겼나요?", 103, [G["discharge-trauma"]], D),

        Q("ear.tinnitus_sound_character", "Tinnitus Sound Character", "string", "tinnitus-sound", "삐-, 윙-, 쉭- 또는 박동음처럼 어떤 소리가 들리는지 표현해주세요.", 107, [G["tinnitus"]], C, terminology_binding={"system": SN, "code": "60862001"}, mrcm_ref=M),
        Q("ear.tinnitus_pulse_synchronous", "Pulse-synchronous Tinnitus", "boolean", "pulse-synchronous", "소리가 심장 박동과 같은 리듬으로 들리나요?", 106, [G["tinnitus"]], R),
        Q("ear.tinnitus_constant_or_intermittent", "Constant or Intermittent Tinnitus", "coded", "tinnitus-timing", "이명은 계속 들리나요, 간헐적으로 들리나요?", 105, [G["tinnitus"]], C, allowed_values=["constant", "intermittent", "unclear"]),
        Q("ear.tinnitus_distress_sleep_or_function", "Tinnitus Distress Sleep or Functional Impact", "coded", "tinnitus-impact", "이명이 수면·집중·일상이나 정서에 미치는 영향은 없음, 약간, 큼, 견디기 어려움 중 어느 정도인가요?", 104, [G["tinnitus"]], R, allowed_values=["none", "mild", "major", "intolerable", "unclear"]),
        Q("ear.tinnitus_with_hearing_change_or_vertigo", "Tinnitus with Hearing Change or Vertigo", "string", "tinnitus-associated", "이명과 함께 청력 저하, 귀 먹먹함 또는 회전성 어지럼이 있나요?", 103, [G["tinnitus"]], D),
    ]
    rules = [
        safety_rule(P, "sudden-hearing-loss", {"fact": "ear.sudden_hearing_loss_within_72h", "equals": True}, "urgent", 980),
        safety_rule(P, "rapid-hearing-decline", {"fact": "ear.rapidly_worsening_hearing_4_to_90_days", "equals": True}, "urgent", 930),
        safety_rule(P, "neurological-deficit", {"fact": "symptom.new_focal_neurological_deficit", "equals": True}, "emergency", 1000),
        safety_rule(P, "uncontrolled-vertigo", {"fact": "ear.acute_uncontrolled_vertigo_or_inability_to_stand", "equals": True}, "emergency", 1000),
        safety_rule(P, "mastoid-warning", {"fact": "ear.postauricular_redness_swelling_tenderness_or_protrusion", "equals": True}, "urgent", 950),
        safety_rule(P, "systemic-illness", {"fact": "ear.severe_systemic_illness_or_high_fever", "equals": True}, "urgent", 930),
        safety_rule(P, "high-risk-host", {"fact": "ear.diabetes_or_immunosuppression_with_severe_pain_or_discharge", "equals": True}, "urgent", 940),
        safety_rule(P, "major-trauma", {"fact": "ear.head_injury_or_penetrating_trauma", "equals": True}, "emergency", 1000),
        safety_rule(P, "post-trauma-discharge", {"fact": "ear.clear_or_bloody_discharge_after_head_injury", "equals": True}, "emergency", 1000),
        safety_rule(P, "dangerous-foreign-body", {"fact": "ear.button_battery_or_sharp_foreign_body", "equals": True}, "emergency", 1000),
        safety_rule(P, "tinnitus-self-harm", {"fact": "ear.tinnitus_with_immediate_self_harm_risk", "equals": True}, "emergency", 1000),
        safety_rule(P, "pulsatile-neuro", {"fact": "ear.pulsatile_tinnitus_with_neurological_or_visual_symptoms", "equals": True}, "urgent", 950),
    ]
    return {"id": "knowledge.generated.ear-hearing-symptoms", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-ear-hearing-symptoms-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="ear.primary_symptom_group", question_budget=38, source_refs=SOURCES)
    branches = {
        "ear_pain_infection": ["ear.pain_location", "ear.pinna_movement_or_tragus_tenderness", "ear.itching_or_canal_skin_change", "ear.pressure_fullness_or_popping", "ear.uri_sore_throat_dental_or_jaw_pain", "ear.rash_or_vesicles_around_ear"],
        "hearing_change": ["ear.hearing_change_pattern", "ear.asymmetric_hearing_change", "ear.associated_tinnitus_vertigo_or_fullness", "ear.noise_exposure_or_acoustic_trauma", "ear.possible_ototoxic_medication"],
        "discharge_trauma": ["ear.discharge_character", "ear.discharge_amount_odor_and_duration", "ear.instrument_cotton_bud_or_foreign_body", "ear.water_pressure_or_barotrauma_exposure", "ear.suspected_perforation_or_sudden_pain_relief"],
        "tinnitus": ["ear.tinnitus_sound_character", "ear.tinnitus_pulse_synchronous", "ear.tinnitus_constant_or_intermittent", "ear.tinnitus_distress_sleep_or_function", "ear.tinnitus_with_hearing_change_or_vertigo"],
        "other_unclear": ["ear.other_detail_or_patient_priority"],
    }
    conditional = {fid for facts in branches.values() for fid in facts}
    policy["required_facts"]["routine"] = [fid for fid in policy["required_facts"]["routine"] if fid not in conditional]
    policy["conditional_required_facts"] = [{"selector_fact": "ear.primary_symptom_group", "cases": branches}]
    return policy


def source_docs():
    defs = [
        ("source.nice.hearing-loss-ng98", "NICE", "Hearing loss in adults: assessment and management", "NG98", "https://www.nice.org.uk/guidance/ng98", "clinical_guideline", 1),
        ("source.nice.tinnitus-ng155", "NICE", "Tinnitus: assessment and management", "NG155", "https://www.nice.org.uk/guidance/ng155/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nhs.ear-infections.2025", "NHS", "Ear infections", "accessed-2026-07-14", "https://www.nhs.uk/conditions/ear-infections/", "public_health_guidance", 7),
        ("source.nhs.hearing-loss.2025", "NHS", "Hearing loss", "accessed-2026-07-14", "https://www.nhs.uk/conditions/hearing-loss/", "public_health_guidance", 7),
        ("source.nhs.mastoiditis.2025", "NHS", "Mastoiditis", "accessed-2026-07-14", "https://www.nhs.uk/conditions/mastoiditis/", "public_health_guidance", 7),
        ("source.uhsussex.sudden-hearing-change.2025", "University Hospitals Sussex NHS Foundation Trust", "What to do if you have a sudden change in hearing", "accessed-2026-07-14", "https://www.uhsussex.nhs.uk/resources/what-to-do-if-you-have-a-sudden-change-in-hearing/", "clinical_guideline", 1),
        ("source.stom.ear-hearing.20260714", "Infoclinic", "STOM ear and hearing terminology mapping summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", 30),
    ]
    artifacts = [{"id": i, "kind": "terminology_mapping_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "metadata_only_not_cached", "license_status": "unknown", "complete": False, "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"), "assertions": ["Build-Time only; Runtime does not browse; content remains unreviewed."]} for i, pub, title, version, url, profile, days in defs]
    research = {"id": "source-manifest.primary-care-ear-hearing-symptoms-research", "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.ear-hearing", "generated_clinical_knowledge", "knowledge/generated/otologic/ear-hearing-symptoms/ear-hearing-symptoms.json", True), ("source.mapping.ear-hearing", "terminology_mapping", "mappings/terminology/snomed-mrcm-ear-hearing-symptoms.json", False), ("source.external.ear-hearing", "external_source_manifest", "sources/manifests/primary-care-ear-hearing-symptoms-research.json", False), ("source.policy.ear-hearing", "runtime_policy", "policies/primary-care-ear-hearing-symptoms-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-ear-hearing-symptoms", "version": VERSION, "acquired_at": CREATED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        def satisfy(condition, hidden):
            if "all" in condition:
                for child in condition["all"]: satisfy(child, hidden)
            elif "equals" in condition: hidden[condition["fact"]] = {"value": condition["equals"]}
            elif "in" in condition: hidden[condition["fact"]] = {"value": condition["in"][0]}
        hidden = {}; satisfy(rule["when"], hidden)
        key = rule["id"].split("safety.")[1]; level = rule["then"]["safety_level"]
        out[f"EAR-{key.upper()}.json"] = {"id": f"EAR-{key.upper()}", "simulation_language": "ko", "persona": {"age": 24 + i}, "initial_statement": {"ko": "귀나 청력이 불편해서 왔어요."}, "hidden_state": hidden, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 30, "forbidden_assertions": ["diagnosis.otitis_media", "diagnosis.sudden_sensorineural_hearing_loss", "diagnosis.mastoiditis"]}, "provenance": provenance(SOURCES)}
    policy = completion(f); required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["tinnitus"])
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}; hidden = {}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        else: hidden[fid] = {"value": "없음"}
    hidden["ear.primary_symptom_group"] = {"value": "tinnitus"}; hidden["ear.tinnitus_sound_character"] = {"value": "삐 소리"}
    declined = "ear.current_treatment_device_or_hearing_aid"; hidden.pop(declined)
    out["EAR-TINNITUS-DATA-ABSENT.json"] = {"id": "EAR-TINNITUS-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 52}, "initial_statement": {"ko": "오른쪽 귀에서 삐 소리가 나요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-declined"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 42, "forbidden_assertions": ["diagnosis.tinnitus_cause"]}, "provenance": provenance(["source.nice.tinnitus-ng155", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Ear and Hearing Symptoms", intents=[("intent.characterize_symptom", "Characterize Symptom"), ("intent.screen_red_flags", "Screen Red Flags"), ("intent.differentiate_common_causes", "Differentiate Common Sources"), ("intent.risk_assessment", "Risk Assessment")])
    primary, research = source_docs()
    concepts = [("301354004", "Pain of ear (finding)"), ("15188001", "Hearing loss (disorder)"), ("79471008", "Sudden hearing loss (disorder)"), ("60862001", "Tinnitus (finding)"), ("300132001", "Ear discharge (finding)")]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": code, "display": display, "mapping_status": "active_candidate_returned"} for code, display in concepts], "laterality": {"reference_set": "723264001", "postcoordination_policy": "policy.snomed-postcoordination-laterality", "application": "Apply only when the selected finding site is confirmed as a member."}, "validation": {"method": "build_time_mapping_support_query", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "mapping_candidates_verified_mrcm_pending"}, "provenance": provenance(["source.stom.ear-hearing.20260714"])}
    docs = [("knowledge/base/primary-care-ear-hearing-symptoms.json", graph), ("rules/base/primary-care-ear-hearing-symptoms.json", rules), ("knowledge/generated/otologic/ear-hearing-symptoms/ear-hearing-symptoms.json", f), ("mappings/terminology/snomed-mrcm-ear-hearing-symptoms.json", mapping), ("sources/manifests/primary-care-ear-hearing-symptoms.json", primary), ("sources/manifests/primary-care-ear-hearing-symptoms-research.json", research), ("policies/primary-care-ear-hearing-symptoms-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/otologic/ear-hearing-symptoms/" + name, case)


if __name__ == "__main__": main()
