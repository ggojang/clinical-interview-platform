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
    "source.nhs.hair-loss.2024",
    "source.bad.telogen-effluvium.2025",
    "source.bad.ccca.2024",
    "source.nhs-scotland.alopecia.2026",
    "source.nottsapc.tinea-capitis.2024",
    "source.nhs.staph-infections.2025",
    "source.stom.snomed-hair-scalp.20260807",
]
G = {key: f"group.skin.{key}" for key in (
    "routing", "course", "morphology-detail", "drug-detail",
    "infection-detail", "exposure-detail", "lesion-detail", "history-detail",
    "treatment-detail", "life-stage", "function-detail", "handoff",
    "hair-scalp-character", "hair-scalp-trigger", "hair-scalp-exposure",
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
        "followup_or_result_review", "hair_or_scalp_change", "other_or_unclear",
    ]
    additions = [
        q("skin.primary_context", "Primary Skin or Scalp Complaint Context", "coded", "primary-context", "가장 가까운 상황은 급성·빠르게 퍼지는 피부 변화, 국소 염증·상처, 약물·알레르기 시간관계, 반복 가려움·발진, 점·지속 병변, 탈모·두피 변화, 소아·보호자 응답, 추적·결과 확인, 또는 불분명 중 무엇인가요?", 117, "routing", C + R, allowed_values=contexts),
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
        q("hair.loss_pattern", "Hair Loss Pattern", "coded", "hair-loss-pattern", "머리카락 변화는 전체적으로 많이 빠짐, 서서히 숱이 줄어듦, 한두 군데 둥근 탈모, 헤어라인·묶는 부위의 끊김, 정수리 중심 변화, 그 밖의 형태 중 어디에 가깝나요?", 116, "hair-scalp-character", C, allowed_values=["diffuse_shedding", "gradual_thinning", "localized_patch", "hairline_or_breakage", "crown_centered", "other_or_unclear"], terminology_binding={"system": "http://snomed.info/sct", "code": "278040002", "display": "Loss of hair (finding)", "version": "http://snomed.info/sct/900000000000207008/version/20260801", "relation": "broader"}, mrcm_ref="mapping.snomed-mrcm.skin-complaint"),
        q("hair.onset", "Hair or Scalp Change Onset", "string", "hair-onset", "탈모나 두피 변화를 처음 알아차린 날짜 또는 얼마나 전인지 알려주세요.", 115, "hair-scalp-character", C),
        q("hair.course", "Hair or Scalp Change Course", "coded", "hair-course", "처음 알아차린 뒤 좋아짐, 비슷함, 서서히 악화, 빠르게 악화, 반복 중 어디에 가깝나요?", 114, "hair-scalp-character", C, allowed_values=["improving", "unchanged", "gradually_worsening", "rapidly_worsening", "recurrent", "unclear"]),
        q("hair.affected_site", "Hair or Scalp Affected Site", "string", "hair-site", "변화가 있는 두피의 정확한 부위와 범위를 알려주세요.", 113, "hair-scalp-character", C, terminology_binding={"system": "http://snomed.info/sct", "focus_code": "278040002", "attribute_code": "363698007", "site_code": "41695006", "version": "http://snomed.info/sct/900000000000207008/version/20260801"}, mrcm_ref="mapping.snomed-mrcm.skin-complaint"),
        q("hair.active_shedding", "Current Active Hair Shedding", "boolean", "hair-active-shedding", "지금도 평소보다 머리카락이 많이 빠지고 있나요?", 112, "hair-scalp-character", C),
        q("hair.broken_hairs", "Broken Hairs", "boolean", "hair-broken", "빠진 부위에 길이가 짧게 끊어진 머리카락이 보이나요?", 111, "hair-scalp-character", C),
        q("hair.non_scalp_hair_loss", "Non-scalp Hair Loss", "boolean", "hair-non-scalp", "눈썹·속눈썹·수염 또는 몸의 털도 함께 빠졌나요?", 110, "hair-scalp-character", C),
        q("hair.scalp_scaling", "Scalp Scaling", "boolean", "hair-scalp-scaling", "두피에 각질이나 비늘처럼 일어나는 부분이 있나요?", 109, "hair-scalp-character", C),
        q("hair.scalp_redness", "Scalp Redness or Colour Change", "boolean", "hair-scalp-redness", "두피에 평소와 다른 붉은색 또는 색 변화가 있나요?", 108, "hair-scalp-character", C),
        q("hair.scalp_itch", "Scalp Itch", "boolean", "hair-scalp-itch", "두피가 가렵나요?", 107, "hair-scalp-character", C),
        q("hair.scalp_pain_nrs", "Scalp Pain NRS", "integer", "hair-scalp-pain-nrs", "현재 두피 통증을 0점부터 10점까지 숫자로 답해 주세요. 0점은 통증 없음, 10점은 가장 심한 통증입니다.", 106, "hair-scalp-character", C, minimum=0, maximum=10),
        q("hair.scalp_burning", "Scalp Burning", "boolean", "hair-scalp-burning", "두피가 화끈거리거나 타는 듯한 느낌이 있나요?", 105, "hair-scalp-character", C),
        q("hair.scalp_tenderness", "Scalp Tenderness", "boolean", "hair-scalp-tenderness", "두피를 만지거나 눌렀을 때 아픈가요?", 104, "hair-scalp-character", C),
        q("hair.scalp_smooth_shiny_change", "Smooth Shiny Scalp Change", "boolean", "hair-scalp-shiny", "머리카락이 빠진 곳의 두피가 매끈하고 반짝이며 모공이 잘 보이지 않나요?", 103, "hair-scalp-character", C, terminology_binding={"system": "http://snomed.info/sct", "code": "400088006", "display": "Scarring alopecia (disorder)", "version": "http://snomed.info/sct/900000000000207008/version/20260801", "relation": "narrower"}, mrcm_ref="mapping.snomed-mrcm.skin-complaint"),
        q("hair.recent_fever", "Recent Fever before Hair Loss", "boolean", "hair-recent-fever", "탈모가 시작되기 약 2~4개월 전에 열이 난 적이 있나요?", 102, "hair-scalp-trigger", D),
        q("hair.recent_major_illness", "Recent Major Illness before Hair Loss", "boolean", "hair-recent-illness", "탈모가 시작되기 약 2~4개월 전에 크게 아팠던 적이 있나요?", 101, "hair-scalp-trigger", D),
        q("hair.recent_major_surgery", "Recent Major Surgery before Hair Loss", "boolean", "hair-recent-surgery", "탈모가 시작되기 약 2~4개월 전에 큰 수술을 받았나요?", 100, "hair-scalp-trigger", D),
        q("hair.recent_childbirth", "Recent Childbirth before Hair Loss", "string", "hair-childbirth", "해당되는 경우 최근 출산일과 탈모를 처음 알아차린 시점을 알려주세요.", 99, "hair-scalp-trigger", D),
        q("hair.recent_marked_weight_loss", "Recent Marked Weight Loss", "boolean", "hair-weight-loss", "탈모 전 몇 달 사이 체중이 눈에 띄게 줄었나요?", 98, "hair-scalp-trigger", D),
        q("hair.restrictive_diet", "Restrictive Diet", "boolean", "hair-restrictive-diet", "탈모 전 몇 달 동안 식사를 심하게 제한하거나 극단적인 식단을 했나요?", 97, "hair-scalp-trigger", D),
        q("hair.recent_major_stress", "Recent Major Stressor", "boolean", "hair-major-stress", "탈모 전 몇 달 사이 큰 정신적 스트레스나 충격적인 일이 있었나요?", 96, "hair-scalp-trigger", D),
        q("hair.recent_medication_change", "Recent Medication Change", "string", "hair-medication-change", "탈모 전 몇 달 사이 시작·중단·용량 변경한 약이나 호르몬제가 있다면 이름과 변경일을 알려주세요.", 95, "hair-scalp-trigger", D + R),
        q("hair.cancer_treatment", "Cancer Treatment Exposure", "string", "hair-cancer-treatment", "항암치료나 방사선치료를 받았다면 치료 종류와 가장 최근 치료일을 알려주세요.", 94, "hair-scalp-trigger", D + R),
        q("hair.iron_deficiency_history", "Iron Deficiency History", "boolean", "hair-iron-history", "철분 부족이나 철결핍빈혈을 진단받은 적이 있나요?", 93, "hair-scalp-trigger", R),
        q("hair.thyroid_condition_history", "Thyroid Condition History", "boolean", "hair-thyroid-history", "갑상선 질환을 진단받은 적이 있나요?", 92, "hair-scalp-trigger", R),
        q("hair.family_history", "Family History of Similar Hair Loss", "string", "hair-family-history", "가족 중 비슷한 형태의 탈모가 있다면 가족관계와 시작 나이를 알려주세요.", 91, "hair-scalp-trigger", R),
        q("hair.tight_hairstyle_exposure", "Tight Hairstyle Exposure", "boolean", "hair-tight-style", "머리를 강하게 당겨 묶거나 땋는 스타일을 자주 하나요?", 90, "hair-scalp-exposure", D),
        q("hair.heat_treatment_exposure", "Hair Heat Treatment Exposure", "boolean", "hair-heat-treatment", "고온 드라이어·고데기 같은 열처리를 자주 하나요?", 89, "hair-scalp-exposure", D),
        q("hair.chemical_treatment_exposure", "Hair Chemical Treatment Exposure", "boolean", "hair-chemical-treatment", "최근 염색·탈색·파마·화학적 스트레이트 시술을 했나요?", 88, "hair-scalp-exposure", D),
        q("hair.household_similar_scalp_symptoms", "Household Contact with Similar Scalp Symptoms", "boolean", "hair-household-contact", "함께 사는 사람에게 비슷한 두피 각질이나 탈모가 있나요?", 87, "hair-scalp-exposure", D),
        q("hair.pet_skin_or_fur_problem", "Pet Skin or Fur Problem", "boolean", "hair-pet-exposure", "접촉한 반려동물에게 털 빠짐이나 피부병이 있나요?", 86, "hair-scalp-exposure", D),
        q("hair.previous_evaluation", "Previous Hair Loss Evaluation", "string", "hair-previous-evaluation", "이 문제로 받은 진찰·혈액검사·두피검사나 설명받은 결과가 있다면 날짜와 자료 출처를 알려주세요.", 85, "treatment-detail", R),
        q("hair.previous_treatment_response", "Previous Hair Loss Treatment Response", "string", "hair-treatment-response", "사용한 탈모·두피 치료가 있다면 이름, 사용 기간과 호전·악화 여부를 알려주세요.", 84, "treatment-detail", R),
        q("hair.emotional_impact", "Hair Loss Emotional Impact", "coded", "hair-emotional-impact", "탈모나 두피 변화로 인한 걱정·당혹감은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 83, "function-detail", R, allowed_values=["none", "mild", "moderate", "severe"]),
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
        {
            "id": "rule.skin.safety.hot-painful-swollen",
            "priority": 899,
            "when": {"fact": "symptom.skin_hot_painful_swollen", "equals": True},
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
        "skin.patient_words_first_notice_and_main_concern",
        "symptom.skin_complaint.functional_impact",
        "skin.information_source_photo_record_reliability_conflict_and_proxy",
        "skin.patient_goal_expected_help_and_additional_rfe",
    ]
    standard_skin_characterization = [
        "symptom.skin_complaint.main_type", "symptom.skin_complaint.onset",
        "symptom.skin_complaint.location", "symptom.skin_complaint.distribution",
        "symptom.skin_complaint.appearance", "symptom.skin_complaint.itch",
        "symptom.skin_complaint.pain",
        "skin.first_latest_timeline_course_recurrence_and_baseline",
        "skin.exact_site_side_extent_sequence_and_body_distribution",
        "skin.count_dimensions_shape_border_colour_surface_and_measurement",
        "skin.sleep_work_school_clothing_hygiene_social_and_emotional_impact",
    ]
    result["conditional_required_facts"] = [{
        "selector_fact": "skin.primary_context",
        "cases": {
            "acute_widespread_or_rapid": [
                *standard_skin_characterization,
                "skin.systemic_symptom_sequence_fever_chills_malaise_joint_and_nodes",
                "skin.mouth_eye_genital_and_other_mucosal_site_timeline",
                "skin.edge_marking_dimension_change_and_spread_rate",
                "skin.pus_odour_crust_drainage_open_skin_and_wound_depth",
            ],
            "local_inflammatory_or_wound": [
                *standard_skin_characterization,
                "event.skin_break_bite_wound",
                "skin.infection_near_eye_or_nose",
                "skin.pus_odour_crust_drainage_open_skin_and_wound_depth",
                "skin.contact_travel_water_bite_wound_procedure_and_infection_timeline",
                "skin.edge_marking_dimension_change_and_spread_rate",
                "skin.treatment_product_dose_frequency_dates_response_and_adverse_effect",
            ],
            "medicine_or_allergic_timing": [
                *standard_skin_characterization,
                "medication.new_recent", "exposure.new_food_sting_product",
                "skin.suspected_medicine_product_strength_route_indication_start_last_dose_and_interval",
                "skin.previous_same_medicine_class_reaction_and_allergy_record",
                "skin.topical_cosmetic_cleaner_adhesive_glove_and_supplement_exposure",
                "skin.mouth_eye_genital_and_other_mucosal_site_timeline",
            ],
            "recurrent_itch_or_rash": [
                *standard_skin_characterization,
                "symptom.skin_complaint.recurrent", "exposure.close_contact_similar_rash",
                "skin.local_symptom_sequence_itch_pain_burning_tenderness_and_sensation",
                "skin.topical_cosmetic_cleaner_adhesive_glove_and_supplement_exposure",
                "skin.occupation_hobby_heat_sweat_sun_plant_animal_and_contact_exposure",
                "skin.previous_skin_diagnosis_biopsy_cancer_and_specialist_history",
            ],
            "pigmented_or_persistent_lesion": [
                *standard_skin_characterization,
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
                *standard_skin_characterization,
                "skin.child_age_feeding_activity_diaper_growth_and_proxy_observation",
                "skin.information_source_photo_record_reliability_conflict_and_proxy",
                "skin.communication_language_vision_cognition_literacy_and_accessibility",
            ],
            "followup_or_result_review": [
                *standard_skin_characterization,
                "skin.photo_date_scale_lighting_focus_source_and_change",
                "skin.prior_exam_swab_biopsy_dermoscopy_pathology_date_result_and_source",
                "skin.treatment_product_dose_frequency_dates_response_and_adverse_effect",
                "skin.previous_skin_diagnosis_biopsy_cancer_and_specialist_history",
            ],
            "hair_or_scalp_change": [
                "symptom.skin_complaint.main_type",
                "hair.loss_pattern", "hair.onset", "hair.course",
                "hair.affected_site", "hair.active_shedding",
                "hair.previous_evaluation", "hair.emotional_impact",
            ],
            "other_or_unclear": [
                *standard_skin_characterization,
                "skin.skin_tone_visibility_and_patient_colour_description",
                "skin.local_symptom_sequence_itch_pain_burning_tenderness_and_sensation",
                "skin.atopy_allergy_autoimmune_immunosuppression_diabetes_vascular_context",
                "skin.pregnancy_postpartum_hormone_and_cycle_context",
                "skin.older_frailty_pressure_mobility_skin_care_and_caregiver_support",
                "skin.communication_language_vision_cognition_literacy_and_accessibility",
            ],
        },
    }, {
        "selector_fact": "hair.loss_pattern",
        "cases": {
            "diffuse_shedding": [
                "hair.recent_fever", "hair.recent_major_illness",
                "hair.recent_major_surgery", "hair.recent_childbirth",
                "hair.recent_marked_weight_loss", "hair.restrictive_diet",
                "hair.recent_major_stress", "hair.recent_medication_change",
                "hair.cancer_treatment", "hair.iron_deficiency_history",
                "hair.thyroid_condition_history", "hair.previous_treatment_response",
            ],
            "gradual_thinning": [
                "hair.family_history", "hair.recent_medication_change",
                "hair.iron_deficiency_history", "hair.thyroid_condition_history",
                "hair.previous_treatment_response",
            ],
            "localized_patch": [
                "hair.broken_hairs", "hair.non_scalp_hair_loss",
                "hair.scalp_scaling", "hair.scalp_redness", "hair.scalp_itch",
                "hair.scalp_pain_nrs", "hair.scalp_burning",
                "hair.scalp_tenderness", "hair.scalp_smooth_shiny_change",
                "hair.household_similar_scalp_symptoms",
                "hair.pet_skin_or_fur_problem", "hair.previous_treatment_response",
            ],
            "hairline_or_breakage": [
                "hair.broken_hairs", "hair.scalp_pain_nrs",
                "hair.scalp_tenderness", "hair.tight_hairstyle_exposure",
                "hair.heat_treatment_exposure", "hair.chemical_treatment_exposure",
                "hair.previous_treatment_response",
            ],
            "crown_centered": [
                "hair.scalp_scaling", "hair.scalp_redness", "hair.scalp_itch",
                "hair.scalp_pain_nrs", "hair.scalp_burning",
                "hair.scalp_tenderness", "hair.scalp_smooth_shiny_change",
                "hair.family_history", "hair.tight_hairstyle_exposure",
                "hair.heat_treatment_exposure", "hair.chemical_treatment_exposure",
                "hair.previous_treatment_response",
            ],
            "other_or_unclear": [
                "hair.broken_hairs", "hair.non_scalp_hair_loss",
                "hair.scalp_scaling", "hair.scalp_redness", "hair.scalp_itch",
                "hair.scalp_pain_nrs", "hair.scalp_burning",
                "hair.scalp_tenderness", "hair.scalp_smooth_shiny_change",
                "hair.family_history", "hair.recent_medication_change",
                "hair.previous_treatment_response",
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
            "version": "CG183-published-2014-09-03-current-accessed-2026-08-07",
            "url": "https://www.nice.org.uk/guidance/cg183/chapter/recommendations",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "restricted", "complete": False,
            "monitor_profile": "nice_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-14",
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
            "version": "NG141-published-2019-09-27-current-accessed-2026-08-07",
            "url": "https://www.nice.org.uk/guidance/ng141/chapter/Recommendations",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "restricted", "complete": False,
            "monitor_profile": "nice_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-14",
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
            "version": "NG14-updated-2022-07-27-current-accessed-2026-08-07",
            "url": "https://www.nice.org.uk/guidance/ng14/chapter/recommendations",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "restricted", "complete": False,
            "monitor_profile": "nice_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-14",
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
            "version": "updated-2024-01-22-accessed-2026-08-07",
            "url": "https://www.aad.org/public/everyday-care/itchy-skin/rash/rash-101",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "unknown", "complete": False,
            "monitor_profile": "public_health_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-14",
            "assertions": [
                "Generalized, blistering, open or raw, febrile, rapidly spreading, painful or mucosa-involving rashes need medical assessment.",
                "Pus, crust, pain, swelling, warmth, odour, lymph-node swelling or fever are infection warning features; breathing or swallowing difficulty and eye or lip swelling need emergency assessment.",
            ],
        },
        {
            "id": "source.nhs.hair-loss.2024",
            "kind": "public_health_guidance_metadata",
            "publisher": "NHS",
            "title": "Hair loss",
            "version": "reviewed-2024-01-24-next-review-2027-01-24",
            "url": "https://www.nhs.uk/symptoms/hair-loss/",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "unknown", "complete": False,
            "monitor_profile": "public_health_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-14",
            "assertions": [
                "Hair-loss history should distinguish gradual or familial patterns from temporary shedding associated with illness, stress, cancer treatment, weight loss or iron deficiency.",
                "The effect on wellbeing and the person's concern are relevant to pre-visit handoff; the questionnaire does not diagnose the cause.",
            ],
        },
        {
            "id": "source.bad.telogen-effluvium.2025",
            "kind": "professional_patient_guidance_metadata",
            "publisher": "British Association of Dermatologists",
            "title": "Telogen effluvium",
            "version": "updated-2025-10-next-review-2028-10",
            "url": "https://www.bad.org.uk/pils/telogen-effluvium",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "unknown", "complete": False,
            "monitor_profile": "clinical_guideline", "monitor_interval_days": 1,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-08",
            "assertions": [
                "Sudden diffuse shedding often begins around three months after a trigger, so the interview preserves trigger-to-onset timing rather than assuming an immediate relationship.",
                "Relevant triggers include childbirth, severe illness or fever, major surgery or trauma, marked weight loss or restrictive diet, stress, scalp problems and medicine or hormone changes.",
                "Prior evaluation may include iron and thyroid context; testing and diagnosis remain clinician decisions.",
            ],
        },
        {
            "id": "source.bad.ccca.2024",
            "kind": "professional_patient_guidance_metadata",
            "publisher": "British Association of Dermatologists",
            "title": "Central centrifugal cicatricial alopecia",
            "version": "published-2024-05",
            "url": "https://www.bad.org.uk/pils/central-centrifugal-cicatricial-alopecia",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "unknown", "complete": False,
            "monitor_profile": "clinical_guideline", "monitor_interval_days": 1,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-08",
            "assertions": [
                "Crown-centred progression, itching, burning, tingling, soreness or tenderness, scalp colour or scale changes and smooth shiny loss of follicular openings are useful handoff features for possible scarring change.",
                "Hair practices involving tension, heat or chemical treatment are relevant exposures; the platform records them without assigning a diagnosis.",
            ],
        },
        {
            "id": "source.nhs-scotland.alopecia.2026",
            "kind": "clinical_pathway_metadata",
            "publisher": "NHS Scotland Right Decisions",
            "title": "Alopecia",
            "version": "next-review-2026-11-01",
            "url": "https://www.rightdecisions.scot.nhs.uk/dermatology-pathways/alopecia/",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "unknown", "complete": False,
            "monitor_profile": "clinical_guideline", "monitor_interval_days": 1,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-08",
            "assertions": [
                "Alopecia handoff distinguishes diffuse from localised, inflamed from non-inflamed and possible scarring from non-scarring change.",
                "Inflammatory scarring change, persistent or extensive loss and diagnostic uncertainty need clinician assessment; referral and tests are not automated by Runtime.",
            ],
        },
        {
            "id": "source.nottsapc.tinea-capitis.2024",
            "kind": "regional_antimicrobial_guidance_metadata",
            "publisher": "Nottinghamshire Area Prescribing Committee",
            "title": "Dermatophyte infection of the scalp",
            "version": "3.0-2024-07-next-review-2027-07",
            "url": "https://www.nottsapc.nhs.uk/media/bxdkmjvg/d-infection-of-the-scalp.pdf",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "unknown", "complete": False,
            "monitor_profile": "clinical_guideline", "monitor_interval_days": 1,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-08",
            "assertions": [
                "Scalp dermatophyte infection is particularly relevant in prepubertal children, and contact history may include household members and animals.",
                "Scaling, broken hairs and localised hair loss are useful handoff observations; confirmation and oral treatment are clinician responsibilities.",
            ],
        },
        {
            "id": "source.nhs.staph-infections.2025",
            "kind": "public_health_guidance_metadata",
            "publisher": "NHS",
            "title": "Staph infection",
            "version": "reviewed-2025-02-11-next-review-2028-02-11",
            "url": "https://www.nhs.uk/conditions/staphylococcal-infections/",
            "language": "en", "digest": "metadata_only_not_cached",
            "license_status": "unknown", "complete": False,
            "monitor_profile": "public_health_guidance", "monitor_interval_days": 7,
            "last_monitored_at": "2026-08-07", "next_monitor_at": "2026-08-14",
            "assertions": [
                "Hot, painful and swollen skin, rapidly spreading redness, sores, crusts, blisters or pus need time-sensitive clinical assessment, especially with immune compromise.",
                "The platform captures warning features and routes to a clinician without diagnosing or prescribing treatment.",
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
    hair_pattern_cases = completion["conditional_required_facts"][1]["cases"]
    forbidden = [
        "diagnosis.melanoma", "diagnosis.cellulitis",
        "diagnosis.stevens_johnson_syndrome", "recommendation.start_antibiotic",
        "diagnosis.alopecia_areata", "diagnosis.telogen_effluvium",
        "diagnosis.tinea_capitis", "diagnosis.scarring_alopecia",
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
        if branch == "hair_or_scalp_change":
            result["symptom.skin_complaint.main_type"] = {"value": "hair_or_scalp_change"}
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
        ("HAIR-DIFFUSE-POSTPARTUM", "hair_or_scalp_change", 32, "출산 몇 달 뒤부터 머리 전체에서 많이 빠지지만 원인을 단정하지 않고 시간관계를 정리합니다.", {"hair.loss_pattern": {"value": "diffuse_shedding"}, "hair.recent_childbirth": {"value": "출산 4개월 전"}, "hair.active_shedding": {"value": True}}),
        ("HAIR-CHILD-SCALY-PATCH", "hair_or_scalp_change", 8, "보호자가 아이의 둥근 탈모, 각질과 끊어진 머리카락을 관찰해 설명합니다.", {"hair.loss_pattern": {"value": "localized_patch"}, "hair.scalp_scaling": {"value": True}, "hair.broken_hairs": {"value": True}, "hair.household_similar_scalp_symptoms": {"value": True}}),
        ("HAIR-SCARRING-LIKE-HANDOFF", "hair_or_scalp_change", 47, "정수리 중심의 매끈하고 반짝이는 두피 변화와 화끈거림을 진단 없이 전달합니다.", {"hair.loss_pattern": {"value": "crown_centered"}, "hair.scalp_smooth_shiny_change": {"value": True}, "hair.scalp_burning": {"value": True}}),
        ("HAIR-REMOTE-UNCERTAIN", "hair_or_scalp_change", 68, "원격 문진에서 탈모 범위가 불분명한 경우 확인되지 않은 관찰을 음성으로 바꾸지 않습니다.", {"hair.loss_pattern": {"value": "other_or_unclear"}, "hair.affected_site": {"value": "정수리로 보이나 화면상 범위 불확실"}}),
    ]
    result = {}
    for key, branch, age, statement, overrides in specs:
        hidden = state(branch)
        hidden.update(overrides)
        if branch == "hair_or_scalp_change":
            pattern = hidden["hair.loss_pattern"]["value"]
            for fact_id in hair_pattern_cases[pattern]:
                hidden.setdefault(fact_id, {"value": value(fact_id)})
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
        if key in {"CHILD-PROXY", "HAIR-CHILD-SCALY-PATCH"}:
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

    missing_exposure = "exposure.new_food_sting_product"
    absent_exposure = state("medicine_or_allergic_timing")
    absent_exposure.pop(missing_exposure)
    result["SKIN-DATA-ABSENT-001.json"] = {
        "id": "SKIN-DATA-ABSENT-001", "simulation_language": "ko",
        "persona": {"age": 34, "communication_style": "declines_exposure_detail"},
        "initial_statement": {"ko": "새 제품 노출 내용은 답변하고 싶지 않습니다."},
        "hidden_state": absent_exposure,
        "response_behavior": {missing_exposure: {"dataAbsentReason": "asked-declined"}},
        "expected": {
            "expected_data_absent_reasons": {missing_exposure: "asked-declined"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 90, "forbidden_assertions": forbidden,
        },
        "provenance": provenance(["source.nice.cg183.drug-allergy.2014"]),
    }

    missing_hair = "hair.recent_medication_change"
    absent_hair = state("hair_or_scalp_change")
    for fact_id in hair_pattern_cases["other_or_unclear"]:
        absent_hair.setdefault(fact_id, {"value": value(fact_id)})
    absent_hair.pop(missing_hair)
    result["SKIN-HAIR-MEDICATION-DATA-ABSENT.json"] = {
        "id": "SKIN-HAIR-MEDICATION-DATA-ABSENT",
        "simulation_language": "ko", "persona": {"age": 73},
        "initial_statement": {"ko": "약이 여러 개라 최근 바뀐 약은 지금 확인할 수 없습니다."},
        "hidden_state": absent_hair,
        "response_behavior": {missing_hair: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {missing_hair: "asked-unknown"},
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
        "HOT-PAINFUL-SWOLLEN": "rule.skin.safety.hot-painful-swollen",
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
