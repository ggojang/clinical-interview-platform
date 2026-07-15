#!/usr/bin/env python3
"""Materialize unreviewed memory and cognitive-concern knowledge."""
from profile_support import *

P = "memory-cognitive-concern"
RFE = "rfe.memory_cognitive_concern"
M = "mapping.snomed-mrcm.memory-cognitive-concern"
SN = "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = [
    "source.nice.ng97.dementia.2018", "source.nice.cg103.delirium.2023",
    "source.nhs.memory-loss.2023", "source.nhs.sudden-confusion.2026",
    "source.nhs.stroke-symptoms.2024", "source.nhs.dementia-symptoms.2023",
    "source.stom.memory-cognitive.20260715",
]
G = {k: f"group.cognition.{k}" for k in (
    "routing", "shared-safety", "common", "memory", "acute-confusion",
    "executive-language", "behavior-perception", "function-safety",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
D = ["intent.differentiate_common_causes"]
R = ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("cognition.primary_concern_group", "Primary Cognitive Concern Group", "coded", "primary-group", "가장 걱정되는 변화는 기억력, 갑작스러운 혼란·집중 저하, 말하기·계획하기, 행동·기분·환각, 일상 기능·안전 중 무엇인가요?", 160, [G["routing"]], C, allowed_values=["memory", "acute_confusion", "executive_language", "behavior_perception", "function_safety", "other_unclear"]),

        Q("cognition.sudden_confusion_hours_or_days", "Sudden Confusion over Hours or Days", "boolean", "sudden-confusion", "몇 시간 또는 며칠 사이에 갑자기 혼란스러워지거나 평소와 확연히 달라졌나요?", 159, [G["shared-safety"], G["acute-confusion"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "130987000"}, mrcm_ref=M),
        Q("cognition.stroke_fast_or_focal_neurology", "Cognitive Change with Stroke Warning Features", "boolean", "stroke-features", "갑자기 얼굴 한쪽 처짐, 한쪽 팔·다리 힘 빠짐·저림, 말이 어눌하거나 이해하기 어려움이 생겼나요?", 158, [G["shared-safety"]], S, safety_relevant=True),
        Q("cognition.reduced_consciousness_or_difficult_to_wake", "Reduced Consciousness or Difficult to Wake", "boolean", "reduced-consciousness", "깨우기 어렵거나 의식이 흐려 대화가 거의 되지 않나요?", 157, [G["shared-safety"], G["acute-confusion"]], S, safety_relevant=True),
        Q("cognition.new_seizure", "New Seizure with Cognitive Change", "boolean", "seizure", "새로 경련하거나 몸이 떨린 뒤 의식·기억이 돌아오지 않았나요?", 156, [G["shared-safety"]], S, safety_relevant=True),
        Q("cognition.sudden_severe_headache_or_head_injury", "Severe Headache or Head Injury with Cognitive Change", "boolean", "headache-head-injury", "갑작스러운 매우 심한 두통이 있거나 머리를 다친 뒤 기억·행동·의식이 변했나요?", 155, [G["shared-safety"]], S, safety_relevant=True),
        Q("cognition.severe_infection_or_systemic_illness", "Severe Infection or Systemic Illness with Confusion", "boolean", "systemic-illness", "혼란과 함께 고열·심한 오한·호흡곤란·심한 처짐 등 전신 상태가 매우 나쁜가요?", 154, [G["shared-safety"], G["acute-confusion"]], S, safety_relevant=True),
        Q("cognition.possible_severe_hypoglycemia", "Possible Severe Hypoglycemia with Confusion", "boolean", "hypoglycemia", "당뇨가 있으면서 식은땀·떨림·심한 졸림·혼란이 있고 혈당이 매우 낮거나 측정할 수 없나요?", 153, [G["shared-safety"], G["acute-confusion"]], S, safety_relevant=True),
        Q("cognition.possible_carbon_monoxide_cluster", "Possible Carbon Monoxide Exposure Cluster", "boolean", "carbon-monoxide", "같은 공간의 다른 사람도 두통·어지럼·메스꺼움·혼란이 있고 난방기나 연소기구를 사용했나요?", 152, [G["shared-safety"], G["acute-confusion"]], S, safety_relevant=True),
        Q("cognition.overdose_intoxication_or_withdrawal", "Overdose Intoxication or Withdrawal Concern", "boolean", "substance-emergency", "약을 과량 복용했거나 술·약물 중독 또는 갑작스러운 금단이 의심되나요?", 151, [G["shared-safety"], G["acute-confusion"]], S, safety_relevant=True),
        Q("cognition.immediate_self_harm_or_harm_to_others", "Immediate Self-harm or Harm Risk", "boolean", "immediate-harm", "지금 자신이나 다른 사람을 해칠 생각·계획이 있거나 안전을 지키기 어렵나요?", 150, [G["shared-safety"], G["behavior-perception"]], S, safety_relevant=True),
        Q("cognition.wandering_missing_or_immediate_environmental_danger", "Wandering or Immediate Environmental Danger", "boolean", "wandering-danger", "길을 잃어 실종될 위험이 있거나 불·가스·교통 등 즉각적인 환경 위험에 노출돼 있나요?", 149, [G["shared-safety"], G["function-safety"]], S, safety_relevant=True),
        Q("cognition.unable_to_eat_drink_or_take_essential_medicine", "Unable to Meet Essential Care Needs", "boolean", "essential-care-failure", "혼자서는 물·음식을 거의 못 먹거나 꼭 필요한 약을 전혀 복용하지 못하는 상태인가요?", 148, [G["shared-safety"], G["function-safety"]], S, safety_relevant=True),
        Q("cognition.dangerous_driving_cooking_finance_or_medication_event", "Recent Serious Functional Safety Event", "boolean", "functional-danger", "운전 사고·가스 방치·큰 금전 피해·약 중복 복용처럼 실제로 위험한 일이 최근 생겼나요?", 147, [G["shared-safety"], G["function-safety"]], S, safety_relevant=True),
        Q("cognition.rapid_progression_over_weeks_or_months", "Rapid Cognitive Progression over Weeks or Months", "boolean", "rapid-progression", "기억·사고·행동 문제가 몇 주 또는 몇 달 사이 빠르게 악화하고 있나요?", 146, [G["shared-safety"]], S, safety_relevant=True),
        Q("cognition.new_hallucination_delusion_with_danger", "New Hallucination or Delusion with Danger", "boolean", "dangerous-psychosis", "새로 환각·심한 의심이 생겨 극도로 흥분하거나 위험하게 행동하나요?", 145, [G["shared-safety"], G["behavior-perception"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "7011001"}, mrcm_ref=M),
        Q("cognition.falls_or_cannot_walk_safely", "Falls or Inability to Walk Safely", "boolean", "falls-mobility-danger", "갑자기 걷기 어려워졌거나 반복해서 넘어져 지금 혼자 이동하기 위험한가요?", 144, [G["shared-safety"], G["function-safety"]], S, safety_relevant=True),
        Q("cognition.abuse_neglect_exploitation_or_safeguarding_concern", "Cognitive Safeguarding Concern", "boolean", "safeguarding", "학대·방임·금전 착취가 의심되거나 돌봄 환경에서 현재 안전이 걱정되나요?", 143, [G["shared-safety"], G["function-safety"]], S, safety_relevant=True),

        Q("cognition.person_or_informant_reporting", "Person or Informant Reporting", "coded", "reporter", "이 변화를 주로 본 사람은 본인, 가족·보호자, 둘 다 중 누구인가요?", 135, [G["common"]], C, allowed_values=["self", "family_carer", "both", "other_unclear"]),
        Q("cognition.onset_duration_and_course", "Cognitive Onset Duration and Course", "string", "duration-course", "언제 처음 시작했고 서서히·갑자기 또는 계단식으로 변했는지 알려주세요.", 134, [G["common"]], C),
        Q("cognition.fluctuation_during_day", "Cognitive Fluctuation", "coded", "fluctuation", "증상이 하루 중 들쭉날쭉한가요, 비교적 일정한가요?", 133, [G["common"]], C, allowed_values=["marked_fluctuation", "mild_fluctuation", "stable", "unclear"]),
        Q("cognition.baseline_and_last_known_well", "Cognitive Baseline and Last Known Well", "string", "baseline", "평소 인지·기능 상태와 마지막으로 평소와 같았던 때를 알려주세요.", 132, [G["common"]], C),
        Q("cognition.education_language_and_literacy_context", "Education Language and Literacy Context", "string", "communication-context", "주로 사용하는 언어, 교육·문해 수준과 의사소통에 필요한 지원이 있나요?", 126, [G["common"]], R),
        Q("cognition.hearing_vision_and_sensory_aids", "Hearing Vision and Sensory Aids", "string", "sensory", "청력·시력 문제가 있거나 보청기·안경을 사용하는데 최근 제대로 사용하지 못했나요?", 125, [G["common"]], R),
        Q("cognition.current_medicines_and_recent_changes", "Medicines and Recent Changes", "string", "medicines", "현재 복용약과 최근 시작·중단·증량한 약, 수면제·진정제·항히스타민제 등을 알려주세요.", 124, [G["common"]], R),
        Q("cognition.alcohol_substance_and_withdrawal_context", "Alcohol Substance and Withdrawal Context", "string", "substance-context", "음주·기타 약물 사용과 최근 갑자기 줄이거나 끊은 일이 있나요?", 123, [G["common"]], R),
        Q("cognition.sleep_mood_stress_and_anxiety", "Sleep Mood Stress and Anxiety", "string", "sleep-mood", "수면 부족, 우울감·흥미 저하, 불안 또는 큰 스트레스가 있나요?", 122, [G["common"]], D),
        Q("cognition.medical_neurological_and_psychiatric_history", "Relevant Medical Neurological and Psychiatric History", "string", "medical-history", "뇌졸중·머리 외상·경련·파킨슨병·치매·정신질환과 다른 중요한 병력이 있나요?", 121, [G["common"]], R),
        Q("cognition.family_history_of_cognitive_disorder", "Family Cognitive History", "string", "family-history", "가족 중 치매나 비교적 이른 나이에 생긴 인지질환이 있었나요?", 112, [G["common"]], R),
        Q("cognition.other_detail_or_patient_priority", "Other Cognitive Detail or Priority", "string", "other-detail", "질문에 없지만 꼭 전달하고 싶은 변화나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("cognition.recent_event_memory", "Recent Event Memory", "string", "recent-memory", "최근 대화·약속·방문 내용을 잊거나 같은 질문을 반복하나요?", 120, [G["memory"]], C, terminology_binding={"system": SN, "code": "386807006"}, mrcm_ref=M),
        Q("cognition.misplacing_items_and_retracing", "Misplacing Items", "string", "misplacing", "물건을 자주 엉뚱한 곳에 두고 찾는 과정을 되짚기 어려운가요?", 119, [G["memory"]], C),
        Q("cognition.appointments_and_dates", "Appointments and Dates", "string", "appointments", "약속·날짜·해야 할 일을 기억하는 데 어떤 변화가 있나요?", 118, [G["memory"]], C),
        Q("cognition.learning_new_information", "Learning New Information", "string", "new-learning", "새로운 기기 사용법이나 사람·장소 정보를 익히는 데 어려움이 있나요?", 117, [G["memory"]], C),
        Q("cognition.remote_memory_and_recognition", "Remote Memory and Recognition", "string", "remote-memory", "오래된 기억이나 가까운 사람·익숙한 장소를 알아보는 데 변화가 있나요?", 116, [G["memory"]], C),
        Q("cognition.memory_compensation_strategies", "Memory Compensation Strategies", "string", "memory-strategies", "메모·달력·휴대전화 알림이나 가족 도움을 얼마나 사용하나요?", 108, [G["memory"]], R),

        Q("cognition.attention_and_following_conversation", "Attention and Conversation Tracking", "string", "attention", "대화나 간단한 설명에 집중하고 순서를 따라가기 어려운가요?", 120, [G["acute-confusion"]], C, terminology_binding={"system": SN, "code": "386806002"}, mrcm_ref=M),
        Q("cognition.orientation_person_place_time", "Orientation to Person Place and Time", "string", "orientation", "자신이 누구인지, 어디에 있는지, 날짜·시간을 평소보다 더 헷갈리나요?", 119, [G["acute-confusion"]], C, terminology_binding={"system": SN, "code": "62476001"}, mrcm_ref=M),
        Q("cognition.sleep_wake_reversal_or_reduced_activity", "Sleep-wake or Activity Change", "string", "sleep-wake", "낮밤이 바뀌거나 평소보다 지나치게 처지고 반응·움직임이 느려졌나요?", 118, [G["acute-confusion"]], C),
        Q("cognition.recent_infection_pain_or_fever", "Recent Infection Pain or Fever", "string", "infection-pain", "최근 감염 증상, 발열, 심한 통증이 있었나요?", 117, [G["acute-confusion"]], D),
        Q("cognition.dehydration_nutrition_constipation_or_urinary_retention", "Basic Physiological Contributors", "string", "physiological-context", "탈수·식사 저하·변비·소변이 안 나오는 문제가 있나요?", 116, [G["acute-confusion"]], D),
        Q("cognition.recent_surgery_hospitalization_or_environment_change", "Recent Surgery Hospital or Environment Change", "string", "recent-care", "최근 수술·입원·마취 또는 거주 환경 변화가 있었나요?", 115, [G["acute-confusion"]], R),
        Q("cognition.delirium_assessment_already_done", "Delirium Assessment Status", "string", "delirium-assessment", "의료진이 4AT 등 급성 혼돈 평가를 시행했다면 언제 어떤 결과였나요?", 107, [G["acute-confusion"]], R),
        Q("cognition.prior_similar_confusional_episode", "Prior Confusional Episode", "string", "prior-confusion", "이전에 감염·입원·약 변화 때 비슷한 혼란이 있었나요?", 106, [G["acute-confusion"]], R),

        Q("cognition.word_finding_and_naming", "Word Finding and Naming", "string", "word-finding", "말하려는 단어가 잘 떠오르지 않거나 사물 이름을 대기 어려운가요?", 120, [G["executive-language"]], C, terminology_binding={"system": SN, "code": "286384007"}, mrcm_ref=M),
        Q("cognition.comprehension_reading_and_writing", "Comprehension Reading and Writing", "string", "language-detail", "말을 이해하거나 읽기·쓰기 능력에 변화가 있나요?", 119, [G["executive-language"]], C),
        Q("cognition.planning_problem_solving_and_multistep_tasks", "Planning and Multistep Tasks", "string", "planning", "요리·여행 준비처럼 여러 단계의 일을 계획하고 순서대로 하기 어려운가요?", 118, [G["executive-language"]], C),
        Q("cognition.judgement_and_decision_making", "Judgement and Decision Making", "string", "judgement", "판단력이 달라져 충동적 구매·의심스러운 계약·위험한 결정을 한 적이 있나요?", 117, [G["executive-language"]], R),
        Q("cognition.visuospatial_navigation_and_getting_lost", "Visuospatial Navigation", "string", "navigation", "익숙한 길에서 헤매거나 거리·방향·물건 위치를 판단하기 어려운가요?", 116, [G["executive-language"]], R),
        Q("cognition.calculation_money_and_technology", "Calculation Money and Technology", "string", "calculation", "계산, 돈 관리, 전화·리모컨 등 익숙한 기기 사용이 어려워졌나요?", 115, [G["executive-language"]], R),

        Q("cognition.depression_anxiety_apathy_or_irritability", "Mood Apathy and Irritability", "string", "mood-behavior", "우울·불안, 무관심, 쉽게 화냄 또는 감정 변화가 있나요?", 120, [G["behavior-perception"]], C),
        Q("cognition.personality_or_social_conduct_change", "Personality or Social Conduct Change", "string", "personality", "평소 성격·공감·예절·충동 조절이 눈에 띄게 달라졌나요?", 119, [G["behavior-perception"]], C),
        Q("cognition.hallucinations", "Hallucinations", "string", "hallucinations", "다른 사람에게 보이거나 들리지 않는 것을 보거나 듣는 일이 있나요?", 118, [G["behavior-perception"]], C, terminology_binding={"system": SN, "code": "7011001"}, mrcm_ref=M),
        Q("cognition.delusions_suspicion_or_misidentification", "Delusions Suspicion or Misidentification", "string", "delusions", "도둑맞았다는 강한 의심이나 가족을 다른 사람으로 착각하는 일이 있나요?", 117, [G["behavior-perception"]], C),
        Q("cognition.sleep_behavior_and_dream_enactment", "Sleep Behavior and Dream Enactment", "string", "sleep-behavior", "잠결에 소리치거나 꿈대로 움직임, 심한 낮 졸림 또는 수면 변화가 있나요?", 116, [G["behavior-perception"]], R),
        Q("cognition.movement_tremor_stiffness_or_slowing", "Movement Change", "string", "movement", "떨림·몸 뻣뻣함·동작 느려짐·보행 변화가 함께 있나요?", 115, [G["behavior-perception"]], R),

        Q("cognition.basic_activities_of_daily_living", "Basic Activities of Daily Living", "string", "basic-adl", "씻기·옷 입기·식사·화장실 사용에 도움이 필요한가요?", 120, [G["function-safety"]], R),
        Q("cognition.instrumental_activities_of_daily_living", "Instrumental Activities of Daily Living", "string", "instrumental-adl", "장보기·요리·청소·전화·교통 이용에 어떤 도움이 필요한가요?", 119, [G["function-safety"]], R),
        Q("cognition.medication_management", "Medication Management Function", "string", "medication-function", "약을 빠뜨리거나 중복 복용하지 않고 스스로 관리할 수 있나요?", 118, [G["function-safety"]], R),
        Q("cognition.financial_management", "Financial Management Function", "string", "financial-function", "공과금·은행 업무·현금 관리를 안전하게 할 수 있나요?", 117, [G["function-safety"]], R),
        Q("cognition.driving_and_transport_safety", "Driving and Transport Safety", "string", "driving", "운전 중 길을 잃거나 사고·접촉이 늘었고 다른 교통수단은 안전하게 이용하나요?", 116, [G["function-safety"]], R),
        Q("cognition.living_arrangement_and_time_alone", "Living Arrangement and Time Alone", "string", "living-arrangement", "누구와 살며 혼자 지내는 시간과 비상시에 연락할 사람을 알려주세요.", 115, [G["function-safety"]], R),
        Q("cognition.carer_support_and_burden", "Carer Support and Burden", "string", "carer-support", "도움을 주는 사람과 돌봄 부담·휴식·추가 지원 필요를 알려주세요.", 114, [G["function-safety"]], R),
        Q("cognition.prior_cognitive_test_and_specialist_assessment", "Prior Cognitive and Specialist Assessment", "string", "prior-assessment", "이전에 검증된 인지검사나 기억클리닉 평가를 받았다면 시기와 결과를 알려주세요.", 108, [G["function-safety"]], R),
    ]
    rules = [
        safety_rule(P, "sudden-confusion", {"fact": "cognition.sudden_confusion_hours_or_days", "equals": True}, "emergency", 1000),
        safety_rule(P, "stroke-features", {"fact": "cognition.stroke_fast_or_focal_neurology", "equals": True}, "emergency", 1000),
        safety_rule(P, "reduced-consciousness", {"fact": "cognition.reduced_consciousness_or_difficult_to_wake", "equals": True}, "emergency", 1000),
        safety_rule(P, "seizure", {"fact": "cognition.new_seizure", "equals": True}, "emergency", 1000),
        safety_rule(P, "headache-head-injury", {"fact": "cognition.sudden_severe_headache_or_head_injury", "equals": True}, "emergency", 1000),
        safety_rule(P, "systemic-illness", {"fact": "cognition.severe_infection_or_systemic_illness", "equals": True}, "emergency", 1000),
        safety_rule(P, "hypoglycemia", {"fact": "cognition.possible_severe_hypoglycemia", "equals": True}, "emergency", 1000),
        safety_rule(P, "carbon-monoxide", {"fact": "cognition.possible_carbon_monoxide_cluster", "equals": True}, "emergency", 1000),
        safety_rule(P, "substance-emergency", {"fact": "cognition.overdose_intoxication_or_withdrawal", "equals": True}, "emergency", 1000),
        safety_rule(P, "immediate-harm", {"fact": "cognition.immediate_self_harm_or_harm_to_others", "equals": True}, "emergency", 1000),
        safety_rule(P, "wandering-danger", {"fact": "cognition.wandering_missing_or_immediate_environmental_danger", "equals": True}, "emergency", 1000),
        safety_rule(P, "essential-care-failure", {"fact": "cognition.unable_to_eat_drink_or_take_essential_medicine", "equals": True}, "urgent", 980),
        safety_rule(P, "functional-danger", {"fact": "cognition.dangerous_driving_cooking_finance_or_medication_event", "equals": True}, "urgent", 970),
        safety_rule(P, "rapid-progression", {"fact": "cognition.rapid_progression_over_weeks_or_months", "equals": True}, "urgent", 970),
        safety_rule(P, "dangerous-psychosis", {"fact": "cognition.new_hallucination_delusion_with_danger", "equals": True}, "emergency", 1000),
        safety_rule(P, "falls-mobility-danger", {"fact": "cognition.falls_or_cannot_walk_safely", "equals": True}, "urgent", 970),
        safety_rule(P, "safeguarding", {"fact": "cognition.abuse_neglect_exploitation_or_safeguarding_concern", "equals": True}, "urgent", 990),
    ]
    return {"id": "knowledge.generated.memory-cognitive-concern", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-memory-cognitive-concern-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="cognition.primary_concern_group", question_budget=56, source_refs=SOURCES)
    branches = {
        "memory": ["cognition.recent_event_memory", "cognition.misplacing_items_and_retracing", "cognition.appointments_and_dates", "cognition.learning_new_information", "cognition.remote_memory_and_recognition", "cognition.memory_compensation_strategies"],
        "acute_confusion": ["cognition.attention_and_following_conversation", "cognition.orientation_person_place_time", "cognition.sleep_wake_reversal_or_reduced_activity", "cognition.recent_infection_pain_or_fever", "cognition.dehydration_nutrition_constipation_or_urinary_retention", "cognition.recent_surgery_hospitalization_or_environment_change", "cognition.delirium_assessment_already_done", "cognition.prior_similar_confusional_episode"],
        "executive_language": ["cognition.word_finding_and_naming", "cognition.comprehension_reading_and_writing", "cognition.planning_problem_solving_and_multistep_tasks", "cognition.judgement_and_decision_making", "cognition.visuospatial_navigation_and_getting_lost", "cognition.calculation_money_and_technology"],
        "behavior_perception": ["cognition.depression_anxiety_apathy_or_irritability", "cognition.personality_or_social_conduct_change", "cognition.hallucinations", "cognition.delusions_suspicion_or_misidentification", "cognition.sleep_behavior_and_dream_enactment", "cognition.movement_tremor_stiffness_or_slowing"],
        "function_safety": ["cognition.basic_activities_of_daily_living", "cognition.instrumental_activities_of_daily_living", "cognition.medication_management", "cognition.financial_management", "cognition.driving_and_transport_safety", "cognition.living_arrangement_and_time_alone", "cognition.carer_support_and_burden", "cognition.prior_cognitive_test_and_specialist_assessment"],
        "other_unclear": ["cognition.other_detail_or_patient_priority"],
    }
    policy["required_facts"]["routine"] = ["cognition.person_or_informant_reporting", "cognition.onset_duration_and_course", "cognition.fluctuation_during_day", "cognition.baseline_and_last_known_well", "cognition.hearing_vision_and_sensory_aids", "cognition.current_medicines_and_recent_changes", "cognition.sleep_mood_stress_and_anxiety", "cognition.medical_neurological_and_psychiatric_history", "cognition.other_detail_or_patient_priority"]
    policy["conditional_required_facts"] = [{"selector_fact": "cognition.primary_concern_group", "cases": branches}]
    return policy


def source_docs():
    defs = [
        ("source.nice.ng97.dementia.2018", "NICE", "Dementia: assessment, management and support", "NG97; accessed-2026-07-15", "https://www.nice.org.uk/guidance/ng97/chapter/Recommendations", "nice_guidance", 7, ["Initial assessment includes cognitive, behavioural and psychological symptoms and daily-life impact from the person and, if possible, someone who knows them well.", "Reversible causes include delirium, depression, sensory impairment and medicine-related cognitive impairment; a normal brief cognitive score alone does not exclude dementia."]),
        ("source.nice.cg103.delirium.2023", "NICE", "Delirium: prevention, diagnosis and management", "CG103; amended-2023", "https://www.nice.org.uk/guidance/cg103/chapter/Recommendations", "nice_guidance", 7, ["Recent hours-to-days change or fluctuation in cognition, perception, physical function or social behaviour indicates delirium assessment.", "A competent practitioner uses an appropriate validated tool and a qualified professional makes the final diagnosis."]),
        ("source.nhs.memory-loss.2023", "NHS", "Memory loss (amnesia)", "reviewed-2023-10-09", "https://www.nhs.uk/symptoms/memory-loss-amnesia/", "public_health_guidance", 7, ["Persistent memory problems affecting daily life warrant clinical assessment and may have treatable causes.", "An informant can help describe changes; this package does not diagnose their cause."]),
        ("source.nhs.sudden-confusion.2026", "NHS", "Sudden confusion (delirium)", "accessed-2026-07-15", "https://www.nhs.uk/symptoms/confusion/", "public_health_guidance", 7, ["Sudden confusion requires immediate medical assessment.", "Potential contexts include infection, stroke or TIA, low glucose, head injury, medicines, alcohol or drug exposure, carbon monoxide and seizures."]),
        ("source.nhs.stroke-symptoms.2024", "NHS", "Symptoms of a stroke", "reviewed-2024-09-12", "https://www.nhs.uk/conditions/stroke/symptoms/", "public_health_guidance", 7, ["Sudden face or arm weakness, speech difficulty, confusion, vision change, imbalance or severe headache require emergency assessment even if transient."]),
        ("source.nhs.dementia-symptoms.2023", "NHS", "Symptoms of dementia", "reviewed-2023-07-10", "https://www.nhs.uk/conditions/dementia/symptoms-and-diagnosis/symptoms/", "public_health_guidance", 7, ["Relevant domains include memory, concentration, familiar tasks, language, time or place orientation, mood, movement, behaviour and functional change."]),
        ("source.stom.memory-cognitive.20260715", "Infoclinic", "STOM memory and cognition terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", 30, ["STOM returned active candidates for memory impairment, impaired cognition, acute confusion, delirium, disorientation, word-finding difficulty, hallucinations and dementia.", "Finding site and Severity were allowed MRCM attributes for selected focus concepts; MRCM does not determine diagnosis or urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-15", "next_monitor_at": "2026-08-14" if days == 30 else "2026-07-22", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, days, assertions in defs]
    research = {"id": "source-manifest.primary-care-memory-cognitive-concern-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([item[0] for item in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.memory-cognitive", "generated_clinical_knowledge", "knowledge/generated/neurological/memory-cognitive-concern/memory-cognitive-concern.json", True), ("source.mapping.memory-cognitive", "terminology_mapping", "mappings/terminology/snomed-mrcm-memory-cognitive-concern.json", False), ("source.external.memory-cognitive", "external_source_manifest", "sources/manifests/primary-care-memory-cognitive-concern-research.json", False), ("source.policy.memory-cognitive", "runtime_policy", "policies/primary-care-memory-cognitive-concern-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-memory-cognitive-concern", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        hidden = {rule["when"]["fact"]: {"value": rule["when"]["equals"]}}
        key = rule["id"].split("safety.")[1]
        level = rule["then"]["safety_level"]
        out[f"COGNITION-{key.upper()}.json"] = {"id": f"COGNITION-{key.upper()}", "simulation_language": "ko", "persona": {"age": 50 + index}, "initial_statement": {"ko": "기억력이나 행동이 달라졌어요."}, "hidden_state": hidden, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 42, "forbidden_assertions": ["diagnosis.dementia", "diagnosis.delirium", "recommendation.start_cognitive_medication"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["memory"])
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}
    hidden = {}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        elif fact["value_type"] == "integer": hidden[fid] = {"value": 1}
        else: hidden[fid] = {"value": "없음"}
    hidden["cognition.primary_concern_group"] = {"value": "memory"}
    hidden["cognition.person_or_informant_reporting"] = {"value": "both"}
    declined = "cognition.current_medicines_and_recent_changes"
    hidden.pop(declined)
    out["COGNITION-MEMORY-DATA-ABSENT.json"] = {"id": "COGNITION-MEMORY-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 67}, "initial_statement": {"ko": "요즘 약속을 자주 잊어서 가족과 상담받으러 왔어요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 58, "forbidden_assertions": ["diagnosis.dementia", "diagnosis.mild_cognitive_impairment"]}, "provenance": provenance(["source.nice.ng97.dementia.2018", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Memory or Cognitive Concern", intents=[("intent.characterize_symptom", "Characterize Cognitive Change"), ("intent.screen_red_flags", "Screen Red Flags"), ("intent.differentiate_common_causes", "Assess Potential Contributors"), ("intent.risk_assessment", "Functional and Safety Assessment")])
    primary, research = source_docs()
    concepts = [("386807006", "Memory impairment (finding)", 20), ("386806002", "Impaired cognition (finding)", 20), ("130987000", "Acute confusion (finding)", 20), ("2776000", "Delirium (disorder)", 22), ("62476001", "Disorientated (finding)", 20), ("286384007", "Difficulty finding words (finding)", 20), ("7011001", "Hallucinations (finding)", 20), ("52448006", "Dementia (disorder)", 22)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["363698007", "246112005"], "validation": {"method": "build_time_live_mapping_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.memory-cognitive.20260715"])}
    documents = [("knowledge/base/primary-care-memory-cognitive-concern.json", graph), ("rules/base/primary-care-memory-cognitive-concern.json", rules), ("knowledge/generated/neurological/memory-cognitive-concern/memory-cognitive-concern.json", f), ("mappings/terminology/snomed-mrcm-memory-cognitive-concern.json", mapping), ("sources/manifests/primary-care-memory-cognitive-concern.json", primary), ("sources/manifests/primary-care-memory-cognitive-concern-research.json", research), ("policies/primary-care-memory-cognitive-concern-completion.json", completion(f))]
    for path, document in documents: write_json(path, document)
    for name, case in cases(f).items(): write_json("simulation/patients/neurological/memory-cognitive-concern/" + name, case)


if __name__ == "__main__": main()
