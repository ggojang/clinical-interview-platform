#!/usr/bin/env python3
"""Strengthen research-only urinary symptom clinician handoff knowledge."""
from __future__ import annotations

import json

from profile_support import ROOT, entry, write_json


P = "urinary"
FRAGMENT = "knowledge/generated/genitourinary/urinary-symptoms/urinary-symptoms.json"
POLICY = "policies/primary-care-urinary-symptoms-completion.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
RESEARCH = "sources/manifests/primary-care-urinary-symptoms-research.json"
CREATED = "2026-07-21T00:00:00Z"
SOURCES = [
    "source.nhs.uti.2025",
    "source.nice.qs90.uti-adults.2023",
    "source.nice.ng111.pyelonephritis.2018",
    "source.nice.cg97.luts.2024",
    "source.nice.ng12.urinary.2026",
]
GROUPS = {
    key: f"group.urinary.{key}"
    for key in (
        "routing", "course", "storage-detail", "voiding-detail", "leakage-detail",
        "urine-change", "infection-detail", "treatment", "history", "life-stage",
        "function", "handoff",
    )
}
C = ["intent.characterize_symptom"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]
S = ["intent.screen_red_flags"]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def provenance(source_refs: list[str]) -> dict:
    return {
        "created_by": {"type": "ai", "id": "codex-gpt5"},
        "created_at": CREATED,
        "source_refs": source_refs,
        "review_status": "unreviewed",
        "version": "0.1.0",
    }


