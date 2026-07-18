#!/usr/bin/env python3
"""Strengthen research-only bowel-symptom knowledge for clinician handoff."""
from __future__ import annotations

from profile_support import *


P = "bowel-symptoms"
FRAGMENT = "knowledge/generated/gastrointestinal/bowel-symptoms/bowel-symptoms.json"
POLICY = "policies/primary-care-bowel-symptoms-completion.json"
RESEARCH = "sources/manifests/primary-care-bowel-symptoms-research.json"
CLINICIAN = "knowledge/shared/clinician-submission-context.json"
SIM_ROOT = ROOT / "simulation/patients/gastrointestinal/bowel-symptoms"
SOURCES = [
    "source.nhs.rectal-bleeding.2023", "source.nhs.constipation.2026",
    "source.nhs.stomach-ache.2023", "source.nice.ng12.colorectal.2026",
    "source.nice.cg99.child-constipation.2017",
    "source.stom.mrcm.bowel.20260714",
]
G = {key: f"group.bowel.{key}" for key in (
    "routing", "course", "stool-detail", "constipation-detail",
    "diarrhea-detail", "pain", "bleeding-detail", "systemic",
    "medicine", "child", "previous-care", "handoff",
)}
C, S = ["intent.characterize_symptom"], ["intent.screen_red_flags"]
D, R = ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def q(fid, display, vt, key, wording, score, group, intents, **kwargs):
    return entry(P, fid, display, vt, key, wording, score, key, [G[group]], intents=intents, **kwargs)


