#!/usr/bin/env python3
"""Materialize unreviewed grouped wound, burn and minor-injury knowledge."""
from profile_support import *

P = "wound-minor-injury"
RFE = "rfe.wound_minor_injury"
M = "mapping.snomed-mrcm.wound-minor-injury"
SN = "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = [
    "source.nhs.cuts-grazes.2026",
    "source.nhs.burns-scalds.2026",
    "source.nhs.acid-chemical-burns.2024",
    "source.nice.ng184.bites.2020",
    "source.nice.ng232.head-injury.2025",
    "source.nhs.sprains-strains.2024",
    "source.stom.wound-minor-injury.20260715",
]
G = {k: f"group.injury.{k}" for k in (
    "routing", "shared-safety", "common", "open-wound", "burn",
    "blunt-sprain", "bite-puncture", "head-injury",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
D = ["intent.differentiate_common_causes"]
R = ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("injury.primary_group", "Primary Wound or Minor Injury Group", "coded", "primary-group", "가장 불편한 문제는 베이거나 찢어진 상처, 화상, 부딪힘·삠, 물림·찔림, 머리 외상 중 무엇인가요?", 160, [G["routing"]], C, allowed_values=["open_wound", "burn", "blunt_sprain", "bite_puncture", "head_injury", "other_unclear"]),

        Q("injury.uncontrolled_heavy_bleeding", "Uncontrolled Heavy Bleeding", "boolean", "uncontrolled-bleeding", "깨끗한 천이나 거즈로 계속 세게 눌러도 피가 멎지 않나요?", 159, [G["shared-safety"], G["open-wound"]], S, safety_relevant=True),
        Q("injury.spurting_bright_red_bleeding", "Spurting Bright Red Bleeding", "boolean", "spurting-bleeding", "밝은 선홍색 피가 맥박에 맞춰 뿜어 나오나요?", 158, [G["shared-safety"], G["open-wound"]], S, safety_relevant=True),
        Q("injury.loss_of_sensation_or_movement", "Loss of Sensation or Movement after Injury", "boolean", "neurovascular-loss", "다친 부위 아래쪽의 감각이 없어졌거나 손가락·발가락 등을 움직이기 어렵나요?", 157, [G["shared-safety"]], S, safety_relevant=True),
        Q("injury.distal_cold_blue_pale", "Cold Blue or Pale Distal Limb", "boolean", "circulation-loss", "다친 부위 아래쪽이 반대편보다 차갑거나 창백·파랗게 변했나요?", 156, [G["shared-safety"]], S, safety_relevant=True),
        Q("injury.amputation_or_near_amputation", "Amputation or Near-amputation", "boolean", "amputation", "손가락·발가락이나 다른 신체 일부가 절단됐거나 거의 떨어져 있나요?", 155, [G["shared-safety"], G["open-wound"]], S, safety_relevant=True),
        Q("injury.open_fracture_or_gross_deformity", "Open Fracture or Gross Deformity", "boolean", "open-fracture-deformity", "뼈가 보이거나 다친 부위 모양이 심하게 변하고 비정상 방향으로 꺾였나요?", 154, [G["shared-safety"], G["blunt-sprain"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "125605004"}, mrcm_ref=M),
        Q("injury.large_deep_or_gaping_wound", "Large Deep or Gaping Wound", "boolean", "large-deep-wound", "상처가 매우 크거나 깊고 벌어져 있으며 지방·근육·뼈가 보이나요?", 153, [G["shared-safety"], G["open-wound"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "125643001"}, mrcm_ref=M),
        Q("injury.embedded_or_impaled_object", "Embedded or Impaled Object", "boolean", "embedded-object", "유리·금속·나무 조각이나 다른 물체가 상처 깊이 박혀 있나요?", 152, [G["shared-safety"], G["open-wound"], G["bite-puncture"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "211463006"}, mrcm_ref=M),
        Q("injury.severe_crush_or_high_energy_mechanism", "Severe Crush or High-energy Mechanism", "boolean", "high-energy", "차량 사고, 높은 곳에서 추락, 기계에 눌림 같은 큰 충격으로 다쳤나요?", 151, [G["shared-safety"]], S, safety_relevant=True),
        Q("injury.eye_or_eyelid_penetrating_or_chemical_injury", "Serious Eye or Eyelid Injury", "boolean", "eye-injury", "눈에 물체가 박혔거나 화학물질이 들어갔거나 갑자기 시력이 변했나요?", 150, [G["shared-safety"]], S, safety_relevant=True),
        Q("injury.burn_airway_or_smoke_exposure", "Burn with Airway or Smoke Exposure", "boolean", "burn-airway", "밀폐된 곳의 연기·불에 노출된 뒤 숨이 차거나 목소리가 변하고 얼굴·입안이 그을렸나요?", 149, [G["shared-safety"], G["burn"]], S, safety_relevant=True),
        Q("injury.chemical_or_electrical_burn", "Chemical or Electrical Burn", "boolean", "chemical-electrical-burn", "산·알칼리 같은 화학물질 또는 전기로 생긴 화상인가요?", 148, [G["shared-safety"], G["burn"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "284196006"}, mrcm_ref=M),
        Q("injury.very_large_deep_or_circumferential_burn", "Very Large Deep or Circumferential Burn", "boolean", "major-burn", "화상이 매우 넓거나 깊어 피부가 희거나 검게 변했거나 팔·다리·몸통을 빙 둘러싸나요?", 147, [G["shared-safety"], G["burn"]], S, safety_relevant=True),
        Q("injury.burn_face_hands_genitals_or_major_joint", "Burn at High-risk Site", "boolean", "high-risk-burn-site", "화상이 얼굴, 손, 발, 생식기·회음부 또는 큰 관절 위에 있나요?", 146, [G["shared-safety"], G["burn"]], S, safety_relevant=True),
        Q("injury.head_loss_consciousness_or_confusion", "Head Injury with Loss of Consciousness or Confusion", "boolean", "head-consciousness", "머리를 다친 뒤 의식을 잃었거나 지금 혼란스럽고 평소와 다르게 처지나요?", 145, [G["shared-safety"], G["head-injury"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "82271004"}, mrcm_ref=M),
        Q("injury.head_seizure_or_focal_neurology", "Head Injury with Seizure or Focal Neurology", "boolean", "head-neurology", "머리를 다친 뒤 경련, 한쪽 힘 빠짐·감각 저하, 말 어눌함이 생겼나요?", 144, [G["shared-safety"], G["head-injury"]], S, safety_relevant=True),
        Q("injury.head_repeated_vomiting_or_worsening_headache", "Head Injury with Repeated Vomiting or Worsening Headache", "boolean", "head-vomiting-headache", "머리를 다친 뒤 반복해서 토하거나 두통이 계속 심해지나요?", 143, [G["shared-safety"], G["head-injury"]], S, safety_relevant=True),
        Q("injury.head_anticoagulant_or_bleeding_disorder", "Head Injury with Anticoagulant or Bleeding Risk", "boolean", "head-bleeding-risk", "머리를 다쳤고 항응고제·항혈소판제(아스피린 단독 제외)를 복용하거나 출혈 질환이 있나요?", 142, [G["shared-safety"], G["head-injury"]], S, safety_relevant=True),
        Q("injury.severe_infection_or_systemic_illness", "Severe Wound Infection or Systemic Illness", "boolean", "severe-infection", "상처 주변 붉은 기운이 빠르게 퍼지거나 고열·심한 오한·혼란·심한 처짐이 있나요?", 141, [G["shared-safety"], G["open-wound"], G["bite-puncture"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "76844004"}, mrcm_ref=M),
        Q("injury.severe_pain_out_of_proportion", "Severe Pain Out of Proportion", "boolean", "pain-out-of-proportion", "겉으로 보이는 상처보다 통증이 훨씬 심하거나 빠르게 악화하나요?", 140, [G["shared-safety"]], S, safety_relevant=True),
        Q("injury.bite_deep_structure_or_dangerous_animal", "High-risk Bite or Deep Penetration", "boolean", "high-risk-bite", "사람·야생동물·떠돌이 동물에게 물렸거나 관절·힘줄·뼈 가까이 깊게 뚫렸나요?", 139, [G["shared-safety"], G["bite-puncture"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "399907009"}, mrcm_ref=M),
        Q("injury.safeguarding_or_non_accidental_concern", "Safeguarding or Non-accidental Injury Concern", "boolean", "safeguarding", "누군가에게 다쳤거나 설명하기 어려운 반복 손상 등 현재 안전이 걱정되는 상황인가요?", 138, [G["shared-safety"]], S, safety_relevant=True),

        Q("injury.time_since_event", "Time Since Injury", "string", "time", "언제 다쳤나요? 날짜와 대략적인 시간을 알려주세요.", 130, [G["common"]], C),
        Q("injury.mechanism", "Injury Mechanism", "string", "mechanism", "무엇에 의해 어떤 방식으로 다쳤나요?", 129, [G["common"]], C),
        Q("injury.body_site_and_laterality", "Body Site and Laterality", "string", "site-laterality", "다친 신체 부위와 왼쪽·오른쪽·양쪽 여부를 알려주세요.", 128, [G["common"]], C),
        Q("injury.number_of_sites", "Number of Injured Sites", "string", "site-count", "다친 곳이 한 군데인가요, 여러 군데인가요?", 127, [G["common"]], C),
        Q("injury.pain_zero_to_ten", "Injury Pain Score", "integer", "pain-score", "현재 통증을 0점부터 10점까지로 표현하면 몇 점인가요?", 126, [G["common"]], C),
        Q("injury.swelling_bruising_and_progression", "Swelling Bruising and Progression", "string", "swelling-bruising", "부기·멍이 있고 좋아지는지, 그대로인지, 커지는지 알려주세요.", 125, [G["common"]], C, terminology_binding={"system": SN, "code": "125667009"}, mrcm_ref=M),
        Q("injury.function_weight_bearing_or_use", "Functional Impact after Injury", "string", "function", "다친 부위를 움직이거나 사용하거나 체중을 실을 수 있나요?", 124, [G["common"]], R),
        Q("injury.first_aid_or_treatment_already_done", "First Aid or Treatment Already Done", "string", "first-aid", "세척·압박·냉각·붕대·약 복용 등 이미 한 처치와 그 반응을 알려주세요.", 118, [G["common"]], R),
        Q("injury.tetanus_immunization_status", "Tetanus Immunization Status", "string", "tetanus", "파상풍 예방접종을 받았는지, 마지막 접종 시기를 기억하나요?", 117, [G["common"], G["open-wound"], G["bite-puncture"]], R),
        Q("injury.diabetes_immunosuppression_or_poor_circulation", "Wound Healing Risk Context", "string", "healing-risk", "당뇨, 면역저하·항암치료, 혈액순환 문제 또는 상처 회복에 영향을 줄 질환이 있나요?", 116, [G["common"]], R),
        Q("injury.medicines_allergies_and_bleeding_risk", "Medicines Allergies and Bleeding Risk", "string", "medicines-allergies", "복용약, 약물 알레르기, 항응고제·항혈소판제 또는 출혈 질환을 알려주세요.", 115, [G["common"]], R),
        Q("injury.other_detail_or_patient_priority", "Other Injury Detail or Patient Priority", "string", "other-detail", "질문에 없지만 꼭 전달하고 싶은 내용이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("injury.wound_type", "Open Wound Type", "coded", "wound-type", "상처는 베임·찢어짐, 긁힘, 피부 벗겨짐, 찔림, 눌려 터짐 중 무엇에 가깝나요?", 123, [G["open-wound"]], C, allowed_values=["cut_laceration", "abrasion", "skin_tear", "puncture", "crush_open_wound", "other_unclear"]),
        Q("injury.wound_length_depth_and_gaping", "Wound Size Depth and Gaping", "string", "wound-size", "상처의 대략적인 길이·깊이와 벌어진 정도를 알려주세요.", 122, [G["open-wound"]], C),
        Q("injury.wound_contamination", "Wound Contamination", "string", "contamination", "흙·녹·유리·나무·체액 등 무엇이 묻었고 씻은 뒤에도 남아 있나요?", 121, [G["open-wound"]], R),
        Q("injury.wound_bleeding_current", "Current Wound Bleeding", "coded", "bleeding-detail", "현재 출혈은 멎음, 조금 배어 나옴, 압박하면 멎음, 계속 많이 남 중 어느 정도인가요?", 120, [G["open-wound"]], C, allowed_values=["stopped", "oozing", "stops_with_pressure", "heavy_persistent", "unclear"]),
        Q("injury.wound_infection_features", "Wound Infection Features", "string", "infection-features", "붉어짐·열감·통증이 증가하거나 고름·나쁜 냄새·붉은 줄이 생겼나요?", 119, [G["open-wound"]], R),
        Q("injury.wound_face_palm_joint_or_cosmetic_site", "Wound at Functionally Important Site", "boolean", "important-site", "상처가 얼굴, 손바닥, 관절 위 또는 기능·흉터가 특히 걱정되는 부위인가요?", 110, [G["open-wound"]], R),

        Q("injury.burn_cause", "Burn Cause", "coded", "burn-cause", "화상 원인은 뜨거운 물·증기, 불·뜨거운 물체, 화학물질, 전기, 마찰 중 무엇인가요?", 123, [G["burn"]], C, allowed_values=["scald", "flame_contact", "chemical", "electrical", "friction", "other_unclear"]),
        Q("injury.burn_extent", "Burn Extent", "string", "burn-extent", "화상 범위를 본인의 손바닥 크기와 비교하면 어느 정도인가요?", 122, [G["burn"]], C),
        Q("injury.burn_skin_appearance_and_blisters", "Burn Appearance and Blisters", "coded", "burn-appearance", "피부는 붉음, 물집, 희거나 얼룩짐, 검게 탐 중 어느 모습인가요?", 121, [G["burn"]], C, allowed_values=["red_only", "blistered", "white_mottled", "charred_black", "mixed_or_unclear"]),
        Q("injury.burn_cooling_duration", "Burn Cooling Duration", "string", "burn-cooling", "흐르는 시원한 물로 식혔다면 언제부터 몇 분간 했나요?", 120, [G["burn"]], R),
        Q("injury.burn_clothing_jewellery_or_adherent_material", "Burn Clothing or Jewellery Context", "string", "burn-material", "화상 부위에 붙은 옷이나 조이는 장신구가 있나요?", 119, [G["burn"]], R),

        Q("injury.blunt_injury_type", "Blunt or Musculoskeletal Injury Type", "coded", "blunt-type", "주된 문제는 멍·타박, 관절 삠, 근육 늘어남, 골절 의심 중 무엇인가요?", 123, [G["blunt-sprain"]], C, allowed_values=["contusion", "sprain", "strain", "possible_fracture", "other_unclear"]),
        Q("injury.crack_or_pop_at_injury", "Crack or Pop at Injury", "boolean", "crack-pop", "다칠 때 뚝·딱 하는 소리를 들었나요?", 122, [G["blunt-sprain"]], R),
        Q("injury.range_of_motion", "Range of Motion after Injury", "coded", "range-motion", "움직임은 정상, 조금 제한, 많이 제한, 전혀 못 움직임 중 어느 정도인가요?", 121, [G["blunt-sprain"]], C, allowed_values=["normal", "mildly_limited", "markedly_limited", "unable", "unclear"]),
        Q("injury.immediate_or_delayed_swelling", "Immediate or Delayed Swelling", "coded", "swelling-timing", "부기는 즉시, 몇 시간 뒤, 다음 날 이후 중 언제 생겼나요?", 120, [G["blunt-sprain"]], D, allowed_values=["immediate", "within_hours", "next_day_or_later", "none", "unclear"]),
        Q("injury.prior_injury_surgery_or_instability", "Prior Injury Surgery or Instability", "string", "prior-injury", "같은 부위의 과거 손상·수술·반복 빠짐 또는 불안정함이 있나요?", 110, [G["blunt-sprain"]], R),

        Q("injury.bite_source", "Bite or Puncture Source", "coded", "bite-source", "사람, 개, 고양이, 야생·떠돌이 동물, 못·바늘·가시 등 무엇에 물리거나 찔렸나요?", 123, [G["bite-puncture"]], C, allowed_values=["human", "dog", "cat", "wild_stray_animal", "sharp_object", "other_unclear"]),
        Q("injury.bite_skin_broken_and_blood_drawn", "Bite Skin Break and Bleeding", "coded", "bite-depth", "피부가 안 뚫림, 뚫렸지만 피 안 남, 피가 남, 깊게 뚫림 중 무엇인가요?", 122, [G["bite-puncture"]], C, allowed_values=["not_broken", "broken_no_blood", "blood_drawn", "deep_penetration", "unclear"]),
        Q("injury.bite_animal_ownership_and_vaccination", "Animal Ownership and Vaccination Context", "string", "animal-context", "동물의 종류, 주인이 있는지, 예방접종 상태와 현재 관찰 가능 여부를 알려주세요.", 121, [G["bite-puncture"]], R),
        Q("injury.bite_location_high_risk_area", "Bite at High-risk Area", "string", "bite-location", "물린 곳이 손·발·얼굴·생식기·관절 위 또는 혈액순환이 나쁜 부위인가요?", 120, [G["bite-puncture"]], R),
        Q("injury.bite_infection_progression", "Bite Infection Progression", "string", "bite-infection", "붉어짐·부기·열감·통증·분비물이 생기거나 빠르게 심해지나요?", 119, [G["bite-puncture"]], R),

        Q("injury.head_mechanism_and_height", "Head Injury Mechanism and Height", "string", "head-mechanism", "머리를 어떻게 다쳤고, 추락했다면 대략 어느 높이였나요?", 123, [G["head-injury"]], C),
        Q("injury.head_amnesia", "Head Injury Amnesia", "boolean", "head-amnesia", "사고 전후 일이 기억나지 않는 구간이 있나요?", 122, [G["head-injury"]], R),
        Q("injury.head_vomiting_count", "Vomiting Count after Head Injury", "integer", "head-vomiting-count", "머리를 다친 뒤 몇 번 토했나요?", 121, [G["head-injury"]], R),
        Q("injury.head_headache_course", "Headache Course after Head Injury", "coded", "headache-course", "두통은 없음, 좋아짐, 그대로, 악화 중 무엇인가요?", 120, [G["head-injury"]], C, allowed_values=["none", "improving", "same", "worsening", "unclear"]),
        Q("injury.head_observer_available", "Competent Observer Available after Head Injury", "boolean", "head-observer", "귀가한다면 상태 변화를 살필 수 있는 성인이 함께 있나요?", 110, [G["head-injury"]], R),
    ]
    rules = [
        safety_rule(P, "uncontrolled-bleeding", {"fact": "injury.uncontrolled_heavy_bleeding", "equals": True}, "emergency", 1000),
        safety_rule(P, "spurting-bleeding", {"fact": "injury.spurting_bright_red_bleeding", "equals": True}, "emergency", 1000),
        safety_rule(P, "neurovascular-loss", {"fact": "injury.loss_of_sensation_or_movement", "equals": True}, "emergency", 1000),
        safety_rule(P, "circulation-loss", {"fact": "injury.distal_cold_blue_pale", "equals": True}, "emergency", 1000),
        safety_rule(P, "amputation", {"fact": "injury.amputation_or_near_amputation", "equals": True}, "emergency", 1000),
        safety_rule(P, "open-fracture-deformity", {"fact": "injury.open_fracture_or_gross_deformity", "equals": True}, "emergency", 1000),
        safety_rule(P, "large-deep-wound", {"fact": "injury.large_deep_or_gaping_wound", "equals": True}, "emergency", 990),
        safety_rule(P, "embedded-object", {"fact": "injury.embedded_or_impaled_object", "equals": True}, "emergency", 990),
        safety_rule(P, "high-energy", {"fact": "injury.severe_crush_or_high_energy_mechanism", "equals": True}, "emergency", 1000),
        safety_rule(P, "eye-injury", {"fact": "injury.eye_or_eyelid_penetrating_or_chemical_injury", "equals": True}, "emergency", 1000),
        safety_rule(P, "burn-airway", {"fact": "injury.burn_airway_or_smoke_exposure", "equals": True}, "emergency", 1000),
        safety_rule(P, "chemical-electrical-burn", {"fact": "injury.chemical_or_electrical_burn", "equals": True}, "emergency", 1000),
        safety_rule(P, "major-burn", {"fact": "injury.very_large_deep_or_circumferential_burn", "equals": True}, "emergency", 1000),
        safety_rule(P, "high-risk-burn-site", {"fact": "injury.burn_face_hands_genitals_or_major_joint", "equals": True}, "urgent", 960),
        safety_rule(P, "head-consciousness", {"fact": "injury.head_loss_consciousness_or_confusion", "equals": True}, "emergency", 1000),
        safety_rule(P, "head-neurology", {"fact": "injury.head_seizure_or_focal_neurology", "equals": True}, "emergency", 1000),
        safety_rule(P, "head-vomiting-headache", {"fact": "injury.head_repeated_vomiting_or_worsening_headache", "equals": True}, "urgent", 980),
        safety_rule(P, "head-bleeding-risk", {"fact": "injury.head_anticoagulant_or_bleeding_disorder", "equals": True}, "urgent", 980),
        safety_rule(P, "severe-infection", {"fact": "injury.severe_infection_or_systemic_illness", "equals": True}, "emergency", 1000),
        safety_rule(P, "pain-out-of-proportion", {"fact": "injury.severe_pain_out_of_proportion", "equals": True}, "urgent", 970),
        safety_rule(P, "high-risk-bite", {"fact": "injury.bite_deep_structure_or_dangerous_animal", "equals": True}, "urgent", 970),
        safety_rule(P, "safeguarding", {"fact": "injury.safeguarding_or_non_accidental_concern", "equals": True}, "urgent", 990),
    ]
    return {
        "id": "knowledge.generated.wound-minor-injury", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-wound-minor-injury-research",
        "default_refresh": default_refresh(),
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": e,
        "provenance": provenance(SOURCES),
    }


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="injury.primary_group", question_budget=58, source_refs=SOURCES)
    branches = {
        "open_wound": ["injury.wound_type", "injury.wound_length_depth_and_gaping", "injury.wound_contamination", "injury.wound_bleeding_current", "injury.wound_infection_features", "injury.wound_face_palm_joint_or_cosmetic_site"],
        "burn": ["injury.burn_cause", "injury.burn_extent", "injury.burn_skin_appearance_and_blisters", "injury.burn_cooling_duration", "injury.burn_clothing_jewellery_or_adherent_material"],
        "blunt_sprain": ["injury.blunt_injury_type", "injury.crack_or_pop_at_injury", "injury.range_of_motion", "injury.immediate_or_delayed_swelling", "injury.prior_injury_surgery_or_instability"],
        "bite_puncture": ["injury.bite_source", "injury.bite_skin_broken_and_blood_drawn", "injury.bite_animal_ownership_and_vaccination", "injury.bite_location_high_risk_area", "injury.bite_infection_progression"],
        "head_injury": ["injury.head_mechanism_and_height", "injury.head_amnesia", "injury.head_vomiting_count", "injury.head_headache_course", "injury.head_observer_available"],
        "other_unclear": ["injury.other_detail_or_patient_priority"],
    }
    policy["required_facts"]["routine"] = [
        "injury.time_since_event", "injury.mechanism", "injury.body_site_and_laterality",
        "injury.pain_zero_to_ten", "injury.function_weight_bearing_or_use",
        "injury.first_aid_or_treatment_already_done", "injury.tetanus_immunization_status",
        "injury.diabetes_immunosuppression_or_poor_circulation",
        "injury.medicines_allergies_and_bleeding_risk", "injury.other_detail_or_patient_priority",
    ]
    policy["conditional_required_facts"] = [{"selector_fact": "injury.primary_group", "cases": branches}]
    return policy


def source_docs():
    defs = [
        ("source.nhs.cuts-grazes.2026", "NHS", "Cuts and grazes", "accessed-2026-07-15", "https://www.nhs.uk/conditions/cuts-and-grazes/", "public_health_guidance", 7, ["Uncontrolled or spurting bleeding, loss of sensation or movement, very large or deep wounds, and embedded objects require emergency assessment.", "Contamination, infection features, large wounds, bites and systemic illness support urgent assessment without establishing a diagnosis."]),
        ("source.nhs.burns-scalds.2026", "NHS", "Burns and scalds", "reviewed-2026-03-31", "https://www.nhs.uk/conditions/burns-and-scalds/", "public_health_guidance", 7, ["Very large or deep burns, burns of the face or genitals, chemical burns and electrical burns require emergency assessment.", "Cause, site, extent, appearance, cooling and adherent material are interview targets."]),
        ("source.nhs.acid-chemical-burns.2024", "NHS", "Acid and chemical burns", "reviewed-2024-06-05", "https://www.nhs.uk/conditions/acid-and-chemical-burns/", "public_health_guidance", 7, ["Acid or chemical exposure to skin or eyes requires immediate first aid and hospital assessment."]),
        ("source.nice.ng184.bites.2020", "NICE", "Human and animal bites: antimicrobial prescribing", "NG184; accessed-2026-07-15", "https://www.nice.org.uk/guidance/ng184/chapter/Recommendations", "nice_guidance", 7, ["Bite assessment includes source, site, depth, infection, tetanus, rabies and bloodborne-virus risk.", "Serious illness or penetration of arteries, joints, nerves, muscle, tendon, bone or CNS warrants hospital referral."]),
        ("source.nice.ng232.head-injury.2025", "NICE", "Head injury: assessment and early management", "NG232; updated-2025-03", "https://www.nice.org.uk/guidance/ng232/chapter/recommendations", "nice_guidance", 7, ["Community referral risk factors include loss of consciousness, focal neurological deficit, amnesia, persistent headache, vomiting, seizure, high-energy injury and anticoagulant or antiplatelet treatment.", "The package screens these risks but does not assign GCS or imaging decisions."]),
        ("source.nhs.sprains-strains.2024", "NHS", "Sprains and strains", "reviewed-2024-04-23", "https://www.nhs.uk/conditions/sprains-and-strains/", "public_health_guidance", 7, ["Crack, deformity, numbness, tingling, coldness or blue-grey colour may indicate a fracture or neurovascular problem requiring emergency assessment."]),
        ("source.stom.wound-minor-injury.20260715", "Infoclinic", "STOM wound and minor-injury terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", 30, ["STOM returned active disorder candidates for open wound, burn of skin, abrasion, puncture wound, animal bite wound, head injury, contusion, fracture, wound infection and foreign body in skin wound.", "Finding site and Severity were allowed MRCM attributes for each selected focus concept; MRCM does not control clinical urgency."]),
    ]
    artifacts = []
    for identifier, publisher, title, version, url, profile, days, assertions in defs:
        artifacts.append({
            "id": identifier, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata",
            "publisher": publisher, "title": title, "version": version, "url": url,
            "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached",
            "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown",
            "complete": False, "monitor_profile": profile, "monitor_interval_days": days,
            "last_monitored_at": "2026-07-15", "next_monitor_at": "2026-08-14" if days == 30 else "2026-07-22",
            "monitor_result": "current_official_source_confirmed", "assertions": assertions,
        })
    research = {"id": "source-manifest.primary-care-wound-minor-injury-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([item[0] for item in defs])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.wound-minor-injury", "generated_clinical_knowledge", "knowledge/generated/injury/wound-minor-injury/wound-minor-injury.json", True),
        ("source.mapping.wound-minor-injury", "terminology_mapping", "mappings/terminology/snomed-mrcm-wound-minor-injury.json", False),
        ("source.external.wound-minor-injury", "external_source_manifest", "sources/manifests/primary-care-wound-minor-injury-research.json", False),
        ("source.policy.wound-minor-injury", "runtime_policy", "policies/primary-care-wound-minor-injury-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-wound-minor-injury", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}

    def satisfy(condition, hidden):
        if "all" in condition:
            for child in condition["all"]:
                satisfy(child, hidden)
        elif "equals" in condition:
            hidden[condition["fact"]] = {"value": condition["equals"]}
        elif "in" in condition:
            hidden[condition["fact"]] = {"value": condition["in"][0]}

    for index, rule in enumerate(f["safety_rules"]):
        hidden = {}
        satisfy(rule["when"], hidden)
        key = rule["id"].split("safety.")[1]
        level = rule["then"]["safety_level"]
        out[f"INJURY-{key.upper()}.json"] = {
            "id": f"INJURY-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 20 + index}, "initial_statement": {"ko": "다쳐서 상처가 생겼어요."},
            "hidden_state": hidden,
            "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 48, "forbidden_assertions": ["diagnosis.fracture", "diagnosis.wound_infection", "recommendation.prescribe_antibiotic"]},
            "provenance": provenance(SOURCES),
        }

    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["open_wound"])
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}
    hidden = {}
    for fact_id in required:
        fact_def = by_id[fact_id]
        if fact_def["value_type"] == "boolean":
            hidden[fact_id] = {"value": False}
        elif fact_def["value_type"] == "coded":
            hidden[fact_id] = {"value": fact_def.get("allowed_values", ["unclear"])[-1]}
        elif fact_def["value_type"] == "integer":
            hidden[fact_id] = {"value": 2}
        else:
            hidden[fact_id] = {"value": "없음"}
    hidden["injury.primary_group"] = {"value": "open_wound"}
    hidden["injury.wound_type"] = {"value": "abrasion"}
    declined = "injury.tetanus_immunization_status"
    hidden.pop(declined)
    out["INJURY-WOUND-DATA-ABSENT.json"] = {
        "id": "INJURY-WOUND-DATA-ABSENT", "simulation_language": "ko",
        "persona": {"age": 34}, "initial_statement": {"ko": "넘어져서 무릎이 조금 까졌어요."},
        "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}},
        "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 65, "forbidden_assertions": ["diagnosis.fracture", "diagnosis.wound_infection"]},
        "provenance": provenance(["source.nhs.cuts-grazes.2026", "specifications/clinical-memory.md"]),
    }
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Wound, Burn and Minor Injury", intents=[
        ("intent.characterize_symptom", "Characterize Injury"),
        ("intent.screen_red_flags", "Screen Red Flags"),
        ("intent.differentiate_common_causes", "Differentiate Injury Pattern"),
        ("intent.risk_assessment", "Risk Assessment"),
    ])
    primary, research = source_docs()
    concepts = [
        ("125643001", "Open wound (disorder)", 22),
        ("284196006", "Burn of skin (disorder)", 22),
        ("399963005", "Abrasion (disorder)", 22),
        ("312609001", "Puncture wound - injury (disorder)", 22),
        ("399907009", "Animal bite wound (disorder)", 22),
        ("82271004", "Injury of head (disorder)", 22),
        ("125667009", "Contusion (disorder)", 22),
        ("125605004", "Fracture of bone (disorder)", 22),
        ("76844004", "Local infection of wound (disorder)", 22),
        ("211463006", "Foreign body in skin wound (disorder)", 22),
    ]
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": [{"code": code, "display": display, "concept_active": True, "attribute_count_returned": count} for code, display, count in concepts],
        "verified_attribute_ids": ["363698007", "246112005"],
        "laterality": {"reference_set": "723264001", "postcoordination_asserted": False, "reason": "Body site and laterality remain separate Facts until the selected anatomical structure is individually verified as lateralizable and normal-form compatible."},
        "validation": {"method": "build_time_live_mapping_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "provenance": provenance(["source.stom.wound-minor-injury.20260715"]),
    }
    documents = [
        ("knowledge/base/primary-care-wound-minor-injury.json", graph),
        ("rules/base/primary-care-wound-minor-injury.json", rules),
        ("knowledge/generated/injury/wound-minor-injury/wound-minor-injury.json", f),
        ("mappings/terminology/snomed-mrcm-wound-minor-injury.json", mapping),
        ("sources/manifests/primary-care-wound-minor-injury.json", primary),
        ("sources/manifests/primary-care-wound-minor-injury-research.json", research),
        ("policies/primary-care-wound-minor-injury-completion.json", completion(f)),
    ]
    for path, document in documents:
        write_json(path, document)
    for name, case in cases(f).items():
        write_json("simulation/patients/injury/wound-minor-injury/" + name, case)


if __name__ == "__main__":
    main()
