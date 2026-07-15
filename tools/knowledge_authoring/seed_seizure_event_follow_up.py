#!/usr/bin/env python3
"""Materialize unreviewed seizure-like event and follow-up knowledge."""
from profile_support import *

P, RFE = "seizure-event-follow-up", "rfe.seizure_event_follow_up"
M, SN = "mapping.snomed-mrcm.seizure-event-follow-up", "http://snomed.info/sct"
ACQUIRED_AT = "2026-07-16T00:00:00Z"
SOURCES = ["source.nice.ng217.2025", "source.nhs.seizure-first-aid.2023", "source.ilae.seizure-classification.2025", "source.stom.seizure.20260716"]
G = {k: f"group.seizure.{k}" for k in ("routing", "safety", "event", "recovery", "context", "followup", "function")}
C, S, D, R = ["intent.characterize_symptom"], ["intent.screen_red_flags"], ["intent.differentiate_common_causes"], ["intent.risk_assessment"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups, intents=intents, **kwargs)


def fragment():
    e = [
        Q("seizure.primary_group", "Primary Seizure Presentation", "coded", "primary-group", "이번 방문은 처음 발생한 경련 의심 사건, 이전에도 있었던 반복 사건, 진단된 뇌전증의 발작 후 평가, 약물·치료 점검, 실신 등 다른 사건과 구분이 필요한 경우 중 무엇에 가깝나요?", 190, [G["routing"]], C, allowed_values=["first_suspected_event", "recurrent_undiagnosed_events", "known_epilepsy_breakthrough", "medication_or_treatment_followup", "alternative_event_unclear", "other_unclear"]),
        Q("seizure.ongoing_five_minutes_or_unknown", "Ongoing Prolonged Seizure", "boolean", "ongoing-prolonged", "지금 경련이 계속되고 있으며 5분 이상이거나 시작 시각을 알 수 없나요?", 189, [G["safety"]], S, safety_relevant=True),
        Q("seizure.repeated_without_recovery", "Repeated Seizures without Recovery", "boolean", "repeated-no-recovery", "경련이 연이어 발생했고 그 사이에 평소 의식으로 회복하지 못했나요?", 188, [G["safety"]], S, safety_relevant=True),
        Q("seizure.breathing_difficulty_or_cyanosis_persistent", "Persistent Breathing Difficulty", "boolean", "breathing", "경련이 멈춘 뒤에도 숨쉬기 어렵거나 입술·얼굴이 파랗거나 회색빛인 상태가 지속되나요?", 187, [G["safety"]], S, safety_relevant=True),
        Q("seizure.not_returned_to_baseline", "Failure to Return to Baseline", "boolean", "not-baseline", "평소보다 오래 의식이 흐리거나 깨우기 어렵고 아직 평소 상태로 돌아오지 못했나요?", 186, [G["safety"], G["recovery"]], S, safety_relevant=True),
        Q("seizure.serious_injury_or_head_trauma", "Serious Injury with Seizure", "boolean", "serious-injury", "사건 중 머리를 세게 다쳤거나 심한 출혈·골절 의심·큰 화상 등 중대한 손상이 생겼나요?", 185, [G["safety"], G["recovery"]], S, safety_relevant=True),
        Q("seizure.pregnant_or_recent_postpartum_event", "Seizure in Pregnancy or Postpartum", "boolean", "pregnancy", "현재 임신 중이거나 출산 후 6주 이내인데 새 경련·의식소실이 있었나요?", 184, [G["safety"], G["context"]], S, safety_relevant=True),
        Q("seizure.new_focal_deficit_or_thunderclap", "Acute Neurologic Warning", "boolean", "focal-warning", "새 한쪽 마비·감각저하·말하기 어려움·시야장애 또는 갑작스러운 극심한 두통이 함께 있나요?", 183, [G["safety"]], S, safety_relevant=True),
        Q("seizure.fever_meningism_or_nonblanching_rash", "Possible CNS Infection Warning", "boolean", "infection-warning", "고열과 함께 심한 두통·목 경직·빛을 몹시 불편해함·눌러도 사라지지 않는 발진 중 하나가 있나요?", 182, [G["safety"]], S, safety_relevant=True),
        Q("seizure.hypoglycemia_or_toxic_exposure", "Metabolic or Toxic Emergency Context", "boolean", "metabolic-toxic", "당뇨가 있으면서 저혈당이 의심되거나 약물 과량·중독물질 노출 뒤 경련이 발생했나요?", 181, [G["safety"], G["context"]], S, safety_relevant=True),
        Q("seizure.water_related_or_drowning_concern", "Water-related Seizure", "boolean", "water-related", "목욕·수영·물속에서 사건이 발생해 물을 들이마셨거나 익수 가능성이 있나요?", 180, [G["safety"]], S, safety_relevant=True),
        Q("seizure.rescue_plan_failed", "Rescue Treatment Failure", "boolean", "rescue-failed", "개인 응급계획에 따라 구조약을 사용했지만 경련이 멈추지 않았거나 계획된 다음 단계가 필요한가요?", 179, [G["safety"], G["followup"]], S, safety_relevant=True),
        Q("seizure.first_event_not_medically_assessed", "Unassessed First Suspected Seizure", "boolean", "first-unassessed", "처음 발생한 경련 의심 사건이며 아직 의료진의 평가를 받지 않았나요?", 178, [G["safety"], G["routing"]], S, safety_relevant=True),

        Q("seizure.information_source_and_witness", "Information Source and Witness", "string", "witness", "내용은 본인 기억, 목격자 설명, 보호자 전달 중 무엇에 근거하나요? 목격자와 연락하거나 함께 진료받을 수 있나요?", 165, [G["event"]], C),
        Q("seizure.video_or_recording_available", "Event Video or Recording", "string", "video", "사건을 촬영한 영상·사진·기기 기록이 있나요? 있다면 의료진에게 안전하게 제공할 수 있는지 알려주세요.", 164, [G["event"]], C),
        Q("seizure.event_date_time_place_and_activity", "Event Circumstances", "string", "circumstances", "사건 날짜·시각·장소와 당시 하던 일, 앉아 있었는지·서 있었는지·자고 있었는지를 알려주세요.", 163, [G["event"]], C),
        Q("seizure.warning_or_aura", "Warning or Aura", "string", "warning", "직전에 이상한 냄새·맛·시야·감각, 데자뷔, 두려움, 메스꺼움, 어지럼 같은 예고 증상이 있었나요?", 162, [G["event"]], C),
        Q("seizure.initial_loss_of_posture_or_fall", "Initial Posture and Fall", "string", "posture-fall", "처음에 몸에 힘이 빠지거나 쓰러졌나요? 넘어지는 방향과 부딪힌 부위를 알려주세요.", 161, [G["event"], G["recovery"]], C),
        Q("seizure.awareness_and_responsiveness", "Awareness and Responsiveness", "string", "awareness", "사건 중 말이나 지시에 반응했는지, 주변을 인식했는지, 기억이 남아 있는지 알려주세요.", 160, [G["event"]], C, terminology_binding={"system": SN, "code": "419045004"}, mrcm_ref=M),
        Q("seizure.onset_body_part_and_laterality", "Initial Body Site and Laterality", "string", "onset-site", "움직임이나 감각 변화가 처음 시작된 신체 부위와 왼쪽·오른쪽 여부, 다른 부위로 퍼진 순서를 알려주세요.", 159, [G["event"]], C),
        Q("seizure.stiffening_jerking_twitching_pattern", "Motor Pattern", "string", "motor-pattern", "몸이 굳음·규칙적 떨림·불규칙한 움찔거림이 있었는지, 어느 부위가 어떤 순서로 움직였는지 알려주세요.", 158, [G["event"]], C, terminology_binding={"system": SN, "code": "91175000"}, mrcm_ref=M),
        Q("seizure.head_eye_deviation", "Head and Eye Deviation", "string", "head-eye", "머리나 눈이 한쪽으로 돌아갔거나 눈이 위로 돌아갔나요? 방향과 지속 시간을 알려주세요.", 157, [G["event"]], C),
        Q("seizure.automatisms_or_unusual_behaviour", "Automatisms or Behaviour", "string", "automatisms", "입맛다시기·옷 만지작거리기·중얼거림·배회·반복 행동처럼 평소와 다른 행동이 있었나요?", 156, [G["event"]], C),
        Q("seizure.event_duration_and_timing_method", "Event Duration", "string", "duration", "전체 사건과 몸이 굳거나 떨린 시간은 각각 얼마나 되었나요? 시계로 잰 것인지 추정인지 알려주세요.", 155, [G["event"]], C),
        Q("seizure.colour_and_breathing_during_event", "Colour and Breathing During Event", "string", "colour-breathing", "사건 중 얼굴·입술 색과 호흡, 침·거품·코골이 같은 소리의 변화를 알려주세요.", 154, [G["event"]], C),
        Q("seizure.tongue_or_mouth_injury", "Tongue or Mouth Injury", "string", "tongue-bite", "혀나 입안을 깨물었나요? 혀의 옆면인지 끝부분인지와 상처 정도를 알려주세요.", 153, [G["event"], G["recovery"]], D),
        Q("seizure.bladder_or_bowel_control", "Bladder or Bowel Control", "string", "incontinence", "사건 중 소변이나 대변을 지렸나요?", 152, [G["event"]], D),
        Q("seizure.event_count_and_clustering", "Event Count and Clustering", "string", "count-cluster", "그날 몇 번 발생했고 각 사건 사이에 완전히 회복했는지 알려주세요.", 151, [G["event"], G["recovery"]], C),

        Q("seizure.postevent_confusion_memory_and_sleep", "Post-event Confusion and Sleep", "string", "postevent", "끝난 뒤 혼란·기억 공백·두통·근육통·졸림이 있었나요? 평소 상태로 돌아오는 데 걸린 시간을 알려주세요.", 150, [G["recovery"]], C),
        Q("seizure.postevent_focal_weakness_or_speech_change", "Post-event Focal Symptoms", "string", "postevent-focal", "끝난 뒤 한쪽 힘 빠짐, 감각·말·시야 변화가 있었나요? 어느 쪽이며 얼마나 지속됐나요?", 149, [G["recovery"]], R),
        Q("seizure.injury_details_and_current_symptoms", "Injury Details", "string", "injury-detail", "머리·얼굴·치아·어깨 등 다친 부위와 현재 통증·부기·출혈·움직임 제한을 알려주세요.", 148, [G["recovery"]], R),
        Q("seizure.first_event_prior_events_and_frequency", "First and Prior Events", "string", "prior-events", "이번이 처음인지, 비슷한 사건의 최초 시기·최근 시기·평소 빈도와 최근 변화를 알려주세요.", 147, [G["context"]], R),
        Q("seizure.known_diagnosis_type_and_care_team", "Known Epilepsy Context", "string", "diagnosis", "뇌전증 진단명·발작 유형, 진단 시기와 담당 의료기관·최근 진료일을 알려주세요.", 146, [G["followup"]], R, terminology_binding={"system": SN, "code": "84757009"}, mrcm_ref=M),
        Q("seizure.sleep_deprivation_stress_and_missed_meals", "Common Precipitating Context", "string", "precipitants", "사건 전 수면 부족·심한 스트레스·과로·금식·식사 거름이 있었나요?", 145, [G["context"]], D),
        Q("seizure.fever_illness_and_recent_infection", "Illness Context", "string", "illness", "최근 발열·감염·구토·설사·탈수 또는 새로 아픈 증상이 있었나요?", 144, [G["context"]], D),
        Q("seizure.alcohol_substance_and_withdrawal", "Alcohol and Substance Context", "string", "substance", "최근 음주량 변화·과음·금주, 기호성 약물·각성제·대마 등 물질 사용 또는 중단이 있었나요?", 143, [G["context"]], D),
        Q("seizure.new_medicines_overdose_or_withdrawal", "Medicine and Toxic Context", "string", "medicine-change", "새로 시작·증량·중단한 약, 처방 외 약·한약·보충제, 과량 복용 가능성을 알려주세요.", 142, [G["context"]], D),
        Q("seizure.syncope_prodrome_and_cardiac_features", "Syncope and Cardiac Features", "string", "syncope-features", "오래 서 있기·통증·배뇨 뒤 발생했거나 직전 식은땀·메스꺼움·시야 흐림, 흉통·두근거림이 있었나요?", 141, [G["context"]], D),
        Q("seizure.previous_head_injury_stroke_or_cns_disease", "Neurologic History", "string", "neurologic-history", "과거 머리 외상·뇌졸중·뇌수술·뇌종양·중추신경 감염·발달 또는 신경계 질환을 알려주세요.", 140, [G["context"]], R),
        Q("seizure.family_history", "Family History", "string", "family", "가족 중 뇌전증·경련·원인 불명 의식소실·젊은 나이 돌연사가 있었나요?", 139, [G["context"]], R),
        Q("seizure.pregnancy_contraception_and_reproductive_plan", "Pregnancy and Reproductive Context", "string", "reproductive", "해당되면 임신 가능성·주수·산후 시기, 피임법과 임신 계획을 알려주세요.", 138, [G["context"], G["followup"]], R),

        Q("seizure.antiseizure_medicines_regimen", "Antiseizure Medicine Regimen", "string", "asm-regimen", "항경련제의 제품명·성분명·용량·하루 횟수·복용 시각을 알려주세요.", 137, [G["followup"]], R),
        Q("seizure.adherence_missed_doses_and_recent_changes", "Adherence and Changes", "string", "adherence", "최근 빠뜨린 횟수·마지막 누락 시각, 용량·제품 변경과 약을 중단한 적이 있는지 알려주세요.", 136, [G["followup"]], R),
        Q("seizure.adverse_effects_and_interactions", "Treatment Adverse Effects", "string", "adverse-effects", "복용 후 졸림·어지럼·발진·기분·기억 변화 등 부작용과 다른 약과의 상호작용 우려가 있나요?", 135, [G["followup"]], R),
        Q("seizure.rescue_medicine_and_emergency_plan", "Rescue Medicine and Plan", "string", "rescue-plan", "개인 응급계획과 구조약 이름·투여 기준·최근 사용 시각·효과, 가족의 사용 교육 여부를 알려주세요.", 134, [G["followup"]], R),
        Q("seizure.latest_eeg_imaging_ecg_and_labs", "Previous Investigations", "string", "investigations", "EEG·뇌 MRI/CT·심전도·혈액검사의 날짜와 주요 결과, 예정 검사를 알려주세요.", 133, [G["followup"]], R),
        Q("seizure.last_seizure_and_control_trend", "Seizure Control Trend", "string", "control-trend", "치료 전후 발작 빈도·지속시간·양상이 어떻게 변했고 마지막 사건은 언제였나요?", 132, [G["followup"]], R),
        Q("seizure.driving_work_heights_and_machinery", "Driving and Occupational Safety", "string", "driving-work", "운전, 고소 작업, 화기·절단기·중장비 업무 여부와 사건이 안전에 미친 영향을 알려주세요.", 131, [G["function"]], R),
        Q("seizure.bathing_swimming_and_living_arrangements", "Home and Water Safety", "string", "home-water", "혼자 목욕·수영하는지, 혼자 사는지, 야간 사건을 발견하거나 도움을 요청할 사람이 있는지 알려주세요.", 130, [G["function"]], R),
        Q("seizure.functional_cognitive_mood_impact", "Functional and Psychosocial Impact", "string", "function-impact", "사건이나 약 때문에 학업·업무·기억·기분·수면·독립생활이 얼마나 달라졌나요?", 129, [G["function"]], R),
        Q("seizure.patient_priority_and_other_detail", "Patient Priority and Other Detail", "string", "other-detail", "질문에 없지만 의료진에게 꼭 전달할 내용, 가장 걱정되는 점이나 진료에서 원하는 도움을 알려주세요.", 80, [G["routing"], G["function"]], C),
    ]
    safety = [
        ("ongoing-prolonged", "seizure.ongoing_five_minutes_or_unknown", "emergency", 1000),
        ("repeated-no-recovery", "seizure.repeated_without_recovery", "emergency", 1000),
        ("breathing", "seizure.breathing_difficulty_or_cyanosis_persistent", "emergency", 1000),
        ("not-baseline", "seizure.not_returned_to_baseline", "emergency", 1000),
        ("serious-injury", "seizure.serious_injury_or_head_trauma", "emergency", 1000),
        ("pregnancy", "seizure.pregnant_or_recent_postpartum_event", "emergency", 1000),
        ("focal-warning", "seizure.new_focal_deficit_or_thunderclap", "emergency", 1000),
        ("infection-warning", "seizure.fever_meningism_or_nonblanching_rash", "emergency", 1000),
        ("metabolic-toxic", "seizure.hypoglycemia_or_toxic_exposure", "emergency", 1000),
        ("water-related", "seizure.water_related_or_drowning_concern", "emergency", 1000),
        ("rescue-failed", "seizure.rescue_plan_failed", "emergency", 1000),
        ("first-unassessed", "seizure.first_event_not_medically_assessed", "urgent", 990),
    ]
    rules = [safety_rule(P, key, {"fact": fid, "equals": True}, level, priority) for key, fid, level, priority in safety]
    return {"id": "knowledge.generated.seizure-event-follow-up", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-seizure-event-follow-up-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": v, "type": "ClinicalGroup", "display": v.split(".")[-1]} for v in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": e, "provenance": provenance(SOURCES)}


