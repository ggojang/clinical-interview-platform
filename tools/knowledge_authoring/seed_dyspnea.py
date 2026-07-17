#!/usr/bin/env python3
"""Rebuild unreviewed dyspnea knowledge for clinician pre-visit handoff."""
from profile_support import *

P, RFE = "dyspnea", "rfe.dyspnea"
M, SN = "mapping.snomed-mrcm.dyspnea", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-17T02:00:00Z"
SOURCES = [
    "source.nice.ng158.vte", "source.nice.ng115.copd",
    "source.nice.ng106.heart-failure", "source.gina.strategy.2026",
    "source.nhs.shortness-of-breath", "source.stom.dyspnea.20260717",
]
G = {key: f"group.dyspnea.{key}" for key in (
    "routing", "safety", "course", "function", "airway", "infection",
    "cardiac", "thromboembolic", "risk", "exposure", "followup",
)}
C, S = ["intent.characterize_symptom"], ["intent.screen_red_flags"]
D, R = ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("dyspnea.primary_group", "Primary Dyspnea Context", "coded", "primary-group", "이번 숨참은 갑자기 시작, 감염 증상과 함께 악화, 활동할 때 주로 발생, 누울 때·밤에 악화하거나 부종 동반, 쌕쌕거림·기침 동반, 수술·장기부동·한쪽 다리 증상 뒤 발생, 기존 심장·폐질환 추적, 임신·산후, 연기·가스·고도 등 노출, 그 밖의 불분명한 경우 중 무엇에 가장 가깝나요?", 250, [G["routing"]], C, allowed_values=["acute_sudden", "acute_progressive_or_infectious", "exertional_or_functional", "positional_nocturnal_or_edema", "airway_wheeze_or_cough", "vte_or_post_immobility", "known_cardiopulmonary_followup", "pregnancy_postpartum", "exposure_altitude_or_toxic", "other_unclear"]),
        Q("symptom.dyspnea", "Breathing Difficulty Severity", "severity", "severity", "지금 숨참은 없음·가벼움·중간·심함 중 어느 정도인가요?", 249, [G["safety"], G["course"]], S, reuse_existing=True),
        Q("dyspnea.severe_breathing_distress", "Severe Breathing Distress", "boolean", "severe-distress", "지금 숨을 쉬는 것 자체가 매우 힘들거나 평소와 달리 심각한 호흡곤란 상태인가요?", 249, [G["safety"]], S, safety_relevant=True),
        Q("dyspnea.inability_to_speak_gasping_or_exhaustion", "Unable to Speak Gasping or Exhausted", "boolean", "unable-to-speak", "숨이 너무 차서 문장을 끝까지 말하기 어렵거나 헐떡임·질식감·심한 탈진이 있나요?", 248, [G["safety"]], S, safety_relevant=True),
        Q("symptom.cyanosis", "Blue Grey or Very Pale Colour", "boolean", "cyanosis", "입술·혀·피부가 갑자기 파랗거나 회색 또는 매우 창백해 보이나요?", 247, [G["safety"]], S, safety_relevant=True),
        Q("symptom.confusion", "New Confusion or Reduced Alertness", "boolean", "confusion", "새로 혼란스럽거나 깨우기 어렵고 평소와 다른 반응이 있나요?", 246, [G["safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("dyspnea.collapse_clammy_or_circulatory_warning", "Collapse or Circulatory Warning", "boolean", "collapse-warning", "쓰러짐·실신, 차갑고 축축한 피부, 심한 어지럼 또는 곧 쓰러질 듯한 상태가 있나요?", 245, [G["safety"], G["cardiac"]], S, safety_relevant=True),
        Q("dyspnea.stridor_choking_or_airway_swelling", "Stridor Choking or Airway Swelling", "boolean", "airway-warning", "숨 들이쉴 때 거친 소리, 갑작스러운 질식, 목·혀·입술 부종 또는 침도 삼키기 어려움이 있나요?", 244, [G["safety"], G["airway"]], S, safety_relevant=True),
        Q("dyspnea.chest_pressure_radiation_or_sweating", "Cardiac Chest Warning", "boolean", "cardiac-warning", "가슴이 조이거나 무겁고, 팔·등·목·턱으로 퍼지는 통증 또는 식은땀이 숨참과 함께 있나요?", 243, [G["safety"], G["cardiac"]], S, safety_relevant=True),
        Q("symptom.hemoptysis", "Coughing Up Blood", "boolean", "hemoptysis", "선명한 피를 기침으로 뱉었나요?", 242, [G["safety"], G["thromboembolic"]], S, safety_relevant=True, reuse_existing=True),
        Q("dyspnea.sudden_with_unilateral_leg_or_vte_warning", "Sudden Dyspnea with VTE Warning", "boolean", "vte-warning", "숨참이 갑자기 시작하면서 한쪽 다리가 새로 붓거나 아프거나, 최근 수술·장기부동·혈전 병력이 있나요?", 241, [G["safety"], G["thromboembolic"]], S, safety_relevant=True),
        Q("dyspnea.pregnancy_postpartum_chest_pain_or_collapse", "Pregnancy or Postpartum Warning", "boolean", "pregnancy-warning", "임신 중이거나 출산·유산·임신종결 후 6주 이내이며 숨참과 함께 흉통·실신·심한 두근거림·한쪽 다리 부종이 있나요?", 240, [G["safety"], G["risk"]], S, safety_relevant=True),
        Q("dyspnea.rescue_treatment_not_helping_or_rapid_worsening", "Rescue Treatment Failure or Rapid Worsening", "boolean", "rescue-failure", "처방받은 응급 흡입제·분무·산소를 사용해도 호전되지 않거나 숨참이 빠르게 심해지고 있나요?", 239, [G["safety"], G["followup"]], S, safety_relevant=True),
        Q("dyspnea.child_retractions_grunting_or_limp", "Child Respiratory Distress Warning", "boolean", "child-warning", "소아라면 갈비뼈 사이·목 아래가 들어가게 숨쉬거나 끙끙거림, 축 늘어짐, 깨우기 어려움이 있나요?", 238, [G["safety"], G["risk"]], S, safety_relevant=True),
        Q("symptom.chest_pain", "Chest Pain or Pressure", "boolean", "chest-pain", "숨참과 함께 가슴 통증·압박감·조임이 있나요?", 237, [G["safety"], G["cardiac"]], S, safety_relevant=True, reuse_existing=True),
        Q("symptom.syncope", "Syncope or Near-syncope", "boolean", "syncope", "숨참 전후로 실제로 의식을 잃었거나 거의 실신했나요?", 236, [G["safety"], G["cardiac"]], S, safety_relevant=True),
    ]
    specs = [
        ("dyspnea.information_source_proxy_and_reliability", "Information Source and Reliability", "string", "information-source", "누가 답변하며 본인 느낌, 보호자 관찰, 산소포화도계, 진료기록·검사결과 중 무엇에 근거하나요? 확실하지 않거나 서로 다른 정보도 알려주세요.", 220, "routing", C),
        ("dyspnea.age_life_stage_and_baseline", "Age Life Stage and Baseline", "string", "age-baseline", "만 나이, 소아·고령·임신·산후 여부와 평소 호흡·활동·산소 사용 상태를 알려주세요.", 219, "risk", R),
        ("symptom.duration", "Dyspnea Duration", "quantity", "duration", "숨참이 처음 시작된 뒤 지금까지의 기간을 알려주세요.", 218, "course", C),
        ("symptom.dyspnea_onset", "Dyspnea Onset Speed", "coded", "onset-speed", "숨참은 갑자기 시작했나요, 서서히 시작했나요?", 217, "course", C),
        ("dyspnea.onset_date_time_activity_and_circumstance", "Onset Context", "string", "onset-context", "처음 시작한 날짜·시각과 당시 활동·자세·수면·식사·노출·시술 등 상황을 알려주세요.", 216, "course", C),
        ("dyspnea.episode_frequency_duration_trend_and_between_episode_baseline", "Episode Pattern and Trend", "string", "episode-pattern", "계속 숨찬지 반복되는지, 반복한다면 빈도·지속시간·호전/악화 추세와 사이사이 정상으로 돌아오는지 알려주세요.", 215, "course", C),
        ("symptom.dyspnea_at_rest", "Dyspnea at Rest", "boolean", "at-rest", "가만히 앉거나 누워 있을 때도 숨이 차나요?", 214, "function", C),
        ("symptom.exertional_dyspnea", "Exertional Dyspnea", "boolean", "exertional", "걷기·계단·일 등 활동할 때 숨참이 생기거나 심해지나요?", 213, "function", C),
        ("dyspnea.exertional_threshold_and_change_from_baseline", "Exertional Threshold", "string", "exertional-threshold", "몇 m 걷기·몇 층 계단·어떤 일에서 멈추게 되며, 평소 가능한 활동과 비교해 얼마나 줄었나요?", 212, "function", C),
        ("dyspnea.speaking_eating_sleep_selfcare_and_mobility_impact", "Daily Function Impact", "string", "function-impact", "말하기, 먹기, 잠자기, 씻기·옷입기, 화장실 가기와 이동이 숨참 때문에 어떻게 제한되나요?", 211, "function", R),
        ("dyspnea.respiratory_pattern_accessory_muscle_and_position", "Observed Breathing Pattern", "string", "breathing-pattern", "호흡수, 얕거나 불규칙한 호흡, 갈비뼈 사이가 들어감, 앞으로 기대는 자세를 관찰했다면 알려주세요.", 210, "function", R),
        ("dyspnea.oxygen_saturation_device_time_oxygen_and_reliability", "Oxygen Saturation Context", "string", "oxygen-saturation", "산소포화도를 쟀다면 값·시각·기기·손가락 상태와 산소 사용 여부·유량을 알려주세요. 측정하지 않았거나 신뢰하기 어렵다면 그렇게 알려주세요.", 209, "followup", R),
        ("symptom.orthopnea", "Orthopnea", "boolean", "orthopnea", "누우면 숨이 더 차거나 상체를 세워야 편한가요?", 195, "cardiac", D),
        ("dyspnea.orthopnea_pillow_count_and_position_detail", "Orthopnea Detail", "string", "orthopnea-detail", "평소와 지금 베개 개수, 앉아서 자는지, 어느 정도 누우면 숨찬지 알려주세요.", 194, "cardiac", D),
        ("symptom.paroxysmal_nocturnal_dyspnea", "Paroxysmal Nocturnal Dyspnea", "boolean", "nocturnal", "자다가 숨이 차서 깨거나 일어나 앉아야 하나요?", 193, "cardiac", D),
        ("dyspnea.nocturnal_episode_sleep_and_recovery_detail", "Nocturnal Episode Detail", "string", "nocturnal-detail", "잠든 뒤 몇 시간 만에 깨고 자세를 바꾼 뒤 회복까지 얼마나 걸리며 코골이·무호흡·쌕쌕거림이 동반되나요?", 192, "cardiac", D),
        ("dyspnea.chest_pain_nrs", "Chest Pain NRS", "integer", "chest-pain-nrs", "[필수] 흉통이 있다면 현재 통증을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 191, "cardiac", C),
        ("dyspnea.chest_pain_location_character_radiation_trigger_and_duration", "Chest Pain Detail", "string", "chest-pain-detail", "가슴 통증의 위치·양상·퍼지는 곳·지속시간과 호흡·활동·식사·자세와의 관계를 알려주세요.", 190, "cardiac", C),
        ("symptom.pleuritic_chest_pain", "Pleuritic Chest Pain", "boolean", "pleuritic-chest-pain", "가슴 통증이 숨을 깊이 들이쉬거나 기침할 때 더 심해지나요?", 190, "thromboembolic", D),
        ("symptom.palpitations", "Palpitations", "boolean", "palpitations", "심장이 빠르거나 불규칙하게 뛰고 두근거리는 느낌이 있나요?", 189, "cardiac", D),
        ("dyspnea.palpitations_rate_rhythm_and_relation_to_breathlessness", "Palpitation Detail", "string", "palpitation-detail", "두근거림의 시작·종료, 규칙성, 측정 맥박과 숨참·어지럼·흉통의 시간 관계를 알려주세요.", 188, "cardiac", D),
        ("dyspnea.syncope_presyncope_dizziness_and_recovery_detail", "Syncope Detail", "string", "syncope-detail", "실신·실신 직전·어지럼이 있다면 자세·전조·의식소실 시간·다친 곳·회복 과정을 알려주세요.", 187, "cardiac", R),
        ("dyspnea.edema_weight_gain_nocturia_and_abdominal_swelling", "Fluid Retention Features", "string", "fluid-features", "양쪽 발·발목 부종, 최근 체중 증가, 밤중 소변 증가 또는 배가 붓는 느낌의 시작과 변화를 알려주세요.", 186, "cardiac", D),
        ("symptom.cough", "Cough", "boolean", "cough", "기침이 있나요?", 180, "airway", D),
        ("symptom.sputum", "Sputum", "boolean", "sputum", "가래가 나오나요?", 180, "airway", D),
        ("dyspnea.cough_sputum_color_volume_blood_and_change", "Cough and Sputum Detail", "string", "cough-sputum-detail", "기침과 가래의 시작, 마른기침 여부, 가래 양·색·냄새·피와 평소 대비 변화를 알려주세요.", 179, "airway", D),
        ("symptom.fever", "Fever", "boolean", "fever", "측정된 발열이나 열감·오한이 있나요?", 178, "infection", D),
        ("dyspnea.fever_infection_contact_and_recent_respiratory_illness", "Infection Context", "string", "infection-context", "체온·오한, 콧물·인후통, 아픈 사람 접촉, 최근 호흡기 감염과 날짜를 알려주세요.", 177, "infection", D),
        ("symptom.wheeze", "Wheeze", "boolean", "wheeze", "숨을 내쉴 때 쌕쌕거리거나 휘파람 같은 소리가 나나요?", 176, "airway", D),
        ("dyspnea.wheeze_stridor_voice_swallowing_and_choking_detail", "Airway Detail", "string", "airway-detail", "쌕쌕거림·들이쉴 때 소리·목소리 변화·삼킴 문제·사레·질식의 시작과 유발 상황을 알려주세요.", 175, "airway", D),
        ("symptom.unilateral_leg_pain_swelling", "Unilateral Leg Pain or Swelling", "boolean", "unilateral-leg", "한쪽 다리에 새 통증·부종이 있나요?", 170, "thromboembolic", R),
        ("dyspnea.leg_side_swelling_pain_redness_and_onset", "Unilateral Leg Detail", "string", "leg-detail", "어느 쪽 다리의 어느 부위가 언제부터 붓고 아픈지, 붉음·열감과 둘레 차이를 알려주세요.", 169, "thromboembolic", R),
        ("dyspnea.vte_risk_surgery_immobility_cancer_prior_vte_estrogen_pregnancy", "VTE Risk Context", "string", "vte-risk-detail", "최근 수술·입원·3일 이상 거동 제한·장거리 이동, 활동성 암, 이전 혈전, 에스트로겐 약, 임신·산후 여부와 날짜를 알려주세요.", 168, "thromboembolic", R),
        ("risk.recent_immobility_or_surgery", "Recent Immobility or Surgery", "boolean", "immobility-surgery", "최근 수술 또는 3일 이상 거의 움직이지 못한 기간이 있었나요?", 167, "thromboembolic", R),
        ("history.venous_thromboembolism", "Previous DVT or Pulmonary Embolism", "boolean", "vte-history", "이전에 다리 심부정맥혈전이나 폐색전증 진단을 받은 적이 있나요?", 166, "thromboembolic", R),
        ("dyspnea.pulmonary_history_and_baseline", "Pulmonary History and Baseline", "string", "pulmonary-history", "천식·COPD·기관지확장증·간질성폐질환·결핵·수면무호흡 등 폐질환, 평소 숨참·산소·흡입제 사용을 알려주세요.", 155, "risk", R),
        ("dyspnea.cardiac_history_and_baseline", "Cardiac History and Baseline", "string", "cardiac-history", "심부전·관상동맥질환·판막질환·부정맥·선천성심장질환과 평소 부종·체중·활동 수준을 알려주세요.", 154, "risk", R),
        ("dyspnea.anemia_bleeding_and_recent_hemoglobin_context", "Anemia and Bleeding Context", "string", "anemia-context", "빈혈, 최근 출혈·검은변·과다월경, 수혈·철분치료와 최근 헤모글로빈 결과가 있나요?", 153, "risk", R),
        ("dyspnea.renal_liver_fluid_and_recent_weight_context", "Renal Liver and Fluid Context", "string", "renal-liver-context", "신장·간 질환, 투석·이뇨제, 소변 변화와 최근 체중·부종 변화를 알려주세요.", 152, "risk", R),
        ("dyspnea.neuromuscular_weakness_swallowing_and_cough_strength", "Neuromuscular Context", "string", "neuromuscular-context", "근육·신경 질환, 새 전신 약화, 목 가누기·삼킴·기침 힘 저하가 있나요?", 151, "risk", R),
        ("dyspnea.pregnancy_postpartum_gestation_delivery_and_complications", "Pregnancy and Postpartum Context", "string", "pregnancy-context", "임신 주수 또는 출산·유산·임신종결 날짜, 분만 방법, 출혈·고혈압·감염·혈전 등 합병증을 알려주세요.", 150, "risk", R),
        ("dyspnea.current_medicines_inhalers_oxygen_sedatives_opioids_and_changes", "Medicines Oxygen and Recent Changes", "string", "medicines", "현재 약·흡입제·산소의 이름·용량·사용법과 최근 시작·중단·변경한 진정제·수면제·마약성진통제 등을 알려주세요.", 149, "followup", R),
        ("dyspnea.rescue_inhaler_nebulizer_oxygen_use_dose_time_and_response", "Rescue Treatment and Response", "string", "rescue-response", "응급 흡입제·분무·산소를 사용했다면 이름·횟수·마지막 시각·용량/유량과 전후 변화를 알려주세요.", 148, "followup", R),
        ("dyspnea.inhaler_adherence_technique_spacer_and_action_plan", "Inhaler Technique and Action Plan", "string", "inhaler-technique", "평소 흡입제 누락, 흡입 방법·스페이서 사용, 개인 행동계획과 최대호기유량 기준을 알려주세요.", 147, "followup", R),
        ("dyspnea.medicine_allergies_and_adverse_reactions", "Medicine Allergies and Reactions", "string", "medicine-allergies", "약물·조영제 알레르기와 실제 발생한 반응을 알려주세요.", 146, "risk", R),
        ("patient.smoking.status", "Smoking Status", "coded", "smoking-status", "현재 흡연, 과거 흡연, 비흡연 중 어디에 해당하나요?", 145, "exposure", R),
        ("dyspnea.smoking_vaping_pack_years_passive_exposure_and_change", "Tobacco and Vaping Detail", "string", "smoking-detail", "담배·전자담배 종류, 하루 양·기간·갑년, 금연 시점과 간접흡연을 알려주세요.", 144, "exposure", R),
        ("dyspnea.occupation_home_pollution_fume_dust_mold_and_animal_exposure", "Occupational and Home Exposure", "string", "occupation-exposure", "직업·취미·주거에서 분진·가스·연기·화학물질·곰팡이·새/동물 노출과 보호구, 증상과의 시간 관계를 알려주세요.", 143, "exposure", R),
        ("dyspnea.travel_flight_altitude_diving_and_recent_infection_exposure", "Travel Altitude Diving and Exposure", "string", "travel-exposure", "최근 장거리 이동·비행, 고도 상승, 잠수와 여행지·날짜, 감염자 접촉을 알려주세요.", 142, "exposure", R),
        ("dyspnea.anxiety_panic_context_after_medical_warning_screen", "Anxiety or Panic Context", "string", "anxiety-context", "의학적 위험 신호를 먼저 확인한 뒤, 불안·공황·과호흡과의 시간 관계, 이전 유사 경험과 진정 후 변화를 알려주세요.", 141, "risk", R),
        ("dyspnea.sleep_snoring_apnea_daytime_sleepiness_and_pap_use", "Sleep Breathing Context", "string", "sleep-context", "코골이·목격된 무호흡·야간 질식감·주간 졸림과 양압기 사용·순응도를 알려주세요.", 140, "airway", R),
        ("dyspnea.spirometry_peak_flow_baseline_personal_best_and_date", "Spirometry and Peak Flow", "string", "lung-function", "폐기능검사·최대호기유량이 있다면 날짜·수치·개인 최고치·측정 조건과 원본 유무를 알려주세요.", 130, "followup", R),
        ("dyspnea.ecg_imaging_labs_and_result_source", "Prior Tests and Source", "string", "prior-tests", "이번 증상 관련 심전도, 흉부영상, 혈액검사, D-dimer·BNP 등이 있다면 날짜·결과·자료 출처를 알려주세요.", 129, "followup", R),
        ("dyspnea.prior_assessment_diagnosis_and_followup_plan", "Prior Assessment and Plan", "string", "prior-assessment", "이미 진료받았다면 의료기관·날짜, 들은 설명과 재검·재진·악화 시 계획을 알려주세요.", 128, "followup", R),
        ("dyspnea.treatment_start_adherence_response_and_adverse_effect", "Treatment and Response", "string", "treatment-response", "이번 숨참에 사용한 약·산소·휴식 등 조치의 시작·순응도·효과·부작용을 알려주세요.", 127, "followup", R),
        ("dyspnea.prior_exacerbations_ed_visits_admissions_intubation_and_baseline", "Prior Exacerbations and Acute Care", "string", "prior-exacerbations", "이전 비슷한 악화의 빈도, 최근 1년 응급실·입원·중환자실·삽관과 당시 평소 상태를 알려주세요.", 126, "followup", R),
        ("dyspnea.patient_concern_goal_and_other_detail", "Patient Concern Goal and Other Detail", "string", "patient-goal", "질문에 없지만 의료진에게 꼭 전달할 내용, 가장 걱정하는 점과 이번 진료에서 원하는 것을 알려주세요.", 120, "routing", C),
    ]
    reuse = {"symptom.duration", "symptom.cough", "symptom.sputum", "symptom.fever", "symptom.wheeze", "patient.smoking.status"}
    for fid, display, vt, key, wording, score, group, intents in specs:
        kwargs = {"reuse_existing": True} if fid in reuse else {}
        if fid == "symptom.dyspnea_onset": kwargs["allowed_values"] = ["sudden", "gradual"]
        if fid == "patient.smoking.status": kwargs["allowed_values"] = ["current", "former", "never"]
        e.append(Q(fid, display, vt, key, wording, score, [G[group]], intents, **kwargs))
    safety = [
        ("severe", "dyspnea.severe_breathing_distress", True, "emergency"),
        ("unable-to-speak", "dyspnea.inability_to_speak_gasping_or_exhaustion", True, "emergency"),
        ("cyanosis", "symptom.cyanosis", True, "emergency"),
        ("confusion", "symptom.confusion", True, "emergency"),
        ("collapse-warning", "dyspnea.collapse_clammy_or_circulatory_warning", True, "emergency"),
        ("airway-warning", "dyspnea.stridor_choking_or_airway_swelling", True, "emergency"),
        ("cardiac-warning", "dyspnea.chest_pressure_radiation_or_sweating", True, "emergency"),
        ("hemoptysis", "symptom.hemoptysis", True, "urgent"),
        ("vte-warning", "dyspnea.sudden_with_unilateral_leg_or_vte_warning", True, "urgent"),
        ("pregnancy-warning", "dyspnea.pregnancy_postpartum_chest_pain_or_collapse", True, "emergency"),
        ("rescue-failure", "dyspnea.rescue_treatment_not_helping_or_rapid_worsening", True, "emergency"),
        ("child-warning", "dyspnea.child_retractions_grunting_or_limp", True, "emergency"),
        ("syncope", "symptom.syncope", True, "urgent"),
    ]
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-17", "next_monitor_at": "2026-07-18", "next_full_review_at": "2027-01-13"})
    return {"id": "knowledge.generated.respiratory.dyspnea", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-dyspnea-research", "default_refresh": refresh, "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()], "group_hypothesis_edges": [], "safety_rules": [safety_rule(P, key, {"fact": fact, "equals": value}, level, 1000 if level == "emergency" else 990) for key, fact, value, level in safety], "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    policy = completion_policy(prefix=P, fragment=f, presentation_fact="dyspnea.primary_group", question_budget=76, source_refs=SOURCES)
    common = {"dyspnea.information_source_proxy_and_reliability", "dyspnea.age_life_stage_and_baseline", "symptom.duration", "symptom.dyspnea_onset", "dyspnea.onset_date_time_activity_and_circumstance", "dyspnea.episode_frequency_duration_trend_and_between_episode_baseline", "symptom.dyspnea_at_rest", "symptom.exertional_dyspnea", "dyspnea.exertional_threshold_and_change_from_baseline", "dyspnea.speaking_eating_sleep_selfcare_and_mobility_impact", "dyspnea.oxygen_saturation_device_time_oxygen_and_reliability", "dyspnea.pulmonary_history_and_baseline", "dyspnea.cardiac_history_and_baseline", "dyspnea.current_medicines_inhalers_oxygen_sedatives_opioids_and_changes", "dyspnea.medicine_allergies_and_adverse_reactions", "patient.smoking.status", "dyspnea.prior_assessment_diagnosis_and_followup_plan", "dyspnea.treatment_start_adherence_response_and_adverse_effect", "dyspnea.patient_concern_goal_and_other_detail"}
    policy["required_facts"]["routine"] = sorted(common)
    branches = {
        "acute_sudden": ["dyspnea.respiratory_pattern_accessory_muscle_and_position", "symptom.chest_pain", "dyspnea.chest_pain_location_character_radiation_trigger_and_duration", "symptom.palpitations", "dyspnea.syncope_presyncope_dizziness_and_recovery_detail", "symptom.unilateral_leg_pain_swelling", "dyspnea.vte_risk_surgery_immobility_cancer_prior_vte_estrogen_pregnancy"],
        "acute_progressive_or_infectious": ["symptom.cough", "dyspnea.cough_sputum_color_volume_blood_and_change", "symptom.fever", "dyspnea.fever_infection_contact_and_recent_respiratory_illness", "symptom.wheeze", "dyspnea.prior_exacerbations_ed_visits_admissions_intubation_and_baseline"],
        "exertional_or_functional": ["dyspnea.exertional_threshold_and_change_from_baseline", "dyspnea.anemia_bleeding_and_recent_hemoglobin_context", "symptom.chest_pain", "symptom.palpitations", "dyspnea.cardiac_history_and_baseline"],
        "positional_nocturnal_or_edema": ["symptom.orthopnea", "dyspnea.orthopnea_pillow_count_and_position_detail", "symptom.paroxysmal_nocturnal_dyspnea", "dyspnea.nocturnal_episode_sleep_and_recovery_detail", "dyspnea.edema_weight_gain_nocturia_and_abdominal_swelling", "dyspnea.renal_liver_fluid_and_recent_weight_context"],
        "airway_wheeze_or_cough": ["symptom.cough", "dyspnea.cough_sputum_color_volume_blood_and_change", "symptom.fever", "dyspnea.fever_infection_contact_and_recent_respiratory_illness", "symptom.wheeze", "dyspnea.wheeze_stridor_voice_swallowing_and_choking_detail", "dyspnea.rescue_inhaler_nebulizer_oxygen_use_dose_time_and_response", "dyspnea.inhaler_adherence_technique_spacer_and_action_plan", "dyspnea.spirometry_peak_flow_baseline_personal_best_and_date"],
        "vte_or_post_immobility": ["symptom.unilateral_leg_pain_swelling", "dyspnea.leg_side_swelling_pain_redness_and_onset", "dyspnea.vte_risk_surgery_immobility_cancer_prior_vte_estrogen_pregnancy", "risk.recent_immobility_or_surgery", "history.venous_thromboembolism", "dyspnea.travel_flight_altitude_diving_and_recent_infection_exposure"],
        "known_cardiopulmonary_followup": ["dyspnea.rescue_inhaler_nebulizer_oxygen_use_dose_time_and_response", "dyspnea.inhaler_adherence_technique_spacer_and_action_plan", "dyspnea.spirometry_peak_flow_baseline_personal_best_and_date", "dyspnea.ecg_imaging_labs_and_result_source", "dyspnea.prior_exacerbations_ed_visits_admissions_intubation_and_baseline", "dyspnea.sleep_snoring_apnea_daytime_sleepiness_and_pap_use"],
        "pregnancy_postpartum": ["dyspnea.pregnancy_postpartum_gestation_delivery_and_complications", "dyspnea.vte_risk_surgery_immobility_cancer_prior_vte_estrogen_pregnancy", "dyspnea.anemia_bleeding_and_recent_hemoglobin_context", "dyspnea.edema_weight_gain_nocturia_and_abdominal_swelling"],
        "exposure_altitude_or_toxic": ["dyspnea.occupation_home_pollution_fume_dust_mold_and_animal_exposure", "dyspnea.travel_flight_altitude_diving_and_recent_infection_exposure", "dyspnea.smoking_vaping_pack_years_passive_exposure_and_change"],
        "other_unclear": ["dyspnea.anemia_bleeding_and_recent_hemoglobin_context", "dyspnea.renal_liver_fluid_and_recent_weight_context", "dyspnea.neuromuscular_weakness_swallowing_and_cough_strength", "dyspnea.anxiety_panic_context_after_medical_warning_screen"],
    }
    policy["conditional_required_facts"] = [{"selector_fact": "dyspnea.primary_group", "cases": branches}]
    return policy


def source_docs():
    defs = [
        ("source.nice.ng158.vte", "NICE", "Venous thromboembolic diseases: diagnosis, management and thrombophilia testing", "NG158-updated-2023-08-02", "https://www.nice.org.uk/guidance/ng158/chapter/Recommendations", "clinical_guideline", ["Possible pulmonary embolism history includes breathlessness, chest pain and haemoptysis; unilateral leg symptoms, surgery, immobility, active cancer and previous VTE are relevant context.", "The interview records inputs but does not calculate Wells or PERC scores or diagnose VTE."]),
        ("source.nice.ng115.copd", "NICE", "Chronic obstructive pulmonary disease in over 16s: diagnosis and management", "NG115-updated-2019-07-26", "https://www.nice.org.uk/guidance/ng115/chapter/Recommendations", "clinical_guideline", ["Breathlessness, activity limitation, cough, sputum volume and colour, wheeze, treatment response, inhaler technique, smoking, oedema and exacerbation history support clinician review.", "Pulse oximeter values require measurement context and can be inaccurate, especially around borderline values and in some skin tones."]),
        ("source.nice.ng106.heart-failure", "NICE", "Chronic heart failure in adults: diagnosis and management", "NG106-updated-2025-09-03", "https://www.nice.org.uk/guidance/ng106/chapter/Recommendations", "clinical_guideline", ["Suspected heart failure requires clinical history, examination and tests; symptom history alone does not establish the diagnosis.", "Orthopnoea, nocturnal breathlessness, oedema, weight change, functional limitation, prior cardiac disease and available test results are useful handoff context."]),
        ("source.gina.strategy.2026", "GINA", "Global Strategy for Asthma Management and Prevention", "2026", "https://ginasthma.org/wp-content/uploads/2026/05/GINA-2026-Strategy-Report-WMS.pdf", "clinical_guideline", ["Asthma-oriented history includes variable respiratory symptoms, triggers, night waking, activity limitation, reliever use and response, inhaler technique, adherence and prior severe exacerbations.", "This package records patient-reported features and does not infer asthma or replace objective confirmation."]),
        ("source.nhs.shortness-of-breath", "NHS", "Shortness of breath", "accessed-2026-07-17", "https://www.nhs.uk/symptoms/shortness-of-breath/", "public_health_guidance", ["Gasping, choking, inability to speak, tight or heavy chest, radiating pain, sudden colour change and sudden confusion are emergency warning features.", "Children with grunting, chest recession, colour change, confusion, limpness or poor responsiveness need emergency assessment."]),
        ("source.stom.dyspnea.20260717", "Infoclinic", "STOM dyspnea terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/267036007", "terminology_server", ["Build-time STOM verification confirmed active Dyspnea 267036007, Dyspnea at rest 161941007, Dyspnea on exertion 60845006 and Orthopnea 62744007.", "MRCM returned Finding site and Severity; MRCM is terminology metadata and does not create clinical rules."]),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, assertions in defs:
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "GINA", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-17", "monitor_result": "current_official_source_confirmed", "assertions": assertions})
    research = {"id": "source-manifest.primary-care-dyspnea-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.dyspnea", "generated_clinical_knowledge", "knowledge/generated/respiratory/dyspnea/dyspnea.json", True),
        ("source.mapping.dyspnea", "terminology_mapping", "mappings/terminology/snomed-mrcm-dyspnea.json", False),
        ("source.external.dyspnea", "external_source_manifest", "sources/manifests/primary-care-dyspnea-research.json", False),
        ("source.policy.dyspnea", "runtime_policy", "policies/primary-care-dyspnea-completion.json", True),
    ]
    primary = {"id": "source-manifest.primary-care-dyspnea", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for index, rule in enumerate(f["safety_rules"]):
        fid, value, level = rule["when"]["fact"], rule["when"]["equals"], rule["then"]["safety_level"]
        key = rule["id"].split("safety.")[1]
        out[f"DYSPNEA-{key.upper()}.json"] = {
            "id": f"DYSPNEA-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 8 if key == "child-warning" else 25 + index * 4},
            "initial_statement": {"ko": "숨이 차고 상태가 좋지 않습니다."},
            "hidden_state": {fid: {"value": value}},
            "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 16, "forbidden_assertions": ["diagnosis.pulmonary_embolism", "diagnosis.heart_failure", "diagnosis.asthma"]},
            "provenance": provenance(SOURCES),
        }
    policy = completion(f)
    by_id = {item["fact"]["id"]: item["fact"] for item in f["entries"]}

    def routine(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"][branch])
        values = {}
        for fid in required:
            fact = by_id[fid]
            if fact["value_type"] == "boolean": value = False
            elif fact["value_type"] == "integer": value = 0
            elif fact["value_type"] == "coded": value = fact.get("allowed_values", ["other_unclear"])[0]
            elif fact["value_type"] == "quantity": value = "3 days"
            elif fact["value_type"] == "severity": value = "mild"
            else: value = "특이사항 없음"
            values[fid] = {"value": value}
        values["dyspnea.primary_group"] = {"value": branch}
        values["symptom.dyspnea"] = {"value": "mild"}
        return values

    routine_specs = [
        ("AIRWAY-ROUTINE", "airway_wheeze_or_cough", 31, "쌕쌕거리면서 숨이 조금 찹니다.", {"symptom.wheeze": {"value": True}, "dyspnea.rescue_inhaler_nebulizer_oxygen_use_dose_time_and_response": {"value": "살부타몰 2회 흡입 후 일부 호전"}}, ["diagnosis.asthma"]),
        ("KNOWN-DISEASE-FOLLOWUP", "known_cardiopulmonary_followup", 57, "기존 폐질환 치료 중 숨참 변화를 진료 전에 정리합니다.", {"dyspnea.spirometry_peak_flow_baseline_personal_best_and_date": {"value": "개인 최고 PEF 480, 오늘 390 L/min, 가정 기록"}}, ["diagnosis.copd_exacerbation"]),
        ("OCCUPATIONAL-EXPOSURE", "exposure_altitude_or_toxic", 40, "작업장에서 냄새를 맡은 뒤 숨이 찹니다.", {"dyspnea.occupation_home_pollution_fume_dust_mold_and_animal_exposure": {"value": "도장 작업 중 용제 냄새 뒤 증상, 마스크 미착용"}}, ["diagnosis.toxic_inhalation"]),
        ("UNRELATED-ADDITIONAL-COMMENT", "exertional_or_functional", 45, "걸을 때 숨차고 별도 행정 문의도 있습니다.", {"dyspnea.patient_concern_goal_and_other_detail": {"value": "숨참 외에 회사 제출용 진료확인서 문의를 별도 전달 요청"}}, []),
        ("MULTI-RFE-HEADACHE", "other_unclear", 36, "숨도 차고 두통도 반복됩니다.", {"dyspnea.patient_concern_goal_and_other_detail": {"value": "숨참 외에 반복되는 두통도 별도 문진 요청"}}, ["diagnosis.anxiety"]),
    ]
    for key, branch, age, statement, overrides, forbidden in routine_specs:
        state = routine(branch); state.update(overrides)
        out[f"DYSPNEA-{key}.json"] = {"id": f"DYSPNEA-{key}", "simulation_language": "ko", "persona": {"age": age}, "initial_statement": {"ko": statement}, "hidden_state": state, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 80, "forbidden_assertions": forbidden}, "provenance": provenance(SOURCES)}
    proxy = routine("positional_nocturnal_or_edema")
    proxy.pop("dyspnea.oxygen_saturation_device_time_oxygen_and_reliability")
    out["DYSPNEA-OLDER-PROXY-DATA-ABSENT.json"] = {"id": "DYSPNEA-OLDER-PROXY-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 81}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "어르신이 누우면 숨차다고 해서 보호자가 전화 문진합니다."}, "hidden_state": proxy, "response_behavior": {"dyspnea.oxygen_saturation_device_time_oxygen_and_reliability": {"dataAbsentReason": "not-performed"}}, "expected": {"expected_data_absent_reasons": {"dyspnea.oxygen_saturation_device_time_oxygen_and_reliability": "not-performed"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 80, "forbidden_assertions": ["diagnosis.heart_failure"]}, "provenance": provenance(SOURCES)}
    pain = routine("acute_sudden")
    pain["symptom.chest_pain"] = {"value": True}
    pain["dyspnea.chest_pain_nrs"] = {"value": 6}
    pain["pain.frequency"] = {"value": "daily"}
    out["DYSPNEA-CHEST-PAIN-NRS.json"] = {"id": "DYSPNEA-CHEST-PAIN-NRS", "simulation_language": "ko", "persona": {"age": 48}, "initial_statement": {"ko": "숨참과 가슴 통증이 있습니다."}, "hidden_state": pain, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"dyspnea.chest_pain_nrs": 6}, "expected_max_turns": 80, "forbidden_assertions": ["diagnosis.acute_coronary_syndrome"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Shortness of Breath or Breathing Difficulty", intents=[
        ("intent.characterize_symptom", "Characterize Onset Pattern Severity Functional Impact and Patient Wording"),
        ("intent.screen_red_flags", "Screen Respiratory Airway Cardiac Thromboembolic Pregnancy and Paediatric Warning Features"),
        ("intent.differentiate_common_causes", "Localize Airway Infectious Cardiac Positional Nocturnal and Exposure Features"),
        ("intent.risk_assessment", "Assess Cardiopulmonary VTE Pregnancy Medicine Exposure Measurement Test Treatment and Patient Goals"),
    ])
    primary, research = source_docs()
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": [{"code": "267036007", "display": "Dyspnea (finding)", "concept_active": True, "attribute_count_returned": 20}, {"code": "161941007", "display": "Dyspnea at rest (finding)", "concept_active": True, "attribute_count_returned": 20}, {"code": "60845006", "display": "Dyspnea on exertion (finding)", "concept_active": True, "attribute_count_returned": 20}, {"code": "62744007", "display": "Orthopnea (finding)", "concept_active": True, "attribute_count_returned": 20}],
        "verified_attribute_ids": ["363698007", "246112005"],
        "validation": {"method": "build_time_live_search_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"},
        "dyspnea_semantics": {"diagnosis_inferred": False, "wells_score_calculated": False, "perc_rule_calculated": False, "news2_or_mews_calculated": False, "pulse_oximetry_alone_controls_safety": False, "runtime_terminology_query_required": False},
        "provenance": provenance(["source.stom.dyspnea.20260717"]),
    }
    documents = [
        ("knowledge/base/primary-care-dyspnea.json", graph), ("rules/base/primary-care-dyspnea.json", rules),
        ("knowledge/generated/respiratory/dyspnea/dyspnea.json", f), ("mappings/terminology/snomed-mrcm-dyspnea.json", mapping),
        ("sources/manifests/primary-care-dyspnea.json", primary), ("sources/manifests/primary-care-dyspnea-research.json", research),
        ("policies/primary-care-dyspnea-completion.json", completion(f)),
    ]
    for path, document in documents: write_json(path, document)
    for name, case in cases(f).items(): write_json("simulation/patients/respiratory/dyspnea/" + name, case)


if __name__ == "__main__":
    main()
