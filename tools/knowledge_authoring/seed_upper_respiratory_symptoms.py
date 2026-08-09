#!/usr/bin/env python3
"""Materialize the unreviewed upper-respiratory-symptom research profile."""
from __future__ import annotations

from profile_support import (
    CREATED_AT, VERSION, base_graph_and_rules, completion_policy,
    default_refresh, entry, provenance, safety_rule, write_json,
)


PREFIX = "upper-respiratory"
RFE = "rfe.upper_respiratory_symptoms"
MRCM_REF = "mapping.snomed-mrcm.upper-respiratory-symptoms"
SNOMED = "http://snomed.info/sct"
SOURCES = [
    "source.nhs.sore-throat.2024",
    "source.nice.ng84.sore-throat.2025",
    "source.nice.ng79.sinusitis.2026",
    "source.nhs.allergic-rhinitis.2026",
    "source.aao-hns.hoarseness-dysphonia.2018",
    "source.pubmed.hoarseness-dysphonia.29494321",
    "source.nice.ng12.laryngeal-cancer.2026",
    "source.stom.snomed-hoarse.20260801",
]

G = {
    "safety": "group.upper-respiratory.immediate-safety",
    "throat": "group.upper-respiratory.throat",
    "nasal": "group.upper-respiratory.nasal-sinus",
    "allergy": "group.upper-respiratory.allergic",
    "voice": "group.upper-respiratory.voice-persistence",
    "context": "group.upper-respiratory.context",
    "handoff": "group.upper-respiratory.clinician-handoff",
}

CHARACTERIZE = ["intent.characterize_symptom"]
SAFETY = ["intent.screen_red_flags"]
RISK = ["intent.risk_assessment"]
DIFFERENTIATE = ["intent.differentiate_common_causes"]


def q(fid, display, vt, key, wording, score, reason, groups, intents, **kwargs):
    return entry(
        PREFIX, fid, display, vt, key, wording, score, reason, groups,
        intents=intents, **kwargs,
    )


