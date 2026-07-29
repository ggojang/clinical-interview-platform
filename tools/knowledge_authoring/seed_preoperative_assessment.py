#!/usr/bin/env python3
"""Materialize an unreviewed preoperative assessment interview package."""
from profile_support import *


P, RFE = "preoperative-assessment", "rfe.preoperative_assessment"
M, SN = "mapping.snomed-mrcm.preoperative-assessment", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-29T00:00:00Z"
SOURCES = [
    "source.nice.ng180.perioperative-care.20260729",
    "source.nice.ng45.preoperative-tests.20260729",
    "source.nice.qs216.perioperative-risk.20260701",
    "source.asa.preanesthesia-evaluation.2012",
    "source.hl7.fhir-r4.servicerequest",
    "source.hl7.fhir-r4.riskassessment",
    "source.stom.preoperative.20260729",
]
G = {
    key: f"group.preoperative.{key}"
    for key in (
        "goal", "safety", "procedure", "records", "function",
        "cardiopulmonary", "conditions", "bleeding", "medication",
        "anesthesia", "preparation", "handoff",
    )
}
I = {
    "characterize": ["intent.preoperative_characterization"],
    "safety": ["intent.preoperative_current_safety"],
    "readiness": ["intent.preoperative_readiness_handoff"],
}