def question(
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
    return entry(
        P, fact_id, display, value_type, key, wording, min(score, 95), key,
        [GROUPS[group]], intents=intents, **kwargs,
    )


def build_fragment() -> dict:
    doc = load(FRAGMENT)
    additions = [
        question("urinary.patient_words_first_change_main_concern", "Patient Description and Main Concern", "string", "patient-words", "처음 달라졌다고 느낀 배뇨 상태, 지금 가장 불편한 점과 가장 걱정되는 점을 본인의 표현으로 알려주세요.", 129, "routing", C),
        question("urinary.first_latest_onset_course_baseline_and_fluctuation", "Detailed Onset Course and Baseline", "string", "course", "처음과 가장 최근 증상의 시작 날짜·상황, 갑작스럽거나 서서히 시작했는지, 지속·반복·악화·호전 양상과 평소 배뇨 상태를 알려주세요.", 128, "course", C + R),
        question("urinary.episode_frequency_duration_triggers_recovery_and_between_state", "Episode Pattern", "string", "episode-pattern", "증상이 반복된다면 하루·주당 횟수, 한 번의 지속시간, 유발 상황, 회복과 증상 사이 상태를 알려주세요.", 127, "course", C),
        question("urinary.symptom_burden_sleep_work_travel_selfcare_and_distress", "Functional Impact and Distress", "string", "function", "배뇨 증상이 수면, 업무·학업, 외출·이동, 성생활, 자기관리와 정서적 부담에 어떤 영향을 주는지 알려주세요.", 126, "function", C + R),
        question("urinary.daytime_frequency_nocturia_actual_counts_baseline_and_change", "Frequency and Nocturia Counts", "string", "frequency-counts", "낮과 밤의 실제 배뇨 횟수, 평소 횟수와 최근 변화, 밤에 깨는 횟수와 다시 잠드는 영향을 알려주세요.", 125, "storage-detail", C),
        question("urinary.urgency_warning_time_triggers_toilet_access_and_leak_relation", "Urgency Pattern", "string", "urgency-pattern", "갑자기 마려울 때 참을 수 있는 시간, 물소리·추위·이동 같은 유발요인, 화장실 접근성과 소변이 새는 시간관계를 알려주세요.", 124, "storage-detail", C),
        question("urinary.voided_volume_fluid_intake_timing_and_frequency_volume_diary", "Voided Volume and Bladder Diary", "string", "frequency-volume", "한 번 소변량의 많고 적음, 하루 수분·카페인·술 섭취량과 시간, 배뇨량 기록표나 방광일지가 있는지 알려주세요.", 123, "storage-detail", C + R),
        question("urinary.hesitancy_straining_intermittency_spray_stream_and_postvoid_dribble", "Detailed Voiding Pattern", "string", "voiding-pattern", "소변 시작 지연, 힘주기, 끊김, 갈라지거나 튀는 줄기, 약한 줄기와 배뇨 후 방울이 떨어지는 양상을 알려주세요.", 122, "voiding-detail", C),
        question("urinary.fullness_distension_residual_sensation_retention_episode_and_relief", "Bladder Fullness and Retention History", "string", "retention-history", "아랫배 팽만·방광이 찬 느낌, 잔뇨감, 전혀 못 본 시간과 이전 요폐·도뇨 후 완화 경험을 알려주세요.", 121, "voiding-detail", C + S),
        question("urinary.incontinence_type_amount_frequency_pad_skin_and_baseline", "Detailed Incontinence Pattern", "string", "incontinence-pattern", "기침·운동 때, 갑자기 마려울 때, 모르게 또는 계속 새는지, 양·횟수·패드 사용과 피부 문제, 평소 상태를 알려주세요.", 120, "leakage-detail", C + R),
        question("urinary.dysuria_site_before_during_after_void_and_pain_radiation", "Dysuria Timing and Site", "string", "dysuria-detail", "통증·화끈거림의 정확한 부위와 소변 전·중·후 언제 심한지, 아랫배·옆구리·등·사타구니·생식기로 퍼지는지 알려주세요.", 119, "infection-detail", C + R),
        question("urinary.urine_colour_clarity_odour_blood_clots_timing_and_source", "Urine Appearance and Blood Detail", "string", "urine-appearance", "소변 색·탁함·냄새, 피의 색과 혈전, 처음·중간·끝 또는 전 과정 중 언제 보이는지, 질출혈 등 다른 출혈 가능성을 알려주세요.", 118, "urine-change", C + R),
        question("urinary.fever_measured_temperature_chills_vomiting_and_systemic_timeline", "Systemic Symptom Timeline", "string", "systemic-timeline", "측정한 최고·최저 체온과 날짜, 오한·떨림, 메스꺼움·구토, 기운 저하가 배뇨 증상과 어떤 순서로 생겼는지 알려주세요.", 117, "infection-detail", R + S),
        question("urinary.intake_hydration_urine_output_dehydration_and_last_void", "Hydration and Urine Output", "string", "hydration-output", "최근 마신 수분량, 소변 총량의 변화, 입마름·어지럼 같은 탈수 증상과 마지막으로 소변 본 시간을 알려주세요.", 116, "infection-detail", R + S),
        question("urinary.recurrent_episode_dates_frequency_culture_organism_and_response", "Recurrent Episode Detail", "string", "recurrence-detail", "이전 비슷한 증상의 날짜와 최근 6개월·12개월 횟수, 당시 소변배양 균·감수성 결과, 치료와 재발까지의 간격을 알려주세요.", 115, "history", R),
        question("urinary.current_recent_antibiotic_product_dose_schedule_start_adherence_and_response", "Antibiotic Detail and Response", "string", "antibiotic-detail", "현재·최근 항생제의 제품/성분명, 용량·횟수, 시작·마지막 복용일, 실제 복용과 48시간 내 증상 변화·부작용을 알려주세요.", 114, "treatment", R + S),
        question("urinary.analgesic_urinary_otc_herbal_selfcare_and_effect", "Self-care and Non-antibiotic Treatment", "string", "selfcare", "진통제, 방광·전립선 약, 일반약·한약·보충제와 수분 조절 등 시도한 방법, 사용 시기·효과·부작용을 알려주세요.", 113, "treatment", R),
        question("urinary.current_medicines_diuretic_anticholinergic_decongestant_sglt2_and_change", "Medicines Affecting Urination", "string", "medicine-context", "복용 중인 모든 약 중 이뇨제, 감기약, 항히스타민·항콜린 약, 당뇨약 등을 포함해 제품명·용량·변경일과 배뇨 변화의 관계를 알려주세요.", 112, "treatment", R + D),
        question("urinary.medicine_food_contrast_latex_allergy_and_reaction", "Relevant Allergy Detail", "string", "allergy", "약·조영제·라텍스·음식 알레르기 또는 이상반응이 있다면 원인, 증상, 심한 정도와 발생 시기를 알려주세요.", 111, "treatment", R),
        question("urinary.prior_urinalysis_dipstick_microscopy_culture_result_date_and_source", "Prior Urine Test Provenance", "string", "urine-results", "최근 소변검사·시험지, 현미경검사·배양·감수성 결과가 있다면 날짜, 수치·균명, 항생제 전후 여부와 자료 출처를 알려주세요.", 110, "handoff", R),
        question("urinary.prior_renal_function_imaging_residual_flow_cystoscopy_prostate_and_pending", "Prior Urological Assessment", "string", "prior-assessment", "신장기능, 초음파·CT, 잔뇨·요속, 방광경, 전립선 평가 결과가 있다면 날짜·결과·자료 출처와 아직 확인하지 못한 항목을 알려주세요.", 109, "handoff", R),
        question("urinary.stone_surgery_procedure_device_structural_neurologic_and_pelvic_history", "Relevant Urinary and Pelvic History", "string", "history-detail", "요로결석, 신장·방광·전립선·골반 질환과 수술·시술, 요로 구조 이상, 신경계 질환, 방사선치료 또는 기기 사용 이력을 알려주세요.", 108, "history", R),
        question("urinary.renal_diabetes_neurologic_constipation_prostate_pelvicfloor_and_gynaecologic_context", "Comorbidity Context", "string", "comorbidity", "신장질환, 당뇨, 신경계 질환, 변비, 전립선·골반저·부인과 질환과 현재 조절 상태를 알려주세요.", 107, "history", R + D),
        question("urinary.catheter_type_indication_insertion_change_drainage_blockage_leak_and_care", "Catheter Detail", "string", "catheter-detail", "도뇨관이 있다면 종류·삽입 이유, 삽입·교체일, 배액량·색, 막힘·누출·통증과 관리 방법을 알려주세요.", 106, "history", R + S),
        question("urinary.pregnancy_lmp_gestation_postpartum_breastfeeding_and_symptom_relation", "Pregnancy and Postpartum Context", "string", "pregnancy-context", "해당되는 경우 마지막 월경일, 임신 가능성·검사·주수, 출산 후 기간과 수유, 증상·약 복용의 시간관계를 알려주세요.", 105, "life-stage", R),
        question("urinary.sexual_contact_sti_discharge_lesion_pelvic_testicular_and_partner_context", "Sexual and Genital Context", "string", "sexual-context", "최근 성접촉·피임·콘돔 사용, 성매개감염 검사, 분비물·병변·골반·고환 증상과 파트너 증상 여부를 알려주세요.", 104, "life-stage", R + D),
        question("urinary.menstrual_menopause_vaginal_dryness_bleeding_discharge_and_prolapse", "Menstrual Menopause and Vaginal Context", "string", "gynaecologic-context", "월경·폐경 상태, 질건조·통증·출혈·분비물, 골반장기 탈출감과 배뇨 증상의 관계를 알려주세요.", 103, "life-stage", R + D),
        question("urinary.child_age_fever_feeding_vomiting_irritability_bedwetting_constipation_and_proxy", "Child Urinary Context", "string", "child-context", "소아라면 나이·체중, 발열, 수유·식사·구토, 보챔, 새 야뇨·실금, 변비와 보호자가 관찰한 평소 대비 변화를 알려주세요.", 102, "life-stage", R + S),
        question("urinary.older_frailty_cognition_delirium_continence_falls_and_baseline", "Older Adult Baseline and Delirium Context", "string", "older-context", "고령·허약한 경우 평소 인지·행동·요실금·이동 상태와 최근 혼돈·졸림·낙상·돌봄 변화 및 관찰자를 알려주세요.", 101, "life-stage", R + S),
        question("urinary.occupation_fluid_toilet_access_heat_exposure_travel_and_safeguarding", "Occupation and Access Context", "string", "occupation-context", "직업·교대근무, 수분과 화장실 접근 제한, 더위·화학물질 노출, 최근 여행·시설생활과 안전·돌봄 우려를 알려주세요.", 100, "function", R),
        question("urinary.smoking_vaping_chemical_exposure_and_hematuria_risk_context", "Smoking and Chemical Exposure", "string", "exposure-context", "현재·과거 흡연·전자담배의 양과 기간, 염료·고무·석유 등 직업성 화학물질 노출이 있다면 종류와 기간을 알려주세요.", 99, "history", R),
        question("urinary.family_renal_stone_recurrent_uti_and_urological_cancer_history", "Relevant Family History", "string", "family-history", "가족의 신장질환, 요로결석·반복 감염, 전립선·방광·신장암 이력이 있다면 관계와 발병 나이를 알려주세요.", 98, "history", R),
        question("urinary.information_source_proxy_record_reliability_conflict_and_consent", "Information Source and Reliability", "string", "information-source", "본인·보호자 중 누가 답하는지, 배뇨일지·약 목록·검사자료 유무, 기억이 불확실하거나 서로 다른 내용과 공유 동의 범위를 알려주세요.", 97, "handoff", R),
        question("urinary.prior_ipss_or_validated_measure_name_raw_score_date_context_and_source", "Prior Validated Measure Provenance", "string", "prior-measure", "이전에 시행한 IPSS 등 배뇨 설문이 있다면 도구명, 원점수, 날짜, 시행 상황과 자료 출처를 알려주세요. 이 문진은 점수를 임의 계산하지 않습니다.", 96, "handoff", R),
        question("urinary.patient_goal_preference_expected_help_additional_comment_and_other_rfe", "Patient Goal and Additional RFE", "string", "goal", "진료에서 확인하고 싶은 내용, 선호하거나 피하고 싶은 도움, 질문에 없던 의견과 별도 문진이 필요한 다른 문제를 알려주세요.", 95, "handoff", C + R),
    ]
    entries = {item["fact"]["id"]: item for item in doc["entries"]}
    entries.update({item["fact"]["id"]: item for item in additions})
    doc["entries"] = list(entries.values())
    nodes = {item["id"]: item for item in doc.get("extra_nodes", [])}
    for key, identifier in GROUPS.items():
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


def build_policy(doc: dict) -> dict:
    policy = load(POLICY)
    policy["required_facts"]["routine"] = [
        "symptom.duration",
        "urinary.patient_words_first_change_main_concern",
        "urinary.first_latest_onset_course_baseline_and_fluctuation",
        "urinary.episode_frequency_duration_triggers_recovery_and_between_state",
        "urinary.symptom_burden_sleep_work_travel_selfcare_and_distress",
        "urinary.information_source_proxy_record_reliability_conflict_and_consent",
        "urinary.patient_goal_preference_expected_help_additional_comment_and_other_rfe",
        "history.recurrent_uti",
        "device.urinary_catheter_present",
        "pregnancy.possible",
        "history.diabetes",
        "patient.immunocompromised",
        "patient.male_urinary_anatomy",
        "patient.age_65_or_older",
    ]
    policy["conditional_required_facts"] = [{
        "selector_fact": "symptom.urinary.presentation",
        "cases": {
            "pain_burning": [
                "symptom.dysuria", "symptom.dysuria.severity",
                "urinary.dysuria_site_before_during_after_void_and_pain_radiation",
                "symptom.urinary_frequency", "symptom.urinary_urgency",
                "urinary.urine_colour_clarity_odour_blood_clots_timing_and_source",
                "urinary.fever_measured_temperature_chills_vomiting_and_systemic_timeline",
                "urinary.intake_hydration_urine_output_dehydration_and_last_void",
                "urinary.current_recent_antibiotic_product_dose_schedule_start_adherence_and_response",
                "urinary.prior_urinalysis_dipstick_microscopy_culture_result_date_and_source",
                "symptom.urethral_discharge", "symptom.genital_or_vaginal_irritation",
                "exposure.new_or_unprotected_sexual_contact",
            ],
            "frequency_urgency": [
                "symptom.urinary_frequency", "symptom.urinary_urgency", "symptom.nocturia_count",
                "urinary.daytime_frequency_nocturia_actual_counts_baseline_and_change",
                "urinary.urgency_warning_time_triggers_toilet_access_and_leak_relation",
                "urinary.voided_volume_fluid_intake_timing_and_frequency_volume_diary",
                "symptom.urinary_incontinence", "history.diabetes",
                "urinary.current_medicines_diuretic_anticholinergic_decongestant_sglt2_and_change",
                "urinary.prior_ipss_or_validated_measure_name_raw_score_date_context_and_source",
                "exposure.new_or_unprotected_sexual_contact",
            ],
            "flow_emptying": [
                "symptom.urinary_hesitancy", "symptom.weak_urine_stream",
                "symptom.incomplete_bladder_emptying",
                "urinary.hesitancy_straining_intermittency_spray_stream_and_postvoid_dribble",
                "urinary.fullness_distension_residual_sensation_retention_episode_and_relief",
                "urinary.current_medicines_diuretic_anticholinergic_decongestant_sglt2_and_change",
                "urinary.stone_surgery_procedure_device_structural_neurologic_and_pelvic_history",
                "urinary.prior_renal_function_imaging_residual_flow_cystoscopy_prostate_and_pending",
                "patient.male_urinary_anatomy", "history.urinary_stones",
            ],
            "leakage": [
                "symptom.urinary_incontinence",
                "urinary.incontinence_type_amount_frequency_pad_skin_and_baseline",
                "urinary.urgency_warning_time_triggers_toilet_access_and_leak_relation",
                "urinary.daytime_frequency_nocturia_actual_counts_baseline_and_change",
                "urinary.voided_volume_fluid_intake_timing_and_frequency_volume_diary",
                "urinary.stone_surgery_procedure_device_structural_neurologic_and_pelvic_history",
                "urinary.menstrual_menopause_vaginal_dryness_bleeding_discharge_and_prolapse",
                "urinary.older_frailty_cognition_delirium_continence_falls_and_baseline",
            ],
            "blood_or_urine_change": [
                "symptom.visible_hematuria", "symptom.cloudy_urine",
                "urinary.urine_colour_clarity_odour_blood_clots_timing_and_source",
                "symptom.hematuria_persists_after_uti_treatment",
                "patient.age_45_or_older", "patient.age_65_or_older",
                "urinary.smoking_vaping_chemical_exposure_and_hematuria_risk_context",
                "urinary.prior_urinalysis_dipstick_microscopy_culture_result_date_and_source",
                "urinary.prior_renal_function_imaging_residual_flow_cystoscopy_prostate_and_pending",
                "history.urinary_stones",
            ],
            "other": [
                "symptom.dysuria", "symptom.urinary_frequency", "symptom.urinary_urgency",
                "symptom.urinary_hesitancy", "symptom.weak_urine_stream",
                "symptom.incomplete_bladder_emptying", "symptom.urinary_incontinence",
                "symptom.cloudy_urine", "symptom.lower_abdominal_pain",
                "urinary.renal_diabetes_neurologic_constipation_prostate_pelvicfloor_and_gynaecologic_context",
                "urinary.prior_urinalysis_dipstick_microscopy_culture_result_date_and_source",
            ],
        },
    }]
    policy["question_budget"] = {"routine": 68, "clarify": 18}
    policy["provenance"] = provenance(SOURCES)
    return policy


def update_sources() -> dict:
    doc = load(RESEARCH)
    updates = {
        "source.nhs.uti.2025": (
            "reviewed-2025-07-11-accessed-2026-07-21",
            "current_official_page_confirmed_no_change",
        ),
        "source.nice.qs90.uti-adults.2023": (
            "QS90-updated-2023-accessed-2026-07-21",
            "current_quality_statements_confirmed_no_change",
        ),
        "source.nice.ng111.pyelonephritis.2018": (
            "NG111-accessed-2026-07-21",
            "current_recommendations_confirmed_no_replacement_identified",
        ),
        "source.nice.cg97.luts.2024": (
            "CG97-reviewed-2024-accessed-2026-07-21",
            "current_recommendations_confirmed_no_replacement_identified",
        ),
        "source.nice.ng12.urinary.2026": (
            "NG12-updated-2026-accessed-2026-07-21",
            "current_urological_cancer_recommendations_confirmed",
        ),
    }
    for artifact in doc["artifacts"]:
        if artifact["id"] not in updates:
            continue
        version, result = updates[artifact["id"]]
        artifact.update({
            "version": version,
            "last_monitored_at": "2026-07-21",
            "next_monitor_at": "2026-07-28",
            "monitor_result": result,
            "recommendation_change_detected": False,
        })
    doc["version"] = "0.2.0"
    doc["updated_at"] = CREATED
    doc["provenance"] = provenance([item["id"] for item in doc["artifacts"]])
    doc["provenance"]["version"] = "0.2.0"
    return doc


def update_clinician(doc: dict) -> dict:
    result = load(CLINICIAN)
    ids = sorted({item["fact"]["id"] for item in doc["entries"]})
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.urinary_symptoms"] = ids
    return result


def simulation_cases(doc: dict, policy: dict) -> dict[str, dict]:
    by_id = {item["fact"]["id"]: item["fact"] for item in doc["entries"]}
    always = policy["required_facts"]["always"]
    routine = policy["required_facts"]["routine"]
    branches = policy["conditional_required_facts"][0]["cases"]
    forbidden = [
        "diagnosis.urinary_tract_infection", "diagnosis.pyelonephritis",
        "diagnosis.urological_cancer", "recommendation.start_antibiotic",
    ]

    def value(fact_id: str):
        fact = by_id[fact_id]
        if fact["value_type"] == "boolean":
            return False
        if fact["value_type"] == "quantity":
            return {"amount": 3, "unit": "day"}
        if fact["value_type"] == "integer":
            return 1
        if fact["value_type"] == "coded":
            values = fact.get("allowed_values", ["other"])
            for candidate in ("not_possible", "none", "mild", "other"):
                if candidate in values:
                    return candidate
            return values[-1]
        return "합성 문진 응답"

    def state(branch: str, clinician: bool = False) -> dict[str, dict]:
        ids = list(by_id) if clinician else list(dict.fromkeys([*always, *routine, *branches[branch]]))
        result = {fact_id: {"value": value(fact_id)} for fact_id in ids}
        result["symptom.urinary.presentation"] = {"value": branch}
        return result

    specs = [
        ("DYSURIA-HANDOFF", "pain_burning", 33, "배뇨통의 시작·통증 시점과 검사·치료 반응을 진료 전에 정리합니다."),
        ("FREQUENCY-DIARY", "frequency_urgency", 52, "빈뇨·절박뇨와 실제 배뇨 횟수·수분 섭취·방광일지를 정리합니다."),
        ("VOIDING-EMPTYING", "flow_emptying", 68, "약한 줄기와 잔뇨감의 경과, 약물·검사·요폐 이력을 정리합니다."),
        ("LEAKAGE-OLDER-PROXY", "leakage", 79, "보호자가 평소 인지·이동·실금 상태와 최근 변화를 구분해 전달합니다."),
        ("HEMATURIA-RISK", "blood_or_urine_change", 61, "소변 색 변화의 시점과 치료 후 경과, 흡연·검사 이력을 정리합니다."),
        ("MIXED-UNCLEAR", "other", 44, "여러 배뇨 증상이 섞여 있어 기본 양상과 미확인 항목을 정리합니다."),
    ]
    result: dict[str, dict] = {}
    for key, branch, age, statement in specs:
        result[f"URINARY-{key}.json"] = {
            "id": f"URINARY-{key}",
            "simulation_language": "ko",
            "persona": {"age": age},
            "initial_statement": {"ko": statement},
            "hidden_state": state(branch),
            "expected": {
                "expected_safety_level": "routine",
                "expected_stop_reason": "all_required_targets_resolved",
                "expected_max_turns": 68,
                "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }

    proxy = state("leakage", clinician=True)
    result["URINARY-CLINICIAN-PROXY-ACCESSIBILITY.json"] = {
        "id": "URINARY-CLINICIAN-PROXY-ACCESSIBILITY",
        "simulation_language": "ko",
        "persona": {"age": 82},
        "initial_statement": {"ko": "고령 환자의 보호자가 실금·혼돈 변화와 자료 출처를 의료인에게 제출합니다."},
        "hidden_state": proxy,
        "clinician_submission": True,
        "encounter_context": {
            "care_setting": "home_visit", "encounter_type": "follow_up",
            "interview_initiator": "caregiver", "interview_mode": "face_to_face",
            "available_information": ["previous_clinical_memory", "caregiver_report"],
            "time_constraint": "scheduled", "clinical_responsibility": "shared_care",
        },
        "expected": {"expected_safety_level": "routine", "expected_max_turns": 130, "forbidden_assertions": forbidden},
        "provenance": provenance(SOURCES),
    }

    missing = "urinary.prior_urinalysis_dipstick_microscopy_culture_result_date_and_source"
    absent = state("pain_burning")
    absent.pop(missing)
    result["URINARY-PRIOR-RESULT-DATA-ABSENT.json"] = {
        "id": "URINARY-PRIOR-RESULT-DATA-ABSENT",
        "simulation_language": "ko",
        "persona": {"age": 47},
        "initial_statement": {"ko": "소변검사를 받았지만 결과 자료와 균명은 기억나지 않습니다."},
        "hidden_state": absent,
        "response_behavior": {missing: {"dataAbsentReason": "asked-unknown"}},
        "expected": {
            "expected_data_absent_reasons": {missing: "asked-unknown"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 68,
            "forbidden_assertions": forbidden,
        },
        "provenance": provenance(SOURCES),
    }
    opening_specs = [
        (
            "URINARY-OPENING-RETENTION.json", "URINARY-OPENING-RETENTION",
            "소변이 전혀 안 나오고 아랫배가 팽팽합니다.", "emergency",
            "emergency_escalation", "rule.urinary.safety.acute-retention",
        ),
        (
            "URINARY-OPENING-HEMATURIA.json", "URINARY-OPENING-HEMATURIA",
            "오늘 소변에 피가 보입니다.", "urgent", "urgent_escalation",
            "rule.urinary.safety.visible-haematuria",
        ),
        (
            "URINARY-OPENING-FEVER-FLANK.json", "URINARY-OPENING-FEVER-FLANK",
            "옆구리가 아프고 열과 오한이 있습니다.", "urgent", "urgent_escalation",
            "rule.urinary.safety.fever-flank-pain",
        ),
    ]
    for filename, identifier, statement, level, stop, rule in opening_specs:
        result[filename] = {
            "id": identifier,
            "simulation_language": "ko",
            "persona": {"age": 45},
            "initial_statement": {"ko": statement},
            "hidden_state": {},
            "expected": {
                "expected_safety_level": level,
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": stop,
                "expected_triggered_rules_contains": [rule],
                "expected_max_turns": 1,
                "forbidden_assertions": forbidden,
            },
            "provenance": provenance(SOURCES),
        }
    return result


def main() -> None:
    doc = build_fragment()
    policy = build_policy(doc)
    write_json(FRAGMENT, doc)
    write_json(POLICY, policy)
    write_json(RESEARCH, update_sources())
    write_json(CLINICIAN, update_clinician(doc))
    for name, case in simulation_cases(doc, policy).items():
        write_json(f"simulation/patients/genitourinary/urinary-symptoms/{name}", case)


if __name__ == "__main__":
    main()
