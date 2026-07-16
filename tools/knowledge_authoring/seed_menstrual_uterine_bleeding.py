#!/usr/bin/env python3
"""Materialize unreviewed menstrual and uterine-bleeding pre-visit knowledge."""
from profile_support import *

P, RFE = "menstrual-uterine-bleeding", "rfe.menstrual_uterine_bleeding"
M, SN = "mapping.snomed-mrcm.menstrual-uterine-bleeding", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-16T08:00:00Z"
SOURCES = [
    "source.nice.ng88.hmb.2024",
    "source.nice.ng126.early-pregnancy-bleeding.2026",
    "source.acog.aub.557.reaffirmed-2026",
    "source.acog.adolescent-hmb.785.reaffirmed-2023",
    "source.cdc.female-bleeding-disorders.2024",
    "source.stom.menstrual-bleeding.20260716",
]
G = {k: f"group.menstrual.{k}" for k in ("routing", "safety", "pattern", "pain", "obstetric", "bleeding", "context", "followup", "function")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("menstrual.primary_group", "Primary Menstrual or Uterine Bleeding Concern", "coded", "primary-group", "이번 방문은 생리량·기간 증가, 불규칙하거나 건너뛰는 생리, 생리 사이·성관계 후 출혈, 생리통·골반통, 폐경 후 출혈, 임신 가능성이 있는 출혈, 치료 후 추적 중 무엇에 가장 가깝나요?", 230, [G["routing"]], C, allowed_values=["heavy_or_prolonged_menses", "irregular_infrequent_or_absent_menses", "intermenstrual_or_postcoital_bleeding", "dysmenorrhea_or_pelvic_pain", "postmenopausal_bleeding", "possible_pregnancy_related_bleeding", "treatment_or_procedure_followup", "other_unclear"]),
        Q("menstrual.hourly_saturation_with_cardiorespiratory_or_presyncope", "Heavy Bleeding with Instability Symptoms", "boolean", "heavy-instability", "패드·탐폰이 1시간마다 흠뻑 젖는 출혈이 2시간 넘게 이어지면서 흉통, 숨참, 심한 어지럼 또는 쓰러질 듯함이 있나요?", 229, [G["safety"], G["pattern"]], S, safety_relevant=True),
        Q("menstrual.faint_confused_clammy_or_unable_to_stand", "Haemodynamic Warning", "boolean", "shock-warning", "출혈과 함께 실신, 의식 혼란, 창백함·식은땀, 매우 심한 쇠약 또는 서 있기 어려움이 있나요?", 228, [G["safety"]], S, safety_relevant=True),
        Q("menstrual.possible_pregnancy_unilateral_pain_shoulder_tip_or_syncope", "Possible Ectopic Pregnancy Warning", "boolean", "ectopic-warning", "임신 가능성 또는 양성 임신검사가 있으면서 한쪽 심한 아랫배 통증, 어깨끝 통증, 어지럼·실신이 있나요?", 227, [G["safety"], G["obstetric"]], S, safety_relevant=True),
        Q("menstrual.known_pregnancy_heavy_bleeding_severe_pain_or_tissue", "Pregnancy Bleeding Warning", "boolean", "pregnancy-heavy", "임신 중이며 많은 출혈, 심해지는 복통·골반통, 큰 혈전·조직 같은 것이 나오거나 상태가 빠르게 나빠지나요?", 226, [G["safety"], G["obstetric"]], S, safety_relevant=True),
        Q("menstrual.anticoagulant_or_bleeding_disorder_uncontrolled_bleeding", "Antithrombotic or Bleeding Disorder Warning", "boolean", "antithrombotic-warning", "항응고제·항혈소판제를 사용하거나 출혈질환이 있는데 많은 출혈이 멈추지 않거나 반복되나요?", 225, [G["safety"], G["bleeding"]], S, safety_relevant=True),
        Q("menstrual.fever_severe_pelvic_pain_foul_discharge_or_recent_procedure", "Pelvic Infection Warning", "boolean", "infection-warning", "고열, 심한 골반통, 악취 나는 분비물이 있거나 최근 출산·유산·자궁 시술 뒤 통증과 출혈이 악화하나요?", 224, [G["safety"], G["context"]], S, safety_relevant=True),
        Q("menstrual.severe_anemia_chest_pain_dyspnea_or_resting_palpitations", "Severe Anaemia Warning", "boolean", "anemia-warning", "출혈과 함께 가만히 있어도 숨이 차거나 두근거림, 흉통, 실신에 가까운 어지럼 또는 일상생활이 불가능한 쇠약이 있나요?", 223, [G["safety"], G["bleeding"]], S, safety_relevant=True),
        Q("menstrual.postmenopausal_new_or_recurrent_bleeding", "Postmenopausal Bleeding", "boolean", "postmenopausal-warning", "12개월 이상 생리가 없다가 새로 피가 비치거나 출혈이 반복되나요?", 222, [G["safety"], G["pattern"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "76742009"}, mrcm_ref=M),
        Q("menstrual.prepubertal_bleeding_or_uncertain_source", "Prepubertal Bleeding", "boolean", "prepubertal-warning", "초경 전 아이에게 질 출혈이 있거나 피가 질·소변·대변·상처 중 어디에서 나온 것인지 불분명한가요?", 221, [G["safety"], G["routing"]], S, safety_relevant=True),
        Q("menstrual.unwanted_sexual_contact_injury_or_not_safe", "Safeguarding Warning", "boolean", "safeguarding-warning", "원치 않은 성적 접촉·폭력·생식기 손상 가능성이 있거나 지금 안전하지 않나요?", 220, [G["safety"], G["context"]], S, safety_relevant=True),
        Q("menstrual.rapidly_worsening_pelvic_mass_pressure_or_urinary_bowel_obstruction", "Rapid Pelvic Pressure Warning", "boolean", "mass-pressure-warning", "빠르게 커지는 아랫배 덩이·팽만과 심한 압박감, 소변이 안 나오거나 대변이 막히는 증상이 있나요?", 219, [G["safety"], G["context"]], S, safety_relevant=True),

        Q("menstrual.information_source_calendar_app_proxy_and_reliability", "Information Source", "string", "information-source", "누가 답변하고 있으며 본인 기억, 생리 달력·앱, 보호자 관찰, 사진 또는 의료기록 중 무엇에 근거하나요? 서로 다른 기록도 알려주세요.", 205, [G["routing"]], C),
        Q("menstrual.age_menarche_and_reproductive_stage", "Age Menarche and Reproductive Stage", "string", "age-stage", "만 나이, 초경 나이와 현재 초경 전·가임기·폐경 이행기·폐경 후 중 어디에 해당하는지 알려주세요.", 204, [G["routing"], G["pattern"]], R),
        Q("menstrual.last_normal_period_start_and_certainty", "Last Normal Menstrual Period", "string", "lmp", "마지막 정상 생리 시작일과 종료일을 알려주세요. 정확한 기록인지 추정인지도 표시해주세요.", 203, [G["pattern"], G["obstetric"]], C),
        Q("menstrual.current_bleeding_start_end_and_status", "Current Bleeding Episode", "string", "current-episode", "현재 출혈의 시작 날짜·시각, 지금도 계속되는지와 가장 최근 확인 시각을 알려주세요.", 202, [G["pattern"]], C),
        Q("menstrual.cycle_interval_regularity_and_change_from_baseline", "Cycle Interval and Regularity", "string", "cycle", "보통 생리 시작일부터 다음 시작일까지 며칠이며 규칙적인지, 최근 주기 변화와 시작 시점을 알려주세요.", 201, [G["pattern"]], C, terminology_binding={"system": SN, "code": "80182007"}, mrcm_ref=M),
        Q("menstrual.bleeding_duration_days_and_longest_episode", "Bleeding Duration", "string", "duration", "보통 출혈 일수, 이번 출혈 일수와 가장 길었던 기간을 알려주세요.", 200, [G["pattern"]], C),
        Q("menstrual.skipped_cycles_amenorrhea_and_longest_gap", "Skipped Cycles", "string", "skipped-cycles", "생리를 건너뛴 횟수와 가장 길게 없었던 기간, 그 전후 변화를 알려주세요.", 199, [G["pattern"]], C),
        Q("menstrual.pad_tampon_cup_type_saturation_and_change_interval", "Menstrual Product Quantification", "string", "product-quantification", "가장 많은 날 사용하는 패드·탐폰·생리컵의 종류·크기, 흠뻑 젖는 정도와 교체 간격을 알려주세요.", 198, [G["pattern"]], C, terminology_binding={"system": SN, "code": "386692008"}, mrcm_ref=M),
        Q("menstrual.flooding_gushing_double_protection_and_leakage", "Flooding and Leakage", "string", "flooding", "갑자기 쏟아지는 느낌, 이중 생리용품 사용, 밤중 교체 또는 옷·침구까지 새는 일이 얼마나 자주 있나요?", 197, [G["pattern"], G["function"]], C),
        Q("menstrual.clot_size_frequency_and_tissue", "Clots and Tissue", "string", "clots", "혈전의 가장 큰 크기를 동전·포도알 등과 비교하고 빈도, 조직처럼 보이는 것이 있었는지 알려주세요.", 196, [G["pattern"]], C),
        Q("menstrual.intermenstrual_postcoital_or_unexpected_bleeding", "Bleeding Outside Expected Menses", "string", "unexpected-bleeding", "생리 사이, 성관계 후, 운동 후 또는 예상하지 못한 때 피가 비치는 빈도·양·지속을 알려주세요.", 195, [G["pattern"]], R),

        Q("menstrual.pelvic_pain_present", "Pelvic or Menstrual Pain Present", "boolean", "pain-present", "이번 문제와 함께 생리통 또는 아랫배·골반 통증이 있나요?", 190, [G["pain"]], C),
        Q("menstrual.pelvic_pain_nrs", "Pelvic Pain NRS", "integer", "pain-nrs", "[필수] 통증이 있다면 현재 통증을 0부터 10까지 숫자로 알려주세요. 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증입니다.", 189, [G["pain"]], C),
        Q("menstrual.pain_timing_site_laterality_and_course", "Pain Pattern", "string", "pain-pattern", "통증이 생리 전·중·후 언제 시작하고, 아랫배·골반·허리의 정확한 부위와 좌우, 지속·진행 양상을 알려주세요.", 188, [G["pain"]], C, terminology_binding={"system": SN, "code": "266599000"}, mrcm_ref=M),
        Q("menstrual.pain_with_sex_bowel_movement_urination_or_activity", "Pain Associations", "string", "pain-associations", "성관계, 배변, 소변, 운동 또는 자세와 통증의 관계를 알려주세요.", 187, [G["pain"]], D),
        Q("menstrual.pelvic_pressure_fullness_abdominal_distension_or_mass", "Pelvic Pressure or Mass Symptoms", "string", "pressure-mass", "아랫배 압박감·묵직함·팽만, 만져지는 덩이 또는 소변·대변 횟수 변화가 있나요?", 186, [G["pain"], G["context"]], R),
        Q("menstrual.discharge_odor_itch_fever_and_genital_symptoms", "Associated Genital Symptoms", "string", "genital-associated", "분비물의 색·냄새 변화, 가려움·통증, 발열 또는 외음부·질 증상이 함께 있나요?", 185, [G["context"]], D),

        Q("menstrual.pregnancy_possibility_test_result_and_test_date", "Pregnancy Possibility and Test", "string", "pregnancy-test", "임신 가능성, 최근 임신검사 결과·검사일과 임신 가능성이 없다고 판단한 근거를 알려주세요.", 180, [G["obstetric"]], R),
        Q("menstrual.gravida_para_term_preterm_abortion_living", "Obstetric Summary", "string", "obstetric-summary", "산과력을 임신 횟수(G), 출산 횟수(P), 만삭·조산·유산/중절·현재 생존 자녀 수로 알려주세요. 모르면 각각 설명해도 됩니다.", 179, [G["obstetric"]], R),
        Q("menstrual.prior_ectopic_miscarriage_and_pregnancy_complications", "Prior Pregnancy Complications", "string", "pregnancy-history", "자궁외임신, 자연유산·중절, 임신·분만 합병증의 횟수·시기와 치료를 알려주세요.", 178, [G["obstetric"]], R),
        Q("menstrual.delivery_modes_postpartum_hemorrhage_and_last_delivery", "Delivery and Postpartum Bleeding History", "string", "delivery-history", "질식분만·제왕절개 횟수, 마지막 분만일과 분만 후 과다출혈·수혈 경험을 알려주세요.", 177, [G["obstetric"], G["bleeding"]], R),
        Q("menstrual.fertility_goals_and_future_pregnancy_preference", "Fertility Goals", "string", "fertility-goals", "현재 피임 또는 임신 계획과 향후 임신 가능성을 보존하는 것이 치료 선택에서 얼마나 중요한지 알려주세요.", 176, [G["obstetric"], G["followup"]], R),

        Q("menstrual.fatigue_dyspnea_dizziness_palpitations_and_pica", "Anaemia Symptoms", "string", "anemia-symptoms", "피로·창백함, 활동 시 숨참, 어지럼·두근거림, 얼음 등 비음식물을 찾는 증상이 있나요?", 170, [G["bleeding"]], R),
        Q("menstrual.anemia_iron_treatment_transfusion_and_recent_results", "Anaemia and Blood Results", "string", "anemia-results", "빈혈·철결핍 진단, 철분 치료·수혈 경험과 최근 혈색소·혈소판·철 관련 검사값·검사일을 알려주세요.", 169, [G["bleeding"], G["followup"]], R),
        Q("menstrual.heavy_since_menarche_and_other_mucocutaneous_bleeding", "Bleeding Disorder Features", "string", "bleeding-features", "초경 때부터 많은 생리였는지와 이유 없는 코피·잇몸출혈, 쉽게 드는 멍 또는 작은 상처 출혈을 알려주세요.", 168, [G["bleeding"]], R),
        Q("menstrual.bleeding_after_dental_surgery_delivery_or_miscarriage", "Bleeding after Haemostatic Challenges", "string", "challenge-bleeding", "발치·수술·출산·유산 뒤 예상보다 오래 출혈하거나 추가 처치·수혈이 필요했던 적이 있나요?", 167, [G["bleeding"], G["obstetric"]], R),
        Q("menstrual.family_bleeding_disorder_or_heavy_menses", "Family Bleeding History", "string", "family-bleeding", "가족의 출혈질환 진단, 많은 생리, 수술·출산 후 과다출혈이 있으면 관계를 알려주세요.", 166, [G["bleeding"]], R),

        Q("menstrual.contraception_iud_hormone_therapy_and_adherence", "Contraception and Hormone Use", "string", "contraception", "피임약·주사·임플란트·자궁내장치, 폐경 호르몬치료의 종류·시작일·실제 사용과 출혈 변화를 알려주세요.", 160, [G["context"]], R),
        Q("menstrual.anticoagulant_antiplatelet_nsaid_and_other_medicines", "Bleeding-relevant Medicines", "string", "medicines", "항응고제·항혈소판제, 소염진통제와 처방약·일반약·한약·보충제의 이름·용량·횟수·최근 변경을 알려주세요.", 159, [G["context"]], R),
        Q("menstrual.gynecologic_endocrine_and_systemic_history", "Relevant Medical History", "string", "medical-history", "자궁근종·선근증·자궁내막증·다낭성난소, 갑상선·간·신장·혈액질환 또는 암 관련 진단을 알려주세요.", 158, [G["context"]], R),
        Q("menstrual.gynecologic_procedure_surgery_and_pathology_history", "Gynecologic Procedure History", "string", "procedure-history", "자궁경·소파술·근종수술·자궁내막 시술·제왕절개 등 수술·시술 날짜와 병리 결과를 알려주세요.", 157, [G["context"], G["followup"]], R),
        Q("menstrual.cervical_screening_result_and_date", "Cervical Screening Context", "string", "cervical-screening", "최근 자궁경부검사 종류·날짜·결과와 이상 결과 후 추가검사를 알려주세요.", 156, [G["context"], G["followup"]], R),
        Q("menstrual.weight_change_acne_hair_growth_galactorrhea_or_thyroid_symptoms", "Endocrine Features", "string", "endocrine-features", "체중 변화, 여드름·털 증가, 유즙 분비, 더위·추위 민감, 떨림·변비 등 호르몬 관련 증상이 있나요?", 155, [G["context"]], D),
        Q("menstrual.sexual_contact_sti_and_source_of_bleeding_context", "Sexual and Bleeding-source Context", "string", "sexual-context", "답변 가능한 범위에서 최근 성접촉·성매개감염 위험, 성관계 후 출혈과 피가 질·소변·대변 중 어디에서 나온 것 같은지 알려주세요.", 154, [G["context"], G["routing"]], R),

        Q("menstrual.prior_examination_ultrasound_hysteroscopy_and_pathology", "Prior Assessment and Imaging", "string", "prior-assessment", "이전 골반진찰·초음파·자궁경·조직검사의 날짜와 주요 결과, 원본 유무를 알려주세요.", 145, [G["followup"]], R),
        Q("menstrual.prior_treatment_dose_duration_response_and_adverse_effects", "Treatment Response", "string", "treatment-response", "철분, 진통제·지혈제·호르몬약, 자궁내장치 또는 시술의 용량·기간·효과·부작용과 중단 이유를 알려주세요.", 144, [G["followup"]], R),
        Q("menstrual.work_school_sleep_activity_and_material_impact", "Functional and Material Impact", "string", "function", "출혈·통증 때문에 결석·결근, 수면·운동·외출 제한, 생리용품 부담 또는 옷·침구 교체가 얼마나 생기나요?", 135, [G["function"]], R),
        Q("menstrual.patient_concern_goal_and_other_detail", "Patient Concern and Goal", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달할 내용, 가장 걱정하는 점과 이번 진료에서 원하는 도움을 알려주세요.", 90, [G["routing"], G["followup"]], C),
    ]
    safety = [
        ("heavy-instability", "menstrual.hourly_saturation_with_cardiorespiratory_or_presyncope", "emergency"),
        ("shock-warning", "menstrual.faint_confused_clammy_or_unable_to_stand", "emergency"),
        ("ectopic-warning", "menstrual.possible_pregnancy_unilateral_pain_shoulder_tip_or_syncope", "emergency"),
        ("pregnancy-heavy", "menstrual.known_pregnancy_heavy_bleeding_severe_pain_or_tissue", "emergency"),
        ("antithrombotic-warning", "menstrual.anticoagulant_or_bleeding_disorder_uncontrolled_bleeding", "urgent"),
        ("infection-warning", "menstrual.fever_severe_pelvic_pain_foul_discharge_or_recent_procedure", "urgent"),
        ("anemia-warning", "menstrual.severe_anemia_chest_pain_dyspnea_or_resting_palpitations", "emergency"),
        ("postmenopausal-warning", "menstrual.postmenopausal_new_or_recurrent_bleeding", "urgent"),
        ("prepubertal-warning", "menstrual.prepubertal_bleeding_or_uncertain_source", "urgent"),
        ("safeguarding-warning", "menstrual.unwanted_sexual_contact_injury_or_not_safe", "emergency"),
        ("mass-pressure-warning", "menstrual.rapidly_worsening_pelvic_mass_pressure_or_urinary_bowel_obstruction", "urgent"),
    ]
    refresh = default_refresh(); refresh.update({"last_assessed_at": "2026-07-16", "next_monitor_at": "2026-07-17", "next_full_review_at": "2027-01-12"})
    return {"id": "knowledge.generated.menstrual-uterine-bleeding", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-menstrual-uterine-bleeding-research", "default_refresh": refresh, "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": [safety_rule(P, k, {"fact": f, "equals": True}, l, 1000 if l == "emergency" else 990) for k, f, l in safety], "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="menstrual.primary_group", question_budget=80, source_refs=SOURCES)
    common = [item["fact"]["id"] for item in f["entries"] if not item["fact"].get("safety_relevant") and item["fact"]["id"] not in {"menstrual.primary_group", "menstrual.pelvic_pain_nrs"}]
    p["required_facts"]["routine"] = common
    cases = {value: [] for value in f["entries"][0]["fact"]["allowed_values"]}
    cases["dysmenorrhea_or_pelvic_pain"] = ["menstrual.pelvic_pain_nrs"]
    cases["possible_pregnancy_related_bleeding"] = ["menstrual.pelvic_pain_nrs"]
    p["conditional_required_facts"] = [{"selector_fact": "menstrual.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nice.ng88.hmb.2024", "NICE", "Heavy menstrual bleeding: assessment and management", "NG88-reviewed-2024", "https://www.nice.org.uk/guidance/ng88/chapter/Recommendations", "clinical_guideline", ["History covers bleeding nature, persistent intermenstrual bleeding, pelvic pain or pressure, quality-of-life impact, comorbidities and prior treatment.", "Full blood count is recommended for all with heavy menstrual bleeding; coagulation testing is considered when heavy bleeding began at menarche with personal or family bleeding history."]),
        ("source.nice.ng126.early-pregnancy-bleeding.2026", "NICE", "Ectopic pregnancy and miscarriage: symptoms and initial assessment", "NG126-updated-2026-06-17", "https://www.nice.org.uk/guidance/NG126/chapter/symptoms-and-signs-of-ectopic-pregnancy-and-initial-assessment", "clinical_guideline", ["Potential ectopic pregnancy symptoms include pelvic pain, amenorrhoea, vaginal bleeding, dizziness or syncope and shoulder-tip pain; atypical presentation is common.", "Haemodynamic instability or significant concern about pain or bleeding requires direct emergency assessment."]),
        ("source.acog.aub.557.reaffirmed-2026", "ACOG", "Management of Acute Abnormal Uterine Bleeding in Nonpregnant Reproductive-Aged Women", "CO557-reaffirmed-2026", "https://www.acog.org/clinical/clinical-guidance/committee-opinion/articles/2013/04/management-of-acute-abnormal-uterine-bleeding-in-nonpregnant-reproductive-aged-women", "clinical_guideline", ["Initial acute bleeding assessment includes prompt evaluation for hypovolaemia and haemodynamic instability.", "Clinical stability, bleeding severity, medical history, treatment response and future fertility affect clinician decisions; the runtime does not diagnose PALM-COEIN causes."]),
        ("source.acog.adolescent-hmb.785.reaffirmed-2023", "ACOG", "Screening and Management of Bleeding Disorders in Adolescents With Heavy Menstrual Bleeding", "CO785-reaffirmed-2023", "https://www.acog.org/clinical/clinical-guidance/committee-opinion/articles/2019/09/screening-and-management-of-bleeding-disorders-in-adolescents-with-heavy-menstrual-bleeding", "clinical_guideline", ["Adolescent evaluation includes anaemia, endocrine anovulation and bleeding-disorder assessment, with haemodynamic stability checked in acute heavy bleeding.", "History includes duration, flooding, rapid product saturation, anaemia treatment, family bleeding disorders and bleeding after dental work, surgery, delivery or miscarriage."]),
        ("source.cdc.female-bleeding-disorders.2024", "CDC", "Signs and Symptoms of Bleeding Disorders in Women", "2024-05-15", "https://www.cdc.gov/female-blood-disorders/signs-symptoms/index.html", "public_health_guidance", ["Heavy bleeding clues include duration over seven days, flooding that limits activities, large clots and saturation of a menstrual product hourly or more often.", "Anaemia, unexplained nosebleeds, bruising, procedural bleeding and family bleeding-disorder history are relevant patient-reportable features."]),
        ("source.stom.menstrual-bleeding.20260716", "Infoclinic", "STOM menstrual and uterine bleeding terminology lookup", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["Build-time lookup confirmed active Menorrhagia 386692008, Irregular periods 80182007, Dysmenorrhea 266599000 and Postmenopausal bleeding 76742009 concepts.", "MRCM for Menorrhagia returned Severity, Clinical course and Finding site among allowed attributes; terminology does not determine diagnosis or urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"ACOG", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-16", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-menstrual-uterine-bleeding-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.menstrual-uterine-bleeding", "generated_clinical_knowledge", "knowledge/generated/womens-health/menstrual-uterine-bleeding/menstrual-uterine-bleeding.json", True), ("source.mapping.menstrual-uterine-bleeding", "terminology_mapping", "mappings/terminology/snomed-mrcm-menstrual-uterine-bleeding.json", False), ("source.external.menstrual-uterine-bleeding", "external_source_manifest", "sources/manifests/primary-care-menstrual-uterine-bleeding-research.json", False), ("source.policy.menstrual-uterine-bleeding", "runtime_policy", "policies/primary-care-menstrual-uterine-bleeding-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-menstrual-uterine-bleeding", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level, key = rule["when"]["fact"], rule["then"]["safety_level"], rule["id"].split("safety.")[1]
        out[f"MENSTRUAL-{key.upper()}.json"] = {"id": f"MENSTRUAL-{key.upper()}", "simulation_language": "ko", "persona": {"age": 11 + i * 6}, "initial_statement": {"ko": "생리와 다른 출혈이 있어요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 40, "forbidden_assertions": ["diagnosis.ectopic_pregnancy", "diagnosis.endometrial_cancer", "diagnosis.bleeding_disorder"]}, "provenance": provenance(SOURCES)}
    policy, by_id = completion(f), {x["fact"]["id"]: x["fact"] for x in f["entries"]}
    def routine(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"][branch]); values = {}
        for fid in required:
            fact = by_id[fid]; values[fid] = {"value": False if fact["value_type"] == "boolean" else 0 if fact["value_type"] == "integer" else fact.get("allowed_values", ["없음"])[0] if fact["value_type"] == "coded" else "없음"}
        values["menstrual.primary_group"] = {"value": branch}; return values
    heavy = routine("heavy_or_prolonged_menses"); heavy["menstrual.pad_tampon_cup_type_saturation_and_change_interval"] = {"value": "대형 패드가 가장 많은 날 약 2시간마다 흠뻑 젖음"}; heavy["menstrual.work_school_sleep_activity_and_material_impact"] = {"value": "밤에 한 번 교체하고 출근은 가능"}
    out["MENSTRUAL-ROUTINE-HEAVY-CLINICIAN-HANDOFF.json"] = {"id": "MENSTRUAL-ROUTINE-HEAVY-CLINICIAN-HANDOFF", "simulation_language": "ko", "persona": {"age": 37}, "initial_statement": {"ko": "최근 생리 양이 많아졌어요."}, "hidden_state": heavy, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 90, "expected_known_facts": {"menstrual.pad_tampon_cup_type_saturation_and_change_interval": "대형 패드가 가장 많은 날 약 2시간마다 흠뻑 젖음"}, "forbidden_assertions": ["diagnosis.fibroid", "diagnosis.coagulopathy"]}, "provenance": provenance(SOURCES)}
    pain = routine("dysmenorrhea_or_pelvic_pain"); pain["menstrual.pelvic_pain_present"] = {"value": True}; pain["menstrual.pelvic_pain_nrs"] = {"value": 7}; pain["pain.frequency"] = {"value": "daily"}
    out["MENSTRUAL-PAIN-MANDATORY-NRS.json"] = {"id": "MENSTRUAL-PAIN-MANDATORY-NRS", "simulation_language": "ko", "persona": {"age": 26}, "initial_statement": {"ko": "생리할 때 골반통이 심해요."}, "hidden_state": pain, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"menstrual.pelvic_pain_nrs": 7}, "expected_max_turns": 90, "forbidden_assertions": ["diagnosis.endometriosis"]}, "provenance": provenance(SOURCES)}
    absent = routine("irregular_infrequent_or_absent_menses"); absent.pop("menstrual.last_normal_period_start_and_certainty"); absent.pop("menstrual.information_source_calendar_app_proxy_and_reliability")
    out["MENSTRUAL-IRREGULAR-DATA-ABSENT.json"] = {"id": "MENSTRUAL-IRREGULAR-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 19}, "initial_statement": {"ko": "생리가 불규칙한데 날짜는 잘 모르겠어요."}, "hidden_state": absent, "response_behavior": {"menstrual.last_normal_period_start_and_certainty": {"dataAbsentReason": "asked-unknown"}, "menstrual.information_source_calendar_app_proxy_and_reliability": {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {"menstrual.last_normal_period_start_and_certainty": "asked-unknown", "menstrual.information_source_calendar_app_proxy_and_reliability": "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 90, "forbidden_assertions": ["diagnosis.pcos"]}, "provenance": provenance(SOURCES)}
    proxy = routine("heavy_or_prolonged_menses"); proxy["menstrual.information_source_calendar_app_proxy_and_reliability"] = {"value": "청소년 본인과 보호자가 함께 답하며 생리 앱 기록을 확인함"}
    out["MENSTRUAL-ADOLESCENT-PROXY-REMOTE.json"] = {"id": "MENSTRUAL-ADOLESCENT-PROXY-REMOTE", "simulation_language": "ko", "persona": {"age": 15}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "video", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "아이 생리 양이 많아 보호자와 함께 답합니다."}, "hidden_state": proxy, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 90, "forbidden_assertions": ["diagnosis.bleeding_disorder", "diagnosis.abuse"]}, "provenance": provenance(SOURCES)}
    extra = routine("treatment_or_procedure_followup"); extra["menstrual.patient_concern_goal_and_other_detail"] = {"value": "출혈 상담 외에 예약 시간 변경 요청도 전달하고 싶음"}
    out["MENSTRUAL-UNRELATED-ADDITIONAL-COMMENT.json"] = {"id": "MENSTRUAL-UNRELATED-ADDITIONAL-COMMENT", "simulation_language": "ko", "persona": {"age": 43}, "initial_statement": {"ko": "출혈 치료 후 점검과 다른 요청이 있어요."}, "hidden_state": extra, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"menstrual.patient_concern_goal_and_other_detail": "출혈 상담 외에 예약 시간 변경 요청도 전달하고 싶음"}, "expected_max_turns": 90, "forbidden_assertions": ["diagnosis.nonadherence"]}, "provenance": provenance(SOURCES)}
    multi = routine("intermenstrual_or_postcoital_bleeding"); multi["menstrual.patient_concern_goal_and_other_detail"] = {"value": "예상 밖 출혈 외에 배뇨통도 별도 문진을 원함"}
    out["MENSTRUAL-MULTI-RFE-URINARY.json"] = {"id": "MENSTRUAL-MULTI-RFE-URINARY", "simulation_language": "ko", "persona": {"age": 31}, "initial_statement": {"ko": "생리 사이 출혈과 배뇨통이 있어요."}, "hidden_state": multi, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 90, "forbidden_assertions": ["diagnosis.sti", "diagnosis.uti"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Menstrual Concern or Abnormal Uterine Bleeding", intents=[("intent.characterize_symptom", "Characterize Menstrual Pattern Bleeding Quantity and Pain"), ("intent.screen_red_flags", "Screen Haemodynamic Pregnancy Infection Anaemia and Safeguarding Warnings"), ("intent.differentiate_common_causes", "Assess Pregnancy Bleeding Endocrine Structural Iatrogenic and Haemostatic Context"), ("intent.risk_assessment", "Assess Obstetric History Function Prior Evaluation Treatment and Goals")])
    primary, research = source_docs()
    concepts = [("386692008", "Menorrhagia (finding)"), ("80182007", "Irregular periods (finding)"), ("266599000", "Dysmenorrhea (disorder)"), ("76742009", "Postmenopausal bleeding (finding)")]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": 0} for c, d in concepts], "verified_attribute_ids": ["246112005", "363714003", "363698007"], "validation": {"method": "build_time_live_mapping_search_fhir_lookup_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "bleeding_semantics": {"pregnancy_status_inferred": False, "bleeding_source_inferred": False, "diagnosis_inferred": False, "pal_m_coein_classification_inferred": False, "runtime_terminology_query_required": False}, "provenance": provenance(["source.stom.menstrual-bleeding.20260716"])}
    docs = [("knowledge/base/primary-care-menstrual-uterine-bleeding.json", graph), ("rules/base/primary-care-menstrual-uterine-bleeding.json", rules), ("knowledge/generated/womens-health/menstrual-uterine-bleeding/menstrual-uterine-bleeding.json", f), ("mappings/terminology/snomed-mrcm-menstrual-uterine-bleeding.json", mapping), ("sources/manifests/primary-care-menstrual-uterine-bleeding.json", primary), ("sources/manifests/primary-care-menstrual-uterine-bleeding-research.json", research), ("policies/primary-care-menstrual-uterine-bleeding-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/womens-health/menstrual-uterine-bleeding/" + name, case)


if __name__ == "__main__":
    main()