def completion(f):
    p = completion_policy(prefix=P, fragment=f, presentation_fact="seizure.primary_group", question_budget=70, source_refs=SOURCES)
    common = ["seizure.information_source_and_witness", "seizure.video_or_recording_available", "seizure.event_date_time_place_and_activity", "seizure.warning_or_aura", "seizure.awareness_and_responsiveness", "seizure.onset_body_part_and_laterality", "seizure.stiffening_jerking_twitching_pattern", "seizure.event_duration_and_timing_method", "seizure.colour_and_breathing_during_event", "seizure.event_count_and_clustering", "seizure.postevent_confusion_memory_and_sleep", "seizure.injury_details_and_current_symptoms", "seizure.first_event_prior_events_and_frequency", "seizure.sleep_deprivation_stress_and_missed_meals", "seizure.fever_illness_and_recent_infection", "seizure.alcohol_substance_and_withdrawal", "seizure.new_medicines_overdose_or_withdrawal", "seizure.syncope_prodrome_and_cardiac_features", "seizure.previous_head_injury_stroke_or_cns_disease", "seizure.family_history", "seizure.patient_priority_and_other_detail"]
    cases = {
        "first_suspected_event": ["seizure.initial_loss_of_posture_or_fall", "seizure.head_eye_deviation", "seizure.automatisms_or_unusual_behaviour", "seizure.tongue_or_mouth_injury", "seizure.bladder_or_bowel_control", "seizure.postevent_focal_weakness_or_speech_change", "seizure.latest_eeg_imaging_ecg_and_labs", "seizure.driving_work_heights_and_machinery"],
        "recurrent_undiagnosed_events": ["seizure.head_eye_deviation", "seizure.automatisms_or_unusual_behaviour", "seizure.tongue_or_mouth_injury", "seizure.bladder_or_bowel_control", "seizure.latest_eeg_imaging_ecg_and_labs", "seizure.driving_work_heights_and_machinery"],
        "known_epilepsy_breakthrough": ["seizure.known_diagnosis_type_and_care_team", "seizure.antiseizure_medicines_regimen", "seizure.adherence_missed_doses_and_recent_changes", "seizure.adverse_effects_and_interactions", "seizure.rescue_medicine_and_emergency_plan", "seizure.last_seizure_and_control_trend", "seizure.pregnancy_contraception_and_reproductive_plan", "seizure.driving_work_heights_and_machinery", "seizure.bathing_swimming_and_living_arrangements"],
        "medication_or_treatment_followup": ["seizure.known_diagnosis_type_and_care_team", "seizure.antiseizure_medicines_regimen", "seizure.adherence_missed_doses_and_recent_changes", "seizure.adverse_effects_and_interactions", "seizure.rescue_medicine_and_emergency_plan", "seizure.latest_eeg_imaging_ecg_and_labs", "seizure.last_seizure_and_control_trend", "seizure.pregnancy_contraception_and_reproductive_plan", "seizure.functional_cognitive_mood_impact"],
        "alternative_event_unclear": ["seizure.initial_loss_of_posture_or_fall", "seizure.automatisms_or_unusual_behaviour", "seizure.postevent_focal_weakness_or_speech_change", "seizure.syncope_prodrome_and_cardiac_features", "seizure.latest_eeg_imaging_ecg_and_labs"],
        "other_unclear": ["seizure.patient_priority_and_other_detail"],
    }
    p["required_facts"]["routine"], p["conditional_required_facts"] = common, [{"selector_fact": "seizure.primary_group", "cases": cases}]
    return p


