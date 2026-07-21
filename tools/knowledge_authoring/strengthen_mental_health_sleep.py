#!/usr/bin/env python3
"""Strengthen research-only mental-health/sleep clinician handoff knowledge."""
from __future__ import annotations

import json

import seed_mental_health_sleep
from profile_support import ROOT, completion_policy, entry, write_json


P = "mental-health-sleep"
FRAGMENT = "knowledge/generated/mental-health/mental-health-sleep/mental-health-sleep.json"
POLICY = "policies/primary-care-mental-health-sleep-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
RESEARCH = "sources/manifests/primary-care-mental-health-sleep-research.json"
CREATED = "2026-07-21T00:00:00Z"
SOURCES = [
    "source.nice.ng222.depression.2022",
    "source.nice.cg113.anxiety.2020",
    "source.nhs.urgent-mental-support.2026",
]
G = {key: f"group.mental-health-sleep.{key}" for key in (
    "routing", "course-detail", "mood-detail", "anxiety-detail",
    "sleep-detail", "treatment-detail", "social-context", "life-stage",
    "function-detail", "handoff",
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


def q(fact_id, display, value_type, key, wording, score, group, intents, **kwargs):
    return entry(
        P, fact_id, display, value_type, key, wording, score, key,
        [G[group]], intents=intents, **kwargs,
    )


def fragment() -> dict:
    doc = load(FRAGMENT)
    contexts = [
        "low_mood", "anxiety_or_worry", "panic", "sleep_problem",
        "stress_trauma_or_loss", "treatment_followup",
        "mania_or_psychosis_followup", "proxy_or_accessibility",
        "pregnancy_postpartum_or_life_stage", "mixed_or_unclear",
    ]
    additions = [
        q("mental_health.primary_context", "Primary Mental Health or Sleep Context", "coded", "primary-context", "가장 가까운 상황은 기분 저하, 불안·걱정, 공황, 수면 문제, 스트레스·충격·상실, 치료 추적, 조증·정신증 관련 추적, 보호자 대리·접근성 지원, 임신·산후·생애단계 관련, 또는 여러 문제·불분명 중 무엇인가요?", 132, "routing", C + R, allowed_values=contexts),
        q("mental_health.patient_words_first_change_and_main_concern", "Patient Description and Main Concern", "string", "patient-words", "본인의 표현으로 처음 달라졌다고 느낀 점, 지금 가장 힘든 점과 가장 걱정되는 점을 알려주세요.", 115, "course-detail", C),
        q("mental_health.first_latest_onset_course_previous_baseline_and_fluctuation", "Detailed Onset Course and Baseline", "string", "timeline", "처음과 가장 최근 변화의 날짜·상황, 서서히 또는 갑자기 시작했는지, 지속·반복·악화·호전 양상과 평소 상태를 알려주세요.", 114, "course-detail", C + R),
        q("mental_health.episode_frequency_duration_triggers_recovery_and_between_state", "Episode Pattern and Recovery", "string", "episode-pattern", "증상이나 발작적 에피소드의 빈도·지속시간, 직전 상황·유발요인, 회복 시간과 에피소드 사이 상태를 알려주세요.", 113, "course-detail", C + R),
        q("mental_health.symptom_intensity_variation_and_distress", "Symptom Intensity Variation and Distress", "string", "intensity-distress", "증상의 가장 약할 때와 심할 때의 정도, 하루 중 변화와 본인이 느끼는 고통의 정도를 알려주세요.", 112, "course-detail", C),
        q("mental_health.panic_frequency_duration_somatic_features_triggers_and_avoidance", "Detailed Panic Episode Features", "string", "panic-detail", "공황처럼 갑자기 몰려오는 증상이 있다면 횟수·지속시간, 신체 증상, 유발 상황, 회복과 이후 피하게 된 활동을 알려주세요.", 111, "anxiety-detail", C + R),
        q("mental_health.anxiety_topics_somatic_reassurance_seeking_and_control", "Anxiety Topics Somatic Symptoms and Reassurance", "string", "anxiety-detail", "걱정하는 주제, 함께 나타나는 신체 증상, 반복 확인·안심을 구하는 행동과 걱정을 조절하기 어려운 정도를 알려주세요.", 110, "anxiety-detail", C + R),
        q("mental_health.past_mood_elevation_reduced_sleep_energy_and_family_observation", "Past Mood Elevation and Collateral Observation", "string", "mood-elevation-history", "과거에도 잠을 거의 자지 않아도 에너지가 많거나 기분·말·활동이 비정상적으로 높아진 기간이 있었는지와 주변 사람이 본 변화를 알려주세요.", 109, "mood-detail", C + S),
        q("mental_health.coexisting_mental_physical_cognitive_and_pain_conditions", "Coexisting Mental Physical and Cognitive Conditions", "string", "coexisting-conditions", "함께 진단받거나 의심된 다른 정신건강, 신체질환, 통증, 인지·발달 문제와 현재 상태를 알려주세요.", 108, "life-stage", R + D),
        q("mental_health.prior_episodes_diagnoses_admissions_crisis_and_recovery", "Prior Episodes and Crisis History", "string", "prior-episodes", "이전 비슷한 시기, 진단, 응급·입원·위기지원 경험과 당시 회복까지의 경과를 알려주세요.", 107, "treatment-detail", R),
        q("mental_health.previous_counselling_psychotherapy_medicine_and_response", "Previous Treatment and Response", "string", "treatment-response", "이전 상담·심리치료·약물·기타 치료의 종류와 시기, 도움이 된 점·되지 않은 점과 부작용을 알려주세요.", 106, "treatment-detail", C + R),
        q("mental_health.current_medicine_product_dose_schedule_adherence_start_change_and_prescriber", "Current Mental Health Medicine Detail", "string", "medicine-detail", "정신건강·수면 관련 처방약, 일반약·보충제마다 제품/성분명, 용량·복용시간, 실제 복용, 시작·변경일과 처방자를 알려주세요.", 105, "treatment-detail", R),
        q("mental_health.medicine_benefit_side_effect_withdrawal_missed_dose_and_symptom_timing", "Medicine Effect and Symptom Timeline", "string", "medicine-effect", "약의 효과·부작용, 빠뜨리거나 갑자기 줄이거나 중단한 일과 기분·불안·수면·초조 변화의 시간관계를 알려주세요.", 104, "treatment-detail", R + S),
        q("mental_health.alcohol_caffeine_nicotine_prescribed_nonprescribed_and_recreational_substances", "Alcohol Caffeine Nicotine and Other Substance Context", "string", "substance-detail", "술, 카페인·에너지음료, 담배·니코틴, 처방 외 약물과 기타 물질의 종류·양·빈도·마지막 사용과 최근 변화를 알려주세요.", 103, "treatment-detail", R + D),
        q("mental_health.relationship_living_debt_employment_loneliness_and_social_isolation", "Relationship Living Financial and Social Context", "string", "social-context", "가족·관계, 주거, 경제·부채, 직장·학업, 외로움·고립과 돌봄 부담 중 증상과 관련해 달라진 점을 알려주세요.", 102, "social-context", R),
        q("mental_health.strengths_coping_supports_and_help_awareness", "Strengths Coping and Support Resources", "string", "strengths-support", "지금 버티는 데 도움이 되는 강점·활동·사람, 연락 가능한 지원과 상태가 나빠질 때 도움을 요청할 방법을 알려주세요.", 101, "social-context", R + S),
        q("mental_health.diet_activity_daily_routine_sleep_and_recent_change", "Lifestyle and Daily Routine Context", "string", "lifestyle", "식사, 신체활동, 하루 일과와 수면 습관이 평소와 어떻게 달라졌고 증상과 어떤 순서로 변했는지 알려주세요.", 100, "social-context", R),
        q("mental_health.pregnancy_postpartum_reproductive_menopause_and_life_stage_context", "Pregnancy Postpartum and Life-stage Context", "string", "life-stage", "해당되는 경우 임신 주수, 출산 후 기간·수유, 월경·폐경 또는 다른 생애단계 변화와 증상·치료의 관계를 알려주세요.", 99, "life-stage", R),
        q("mental_health.family_mood_psychosis_suicide_substance_and_treatment_history", "Relevant Family Mental Health History", "string", "family-history", "가족의 기분·불안·조증·정신증, 자살·자해, 물질 사용 문제와 치료력이 있다면 관계와 알려진 내용을 알려주세요.", 98, "life-stage", R),
        q("mental_health.work_school_relationship_selfcare_sleep_driving_and_safety_impact", "Detailed Functional and Safety Impact", "string", "function-detail", "업무·학업, 관계, 씻기·식사·약 복용 같은 자기관리, 수면, 운전·기계 사용과 일상 안전에 어떤 영향이 있는지 알려주세요.", 97, "function-detail", C + R),
        q("mental_health.communication_language_hearing_vision_cognition_literacy_and_privacy_needs", "Communication Accessibility and Privacy Needs", "string", "accessibility", "선호 언어, 통역·청각·시각·인지·문해·디지털 사용 지원, 혼자 답할 필요나 선호하는 응답 방법을 알려주세요.", 96, "handoff", R),
        q("mental_health.information_source_proxy_record_reliability_conflict_and_consent", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자 중 누가 답하는지, 일기·약 목록·의무기록 등 자료 유무, 기억이 불확실하거나 서로 다른 내용과 공유 동의 범위를 알려주세요.", 95, "handoff", R),
        q("mental_health.prior_scale_name_score_date_context_and_source", "Prior Validated Measure Provenance", "string", "prior-measure", "이전에 시행한 정신건강·기능 설문이 있다면 도구명, 원점수, 날짜, 시행 상황과 자료 출처를 알려주세요. 이 문진은 점수를 새로 계산하지 않습니다.", 94, "handoff", R),
        q("mental_health.prior_assessment_physical_review_tests_date_result_source_and_pending", "Prior Assessment and Result Provenance", "string", "prior-assessment", "이전 정신건강 평가, 신체진찰·검사 또는 의뢰 결과가 있다면 날짜, 설명받은 결과, 자료 출처와 아직 확인하지 못한 항목을 알려주세요.", 93, "handoff", R),
        q("mental_health.patient_goal_treatment_preference_expected_help_and_additional_rfe", "Patient Goal Preference and Additional RFE", "string", "goal", "진료에서 확인하고 싶은 내용, 선호하거나 피하고 싶은 도움, 기대하는 변화와 질문에 없던 의견 또는 별도 문진이 필요한 다른 문제를 알려주세요.", 92, "handoff", C + R),
        q("sleep.daytime_sleepiness_naps_function_driving_and_accident_risk", "Daytime Sleepiness and Safety Impact", "string", "daytime-sleep", "낮 졸림·낮잠, 집중·업무·운전 영향과 졸음 때문에 아찔하거나 사고가 날 뻔한 일이 있었는지 알려주세요.", 91, "sleep-detail", C + R),
        q("sleep.bedroom_environment_screen_nap_routine_and_sleep_opportunity", "Sleep Opportunity and Environment", "string", "sleep-context", "수면 기회, 침실 환경, 화면 사용, 낮잠·취침 전 습관과 평일·휴일 일정 차이를 알려주세요.", 90, "sleep-detail", C + R),
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
    doc["default_refresh"].update({
        "last_assessed_at": "2026-07-21",
        "next_monitor_at": "2026-07-22",
        "next_full_review_at": "2027-01-17",
    })
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc: dict) -> dict:
    result = completion_policy(
        prefix=P,
        fragment=doc,
        presentation_fact="symptom.mental_health_sleep.current",
        question_budget=82,
        source_refs=SOURCES,
    )
    result["required_facts"]["routine"] = [
        "mental_health.primary_context",
        "symptom.mental_health_sleep.main_type",
        "symptom.duration",
        "mental_health.patient_words_first_change_and_main_concern",
        "mental_health.first_latest_onset_course_previous_baseline_and_fluctuation",
        "mental_health.symptom_intensity_variation_and_distress",
        "symptom.mental_health_sleep.functional_impact",
        "mental_health.work_school_relationship_selfcare_sleep_driving_and_safety_impact",
        "mental_health.information_source_proxy_record_reliability_conflict_and_consent",
        "mental_health.patient_goal_treatment_preference_expected_help_and_additional_rfe",
    ]
    result["conditional_required_facts"] = [{
        "selector_fact": "mental_health.primary_context",
        "cases": {
            "low_mood": [
                "symptom.low_mood", "symptom.loss_of_interest_or_pleasure",
                "symptom.hopelessness_or_worthlessness",
                "symptom.energy_or_psychomotor_change",
                "symptom.appetite_or_weight_change",
                "symptom.concentration_difficulty",
                "mental_health.past_mood_elevation_reduced_sleep_energy_and_family_observation",
                "mental_health.prior_episodes_diagnoses_admissions_crisis_and_recovery",
                "mental_health.previous_counselling_psychotherapy_medicine_and_response",
                "mental_health.relationship_living_debt_employment_loneliness_and_social_isolation",
            ],
            "anxiety_or_worry": [
                "symptom.excessive_anxiety_or_worry",
                "symptom.difficulty_controlling_worry",
                "symptom.anxiety_avoidance",
                "mental_health.anxiety_topics_somatic_reassurance_seeking_and_control",
                "mental_health.episode_frequency_duration_triggers_recovery_and_between_state",
                "mental_health.coexisting_mental_physical_cognitive_and_pain_conditions",
                "mental_health.alcohol_caffeine_nicotine_prescribed_nonprescribed_and_recreational_substances",
            ],
            "panic": [
                "symptom.panic_attack_features", "symptom.anxiety_avoidance",
                "mental_health.panic_frequency_duration_somatic_features_triggers_and_avoidance",
                "mental_health.episode_frequency_duration_triggers_recovery_and_between_state",
                "mental_health.coexisting_mental_physical_cognitive_and_pain_conditions",
                "mental_health.alcohol_caffeine_nicotine_prescribed_nonprescribed_and_recreational_substances",
            ],
            "sleep_problem": [
                "sleep.main_problem", "sleep.schedule_and_hours",
                "sleep.frequency_per_week", "sleep.snoring_apnea_or_choking",
                "sleep.restless_legs_features", "sleep.shift_work_or_irregular_schedule",
                "sleep.daytime_sleepiness_naps_function_driving_and_accident_risk",
                "sleep.bedroom_environment_screen_nap_routine_and_sleep_opportunity",
                "mental_health.alcohol_caffeine_nicotine_prescribed_nonprescribed_and_recreational_substances",
            ],
            "stress_trauma_or_loss": [
                "event.recent_stressor_trauma_or_loss",
                "mental_health.relationship_living_debt_employment_loneliness_and_social_isolation",
                "mental_health.strengths_coping_supports_and_help_awareness",
                "support.trusted_person_available",
                "risk.safeguarding_or_domestic_violence_current",
            ],
            "treatment_followup": [
                "history.mental_health_diagnosis_or_treatment",
                "medication.mental_health_sleep_current_or_changed",
                "mental_health.prior_episodes_diagnoses_admissions_crisis_and_recovery",
                "mental_health.previous_counselling_psychotherapy_medicine_and_response",
                "mental_health.current_medicine_product_dose_schedule_adherence_start_change_and_prescriber",
                "mental_health.medicine_benefit_side_effect_withdrawal_missed_dose_and_symptom_timing",
                "mental_health.prior_scale_name_score_date_context_and_source",
                "mental_health.prior_assessment_physical_review_tests_date_result_source_and_pending",
            ],
            "mania_or_psychosis_followup": [
                "symptom.first_onset_hallucination_or_delusion",
                "symptom.markedly_reduced_sleep_with_high_energy",
                "symptom.manic_risky_or_disinhibited_behavior",
                "mental_health.past_mood_elevation_reduced_sleep_energy_and_family_observation",
                "mental_health.prior_episodes_diagnoses_admissions_crisis_and_recovery",
                "mental_health.current_medicine_product_dose_schedule_adherence_start_change_and_prescriber",
                "mental_health.alcohol_caffeine_nicotine_prescribed_nonprescribed_and_recreational_substances",
            ],
            "proxy_or_accessibility": [
                "mental_health.communication_language_hearing_vision_cognition_literacy_and_privacy_needs",
                "mental_health.information_source_proxy_record_reliability_conflict_and_consent",
                "mental_health.coexisting_mental_physical_cognitive_and_pain_conditions",
                "mental_health.strengths_coping_supports_and_help_awareness",
                "mental_health.prior_assessment_physical_review_tests_date_result_source_and_pending",
            ],
            "pregnancy_postpartum_or_life_stage": [
                "mental_health.pregnancy_postpartum_reproductive_menopause_and_life_stage_context",
                "mental_health.coexisting_mental_physical_cognitive_and_pain_conditions",
                "mental_health.current_medicine_product_dose_schedule_adherence_start_change_and_prescriber",
                "mental_health.strengths_coping_supports_and_help_awareness",
                "mental_health.family_mood_psychosis_suicide_substance_and_treatment_history",
            ],
            "mixed_or_unclear": [
                "symptom.low_mood", "symptom.excessive_anxiety_or_worry",
                "sleep.main_problem", "event.recent_stressor_trauma_or_loss",
                "mental_health.coexisting_mental_physical_cognitive_and_pain_conditions",
                "mental_health.current_medicine_product_dose_schedule_adherence_start_change_and_prescriber",
                "mental_health.relationship_living_debt_employment_loneliness_and_social_isolation",
                "mental_health.strengths_coping_supports_and_help_awareness",
            ],
        },
    }]
    result["provenance"] = provenance(SOURCES)
    return result


def sources() -> dict:
    doc = load(RESEARCH)
    for artifact in doc["artifacts"]:
        source_id = artifact["id"]
        if source_id == "source.nice.ng222.depression.2022":
            artifact.update({
                "version": "NG222-2022-surveillance-2026-01-accessed-2026-07-21",
                "last_monitored_at": "2026-07-21",
                "next_monitor_at": "2026-07-28",
                "monitor_result": "current_recommendations_confirmed; january_2026_exceptional_surveillance_proposed_no_update_to_treatment_resistant_depression_section",
                "recommendation_change_detected": False,
                "assertions": [
                    "Assessment preserves symptom severity, history, duration, course, function, coexisting conditions, mood elevation, previous treatment response, strengths, relationships, lifestyle, trauma, living conditions, substance use, debt, employment, loneliness and social isolation.",
                    "Current suicidal ideation and intent are asked directly; Runtime does not diagnose depression or calculate a proprietary score.",
                ],
            })
        elif source_id == "source.nice.cg113.anxiety.2020":
            artifact.update({
                "version": "CG113-updated-2020-accessed-2026-07-21",
                "last_monitored_at": "2026-07-21",
                "next_monitor_at": "2026-07-28",
                "monitor_result": "current_official_guideline_confirmed_no_replacement_identified",
                "recommendation_change_detected": False,
                "assertions": [
                    "Anxiety assessment preserves distress, functional impact, coexisting depression or anxiety, substance use, medical conditions, prior mental-health history and treatment response.",
                    "Over-the-counter and other substance exposure is recorded without Runtime diagnosis or medicine advice.",
                ],
            })
        elif source_id == "source.nhs.urgent-mental-support.2026":
            artifact.update({
                "version": "accessed-2026-07-21",
                "last_monitored_at": "2026-07-21",
                "next_monitor_at": "2026-07-28",
                "monitor_result": "current_official_page_confirmed",
                "recommendation_change_detected": False,
                "assertions": [
                    "Immediate danger triggers emergency handoff and first hallucinations or delusions remain time-sensitive for clinician assessment.",
                    "Jurisdiction-specific contact details are not copied into the general Runtime package.",
                ],
            })
    doc["version"] = "0.2.0"
    doc["updated_at"] = CREATED
    doc["provenance"] = provenance([item["id"] for item in doc["artifacts"]])
    doc["provenance"]["version"] = "0.2.0"
    return doc


def clinician(doc: dict) -> dict:
    result = load(CLINICIAN)
    ids = sorted({item["fact"]["id"] for item in doc["entries"]})
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.mental_health_sleep"] = ids
    return result


def routine_cases(doc: dict, completion: dict) -> dict[str, dict]:
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    always = completion["required_facts"]["always"]
    core = completion["required_facts"]["routine"]
    branches = completion["conditional_required_facts"][0]["cases"]
    forbidden = [
        "diagnosis.major_depression", "diagnosis.generalized_anxiety_disorder",
        "diagnosis.bipolar_disorder", "diagnosis.psychosis",
        "recommendation.start_antidepressant", "recommendation.sleeping_pill",
    ]

    def value(fact_id: str):
        fact = by_id[fact_id]
        if fact["value_type"] == "boolean":
            return False
        if fact["value_type"] == "quantity":
            return {"amount": 3, "unit": "weeks"}
        if fact["value_type"] == "integer":
            return 0
        if fact["value_type"] == "coded":
            values = fact.get("allowed_values", ["other"])
            for candidate in ("none", "mixed", "other", "unchanged"):
                if candidate in values:
                    return candidate
            return values[-1]
        return "특이사항 없음"

    def state(branch: str) -> dict[str, dict]:
        identifiers = dict.fromkeys([*always, *core, *branches[branch]])
        result = {fact_id: {"value": value(fact_id)} for fact_id in identifiers}
        result["symptom.mental_health_sleep.current"] = {"value": True}
        result["mental_health.primary_context"] = {"value": branch}
        result["symptom.mental_health_sleep.main_type"] = {"value": "mixed"}
        return result

    specs = [
        ("LOW-MOOD-HANDOFF", "low_mood", 43, "기분 저하의 경과와 기능·치료·사회적 영향을 진료 전에 정리합니다.", {}),
        ("ANXIETY-REMOTE", "anxiety_or_worry", 37, "원격 진료 전에 걱정 주제, 신체 증상과 회피·기능 변화를 정리합니다.", {}),
        ("PANIC-EPISODE", "panic", 29, "갑자기 몰려오는 불안 에피소드의 시간·신체 증상·회복을 정리합니다.", {}),
        ("SLEEP-SHIFT-WORK", "sleep_problem", 46, "교대근무와 불면·낮 졸림의 일정과 안전 영향을 정리합니다.", {}),
        ("STRESS-SOCIAL-CONTEXT", "stress_trauma_or_loss", 51, "최근 스트레스와 관계·주거·경제·지원 상황을 구분해 전달합니다.", {}),
        ("TREATMENT-FOLLOWUP", "treatment_followup", 34, "약과 상담의 실제 사용, 효과·부작용과 이전 평가를 추적 진료에 전달합니다.", {}),
        ("PSYCHOSIS-MANIA-FOLLOWUP", "mania_or_psychosis_followup", 40, "기존 치료 중 기분·수면·지각 변화와 자료 출처를 추적합니다.", {}),
        ("PREGNANCY-POSTPARTUM", "pregnancy_postpartum_or_life_stage", 32, "임신·산후 생애단계와 정신건강·약물·지원 맥락을 정리합니다.", {}),
        ("MULTI-RFE-COMMENT", "mixed_or_unclear", 56, "기분과 수면 문제 외 다른 신체 증상은 별도 RFE로 보존합니다.", {"mental_health.patient_goal_treatment_preference_expected_help_and_additional_rfe": {"value": "두통은 별도 문진 요청"}}),
    ]
    result = {}
    for key, branch, age, statement, overrides in specs:
        hidden = state(branch)
        hidden.update(overrides)
        case = {
            "id": f"MHS-{key}",
            "simulation_language": "ko",
            "persona": {"age": age},
            "initial_statement": {"ko": statement},
            "hidden_state": hidden,
            "expected": {
                "expected_safety_level": "routine",
                "expected_stop_reason": "all_required_targets_resolved",
                "expected_max_turns": 82,
                "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }
        if key == "ANXIETY-REMOTE":
            case["encounter_context"] = {
                "care_setting": "telemedicine", "encounter_type": "new_encounter",
                "interview_initiator": "patient", "interview_mode": "video",
                "available_information": ["no_previous_records"],
                "time_constraint": "routine", "clinical_responsibility": "decision_support",
            }
        result[f"MHS-{key}.json"] = case

    proxy = state("proxy_or_accessibility")
    result["MHS-PROXY-ACCESSIBILITY.json"] = {
        "id": "MHS-PROXY-ACCESSIBILITY",
        "simulation_language": "ko",
        "persona": {"age": 74},
        "initial_statement": {"ko": "보호자가 정보 출처를 구분해 수면·기분 변화와 필요한 의사소통 지원을 전달합니다."},
        "hidden_state": proxy,
        "encounter_context": {
            "care_setting": "home_visit", "encounter_type": "follow_up",
            "interview_initiator": "caregiver", "interview_mode": "face_to_face",
            "available_information": ["previous_clinical_memory", "caregiver_report"],
            "time_constraint": "scheduled", "clinical_responsibility": "shared_care",
        },
        "clinician_submission": True,
        "expected": {
            "expected_safety_level": "routine",
            "expected_max_turns": 130,
            "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }

    missing = "mental_health.prior_scale_name_score_date_context_and_source"
    absent = state("treatment_followup")
    absent.pop(missing)
    result["MHS-PRIOR-MEASURE-DATA-ABSENT.json"] = {
        "id": "MHS-PRIOR-MEASURE-DATA-ABSENT",
        "simulation_language": "ko",
        "persona": {"age": 48},
        "initial_statement": {"ko": "이전 설문을 했지만 도구명과 원점수 자료는 기억나지 않습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "asked-unknown"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 82,
            "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }

    declined = "event.recent_stressor_trauma_or_loss"
    stress_absent = state("stress_trauma_or_loss")
    stress_absent.pop(declined)
    result["MHS-DATA-ABSENT.json"] = {
        "id": "MHS-DATA-ABSENT",
        "simulation_language": "ko",
        "persona": {"age": 34},
        "initial_statement": {"ko": "요즘 잠들기 어렵고 걱정이 많지만 일부 스트레스 내용은 답하고 싶지 않습니다."},
        "hidden_state": stress_absent,
        "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}},
        "expected": {
            "expected_data_absent_reasons": {declined: "asked-declined"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 82,
            "forbidden_assertions": forbidden,
        },
        "provenance": provenance(["source.nice.ng222.depression.2022", "specifications/clinical-memory.md"]),
    }
    result["MHS-OPENING-SUICIDE-PLAN.json"] = {
        "id": "MHS-OPENING-SUICIDE-PLAN",
        "simulation_language": "ko",
        "persona": {"age": 31},
        "initial_statement": {"ko": "오늘 밤 너무 불안하고 죽을 계획이 있습니다."},
        "hidden_state": {},
        "encounter_context": {
            "care_setting": "emergency_department", "encounter_type": "new_encounter",
            "interview_initiator": "patient", "interview_mode": "face_to_face",
            "available_information": ["no_previous_records"],
            "time_constraint": "emergency", "clinical_responsibility": "independent_assessment",
        },
        "expected": {
            "expected_safety_level": "emergency",
            "expected_safety_action": "human_handoff",
            "expected_stop_reason": "emergency_escalation",
            "expected_triggered_rules_contains": [
                "rule.mental-health-sleep.safety.suicide-plan",
            ],
            "expected_max_turns": 1,
            "forbidden_assertions": forbidden,
        },
        "provenance": provenance([
            "source.nice.ng222.depression.2022",
            "source.nhs.urgent-mental-support.2026",
        ]),
    }
    return result


def main() -> None:
    seed_mental_health_sleep.main()
    doc = fragment()
    result_policy = policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, result_policy)
    write_json(RESEARCH, sources())
    write_json(CLINICIAN, clinician(doc))
    for name, case in routine_cases(doc, result_policy).items():
        write_json(f"simulation/patients/mental-health/mental-health-sleep/{name}", case)


if __name__ == "__main__":
    main()