def Q(fact_id, display, value_type, key, wording, score, groups, intent="readiness", **kwargs):
    return entry(
        P, fact_id, display, value_type, key, wording, score, key, groups,
        intents=I[intent], **kwargs,
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
            "preoperative.primary_group", "Preoperative Interview Goal", "coded",
            "primary-group",
            "이번 문진은 예정 수술 평가, 준비 안내 확인, 기존 검사결과 전달, 과거 연기·취소 후 재평가, 수술 전 새 건강변화 전달 중 무엇에 가깝나요?",
            250, [G["goal"]], "characterize",
            allowed_values=[
                "scheduled_assessment", "preparation_instruction_review",
                "prior_test_review", "previous_delay_or_cancellation",
                "new_health_change", "other_unclear",
            ],
        ),
        Q("preoperative.current_severe_chest_pain", "Current Severe Chest Pain", "boolean", "current-severe-chest-pain", "현재 심한 가슴 통증이 있나요?", 249, [G["safety"]], "safety", safety_relevant=True),
        Q("preoperative.current_rest_dyspnea", "Current Dyspnea at Rest", "boolean", "current-rest-dyspnea", "현재 가만히 있어도 숨쉬기 어려운가요?", 248, [G["safety"]], "safety", safety_relevant=True),
        Q("preoperative.current_syncope_or_near_collapse", "Current Syncope or Near Collapse", "boolean", "current-syncope", "현재 의식을 잃었거나 곧 쓰러질 것 같은 상태인가요?", 247, [G["safety"]], "safety", safety_relevant=True),
        Q("preoperative.current_new_unilateral_weakness", "Current New Unilateral Weakness", "boolean", "current-unilateral-weakness", "현재 새로 생긴 한쪽 팔다리 힘 빠짐이 있나요?", 246, [G["safety"]], "safety", safety_relevant=True),
        Q("preoperative.current_new_speech_difficulty", "Current New Speech Difficulty", "boolean", "current-speech-difficulty", "현재 새로 생긴 말하기 어려움이 있나요?", 245, [G["safety"]], "safety", safety_relevant=True),
        Q("preoperative.current_uncontrolled_bleeding", "Current Uncontrolled Bleeding", "boolean", "current-uncontrolled-bleeding", "현재 압박해도 멈추지 않는 출혈이 있나요?", 244, [G["safety"], G["bleeding"]], "safety", safety_relevant=True),
        Q("preoperative.current_rapidly_worsening_illness", "Current Rapidly Worsening Illness", "boolean", "current-worsening-illness", "현재 새로운 질환이나 증상이 빠르게 악화하고 있나요?", 243, [G["safety"]], "safety", safety_relevant=True),
        Q("preoperative.planned_procedure_name", "Planned Procedure Name", "coded_or_string", "procedure-name", "예정된 수술 또는 시술의 이름을 알려주세요.", 230, [G["procedure"]], "characterize"),
        Q("preoperative.planned_procedure_site", "Planned Procedure Site", "string", "procedure-site", "수술 또는 시술할 신체 부위를 알려주세요.", 229, [G["procedure"]], "characterize"),
        Q("preoperative.planned_procedure_laterality", "Planned Procedure Laterality", "coded", "procedure-laterality", "수술 부위는 오른쪽, 왼쪽, 양쪽, 정중앙 또는 해당 없음 중 어디인가요?", 228, [G["procedure"]], "characterize", allowed_values=["right", "left", "bilateral", "midline", "not_applicable", "unknown"]),
        Q("preoperative.planned_procedure_date", "Planned Procedure Date", "date_or_period", "procedure-date", "예정된 수술 또는 시술 날짜를 알려주세요.", 227, [G["procedure"]], "characterize"),
        Q("preoperative.planned_facility", "Planned Facility", "string", "facility", "수술 또는 시술을 받을 의료기관을 알려주세요.", 226, [G["procedure"], G["handoff"]], "characterize"),
        Q("preoperative.surgical_specialty", "Surgical Specialty", "string", "specialty", "수술 또는 시술을 담당하는 진료과를 알려주세요.", 225, [G["procedure"]], "characterize"),
        Q("preoperative.procedure_urgency", "Procedure Urgency", "coded", "procedure-urgency", "의료진에게 들은 일정은 계획 수술, 신속히 필요한 수술, 응급수술 중 어느 것인가요?", 224, [G["procedure"]], "characterize", allowed_values=["elective", "time_sensitive", "emergency", "unknown"]),
        Q("preoperative.expected_anesthesia_type", "Expected Anesthesia Type", "coded", "anesthesia-type", "안내받은 마취 방법은 전신마취, 부위마취, 진정, 국소마취 중 무엇인가요?", 223, [G["procedure"], G["anesthesia"]], "characterize", allowed_values=["general", "regional", "sedation", "local", "multiple_or_other", "unknown"]),
        Q("preoperative.expected_care_setting", "Expected Care Setting", "coded", "care-setting", "당일 귀가, 입원 예정, 아직 미정 중 어느 것인가요?", 222, [G["procedure"], G["preparation"]], "characterize", allowed_values=["same_day_discharge", "inpatient", "unknown"]),
        Q("preoperative.patient_understanding_of_indication", "Patient Understanding of Procedure Indication", "string", "procedure-indication", "이 수술 또는 시술을 받는 이유를 어떻게 설명 들었나요?", 221, [G["goal"], G["procedure"]], "characterize"),
        Q("preoperative.information_source", "Preoperative Information Source", "coded", "information-source", "수술 정보는 예약문서, 의료기관 전산기록, 의료진 설명, 본인 또는 보호자 기억 중 어디에서 확인했나요?", 220, [G["records"]], "characterize", allowed_values=["booking_document", "clinical_record", "clinician_explanation", "patient_recall", "caregiver_recall", "multiple_sources", "unknown"]),
        Q("preoperative.available_documents", "Available Preoperative Documents", "string", "available-documents", "현재 확인 가능한 예약지, 의뢰서 또는 준비 안내서가 있나요?", 219, [G["records"], G["handoff"]]),
        Q("preoperative.information_conflict", "Preoperative Information Conflict", "boolean", "information-conflict", "문서와 의료진 설명 또는 기억 사이에 서로 맞지 않는 내용이 있나요?", 218, [G["records"], G["handoff"]]),
        Q("preoperative.usual_walking_capacity", "Usual Walking Capacity", "string", "walking-capacity", "평소 쉬지 않고 걸을 수 있는 거리 또는 시간을 알려주세요.", 210, [G["function"]]),
        Q("preoperative.can_climb_two_flights", "Ability to Climb Two Flights", "boolean", "stairs-capacity", "평소 계단 두 층을 쉬지 않고 오를 수 있나요?", 209, [G["function"]]),
        Q("preoperative.independent_self_care", "Independent Self Care", "boolean", "self-care", "평소 씻기, 옷 입기, 식사 같은 기본 일상생활을 혼자 할 수 있나요?", 208, [G["function"]]),
        Q("preoperative.mobility_aid", "Mobility Aid", "string", "mobility-aid", "평소 이동할 때 사용하는 보행 보조기구가 있나요?", 207, [G["function"]]),
        Q("preoperative.recent_functional_decline", "Recent Functional Decline", "boolean", "functional-decline", "최근 평소보다 활동 능력이 줄었나요?", 206, [G["function"]]),
        Q("preoperative.exertional_chest_pain", "Exertional Chest Pain", "boolean", "exertional-chest-pain", "걷거나 계단을 오를 때 가슴 통증이 생기나요?", 205, [G["function"], G["cardiopulmonary"]]),
        Q("preoperative.exertional_dyspnea", "Exertional Dyspnea", "boolean", "exertional-dyspnea", "걷거나 계단을 오를 때 숨이 차서 멈춰야 하나요?", 204, [G["function"], G["cardiopulmonary"]]),
        Q("preoperative.known_cardiac_condition", "Known Cardiac Condition", "string", "cardiac-condition", "진단받은 심장 또는 혈관 질환이 있다면 알려주세요.", 200, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.cardiac_device", "Cardiac Implanted Device", "string", "cardiac-device", "심박동기나 삽입형 제세동기 같은 심장 기기가 있나요?", 199, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.known_respiratory_condition", "Known Respiratory Condition", "string", "respiratory-condition", "진단받은 호흡기 질환이 있다면 알려주세요.", 198, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.sleep_apnea_diagnosis", "Sleep Apnea Diagnosis", "boolean", "sleep-apnea", "수면무호흡증을 진단받았나요?", 197, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.positive_airway_pressure_use", "Positive Airway Pressure Use", "boolean", "positive-airway-pressure-use", "현재 수면 중 양압기 장비를 사용하나요?", 196, [G["cardiopulmonary"], G["preparation"]]),
        Q("preoperative.positive_airway_pressure_type", "Positive Airway Pressure Type", "string", "positive-airway-pressure-type", "사용하는 양압기 장비의 종류를 알려주세요.", 195, [G["cardiopulmonary"], G["preparation"]]),
        Q("preoperative.home_oxygen_use", "Home Oxygen Use", "boolean", "home-oxygen", "현재 집에서 산소를 사용하나요?", 194, [G["cardiopulmonary"]]),
        Q("preoperative.recent_respiratory_infection", "Recent Respiratory Infection", "boolean", "recent-respiratory-infection", "최근 호흡기 감염으로 진료받았나요?", 193, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.recent_infection_timing", "Recent Infection Timing", "date_or_period", "recent-infection-timing", "가장 최근 호흡기 감염이 시작된 시기를 알려주세요.", 192, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.tobacco_use_status", "Tobacco Use Status", "coded", "tobacco-use-status", "일반담배 사용 상태는 현재 흡연, 과거 흡연, 비흡연, 잘 모름 중 무엇인가요?", 191, [G["cardiopulmonary"], G["conditions"]], allowed_values=["current", "former", "never", "unknown"]),
        Q("preoperative.combustible_cigarettes_per_day", "Combustible Cigarettes per Day", "integer", "cigarettes-per-day", "일반담배를 하루 평균 몇 개비 피우거나 피웠나요?", 190, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.tobacco_use_duration", "Tobacco Use Duration", "string", "tobacco-use-duration", "일반담배를 사용한 총 기간을 알려주세요.", 189, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.vaping_use_status", "Vaping Use Status", "coded", "vaping-use-status", "전자담배 사용 상태는 현재 사용, 과거 사용, 사용한 적 없음, 잘 모름 중 무엇인가요?", 188, [G["cardiopulmonary"], G["conditions"]], allowed_values=["current", "former", "never", "unknown"]),
        Q("preoperative.vaping_use_frequency", "Vaping Use Frequency", "string", "vaping-use-frequency", "전자담배를 사용하는 빈도를 알려주세요.", 187, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.vaping_use_duration", "Vaping Use Duration", "string", "vaping-use-duration", "전자담배를 사용한 총 기간을 알려주세요.", 186, [G["cardiopulmonary"], G["conditions"]]),
        Q("preoperative.alcohol_use_status", "Alcohol Use Status", "coded", "alcohol-use-status", "음주 상태는 현재 음주, 과거 음주, 마신 적 없음, 잘 모름 중 무엇인가요?", 185, [G["conditions"]], allowed_values=["current", "former", "never", "unknown"]),
        Q("preoperative.alcohol_frequency", "Alcohol Use Frequency", "string", "alcohol-frequency", "술을 마시는 빈도를 알려주세요.", 184, [G["conditions"]]),
        Q("preoperative.alcohol_type", "Alcohol Type", "string", "alcohol-type", "주로 마시는 술의 종류를 알려주세요.", 183, [G["conditions"]]),
        Q("preoperative.alcohol_amount_per_occasion", "Alcohol Amount per Occasion", "string", "alcohol-amount-per-occasion", "한 번 마실 때의 양을 종류별 잔 또는 병 기준으로 알려주세요.", 182, [G["conditions"]]),
        Q("preoperative.diabetes_status", "Diabetes Status", "boolean", "diabetes-status", "당뇨병을 진단받았나요?", 188, [G["conditions"]]),
        Q("preoperative.latest_hba1c_value", "Latest HbA1c Value", "string", "latest-hba1c-value", "최근 당화혈색소 수치를 알고 있다면 알려주세요.", 181, [G["conditions"], G["records"]]),
        Q("preoperative.latest_hba1c_date", "Latest HbA1c Date", "date_or_period", "latest-hba1c-date", "최근 당화혈색소 검사일을 알고 있다면 알려주세요.", 180, [G["conditions"], G["records"]]),
        Q("preoperative.kidney_disease_status", "Kidney Disease Status", "boolean", "kidney-disease", "만성콩팥병 또는 신장기능 저하를 진단받았나요?", 186, [G["conditions"]]),
        Q("preoperative.dialysis_status", "Dialysis Status", "boolean", "dialysis-status", "현재 투석 치료를 받고 있나요?", 185, [G["conditions"]]),
        Q("preoperative.liver_disease_status", "Liver Disease Status", "boolean", "liver-disease", "간경변 또는 만성 간질환을 진단받았나요?", 184, [G["conditions"]]),
        Q("preoperative.anemia_status", "Anemia Status", "boolean", "anemia-status", "빈혈을 진단받았나요?", 183, [G["conditions"], G["bleeding"]]),
        Q("preoperative.nutrition_concern", "Nutrition Concern", "boolean", "nutrition-concern", "최근 식사량 감소나 영양상태에 대한 우려가 있나요?", 182, [G["conditions"]]),
        Q("preoperative.unintentional_weight_loss", "Unintentional Weight Loss", "boolean", "unintentional-weight-loss", "최근 의도하지 않은 체중 감소가 있었나요?", 181, [G["conditions"]]),
        Q("preoperative.bleeding_tendency_history", "Bleeding Tendency History", "boolean", "bleeding-history", "작은 상처나 치과 치료 후에도 출혈이 오래 지속된 적이 있나요?", 178, [G["bleeding"]]),
        Q("preoperative.prior_venous_thromboembolism", "Prior Venous Thromboembolism", "boolean", "prior-vte", "과거 다리 혈전 또는 폐색전증을 진단받은 적이 있나요?", 177, [G["bleeding"], G["conditions"]]),
        Q("preoperative.current_anticoagulant", "Current Anticoagulant", "string", "anticoagulant", "현재 복용하거나 주사하는 항응고제가 있다면 이름을 알려주세요.", 176, [G["bleeding"], G["medication"]]),
        Q("preoperative.current_antiplatelet", "Current Antiplatelet", "string", "antiplatelet", "현재 복용하는 항혈소판제가 있다면 이름을 알려주세요.", 175, [G["bleeding"], G["medication"]]),
        Q("preoperative.current_medicine_list", "Current Medicine List", "string", "medicine-list", "현재 실제로 사용하는 처방약, 일반약, 한약 또는 보충제를 알려주세요.", 174, [G["medication"], G["handoff"]]),
        Q("preoperative.medicine_instruction_received", "Perioperative Medicine Instruction Received", "boolean", "medicine-instruction", "수술 전후 약 복용 또는 중단 방법을 의료진에게 안내받았나요?", 173, [G["medication"], G["preparation"]]),
        Q("preoperative.medicine_instruction_question", "Perioperative Medicine Instruction Question", "string", "medicine-instruction-question", "약 복용 안내에서 이해되지 않거나 서로 다른 내용이 있다면 알려주세요.", 172, [G["medication"], G["preparation"], G["handoff"]]),
        Q("preoperative.known_allergy", "Known Allergy", "string", "known-allergy", "약, 음식 또는 의료용품 알레르기가 있다면 원인 물질을 알려주세요.", 170, [G["anesthesia"], G["handoff"]]),
        Q("preoperative.allergy_reaction", "Allergy Reaction", "string", "allergy-reaction", "알레르기 때 나타난 반응을 알려주세요.", 169, [G["anesthesia"], G["handoff"]]),
        Q("preoperative.prior_anesthesia_problem", "Prior Anesthesia Problem", "boolean", "prior-anesthesia-problem", "과거 마취 중 또는 마취 후 문제가 있었나요?", 168, [G["anesthesia"]]),
        Q("preoperative.prior_anesthesia_problem_detail", "Prior Anesthesia Problem Detail", "string", "prior-anesthesia-detail", "과거 마취 문제의 증상 또는 의료진 설명을 알려주세요.", 167, [G["anesthesia"], G["handoff"]]),
        Q("preoperative.difficult_airway_history", "Difficult Airway History", "boolean", "difficult-airway", "과거 기도삽관이나 마취용 기도 확보가 어렵다는 설명을 들었나요?", 166, [G["anesthesia"]]),
        Q("preoperative.postoperative_nausea_history", "Postoperative Nausea or Vomiting History", "boolean", "postoperative-nausea", "과거 마취 후 심한 메스꺼움 또는 구토가 있었나요?", 165, [G["anesthesia"]]),
        Q("preoperative.family_anesthesia_reaction", "Family Severe Anesthesia Reaction", "boolean", "family-anesthesia-reaction", "가족 중 마취와 관련해 심한 반응을 겪었다는 사람이 있나요?", 164, [G["anesthesia"]]),
        Q("preoperative.dental_or_oral_issue", "Dental or Oral Issue Relevant to Airway", "string", "dental-oral-issue", "흔들리는 치아, 틀니 또는 입 벌리기 어려움이 있다면 알려주세요.", 163, [G["anesthesia"]]),
        Q("preoperative.pregnancy_possibility", "Pregnancy Possibility", "coded", "pregnancy-possibility", "현재 임신 가능성이 있나요?", 162, [G["conditions"], G["preparation"]], allowed_values=["possible", "not_possible", "not_applicable", "unknown"]),
        Q("preoperative.previous_delay_or_cancellation", "Previous Surgical Delay or Cancellation", "boolean", "previous-delay", "이 수술 또는 시술이 건강 문제 때문에 연기되거나 취소된 적이 있나요?", 160, [G["records"], G["goal"]]),
        Q("preoperative.previous_delay_reason", "Previous Delay or Cancellation Reason", "string", "previous-delay-reason", "이전에 연기 또는 취소된 이유를 알려주세요.", 159, [G["records"], G["handoff"]]),
        Q("preoperative.available_test_results", "Available Preoperative Test Results", "string", "available-test-results", "이미 받은 수술 전 검사와 결과가 있다면 알려주세요.", 158, [G["records"], G["handoff"]]),
        Q("preoperative.prior_risk_assessment", "Prior Perioperative Risk Assessment", "string", "prior-risk-assessment", "의료진이 사용한 수술 위험평가 도구나 결과를 알고 있다면 그대로 알려주세요.", 157, [G["records"], G["handoff"]]),
        Q("preoperative.fasting_instruction_received", "Fasting Instruction Received", "boolean", "fasting-instruction", "수술 전 금식 방법을 의료진에게 안내받았나요?", 156, [G["preparation"]]),
        Q("preoperative.transport_and_home_support", "Transport and Home Support", "string", "transport-support", "퇴원 후 이동과 집에서 도움을 줄 사람에 관한 준비상태를 알려주세요.", 100, [G["preparation"], G["handoff"]]),
        Q("preoperative.accessibility_or_communication_need", "Accessibility or Communication Need", "string", "accessibility", "문진과 수술 준비를 위해 필요한 통역 또는 접근성 지원을 알려주세요.", 90, [G["handoff"]]),
        Q("preoperative.new_health_change", "New Health Change before Surgery", "string", "new-health-change", "수술 일정이 정해진 뒤 새로 생기거나 달라진 건강 문제를 알려주세요.", 85, [G["goal"], G["handoff"]]),
        Q("preoperative.patient_concern_or_goal", "Patient Preoperative Concern or Goal", "string", "patient-goal", "수술 전에 의료진에게 가장 확인하거나 전달하고 싶은 점은 무엇인가요?", 80, [G["goal"], G["handoff"]]),
    ]
    safety = [
        ("current-severe-chest-pain", "preoperative.current_severe_chest_pain", "emergency"),
        ("current-rest-dyspnea", "preoperative.current_rest_dyspnea", "emergency"),
        ("current-syncope", "preoperative.current_syncope_or_near_collapse", "emergency"),
        ("current-unilateral-weakness", "preoperative.current_new_unilateral_weakness", "emergency"),
        ("current-speech-difficulty", "preoperative.current_new_speech_difficulty", "emergency"),
        ("current-uncontrolled-bleeding", "preoperative.current_uncontrolled_bleeding", "emergency"),
        ("current-worsening-illness", "preoperative.current_rapidly_worsening_illness", "urgent"),
    ]
    return {
        "id": "knowledge.generated.preoperative-assessment",
        "version": VERSION,
        "status": "research_only",
        "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-preoperative-assessment-research",
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
        presentation_fact="preoperative.primary_group",
        question_budget=60,
        source_refs=SOURCES,
    )
    policy["required_facts"]["always"] = [
        "preoperative.primary_group",
        *[rule["when"]["fact"] for rule in fragment_document["safety_rules"]],
    ]
    policy["required_facts"]["routine"] = [
        "preoperative.planned_procedure_name",
        "preoperative.planned_procedure_site",
        "preoperative.planned_procedure_laterality",
        "preoperative.planned_procedure_date",
        "preoperative.planned_facility",
        "preoperative.procedure_urgency",
        "preoperative.expected_anesthesia_type",
        "preoperative.expected_care_setting",
        "preoperative.patient_understanding_of_indication",
        "preoperative.information_source",
        "preoperative.information_conflict",
        "preoperative.usual_walking_capacity",
        "preoperative.can_climb_two_flights",
        "preoperative.independent_self_care",
        "preoperative.recent_functional_decline",
        "preoperative.exertional_chest_pain",
        "preoperative.exertional_dyspnea",
        "preoperative.known_cardiac_condition",
        "preoperative.known_respiratory_condition",
        "preoperative.sleep_apnea_diagnosis",
        "preoperative.recent_respiratory_infection",
        "preoperative.tobacco_use_status",
        "preoperative.vaping_use_status",
        "preoperative.alcohol_use_status",
        "preoperative.diabetes_status",
        "preoperative.kidney_disease_status",
        "preoperative.liver_disease_status",
        "preoperative.anemia_status",
        "preoperative.nutrition_concern",
        "preoperative.bleeding_tendency_history",
        "preoperative.prior_venous_thromboembolism",
        "preoperative.current_anticoagulant",
        "preoperative.current_antiplatelet",
        "preoperative.current_medicine_list",
        "preoperative.medicine_instruction_received",
        "preoperative.known_allergy",
        "preoperative.prior_anesthesia_problem",
        "preoperative.difficult_airway_history",
        "preoperative.family_anesthesia_reaction",
        "preoperative.pregnancy_possibility",
        "preoperative.previous_delay_or_cancellation",
        "preoperative.fasting_instruction_received",
        "preoperative.accessibility_or_communication_need",
        "preoperative.patient_concern_or_goal",
    ]
    policy["conditional_required_facts"] = [{
        "selector_fact": "preoperative.primary_group",
        "cases": {
            "scheduled_assessment": ["preoperative.available_documents"],
            "preparation_instruction_review": [
                "preoperative.available_documents",
                "preoperative.medicine_instruction_question",
                "preoperative.transport_and_home_support",
            ],
            "prior_test_review": [
                "preoperative.available_test_results",
                "preoperative.prior_risk_assessment",
            ],
            "previous_delay_or_cancellation": [
                "preoperative.previous_delay_reason",
                "preoperative.new_health_change",
            ],
            "new_health_change": ["preoperative.new_health_change"],
            "other_unclear": ["preoperative.patient_concern_or_goal"],
        },
    }, {
        "selector_fact": "preoperative.tobacco_use_status",
        "cases": {
            "current": ["preoperative.combustible_cigarettes_per_day", "preoperative.tobacco_use_duration"],
            "former": ["preoperative.combustible_cigarettes_per_day", "preoperative.tobacco_use_duration"],
            "never": [],
            "unknown": [],
        },
    }, {
        "selector_fact": "preoperative.vaping_use_status",
        "cases": {
            "current": ["preoperative.vaping_use_frequency", "preoperative.vaping_use_duration"],
            "former": ["preoperative.vaping_use_frequency", "preoperative.vaping_use_duration"],
            "never": [],
            "unknown": [],
        },
    }, {
        "selector_fact": "preoperative.alcohol_use_status",
        "cases": {
            "current": ["preoperative.alcohol_frequency", "preoperative.alcohol_type", "preoperative.alcohol_amount_per_occasion"],
            "former": [],
            "never": [],
            "unknown": [],
        },
    }, {
        "when": {"fact": "preoperative.positive_airway_pressure_use", "equals": True},
        "required_facts": ["preoperative.positive_airway_pressure_type"],
    }]
    policy["clinical_boundary"] = {
        "fitness_or_clearance_determined": False,
        "surgery_go_no_go_determined": False,
        "test_or_medicine_plan_prescribed": False,
        "risk_score_calculated": False,
        "requires_local_protocol_and_clinician_review": True,
    }
    return policy


