#!/usr/bin/env python3
"""Materialize unreviewed reproductive and genital symptom knowledge."""
from profile_support import *

P = "reproductive-genital-symptoms"
RFE = "rfe.reproductive_genital_symptoms"
M = "mapping.snomed-mrcm.reproductive-genital-symptoms"
SN = "http://snomed.info/sct"
SOURCES = [
    "source.nice.ng126.ectopic-pregnancy.2026",
    "source.nice.ng12.genital-symptoms.2026",
    "source.nhs.vaginal-discharge.2024",
    "source.nhs.pelvic-pain.2025",
    "source.nhs.sti.2024",
    "source.nhs.testicle-lumps.2023",
    "source.nhs.priapism.2026",
    "source.nhs.sexual-assault-support.2026",
]
G = {key: f"group.reproductive-genital.{key}" for key in (
    "routing", "shared-safety", "sexual-health", "background",
    "vaginal-vulvar-pelvic", "penile-urethral", "testicular-scrotal",
)}
C = ["intent.characterize_symptom"]
S = ["intent.screen_red_flags"]
R = ["intent.risk_assessment"]
D = ["intent.differentiate_common_causes"]


def Q(fid, display, value_type, key, wording, score, groups, intents, **kwargs):
    return entry(P, fid, display, value_type, key, wording, score, key, groups,
                 intents=intents, **kwargs)


