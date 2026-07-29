#!/usr/bin/env python3
"""Materialize an unreviewed pre-visit immunization consultation package."""
from profile_support import *


P, RFE = "immunization-consultation", "rfe.immunization_consultation"
M, SN = "mapping.snomed-mrcm.immunization-consultation", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-29T00:00:00Z"
SOURCES = [
    "source.kdca.immunization-standard.2026-1",
    "source.kdca.immunization-guideline.2026",
    "source.kdca.immunization-precautions.20260105",
    "source.hl7.fhir-r4.immunization",
    "source.hl7.fhir-r4.immunization-recommendation",
    "source.stom.immunization.20260729",
]
G = {
    key: f"group.immunization.{key}"
    for key in (
        "goal", "safety", "record", "vaccine", "contraindication",
        "timing", "special-population", "post-vaccine", "handoff",
    )
}
C = ["intent.immunization_history_review"]
S = ["intent.immunization_safety_screening"]
R = ["intent.immunization_readiness_handoff"]


def Q(fact_id, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(
        P, fact_id, display, value_type, key, wording, score, key, groups,
        intents=intents, **kwargs,
    )


def fragment():
    refresh = default_refresh()
    refresh.update({
        "last_assessed_at": "2026-07-29",
        "next_monitor_at": "2026-07-30",
        "next_full_review_at": "2027-01-25",
    })
    entries = [
        Q(
            "immunization.primary_group", "Immunization Consultation Type", "coded",
            "primary-group",
            "이번 방문은 예정된 예방접종 상담, 접종기록 확인, 누락 접종 상담, 여행·직업·노출 관련 상담, 접종 후 이상반응 상담 중 무엇에 가깝나요?",
            240, [G["goal"]], C,
            allowed_values=[
                "planned_vaccination", "record_review", "catch_up_review",
                "travel_occupation_or_exposure", "post_vaccination_concern",
                "other_unclear",
            ],
        ),
        Q(
            "immunization.current_breathing_difficulty_after_vaccine",
            "Current Breathing Difficulty after Vaccine", "boolean", "current-breathing-warning",
            "접종 후 현재 숨쉬기 어려운가요?",
            243, [G["safety"], G["post-vaccine"]], S, safety_relevant=True,
        ),
        Q(
            "immunization.current_throat_or_tongue_swelling_after_vaccine",
            "Current Throat or Tongue Swelling after Vaccine", "boolean", "current-airway-swelling-warning",
            "접종 후 현재 목 또는 혀가 붓는 느낌이 있나요?",
            242, [G["safety"], G["post-vaccine"]], S, safety_relevant=True,
        ),
        Q(
            "immunization.current_collapse_or_near_syncope_after_vaccine",
            "Current Collapse or Near-syncope after Vaccine", "boolean", "current-collapse-warning",
            "접종 후 현재 쓰러졌거나 곧 쓰러질 것 같은 상태인가요?",
            241, [G["safety"], G["post-vaccine"]], S, safety_relevant=True,
        ),
        Q(
            "immunization.current_altered_responsiveness_after_vaccine",
            "Current Altered Responsiveness after Vaccine", "boolean", "current-responsiveness-warning",
            "접종 후 현재 깨우기 어렵거나 평소처럼 반응하지 않나요?",
            240, [G["safety"], G["post-vaccine"]], S, safety_relevant=True,
        ),
        Q(
            "immunization.current_seizure_after_vaccine",
            "Current Seizure after Vaccine", "boolean", "current-seizure-warning",
            "접종 후 현재 경련 중인가요?",
            239, [G["safety"], G["post-vaccine"]], S, safety_relevant=True,
        ),
        Q(
            "immunization.current_severe_or_rapidly_worsening_symptom",
            "Current Severe or Rapidly Worsening Symptom", "boolean", "current-severe-warning",
            "접종 후 고열·심한 통증·전신 발진 등 새로운 증상이 심하거나 빠르게 악화하고 있나요?",
            237, [G["safety"], G["post-vaccine"]], S, safety_relevant=True,
        ),
        Q(
            "immunization.child_difficult_to_wake_after_vaccine",
            "Child Difficult to Wake after Vaccine", "boolean", "child-wake-warning",
            "접종 후 아이를 평소처럼 깨우기 어려운가요?",
            236, [G["safety"], G["post-vaccine"]], S, safety_relevant=True,
        ),
        Q(
            "immunization.child_unable_to_feed_after_vaccine",
            "Child Unable to Feed after Vaccine", "boolean", "child-feeding-warning",
            "접종 후 아이가 평소처럼 먹거나 마시지 못하나요?",
            235, [G["safety"], G["post-vaccine"]], S, safety_relevant=True,
        ),
        Q(
            "immunization.information_source", "Immunization Information Source", "coded",
            "information-source",
            "접종 정보는 예방접종도우미·의료기관 전산기록, 수첩·증명서, 보호자 기억, 본인 기억 중 어디에서 확인했나요?",
            220, [G["record"]], C,
            allowed_values=[
                "kdca_or_clinical_registry", "written_record", "caregiver_recall",
                "self_recall", "multiple_sources", "no_source", "unknown",
            ],
        ),
        Q(
            "immunization.record_completeness", "Immunization Record Completeness", "coded",
            "record-completeness",
            "현재 확인 가능한 접종기록은 전체 기록, 일부 기록, 기록 없음 중 어느 상태인가요?",
            219, [G["record"]], C,
            allowed_values=["complete", "partial", "none", "unknown"],
        ),
        Q(
            "immunization.record_conflict", "Immunization Record Conflict", "boolean",
            "record-conflict",
            "전산기록·수첩·본인 또는 보호자 기억 사이에 서로 맞지 않는 접종 정보가 있나요?",
            218, [G["record"]], C,
        ),
        Q(
            "immunization.record_conflict_detail", "Immunization Record Conflict Detail", "string",
            "record-conflict-detail",
            "서로 맞지 않는 접종 정보가 있다면 어떤 백신의 어떤 내용인지 알려주세요.",
            217, [G["record"], G["handoff"]], C,
        ),
        Q(
            "patient.age_years", "Age in Years", "integer", "age-years",
            "현재 만 나이는 몇 세인가요? 숫자로 알려주세요.",
            216, [G["special-population"]], R, reuse_existing=True,
        ),
        Q(
            "immunization.current_jurisdiction", "Current Immunization Jurisdiction", "string",
            "jurisdiction",
            "접종 일정과 지원 기준을 확인할 국가 또는 지역은 어디인가요?",
            215, [G["goal"], G["handoff"]], R,
        ),
        Q(
            "immunization.consultation_goal", "Patient Immunization Goal", "string",
            "consultation-goal",
            "이번 상담에서 의료진에게 가장 확인하거나 도움받고 싶은 점은 무엇인가요?",
            214, [G["goal"], G["handoff"]], R,
        ),
        Q(
            "immunization.target_vaccine", "Target Vaccine", "coded_or_string",
            "target-vaccine",
            "접종하거나 확인하려는 백신 이름을 알고 있다면 알려주세요.",
            210, [G["vaccine"]], R,
        ),
        Q(
            "immunization.target_disease", "Target Vaccine-preventable Disease", "coded_or_string",
            "target-disease",
            "예방하려는 감염병이나 접종 목적을 알고 있다면 알려주세요.",
            209, [G["vaccine"]], R,
        ),
        Q(
            "immunization.previous_dose_count", "Previous Dose Count", "integer",
            "previous-dose-count",
            "해당 백신을 이전에 몇 차례 접종했는지 숫자로 알려주세요.",
            208, [G["record"], G["vaccine"]], C,
        ),
        Q(
            "immunization.last_dose_date", "Last Dose Date", "date_or_period",
            "last-dose-date",
            "해당 백신의 가장 최근 접종 시기를 알려주세요.",
            207, [G["record"], G["timing"]], C,
        ),
        Q(
            "immunization.last_dose_product", "Last Dose Product", "coded_or_string",
            "last-dose-product",
            "가장 최근에 접종한 백신의 제품명 또는 종류를 알고 있다면 알려주세요.",
            206, [G["record"], G["vaccine"]], C,
        ),
        Q(
            "immunization.previous_target_infection", "Previous Target Infection", "boolean",
            "previous-target-infection",
            "예방하려는 감염병에 과거 확진되거나 의료진에게 감염되었다는 설명을 들은 적이 있나요?",
            205, [G["record"], G["vaccine"]], R,
        ),
        Q(
            "immunization.previous_target_infection_date", "Previous Target Infection Date", "date_or_period",
            "previous-target-infection-date",
            "그 감염의 진단 또는 발생 시기를 알려주세요.",
            204, [G["record"], G["timing"]], R,
        ),
        Q(
            "immunization.prior_severe_allergic_reaction", "Prior Severe Vaccine Allergic Reaction", "boolean",
            "prior-severe-allergy",
            "이전에 백신 접종 후 아나필락시스와 같은 심한 알레르기 반응이 있었나요?",
            200, [G["contraindication"]], R,
        ),
        Q(
            "immunization.prior_reaction_vaccine", "Vaccine Associated with Prior Reaction", "coded_or_string",
            "prior-reaction-vaccine",
            "심한 반응과 관련된 백신 이름 또는 제품을 알려주세요.",
            199, [G["contraindication"], G["vaccine"]], R,
        ),
        Q(
            "immunization.prior_reaction_manifestation", "Prior Vaccine Reaction Manifestation", "string",
            "prior-reaction-manifestation",
            "당시 어떤 증상이나 반응이 나타났는지 알려주세요.",
            198, [G["contraindication"]], R,
        ),
        Q(
            "immunization.prior_reaction_onset", "Prior Vaccine Reaction Onset", "date_or_period",
            "prior-reaction-onset",
            "접종 후 반응이 시작되기까지 얼마나 걸렸나요?",
            197, [G["contraindication"], G["timing"]], R,
        ),
        Q(
            "immunization.known_component_allergy", "Known Vaccine Component Allergy", "boolean",
            "component-allergy",
            "백신 성분에 알레르기가 있다고 의료진에게 진단받은 적이 있나요?",
            196, [G["contraindication"]], R,
        ),
        Q(
            "immunization.known_component_allergy_detail", "Vaccine Component Allergy Detail", "coded_or_string",
            "component-allergy-detail",
            "진단받은 백신 성분과 반응을 알고 있다면 알려주세요.",
            195, [G["contraindication"]], R,
        ),
        Q(
            "immunization.pertussis_vaccine_encephalopathy_history", "Encephalopathy after Pertussis-containing Vaccine", "boolean",
            "pertussis-encephalopathy",
            "백일해 성분이 포함된 백신 접종 후 7일 이내 원인을 알 수 없는 뇌증을 진단받은 적이 있나요?",
            194, [G["contraindication"], G["special-population"]], R,
        ),
        Q(
            "immunization.scid_history", "Severe Combined Immunodeficiency History", "boolean",
            "scid-history",
            "중증복합면역결핍을 진단받은 적이 있나요?",
            193, [G["contraindication"], G["special-population"]], R,
        ),
        Q(
            "immunization.intussusception_history", "Intussusception History", "boolean",
            "intussusception-history",
            "장중첩증 또는 장겹침증을 진단받은 적이 있나요?",
            192, [G["contraindication"], G["special-population"]], R,
        ),
        Q(
            "immunization.pregnancy_status", "Pregnancy Status", "coded",
            "pregnancy-status",
            "현재 임신 중인가요?",
            191, [G["contraindication"], G["special-population"]], R,
            allowed_values=["pregnant", "not_pregnant", "not_applicable", "unknown"],
        ),
        Q(
            "immunization.breastfeeding_status", "Breastfeeding Status", "boolean",
            "breastfeeding-status",
            "현재 모유수유 중인가요?",
            190, [G["special-population"]], R,
        ),
        Q(
            "immunization.immunocompromised_status", "Immunocompromised Status", "boolean",
            "immunocompromised-status",
            "면역저하 질환이나 장기이식 등으로 면역기능이 저하되었다는 설명을 들은 적이 있나요?",
            189, [G["contraindication"], G["special-population"]], R,
        ),
        Q(
            "immunization.immunocompromised_condition", "Immunocompromising Condition", "string",
            "immunocompromised-condition",
            "면역기능에 영향을 주는 진단이나 상태를 알려주세요.",
            188, [G["contraindication"], G["special-population"]], R,
        ),
        Q(
            "immunization.immunosuppressive_treatment", "Immunosuppressive Treatment", "boolean",
            "immunosuppressive-treatment",
            "현재 항암치료, 고용량 스테로이드, 생물학적 제제 또는 다른 면역억제 치료를 받고 있나요?",
            187, [G["contraindication"], G["special-population"]], R,
        ),
        Q(
            "immunization.immunosuppressive_treatment_name", "Immunosuppressive Treatment Name", "coded_or_string",
            "immunosuppressive-treatment-name",
            "면역에 영향을 주는 치료제나 치료 이름을 알려주세요.",
            186, [G["contraindication"], G["special-population"]], R,
        ),
        Q(
            "immunization.immunosuppressive_treatment_timing", "Immunosuppressive Treatment Timing", "date_or_period",
            "immunosuppressive-treatment-timing",
            "그 치료의 최근 투여일 또는 치료 기간을 알려주세요.",
            185, [G["contraindication"], G["timing"]], R,
        ),
        Q(
            "immunization.current_moderate_or_severe_acute_illness", "Current Moderate or Severe Acute Illness", "boolean",
            "acute-illness",
            "현재 일상생활이 어려울 정도의 중등도 또는 중증 급성 질환이 있나요?",
            184, [G["contraindication"], G["special-population"]], R,
        ),
        Q(
            "immunization.current_temperature", "Current Temperature", "string",
            "current-temperature",
            "최근 체온을 측정했다면 수치, 단위, 측정 시각과 방법을 알려주세요.",
            183, [G["contraindication"], G["timing"]], R,
        ),
        Q(
            "immunization.recent_antibody_blood_product", "Recent Antibody-containing Blood Product", "boolean",
            "recent-blood-product",
            "최근 면역글로불린, 수혈 또는 항체가 포함된 혈액제제를 투여받았나요?",
            182, [G["contraindication"], G["timing"]], R,
        ),
        Q(
            "immunization.recent_antibody_blood_product_type", "Recent Blood Product Type", "coded_or_string",
            "recent-blood-product-type",
            "투여받은 면역글로불린 또는 혈액제제의 종류를 알려주세요.",
            181, [G["contraindication"]], R,
        ),
        Q(
            "immunization.recent_antibody_blood_product_date", "Recent Blood Product Date", "date_or_period",
            "recent-blood-product-date",
            "면역글로불린 또는 혈액제제를 투여받은 시기를 알려주세요.",
            180, [G["contraindication"], G["timing"]], R,
        ),
        Q(
            "immunization.recent_other_vaccine", "Recent Other Vaccine", "boolean",
            "recent-other-vaccine",
            "최근 다른 예방접종을 받았나요?",
            179, [G["timing"]], R,
        ),
        Q(
            "immunization.recent_other_vaccine_name", "Recent Other Vaccine Name", "coded_or_string",
            "recent-other-vaccine-name",
            "최근 접종한 다른 백신의 이름 또는 종류를 알려주세요.",
            178, [G["timing"], G["vaccine"]], R,
        ),
        Q(
            "immunization.recent_other_vaccine_date", "Recent Other Vaccine Date", "date_or_period",
            "recent-other-vaccine-date",
            "최근 다른 백신을 접종한 시기를 알려주세요.",
            177, [G["timing"]], R,
        ),
        Q(
            "immunization.bleeding_risk", "Bleeding Risk", "boolean",
            "bleeding-risk",
            "출혈질환이 있거나 항응고제·항혈소판제를 복용하고 있나요?",
            176, [G["special-population"]], R,
        ),
        Q(
            "immunization.injection_syncope_history", "Injection-associated Syncope History", "boolean",
            "injection-syncope",
            "주사나 채혈 전후에 실신하거나 거의 쓰러진 적이 있나요?",
            175, [G["special-population"]], R,
        ),
        Q(
            "immunization.travel_destination", "Travel Destination", "string",
            "travel-destination",
            "여행 관련 상담이라면 방문할 국가 또는 지역을 알려주세요.",
            170, [G["special-population"], G["handoff"]], R,
        ),
        Q(
            "immunization.travel_departure_date", "Travel Departure Date", "date_or_period",
            "travel-departure-date",
            "여행 출발 예정일을 알려주세요.",
            169, [G["special-population"], G["timing"]], R,
        ),
        Q(
            "immunization.occupation_or_exposure", "Occupation or Exposure Requiring Review", "string",
            "occupation-exposure",
            "직업, 학교, 군 복무, 돌봄, 실험실 또는 감염 노출 때문에 접종 상담이 필요하다면 상황을 알려주세요.",
            168, [G["special-population"], G["handoff"]], R,
        ),
        Q(
            "immunization.post_vaccine_product", "Vaccine Product before Current Concern", "coded_or_string",
            "post-vaccine-product",
            "현재 이상반응 상담과 관련된 백신 이름 또는 제품을 알려주세요.",
            160, [G["post-vaccine"], G["vaccine"]], C,
        ),
        Q(
            "immunization.post_vaccine_date", "Vaccination Date before Current Concern", "date_or_period",
            "post-vaccine-date",
            "해당 백신을 접종한 날짜와 가능하면 시각을 알려주세요.",
            159, [G["post-vaccine"], G["timing"]], C,
        ),
        Q(
            "immunization.post_vaccine_symptom", "Post-vaccine Symptom", "string",
            "post-vaccine-symptom",
            "접종 후 새로 나타난 증상을 환자 또는 보호자의 표현으로 알려주세요.",
            158, [G["post-vaccine"]], C,
        ),
        Q(
            "immunization.post_vaccine_symptom_onset", "Post-vaccine Symptom Onset", "date_or_period",
            "post-vaccine-symptom-onset",
            "접종 후 증상이 시작되기까지 얼마나 걸렸나요?",
            157, [G["post-vaccine"], G["timing"]], C,
        ),
        Q(
            "immunization.post_vaccine_symptom_course", "Post-vaccine Symptom Course", "coded",
            "post-vaccine-symptom-course",
            "증상은 호전, 변화 없음, 악화, 반복 중 어느 양상인가요?",
            156, [G["post-vaccine"]], C,
            allowed_values=["improving", "unchanged", "worsening", "recurrent", "unknown"],
        ),
        Q(
            "immunization.post_vaccine_prior_assessment", "Prior Assessment for Post-vaccine Concern", "string",
            "post-vaccine-prior-assessment",
            "이 증상으로 이미 받은 진찰·검사와 의료진의 설명이 있다면 알려주세요.",
            155, [G["post-vaccine"], G["handoff"]], R,
        ),
        Q(
            "immunization.post_vaccine_treatment_response", "Treatment Response for Post-vaccine Concern", "string",
            "post-vaccine-treatment-response",
            "접종 후 증상에 대해 시행한 처치나 복용한 약과 그 반응을 알려주세요.",
            154, [G["post-vaccine"], G["handoff"]], R,
        ),
        Q(
            "immunization.accessibility_or_support_need", "Accessibility or Support Need", "string",
            "accessibility-support",
            "접종과 설명을 위해 통역, 보호자 동행, 청각·시각·인지 지원 또는 주사 불안 지원이 필요한가요?",
            90, [G["handoff"]], R,
        ),
        Q(
            "immunization.patient_question_or_concern", "Patient Question or Concern", "string",
            "patient-question",
            "의료진에게 꼭 전달할 걱정, 질문 또는 추가 의견을 알려주세요.",
            80, [G["goal"], G["handoff"]], R,
        ),
    ]
    safety = [
        ("current-breathing-warning", "immunization.current_breathing_difficulty_after_vaccine", "emergency"),
        ("current-airway-swelling-warning", "immunization.current_throat_or_tongue_swelling_after_vaccine", "emergency"),
        ("current-collapse-warning", "immunization.current_collapse_or_near_syncope_after_vaccine", "emergency"),
        ("current-responsiveness-warning", "immunization.current_altered_responsiveness_after_vaccine", "emergency"),
        ("current-seizure-warning", "immunization.current_seizure_after_vaccine", "emergency"),
        ("current-severe-warning", "immunization.current_severe_or_rapidly_worsening_symptom", "urgent"),
        ("child-wake-warning", "immunization.child_difficult_to_wake_after_vaccine", "emergency"),
        ("child-feeding-warning", "immunization.child_unable_to_feed_after_vaccine", "emergency"),
    ]
    return {
        "id": "knowledge.generated.immunization-consultation",
        "version": VERSION,
        "status": "research_only",
        "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-immunization-consultation-research",
        "default_refresh": refresh,
        "extra_nodes": [
            {"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]}
            for value in G.values()
        ],
        "group_hypothesis_edges": [],
        "safety_rules": [
            safety_rule(P, key, {"fact": fact_id, "equals": True}, level, 1000 if level == "emergency" else 990)
            for key, fact_id, level in safety
        ],
        "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(fragment_document):
    policy = completion_policy(
        prefix=P,
        fragment=fragment_document,
        presentation_fact="immunization.primary_group",
        question_budget=55,
        source_refs=SOURCES,
    )
    common = [
        "immunization.information_source",
        "immunization.record_completeness",
        "immunization.record_conflict",
        "patient.age_years",
        "immunization.current_jurisdiction",
        "immunization.consultation_goal",
        "immunization.prior_severe_allergic_reaction",
        "immunization.known_component_allergy",
        "immunization.pregnancy_status",
        "immunization.immunocompromised_status",
        "immunization.immunosuppressive_treatment",
        "immunization.current_moderate_or_severe_acute_illness",
        "immunization.recent_antibody_blood_product",
        "immunization.recent_other_vaccine",
        "immunization.bleeding_risk",
        "immunization.injection_syncope_history",
        "immunization.accessibility_or_support_need",
        "immunization.patient_question_or_concern",
    ]
    cases = {
        "planned_vaccination": [
            "immunization.target_vaccine", "immunization.target_disease",
            "immunization.previous_dose_count", "immunization.last_dose_date",
            "immunization.last_dose_product", "immunization.previous_target_infection",
            "immunization.pertussis_vaccine_encephalopathy_history",
            "immunization.scid_history", "immunization.intussusception_history",
            "immunization.breastfeeding_status",
        ],
        "record_review": [
            "immunization.record_conflict_detail", "immunization.target_vaccine",
            "immunization.previous_dose_count", "immunization.last_dose_date",
            "immunization.last_dose_product", "immunization.previous_target_infection",
        ],
        "catch_up_review": [
            "immunization.record_conflict_detail", "immunization.target_vaccine",
            "immunization.previous_dose_count", "immunization.last_dose_date",
            "immunization.last_dose_product", "immunization.previous_target_infection",
            "immunization.pertussis_vaccine_encephalopathy_history",
            "immunization.scid_history", "immunization.intussusception_history",
        ],
        "travel_occupation_or_exposure": [
            "immunization.target_vaccine", "immunization.target_disease",
            "immunization.previous_dose_count", "immunization.last_dose_date",
            "immunization.travel_destination", "immunization.travel_departure_date",
            "immunization.occupation_or_exposure",
        ],
        "post_vaccination_concern": [
            "immunization.current_breathing_difficulty_after_vaccine",
            "immunization.current_throat_or_tongue_swelling_after_vaccine",
            "immunization.current_collapse_or_near_syncope_after_vaccine",
            "immunization.current_altered_responsiveness_after_vaccine",
            "immunization.current_seizure_after_vaccine",
            "immunization.current_severe_or_rapidly_worsening_symptom",
            "immunization.child_difficult_to_wake_after_vaccine",
            "immunization.child_unable_to_feed_after_vaccine",
            "immunization.post_vaccine_product", "immunization.post_vaccine_date",
            "immunization.post_vaccine_symptom", "immunization.post_vaccine_symptom_onset",
            "immunization.post_vaccine_symptom_course",
            "immunization.post_vaccine_prior_assessment",
            "immunization.post_vaccine_treatment_response",
        ],
        "other_unclear": ["immunization.patient_question_or_concern"],
    }
    policy["required_facts"]["always"] = ["immunization.primary_group"]
    policy["required_facts"]["routine"] = common
    policy["conditional_required_facts"] = [
        {"selector_fact": "immunization.primary_group", "cases": cases}
    ]
    policy["clinical_boundary"] = {
        "vaccine_due_status_inferred": False,
        "contraindication_or_eligibility_determined": False,
        "requires_current_schedule_age_risk_jurisdiction_and_clinician_review": True,
    }
    return policy


def source_documents():
    definitions = [
        (
            "source.kdca.immunization-standard.2026-1", "KDCA",
            "예방접종의 실시기준 및 방법 (질병관리청고시 제2026-1호)", "2026-1",
            "https://www.kdca.go.kr/bbs/kdca/51/304475/download.do",
            "public_health_guidance",
            [
                "The current Korean national standard and schedule are jurisdiction- and date-dependent.",
                "The interview must collect vaccine, dose and timing facts without independently inferring due status.",
            ],
        ),
        (
            "source.kdca.immunization-guideline.2026", "KDCA",
            "2026년 국가예방접종 지침", "2026",
            "https://www.kdca.go.kr/bbs/kdca/55/305179/download.do",
            "public_health_guidance",
            [
                "Pre-vaccination workflow includes identity, registry history, screening, consent and adverse-event information.",
                "Vaccination history and next schedule must be documented and handed off to the administering clinician.",
            ],
        ),
        (
            "source.kdca.immunization-precautions.20260105", "KDCA",
            "예방접종 주의사항 및 금기사항", "reviewed-2026-01-05",
            "https://nip.kdca.go.kr/irhp/infm/goVcntInfo.do?menuCd=114&menuLv=1",
            "public_health_guidance",
            [
                "Prior anaphylaxis to a vaccine or component, pertussis-vaccine-associated unexplained encephalopathy, SCID and intussusception are vaccine-specific history elements requiring clinician review.",
                "Pregnancy, immunocompromise, moderate or severe acute illness and recent antibody-containing blood products can affect vaccine-specific timing or precautions.",
                "Mild illness, breastfeeding and prematurity are not automatically treated as contraindications by this interview.",
            ],
        ),
        (
            "source.hl7.fhir-r4.immunization", "HL7",
            "FHIR R4 Immunization Resource", "4.0.1",
            "https://hl7.org/fhir/R4/immunization.html",
            "interoperability_standard",
            [
                "Immunization records vaccine code, occurrence, status, primary source, lot and protocol details.",
                "FHIR element bindings guide export representation but do not determine clinical eligibility.",
            ],
        ),
        (
            "source.hl7.fhir-r4.immunization-recommendation", "HL7",
            "FHIR R4 ImmunizationRecommendation Resource", "4.0.1",
            "https://hl7.org/fhir/R4/immunizationrecommendation.html",
            "interoperability_standard",
            [
                "Forecast status and recommendation reason are separate from raw vaccination history.",
                "This package does not emit a recommendation without a current schedule and clinical review.",
            ],
        ),
        (
            "source.stom.immunization.20260729", "Infoclinic",
            "STOM immunization terminology lookup", "SNOMEDCT-20260701_LOINC-2.82",
            "http://localhost:8088/fhir", "terminology_server",
            [
                "FHIR lookup verified SNOMED CT 33879002, 171044003, 293104008 and 77386006 as active concepts.",
                "FHIR lookup verified LOINC 11369-6 History of Immunization note.",
                "Terminology supports representation only and does not determine vaccine eligibility, contraindication or urgency.",
            ],
        ),
    ]
    artifacts = []
    for identifier, publisher, title, version, url, profile, assertions in definitions:
        artifacts.append({
            "id": identifier,
            "kind": "terminology_lookup_summary" if profile == "terminology_server" else "official_guidance_metadata",
            "publisher": publisher,
            "title": title,
            "version": version,
            "url": url,
            "language": "ko" if publisher == "KDCA" else "en",
            "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached",
            "license_status": "restricted" if publisher == "Infoclinic" else "official_link_only",
            "complete": False,
            "monitor_profile": profile,
            "last_monitored_at": "2026-07-29",
            "monitor_result": "current_official_source_confirmed",
            "assertions": assertions,
        })
    research = {
        "id": "source-manifest.primary-care-immunization-consultation-research",
        "version": VERSION,
        "acquired_at": ACQUIRED_AT,
        "status": "research_only",
        "artifacts": artifacts,
        "provenance": provenance([item[0] for item in definitions]),
    }
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.immunization-consultation", "generated_clinical_knowledge", "knowledge/generated/preventive/immunization-consultation/immunization-consultation.json", True),
        ("source.mapping.immunization-consultation", "terminology_mapping", "mappings/terminology/snomed-mrcm-immunization-consultation.json", False),
        ("source.external.immunization-consultation", "external_source_manifest", "sources/manifests/primary-care-immunization-consultation-research.json", False),
        ("source.policy.immunization-consultation", "runtime_policy", "policies/primary-care-immunization-consultation-completion.json", True),
    ]
    primary = {
        "id": "source-manifest.primary-care-immunization-consultation",
        "version": VERSION,
        "acquired_at": ACQUIRED_AT,
        "artifacts": [
            {
                "id": identifier, "kind": kind, "publisher": "clinical-interview-platform",
                "version": VERSION, "language": "en", "path": path,
                "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown",
                "complete": complete,
            }
            for identifier, kind, path, complete in paths
        ],
        "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"]),
    }
    return primary, research


