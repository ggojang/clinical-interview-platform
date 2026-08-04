#!/usr/bin/env python3
"""Materialize a research-only jaundice interview package."""
from profile_support import *


P, RFE = "jaundice", "rfe.jaundice"
M = "mapping.terminology.jaundice"
ACQUIRED_AT = "2026-08-03T00:00:00Z"
SOURCES = [
    "source.kdca.viral-hepatitis-guideline.2026",
    "source.nhs.jaundice.20240122",
    "source.cdc.hepatitis-clinical-overview.20251128",
    "source.nice.ng12.jaundice.20260415",
    "source.nice.cg98.newborn-jaundice.20231031",
    "source.stom.jaundice.20260803",
]
G = {key: f"group.jaundice.{key}" for key in (
    "identity", "safety", "pattern", "associated", "context", "previous", "handoff",
)}
I = [
    "intent.characterize_jaundice",
    "intent.screen_jaundice_safety",
    "intent.assess_jaundice_context",
    "intent.prepare_jaundice_handoff",
]


def Q(fact_id, display, value_type, key, wording, score, group, intent, **kwargs):
    return entry(P, fact_id, display, value_type, key, wording, score, key,
                 [G[group]], intents=[intent], **kwargs)


def fragment():
    characterize, safety, assess, handoff = I
    entries = [
        Q("jaundice.presentation", "Main Jaundice Presentation", "coded_or_string", "presentation",
          "이번 문진의 주된 이유는 눈 흰자 또는 피부의 노란 변화, 진한 소변, 옅은 변, 검사결과 확인 중 무엇인가요? 보기에 없으면 직접 입력해 주세요.", 300, "identity", characterize,
          allowed_values=["yellow_sclera", "yellow_skin", "dark_urine", "pale_stool", "abnormal_test", "follow_up", "other"]),
        Q("jaundice.information_source", "Jaundice Information Source", "coded", "information-source",
          "황색 변화와 동반 상태를 누가 답하고 있나요? 보기에 없으면 직접 입력해 주세요.", 299, "identity", characterize,
          allowed_values=["patient", "caregiver", "patient_and_caregiver", "record", "unknown", "other"]),
        Q("jaundice.source_reliability", "Jaundice Information Reliability", "coded", "source-reliability",
          "답변의 신뢰도는 최근 직접 관찰, 기억 불확실, 다른 사람 또는 기록과 상충 중 어디에 가깝나요? 보기에 없으면 직접 입력해 주세요.", 298, "identity", characterize,
          allowed_values=["reliable", "partly_reliable", "memory_uncertain", "conflicting_sources", "unknown", "other"]),
        Q("jaundice.noticed_by", "Person Who First Noticed Yellowing", "string", "noticed-by",
          "노란 변화를 처음 알아본 사람을 알려주세요.", 297, "identity", characterize),

        Q("jaundice.current_reduced_consciousness", "Current Reduced Consciousness", "boolean", "reduced-consciousness",
          "지금 깨우기 어렵거나 의식이 뚜렷하게 떨어져 있나요?", 1300, "safety", safety, safety_relevant=True),
        Q("jaundice.new_confusion", "New Confusion", "boolean", "new-confusion",
          "평소와 달리 새로 혼란스럽거나 말과 행동이 맞지 않나요?", 1299, "safety", safety, safety_relevant=True),
        Q("jaundice.collapse", "Collapse", "boolean", "collapse",
          "지금 쓰러졌거나 서 있기 어려울 정도로 기운이 없나요?", 1298, "safety", safety, safety_relevant=True),
        Q("jaundice.severe_right_upper_abdominal_pain", "Severe Right Upper Abdominal Pain", "boolean", "severe-ruq-pain",
          "지금 오른쪽 윗배에 심한 통증이 있나요?", 1297, "safety", safety, safety_relevant=True),
        Q("jaundice.fever", "Current Fever", "boolean", "fever",
          "현재 열이 나거나 측정한 체온이 높나요?", 1296, "safety", safety, safety_relevant=True),
        Q("jaundice.rigors", "Current Rigors", "boolean", "rigors",
          "현재 몸이 심하게 떨릴 정도의 오한이 있나요?", 1295, "safety", safety, safety_relevant=True),
        Q("jaundice.repeated_vomiting", "Repeated Vomiting", "boolean", "repeated-vomiting",
          "오늘 여러 차례 반복해서 토했나요?", 1294, "safety", safety, safety_relevant=True),
        Q("jaundice.unable_to_keep_fluids", "Unable to Maintain Fluids", "boolean", "unable-maintain-fluids",
          "물을 마셔도 유지하지 못하고 다시 토하나요?", 1293, "safety", safety, safety_relevant=True),
        Q("jaundice.markedly_reduced_urine", "Markedly Reduced Urine", "boolean", "markedly-reduced-urine",
          "평소보다 소변 양이 뚜렷하게 줄었나요?", 1292, "safety", safety, safety_relevant=True),
        Q("jaundice.vomiting_blood", "Vomiting Blood", "boolean", "vomiting-blood",
          "피를 토했거나 토한 것에 피가 섞였나요?", 1291, "safety", safety, safety_relevant=True),
        Q("jaundice.black_or_bloody_stool", "Black or Bloody Stool", "boolean", "black-bloody-stool",
          "검고 끈적한 변 또는 피가 섞인 변을 보았나요?", 1290, "safety", safety, safety_relevant=True),
        Q("jaundice.unexplained_bleeding", "Unexplained Bleeding", "boolean", "unexplained-bleeding",
          "코피나 잇몸 출혈처럼 평소와 다른 출혈이 멈추지 않나요?", 1289, "safety", safety, safety_relevant=True),
        Q("jaundice.suspected_overdose_or_toxic_exposure", "Suspected Overdose or Toxic Exposure", "boolean", "toxic-exposure",
          "약을 정해진 양보다 많이 먹었거나 독성 물질에 노출됐을 가능성이 있나요?", 1288, "safety", safety, safety_relevant=True),
        Q("jaundice.newborn_under_28_days", "Newborn Under 28 Days", "boolean", "newborn-under-28-days",
          "황색 변화가 있는 대상은 생후 28일 미만의 신생아인가요?", 1287, "safety", safety, safety_relevant=True),
        Q("jaundice.newborn_poor_feeding", "Newborn Poor Feeding", "boolean", "newborn-poor-feeding",
          "신생아가 평소보다 잘 먹지 못하나요?", 1286, "safety", safety, safety_relevant=True),
        Q("jaundice.newborn_difficult_to_wake", "Newborn Difficult to Wake", "boolean", "newborn-difficult-wake",
          "신생아를 깨우기 어렵거나 지나치게 처져 있나요?", 1285, "safety", safety, safety_relevant=True),
        Q("jaundice.pregnant_or_postpartum", "Pregnancy or Postpartum Status", "coded", "pregnancy-postpartum",
          "현재 임신 중이거나 출산 후 6주 이내인가요? 보기에 없으면 직접 입력해 주세요.", 1284, "safety", safety, safety_relevant=True,
          allowed_values=["pregnant", "postpartum_6_weeks", "not_pregnant_or_postpartum", "not_applicable", "unknown"]),
        Q("jaundice.rapidly_worsening_yellowing", "Rapidly Worsening Yellowing", "boolean", "rapid-worsening",
          "눈이나 피부의 노란 변화가 몇 시간 또는 며칠 사이 빠르게 심해지고 있나요?", 1283, "safety", safety, safety_relevant=True),

        Q("jaundice.first_onset", "First Jaundice Onset", "date_or_period", "first-onset",
          "노란 변화나 관련 이상을 처음 알아본 때는 언제인가요?", 280, "pattern", characterize),
        Q("jaundice.latest_observed", "Latest Jaundice Observation", "date_or_period", "latest-observed",
          "가장 최근에 노란 변화를 확인한 때는 언제인가요?", 279, "pattern", characterize),
        Q("jaundice.course", "Jaundice Course", "coded", "course",
          "처음보다 좋아짐, 비슷함, 심해짐, 들쭉날쭉함 중 어디에 가깝나요? 보기에 없으면 직접 입력해 주세요.", 278, "pattern", characterize,
          allowed_values=["improving", "unchanged", "worsening", "fluctuating", "resolved", "uncertain", "other"]),
        Q("jaundice.prior_episode", "Prior Jaundice Episode", "boolean", "prior-episode",
          "이전에도 눈이나 피부가 노랗게 보인 적이 있나요?", 277, "pattern", characterize),
        Q("jaundice.scleral_yellowing", "Scleral Yellowing", "boolean", "scleral-yellowing",
          "눈 흰자가 노랗게 보이나요?", 276, "pattern", characterize),
        Q("jaundice.skin_yellowing", "Skin Yellowing", "boolean", "skin-yellowing",
          "피부가 평소보다 노랗게 보이나요?", 275, "pattern", characterize),
        Q("jaundice.observation_conditions", "Yellowing Observation Conditions", "string", "observation-conditions",
          "노란 변화를 어떤 조명이나 사진·대면 상황에서 확인했는지 알려주세요.", 274, "pattern", characterize),
        Q("jaundice.visibility_uncertainty", "Yellowing Visibility Uncertainty", "string", "visibility-uncertainty",
          "피부색이나 조명 때문에 노란 변화를 판단하기 어려운 점이 있나요?", 273, "pattern", characterize),
        Q("jaundice.dark_urine", "Dark Urine", "boolean", "dark-urine",
          "소변 색이 평소보다 진한 갈색이나 차색으로 변했나요?", 272, "pattern", characterize),
        Q("jaundice.pale_stool", "Pale Stool", "boolean", "pale-stool",
          "변 색이 평소보다 매우 옅거나 회백색으로 변했나요?", 271, "pattern", characterize),
        Q("jaundice.itching", "Itching", "boolean", "itching",
          "피부 가려움이 있나요?", 270, "pattern", characterize),
        Q("jaundice.itching_impact", "Itching Impact", "string", "itching-impact",
          "가려움이 수면이나 일상에 미치는 영향을 알려주세요.", 269, "pattern", characterize),

        Q("jaundice.abdominal_pain", "Abdominal Pain", "boolean", "abdominal-pain",
          "배에 통증이 있나요?", 250, "associated", assess),
        Q("jaundice.pain_location", "Abdominal Pain Location", "string", "pain-location",
          "배가 아프다면 가장 아픈 위치를 알려주세요.", 249, "associated", assess),
        Q("jaundice.pain_nrs", "Abdominal Pain Numeric Rating", "integer", "pain-nrs",
          "배 통증이 있다면 0점부터 10점 중 몇 점인가요?", 248, "associated", assess,
          unit="{score}", minimum=0, maximum=10,
          terminology_binding={"system": "http://loinc.org", "code": "72514-3", "display": "Pain severity - 0-10 verbal numeric rating [Score] - Reported", "version": "2.82", "relation": "equivalent"}),
        Q("jaundice.measured_temperature", "Measured Body Temperature", "quantity", "measured-temperature",
          "측정한 체온이 있다면 섭씨 수치를 알려주세요.", 247, "associated", assess, unit="Cel"),
        Q("jaundice.nausea", "Nausea", "boolean", "nausea",
          "메스꺼움이 있나요?", 246, "associated", assess),
        Q("jaundice.vomiting_count", "Vomiting Count", "integer", "vomiting-count",
          "지난 24시간 동안 토한 횟수를 알려주세요.", 245, "associated", assess, minimum=0),
        Q("jaundice.appetite_reduction", "Appetite Reduction", "coded", "appetite-reduction",
          "평소와 비교해 식욕이 어떤가요? 보기에 없으면 직접 입력해 주세요.", 244, "associated", assess,
          allowed_values=["unchanged", "slightly_reduced", "markedly_reduced", "almost_none", "unknown", "other"]),
        Q("jaundice.unintentional_weight_change", "Unintentional Weight Change", "string", "weight-change",
          "의도하지 않은 체중 변화가 있다면 양과 기간을 알려주세요.", 243, "associated", assess),
        Q("jaundice.fatigue", "Fatigue", "string", "fatigue",
          "평소보다 피로하거나 기운이 없는 정도를 알려주세요.", 242, "associated", assess),
        Q("jaundice.abdominal_swelling", "Abdominal Swelling", "boolean", "abdominal-swelling",
          "배가 평소보다 붓거나 불러왔나요?", 241, "associated", assess),
        Q("jaundice.leg_swelling", "Leg Swelling", "boolean", "leg-swelling",
          "다리나 발이 평소보다 붓나요?", 240, "associated", assess),
        Q("jaundice.easy_bruising", "Easy Bruising", "boolean", "easy-bruising",
          "부딪힌 기억이 없는데 멍이 쉽게 생기나요?", 239, "associated", assess),
        Q("jaundice.sleep_wake_change", "Sleep Wake Pattern Change", "boolean", "sleep-wake-change",
          "최근 낮밤이 바뀌는 등 수면 시간대가 평소와 달라졌나요?", 238, "associated", assess),
        Q("jaundice.daily_function_impact", "Daily Function Impact", "string", "function-impact",
          "증상 때문에 식사, 수면, 이동, 일 또는 돌봄에 어떤 영향이 있나요?", 237, "associated", assess),

        Q("jaundice.known_liver_history", "Known Liver History", "string", "liver-history",
          "알고 있는 간질환이나 간수치 이상 이력이 있나요?", 220, "context", assess),
        Q("jaundice.biliary_pancreatic_history", "Biliary or Pancreatic History", "string", "biliary-pancreatic-history",
          "담석, 담도 또는 췌장 질환·시술 이력이 있나요?", 219, "context", assess),
        Q("jaundice.blood_disorder_history", "Blood Disorder History", "string", "blood-history",
          "용혈이나 다른 혈액질환 이력이 있나요?", 218, "context", assess),
        Q("jaundice.prior_surgery_procedure", "Prior Surgery or Procedure", "string", "prior-procedure",
          "관련된 수술이나 시술 이력이 있다면 종류와 시기를 알려주세요.", 217, "context", assess),
        Q("jaundice.current_medicines", "Current Medicines", "string", "current-medicines",
          "현재 복용하는 처방약과 일반약을 이름·용량·복용법과 함께 알려주세요.", 216, "context", assess),
        Q("jaundice.recent_medicine_change", "Recent Medicine Change", "string", "medicine-change",
          "최근 시작하거나 용량·복용법이 바뀐 약과 변경 시기를 알려주세요.", 215, "context", assess),
        Q("jaundice.supplements_herbals", "Supplements and Herbals", "string", "supplements",
          "복용 중인 건강기능식품, 한약 또는 생약 제품을 알려주세요.", 214, "context", assess),
        Q("jaundice.alcohol_pattern", "Alcohol Pattern", "string", "alcohol-pattern",
          "최근 음주한 주종, 한 번에 마시는 양, 빈도와 마지막 음주 시점을 알려주세요.", 213, "context", assess),
        Q("jaundice.acetaminophen_exposure", "Acetaminophen Exposure", "string", "acetaminophen-exposure",
          "최근 아세트아미노펜 성분 약을 복용했다면 제품, 1회량, 횟수와 기간을 알려주세요.", 212, "context", assess),
        Q("jaundice.blood_body_fluid_needle_exposure", "Blood Body Fluid or Needle Exposure", "string", "blood-exposure",
          "최근 혈액·체액 접촉, 주사침, 문신 또는 피어싱 노출이 있었나요?", 211, "context", assess),
        Q("jaundice.travel_food_water_exposure", "Travel Food or Water Exposure", "string", "travel-food-water",
          "최근 여행이나 평소와 다른 음식·물 섭취가 있었다면 장소와 시기를 알려주세요.", 210, "context", assess),
        Q("jaundice.close_contact_illness", "Close Contact Illness", "string", "close-contact-illness",
          "가까이 지낸 사람 중 비슷한 증상이나 간염 진단을 받은 사람이 있나요?", 209, "context", assess),
        Q("jaundice.recent_infection_illness", "Recent Infection or Illness", "string", "recent-illness",
          "황색 변화 전 최근 감염이나 다른 급성 질환이 있었나요?", 208, "context", assess),
        Q("jaundice.allergies", "Known Allergies", "string", "allergies",
          "알고 있는 약물 또는 물질 알레르기가 있나요?", 207, "context", assess),

        Q("jaundice.previous_assessment", "Previous Assessment", "string", "previous-assessment",
          "이 문제로 이전에 진찰이나 상담을 받은 적이 있다면 시기와 내용을 알려주세요.", 190, "previous", assess),
        Q("jaundice.latest_total_bilirubin", "Latest Total Bilirubin", "quantity", "total-bilirubin",
          "가장 최근 총빌리루빈 검사값이 있다면 수치와 단위를 알려주세요.", 189, "previous", assess,
          unit="mg/dL",
          terminology_binding={"system": "http://loinc.org", "code": "1975-2", "display": "Bilirubin.total [Mass/volume] in Serum or Plasma", "version": "2.82", "relation": "equivalent"}),
        Q("jaundice.latest_total_bilirubin_date", "Latest Total Bilirubin Date", "date_or_period", "total-bilirubin-date",
          "가장 최근 총빌리루빈 검사일을 알려주세요.", 188, "previous", assess),
        Q("jaundice.latest_direct_bilirubin", "Latest Direct Bilirubin", "quantity", "direct-bilirubin",
          "가장 최근 직접빌리루빈 검사값이 있다면 수치와 단위를 알려주세요.", 187, "previous", assess,
          unit="mg/dL",
          terminology_binding={"system": "http://loinc.org", "code": "1968-7", "display": "Bilirubin.direct [Mass/volume] in Serum or Plasma", "version": "2.82", "relation": "equivalent"}),
        Q("jaundice.latest_direct_bilirubin_date", "Latest Direct Bilirubin Date", "date_or_period", "direct-bilirubin-date",
          "가장 최근 직접빌리루빈 검사일을 알려주세요.", 186, "previous", assess),
        Q("jaundice.other_previous_tests", "Other Previous Tests", "string", "other-tests",
          "그 밖에 관련 혈액검사 결과가 있다면 검사명, 결과, 단위와 기준범위를 알려주세요.", 185, "previous", assess),
        Q("jaundice.prior_imaging", "Prior Imaging", "string", "prior-imaging",
          "관련 초음파, CT, MRI 또는 다른 영상검사를 받았다면 시기와 결과를 알려주세요.", 184, "previous", assess),
        Q("jaundice.previous_strategy", "Previous Strategy", "string", "previous-strategy",
          "이 증상에 대해 전에 받은 안내나 치료가 있다면 알려주세요.", 183, "previous", assess),
        Q("jaundice.previous_response", "Previous Response", "string", "previous-response",
          "이전 안내나 치료 후 좋아진 점과 남은 문제를 알려주세요.", 182, "previous", assess),

        Q("jaundice.accessibility_need", "Accessibility Need", "string", "accessibility-need",
          "문진이나 진료에 필요한 언어, 청각, 시각, 인지, 이동 또는 보호자 지원이 있나요?", 110, "handoff", handoff),
        Q("jaundice.patient_concern", "Patient Concern", "string", "patient-concern",
          "현재 가장 걱정되는 점은 무엇인가요?", 100, "handoff", handoff),
        Q("jaundice.expected_help", "Expected Help", "string", "expected-help",
          "이번 진료에서 의료진에게 가장 받고 싶은 도움은 무엇인가요?", 99, "handoff", handoff),
        Q("jaundice.additional_comment", "Additional Comment", "string", "additional-comment",
          "질문에 없지만 의료진에게 추가로 전달할 내용이 있나요?", 90, "handoff", handoff),
    ]
    rules = [
        safety_rule(P, "reduced-consciousness", {"fact": "jaundice.current_reduced_consciousness", "equals": True}, "emergency", 1400),
        safety_rule(P, "new-confusion", {"fact": "jaundice.new_confusion", "equals": True}, "emergency", 1399),
        safety_rule(P, "collapse", {"fact": "jaundice.collapse", "equals": True}, "emergency", 1398),
        safety_rule(P, "ruq-pain-fever-rigors", {"all": [{"fact": "jaundice.severe_right_upper_abdominal_pain", "equals": True}, {"any": [{"fact": "jaundice.fever", "equals": True}, {"fact": "jaundice.rigors", "equals": True}]}]}, "urgent", 1397),
        safety_rule(P, "vomiting-dehydration", {"all": [{"fact": "jaundice.repeated_vomiting", "equals": True}, {"fact": "jaundice.unable_to_keep_fluids", "equals": True}, {"fact": "jaundice.markedly_reduced_urine", "equals": True}]}, "urgent", 1396),
        safety_rule(P, "gastrointestinal-bleeding", {"any": [{"fact": "jaundice.vomiting_blood", "equals": True}, {"fact": "jaundice.black_or_bloody_stool", "equals": True}, {"fact": "jaundice.unexplained_bleeding", "equals": True}]}, "emergency", 1395),
        safety_rule(P, "toxic-exposure", {"fact": "jaundice.suspected_overdose_or_toxic_exposure", "equals": True}, "emergency", 1394),
        safety_rule(P, "newborn-jaundice", {"all": [{"fact": "jaundice.newborn_under_28_days", "equals": True}, {"fact": "jaundice.newborn_poor_feeding", "equals": False}, {"fact": "jaundice.newborn_difficult_to_wake", "equals": False}]}, "urgent", 1393),
        safety_rule(P, "newborn-unwell", {"all": [{"fact": "jaundice.newborn_under_28_days", "equals": True}, {"any": [{"fact": "jaundice.newborn_poor_feeding", "equals": True}, {"fact": "jaundice.newborn_difficult_to_wake", "equals": True}]}]}, "emergency", 1392),
        safety_rule(P, "pregnancy-postpartum", {"fact": "jaundice.pregnant_or_postpartum", "in": ["pregnant", "postpartum_6_weeks"]}, "urgent", 1391),
        safety_rule(P, "rapidly-worsening", {"fact": "jaundice.rapidly_worsening_yellowing", "equals": True}, "urgent", 1390),
    ]
    return {
        "id": "knowledge.generated.jaundice", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-jaundice-research",
        "default_refresh": {**default_refresh(), "last_assessed_at": "2026-08-03", "next_monitor_at": "2026-08-04", "next_full_review_at": "2027-01-30"},
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def completion(document):
    safety_facts = []
    def collect(condition):
        if "fact" in condition and condition["fact"] not in safety_facts:
            safety_facts.append(condition["fact"])
        for operator in ("all", "any"):
            for child in condition.get(operator, []): collect(child)
    for rule in document["safety_rules"]: collect(rule["when"])
    core = [item["fact"]["id"] for item in document["entries"] if item["fact"]["id"] not in {
        "jaundice.pain_location", "jaundice.pain_nrs", "jaundice.measured_temperature",
        "jaundice.vomiting_count", "jaundice.itching_impact",
    }]
    return {
        "id": "policy.primary-care-jaundice-completion", "version": VERSION,
        "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"],
        "required_facts": {"always": safety_facts + [item for item in core if item not in safety_facts], "routine": []},
        "conditional_required_facts": [
            {"when": {"fact": "jaundice.abdominal_pain", "equals": True}, "required_facts": ["jaundice.pain_location", "jaundice.pain_nrs"]},
            {"when": {"fact": "jaundice.fever", "equals": True}, "required_facts": ["jaundice.measured_temperature"]},
            {"when": {"fact": "jaundice.repeated_vomiting", "equals": True}, "required_facts": ["jaundice.vomiting_count"]},
            {"when": {"fact": "jaundice.itching", "equals": True}, "required_facts": ["jaundice.itching_impact"]},
        ],
        "clarification_facts_by_rule": {}, "question_budget": {"routine": 72, "clarify": 12},
        "provenance": provenance(SOURCES),
    }