def fragment():
    doc = load(FRAGMENT)
    branches = [
        "constipation_or_difficult_passage", "loose_frequent_or_urgent",
        "rectal_bleeding_or_blood", "pain_bloating_or_obstruction",
        "persistent_change_or_systemic", "child_or_proxy",
        "medicine_or_postprocedure", "other_unclear",
    ]
    additions = [
        q("bowel.primary_group", "Primary Bowel Symptom Context", "coded", "primary-group", "가장 가까운 상황은 변비·배변곤란, 묽거나 잦고 급한 변, 항문출혈·혈변, 복통·팽만·막힘 느낌, 지속 변화·전신 증상, 소아·보호자 관찰, 약물·시술 후 변화, 또는 불분명 중 무엇인가요?", 118, "routing", C + D, allowed_values=branches),
        q("bowel.patient_words_and_change_from_baseline", "Patient Description and Baseline Change", "string", "patient-words", "본인의 표현으로 가장 불편한 점과 평소 배변 습관에서 무엇이 달라졌는지 알려주세요.", 108, "handoff", C),
        q("bowel.exact_onset_date_context_sequence_and_trend", "Exact Onset Sequence and Trend", "string", "onset-detail", "처음 달라진 날짜, 당시 감염·식사·여행·입원·약 변경과 증상이 생긴 순서, 최근 호전/악화 추세를 알려주세요.", 107, "course", C + R),
        q("bowel.episode_days_frequency_baseline_and_current", "Baseline and Current Frequency", "string", "frequency-detail", "평소와 현재 각각 하루·주당 배변 횟수, 며칠씩 못 보는지와 증상이 있는 날 수를 알려주세요.", 106, "course", C),
        q("bowel.stool_bristol_size_colour_odour_float_and_variability", "Detailed Stool Description", "string", "stool-detail", "가능하면 Bristol 1~7형, 변의 크기·색·냄새·기름지거나 뜨는지와 매번 같은지 알려주세요.", 105, "stool-detail", C),
        q("bowel.urgency_nocturnal_stool_incontinence_and_toilet_access", "Urgency Nocturnal Symptoms and Incontinence", "string", "urgency", "갑작스러운 변의, 밤에 깨서 배변, 변을 참지 못함·속옷에 묻음과 화장실 접근 어려움이 있나요?", 104, "diarrhea-detail", C + R),
        q("bowel.pain_relation_to_meals_defecation_gas_and_site", "Abdominal Pain Pattern", "string", "pain-detail", "복통이 있다면 정확한 부위, 식사·배변·가스 전후 변화, 지속시간과 퍼지는 곳을 알려주세요.", 103, "pain", C),
        q("bowel.abdominal_pain_present", "Abdominal Pain Present", "boolean", "pain-present", "현재 또는 이번 배변 변화와 함께 복통이 있나요?", 102, "pain", C),
        q("bowel.blood_amount_frequency_duration_mixed_surface_or_separate", "Bleeding Amount and Pattern", "string", "bleeding-detail", "피의 양·색·피떡, 휴지/변 표면/변 속/변기 중 어디에 보였는지와 횟수·지속기간을 알려주세요.", 101, "bleeding-detail", C + R),
        q("bowel.anal_lump_fissure_prolapse_discharge_and_defecation_pain", "Anal and Rectal Local Symptoms", "string", "anal-detail", "항문 통증·가려움·찢어짐, 돌출되는 덩이·탈출, 고름/분비물과 배변 시 악화 여부를 알려주세요.", 93, "bleeding-detail", D),
        q("bowel.appetite_early_satiety_nausea_vomiting_and_intake", "Appetite and Intake", "string", "intake", "식욕·조기 포만감·메스꺼움·구토와 먹고 마실 수 있는 양의 변화를 알려주세요.", 92, "systemic", C + R),
        q("bowel.weight_change_amount_timeframe_and_intent", "Weight Change Detail", "string", "weight-detail", "체중이 변했다면 얼마가 얼마나 오랫동안 변했고 의도적으로 감량한 것인지 알려주세요.", 91, "systemic", R),
        q("bowel.hydration_urine_dizziness_dry_mouth_and_intake_warning", "Dehydration Warning", "boolean", "dehydration-warning", "물을 거의 못 마시거나 소변이 현저히 줄고, 심한 어지럼·입마름·축 처짐이 있나요?", 118, "systemic", S, safety_relevant=True),
        q("bowel.infection_travel_food_water_contact_and_antibiotic_timing", "Infectious and Antibiotic Context", "string", "infection-context", "최근 여행·의심 음식/물·같이 아픈 사람·동물 접촉, 발열과 최근 항생제/입원 시점을 알려주세요.", 90, "diarrhea-detail", R),
        q("bowel.current_medicines_dose_schedule_change_and_bowel_effect", "Current Medicines and Changes", "string", "medicine-detail", "처방약·일반약·한약·영양제의 이름·용량·횟수, 최근 시작/중단/변경과 배변 변화 시점을 알려주세요.", 89, "medicine", R),
        q("bowel.laxative_antidiarrheal_enema_suppository_and_response", "Bowel Treatment Exposure and Response", "string", "bowel-treatment", "완하제·지사제·관장·좌약·식이 조절을 언제 얼마나 사용했고 효과·재발·부작용이 어땠는지 알려주세요.", 88, "medicine", R),
        q("bowel.anticoagulant_antiplatelet_nsaid_opioid_iron_and_allergy", "High-risk Medicines and Allergies", "string", "medicine-risk", "항응고제·아스피린/항혈소판제·소염진통제·마약성 진통제·철분제와 약물 알레르기를 알려주세요.", 87, "medicine", R),
        q("bowel.metabolic_neurologic_pelvic_floor_and_mobility_context", "Relevant Medical and Functional Context", "string", "medical-context", "갑상선·당뇨·신경질환·골반저 문제·거동 제한·인지 변화 등 배변에 영향을 줄 수 있는 병력을 알려주세요.", 78, "previous-care", R),
        q("bowel.pregnancy_lmp_postpartum_and_pelvic_history", "Pregnancy and Pelvic Context", "string", "pregnancy", "해당되는 경우 임신 가능성·마지막 월경일·임신 주수·산후 기간과 골반 수술/출산 손상 병력을 알려주세요.", 77, "previous-care", R),
        q("bowel.child_meconium_onset_growth_feeding_withholding_soiling_and_proxy", "Child Constipation and Proxy Detail", "string", "child-detail", "소아라면 출생 후 첫 태변 시점, 생후 언제부터 시작했는지, 성장·수유/식사, 변 참는 자세·통증·속옷에 묻음과 답변자를 알려주세요.", 116, "child", R),
        q("bowel.child_early_onset_growth_neurologic_or_gross_distension_warning", "Child Constipation Red Flag", "boolean", "child-warning", "소아라면 생후 첫 주부터 변비, 48시간 이후 태변, 성장부진, 다리 힘/보행·허리/천골 이상, 심한 복부팽만과 구토 중 하나가 있나요?", 117, "child", S, safety_relevant=True),
        q("bowel.prior_episode_diagnosis_ed_admission_and_baseline_recovery", "Prior Episode and Care", "string", "prior-care", "비슷한 증상의 시기·설명받은 진단·응급실/입원 여부와 평소 배변으로 얼마나 회복했는지 알려주세요.", 76, "previous-care", R),
        q("bowel.prior_fit_blood_stool_colonoscopy_imaging_and_source", "Prior Tests and Results", "string", "prior-tests", "이전 FIT/대변검사·혈액검사(빈혈 포함)·대장내시경·CT/초음파의 날짜·결과와 자료 출처를 알려주세요.", 75, "previous-care", R),
        q("bowel.prior_examination_mass_rectal_findings_and_source", "Prior Examination Findings", "string", "prior-exam", "의료진이 배·항문·직장을 진찰했다면 덩이·압통·치핵/열상 등 설명받은 결과와 시점을 알려주세요.", 74, "previous-care", R),
        q("bowel.function_sleep_school_work_selfcare_and_social_impact", "Functional and Social Impact", "string", "function", "수면·식사·등교/출근·외출·운동·자가관리와 대인관계에서 어려워진 점을 알려주세요.", 73, "handoff", C + R),
        q("bowel.diet_fibre_fluid_dairy_caffeine_alcohol_and_recent_change", "Detailed Diet and Fluid Context", "string", "diet-detail", "식이섬유·수분·유제품·카페인·술 섭취와 최근 식단 변화, 증상과 관련된 음식을 알려주세요.", 72, "handoff", D + R),
        q("bowel.occupation_shift_toilet_access_activity_and_stress_context", "Occupation and Toilet Access", "string", "occupation", "직업·교대근무·장시간 앉음·활동량·화장실 접근 제한과 스트레스가 증상에 미친 영향을 알려주세요.", 71, "handoff", R),
        q("bowel.family_colorectal_polyps_ibd_celiac_hirschsprung_age", "Detailed Family History", "string", "family-detail", "가족의 대장암·용종·염증성 장질환·셀리악병·히르슈스프룽병과 진단 나이를 알려주세요.", 70, "handoff", R),
        q("bowel.information_source_record_reliability_and_conflict", "Information Source Reliability and Conflict", "string", "information-source", "본인·보호자 중 누가 답하는지, 배변일지·사진·검사자료가 있는지, 기억이 불확실하거나 설명이 다른 부분을 알려주세요.", 69, "handoff", R),
        q("bowel.patient_concern_goal_expectation_and_additional_comment", "Patient Concern Goal and Additional Comment", "string", "goal", "가장 걱정되는 점, 진료에서 확인하고 싶은 점과 질문에 없던 의견을 알려주세요.", 68, "handoff", R),
    ]
    entries = {x["fact"]["id"]: x for x in doc["entries"]}
    entries.update({x["fact"]["id"]: x for x in additions})
    doc["entries"] = list(entries.values())
    new_rules = [
        safety_rule(P, "dehydration", {"fact": "bowel.hydration_urine_dizziness_dry_mouth_and_intake_warning", "equals": True}, "urgent", 920),
        safety_rule(P, "child-red-flag", {"fact": "bowel.child_early_onset_growth_neurologic_or_gross_distension_warning", "equals": True}, "urgent", 910),
    ]
    rules = {x["id"]: x for x in doc["safety_rules"]}
    rules.update({x["id"]: x for x in new_rules})
    doc["safety_rules"] = sorted(rules.values(), key=lambda x: (-x["priority"], x["id"]))
    nodes = {x["id"]: x for x in doc["extra_nodes"]}
    for key, identifier in G.items():
        nodes[identifier] = {"id": identifier, "type": "ClinicalGroup", "display": key.replace("-", " ").title()}
    doc["extra_nodes"] = list(nodes.values())
    doc["default_refresh"].update({"last_assessed_at": "2026-07-19", "next_monitor_at": "2026-07-20", "next_full_review_at": "2027-01-15"})
    doc["provenance"] = provenance(SOURCES)
    return doc


