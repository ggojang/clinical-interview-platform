#!/usr/bin/env python3
"""Strengthen research-only cough knowledge for clinician pre-visit handoff."""
from __future__ import annotations

import json

from profile_support import ROOT, entry, provenance, safety_rule, write_json


P = "cough"
FRAGMENT = "knowledge/generated/respiratory/cough-expansion.json"
BASE_GRAPH = "knowledge/base/primary-care-cough.json"
POLICY = "policies/primary-care-cough-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
PAIN = "knowledge/shared/hira-pain-assessment.json"
SIM_ROOT = ROOT / "simulation/patients/respiratory"
SOURCES = [
    "source.cdc.common-cold.2026",
    "source.nice.ng120",
    "source.ers.chronic-cough.2020",
    "source.gina.strategy.2026",
    "source.bts.chronic-cough.2023",
]
G = {key: f"group.cough.{key}" for key in (
    "routing", "course", "character", "associated", "trigger",
    "exposure", "history", "investigation", "function", "handoff",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
D = ["intent.differentiate_common_causes"]
R = ["intent.risk_assessment"]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def refresh() -> dict:
    return {
        "class": "clinical_guideline",
        "last_assessed_at": "2026-07-19",
        "monitor_interval_days": 1,
        "full_review_interval_days": 180,
        "next_monitor_at": "2026-07-20",
        "next_full_review_at": "2027-01-15",
        "policy_id": "policy.knowledge-refresh",
        "overdue_behavior": {
            "production": "exclude_or_require_review",
            "research_test": "allow_with_warning",
        },
    }


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
    item = entry(
        P, fact_id, display, value_type, key, wording, score, key,
        [G[group]], intents=intents, **kwargs,
    )
    item["fact"]["refresh"] = refresh()
    return item


def strengthen_fragment() -> dict:
    doc = load(FRAGMENT)
    contexts = [
        "current_acute", "subacute_or_postinfectious", "chronic_or_recurrent",
        "productive_or_recurrent_infection", "trigger_or_exposure_related",
        "medicine_related", "child_or_proxy", "followup_or_result_context",
        "other_or_unclear",
    ]
    additions = [
        q("cough.primary_context", "Primary Cough Context", "coded", "primary-context", "현재 급성 기침, 감염 후·아급성, 만성·반복, 가래·반복 감염, 유발·노출 관련, 약물 관련, 소아·보호자 응답, 추적·결과 확인, 또는 불분명 중 가장 가까운 상황은 무엇인가요?", 110, "routing", C + R, allowed_values=contexts),
        q("cough.patient_words_dry_productive_and_main_concern", "Patient Description and Dry or Productive Pattern", "string", "patient-description", "본인의 표현으로 기침 소리·느낌과 마른기침인지 가래가 나오는지, 가장 불편하거나 걱정되는 점을 알려주세요.", 109, "character", C),
        q("cough.first_latest_onset_exact_time_context_and_trend", "First and Latest Cough Timeline", "string", "timeline", "처음과 가장 최근 기침의 날짜·시각, 당시 하던 일과 이후 좋아짐·악화·반복 양상을 알려주세요.", 108, "course", C + R),
        q("cough.daily_frequency_episode_duration_bouts_and_between_state", "Cough Frequency Bout Duration and Inter-episode State", "string", "frequency-bouts", "하루 기침 횟수나 심한 발작 횟수, 한 번 시작하면 지속되는 시간과 발작 사이에는 정상으로 돌아오는지 알려주세요.", 114, "course", C),
        q("cough.rapid_or_significant_worsening", "Rapid or Significant Cough Worsening", "boolean", "rapid-worsening", "기침이나 전신 상태가 최근 빠르게 또는 뚜렷하게 악화하고 있나요?", 114, "associated", S + R, safety_relevant=True),
        q("cough.day_night_sleep_posture_voice_laugh_and_meal_variation", "Cough Variation by Time Posture Voice and Meal", "string", "variation", "낮·밤·수면 중, 눕기, 말하기·웃기, 식사 전후 중 언제 심해지거나 좋아지는지 알려주세요.", 105, "trigger", C + D),
        q("cough.sputum_amount_colour_consistency_odor_and_change", "Sputum Amount Appearance and Change", "string", "sputum-detail", "가래가 있다면 하루 양, 색·점도·냄새와 평소보다 달라진 시점을 알려주세요.", 108, "character", C + D),
        q("cough.hemoptysis_amount_frequency_appearance_and_source", "Hemoptysis Amount Frequency and Source", "string", "hemoptysis-detail", "피가 보였다면 줄무늬·덩어리 등 모양, 대략적인 양·횟수와 기침 가래에서 나온 것이 확실한지 알려주세요.", 117, "associated", S + R),
        q("cough.dyspnea_rest_exertion_speech_sleep_oxygen_and_recovery", "Dyspnea Functional and Measurement Detail", "string", "dyspnea-detail", "숨참이 있다면 안정·운동·말하기·수면 영향, 산소포화도 측정값·기기·시각과 회복 과정을 알려주세요.", 113, "associated", C + S),
        q("cough.chest_pain_nrs", "Chest Pain NRS", "integer", "chest-pain-nrs", "[필수] 기침과 관련된 흉통이 있었다면 가장 심할 때 통증을 0부터 10까지 숫자로 알려주세요.", 112, "associated", C + S),
        q("cough.chest_pain_site_character_duration_and_cough_relation", "Chest Pain Pattern with Cough", "string", "chest-pain-detail", "흉통이 있다면 부위·양상·지속시간, 퍼지는 곳과 기침·호흡·움직임과의 관계를 알려주세요.", 111, "associated", C + S),
        q("cough.fever_temperature_chills_systemic_state_and_timeline", "Fever and Systemic Illness Timeline", "string", "fever-detail", "발열이 있다면 최고 체온·측정방법·시각, 오한·몸살·전신 상태와 기침 전후 순서를 알려주세요.", 110, "associated", C + S),
        q("cough.upper_airway_symptom_sequence_and_baseline", "Upper Airway Symptom Sequence", "string", "upper-airway", "콧물·코막힘·재채기·목통증·후비루·목 가다듬기가 있다면 시작 순서와 평소 알레르기·비염 상태를 알려주세요.", 96, "associated", C + D),
        q("cough.wheeze_chest_tightness_variability_and_prior_pattern", "Wheeze Tightness and Variability", "string", "wheeze-detail", "쌕쌕거림·가슴 답답함이 있다면 시간대·운동·감염과의 관계, 변동성과 이전에도 같은 양상이 있었는지 알려주세요.", 104, "associated", C + D),
        q("cough.paroxysm_whoop_posttussive_vomit_and_recovery", "Paroxysm Whoop Vomit and Recovery", "string", "paroxysm-detail", "연속 발작, 숨 들이쉴 때 소리, 기침 뒤 구토·청색증·탈진이 있는지와 회복까지 걸리는 시간을 알려주세요.", 107, "associated", C + R),
        q("cough.eating_drinking_swallowing_choking_and_aspiration_context", "Swallowing Choking and Aspiration Context", "string", "swallowing-context", "음식·물·침을 삼킬 때 기침·사레가 들거나 걸리는 느낌, 구토·흡인 우려와 시작 시점을 알려주세요.", 109, "trigger", C + R),
        q("cough.exercise_cold_air_speech_laugh_fume_and_scent_triggers", "Detailed Cough Triggers", "string", "trigger-detail", "운동·찬 공기·말하기·웃기·연기·향·먼지 중 유발 요인과 노출 후 시작시간·회복시간을 알려주세요.", 101, "trigger", C + D),
        q("cough.home_work_hobby_mold_dust_fume_animal_and_season_exposure", "Home Work and Environmental Exposure Detail", "string", "environment-detail", "집·직장·취미의 곰팡이·분진·가스·화학물질·동물·계절 노출, 보호구와 쉬는 날 증상 변화를 알려주세요.", 100, "exposure", D + R),
        q("cough.smoking_vaping_cannabis_pack_years_last_use_and_change", "Smoking Vaping and Inhaled Exposure Detail", "string", "smoking-detail", "담배·전자담배·가열담배·대마 등 흡입 노출의 종류, 하루 양·기간·마지막 사용과 최근 변화를 알려주세요.", 103, "exposure", D + R),
        q("cough.infectious_contact_travel_tb_setting_and_timing", "Infectious Contact Travel and Tuberculosis Context", "string", "infection-exposure", "기침 환자 접촉, 집단생활·의료·교정시설·해외 체류와 결핵 노출·검사 이력 및 증상과의 시점을 알려주세요.", 106, "exposure", R),
        q("cough.medicine_name_dose_start_change_acei_inhaler_and_adherence", "Medicine Exposure Timing and Adherence", "string", "medicine-detail", "처방약·감기약·흡입제의 이름·용량·시작/변경일, 복용 여부와 기침 시작 시점의 관계를 알려주세요.", 102, "history", D + R),
        q("cough.respiratory_cardiac_reflux_ent_immunity_and_cancer_history", "Relevant Medical History", "string", "medical-history", "천식·COPD·기관지확장증·폐렴·결핵, 심장·역류·비염/부비동·면역저하·암 병력의 진단 시기와 현재 상태를 알려주세요.", 99, "history", D + R),
        q("cough.prior_recurrent_episode_ed_admission_and_baseline_recovery", "Prior Episodes Emergency Care and Recovery", "string", "prior-episode", "이전 유사 기침의 시기·진단·응급실/입원 여부, 평소 상태로 회복했는지와 이번과 다른 점을 알려주세요.", 98, "history", C + R),
        q("cough.pregnancy_age_frailty_comorbidity_and_risk_context", "Pregnancy Age Frailty and Risk Context", "string", "risk-context", "해당되는 경우 임신·산후 기간, 소아·고령·허약 상태와 심폐·신장·간·당뇨 등 합병증 위험 병력을 알려주세요.", 97, "history", R),
        q("cough.child_age_feeding_sleep_breathing_growth_and_caregiver_observation", "Child Cough and Caregiver Observation", "string", "child-context", "소아라면 나이·체중, 수유/식사·수면·호흡·활동·성장 변화와 보호자가 직접 본 기침 양상을 알려주세요.", 100, "history", C + R),
        q("cough.older_frailty_swallowing_polypharmacy_and_care_support", "Older Adult Frailty Aspiration and Care Support", "string", "older-context", "고령자라면 허약·삼킴/사레·인지·이동 상태, 복용약 수와 식사·복약을 돕는 사람이 있는지 알려주세요.", 95, "history", R),
        q("cough.prior_chest_xray_ct_spirometry_feno_and_result_source", "Prior Respiratory Investigations", "string", "investigation", "흉부 X-ray/CT, 폐기능·기관지확장·FeNO 검사의 날짜·설명받은 결과, 검사 당시 증상과 자료 출처를 알려주세요.", 94, "investigation", R),
        q("cough.prior_blood_sputum_swab_allergy_tb_and_other_tests", "Prior Laboratory Microbiology and Allergy Tests", "string", "other-tests", "혈액·가래·호흡기 검체, 알레르기·결핵 검사의 날짜·결과·추세와 아직 확인하지 못한 항목을 알려주세요.", 93, "investigation", R),
        q("cough.treatment_antibiotic_inhaler_antacid_antihistamine_and_response", "Prior Treatment and Response", "string", "treatment-response", "항생제·흡입제·위산/알레르기 약·기침약 등 사용한 치료의 이름·기간·반응·부작용과 중단 후 변화를 알려주세요.", 92, "investigation", C + R),
        q("cough.vaccination_influenza_covid_pertussis_status_and_date", "Relevant Vaccination Status and Date", "string", "vaccination", "독감·COVID-19·백일해 등 관련 예방접종 여부와 가능한 최근 접종일을 알려주세요.", 88, "history", R),
        q("cough.sleep_work_school_voice_eating_activity_and_care_impact", "Cough Functional Impact", "string", "function", "수면·출근/등교·말하기·식사·운동·자가관리와 가족 돌봄에 미치는 제한을 알려주세요.", 91, "function", C + R),
        q("cough.communication_language_hearing_literacy_and_accessibility", "Communication and Accessibility Needs", "string", "accessibility", "선호 언어, 통역·청각·시각·문해·디지털 지원 등 문진과 진료에 필요한 도움이 있나요?", 84, "handoff", R),
        q("cough.information_source_witness_record_reliability_and_conflict", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자 중 누가 답하는지, 일지·사진·기기·의무기록 유무와 기억이 불확실하거나 자료가 서로 다른 부분을 알려주세요.", 90, "handoff", R),
        q("cough.patient_goal_expectation_additional_comment_and_other_rfe", "Patient Goal Additional Comment and Other RFE", "string", "goal", "진료에서 확인하고 싶은 내용, 질문에 없던 의견과 별도로 문진받고 싶은 다른 방문 이유가 있나요?", 89, "handoff", C + R),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())

    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    for key, identifier in G.items():
        nodes[identifier] = {
            "id": identifier, "type": "ClinicalGroup",
            "display": key.replace("-", " ").title(),
        }
    doc["extra_nodes"] = list(nodes.values())

    rules = {item["id"]: item for item in doc["safety_rules"]}
    for item in (
        safety_rule(P, "rapid-significant-worsening", {"fact": "cough.rapid_or_significant_worsening", "equals": True}, "urgent", 850),
        safety_rule(P, "severe-systemic-illness", {"fact": "symptom.systemic_unwellness", "equals": "severe"}, "urgent", 860),
    ):
        rules[item["id"]] = item
    doc["safety_rules"] = list(rules.values())
    doc["provenance"] = provenance(SOURCES)
    return doc


def strengthen_policy() -> dict:
    doc = load(POLICY)
    common = [
        "cough.primary_context", "symptom.duration", "symptom.dyspnea",
        "cough.patient_words_dry_productive_and_main_concern",
        "cough.first_latest_onset_exact_time_context_and_trend",
        "cough.daily_frequency_episode_duration_bouts_and_between_state",
        "cough.rapid_or_significant_worsening",
        "symptom.systemic_unwellness",
        "symptom.hemoptysis", "symptom.chest_pain",
        "cough.sleep_work_school_voice_eating_activity_and_care_impact",
        "cough.information_source_witness_record_reliability_and_conflict",
        "cough.patient_goal_expectation_additional_comment_and_other_rfe",
    ]
    doc["required_facts"]["always"] = common
    for branch in ("acute", "subacute", "chronic"):
        existing = doc["required_facts"].get(branch, [])
        doc["required_facts"][branch] = list(dict.fromkeys(existing))
    doc["conditional_required_facts"] = [{
        "selector_fact": "cough.primary_context",
        "cases": {
            "current_acute": [
                "symptom.fever", "symptom.systemic_unwellness",
                "symptom.cough_trajectory", "cough.fever_temperature_chills_systemic_state_and_timeline",
                "cough.upper_airway_symptom_sequence_and_baseline",
            ],
            "subacute_or_postinfectious": [
                "cough.day_night_sleep_posture_voice_laugh_and_meal_variation",
                "cough.wheeze_chest_tightness_variability_and_prior_pattern",
                "cough.treatment_antibiotic_inhaler_antacid_antihistamine_and_response",
            ],
            "chronic_or_recurrent": [
                "cough.day_night_sleep_posture_voice_laugh_and_meal_variation",
                "cough.exercise_cold_air_speech_laugh_fume_and_scent_triggers",
                "cough.smoking_vaping_cannabis_pack_years_last_use_and_change",
                "cough.respiratory_cardiac_reflux_ent_immunity_and_cancer_history",
                "cough.prior_chest_xray_ct_spirometry_feno_and_result_source",
            ],
            "productive_or_recurrent_infection": [
                "symptom.sputum", "cough.sputum_amount_colour_consistency_odor_and_change",
                "history.recurrent_respiratory_infections",
                "cough.prior_recurrent_episode_ed_admission_and_baseline_recovery",
                "cough.prior_blood_sputum_swab_allergy_tb_and_other_tests",
            ],
            "trigger_or_exposure_related": [
                "cough.exercise_cold_air_speech_laugh_fume_and_scent_triggers",
                "cough.home_work_hobby_mold_dust_fume_animal_and_season_exposure",
                "cough.infectious_contact_travel_tb_setting_and_timing",
            ],
            "medicine_related": [
                "medication.ace_inhibitor_exposure",
                "cough.medicine_name_dose_start_change_acei_inhaler_and_adherence",
                "cough.treatment_antibiotic_inhaler_antacid_antihistamine_and_response",
            ],
            "child_or_proxy": [
                "cough.child_age_feeding_sleep_breathing_growth_and_caregiver_observation",
                "cough.paroxysm_whoop_posttussive_vomit_and_recovery",
                "cough.eating_drinking_swallowing_choking_and_aspiration_context",
                "cough.communication_language_hearing_literacy_and_accessibility",
            ],
            "followup_or_result_context": [
                "cough.prior_chest_xray_ct_spirometry_feno_and_result_source",
                "cough.prior_blood_sputum_swab_allergy_tb_and_other_tests",
                "cough.treatment_antibiotic_inhaler_antacid_antihistamine_and_response",
            ],
            "other_or_unclear": [
                "cough.day_night_sleep_posture_voice_laugh_and_meal_variation",
                "cough.eating_drinking_swallowing_choking_and_aspiration_context",
                "cough.older_frailty_swallowing_polypharmacy_and_care_support",
                "cough.communication_language_hearing_literacy_and_accessibility",
            ],
        },
    }]
    doc["clarification_facts_by_rule"]["rule.cough.safety.rapid-significant-worsening"] = [
        "symptom.dyspnea", "symptom.systemic_unwellness", "symptom.hemoptysis", "symptom.chest_pain",
    ]
    doc["clarification_facts_by_rule"]["rule.cough.safety.severe-systemic-illness"] = [
        "symptom.dyspnea", "symptom.hemoptysis", "symptom.chest_pain",
    ]
    doc["question_budget"] = {"routine": 60, "clarify": 20}
    doc["provenance"] = provenance(SOURCES)
    return doc


def strengthen_clinician(fragment: dict) -> dict:
    doc = load(CLINICIAN)
    base = load(BASE_GRAPH)
    ids = {node["id"] for node in base["nodes"] if node.get("type") == "Fact"}
    ids.update(item["fact"]["id"] for item in fragment["entries"])
    ids.update({"pain.frequency", "cough.chest_pain_nrs"})
    doc["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.cough"] = sorted(ids)
    return doc


def condition_state(condition: dict) -> dict:
    result = {}
    for child in condition.get("all", [condition]):
        if "fact" in child:
            result[child["fact"]] = {
                "value": child.get("equals", child.get("in", [True])[0])
            }
    return result


def add_simulations(fragment: dict, policy: dict) -> None:
    for old in SIM_ROOT.glob("COUGH-HANDOFF-*.json"):
        old.unlink()
    base = load(BASE_GRAPH)
    facts = {node["id"]: node for node in base["nodes"] if node.get("type") == "Fact"}
    facts.update({item["fact"]["id"]: item["fact"] for item in fragment["entries"]})

    def value(fact_id: str):
        node = facts[fact_id]
        if fact_id == "symptom.duration":
            return {"amount": 10, "unit": "day"}
        if node["value_type"] == "boolean":
            return False
        if node["value_type"] in {"severity"}:
            return "none"
        if node["value_type"] == "coded":
            return node.get("allowed_values", ["unknown"])[-1]
        if node["value_type"] == "integer":
            return 0
        return "특이사항 없음"

    duration_by_context = {
        "current_acute": {"amount": 10, "unit": "day"},
        "subacute_or_postinfectious": {"amount": 30, "unit": "day"},
        "chronic_or_recurrent": {"amount": 12, "unit": "week"},
        "productive_or_recurrent_infection": {"amount": 12, "unit": "week"},
        "trigger_or_exposure_related": {"amount": 12, "unit": "week"},
        "medicine_related": {"amount": 12, "unit": "week"},
        "child_or_proxy": {"amount": 10, "unit": "day"},
        "followup_or_result_context": {"amount": 12, "unit": "week"},
        "other_or_unclear": {"amount": 12, "unit": "week"},
    }

    def routine(context: str) -> dict:
        ids = list(policy["required_facts"]["always"])
        ids.extend(policy["conditional_required_facts"][0]["cases"][context])
        duration = duration_by_context[context]
        days = duration["amount"] * {"day": 1, "week": 7, "month": 30}[duration["unit"]]
        branch = "acute" if days < 21 else "subacute" if days <= 56 else "chronic"
        ids.extend(policy["required_facts"][branch])
        state = {fact_id: {"value": value(fact_id)} for fact_id in dict.fromkeys(ids)}
        state["cough.primary_context"] = {"value": context}
        state["symptom.duration"] = {"value": duration}
        return state

    forbidden = [
        "diagnosis.asthma", "diagnosis.pneumonia", "diagnosis.tuberculosis",
        "diagnosis.malignancy", "recommendation.antibiotic",
        "recommendation.inhaler", "recommendation.chest_xray",
    ]
    specs = [
        ("ACUTE-TIMELINE", "current_acute", 29, "급성 기침의 시작과 전신 증상 순서를 의료진에게 전달합니다.", {}),
        ("POSTINFECTIOUS-COURSE", "subacute_or_postinfectious", 43, "감염 뒤 남은 기침의 시간대와 치료 반응을 정리합니다.", {}),
        ("CHRONIC-EXPOSURE", "chronic_or_recurrent", 56, "오래 반복되는 기침과 흡입 노출·이전 검사를 정리합니다.", {}),
        ("PRODUCTIVE-RECURRENT", "productive_or_recurrent_infection", 67, "가래와 반복 감염 이력, 이전 검사를 의료진에게 전달합니다.", {"symptom.sputum": {"value": True}}),
        ("OCCUPATIONAL-TRIGGER", "trigger_or_exposure_related", 38, "직장 분진과 찬 공기 뒤 기침 양상을 정리합니다.", {}),
        ("MEDICINE-TIMING", "medicine_related", 61, "혈압약 변경과 기침 시작 시점을 정리합니다.", {"medication.ace_inhibitor_exposure": {"value": True}}),
        ("CHILD-PROXY-REMOTE", "child_or_proxy", 7, "보호자가 소아 기침과 수유·수면 변화를 원격으로 답합니다.", {}),
        ("FOLLOWUP-RESULT", "followup_or_result_context", 49, "이전 흉부검사와 치료 반응을 확인하러 왔습니다.", {}),
        ("OLDER-UNCLEAR", "other_or_unclear", 84, "고령자의 기침을 보호자가 답하며 사레와 약 정보가 불확실합니다.", {}),
        ("MULTI-RFE-COMMENT", "other_or_unclear", 52, "기침 외 체중 변화도 별도 문진으로 전달하고 싶습니다.", {"cough.patient_goal_expectation_additional_comment_and_other_rfe": {"value": "체중 변화를 별도 RFE로 전달 요청"}}),
    ]
    for key, context, age, statement, overrides in specs:
        state = routine(context)
        state.update(overrides)
        case = {
            "id": f"COUGH-HANDOFF-{key}", "simulation_language": "ko",
            "persona": {"age": age}, "initial_statement": {"ko": statement},
            "hidden_state": state,
            "expected": {
                "expected_safety_level": "routine",
                "expected_stop_reason": "all_required_targets_resolved",
                "expected_max_turns": 60,
                "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }
        if key == "CHILD-PROXY-REMOTE":
            case["encounter_context"] = {
                "care_setting": "telemedicine", "encounter_type": "new_encounter",
                "interview_initiator": "caregiver", "interview_mode": "video",
                "available_information": ["no_previous_records"],
                "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
            }
        write_json(f"simulation/patients/respiratory/COUGH-HANDOFF-{key}.json", case)

    absent = routine("followup_or_result_context")
    missing = "cough.prior_chest_xray_ct_spirometry_feno_and_result_source"
    absent.pop(missing)
    write_json("simulation/patients/respiratory/COUGH-HANDOFF-DATA-ABSENT-RESULT.json", {
        "id": "COUGH-HANDOFF-DATA-ABSENT-RESULT", "simulation_language": "ko",
        "persona": {"age": 72},
        "initial_statement": {"ko": "검사를 받았지만 결과 원문은 지금 확인할 수 없습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_data_absent_reasons": {missing: "asked-unknown"},
            "expected_max_turns": 60, "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    })

    for key, rule_id, state in (
        ("RAPID-WORSENING", "rule.cough.safety.rapid-significant-worsening", {"cough.rapid_or_significant_worsening": {"value": True}}),
        ("SEVERE-SYSTEMIC", "rule.cough.safety.severe-systemic-illness", {"symptom.systemic_unwellness": {"value": "severe"}}),
    ):
        write_json(f"simulation/patients/respiratory/COUGH-HANDOFF-{key}.json", {
            "id": f"COUGH-HANDOFF-{key}", "simulation_language": "ko",
            "persona": {"age": 58},
            "initial_statement": {"ko": "기침과 함께 빠르게 악화하는 위험 증상이 있습니다."},
            "hidden_state": state,
            "expected": {
                "expected_safety_level": "urgent", "expected_safety_action": "human_handoff",
                "expected_stop_reason": "urgent_escalation",
                "expected_triggered_rules_contains": [rule_id],
                "expected_max_turns": 20, "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        })

    legacy_contexts = {
        "COUGH-ACEI-001.json": "medicine_related",
        "COUGH-COLD-001.json": "current_acute",
        "COUGH-DATA-ABSENT-001.json": "current_acute",
        "COUGH-DYSPHAGIA-001.json": "other_or_unclear",
        "COUGH-DYSPHONIA-001.json": "chronic_or_recurrent",
        "COUGH-GERD-001.json": "chronic_or_recurrent",
        "COUGH-IMMUNOCOMPROMISED-001.json": "current_acute",
        "COUGH-KO-COLD-001.json": "current_acute",
        "COUGH-SUDDEN-001.json": "other_or_unclear",
        "COUGH-SYSTEMIC-001.json": "current_acute",
        "COUGH-TB-RISK-001.json": "chronic_or_recurrent",
    }
    new_fact_ids = {item["fact"]["id"] for item in fragment["entries"] if item["fact"]["id"].startswith("cough.")}
    for name, context in legacy_contexts.items():
        path = SIM_ROOT / name
        case = json.loads(path.read_text(encoding="utf-8"))
        supplemental = routine(context)
        for fact_id, state in supplemental.items():
            if fact_id in new_fact_ids or fact_id == "cough.primary_context":
                case.setdefault("hidden_state", {}).setdefault(fact_id, state)
        expected = case.setdefault("expected", {})
        if expected.get("expected_safety_level") in {None, "routine", "clarify"}:
            expected["expected_max_turns"] = max(expected.get("expected_max_turns", 0), 35)
        write_json(f"simulation/patients/respiratory/{name}", case)


def main() -> None:
    fragment = strengthen_fragment()
    policy = strengthen_policy()
    write_json(FRAGMENT, fragment)
    write_json(POLICY, policy)
    write_json(CLINICIAN, strengthen_clinician(fragment))
    pain = load(PAIN)
    pain["profile_bindings"]["cough"] = {
        "activation": "when",
        "when": {"fact": "symptom.chest_pain", "equals": True},
        "existing_nrs_fact": "cough.chest_pain_nrs",
    }
    write_json(PAIN, pain)
    add_simulations(fragment, policy)


if __name__ == "__main__":
    main()
