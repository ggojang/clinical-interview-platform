#!/usr/bin/env python3
"""Materialize unreviewed breast-symptom clinician pre-visit knowledge."""
from profile_support import *

P, RFE = "breast-symptoms", "rfe.breast_symptoms"
M, SN = "mapping.snomed-mrcm.breast-symptoms", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-16T09:00:00Z"
SOURCES = [
    "source.nice.ng12.breast.2026",
    "source.acr.palpable-breast-masses.current-2026",
    "source.acr.nipple-discharge.2022",
    "source.acr.breast-pain.current-2026",
    "source.nhs.mastitis.2023",
    "source.nhs.breast-abscess.2023",
    "source.nhs.breast-pain.2023",
    "source.nhs.nipple-discharge.2024",
    "source.abm.mastitis-protocol-36.2022",
    "source.stom.breast-symptoms.20260716",
]
G = {key: f"group.breast.{key}" for key in (
    "routing", "safety", "site", "lump", "pain", "nipple", "skin",
    "lactation", "risk", "followup", "function",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
D = ["intent.differentiate_common_causes"]
R = ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("breast.primary_group", "Primary Breast Concern", "coded", "primary-group", "이번 방문은 유방·가슴의 멍울이나 단단한 부위, 통증, 유두 분비, 유두·피부·모양 변화, 붉음·열감·부기 또는 수유기 염증, 외상·수술·보형물 문제, 이전 검사·치료 추적 중 무엇에 가장 가깝나요?", 230, [G["routing"]], C, allowed_values=["lump_or_thickening", "pain", "nipple_discharge", "nipple_or_skin_change", "inflammation_or_lactation", "injury_procedure_or_implant", "prior_test_or_treatment_followup", "other_unclear"]),
        Q("breast.collapse_confusion_or_severe_breathing_with_illness", "Severe Systemic Illness", "boolean", "severe-systemic", "유방의 통증·붉음·부기와 함께 쓰러짐, 의식 혼란, 심한 숨참 또는 깨우기 어려울 정도의 전신 악화가 있나요?", 229, [G["safety"]], S, safety_relevant=True),
        Q("breast.uncontrolled_bleeding_after_injury_or_procedure", "Uncontrolled Breast Bleeding", "boolean", "uncontrolled-bleeding", "유방·유두의 외상이나 시술 뒤 직접 압박해도 많은 출혈이 계속되거나 어지럽고 쓰러질 것 같은가요?", 228, [G["safety"]], S, safety_relevant=True),
        Q("breast.rapid_spreading_redness_high_fever_or_shaking_chills", "Rapidly Progressive Breast Infection Warning", "boolean", "spreading-infection", "붉음·열감·부기가 빠르게 번지면서 고열, 심한 오한 또는 전신 상태 악화가 있나요?", 227, [G["safety"], G["skin"]], S, safety_relevant=True),
        Q("breast.painful_warm_lump_with_fever_or_pus", "Breast Abscess Warning", "boolean", "abscess-warning", "매우 아프고 뜨거운 멍울·부기가 있으면서 열이 나거나 유두·상처에서 고름이 나오나요?", 226, [G["safety"], G["lump"]], S, safety_relevant=True),
        Q("breast.implant_or_trauma_rapid_swelling_deformity_or_severe_pain", "Implant or Trauma Warning", "boolean", "implant-trauma-warning", "보형물이 있거나 유방을 다친 뒤 한쪽이 빠르게 붓고 모양이 변하거나 피부색 변화·참기 어려운 통증이 생겼나요?", 225, [G["safety"]], S, safety_relevant=True),
        Q("breast.new_unexplained_breast_or_axillary_lump", "New Unexplained Breast or Axillary Lump", "boolean", "new-lump-warning", "새로 생긴 원인 불명의 유방 멍울·단단한 부위 또는 겨드랑이 멍울이 있나요?", 224, [G["safety"], G["lump"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "89164003"}, mrcm_ref=M),
        Q("breast.spontaneous_unilateral_bloody_or_clear_discharge", "Concerning Nipple Discharge", "boolean", "discharge-warning", "짜지 않았는데 한쪽 유두에서 피가 섞이거나 맑은 분비물이 저절로 나오나요?", 223, [G["safety"], G["nipple"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "54302000"}, mrcm_ref=M),
        Q("breast.new_nipple_retraction_ulcer_or_persistent_eczema", "New Nipple Change Warning", "boolean", "nipple-change-warning", "한쪽 유두가 새로 안으로 들어가거나 낫지 않는 습진·딱지·궤양·출혈이 생겼나요?", 222, [G["safety"], G["nipple"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "271955004"}, mrcm_ref=M),
        Q("breast.skin_dimpling_peau_orange_or_shape_change", "Breast Skin or Shape Warning", "boolean", "skin-shape-warning", "피부가 움푹 패이거나 귤껍질처럼 변하고, 한쪽 유방의 크기·윤곽·모양이 새로 달라졌나요?", 221, [G["safety"], G["skin"]], S, safety_relevant=True),
        Q("breast.inflammation_not_improving_after_treatment", "Persistent Inflammation after Treatment", "boolean", "persistent-inflammation", "염증 치료를 시작한 뒤 48시간이 지나도 호전되지 않거나 치료 중인데 더 악화하나요?", 220, [G["safety"], G["followup"]], S, safety_relevant=True),

        Q("breast.information_source_and_reliability", "Information Source", "string", "information-source", "누가 답변하고 있으며 본인 관찰, 보호자, 사진, 이전 진료기록 중 무엇에 근거하나요? 서로 다른 정보나 확실하지 않은 부분도 알려주세요.", 205, [G["routing"]], C),
        Q("breast.age_and_relevant_anatomy_context", "Age and Anatomy Context", "string", "age-anatomy", "만 나이와 현재 유방 조직·유두 관련 진료에 필요한 성별 또는 해부학적 정보를 답변 가능한 범위에서 알려주세요.", 204, [G["routing"], G["risk"]], R),
        Q("breast.reproductive_stage_and_menstrual_status", "Reproductive and Menstrual Stage", "string", "reproductive-stage", "초경 전·가임기·임신·수유·산후·폐경 이행기·폐경 후 중 해당하는 상태와 마지막 생리 시작일을 알려주세요.", 203, [G["risk"], G["lactation"]], R),
        Q("breast.onset_duration_current_status_and_course", "Onset Duration and Course", "string", "onset-course", "처음 발견한 날짜·상황, 지금도 있는지와 커짐·줄어듦·반복·빠른 변화 등 경과를 알려주세요.", 202, [G["site"]], C),
        Q("breast.side_and_bilateral_status", "Breast Side", "coded", "side", "어느 쪽인가요?", 201, [G["site"]], C, allowed_values=["left", "right", "bilateral", "midline_or_chest_wall", "unclear"]),
        Q("breast.exact_site_quadrant_clock_face_and_distance_from_nipple", "Exact Breast Site", "string", "exact-site", "유두·유륜·유방·겨드랑이 중 정확한 부위와 가능하면 위·아래/안쪽·바깥쪽 또는 시계방향, 유두에서의 거리를 알려주세요.", 200, [G["site"]], C),
        Q("breast.number_and_distribution_of_areas", "Number and Distribution", "string", "number-distribution", "한 군데인지 여러 군데인지, 한쪽에 모여 있는지 양쪽에 흩어져 있는지 알려주세요.", 199, [G["site"], G["lump"]], C),

        Q("breast.lump_or_thickening_present", "Breast Lump or Thickening Present", "boolean", "lump-present", "직접 느껴지는 멍울, 결절 또는 주변과 다른 단단한 부위가 있나요?", 195, [G["lump"]], C, terminology_binding={"system": SN, "code": "89164003"}, mrcm_ref=M),
        Q("breast.lump_size_measurement_and_change", "Lump Size and Change", "string", "lump-size", "멍울의 대략적인 가로·세로 크기 또는 비교 가능한 크기와 처음보다 변했는지 알려주세요. 직접 측정하지 않았다면 그렇게 표시해주세요.", 194, [G["lump"]], C),
        Q("breast.lump_patient_observed_texture_mobility_and_tenderness", "Patient-observed Lump Features", "string", "lump-features", "본인이 느끼기에 단단함·말랑함, 잘 움직임·고정된 느낌, 누르면 아픔이 어떤가요? 이는 의료진 진찰 결과가 아니라 본인 관찰로 기록됩니다.", 193, [G["lump"]], C),
        Q("breast.axillary_or_supraclavicular_lump", "Axillary or Supraclavicular Lump", "string", "node-lump", "겨드랑이 또는 쇄골 위에 새 멍울이 있으면 위치·크기·통증·지속기간을 알려주세요.", 192, [G["lump"], G["risk"]], R),
        Q("breast.change_with_menstrual_cycle_pregnancy_or_lactation", "Hormonal or Lactation Relationship", "string", "hormonal-pattern", "생리 전후, 임신, 수유·유축, 단유와 증상 변화가 연관되어 보이나요? 반복 주기와 양쪽 여부를 알려주세요.", 191, [G["lump"], G["pain"], G["lactation"]], D),

        Q("breast.pain_present", "Breast Pain Present", "boolean", "pain-present", "유방·유두·겨드랑이 또는 가슴벽 통증이 있나요?", 187, [G["pain"]], C, terminology_binding={"system": SN, "code": "53430007"}, mrcm_ref=M),
        Q("breast.pain_nrs", "Breast Pain NRS", "integer", "pain-nrs", "[필수] 통증이 있다면 현재 통증을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 186, [G["pain"]], C),
        Q("breast.pain_focal_diffuse_cyclical_and_timing", "Breast Pain Pattern", "string", "pain-pattern", "통증이 한 점에 국한되는지 넓게 퍼지는지, 지속·간헐·생리 주기성인지와 하루 중 시기·지속시간을 알려주세요.", 185, [G["pain"]], C),
        Q("breast.pain_character_radiation_and_trigger", "Breast Pain Character", "string", "pain-character", "찌름·화끈거림·묵직함 등 양상, 겨드랑이·팔·등으로 퍼짐과 누르기·움직임·운동·수유로 유발되는지 알려주세요.", 184, [G["pain"]], C),
        Q("breast.chest_wall_neck_shoulder_or_back_relation", "Chest Wall and Musculoskeletal Relation", "string", "musculoskeletal-relation", "목·어깨·등·갈비뼈 통증, 자세·팔 움직임·기침·깊은숨과 유방 통증의 관계가 있나요?", 183, [G["pain"]], D),

        Q("breast.nipple_discharge_present", "Nipple Discharge Present", "boolean", "discharge-present", "유두에서 모유 외 액체가 나오거나 묻어 있나요?", 178, [G["nipple"]], C, terminology_binding={"system": SN, "code": "54302000"}, mrcm_ref=M),
        Q("breast.discharge_spontaneous_or_expressed_and_laterality", "Discharge Trigger and Side", "string", "discharge-trigger", "분비물이 저절로 나오는지 눌렀을 때만 나오는지, 한쪽·양쪽과 한 구멍·여러 구멍 중 무엇인지 알려주세요.", 177, [G["nipple"]], C),
        Q("breast.discharge_color_amount_frequency_and_blood", "Discharge Appearance", "string", "discharge-appearance", "색(맑음·흰색·노랑·초록·갈색·피), 양, 빈도, 속옷에 묻는지와 냄새를 알려주세요.", 176, [G["nipple"]], C),
        Q("breast.nipple_inversion_retraction_or_direction_change", "Nipple Retraction or Direction Change", "string", "nipple-retraction", "유두가 원래부터 들어가 있었는지 새로 들어가거나 방향이 변했는지, 한쪽·양쪽과 시작 시점을 알려주세요.", 175, [G["nipple"]], R, terminology_binding={"system": SN, "code": "271955004"}, mrcm_ref=M),
        Q("breast.nipple_rash_crust_fissure_ulcer_or_bleeding", "Nipple Skin Change", "string", "nipple-skin", "유두·유륜의 발진, 가려움, 각질·딱지, 갈라짐·상처·궤양 또는 출혈의 위치와 지속기간을 알려주세요.", 174, [G["nipple"], G["skin"]], R),

        Q("breast.redness_warmth_swelling_and_extent", "Breast Redness Warmth and Swelling", "string", "inflammation-local", "붉음·열감·부기의 위치, 범위, 경계, 빠르게 번지는지와 피부색 때문에 붉음을 확인하기 어려운지도 알려주세요.", 169, [G["skin"]], C),
        Q("breast.fever_chills_aches_fatigue_and_measured_temperature", "Systemic Infection Features", "string", "infection-systemic", "측정한 체온과 오한·몸살·피로·메스꺼움 등 전신 증상, 시작 시점을 알려주세요.", 168, [G["skin"]], R),
        Q("breast.skin_dimpling_thickening_orange_peel_and_shape", "Breast Skin and Shape Change", "string", "skin-shape", "피부 함몰·두꺼워짐·귤껍질 모양, 정맥이 두드러짐 또는 유방 크기·윤곽·대칭 변화와 시작 시점을 알려주세요.", 167, [G["skin"], G["risk"]], R),
        Q("breast.skin_wound_piercing_bite_or_dermatitis", "Breast Skin Barrier Injury", "string", "skin-barrier", "최근 상처·긁힘·벌레물림·피어싱·면도·습진 등 피부 손상과 분비물·감염 징후가 있나요?", 166, [G["skin"]], D),

        Q("breast.pregnancy_postpartum_lactation_and_weaning_dates", "Pregnancy and Lactation Status", "string", "lactation-status", "임신 주수, 출산일, 현재 수유·유축 여부, 단유 시점과 마지막 수유·유축 시각을 알려주세요.", 161, [G["lactation"], G["risk"]], R),
        Q("breast.feeding_pumping_pattern_affected_side_and_recent_change", "Feeding and Pumping Pattern", "string", "feeding-pattern", "직접수유·유축 빈도, 한쪽 선호·건너뜀, 최근 간격·양 변화, 과다분비 또는 젖이 남는 느낌을 알려주세요.", 160, [G["lactation"]], D),
        Q("breast.latch_nipple_trauma_and_infant_feeding_context", "Latch and Nipple Trauma", "string", "latch-trauma", "아기 물림·자세 문제, 유두 통증·상처·출혈과 아기의 수유 곤란·구강 문제를 알려주세요.", 159, [G["lactation"]], D),
        Q("breast.prior_mastitis_abscess_recurrence_and_culture", "Prior Mastitis or Abscess", "string", "prior-infection", "이전 유선염·농양의 횟수·쪽·시기, 배양검사·배농·입원 여부와 같은 부위 재발인지 알려주세요.", 158, [G["lactation"], G["followup"]], R, terminology_binding={"system": SN, "code": "266579006"}, mrcm_ref=M),

        Q("breast.personal_breast_ovarian_cancer_or_high_risk_lesion", "Personal Breast Cancer Risk History", "string", "personal-risk", "유방암·난소암, 비정형증식·상피내암 등 고위험 병변 또는 흉부 방사선치료 병력을 진단 나이·쪽과 함께 알려주세요.", 152, [G["risk"]], R),
        Q("breast.family_cancer_and_genetic_test_history", "Family and Genetic Risk", "string", "family-risk", "혈연가족의 유방암·난소암·췌장암·전립선암과 진단 나이·관계, BRCA 등 유전검사 결과를 알려주세요.", 151, [G["risk"]], R),
        Q("breast.hormonal_psychotropic_and_discharge_related_medicines", "Breast-relevant Medicines", "string", "medicines", "피임약·호르몬치료, 항정신병약·항우울제 등 유즙분비 관련 약과 처방약·일반약·보충제의 이름·용량·최근 변경을 알려주세요.", 150, [G["risk"]], R),
        Q("breast.smoking_diabetes_immunosuppression_and_infection_risk", "Infection and Healing Risk", "string", "infection-risk", "흡연·전자담배, 당뇨, 면역저하 질환·치료, 피부질환 등 감염·회복에 영향을 줄 수 있는 상태를 알려주세요.", 149, [G["risk"]], R),
        Q("breast.implant_type_side_date_and_known_complications", "Breast Implant Context", "string", "implant", "보형물·조직확장기·주입물의 종류, 삽입 날짜·쪽과 파열·구축·감염 등 이전 문제를 알려주세요.", 148, [G["risk"], G["followup"]], R),
        Q("breast.surgery_biopsy_procedure_radiation_and_pathology", "Breast Procedure History", "string", "procedure-history", "유방·겨드랑이 수술, 생검·배농·성형·방사선치료의 날짜·쪽과 병리 결과를 알려주세요.", 147, [G["risk"], G["followup"]], R),
        Q("breast.prior_examination_imaging_birads_and_date", "Prior Breast Assessment", "string", "prior-assessment", "이전 의료진 진찰, 유방촬영·초음파·MRI의 날짜·쪽·주요 결과와 BI-RADS를 알면 알려주세요. 원본 유무도 표시해주세요.", 146, [G["followup"]], R),
        Q("breast.screening_history_result_and_followup_due", "Breast Screening History", "string", "screening", "가장 최근 유방검진의 종류·날짜·결과와 추가검사 또는 추적 권고를 알려주세요.", 145, [G["followup"]], R),
        Q("breast.current_and_prior_treatment_response_and_adverse_effects", "Treatment and Response", "string", "treatment-response", "진통제·항생제·냉찜질·수유 조정·배농 등 시행한 치료의 시작일·효과·부작용과 악화 여부를 알려주세요.", 144, [G["followup"]], R),
        Q("breast.work_sleep_activity_feeding_and_daily_impact", "Functional Impact", "string", "function", "통증·분비·부기 때문에 수면, 일·학교, 팔 사용·운동, 수유·유축 또는 아기 돌봄에 어떤 영향이 있나요?", 130, [G["function"]], R),
        Q("breast.patient_concern_goal_and_other_detail", "Patient Concern and Goal", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달할 내용, 가장 걱정하는 점과 이번 진료에서 원하는 도움을 알려주세요.", 90, [G["routing"], G["followup"]], C),
    ]
    safety = [
        ("severe-systemic", "breast.collapse_confusion_or_severe_breathing_with_illness", "emergency"),
        ("uncontrolled-bleeding", "breast.uncontrolled_bleeding_after_injury_or_procedure", "emergency"),
        ("spreading-infection", "breast.rapid_spreading_redness_high_fever_or_shaking_chills", "urgent"),
        ("abscess-warning", "breast.painful_warm_lump_with_fever_or_pus", "urgent"),
        ("implant-trauma-warning", "breast.implant_or_trauma_rapid_swelling_deformity_or_severe_pain", "urgent"),
        ("new-lump-warning", "breast.new_unexplained_breast_or_axillary_lump", "clarify"),
        ("discharge-warning", "breast.spontaneous_unilateral_bloody_or_clear_discharge", "clarify"),
        ("nipple-change-warning", "breast.new_nipple_retraction_ulcer_or_persistent_eczema", "clarify"),
        ("skin-shape-warning", "breast.skin_dimpling_peau_orange_or_shape_change", "clarify"),
        ("persistent-inflammation", "breast.inflammation_not_improving_after_treatment", "urgent"),
    ]
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-16", "next_monitor_at": "2026-07-17", "next_full_review_at": "2027-01-12"})
    return {
        "id": "knowledge.generated.breast-symptoms", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-breast-symptoms-research",
        "default_refresh": refresh,
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [],
        "safety_rules": [safety_rule(P, key, {"fact": fact, "equals": True}, level, 1000 if level == "emergency" else 990 if level == "urgent" else 980) for key, fact, level in safety],
        "entries": e, "provenance": provenance(SOURCES),
    }


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="breast.primary_group", question_budget=68, source_refs=SOURCES)
    # Time-sensitive breast warning features require prompt handoff, but the
    # pre-visit interview should still collect the short clinician dataset when
    # the patient can continue. A 12-question clarify cap ended immediately
    # after the safety screen and omitted the lump/discharge/skin description.
    policy["question_budget"]["clarify"] = 68
    safety_ids = {rule["when"]["fact"] for rule in f["safety_rules"]}
    common = {
        "breast.information_source_and_reliability", "breast.age_and_relevant_anatomy_context",
        "breast.reproductive_stage_and_menstrual_status", "breast.onset_duration_current_status_and_course",
        "breast.side_and_bilateral_status", "breast.exact_site_quadrant_clock_face_and_distance_from_nipple",
        "breast.number_and_distribution_of_areas", "breast.pregnancy_postpartum_lactation_and_weaning_dates",
        "breast.personal_breast_ovarian_cancer_or_high_risk_lesion", "breast.family_cancer_and_genetic_test_history",
        "breast.hormonal_psychotropic_and_discharge_related_medicines", "breast.smoking_diabetes_immunosuppression_and_infection_risk",
        "breast.implant_type_side_date_and_known_complications", "breast.surgery_biopsy_procedure_radiation_and_pathology",
        "breast.prior_examination_imaging_birads_and_date", "breast.screening_history_result_and_followup_due",
        "breast.current_and_prior_treatment_response_and_adverse_effects", "breast.work_sleep_activity_feeding_and_daily_impact",
        "breast.patient_concern_goal_and_other_detail",
    }
    policy["required_facts"]["routine"] = sorted(common)
    branches = {
        "lump_or_thickening": ["breast.lump_or_thickening_present", "breast.lump_size_measurement_and_change", "breast.lump_patient_observed_texture_mobility_and_tenderness", "breast.axillary_or_supraclavicular_lump", "breast.change_with_menstrual_cycle_pregnancy_or_lactation"],
        "pain": ["breast.pain_present", "breast.pain_nrs", "breast.pain_focal_diffuse_cyclical_and_timing", "breast.pain_character_radiation_and_trigger", "breast.chest_wall_neck_shoulder_or_back_relation", "breast.change_with_menstrual_cycle_pregnancy_or_lactation"],
        "nipple_discharge": ["breast.nipple_discharge_present", "breast.discharge_spontaneous_or_expressed_and_laterality", "breast.discharge_color_amount_frequency_and_blood", "breast.nipple_inversion_retraction_or_direction_change", "breast.nipple_rash_crust_fissure_ulcer_or_bleeding"],
        "nipple_or_skin_change": ["breast.nipple_inversion_retraction_or_direction_change", "breast.nipple_rash_crust_fissure_ulcer_or_bleeding", "breast.redness_warmth_swelling_and_extent", "breast.skin_dimpling_thickening_orange_peel_and_shape", "breast.skin_wound_piercing_bite_or_dermatitis"],
        "inflammation_or_lactation": ["breast.redness_warmth_swelling_and_extent", "breast.fever_chills_aches_fatigue_and_measured_temperature", "breast.skin_wound_piercing_bite_or_dermatitis", "breast.feeding_pumping_pattern_affected_side_and_recent_change", "breast.latch_nipple_trauma_and_infant_feeding_context", "breast.prior_mastitis_abscess_recurrence_and_culture"],
        "injury_procedure_or_implant": ["breast.skin_wound_piercing_bite_or_dermatitis", "breast.implant_type_side_date_and_known_complications", "breast.surgery_biopsy_procedure_radiation_and_pathology"],
        "prior_test_or_treatment_followup": ["breast.prior_examination_imaging_birads_and_date", "breast.screening_history_result_and_followup_due", "breast.current_and_prior_treatment_response_and_adverse_effects"],
        "other_unclear": [],
    }
    policy["conditional_required_facts"] = [{"selector_fact": "breast.primary_group", "cases": branches}]
    assert safety_ids.issubset(set(policy["required_facts"]["always"]))
    return policy


def source_docs():
    defs = [
        ("source.nice.ng12.breast.2026", "NICE", "Suspected cancer: recognition and referral — breast recommendations", "NG12; last-reviewed-2026-04-15", "https://www.nice.org.uk/guidance/ng12/chapter/Recommendations-organised-by-site-of-cancer", "nice_guidance", ["Referral factors include age, unexplained breast or axillary lump, unilateral nipple discharge or retraction and concerning breast skin change.", "These UK referral thresholds are source context for time-sensitive clinician review and are not automatically treated as Korean jurisdiction policy."]),
        ("source.acr.palpable-breast-masses.current-2026", "American College of Radiology", "ACR Appropriateness Criteria: Palpable Breast Masses", "current-accessed-2026-07-16", "https://acsearch.acr.org/docs/69495/Narrative", "clinical_guideline", ["Age, pregnancy or lactation context, exact palpable site and prior imaging result affect the clinician's diagnostic imaging pathway.", "The interview records existing results but does not order or select imaging."]),
        ("source.acr.nipple-discharge.2022", "American College of Radiology", "ACR Appropriateness Criteria: Evaluation of Nipple Discharge", "2022-update", "https://acsearch.acr.org/docs/3099312/Narrative/", "clinical_guideline", ["Nipple-discharge evaluation distinguishes physiologic from pathologic patterns using spontaneity, laterality, duct distribution, appearance, age and pregnancy or lactation context.", "Imaging appropriateness remains a clinician decision outside Runtime."]),
        ("source.acr.breast-pain.current-2026", "American College of Radiology", "ACR Appropriateness Criteria: Breast Pain", "current-accessed-2026-07-16", "https://acsearch.acr.org/docs/3091546/Narrative/", "clinical_guideline", ["Breast pain characterization includes focal versus diffuse, cyclical versus noncyclical pattern, age and associated suspicious findings.", "The package preserves mandatory raw NRS separately from imaging considerations."]),
        ("source.nhs.mastitis.2023", "NHS", "Mastitis", "reviewed-2023-03-17", "https://www.nhs.uk/conditions/mastitis/", "public_health_guidance", ["Mastitis may include unilateral rapid-onset painful hot swelling, hard or wedge-shaped area, discharge, fever, chills, aches and fatigue.", "History includes breastfeeding status, nipple damage, implant, smoking, diabetes or immunosuppression, recurrence and response after 12–24 hours or 48 hours of antibiotics."]),
        ("source.nhs.breast-abscess.2023", "NHS", "Breast abscess", "reviewed-2023-06-14", "https://www.nhs.uk/conditions/breast-abscess/", "public_health_guidance", ["A painful warm or red breast lump with fever or feeling unwell needs prompt clinical assessment.", "Prior mastitis or abscess and response after antibiotics are relevant handoff facts."]),
        ("source.nhs.breast-pain.2023", "NHS", "Breast pain", "reviewed-2023-05-03", "https://www.nhs.uk/symptoms/breast-pain/", "public_health_guidance", ["Pain history distinguishes cyclical bilateral diffuse pain from focal symptoms and captures pregnancy, medicines, musculoskeletal relation and family history.", "Hard lump, discharge, shape change, dimpling, nipple rash or retraction and febrile hot swelling are warning features."]),
        ("source.nhs.nipple-discharge.2024", "NHS", "Nipple discharge", "reviewed-2024-01-29", "https://www.nhs.uk/symptoms/nipple-discharge/", "public_health_guidance", ["Discharge history includes spontaneous versus expressed, side, color including blood, amount, pregnancy or breastfeeding and medication context.", "The interview does not infer a cause from appearance alone."]),
        ("source.abm.mastitis-protocol-36.2022", "Academy of Breastfeeding Medicine", "Clinical Protocol #36: The Mastitis Spectrum", "revised-2022", "https://doi.org/10.1089/bfm.2022.29207.kbm", "clinical_guideline", ["Lactation history includes feeding and pumping pattern, oversupply, nipple trauma, prior episodes, systemic symptoms, treatment and abscess or phlegmon concern.", "The protocol informs interview targets only; treatment advice is withheld until completion and remains non-prescriptive."]),
        ("source.stom.breast-symptoms.20260716", "Infoclinic", "STOM breast symptom terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["Build-time searches confirmed active candidates for Breast lump 89164003, Pain of breast 53430007, Discharge from nipple 54302000, Inflammatory disorder of breast 266579006 and Retraction of nipple 271955004.", "MRCM returned Finding site and Severity among allowed attributes. Breast-structure reference-set membership was returned but active-status interpretation was inconclusive, so side and exact site remain separate Facts and no post-coordinated expression is asserted."]),
    ]
    artifacts = [{
        "id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata",
        "publisher": publisher, "title": title, "version": version, "url": url,
        "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached",
        "license_status": "restricted" if publisher in {"Infoclinic", "Academy of Breastfeeding Medicine"} else "unknown",
        "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-16",
        "monitor_result": "current_official_source_confirmed", "assertions": assertions,
    } for sid, publisher, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-breast-symptoms-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([item[0] for item in defs])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.breast-symptoms", "generated_clinical_knowledge", "knowledge/generated/breast/breast-symptoms/breast-symptoms.json", True),
        ("source.mapping.breast-symptoms", "terminology_mapping", "mappings/terminology/snomed-mrcm-breast-symptoms.json", False),
        ("source.external.breast-symptoms", "external_source_manifest", "sources/manifests/primary-care-breast-symptoms-research.json", False),
        ("source.policy.breast-symptoms", "runtime_policy", "policies/primary-care-breast-symptoms-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-breast-symptoms", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        fact_id = rule["when"]["fact"]
        level = rule["then"]["safety_level"]
        key = rule["id"].split("safety.")[1]
        out[f"BREAST-{key.upper()}.json"] = {
            "id": f"BREAST-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 22 + index * 5}, "initial_statement": {"ko": "유방에 변화가 생겼어요."},
            "hidden_state": {fact_id: {"value": True}},
            "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation" if level in {"urgent", "emergency"} else "required_targets_addressed_with_absent_data", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.breast_cancer", "diagnosis.mastitis", "diagnosis.breast_abscess"]},
            "provenance": provenance(SOURCES),
        }
    policy = completion(f)
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}
    def routine(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"][branch])
        values = {}
        for fact_id in required:
            fact = by_id[fact_id]
            values[fact_id] = {"value": False if fact["value_type"] == "boolean" else 0 if fact["value_type"] == "integer" else fact.get("allowed_values", ["없음"])[0] if fact["value_type"] == "coded" else "없음"}
        values["breast.primary_group"] = {"value": branch}
        return values
    lump = routine("lump_or_thickening")
    lump["breast.lump_or_thickening_present"] = {"value": True}
    lump["breast.new_unexplained_breast_or_axillary_lump"] = {"value": True}
    lump["breast.lump_size_measurement_and_change"] = {"value": "왼쪽 위바깥쪽 약 1.5 cm로 추정, 2주 동안 큰 변화 없음"}
    out["BREAST-ROUTINE-LUMP-CLINICIAN-HANDOFF.json"] = {"id": "BREAST-ROUTINE-LUMP-CLINICIAN-HANDOFF", "simulation_language": "ko", "persona": {"age": 28}, "initial_statement": {"ko": "왼쪽 유방에 작은 멍울이 만져져 진료 전 문진을 작성합니다."}, "hidden_state": lump, "expected": {"expected_safety_level": "clarify", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"breast.lump_size_measurement_and_change": "왼쪽 위바깥쪽 약 1.5 cm로 추정, 2주 동안 큰 변화 없음"}, "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.fibroadenoma", "diagnosis.breast_cancer"]}, "provenance": provenance(SOURCES)}
    pain = routine("pain")
    pain["breast.pain_present"] = {"value": True}; pain["breast.pain_nrs"] = {"value": 6}; pain["pain.frequency"] = {"value": "daily"}
    out["BREAST-PAIN-MANDATORY-NRS.json"] = {"id": "BREAST-PAIN-MANDATORY-NRS", "simulation_language": "ko", "persona": {"age": 41}, "initial_statement": {"ko": "한쪽 유방이 매일 아파요."}, "hidden_state": pain, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"breast.pain_nrs": 6}, "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.breast_cancer"]}, "provenance": provenance(SOURCES)}
    absent = routine("nipple_discharge")
    absent.pop("breast.discharge_color_amount_frequency_and_blood")
    out["BREAST-DISCHARGE-DATA-ABSENT.json"] = {"id": "BREAST-DISCHARGE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 35}, "initial_statement": {"ko": "유두에 분비물이 있었는데 색은 기억나지 않아요."}, "hidden_state": absent, "response_behavior": {"breast.discharge_color_amount_frequency_and_blood": {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {"breast.discharge_color_amount_frequency_and_blood": "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.intraductal_papilloma"]}, "provenance": provenance(SOURCES)}
    proxy = routine("inflammation_or_lactation")
    proxy["breast.information_source_and_reliability"] = {"value": "산후 보호자가 영상통화로 대신 답변하며 본인과 함께 확인함"}
    out["BREAST-POSTPARTUM-PROXY-REMOTE.json"] = {"id": "BREAST-POSTPARTUM-PROXY-REMOTE", "simulation_language": "ko", "persona": {"age": 32}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "video", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "출산 후 유방이 불편해 보호자와 영상으로 답합니다."}, "hidden_state": proxy, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.mastitis"]}, "provenance": provenance(SOURCES)}
    extra = routine("prior_test_or_treatment_followup")
    extra["breast.patient_concern_goal_and_other_detail"] = {"value": "검사 추적 외에 진료확인서 발급 가능 여부도 전달하고 싶음"}
    out["BREAST-UNRELATED-ADDITIONAL-COMMENT.json"] = {"id": "BREAST-UNRELATED-ADDITIONAL-COMMENT", "simulation_language": "ko", "persona": {"age": 52}, "initial_statement": {"ko": "유방검사 추적과 다른 요청도 있어요."}, "hidden_state": extra, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"breast.patient_concern_goal_and_other_detail": "검사 추적 외에 진료확인서 발급 가능 여부도 전달하고 싶음"}, "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.abnormal_mammogram"]}, "provenance": provenance(SOURCES)}
    multi = routine("pain")
    multi["breast.patient_concern_goal_and_other_detail"] = {"value": "유방 통증 외에 최근 목 통증도 별도 문진을 원함"}
    out["BREAST-MULTI-RFE-NECK-PAIN.json"] = {"id": "BREAST-MULTI-RFE-NECK-PAIN", "simulation_language": "ko", "persona": {"age": 47}, "initial_statement": {"ko": "유방 통증과 목 통증이 같이 있어요."}, "hidden_state": multi, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 75, "forbidden_assertions": ["diagnosis.cervical_radiculopathy", "diagnosis.referred_breast_pain"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Breast Symptom or Concern", intents=[
        ("intent.characterize_symptom", "Characterize Breast Lump Pain Nipple Skin and Lactation Symptoms"),
        ("intent.screen_red_flags", "Screen Severe Infection Bleeding Trauma and Time-sensitive Breast Warning Features"),
        ("intent.differentiate_common_causes", "Assess Cyclical Lactational Inflammatory Medication and Musculoskeletal Context"),
        ("intent.risk_assessment", "Assess Cancer Risk Prior Procedures Imaging Treatment Function and Patient Goals"),
    ])
    primary, research = source_docs()
    concepts = [("89164003", "Breast lump (finding)", 20), ("53430007", "Pain of breast (finding)", 20), ("54302000", "Discharge from nipple (disorder)", 21), ("266579006", "Inflammatory disorder of breast (disorder)", 21), ("271955004", "Retraction of nipple (finding)", 20)]
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": [{"code": code, "display": display, "concept_active": True, "attribute_count_returned": count} for code, display, count in concepts],
        "verified_attribute_ids": ["363698007", "246112005"],
        "laterality": {"reference_set": "723264001", "candidate_finding_site_codes": ["76752008", "82038008", "272670002", "279005008"], "membership_rows_returned": True, "postcoordination_asserted": False, "reason": "Reference-set rows were returned but referenced-component active status was inconclusive; exact site and side remain separate Facts until a version-consistent normal-form validation passes."},
        "validation": {"method": "build_time_live_search_mrcm_and_refset_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "partial_provisional_pass"},
        "breast_semantics": {"diagnosis_inferred": False, "malignancy_probability_calculated": False, "imaging_selected_by_runtime": False, "patient_self_examination_treated_as_clinician_exam": False, "runtime_terminology_query_required": False},
        "provenance": provenance(["source.stom.breast-symptoms.20260716"]),
    }
    documents = [
        ("knowledge/base/primary-care-breast-symptoms.json", graph),
        ("rules/base/primary-care-breast-symptoms.json", rules),
        ("knowledge/generated/breast/breast-symptoms/breast-symptoms.json", f),
        ("mappings/terminology/snomed-mrcm-breast-symptoms.json", mapping),
        ("sources/manifests/primary-care-breast-symptoms.json", primary),
        ("sources/manifests/primary-care-breast-symptoms-research.json", research),
        ("policies/primary-care-breast-symptoms-completion.json", completion(f)),
    ]
    for path, document in documents:
        write_json(path, document)
    for name, case in cases(f).items():
        write_json("simulation/patients/breast/breast-symptoms/" + name, case)


if __name__ == "__main__":
    main()
