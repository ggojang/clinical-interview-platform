#!/usr/bin/env python3
"""Materialize unreviewed grouped eye-symptom knowledge."""
from profile_support import *

P = "eye-symptoms"
RFE = "rfe.eye_symptoms"
M = "mapping.snomed-mrcm.eye-symptoms"
SN = "http://snomed.info/sct"
SOURCES = [
    "source.nhs.red-eye.2025", "source.nhs.eye-pain.2025",
    "source.nhs.vision-loss.2025", "source.nhs.floaters-flashes.2023",
    "source.nhs.glaucoma.2025", "source.uhd.chemical-eye-injury.2026",
    "source.moorfields.orbital-cellulitis.2021", "source.stom.eye.20260714",
]
G = {k: f"group.eye.{k}" for k in (
    "routing", "shared-safety", "common", "red-eye-surface",
    "visual-disturbance", "eyelid-periorbital", "trauma-foreign-body",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups,
                 intents=intents, **kwargs)


def fragment():
    e = [
        Q("eye.primary_symptom_group", "Primary Eye Symptom Group", "coded", "primary-group", "가장 불편한 증상은 충혈·표면 불편, 시력·시야 변화, 눈꺼풀·눈 주변 문제, 외상·이물질 중 무엇인가요?", 130, [G["routing"]], C, allowed_values=["red_eye_surface", "visual_disturbance", "eyelid_periorbital", "trauma_foreign_body", "other_unclear"]),
        Q("eye.sudden_complete_or_major_vision_loss", "Sudden Complete or Major Vision Loss", "boolean", "sudden-vision-loss", "한쪽 또는 양쪽 눈이 갑자기 보이지 않거나 시력이 크게 떨어졌나요?", 129, [G["shared-safety"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "15203004"}),
        Q("eye.chemical_exposure", "Chemical Eye Exposure", "boolean", "chemical-exposure", "세제·산·알칼리·시멘트 같은 화학물질이 눈에 들어갔나요?", 128, [G["shared-safety"], G["trauma-foreign-body"]], S, safety_relevant=True),
        Q("eye.penetrating_or_high_velocity_injury", "Penetrating or High Velocity Eye Injury", "boolean", "penetrating-injury", "날카로운 물체가 눈을 찔렀거나 금속·유리 조각 등이 빠르게 튀어 눈을 맞았나요?", 127, [G["shared-safety"], G["trauma-foreign-body"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "367132005"}),
        Q("eye.object_embedded_or_globe_deformed", "Embedded Object or Globe Deformity", "boolean", "embedded-object", "물체가 눈에 박혀 있거나 눈 모양이 달라지고 피가 나는 것처럼 보이나요?", 126, [G["shared-safety"], G["trauma-foreign-body"]], S, safety_relevant=True),
        Q("eye.severe_or_sudden_pain", "Severe or Sudden Eye Pain", "boolean", "severe-pain", "눈 통증이 갑자기 시작됐거나 매우 심한가요?", 125, [G["shared-safety"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "41652007"}, mrcm_ref=M),
        Q("eye.photophobia", "Photophobia", "boolean", "photophobia", "빛을 볼 때 눈이 심하게 아프거나 견디기 어렵나요?", 124, [G["shared-safety"], G["red-eye-surface"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "409668002"}, mrcm_ref=M),
        Q("eye.red_painful_with_vision_change", "Red Painful Eye with Vision Change", "boolean", "red-pain-vision", "눈이 붉고 아프면서 시야가 흐리거나 시력이 변했나요?", 123, [G["shared-safety"], G["red-eye-surface"]], S, safety_relevant=True),
        Q("eye.halos_headache_nausea_or_vomiting", "Halos Headache Nausea or Vomiting", "boolean", "halos-nausea", "불빛 주변에 무지개빛 테가 보이면서 심한 두통, 메스꺼움 또는 구토가 있나요?", 122, [G["shared-safety"], G["visual-disturbance"]], S, safety_relevant=True),
        Q("eye.new_or_increased_flashes_floaters", "New or Increased Flashes or Floaters", "boolean", "flashes-floaters", "처음 생겼거나 갑자기 늘어난 번쩍임·검은 점·실오라기 같은 것이 보이나요?", 121, [G["shared-safety"], G["visual-disturbance"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "139547009"}),
        Q("eye.curtain_shadow_or_field_loss", "Curtain Shadow or Visual Field Loss", "boolean", "curtain-shadow", "시야 한쪽에서 검은 커튼이나 그림자가 퍼지거나 일부가 가려지나요?", 120, [G["shared-safety"], G["visual-disturbance"]], S, safety_relevant=True),
        Q("eye.contact_lens_with_pain_or_vision_change", "Contact Lens with Pain or Vision Change", "boolean", "contact-lens-warning", "콘택트렌즈를 착용하는 눈이 붉고 아프거나 시력이 달라졌나요?", 119, [G["shared-safety"], G["red-eye-surface"]], S, safety_relevant=True),
        Q("eye.recent_surgery_injection_with_pain_or_vision_loss", "Recent Eye Procedure with Pain or Vision Loss", "boolean", "recent-procedure-warning", "최근 4주 안에 눈 수술·주사·레이저를 받은 뒤 심한 통증이나 시력 저하가 생겼나요?", 118, [G["shared-safety"]], S, safety_relevant=True),
        Q("eye.proptosis_or_painful_restricted_movement", "Proptosis or Painful Restricted Eye Movement", "boolean", "orbital-warning", "눈이 앞으로 튀어나와 보이거나 눈을 움직일 때 아프고 잘 움직이지 않나요?", 117, [G["shared-safety"], G["eyelid-periorbital"]], S, safety_relevant=True),
        Q("eye.periorbital_swelling_with_fever_or_unwell", "Periorbital Swelling with Fever or Systemic Illness", "boolean", "periorbital-fever", "눈꺼풀·눈 주변이 심하게 붓고 열이 나거나 온몸이 많이 아픈가요?", 116, [G["shared-safety"], G["eyelid-periorbital"]], S, safety_relevant=True),
        Q("symptom.new_focal_neurological_deficit", "New Focal Neurological Deficit", "boolean", "neurological-deficit", "시력 변화와 함께 한쪽 힘 빠짐·감각 저하, 말이 어눌함, 얼굴 처짐이 새로 생겼나요?", 115, [G["shared-safety"], G["visual-disturbance"]], S, safety_relevant=True, reuse_existing=True),

        Q("eye.symptom_duration", "Eye Symptom Duration", "string", "duration", "증상은 언제 시작됐고 계속되는지 반복되는지 알려주세요.", 110, [G["common"]], C),
        Q("eye.onset_and_progression", "Eye Symptom Onset and Progression", "coded", "onset-progression", "증상은 갑자기 또는 서서히 시작했고, 좋아짐·같음·악화 중 어느 쪽인가요?", 109, [G["common"]], C, allowed_values=["sudden_improving", "sudden_same", "sudden_worsening", "gradual_improving", "gradual_same", "gradual_worsening", "unclear"]),
        Q("eye.laterality", "Eye Laterality", "coded", "laterality", "왼쪽 눈, 오른쪽 눈, 양쪽 눈 중 어디인가요?", 108, [G["common"]], C, allowed_values=["left", "right", "bilateral", "unclear"], mrcm_ref=M),
        Q("eye.current_vision_impact", "Current Vision Impact", "coded", "vision-impact", "현재 시력 영향은 없음, 약간 흐림, 많이 흐림, 거의 보이지 않음 중 무엇인가요?", 107, [G["common"], G["visual-disturbance"]], C, allowed_values=["none", "mild_blur", "major_blur", "near_complete_loss", "unclear"]),
        Q("eye.pain_severity", "Eye Pain Severity", "coded", "pain-severity", "눈 통증은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 106, [G["common"]], C, allowed_values=["none", "mild", "moderate", "severe"]),
        Q("eye.prior_eye_disease_or_similar_episode", "Prior Eye Disease or Similar Episode", "string", "prior-history", "녹내장·망막질환·포도막염·각막질환 같은 눈 질환이나 비슷한 증상 병력이 있나요?", 96, [G["common"]], R),
        Q("eye.current_drops_medication_or_contact_lens", "Eye Drops Medication or Contact Lens", "string", "treatment-context", "사용 중인 안약·눈 관련 약, 콘택트렌즈 종류와 마지막 착용 시점을 알려주세요.", 95, [G["common"]], R),
        Q("history.diabetes_immunosuppression_or_autoimmune_disease", "Diabetes Immunosuppression or Autoimmune Disease", "string", "medical-context", "당뇨, 면역저하, 자가면역질환 또는 암 치료 중인 상태가 있나요?", 94, [G["common"]], R),
        Q("eye.other_detail_or_patient_priority", "Other Eye Detail or Patient Priority", "string", "other-detail", "질문에 없지만 꼭 전달하고 싶은 눈 증상이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("eye.redness_present", "Eye Redness Present", "boolean", "redness", "눈 흰자나 눈꺼풀 안쪽이 붉나요?", 105, [G["red-eye-surface"]], C, terminology_binding={"system": SN, "code": "703630003"}, mrcm_ref=M),
        Q("eye.discharge_character", "Eye Discharge Character", "coded", "discharge", "눈곱·분비물은 없음, 물 같음, 끈적하거나 고름 같음 중 무엇인가요?", 104, [G["red-eye-surface"]], D, allowed_values=["none", "watery", "sticky_purulent", "unclear"], terminology_binding={"system": SN, "code": "246679005"}, mrcm_ref=M),
        Q("eye.itching", "Eye Itching", "boolean", "itching", "눈이 주로 가렵나요?", 103, [G["red-eye-surface"]], D),
        Q("eye.gritty_or_foreign_body_sensation", "Gritty or Foreign Body Sensation", "boolean", "gritty", "모래가 들어간 듯 까끌거리거나 이물감이 있나요?", 102, [G["red-eye-surface"]], D),
        Q("eye.recent_uri_allergy_or_exposure", "Recent URI Allergy or Eye Exposure", "string", "surface-context", "최근 감기·알레르기, 아픈 사람 접촉, 화장품·수영장·연기·먼지 노출이 있었나요?", 93, [G["red-eye-surface"]], D),

        Q("eye.visual_change_type", "Visual Change Type", "coded", "visual-type", "시야 변화는 흐림, 겹쳐 보임, 번쩍임·비문, 시야 일부 가림, 색 변화, 일시적 소실 중 무엇인가요?", 105, [G["visual-disturbance"]], C, allowed_values=["blur", "double", "flashes_floaters", "field_defect", "color_change", "transient_loss", "other_unclear"], terminology_binding={"system": SN, "code": "267726008"}),
        Q("eye.monocular_or_binocular_visual_change", "Monocular or Binocular Visual Change", "coded", "mono-binocular", "한쪽씩 가려보면 한 눈에서만 지속되나요, 두 눈에서 보이나요?", 104, [G["visual-disturbance"]], C, allowed_values=["monocular", "binocular", "not_checked", "unclear"]),
        Q("eye.double_vision_resolves_covering_one_eye", "Diplopia Cover Test History", "coded", "diplopia-cover", "겹쳐 보일 때 한쪽 눈을 가리면 겹침이 사라지나요?", 99, [G["visual-disturbance"]], D, allowed_values=["resolves", "persists", "not_applicable", "not_checked"]),
        Q("eye.headache_scalp_tenderness_or_jaw_pain", "Headache Scalp Tenderness or Jaw Pain", "boolean", "arteritic-context", "새 두통, 두피를 만질 때 통증, 씹을 때 턱 통증이 함께 있나요?", 98, [G["visual-disturbance"]], R),
        Q("eye.myopia_retinal_history_or_family_detachment", "Myopia Retinal or Detachment History", "string", "retinal-risk", "심한 근시, 망막질환·망막박리, 백내장 수술 또는 가족의 망막박리 병력이 있나요?", 97, [G["visual-disturbance"]], R),

        Q("eye.eyelid_swelling_lump_or_droop", "Eyelid Swelling Lump or Droop", "coded", "eyelid-problem", "눈꺼풀 문제는 전체 부종, 국소 멍울, 처짐, 피부 변화 중 무엇인가요?", 105, [G["eyelid-periorbital"]], C, allowed_values=["diffuse_swelling", "localized_lump", "droop", "skin_change", "other_unclear"], terminology_binding={"system": SN, "code": "193967004"}, mrcm_ref=M),
        Q("eye.eyelid_tender_red_hot_or_draining", "Tender Red Hot or Draining Eyelid", "boolean", "eyelid-inflammation", "눈꺼풀·눈 주변이 붉고 뜨겁거나 아프고 진물·고름이 있나요?", 104, [G["eyelid-periorbital"]], D),
        Q("eye.vesicles_rash_or_facial_spread", "Vesicles Rash or Facial Spread", "boolean", "vesicle-rash", "눈꺼풀이나 이마·코 주변에 물집·발진이 있거나 붉은 부위가 퍼지나요?", 103, [G["eyelid-periorbital"]], R),
        Q("eye.recent_sinus_dental_skin_infection", "Recent Sinus Dental or Skin Infection", "string", "infection-context", "최근 부비동염·감기, 치과 감염, 눈 주변 상처·벌레 물림이 있었나요?", 93, [G["eyelid-periorbital"]], R),

        Q("eye.injury_mechanism_and_time", "Eye Injury Mechanism and Time", "string", "injury-mechanism", "언제 무엇에 어떻게 다쳤는지, 충격 속도와 보호안경 착용 여부를 알려주세요.", 105, [G["trauma-foreign-body"]], C),
        Q("eye.foreign_body_sensation_after_exposure", "Foreign Body Sensation after Exposure", "boolean", "foreign-body", "먼지·모래·금속·유리 등이 들어간 뒤 계속 이물감이 있나요?", 104, [G["trauma-foreign-body"]], C, terminology_binding={"system": SN, "code": "82576008"}),
        Q("eye.irrigation_or_first_aid_done", "Eye Irrigation or First Aid Done", "string", "first-aid", "눈을 씻었는지, 콘택트렌즈를 뺐는지 등 지금까지 한 처치를 알려주세요.", 103, [G["trauma-foreign-body"]], R),
        Q("eye.bleeding_cut_or_inability_to_open", "Eye Bleeding Cut or Inability to Open", "boolean", "trauma-severity", "눈이나 눈꺼풀에 깊은 상처·출혈이 있거나 눈을 뜰 수 없나요?", 102, [G["trauma-foreign-body"]], R),
    ]
    rules = [
        safety_rule(P, "sudden-vision-loss", {"fact": "eye.sudden_complete_or_major_vision_loss", "equals": True}, "emergency", 1000),
        safety_rule(P, "chemical-exposure", {"fact": "eye.chemical_exposure", "equals": True}, "emergency", 1000),
        safety_rule(P, "penetrating-injury", {"fact": "eye.penetrating_or_high_velocity_injury", "equals": True}, "emergency", 1000),
        safety_rule(P, "embedded-object", {"fact": "eye.object_embedded_or_globe_deformed", "equals": True}, "emergency", 1000),
        safety_rule(P, "severe-pain-vision", {"all": [{"fact": "eye.severe_or_sudden_pain", "equals": True}, {"fact": "eye.current_vision_impact", "in": ["major_blur", "near_complete_loss"]}]}, "emergency", 1000),
        safety_rule(P, "halos-nausea", {"fact": "eye.halos_headache_nausea_or_vomiting", "equals": True}, "emergency", 1000),
        safety_rule(P, "neurological-deficit", {"fact": "symptom.new_focal_neurological_deficit", "equals": True}, "emergency", 1000),
        safety_rule(P, "curtain-shadow", {"fact": "eye.curtain_shadow_or_field_loss", "equals": True}, "urgent", 950),
        safety_rule(P, "new-flashes-floaters", {"fact": "eye.new_or_increased_flashes_floaters", "equals": True}, "urgent", 920),
        safety_rule(P, "red-pain-vision", {"fact": "eye.red_painful_with_vision_change", "equals": True}, "urgent", 920),
        safety_rule(P, "photophobia", {"fact": "eye.photophobia", "equals": True}, "urgent", 900),
        safety_rule(P, "contact-lens-warning", {"fact": "eye.contact_lens_with_pain_or_vision_change", "equals": True}, "urgent", 900),
        safety_rule(P, "recent-procedure-warning", {"fact": "eye.recent_surgery_injection_with_pain_or_vision_loss", "equals": True}, "urgent", 900),
        safety_rule(P, "orbital-warning", {"fact": "eye.proptosis_or_painful_restricted_movement", "equals": True}, "urgent", 900),
        safety_rule(P, "periorbital-fever", {"fact": "eye.periorbital_swelling_with_fever_or_unwell", "equals": True}, "urgent", 900),
    ]
    return {"id": "knowledge.generated.eye-symptoms", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-eye-symptoms-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def source_docs():
    defs = [
        ("source.nhs.red-eye.2025", "NHS", "Red eye", "reviewed-2025", "https://www.nhs.uk/symptoms/red-eye/", "public_health_guidance", 7),
        ("source.nhs.eye-pain.2025", "NHS", "Eye pain", "reviewed-2025-10-21", "https://www.nhs.uk/symptoms/eye-pain/", "public_health_guidance", 7),
        ("source.nhs.vision-loss.2025", "NHS", "Vision loss", "reviewed-2025", "https://www.nhs.uk/conditions/vision-loss/", "public_health_guidance", 7),
        ("source.nhs.floaters-flashes.2023", "NHS", "Floaters and flashes in the eyes", "reviewed-2023", "https://www.nhs.uk/symptoms/floaters-and-flashes-in-the-eyes/", "public_health_guidance", 7),
        ("source.nhs.glaucoma.2025", "NHS", "Glaucoma", "reviewed-2025", "https://www.nhs.uk/conditions/glaucoma/", "public_health_guidance", 7),
        ("source.uhd.chemical-eye-injury.2026", "University Hospitals Dorset NHS Foundation Trust", "Chemical injury to the eye", "reviewed-2026", "https://www.uhd.nhs.uk/uploads/about/docs/our_publications/patient_information_leaflets/Eye_Department/Chemical_injury_to_the_eye_040-21.pdf", "public_health_guidance", 7),
        ("source.moorfields.orbital-cellulitis.2021", "Moorfields Eye Hospital NHS Foundation Trust", "Preseptal and orbital cellulitis", "accessed-2026-07-14", "https://www.moorfields.nhs.uk/for-health-professionals/childrens-eye-conditions-management/preseptalorbital-cellulitis", "clinical_guideline", 1),
        ("source.stom.eye.20260714", "Infoclinic", "STOM eye symptom terminology, MRCM and lateralizable anatomy", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/41652007", "terminology_server", 30),
    ]
    arts = [{"id": i, "kind": "terminology_mrcm_query_summary" if p == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": t, "version": v, "url": u, "language": "en", "digest": "metadata_only_not_cached", "license_status": "unknown", "complete": False, "monitor_profile": p, "monitor_interval_days": d, "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-08-13" if d == 30 else ("2026-07-21" if d == 7 else "2026-07-15"), "assertions": ["Build-Time only; Runtime does not browse; content remains unreviewed."]} for i, pub, t, v, u, p, d in defs]
    research = {"id": "source-manifest.primary-care-eye-symptoms-research", "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only", "artifacts": arts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.eye", "generated_clinical_knowledge", "knowledge/generated/ophthalmic/eye-symptoms/eye-symptoms.json", True), ("source.mapping.eye", "terminology_mapping", "mappings/terminology/snomed-mrcm-eye-symptoms.json", False), ("source.external.eye", "external_source_manifest", "sources/manifests/primary-care-eye-symptoms-research.json", False), ("source.policy.eye", "runtime_policy", "policies/primary-care-eye-symptoms-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-eye-symptoms", "version": VERSION, "acquired_at": CREATED_AT, "artifacts": [{"id": i, "kind": k, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": p, "digest": "computed_at_build", "license_status": "allowed" if c else "unknown", "complete": c} for i, k, p, c in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="eye.primary_symptom_group", question_budget=34, source_refs=SOURCES)
    branch = {
        "red_eye_surface": ["eye.redness_present", "eye.discharge_character", "eye.itching", "eye.gritty_or_foreign_body_sensation", "eye.recent_uri_allergy_or_exposure"],
        "visual_disturbance": ["eye.visual_change_type", "eye.monocular_or_binocular_visual_change", "eye.double_vision_resolves_covering_one_eye", "eye.headache_scalp_tenderness_or_jaw_pain", "eye.myopia_retinal_history_or_family_detachment"],
        "eyelid_periorbital": ["eye.eyelid_swelling_lump_or_droop", "eye.eyelid_tender_red_hot_or_draining", "eye.vesicles_rash_or_facial_spread", "eye.recent_sinus_dental_skin_infection"],
        "trauma_foreign_body": ["eye.injury_mechanism_and_time", "eye.foreign_body_sensation_after_exposure", "eye.irrigation_or_first_aid_done", "eye.bleeding_cut_or_inability_to_open"],
        "other_unclear": ["eye.other_detail_or_patient_priority"],
    }
    conditional = {x for values in branch.values() for x in values}
    p["required_facts"]["routine"] = [x for x in p["required_facts"]["routine"] if x not in conditional]
    p["conditional_required_facts"] = [{"selector_fact": "eye.primary_symptom_group", "cases": branch}]
    return p


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        def satisfy(c, h):
            if "all" in c:
                for x in c["all"]: satisfy(x, h)
            elif "equals" in c: h[c["fact"]] = {"value": c["equals"]}
            elif "in" in c: h[c["fact"]] = {"value": c["in"][0]}
        hidden = {}; satisfy(rule["when"], hidden)
        key = rule["id"].split("safety.")[1]; level = rule["then"]["safety_level"]
        out[f"EYE-{key.upper()}.json"] = {"id": f"EYE-{key.upper()}", "simulation_language": "ko", "persona": {"age": 28 + i}, "initial_statement": {"ko": "눈이 불편해서 왔어요."}, "hidden_state": hidden, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 28, "forbidden_assertions": ["diagnosis.glaucoma", "diagnosis.retinal_detachment", "diagnosis.orbital_cellulitis"]}, "provenance": provenance(SOURCES)}
    policy = completion(f); required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["red_eye_surface"])
    by_id = {x["fact"]["id"]: x["fact"] for x in f["entries"]}; hidden = {}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        else: hidden[fid] = {"value": "없음"}
    hidden["eye.primary_symptom_group"] = {"value": "red_eye_surface"}; hidden["eye.redness_present"] = {"value": True}
    declined = "eye.current_drops_medication_or_contact_lens"; hidden.pop(declined)
    out["EYE-RED-DATA-ABSENT.json"] = {"id": "EYE-RED-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 36}, "initial_statement": {"ko": "오른쪽 눈이 충혈됐어요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-declined"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 38, "forbidden_assertions": ["diagnosis.conjunctivitis"]}, "provenance": provenance(["source.nhs.red-eye.2025", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Eye Symptoms", intents=[("intent.characterize_symptom", "Characterize Symptom"), ("intent.screen_red_flags", "Screen Red Flags"), ("intent.differentiate_common_causes", "Differentiate Common Sources"), ("intent.risk_assessment", "Risk Assessment")])
    primary, research = source_docs()
    concepts = [("41652007", "Pain in eye (finding)", 20), ("703630003", "Red eye (finding)", 20), ("409668002", "Photophobia (finding)", 20), ("246679005", "Discharge from eye (finding)", 20), ("193967004", "Swelling of eyelid (finding)", 20), ("371398005", "Eye region structure (body structure)", 8)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "attribute_count_returned": n} for c, d, n in concepts], "checks": [{"focus_code": c, "attribute_code": a, "allowed": True} for c, _, _ in concepts[:5] for a in ("363698007", "246112005")], "unsupported_checks": [{"focus_code": "267726008", "display": "Blurred vision (disorder)", "attribute_count_returned": 0, "mrcm_status": "unsupported_by_endpoint"}], "laterality": {"reference_set": "723264001", "finding_site_code": "371398005", "display": "Eye region structure (body structure)", "member": True, "postcoordination_policy": "policy.snomed-postcoordination-laterality"}, "validation": {"method": "build_time_live_mrcm_and_refset_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "partial_provisional_pass"}, "provenance": provenance(["source.stom.eye.20260714"])}
    docs = [("knowledge/base/primary-care-eye-symptoms.json", graph), ("rules/base/primary-care-eye-symptoms.json", rules), ("knowledge/generated/ophthalmic/eye-symptoms/eye-symptoms.json", f), ("mappings/terminology/snomed-mrcm-eye-symptoms.json", mapping), ("sources/manifests/primary-care-eye-symptoms.json", primary), ("sources/manifests/primary-care-eye-symptoms-research.json", research), ("policies/primary-care-eye-symptoms-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/ophthalmic/eye-symptoms/" + name, case)


if __name__ == "__main__": main()