def source_documents():
    artifacts = [
        {"id": SOURCES[0], "kind": "official_korean_clinical_guideline_metadata", "publisher": "Korea Disease Control and Prevention Agency", "title": "2026년도 바이러스 간염 관리지침(A형·B형·C형·E형)", "version": "2026-05-15", "url": "https://www.kdca.go.kr/bbs/kdca/55/309601/artclView.do", "language": "ko", "digest": "official_korean_viral_hepatitis_context_and_exposure_metadata_verified_2026-08-03", "license_status": "KOGL_type_4_metadata_and_summary_only_no_redistribution", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[1], "kind": "official_public_health_guidance_metadata", "publisher": "NHS", "title": "Jaundice", "version": "reviewed-2024-01-22", "url": "https://www.nhs.uk/conditions/jaundice/", "language": "en", "digest": "official_yellow_skin_sclera_dark_urine_pale_stool_pruritus_and_urgent_assessment_verified_2026-08-03", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[2], "kind": "official_public_health_guidance_metadata", "publisher": "US Centers for Disease Control and Prevention", "title": "Clinical Signs and Symptoms of Hepatitis B", "version": "2025-11-28", "url": "https://www.cdc.gov/hepatitis-b/hcp/clinical-signs/index.html", "language": "en", "digest": "official_jaundice_dark_urine_clay_stool_fatigue_fever_abdominal_pain_nausea_vomiting_appetite_and_exposure_context_verified_2026-08-03", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[3], "kind": "official_clinical_guideline_metadata", "publisher": "NICE", "title": "Suspected cancer: recognition and referral - jaundice recommendations", "version": "NG12-updated-2026-04-15", "url": "https://www.nice.org.uk/guidance/ng12/chapter/recommendations-organised-by-site-of-cancer", "language": "en", "digest": "official_adult_jaundice_time_sensitive_signal_verified_without_korean_pathway_projection_2026-08-03", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "nice_guidance", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[4], "kind": "official_clinical_guideline_metadata", "publisher": "NICE", "title": "Jaundice in newborn babies under 28 days", "version": "CG98-updated-2023-10-31", "url": "https://www.nice.org.uk/guidance/cg98", "language": "en", "digest": "official_newborn_age_detection_measurement_visibility_and_underlying_disease_context_verified_2026-08-03", "license_status": "metadata_and_summary_only", "complete": False, "monitor_profile": "nice_guidance", "last_monitored_at": "2026-08-03", "monitor_result": "current"},
        {"id": SOURCES[5], "kind": "terminology_service_verification", "publisher": "STOM", "title": "Jaundice terminology verification", "version": "LOINC-2.82_SNOMEDCT-observed-20260801", "url": "http://localhost:8088/fhir", "language": "en", "digest": "snomed_18165001_418290006_and_loinc_1975-2_1968-7_1971-1_72514-3_verified", "license_status": "licensed_lookup_metadata_only", "complete": False, "monitor_profile": "terminology_server", "last_monitored_at": "2026-08-03", "monitor_result": "verified_active_baseline_change_observed"},
    ]
    research = {"id": "source-manifest.primary-care-jaundice-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance(SOURCES)}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.jaundice", "generated_clinical_knowledge", "knowledge/generated/hepatology/jaundice/jaundice.json", True),
        ("source.mapping.jaundice", "terminology_mapping", "mappings/terminology/snomed-mrcm-jaundice.json", False),
        ("source.external.jaundice", "external_source_manifest", "sources/manifests/primary-care-jaundice-research.json", False),
        ("source.policy.jaundice", "runtime_policy", "policies/primary-care-jaundice-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-jaundice", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def routine_state():
    values = {}
    boolean_true = {"jaundice.scleral_yellowing", "jaundice.dark_urine", "jaundice.itching"}
    for item in fragment()["entries"]:
        fact = item["fact"]
        fid, value_type = fact["id"], fact["value_type"]
        if value_type == "boolean": value = fid in boolean_true
        elif value_type == "integer": value = 0
        elif value_type == "quantity": value = "0.8"
        elif value_type == "date_or_period": value = "2일 전"
        elif value_type == "coded": value = fact.get("allowed_values", ["unknown"])[0]
        elif value_type == "coded_or_string": value = fact.get("allowed_values", ["other"])[0]
        else: value = "없음"
        values[fid] = {"value": value}
    values.update({
        "jaundice.presentation": {"value": "yellow_sclera"}, "jaundice.information_source": {"value": "patient"},
        "jaundice.source_reliability": {"value": "reliable"}, "jaundice.noticed_by": {"value": "본인"},
        "jaundice.first_onset": {"value": "2일 전"}, "jaundice.latest_observed": {"value": "오늘"},
        "jaundice.course": {"value": "unchanged"}, "jaundice.pregnant_or_postpartum": {"value": "not_applicable"},
        "jaundice.observation_conditions": {"value": "낮 자연광에서 거울로 확인"},
        "jaundice.visibility_uncertainty": {"value": "없음"}, "jaundice.itching_impact": {"value": "잠들기 조금 어려움"},
        "jaundice.appetite_reduction": {"value": "slightly_reduced"}, "jaundice.fatigue": {"value": "평소보다 약간 피로"},
        "jaundice.latest_total_bilirubin": {"value": "0.8"},
        "jaundice.latest_direct_bilirubin": {"value": "0.2"},
        "jaundice.daily_function_impact": {"value": "일상 활동은 가능"}, "jaundice.current_medicines": {"value": "복용약 없음"},
        "jaundice.previous_assessment": {"value": "없음"}, "jaundice.patient_concern": {"value": "갑자기 눈이 노래진 이유"},
        "jaundice.expected_help": {"value": "진료 전 필요한 정보 전달"}, "jaundice.additional_comment": {"value": "없음"},
    })
    return values


def simulations():
    cases = {}
    cases["JAUNDICE-VAGUE-REMOTE-FIRST-VISIT.json"] = {"id": "JAUNDICE-VAGUE-REMOTE-FIRST-VISIT", "simulation_language": "ko", "persona": {"age": 46}, "encounter_context": {"care_setting": "telemedicine", "encounter_type": "new_encounter", "interview_initiator": "patient", "interview_mode": "video", "available_information": [], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "이틀 전부터 눈 흰자가 노랗고 소변색이 진해진 것 같습니다."}, "hidden_state": routine_state(), "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"jaundice.scleral_yellowing": True, "jaundice.dark_urine": True}, "expected_max_turns": 72, "forbidden_assertions": ["diagnosis.hepatitis", "diagnosis.biliary_obstruction", "recommendation.liver_test"]}, "provenance": provenance(SOURCES)}
    absent = routine_state(); absent.pop("jaundice.latest_observed"); absent.pop("jaundice.prior_imaging")
    behavior = {"jaundice.latest_observed": {"dataAbsentReason": "asked-unknown"}, "jaundice.prior_imaging": {"dataAbsentReason": "asked-declined"}}
    cases["JAUNDICE-CONFLICT-DATA-ABSENT.json"] = {"id": "JAUNDICE-CONFLICT-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 39}, "initial_statement": {"ko": "가족은 어제부터라는데 저는 잘 모르겠고 영상검사는 답하지 않겠습니다."}, "hidden_state": absent, "response_behavior": behavior, "expected": {"expected_data_absent_reasons": {k: v["dataAbsentReason"] for k, v in behavior.items()}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 72, "forbidden_assertions": ["jaundice.latest_observed.never"]}, "provenance": provenance(SOURCES)}
    proxy = routine_state(); proxy.update({"jaundice.information_source": {"value": "caregiver"}, "jaundice.source_reliability": {"value": "partly_reliable"}, "jaundice.accessibility_need": {"value": "청각 지원과 보호자 동행"}})
    cases["JAUNDICE-OLDER-PROXY-ACCESSIBILITY.json"] = {"id": "JAUNDICE-OLDER-PROXY-ACCESSIBILITY", "simulation_language": "ko", "persona": {"age": 84}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "chat", "available_information": ["caregiver_report"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "아버지 눈이 노랗게 보여 대신 답합니다. 잘 못 들으셔서 제가 같이 있어야 합니다."}, "hidden_state": proxy, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"jaundice.information_source": "caregiver"}, "expected_max_turns": 72, "forbidden_assertions": ["diagnosis.liver_failure"]}, "provenance": provenance(SOURCES)}
    safety_cases = [
        ("REDUCED-CONSCIOUSNESS", {"jaundice.current_reduced_consciousness": True}, "emergency", "rule.jaundice.safety.reduced-consciousness"),
        ("NEW-CONFUSION", {"jaundice.new_confusion": True}, "emergency", "rule.jaundice.safety.new-confusion"),
        ("COLLAPSE", {"jaundice.collapse": True}, "emergency", "rule.jaundice.safety.collapse"),
        ("RUQ-FEVER", {"jaundice.severe_right_upper_abdominal_pain": True, "jaundice.fever": True}, "urgent", "rule.jaundice.safety.ruq-pain-fever-rigors"),
        ("DEHYDRATION", {"jaundice.repeated_vomiting": True, "jaundice.unable_to_keep_fluids": True, "jaundice.markedly_reduced_urine": True}, "urgent", "rule.jaundice.safety.vomiting-dehydration"),
        ("BLEEDING", {"jaundice.vomiting_blood": True}, "emergency", "rule.jaundice.safety.gastrointestinal-bleeding"),
        ("TOXIC-EXPOSURE", {"jaundice.suspected_overdose_or_toxic_exposure": True}, "emergency", "rule.jaundice.safety.toxic-exposure"),
        ("NEWBORN", {"jaundice.newborn_under_28_days": True}, "urgent", "rule.jaundice.safety.newborn-jaundice"),
        ("NEWBORN-UNWELL", {"jaundice.newborn_under_28_days": True, "jaundice.newborn_poor_feeding": True}, "emergency", "rule.jaundice.safety.newborn-unwell"),
        ("PREGNANCY", {"jaundice.pregnant_or_postpartum": "pregnant"}, "urgent", "rule.jaundice.safety.pregnancy-postpartum"),
        ("RAPID-WORSENING", {"jaundice.rapidly_worsening_yellowing": True}, "urgent", "rule.jaundice.safety.rapidly-worsening"),
    ]
    for key, updates, level, rule in safety_cases:
        state = routine_state()
        for fact, value in updates.items(): state[fact] = {"value": value}
        cases[f"JAUNDICE-{key}.json"] = {"id": f"JAUNDICE-{key}", "simulation_language": "ko", "persona": {"age": 55}, "initial_statement": {"ko": "눈과 피부가 노랗게 보이고 지금 확인이 필요한 증상이 있습니다."}, "hidden_state": state, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule], "expected_max_turns": 20, "forbidden_assertions": ["diagnosis.hepatitis", "diagnosis.cholangitis", "recommendation.imaging"]}, "provenance": provenance(SOURCES)}
    follow = routine_state(); follow.update({"jaundice.presentation": {"value": "abnormal_test"}, "jaundice.latest_total_bilirubin": {"value": "3.2"}, "jaundice.latest_total_bilirubin_date": {"value": "2026-08-01"}, "jaundice.latest_direct_bilirubin": {"value": "1.8"}, "jaundice.latest_direct_bilirubin_date": {"value": "2026-08-01"}, "jaundice.prior_imaging": {"value": "합성 초음파 보고서 첨부, 세부 해석은 모름"}})
    cases["JAUNDICE-SPECIALTY-FOLLOWUP-SYNTHETIC-RESULT.json"] = {"id": "JAUNDICE-SPECIALTY-FOLLOWUP-SYNTHETIC-RESULT", "simulation_language": "ko", "persona": {"age": 63}, "encounter_context": {"care_setting": "specialist_clinic", "encounter_type": "follow_up", "interview_initiator": "patient", "interview_mode": "chat", "available_information": ["synthetic_lab", "synthetic_report"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "재진 전 합성 검사값과 초음파 보고 내용을 정리하려고 합니다."}, "hidden_state": follow, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"jaundice.latest_total_bilirubin": {"amount": 3.2, "unit": "mg/dL"}}, "expected_max_turns": 72, "forbidden_assertions": ["interpretation.ultrasound", "diagnosis.obstruction"]}, "provenance": provenance(SOURCES)}
    return cases


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Jaundice", intents=[
        (I[0], "Characterize Jaundice"), (I[1], "Screen Jaundice Safety"),
        (I[2], "Assess Jaundice Context"), (I[3], "Prepare Jaundice Handoff")])
    primary, research = source_documents()
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"source": "STOM localhost:8088/fhir", "loinc_version": "2.82", "snomed_ct_observed_version": "http://snomed.info/sct/900000000000207008/version/20260801", "repository_mapping_baseline": "http://snomed.info/sct/900000000000207008/version/20260701"},
        "verified_focus_concept": {"code": "18165001", "display": "Jaundice (finding)", "active": True, "use": "rfe_indexing_only_not_diagnosis"},
        "verified_related_concepts": [{"code": "418290006", "display": "Itching (finding)", "active": True}],
        "verified_exact_questions": [
            {"fact_id": "jaundice.pain_nrs", "code": "72514-3", "display": "Pain severity - 0-10 verbal numeric rating [Score] - Reported", "relation": "equivalent"},
            {"fact_id": "jaundice.latest_total_bilirubin", "code": "1975-2", "display": "Bilirubin.total [Mass/volume] in Serum or Plasma", "relation": "equivalent"},
            {"fact_id": "jaundice.latest_direct_bilirubin", "code": "1968-7", "display": "Bilirubin.direct [Mass/volume] in Serum or Plasma", "relation": "equivalent"},
        ],
        "verified_reference_not_used": [{"code": "1971-1", "display": "Bilirubin.indirect [Mass/volume] in Serum or Plasma", "reason": "no_distinct_atomic_fact_in_current_package"}],
        "atomicity": {"answer_bearing_questions": len(generated["entries"]), "compound_exact_mapping_allowed": False, "source_defined_fixed_questionnaire_excluded": True},
        "validation": {"method": "build_time_local_fhir_lookup", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "clinical_rule_authority": False, "result": "provisional_pass_with_snomed_baseline_change_trigger"},
        "provenance": provenance([SOURCES[5]])}
    for path, document in [
        ("knowledge/base/primary-care-jaundice.json", graph),
        ("rules/base/primary-care-jaundice.json", rules),
        ("knowledge/generated/hepatology/jaundice/jaundice.json", generated),
        ("mappings/terminology/snomed-mrcm-jaundice.json", mapping),
        ("sources/manifests/primary-care-jaundice.json", primary),
        ("sources/manifests/primary-care-jaundice-research.json", research),
        ("policies/primary-care-jaundice-completion.json", completion(generated)),
    ]: write_json(path, document)
    for filename, case in simulations().items():
        write_json(f"simulation/patients/hepatology/jaundice/{filename}", case)


if __name__ == "__main__":
    main()
