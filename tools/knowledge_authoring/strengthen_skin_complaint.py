#!/usr/bin/env python3
"""Strengthen research-only skin-complaint knowledge for clinician handoff."""
from __future__ import annotations

import json

import seed_skin_complaint
from profile_support import ROOT, completion_policy, entry, write_json


P = "skin"
FRAGMENT = "knowledge/generated/dermatological/skin-complaint/skin-complaint.json"
POLICY = "policies/primary-care-skin-complaint-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
RESEARCH = "sources/manifests/primary-care-skin-complaint-research.json"
CREATED = "2026-07-20T00:00:00Z"
SOURCES = [
    "source.nhs.anaphylaxis.2026",
    "source.nice.ng240.meningococcal-rash.2026",
    "source.nhs.stevens-johnson.2026",
    "source.nhs.cellulitis.2024",
    "source.nice.ng12.skin-cancer.2026",
    "source.nice.cg183.drug-allergy.2014",
    "source.nice.ng141.cellulitis.2026",
    "source.nice.ng14.melanoma.2026",
    "source.aad.rash-warning.2024",
]
G = {key: f"group.skin.{key}" for key in (
    "routing", "course", "morphology-detail", "drug-detail",
    "infection-detail", "exposure-detail", "lesion-detail", "history-detail",
    "treatment-detail", "life-stage", "function-detail", "handoff",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]


def provenance(source_refs: list[str]) -> dict:
    return {
        "created_by": {"type": "ai", "id": "codex-gpt5"},
        "created_at": CREATED,
        "source_refs": source_refs,
        "review_status": "unreviewed",
        "version": "0.1.0",
    }


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def q(
    fact_id: str,
    display: str,
    value_type: str,
    key: str,
    wording: str,
    score: int,
    group: str,
    intents: list[str],
    **kwargs,
) -> dict:
    return entry(
        P, fact_id, display, value_type, key, wording, score, key,
        [G[group]], intents=intents, **kwargs,
    )


def fragment() -> dict:
    doc = load(FRAGMENT)
    contexts = [
        "acute_widespread_or_rapid", "local_inflammatory_or_wound",
        "medicine_or_allergic_timing", "recurrent_itch_or_rash",
        "pigmented_or_persistent_lesion", "child_or_proxy",
        "followup_or_result_review", "other_or_unclear",
    ]
    additions = [
        q("skin.primary_context", "Primary Skin Complaint Context", "coded", "primary-context", "가장 가까운 상황은 급성·빠르게 퍼지는 피부 변화, 국소 염증·상처, 약물·알레르기 시간관계, 반복 가려움·발진, 점·지속 병변, 소아·보호자 응답, 추적·결과 확인, 또는 불분명 중 무엇인가요?", 117, "routing", C + R, allowed_values=contexts),
        q("skin.patient_words_first_notice_and_main_concern", "Patient Description and Main Concern", "string", "patient-words", "본인의 표현으로 처음 알아차린 피부 변화, 현재 가장 불편한 점과 가장 걱정되는 점을 알려주세요.", 116, "course", C),
        q("skin.first_latest_timeline_course_recurrence_and_baseline", "Detailed Skin Timeline", "string", "timeline", "처음과 가장 최근 피부 변화의 날짜·시각, 퍼짐·호전·악화·반복 과정과 평소 피부 상태에서 달라진 점을 알려주세요.", 115, "course", C + R),
        q("skin.exact_site_side_extent_sequence_and_body_distribution", "Exact Site Side and Distribution", "string", "site-detail", "정확한 신체 부위와 좌우, 한 곳 또는 여러 곳인지, 시작 부위부터 퍼진 순서와 대략적인 범위를 알려주세요.", 114, "morphology-detail", C + R, terminology_binding={"system": "http://snomed.info/sct", "focus_code": "95324001", "attribute_code": "363698007"}, mrcm_ref="mapping.snomed-mrcm.skin-complaint"),
        q("skin.count_dimensions_shape_border_colour_surface_and_measurement", "Lesion Morphology and Measurement", "string", "morphology-measurement", "병변 개수, 가로·세로 mm 또는 cm, 모양·경계·색·표면·두께와 측정 방법을 알려주세요. 모르면 확인하지 못했다고 답해 주세요.", 113, "morphology-detail", C + R),
        q("skin.photo_date_scale_lighting_focus_source_and_change", "Image Provenance and Quality", "string", "photo-provenance", "사진이 있다면 촬영 날짜·시각, 자·동전 같은 크기 기준, 조명·초점·색 재현, 촬영자와 이전 사진 대비 변화를 알려주세요.", 112, "morphology-detail", C + R),
        q("skin.skin_tone_visibility_and_patient_colour_description", "Skin Tone and Visibility Context", "string", "visibility-context", "평소 피부색과 비교해 환자가 표현하는 색 변화, 눌렀을 때 변화와 사진·화면에서 잘 보이지 않는 부분을 알려주세요.", 111, "morphology-detail", C + R),
        q("skin.local_symptom_sequence_itch_pain_burning_tenderness_and_sensation", "Local Symptom Sequence", "string", "local-symptom-sequence", "가려움·통증·화끈거림·압통·저림 또는 감각 변화가 있다면 각각 시작 순서, 지속시간과 피부 변화 전후 관계를 알려주세요.", 110, "course", C + R),
        q("skin.systemic_symptom_sequence_fever_chills_malaise_joint_and_nodes", "Systemic Symptom Sequence", "string", "systemic-sequence", "열·오한·심한 피로·관절통·목 또는 겨드랑이 멍울이 있다면 피부 변화 전후 시작 순서와 현재 상태를 알려주세요.", 109, "infection-detail", C + S),
        q("skin.mouth_eye_genital_and_other_mucosal_site_timeline", "Mucosal Site Detail", "string", "mucosal-detail", "입술·입안·목·눈·요도·성기 주변의 통증·물집·헐음이 있다면 정확한 부위와 시작 시점을 알려주세요.", 108, "drug-detail", C + S),
        q("skin.suspected_medicine_product_strength_route_indication_start_last_dose_and_interval", "Structured Suspected Medicine Exposure", "string", "medicine-timeline", "의심되는 약마다 제품명·성분명, 함량·제형·경로·복용 목적, 시작/변경일, 복용 횟수와 마지막 사용부터 피부 변화까지 시간을 알려주세요.", 107, "drug-detail", D + R),
        q("skin.previous_same_medicine_class_reaction_and_allergy_record", "Previous Medicine Reaction", "string", "previous-drug-reaction", "같은 약이나 유사 계열 약으로 이전에 피부·호흡·전신 반응이 있었는지, 당시 증상·날짜와 알레르기 기록 내용을 알려주세요.", 106, "drug-detail", D + R),
        q("skin.topical_cosmetic_cleaner_adhesive_glove_and_supplement_exposure", "Topical and Product Exposure", "string", "product-exposure", "새 연고·화장품·세정제·세제·염색약·접착제·장갑·한약·보충제의 제품명, 사용 부위·시작일과 피부 변화의 시간관계를 알려주세요.", 105, "exposure-detail", D + R),
        q("skin.occupation_hobby_heat_sweat_sun_plant_animal_and_contact_exposure", "Environmental and Occupational Exposure", "string", "environment-exposure", "직업·취미에서 물·기름·화학물질·금속·식물·동물·햇빛·열·땀·마찰 노출과 보호구 사용, 증상과의 시간관계를 알려주세요.", 104, "exposure-detail", D + R),
        q("skin.contact_travel_water_bite_wound_procedure_and_infection_timeline", "Infectious and Injury Exposure Timeline", "string", "infection-exposure", "비슷한 증상 접촉자, 최근 여행, 수영·해수·오염수, 벌레·동물 물림, 상처·수술·주사와 피부 변화의 날짜 관계를 알려주세요.", 103, "infection-detail", D + R),
        q("skin.pus_odour_crust_drainage_open_skin_and_wound_depth", "Drainage and Open Skin Detail", "string", "drainage-detail", "고름·진물·냄새·노란 딱지·출혈·벗겨진 피부나 상처가 있다면 양·색·깊이·주변 변화와 시작 시점을 알려주세요.", 102, "infection-detail", C + S),
        q("skin.edge_marking_dimension_change_and_spread_rate", "Spread Measurement and Rate", "string", "spread-measurement", "경계를 표시하거나 크기를 재었다면 날짜·시각별 크기와 몇 시간 또는 며칠 사이 얼마나 퍼졌는지 알려주세요.", 101, "infection-detail", C + S),
        q("skin.infection_near_eye_or_nose", "Inflamed Skin Near Eye or Nose", "boolean", "near-eye-nose", "뜨겁고 아프며 붓는 피부 변화가 눈이나 코 주변에 있나요?", 125, "infection-detail", S, safety_relevant=True),
        q("skin.rapid_breathing_heartbeat_dizziness_or_clammy", "Systemic Circulatory Warning Features", "boolean", "systemic-circulation", "피부 문제와 함께 숨이나 맥박이 매우 빨라지거나, 심한 어지럼·식은땀·차고 축축한 피부가 있나요?", 126, "infection-detail", S, safety_relevant=True),
        q("skin.previous_skin_diagnosis_biopsy_cancer_and_specialist_history", "Previous Skin Diagnosis and Procedure History", "string", "skin-history", "아토피·습진·건선·두드러기·감염·자가면역 피부질환·피부암 진단, 조직검사·절제와 피부과 진료 이력을 알려주세요.", 100, "history-detail", R),
        q("skin.atopy_allergy_autoimmune_immunosuppression_diabetes_vascular_context", "Relevant Medical Risk Context", "string", "medical-risk", "천식·비염·알레르기, 자가면역질환, 면역저하 치료, 당뇨·정맥·림프·혈액순환 문제의 진단과 현재 치료 상태를 알려주세요.", 99, "history-detail", R),
        q("skin.personal_uv_sunburn_tanning_and_family_skin_cancer_history", "UV and Family Skin Cancer Risk", "string", "uv-family-risk", "햇빛·인공 태닝 노출, 심한 화상 이력과 본인·가족의 흑색종 또는 피부암 종류, 관계와 진단 나이를 알려주세요.", 98, "lesion-detail", R),
        q("skin.pigmented_lesion_baseline_change_sensation_inflammation_and_bleeding", "Pigmented Lesion Evolution", "string", "pigmented-evolution", "점·색소 병변의 평소 모습과 비교해 크기·모양·색·감각·염증·딱지·진물·출혈이 언제 어떻게 변했는지 알려주세요.", 97, "lesion-detail", C + R),
        q("skin.pregnancy_postpartum_hormone_and_cycle_context", "Pregnancy and Hormone Context", "string", "pregnancy-context", "해당되는 경우 임신 주수·출산 후 기간, 수유·월경 변화와 피임약·호르몬 사용 시점 및 피부 변화의 관계를 알려주세요.", 96, "life-stage", R),
        q("skin.treatment_product_dose_frequency_dates_response_and_adverse_effect", "Treatment Attempt and Response", "string", "treatment-response", "사용한 연고·약·보습·세척·드레싱마다 이름·용량·횟수·사용일, 호전/악화 시점과 부작용을 알려주세요.", 95, "treatment-detail", C + R),
        q("skin.prior_exam_swab_biopsy_dermoscopy_pathology_date_result_and_source", "Prior Examination and Test Provenance", "string", "prior-tests", "이전 진찰·배양/도말·피부경·조직검사·병리 결과가 있다면 날짜, 설명받은 결과, 자료 출처와 아직 확인하지 못한 결과를 알려주세요.", 94, "treatment-detail", R),
        q("skin.sleep_work_school_clothing_hygiene_social_and_emotional_impact", "Detailed Functional and Psychosocial Impact", "string", "function-detail", "수면·업무/등교·운동·옷 입기·씻기·외출·대인관계와 불안·당혹감에 어떤 영향이 있는지 알려주세요.", 93, "function-detail", C + R),
        q("skin.child_age_feeding_activity_diaper_growth_and_proxy_observation", "Child and Proxy Skin Context", "string", "child-context", "소아라면 나이·수유/식사·활동·성장·기저귀 부위 변화와 보호자가 직접 본 내용, 아이가 표현한 증상을 구분해 알려주세요.", 92, "life-stage", C + R),
        q("skin.older_frailty_pressure_mobility_skin_care_and_caregiver_support", "Older Adult Skin and Care Context", "string", "older-context", "고령자라면 보행·압박 위험·실금·씻기·피부관리·인지 변화와 보호자 또는 돌봄 지원을 알려주세요.", 91, "life-stage", R),
        q("skin.communication_language_vision_cognition_literacy_and_accessibility", "Communication and Accessibility Needs", "string", "accessibility", "선호 언어, 통역·시각·인지·문해·디지털 사용과 사진 촬영·업로드에 필요한 도움 및 선호하는 응답 방법을 알려주세요.", 90, "handoff", R),
        q("skin.information_source_photo_record_reliability_conflict_and_proxy", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자 중 누가 답하는지, 사진·측정·약 목록·검사자료 유무와 기억이 불확실하거나 자료가 서로 다른 부분을 알려주세요.", 89, "handoff", R),
        q("skin.patient_goal_expected_help_and_additional_rfe", "Patient Goal and Additional RFE", "string", "goal", "진료에서 확인하고 싶은 내용, 원하는 도움과 질문에 없던 의견 또는 별도 문진이 필요한 다른 문제를 알려주세요.", 88, "handoff", C + R),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    for key, identifier in G.items():
        nodes[identifier] = {
            "id": identifier,
            "type": "ClinicalGroup",
            "display": key.replace("-", " ").title(),
        }
    doc["extra_nodes"] = list(nodes.values())
    new_rules = [
        {
            "id": "rule.skin.safety.blistering-new-medicine",
            "priority": 1000,
            "when": {"all": [
                {"fact": "symptom.skin_blistering_or_peeling", "equals": True},
                {"fact": "medication.new_recent", "equals": True},
            ]},
            "then": {"safety_level": "emergency", "action": "human_handoff", "suppress_routine": True},
        },
        {
            "id": "rule.skin.safety.mucosal-new-medicine",
            "priority": 1000,
            "when": {"all": [
                {"fact": "symptom.mucosal_sores", "equals": True},
                {"fact": "medication.new_recent", "equals": True},
            ]},
            "then": {"safety_level": "emergency", "action": "human_handoff", "suppress_routine": True},
        },
        {
            "id": "rule.skin.safety.systemic-circulation",
            "priority": 1000,
            "when": {"all": [
                {"fact": "symptom.systemically_unwell", "equals": True},
                {"fact": "skin.rapid_breathing_heartbeat_dizziness_or_clammy", "equals": True},
            ]},
            "then": {"safety_level": "emergency", "action": "human_handoff", "suppress_routine": True},
        },
        {
            "id": "rule.skin.safety.near-eye-hot-swollen",
            "priority": 900,
            "when": {"all": [
                {"fact": "symptom.skin_hot_painful_swollen", "equals": True},
                {"fact": "skin.infection_near_eye_or_nose", "equals": True},
            ]},
            "then": {"safety_level": "urgent", "action": "human_handoff", "suppress_routine": True},
        },
    ]
    rules = {item["id"]: item for item in doc["safety_rules"]}
    rules.update({item["id"]: item for item in new_rules})
    doc["safety_rules"] = list(rules.values())
    doc["default_refresh"].update({
        "last_assessed_at": "2026-07-20",
        "next_monitor_at": "2026-07-21",
        "next_full_review_at": "2027-01-16",
    })
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc: dict) -> dict:
    result = completion_policy(
        prefix=P,
        fragment=doc,
        presentation_fact="symptom.skin_complaint.current",
        question_budget=85,
        source_refs=SOURCES,
    )
    result["required_facts"]["routine"] = [
        "skin.primary_context", "symptom.duration",
        "symptom.skin_complaint.main_type", "symptom.skin_complaint.onset",
        "symptom.skin_complaint.location", "symptom.skin_complaint.distribution",
        "symptom.skin_complaint.appearance", "symptom.skin_complaint.itch",
        "symptom.skin_complaint.pain", "symptom.skin_complaint.functional_impact",
        "exposure.new_food_sting_product",
        "skin.patient_words_first_notice_and_main_concern",
        "skin.first_latest_timeline_course_recurrence_and_baseline",
        "skin.exact_site_side_extent_sequence_and_body_distribution",
        "skin.count_dimensions_shape_border_colour_surface_and_measurement",
        "skin.sleep_work_school_clothing_hygiene_social_and_emotional_impact",
        "skin.information_source_photo_record_reliability_conflict_and_proxy",
        "skin.patient_goal_expected_help_and_additional_rfe",
    ]
    result["conditional_required_facts"] = [{
        "selector_fact": "skin.primary_context",
        "cases": {
            "acute_widespread_or_rapid": [
                "skin.systemic_symptom_sequence_fever_chills_malaise_joint_and_nodes",
                "skin.mouth_eye_genital_and_other_mucosal_site_timeline",
                "skin.edge_marking_dimension_change_and_spread_rate",
                "skin.pus_odour_crust_drainage_open_skin_and_wound_depth",
            ],
            "local_inflammatory_or_wound": [
                "event.skin_break_bite_wound",
                "skin.infection_near_eye_or_nose",
                "skin.pus_odour_crust_drainage_open_skin_and_wound_depth",
                "skin.contact_travel_water_bite_wound_procedure_and_infection_timeline",
                "skin.edge_marking_dimension_change_and_spread_rate",
                "skin.treatment_product_dose_frequency_dates_response_and_adverse_effect",
            ],
            "medicine_or_allergic_timing": [
                "medication.new_recent", "exposure.new_food_sting_product",
                "skin.suspected_medicine_product_strength_route_indication_start_last_dose_and_interval",
                "skin.previous_same_medicine_class_reaction_and_allergy_record",
                "skin.topical_cosmetic_cleaner_adhesive_glove_and_supplement_exposure",
                "skin.mouth_eye_genital_and_other_mucosal_site_timeline",
            ],
            "recurrent_itch_or_rash": [
                "symptom.skin_complaint.recurrent", "exposure.close_contact_similar_rash",
                "skin.local_symptom_sequence_itch_pain_burning_tenderness_and_sensation",
                "skin.topical_cosmetic_cleaner_adhesive_glove_and_supplement_exposure",
                "skin.occupation_hobby_heat_sweat_sun_plant_animal_and_contact_exposure",
                "skin.previous_skin_diagnosis_biopsy_cancer_and_specialist_history",
            ],
            "pigmented_or_persistent_lesion": [
                "symptom.pigmented_lesion_change_size",
                "symptom.pigmented_lesion_irregular_shape",
                "symptom.pigmented_lesion_irregular_colour",
                "symptom.skin_lesion_diameter_7mm_or_more",
                "symptom.skin_lesion_oozing_bleeding_nonhealing",
                "skin.photo_date_scale_lighting_focus_source_and_change",
                "skin.pigmented_lesion_baseline_change_sensation_inflammation_and_bleeding",
                "skin.personal_uv_sunburn_tanning_and_family_skin_cancer_history",
                "skin.previous_skin_diagnosis_biopsy_cancer_and_specialist_history",
            ],
            "child_or_proxy": [
                "skin.child_age_feeding_activity_diaper_growth_and_proxy_observation",
                "skin.information_source_photo_record_reliability_conflict_and_proxy",
                "skin.communication_language_vision_cognition_literacy_and_accessibility",
            ],
            "followup_or_result_review": [
                "skin.photo_date_scale_lighting_focus_source_and_change",
                "skin.prior_exam_swab_biopsy_dermoscopy_pathology_date_result_and_source",
                "skin.treatment_product_dose_frequency_dates_response_and_adverse_effect",
                "skin.previous_skin_diagnosis_biopsy_cancer_and_specialist_history",
            ],
            "other_or_unclear": [
                "skin.skin_tone_visibility_and_patient_colour_description",
                "skin.local_symptom_sequence_itch_pain_burning_tenderness_and_sensation",
                "skin.atopy_allergy_autoimmune_immunosuppression_diabetes_vascular_context",
                "skin.pregnancy_postpartum_hormone_and_cycle_context",
                "skin.older_frailty_pressure_mobility_skin_care_and_caregiver_support",
                "skin.communication_language_vision_cognition_literacy_and_accessibility",
            ],
        },
    }]
    result["provenance"] = provenance(SOURCES)
    return result


def sources() -> dict:
    doc = load(RESEARCH)
    additions = [
        {
            "id": "source.nice.cg183.drug-allergy.2014",
            "kind": "clinical_guideline_metadata",
            "publisher": "NICE",
            "title": "Drug allergy: diagnosis and management",
            "version": "CG183-current-accessed-2026-07-20",
            "url": "https://www.nice.org.uk/guidance/cg183/chapter/recommendations",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "restricted", "complete": False,
            "monitor_profile": "nice_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-07-20", "next_monitor_at": "2026-07-27",
            "assertions": [
                "Suspected drug-reaction history preserves exact product, strength, formulation, indication, route, dose count or days, reaction date and time, and exposure-to-onset interval.",
                "Painful rash with fever, mucosal erosion, blistering or skin detachment is a severe-reaction warning pattern; Runtime records warning features without diagnosing drug allergy.",
            ],
        },
        {
            "id": "source.nice.ng141.cellulitis.2026",
            "kind": "clinical_guideline_metadata",
            "publisher": "NICE",
            "title": "Cellulitis and erysipelas: antimicrobial prescribing",
            "version": "NG141-current-accessed-2026-07-20",
            "url": "https://www.nice.org.uk/guidance/ng141/chapter/Recommendations",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "restricted", "complete": False,
            "monitor_profile": "nice_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-07-20", "next_monitor_at": "2026-07-27",
            "assertions": [
                "Extent and spread should be reproducibly documented, with awareness that redness can be less visible on darker skin tones.",
                "History includes wound or penetrating injury, water exposure, travel acquisition, previous antibiotics, eczema, oedema, diabetes or venous insufficiency and treatment response.",
                "Rapid worsening, disproportionate pain, severe systemic illness or hot swollen skin near the eye or nose requires time-sensitive clinician assessment.",
            ],
        },
        {
            "id": "source.nice.ng14.melanoma.2026",
            "kind": "clinical_guideline_metadata",
            "publisher": "NICE",
            "title": "Melanoma: assessment and management",
            "version": "NG14-current-accessed-2026-07-20",
            "url": "https://www.nice.org.uk/guidance/ng14/chapter/recommendations",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "restricted", "complete": False,
            "monitor_profile": "nice_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-07-20", "next_monitor_at": "2026-07-27",
            "assertions": [
                "Baseline photography and comparison over time can preserve change evidence for atypical lesions; professional dermoscopy and diagnosis remain outside Runtime.",
                "Prior melanoma, atypical mole syndrome and first-degree family history are relevant risk and follow-up context.",
            ],
        },
        {
            "id": "source.aad.rash-warning.2024",
            "kind": "professional_public_health_guidance_metadata",
            "publisher": "American Academy of Dermatology",
            "title": "Rash 101 in adults: When to seek medical treatment",
            "version": "updated-2024-01-22-accessed-2026-07-20",
            "url": "https://www.aad.org/public/everyday-care/itchy-skin/rash/rash-101",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "unknown", "complete": False,
            "monitor_profile": "public_health_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-07-20", "next_monitor_at": "2026-07-27",
            "assertions": [
                "Generalized, blistering, open or raw, febrile, rapidly spreading, painful or mucosa-involving rashes need medical assessment.",
                "Pus, crust, pain, swelling, warmth, odour, lymph-node swelling or fever are infection warning features; breathing or swallowing difficulty and eye or lip swelling need emergency assessment.",
            ],
        },
    ]
    artifacts = {item["id"]: item for item in doc["artifacts"]}
    artifacts.update({item["id"]: item for item in additions})
    doc["artifacts"] = list(artifacts.values())
    doc["updated_at"] = CREATED
    doc["provenance"] = provenance([item["id"] for item in doc["artifacts"]])
    return doc


def clinician(doc: dict) -> dict:
    result = load(CLINICIAN)
    ids = {item["fact"]["id"] for item in doc["entries"] if item["fact"]["id"].startswith("skin.")}
    ids.update({"pain.frequency", "pain.nrs_score"})
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.skin_complaint"] = sorted(ids)
    return result


def condition_state(condition: dict) -> dict[str, dict]:
    result: dict[str, dict] = {}
    if "fact" in condition:
        result[condition["fact"]] = {"value": condition.get("equals", True)}
    for child in condition.get("all", []):
        result.update(condition_state(child))
    return result


def routine_cases(doc: dict, completion: dict) -> dict[str, dict]:
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    always = completion["required_facts"]["always"]
    core = completion["required_facts"]["routine"]
    branches = completion["conditional_required_facts"][0]["cases"]
    forbidden = [
        "diagnosis.melanoma", "diagnosis.cellulitis",
        "diagnosis.stevens_johnson_syndrome", "recommendation.start_antibiotic",
    ]

    def value(fact_id: str):
        fact = by_id[fact_id]
        if fact["value_type"] == "boolean":
            return False
        if fact["value_type"] == "integer":
            return 5
        if fact["value_type"] == "quantity":
            return {"amount": 4, "unit": "days"}
        if fact["value_type"] == "coded":
            return fact.get("allowed_values", ["other_or_unclear"])[-1]
        return "특이사항 없음"

    def state(branch: str) -> dict:
        ids = dict.fromkeys([*always, *core, *branches[branch]])
        result = {fact_id: {"value": value(fact_id)} for fact_id in ids}
        result["symptom.skin_complaint.current"] = {"value": True}
        result["skin.primary_context"] = {"value": branch}
        result["symptom.skin_complaint.pain"] = {"value": "none"}
        result["symptom.skin_complaint.itch"] = {"value": "mild"}
        result["symptom.skin_complaint.main_type"] = {"value": "other"}
        return result

    specs = [
        ("ACUTE-WIDESPREAD-ROUTINE", "acute_widespread_or_rapid", 37, "빠르게 변한 피부 증상의 범위와 전신·점막 증상 순서를 정리합니다.", {}),
        ("LOCAL-WOUND-TREATMENT", "local_inflammatory_or_wound", 52, "상처 주변 피부 변화와 노출·치료 반응을 진료 전에 정리합니다.", {}),
        ("MEDICINE-TIMELINE", "medicine_or_allergic_timing", 45, "새 약과 피부 변화의 정확한 시간관계와 이전 반응을 정리합니다.", {}),
        ("RECURRENT-ITCH-OCCUPATION", "recurrent_itch_or_rash", 33, "반복 가려움과 제품·직업 노출, 기존 피부질환을 정리합니다.", {}),
        ("PIGMENTED-PHOTO-HISTORY", "pigmented_or_persistent_lesion", 61, "점의 크기·색 변화, 비교 사진과 가족력을 정리합니다.", {"symptom.skin_complaint.main_type": {"value": "mole_lump"}}),
        ("CHILD-PROXY", "child_or_proxy", 7, "보호자가 소아 피부 변화와 식사·활동을 직접 관찰한 내용으로 설명합니다.", {}),
        ("FOLLOWUP-RESULT-SOURCE", "followup_or_result_review", 69, "피부과 추적에서 이전 사진·조직검사 결과와 자료 출처를 정리합니다.", {}),
        ("OLDER-ACCESSIBILITY", "other_or_unclear", 86, "고령자의 피부관리·압박 위험과 시각·보호자 지원을 정리합니다.", {"skin.older_frailty_pressure_mobility_skin_care_and_caregiver_support": {"value": "피부관리에 보호자 도움이 필요함"}}),
        ("MULTI-RFE-ADDITIONAL-COMMENT", "other_or_unclear", 48, "피부 문제 외 다른 증상은 별도 RFE로 보존합니다.", {"skin.patient_goal_expected_help_and_additional_rfe": {"value": "관절통은 별도 문진 요청"}}),
        ("PAIN-NRS-REQUIRED", "local_inflammatory_or_wound", 42, "통증이 있는 피부 문제에서 통증 빈도와 NRS 원점수를 필수 기록합니다.", {"symptom.skin_complaint.pain": {"value": "moderate"}, "pain.frequency": {"value": "daily"}, "pain.nrs_score": {"value": 6}}),
        ("REMOTE-PHOTO-UNREADABLE", "pigmented_or_persistent_lesion", 56, "원격 사진이 불명확하면 음성으로 간주하지 않고 품질과 미확인을 전달합니다.", {}),
    ]
    result = {}
    for key, branch, age, statement, overrides in specs:
        hidden = state(branch)
        hidden.update(overrides)
        expected = {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 90,
            "forbidden_assertions": forbidden,
        }
        if key == "PAIN-NRS-REQUIRED":
            expected["expected_known_facts"] = {"pain.nrs_score": 6}
        case = {
            "id": f"SKIN-{key}", "simulation_language": "ko",
            "persona": {"age": age}, "initial_statement": {"ko": statement},
            "hidden_state": hidden, "expected": expected,
            "provenance": provenance(SOURCES),
        }
        if key == "CHILD-PROXY":
            case["encounter_context"] = {
                "care_setting": "primary_care", "encounter_type": "new_encounter",
                "interview_initiator": "caregiver", "interview_mode": "face_to_face",
                "available_information": ["caregiver_report"],
                "time_constraint": "routine", "clinical_responsibility": "decision_support",
            }
        result[f"SKIN-{key}.json"] = case

    missing = "skin.photo_date_scale_lighting_focus_source_and_change"
    absent = state("pigmented_or_persistent_lesion")
    absent.pop(missing)
    result["SKIN-PHOTO-DATA-ABSENT.json"] = {
        "id": "SKIN-PHOTO-DATA-ABSENT", "simulation_language": "ko",
        "persona": {"age": 58},
        "encounter_context": {
            "care_setting": "telemedicine", "encounter_type": "new_encounter",
            "interview_initiator": "patient", "interview_mode": "video",
            "available_information": ["image_unreadable"],
            "time_constraint": "self_paced", "clinical_responsibility": "decision_support",
        },
        "initial_statement": {"ko": "사진은 올렸지만 촬영 시점과 크기 기준을 확인할 수 없습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "asked-unknown"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 90, "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }

    new_rule_ids = {
        "BLISTER-NEW-MEDICINE": "rule.skin.safety.blistering-new-medicine",
        "MUCOSAL-NEW-MEDICINE": "rule.skin.safety.mucosal-new-medicine",
        "SYSTEMIC-CIRCULATION": "rule.skin.safety.systemic-circulation",
        "NEAR-EYE-HOT-SWOLLEN": "rule.skin.safety.near-eye-hot-swollen",
    }
    rules = {item["id"]: item for item in doc["safety_rules"]}
    for key, rule_id in new_rule_ids.items():
        rule = rules[rule_id]
        level = rule["then"]["safety_level"]
        result[f"SKIN-{key}.json"] = {
            "id": f"SKIN-{key}", "simulation_language": "ko",
            "persona": {"age": 44},
            "initial_statement": {"ko": "피부 변화와 함께 위험 신호가 있어 안전평가를 진행합니다."},
            "hidden_state": condition_state(rule["when"]),
            "expected": {
                "expected_safety_level": level,
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [rule_id],
                "expected_max_turns": 45,
                "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }
    return result


def main() -> None:
    seed_skin_complaint.main()
    doc = fragment()
    completion = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, completion)
    write_json(RESEARCH, sources())
    write_json(CLINICIAN, clinician(doc))
    for name, case in routine_cases(doc, completion).items():
        write_json(f"simulation/patients/dermatological/skin-complaint/{name}", case)


if __name__ == "__main__":
    main()
