#!/usr/bin/env python3
"""Materialize unreviewed lump, lymph-node and soft-tissue-mass knowledge."""
from profile_support import *

P = "lump-lymph-node"
RFE = "rfe.lump_lymph_node"
M = "mapping.snomed-mrcm.lump-lymph-node"
SN = "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = ["source.nice.ng12.lump.2026", "source.nhs.lumps.2026", "source.nhs.swollen-glands.2023", "source.nhs.non-hodgkin-lymphoma.2026", "source.stom.lump-lymph-node.20260715"]
G = {k: f"group.lump.{k}" for k in ("routing", "safety", "common", "lymph-node", "skin-soft-tissue", "breast-axilla", "neck", "groin-scrotal", "abdominal-pelvic", "bone")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("lump.primary_group", "Primary Lump Group", "coded", "primary-group", "덩이나 부기는 림프절, 피부·피하, 깊은 연부조직, 유방·겨드랑이, 목, 서혜부·음낭, 복부·골반 또는 뼈 중 어디에 가깝나요?", 180, [G["routing"]], C, allowed_values=["lymph_node", "skin_subcutaneous", "deep_soft_tissue", "breast_axilla", "neck", "groin_scrotal", "abdominal_pelvic", "bone", "other_unclear"]),
        Q("lump.airway_or_swallowing_compromise", "Airway or Swallowing Compromise from Lump", "boolean", "airway-swallow", "목·입안의 덩이나 부기 때문에 숨쉬기 매우 어렵거나 침도 삼키기 힘든가요?", 179, [G["safety"], G["neck"]], S, safety_relevant=True),
        Q("lump.rapidly_spreading_red_hot_swelling_with_systemic_illness", "Rapidly Spreading Inflamed Swelling", "boolean", "spreading-infection", "덩이 주변의 붉음·열감·통증이 빠르게 퍼지면서 고열·오한·혼란·심한 처짐이 있나요?", 178, [G["safety"], G["skin-soft-tissue"]], S, safety_relevant=True),
        Q("lump.pulsatile_or_suddenly_expanding_mass", "Pulsatile or Suddenly Expanding Mass", "boolean", "pulsatile", "덩이가 맥박처럼 뛰거나 갑자기 커지면서 심한 통증·어지럼·실신이 있나요?", 177, [G["safety"]], S, safety_relevant=True),
        Q("lump.limb_neurovascular_compromise", "Limb Neurovascular Compromise from Mass", "boolean", "neurovascular", "팔·다리 덩이 아래쪽이 갑자기 차갑고 창백·파래지거나 감각·움직임이 떨어졌나요?", 176, [G["safety"], G["skin-soft-tissue"]], S, safety_relevant=True),
        Q("lump.sudden_severe_testicular_or_scrotal_pain", "Sudden Severe Testicular or Scrotal Pain", "boolean", "testicular-pain", "고환·음낭 덩이와 함께 갑자기 심한 통증, 메스꺼움·구토가 생겼나요?", 175, [G["safety"], G["groin-scrotal"]], S, safety_relevant=True),
        Q("lump.painful_irreducible_groin_mass_with_vomiting", "Painful Irreducible Groin Mass", "boolean", "incarcerated-groin", "서혜부 덩이가 매우 아프고 눕거나 가볍게 눌러도 들어가지 않으면서 구토·복부팽만이 있나요?", 174, [G["safety"], G["groin-scrotal"]], S, safety_relevant=True),
        Q("lump.breast_inflammation_with_systemic_illness", "Breast Inflammation with Systemic Illness", "boolean", "breast-infection", "유방이 빠르게 붉고 뜨겁게 붓고 심하게 아프면서 고열·오한·심한 처짐이 있나요?", 173, [G["safety"], G["breast-axilla"]], S, safety_relevant=True),
        Q("lump.rapid_growth_or_large_deep_fixed_mass", "Rapidly Growing Deep or Fixed Mass", "boolean", "rapid-deep-fixed", "원인 모를 덩이가 계속 커지거나 깊고 단단하며 주변에 고정된 느낌인가요?", 172, [G["safety"], G["skin-soft-tissue"]], S, safety_relevant=True),
        Q("lump.supraclavicular_or_persistent_cervical_node", "Supraclavicular or Persistent Cervical Node", "boolean", "supraclavicular", "쇄골 위·아래 림프절이 붓거나 목의 덩이가 지속되고 원인이 분명하지 않나요?", 171, [G["safety"], G["lymph-node"], G["neck"]], S, safety_relevant=True),
        Q("lump.generalized_nodes_with_b_symptoms", "Generalized Nodes with Systemic Symptoms", "boolean", "generalized-b", "여러 부위 림프절이 붓고 원인 모를 발열·흠뻑 젖는 야간발한·체중감소·가려움 중 하나 이상이 있나요?", 170, [G["safety"], G["lymph-node"]], S, safety_relevant=True),
        Q("lump.unexplained_breast_or_axillary_lump", "Unexplained Breast or Axillary Lump", "boolean", "breast-axillary", "유방 또는 겨드랑이에 원인이 분명하지 않은 새 덩이가 있나요?", 169, [G["safety"], G["breast-axilla"]], S, safety_relevant=True),
        Q("lump.nonpainful_testicular_change", "Non-painful Testicular Change", "boolean", "testicular-change", "고환 자체가 아프지 않게 커졌거나 모양·단단함·표면 감촉이 달라졌나요?", 168, [G["safety"], G["groin-scrotal"]], S, safety_relevant=True),
        Q("lump.abdominal_pelvic_mass_or_ascites", "Abdominal or Pelvic Mass or Ascites", "boolean", "abdominal-pelvic", "배나 골반에서 덩이가 만져지거나 원인 모르게 배가 계속 불러오고 복수가 의심되나요?", 167, [G["safety"], G["abdominal-pelvic"]], S, safety_relevant=True),
        Q("lump.child_unexplained_lymphadenopathy_or_bone_swelling", "Child Unexplained Nodes or Bone Swelling", "boolean", "child-warning", "소아·청소년에게 원인 모를 지속성 림프절 또는 뼈의 부기·통증이 있나요?", 166, [G["safety"], G["lymph-node"], G["bone"]], S, safety_relevant=True),
        Q("lump.ulceration_bleeding_or_skin_breakdown", "Ulcerating or Bleeding Lump", "boolean", "ulceration-bleeding", "덩이 위 피부가 헐거나 잘 낫지 않고 반복 출혈·진물·괴사가 있나요?", 165, [G["safety"], G["skin-soft-tissue"]], S, safety_relevant=True),

        Q("lump.exact_body_site", "Exact Lump Body Site", "string", "body-site", "덩이의 정확한 신체 부위와 표면·피부 아래·깊은 곳 중 어디인지 알려주세요.", 155, [G["common"]], C),
        Q("lump.laterality", "Lump Laterality", "coded", "laterality", "덩이는 왼쪽, 오른쪽, 양쪽 또는 정중앙 중 어디인가요?", 154, [G["common"]], C, allowed_values=["left", "right", "bilateral", "midline", "not_lateralizable_or_unclear"]),
        Q("lump.number_and_distribution", "Number and Distribution of Lumps", "string", "number-distribution", "한 개인가요 여러 개인가요? 여러 개라면 한 부위에 모였는지 여러 신체 부위에 있는지 알려주세요.", 153, [G["common"]], C),
        Q("lump.onset_duration_and_discovery", "Lump Onset Duration and Discovery", "string", "onset-duration", "처음 발견한 날짜·상황과 얼마나 지속됐는지 알려주세요.", 152, [G["common"]], C),
        Q("lump.size_and_measurement", "Lump Size and Measurement", "string", "size", "현재 크기를 센티미터 또는 콩·포도·달걀 같은 비교물로 알려주세요. 이전 측정값도 있으면 알려주세요.", 151, [G["common"]], C),
        Q("lump.growth_course", "Lump Growth Course", "coded", "growth", "크기는 줄어듦, 그대로, 서서히 커짐, 빠르게 커짐 또는 커졌다 작아짐 중 무엇인가요?", 150, [G["common"]], C, allowed_values=["decreasing", "stable", "slowly_increasing", "rapidly_increasing", "fluctuating", "unclear"]),
        Q("lump.pain_nrs", "Lump Pain NRS", "integer", "pain-nrs", "덩이가 아프다면 현재 통증을 0점부터 10점까지 숫자로 알려주세요.", 149, [G["common"]], C),
        Q("lump.tenderness_and_pain_pattern", "Lump Tenderness and Pain Pattern", "string", "pain-pattern", "만질 때만 아픈지, 가만히 있어도 아픈지, 밤이나 움직임·식사·생리와 연관되는지 알려주세요.", 148, [G["common"]], C),
        Q("lump.consistency_mobility_and_depth", "Lump Consistency Mobility and Depth", "string", "consistency", "부드러움·고무같음·단단함, 손으로 밀면 움직이는지, 피부나 깊은 조직에 고정됐는지 알려주세요.", 147, [G["common"]], C),
        Q("lump.skin_surface_changes", "Skin Changes over Lump", "string", "skin-change", "덩이 위 피부의 붉음·열감·멍·색 변화·구멍·진물·궤양 여부를 알려주세요.", 146, [G["common"]], C),
        Q("lump.relation_to_movement_swallowing_or_straining", "Lump Dynamic Features", "string", "dynamic", "움직임·삼킴·기침·힘주기·자세에 따라 덩이가 움직이거나 커졌다 작아지나요?", 145, [G["common"]], D),
        Q("lump.recurrence_prior_removal_or_pathology", "Prior Lump Removal or Pathology", "string", "prior-lump", "같은 곳에 이전에도 생겼거나 제거·배액·조직검사를 했나요? 결과를 알려주세요.", 144, [G["common"]], R),
        Q("lump.recent_injury_injection_procedure_or_implant", "Local Injury Procedure or Implant", "string", "local-event", "최근 해당 부위의 외상·주사·수술·보형물·필러 또는 반복 압박이 있었나요?", 143, [G["common"]], D),
        Q("lump.current_tests_and_referrals", "Lump Tests and Referrals", "string", "tests-referral", "이미 받은 진찰·혈액검사·초음파·X선·CT·MRI·조직검사 결과와 예약된 진료를 알려주세요.", 142, [G["common"]], R),
        Q("lump.cancer_immunosuppression_and_radiation_history", "Cancer and Immunosuppression Context", "string", "cancer-risk", "과거 암·방사선치료·장기이식·면역저하 또는 현재 항암·면역억제 치료가 있나요?", 141, [G["common"]], R),
        Q("lump.family_history_and_genetic_risk", "Family and Genetic Risk for Lump", "string", "family-risk", "가족의 암·림프종·유전성 종양 또는 비슷한 덩이 병력을 알려주세요.", 140, [G["common"]], R),
        Q("lump.current_medicines_and_anticoagulation", "Medicines and Bleeding Risk", "string", "medicines", "현재 복용약과 항응고제·항혈소판제, 최근 시작한 약을 알려주세요.", 139, [G["common"]], R),
        Q("lump.other_detail_or_patient_priority", "Other Lump Detail or Patient Priority", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달하고 싶은 내용이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("lump.node_regions", "Lymph Node Regions", "string", "node-regions", "목·턱밑·쇄골·겨드랑이·서혜부 중 어느 림프절이 부었나요?", 130, [G["lymph-node"]], C, terminology_binding={"system": SN, "code": "30746006"}, mrcm_ref=M),
        Q("lump.local_infection_symptoms", "Local Infection near Lymph Nodes", "string", "local-infection", "최근 감기·인후통·귀·치아·피부 상처·감염 등 림프절 주변의 증상이 있었나요?", 129, [G["lymph-node"]], D),
        Q("lump.systemic_b_symptoms", "Systemic Symptoms with Lymphadenopathy", "string", "b-symptoms", "원인 모를 발열, 흠뻑 젖는 야간발한, 체중감소·식욕저하·가려움·숨참이 있나요?", 128, [G["lymph-node"]], R),
        Q("lump.recent_vaccination_infection_travel_or_animal_exposure", "Lymph Node Exposure Context", "string", "node-exposures", "최근 예방접종·감염, 해외여행, 결핵 노출, 고양이 등 동물 접촉이 있었나요?", 127, [G["lymph-node"]], D),
        Q("lump.alcohol_induced_node_pain", "Alcohol-induced Lymph Node Pain", "boolean", "alcohol-node-pain", "술을 마신 뒤 림프절 부위 통증이 생기거나 심해지나요?", 126, [G["lymph-node"]], R),

        Q("lump.skin_punctum_fluctuation_or_drainage", "Skin Lump Punctum Fluctuation or Drainage", "string", "skin-features", "피부 덩이에 가운데 구멍, 말랑한 고름 느낌, 냄새 나는 내용물이나 배출이 있나요?", 130, [G["skin-soft-tissue"]], D),
        Q("lump.soft_tissue_depth_fascia_and_function", "Soft Tissue Mass Depth and Functional Impact", "string", "soft-tissue-depth", "덩이가 근육·근막 아래 깊은 느낌인지, 관절·근육 움직임이나 기능을 방해하는지 알려주세요.", 129, [G["skin-soft-tissue"]], R),
        Q("lump.soft_tissue_size_growth_and_recurrence", "Soft Tissue Mass Growth and Recurrence", "string", "soft-tissue-growth", "연부조직 덩이의 현재·이전 크기, 증가 속도와 제거 후 재발 여부를 알려주세요.", 128, [G["skin-soft-tissue"]], R),

        Q("lump.breast_anatomy_age_and_hormonal_context", "Breast Lump Clinical Context", "string", "breast-context", "연령과 유방 조직·호르몬 치료 여부, 임신·수유·폐경 및 마지막 생리 시기를 알려주세요.", 130, [G["breast-axilla"]], R),
        Q("lump.breast_cycle_relation_and_change", "Breast Lump Cycle Relation", "string", "breast-cycle", "덩이와 통증이 생리 주기에 따라 변하는지, 계속 남아 있거나 커지는지 알려주세요.", 129, [G["breast-axilla"]], C),
        Q("lump.nipple_discharge_retraction_or_skin_dimpling", "Nipple and Breast Skin Changes", "string", "breast-warning", "한쪽 유두 분비물·피, 유두 함몰, 피부 함몰·오렌지껍질 변화가 있나요?", 128, [G["breast-axilla"]], R),
        Q("lump.breast_implant_surgery_and_family_history", "Breast Procedure and Family History", "string", "breast-history", "유방 보형물·수술·조직검사와 본인·가족의 유방·난소암 병력을 알려주세요.", 127, [G["breast-axilla"]], R),

        Q("lump.neck_subsite_and_swallow_movement", "Neck Lump Subsite and Movement", "string", "neck-subsite", "목 앞·옆·턱밑·귀밑 중 어디이며 침 삼킬 때나 혀를 내밀 때 움직이나요?", 130, [G["neck"]], C),
        Q("lump.hoarseness_dysphagia_or_oral_lesion", "Head and Neck Associated Symptoms", "string", "neck-associated", "지속되는 목쉼, 삼킴곤란·통증, 한쪽 귀 통증 또는 입안 궤양·덩이가 있나요?", 129, [G["neck"]], R),
        Q("lump.thyroid_or_salivary_features", "Thyroid or Salivary Features", "string", "thyroid-salivary", "두근거림·체중변화·더위·추위 민감 또는 식사 때 턱밑·귀밑이 붓고 아픈 증상이 있나요?", 128, [G["neck"]], D),
        Q("lump.head_neck_tobacco_alcohol_and_hpv_context", "Head and Neck Risk Context", "string", "neck-risk", "흡연·음주력, HPV 관련 병력과 과거 두경부암·방사선치료를 알려주세요.", 127, [G["neck"]], R),

        Q("lump.groin_scrotal_exact_structure", "Groin or Scrotal Lump Structure", "string", "groin-structure", "덩이가 서혜부, 음낭 피부, 고환 자체 또는 고환 주변 중 어디에서 만져지나요?", 130, [G["groin-scrotal"]], C),
        Q("lump.groin_reducibility_and_cough_impulse", "Groin Lump Reducibility", "string", "groin-reducibility", "누우면 작아지거나 손으로 들어가고, 기침·힘주기·서 있을 때 커지나요?", 129, [G["groin-scrotal"]], D),
        Q("lump.testicular_shape_texture_and_heaviness", "Testicular Shape Texture and Heaviness", "string", "testicular-detail", "고환의 크기·모양·단단함 변화, 묵직함 또는 둔한 통증이 있나요?", 128, [G["groin-scrotal"]], R),
        Q("lump.genital_urinary_infection_or_trauma", "Genital Urinary Infection or Trauma Context", "string", "genital-context", "배뇨 증상·분비물·성매개감염 위험, 최근 외상·수술이 있었나요?", 127, [G["groin-scrotal"]], D),

        Q("lump.abdominal_pelvic_location_and_distension", "Abdominal Pelvic Lump Detail", "string", "abdomen-detail", "배·골반 어느 부위에서 만져지고, 복부팽만·조기포만·식욕저하가 있나요?", 130, [G["abdominal-pelvic"]], C, terminology_binding={"system": SN, "code": "309524007"}, mrcm_ref=M),
        Q("lump.abdominal_bowel_urinary_or_bleeding_symptoms", "Abdominal Pelvic Associated Symptoms", "string", "abdomen-associated", "배변·배뇨 변화, 혈변·혈뇨, 질 출혈·분비물 또는 체중감소가 있나요?", 129, [G["abdominal-pelvic"]], R),
        Q("lump.pregnancy_reproductive_and_gynaecologic_context", "Reproductive Context for Pelvic Mass", "string", "pelvic-context", "임신 가능성, 마지막 생리, 폐경 상태와 자궁·난소 질환·수술력을 알려주세요.", 128, [G["abdominal-pelvic"]], R),

        Q("lump.bone_site_pain_and_night_pattern", "Bone Swelling and Pain Pattern", "string", "bone-pattern", "뼈의 부위와 부기, 밤에 깨는 통증·지속 통증 또는 압통이 있나요?", 130, [G["bone"]], C),
        Q("lump.bone_trauma_function_and_fracture_context", "Bone Lump Trauma and Function", "string", "bone-function", "외상 없이 생겼는지, 움직임·체중부하 제한 또는 병적 골절 의심 상황이 있나요?", 129, [G["bone"]], R),
    ]
    rules = [
        safety_rule(P, "airway-swallow", {"fact": "lump.airway_or_swallowing_compromise", "equals": True}, "emergency", 1000),
        safety_rule(P, "spreading-infection", {"fact": "lump.rapidly_spreading_red_hot_swelling_with_systemic_illness", "equals": True}, "emergency", 1000),
        safety_rule(P, "pulsatile", {"fact": "lump.pulsatile_or_suddenly_expanding_mass", "equals": True}, "emergency", 1000),
        safety_rule(P, "neurovascular", {"fact": "lump.limb_neurovascular_compromise", "equals": True}, "emergency", 1000),
        safety_rule(P, "testicular-pain", {"fact": "lump.sudden_severe_testicular_or_scrotal_pain", "equals": True}, "emergency", 1000),
        safety_rule(P, "incarcerated-groin", {"fact": "lump.painful_irreducible_groin_mass_with_vomiting", "equals": True}, "emergency", 1000),
        safety_rule(P, "breast-infection", {"fact": "lump.breast_inflammation_with_systemic_illness", "equals": True}, "urgent", 980),
        safety_rule(P, "rapid-deep-fixed", {"fact": "lump.rapid_growth_or_large_deep_fixed_mass", "equals": True}, "urgent", 970),
        safety_rule(P, "supraclavicular", {"fact": "lump.supraclavicular_or_persistent_cervical_node", "equals": True}, "urgent", 970),
        safety_rule(P, "generalized-b", {"fact": "lump.generalized_nodes_with_b_symptoms", "equals": True}, "urgent", 970),
        safety_rule(P, "breast-axillary", {"fact": "lump.unexplained_breast_or_axillary_lump", "equals": True}, "urgent", 960),
        safety_rule(P, "testicular-change", {"fact": "lump.nonpainful_testicular_change", "equals": True}, "urgent", 960),
        safety_rule(P, "abdominal-pelvic", {"fact": "lump.abdominal_pelvic_mass_or_ascites", "equals": True}, "urgent", 960),
        safety_rule(P, "child-warning", {"fact": "lump.child_unexplained_lymphadenopathy_or_bone_swelling", "equals": True}, "urgent", 970),
        safety_rule(P, "ulceration-bleeding", {"fact": "lump.ulceration_bleeding_or_skin_breakdown", "equals": True}, "urgent", 950),
    ]
    return {"id": "knowledge.generated.lump-lymph-node", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-lump-lymph-node-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="lump.primary_group", question_budget=65, source_refs=SOURCES)
    common = ["lump.exact_body_site", "lump.laterality", "lump.number_and_distribution", "lump.onset_duration_and_discovery", "lump.size_and_measurement", "lump.growth_course", "lump.pain_nrs", "lump.tenderness_and_pain_pattern", "lump.consistency_mobility_and_depth", "lump.skin_surface_changes", "lump.recurrence_prior_removal_or_pathology", "lump.current_tests_and_referrals", "lump.cancer_immunosuppression_and_radiation_history", "lump.other_detail_or_patient_priority"]
    cases = {
        "lymph_node": ["lump.node_regions", "lump.local_infection_symptoms", "lump.systemic_b_symptoms", "lump.recent_vaccination_infection_travel_or_animal_exposure", "lump.alcohol_induced_node_pain"],
        "skin_subcutaneous": ["lump.skin_punctum_fluctuation_or_drainage", "lump.recent_injury_injection_procedure_or_implant"],
        "deep_soft_tissue": ["lump.soft_tissue_depth_fascia_and_function", "lump.soft_tissue_size_growth_and_recurrence"],
        "breast_axilla": ["lump.breast_anatomy_age_and_hormonal_context", "lump.breast_cycle_relation_and_change", "lump.nipple_discharge_retraction_or_skin_dimpling", "lump.breast_implant_surgery_and_family_history"],
        "neck": ["lump.neck_subsite_and_swallow_movement", "lump.hoarseness_dysphagia_or_oral_lesion", "lump.thyroid_or_salivary_features", "lump.head_neck_tobacco_alcohol_and_hpv_context"],
        "groin_scrotal": ["lump.groin_scrotal_exact_structure", "lump.groin_reducibility_and_cough_impulse", "lump.testicular_shape_texture_and_heaviness", "lump.genital_urinary_infection_or_trauma"],
        "abdominal_pelvic": ["lump.abdominal_pelvic_location_and_distension", "lump.abdominal_bowel_urinary_or_bleeding_symptoms", "lump.pregnancy_reproductive_and_gynaecologic_context"],
        "bone": ["lump.bone_site_pain_and_night_pattern", "lump.bone_trauma_function_and_fracture_context"],
        "other_unclear": ["lump.other_detail_or_patient_priority"],
    }
    policy["required_facts"]["routine"] = common
    policy["conditional_required_facts"] = [{"selector_fact": "lump.primary_group", "cases": cases}]
    return policy


def source_docs():
    defs = [
        ("source.nice.ng12.lump.2026", "NICE", "Suspected cancer: recognition and referral", "NG12; updated-2026-04-15", "https://www.nice.org.uk/guidance/ng12/chapter/Recommendations-organised-by-site-of-cancer", "nice_guidance", 7, ["Unexplained increasing soft-tissue lumps, persistent unexplained lymphadenopathy, breast or axillary lumps, neck lumps, testicular changes, abdominal or pelvic masses and unexplained child bone swelling require site- and age-specific assessment or referral.", "Associated fever, night sweats, weight loss, pruritus, breathlessness and alcohol-induced node pain inform lymphadenopathy referral; this package supports history collection and does not diagnose cancer."]),
        ("source.nhs.lumps.2026", "NHS", "Lumps", "accessed-2026-07-15", "https://www.nhs.uk/symptoms/lumps/", "public_health_guidance", 7, ["Record growth, duration, pain, redness or heat, hardness, mobility, recurrence and breast or testicular location; persistent or concerning lumps need clinical assessment."]),
        ("source.nhs.swollen-glands.2023", "NHS", "Swollen glands", "reviewed-2023-09-29", "https://www.nhs.uk/symptoms/swollen-glands/", "public_health_guidance", 7, ["Lymph-node assessment includes distribution, tenderness, local infection, persistence, growth, hardness or fixation, supraclavicular location, fever and night sweats."]),
        ("source.nhs.non-hodgkin-lymphoma.2026", "NHS", "Symptoms of non-Hodgkin lymphoma", "reviewed-2026-03-10", "https://www.nhs.uk/conditions/non-hodgkin-lymphoma/symptoms/", "public_health_guidance", 7, ["Painless persistent nodes may coexist with fever, night sweats, breathlessness, pruritus and unexplained weight loss, but these findings are not diagnostic."]),
        ("source.stom.lump-lymph-node.20260715", "Infoclinic", "STOM lump and lymph-node terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", 30, ["FHIR lookup confirmed active concepts for lymphadenopathy, localized enlarged lymph nodes, subcutaneous nodule and mass of trunk.", "Body site and laterality remain separate Facts until the selected anatomical concept is verified in reference set 723264001 and a valid post-coordinated expression is produced; MRCM does not determine urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-15", "next_monitor_at": "2026-08-14" if days == 30 else "2026-07-22", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, days, assertions in defs]
    research = {"id": "source-manifest.primary-care-lump-lymph-node-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.lump-lymph-node", "generated_clinical_knowledge", "knowledge/generated/general/lump-lymph-node/lump-lymph-node.json", True), ("source.mapping.lump-lymph-node", "terminology_mapping", "mappings/terminology/snomed-mrcm-lump-lymph-node.json", False), ("source.external.lump-lymph-node", "external_source_manifest", "sources/manifests/primary-care-lump-lymph-node-research.json", False), ("source.policy.lump-lymph-node", "runtime_policy", "policies/primary-care-lump-lymph-node-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-lump-lymph-node", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level = rule["when"]["fact"], rule["then"]["safety_level"]
        key = rule["id"].split("safety.")[1]
        out[f"LUMP-{key.upper()}.json"] = {"id": f"LUMP-{key.upper()}", "simulation_language": "ko", "persona": {"age": 25 + i}, "initial_statement": {"ko": "몸에 덩이가 만져져서 왔어요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.cancer", "diagnosis.lymphoma", "diagnosis.soft_tissue_sarcoma"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["lymph_node"])
    by_id = {x["fact"]["id"]: x["fact"] for x in f["entries"]}
    hidden = {}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        elif fact["value_type"] == "integer": hidden[fid] = {"value": 0}
        else: hidden[fid] = {"value": "없음"}
    hidden["lump.primary_group"] = {"value": "lymph_node"}
    declined = "lump.recent_vaccination_infection_travel_or_animal_exposure"
    hidden.pop(declined)
    out["LUMP-NODE-DATA-ABSENT.json"] = {"id": "LUMP-NODE-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 38}, "initial_statement": {"ko": "목에 작은 멍울이 만져져요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 65, "forbidden_assertions": ["diagnosis.lymphoma", "diagnosis.reactive_node"]}, "provenance": provenance(["source.nhs.swollen-glands.2023", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Lump, Lymph Node or Soft Tissue Mass", intents=[("intent.characterize_symptom", "Characterize Lump"), ("intent.screen_red_flags", "Screen Immediate and Urgent Features"), ("intent.differentiate_common_causes", "Assess Local and Systemic Context"), ("intent.risk_assessment", "Assess Persistence and Referral Risk")])
    primary, research = source_docs()
    concepts = [("30746006", "Lymphadenopathy (disorder)", 22), ("274744005", "Localized enlarged lymph nodes (disorder)", 22), ("95325000", "Subcutaneous nodule (finding)", 0), ("309524007", "Mass of trunk (finding)", 20)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["363698007", "272741003", "246112005"], "laterality": {"reference_set": "723264001", "postcoordination_asserted": False, "reason": "Exact anatomy and laterality are separate Facts until the selected structure is verified as lateralizable and MRCM-compatible."}, "validation": {"method": "build_time_live_fhir_lookup_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.lump-lymph-node.20260715"])}
    docs = [("knowledge/base/primary-care-lump-lymph-node.json", graph), ("rules/base/primary-care-lump-lymph-node.json", rules), ("knowledge/generated/general/lump-lymph-node/lump-lymph-node.json", f), ("mappings/terminology/snomed-mrcm-lump-lymph-node.json", mapping), ("sources/manifests/primary-care-lump-lymph-node.json", primary), ("sources/manifests/primary-care-lump-lymph-node-research.json", research), ("policies/primary-care-lump-lymph-node-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/general/lump-lymph-node/" + name, case)


if __name__ == "__main__": main()