def policy(doc):
    result = completion_policy(prefix=P, fragment=doc, presentation_fact="symptom.bowel.current", question_budget=70, source_refs=SOURCES)
    result["required_facts"]["routine"] = [
        "bowel.primary_group", "symptom.bowel.main_type", "symptom.duration",
        "symptom.bowel.sudden_or_gradual", "bowel.patient_words_and_change_from_baseline",
        "bowel.exact_onset_date_context_sequence_and_trend",
        "bowel.episode_days_frequency_baseline_and_current", "symptom.bowel.frequency",
        "symptom.stool_form", "bowel.stool_bristol_size_colour_odour_float_and_variability",
        "bowel.function_sleep_school_work_selfcare_and_social_impact",
        "bowel.current_medicines_dose_schedule_change_and_bowel_effect",
        "bowel.prior_episode_diagnosis_ed_admission_and_baseline_recovery",
        "bowel.prior_fit_blood_stool_colonoscopy_imaging_and_source",
        "bowel.information_source_record_reliability_and_conflict",
        "bowel.patient_concern_goal_expectation_and_additional_comment",
    ]
    result["conditional_required_facts"] = [{"selector_fact": "bowel.primary_group", "cases": {
        "constipation_or_difficult_passage": ["symptom.straining", "symptom.incomplete_evacuations", "symptom.manual_maneuver_for_defecation", "bowel.laxative_antidiarrheal_enema_suppository_and_response", "bowel.diet_fibre_fluid_dairy_caffeine_alcohol_and_recent_change", "bowel.metabolic_neurologic_pelvic_floor_and_mobility_context"],
        "loose_frequent_or_urgent": ["bowel.urgency_nocturnal_stool_incontinence_and_toilet_access", "symptom.mucus_in_stool", "bowel.infection_travel_food_water_contact_and_antibiotic_timing", "bowel.hydration_urine_dizziness_dry_mouth_and_intake_warning", "bowel.diet_fibre_fluid_dairy_caffeine_alcohol_and_recent_change"],
        "rectal_bleeding_or_blood": ["symptom.blood_appearance", "bowel.blood_amount_frequency_duration_mixed_surface_or_separate", "symptom.rectal_pain_or_itch", "bowel.anal_lump_fissure_prolapse_discharge_and_defecation_pain", "bowel.anticoagulant_antiplatelet_nsaid_opioid_iron_and_allergy", "bowel.prior_examination_mass_rectal_findings_and_source"],
        "pain_bloating_or_obstruction": ["bowel.abdominal_pain_present", "symptom.abdominal_pain", "bowel.pain_relation_to_meals_defecation_gas_and_site", "symptom.bloating", "bowel.appetite_early_satiety_nausea_vomiting_and_intake", "history.abdominal_or_bowel_surgery"],
        "persistent_change_or_systemic": ["symptom.narrow_stool", "symptom.unintentional_weight_loss", "bowel.weight_change_amount_timeframe_and_intent", "symptom.anemia_or_fatigue_features", "observation.abdominal_or_rectal_mass_known", "bowel.family_colorectal_polyps_ibd_celiac_hirschsprung_age"],
        "child_or_proxy": ["bowel.child_meconium_onset_growth_feeding_withholding_soiling_and_proxy", "bowel.child_early_onset_growth_neurologic_or_gross_distension_warning", "bowel.family_colorectal_polyps_ibd_celiac_hirschsprung_age", "bowel.information_source_record_reliability_and_conflict"],
        "medicine_or_postprocedure": ["bowel.current_medicines_dose_schedule_change_and_bowel_effect", "bowel.laxative_antidiarrheal_enema_suppository_and_response", "bowel.anticoagulant_antiplatelet_nsaid_opioid_iron_and_allergy", "history.abdominal_or_bowel_surgery", "bowel.pregnancy_lmp_postpartum_and_pelvic_history"],
        "other_unclear": ["bowel.urgency_nocturnal_stool_incontinence_and_toilet_access", "bowel.abdominal_pain_present", "bowel.infection_travel_food_water_contact_and_antibiotic_timing", "bowel.metabolic_neurologic_pelvic_floor_and_mobility_context", "bowel.pregnancy_lmp_postpartum_and_pelvic_history", "bowel.diet_fibre_fluid_dairy_caffeine_alcohol_and_recent_change", "bowel.occupation_shift_toilet_access_activity_and_stress_context"],
    }}]
    return result