def source_docs():
    defs = [
        ("source.nice.ng217.2025", "NICE", "Epilepsies in children, young people and adults", "NG217; updated-2025-01-30", "https://www.nice.org.uk/guidance/ng217", "nice_guidance", ["After a first suspected seizure, assessment should use a detailed patient and caregiver history, eyewitness accounts and video when available, and consider cardiac or metabolic mimics.", "Urgent specialist assessment, treatment review, pregnancy counselling and individualised emergency plans are represented as pre-visit information needs rather than diagnoses."]),
        ("source.nhs.seizure-first-aid.2023", "NHS", "What to do if someone has a seizure (fit)", "reviewed-2023-12-19", "https://www.nhs.uk/symptoms/what-to-do-if-someone-has-a-seizure-fit/", "public_health_guidance", ["Emergency criteria include a seizure lasting over five minutes, repeated seizures without recovery, failure to regain consciousness, serious injury or breathing difficulty.", "Useful witness details include activity before the event, warning sensations, awareness, colour, motor parts, breathing, duration, continence, tongue injury and recovery."]),
        ("source.ilae.seizure-classification.2025", "ILAE", "Updated classification of epileptic seizures", "position-paper-2025", "https://www.ilae.org/guidelines/definition-and-classification", "clinical_guideline", ["Event description should preserve onset, awareness or consciousness, observed motor and non-motor features and uncertainty instead of assigning an epilepsy diagnosis from one report."]),
        ("source.stom.seizure.20260716", "Infoclinic", "STOM seizure terminology and MRCM summary", "SNOMEDCT-20260701", "https://stom.infoclinic.co", "terminology_server", ["FHIR lookup confirmed active seizure, epilepsy, generalized-onset seizure and loss-of-consciousness concepts on the 20260701 international edition.", "Terminology and MRCM support semantic binding only and do not determine whether an event was epileptic or its urgency."]),
    ]
    artifacts = [{"id": i, "kind": "terminology_mrcm_query_summary" if profile == "terminology_server" else "clinical_guidance_metadata", "publisher": pub, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if profile == "terminology_server" else "metadata_only_not_cached", "license_status": "restricted" if pub in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "last_monitored_at": "2026-07-16", "monitor_result": "current_official_source_confirmed", "assertions": assertions} for i, pub, title, version, url, profile, assertions in defs]
    research = {"id": "source-manifest.primary-care-seizure-event-follow-up-research", "version": VERSION, "acquired_at": ACQUIRED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([x[0] for x in defs])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.seizure", "generated_clinical_knowledge", "knowledge/generated/neurology/seizure-event-follow-up/seizure-event-follow-up.json", True), ("source.mapping.seizure", "terminology_mapping", "mappings/terminology/snomed-mrcm-seizure-event-follow-up.json", False), ("source.external.seizure", "external_source_manifest", "sources/manifests/primary-care-seizure-event-follow-up-research.json", False), ("source.policy.seizure", "runtime_policy", "policies/primary-care-seizure-event-follow-up-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-seizure-event-follow-up", "version": VERSION, "acquired_at": ACQUIRED_AT, "artifacts": [{"id": i, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for i, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def cases(f):
    out = {}
    for i, rule in enumerate(f["safety_rules"]):
        fid, level, key = rule["when"]["fact"], rule["then"]["safety_level"], rule["id"].split("safety.")[1]
        out[f"SEIZURE-{key.upper()}.json"] = {"id": f"SEIZURE-{key.upper()}", "simulation_language": "ko", "persona": {"age": 19 + i}, "initial_statement": {"ko": "경련 같은 일이 있었어요."}, "hidden_state": {fid: {"value": True}}, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 45, "forbidden_assertions": ["diagnosis.epilepsy", "diagnosis.psychogenic_nonepileptic_seizure", "diagnosis.syncope"]}, "provenance": provenance(SOURCES)}
    policy = completion(f)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["known_epilepsy_breakthrough"])
    by_id, hidden = {x["fact"]["id"]: x["fact"] for x in f["entries"]}, {}
    for fid in required:
        fact = by_id[fid]
        hidden[fid] = {"value": False if fact["value_type"] == "boolean" else fact.get("allowed_values", ["없음"])[-1] if fact["value_type"] == "coded" else "없음"}
    hidden["seizure.primary_group"] = {"value": "known_epilepsy_breakthrough"}
    declined = "seizure.information_source_and_witness"
    hidden.pop(declined)
    out["SEIZURE-KNOWN-EPILEPSY-DATA-ABSENT.json"] = {"id": "SEIZURE-KNOWN-EPILEPSY-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 37}, "initial_statement": {"ko": "뇌전증 치료 중인데 다시 발작이 있었어요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.status_epilepticus", "diagnosis.nonadherence"]}, "provenance": provenance(["source.nice.ng217.2025", "specifications/clinical-memory.md"])}

    def routine_hidden(branch):
        required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"][branch])
        values = {}
        for fid in required:
            fact = by_id[fid]
            values[fid] = {"value": False if fact["value_type"] == "boolean" else fact.get("allowed_values", ["없음"])[0] if fact["value_type"] == "coded" else "없음"}
        values["seizure.primary_group"] = {"value": branch}
        return values

    first = routine_hidden("first_suspected_event")
    first["seizure.event_duration_and_timing_method"] = {"value": "약 4분, 목격자가 시계로 측정"}
    first["seizure.information_source_and_witness"] = {"value": "본인 기억과 동료 목격, 동료 연락 가능"}
    out["SEIZURE-BOUNDARY-FOUR-MINUTE-FIRST-ASSESSED.json"] = {"id": "SEIZURE-BOUNDARY-FOUR-MINUTE-FIRST-ASSESSED", "simulation_language": "ko", "persona": {"age": 28}, "initial_statement": {"ko": "처음 경련 같은 일이 있었고 응급실 평가 후 진료 전 문진을 작성합니다."}, "hidden_state": first, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_selected_facts_contains": ["seizure.event_duration_and_timing_method", "seizure.information_source_and_witness"], "expected_known_facts": {"seizure.event_duration_and_timing_method": "약 4분, 목격자가 시계로 측정"}, "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.epilepsy", "diagnosis.status_epilepticus"]}, "provenance": provenance(SOURCES)}

    ambiguous = routine_hidden("alternative_event_unclear")
    ambiguous.pop("seizure.information_source_and_witness")
    ambiguous["seizure.syncope_prodrome_and_cardiac_features"] = {"value": "식은땀과 시야 흐림은 있었으나 목격자가 없어 정확하지 않음"}
    out["SEIZURE-AMBIGUOUS-NO-WITNESS.json"] = {"id": "SEIZURE-AMBIGUOUS-NO-WITNESS", "simulation_language": "ko", "persona": {"age": 45}, "initial_statement": {"ko": "잠깐 쓰러졌는데 경련이었는지 잘 모르겠어요."}, "hidden_state": ambiguous, "response_behavior": {"seizure.information_source_and_witness": {"dataAbsentReason": "asked-unknown"}}, "expected": {"expected_data_absent_reasons": {"seizure.information_source_and_witness": "asked-unknown"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_selected_facts_contains": ["seizure.syncope_prodrome_and_cardiac_features"], "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.epilepsy", "diagnosis.syncope", "diagnosis.psychogenic_nonepileptic_seizure"]}, "provenance": provenance(SOURCES)}

    proxy = routine_hidden("known_epilepsy_breakthrough")
    proxy["seizure.information_source_and_witness"] = {"value": "보호자가 영상통화로 대신 답변하며 사건을 직접 목격함"}
    out["SEIZURE-PROXY-REMOTE-FOLLOW-UP.json"] = {"id": "SEIZURE-PROXY-REMOTE-FOLLOW-UP", "simulation_language": "ko", "persona": {"age": 16}, "encounter_context": {"care_setting": "specialist_clinic", "encounter_type": "follow_up", "interview_initiator": "caregiver", "interview_mode": "video", "available_information": ["previous_clinical_memory", "medication_history"], "time_constraint": "scheduled", "clinical_responsibility": "follow_up_support"}, "initial_statement": {"ko": "아이의 경련 후 영상진료 전 보호자가 대신 작성합니다."}, "hidden_state": proxy, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"seizure.information_source_and_witness": "보호자가 영상통화로 대신 답변하며 사건을 직접 목격함"}, "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.nonadherence"]}, "provenance": provenance(SOURCES)}

    additional = routine_hidden("medication_or_treatment_followup")
    additional["seizure.patient_priority_and_other_detail"] = {"value": "질문과 별개로 최근 업무 교대 때문에 진료시간 조정도 상담하고 싶음"}
    out["SEIZURE-UNRELATED-ADDITIONAL-COMMENT.json"] = {"id": "SEIZURE-UNRELATED-ADDITIONAL-COMMENT", "simulation_language": "ko", "persona": {"age": 33}, "initial_statement": {"ko": "발작약 점검과 함께 다른 의견도 남기고 싶어요."}, "hidden_state": additional, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"seizure.patient_priority_and_other_detail": "질문과 별개로 최근 업무 교대 때문에 진료시간 조정도 상담하고 싶음"}, "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.work_stress_seizure"]}, "provenance": provenance(SOURCES)}

    multi = routine_hidden("recurrent_undiagnosed_events")
    multi["seizure.patient_priority_and_other_detail"] = {"value": "경련 의심 사건 외에 새로 반복되는 두통도 별도 평가받고 싶음"}
    out["SEIZURE-MULTI-RFE-HEADACHE.json"] = {"id": "SEIZURE-MULTI-RFE-HEADACHE", "simulation_language": "ko", "persona": {"age": 41}, "initial_statement": {"ko": "경련 같은 일이 반복되고 요즘 두통도 새로 생겼어요."}, "hidden_state": multi, "expected": {"expected_safety_level": "routine", "expected_stop_reason": "all_required_targets_resolved", "expected_known_facts": {"seizure.patient_priority_and_other_detail": "경련 의심 사건 외에 새로 반복되는 두통도 별도 평가받고 싶음"}, "expected_max_turns": 70, "forbidden_assertions": ["diagnosis.epilepsy", "diagnosis.migraine"]}, "provenance": provenance(SOURCES)}
    return out