def fragment():
    entries = [
        Q("genital.primary_symptom_group", "Primary Genital Symptom Group", "coded", "primary-group", "가장 불편한 부위는 질·외음부·골반, 음경·요도, 고환·음낭 중 어디인가요? 해당 부위가 없거나 확실하지 않으면 기타·불명확을 선택할 수 있습니다.", 130, [G["routing"]], C, allowed_values=["vaginal_vulvar_pelvic", "penile_urethral", "testicular_scrotal", "other_unclear"]),
        Q("genital.symptom_duration", "Genital Symptom Duration", "string", "duration", "증상은 언제 시작됐고 계속되는지 반복되는지 알려주세요.", 108, [G["background"]], C),
        Q("genital.severe_injury_or_uncontrolled_bleeding", "Severe Genital Injury or Uncontrolled Bleeding", "boolean", "severe-injury-bleeding", "성기나 골반 부위에 큰 외상이 있거나 압박해도 멈추지 않는 심한 출혈이 있나요?", 129, [G["shared-safety"]], S, safety_relevant=True),
        Q("genital.rapid_spread_discoloration_or_tissue_change", "Rapid Genital Spread Discoloration or Tissue Change", "boolean", "rapid-spread", "성기·회음부 통증과 부종이 빠르게 퍼지거나 피부가 검붉게 변하고 물집·조직 손상이 보이나요?", 128, [G["shared-safety"]], S, safety_relevant=True),
        Q("symptom.fever_or_systemically_unwell", "Fever or Systemically Unwell", "boolean", "fever-unwell", "열, 오한 또는 온몸이 매우 아픈 느낌이 있나요?", 127, [G["shared-safety"]], S, safety_relevant=True),
        Q("symptom.unable_to_urinate", "Unable to Urinate", "boolean", "urinary-retention", "소변이 마려운데 전혀 나오지 않거나 방광이 심하게 불편한가요?", 126, [G["shared-safety"]], S, safety_relevant=True, reuse_existing=True),
        Q("safeguarding.unwanted_sexual_contact", "Unwanted Sexual Contact", "coded", "unwanted-contact", "원하지 않은 성적 접촉이나 강요와 관련된 증상인가요? 답변하지 않아도 됩니다.", 125, [G["shared-safety"]], S, safety_relevant=True, allowed_values=["yes_recent", "yes_past", "no", "prefer_not_to_answer"]),
        Q("safeguarding.safe_now", "Safe Now", "coded", "safe-now", "현재 안전한 곳에 있고 상대방의 즉각적인 위협이 없나요?", 124, [G["shared-safety"]], S, safety_relevant=True, allowed_values=["safe", "not_safe", "uncertain", "not_applicable"]),
        Q("sexual_health.recent_new_or_unprotected_contact", "Recent New or Unprotected Sexual Contact", "coded", "sexual-contact", "최근 새 파트너와의 성접촉이나 콘돔 없이 한 성접촉이 있었나요? 답변하지 않아도 됩니다.", 93, [G["sexual-health"]], R, allowed_values=["yes", "no", "uncertain", "prefer_not_to_answer"]),
        Q("sexual_health.partner_symptoms_or_sti_notice", "Partner Symptoms or STI Notice", "boolean", "partner-symptoms", "파트너에게 분비물·통증·궤양 같은 증상이 있거나 STI 진단·검사 안내를 받은 적이 있나요?", 92, [G["sexual-health"]], R),
        Q("sexual_health.recent_sti_test_or_history", "Recent STI Test or History", "string", "sti-history", "최근 STI 검사 시기와 결과, 과거 진단·치료가 있다면 알려주세요.", 91, [G["sexual-health"]], R),
        Q("medication.genital_recent_treatment_or_antibiotic", "Recent Genital Treatment or Antibiotic", "string", "recent-treatment", "최근 항생제, 항진균제, 연고, 호르몬 또는 자가치료를 사용했나요?", 88, [G["background"]], D),
        Q("history.diabetes_immunosuppression_or_recurrent_genital_problem", "Diabetes Immunosuppression or Recurrent Genital Problem", "string", "background-history", "당뇨·면역저하가 있거나 비슷한 성기 증상이 반복된 적이 있나요?", 87, [G["background"]], R),
        Q("exposure.genital_irritant_or_hygiene_product", "Genital Irritant or Hygiene Product", "string", "irritant", "새 비누·세정제·윤활제·콘돔·생리용품·면도 또는 꽉 끼는 옷과 관련 있나요?", 86, [G["background"]], D),
        Q("genital.other_detail_or_patient_priority", "Other Genital Detail or Patient Priority", "string", "other-detail", "질문에 없지만 꼭 전달하고 싶은 증상이나 가장 걱정되는 점을 알려주세요.", 80, [G["routing"], G["background"]], C),

        Q("vaginal.discharge_changed", "Changed Vaginal Discharge", "boolean", "vaginal-discharge", "평소와 다른 질 분비물이 있나요?", 118, [G["vaginal-vulvar-pelvic"]], C, terminology_binding={"system": SN, "code": "271939006"}),
        Q("vaginal.discharge_character", "Vaginal Discharge Character", "string", "discharge-character", "분비물의 양, 색, 냄새와 묽기·덩어리·거품 같은 모양을 알려주세요.", 107, [G["vaginal-vulvar-pelvic"]], C),
        Q("vulvar.itch_soreness_or_swelling", "Vulvar Itch Soreness or Swelling", "boolean", "vulvar-itch", "외음부가 가렵거나 화끈거리고 붓거나 아픈가요?", 106, [G["vaginal-vulvar-pelvic"]], C, terminology_binding={"system": SN, "code": "67882000"}),
        Q("vulvar.blister_ulcer_lump_or_mass", "Vulvar Blister Ulcer Lump or Mass", "boolean", "vulvar-lesion", "외음부나 질 입구에 물집, 궤양, 사마귀, 멍울 또는 만져지는 덩이가 있나요?", 105, [G["vaginal-vulvar-pelvic"]], R),
        Q("pelvic.pain_current", "Current Pelvic Pain", "boolean", "pelvic-pain", "아랫배나 골반 통증이 있나요?", 123, [G["vaginal-vulvar-pelvic"]], S, safety_relevant=True),
        Q("pelvic.pain_severe_worsening_or_tender", "Severe or Worsening Pelvic Pain", "boolean", "severe-pelvic-pain", "통증이 매우 심하거나 빠르게 악화되며 움직이거나 만질 때 더 아픈가요?", 122, [G["vaginal-vulvar-pelvic"]], S, safety_relevant=True),
        Q("vaginal.bleeding_pattern", "Vaginal Bleeding Pattern", "coded", "bleeding-pattern", "비정상 출혈은 없음, 생리 사이, 성관계 후, 폐경 후, 임신 중, 기타 중 무엇인가요?", 121, [G["vaginal-vulvar-pelvic"]], S, safety_relevant=True, allowed_values=["none", "between_periods", "after_sex", "postmenopausal", "during_possible_pregnancy", "other"]),
        Q("vaginal.heavy_bleeding", "Heavy Vaginal Bleeding", "boolean", "heavy-bleeding", "패드를 매우 자주 갈 정도의 많은 출혈, 큰 혈덩이 또는 멈추지 않는 출혈이 있나요?", 120, [G["vaginal-vulvar-pelvic"]], S, safety_relevant=True),
        Q("pregnancy.possible_or_test_result", "Pregnancy Possibility or Test Result", "coded", "pregnancy", "임신 가능성은 있음, 검사 양성, 검사 음성, 해당 없음, 불확실 중 무엇인가요?", 119, [G["vaginal-vulvar-pelvic"]], S, safety_relevant=True, allowed_values=["possible", "positive", "negative", "not_applicable", "uncertain"]),
        Q("pregnancy.fainting_shoulder_tip_or_collapse", "Pregnancy Fainting Shoulder Tip Pain or Collapse", "boolean", "ectopic-warning", "임신 가능성이 있으면서 어지럼·실신, 어깨 끝 통증 또는 쓰러짐이 있나요?", 117, [G["vaginal-vulvar-pelvic"]], S, safety_relevant=True),
        Q("vaginal.menstrual_or_menopause_context", "Menstrual or Menopause Context", "string", "menstrual-context", "마지막 생리일, 주기 변화, 폐경 여부와 호르몬·피임 사용을 알려주세요.", 104, [G["vaginal-vulvar-pelvic"]], R),
        Q("vaginal.dysuria_or_urinary_frequency", "Vaginal Branch Dysuria or Frequency", "boolean", "vaginal-urinary", "소변볼 때 아프거나 평소보다 자주·급하게 보나요?", 103, [G["vaginal-vulvar-pelvic"]], R),
        Q("vaginal.deep_pain_during_sex", "Deep Pain during Sex", "boolean", "dyspareunia", "성관계 중이나 후에 깊은 골반 통증이 있나요?", 102, [G["vaginal-vulvar-pelvic"]], R),
        Q("vaginal.recent_birth_procedure_or_iud", "Recent Birth Procedure or IUD", "string", "procedure-context", "최근 출산·유산·임신중지·골반 시술 또는 자궁내장치 삽입이 있었나요?", 101, [G["vaginal-vulvar-pelvic"]], R),
        Q("vaginal.dryness_or_hormonal_context", "Vaginal Dryness or Hormonal Context", "boolean", "dryness", "질 건조, 성교통 또는 임신·수유·폐경·암치료와 관련된 호르몬 변화가 있나요?", 90, [G["vaginal-vulvar-pelvic"]], D),

        Q("penile.discharge", "Penile Discharge", "boolean", "penile-discharge", "음경 끝에서 평소와 다른 분비물이 나오나요?", 118, [G["penile-urethral"]], C, terminology_binding={"system": SN, "code": "2910007"}),
        Q("penile.dysuria", "Penile Branch Dysuria", "boolean", "penile-dysuria", "소변볼 때 음경이나 요도가 따갑거나 아픈가요?", 107, [G["penile-urethral"]], C),
        Q("penile.rash_itch_swelling_or_odor", "Penile Rash Itch Swelling or Odor", "boolean", "penile-rash", "음경 끝이나 포피가 붓고 가렵거나 아프고, 발진·냄새가 있나요?", 106, [G["penile-urethral"]], C),
        Q("penile.blister_ulcer_lump_or_persistent_change", "Penile Blister Ulcer Lump or Persistent Change", "boolean", "penile-lesion", "음경에 물집, 궤양, 사마귀, 멍울 또는 낫지 않는 피부 변화가 있나요?", 105, [G["penile-urethral"]], R),
        Q("penile.foreskin_trapped_with_glans_swelling", "Foreskin Trapped with Glans Swelling", "boolean", "trapped-foreskin", "젖혀진 포피가 원래 위치로 돌아오지 않고 귀두가 심하게 붓고 아픈가요?", 123, [G["penile-urethral"]], S, safety_relevant=True),
        Q("penile.erection_over_three_to_four_hours", "Erection over Three to Four Hours", "boolean", "priapism", "성적 자극과 무관하게 아픈 발기가 3~4시간 넘게 지속되나요?", 122, [G["penile-urethral"]], S, safety_relevant=True),
        Q("penile.painful_swelling_with_urinary_retention", "Painful Penile Swelling with Urinary Retention", "boolean", "penile-retention", "음경·포피가 심하게 붓고 아프면서 소변을 볼 수 없나요?", 121, [G["penile-urethral"]], S, safety_relevant=True),
        Q("penile.erectile_ejaculatory_or_curvature_change", "Erectile Ejaculatory or Curvature Change", "string", "sexual-function", "발기, 사정, 통증 또는 새로 생긴 휘어짐 변화가 있나요?", 100, [G["penile-urethral"]], R),
        Q("penile.blood_in_semen_or_urethral_bleeding", "Blood in Semen or Urethral Bleeding", "boolean", "blood-semen", "정액에 피가 섞이거나 요도에서 출혈하나요?", 99, [G["penile-urethral"]], R),
        Q("penile.recent_injury_or_instrumentation", "Recent Penile Injury or Instrumentation", "string", "penile-injury", "최근 성관계·운동 중 외상, 도뇨관·시술 또는 이물질 사용이 있었나요?", 98, [G["penile-urethral"]], R),

        Q("testicular.sudden_severe_unilateral_pain", "Sudden Severe Unilateral Testicular Pain", "boolean", "sudden-testicle-pain", "한쪽 고환에 갑자기 심한 통증이 시작됐나요?", 123, [G["testicular-scrotal"]], S, safety_relevant=True, terminology_binding={"system": SN, "code": "63901009"}),
        Q("testicular.pain_over_one_hour_or_at_rest", "Testicular Pain over One Hour or at Rest", "boolean", "testicle-pain-hour", "고환 통증이 1시간 넘게 지속되거나 쉬어도 계속되나요?", 122, [G["testicular-scrotal"]], S, safety_relevant=True),
        Q("testicular.pain_with_nausea_vomiting_or_abdominal_pain", "Testicular Pain with Nausea Vomiting or Abdominal Pain", "boolean", "testicle-nausea", "고환 통증과 함께 메스꺼움·구토 또는 아랫배 통증이 있나요?", 121, [G["testicular-scrotal"]], S, safety_relevant=True),
        Q("testicular.swelling_redness_or_position_change", "Testicular Swelling Redness or Position Change", "boolean", "scrotal-swelling", "음낭이 붓거나 붉고, 한쪽 고환 위치가 평소보다 높거나 달라 보이나요?", 120, [G["testicular-scrotal"]], S, safety_relevant=True),
        Q("testicular.painless_lump_shape_or_texture_change", "Painless Testicular Lump Shape or Texture Change", "boolean", "testicle-lump", "통증이 없더라도 고환의 멍울, 커짐, 모양·단단함 변화가 있나요?", 107, [G["testicular-scrotal"]], R),
        Q("testicular.dull_ache_or_heaviness", "Testicular Dull Ache or Heaviness", "boolean", "testicle-ache", "고환·음낭의 묵직함이나 계속되는 뻐근한 통증이 있나요?", 106, [G["testicular-scrotal"]], C),
        Q("testicular.recent_trauma_activity_or_surgery", "Recent Testicular Trauma Activity or Surgery", "string", "testicle-context", "최근 외상, 격한 운동, 수술·시술 또는 탈장 병력이 있나요?", 101, [G["testicular-scrotal"]], R),
        Q("testicular.urinary_or_urethral_symptoms", "Testicular Branch Urinary or Urethral Symptoms", "boolean", "testicle-urinary", "소변 통증·빈뇨 또는 음경 분비물이 함께 있나요?", 100, [G["testicular-scrotal"]], R),
        Q("testicular.fertility_or_undescended_history", "Fertility or Undescended Testis History", "string", "testicle-history", "잠복고환, 불임 평가, 과거 고환 염전·감염 또는 관련 수술 병력이 있나요?", 97, [G["testicular-scrotal"]], R),
    ]
    pregnant = {"fact": "pregnancy.possible_or_test_result", "in": ["possible", "positive", "uncertain"]}
    abnormal_bleeding = {"fact": "vaginal.bleeding_pattern", "in": ["between_periods", "after_sex", "during_possible_pregnancy", "other"]}
    rules = [
        safety_rule(P, "severe-injury-bleeding", {"fact": "genital.severe_injury_or_uncontrolled_bleeding", "equals": True}, "emergency", 1000),
        safety_rule(P, "rapid-spread-fever", {"all": [{"fact": "genital.rapid_spread_discoloration_or_tissue_change", "equals": True}, {"fact": "symptom.fever_or_systemically_unwell", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "not-safe-after-assault", {"all": [{"fact": "safeguarding.unwanted_sexual_contact", "in": ["yes_recent", "yes_past"]}, {"fact": "safeguarding.safe_now", "in": ["not_safe", "uncertain"]}]}, "emergency", 1000),
        safety_rule(P, "pregnancy-pain-faint-heavy", {"all": [pregnant, {"fact": "pelvic.pain_current", "equals": True}, {"fact": "pregnancy.fainting_shoulder_tip_or_collapse", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "severe-pelvic-heavy-bleeding", {"all": [{"fact": "pelvic.pain_severe_worsening_or_tender", "equals": True}, {"fact": "vaginal.heavy_bleeding", "equals": True}]}, "emergency", 1000),
        safety_rule(P, "pregnancy-pain-bleeding", {"all": [pregnant, {"fact": "pelvic.pain_current", "equals": True}, abnormal_bleeding]}, "urgent", 950),
        safety_rule(P, "pelvic-pain-fever", {"all": [{"fact": "pelvic.pain_current", "equals": True}, {"fact": "symptom.fever_or_systemically_unwell", "equals": True}]}, "urgent", 900),
        safety_rule(P, "priapism", {"fact": "penile.erection_over_three_to_four_hours", "equals": True}, "emergency", 1000),
        safety_rule(P, "trapped-foreskin", {"fact": "penile.foreskin_trapped_with_glans_swelling", "equals": True}, "emergency", 1000),
        safety_rule(P, "penile-retention", {"fact": "penile.painful_swelling_with_urinary_retention", "equals": True}, "urgent", 900),
        safety_rule(P, "sudden-testicle-pain", {"fact": "testicular.sudden_severe_unilateral_pain", "equals": True}, "emergency", 1000),
        safety_rule(P, "testicle-pain-nausea", {"fact": "testicular.pain_with_nausea_vomiting_or_abdominal_pain", "equals": True}, "emergency", 1000),
        safety_rule(P, "testicle-pain-over-hour", {"fact": "testicular.pain_over_one_hour_or_at_rest", "equals": True}, "emergency", 1000),
        safety_rule(P, "scrotal-pain-fever", {"all": [{"fact": "testicular.swelling_redness_or_position_change", "equals": True}, {"fact": "symptom.fever_or_systemically_unwell", "equals": True}]}, "urgent", 900),
        safety_rule(P, "global-retention-swelling", {"all": [{"fact": "symptom.unable_to_urinate", "equals": True}, {"fact": "genital.rapid_spread_discoloration_or_tissue_change", "equals": True}]}, "urgent", 900),
    ]
    return {"id": "knowledge.generated.reproductive-genital-symptoms", "version": VERSION, "status": "research_only", "usage_modes": ["research_test", "simulation"], "source_manifest": "source-manifest.primary-care-reproductive-genital-symptoms-research", "default_refresh": default_refresh(), "extra_nodes": [{"id": value, "type": "ClinicalGroup", "display": value.split(".")[-1]} for value in G.values()], "group_hypothesis_edges": [], "safety_rules": rules, "entries": entries, "provenance": provenance(SOURCES)}


def source_docs():
    definitions = [
        ("source.nice.ng126.ectopic-pregnancy.2026", "NICE", "Ectopic pregnancy and miscarriage", "NG126-updated-2026", "https://www.nice.org.uk/guidance/NG126/chapter/symptoms-and-signs-of-ectopic-pregnancy-and-initial-assessment", "clinical_guideline", 1),
        ("source.nice.ng12.genital-symptoms.2026", "NICE", "Suspected cancer — genital symptoms", "NG12-updated-2026", "https://www.nice.org.uk/guidance/ng12/chapter/Recommended-actions-organised-by-symptom-and-findings-of-primary-care-investigations", "clinical_guideline", 1),
        ("source.nhs.vaginal-discharge.2024", "NHS", "Vaginal discharge", "reviewed-2024-02-15", "https://www.nhs.uk/symptoms/vaginal-discharge/", "public_health_guidance", 7),
        ("source.nhs.pelvic-pain.2025", "NHS", "Pelvic pain", "reviewed-2025-11-24", "https://www.nhs.uk/symptoms/pelvic-pain/", "public_health_guidance", 7),
        ("source.nhs.sti.2024", "NHS", "Sexually transmitted infections", "accessed-2026-07-14", "https://www.nhs.uk/conditions/sexually-transmitted-infections-stis/", "public_health_guidance", 7),
        ("source.nhs.testicle-lumps.2023", "NHS", "Testicle lumps and swellings", "reviewed-2023-07-18", "https://www.nhs.uk/symptoms/testicle-lumps-and-swellings/", "public_health_guidance", 7),
        ("source.nhs.priapism.2026", "NHS", "Priapism", "accessed-2026-07-14", "https://www.nhs.uk/symptoms/priapism-painful-erections/", "public_health_guidance", 7),
        ("source.nhs.sexual-assault-support.2026", "NHS", "Help after rape and sexual assault", "accessed-2026-07-14", "https://www.nhs.uk/live-well/sexual-health/help-after-rape-and-sexual-assault/", "public_health_guidance", 7),
        ("source.stom.reproductive-genital.20260714", "Infoclinic", "STOM reproductive and genital symptom terminology", "SNOMEDCT-20260701", "https://stom.infoclinic.co/allow/attributes/SNOMEDCT/271939006", "terminology_server", 30),
    ]
    artifacts = []
    for sid, publisher, title, version, url, profile, days in definitions:
        artifacts.append({"id": sid, "kind": "terminology_mrcm_query_summary" if days == 30 else "clinical_guidance_metadata", "publisher": publisher, "title": title, "version": version, "url": url, "language": "en", "digest": "live_response_summary_not_raw_cache" if days == 30 else "metadata_only_not_cached", "license_status": "restricted" if publisher in {"NICE", "Infoclinic"} else "unknown", "complete": False, "monitor_profile": profile, "monitor_interval_days": days, "last_monitored_at": "2026-07-14", "next_monitor_at": "2026-08-13" if days == 30 else ("2026-07-21" if days == 7 else "2026-07-15"), "assertions": ["Build-Time source only; Runtime does not browse it; generated content remains unreviewed."]})
    research = {"id": "source-manifest.primary-care-reproductive-genital-symptoms-research", "version": VERSION, "acquired_at": CREATED_AT, "status": "research_only", "artifacts": artifacts, "provenance": provenance([item[0] for item in definitions])}
    paths = [("source.repository.foundation", "repository_specification", "FOUNDATION.md", True), ("source.generated.reproductive-genital", "generated_clinical_knowledge", "knowledge/generated/genitourinary/reproductive-genital-symptoms/reproductive-genital-symptoms.json", True), ("source.mapping.reproductive-genital", "terminology_mapping", "mappings/terminology/snomed-mrcm-reproductive-genital-symptoms.json", False), ("source.external.reproductive-genital", "external_source_manifest", "sources/manifests/primary-care-reproductive-genital-symptoms-research.json", False), ("source.policy.reproductive-genital", "runtime_policy", "policies/primary-care-reproductive-genital-symptoms-completion.json", True)]
    primary = {"id": "source-manifest.primary-care-reproductive-genital-symptoms", "version": VERSION, "acquired_at": CREATED_AT, "artifacts": [{"id": sid, "kind": kind, "publisher": "clinical-interview-platform", "version": VERSION, "language": "en", "path": path, "digest": "computed_at_build", "license_status": "allowed" if complete else "unknown", "complete": complete} for sid, kind, path, complete in paths], "provenance": provenance(["FOUNDATION.md", "PROJECT_CONTEXT.md"])}
    return primary, research


def completion(fragment_document):
    branch_groups = {"vaginal_vulvar_pelvic": G["vaginal-vulvar-pelvic"], "penile_urethral": G["penile-urethral"], "testicular_scrotal": G["testicular-scrotal"]}
    cases = {case: [item["fact"]["id"] for item in fragment_document["entries"] if group in item.get("supports", [])] for case, group in branch_groups.items()}
    branch_facts = {fact_id for values in cases.values() for fact_id in values}
    shared = [item["fact"]["id"] for item in fragment_document["entries"] if item["fact"]["id"] not in branch_facts]
    always = ["genital.primary_symptom_group", "genital.severe_injury_or_uncontrolled_bleeding", "genital.rapid_spread_discoloration_or_tissue_change", "symptom.fever_or_systemically_unwell", "symptom.unable_to_urinate", "safeguarding.unwanted_sexual_contact", "safeguarding.safe_now"]
    return {"id": "policy.primary-care-reproductive-genital-symptoms-completion", "version": VERSION, "status": "research_only", "addressed_fact_states": ["known", "unknown", "not_applicable"], "required_facts": {"always": always, "routine": [fact_id for fact_id in shared if fact_id not in always]}, "conditional_required_facts": [{"selector_fact": "genital.primary_symptom_group", "cases": cases, "default": []}], "clarification_facts_by_rule": {}, "question_budget": {"routine": 38, "clarify": 12}, "provenance": provenance(SOURCES)}


def cases(fragment_document):
    triggers = {
        "severe-injury-bleeding": ("other_unclear", ["genital.severe_injury_or_uncontrolled_bleeding"]),
        "rapid-spread-fever": ("other_unclear", ["genital.rapid_spread_discoloration_or_tissue_change", "symptom.fever_or_systemically_unwell"]),
        "not-safe-after-assault": ("other_unclear", ["safeguarding.unwanted_sexual_contact", "safeguarding.safe_now"]),
        "pregnancy-pain-faint-heavy": ("vaginal_vulvar_pelvic", ["pregnancy.possible_or_test_result", "pelvic.pain_current", "pregnancy.fainting_shoulder_tip_or_collapse"]),
        "severe-pelvic-heavy-bleeding": ("vaginal_vulvar_pelvic", ["pelvic.pain_severe_worsening_or_tender", "vaginal.heavy_bleeding"]),
        "pregnancy-pain-bleeding": ("vaginal_vulvar_pelvic", ["pregnancy.possible_or_test_result", "pelvic.pain_current", "vaginal.bleeding_pattern"]),
        "pelvic-pain-fever": ("vaginal_vulvar_pelvic", ["pelvic.pain_current", "symptom.fever_or_systemically_unwell"]),
        "priapism": ("penile_urethral", ["penile.erection_over_three_to_four_hours"]),
        "trapped-foreskin": ("penile_urethral", ["penile.foreskin_trapped_with_glans_swelling"]),
        "penile-retention": ("penile_urethral", ["penile.painful_swelling_with_urinary_retention"]),
        "sudden-testicle-pain": ("testicular_scrotal", ["testicular.sudden_severe_unilateral_pain"]),
        "testicle-pain-nausea": ("testicular_scrotal", ["testicular.pain_with_nausea_vomiting_or_abdominal_pain"]),
        "testicle-pain-over-hour": ("testicular_scrotal", ["testicular.pain_over_one_hour_or_at_rest"]),
        "scrotal-pain-fever": ("testicular_scrotal", ["testicular.swelling_redness_or_position_change", "symptom.fever_or_systemically_unwell"]),
        "global-retention-swelling": ("other_unclear", ["symptom.unable_to_urinate", "genital.rapid_spread_discoloration_or_tissue_change"]),
    }
    output = {}
    for index, rule in enumerate(fragment_document["safety_rules"], 1):
        key = rule["id"].split("safety.", 1)[1]
        branch, fact_ids = triggers[key]
        hidden = {"genital.primary_symptom_group": {"value": branch}, **{fact_id: {"value": True} for fact_id in fact_ids}}
        if key == "not-safe-after-assault":
            hidden["safeguarding.unwanted_sexual_contact"] = {"value": "yes_recent"}; hidden["safeguarding.safe_now"] = {"value": "not_safe"}
        if key in {"pregnancy-pain-faint-heavy", "pregnancy-pain-bleeding"}:
            hidden["pregnancy.possible_or_test_result"] = {"value": "possible"}
        if key == "pregnancy-pain-bleeding": hidden["vaginal.bleeding_pattern"] = {"value": "during_possible_pregnancy"}
        level = rule["then"]["safety_level"]
        output[f"GEN-{key.upper()}.json"] = {"id": f"GEN-{key.upper()}", "simulation_language": "ko", "persona": {"age": 22 + index}, "initial_statement": {"ko": "성기 부위 증상 때문에 상담받고 싶어요."}, "hidden_state": hidden, "expected": {"expected_safety_level": level, "expected_safety_action": "human_handoff", "expected_stop_reason": f"{level}_escalation", "expected_triggered_rules_contains": [rule["id"]], "expected_max_turns": 28, "forbidden_assertions": ["diagnosis.ectopic_pregnancy", "diagnosis.testicular_torsion", "diagnosis.sti"]}, "provenance": provenance(SOURCES)}
    policy = completion(fragment_document)
    required = set(policy["required_facts"]["always"] + policy["required_facts"]["routine"] + policy["conditional_required_facts"][0]["cases"]["vaginal_vulvar_pelvic"])
    hidden = {}
    by_id = {item["fact"]["id"]: item["fact"] for item in fragment_document["entries"]}
    for fid in required:
        fact = by_id[fid]
        if fact["value_type"] == "boolean": hidden[fid] = {"value": False}
        elif fact["value_type"] == "coded": hidden[fid] = {"value": fact.get("allowed_values", ["other"])[-1]}
        else: hidden[fid] = {"value": "없음"}
    hidden["genital.primary_symptom_group"] = {"value": "vaginal_vulvar_pelvic"}
    declined = "sexual_health.recent_new_or_unprotected_contact"; hidden.pop(declined)
    output["GEN-VAGINAL-DATA-ABSENT.json"] = {"id": "GEN-VAGINAL-DATA-ABSENT", "simulation_language": "ko", "persona": {"age": 34}, "initial_statement": {"ko": "질 분비물이 달라져서 상담받고 싶어요."}, "hidden_state": hidden, "response_behavior": {declined: {"dataAbsentReason": "asked-declined"}}, "expected": {"expected_data_absent_reasons": {declined: "asked-declined"}, "expected_safety_level": "routine", "expected_stop_reason": "required_targets_addressed_with_absent_data", "expected_max_turns": 34, "forbidden_assertions": ["diagnosis.vaginitis", "diagnosis.sti"]}, "provenance": provenance(["source.nhs.vaginal-discharge.2024", "specifications/clinical-memory.md"])}
    return output


def main():
    generated = fragment()
    graph, rules = base_graph_and_rules(prefix=P, rfe=RFE, display="Reproductive or Genital Symptoms", intents=[("intent.characterize_symptom", "Characterize Symptom"), ("intent.screen_red_flags", "Screen Red Flags"), ("intent.differentiate_common_causes", "Differentiate Common Sources"), ("intent.risk_assessment", "Risk Assessment")])
    primary, research = source_docs()
    concepts = [("271939006", "Vaginal discharge (finding)", 20), ("2910007", "Discharge from penis (finding)", 20), ("63901009", "Pain in testicle (finding)", 20), ("67882000", "Pruritus of vulva (disorder)", 22)]
    mapping = {"id": M, "version": VERSION, "status": "research_only", "review_status": "unreviewed", "terminology": {"system": SN, "version": "http://snomed.info/sct/900000000000207008/version/20260701", "source": "STOM"}, "focus_concepts": [{"code": code, "display": display, "attribute_count_returned": count} for code, display, count in concepts], "checks": [{"focus_code": code, "attribute_code": attribute, "allowed": True} for code, _, _ in concepts for attribute in ("363698007", "246112005")], "validation": {"method": "build_time_live_mrcm_summary", "checked_at": CREATED_AT, "raw_response_cached": False, "complete_mrcm_snapshot": False, "clinical_rule_authority": False, "result": "provisional_pass"}, "provenance": provenance(["source.stom.reproductive-genital.20260714"])}
    documents = [("knowledge/base/primary-care-reproductive-genital-symptoms.json", graph), ("rules/base/primary-care-reproductive-genital-symptoms.json", rules), ("knowledge/generated/genitourinary/reproductive-genital-symptoms/reproductive-genital-symptoms.json", generated), ("mappings/terminology/snomed-mrcm-reproductive-genital-symptoms.json", mapping), ("sources/manifests/primary-care-reproductive-genital-symptoms.json", primary), ("sources/manifests/primary-care-reproductive-genital-symptoms-research.json", research), ("policies/primary-care-reproductive-genital-symptoms-completion.json", completion(generated))]
    for path, document in documents: write_json(path, document)
    for name, case in cases(generated).items(): write_json("simulation/patients/genitourinary/reproductive-genital-symptoms/" + name, case)


if __name__ == "__main__": main()
