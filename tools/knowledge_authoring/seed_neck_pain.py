#!/usr/bin/env python3
"""Materialize unreviewed neck-pain and cervical-symptom pre-visit knowledge."""
from profile_support import *

P, RFE = "neck-pain", "rfe.neck_pain"
M, SN = "mapping.snomed-mrcm.neck-pain", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-16T05:00:00Z"
SOURCES = [
    "source.nice.ng127.cervical.2023",
    "source.acr.cervical-pain-radiculopathy.2024",
    "source.cdc.meningococcal-symptoms.2026",
    "source.stom.neck-pain.20260716",
]
G = {k: f"group.neck.{k}" for k in ("routing", "safety", "character", "neurologic", "context", "function", "followup")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("neck.primary_group", "Primary Neck Presentation", "coded", "primary-group", "이번 방문은 목 중심 통증·뻣뻣함, 어깨·팔로 뻗치는 증상, 외상 뒤 증상, 두통·발열과 동반된 목 경직, 시술·수술 또는 기존 경추질환 추적 중 무엇에 가장 가깝나요?", 210, [G["routing"]], C, allowed_values=["axial_pain_or_stiffness", "arm_radiating_or_neurologic", "post_trauma", "headache_fever_or_systemic", "established_cervical_condition_followup", "other_unclear"]),
        Q("neck.major_trauma_or_high_risk_mechanism", "Major Cervical Trauma", "boolean", "major-trauma", "교통사고, 높은 곳 낙상, 다이빙, 목에 강한 충격 뒤 심한 통증이 생겼거나 목을 움직일 수 없나요?", 209, [G["safety"], G["context"]], S, safety_relevant=True),
        Q("neck.new_bilateral_limb_weakness_or_numbness", "Bilateral Limb Neurologic Warning", "boolean", "bilateral-neurologic", "새로 양팔 또는 팔·다리에 힘이 빠지거나 감각이 둔해졌나요?", 208, [G["safety"], G["neurologic"]], S, safety_relevant=True),
        Q("neck.gait_disturbance_clumsy_hands_or_progressive_weakness", "Possible Cervical Cord Warning", "boolean", "cord-warning", "걷기가 불안해지거나 손이 서툴러 물건을 자주 떨어뜨리고, 팔·다리 힘 빠짐이 진행하나요?", 207, [G["safety"], G["neurologic"]], S, safety_relevant=True),
        Q("neck.new_bladder_bowel_or_saddle_change", "Bladder Bowel Neurologic Warning", "boolean", "bladder-bowel", "목 증상과 함께 새 소변·대변 조절 문제 또는 회음부 감각 변화가 생겼나요?", 206, [G["safety"], G["neurologic"]], S, safety_relevant=True),
        Q("neck.breathing_swallowing_drooling_or_airway_compromise", "Airway or Swallowing Warning", "boolean", "airway-swallow", "목이 붓거나 뻣뻣하면서 숨쉬기 어렵고, 침도 삼키기 어렵거나 침을 흘리나요?", 205, [G["safety"]], S, safety_relevant=True),
        Q("neck.fever_severe_headache_stiffness_confusion_or_rash", "Meningeal Infection Warning", "boolean", "meningeal-warning", "발열과 심한 두통·목 경직이 함께 있으면서 혼란, 반복 구토, 빛이 몹시 불편함 또는 눌러도 사라지지 않는 발진이 있나요?", 204, [G["safety"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "161882006"}, mrcm_ref=M),
        Q("neck.sudden_severe_neck_head_pain_with_focal_deficit", "Sudden Neurovascular Warning", "boolean", "vascular-warning", "갑작스러운 매우 심한 목·머리 통증과 함께 얼굴 처짐, 한쪽 힘 빠짐, 말·시야 변화 또는 심한 균형 장애가 생겼나요?", 203, [G["safety"], G["neurologic"]], S, safety_relevant=True),
        Q("neck.cancer_immunosuppression_infection_with_systemic_warning", "Serious Systemic Context", "boolean", "systemic-warning", "암, 면역저하, 최근 심한 감염 또는 주사 약물 사용력이 있으면서 발열·오한, 밤에도 심한 통증 또는 빠른 악화가 있나요?", 202, [G["safety"], G["context"]], S, safety_relevant=True),
        Q("neck.child_torticollis_drooling_stridor_or_ill_appearance", "Child Acute Neck Warning", "boolean", "child-warning", "아이의 목이 갑자기 한쪽으로 돌아간 채 움직이지 않고, 침 흘림·숨 쉴 때 거친 소리·고열 또는 매우 아파 보이는 상태가 있나요?", 201, [G["safety"]], S, safety_relevant=True),
        Q("neck.pregnancy_postpartum_severe_headache_or_neurologic_warning", "Pregnancy Postpartum Warning", "boolean", "pregnancy-warning", "임신 중이거나 출산 후 6주 이내이며 심한 두통·시야 변화·경련·한쪽 증상 또는 매우 높은 혈압과 새 목 통증이 함께 있나요?", 200, [G["safety"], G["context"]], S, safety_relevant=True),

        Q("neck.information_source_proxy_and_reliability", "Information Source", "string", "information-source", "누가 답변하고 있으며 본인 경험, 보호자 관찰, 사진·영상 또는 의료기록 중 무엇에 근거하나요? 서로 다른 설명이 있다면 함께 알려주세요.", 190, [G["routing"]], C),
        Q("neck.age_and_relevant_demographics", "Age and Demographics", "string", "age-demographics", "만 나이와 증상 해석에 필요한 임신·산후 여부 등 관련 정보를 알려주세요.", 189, [G["routing"], G["context"]], R),
        Q("neck.onset_date_time_and_speed", "Onset", "string", "onset", "목 증상이 처음 시작된 날짜·시각과 갑자기 또는 서서히 시작했는지 알려주세요.", 188, [G["character"]], C),
        Q("neck.duration_course_frequency_and_progression", "Course and Frequency", "string", "course", "계속되는지 간헐적인지, 한 번에 얼마나 지속되는지와 좋아짐·악화·반복 양상을 알려주세요.", 187, [G["character"]], C),
        Q("neck.exact_site_laterality_and_extent", "Site and Laterality", "string", "site-laterality", "목 앞·뒤·옆, 목덜미 또는 어깨선 중 정확한 부위와 왼쪽·오른쪽·가운데, 퍼지는 범위를 알려주세요.", 186, [G["character"]], C, terminology_binding={"system": SN, "code": "81680005"}, mrcm_ref=M),
        Q("neck.pain_nrs_current_worst_and_rest", "Pain NRS", "string", "pain-nrs", "통증이 있다면 0은 통증 없음, 10은 상상할 수 있는 가장 심한 통증일 때 현재·가장 심할 때·쉴 때 점수를 각각 알려주세요. 의료진 제출을 위한 필수 통증 항목입니다.", 185, [G["character"]], C),
        Q("neck.pain_quality_and_stiffness", "Pain Quality and Stiffness", "string", "quality", "뻐근함·쑤심·찌름·타는 느낌·전기 오는 느낌·압박감 중 가까운 양상과 뻣뻣함 정도를 알려주세요.", 184, [G["character"]], C),
        Q("neck.radiation_to_head_shoulder_arm_hand_or_chest", "Radiation", "string", "radiation", "통증이나 이상감각이 뒤통수·어깨·날개뼈·팔·손 또는 가슴으로 뻗치나요? 어느 쪽 어느 손가락까지인지 알려주세요.", 183, [G["character"], G["neurologic"]], C, terminology_binding={"system": SN, "code": "54404000"}, mrcm_ref=M),
        Q("neck.movement_posture_cough_strain_and_activity_triggers", "Provoking Factors", "string", "triggers", "목 돌리기·숙이기·젖히기, 팔 움직임, 오래 앉기·화면 보기, 기침·힘주기 또는 운동 중 무엇이 재현·악화하나요?", 182, [G["character"]], D),
        Q("neck.relief_position_rest_heat_medicine_or_support", "Relieving Factors", "string", "relief", "자세 변경, 휴식, 온찜질·냉찜질, 목 지지 또는 약으로 얼마나 좋아지고 효과가 얼마나 지속되나요?", 181, [G["character"]], D),
        Q("neck.range_of_motion_and_torticollis", "Range of Motion", "string", "range-motion", "목을 좌우·앞뒤로 움직일 수 있는 범위와 한쪽으로 기울거나 돌아간 상태, 움직임 제한을 알려주세요.", 180, [G["character"]], C),
        Q("neck.night_rest_pain_and_sleep_interruption", "Night and Rest Pain", "string", "night-rest", "가만히 있거나 밤에 더 아픈지, 통증으로 잠에서 깨는 횟수와 자세 영향을 알려주세요.", 179, [G["character"], G["function"]], R),

        Q("neck.arm_hand_numbness_tingling_distribution", "Arm or Hand Sensory Change", "string", "sensory", "어깨·팔·손의 저림, 감각 둔함 또는 전기 오는 느낌의 부위·손가락·좌우와 지속 시간을 알려주세요.", 170, [G["neurologic"]], D),
        Q("neck.arm_hand_weakness_grip_and_dexterity", "Upper Limb Weakness and Dexterity", "string", "weakness-dexterity", "팔 들기, 손아귀 힘, 단추·글씨·젓가락 사용과 물건을 떨어뜨리는 변화가 있나요? 시작과 진행을 알려주세요.", 169, [G["neurologic"], G["function"]], R),
        Q("neck.leg_symptoms_gait_balance_and_falls", "Leg Gait and Balance", "string", "gait-balance", "다리 힘·감각 변화, 걷기·균형·계단 문제, 거의 넘어짐 또는 실제 낙상이 있나요?", 168, [G["neurologic"], G["function"]], R),
        Q("neck.headache_dizziness_visual_speech_or_facial_symptoms", "Associated Head and Neurologic Symptoms", "string", "head-neuro", "두통·어지럼, 복시·시야 변화, 말 어눌함, 얼굴 감각·움직임 변화가 함께 있나요?", 167, [G["neurologic"]], R),
        Q("neck.fever_chills_weight_loss_night_sweats_or_rash", "Systemic Symptoms", "string", "systemic", "발열·오한, 설명되지 않는 체중 감소, 식은땀·심한 피로 또는 발진이 있나요?", 166, [G["context"]], R),

        Q("neck.recent_injury_whiplash_sport_or_repetitive_load", "Injury and Load", "string", "injury-load", "교통사고·넘어짐·스포츠·무거운 물건·갑작스런 회전 또는 반복 작업과 증상 시작의 관계를 알려주세요.", 160, [G["context"]], R),
        Q("neck.occupation_ergonomics_screen_and_driving_exposure", "Occupation and Ergonomics", "string", "occupation", "직업·학업, 화면·휴대전화 사용, 운전, 고정 자세·진동·머리 위 작업 시간과 증상 변화를 알려주세요.", 159, [G["context"], G["function"]], R),
        Q("neck.infection_dental_ent_or_recent_procedure_context", "Recent Infection or Procedure", "string", "infection-procedure", "최근 감염, 인후·귀·치과 문제, 예방접종, 목 주변 시술·주사 또는 수술과 날짜를 알려주세요.", 158, [G["context"]], R),
        Q("neck.cancer_immunosuppression_osteoporosis_inflammatory_or_vascular_history", "Relevant Medical History", "string", "medical-history", "암·면역저하, 골다공증, 류마티스·염증질환, 혈관질환 또는 반복 감염 진단을 알려주세요.", 157, [G["context"]], R),
        Q("neck.prior_cervical_disease_surgery_injection_or_hardware", "Cervical History", "string", "cervical-history", "이전 목디스크·협착·신경 문제, 목 수술·주사·고정기구와 시행일, 이후 상태를 알려주세요.", 156, [G["context"], G["followup"]], R),
        Q("neck.current_medicines_anticoagulant_steroid_and_adherence", "Current Medicines", "string", "medicines", "현재 복용·사용하는 처방약·일반약·한약·보충제의 이름·용량·횟수와 항응고제·스테로이드 사용, 실제 복용 상태를 알려주세요.", 155, [G["context"]], R),
        Q("neck.allergies_and_adverse_reactions", "Allergies", "string", "allergies", "약물·조영제·접착제 등 알레르기와 나타났던 반응을 알려주세요.", 154, [G["context"]], R),
        Q("neck.family_neurologic_inflammatory_or_spine_history", "Family History", "string", "family-history", "가족의 신경질환, 염증성 관절질환 또는 중요한 척추질환이 있으면 관계와 발병 나이를 알려주세요.", 153, [G["context"]], R),
        Q("neck.smoking_alcohol_substance_and_occupational_exposure", "Social and Exposure History", "string", "social-exposure", "흡연·음주·기타 물질 사용과 분진·화학물질·진동·중량물 등 직업 노출을 알려주세요.", 152, [G["context"]], R),

        Q("neck.prior_examination_diagnosis_and_specialist_assessment", "Prior Assessment", "string", "prior-assessment", "이전에 진찰받은 기관·진료과·날짜와 들은 진단 또는 미확정 설명을 그대로 알려주세요.", 145, [G["followup"]], R),
        Q("neck.prior_imaging_tests_dates_and_results", "Prior Tests", "string", "prior-tests", "목 X선·CT·MRI, 근전도·신경검사 또는 혈액검사의 날짜·주요 결과와 원본 유무를 알려주세요.", 144, [G["followup"]], R),
        Q("neck.prior_treatment_duration_response_and_adverse_effects", "Treatment Response", "string", "treatment-response", "사용한 약·물리치료·운동·주사·시술의 기간, 효과·부작용과 중단 이유를 알려주세요.", 143, [G["followup"]], R),
        Q("neck.function_sleep_work_selfcare_driving_and_activity", "Functional Impact", "string", "function", "수면, 세수·옷입기, 일·학업, 운전, 운동과 돌봄 활동이 얼마나 제한되며 도움이 필요한지 알려주세요.", 135, [G["function"]], R),
        Q("neck.patient_concern_goal_and_other_detail", "Patient Goal and Additional Detail", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달할 내용, 가장 걱정하는 원인과 이번 진료에서 원하는 도움을 알려주세요.", 90, [G["routing"], G["followup"]], C),
    ]
    safety = [
        ("major-trauma", "neck.major_trauma_or_high_risk_mechanism", "emergency"),
        ("bilateral-neurologic", "neck.new_bilateral_limb_weakness_or_numbness", "emergency"),
        ("cord-warning", "neck.gait_disturbance_clumsy_hands_or_progressive_weakness", "urgent"),
        ("bladder-bowel", "neck.new_bladder_bowel_or_saddle_change", "emergency"),
        ("airway-swallow", "neck.breathing_swallowing_drooling_or_airway_compromise", "emergency"),
        ("meningeal-warning", "neck.fever_severe_headache_stiffness_confusion_or_rash", "emergency"),
        ("vascular-warning", "neck.sudden_severe_neck_head_pain_with_focal_deficit", "emergency"),
        ("systemic-warning", "neck.cancer_immunosuppression_infection_with_systemic_warning", "urgent"),
        ("child-warning", "neck.child_torticollis_drooling_stridor_or_ill_appearance", "emergency"),
        ("pregnancy-warning", "neck.pregnancy_postpartum_severe_headache_or_neurologic_warning", "emergency"),
    ]
    refresh = default_refresh()
    refresh.update({"last_assessed_at": "2026-07-16", "next_monitor_at": "2026-07-17", "next_full_review_at": "2027-01-12"})
    return {"id": "knowledge.generated.neck-pain", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-neck-pain-research", "default_refresh": refresh, "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": [safety_rule(P, k, {"fact": f, "equals": True}, l, 1000 if l == "emergency" else 990) for k, f, l in safety], "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="neck.primary_group", question_budget=65, source_refs=SOURCES)
    common = [item["fact"]["id"] for item in f["entries"] if not item["fact"].get("safety_relevant") and item["fact"]["id"] != "neck.primary_group"]
    p["required_facts"]["routine"] = common
    p["conditional_required_facts"] = [{"selector_fact": "neck.primary_group", "cases": {value: [] for value in f["entries"][0]["fact"]["allowed_values"]}}]
    return p


def source_docs():
    defs = [
        ("source.nice.ng127.cervical.2023", "NICE", "Suspected neurological conditions: recognition and referral", "NG127-updated-2023", "https://www.nice.org.uk/guidance/ng127/chapter/Recommendations-for-adults-aged-over-16", "clinical_guideline", ["Cervical radiculopathy referral assessment includes gait disturbance, clumsy or weak hands or legs, brisk reflexes, extensor plantar responses and new bladder or bowel disturbance.", "Persistent disabling or uncontrolled pain and age under 20 modify referral decisions; rapidly progressive weakness and swallowing or breathing compromise require urgent assessment."]),
        ("source.acr.cervical-pain-radiculopathy.2024", "American College of Radiology", "ACR Appropriateness Criteria: Cervical Pain or Cervical Radiculopathy", "revised-2024", "https://acsearch.acr.org/docs/69426/Narrative/", "clinical_guideline", ["Imaging pathways distinguish acute or increasing pain, radiculopathy, trauma, infection, malignancy and prior cervical surgery contexts.", "The source supports collecting red flags and prior procedure context but is not used by runtime to order or diagnose."]),
        ("source.cdc.meningococcal-symptoms.2026", "CDC", "Meningococcal Disease Symptoms and Complications", "2026-03-06", "https://www.cdc.gov/meningococcal/symptoms/", "public_health_guidance", ["Meningitis symptoms can include fever, headache, stiff neck, confusion, nausea or vomiting and photophobia.", "Meningococcal disease can worsen rapidly and requires immediate medical attention."]),
        ("source.stom.neck-pain.20260716", "Infoclinic", "STOM neck-pain terminology and MRCM lookup", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["Build-time lookup confirmed active Neck pain (finding) 81680005, Cervical radiculopathy (disorder) 54404000 and Neck stiffness (finding) 161882006 with Korean descriptions.", "MRCM lookup for Neck pain returned Severity 246112005 and Finding site 363698007 among allowed attributes; terminology does not determine urgency or diagnosis."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"American College of Radiology", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-16", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-neck-pain-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.neck-pain", "generated_clinical_knowledge", "knowledge/generated/musculoskeletal/neck-pain/neck-pain.json", True), ("source.mapping.neck-pain", "terminology_mapping", "mappings/terminology/snomed-mrcm-neck-pain.json", False), ("source.external.neck-pain", "external_source_manifest", "sources/manifests/primary-care-neck-pain-research.json", False), ("source.policy.neck-pain", "runtime_policy", "policies/primary-care-neck-pain-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-neck-pain", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level, key = rule["when"]["fact"], rule["then"]["safety_level"], rule["id"].split("safety.")[1]
        out[f"NECK-{key.upper()}.json"] = {"id": f"NECK-{key.upper()}", "simulation_language": "ko", "persona": {"age": 8 + i * 7}, "initial_statement": {"ko": "목이 아프고 뻣뻣해요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 35, "forbidden_assertions": ["diagnosis.cervical_myelopathy", "diagnosis.meningitis", "diagnosis.cervical_dissection"]}, "provenance": provenance(SOURCES)}
    policy, by_id = completion(f), {x["fact"]["id"]: x["fact"] for x in f["entries"]}
    def routine(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"]); values = {}
        for fid in required:
            fact = by_id[fid]; values[fid] = {"value": False if fact["value_type"] == "boolean" else fact.get("allowed_values", ["없음"])[0] if fact["value_type"] == "coded" else "없음"}
        values["neck.primary_group"] = {"value": branch}; return values
    axial = routine("axial_pain_or_stiffness"); axial["neck.pain_nrs_current_worst_and_rest"] = {"value": "현재 3, 최악 6, 휴식 1"}; axial["neck.function_sleep_work_selfcare_driving_and_activity"] = {"value": "컴퓨터 업무 중 불편하지만 일상생활은 가능"}
    out["NECK-ROUTINE-AXIAL-CLINICIAN-HANDOFF.json"] = {"id": "NECK-ROUTINE-AXIAL-CLINICIAN-HANDOFF", "simulation_language": "ko", "persona": {"age": 44}, "initial_statement": {"ko": "며칠 전부터 오른쪽 목이 간헐적으로 아파요."}, "hidden_state": axial, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 70, "expected_known_facts": {"neck.pain_nrs_current_worst_and_rest": "현재 3, 최악 6, 휴식 1"}, "forbidden_assertions": ["diagnosis.cervical_spondylosis"]}, "provenance": provenance(SOURCES)}
    radicular = routine("arm_radiating_or_neurologic"); radicular["neck.radiation_to_head_shoulder_arm_hand_or_chest"] = {"value": "왼쪽 팔과 엄지까지 뻗침"}; radicular["neck.arm_hand_numbness_tingling_distribution"] = {"value": "왼쪽 엄지 저림, 간헐적"}
    out["NECK-RADICULAR-BOUNDARY-NO-CORD-WARNING.json"] = {"id": "NECK-RADICULAR-BOUNDARY-NO-CORD-WARNING", "simulation_language": "ko", "persona": {"age": 51}, "initial_statement": {"ko": "목에서 왼팔로 뻗치는 느낌이 있어요."}, "hidden_state": radicular, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.cervical_radiculopathy"]}, "provenance": provenance(SOURCES)}
    absent = routine("other_unclear"); absent.pop("neck.onset_date_time_and_speed"); absent.pop("neck.information_source_proxy_and_reliability")
    out["NECK-AMBIGUOUS-DATA-ABSENT.json"] = {"id": "NECK-AMBIGUOUS-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 72}, "initial_statement": {"ko": "목이 좀 이상한데 언제부터인지는 모르겠어요."}, "hidden_state": absent, "response_behavior": {"neck.onset_date_time_and_speed": {"dataAbsentReason": "asked-unknown"}, "neck.information_source_proxy_and_reliability": {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {"neck.onset_date_time_and_speed": "asked-unknown", "neck.information_source_proxy_and_reliability": "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.cervical_spine_disorder"]}, "provenance": provenance(SOURCES)}
    proxy = routine("post_trauma"); proxy["neck.information_source_proxy_and_reliability"] = {"value": "보호자가 전화로 답변하며 본인은 옆에서 확인함"}
    out["NECK-REMOTE-PROXY-POST-MINOR-TRAUMA.json"] = {"id": "NECK-REMOTE-PROXY-POST-MINOR-TRAUMA", "simulation_language": "ko", "persona": {"age": 81}, "encounter_context": {"care_setting": "primary_care", "encounter_type": "new_encounter", "interview_initiator": "caregiver", "interview_mode": "telephone", "available_information": ["no_previous_records"], "time_constraint": "scheduled", "clinical_responsibility": "decision_support"}, "initial_statement": {"ko": "가볍게 넘어진 뒤 목이 불편해 보호자가 답합니다."}, "hidden_state": proxy, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.cervical_fracture"]}, "provenance": provenance(SOURCES)}
    extra = routine("established_cervical_condition_followup"); extra["neck.patient_concern_goal_and_other_detail"] = {"value": "목 증상 외에 예약 시간 변경 요청도 전달하고 싶음"}
    out["NECK-UNRELATED-ADDITIONAL-COMMENT.json"] = {"id": "NECK-UNRELATED-ADDITIONAL-COMMENT", "simulation_language": "ko", "persona": {"age": 60}, "initial_statement": {"ko": "목 치료 후 점검과 다른 요청이 있어요."}, "hidden_state": extra, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"neck.patient_concern_goal_and_other_detail": "목 증상 외에 예약 시간 변경 요청도 전달하고 싶음"}, "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.nonadherence"]}, "provenance": provenance(SOURCES)}
    multi = routine("headache_fever_or_systemic"); multi["neck.patient_concern_goal_and_other_detail"] = {"value": "목 통증 외에 반복 두통도 별도 문진을 원함"}
    out["NECK-MULTI-RFE-HEADACHE.json"] = {"id": "NECK-MULTI-RFE-HEADACHE", "simulation_language": "ko", "persona": {"age": 39}, "initial_statement": {"ko": "목도 아프고 두통도 반복돼요."}, "hidden_state": multi, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.migraine", "diagnosis.meningitis"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Neck Pain or Cervical Symptom", intents=[("intent.characterize_symptom", "Characterize Neck Pain Stiffness and Radiation"), ("intent.screen_red_flags", "Screen Trauma Neurologic Infection and Airway Warning Features"), ("intent.differentiate_common_causes", "Assess Mechanical Radicular Systemic and Exposure Context"), ("intent.risk_assessment", "Assess Prior Treatment Function and Clinician Handoff Needs")])
    primary, research = source_docs()
    concepts = [("81680005", "Neck pain (finding)"), ("54404000", "Cervical radiculopathy (disorder)"), ("161882006", "Neck stiffness (finding)")]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": 0} for c, d in concepts], "verified_attribute_ids": ["246112005", "363698007"], "validation": {"method": "build_time_live_fhir_lookup_mapping_search_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "neck_semantics": {"diagnosis_inferred": False, "etiology_inferred": False, "laterality_postcoordinated_without_site_validation": False, "runtime_terminology_query_required": False}, "provenance": provenance(["source.stom.neck-pain.20260716"])}
    docs = [("knowledge/base/primary-care-neck-pain.json", graph), ("rules/base/primary-care-neck-pain.json", rules), ("knowledge/generated/musculoskeletal/neck-pain/neck-pain.json", f), ("mappings/terminology/snomed-mrcm-neck-pain.json", mapping), ("sources/manifests/primary-care-neck-pain.json", primary), ("sources/manifests/primary-care-neck-pain-research.json", research), ("policies/primary-care-neck-pain-completion.json", completion(f))]
    for path, doc in docs: write_json(path, doc)
    for name, case in cases(f).items(): write_json("simulation/patients/musculoskeletal/neck-pain/" + name, case)


if __name__ == "__main__":
    main()
