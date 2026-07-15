#!/usr/bin/env python3
"""Materialize unreviewed pregnancy and postpartum concern knowledge."""
from profile_support import *

P = "pregnancy-postpartum-concern"
RFE = "rfe.pregnancy_postpartum_concern"
M = "mapping.snomed-mrcm.pregnancy-postpartum-concern"
SN = "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-15T00:00:00Z"
SOURCES = [
    "source.nice.ng126.early-pregnancy.2026", "source.nice.ng133.hypertension-pregnancy.2023",
    "source.nice.ng194.postnatal-care.2021", "source.nice.cg192.perinatal-mental-health.2025",
    "source.nhs.pregnancy-urgent-symptoms.2026", "source.nhs.fetal-movements.2024",
    "source.nhs.labour-signs.2026", "source.nhs.postpartum-body.2024",
    "source.nice.ng201.antenatal-history.2021", "source.acog.revitalize-obstetric-definitions.2026",
    "source.stom.pregnancy-postpartum.20260715",
]
G = {k: f"group.pregnancy.{k}" for k in (
    "routing", "shared-safety", "common", "early-pain-bleeding", "later-fetal-labour",
    "maternal-medical", "postpartum-physical", "mental-feeding",
)}
C, S = ["intent.characterize_symptom"], ["intent.screen_red_flags"]
D, R = ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("pregnancy.primary_concern_group", "Primary Pregnancy or Postpartum Concern Group", "coded", "primary-group", "가장 걱정되는 문제는 임신 초기 통증·출혈, 임신 후기 태동·양수·진통, 임신 중 전신 증상, 산후 신체 회복, 산후 정신건강·수유 중 무엇인가요?", 170, [G["routing"]], C, allowed_values=["early_pain_bleeding", "later_fetal_labour", "maternal_medical", "postpartum_physical", "mental_feeding", "other_unclear"]),

        Q("pregnancy.hemodynamic_instability_or_collapse", "Collapse or Shock with Pregnancy Concern", "boolean", "collapse", "심한 어지럼·실신, 창백함, 식은땀, 빠른 맥박 또는 의식 저하가 있나요?", 169, [G["shared-safety"]], S, safety_relevant=True),
        Q("pregnancy.heavy_vaginal_bleeding", "Heavy Vaginal Bleeding", "boolean", "heavy-bleeding", "생리대가 빠르게 흠뻑 젖을 정도로 피가 많이 나거나 큰 혈괴가 계속 나오나요?", 168, [G["shared-safety"], G["early-pain-bleeding"], G["later-fetal-labour"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "16320551000119109"}, mrcm_ref=M),
        Q("pregnancy.severe_unilateral_pain_or_shoulder_tip_pain", "Severe Unilateral or Shoulder-tip Pain", "boolean", "ectopic-warning", "임신 가능성이 있으면서 한쪽 아랫배가 심하게 아프거나 어깨 끝 통증·실신 느낌이 있나요?", 167, [G["shared-safety"], G["early-pain-bleeding"]], S, safety_relevant=True),
        Q("pregnancy.severe_constant_abdominal_pain", "Severe Constant Abdominal Pain", "boolean", "severe-abdominal-pain", "배가 지속적으로 매우 아프거나 딱딱하게 긴장되고 쉬어도 낫지 않나요?", 166, [G["shared-safety"]], S, safety_relevant=True),
        Q("pregnancy.chest_pain_sudden_dyspnea_or_hemoptysis", "Possible Pulmonary Embolism Symptoms", "boolean", "chest-dyspnea", "갑작스러운 숨참, 가슴 통증, 실신 또는 피 섞인 기침이 있나요?", 165, [G["shared-safety"], G["maternal-medical"], G["postpartum-physical"]], S, safety_relevant=True),
        Q("pregnancy.unilateral_leg_swelling_pain_redness", "Unilateral Leg Thrombosis Features", "boolean", "leg-thrombosis", "한쪽 종아리나 다리만 붓고 아프거나 붉고 뜨거운가요?", 164, [G["shared-safety"], G["maternal-medical"], G["postpartum-physical"]], S, safety_relevant=True),
        Q("pregnancy.severe_headache_vision_or_upper_abdominal_pain", "Pre-eclampsia Warning Symptoms", "boolean", "preeclampsia-warning", "심한 두통, 시야 흐림·번쩍임, 명치나 오른쪽 윗배의 심한 통증이 있나요?", 163, [G["shared-safety"], G["maternal-medical"], G["postpartum-physical"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "398254007"}, mrcm_ref=M),
        Q("pregnancy.seizure_or_reduced_consciousness", "Seizure or Reduced Consciousness", "boolean", "seizure-consciousness", "경련했거나 깨우기 어렵고 의식이 흐린가요?", 162, [G["shared-safety"]], S, safety_relevant=True),
        Q("pregnancy.severe_hypertension_measured", "Severe Hypertension Measurement", "boolean", "severe-hypertension", "최근 혈압이 160/110 mmHg 이상으로 측정됐거나 의료진이 중증 고혈압이라고 했나요?", 161, [G["shared-safety"], G["maternal-medical"], G["postpartum-physical"]], S, safety_relevant=True),
        Q("pregnancy.reduced_or_absent_fetal_movement", "Reduced or Absent Fetal Movement", "boolean", "reduced-fetal-movement", "평소 느끼던 태동이 줄었거나 전혀 느껴지지 않나요?", 160, [G["shared-safety"], G["later-fetal-labour"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "276369006"}, mrcm_ref=M),
        Q("pregnancy.later_pregnancy_vaginal_bleeding", "Vaginal Bleeding in Later Pregnancy", "boolean", "later-bleeding", "임신 중기·후기에 선홍색 질출혈이 있나요?", 159, [G["shared-safety"], G["later-fetal-labour"]], S, safety_relevant=True),
        Q("pregnancy.prolapsed_cord_or_part_visible", "Possible Cord or Fetal Part Prolapse", "boolean", "cord-prolapse", "물이 터진 뒤 질 입구로 탯줄 같은 끈이나 아기 일부가 보이거나 만져지나요?", 158, [G["shared-safety"], G["later-fetal-labour"]], S, safety_relevant=True),
        Q("pregnancy.preterm_labour_or_membrane_rupture", "Possible Preterm Labour or Membrane Rupture", "boolean", "preterm-labour", "37주 미만인데 규칙적 진통이 있거나 물 같은 액체가 계속 흐르나요?", 157, [G["shared-safety"], G["later-fetal-labour"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "371380006"}, mrcm_ref=M),
        Q("pregnancy.imminent_birth_urge_to_push", "Possible Imminent Birth", "boolean", "imminent-birth", "진통이 매우 잦고 강하면서 아래로 밀리는 느낌이나 힘주고 싶은 충동, 아기 머리가 보이는 느낌이 있나요?", 156, [G["shared-safety"], G["later-fetal-labour"]], S, safety_relevant=True),
        Q("pregnancy.fever_rigors_or_severe_systemic_illness", "Severe Infection or Sepsis Features", "boolean", "severe-infection", "고열·심한 오한·혼란·숨참 또는 매우 심한 처짐이 있나요?", 155, [G["shared-safety"], G["maternal-medical"], G["postpartum-physical"]], S, safety_relevant=True),
        Q("pregnancy.persistent_vomiting_dehydration", "Persistent Vomiting with Dehydration", "boolean", "vomiting-dehydration", "계속 토해 물도 못 마시고 소변이 매우 줄거나 심하게 어지러운가요?", 154, [G["shared-safety"], G["maternal-medical"]], S, safety_relevant=True),
        Q("postpartum.sudden_or_very_heavy_bleeding", "Sudden or Very Heavy Postpartum Bleeding", "boolean", "postpartum-hemorrhage", "출산 후 갑자기 피가 매우 많이 나거나 어지럽고 심장이 빨리 뛰나요?", 153, [G["shared-safety"], G["postpartum-physical"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "47821001"}, mrcm_ref=M),
        Q("postpartum.foul_discharge_fever_or_worsening_pelvic_pain", "Postpartum Uterine Infection Features", "boolean", "postpartum-infection", "산후 악취 나는 분비물, 발열·오한 또는 심해지는 아랫배·골반 통증이 있나요?", 152, [G["shared-safety"], G["postpartum-physical"]], S, safety_relevant=True),
        Q("postpartum.wound_breakdown_or_spreading_infection", "Postpartum Wound Breakdown or Infection", "boolean", "postpartum-wound", "제왕절개나 회음부 상처가 벌어지거나 붉은 기운·고름·통증이 빠르게 심해지나요?", 151, [G["shared-safety"], G["postpartum-physical"]], S, safety_relevant=True),
        Q("postpartum.breast_inflammation_with_systemic_illness", "Severe Breast Inflammation", "boolean", "mastitis-systemic", "유방이 붉고 뜨겁고 아프면서 고열·오한 또는 심한 전신 쇠약이 있나요?", 150, [G["shared-safety"], G["mental-feeding"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "266579006"}, mrcm_ref=M),
        Q("postpartum.self_harm_or_harm_to_baby", "Immediate Self-harm or Baby-harm Risk", "boolean", "self-baby-harm", "지금 자신이나 아기를 해칠 생각·계획이 있거나 안전을 지키기 어렵나요?", 149, [G["shared-safety"], G["mental-feeding"]], S, safety_relevant=True),
        Q("postpartum.psychosis_or_mania", "Possible Postpartum Psychosis or Mania", "boolean", "postpartum-psychosis", "출산 후 갑자기 심한 혼란·환각·망상, 거의 자지 않아도 과도하게 들뜸 또는 비정상적 행동이 생겼나요?", 148, [G["shared-safety"], G["mental-feeding"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "18260003"}, mrcm_ref=M),
        Q("pregnancy.domestic_abuse_or_safeguarding_concern", "Pregnancy or Postpartum Safeguarding Concern", "boolean", "safeguarding", "폭력·강압·성적 또는 금전적 통제, 안전하지 않은 집이나 돌봄 환경이 걱정되나요?", 147, [G["shared-safety"]], S, safety_relevant=True),

        Q("pregnancy.stage", "Pregnancy or Postpartum Stage", "coded", "stage", "현재 임신 가능성 있음, 임신 확인됨, 출산 후, 최근 유산·임신 종료 후, 잘 모름 중 어디에 해당하나요?", 140, [G["common"]], C, allowed_values=["possible_pregnancy", "confirmed_pregnancy", "postpartum", "recent_pregnancy_loss_or_end", "unclear"], terminology_binding={"system": SN, "code": "77386006"}, mrcm_ref=M),
        Q("pregnancy.gestational_age_or_postpartum_day", "Gestational Age or Postpartum Interval", "string", "timing", "임신 몇 주인지 또는 출산·유산·임신 종료 후 며칠이나 몇 주인지 알려주세요.", 139, [G["common"]], C),
        Q("pregnancy.main_symptom_duration_and_progression", "Main Symptom Duration and Progression", "string", "duration", "주된 증상은 언제 시작했고 좋아짐·같음·악화 중 어느 쪽인가요?", 138, [G["common"]], C),
        Q("pregnancy.prior_pregnancies_and_outcomes", "Prior Pregnancy and Outcome History", "string", "obstetric-history", "알고 있다면 의료기록에 적힌 산과력 표기(G/P 또는 GTPAL)와 각 임신의 연도·임신 주수·결과를 알려주세요.", 136, [G["common"]], R),
        Q("pregnancy.obstetric_gravidity_total", "Gravidity", "integer", "gravidity", "현재 임신을 포함해 지금까지 임신한 총횟수(G)는 몇 회인가요?", 135, [G["common"]], R),
        Q("pregnancy.obstetric_parity_total", "Parity", "integer", "parity", "의료기관에서 G/P 형식으로 기록한 출산력(P)은 몇 회인가요?", 134, [G["common"]], R),
        Q("pregnancy.obstetric_parity_threshold_as_recorded", "Parity Gestational Threshold as Recorded", "string", "parity-threshold", "출산력(P) 계산에 적용한 기준 임신 주수나 기관 기준을 알고 있나요? 모르면 모름이라고 답해주세요.", 134, [G["common"]], R),
        Q("pregnancy.obstetric_term_birth_count", "Term Birth Count", "integer", "term-births", "만삭 분만 횟수(T)는 몇 회인가요?", 133, [G["common"]], R),
        Q("pregnancy.obstetric_preterm_birth_count", "Preterm Birth Count", "integer", "preterm-births", "GTPAL에서 조산에 해당하는 횟수(P)는 몇 회인가요?", 133, [G["common"]], R),
        Q("pregnancy.obstetric_spontaneous_loss_count", "Spontaneous Pregnancy Loss Count", "integer", "spontaneous-losses", "자연유산 횟수는 몇 회인가요?", 132, [G["common"]], R),
        Q("pregnancy.obstetric_induced_termination_count", "Induced Termination Count", "integer", "induced-terminations", "인공임신중절 또는 의학적 임신종결 횟수는 몇 회인가요?", 132, [G["common"]], R),
        Q("pregnancy.obstetric_ectopic_count", "Ectopic Pregnancy Count", "integer", "ectopic-count", "자궁외임신 횟수는 몇 회인가요?", 132, [G["common"]], R),
        Q("pregnancy.obstetric_molar_pregnancy_count", "Molar Pregnancy Count", "integer", "molar-count", "포상기태 임신 횟수는 몇 회인가요?", 131, [G["common"]], R),
        Q("pregnancy.obstetric_living_children_count", "Living Children Count", "integer", "living-children", "현재 생존한 자녀 수(L)는 몇 명인가요?", 131, [G["common"]], R),
        Q("pregnancy.prior_multiple_gestation_history", "Prior Multiple Gestation History", "string", "multiple-gestation-history", "쌍태아 이상 다태임신 병력이 있다면 임신 결과를 알려주세요.", 130, [G["common"]], R),
        Q("pregnancy.prior_delivery_modes_and_caesarean_count", "Prior Delivery Modes and Caesarean Count", "string", "prior-delivery-modes", "이전 분만별로 자연분만·흡입/겸자분만·제왕절개 여부와 제왕절개 횟수를 알려주세요.", 130, [G["common"]], R),
        Q("pregnancy.prior_obstetric_complications", "Prior Obstetric Complications", "string", "prior-obstetric-complications", "이전 임신에서 임신성 고혈압·전자간증, 임신성 당뇨, 조산, 태반 문제, 산후출혈 또는 혈전이 있었나요?", 130, [G["common"]], R),
        Q("pregnancy.prior_fetal_neonatal_outcomes", "Prior Fetal and Neonatal Outcomes", "string", "prior-fetal-neonatal-outcomes", "이전 임신에서 사산, 신생아 사망, 선천성 질환 또는 신생아중환자실 치료가 있었나요?", 130, [G["common"]], R),
        Q("pregnancy.estimated_due_date_and_dating_method", "Estimated Due Date and Dating Method", "string", "due-date-dating", "분만예정일과 산정 방법(마지막 생리, 초기 초음파 또는 보조생식 날짜)을 알려주세요.", 137, [G["common"]], R),
        Q("pregnancy.current_conception_method_and_plurality", "Current Conception Method and Plurality", "string", "conception-plurality", "이번 임신이 자연임신인지 보조생식인지와 단태아·다태아 여부를 알려주세요.", 130, [G["common"]], R),
        Q("pregnancy.current_antenatal_or_postnatal_care", "Current Maternity Care", "string", "care-team", "현재 다니는 산부인과·조산사·산후 진료팀과 다음 예약이 있나요?", 129, [G["common"]], R),
        Q("pregnancy.medical_and_surgical_history", "Relevant Medical and Surgical History", "string", "medical-history", "고혈압·당뇨·혈전·심장·신장·간·갑상선 질환과 수술력을 알려주세요.", 128, [G["common"]], R),
        Q("pregnancy.current_medicines_allergies_and_supplements", "Medicines Allergies and Supplements", "string", "medicines", "처방약·일반약·영양제와 약물 알레르기를 알려주세요.", 127, [G["common"]], R),
        Q("pregnancy.blood_group_rh_and_antenatal_results", "Blood Group Rh and Antenatal Results", "string", "blood-results", "알고 있다면 혈액형·Rh, 최근 혈압·소변·혈액검사와 초음파 결과를 알려주세요.", 126, [G["common"]], R),
        Q("pregnancy.smoking_alcohol_substance_and_occupation", "Pregnancy Exposure Context", "string", "exposures", "흡연·음주·기타 약물, 직업상 노출과 최근 여행을 알려주세요.", 118, [G["common"]], R),
        Q("pregnancy.support_and_living_situation", "Support and Living Situation", "string", "support", "함께 지내며 도와줄 사람과 응급 시 연락·이동 가능한 방법이 있나요?", 117, [G["common"]], R),
        Q("pregnancy.other_detail_or_patient_priority", "Other Pregnancy or Postpartum Detail", "string", "other-detail", "질문에 없지만 꼭 전달하고 싶은 내용이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["common"]], C),

        Q("pregnancy.early_bleeding_amount_color_and_clots", "Early Pregnancy Bleeding Detail", "string", "early-bleeding", "출혈의 색·양, 혈괴나 조직 같은 것이 나왔는지 알려주세요.", 125, [G["early-pain-bleeding"]], C),
        Q("pregnancy.early_pain_site_severity_and_pattern", "Early Pregnancy Pain Detail", "string", "early-pain", "통증 위치·좌우, 0~10점 정도와 지속적·간헐적 여부를 알려주세요.", 124, [G["early-pain-bleeding"]], C),
        Q("pregnancy.last_menstrual_period_and_test", "Last Menstrual Period and Pregnancy Test", "string", "lmp-test", "마지막 생리 시작일과 임신검사 날짜·결과를 알려주세요.", 123, [G["early-pain-bleeding"]], C),
        Q("pregnancy.intrauterine_pregnancy_confirmation", "Intrauterine Pregnancy Confirmation", "string", "pregnancy-location", "초음파로 자궁 안 임신을 확인했는지, 태아 심박을 들었는지 알려주세요.", 122, [G["early-pain-bleeding"]], R),
        Q("pregnancy.ectopic_or_miscarriage_risk_history", "Ectopic or Miscarriage Risk History", "string", "early-risk", "이전 자궁외임신·유산, 난관 수술·감염, 보조생식 또는 자궁내장치 사용이 있나요?", 121, [G["early-pain-bleeding"]], R),
        Q("pregnancy.gastrointestinal_urinary_or_shoulder_symptoms", "Associated Early Pregnancy Symptoms", "string", "early-associated", "구토·설사, 배뇨 증상, 어깨 통증 또는 직장 압박감이 있나요?", 120, [G["early-pain-bleeding"]], D),
        Q("pregnancy.prior_assessment_hcg_or_ultrasound", "Prior Early Pregnancy Assessment", "string", "early-assessment", "이번 문제로 진료·초음파·hCG 검사를 받았다면 날짜와 결과·변화를 알려주세요.", 112, [G["early-pain-bleeding"]], R),

        Q("pregnancy.fetal_movement_usual_pattern_and_change", "Fetal Movement Pattern", "string", "movement-detail", "평소 태동 패턴과 언제부터 어떻게 달라졌는지 알려주세요.", 125, [G["later-fetal-labour"]], C),
        Q("pregnancy.fluid_leak_time_amount_color_odor", "Possible Membrane Rupture Detail", "string", "fluid-leak", "질에서 흐르는 액체가 시작된 시간, 양·색·냄새와 계속 새는지 알려주세요.", 124, [G["later-fetal-labour"]], C, terminology_binding={"system": SN, "code": "371380006"}, mrcm_ref=M),
        Q("pregnancy.contraction_frequency_duration_and_strength", "Contraction Pattern", "string", "contractions", "배 뭉침·진통이 몇 분 간격이고 한 번에 얼마나 지속되며 점점 강해지나요?", 123, [G["later-fetal-labour"]], C, terminology_binding={"system": SN, "code": "249149000"}, mrcm_ref=M),
        Q("pregnancy.show_bleeding_or_mucus", "Show or Bleeding Detail", "string", "show-bleeding", "점액 섞인 소량의 이슬인지 선홍색 출혈인지 알려주세요.", 122, [G["later-fetal-labour"]], C),
        Q("pregnancy.fetal_presentation_multiple_or_placenta_context", "Known Pregnancy Anatomy Context", "string", "pregnancy-context", "알고 있다면 태아 자세, 다태임신, 태반 위치 또는 자궁경부 관련 설명을 들었나요?", 115, [G["later-fetal-labour"]], R),
        Q("pregnancy.last_fetal_check_and_result", "Last Fetal Assessment", "string", "last-fetal-check", "마지막 태아 심박·초음파·성장 검사는 언제였고 결과가 어땠나요?", 114, [G["later-fetal-labour"]], R),
        Q("pregnancy.planned_birth_location_and_contact", "Birth Plan and Maternity Contact", "string", "birth-plan", "분만 예정 병원과 연락처, 이동 계획이 있나요?", 108, [G["later-fetal-labour"]], R),

        Q("pregnancy.latest_blood_pressure_and_trend", "Latest Blood Pressure", "string", "blood-pressure", "가장 최근 혈압 수치와 평소보다 상승했는지 알려주세요.", 125, [G["maternal-medical"]], C),
        Q("pregnancy.edema_face_hands_or_rapid_weight_gain", "Edema or Rapid Weight Change", "string", "edema", "얼굴·손이 갑자기 붓거나 체중이 빠르게 늘었나요?", 124, [G["maternal-medical"]], R),
        Q("pregnancy.fever_infection_or_urinary_symptoms", "Infection or Urinary Symptoms", "string", "infection", "발열, 기침·호흡기 증상, 배뇨통·옆구리 통증 또는 다른 감염 증상이 있나요?", 123, [G["maternal-medical"]], D),
        Q("pregnancy.nausea_vomiting_intake_and_urine", "Nausea Vomiting and Hydration", "string", "vomiting", "하루 구토 횟수, 물·음식 섭취 가능 여부와 소변 양을 알려주세요.", 122, [G["maternal-medical"]], C),
        Q("pregnancy.itching_rash_or_jaundice", "Itching Rash or Jaundice", "string", "itching", "특히 손바닥·발바닥의 심한 가려움, 발진 또는 눈·피부가 노래짐이 있나요?", 121, [G["maternal-medical"]], R),
        Q("pregnancy.glucose_diabetes_and_ketone_context", "Diabetes and Glucose Context", "string", "glucose", "당뇨·임신성 당뇨 여부와 최근 혈당·케톤, 인슐린 사용을 알려주세요.", 114, [G["maternal-medical"]], R),
        Q("pregnancy.vte_risk_immobility_surgery_or_history", "Venous Thromboembolism Risk", "string", "vte-risk", "과거 혈전, 최근 수술·장기간 움직이지 못함, 장거리 이동 또는 혈전 가족력이 있나요?", 113, [G["maternal-medical"]], R),

        Q("postpartum.delivery_date_mode_and_complications", "Delivery Detail", "string", "delivery-detail", "출산 날짜, 질식·제왕절개·도움 분만 여부와 출혈·고혈압 등 합병증을 알려주세요.", 125, [G["postpartum-physical"]], C, terminology_binding={"system": SN, "code": "86569001"}, mrcm_ref=M),
        Q("postpartum.bleeding_lochia_amount_color_odor", "Postpartum Bleeding Detail", "string", "lochia", "산후 출혈·오로의 양·색·냄새와 줄다가 다시 늘었는지 알려주세요.", 124, [G["postpartum-physical"]], C),
        Q("postpartum.abdominal_pelvic_or_perineal_pain", "Postpartum Pain", "string", "postpartum-pain", "배·골반·회음부 통증 위치와 심해지는지 알려주세요.", 123, [G["postpartum-physical"]], C),
        Q("postpartum.caesarean_or_perineal_wound", "Postpartum Wound Status", "string", "postpartum-wound-detail", "제왕절개·회음부 상처의 벌어짐, 붉어짐, 부기·분비물이 있나요?", 122, [G["postpartum-physical"]], C),
        Q("postpartum.urination_and_bowel_function", "Postpartum Bladder and Bowel Function", "string", "bladder-bowel", "소변·대변 보기, 요실금·변실금 또는 심한 변비 문제가 있나요?", 121, [G["postpartum-physical"]], R),
        Q("postpartum.anemia_fatigue_dizziness_or_palpitations", "Postpartum Anaemia Symptoms", "string", "anemia", "심한 피로·어지럼·두근거림·숨참과 최근 혈색소 결과가 있나요?", 120, [G["postpartum-physical"]], R),
        Q("postpartum.follow_up_blood_pressure_or_diabetes_plan", "Postpartum Follow-up Plan", "string", "postpartum-followup", "임신성 고혈압·당뇨 또는 다른 합병증의 산후 검사·약·예약 계획이 있나요?", 112, [G["postpartum-physical"]], R),

        Q("postpartum.mood_anxiety_and_interest", "Perinatal Mood and Anxiety", "string", "mood", "우울감·불안·죄책감, 흥미 저하 또는 감정적으로 감당하기 어려움이 있나요?", 125, [G["mental-feeding"]], C),
        Q("postpartum.sleep_when_baby_sleeps", "Perinatal Sleep Pattern", "string", "sleep", "아기가 잘 때도 거의 잠들지 못하거나 지나치게 들뜨고 잠이 필요 없게 느껴지나요?", 124, [G["mental-feeding"]], R),
        Q("postpartum.bonding_intrusive_thoughts_and_function", "Bonding and Intrusive Thoughts", "string", "bonding", "아기와 유대감, 원치 않는 무서운 생각, 일상 돌봄 수행에 어려움이 있나요?", 123, [G["mental-feeding"]], R),
        Q("postpartum.prior_mental_health_and_family_history", "Perinatal Mental Health History", "string", "mental-history", "과거 우울·양극성장애·정신병, 산후 정신건강 문제 또는 가까운 가족의 산후 정신병 병력이 있나요?", 122, [G["mental-feeding"]], R),
        Q("postpartum.feeding_method_and_intake", "Infant Feeding Method", "string", "feeding", "모유·분유·혼합 중 어떤 방법이며 아기가 먹는 양·횟수에 걱정이 있나요?", 121, [G["mental-feeding"]], C),
        Q("postpartum.breast_nipple_pain_redness_or_lump", "Breast and Nipple Symptoms", "string", "breast-symptoms", "유방·유두 통증, 갈라짐, 붉어짐·열감·멍울이 있나요?", 120, [G["mental-feeding"]], C),
        Q("postpartum.lactation_support_and_baby_output", "Feeding Support and Baby Output", "string", "feeding-support", "수유 지원을 받았는지와 아기의 젖은 기저귀·체중 변화에 대한 우려가 있나요?", 112, [G["mental-feeding"]], R),
    ]
    specs = [
        ("collapse", "pregnancy.hemodynamic_instability_or_collapse", "emergency"), ("heavy-bleeding", "pregnancy.heavy_vaginal_bleeding", "emergency"),
        ("ectopic-warning", "pregnancy.severe_unilateral_pain_or_shoulder_tip_pain", "emergency"), ("severe-abdominal-pain", "pregnancy.severe_constant_abdominal_pain", "emergency"),
        ("chest-dyspnea", "pregnancy.chest_pain_sudden_dyspnea_or_hemoptysis", "emergency"), ("leg-thrombosis", "pregnancy.unilateral_leg_swelling_pain_redness", "urgent"),
        ("preeclampsia-warning", "pregnancy.severe_headache_vision_or_upper_abdominal_pain", "urgent"), ("seizure-consciousness", "pregnancy.seizure_or_reduced_consciousness", "emergency"),
        ("severe-hypertension", "pregnancy.severe_hypertension_measured", "urgent"), ("reduced-fetal-movement", "pregnancy.reduced_or_absent_fetal_movement", "urgent"),
        ("later-bleeding", "pregnancy.later_pregnancy_vaginal_bleeding", "urgent"), ("cord-prolapse", "pregnancy.prolapsed_cord_or_part_visible", "emergency"),
        ("preterm-labour", "pregnancy.preterm_labour_or_membrane_rupture", "urgent"), ("imminent-birth", "pregnancy.imminent_birth_urge_to_push", "emergency"),
        ("severe-infection", "pregnancy.fever_rigors_or_severe_systemic_illness", "emergency"), ("vomiting-dehydration", "pregnancy.persistent_vomiting_dehydration", "urgent"),
        ("postpartum-hemorrhage", "postpartum.sudden_or_very_heavy_bleeding", "emergency"), ("postpartum-infection", "postpartum.foul_discharge_fever_or_worsening_pelvic_pain", "urgent"),
        ("postpartum-wound", "postpartum.wound_breakdown_or_spreading_infection", "urgent"), ("mastitis-systemic", "postpartum.breast_inflammation_with_systemic_illness", "urgent"),
        ("self-baby-harm", "postpartum.self_harm_or_harm_to_baby", "emergency"), ("postpartum-psychosis", "postpartum.psychosis_or_mania", "emergency"),
        ("safeguarding", "pregnancy.domestic_abuse_or_safeguarding_concern", "urgent"),
    ]
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, 1000 if level == "emergency" else 970) for key, fid, level in specs]
    return {"id": "knowledge.generated.pregnancy-postpartum-concern", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-pregnancy-postpartum-concern-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="pregnancy.primary_concern_group", question_budget=62, source_refs=SOURCES)
    branches = {
        "early_pain_bleeding": ["pregnancy.early_bleeding_amount_color_and_clots", "pregnancy.early_pain_site_severity_and_pattern", "pregnancy.last_menstrual_period_and_test", "pregnancy.intrauterine_pregnancy_confirmation", "pregnancy.ectopic_or_miscarriage_risk_history", "pregnancy.gastrointestinal_urinary_or_shoulder_symptoms", "pregnancy.prior_assessment_hcg_or_ultrasound"],
        "later_fetal_labour": ["pregnancy.fetal_movement_usual_pattern_and_change", "pregnancy.fluid_leak_time_amount_color_odor", "pregnancy.contraction_frequency_duration_and_strength", "pregnancy.show_bleeding_or_mucus", "pregnancy.fetal_presentation_multiple_or_placenta_context", "pregnancy.last_fetal_check_and_result", "pregnancy.planned_birth_location_and_contact"],
        "maternal_medical": ["pregnancy.latest_blood_pressure_and_trend", "pregnancy.edema_face_hands_or_rapid_weight_gain", "pregnancy.fever_infection_or_urinary_symptoms", "pregnancy.nausea_vomiting_intake_and_urine", "pregnancy.itching_rash_or_jaundice", "pregnancy.glucose_diabetes_and_ketone_context", "pregnancy.vte_risk_immobility_surgery_or_history"],
        "postpartum_physical": ["postpartum.delivery_date_mode_and_complications", "postpartum.bleeding_lochia_amount_color_odor", "postpartum.abdominal_pelvic_or_perineal_pain", "postpartum.caesarean_or_perineal_wound", "postpartum.urination_and_bowel_function", "postpartum.anemia_fatigue_dizziness_or_palpitations", "postpartum.follow_up_blood_pressure_or_diabetes_plan"],
        "mental_feeding": ["postpartum.mood_anxiety_and_interest", "postpartum.sleep_when_baby_sleeps", "postpartum.bonding_intrusive_thoughts_and_function", "postpartum.prior_mental_health_and_family_history", "postpartum.feeding_method_and_intake", "postpartum.breast_nipple_pain_redness_or_lump", "postpartum.lactation_support_and_baby_output"],
        "other_unclear": ["pregnancy.other_detail_or_patient_priority"],
    }
    policy["required_facts"]["routine"] = [
        "pregnancy.stage", "pregnancy.gestational_age_or_postpartum_day", "pregnancy.estimated_due_date_and_dating_method",
        "pregnancy.current_conception_method_and_plurality", "pregnancy.main_symptom_duration_and_progression",
        "pregnancy.prior_pregnancies_and_outcomes", "pregnancy.obstetric_gravidity_total", "pregnancy.obstetric_parity_total",
        "pregnancy.obstetric_parity_threshold_as_recorded",
        "pregnancy.obstetric_term_birth_count", "pregnancy.obstetric_preterm_birth_count",
        "pregnancy.obstetric_spontaneous_loss_count", "pregnancy.obstetric_induced_termination_count",
        "pregnancy.obstetric_ectopic_count", "pregnancy.obstetric_molar_pregnancy_count",
        "pregnancy.obstetric_living_children_count", "pregnancy.prior_multiple_gestation_history",
        "pregnancy.prior_delivery_modes_and_caesarean_count", "pregnancy.prior_obstetric_complications",
        "pregnancy.prior_fetal_neonatal_outcomes", "pregnancy.current_antenatal_or_postnatal_care",
        "pregnancy.medical_and_surgical_history", "pregnancy.current_medicines_allergies_and_supplements",
        "pregnancy.support_and_living_situation", "pregnancy.other_detail_or_patient_priority",
    ]
    policy["conditional_required_facts"] = [{"selector_fact": "pregnancy.primary_concern_group", "cases": branches}]
    return policy


def source_docs():
    defs = [
        ("source.nice.ng126.early-pregnancy.2026", "NICE", "Ectopic pregnancy and miscarriage: symptoms, signs and initial assessment", "NG126; updated-2026-06-17", "https://www.nice.org.uk/guidance/ng126/chapter/symptoms-and-signs-of-ectopic-pregnancy-and-initial-assessment", "nice_guidance", 7, ["Haemodynamic instability or significant pain or bleeding requires direct emergency assessment.", "Early-pregnancy targets include pain, amenorrhoea, bleeding, dizziness or syncope, shoulder-tip pain, urinary or gastrointestinal symptoms and pregnancy location uncertainty."]),
        ("source.nice.ng133.hypertension-pregnancy.2023", "NICE", "Hypertension in pregnancy: diagnosis and management", "NG133; updated-2023-04-17", "https://www.nice.org.uk/guidance/ng133/chapter/Recommendations", "nice_guidance", 7, ["Severe headache, visual disturbance and severe pain below the ribs require immediate assessment for possible pre-eclampsia; symptoms do not establish the diagnosis."]),
        ("source.nice.ng194.postnatal-care.2021", "NICE", "Postnatal care", "NG194; accessed-2026-07-15", "https://www.nice.org.uk/guidance/ng194/chapter/Recommendations", "nice_guidance", 7, ["Postnatal contacts assess bleeding, infection, pain, bladder and bowel function, breast symptoms, thromboembolism, anaemia, pre-eclampsia and psychological wellbeing.", "Sudden heavy bleeding, infection symptoms, unilateral leg swelling, dyspnoea, chest pain and severe headache require prompt assessment."]),
        ("source.nice.cg192.perinatal-mental-health.2025", "NICE", "Antenatal and postnatal mental health", "CG192; reviewed-2025-05-30", "https://www.nice.org.uk/guidance/cg192", "nice_guidance", 7, ["Pregnancy and the first postnatal year require assessment for depression, anxiety, substance use and severe mental illness.", "Sudden suspected postpartum psychosis requires immediate specialist assessment; self-harm or infant-harm risk requires emergency safety action."]),
        ("source.nhs.pregnancy-urgent-symptoms.2026", "NHS", "Pregnancy symptoms you need to get help for", "reviewed-2026-06-24", "https://www.nhs.uk/pregnancy/common-symptoms/pregnancy-symptoms-you-need-to-get-help-for/", "public_health_guidance", 7, ["Urgent maternity concerns include bleeding, pain, sudden breathlessness, chest pain, visual change, reduced fetal movement and signs of labour."]),
        ("source.nhs.fetal-movements.2024", "NHS", "Your baby's movements", "reviewed-2024-07-08", "https://www.nhs.uk/pregnancy/keeping-well/your-babys-movements/", "public_health_guidance", 7, ["Reduced, absent or changed fetal movement requires immediate maternity-unit contact and should not wait until the next day."]),
        ("source.nhs.labour-signs.2026", "NHS", "Signs that labour has begun", "accessed-2026-07-15", "https://www.nhs.uk/pregnancy/labour-and-birth/signs-that-labour-has-begun/", "public_health_guidance", 7, ["Waters breaking, vaginal bleeding, reduced fetal movement and possible labour before 37 weeks require urgent maternity contact."]),
        ("source.nhs.postpartum-body.2024", "NHS", "Your body after the birth", "reviewed-2024-04-25", "https://www.nhs.uk/pregnancy/labour-and-birth/your-body/", "public_health_guidance", 7, ["Postpartum warning features include unilateral calf swelling, chest pain or dyspnoea, sudden heavy bleeding, fever with abdominal tenderness and headache with visual change or vomiting."]),
        ("source.nice.ng201.antenatal-history.2021", "NICE", "Antenatal care: schedule of antenatal appointments", "NG201; accessed-2026-07-15", "https://www.nice.org.uk/guidance/ng201/resources/schedule-of-antenatal-appointments-pdf-9204300829", "nice_guidance", 7, ["The booking record should include obstetric, medical and family history, medicines, allergies, lifestyle, occupation, home situation and support network.", "Antenatal records should retain history, test results, examination findings, medicines and discussions for clinical use."]),
        ("source.acog.revitalize-obstetric-definitions.2026", "ACOG", "reVITALize: Obstetrics Data Definitions", "accessed-2026-07-15", "https://www.acog.org/practice-management/health-it-and-clinical-informatics/revitalize-obstetrics-data-definitions", "clinical_guideline", 1, ["Parity is a count of pregnancies reaching the stated gestational threshold, independent of fetal number or outcome.", "Structured obstetric data should preserve plurality and pregnancy outcome concepts without inferring parity from number of fetuses."]),
        ("source.stom.pregnancy-postpartum.20260715", "Infoclinic", "STOM pregnancy and postpartum terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", 30, ["STOM returned active candidates for pregnancy, postpartum state, pregnancy-associated genital bleeding, reduced fetal movement, amniotic fluid leak, labour contraction, postpartum haemorrhage, pre-eclampsia, mastitis and postpartum psychosis.", "Finding site and Severity were allowed MRCM attributes for the selected concepts; MRCM does not determine clinical urgency."]),
    ]
    arts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": ver, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-15", "next_monitor_at": "2026-08-14" if days == 30 else "2026-07-22", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, ver, url, profile, days, assertions in defs]
    research = {"id": "source-manifest.primary-care-pregnancy-postpartum-concern-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": arts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.pregnancy-postpartum", "generated_clinical_knowledge", "knowledge/generated/obstetric/pregnancy-postpartum-concern/pregnancy-postpartum-concern.json", True), ("source.mapping.pregnancy-postpartum", "terminology_mapping", "mappings/terminology/snomed-mrcm-pregnancy-postpartum-concern.json", False), ("source.external.pregnancy-postpartum", "external_source_manifest", "sources/manifests/primary-care-pregnancy-postpartum-concern-research.json", False), ("source.policy.pregnancy-postpartum", "runtime_policy", "policies/primary-care-pregnancy-postpartum-concern-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-pregnancy-postpartum-concern", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, value = rule["when"]["fact"], rule["when"]["equals"]
        key = rule["id"].split("safety.")[1]; level = rule["then"]["safety_level"]
        out[f"PREG-{key.upper()}.json"] = {"id": f"PREG-{key.upper()}", "simulation_language": "ko", "persona": {"age": 24 + i}, "initial_statement": {"ko": "임신 또는 산후 증상 때문에 상담받고 싶어요."}, "hidden_state": {fid: {"value": value}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 48, "forbidden_assertions": ["diagnosis.ectopic_pregnancy", "diagnosis.preeclampsia", "recommendation.change_medication"]}, "provenance": provenance(SOURCES)}
    policy = completion(f); required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["early_pain_bleeding"]); by = {x["fact"]["id"]: x["fact"] for x in f["entries"]}; hidden = {}
    for fid in required:
        fact = by[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["unclear"])[-1]}
        elif fact["value_type"] == "integer": hidden[fid] = {"value": 1}
        else: hidden[fid] = {"value": "없음"}
    hidden["pregnancy.primary_concern_group"] = {"value": "early_pain_bleeding"}; hidden["pregnancy.stage"] = {"value": "possible_pregnancy"}
    declined = "pregnancy.gestational_age_or_postpartum_day"; hidden.pop(declined)
    out["PREG-EARLY-DATA-ABSENT.json"] = {"id": "PREG-EARLY-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 31}, "initial_statement": {"ko": "임신 가능성이 있는데 소량 출혈이 있어요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 65, "forbidden_assertions": ["diagnosis.ectopic_pregnancy", "diagnosis.miscarriage"]}, "provenance": provenance(["source.nice.ng126.early-pregnancy.2026", "specifications/clinical-memory.md"])}
    return out


def main():
    f = fragment(); graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Pregnancy or Postpartum Concern", intents=[("intent.characterize_symptom", "Characterize Pregnancy or Postpartum Concern"), ("intent.screen_red_flags", "Screen Maternal and Fetal Red Flags"), ("intent.differentiate_common_causes", "Assess Symptom Context"), ("intent.risk_assessment", "Maternal Fetal and Postpartum Risk Assessment")]); primary, research = source_docs()
    concepts = [("77386006", "Pregnancy (finding)", 20), ("86569001", "Postpartum state (finding)", 20), ("16320551000119109", "Bleeding from female genital tract co-occurrent with pregnancy (disorder)", 22), ("276369006", "Reduced fetal movement (finding)", 20), ("371380006", "Amniotic fluid leaking (disorder)", 22), ("249149000", "Contraction of uterus during labor (finding)", 20), ("47821001", "Postpartum hemorrhage (disorder)", 22), ("398254007", "Pre-eclampsia (disorder)", 22), ("266579006", "Inflammatory disorder of breast (disorder)", 22), ("18260003", "Postpartum psychosis (disorder)", 22)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["363698007", "246112005"], "validation": {"method": "build_time_live_mapping_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.pregnancy-postpartum.20260715"])}
    docs = [("knowledge/base/primary-care-pregnancy-postpartum-concern.json", graph), ("rules/base/primary-care-pregnancy-postpartum-concern.json", rules), ("knowledge/generated/obstetric/pregnancy-postpartum-concern/pregnancy-postpartum-concern.json", f), ("mappings/terminology/snomed-mrcm-pregnancy-postpartum-concern.json", mapping), ("sources/manifests/primary-care-pregnancy-postpartum-concern.json", primary), ("sources/manifests/primary-care-pregnancy-postpartum-concern-research.json", research), ("policies/primary-care-pregnancy-postpartum-concern-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/obstetric/pregnancy-postpartum-concern/" + name, case)


if __name__ == "__main__": main()