def source_documents():
    definitions = [
        (
            "source.nice.ng180.perioperative-care.20260729", "NICE",
            "Perioperative care in adults (NG180)", "current-page-2026-07-29",
            "https://www.nice.org.uk/guidance/ng180/chapter/Recommendations",
            "nice_guidance",
            [
                "Clinical assessment is supplemented, not replaced, by validated risk stratification.",
                "Preoperative care considers smoking, alcohol, anaemia, venous thromboembolism and nutrition.",
            ],
        ),
        (
            "source.nice.ng45.preoperative-tests.20260729", "NICE",
            "Routine preoperative tests for elective surgery (NG45)", "current-page-2026-07-29",
            "https://www.nice.org.uk/guidance/ng45/chapter/recommendations",
            "nice_guidance",
            [
                "Existing medicines and relevant comorbidities inform clinician decisions about testing.",
                "The interview records existing tests and pregnancy possibility but does not order routine tests.",
            ],
        ),
        (
            "source.nice.qs216.perioperative-risk.20260701", "NICE",
            "Perioperative care in adults quality standard QS216", "2026-07-01",
            "https://www.nice.org.uk/guidance/qs216/chapter/quality-statement-2-assessment-of-perioperative-risk",
            "nice_guidance",
            [
                "A validated risk tool may supplement clinical assessment before surgery.",
                "Clinical judgement remains necessary where tools omit frailty, disability or other individual context.",
            ],
        ),
        (
            "source.asa.preanesthesia-evaluation.2012", "ASA",
            "Practice Advisory for Preanesthesia Evaluation", "2012",
            "https://www.asahq.org/~/media/sites/asahq/files/public/resources/standards-guidelines/practice-advisory-for-preanesthesia-evaluation.pdf",
            "clinical_guideline",
            [
                "Preanesthesia evaluation includes relevant records, patient interview and focused examination by qualified clinicians.",
                "Testing and consultation are individualized; this interview does not select them.",
            ],
        ),
        (
            "source.hl7.fhir-r4.servicerequest", "HL7",
            "FHIR R4 ServiceRequest", "4.0.1",
            "https://hl7.org/fhir/R4/servicerequest.html",
            "interoperability_standard",
            [
                "A planned procedure request and its supporting information are distinct from completed procedures.",
                "FHIR element bindings guide projection and do not determine surgical readiness.",
            ],
        ),
        (
            "source.hl7.fhir-r4.riskassessment", "HL7",
            "FHIR R4 RiskAssessment", "4.0.1",
            "https://hl7.org/fhir/R4/riskassessment.html",
            "interoperability_standard",
            [
                "RiskAssessment represents a clinician or algorithm assessment with method and basis.",
                "Patient-entered interview facts are not themselves a computed RiskAssessment.",
            ],
        ),
        (
            "source.stom.preoperative.20260729", "Infoclinic",
            "STOM preoperative terminology lookup", "SNOMEDCT-20260701_LOINC-2.82",
            "http://localhost:8088/fhir", "terminology_server",
            [
                "FHIR lookup verified SNOMED CT 133898004 and 429160000 as active concepts.",
                "FHIR lookup verified LOINC 34123-0, 34876-3 and 103546-8.",
                "Terminology supports representation only and has no clinical rule authority.",
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
            "language": "en",
            "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached",
            "license_status": "restricted" if publisher == "Infoclinic" else "official_link_only",
            "complete": False,
            "monitor_profile": profile,
            "last_monitored_at": "2026-07-29",
            "monitor_result": "current_official_source_confirmed",
            "assertions": assertions,
        })
    research = {
        "id": "source-manifest.primary-care-preoperative-assessment-research",
        "version": VERSION,
        "acquired_at": ACQUIRED_AT,
        "status": "research_only",
        "artifacts": artifacts,
        "excluded_sources": [{
            "publisher": "ESC",
            "title": "2022 ESC Guidelines on non-cardiac surgery",
            "url": "https://www.escardio.org/guidelines/clinical-practice-guidelines/all-esc-practice-guidelines/non-cardiac-surgery/",
            "reason": "The official page requires a formal licence for guideline content used or transformed in software or AI; no clinical content was incorporated.",
        }],
        "provenance": provenance([item[0] for item in definitions]),
    }
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.preoperative-assessment", "generated_clinical_knowledge", "knowledge/generated/preventive/preoperative-assessment/preoperative-assessment.json", True),
        ("source.mapping.preoperative-assessment", "terminology_mapping", "mappings/terminology/snomed-mrcm-preoperative-assessment.json", False),
        ("source.external.preoperative-assessment", "external_source_manifest", "sources/manifests/primary-care-preoperative-assessment-research.json", False),
        ("source.policy.preoperative-assessment", "runtime_policy", "policies/primary-care-preoperative-assessment-completion.json", True),
    ]
    primary = {
        "id": "source-manifest.primary-care-preoperative-assessment",
        "version": VERSION,
        "acquired_at": ACQUIRED_AT,
        "artifacts": [{
            "id": identifier, "kind": kind, "publisher": "clinical-interview-platform",
            "version": VERSION, "language": "en", "path": path,
            "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown",
            "complete": complete,
        } for identifier, kind, path, complete in paths],
        "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"]),
    }
    return primary, research


