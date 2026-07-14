#!/usr/bin/env python3
"""Materialize unreviewed hypertension follow-up knowledge."""
from profile_support import *

P = "hypertension-follow-up"
RFE = "rfe.hypertension_follow_up"
M = "mapping.snomed-mrcm.hypertension-follow-up"
SN = "http://snomed.info/sct"
SOURCES = [
    "source.nice.ng136.hypertension.2026",
    "source.nice.ng133.pregnancy-hypertension.2023",
    "source.nhs.high-blood-pressure.2026",
]
G = {key: f"group.hypertension-follow-up.{key}" for key in (
    "measurement", "immediate-safety", "medication", "postural",
    "cardiovascular-risk", "self-management", "monitoring", "pregnancy",
)}
C = ["intent.characterize_follow_up"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
F = ["intent.follow_up_support"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups,
                 intents=intents, **kwargs)


def fragment():
    entries = [
        Q("hypertension.follow_up.requested", "Hypertension Follow-up Requested", "boolean", "requested", "고혈압이나 혈압약의 추적관리를 위해 방문한 것이 맞나요?", 130, [G["measurement"]], C, terminology_binding={"system": SN, "code": "38341003"}),
        Q("blood_pressure.latest_systolic", "Latest Systolic Blood Pressure", "integer", "latest-systolic", "가장 최근 수축기 혈압(위 숫자)은 몇 mmHg였나요?", 118, [G["measurement"]], C, terminology_binding={"system": SN, "focus_code": "75367002"}, mrcm_ref=M, mrcm_status="not_applicable_observable"),
        Q("blood_pressure.latest_diastolic", "Latest Diastolic Blood Pressure", "integer", "latest-diastolic", "가장 최근 이완기 혈압(아래 숫자)은 몇 mmHg였나요?", 117, [G["measurement"]], C, terminology_binding={"system": SN, "focus_code": "75367002"}, mrcm_ref=M, mrcm_status="not_applicable_observable"),
        Q("blood_pressure.latest_measurement_time", "Latest Blood Pressure Measurement Time", "string", "measurement-time", "그 혈압은 언제 측정했나요?", 110, [G["measurement"]], C),
        Q("blood_pressure.measurement_setting", "Blood Pressure Measurement Setting", "coded", "setting", "집, 의료기관, 약국·공공기기, 웨어러블 중 어디서 측정했나요?", 109, [G["measurement"]], C, allowed_values=["home", "clinic", "pharmacy_public", "wearable", "other", "unknown"]),
        Q("blood_pressure.repeated_after_rest", "Blood Pressure Repeated after Rest", "boolean", "repeat-rest", "등을 기대고 5분 이상 쉰 뒤 같은 팔에서 다시 측정했나요?", 108, [G["measurement"]], C),
        Q("blood_pressure.device_and_cuff_suitable", "Suitable Device and Cuff", "coded", "device-cuff", "검증된 위팔 혈압계와 팔둘레에 맞는 커프를 사용했나요?", 96, [G["measurement"]], C, allowed_values=["yes", "no", "uncertain"]),
        Q("blood_pressure.home_log_available", "Home Blood Pressure Log Available", "boolean", "home-log", "최근 여러 날의 아침·저녁 가정혈압 기록이 있나요?", 107, [G["measurement"], G["monitoring"]], F),
        Q("blood_pressure.home_average_or_range", "Home Blood Pressure Average or Range", "string", "home-average", "기록이 있다면 최근 평균 또는 대략적인 범위를 알려주세요.", 106, [G["measurement"], G["monitoring"]], F),
        Q("blood_pressure.repeated_180_120_or_higher", "Repeated Blood Pressure at Least 180 over 120", "boolean", "severe-bp", "최근 혈압을 바르게 다시 쟀을 때 수축기 180 이상 또는 이완기 120 이상이 한 번이라도 계속 나왔나요?", 129, [G["immediate-safety"]], S, safety_relevant=True),
        Q("symptom.new_confusion", "New Confusion", "boolean", "confusion", "높은 혈압과 함께 새로 혼란하거나 의식이 흐린가요?", 128, [G["immediate-safety"]], S, safety_relevant=True),
        Q("symptom.chest_pain", "Chest Pain", "boolean", "chest-pain", "높은 혈압과 함께 가슴 통증이나 압박감이 있나요?", 127, [G["immediate-safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("symptom.severe_dyspnea", "Severe Shortness of Breath", "boolean", "severe-dyspnea", "높은 혈압과 함께 가만히 있어도 숨이 매우 차거나 누워 있기 어려운가요?", 126, [G["immediate-safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("symptom.new_focal_neurological_deficit", "New Focal Neurological Deficit", "boolean", "focal-deficit", "갑자기 한쪽 얼굴·팔·다리에 힘이 빠지거나 말이 어눌하거나 시야가 달라졌나요?", 125, [G["immediate-safety"]], S, safety_relevant=True),
        Q("symptom.markedly_reduced_urine", "Markedly Reduced Urine", "boolean", "low-urine", "높은 혈압과 함께 소변량이 크게 줄거나 거의 나오지 않나요?", 124, [G["immediate-safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("patient.pregnant_or_postpartum", "Pregnant or Postpartum", "coded", "pregnancy", "현재 임신 중이거나 출산 후 6주 이내인가요?", 123, [G["pregnancy"]], S, safety_relevant=True, allowed_values=["pregnant", "postpartum_6_weeks", "not_applicable", "unclear"], reuse_existing=True),
        Q("blood_pressure.pregnancy_160_110_or_higher", "Pregnancy Blood Pressure at Least 160 over 110", "boolean", "pregnancy-severe-bp", "임신·산후 상태에서 수축기 160 이상 또는 이완기 110 이상이 나왔나요?", 122, [G["pregnancy"]], S, safety_relevant=True),
        Q("symptom.preeclampsia_warning_features", "Pregnancy Hypertension Warning Features", "boolean", "pregnancy-warning", "임신·산후 상태에서 심한 두통, 시야 변화, 명치·오른쪽 윗배 통증, 구토 또는 얼굴·손·발의 갑작스러운 부종이 있나요?", 121, [G["pregnancy"]], S, safety_relevant=True, reuse_existing=True),
        Q("symptom.current_syncope", "Current Syncope", "boolean", "syncope", "혈압약 복용 후 실신했거나 지금 쓰러질 것 같은 심한 증상이 있나요?", 120, [G["postural"], G["immediate-safety"]], S, safety_relevant=True),
        Q("symptom.paroxysmal_headache_palpitations_sweating", "Paroxysmal Headache Palpitations and Sweating", "boolean", "paroxysmal-cluster", "혈압이 크게 오르내리면서 발작적인 두통, 두근거림, 창백함·식은땀 또는 복통이 함께 반복되나요?", 119, [G["immediate-safety"]], S, safety_relevant=True),
        Q("symptom.postural_dizziness", "Postural Dizziness", "boolean", "postural-dizziness", "앉거나 누웠다가 일어날 때 어지럽거나 눈앞이 캄캄한가요?", 105, [G["postural"], G["medication"]], R),
        Q("event.recent_fall", "Recent Fall", "boolean", "fall", "최근 어지럼이나 균형 문제로 넘어졌나요?", 104, [G["postural"]], R),
        Q("medication.antihypertensive_current_list", "Current Antihypertensive Medicines", "string", "medicine-list", "현재 혈압약 이름, 용량, 하루 횟수와 실제 복용 방법을 알려주세요.", 115, [G["medication"]], F),
        Q("medication.missed_dose_frequency", "Missed Dose Frequency", "coded", "missed-doses", "최근 한 달 동안 혈압약을 빼먹은 정도는 없음, 드물게, 주 1회 이상, 거의 매일 중 무엇인가요?", 114, [G["medication"]], F, allowed_values=["none", "rare", "weekly_or_more", "almost_daily"], reuse_existing=True),
        Q("medication.recent_start_stop_dose_change", "Recent Medicine Start Stop or Dose Change", "string", "recent-change", "최근 혈압약을 시작·중단·증량·감량한 내용과 날짜가 있나요?", 103, [G["medication"]], F, reuse_existing=True),
        Q("medication.suspected_adverse_effects", "Suspected Adverse Effects", "string", "adverse-effects", "혈압약과 관련 있다고 생각하는 어지럼, 부종, 기침, 피로 또는 다른 불편이 있나요?", 102, [G["medication"], G["postural"]], F, reuse_existing=True),
        Q("medication.blood_pressure_raising_products", "Blood Pressure Raising Medicines or Products", "string", "raising-products", "소염진통제, 코막힘약, 스테로이드, 피임약·호르몬, 각성제, 한약·보충제처럼 혈압에 영향을 줄 수 있는 제품을 사용하나요?", 98, [G["medication"], G["cardiovascular-risk"]], R),
        Q("history.cardiovascular_or_cerebrovascular_disease", "Cardiovascular or Cerebrovascular Disease", "boolean", "cvd-history", "심근경색, 협심증, 심부전, 뇌졸중 또는 말초혈관질환을 진단받은 적이 있나요?", 101, [G["cardiovascular-risk"]], R),
        Q("history.kidney_impairment", "Kidney Impairment", "boolean", "kidney-history", "만성콩팥병, 단백뇨, 신장기능 저하 또는 투석 병력이 있나요?", 100, [G["cardiovascular-risk"], G["monitoring"]], R, reuse_existing=True),
        Q("history.diabetes", "Diabetes History", "boolean", "diabetes", "당뇨병을 진단받았나요?", 99, [G["cardiovascular-risk"]], R),
        Q("symptom.sleep_apnoea_features", "Sleep Apnoea Features", "boolean", "sleep-apnoea", "코골이가 심하거나 자다가 숨이 멎는다는 말을 듣거나 낮에 매우 졸린가요?", 88, [G["cardiovascular-risk"]], R),
        Q("lifestyle.tobacco_current", "Current Tobacco Use", "coded", "tobacco", "현재 담배나 전자담배를 사용하나요?", 95, [G["self-management"], G["cardiovascular-risk"]], R, allowed_values=["never", "former", "current", "unknown"]),
        Q("lifestyle.alcohol_pattern", "Alcohol Pattern", "string", "alcohol", "술은 일주일에 며칠, 한 번에 어느 정도 마시나요?", 94, [G["self-management"]], R),
        Q("lifestyle.salt_intake", "Salt Intake", "coded", "salt", "국물·찌개·젓갈·가공식품 등 짠 음식 섭취는 적음, 보통, 많음 중 어디에 가깝나요?", 93, [G["self-management"]], F, allowed_values=["low", "moderate", "high", "uncertain"]),
        Q("lifestyle.physical_activity", "Physical Activity", "string", "activity", "최근 일주일의 걷기나 중강도 운동 횟수와 시간을 알려주세요.", 92, [G["self-management"]], F),
        Q("patient.recent_weight_or_weight_change", "Recent Weight or Weight Change", "string", "weight", "현재 체중과 최근 변화가 있다면 알려주세요.", 90, [G["self-management"], G["cardiovascular-risk"]], R),
        Q("hypertension.monitoring_tests_due_or_known", "Hypertension Monitoring Tests", "string", "monitoring-tests", "최근 신장기능·전해질·소변 단백, 혈당, 지질 또는 심전도 검사 결과와 다음 검사 일정이 있나요?", 89, [G["monitoring"]], F),
        Q("hypertension.patient_goal_or_question", "Patient Goal or Question", "string", "patient-goal", "이번 추적관리에서 가장 확인하거나 개선하고 싶은 것은 무엇인가요?", 86, [G["self-management"], G["medication"]], F),
    ]
    severe = {"fact": "blood_pressure.repeated_180_120_or_higher", "equals": True}
    pregnancy = {"fact": "patient.pregnant_or_postpartum", "in": ["pregnant", "postpartum_6_weeks"]}
    rules = [
        safety_rule(P, "severe-bp-confusion", {"all": [severe, {"fact": "symptom.new_confusion", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "severe-bp-chest-pain", {"all": [severe, {"fact": "symptom.chest_pain", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "severe-bp-dyspnea", {"all": [severe, {"fact": "symptom.severe_dyspnea", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "severe-bp-focal-deficit", {"all": [severe, {"fact": "symptom.new_focal_neurological_deficit", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "severe-bp-low-urine", {"all": [severe, {"fact": "symptom.markedly_reduced_urine", "equals": True}]}, "urgent", 900),
        safety_rule(P, "pregnancy-severe-bp", {"all": [pregnancy, {"fact": "blood_pressure.pregnancy_160_110_or_higher", "equals": True}]}, "urgent", 950),
        safety_rule(P, "pregnancy-warning", {"all": [pregnancy, {"fact": "symptom.preeclampsia_warning_features", "equals": True}]}, "urgent", 950),
        safety_rule(P, "current-syncope", {"fact": "symptom.current_syncope", "equals": True}, "urgent", 900),
        safety_rule(P, "paroxysmal-cluster", {"fact": "symptom.paroxysmal_headache_palpitations_sweating", "equals": True}, "urgent", 880),
    ]
    return {
        "id": "knowledge.generated.hypertension-follow-up", "version": VERSION,
        "status": "research_only", "usage_modes": ["research_test", "simulation"],
        "source_manifest": "source-manifest.primary-care-hypertension-follow-up-research",
        "default_refresh": default_refresh(),
        "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()],
        "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries,
        "provenance": provenance(SOURCES),
    }


def source_docs():
    definitions = [
        ("source.nice.ng136.hypertension.2026", "NICE", "Hypertension in adults: diagnosis and management", "NG136-updated-2026", "https://www.nice.org.uk/guidance/ng136/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nice.ng133.pregnancy-hypertension.2023", "NICE", "Hypertension in pregnancy: diagnosis and management", "NG133-updated-2023", "https://www.nice.org.uk/guidance/ng133/chapter/Recommendations", "clinical_guideline", 1),
        ("source.nhs.high-blood-pressure.2026", "NHS", "High blood pressure", "accessed-2026-07-14", "https://www.nhs.uk/conditions/high-blood-pressure-hypertension/", "public_health_guidance", 7),
        ("source.stom.hypertension.20260714", "Infoclinic", "STOM hypertension terminology and MRCM", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/38341003", "terminology_server", 30),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, days in definitions:
        artifacts.append({
            "id": sid, "kind": "terminology_mrcm_query_summary" if days == 30 else "clinical_guidance_metadata",
            "publisher": publisher, "title": title, "version": version, "url": url,
            "language": "en", "digest": "live_response_summary_not_raw_cache" if days == 30 else "metadata_only_not_cached",
            "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown",
            "complete": False, "monitor_profile": profile, "monitor_interval_days": days,
            "last_monitored_at": "2026-07-14",
            "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"),
            "assertions": ["Build-Time source only; Runtime does not browse it; generated content remains unreviewed."],
        })
    research = {
        "id": "source-manifest.primary-care-hypertension-follow-up-research", "version": VERSION,
        "acquired_at": CREATED_AT, "status": "research_only", "artifacts": artifacts,
        "provenance": provenance([item[0] for item in definitions]),
    }
    paths = [
        ("source.repository.foundation", "repository_specification", "FOUNDATION.md", True),
        ("source.generated.hypertension-follow-up", "generated_clinical_knowledge", "knowledge/generated/cardiovascular/hypertension-follow-up/hypertension-follow-up.json", True),
        ("source.mapping.hypertension-follow-up", "terminology_mapping", "mappings/terminology/snomed-mrcm-hypertension-follow-up.json", False),
        ("source.external.hypertension-follow-up", "external_source_manifest", "sources/manifests/primary-care-hypertension-follow-up-research.json", False),
        ("source.policy.hypertension-follow-up", "runtime_policy", "policies/primary-care-hypertension-follow-up-completion.json", True),
    ]
    primary = {
        "id": "source-manifest.primary-care-hypertension-follow-up", "version": VERSION,
        "acquired_at": CREATED_AT,
        "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths],
        "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"]),
    }
    return primary, research


def cases(fragment_document):
    triggers = {
        "severe-bp-confusion": ["blood_pressure.repeated_180_120_or_higher", "symptom.new_confusion"],
        "severe-bp-chest-pain": ["blood_pressure.repeated_180_120_or_higher", "symptom.chest_pain"],
        "severe-bp-dyspnea": ["blood_pressure.repeated_180_120_or_higher", "symptom.severe_dyspnea"],
        "severe-bp-focal-deficit": ["blood_pressure.repeated_180_120_or_higher", "symptom.new_focal_neurological_deficit"],
        "severe-bp-low-urine": ["blood_pressure.repeated_180_120_or_higher", "symptom.markedly_reduced_urine"],
        "pregnancy-severe-bp": ["patient.pregnant_or_postpartum", "blood_pressure.pregnancy_160_110_or_higher"],
        "pregnancy-warning": ["patient.pregnant_or_postpartum", "symptom.preeclampsia_warning_features"],
        "current-syncope": ["symptom.current_syncope"],
        "paroxysmal-cluster": ["symptom.paroxysmal_headache_palpitations_sweating"],
    }
    output = {}
    for index, safety in enumerate(fragment_document["safety_rules"], 1):
        key = safety["id"].split("safety.", 1)[1]
        level = safety["then"]["safety_level"]
        hidden = {fact_id: {"value": True} for fact_id in triggers[key]}
        if "patient.pregnant_or_postpartum" in hidden:
            hidden["patient.pregnant_or_postpartum"] = {"value": "pregnant"}
        output[f"HTN-{key.upper()}.json"] = {
            "id": f"HTN-{key.upper()}", "simulation_language": "ko",
            "persona": {"age": 38 + index}, "initial_statement": {"ko": "고혈압 추적 진료를 받으러 왔어요."},
            "hidden_state": hidden,
            "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [safety["id"]], "expected_max_turns": 26, "forbidden_assertions": ["diagnosis.hypertensive_emergency", "recommendation.change_dose"]},
            "provenance": provenance(SOURCES),
        }
    hidden = {}
    for item in fragment_document["entries"]:
        fact = item["fact"]
        fid = fact["id"]
        if fact["value_type"] == "boolean":
            hidden[fid] = {"value": fid == "hypertension.follow_up.requested"}
        elif fact["value_type"] == "integer":
            hidden[fid] = {"value": 130 if fid.endswith("systolic") else 80}
        elif fact["value_type"] == "coded":
            hidden[fid] = {"value": fact.get("allowed_values", ["uncertain"])[-1]}
        else:
            hidden[fid] = {"value": "없음"}
    declined = "medication.antihypertensive_current_list"
    hidden.pop(declined)
    output["HTN-DATA-ABSENT.json"] = {
        "id": "HTN-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 58},
        "initial_statement": {"ko": "혈압약 정기 진료를 받으러 왔어요."}, "hidden_state": hidden,
        "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}},
        "expected": {"expected_data_absent_reasons": {declined: "asked-declined"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 42, "forbidden_assertions": ["diagnosis.controlled_hypertension", "recommendation.change_dose"]},
        "provenance": provenance(["source.nice.ng136.hypertension.2026", "specifications/clinical-memory.md"]),
    }
    return output


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(
        prefix=P, rfe=RFE, display="Hypertension Follow-up",
        intents=[("intent.characterize_follow_up", "Characterize Follow-up"), ("intent.screen_red_flags", "Screen Red Flags"), ("intent.risk_assessment", "Risk Assessment"), ("intent.follow_up_support", "Follow-up Support")],
    )
    primary, research = source_docs()
    concepts = [("38341003", "Hypertensive disorder, systemic arterial (disorder)", 22), ("59621000", "Essential hypertension (disorder)", 22), ("75367002", "Blood pressure (observable entity)", 22)]
    mapping = {
        "id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed",
        "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"},
        "focus_concepts": [{"code": code, "display": display, "attribute_count_returned": count} for code, display, count in concepts],
        "checks": [{"focus_code": code, "attribute_code": attribute, "allowed": True} for code in ("38341003", "59621000") for attribute in ("363698007", "246112005")],
        "unsupported_checks": [{"focus_code": "75367002", "reason": "observable_entity_not_modeled_with_finding_site_or_severity"}],
        "validation": {"method": "build_time_live_mrcm_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "partial_provisional_pass"},
        "provenance": provenance(["source.stom.hypertension.20260714"]),
    }
    documents = [
        ("knowledge/base/primary-care-hypertension-follow-up.json", graph),
        ("rules/base/primary-care-hypertension-follow-up.json", rules),
        ("knowledge/generated/cardiovascular/hypertension-follow-up/hypertension-follow-up.json", generated),
        ("mappings/terminology/snomed-mrcm-hypertension-follow-up.json", mapping),
        ("sources/manifests/primary-care-hypertension-follow-up.json", primary),
        ("sources/manifests/primary-care-hypertension-follow-up-research.json", research),
        ("policies/primary-care-hypertension-follow-up-completion.json", completion_policy(prefix=P, fragment=generated, presentation_fact="hypertension.follow_up.requested", question_budget=42, source_refs=SOURCES)),
    ]
    for path, document in documents:
        write_json(path, document)
    for name, case in cases(generated).items():
        write_json("simulation/patients/cardiovascular/hypertension-follow-up/" + name, case)


if __name__ == "__main__":
    main()
