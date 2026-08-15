#!/usr/bin/env python3
"""Materialize unreviewed allergic-reaction and drug-allergy knowledge."""
from profile_support import *

P = "allergy-concern"
RFE = "rfe.allergy_concern"
M = "mapping.snomed-mrcm.allergy-concern"
SN = "http://snomed.info/sct"
ACQUIRED_AT = "2026-08-10T10:58:00Z"
SOURCES = [
    "source.nice.ng258.anaphylaxis.2026",
    "source.nice.cg183.drug-allergy.2014",
    "source.nice.qs97.drug-allergy.2015",
    "source.hl7.fhir-r4.allergyintolerance.4.0.1",
    "source.nhs.anaphylaxis.2026",
    "source.nhs.stevens-johnson.2026",
    "source.stom.allergy-concern.20260810",
]
G = {k: f"group.allergy.{k}" for k in (
    "routing", "shared-safety", "common", "skin-angioedema",
    "respiratory", "food", "drug", "sting-contact",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
D = ["intent.differentiate_common_causes"]
R = ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("allergy.primary_group", "Primary Allergy Concern Group", "coded", "primary-group", "주된 문제는 갑작스러운 전신 알레르기 반응, 피부·부종, 코·눈·호흡기 증상, 음식, 약물, 벌레·접촉 노출 중 무엇인가요?", 170, [G["routing"]], C, allowed_values=["acute_systemic", "skin_angioedema", "respiratory", "food", "drug", "sting_contact", "other_unclear"]),

        Q("allergy.airway_compromise", "Airway Compromise in Allergic Reaction", "boolean", "airway", "현재 혀·목이 붓거나 목소리가 갑자기 쉬고, 침을 삼키기 어렵거나 숨쉴 때 목에서 거친 소리가 나나요?", 169, [G["shared-safety"]], S, safety_relevant=True),
        Q("allergy.breathing_compromise", "Breathing Compromise in Allergic Reaction", "boolean", "breathing", "현재 숨이 매우 차거나 쌕쌕거리고, 말을 이어가기 어렵거나 입술이 파래지나요?", 168, [G["shared-safety"], G["respiratory"]], S, safety_relevant=True),
        Q("allergy.circulatory_compromise", "Circulatory Compromise in Allergic Reaction", "boolean", "circulation", "현재 쓰러질 것처럼 어지럽거나 실제로 실신했고, 식은땀·창백함·맥박이 매우 빠른 느낌이 있나요?", 167, [G["shared-safety"]], S, safety_relevant=True),
        Q("allergy.altered_consciousness_or_collapse", "Altered Consciousness or Collapse", "boolean", "collapse", "현재 의식이 흐리거나 반응이 둔해졌거나 쓰러진 적이 있나요?", 166, [G["shared-safety"]], S, safety_relevant=True),
        Q("allergy.rapid_multisystem_progression", "Rapid Multisystem Allergic Progression", "boolean", "rapid-multisystem", "노출 뒤 수분~수시간 안에 피부·입안, 호흡기, 어지럼·실신, 심한 복통·구토 중 둘 이상의 증상이 빠르게 함께 생기거나 악화하나요?", 165, [G["shared-safety"]], S, safety_relevant=True),
        Q("allergy.current_adrenaline_autoinjector_use", "Current Adrenaline Autoinjector Use", "boolean", "adrenaline-used", "이번 반응 때문에 아드레날린 자가주사기를 이미 사용했나요?", 164, [G["shared-safety"]], S, safety_relevant=True),
        Q("allergy.severe_asthma_or_rescue_failure", "Severe Asthma or Rescue Treatment Failure", "boolean", "asthma-failure", "천식이 있으면서 흡입제를 사용해도 숨참·쌕쌕거림이 빠르게 악화하나요?", 163, [G["shared-safety"], G["respiratory"]], S, safety_relevant=True),
        Q("allergy.skin_pain_blistering_or_detachment", "Painful Blistering or Detaching Rash", "boolean", "skin-detachment", "새 약을 사용한 뒤 피부가 아프고 넓게 물집이 잡히거나 벗겨지나요?", 162, [G["shared-safety"], G["drug"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "73442001"}, mrcm_ref=M),
        Q("allergy.mucosal_erosion_or_eye_involvement", "Mucosal Erosion or Eye Involvement", "boolean", "mucosal-eye", "입술·입안·눈·생식기에 통증성 물집이나 헐음이 생겼거나 눈이 붓고 아픈가요?", 161, [G["shared-safety"], G["drug"]], S, safety_relevant=True),
        Q("allergy.drug_rash_fever_facial_edema_or_organ_symptoms", "Systemic Features with Drug Rash", "boolean", "systemic-drug-rash", "새 약 뒤 발진과 함께 고열, 얼굴 부종, 심한 처짐, 황달·진한 소변 또는 숨참이 있나요?", 160, [G["shared-safety"], G["drug"]], S, safety_relevant=True),
        Q("allergy.repeated_vomiting_or_severe_abdominal_pain", "Repeated Vomiting or Severe Abdominal Pain", "boolean", "gi-severe", "의심 노출 뒤 반복 구토나 심한 복통이 생겼고 다른 알레르기 증상도 함께 있나요?", 159, [G["shared-safety"], G["food"]], S, safety_relevant=True),
        Q("allergy.reaction_after_injection_or_procedure", "Reaction after Injection or Procedure", "boolean", "injection-procedure", "주사·조영제·예방접종·수술 또는 처치 직후 전신 증상이 빠르게 생겼나요?", 158, [G["shared-safety"], G["drug"]], S, safety_relevant=True),

        Q("allergy.current_or_historical_episode", "Current or Historical Allergy Episode", "coded", "episode-context", "지금 진행 중인 반응인가요, 이미 회복한 반응을 기록·상담하려는 것인가요?", 150, [G["common"]], C, allowed_values=["current", "recovering", "historical", "unclear"]),
        Q("allergy.onset_date_time_and_course", "Onset Date Time and Course", "string", "onset-course", "증상은 언제 시작했고, 얼마나 빨리 심해졌으며 지금은 좋아짐·그대로·악화 중 어느 상태인가요?", 149, [G["common"]], C),
        Q("allergy.circumstances_before_onset", "Circumstances Immediately Before Onset", "string", "circumstances", "시작 직전에 먹거나 복용·주사한 것, 벌레 물림, 운동, 작업·접촉 등 어떤 일이 있었나요?", 148, [G["common"]], C),
        Q("allergy.suspected_trigger_and_latency", "Suspected Trigger and Latency", "string", "trigger-latency", "의심되는 원인과 노출 후 첫 증상까지 걸린 시간을 알려주세요.", 147, [G["common"]], D),
        Q("allergy.symptom_sequence_and_systems", "Symptom Sequence and Involved Systems", "string", "sequence-systems", "어떤 증상이 어떤 순서로 생겼고 피부·입안, 호흡, 위장관, 어지럼·실신 중 어디에 나타났나요?", 146, [G["common"]], C),
        Q("allergy.treatment_and_response", "Treatment and Response", "string", "treatment-response", "항히스타민제·흡입제·아드레날린·병원 치료 등 받은 처치와 반응을 알려주세요.", 145, [G["common"]], R),
        Q("allergy.prior_similar_reaction", "Prior Similar Reaction", "string", "prior-reaction", "같은 물질이나 비슷한 상황에서 이전에도 반응했나요? 당시 증상과 중증도를 알려주세요.", 144, [G["common"]], R),
        Q("allergy.known_allergies_and_avoidance", "Known Allergies and Avoidance", "string", "known-allergies", "이미 확인되었거나 의심되는 음식·약물·벌독·라텍스 등 알레르기와 피하는 항목을 알려주세요.", 143, [G["common"]], R, terminology_binding={"system": SN, "code": "418038007"}, mrcm_ref=M),
        Q("allergy.specialist_testing_and_emergency_plan", "Allergy Testing and Emergency Plan", "string", "testing-plan", "알레르기 전문검사 결과, 아드레날린 자가주사기 처방 또는 응급 행동계획이 있나요?", 142, [G["common"]], R),
        Q("allergy.asthma_cardiovascular_mast_cell_context", "Allergy Severity Risk Context", "string", "risk-context", "천식, 심혈관질환, 비만세포질환 또는 과거 아나필락시스가 있나요?", 141, [G["common"]], R),
        Q("allergy.current_medicines_and_risk_modifiers", "Current Medicines and Risk Modifiers", "string", "current-medicines", "현재 복용약, 최근 바뀐 약, 베타차단제·ACE억제제·NSAID 복용 여부를 알려주세요.", 140, [G["common"]], R),
        Q("allergy.pregnancy_age_and_care_context", "Age Pregnancy and Care Context", "string", "patient-context", "연령, 임신 여부와 현재 혼자인지·도움을 줄 사람이 있는지 알려주세요.", 139, [G["common"]], R),
        Q("allergy.other_detail_or_patient_priority", "Other Allergy Detail or Patient Priority", "string", "other-detail", "질문에 없지만 꼭 전달하고 싶은 내용이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("allergy.skin_lesion_type", "Allergic Skin Lesion Type", "coded", "skin-type", "피부 증상은 두드러기처럼 솟음, 붉은 발진, 가려움만, 물집·벗겨짐 중 무엇에 가깝나요?", 130, [G["skin-angioedema"]], C, allowed_values=["urticaria", "rash", "itch_only", "blistering_detachment", "other_unclear"], terminology_binding={"system": SN, "code": "126485001"}, mrcm_ref=M),
        Q("allergy.skin_distribution_duration_and_recurrence", "Skin Distribution Duration and Recurrence", "string", "skin-detail", "어디에서 시작해 어디까지 퍼졌고, 한 병변이 얼마나 지속되며 반복해서 나타나나요?", 129, [G["skin-angioedema"]], C),
        Q("allergy.angioedema_sites", "Angioedema Sites", "string", "angioedema-sites", "눈꺼풀·입술·혀·손발 등 피부 깊은 부종이 생긴 부위를 알려주세요.", 128, [G["skin-angioedema"]], C, terminology_binding={"system": SN, "code": "41291007"}, mrcm_ref=M),
        Q("allergy.skin_photograph_available", "Allergy Photograph Available", "boolean", "photo", "현재 또는 당시 발진·부종 사진이 있나요?", 127, [G["skin-angioedema"]], R),

        Q("allergy.nasal_and_ocular_features", "Nasal and Ocular Allergy Features", "string", "nasal-ocular", "재채기·맑은 콧물·코막힘과 눈 가려움·눈물 증상이 있나요? 계절이나 장소에 따라 달라지나요?", 130, [G["respiratory"]], C),
        Q("allergy.cough_wheeze_chest_tightness", "Lower Respiratory Allergy Features", "string", "lower-respiratory", "기침·쌕쌕거림·가슴 답답함이 있고 운동이나 수면에 영향을 주나요?", 129, [G["respiratory"]], C),
        Q("allergy.environmental_or_occupational_pattern", "Environmental or Occupational Allergy Pattern", "string", "environment-pattern", "집먼지·동물·곰팡이·꽃가루·직장 물질과 접촉하거나 특정 장소에 있을 때 심해지나요?", 128, [G["respiratory"], G["sting-contact"]], D),

        Q("allergy.food_identity_amount_and_preparation", "Food Identity Amount and Preparation", "string", "food-identity", "의심 음식의 정확한 이름, 먹은 양과 생식·가열·혼합식품 여부를 알려주세요.", 130, [G["food"]], C),
        Q("allergy.food_cofactors", "Food Allergy Cofactors", "string", "food-cofactors", "음식 전후 운동, 음주, NSAID 복용, 감염 또는 생리 같은 동반 요인이 있었나요?", 129, [G["food"]], D),
        Q("allergy.food_reproducibility_and_current_tolerance", "Food Reaction Reproducibility and Tolerance", "string", "food-tolerance", "같은 음식을 다시 먹었을 때 반복됐나요? 현재 소량 또는 가열 형태는 먹을 수 있나요?", 128, [G["food"]], R),

        Q("allergy.drug_generic_name", "Suspected Drug Generic Name", "string", "drug-generic-name", "의심되는 약의 성분명을 알려주세요. 기억나지 않으면 모른다고 답해도 됩니다.", 147, [G["drug"]], C, terminology_binding={"system": SN, "code": "416098002"}, mrcm_ref=M),
        Q("allergy.drug_brand_name", "Suspected Drug Brand Name", "string", "drug-brand-name", "의심되는 약의 제품명을 알려주세요. 처방전·약봉투·사진에서 확인한 이름도 좋습니다.", 146, [G["drug"]], C),
        Q("allergy.drug_strength", "Suspected Drug Strength", "string", "drug-strength", "의심되는 약의 함량은 얼마였나요? 예: 500 mg.", 145, [G["drug"]], C),
        Q("allergy.drug_formulation", "Suspected Drug Formulation", "string", "drug-formulation", "의심되는 약의 제형은 정제, 캡슐, 시럽, 주사, 연고 중 무엇이었나요? 보기에 없으면 직접 입력해 주세요.", 144, [G["drug"]], C),
        Q("allergy.drug_indication", "Drug Indication", "string", "drug-indication", "그 약을 어떤 증상이나 질환 때문에 사용했나요?", 143, [G["drug"]], C),
        Q("allergy.drug_exposure_route", "Drug Exposure Route", "coded", "drug-exposure-route", "그 약은 먹음, 정맥주사, 근육주사, 피하주사, 흡입, 피부 도포 중 어떤 경로로 사용했나요? 보기에 없으면 직접 입력해 주세요.", 142, [G["drug"]], C, allowed_values=["oral", "intravenous", "intramuscular", "subcutaneous", "inhaled", "topical", "other"]),
        Q("allergy.drug_exposure_count_before_onset", "Drug Exposure Count Before Onset", "integer", "drug-exposure-count", "첫 증상이 나타나기 전까지 그 약을 몇 번 사용했나요?", 141, [G["drug"]], C, minimum=1),
        Q("allergy.drug_exposure_duration_before_onset", "Drug Exposure Duration Before Onset", "date_or_period", "drug-exposure-duration", "첫 증상이 나타나기 전까지 그 약을 사용한 기간은 얼마였나요?", 140, [G["drug"]], C),
        Q("allergy.drug_last_dose_time", "Last Drug Dose Time", "date_or_period", "drug-last-dose-time", "반응 전 마지막으로 그 약을 사용한 날짜와 시각을 알려주세요.", 139, [G["drug"]], C),
        Q("allergy.drug_reaction_onset", "Drug Reaction Onset", "date_or_period", "drug-reaction-onset", "약물 반응이 시작된 날짜와 시각을 알려주세요.", 138, [G["drug"]], C),
        Q("allergy.drug_reaction_manifestations", "Drug Reaction Manifestations", "string", "drug-reaction-manifestations", "당시 나타난 징후와 증상을 구체적으로 알려주세요.", 137, [G["drug"]], C),
        Q("allergy.drug_reaction_severity", "Drug Reaction Event Severity", "coded", "drug-reaction-severity", "반응 전체의 심한 정도는 경도, 중등도, 중증 중 어디에 가깝나요? 판단하기 어려우면 모른다고 답해도 됩니다.", 136, [G["drug"]], C, allowed_values=["mild", "moderate", "severe"]),
        Q("allergy.drug_reaction_healthcare_required", "Healthcare Required for Drug Reaction", "coded", "drug-reaction-healthcare", "그 반응으로 받은 치료는 없음, 외래, 응급실, 입원 중 무엇이었나요? 보기에 없으면 직접 입력해 주세요.", 135, [G["drug"]], C, allowed_values=["none", "outpatient", "emergency_department", "hospital_admission", "other"]),
        Q("allergy.drug_stopped_after_reaction", "Drug Stopped After Reaction", "boolean", "drug-stopped", "반응이 생긴 뒤 의심되는 약을 중단했나요?", 134, [G["drug"]], D),
        Q("allergy.drug_outcome_after_stop", "Outcome After Drug Stop", "coded", "drug-outcome-after-stop", "의심 약을 중단한 뒤 증상은 회복, 호전, 변화 없음, 악화 중 어떻게 되었나요? 보기에 없으면 직접 입력해 주세요.", 133, [G["drug"]], D, allowed_values=["resolved", "improved", "unchanged", "worsened", "other"]),
        Q("allergy.drug_rechallenge_status", "Drug Rechallenge Status", "coded", "drug-rechallenge-status", "이후 같은 약이나 같은 계열 약을 다시 사용했나요? 사용하지 않음, 같은 약, 같은 계열 중 선택해 주세요.", 132, [G["drug"]], D, allowed_values=["not_rechallenged", "same_drug", "same_class"]),
        Q("allergy.drug_rechallenge_outcome", "Drug Rechallenge Outcome", "string", "drug-rechallenge-outcome", "다시 사용했다면 어떤 반응이 나타났나요? 다시 사용하지 않았다면 해당 없음이라고 답해 주세요.", 131, [G["drug"]], D),
        Q("allergy.drug_concurrent_medicines_and_alternative_causes", "Concurrent Drugs and Alternative Causes", "string", "drug-alternatives", "당시 함께 사용한 다른 약과 감염·음식·비약물 노출 등 다른 가능한 원인이 있었나요?", 130, [G["drug"]], D),
        Q("allergy.drug_status_and_avoid_list", "Drug Allergy Status and Avoid List", "string", "drug-status", "의무기록상 약물 알레르기 상태가 알레르기 있음·없음·확인 불가 중 무엇이며, 피하라고 들은 약이나 계열은 무엇인가요?", 129, [G["drug"]], R),
        Q("allergy.drug_specialist_confirmation_and_safe_alternatives", "Drug Allergy Confirmation and Alternatives", "string", "drug-confirmation", "전문의 검사로 알레르기 또는 비알레르기 반응이 확인됐나요? 안전하다고 확인된 대체약이 있나요?", 128, [G["drug"]], R),

        Q("allergy.sting_contact_identity_and_count", "Sting or Contact Exposure Detail", "string", "sting-identity", "벌레 종류·쏘인 횟수와 부위 또는 접촉 물질·접촉 부위를 알려주세요.", 130, [G["sting-contact"]], C),
        Q("allergy.local_reaction_size_and_progression", "Local Reaction Size and Progression", "string", "local-reaction", "국소 붉어짐·통증·부종의 대략적인 크기와 커지는 속도를 알려주세요.", 129, [G["sting-contact"]], C),
        Q("allergy.latex_adhesive_cosmetic_or_chemical_exposure", "Contact Allergen Context", "string", "contact-context", "라텍스·접착제·화장품·염색약·금속·세정제 등 새로 접촉한 물질이 있나요?", 128, [G["sting-contact"]], D),
    ]
    rules = [
        safety_rule(P, "airway", {"fact": "allergy.airway_compromise", "equals": True}, "emergency", 1000),
        safety_rule(P, "breathing", {"fact": "allergy.breathing_compromise", "equals": True}, "emergency", 1000),
        safety_rule(P, "circulation", {"fact": "allergy.circulatory_compromise", "equals": True}, "emergency", 1000),
        safety_rule(P, "collapse", {"fact": "allergy.altered_consciousness_or_collapse", "equals": True}, "emergency", 1000),
        safety_rule(P, "rapid-multisystem", {"fact": "allergy.rapid_multisystem_progression", "equals": True}, "emergency", 1000),
        safety_rule(P, "adrenaline-used", {"fact": "allergy.current_adrenaline_autoinjector_use", "equals": True}, "emergency", 1000),
        safety_rule(P, "asthma-failure", {"fact": "allergy.severe_asthma_or_rescue_failure", "equals": True}, "emergency", 990),
        safety_rule(P, "skin-detachment", {"fact": "allergy.skin_pain_blistering_or_detachment", "equals": True}, "emergency", 1000),
        safety_rule(P, "mucosal-eye", {"fact": "allergy.mucosal_erosion_or_eye_involvement", "equals": True}, "emergency", 990),
        safety_rule(P, "systemic-drug-rash", {"fact": "allergy.drug_rash_fever_facial_edema_or_organ_symptoms", "equals": True}, "urgent", 980),
        safety_rule(P, "gi-severe", {"fact": "allergy.repeated_vomiting_or_severe_abdominal_pain", "equals": True}, "urgent", 970),
        safety_rule(P, "injection-procedure", {"fact": "allergy.reaction_after_injection_or_procedure", "equals": True}, "urgent", 970),
    ]
    refresh = default_refresh()
    refresh.update({
        "last_assessed_at": "2026-08-10",
        "next_monitor_at": "2026-08-11",
        "next_full_review_at": "2027-02-06",
    })
    return {"id": "knowledge.generated.allergy-concern", "version": VERSION, "status": "research_only", "lifecycle_status": "draft", "review_status": "unreviewed", "clinical_use_status": "limited", "clinical_use_policy_ref": "policies/draft-clinical-use-boundary.json", "usage_modes": ["research_test", "simulation", "clinician_supervised_pilot"], "source_manifest": "source-manifest.primary-care-allergy-concern-research", "default_refresh": refresh, "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="allergy.primary_group", question_budget=67, source_refs=SOURCES)
    branches = {
        "acute_systemic": ["allergy.current_or_historical_episode", "allergy.onset_date_time_and_course", "allergy.circumstances_before_onset", "allergy.suspected_trigger_and_latency", "allergy.symptom_sequence_and_systems", "allergy.treatment_and_response"],
        "skin_angioedema": ["allergy.skin_lesion_type", "allergy.skin_distribution_duration_and_recurrence", "allergy.angioedema_sites", "allergy.skin_photograph_available"],
        "respiratory": ["allergy.nasal_and_ocular_features", "allergy.cough_wheeze_chest_tightness", "allergy.environmental_or_occupational_pattern"],
        "food": ["allergy.food_identity_amount_and_preparation", "allergy.food_cofactors", "allergy.food_reproducibility_and_current_tolerance"],
        "drug": ["allergy.drug_generic_name", "allergy.drug_brand_name", "allergy.drug_strength", "allergy.drug_formulation", "allergy.drug_indication", "allergy.drug_exposure_route", "allergy.drug_exposure_count_before_onset", "allergy.drug_exposure_duration_before_onset", "allergy.drug_last_dose_time", "allergy.drug_reaction_onset", "allergy.drug_reaction_manifestations", "allergy.drug_reaction_severity", "allergy.drug_reaction_healthcare_required", "allergy.drug_stopped_after_reaction", "allergy.drug_outcome_after_stop", "allergy.drug_rechallenge_status", "allergy.drug_rechallenge_outcome", "allergy.drug_concurrent_medicines_and_alternative_causes", "allergy.drug_status_and_avoid_list", "allergy.drug_specialist_confirmation_and_safe_alternatives"],
        "sting_contact": ["allergy.sting_contact_identity_and_count", "allergy.local_reaction_size_and_progression", "allergy.latex_adhesive_cosmetic_or_chemical_exposure"],
        "other_unclear": ["allergy.other_detail_or_patient_priority"],
    }
    policy["required_facts"]["routine"] = ["allergy.current_or_historical_episode", "allergy.onset_date_time_and_course", "allergy.circumstances_before_onset", "allergy.suspected_trigger_and_latency", "allergy.symptom_sequence_and_systems", "allergy.treatment_and_response", "allergy.prior_similar_reaction", "allergy.known_allergies_and_avoidance", "allergy.specialist_testing_and_emergency_plan", "allergy.asthma_cardiovascular_mast_cell_context", "allergy.current_medicines_and_risk_modifiers", "allergy.pregnancy_age_and_care_context", "allergy.other_detail_or_patient_priority"]
    policy["conditional_required_facts"] = [{"selector_fact": "allergy.primary_group", "cases": branches}]
    return policy


def source_docs():
    defs = [
        ("source.nice.ng258.anaphylaxis.2026", "NICE", "Anaphylaxis: assessment and referral after emergency treatment", "NG258; published-2026-05-27", "https://www.nice.org.uk/guidance/ng258/chapter/Recommendations", "nice_guidance", 7, ["Suspected anaphylaxis is rapidly developing airway, breathing or circulation compromise and may occur without typical skin features.", "Record acute features, onset time, symptom sequence and circumstances immediately before onset; this package performs interview screening, not diagnosis or treatment."]),
        ("source.nice.cg183.drug-allergy.2014", "NICE", "Drug allergy: diagnosis and management", "CG183; current-2026-08-10", "https://www.nice.org.uk/guidance/cg183/chapter/Recommendations", "nice_guidance", 7, ["Structured suspected-drug-allergy documentation includes generic and proprietary drug names, strength, formulation, indication, reaction, date and time, doses or days before onset, route and future avoid list.", "Drug allergy status is recorded separately as drug allergy, none known or unable to ascertain; severe immediate or severe non-immediate reactions warrant specialist assessment."]),
        ("source.nice.qs97.drug-allergy.2015", "NICE", "Drug allergy quality standard", "QS97; current-2026-08-10", "https://www.nice.org.uk/guidance/qs97/chapter/Quality-statements", "nice_guidance", 7, ["People with suspected drug allergy should have the reaction documented with the structured assessment guide.", "Structured information improves communication and includes drug identity, reaction, indication, timing, exposure count or duration, route and future avoidance information."]),
        ("source.hl7.fhir-r4.allergyintolerance.4.0.1", "HL7 International", "FHIR R4 AllergyIntolerance resource and reaction severity ValueSet", "FHIR-4.0.1; verified-2026-08-10", "https://hl7.org/fhir/R4/allergyintolerance.html", "fhir_specification", 30, ["AllergyIntolerance.reaction separates manifestation, onset, severity and exposure route.", "AllergyIntolerance.reaction.severity has a required binding to reaction-event-severity with mild, moderate and severe codes."]),
        ("source.nhs.anaphylaxis.2026", "NHS", "Anaphylaxis", "accessed-2026-07-15", "https://www.nhs.uk/conditions/anaphylaxis/", "public_health_guidance", 7, ["Airway swelling, breathing difficulty, circulatory symptoms or collapse after allergen exposure require emergency action.", "Common triggers include foods, medicines, insect stings and latex; the runtime must not delay emergency escalation for routine questions."]),
        ("source.nhs.stevens-johnson.2026", "NHS", "Stevens-Johnson syndrome", "accessed-2026-07-15", "https://www.nhs.uk/conditions/stevens-johnson-syndrome/", "public_health_guidance", 7, ["Painful spreading rash, blisters, skin detachment and mucosal or eye involvement after medicine exposure require emergency assessment."]),
        ("source.stom.allergy-concern.20260810", "Infoclinic", "STOM allergy terminology, FHIR ValueSet and MRCM summary", "SNOMEDCT-20260801; FHIR-4.0.1", "http://localhost:8088/fhir", "terminology_server", 30, ["FHIR lookup confirmed the active 20260801 SNOMED CT version for allergy-to-drug and the existing allergy focus concepts.", "FHIR ValueSet expansion confirmed the required reaction-event-severity codes mild, moderate and severe; dataAbsentReason remains outside this clinical answer set."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-08-10", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, days, assertions in defs]
    research = {"id": "source-manifest.primary-care-allergy-concern-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "lifecycle_status": "draft", "clinical_use_status": "limited", "artifacts": artifacts, "provenance": provenance([item[0] for item in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.allergy-concern", "generated_clinical_knowledge", "knowledge/generated/allergy/allergy-concern/allergy-concern.json", True), ("source.mapping.allergy-concern", "terminology_mapping", "mappings/terminology/snomed-mrcm-allergy-concern.json", False), ("source.external.allergy-concern", "external_source_manifest", "sources/manifests/primary-care-allergy-concern-research.json", False), ("source.policy.allergy-concern", "runtime_policy", "policies/primary-care-allergy-concern-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-allergy-concern", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        fact_id = rule["when"]["fact"]
        key = rule["id"].split("safety.")[1]
        level = rule["then"]["safety_level"]
        out[f"ALLERGY-{key.upper()}.json"] = {"id": f"ALLERGY-{key.upper()}", "simulation_language": "ko", "persona": {"age": 24 + index}, "initial_statement": {"ko": "알레르기 반응이 생긴 것 같아요."}, "hidden_state": {fact_id: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 32, "forbidden_assertions": ["diagnosis.anaphylaxis", "recommendation.self_administer_unprescribed_adrenaline", "diagnosis.drug_allergy_confirmed"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = sorted(set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["drug"]))
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}
    hidden = {}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        elif fact["value_type"] == "integer": hidden[fid] = {"value": 1}
        else: hidden[fid] = {"value": "없음"}
    hidden["allergy.primary_group"] = {"value": "drug"}
    declined = "allergy.drug_generic_name"
    hidden.pop(declined)
    out["ALLERGY-DRUG-DATA-ABSENT.json"] = {"id": "ALLERGY-DRUG-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 41}, "initial_statement": {"ko": "예전에 약을 먹고 발진이 있었는데 약 이름이 기억나지 않아요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 55, "forbidden_assertions": ["diagnosis.drug_allergy_confirmed", "recommendation.permanent_avoidance_without_review"]}, "provenance": provenance(["source.nice.cg183.drug-allergy.2014", "specifications/clinical-memory.md"])}
    structured = dict(hidden)
    structured.update({
        "allergy.primary_group": {"value": "drug"},
        "allergy.current_or_historical_episode": {"value": "historical"},
        "allergy.drug_generic_name": {"value": "amoxicillin"},
        "allergy.drug_strength": {"value": "500 mg"},
        "allergy.drug_formulation": {"value": "capsule"},
        "allergy.drug_indication": {"value": "dental infection"},
        "allergy.drug_exposure_route": {"value": "oral"},
        "allergy.drug_exposure_count_before_onset": {"value": 3},
        "allergy.drug_exposure_duration_before_onset": {"value": "1 day"},
        "allergy.drug_last_dose_time": {"value": "2 years ago, evening"},
        "allergy.drug_reaction_onset": {"value": "2 years ago, 2 hours after the dose"},
        "allergy.drug_reaction_manifestations": {"value": "generalized urticaria without breathing difficulty"},
        "allergy.drug_reaction_severity": {"value": "moderate"},
        "allergy.drug_reaction_healthcare_required": {"value": "outpatient"},
        "allergy.drug_stopped_after_reaction": {"value": True},
        "allergy.drug_outcome_after_stop": {"value": "improved"},
        "allergy.drug_rechallenge_status": {"value": "not_rechallenged"},
        "allergy.drug_rechallenge_outcome": {"value": "not applicable"},
    })
    structured.pop("allergy.drug_brand_name", None)
    out["ALLERGY-DRUG-STRUCTURED-HANDOFF-PROXY.json"] = {
        "id": "ALLERGY-DRUG-STRUCTURED-HANDOFF-PROXY",
        "simulation_language": "ko",
        "persona": {"age": 72, "proxy": "adult_child"},
        "initial_statement": {"ko": "어머니가 예전에 아목시실린을 드시고 두드러기가 생겼다고 해서 제가 대신 답할게요."},
        "clinician_submission": True,
        "hidden_state": structured,
        "response_behavior": {"allergy.drug_brand_name": {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {"allergy.drug_brand_name": "asked-unknown"},
            "expected_selected_facts_contains": ["allergy.drug_generic_name", "allergy.drug_exposure_route", "allergy.drug_reaction_onset", "allergy.drug_reaction_manifestations", "allergy.drug_reaction_severity", "allergy.drug_rechallenge_status"],
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 67,
            "forbidden_assertions": ["diagnosis.drug_allergy_confirmed", "recommendation.permanent_avoidance_without_review"]
        },
        "provenance": provenance(["source.nice.cg183.drug-allergy.2014", "source.nice.qs97.drug-allergy.2015", "source.hl7.fhir-r4.allergyintolerance.4.0.1"])
    }
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Allergic Reaction or Allergy Concern", intents=[("intent.characterize_symptom", "Characterize Allergic Reaction"), ("intent.screen_red_flags", "Screen Anaphylaxis and Severe Drug Reactions"), ("intent.differentiate_common_causes", "Assess Potential Trigger"), ("intent.risk_assessment", "Allergy Risk and Documentation Assessment")])
    primary, research = source_docs()
    concepts = [("419076005", "Allergic reaction (disorder)", 22), ("39579001", "Anaphylaxis (disorder)", 22), ("418038007", "Propensity to adverse reactions to substance (finding)", 20), ("416098002", "Allergy to drug (finding)", 20), ("91936005", "Allergy to penicillin (finding)", 20), ("41291007", "Angioedema (disorder)", 22), ("126485001", "Urticaria (disorder)", 22), ("271807003", "Eruption of skin (disorder)", 22), ("73442001", "Stevens-Johnson syndrome (disorder)", 22), ("735173007", "Shock due to anaphylaxis (disorder)", 22)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "lifecycle_status": "draft", "review_status": "unreviewed", "clinical_use_status": "limited", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260801", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["246112005", "263502005", "246090004"], "validation": {"method": "build_time_live_fhir_lookup_valueset_expand_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.allergy-concern.20260810", "source.hl7.fhir-r4.allergyintolerance.4.0.1"])}
    documents = [("knowledge/base/primary-care-allergy-concern.json", graph), ("rules/base/primary-care-allergy-concern.json", rules), ("knowledge/generated/allergy/allergy-concern/allergy-concern.json", f), ("mappings/terminology/snomed-mrcm-allergy-concern.json", mapping), ("sources/manifests/primary-care-allergy-concern.json", primary), ("sources/manifests/primary-care-allergy-concern-research.json", research), ("policies/primary-care-allergy-concern-completion.json", completion(f))]
    for path, document in documents: write_json(path, document)
    for name, case in cases(f).items(): write_json("simulation/patients/allergy/allergy-concern/" + name, case)


if __name__ == "__main__": main()