def simulations(fragment_document):
    output = {}
    for index, rule in enumerate(fragment_document["safety_rules"]):
        fact_id = rule["when"]["fact"]
        level = rule["then"]["safety_level"]
        key = rule["id"].split("safety.")[1]
        output[f"IMMUNIZATION-{key.upper()}.json"] = {
            "id": f"IMMUNIZATION-{key.upper()}",
            "simulation_language": "ko",
            "persona": {"age": 2 + index * 19},
            "initial_statement": {"ko": "예방접종 후 상태가 걱정됩니다."},
            "hidden_state": {
                "immunization.primary_group": {"value": "post_vaccination_concern"},
                fact_id: {"value": True},
            },
            "expected": {
                "expected_safety_level": level,
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [rule["id"]],
                "expected_max_turns": 20,
                "forbidden_assertions": [
                    "diagnosis.vaccine_anaphylaxis_confirmed",
                    "recommendation.vaccine_due",
                    "recommendation.vaccine_contraindicated",
                ],
            },
            "provenance": provenance(SOURCES),
        }
    output["IMMUNIZATION-PLANNED-RECORD-PARTIAL.json"] = {
        "id": "IMMUNIZATION-PLANNED-RECORD-PARTIAL",
        "simulation_language": "ko",
        "persona": {"age": 38},
        "initial_statement": {"ko": "접종 기록이 일부만 있어 예정 백신을 상담하려고 합니다."},
        "hidden_state": _routine_hidden(fragment_document, "planned_vaccination", {
            "immunization.record_completeness": "partial",
            "immunization.information_source": "multiple_sources",
            "immunization.target_vaccine": "백신 이름은 확인 필요",
        }),
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 65,
            "forbidden_assertions": ["recommendation.vaccine_due", "recommendation.vaccine_contraindicated"],
        },
        "provenance": provenance(SOURCES),
    }
    output["IMMUNIZATION-CHILD-PROXY-CATCH-UP-DATA-ABSENT.json"] = {
        "id": "IMMUNIZATION-CHILD-PROXY-CATCH-UP-DATA-ABSENT",
        "simulation_language": "ko",
        "persona": {"age": 6},
        "encounter_context": {
            "care_setting": "primary_care", "encounter_type": "new_encounter",
            "interview_initiator": "caregiver", "interview_mode": "telephone",
            "available_information": ["partial_immunization_record"],
            "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
        },
        "initial_statement": {"ko": "아이의 누락 접종을 확인하고 싶지만 수첩이 없습니다."},
        "hidden_state": _routine_hidden(fragment_document, "catch_up_review", {
            "immunization.record_completeness": "none",
            "immunization.information_source": "caregiver_recall",
        }, omit={"immunization.last_dose_date", "immunization.previous_dose_count"}),
        "response_behavior": {
            "immunization.last_dose_date": {"dataAbsentReason": "asked-unknown"},
            "immunization.previous_dose_count": {"dataAbsentReason": "asked-unknown"},
        },
        "expected": {
            "expected_data_absent_reasons": {
                "immunization.last_dose_date": "asked-unknown",
                "immunization.previous_dose_count": "asked-unknown",
            },
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 65,
            "forbidden_assertions": ["recommendation.catch_up_schedule", "recommendation.vaccine_due"],
        },
        "provenance": provenance(SOURCES),
    }
    output["IMMUNIZATION-TRAVEL-MULTI-RFE-TERMINOLOGY-OFFLINE.json"] = {
        "id": "IMMUNIZATION-TRAVEL-MULTI-RFE-TERMINOLOGY-OFFLINE",
        "simulation_language": "ko",
        "persona": {"age": 29},
        "encounter_context": {
            "care_setting": "primary_care", "encounter_type": "new_encounter",
            "interview_initiator": "patient", "interview_mode": "chat",
            "available_information": ["no_previous_records"],
            "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
        },
        "operational_state": {"terminology_adapter": "unavailable"},
        "initial_statement": {"ko": "해외 출국 전 예방접종 상담과 복용약 검토가 필요합니다."},
        "hidden_state": _routine_hidden(fragment_document, "travel_occupation_or_exposure", {
            "immunization.travel_destination": "합성 해외 지역",
            "immunization.travel_departure_date": "6주 후",
            "immunization.patient_question_or_concern": "복용약 검토도 별도 방문 이유로 전달",
        }),
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 65,
            "forbidden_assertions": ["recommendation.travel_vaccine", "recommendation.vaccine_due"],
        },
        "provenance": provenance(SOURCES),
    }
    return output