def _routine_hidden(fragment_document, branch, overrides=None, omit=None):
    policy = completion(fragment_document)
    by_id = {item["fact"]["id"]: item["fact"] for item in fragment_document["entries"]}
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"])
    required.update(policy["conditional_required_facts"][0]["cases"][branch])
    values = {}
    for fact_id in required:
        if omit and fact_id in omit:
            continue
        definition = by_id[fact_id]
        if definition["value_type"] == "boolean":
            value = False
        elif definition.get("allowed_values"):
            value = definition["allowed_values"][0]
        elif definition["value_type"] == "integer":
            value = 1
        else:
            value = "합성 정보"
        values[fact_id] = {"value": value}
    values["preoperative.primary_group"] = {"value": branch}
    for fact_id, value in (overrides or {}).items():
        values[fact_id] = {"value": value}
    for conditional in policy["conditional_required_facts"][1:]:
        if "when" in conditional:
            condition = conditional["when"]
            if values.get(condition["fact"], {}).get("value") == condition.get("equals"):
                required.update(conditional.get("required_facts", []))
            continue
        selector = conditional["selector_fact"]
        selector_value = values.get(selector, {}).get("value")
        required.update(conditional.get("cases", {}).get(selector_value, []))
    for fact_id in required:
        if fact_id in values or (omit and fact_id in omit):
            continue
        definition = by_id[fact_id]
        if definition["value_type"] == "boolean":
            value = False
        elif definition.get("allowed_values"):
            value = definition["allowed_values"][0]
        elif definition["value_type"] == "integer":
            value = 1
        else:
            value = "합성 정보"
        values[fact_id] = {"value": value}
    return values