def build_fragment():
    entries = [
        q("symptom.upper_respiratory.current", "Current Upper Respiratory Symptom", "boolean", "current", "지금도 목 통증, 코막힘·콧물, 재채기 또는 목소리 변화가 있나요?", 130, "confirm_presentation", [G["throat"], G["nasal"]], CHARACTERIZE),
        q("symptom.upper_respiratory.main_type", "Main Upper Respiratory Symptom", "coded", "main-type", "가장 불편한 것은 목 통증, 코막힘, 콧물, 재채기·가려움, 얼굴 통증, 쉰목소리 중 무엇인가요?", 105, "characterize_type", [G["throat"], G["nasal"]], CHARACTERIZE, allowed_values=["sore_throat", "nasal_obstruction", "nasal_discharge", "sneezing_itch", "facial_pain", "hoarseness", "other"]),
        q("symptom.duration", "Symptom Duration", "quantity", "duration", "증상은 언제부터 시작했나요?", 104, "characterize_duration", [G["context"]], CHARACTERIZE, reuse_existing=True),
        q("symptom.upper_respiratory.onset", "Upper Respiratory Symptom Onset", "coded", "onset", "갑자기 시작했나요, 서서히 시작했나요?", 103, "characterize_onset", [G["context"]], CHARACTERIZE, allowed_values=["sudden", "gradual", "unclear"]),
        q("symptom.upper_respiratory.severity", "Upper Respiratory Symptom Severity", "coded", "severity", "전체 불편은 가벼움, 중간, 심함 중 어디에 가깝나요?", 102, "characterize_severity", [G["context"]], CHARACTERIZE, allowed_values=["mild", "moderate", "severe"]),
        q("symptom.severe_breathing_difficulty", "Severe Breathing Difficulty", "boolean", "severe-breathing", "현재 숨쉬기가 매우 어렵나요?", 129, "airway_gate", [G["safety"]], SAFETY, safety_relevant=True),
        q("symptom.inspiratory_stridor", "Inspiratory Stridor", "boolean", "inspiratory-stridor", "숨을 들이쉴 때 목에서 높고 거친 소리가 나나요?", 129, "airway_gate", [G["safety"]], SAFETY, safety_relevant=True),
        q("symptom.unable_to_swallow_saliva_or_drooling", "Unable to Swallow Saliva or Drooling", "boolean", "drooling", "침도 삼키기 어려워 흘리거나 계속 뱉고 있나요?", 128, "airway_gate", [G["safety"], G["throat"]], SAFETY, safety_relevant=True),
        q("symptom.upper_respiratory.severe_rapid_worsening", "Severe and Rapidly Worsening Upper Respiratory Symptoms", "boolean", "rapid-worsening", "증상이 매우 심하면서 빠르게 악화하고 있나요?", 127, "rapid_deterioration_gate", [G["safety"]], SAFETY, safety_relevant=True),
        q("symptom.sudden_lip_tongue_or_throat_swelling", "Sudden Lip Tongue or Throat Swelling", "boolean", "allergic-swelling", "입술, 혀 또는 목이 갑자기 붓고 있나요?", 126, "anaphylaxis_gate", [G["safety"], G["allergy"]], SAFETY, safety_relevant=True),
        q("symptom.periorbital_swelling_or_displaced_eye", "Periorbital Swelling or Displaced Eye", "boolean", "orbital-swelling", "한쪽 눈 주위가 심하게 붓거나 눈이 앞으로 나오거나 위치가 달라 보이나요?", 125, "orbital_gate", [G["safety"], G["nasal"]], SAFETY, safety_relevant=True),
        q("symptom.double_vision_painful_eye_movement_or_reduced_vision", "Double Vision Painful Eye Movement or Reduced Vision", "boolean", "orbital-vision", "겹쳐 보이거나 눈을 움직일 때 아프거나 시력이 새로 떨어졌나요?", 124, "orbital_gate", [G["safety"], G["nasal"]], SAFETY, safety_relevant=True),
        q("symptom.sinus_intracranial_warning", "Sinus Intracranial Warning Feature", "boolean", "intracranial", "심한 이마 두통과 함께 목이 뻣뻣하거나 한쪽 팔다리 힘·말하기가 달라졌나요?", 123, "intracranial_gate", [G["safety"], G["nasal"]], SAFETY, safety_relevant=True),
        q("symptom.fever", "Fever", "boolean", "fever", "열이 나거나 몸이 뜨겁고 춥고 떨리나요?", 122, "infection_gate", [G["safety"], G["throat"], G["nasal"]], SAFETY, safety_relevant=True, reuse_existing=True),
        q("symptom.systemically_unwell", "Systemically Unwell", "boolean", "systemically-unwell", "평소와 달리 전신 상태가 몹시 나쁘고 기운이 없나요?", 121, "systemic_gate", [G["safety"]], SAFETY, safety_relevant=True),
        q("symptom.confusion", "New Confusion", "boolean", "confusion", "새로 혼란스럽거나 깨우기 어렵거나 평소와 다르게 반응하나요?", 120, "sepsis_gate", [G["safety"]], SAFETY, safety_relevant=True, reuse_existing=True),
        q("patient.immunocompromised", "Immunocompromised", "boolean", "immunocompromised", "면역을 낮추는 약을 사용하거나 면역이 약해지는 질환·치료를 받고 있나요?", 119, "complication_risk", [G["safety"], G["context"]], SAFETY + RISK, safety_relevant=True, reuse_existing=True),
        q("symptom.dehydration_or_unable_fluids", "Dehydration or Unable to Take Fluids", "boolean", "dehydration", "물을 충분히 마실 수 없거나 소변이 크게 줄고 진해졌나요?", 118, "dehydration_gate", [G["safety"], G["throat"]], SAFETY, safety_relevant=True),
        q("symptom.unilateral_neck_swelling", "Unilateral Neck Swelling", "boolean", "unilateral-neck-swelling", "목 한쪽이 새로 붓거나 불룩해졌나요?", 117, "suppurative_complication_gate", [G["safety"], G["throat"]], SAFETY, safety_relevant=True),
        q("symptom.trismus", "Trismus", "boolean", "trismus", "입을 평소처럼 벌리기 어렵나요?", 117, "suppurative_complication_gate", [G["safety"], G["throat"]], SAFETY, safety_relevant=True),
        q("symptom.muffled_voice", "Muffled Voice", "boolean", "muffled-voice", "목소리가 입에 무언가 문 듯 먹먹하게 변했나요?", 117, "suppurative_complication_gate", [G["safety"], G["throat"]], SAFETY, safety_relevant=True),
        q("symptom.throat_pain", "Throat Pain", "coded", "throat-pain", "목 통증은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 98, "throat_characterization", [G["throat"]], CHARACTERIZE, allowed_values=["none", "mild", "moderate", "severe"], terminology_binding={"system": SNOMED, "focus_code": "162397003", "attribute_code": "246112005"}, mrcm_ref=MRCM_REF),
        q("symptom.painful_swallowing", "Painful Swallowing", "boolean", "painful-swallow", "음식이나 물을 삼킬 때 목이 아픈가요?", 97, "throat_characterization", [G["throat"]], CHARACTERIZE),
        q("observation.tonsillar_exudate_or_pus", "Tonsillar Exudate or Pus", "boolean", "tonsillar-exudate", "편도에 흰 점이나 고름처럼 보이는 것이 있나요? 보지 못했다면 모름으로 답해 주세요.", 91, "feverpain_context", [G["throat"]], DIFFERENTIATE),
        q("symptom.tender_anterior_neck_nodes", "Tender Anterior Neck Nodes", "boolean", "neck-nodes", "목 앞쪽 림프절이 붓고 누르면 아픈가요?", 90, "centor_context", [G["throat"]], DIFFERENTIATE),
        q("symptom.cough", "Cough", "boolean", "cough", "기침이 함께 있나요?", 89, "upper_respiratory_context", [G["throat"], G["nasal"]], DIFFERENTIATE, reuse_existing=True),
        q("symptom.nasal_obstruction", "Nasal Obstruction", "coded", "nasal-obstruction", "코막힘은 없음, 한쪽, 양쪽 중 무엇인가요?", 96, "nasal_characterization", [G["nasal"]], CHARACTERIZE, allowed_values=["none", "unilateral", "bilateral"], terminology_binding={"system": SNOMED, "code": "232209000"}),
        q("symptom.nasal_discharge", "Nasal Discharge", "coded", "nasal-discharge", "콧물은 없음, 맑음, 누렇거나 녹색, 피가 섞임 중 무엇인가요?", 95, "nasal_characterization", [G["nasal"]], CHARACTERIZE, allowed_values=["none", "clear", "discoloured", "blood_stained"], terminology_binding={"system": SNOMED, "code": "64531003"}),
        q("symptom.unilateral_purulent_nasal_discharge", "Unilateral Purulent Nasal Discharge", "boolean", "unilateral-discharge", "누렇거나 녹색 콧물이 주로 한쪽 코에서 나오나요?", 88, "sinus_context", [G["nasal"]], DIFFERENTIATE),
        q("symptom.facial_pain_or_pressure", "Facial Pain or Pressure", "coded", "facial-pain", "눈·볼·이마 주변 통증이나 압박은 없음, 가벼움, 중간, 심함 중 어느 정도인가요?", 94, "sinus_context", [G["nasal"]], CHARACTERIZE, allowed_values=["none", "mild", "moderate", "severe"]),
        q("symptom.double_worsening_after_initial_improvement", "Worsening after Initial Improvement", "boolean", "double-worsening", "처음에는 나아지다가 다시 뚜렷하게 심해졌나요?", 87, "sinus_context", [G["nasal"]], DIFFERENTIATE),
        q("symptom.reduced_or_lost_smell", "Reduced or Lost Smell", "boolean", "smell", "후각이 줄거나 없어졌나요?", 86, "nasal_context", [G["nasal"]], DIFFERENTIATE),
        q("symptom.sneezing_or_itchy_nose", "Sneezing or Itchy Nose", "boolean", "sneezing-itch", "재채기가 반복되거나 코가 가려운가요?", 93, "allergic_context", [G["allergy"]], DIFFERENTIATE, terminology_binding={"system": SNOMED, "code": "76067001"}),
        q("symptom.itchy_red_watery_eyes", "Itchy Red Watery Eyes", "boolean", "itchy-eyes", "눈이 가렵고 붉거나 눈물이 나나요?", 85, "allergic_context", [G["allergy"]], DIFFERENTIATE),
        q("exposure.upper_respiratory_allergen", "Upper Respiratory Allergen Exposure", "string", "allergen", "꽃가루, 집먼지진드기, 동물, 곰팡이, 목재·밀가루 가루 또는 라텍스 접촉 뒤 심해지나요?", 84, "allergic_context", [G["allergy"], G["context"]], DIFFERENTIATE),
        q("symptom.hoarseness", "Hoarseness", "boolean", "hoarseness", "목소리가 쉬거나 평소와 달라졌나요?", 92, "voice_context", [G["voice"]], CHARACTERIZE, terminology_binding={"system": SNOMED, "code": "50219008", "display": "Hoarse (finding)", "version": "http://snomed.info/sct/900000000000207008/version/20260801", "relation": "equivalent"}),
        q("symptom.hoarseness_persistent_four_weeks", "Hoarseness Persistent Four Weeks", "boolean", "persistent-hoarseness", "쉰목소리가 좋아지지 않은 채 4주 이상 계속되나요?", 89, "persistent_voice_context", [G["voice"]], RISK),
        q("symptom.hoarseness_progressive", "Progressive Hoarseness", "boolean", "progressive-hoarseness", "쉰목소리가 시간이 지나면서 점점 심해지나요?", 88, "persistent_voice_context", [G["voice"]], RISK),
        q("patient.age_45_or_older", "Age 45 Years or Older", "boolean", "age-45-or-older", "만 45세 이상인가요?", 87, "persistent_voice_context", [G["voice"], G["context"]], RISK),
        q("symptom.persistent_mouth_ulcer_three_weeks", "Persistent Mouth Ulcer Three Weeks", "boolean", "persistent-mouth-ulcer", "입안 궤양이 3주 이상 낫지 않고 있나요?", 86, "persistent_warning_context", [G["voice"], G["throat"]], RISK),
        q("symptom.persistent_neck_lump_three_weeks", "Persistent Neck Lump Three Weeks", "boolean", "persistent-neck-lump", "입이나 목의 덩이·부기가 3주 이상 지속되나요?", 86, "persistent_warning_context", [G["voice"], G["throat"]], RISK),
        q("symptom.unilateral_referred_ear_pain", "Unilateral Referred Ear Pain", "boolean", "unilateral-ear-pain", "귀 자체 문제 없이 한쪽 귀에만 통증이 느껴지나요?", 85, "persistent_warning_context", [G["voice"], G["throat"]], RISK),
        q("history.recent_endotracheal_intubation", "Recent Endotracheal Intubation", "boolean", "recent-intubation", "목소리가 변하기 전에 기관삽관을 받은 적이 있나요?", 84, "laryngeal_evaluation_modifier", [G["voice"], G["context"]], RISK),
        q("history.recent_head_neck_or_chest_surgery", "Recent Head Neck or Chest Surgery", "boolean", "recent-head-neck-chest-surgery", "목소리가 변하기 전에 머리·목·가슴 수술을 받은 적이 있나요?", 84, "laryngeal_evaluation_modifier", [G["voice"], G["context"]], RISK),
        q("history.prior_head_neck_cancer", "Prior Head or Neck Cancer", "boolean", "prior-head-neck-cancer", "머리나 목 부위 암을 진단받거나 치료받은 적이 있나요?", 84, "laryngeal_evaluation_modifier", [G["voice"], G["context"]], RISK),
        q("patient.professional_or_high_demand_voice_use", "Professional or High-demand Voice Use", "boolean", "high-demand-voice", "직업이나 일상에서 목소리를 많이 또는 전문적으로 사용하나요?", 80, "voice_function_context", [G["voice"], G["context"]], RISK),
        q("symptom.upper_respiratory.recurrent", "Recurrent Upper Respiratory Symptoms", "boolean", "recurrent", "같은 증상이 자주 반복되나요?", 81, "recurrence_context", [G["context"]], RISK),
        q("exposure.sick_contact", "Sick Contact", "boolean", "sick-contact", "가족, 직장 또는 학교에 비슷한 증상이 있는 사람이 있나요?", 80, "infectious_context", [G["context"]], DIFFERENTIATE, reuse_existing=True),
        q("patient.smoking.status", "Smoking Status", "coded", "smoking-status", "일반담배·전자담배·가열담배 등 담배나 니코틴 제품 사용 상태는 현재 사용, 과거 사용, 사용한 적 없음 중 무엇인가요?", 83, "irritant_context", [G["context"], G["voice"]], RISK, allowed_values=["current", "former", "never"], reuse_existing=True),
        q("patient.smoking.product_types", "Tobacco or Nicotine Product Types", "coded_or_string", "smoking-product-types", "현재 또는 과거에 사용한 담배·니코틴 제품을 모두 선택하거나 보기에 없으면 직접 입력해 주세요.", 82, "irritant_context", [G["context"], G["voice"]], RISK, allowed_values=["combustible_cigarette", "heated_tobacco", "electronic_cigarette", "cigar_or_pipe", "smokeless_tobacco", "other"], reuse_existing=True),
        q("patient.smoking.cigarettes_per_day", "Combustible Cigarettes per Day", "quantity", "smoking-cigarettes-per-day", "일반담배를 피우거나 피웠다면 하루 평균 몇 개비였나요? 사용하지 않았다면 0개비라고 답해 주세요.", 81, "irritant_context", [G["context"], G["voice"]], RISK, unit="{cigarette}/d", minimum=0, reuse_existing=True),
        q("patient.smoking.duration_years", "Total Smoking Duration", "quantity", "smoking-duration-years", "담배·전자담배를 실제로 사용한 총 기간은 몇 년인가요?", 81, "irritant_context", [G["context"], G["voice"]], RISK, unit="a", minimum=0, reuse_existing=True),
        q("exposure.inhaled_irritant_current", "Current Inhaled Irritant Exposure", "boolean", "current-inhaled-irritant", "현재 직장이나 생활환경에서 연기·먼지·분진·화학 자극에 노출되나요?", 80, "irritant_context", [G["context"], G["voice"]], RISK),
        q("exposure.inhaled_irritant_type", "Inhaled Irritant Type", "string", "inhaled-irritant-type", "노출되는 연기·먼지·분진·화학 자극의 종류를 알려주세요.", 79, "irritant_context", [G["context"], G["voice"]], RISK),
        q("exposure.inhaled_irritant_duration", "Inhaled Irritant Exposure Duration", "quantity", "inhaled-irritant-duration", "그 자극에 노출된 기간은 몇 년인가요?", 79, "irritant_context", [G["context"], G["voice"]], RISK, unit="a", minimum=0),
        q("upper_respiratory.prior_laryngoscopy_and_results", "Prior Laryngoscopy and Results", "string", "prior-laryngoscopy", "이번 목소리 변화로 후두내시경을 받았다면 날짜와 결과, 정보 출처를 알려주세요. 받지 않았다면 받지 않음으로 답해 주세요.", 78, "laryngeal_evaluation_handoff", [G["voice"], G["handoff"]], RISK),
        q("treatment.upper_respiratory_self_care_response", "Upper Respiratory Self-care Response", "coded", "self-care", "수분 섭취, 가글, 일반 진통제·비강 세척·알레르기약 등을 사용했다면 좋아짐, 변화 없음, 악화 중 무엇인가요? 안 해봤다면 안 해봄으로 답해 주세요.", 78, "management_context", [G["context"]], RISK, allowed_values=["not_tried", "improved", "unchanged", "worsened"]),
        q("upper_respiratory.information_source_and_reliability", "Information Source and Reliability", "string", "information-source", "답변은 본인이 직접 하는지, 보호자가 대신하는지와 확인이 어려운 내용이 있는지 알려주세요.", 77, "handoff_source", [G["handoff"]], RISK),
        q("upper_respiratory.timeline_course_and_episode_pattern", "Timeline Course and Episode Pattern", "string", "timeline-course", "정확한 시작 시점, 이후 좋아지는지·악화하는지·변함없는지, 하루 중 달라지는 양상을 알려주세요.", 101, "clinician_timeline", [G["context"], G["handoff"]], CHARACTERIZE),
        q("upper_respiratory.exact_site_laterality_and_spread", "Exact Site Laterality and Spread", "string", "site-laterality", "불편한 정확한 부위와 한쪽·양쪽 여부, 귀·턱·목 등으로 퍼지는 느낌이 있으면 알려주세요.", 100, "clinician_location", [G["throat"], G["nasal"], G["handoff"]], CHARACTERIZE),
        q("observation.body_temperature", "Body Temperature", "quantity", "temperature", "체온을 쟀다면 가장 높았던 수치와 잰 시각을 알려주세요. 재지 않았다면 재지 않음으로 답해 주세요.", 99, "measured_fever_context", [G["context"], G["handoff"]], CHARACTERIZE, reuse_existing=True),
        q("upper_respiratory.associated_symptoms_detail", "Associated Symptoms Detail", "string", "associated-symptoms", "귀 통증, 두통, 몸살, 발진, 구토·설사 등 함께 있는 증상을 모두 알려주세요. 없으면 없음으로 답해 주세요.", 76, "clinician_associated_symptoms", [G["context"], G["handoff"]], DIFFERENTIATE),
        q("upper_respiratory.functional_impact_sleep_work_school_intake", "Functional Impact on Sleep Work School and Intake", "string", "functional-impact", "수면, 식사·수분 섭취, 말하기, 직장·학교생활에 어느 정도 지장이 있나요?", 75, "clinician_function", [G["context"], G["handoff"]], CHARACTERIZE),
        q("upper_respiratory.previous_episodes_and_baseline", "Previous Episodes and Baseline", "string", "previous-episodes", "이전에도 비슷한 증상이 있었는지, 있었다면 빈도와 평소 상태로 돌아왔는지 알려주세요.", 74, "recurrence_handoff", [G["context"], G["handoff"]], RISK),
        q("upper_respiratory.current_medicines_and_response", "Current Medicines and Response", "string", "medicines-response", "현재 복용 중인 약과 이번 증상에 사용한 약의 이름·용량·시각·효과 또는 부작용을 알려주세요.", 73, "medicine_handoff", [G["context"], G["handoff"]], RISK),
        q("upper_respiratory.recent_antibiotic_use_and_response", "Recent Antibiotic Use and Response", "string", "antibiotic-history", "최근 항생제를 복용했다면 이름, 시작·종료일, 복용 누락, 효과와 부작용을 알려주세요. 없으면 없음으로 답해 주세요.", 72, "antibiotic_handoff", [G["context"], G["handoff"]], RISK),
        q("upper_respiratory.medicine_allergies_and_reactions", "Medicine Allergies and Reactions", "string", "medicine-allergy", "약물 알레르기나 심한 부작용이 있다면 약 이름과 반응을 알려주세요. 없으면 없음으로 답해 주세요.", 71, "allergy_handoff", [G["context"], G["handoff"]], RISK),
        q("upper_respiratory.age_pregnancy_and_high_risk_context", "Age Pregnancy and High Risk Context", "string", "high-risk-context", "영유아·고령, 임신·산후, 만성질환·면역저하 등 진료에 참고할 상황이 있나요?", 70, "risk_handoff", [G["context"], G["handoff"]], RISK),
        q("upper_respiratory.prior_examination_swab_tests_and_results", "Prior Examination Swab Tests and Results", "string", "prior-tests", "이번 증상으로 진찰, 신속검사·배양검사 등 검사를 받았다면 날짜, 검사명, 결과와 정보 출처를 알려주세요. 받지 않았다면 받지 않음으로 답해 주세요.", 69, "test_handoff", [G["context"], G["handoff"]], RISK),
        q("upper_respiratory.prior_imaging_and_results", "Prior Imaging and Results", "string", "prior-imaging", "이번 증상으로 영상검사를 받았다면 날짜, 검사명, 결과와 정보 출처를 알려주세요. 받지 않았다면 받지 않음으로 답해 주세요.", 68, "imaging_handoff", [G["nasal"], G["handoff"]], RISK),
        q("upper_respiratory.ent_dental_history_and_recent_procedure", "ENT Dental History and Recent Procedure", "string", "ent-dental-history", "관련된 귀·코·목 또는 치과 질환, 수술·시술·치료가 있다면 종류와 시기를 알려주세요.", 67, "history_handoff", [G["throat"], G["nasal"], G["handoff"]], RISK),
        q("upper_respiratory.patient_concern_goal_and_other_rfe", "Patient Concern Goal and Other Reason for Encounter", "string", "patient-goal", "가장 걱정되는 점, 진료에서 확인받고 싶은 점, 함께 상담할 다른 문제가 있으면 알려주세요.", 66, "patient_priority", [G["handoff"]], RISK),
        q("upper_respiratory.conflicting_information_and_unverified_items", "Conflicting Information and Unverified Items", "string", "conflict-unverified", "기억과 기록이 다르거나 아직 확인하지 못한 정보가 있으면 무엇인지 알려주세요.", 65, "handoff_uncertainty", [G["handoff"]], RISK),
    ]
    rules = [
        safety_rule(PREFIX, "severe-breathing", {"fact": "symptom.severe_breathing_difficulty", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "inspiratory-stridor", {"fact": "symptom.inspiratory_stridor", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "unable-swallow-drooling", {"fact": "symptom.unable_to_swallow_saliva_or_drooling", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "rapid-worsening", {"fact": "symptom.upper_respiratory.severe_rapid_worsening", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "allergic-swelling", {"fact": "symptom.sudden_lip_tongue_or_throat_swelling", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "orbital-complication", {"all": [{"fact": "symptom.periorbital_swelling_or_displaced_eye", "equals": True}, {"fact": "symptom.double_vision_painful_eye_movement_or_reduced_vision", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "intracranial-warning", {"fact": "symptom.sinus_intracranial_warning", "equals": True}, "emergency", 1000),
        safety_rule(PREFIX, "confusion-systemic", {"all": [{"fact": "symptom.confusion", "equals": True}, {"fact": "symptom.fever", "equals": True}]}, "emergency", 1000),
        safety_rule(PREFIX, "immunocompromised-fever", {"all": [{"fact": "patient.immunocompromised", "equals": True}, {"fact": "symptom.fever", "equals": True}]}, "urgent", 900),
        safety_rule(PREFIX, "dehydration", {"fact": "symptom.dehydration_or_unable_fluids", "equals": True}, "urgent", 900),
        safety_rule(PREFIX, "deep-neck-warning", {"any": [{"fact": "symptom.unilateral_neck_swelling", "equals": True}, {"fact": "symptom.trismus", "equals": True}, {"fact": "symptom.muffled_voice", "equals": True}]}, "urgent", 900),
        safety_rule(PREFIX, "persistent-hoarseness-45-plus", {"all": [{"fact": "symptom.hoarseness_persistent_four_weeks", "equals": True}, {"fact": "patient.age_45_or_older", "equals": True}]}, "urgent", 890),
        safety_rule(PREFIX, "hoarseness-neck-lump", {"all": [{"fact": "symptom.hoarseness", "equals": True}, {"fact": "symptom.persistent_neck_lump_three_weeks", "equals": True}]}, "urgent", 890),
    ]
    extra_nodes = [
        {"id": identifier, "type": "ClinicalGroup", "display": identifier.split(".")[-1].replace("-", " ").title()}
        for identifier in G.values()
    ] + [
        {"id": "hypothesis.upper-respiratory.immediate-safety", "type": "Hypothesis", "display": "Immediate Upper Airway Safety Warning Pattern"},
        {"id": "hypothesis.upper-respiratory.throat", "type": "Hypothesis", "display": "Throat Symptom Pattern"},
        {"id": "hypothesis.upper-respiratory.sinus", "type": "Hypothesis", "display": "Nasal and Sinus Symptom Pattern"},
        {"id": "hypothesis.upper-respiratory.allergic", "type": "Hypothesis", "display": "Allergic Upper Respiratory Pattern"},
        {"id": "hypothesis.upper-respiratory.persistence", "type": "Hypothesis", "display": "Persistent Voice or Lesion Warning Pattern"},
    ]
    group_edges = [
        [G["safety"], "hypothesis.upper-respiratory.immediate-safety"],
        [G["throat"], "hypothesis.upper-respiratory.throat"],
        [G["nasal"], "hypothesis.upper-respiratory.sinus"],
        [G["allergy"], "hypothesis.upper-respiratory.allergic"],
        [G["voice"], "hypothesis.upper-respiratory.persistence"],
    ]
    return {
        "id": "knowledge.generated.upper-respiratory-symptoms",
        "version": VERSION, "status": "research_only",
        "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-upper-respiratory-symptoms-research",
        "default_refresh": default_refresh(),
        "extra_nodes": extra_nodes, "group_hypothesis_edges": group_edges,
        "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def build_mrcm():
    concepts = [
        {"code": "162397003", "display": "Pain in throat (finding)", "attribute_count_returned": 20},
        {"code": "232209000", "display": "Nasal obstruction (disorder)", "attribute_count_returned": 22},
        {"code": "64531003", "display": "Nasal discharge (finding)", "attribute_count_returned": 0},
        {"code": "76067001", "display": "Sneezing (finding)", "attribute_count_returned": 20},
        {"code": "50219008", "display": "Hoarse (finding)", "attribute_count_returned": 20},
    ]
    supported = [item for item in concepts if item["attribute_count_returned"] > 0]
    checks = [
        {"focus_code": concept["code"], "attribute_code": attribute, "allowed": True}
        for concept in supported for attribute in ("363698007", "246112005")
    ]
    return {
        "id": MRCM_REF, "version": VERSION,
        "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SNOMED, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": concepts, "checks": checks,
        "unsupported_checks": [{"focus_code": "64531003", "reason": "STOM allowed-attribute endpoint returned an empty array; no post-coordination assertion made."}],
        "validation": {"method": "build_time_live_mrcm_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "partial_provisional_pass"},
        "provenance": provenance(["source.stom.mrcm.upper-respiratory.20260714"]),
    }


def build_completion_policy(fragment):
    policy = completion_policy(
        prefix="upper-respiratory-symptoms", fragment=fragment,
        presentation_fact="symptom.upper_respiratory.current", question_budget=45,
        source_refs=SOURCES,
    )
    branch_specific_safety = {
        "symptom.periorbital_swelling_or_displaced_eye",
        "symptom.double_vision_painful_eye_movement_or_reduced_vision",
        "symptom.sinus_intracranial_warning",
        "symptom.confusion",
        "symptom.fever",
        "patient.immunocompromised",
        "symptom.dehydration_or_unable_fluids",
        "symptom.unilateral_neck_swelling",
        "symptom.trismus",
        "symptom.muffled_voice",
        "symptom.hoarseness",
        "symptom.hoarseness_persistent_four_weeks",
        "patient.age_45_or_older",
        "symptom.persistent_neck_lump_three_weeks",
    }
    policy["required_facts"]["always"] = [
        fact_id
        for fact_id in policy["required_facts"]["always"]
        if fact_id not in branch_specific_safety
    ]
    policy["required_facts"]["routine"] = [
        "symptom.upper_respiratory.main_type",
        "symptom.duration",
        "symptom.upper_respiratory.onset",
        "symptom.upper_respiratory.severity",
        "upper_respiratory.information_source_and_reliability",
        "upper_respiratory.timeline_course_and_episode_pattern",
        "upper_respiratory.exact_site_laterality_and_spread",
        "observation.body_temperature",
        "upper_respiratory.associated_symptoms_detail",
        "upper_respiratory.functional_impact_sleep_work_school_intake",
        "upper_respiratory.current_medicines_and_response",
        "upper_respiratory.medicine_allergies_and_reactions",
        "upper_respiratory.age_pregnancy_and_high_risk_context",
        "upper_respiratory.patient_concern_goal_and_other_rfe",
        "upper_respiratory.conflicting_information_and_unverified_items",
    ]
    nasal = [
        "symptom.nasal_obstruction", "symptom.nasal_discharge",
        "symptom.unilateral_purulent_nasal_discharge",
        "symptom.facial_pain_or_pressure",
        "symptom.double_worsening_after_initial_improvement",
        "symptom.reduced_or_lost_smell",
        "upper_respiratory.recent_antibiotic_use_and_response",
        "upper_respiratory.prior_examination_swab_tests_and_results",
        "upper_respiratory.prior_imaging_and_results",
        "upper_respiratory.ent_dental_history_and_recent_procedure",
    ]
    policy["conditional_required_facts"] = [{
        "selector_fact": "symptom.upper_respiratory.main_type",
        "cases": {
            "sore_throat": [
                "symptom.fever", "symptom.confusion",
                "patient.immunocompromised",
                "symptom.dehydration_or_unable_fluids",
                "symptom.unilateral_neck_swelling", "symptom.trismus",
                "symptom.muffled_voice",
                "symptom.throat_pain", "symptom.painful_swallowing",
                "observation.tonsillar_exudate_or_pus",
                "symptom.tender_anterior_neck_nodes", "symptom.cough",
                "upper_respiratory.recent_antibiotic_use_and_response",
                "upper_respiratory.prior_examination_swab_tests_and_results",
                "upper_respiratory.ent_dental_history_and_recent_procedure",
            ],
            "nasal_obstruction": nasal,
            "nasal_discharge": nasal,
            "facial_pain": nasal,
            "sneezing_itch": [
                "symptom.sneezing_or_itchy_nose",
                "symptom.itchy_red_watery_eyes",
                "exposure.upper_respiratory_allergen",
                "treatment.upper_respiratory_self_care_response",
                "upper_respiratory.previous_episodes_and_baseline",
            ],
            "hoarseness": [
                "symptom.hoarseness",
                "symptom.hoarseness_persistent_four_weeks",
                "symptom.hoarseness_progressive",
                "patient.age_45_or_older",
                "symptom.persistent_mouth_ulcer_three_weeks",
                "symptom.persistent_neck_lump_three_weeks",
                "symptom.unilateral_referred_ear_pain",
                "history.recent_endotracheal_intubation",
                "history.recent_head_neck_or_chest_surgery",
                "history.prior_head_neck_cancer",
                "patient.professional_or_high_demand_voice_use",
                "patient.smoking.status",
                "exposure.inhaled_irritant_current",
                "upper_respiratory.prior_laryngoscopy_and_results",
                "upper_respiratory.previous_episodes_and_baseline",
                "upper_respiratory.ent_dental_history_and_recent_procedure",
            ],
            "other": [
                "symptom.upper_respiratory.recurrent",
                "exposure.sick_contact",
                "treatment.upper_respiratory_self_care_response",
                "upper_respiratory.previous_episodes_and_baseline",
            ],
        },
    }]
    nasal_safety = [
        "symptom.periorbital_swelling_or_displaced_eye",
        "symptom.double_vision_painful_eye_movement_or_reduced_vision",
        "symptom.sinus_intracranial_warning",
        "symptom.fever",
        "patient.immunocompromised",
        "symptom.dehydration_or_unable_fluids",
    ]
    cases = policy["conditional_required_facts"][0]["cases"]
    for branch in ("nasal_obstruction", "nasal_discharge", "facial_pain"):
        cases[branch] = nasal_safety + cases[branch]
    policy["conditional_required_facts"].extend([
        {
            "when": {
                "fact": "patient.smoking.status",
                "in": ["current", "former"],
            },
            "required_facts": [
                "patient.smoking.product_types",
                "patient.smoking.duration_years",
            ],
            "reason": "reported_tobacco_or_nicotine_use_requires_product_and_duration",
        },
        {
            "when": {
                "fact": "patient.smoking.product_types",
                "equals": "combustible_cigarette",
            },
            "required_facts": ["patient.smoking.cigarettes_per_day"],
            "reason": "combustible_cigarette_use_requires_daily_amount",
        },
        {
            "when": {
                "fact": "exposure.inhaled_irritant_current",
                "equals": True,
            },
            "required_facts": [
                "exposure.inhaled_irritant_type",
                "exposure.inhaled_irritant_duration",
            ],
            "reason": "reported_inhaled_irritant_requires_type_and_duration",
        },
    ])
    return policy


def build_sources():
    definitions = [
        ("source.nhs.sore-throat.2024", "NHS", "Sore throat", "reviewed-2024-04-08", "https://www.nhs.uk/symptoms/sore-throat/", "public_health_guidance", 7),
        ("source.nice.ng84.sore-throat.2025", "NICE", "Sore throat (acute): antimicrobial prescribing", "NG84-updated-2025", "https://www.nice.org.uk/guidance/ng84/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nice.ng79.sinusitis.2026", "NICE", "Sinusitis (acute): antimicrobial prescribing", "NG79-updated-2026", "https://www.nice.org.uk/guidance/ng79/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nhs.allergic-rhinitis.2026", "NHS", "Allergic rhinitis", "accessed-2026-07-14", "https://www.nhs.uk/conditions/allergic-rhinitis/", "public_health_guidance", 7),
        ("source.aao-hns.hoarseness-dysphonia.2018", "AAO-HNS", "Clinical Practice Guideline: Hoarseness (Dysphonia) (Update)", "2018-guideline-page-modified-2026-05-08", "https://www.entnet.org/quality-practice/quality-products/clinical-practice-guidelines/hoarseness-dysphonia/", "clinical_guideline", 1),
        ("source.pubmed.hoarseness-dysphonia.29494321", "NLM PubMed", "Clinical Practice Guideline: Hoarseness (Dysphonia) (Update)", "PMID-29494321", "https://pubmed.ncbi.nlm.nih.gov/29494321/", "clinical_guideline", 1),
        ("source.nice.ng12.laryngeal-cancer.2026", "NICE", "Suspected cancer: recognition and referral — laryngeal cancer", "NG12-current-2026-08-09", "https://www.nice.org.uk/guidance/ng12/chapter/recommendations-organised-by-site-of-cancer#laryngeal-cancer", "nice_guidance", 7),
        ("source.stom.snomed-hoarse.20260801", "Infoclinic", "STOM SNOMED CT lookup: Hoarse (finding)", "SNOMEDCT-20260801", "http://localhost:8088/fhir/CodeSystem/$lookup?system=http%3A%2F%2Fsnomed.info%2Fsct&code=50219008", "terminology_server", 30),
        ("source.stom.mrcm.upper-respiratory.20260714", "Infoclinic", "STOM upper respiratory SNOMED CT lookup and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/162397003", "terminology_server", 30),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, days in definitions:
        is_new_voice_source = sid in SOURCES[4:]
        last_monitored = "2026-08-09" if is_new_voice_source else ("2026-07-14" if profile == "terminology_server" else "2026-07-22")
        if is_new_voice_source and profile == "terminology_server":
            next_monitor = "2026-09-08"
        elif is_new_voice_source and profile in {"clinical_guideline"}:
            next_monitor = "2026-08-10"
        elif is_new_voice_source:
            next_monitor = "2026-08-16"
        elif profile == "terminology_server":
            next_monitor = "2026-08-13"
        elif publisher == "NICE":
            next_monitor = "2026-07-23"
        else:
            next_monitor = "2026-07-29"
        artifacts.append({
            "id": sid,
            "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata",
            "publisher": publisher, "title": title, "version": version, "url": url,
            "language": "en",
            "digest": ({
                "source.aao-hns.hoarseness-dysphonia.2018": "sha256:029a3c6a5e1133fef4904607561c4aea2e56313ee21c54f71f694bd09425a703",
                "source.pubmed.hoarseness-dysphonia.29494321": "sha256:30510eec4d92db9791136421f508f5ef27208c334910a68b75cff66db6a9ed7c",
                "source.nice.ng12.laryngeal-cancer.2026": "sha256:1776edae05bad6d2f83e940376dedbcc9166d60774d46121b19a23c7ac9c4fd4",
                "source.stom.snomed-hoarse.20260801": "stom_lookup_active_code_50219008_version_20260801",
            }.get(sid, "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached")),
            "license_status": "restricted" if publisher != "NHS" else "unknown",
            "complete": False, "monitor_profile": profile, "monitor_interval_days": days,
            "last_monitored_at": last_monitored,
            "next_monitor_at": next_monitor,
            "monitor_result": "current_official_source_confirmed_no_replacement_identified",
            "assertions": [
                "Build-Time metadata only; Runtime does not browse this source and the generated clinical content remains unreviewed.",
                "The official page was checked for current symptom history, expected course, reassessment and complication context; no source text is reproduced at Runtime.",
            ],
        })
    research = {
        "id": "source-manifest.primary-care-upper-respiratory-symptoms-research",
        "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only",
        "artifacts": artifacts,
        "provenance": provenance([item[0] for item in definitions]),
    }
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.repository.context", "repository_specification", "docs/context", True),
        ("source.catalog.primary-care-rfe", "knowledge_catalog", "knowledge/catalog/primary-care-rfe.json", True),
        ("source.registry.shared-primary-care-facts", "fact_registry", "knowledge/shared/primary-care-facts.json", True),
        ("source.generated.primary-care-upper-respiratory", "generated_clinical_knowledge", "knowledge/generated/upper-respiratory/upper-respiratory-symptoms.json", True),
        ("source.mapping.snomed-mrcm.upper-respiratory", "terminology_mapping", "mappings/terminology/snomed-mrcm-upper-respiratory-symptoms.json", False),
        ("source.external.primary-care-upper-respiratory-research", "external_source_manifest", "sources/manifests/primary-care-upper-respiratory-symptoms-research.json", False),
        ("source.policy.primary-care-upper-respiratory-completion", "runtime_policy", "policies/primary-care-upper-respiratory-symptoms-completion.json", True),
    ]
    primary = {
        "id": "source-manifest.primary-care-upper-respiratory-symptoms",
        "version": VERSION, "acquired_at": CREATED_AT,
        "artifacts": [{
            "id": sid, "kind": kind, "publisher": "clinical-interview-platform",
            "version": VERSION, "language": "en", "path": path,
            "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown",
            "complete": complete,
        } for sid, kind, path, complete in paths],
        "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md", "sources/manifests/primary-care-upper-respiratory-symptoms-research.json"]),
    }
    return primary, research


def build_cases(fragment):
    true_map = {
        "severe-breathing": ["symptom.severe_breathing_difficulty"],
        "inspiratory-stridor": ["symptom.inspiratory_stridor"],
        "unable-swallow-drooling": ["symptom.unable_to_swallow_saliva_or_drooling"],
        "rapid-worsening": ["symptom.upper_respiratory.severe_rapid_worsening"],
        "allergic-swelling": ["symptom.sudden_lip_tongue_or_throat_swelling"],
        "orbital-complication": ["symptom.periorbital_swelling_or_displaced_eye", "symptom.double_vision_painful_eye_movement_or_reduced_vision"],
        "intracranial-warning": ["symptom.sinus_intracranial_warning"],
        "confusion-systemic": ["symptom.confusion", "symptom.fever"],
        "immunocompromised-fever": ["patient.immunocompromised", "symptom.fever"],
        "dehydration": ["symptom.dehydration_or_unable_fluids"],
        "deep-neck-warning": ["symptom.unilateral_neck_swelling", "symptom.trismus", "symptom.muffled_voice"],
        "persistent-hoarseness-45-plus": ["symptom.hoarseness_persistent_four_weeks", "patient.age_45_or_older"],
        "hoarseness-neck-lump": ["symptom.hoarseness", "symptom.persistent_neck_lump_three_weeks"],
    }
    cases = {}
    safety_branch = {
        "orbital-complication": "nasal_obstruction",
        "intracranial-warning": "nasal_obstruction",
        "confusion-systemic": "sore_throat",
        "immunocompromised-fever": "sore_throat",
        "dehydration": "sore_throat",
        "deep-neck-warning": "sore_throat",
        "persistent-hoarseness-45-plus": "hoarseness",
        "hoarseness-neck-lump": "hoarseness",
    }
    for index, item in enumerate(fragment["safety_rules"], 1):
        key = item["id"].split("safety.", 1)[1]
        level = item["then"]["safety_level"]
        hidden_state = {
            fact_id: {"value": True} for fact_id in true_map[key]
        }
        if key in safety_branch:
            hidden_state["symptom.upper_respiratory.current"] = {"value": True}
            hidden_state["symptom.upper_respiratory.main_type"] = {
                "value": safety_branch[key]
            }
        cases[f"UPPER-{key.upper()}-001.json"] = {
            "id": f"UPPER-{key.upper()}-001", "simulation_language": "ko",
            "persona": {"age": 30 + index},
            "initial_statement": {"ko": "목과 코가 불편해요."},
            "hidden_state": hidden_state,
            "expected": {
                "expected_safety_level": level,
                "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [item["id"]],
                "expected_max_turns": 22,
                "forbidden_assertions": ["diagnosis.epiglottitis", "diagnosis.sinusitis", "recommendation.antibiotic"],
            },
            "provenance": provenance(SOURCES),
        }
    policy = build_completion_policy(fragment)
    by_id = {item["fact"]["id"]: item["fact"] for item in fragment["entries"]}

    def routine_hidden(branch):
        required = set(
            policy["required_facts"]["always"]
            + policy["required_facts"]["routine"]
            + policy["conditional_required_facts"][0]["cases"][branch]
        )
        hidden = {}
        for fid in required:
            fact = by_id[fid]
            if fact["value_type"] == "boolean":
                hidden[fid] = {"value": fid == "symptom.upper_respiratory.current"}
            elif fact["value_type"] == "quantity":
                hidden[fid] = {"value": {"amount": 37.2, "unit": "Cel"}} if fid == "observation.body_temperature" else {"value": {"amount": 3, "unit": "days"}}
            elif fact["value_type"] == "coded":
                hidden[fid] = {"value": fact.get("allowed_values", ["none"])[0]}
            else:
                hidden[fid] = {"value": "없음"}
        hidden["symptom.upper_respiratory.main_type"] = {"value": branch}
        return hidden

    hidden = routine_hidden("nasal_obstruction")
    declined = "upper_respiratory.prior_imaging_and_results"
    hidden.pop(declined)
    cases["UPPER-DATA-ABSENT-001.json"] = {
        "id": "UPPER-DATA-ABSENT-001", "simulation_language": "ko",
        "persona": {"age": 37}, "initial_statement": {"ko": "코가 막히고 목이 조금 아파요."},
        "hidden_state": hidden,
        "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}},
        "expected": {
            "expected_data_absent_reasons": {declined: "asked-declined"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 40,
            "forbidden_assertions": ["diagnosis.common_cold", "recommendation.antibiotic"],
        },
        "provenance": provenance(["source.nice.ng84.sore-throat.2025", "specifications/clinical-memory.md"]),
    }
    child = routine_hidden("sore_throat")
    child["upper_respiratory.information_source_and_reliability"] = {"value": "보호자가 답변하며 아이가 직접 표현한 내용은 제한적"}
    child["upper_respiratory.age_pregnancy_and_high_risk_context"] = {"value": "4세 아동, 보호자 대리 답변"}
    child.pop("observation.body_temperature")
    cases["UPPER-CHILD-PROXY-SORE-THROAT-001.json"] = {
        "id": "UPPER-CHILD-PROXY-SORE-THROAT-001", "simulation_language": "ko",
        "persona": {"age": 4, "response_source": "proxy_report"},
        "initial_statement": {"ko": "아이 목이 아프다고 해서 보호자가 대신 답합니다."},
        "hidden_state": child,
        "response_behavior": {"observation.body_temperature": {"dataAbsentReason": "not-performed"}},
        "expected": {
            "expected_data_absent_reasons": {"observation.body_temperature": "not-performed"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 40,
            "forbidden_assertions": ["diagnosis.strep_throat", "recommendation.antibiotic"],
        },
        "provenance": provenance(["source.nice.ng84.sore-throat.2025", "specifications/clinical-memory.md"]),
    }
    adult = routine_hidden("sore_throat")
    adult.update({
        "symptom.upper_respiratory.current": {"value": True},
        "symptom.upper_respiratory.main_type": {"value": "sore_throat"},
        "symptom.duration": {"value": {"amount": 2, "unit": "days"}},
        "symptom.upper_respiratory.onset": {"value": "gradual"},
        "symptom.upper_respiratory.severity": {"value": "moderate"},
        "symptom.throat_pain": {"value": "moderate"},
        "symptom.painful_swallowing": {"value": True},
        "upper_respiratory.timeline_course_and_episode_pattern": {"value": "2일 전 서서히 시작했고 오늘까지 비슷함"},
        "upper_respiratory.exact_site_laterality_and_spread": {"value": "목 중앙 통증, 한쪽 치우침이나 귀·턱으로 퍼짐 없음"},
        "upper_respiratory.functional_impact_sleep_work_school_intake": {"value": "물과 부드러운 음식은 가능하지만 삼킬 때 불편하고 수면 방해는 없음"},
        "upper_respiratory.current_medicines_and_response": {"value": "일반 진통제를 한 번 복용했고 통증이 조금 감소"},
        "upper_respiratory.medicine_allergies_and_reactions": {"value": "알려진 약물 알레르기 없음"},
        "upper_respiratory.prior_examination_swab_tests_and_results": {"value": "이번 증상으로 아직 진찰이나 검사를 받지 않음"},
        "upper_respiratory.ent_dental_history_and_recent_procedure": {"value": "관련 이비인후과·치과 질환이나 최근 시술 없음"},
        "upper_respiratory.patient_concern_goal_and_other_rfe": {"value": "원인 단정보다 진찰 전 필요한 정보를 전달하고 싶음"},
    })
    cases["UPPER-ADULT-SORE-THROAT-CLINICIAN-HANDOFF-001.json"] = {
        "id": "UPPER-ADULT-SORE-THROAT-CLINICIAN-HANDOFF-001",
        "simulation_language": "ko",
        "clinician_submission": True,
        "encounter_context": {
            "care_setting": "primary_care",
            "encounter_type": "new_encounter",
            "interview_initiator": "patient",
            "interview_mode": "chat",
            "available_information": ["no_previous_records"],
            "time_constraint": "routine",
            "clinical_responsibility": "decision_support",
        },
        "persona": {"age": 34},
        "initial_statement": {"ko": "이틀 전부터 목이 아프고 삼킬 때 불편해서 진료 전 문진을 작성해요."},
        "hidden_state": adult,
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_clinician_handoff": True,
            "expected_known_facts": {
                "symptom.upper_respiratory.main_type": "sore_throat",
                "symptom.throat_pain": "moderate",
                "pain.nrs_score": 5,
                "upper_respiratory.prior_examination_swab_tests_and_results": "이번 증상으로 아직 진찰이나 검사를 받지 않음",
            },
            "expected_max_turns": 60,
            "forbidden_assertions": ["diagnosis.strep_throat", "diagnosis.laryngitis", "recommendation.antibiotic"],
        },
        "provenance": provenance(["source.nhs.sore-throat.2024", "source.nice.ng84.sore-throat.2025", "specifications/clinical-memory.md"]),
    }
    voice = routine_hidden("hoarseness")
    voice["symptom.hoarseness"] = {"value": True}
    voice["symptom.hoarseness_persistent_four_weeks"] = {"value": True}
    voice["symptom.hoarseness_progressive"] = {"value": True}
    voice["patient.age_45_or_older"] = {"value": True}
    voice["patient.smoking.status"] = {"value": "current"}
    voice["patient.smoking.product_types"] = {"value": "combustible_cigarette"}
    voice["patient.smoking.cigarettes_per_day"] = {"value": {"amount": 10, "unit": "{cigarette}/d"}}
    voice["patient.smoking.duration_years"] = {"value": {"amount": 25, "unit": "a"}}
    voice["exposure.inhaled_irritant_current"] = {"value": True}
    voice["exposure.inhaled_irritant_type"] = {"value": "작업장 목재 분진"}
    voice["exposure.inhaled_irritant_duration"] = {"value": {"amount": 12, "unit": "a"}}
    voice["upper_respiratory.conflicting_information_and_unverified_items"] = {"value": "본인은 2주라고 하나 이전 기록에는 4주로 적혀 있어 의료진 확인 필요"}
    cases["UPPER-PERSISTENT-HOARSENESS-HANDOFF-001.json"] = {
        "id": "UPPER-PERSISTENT-HOARSENESS-HANDOFF-001", "simulation_language": "ko",
        "persona": {"age": 58}, "initial_statement": {"ko": "목소리가 계속 쉬어 있고 작업장에서 먼지를 마셔요."},
        "hidden_state": voice,
        "expected": {
            "expected_safety_level": "urgent", "expected_safety_action": "human_handoff", "expected_stop_reason": "urgent_escalation",
            "expected_triggered_rules_contains": ["rule.upper-respiratory.safety.persistent-hoarseness-45-plus"],
            "expected_max_turns": 40,
            "forbidden_assertions": ["diagnosis.laryngeal_cancer", "diagnosis.laryngitis"],
        },
        "provenance": provenance(SOURCES),
    }
    routine_voice = dict(voice)
    routine_voice["symptom.hoarseness_persistent_four_weeks"] = {"value": False}
    routine_voice["symptom.persistent_neck_lump_three_weeks"] = {"value": False}
    routine_voice["symptom.unilateral_referred_ear_pain"] = {"value": True}
    routine_voice["upper_respiratory.patient_concern_goal_and_other_rfe"] = {
        "value": "목소리 원인 확인과 새 한쪽 귀 불편도 의료진에게 전달 희망"
    }
    routine_voice["upper_respiratory.conflicting_information_and_unverified_items"] = {
        "value": "본인은 3주라고 하나 이전 메모에는 2주로 적혀 있어 시작 시점 확인 필요"
    }
    cases["UPPER-HOARSENESS-REMOTE-CONFLICT-DATA-ABSENT-001.json"] = {
        "id": "UPPER-HOARSENESS-REMOTE-CONFLICT-DATA-ABSENT-001",
        "simulation_language": "ko",
        "clinician_submission": True,
        "persona": {"age": 68, "communication_need": "large_text_and_slow_pacing"},
        "encounter_context": {
            "care_setting": "telemedicine",
            "encounter_type": "follow_up",
            "interview_initiator": "patient",
            "interview_mode": "chat",
            "available_information": ["patient_recalled_prior_note"],
            "time_constraint": "scheduled",
            "clinical_responsibility": "decision_support",
        },
        "operational_state": {"terminology_adapter": "unavailable"},
        "initial_statement": {
            "ko": "예약된 원격 재진입니다. 3주째 목소리가 점점 쉬고 담배와 목재 분진에 노출됩니다. 귀 불편도 함께 전달하고 싶어요."
        },
        "hidden_state": routine_voice,
        "response_behavior": {
            "upper_respiratory.prior_laryngoscopy_and_results": {
                "dataAbsentReason": "asked-unknown"
            }
        },
        "expected": {
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_data_absent_reasons": {
                "upper_respiratory.prior_laryngoscopy_and_results": "asked-unknown"
            },
            "expected_max_turns": 80,
            "expected_clinician_handoff": True,
            "forbidden_assertions": [
                "diagnosis.laryngeal_cancer",
                "diagnosis.laryngitis",
                "recommendation.antibiotic",
            ],
        },
        "provenance": provenance(SOURCES),
    }
    sinus = routine_hidden("facial_pain")
    sinus["symptom.facial_pain_or_pressure"] = {"value": "moderate"}
    sinus["upper_respiratory.recent_antibiotic_use_and_response"] = {"value": "5일 전 처방 항생제를 시작했으나 이름은 모름; 호전 없음"}
    sinus["upper_respiratory.prior_examination_swab_tests_and_results"] = {"value": "동네의원 진찰, 검사명과 결과는 확인되지 않음"}
    sinus["upper_respiratory.patient_concern_goal_and_other_rfe"] = {"value": "얼굴 통증과 함께 새 귀 통증도 의료진에게 전달 희망"}
    cases["UPPER-SINUS-PRIOR-TREATMENT-MULTI-RFE-001.json"] = {
        "id": "UPPER-SINUS-PRIOR-TREATMENT-MULTI-RFE-001", "simulation_language": "ko",
        "persona": {"age": 46}, "initial_statement": {"ko": "얼굴이 아프고 코가 막히는데 귀도 새로 아파요."},
        "hidden_state": sinus,
        "expected": {
            "expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved",
            "expected_max_turns": 40,
            "forbidden_assertions": ["diagnosis.bacterial_sinusitis", "recommendation.antibiotic"],
        },
        "provenance": provenance(["source.nice.ng79.sinusitis.2026", "specifications/reasoning-loop.md"]),
    }
    return cases


def main():
    fragment = build_fragment()
    graph, rules = base_graph_and_rules(
        prefix=PREFIX, rfe=RFE, display="Upper Respiratory Symptoms",
        intents=[
            ("intent.characterize_symptom", "Characterize Symptom"),
            ("intent.screen_red_flags", "Screen Red Flags"),
            ("intent.differentiate_common_causes", "Differentiate Common Sources"),
            ("intent.risk_assessment", "Risk Assessment"),
        ],
    )
    primary, research = build_sources()
    policy = build_completion_policy(fragment)
    for path, document in [
        ("knowledge/base/primary-care-upper-respiratory-symptoms.json", graph),
        ("rules/base/primary-care-upper-respiratory-symptoms.json", rules),
        ("knowledge/generated/upper-respiratory/upper-respiratory-symptoms.json", fragment),
        ("mappings/terminology/snomed-mrcm-upper-respiratory-symptoms.json", build_mrcm()),
        ("sources/manifests/primary-care-upper-respiratory-symptoms.json", primary),
        ("sources/manifests/primary-care-upper-respiratory-symptoms-research.json", research),
        ("policies/primary-care-upper-respiratory-symptoms-completion.json", policy),
    ]:
        write_json(path, document)
    for filename, case in build_cases(fragment).items():
        write_json(f"simulation/patients/upper-respiratory/{filename}", case)


if __name__ == "__main__":
    main()