def main():
    f = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Seizure-like Event or Follow-up", intents=[("intent.characterize_symptom", "Characterize Seizure-like Event and Recovery"), ("intent.screen_red_flags", "Screen Prolonged Event Injury and Neurological Risk"), ("intent.differentiate_common_causes", "Assess Precipitating and Alternative Event Context"), ("intent.risk_assessment", "Assess Treatment Safety Function and Follow-up")])
    primary, research = source_docs()
    concepts = [("91175000", "Seizure (finding)", 0), ("84757009", "Epilepsy (disorder)", 0), ("128613002", "Seizure disorder (disorder)", 0), ("246545002", "Generalized onset epileptic seizure (finding)", 0), ("419045004", "Loss of consciousness (finding)", 0), ("386661006", "Fever (finding)", 0)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": c, "display": d, "concept_active": True, "attribute_count_returned": n} for c, d, n in concepts], "verified_attribute_ids": ["246112005", "363714003", "363698007"], "validation": {"method": "build_time_live_fhir_lookup_and_mrcm_summary", "checked_at": ACQUIRED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "event_semantics": {"diagnosis_inferred": False, "onset_awareness_motor_features_preserved": True, "laterality_postcoordination_asserted": False}, "provenance": provenance(["source.stom.seizure.20260716"])}
    docs = [("knowledge/base/primary-care-seizure-event-follow-up.json", graph), ("rules/base/primary-care-seizure-event-follow-up.json", rules), ("knowledge/generated/neurology/seizure-event-follow-up/seizure-event-follow-up.json", f), ("mappings/terminology/snomed-mrcm-seizure-event-follow-up.json", mapping), ("sources/manifests/primary-care-seizure-event-follow-up.json", primary), ("sources/manifests/primary-care-seizure-event-follow-up-research.json", research), ("policies/primary-care-seizure-event-follow-up-completion.json", completion(f))]
    for path, doc in docs:
        write_json(path, doc)
    for name, case in cases(f).items():
        write_json("simulation/patients/neurology/seizure-event-follow-up/" + name, case)


if __name__ == "__main__":
    main()