def simulations(fragment_document):
    output = {}
    for index, rule in enumerate(fragment_document["safety_rules"]):
        fact_id = rule["when"]["fact"]
        level = rule["then"]["safety_level"]
        key = rule["id"].split("safety.")[1]
        output[f"PREOP-{key.upper()}.json"] = {
            "id": f"PREOP-{key.upper()}",
            "simulation_language": "ko",
            "persona": {"age": 41 + index},
            "initial_statement": {"ko": "수술 전 문진 중 현재 증상을 알립니다."},
            "hidden_state": {
                "preoperative.primary_group": {"value": "new_health_change"},
                fact_id: {"value": True},
            },
            "expected": {
                "expected_safety_level": level,
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [rule["id"]],
                "expected_max_turns": 20,
                "forbidden_assertions": [
                    "preoperative.clearance_granted",
                    "preoperative.surgery_should_proceed",
                    "preoperative.test_ordered",
                    "preoperative.medicine_stop_advice",
                ],
            },
            "provenance": provenance(SOURCES),
        }
    output["PREOP-ROUTINE-PLANNED-SURGERY.json"] = {
        "id": "PREOP-ROUTINE-PLANNED-SURGERY",
        "simulation_language": "ko",
        "persona": {"age": 62},
        "initial_statement": {"ko": "다음 달 예정된 수술 전에 건강정보를 전달하려고 합니다."},
        "hidden_state": _routine_hidden(fragment_document, "scheduled_assessment"),
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 65,
            "forbidden_assertions": ["preoperative.clearance_granted", "preoperative.risk_score_calculated"],
        },
        "provenance": provenance(SOURCES),
    }
    output["PREOP-OLDER-PROXY-DATA-ABSENT.json"] = {
        "id": "PREOP-OLDER-PROXY-DATA-ABSENT",
        "simulation_language": "ko",
        "persona": {"age": 82},
        "encounter_context": {
            "care_setting": "primary_care", "encounter_type": "referral_consultation",
            "interview_initiator": "caregiver", "interview_mode": "telephone",
            "available_information": ["partial_booking_document"],
            "time_constraint": "scheduled", "clinical_responsibility": "referral_support",
        },
        "initial_statement": {"ko": "보호자로서 수술 전 정보를 대신 정리하지만 마취 종류는 모릅니다."},
        "hidden_state": _routine_hidden(
            fragment_document, "scheduled_assessment",
            omit={"preoperative.expected_anesthesia_type", "preoperative.planned_procedure_laterality"},
        ),
        "response_behavior": {
            "preoperative.expected_anesthesia_type": {"dataAbsentReason": "asked-unknown"},
            "preoperative.planned_procedure_laterality": {"dataAbsentReason": "asked-unknown"},
        },
        "expected": {
            "expected_data_absent_reasons": {
                "preoperative.expected_anesthesia_type": "asked-unknown",
                "preoperative.planned_procedure_laterality": "asked-unknown",
            },
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 65,
            "forbidden_assertions": ["preoperative.clearance_granted"],
        },
        "provenance": provenance(SOURCES),
    }
    output["PREOP-MULTI-RFE-TERMINOLOGY-OFFLINE.json"] = {
        "id": "PREOP-MULTI-RFE-TERMINOLOGY-OFFLINE",
        "simulation_language": "ko",
        "persona": {"age": 53},
        "operational_state": {"terminology_adapter": "unavailable"},
        "initial_statement": {"ko": "수술 전 평가와 별도로 새 두통도 의료진에게 전달하고 싶습니다."},
        "hidden_state": _routine_hidden(fragment_document, "new_health_change", {
            "preoperative.new_health_change": "새 두통은 별도 RFE로 전달",
        }),
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 65,
            "forbidden_assertions": ["diagnosis.headache", "preoperative.clearance_granted"],
        },
        "provenance": provenance(SOURCES),
    }
    return output