def sources():
    doc = load(RESEARCH)
    artifacts = {x["id"]: x for x in doc["artifacts"]}
    artifacts["source.nhs.constipation.2026"] = {
        "id": "source.nhs.constipation.2026", "kind": "public_health_guidance_metadata",
        "publisher": "NHS", "title": "Constipation", "version": "current-accessed-2026-07-19",
        "url": "https://www.nhs.uk/conditions/constipation/", "language": "en",
        "digest": "metadata_only_not_cached", "license_status": "unknown", "complete": False,
        "monitor_profile": "public_health_guidance", "last_monitored_at": "2026-07-19",
        "monitor_result": "current_official_source_confirmed",
        "assertions": ["History includes stool frequency and difficulty, abdominal symptoms, blood, weight change, medicines, fluid, fibre, activity and prior treatment response without assuming a cause."],
    }
    artifacts["source.nice.cg99.child-constipation.2017"] = {
        "id": "source.nice.cg99.child-constipation.2017", "kind": "clinical_guidance_metadata",
        "publisher": "NICE", "title": "Constipation in children and young people: diagnosis and management",
        "version": "CG99-updated-2017-07-13", "url": "https://www.nice.org.uk/guidance/cg99/chapter/Recommendations",
        "language": "en", "digest": "metadata_only_not_cached", "license_status": "restricted", "complete": False,
        "monitor_profile": "nice_guidance", "last_monitored_at": "2026-07-19",
        "monitor_result": "current_official_source_confirmed",
        "assertions": ["Child history includes stool frequency and form, painful defecation, withholding, overflow soiling, appetite and abdominal symptoms, onset in infancy, meconium timing, growth and neurologic or anatomic warning features.", "Child and proxy data remain age-specific and do not trigger diagnosis or treatment selection."],
    }
    for sid in ("source.nhs.rectal-bleeding.2023", "source.nhs.stomach-ache.2023", "source.nice.ng12.colorectal.2026"):
        artifacts[sid]["last_monitored_at"] = "2026-07-19"
        artifacts[sid]["monitor_result"] = "current_official_source_confirmed"
    artifacts["source.nhs.rectal-bleeding.2023"]["assertions"] = ["Continuous or large-volume rectal bleeding, red toilet water or large clots require emergency assessment; blood colour and relationship to stool are recorded without assigning a source."]
    artifacts["source.nice.ng12.colorectal.2026"]["assertions"] = ["Change in bowel habit, iron-deficiency anaemia, rectal bleeding with abdominal pain or weight loss and other age-context combinations are clinician assessment inputs; Runtime does not calculate referral eligibility or diagnose cancer."]
    artifacts["source.stom.mrcm.bowel.20260714"]["monitor_result"] = "not_due_existing_metadata_preserved"
    doc["artifacts"] = list(artifacts.values())
    doc["provenance"] = provenance(SOURCES)
    return doc


