#!/usr/bin/env python3
"""Materialize unreviewed grouped oral and dental symptom knowledge."""
from profile_support import *

P = "oral-dental-symptoms"
RFE = "rfe.oral_dental_symptoms"
M = "mapping.snomed-mrcm.oral-dental-symptoms"
SN = "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = [
    "source.nhs-england.unscheduled-dental-care.2025",
    "source.nice.ng12.oral-cancer.2026",
    "source.nhs.dental-abscess.2026",
    "source.nhs.emergency-dentist.2025",
    "source.nhs.mouth-ulcers.2026",
    "source.nhs.knocked-out-tooth.2025",
    "source.nhs.oral-thrush.2026",
    "source.stom.oral-dental.20260715",
]
G = {k: f"group.oral-dental.{k}" for k in (
    "routing", "shared-safety", "common", "tooth-pain",
    "swelling-infection", "lesion-mucosa", "gum-periodontal", "trauma-procedure",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
D = ["intent.differentiate_common_causes"]
R = ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("oral.primary_symptom_group", "Primary Oral or Dental Symptom Group", "coded", "primary-group", "가장 불편한 문제는 치아 통증·민감함, 입안·얼굴 부종이나 감염, 구강 궤양·반점·덩이, 잇몸 문제, 외상·치과 처치 후 문제 중 무엇인가요?", 150, [G["routing"]], C, allowed_values=["tooth_pain", "swelling_infection", "lesion_mucosa", "gum_periodontal", "trauma_procedure", "other_unclear"]),

        Q("oral.difficulty_breathing_due_to_swelling", "Breathing Difficulty with Oral or Facial Swelling", "boolean", "breathing-compromise", "입안·얼굴·목이 부으면서 지금 숨쉬기 어렵나요?", 149, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.difficulty_swallowing_saliva_due_to_swelling", "Difficulty Swallowing Saliva with Swelling", "boolean", "swallowing-compromise", "입안·얼굴·목이 부으면서 침도 삼키기 어렵거나 침을 흘리나요?", 148, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "40739000"}, mrcm_ref=M),
        Q("oral.difficulty_speaking_due_to_swelling", "Difficulty Speaking with Oral Swelling", "boolean", "speaking-compromise", "입안이나 목이 부으면서 평소처럼 말하기 어렵나요?", 147, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.rapid_floor_of_mouth_tongue_or_neck_swelling", "Rapid Floor of Mouth Tongue or Neck Swelling", "boolean", "deep-spreading-swelling", "혀 아래·입바닥·목의 부기가 빠르게 커지거나 혀가 밀려 올라오는 느낌이 있나요?", 146, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.swelling_closing_eye_or_severe_eye_pain", "Oral Facial Swelling Closing Eye or Causing Severe Eye Pain", "boolean", "eye-swelling", "입안이나 얼굴의 부기가 눈 주변까지 번져 눈을 뜨기 어렵거나 눈이 심하게 아픈가요?", 145, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.new_vision_change_with_facial_swelling", "New Vision Change with Facial Swelling", "boolean", "vision-change", "얼굴이 부으면서 시야가 갑자기 흐려지거나 겹쳐 보이나요?", 144, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.severe_systemic_illness_with_infection", "Severe Systemic Illness with Oral Infection", "boolean", "severe-systemic-illness", "입안 통증이나 부기와 함께 의식이 흐리거나 심한 오한·탈진 등으로 전신 상태가 매우 나쁜가요?", 143, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.uncontrolled_heavy_bleeding", "Uncontrolled Heavy Oral Bleeding", "boolean", "uncontrolled-bleeding", "입안에서 피가 많이 나고 깨끗한 거즈로 계속 눌러도 멎지 않나요?", 142, [G["shared-safety"], G["trauma-procedure"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "249418002"}, mrcm_ref=M),
        Q("oral.serious_face_or_jaw_trauma", "Serious Face or Jaw Trauma", "boolean", "serious-trauma", "얼굴이나 턱을 심하게 다쳐 턱 모양이 변했거나 의식을 잃음·반복 구토·겹쳐 보임이 있었나요?", 141, [G["shared-safety"], G["trauma-procedure"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "397869004"}, mrcm_ref=M),
        Q("oral.permanent_tooth_completely_avulsed", "Permanent Tooth Completely Knocked Out", "boolean", "permanent-tooth-avulsion", "영구치가 외상으로 완전히 빠졌나요?", 140, [G["shared-safety"], G["trauma-procedure"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "109671008"}, mrcm_ref=M),
        Q("oral.spreading_or_rapidly_worsening_swelling", "Spreading or Rapidly Worsening Oral Facial Swelling", "boolean", "spreading-swelling", "입안·잇몸·얼굴의 부기가 퍼지거나 빠르게 심해지고 있나요?", 139, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.significant_trismus", "Significant Trismus", "boolean", "significant-trismus", "입이 잘 벌어지지 않아 손가락 두 개 정도도 넣기 어렵나요?", 138, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.severe_pain_not_controlled", "Severe Dental Pain Not Controlled by Usual Measures", "boolean", "uncontrolled-pain", "치아나 입안 통증이 매우 심하고 일반적인 진통 방법으로도 조절되지 않아 잠이나 일상이 어렵나요?", 137, [G["shared-safety"], G["tooth-pain"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "27355003"}, mrcm_ref=M),
        Q("oral.high_risk_host_with_infection", "High-risk Host with Oral Infection", "boolean", "high-risk-infection", "면역억제 치료·항암치료·조절되지 않는 당뇨가 있으면서 입안 감염이나 부기가 있나요?", 136, [G["shared-safety"], G["swelling-infection"]], S, safety_relevant=True),
        Q("oral.persistent_bleeding_after_dental_procedure", "Persistent Bleeding after Dental Procedure", "boolean", "postprocedure-bleeding", "최근 발치나 치과 처치 뒤 압박해도 출혈이 계속되거나 다시 많이 나나요?", 135, [G["shared-safety"], G["trauma-procedure"]], S, safety_relevant=True),
        Q("oral.unexplained_ulcer_over_three_weeks", "Unexplained Oral Ulcer over Three Weeks", "boolean", "ulcer-over-three-weeks", "원인이 분명하지 않은 입안 궤양이 3주 넘게 낫지 않고 있나요?", 134, [G["shared-safety"], G["lesion-mucosa"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "26284000"}, mrcm_ref=M),
        Q("oral.unexplained_lip_or_mouth_lump", "Unexplained Lip or Oral Cavity Lump", "boolean", "oral-lump", "입술이나 입안에 원인을 모르는 덩이 또는 단단해진 부위가 있나요?", 133, [G["shared-safety"], G["lesion-mucosa"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "1071000119107"}, mrcm_ref=M),
        Q("oral.persistent_red_or_red_white_patch", "Persistent Red or Red-white Oral Patch", "boolean", "red-patch", "입안에 없어지지 않는 붉은 반점 또는 붉고 흰 반점이 있나요?", 132, [G["shared-safety"], G["lesion-mucosa"]], S, safety_relevant=True),
        Q("oral.persistent_unexplained_neck_lump", "Persistent Unexplained Neck Lump", "boolean", "neck-lump", "목에 원인을 모르고 계속되는 덩이나 림프절 부기가 있나요?", 131, [G["shared-safety"], G["lesion-mucosa"]], S, safety_relevant=True),
        Q("oral.loose_tooth_or_appliance_airway_risk", "Loose Tooth or Appliance Airway Risk", "boolean", "airway-foreign-body-risk", "빠질 듯 흔들리는 치아나 깨진 보철물이 목으로 넘어갈 위험이 있나요?", 130, [G["shared-safety"], G["trauma-procedure"]], S, safety_relevant=True),

        Q("oral.symptom_duration", "Oral Dental Symptom Duration", "string", "duration", "증상은 언제 시작됐고 계속되는지 반복되는지 알려주세요.", 120, [G["common"]], C),
        Q("oral.onset_and_progression", "Oral Dental Onset and Progression", "coded", "onset-progression", "갑자기 또는 서서히 시작했고, 좋아짐·같음·악화 중 어느 쪽인가요?", 119, [G["common"]], C, allowed_values=["sudden_improving", "sudden_same", "sudden_worsening", "gradual_improving", "gradual_same", "gradual_worsening", "unclear"]),
        Q("oral.main_location", "Main Oral Dental Location", "coded", "main-location", "가장 불편한 곳은 치아, 잇몸, 혀, 입술, 볼 안쪽, 입천장, 혀 아래·입바닥, 턱·얼굴 중 어디인가요?", 118, [G["common"]], C, allowed_values=["tooth", "gum", "tongue", "lip", "buccal_mucosa", "palate", "floor_of_mouth", "jaw_face", "multiple_or_unclear"]),
        Q("oral.side_arch_and_tooth", "Oral Side Arch and Tooth", "string", "side-arch-tooth", "왼쪽·오른쪽·양쪽 중 어디이며, 위턱·아래턱과 알 수 있다면 어느 치아인지 알려주세요.", 117, [G["common"]], C),
        Q("oral.pain_score_zero_to_ten", "Oral Dental Pain Score", "integer", "pain-score", "통증을 0점부터 10점까지로 표현하면 몇 점인가요?", 116, [G["common"]], C),
        Q("oral.chewing_sleep_speech_or_intake_impact", "Oral Functional Impact", "string", "functional-impact", "씹기·수면·말하기·음식이나 물 섭취에 어느 정도 영향이 있나요?", 115, [G["common"]], R),
        Q("oral.fever_chills_or_general_unwellness", "Fever Chills or General Unwellness", "string", "fever-systemic", "열, 오한, 기운 없음 또는 몸이 아픈 느낌이 함께 있나요?", 114, [G["common"]], R),
        Q("oral.diabetes_immunosuppression_or_pregnancy", "Medical Risk Context", "string", "medical-risk", "당뇨, 면역저하·항암치료, 임신 또는 다른 중요한 질환이 있나요?", 108, [G["common"]], R),
        Q("oral.anticoagulant_or_bleeding_disorder", "Anticoagulant or Bleeding Disorder", "string", "bleeding-risk", "항응고제·항혈소판제를 복용하거나 출혈 질환이 있나요?", 107, [G["common"], G["trauma-procedure"]], R),
        Q("oral.current_medicines_allergies_and_self_treatment", "Current Medicines Allergies and Self-treatment", "string", "medicines-allergies", "현재 약·약물 알레르기와 이번 증상에 사용한 진통제·항생제·구강 제품을 알려주세요.", 106, [G["common"]], R),
        Q("oral.recent_dental_visit_procedure_or_appliance", "Recent Dental Visit Procedure or Appliance", "string", "recent-dental-care", "최근 발치·충전·신경치료·임플란트·교정 등 치과 처치나 틀니·보철 변화가 있었나요?", 105, [G["common"]], R),
        Q("oral.other_detail_or_patient_priority", "Other Oral Dental Detail or Patient Priority", "string", "other-detail", "질문에 없지만 꼭 전달하고 싶은 증상이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("oral.tooth_pain_character", "Tooth Pain Character", "coded", "tooth-pain-character", "치아 통증은 욱신거림, 날카로움, 전기처럼 찌릿함, 묵직함 중 어느 느낌에 가깝나요?", 112, [G["tooth-pain"]], C, allowed_values=["throbbing", "sharp", "electric_shock_like", "dull_pressure", "mixed_or_unclear"]),
        Q("oral.hot_cold_sweet_sensitivity", "Hot Cold or Sweet Tooth Sensitivity", "string", "temperature-sensitivity", "차갑거나 뜨겁거나 단 음식에 아프며, 자극이 사라진 뒤에도 통증이 남나요?", 111, [G["tooth-pain"]], D, terminology_binding={"system": SN, "code": "13468005"}, mrcm_ref=M),
        Q("oral.pain_on_biting_or_chewing", "Pain on Biting or Chewing", "boolean", "biting-pain", "그 치아로 씹거나 이를 맞물릴 때 더 아픈가요?", 110, [G["tooth-pain"]], D),
        Q("oral.spontaneous_or_night_waking_pain", "Spontaneous or Night-waking Tooth Pain", "boolean", "night-pain", "자극이 없어도 아프거나 밤에 통증 때문에 깨나요?", 109, [G["tooth-pain"]], D),
        Q("oral.visible_cavity_fracture_or_lost_restoration", "Visible Cavity Fracture or Lost Restoration", "string", "tooth-damage", "치아에 구멍·깨짐이 보이거나 충전재·크라운이 빠졌나요?", 104, [G["tooth-pain"]], D),
        Q("oral.pus_draining_pimple_or_bad_taste", "Pus Drainage Gum Pimple or Bad Taste", "string", "pus-bad-taste", "잇몸에서 고름이 나오거나 뾰루지 같은 부위, 나쁜 맛·냄새가 있나요?", 103, [G["tooth-pain"], G["swelling-infection"]], D, terminology_binding={"system": SN, "code": "299709002"}, mrcm_ref=M),
        Q("oral.tooth_mobility_or_bite_change", "Tooth Mobility or Bite Change", "string", "tooth-mobility", "치아가 흔들리거나 이전과 다르게 먼저 닿는 느낌이 있나요?", 102, [G["tooth-pain"], G["gum-periodontal"]], R),
        Q("oral.erupting_wisdom_tooth_or_pericoronal_symptoms", "Wisdom Tooth Eruption Context", "string", "wisdom-tooth", "맨 뒤 사랑니 주변 잇몸이 붓거나 음식이 끼고 입 벌리기 불편한가요?", 101, [G["tooth-pain"], G["gum-periodontal"]], D),
        Q("oral.jaw_joint_clenching_or_grinding_context", "Jaw Joint Clenching or Grinding Context", "string", "jaw-context", "턱관절 소리·턱 근육 통증, 이 악물기나 이갈이가 있나요?", 94, [G["tooth-pain"]], D),

        Q("oral.swelling_site_and_extent", "Oral Facial Swelling Site and Extent", "string", "swelling-site", "부기는 잇몸·볼·턱·입술·혀 아래·목 중 어디에서 어디까지 퍼져 있나요?", 113, [G["swelling-infection"]], C),
        Q("oral.swelling_speed_and_recurrence", "Swelling Speed and Recurrence", "string", "swelling-course", "부기는 언제 시작해 얼마나 빨리 커졌고 이전에도 반복됐나요?", 112, [G["swelling-infection"]], C),
        Q("oral.swelling_redness_warmth_or_pus", "Swelling Redness Warmth or Pus", "string", "swelling-character", "부은 곳이 붉거나 뜨겁고, 고름이나 분비물이 나오나요?", 111, [G["swelling-infection"]], D),
        Q("oral.mouth_opening_degree", "Mouth Opening Degree", "coded", "mouth-opening", "입 벌리기는 정상, 약간 제한, 손가락 두 개 미만, 거의 못 벌림 중 어느 정도인가요?", 110, [G["swelling-infection"]], C, allowed_values=["normal", "mildly_limited", "less_than_two_fingers", "nearly_unable", "unclear"]),
        Q("oral.swallowing_saliva_and_voice_detail", "Swallowing Saliva and Voice Detail", "string", "swallowing-voice-detail", "침과 물을 삼킬 수 있는지, 목소리가 먹먹하게 변했는지 알려주세요.", 109, [G["swelling-infection"]], C),
        Q("oral.eye_or_vision_detail", "Eye or Vision Detail with Facial Swelling", "string", "eye-detail", "눈 주변 부기·통증, 눈을 뜨기 어려움 또는 시야 변화가 있다면 자세히 알려주세요.", 108, [G["swelling-infection"]], C),
        Q("oral.prior_antibiotic_or_drainage_response", "Prior Antibiotic or Drainage Response", "string", "treatment-response", "이번 문제로 항생제나 배농 치료를 받았다면 시작일과 좋아짐·같음·악화를 알려주세요.", 100, [G["swelling-infection"]], R),

        Q("oral.lesion_type", "Oral Lesion Type", "coded", "lesion-type", "병변은 궤양, 흰 반점, 붉은 반점, 붉고 흰 반점, 덩이, 물집, 닦이는 흰 막 중 무엇인가요?", 113, [G["lesion-mucosa"]], C, allowed_values=["ulcer", "white_patch", "red_patch", "red_white_patch", "lump_or_induration", "vesicle", "wipeable_white_coating", "other_unclear"], terminology_binding={"system": SN, "code": "1071000119107"}, mrcm_ref=M),
        Q("oral.lesion_site_number_and_size", "Oral Lesion Site Number and Size", "string", "lesion-site-size", "입안의 정확한 위치와 개수, 대략적인 크기를 알려주세요.", 112, [G["lesion-mucosa"]], C),
        Q("oral.lesion_color_surface_and_border", "Oral Lesion Color Surface and Border", "string", "lesion-appearance", "색, 표면이 매끈한지 거친지, 가장자리 모양과 단단함을 설명해주세요.", 111, [G["lesion-mucosa"]], C),
        Q("oral.lesion_recurrence_and_healing_pattern", "Oral Lesion Recurrence and Healing Pattern", "string", "lesion-recurrence", "처음인지 반복되는지, 이전 병변은 완전히 나았다가 다시 생겼는지 알려주세요.", 110, [G["lesion-mucosa"]], C),
        Q("oral.lesion_pain_bleeding_or_induration", "Oral Lesion Pain Bleeding or Induration", "string", "lesion-symptoms", "병변이 아프거나 쉽게 피가 나거나 만졌을 때 단단한가요?", 109, [G["lesion-mucosa"]], R),
        Q("oral.local_trauma_denture_or_sharp_tooth", "Local Trauma Denture or Sharp Tooth", "string", "local-irritation", "볼·혀를 깨물었거나 날카로운 치아, 틀니·교정장치가 계속 닿았나요?", 103, [G["lesion-mucosa"]], D),
        Q("oral.extraoral_ulcers_rash_eye_or_genital_symptoms", "Extraoral Ulcers Rash Eye or Genital Symptoms", "string", "extraoral-symptoms", "피부·눈·생식기 등 다른 부위에도 궤양·발진·염증이 있나요?", 102, [G["lesion-mucosa"]], R),
        Q("oral.weight_loss_hoarseness_or_persistent_swallowing_problem", "Weight Loss Hoarseness or Persistent Swallowing Problem", "string", "associated-warning", "원치 않는 체중 감소, 계속되는 쉰 목소리 또는 삼킴 어려움이 있나요?", 101, [G["lesion-mucosa"]], R),
        Q("oral.tobacco_alcohol_or_betel_exposure", "Tobacco Alcohol or Betel Exposure", "string", "exposure-risk", "흡연·씹는 담배·전자담배, 음주 또는 빈랑 사용 정도를 알려주세요.", 99, [G["lesion-mucosa"], G["gum-periodontal"]], R),
        Q("oral.thrush_or_ulcer_risk_context", "Thrush or Ulcer Risk Context", "string", "mucosal-risk", "최근 항생제·흡입 스테로이드, 구강건조, 틀니, 영양 문제 또는 면역저하가 있나요?", 98, [G["lesion-mucosa"]], R),

        Q("oral.gum_bleeding_pattern", "Gum Bleeding Pattern", "coded", "gum-bleeding", "잇몸 출혈은 칫솔질 때만, 저절로, 오래 지속됨, 거의 없음 중 무엇인가요?", 113, [G["gum-periodontal"]], C, allowed_values=["brushing_only", "spontaneous", "prolonged", "none", "unclear"], terminology_binding={"system": SN, "code": "86276007"}, mrcm_ref=M),
        Q("oral.gum_swelling_tenderness_or_recession", "Gum Swelling Tenderness or Recession", "string", "gum-condition", "잇몸이 붓고 아프거나 내려가 치아 뿌리가 보이나요?", 112, [G["gum-periodontal"]], C),
        Q("oral.loose_teeth_pus_or_halitosis", "Loose Teeth Pus or Halitosis", "string", "periodontal-features", "치아 흔들림, 잇몸 고름 또는 계속되는 입 냄새가 있나요?", 111, [G["gum-periodontal"]], R),
        Q("oral.brushing_interdental_and_dental_review", "Oral Hygiene and Dental Review", "string", "oral-hygiene", "칫솔질·치실이나 치간칫솔 사용과 마지막 치과 검진 시기를 알려주세요.", 100, [G["gum-periodontal"]], R),
        Q("oral.periodontal_risk_context", "Periodontal Risk Context", "string", "periodontal-risk", "흡연, 당뇨, 임신·호르몬 변화 또는 관련 약 복용이 있나요?", 99, [G["gum-periodontal"]], R),

        Q("oral.trauma_or_procedure_time_and_mechanism", "Dental Trauma or Procedure Time and Mechanism", "string", "trauma-time", "언제 어떤 사고나 치과 처치 뒤 문제가 생겼나요?", 113, [G["trauma-procedure"]], C),
        Q("oral.primary_or_permanent_tooth", "Primary or Permanent Tooth", "coded", "tooth-type", "다친 치아는 유치, 영구치, 잘 모르겠음 중 무엇인가요?", 112, [G["trauma-procedure"]], R, allowed_values=["primary", "permanent", "unclear"]),
        Q("oral.trauma_injury_type", "Dental Trauma Injury Type", "coded", "injury-type", "치아는 깨짐, 흔들림, 위치 이동, 부분적으로 빠짐, 완전히 빠짐 중 어떤 상태인가요?", 111, [G["trauma-procedure"]], C, allowed_values=["fractured", "loose", "displaced", "partially_avulsed", "completely_avulsed", "soft_tissue_only", "unclear"]),
        Q("oral.avulsed_tooth_handling_and_storage", "Avulsed Tooth Handling and Storage", "string", "tooth-storage", "빠진 치아를 찾았는지, 뿌리를 만지거나 씻었는지, 다시 넣었는지 또는 무엇에 보관 중인지 알려주세요.", 110, [G["trauma-procedure"]], R),
        Q("oral.jaw_bite_alignment_or_mobility", "Jaw Bite Alignment or Mobility", "string", "jaw-alignment", "이를 물었을 때 맞물림이 달라졌거나 턱이 움직이지 않거나 비정상적으로 움직이나요?", 109, [G["trauma-procedure"]], R),
        Q("oral.trauma_bleeding_cut_or_missing_fragment", "Trauma Bleeding Cut or Missing Fragment", "string", "trauma-soft-tissue", "입술·혀·잇몸 상처와 출혈, 찾지 못한 치아 조각이나 보철물이 있나요?", 108, [G["trauma-procedure"]], R),
    ]

    rules = [
        safety_rule(P, "breathing-compromise", {"fact": "oral.difficulty_breathing_due_to_swelling", "equals": True}, "emergency", 1000),
        safety_rule(P, "swallowing-compromise", {"fact": "oral.difficulty_swallowing_saliva_due_to_swelling", "equals": True}, "emergency", 1000),
        safety_rule(P, "speaking-compromise", {"fact": "oral.difficulty_speaking_due_to_swelling", "equals": True}, "emergency", 1000),
        safety_rule(P, "deep-spreading-swelling", {"fact": "oral.rapid_floor_of_mouth_tongue_or_neck_swelling", "equals": True}, "emergency", 1000),
        safety_rule(P, "eye-swelling", {"fact": "oral.swelling_closing_eye_or_severe_eye_pain", "equals": True}, "emergency", 1000),
        safety_rule(P, "vision-change", {"fact": "oral.new_vision_change_with_facial_swelling", "equals": True}, "emergency", 1000),
        safety_rule(P, "severe-systemic-illness", {"fact": "oral.severe_systemic_illness_with_infection", "equals": True}, "emergency", 1000),
        safety_rule(P, "uncontrolled-bleeding", {"fact": "oral.uncontrolled_heavy_bleeding", "equals": True}, "emergency", 1000),
        safety_rule(P, "serious-trauma", {"fact": "oral.serious_face_or_jaw_trauma", "equals": True}, "emergency", 1000),
        safety_rule(P, "permanent-tooth-avulsion", {"fact": "oral.permanent_tooth_completely_avulsed", "equals": True}, "urgent", 980),
        safety_rule(P, "spreading-swelling", {"fact": "oral.spreading_or_rapidly_worsening_swelling", "equals": True}, "urgent", 960),
        safety_rule(P, "significant-trismus", {"fact": "oral.significant_trismus", "equals": True}, "urgent", 950),
        safety_rule(P, "uncontrolled-pain", {"fact": "oral.severe_pain_not_controlled", "equals": True}, "urgent", 940),
        safety_rule(P, "high-risk-infection", {"fact": "oral.high_risk_host_with_infection", "equals": True}, "urgent", 940),
        safety_rule(P, "postprocedure-bleeding", {"fact": "oral.persistent_bleeding_after_dental_procedure", "equals": True}, "urgent", 940),
        safety_rule(P, "ulcer-over-three-weeks", {"fact": "oral.unexplained_ulcer_over_three_weeks", "equals": True}, "urgent", 920),
        safety_rule(P, "oral-lump", {"fact": "oral.unexplained_lip_or_mouth_lump", "equals": True}, "urgent", 920),
        safety_rule(P, "red-patch", {"fact": "oral.persistent_red_or_red_white_patch", "equals": True}, "urgent", 920),
        safety_rule(P, "neck-lump", {"fact": "oral.persistent_unexplained_neck_lump", "equals": True}, "urgent", 920),
        safety_rule(P, "airway-foreign-body-risk", {"fact": "oral.loose_tooth_or_appliance_airway_risk", "equals": True}, "urgent", 930),
    ]
    return {
        "id": "knowledge.generated.oral-dental-symptoms", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-oral-dental-symptoms-research",
        "default_refresh": default_refresh(),
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": e,
        "provenance": provenance(SOURCES),
    }


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="oral.primary_symptom_group", question_budget=58, source_refs=SOURCES)
    branches = {
        "tooth_pain": ["oral.tooth_pain_character", "oral.hot_cold_sweet_sensitivity", "oral.pain_on_biting_or_chewing", "oral.spontaneous_or_night_waking_pain", "oral.visible_cavity_fracture_or_lost_restoration", "oral.pus_draining_pimple_or_bad_taste", "oral.tooth_mobility_or_bite_change", "oral.erupting_wisdom_tooth_or_pericoronal_symptoms", "oral.jaw_joint_clenching_or_grinding_context"],
        "swelling_infection": ["oral.swelling_site_and_extent", "oral.swelling_speed_and_recurrence", "oral.swelling_redness_warmth_or_pus", "oral.mouth_opening_degree", "oral.swallowing_saliva_and_voice_detail", "oral.eye_or_vision_detail", "oral.prior_antibiotic_or_drainage_response"],
        "lesion_mucosa": ["oral.lesion_type", "oral.lesion_site_number_and_size", "oral.lesion_color_surface_and_border", "oral.lesion_recurrence_and_healing_pattern", "oral.lesion_pain_bleeding_or_induration", "oral.local_trauma_denture_or_sharp_tooth", "oral.extraoral_ulcers_rash_eye_or_genital_symptoms", "oral.weight_loss_hoarseness_or_persistent_swallowing_problem", "oral.tobacco_alcohol_or_betel_exposure", "oral.thrush_or_ulcer_risk_context"],
        "gum_periodontal": ["oral.gum_bleeding_pattern", "oral.gum_swelling_tenderness_or_recession", "oral.loose_teeth_pus_or_halitosis", "oral.brushing_interdental_and_dental_review", "oral.periodontal_risk_context"],
        "trauma_procedure": ["oral.trauma_or_procedure_time_and_mechanism", "oral.primary_or_permanent_tooth", "oral.trauma_injury_type", "oral.avulsed_tooth_handling_and_storage", "oral.jaw_bite_alignment_or_mobility", "oral.trauma_bleeding_cut_or_missing_fragment"],
        "other_unclear": ["oral.other_detail_or_patient_priority"],
    }
    conditional = {fact_id for facts in branches.values() for fact_id in facts}
    policy["required_facts"]["routine"] = [
        "oral.symptom_duration", "oral.main_location", "oral.pain_score_zero_to_ten",
        "oral.chewing_sleep_speech_or_intake_impact",
        "oral.fever_chills_or_general_unwellness",
        "oral.diabetes_immunosuppression_or_pregnancy",
        "oral.other_detail_or_patient_priority",
    ]
    policy["conditional_required_facts"] = [{"selector_fact": "oral.primary_symptom_group", "cases": branches}]
    return policy


def source_docs():
    defs = [
        ("source.nhs-england.unscheduled-dental-care.2025", "NHS England", "Clinical guidance: unscheduled urgent and non-urgent dental care", "published-2025-05-01; updated-2025-10-03", "https://www.england.nhs.uk/long-read/clinical-guidance-unscheduled-urgent-and-non-urgent-dental-care/", "clinical_guideline", 1, ["Emergency dental triage includes spreading oro-facial swelling with airway risk, severe systemic illness, uncontrolled intra-oral bleeding, oro-facial fracture and avulsed permanent teeth.", "Urgent assessment includes spreading infection without airway compromise, severe uncontrolled pain, dentoalveolar injury, significant trismus and severe gingival or mucosal conditions."]),
        ("source.nice.ng12.oral-cancer.2026", "NICE", "Suspected cancer: recognition and referral — oral cancer", "NG12; updated-2026-04-15", "https://www.nice.org.uk/guidance/ng12/chapter/Recommendations-organised-by-site-of-cancer", "nice_guidance", 7, ["Unexplained oral ulceration lasting more than three weeks or a persistent unexplained neck lump warrants a suspected cancer pathway consideration.", "A lip or oral-cavity lump and red or red-white oral patch warrant urgent dental assessment; these findings do not establish cancer."]),
        ("source.nhs.dental-abscess.2026", "NHS", "Dental abscess", "accessed-2026-07-15", "https://www.nhs.uk/conditions/dental-abscess/", "public_health_guidance", 7, ["Dental abscess features may include intense tooth or gum pain, facial or jaw swelling, hot-cold sensitivity, bad taste, restricted mouth opening and fever.", "Difficulty breathing, speaking or swallowing, extensive mouth swelling, marked trismus, or eye pain and visual change require emergency assessment."]),
        ("source.nhs.emergency-dentist.2025", "NHS", "How to find an emergency or urgent NHS dentist appointment", "reviewed-2025-05-14", "https://www.nhs.uk/nhs-services/dentists/how-to-find-an-nhs-dentist-in-an-emergency/", "public_health_guidance", 7, ["Heavy oral bleeding that will not stop, serious face or jaw injury, or severe oral, lip, throat or neck swelling with breathing or eye-opening difficulty requires emergency care.", "Knocked-out teeth, persistent severe pain, enlarging or persistent oral swelling, lumps or patches, and post-extraction bleeding require urgent dental assessment."]),
        ("source.nhs.mouth-ulcers.2026", "NHS", "Mouth ulcers", "accessed-2026-07-15", "https://www.nhs.uk/conditions/mouth-ulcers/", "public_health_guidance", 7, ["Most common mouth ulcers resolve within one or two weeks.", "An ulcer lasting longer than three weeks, differing from prior ulcers, bleeding, or becoming more painful and red should be assessed by a dentist or clinician."]),
        ("source.nhs.knocked-out-tooth.2025", "NHS", "Knocked-out tooth", "accessed-2026-07-15", "https://www.nhs.uk/conditions/knocked-out-tooth/", "public_health_guidance", 7, ["A knocked-out permanent tooth requires immediate emergency dental assessment; a primary tooth should not be replanted.", "Handling and storage context affects the handoff, but the interview does not perform or guarantee reimplantation."]),
        ("source.nhs.oral-thrush.2026", "NHS", "Oral thrush", "accessed-2026-07-15", "https://www.nhs.uk/conditions/oral-thrush-mouth-thrush/", "public_health_guidance", 7, ["Wipeable white oral plaques, oral soreness and altered taste can inform mucosal assessment.", "Antibiotics, inhaled corticosteroids, dentures, dry mouth, diabetes, cancer treatment and immune suppression are relevant contexts without establishing a diagnosis."]),
        ("source.stom.oral-dental.20260715", "Infoclinic", "STOM oral and dental terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", 30, ["STOM confirmed active candidates for toothache, mouth ulcer, oral lesion, bleeding gums, dental abscess, dysphagia, complete tooth avulsion, dental trauma, oral mucosal bleeding and sensitive dentin.", "Finding site and Severity were returned as allowed MRCM attributes for the selected active focus concepts; MRCM does not control clinical rules or urgency."]),
    ]
    artifacts = []
    for identifier, publisher, title, version, url, profile, days, assertions in defs:
        artifacts.append({
            "id": identifier,
            "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata",
            "publisher": publisher, "title": title, "version": version, "url": url,
            "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached",
            "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown",
            "complete": False, "monitor_profile": profile, "monitor_interval_days": days,
            "last_monitored_at": "2026-07-15",
            "next_monitor_at": "2026-08-14" if days == 30 else ("2026-07-22" if days == 7 else "2026-07-16"),
            "monitor_result": "current_official_source_confirmed", "assertions": assertions,
        })
    research = {"id": "source-manifest.primary-care-oral-dental-symptoms-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([item[0] for item in defs])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.oral-dental", "generated_clinical_knowledge", "knowledge/generated/oral-dental/oral-dental-symptoms/oral-dental-symptoms.json", True),
        ("source.mapping.oral-dental", "terminology_mapping", "mappings/terminology/snomed-mrcm-oral-dental-symptoms.json", False),
        ("source.external.oral-dental", "external_source_manifest", "sources/manifests/primary-care-oral-dental-symptoms-research.json", False),
        ("source.policy.oral-dental", "runtime_policy", "policies/primary-care-oral-dental-symptoms-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-oral-dental-symptoms", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": identifier, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for identifier, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}

    def satisfy(condition, hidden):
        if "all" in condition:
            for child in condition["all"]:
                satisfy(child, hidden)
        elif "equals" in condition:
            hidden[condition["fact"]] = {"value": condition["equals"]}
        elif "in" in condition:
            hidden[condition["fact"]] = {"value": condition["in"][0]}

    for index, rule in enumerate(f["safety_rules"]):
        hidden = {}
        satisfy(rule["when"], hidden)
        key = rule["id"].split("safety.")[1]
        level = rule["then"]["safety_level"]
        out[f"ORAL-{key.upper()}.json"] = {
            "id": f"ORAL-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 20 + index},
            "initial_statement": {"ko": "치아나 입안 문제로 왔어요."},
            "hidden_state": hidden,
            "expected": {
                "expected_safety_level": level, "expected_safety_action": "human_handoff",
                "expected_stop_reason": f"{level}_escalation",
                "expected_triggered_rules_contains": [rule["id"]],
                "expected_max_turns": 45,
                "forbidden_assertions": ["diagnosis.dental_abscess", "diagnosis.oral_cancer", "recommendation.prescribe_antibiotic"],
            },
            "provenance": provenance(SOURCES),
        }

    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["lesion_mucosa"])
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}
    hidden = {}
    for fact_id in required:
        fact_def = by_id[fact_id]
        if fact_def["value_type"] == "boolean":
            hidden[fact_id] = {"value": False}
        elif fact_def["value_type"] == "coded":
            hidden[fact_id] = {"value": fact_def.get("allowed_values", ["unclear"])[-1]}
        elif fact_def["value_type"] == "integer":
            hidden[fact_id] = {"value": 2}
        else:
            hidden[fact_id] = {"value": "없음"}
    hidden["oral.primary_symptom_group"] = {"value": "lesion_mucosa"}
    hidden["oral.lesion_type"] = {"value": "ulcer"}
    declined = "oral.thrush_or_ulcer_risk_context"
    hidden.pop(declined)
    out["ORAL-LESION-DATA-ABSENT.json"] = {
        "id": "ORAL-LESION-DATA-ABSENT", "simulation_language": "ko",
        "persona": {"age": 38}, "initial_statement": {"ko": "입안에 작은 궤양이 생겼어요."},
        "hidden_state": hidden,
        "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}},
        "expected": {
            "expected_data_absent_reasons": {declined: "asked-declined"},
            "expected_safety_level": "routine",
            "expected_stop_reason": "required_targets_addressed_with_absent_data",
            "expected_max_turns": 65,
            "forbidden_assertions": ["diagnosis.aphthous_ulcer", "diagnosis.oral_cancer"],
        },
        "provenance": provenance(["source.nhs.mouth-ulcers.2026", "specifications/clinical-memory.md"]),
    }
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Oral and Dental Symptoms", intents=[
        ("intent.characterize_symptom", "Characterize Symptom"),
        ("intent.screen_red_flags", "Screen Red Flags"),
        ("intent.differentiate_common_causes", "Differentiate Common Sources"),
        ("intent.risk_assessment", "Risk Assessment"),
    ])
    primary, research = source_docs()
    concepts = [
        ("27355003", "Toothache (finding)", 20),
        ("26284000", "Ulcer of mouth (disorder)", 22),
        ("1071000119107", "Oral lesion (disorder)", 22),
        ("86276007", "Bleeding gums (finding)", 20),
        ("299709002", "Dental abscess (disorder)", 22),
        ("40739000", "Dysphagia (disorder)", 22),
        ("109671008", "Complete avulsion of tooth (disorder)", 22),
        ("397869004", "Dental trauma (disorder)", 22),
        ("249418002", "Bleeding of oral mucosa (finding)", 20),
        ("13468005", "Sensitive dentin (disorder)", 22),
    ]
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": [{"code": code, "display": display, "concept_active": True, "attribute_count_returned": count} for code, display, count in concepts],
        "verified_attribute_ids": ["363698007", "246112005"],
        "laterality": {"reference_set": "723264001", "postcoordination_asserted": False, "reason": "Oral side, arch and tooth remain separate Facts until the selected anatomical structure is individually verified as lateralizable and normal-form compatible."},
        "validation": {"method": "build_time_live_mapping_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "provenance": provenance(["source.stom.oral-dental.20260715"]),
    }
    documents = [
        ("knowledge/base/primary-care-oral-dental-symptoms.json", graph),
        ("rules/base/primary-care-oral-dental-symptoms.json", rules),
        ("knowledge/generated/oral-dental/oral-dental-symptoms/oral-dental-symptoms.json", f),
        ("mappings/terminology/snomed-mrcm-oral-dental-symptoms.json", mapping),
        ("sources/manifests/primary-care-oral-dental-symptoms.json", primary),
        ("sources/manifests/primary-care-oral-dental-symptoms-research.json", research),
        ("policies/primary-care-oral-dental-symptoms-completion.json", completion(f)),
    ]
    for path, document in documents:
        write_json(path, document)
    for name, case in cases(f).items():
        write_json("simulation/patients/oral-dental/oral-dental-symptoms/" + name, case)


if __name__ == "__main__":
    main()
