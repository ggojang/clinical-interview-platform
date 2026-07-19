#!/usr/bin/env python3
"""Strengthen research-only palpitations knowledge for clinician handoff."""
from __future__ import annotations

import seed_palpitations
from profile_support import *


P = "palpitations"
FRAGMENT = "knowledge/generated/cardiovascular/palpitations/palpitations.json"
POLICY = "policies/primary-care-palpitations-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
PAIN = "knowledge/shared/hira-pain-assessment.json"
SIM_ROOT = ROOT / "simulation/patients/cardiovascular/palpitations"
SOURCES = [
    "source.nhs.heart-palpitations.2026",
    "source.nice.ng196.atrial-fibrillation.2021",
    "source.nice.cg109.blackouts.2023",
    "source.stom.mrcm.palpitations.20260714",
]
G = {key: f"group.palpitations.{key}" for key in (
    "routing", "episode-course", "rhythm-detail", "associated-sequence",
    "trigger-detail", "cardiac-history", "systemic-context",
    "previous-investigation", "function", "handoff",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def q(fid, display, vt, key, wording, score, group, intents, **kwargs):
    return entry(
        P, fid, display, vt, key, wording, score, key, [G[group]],
        intents=intents, **kwargs,
    )


def fragment():
    doc = load(FRAGMENT)
    contexts = [
        "current_or_persistent", "episodic_recurrent", "wearable_or_pulse_record",
        "exertional", "postural_or_volume_related", "medicine_or_substance_related",
        "pregnancy_anemia_thyroid_or_systemic", "other_unclear",
    ]
    additions = [
        q("palpitations.primary_context", "Primary Palpitations Context", "coded", "primary-context", "가장 가까운 상황은 현재 지속 중, 간헐적 반복, 기기·맥박 기록 확인, 운동 관련, 자세·탈수 관련, 약물·카페인 등 관련, 임신·빈혈·갑상선 등 전신 상황, 또는 불분명 중 무엇인가요?", 119, "routing", C + R, allowed_values=contexts),
        q("palpitations.patient_words_and_heartbeat_location", "Patient Description and Perceived Location", "string", "patient-words", "본인의 표현으로 심장이 어떻게 뛰는 느낌인지와 가슴·목·귀·배 등 어디에서 느끼는지 알려주세요.", 113, "rhythm-detail", C),
        q("palpitations.first_latest_onset_exact_time_context_and_trend", "First and Latest Episode Timeline", "string", "onset-timeline", "처음과 가장 최근 증상의 날짜·시각, 당시 하던 일과 최근 빈도·지속시간·강도의 변화 추세를 알려주세요.", 112, "episode-course", C + R),
        q("palpitations.episode_count_duration_range_and_between_episode_state", "Episode Count Duration Range and Inter-episode State", "string", "episode-count", "하루·주당 횟수, 가장 짧고 긴 지속시간과 증상 사이에는 완전히 정상으로 돌아오는지 알려주세요.", 111, "episode-course", C),
        q("palpitations.onset_offset_precipitant_termination_and_maneuver", "Episode Start Stop and Termination Detail", "string", "onset-offset-detail", "갑자기 또는 서서히 시작·종료하는지, 시작 직전 상황과 저절로·휴식·자세변화·기침·숨참기 등 어떻게 끝났는지 알려주세요.", 110, "episode-course", C),
        q("palpitations.pulse_measurement_method_time_rate_range_and_reliability", "Pulse Measurement Method Rate and Reliability", "string", "pulse-provenance", "증상 중 맥박을 손으로 잰 것인지 기기로 측정했는지, 측정 시각·분당 최저/최고·규칙성과 기록의 신뢰도를 알려주세요.", 109, "rhythm-detail", C + R),
        q("palpitations.wearable_ecg_timestamp_duration_symptom_correlation_and_source", "Wearable ECG and Symptom Correlation", "string", "wearable-record", "스마트워치·휴대형 ECG 기록이 있다면 날짜·시각·기록 길이, 그때 증상과 기기 표시 문구를 원문 그대로 알려주세요.", 108, "rhythm-detail", C + R),
        q("palpitations.associated_symptom_order_before_during_after_and_recovery", "Associated Symptom Sequence and Recovery", "string", "associated-sequence", "흉통·호흡곤란·어지럼·실신·땀·메스꺼움 등이 두근거림 전·중·후 어느 순서로 생겼고 회복까지 얼마나 걸렸는지 알려주세요.", 107, "associated-sequence", C + S),
        q("palpitations.chest_pain_nrs", "Chest Pain NRS", "quantity", "chest-pain-nrs", "[필수] 두근거림과 관련된 흉통이 있었다면 가장 심할 때 통증을 0부터 10까지 숫자로 알려주세요.", 106, "associated-sequence", C + S),
        q("palpitations.chest_pain_site_character_radiation_duration_and_relation", "Chest Pain Pattern with Palpitations", "string", "chest-pain-detail", "흉통이 있었다면 부위·양상·퍼지는 곳·지속시간과 두근거림·운동·호흡·자세와의 관계를 알려주세요.", 105, "associated-sequence", C + S),
        q("palpitations.dyspnea_rest_exertion_speech_sleep_and_recovery", "Dyspnea Detail with Palpitations", "string", "dyspnea-detail", "숨참이 있었다면 안정 시·운동 시 여부, 말하기·눕기·수면 영향, 지속시간과 회복 과정을 알려주세요.", 104, "associated-sequence", C + S),
        q("palpitations.syncope_witness_posture_prodrome_injury_duration_recovery", "Syncope Witness and Recovery Detail", "string", "syncope-detail", "실신·실신 직전 증상이 있었다면 자세·전조·목격 내용·의식소실 시간·부상·회복 후 혼란과 응급진료 여부를 알려주세요.", 103, "associated-sequence", S + R),
        q("palpitations.exertion_activity_threshold_during_or_after_and_recovery", "Exertional Threshold and Recovery", "string", "exertion-detail", "걷기·계단·달리기 등 어느 활동 수준에서 운동 중 또는 직후 시작했고 쉬면 얼마 만에 회복하는지 알려주세요.", 102, "trigger-detail", C + R),
        q("palpitations.posture_standing_time_hydration_heat_illness_and_bp", "Postural Hydration and Blood Pressure Context", "string", "postural-detail", "눕거나 앉았다 일어난 뒤 몇 초·분에 생기는지, 수분섭취·더위·설사/구토·최근 질병과 당시 혈압 기록을 알려주세요.", 96, "trigger-detail", D + R),
        q("palpitations.sleep_nocturnal_lying_meal_and_reflux_relation", "Sleep Nocturnal Meal and Lying Relation", "string", "sleep-meal", "수면 중 깨거나 누울 때, 식사·과식·역류 증상 전후로 생기는지와 수면을 얼마나 방해하는지 알려주세요.", 88, "trigger-detail", C + D),
        q("palpitations.caffeine_energy_alcohol_nicotine_amount_timing_change", "Detailed Stimulant Exposure Timing", "string", "stimulant-detail", "커피·차·에너지음료·술·담배·전자담배의 하루·주당 양, 마지막 사용 시각과 최근 증가·중단을 알려주세요.", 95, "trigger-detail", D + R),
        q("palpitations.medicine_decongestant_inhaler_thyroid_supplement_dose_timing", "Medicine and Supplement Timing Detail", "string", "medicine-detail", "처방약·감기약/비충혈제거제·흡입제·갑상선약·체중감량제·한약/보충제의 이름·용량·변경일과 증상 시점을 알려주세요.", 101, "trigger-detail", D + R),
        q("palpitations.recreational_stimulant_withdrawal_and_other_exposure_timing", "Recreational Stimulant and Withdrawal Timing", "string", "substance-detail", "코카인·암페타민 등 각성제나 다른 물질 사용, 술·진정제 중단과 증상 시점의 관계를 답할 수 있는 범위에서 알려주세요.", 94, "trigger-detail", R),
        q("palpitations.prior_arrhythmia_cardioversion_ablation_device_and_followup", "Prior Arrhythmia Procedure and Device History", "string", "arrhythmia-history", "이전 부정맥 진단, 전기충격·도자절제술, 심박동기/제세동기 여부와 담당 의료기관·최근 추적일을 알려주세요.", 100, "cardiac-history", R),
        q("palpitations.structural_heart_failure_ischemic_valve_congenital_history", "Detailed Cardiac History", "string", "cardiac-history", "심부전·관상동맥질환·심근병증·판막·선천성 심장질환의 진단명, 시기, 현재 상태를 알려주세요.", 99, "cardiac-history", R),
        q("palpitations.thyroid_anemia_electrolyte_glucose_lab_date_result_source", "Relevant Laboratory Result Context", "string", "lab-context", "갑상선·혈색소/철분·전해질·혈당 검사의 최근 날짜·결과·추세와 자료 출처를 알려주세요.", 93, "systemic-context", D + R),
        q("palpitations.pregnancy_gestation_postpartum_bleeding_and_obstetric_context", "Pregnancy and Postpartum Detail", "string", "pregnancy-detail", "해당되는 경우 임신 주수·출산 후 기간, 출혈·빈혈·고혈압과 임신 전후 약 변경을 알려주세요.", 92, "systemic-context", R),
        q("palpitations.fever_infection_dehydration_sleep_and_recent_illness", "Recent Illness Dehydration and Sleep Context", "string", "illness-context", "최근 발열·감염·탈수·구토/설사, 수면 부족과 회복 중인 질환이 증상보다 언제 생겼는지 알려주세요.", 91, "systemic-context", D + R),
        q("palpitations.family_arrhythmia_cardiomyopathy_channelopathy_sudden_death_age", "Detailed Family Cardiac History", "string", "family-detail", "가족의 부정맥·심근병증·유전성 심장질환·심박동기와 돌연사 당시 나이·상황을 알려주세요.", 98, "cardiac-history", R),
        q("palpitations.prior_12lead_ecg_date_result_symptom_state_and_source", "Prior 12-lead ECG Result", "string", "ecg-result", "이전 12유도 ECG의 날짜·설명받은 결과, 검사 당시 증상 유무와 결과 자료 출처를 알려주세요.", 97, "previous-investigation", R),
        q("palpitations.ambulatory_monitor_type_duration_result_and_symptom_correlation", "Ambulatory Rhythm Monitor Result", "string", "monitor-result", "Holter·패치·event monitor의 종류·착용기간·날짜, 설명받은 결과와 증상 버튼·일지의 일치 여부를 알려주세요.", 96, "previous-investigation", R),
        q("palpitations.echo_stress_test_lab_and_device_check_result", "Other Cardiac Test and Device Check Result", "string", "other-tests", "심초음파·운동검사·혈액검사·기기 점검의 날짜·결과와 아직 확인하지 못한 항목을 알려주세요.", 90, "previous-investigation", R),
        q("palpitations.prior_ed_admission_treatment_response_and_recurrence", "Prior Emergency Care Treatment and Recurrence", "string", "prior-care", "이 증상으로 응급실·입원한 시기, 당시 맥박/리듬·처치와 반응, 퇴원 후 재발 과정을 알려주세요.", 89, "previous-investigation", R),
        q("palpitations.function_sleep_work_driving_exercise_and_selfcare_impact", "Functional Safety and Activity Impact", "string", "function", "수면·출근/등교·운전·기계조작·운동·식사·자가관리에서 제한하거나 중단한 활동을 알려주세요.", 87, "function", C + R),
        q("palpitations.occupation_shift_heat_exertion_and_safety_exposure", "Occupation Shift and Safety Exposure", "string", "occupation", "직업·교대근무·고온·고강도 활동·고소작업·운전 등 증상과 관련되거나 안전에 영향을 주는 환경을 알려주세요.", 86, "function", R),
        q("palpitations.information_source_reliability_conflict_and_proxy", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자·목격자 중 누가 답하는지, 일지·기기·의무기록 유무와 기억이 불확실하거나 자료가 서로 다른 부분을 알려주세요.", 85, "handoff", R),
        q("palpitations.patient_concern_goal_expectation_and_additional_comment", "Patient Concern Goal and Additional Comment", "string", "goal", "가장 걱정되는 점, 진료에서 확인하고 싶은 내용과 질문에 없던 다른 증상·의견을 알려주세요.", 84, "handoff", C + R),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.update({item["fact"]["id"]: item for item in additions})
    # A patient commonly reports a pulse as a bare number. Declare the UCUM
    # unit so Runtime can preserve it as an interoperable quantity without
    # guessing units for unrelated quantity Facts such as symptom duration.
    entries["observation.pulse_rate_during_episode"]["fact"]["unit"] = "/min"
    doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc["extra_nodes"]}
    for key, identifier in G.items():
        nodes[identifier] = {
            "id": identifier, "type": "ClinicalGroup",
            "display": key.replace("-", " ").title(),
        }
    doc["extra_nodes"] = list(nodes.values())
    doc["default_refresh"].update({
        "last_assessed_at": "2026-07-19",
        "next_monitor_at": "2026-07-21",
        "next_full_review_at": "2027-01-15",
    })
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc):
    result = completion_policy(
        prefix=P, fragment=doc, presentation_fact="symptom.palpitations.current",
        question_budget=75, source_refs=SOURCES,
    )
    result["required_facts"]["routine"] = [
        "palpitations.primary_context", "symptom.duration",
        "symptom.palpitations.episode_duration", "symptom.palpitations.frequency",
        "symptom.palpitations.onset_offset", "symptom.palpitations.sensation",
        "palpitations.patient_words_and_heartbeat_location",
        "palpitations.first_latest_onset_exact_time_context_and_trend",
        "palpitations.episode_count_duration_range_and_between_episode_state",
        "palpitations.associated_symptom_order_before_during_after_and_recovery",
        "symptom.dyspnea", "symptom.dizziness",
        "palpitations.function_sleep_work_driving_exercise_and_selfcare_impact",
        "palpitations.information_source_reliability_conflict_and_proxy",
        "palpitations.patient_concern_goal_expectation_and_additional_comment",
    ]
    result["conditional_required_facts"] = [{
        "selector_fact": "palpitations.primary_context",
        "cases": {
            "current_or_persistent": [
                "observation.pulse_rate_during_episode", "observation.pulse_regular_during_episode",
                "palpitations.pulse_measurement_method_time_rate_range_and_reliability",
                "palpitations.chest_pain_site_character_radiation_duration_and_relation",
                "palpitations.dyspnea_rest_exertion_speech_sleep_and_recovery",
            ],
            "episodic_recurrent": [
                "palpitations.onset_offset_precipitant_termination_and_maneuver",
                "palpitations.sleep_nocturnal_lying_meal_and_reflux_relation",
                "palpitations.prior_12lead_ecg_date_result_symptom_state_and_source",
                "palpitations.ambulatory_monitor_type_duration_result_and_symptom_correlation",
                "palpitations.prior_ed_admission_treatment_response_and_recurrence",
            ],
            "wearable_or_pulse_record": [
                "observation.pulse_rate_during_episode", "observation.pulse_regular_during_episode",
                "palpitations.pulse_measurement_method_time_rate_range_and_reliability",
                "palpitations.wearable_ecg_timestamp_duration_symptom_correlation_and_source",
                "investigation.ecg_or_device_record_available",
            ],
            "exertional": [
                "trigger.palpitations.exertion",
                "palpitations.exertion_activity_threshold_during_or_after_and_recovery",
                "palpitations.syncope_witness_posture_prodrome_injury_duration_recovery",
                "palpitations.structural_heart_failure_ischemic_valve_congenital_history",
                "palpitations.family_arrhythmia_cardiomyopathy_channelopathy_sudden_death_age",
            ],
            "postural_or_volume_related": [
                "trigger.palpitations.postural",
                "palpitations.posture_standing_time_hydration_heat_illness_and_bp",
                "palpitations.fever_infection_dehydration_sleep_and_recent_illness",
                "palpitations.thyroid_anemia_electrolyte_glucose_lab_date_result_source",
            ],
            "medicine_or_substance_related": [
                "medication.recent_change_palpitations",
                "palpitations.medicine_decongestant_inhaler_thyroid_supplement_dose_timing",
                "palpitations.caffeine_energy_alcohol_nicotine_amount_timing_change",
                "palpitations.recreational_stimulant_withdrawal_and_other_exposure_timing",
                "palpitations.fever_infection_dehydration_sleep_and_recent_illness",
            ],
            "pregnancy_anemia_thyroid_or_systemic": [
                "patient.pregnant_or_postpartum", "history.thyroid_disease", "history.anemia",
                "symptom.bleeding_or_anemia_features", "symptom.weight_loss_heat_intolerance",
                "palpitations.pregnancy_gestation_postpartum_bleeding_and_obstetric_context",
                "palpitations.thyroid_anemia_electrolyte_glucose_lab_date_result_source",
            ],
            "other_unclear": [
                "trigger.palpitations.exertion", "trigger.palpitations.postural",
                "trigger.palpitations.stress_or_panic",
                "palpitations.sleep_nocturnal_lying_meal_and_reflux_relation",
                "palpitations.caffeine_energy_alcohol_nicotine_amount_timing_change",
                "palpitations.prior_arrhythmia_cardioversion_ablation_device_and_followup",
                "palpitations.echo_stress_test_lab_and_device_check_result",
                "palpitations.occupation_shift_heat_exertion_and_safety_exposure",
            ],
        },
    }]
    return result


def clinician(doc):
    result = load(CLINICIAN)
    ids = {item["fact"]["id"] for item in doc["entries"]}
    ids.update({"pain.frequency", "palpitations.chest_pain_nrs"})
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.palpitations"] = sorted(ids)
    return result


def condition_state(condition):
    result = {}
    for child in condition.get("all", [condition]):
        if "fact" in child:
            result[child["fact"]] = {
                "value": child.get("equals", child.get("in", [True])[0])
            }
    return result


def cases(doc, completion):
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    forbidden = [
        "diagnosis.atrial_fibrillation", "diagnosis.supraventricular_tachycardia",
        "diagnosis.ventricular_tachycardia", "recommendation.beta_blocker",
        "recommendation.antiarrhythmic", "recommendation.cardioversion",
    ]
    result = {}
    for index, rule in enumerate(doc["safety_rules"]):
        key = rule["id"].split("safety.", 1)[1]
        level = rule["then"]["safety_level"]
        result[f"PALP-{key.upper()}.json"] = {
            "id": f"PALP-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 28 + index * 5},
            "initial_statement": {"ko": "두근거림과 함께 즉시 확인할 증상이 있습니다."},
            "hidden_state": condition_state(rule["when"]),
            "expected": {
                "expected_safety_level": level, "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [rule["id"]],
                "expected_max_turns": 30, "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }
    always = completion["required_facts"]["always"]
    base = completion["required_facts"]["routine"]
    branches = completion["conditional_required_facts"][0]["cases"]

    def value(fid):
        fact = by_id[fid]
        if fid == "observation.pulse_rate_during_episode": return 96
        if fact["value_type"] == "boolean": return False
        if fact["value_type"] == "coded": return fact.get("allowed_values", ["unclear"])[-1]
        if fact["value_type"] == "quantity": return {"amount": 3, "unit": "days"}
        return "특이사항 없음"

    def routine(branch):
        state = {fid: {"value": value(fid)} for fid in dict.fromkeys([*always, *base, *branches[branch]])}
        state["symptom.palpitations.current"] = {"value": False}
        state["palpitations.primary_context"] = {"value": branch}
        return state

    specs = [
        ("EPISODIC-COURSE", "episodic_recurrent", 44, "간헐적으로 반복되는 두근거림의 시간 양상을 정리합니다.", {}),
        ("WEARABLE-RECORD", "wearable_or_pulse_record", 39, "스마트워치 기록과 증상 시점을 의료진에게 전달합니다.", {"investigation.ecg_or_device_record_available": {"value": True}}),
        ("EXERTIONAL-NO-SYNCOPE", "exertional", 33, "운동 때 생기지만 실신은 없는 두근거림을 정리합니다.", {"trigger.palpitations.exertion": {"value": True}}),
        ("POSTURAL-DEHYDRATION-CONTEXT", "postural_or_volume_related", 68, "일어설 때 생기는 두근거림과 수분·혈압 상황을 정리합니다.", {"trigger.palpitations.postural": {"value": True}}),
        ("MEDICINE-SUBSTANCE-TIMING", "medicine_or_substance_related", 51, "감기약과 카페인 변화 뒤 두근거림 시점을 정리합니다.", {}),
        ("PREGNANCY-SYSTEMIC", "pregnancy_anemia_thyroid_or_systemic", 31, "임신 중 두근거림과 빈혈·갑상선 검사 내용을 정리합니다.", {"patient.pregnant_or_postpartum": {"value": "pregnant"}}),
        ("UNCLEAR-PROXY-OLDER", "other_unclear", 82, "보호자가 고령자의 불분명한 두근거림을 대신 설명합니다.", {"palpitations.information_source_reliability_conflict_and_proxy": {"value": "보호자 대리, 목격과 본인 기억이 다름"}}),
        ("PRIOR-CHEST-PAIN-NRS", "episodic_recurrent", 57, "지금은 멎었지만 이전 두근거림 중 흉통이 있었습니다.", {"symptom.chest_pain": {"value": True}, "pain.frequency": {"value": "less_than_daily"}, "palpitations.chest_pain_nrs": {"value": 4}}),
        ("OCCUPATIONAL-SAFETY", "other_unclear", 48, "교대근무와 운전 업무 중 생긴 두근거림의 영향을 정리합니다.", {"palpitations.occupation_shift_heat_exertion_and_safety_exposure": {"value": "야간 교대와 운전 업무, 증상 때 운전 중단"}}),
        ("MULTI-RFE-ADDITIONAL-COMMENT", "other_unclear", 62, "두근거림 외에 체중 감소도 별도 문진하고 싶습니다.", {"palpitations.patient_concern_goal_expectation_and_additional_comment": {"value": "체중 감소를 별도 RFE로 전달 요청"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine(branch); state.update(overrides)
        expected = {
            "expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 70, "forbidden_assertions": forbidden,
        }
        if key == "PRIOR-CHEST-PAIN-NRS":
            expected["expected_known_facts"] = {"palpitations.chest_pain_nrs": 4}
        result[f"PALP-{key}.json"] = {
            "id": f"PALP-{key}", "simulation_language": "ko", "persona": {"age": age},
            "initial_statement": {"ko": statement}, "hidden_state": state,
            "expected": expected, "provenance": provenance(SOURCES),
        }
    absent = routine("wearable_or_pulse_record")
    missing = "palpitations.wearable_ecg_timestamp_duration_symptom_correlation_and_source"
    absent.pop(missing)
    result["PALP-DATA-ABSENT-RECORD.json"] = {
        "id": "PALP-DATA-ABSENT-RECORD", "simulation_language": "ko",
        "persona": {"age": 73},
        "encounter_context": {
            "care_setting": "primary_care", "encounter_type": "new_encounter",
            "interview_initiator": "caregiver", "interview_mode": "telephone",
            "available_information": ["no_previous_records"],
            "time_constraint": "scheduled", "clinical_responsibility": "decision_support",
        },
        "initial_statement": {"ko": "보호자가 답하지만 기기 기록 원본은 확인할 수 없습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "asked-unknown"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 70, "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }
    return result


def main():
    seed_palpitations.main()
    doc = fragment(); completion = policy(doc)
    write_json(FRAGMENT, doc); write_json(POLICY, completion)
    write_json(CLINICIAN, clinician(doc))
    pain = load(PAIN)
    pain["profile_bindings"]["palpitations"] = {
        "activation": "when", "when": {"fact": "symptom.chest_pain", "equals": True},
        "existing_nrs_fact": "palpitations.chest_pain_nrs",
    }
    write_json(PAIN, pain)
    for old in SIM_ROOT.glob("*.json"): old.unlink()
    for name, case in cases(doc, completion).items():
        write_json(f"simulation/patients/cardiovascular/palpitations/{name}", case)


if __name__ == "__main__":
    main()