def _routine_hidden(fragment_document, branch, overrides=None, omit=None):
    policy = completion(fragment_document)
    by_id = {item["fact"]["id"]: item["fact"] for item in fragment_document["entries"]}
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"])
    required.update(policy["conditional_required_facts"][0]["cases"][branch])
    values = {}
    for fact_id in required:
        if omit and fact_id in omit:
            continue
        fact_definition = by_id[fact_id]
        if fact_definition["value_type"] == "boolean":
            value = False
        elif fact_definition.get("allowed_values"):
            value = fact_definition["allowed_values"][0]
        elif fact_definition["value_type"] == "integer":
            value = 1
        else:
            value = "없음"
        values[fact_id] = {"value": value}
    values["immunization.primary_group"] = {"value": branch}
    for fact_id, value in (overrides or {}).items():
        values[fact_id] = {"value": value}
    return values


def main():
    fragment_document = fragment()
    graph, rules = base_graph_and_rules(
        prefix=P,
        rfe=RFE,
        display="Immunization Consultation or Vaccination Record Review",
        intents=[
            ("intent.immunization_history_review", "Review Immunization History and Goal"),
            ("intent.immunization_safety_screening", "Screen Time-sensitive Post-vaccine Concerns"),
            ("intent.immunization_readiness_handoff", "Prepare Clinician Immunization Readiness Handoff"),
        ],
    )
    primary, research = source_documents()
    mapping = {
        "id": M,
        "version": VERSION,
        "status": "research_only",
        "review_status": "unreviewed",
        "terminology": {
            "system": SN,
            "version": "http://snomed.info/sct/900000000000207008/version/20260701",
            "loinc_version": "2.82",
            "source": "STOM localhost:8088/fhir",
        },
        "verified_focus_concepts": [
            {"code": "33879002", "display": "Administration of vaccine to produce active immunity (procedure)", "active": True},
            {"code": "171044003", "display": "Education about immunization (procedure)", "active": True},
            {"code": "293104008", "display": "Adverse reaction to component of vaccine product (disorder)", "active": True},
            {"code": "77386006", "display": "Pregnancy (finding)", "active": True},
        ],
        "verified_loinc": [
            {"code": "11369-6", "display": "History of Immunization note", "version": "2.82"}
        ],
        "validation": {
            "method": "build_time_local_fhir_lookup",
            "checked_at": ACQUIRED_AT,
            "raw_response_cached": False,
            "clinical_rule_authority": False,
            "question_equivalence_inferred": False,
            "result": "provisional_pass",
        },
        "fhir_projection_candidates": [
            "http://hl7.org/fhir/StructureDefinition/Immunization",
            "http://hl7.org/fhir/StructureDefinition/ImmunizationRecommendation",
            "http://www.hl7korea.or.kr/fhir/krcore/StructureDefinition/krcore-immunization",
        ],
        "provenance": provenance(["source.stom.immunization.20260729"]),
    }
    documents = [
        ("knowledge/base/primary-care-immunization-consultation.json", graph),
        ("rules/base/primary-care-immunization-consultation.json", rules),
        ("knowledge/generated/preventive/immunization-consultation/immunization-consultation.json", fragment_document),
        ("mappings/terminology/snomed-mrcm-immunization-consultation.json", mapping),
        ("sources/manifests/primary-care-immunization-consultation.json", primary),
        ("sources/manifests/primary-care-immunization-consultation-research.json", research),
        ("policies/primary-care-immunization-consultation-completion.json", completion(fragment_document)),
    ]
    for path, document in documents:
        write_json(path, document)
    for name, case in simulations(fragment_document).items():
        write_json("simulation/patients/preventive/immunization-consultation/" + name, case)


if __name__ == "__main__":
    main()