def main():
    fragment_document = fragment()
    graph, rules = base_graph_and_rules(
        prefix=P,
        rfe=RFE,
        display="Preoperative Assessment or Preparation Review",
        intents=[
            ("intent.preoperative_characterization", "Characterize Planned Procedure and Interview Goal"),
            ("intent.preoperative_current_safety", "Screen Current Time-sensitive Health Changes"),
            ("intent.preoperative_readiness_handoff", "Prepare Clinician Preoperative Handoff"),
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
            {"code": "133898004", "display": "Preoperative care (regime/therapy)", "active": True},
            {"code": "429160000", "display": "Functional capacity (observable entity)", "active": True},
        ],
        "verified_loinc_document_codes": [
            {"code": "34123-0", "display": "Anesthesiology Hospital Preoperative evaluation and management note", "version": "2.82"},
            {"code": "34876-3", "display": "Surgery Preoperative evaluation and management note", "version": "2.82"},
            {"code": "103546-8", "display": "General medicine Preoperative evaluation and management note", "version": "2.82"},
        ],
        "verified_loinc_question_candidates": [
            {"code": "72166-2", "display": "Tobacco smoking status", "relation": "equivalent", "version": "2.82"},
            {"code": "8663-7", "display": "Cigarettes smoked current (pack per day) - Reported", "relation": "partial", "version": "2.82"},
            {"code": "74013-4", "display": "Alcoholic drinks per day", "relation": "partial", "version": "2.82"},
            {"code": "82810-3", "display": "Pregnancy status", "relation": "partial", "version": "2.82"},
            {"code": "4548-4", "display": "Hemoglobin A1c/Hemoglobin.total in Blood", "relation": "partial", "version": "2.82"},
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
            "http://hl7.org/fhir/StructureDefinition/ServiceRequest",
            "http://hl7.org/fhir/StructureDefinition/Observation",
            "http://hl7.org/fhir/StructureDefinition/RiskAssessment",
            "http://hl7.org/fhir/StructureDefinition/QuestionnaireResponse",
        ],
        "preoperative_semantics": {
            "fitness_or_clearance_inferred": False,
            "surgery_go_no_go_inferred": False,
            "test_or_medicine_plan_inferred": False,
            "risk_score_calculated": False,
            "runtime_terminology_query_required": False,
        },
        "provenance": provenance(["source.stom.preoperative.20260729"]),
    }
    documents = [
        ("knowledge/base/primary-care-preoperative-assessment.json", graph),
        ("rules/base/primary-care-preoperative-assessment.json", rules),
        ("knowledge/generated/preventive/preoperative-assessment/preoperative-assessment.json", fragment_document),
        ("mappings/terminology/snomed-mrcm-preoperative-assessment.json", mapping),
        ("sources/manifests/primary-care-preoperative-assessment.json", primary),
        ("sources/manifests/primary-care-preoperative-assessment-research.json", research),
        ("policies/primary-care-preoperative-assessment-completion.json", completion(fragment_document)),
    ]
    for path, document in documents:
        write_json(path, document)
    for name, case in simulations(fragment_document).items():
        write_json("simulation/patients/preventive/preoperative-assessment/" + name, case)


if __name__ == "__main__":
    main()