def clinician(doc):
    result = load(CLINICIAN)
    result["completion"]["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]["rfe.bowel_symptoms"] = sorted({*(x["fact"]["id"] for x in doc["entries"]), "pain.frequency", "pain.nrs_score"})
    return result


def condition_state(condition):
    out = {}
    for child in condition.get("all", [condition]):
        if "fact" in child:
            out[child["fact"]] = {"value": child.get("equals", child.get("in", [True])[0])}
    return out


def cases(doc, completion):
    by_id = {x["fact"]["id"]: x["fact"] for x in doc["entries"]}
    forbidden = ["diagnosis.colorectal_cancer", "diagnosis.bowel_obstruction", "diagnosis.inflammatory_bowel_disease", "recommendation.laxative", "recommendation.colonoscopy"]
    out = {}
    for index, rule in enumerate(doc["safety_rules"]):
        key = rule["id"].split("safety.", 1)[1]; level = rule["then"]["safety_level"]
        out[f"BOWEL-{key.upper()}.json"] = {"id": f"BOWEL-{key.upper()}", "simulation_language": "ko", "persona": {"age": 7 if "child" in key else 35 + index * 3}, "initial_statement": {"ko": "배변 증상으로 진료 전 문진을 시작합니다."}, "hidden_state": condition_state(rule["when"]), "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 35, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    always, base, branches = completion["required_facts"]["always"], completion["required_facts"]["routine"], completion["conditional_required_facts"][0]["cases"]
    def value(fid):
        f = by_id[fid]
        if f["value_type"] == "boolean": return False
        if f["value_type"] == "coded": return f.get("allowed_values", ["other"])[-1]
        if f["value_type"] == "quantity": return "2 weeks"
        return "특이사항 없음"
    def routine(branch):
        state = {fid: {"value": value(fid)} for fid in dict.fromkeys([*always, *base, *branches[branch]])}
        state["symptom.bowel.current"] = {"value": True}; state["bowel.primary_group"] = {"value": branch}
        return state
    specs = [
        ("CONSTIPATION-ADULT", "constipation_or_difficult_passage", 54, "최근 배변이 어렵고 변이 단단합니다.", {}),
        ("LOOSE-REMOTE", "loose_frequent_or_urgent", 43, "원격으로 잦고 묽은 변을 정리합니다.", {}),
        ("BLEEDING-STABLE", "rectal_bleeding_or_blood", 61, "소량의 항문 출혈이 반복되어 기록을 정리합니다.", {}),
        ("PAIN-NRS", "pain_bloating_or_obstruction", 48, "복통과 배변 변화가 함께 있습니다.", {"bowel.abdominal_pain_present": {"value": True}, "symptom.abdominal_pain": {"value": True}, "pain.frequency": {"value": "daily"}, "pain.nrs_score": {"value": 5}}),
        ("PERSISTENT-HANDOFF", "persistent_change_or_systemic", 72, "오래된 배변 변화와 이전 검사 내용을 의료진에게 전달하려 합니다.", {}),
        ("CHILD-PROXY", "child_or_proxy", 8, "보호자가 아이의 변비와 속옷에 묻는 증상을 설명합니다.", {"bowel.child_meconium_onset_growth_feeding_withholding_soiling_and_proxy": {"value": "8세, 보호자 답변, 배변 회피와 속옷 묻음"}}),
        ("MEDICINE-POLYPHARMACY", "medicine_or_postprocedure", 79, "여러 약을 복용한 뒤 생긴 배변 변화를 정리합니다.", {}),
        ("UNCLEAR-MULTI-RFE", "other_unclear", 34, "배변 변화 외에 소변 증상도 별도 문진하고 싶습니다.", {"bowel.patient_concern_goal_expectation_and_additional_comment": {"value": "소변 증상을 별도 RFE로 전달 요청"}}),
    ]
    for key, branch, age, statement, overrides in specs:
        state = routine(branch); state.update(overrides)
        expected = {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 95, "forbidden_assertions": forbidden}
        if key == "PAIN-NRS": expected["expected_known_facts"] = {"pain.nrs_score": 5}
        out[f"BOWEL-{key}.json"] = {"id": f"BOWEL-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": state, "expected": expected, "provenance": provenance(SOURCES)}
    absent = routine("other_unclear"); missing = "bowel.prior_fit_blood_stool_colonoscopy_imaging_and_source"; absent.pop(missing)
    out["BOWEL-DATA-ABSENT-REMOTE.json"] = {"id": "BOWEL-DATA-ABSENT-REMOTE", "simulation_language": "ko", "persona": {"age": 83}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "보호자가 설명하지만 이전 검사자료는 없습니다."}, "hidden_state": absent, "response_behavior": {missing: {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {missing: "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 95, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    return out


def main():
    doc = fragment(); completion = policy(doc)
    write_json(FRAGMENT, doc); write_json(POLICY, completion); write_json(RESEARCH, sources()); write_json(CLINICIAN, clinician(doc))
    pain = load("knowledge/shared/hira-pain-assessment.json")
    pain["profile_bindings"]["bowel_symptoms"] = {"activation": "when", "when": {"fact": "bowel.abdominal_pain_present", "equals": True}}
    write_json("knowledge/shared/hira-pain-assessment.json", pain)
    for old in SIM_ROOT.glob("*.json"): old.unlink()
    for name, case in cases(doc, completion).items(): write_json(f"simulation/patients/gastrointestinal/bowel-symptoms/{name}", case)


if __name__ == "__main__": main()
