# 설문·문진 자원 출처 및 권리 Inventory

기준일: 2026-08-13
상태: `draft / unreviewed`

> 이 문서는 저장소의 권리·출처 상태를 보수적으로 점검한 결과이며 법률 의견이 아니다. 내부 테스트는 저작권·전자 시행·번역 허가를 자동으로 면제하지 않는다.

## 요약

- 현재 자원: **78개**
- 외부 획득 후보군: **7개**
- source manifest artifact entry: **728개**
- 고유 source ID: **630개**
- 검증 오류: **0개**

### 자원 유형별 수

| 자원 유형 | 수 |
|---|---:|
| `adaptive_preventive_question_group` | 10 |
| `assessment_program` | 8 |
| `dynamic_clinical_interview` | 56 |
| `fhir_fixed_questionnaire` | 1 |
| `fixed_questionnaire` | 1 |
| `fixed_standardized_instrument` | 1 |
| `shared_assessment_component` | 1 |

## 해석 원칙

- 동적 문진은 프로젝트가 작성한 draft 질문이며 source-defined fixed questionnaire가 아니다.
- HIRA 평가 프로그램 중 공식 원문이 확인되지 않은 항목은 공식 평가도구가 아니라 연구용 문진 또는 기존 결과 입력 구조다.
- 국가건강검진 질문군은 공식 NHIS 설문 원본이 아니라 공식 제도 자료를 참고한 adaptive draft다.
- 공식 원문 기반 환자경험 Questionnaire는 내부 연구 source 상태만 기록되어 있어 외부 배포를 차단한다.
- PROMIS 문항은 현재 저장소에 탑재하지 않았다. 회사 내부 디지털 테스트도 HEAP 또는 별도 허가 필요 여부를 먼저 확인한다.

## 문항을 탑재하지 않은 외부 도구 참조

HIRA 프로그램에 이름이 등장하더라도 해당 척도의 문항을 시행한다는 뜻은 아니다. 현재는 도구명·버전·총점과 안전 관련 결과를 입력받는 구조이며, 실제 문항 탑재에는 도구별 권리 검토가 필요하다.

| 프로그램 | 참조 도구 | 현재 역할 | 권리 상태 |
|---|---|---|---|
| `hira.depression_outpatient` | `BDI` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `CES-D` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `CSDD` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `EPDS` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `GDS` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `HADS` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `HDRS` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `IDS` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `PHQ-9` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `QIDS` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `RRS` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |
| `hira.depression_outpatient` | `SNSB` | `name_version_score_and_safety_result_capture_only` | `instrument_specific_review_required` |

## 현재 자원

| ID | 유형 | 문항 | 원문 고정 | 내부 시험 | 외부 사용 gate |
|---|---|---:|:---:|---|---|
| `rfe.cough` | `dynamic_clinical_interview` | 70 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.fever` | `dynamic_clinical_interview` | 62 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.dyspnea` | `dynamic_clinical_interview` | 74 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.chest_pain` | `dynamic_clinical_interview` | 73 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.abdominal_pain` | `dynamic_clinical_interview` | 75 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.headache` | `dynamic_clinical_interview` | 76 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.dizziness_syncope` | `dynamic_clinical_interview` | 73 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.vomiting_diarrhea` | `dynamic_clinical_interview` | 74 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.urinary_symptoms` | `dynamic_clinical_interview` | 74 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.fatigue` | `dynamic_clinical_interview` | 75 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.back_pain` | `dynamic_clinical_interview` | 68 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.skin_complaint` | `dynamic_clinical_interview` | 104 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.medication_review` | `dynamic_clinical_interview` | 67 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.upper_respiratory_symptoms` | `dynamic_clinical_interview` | 75 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.palpitations` | `dynamic_clinical_interview` | 69 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.bowel_symptoms` | `dynamic_clinical_interview` | 67 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.focal_weakness_numbness` | `dynamic_clinical_interview` | 67 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.joint_limb_complaint` | `dynamic_clinical_interview` | 83 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.neck_pain` | `dynamic_clinical_interview` | 51 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.mental_health_sleep` | `dynamic_clinical_interview` | 87 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.edema` | `dynamic_clinical_interview` | 69 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.hypertension_follow_up` | `dynamic_clinical_interview` | 71 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.weight_constitutional_change` | `dynamic_clinical_interview` | 78 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.reproductive_genital_symptoms` | `dynamic_clinical_interview` | 51 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.menstrual_uterine_bleeding` | `dynamic_clinical_interview` | 51 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.eye_symptoms` | `dynamic_clinical_interview` | 48 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.ear_hearing_symptoms` | `dynamic_clinical_interview` | 50 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.diabetes_follow_up` | `dynamic_clinical_interview` | 69 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.oral_dental_symptoms` | `dynamic_clinical_interview` | 71 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.wound_minor_injury` | `dynamic_clinical_interview` | 62 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.memory_cognitive_concern` | `dynamic_clinical_interview` | 64 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.acute_confusion` | `dynamic_clinical_interview` | 64 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.pregnancy_postpartum_concern` | `dynamic_clinical_interview` | 86 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.allergy_concern` | `dynamic_clinical_interview` | 70 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.asthma_copd_follow_up` | `dynamic_clinical_interview` | 70 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.lump_lymph_node` | `dynamic_clinical_interview` | 60 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.dyspepsia_reflux` | `dynamic_clinical_interview` | 52 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.swallowing_difficulty` | `dynamic_clinical_interview` | 60 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.jaundice` | `dynamic_clinical_interview` | 75 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.thyroid_concern_follow_up` | `dynamic_clinical_interview` | 52 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.anemia_concern_follow_up` | `dynamic_clinical_interview` | 61 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.kidney_function_ckd_follow_up` | `dynamic_clinical_interview` | 60 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.liver_function_chronic_follow_up` | `dynamic_clinical_interview` | 48 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.epistaxis` | `dynamic_clinical_interview` | 51 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.tremor_movement_concern` | `dynamic_clinical_interview` | 56 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.seizure_event_follow_up` | `dynamic_clinical_interview` | 51 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.pediatric_growth_development` | `dynamic_clinical_interview` | 61 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.gait_falls_concern` | `dynamic_clinical_interview` | 55 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.breast_symptoms` | `dynamic_clinical_interview` | 53 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.test_result_follow_up` | `dynamic_clinical_interview` | 53 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.post_discharge_follow_up` | `dynamic_clinical_interview` | 58 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.tobacco_nicotine_counselling` | `dynamic_clinical_interview` | 65 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.alcohol_use_counselling` | `dynamic_clinical_interview` | 47 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.physical_activity_counselling` | `dynamic_clinical_interview` | 50 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.immunization_consultation` | `dynamic_clinical_interview` | 61 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `rfe.preoperative_assessment` | `dynamic_clinical_interview` | 81 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |
| `hira.long_term_care_hospital_inpatient.2026-cycle2-8` | `assessment_program` | 20 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.depression_outpatient` | `fixed_standardized_instrument` | 6 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.acute_stroke_event_history` | `assessment_program` | 7 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.rheumatoid_arthritis` | `assessment_program` | 1 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.medical_aid_psychiatry_patient_experience` | `assessment_program` | 6 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.mental_health_inpatient_patient_experience` | `assessment_program` | 6 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.anesthesia_patient_assessment` | `assessment_program` | 13 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.imaging_pre_examination_assessment` | `assessment_program` | 11 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.dementia_patient_proxy_assessment` | `assessment_program` | 9 | 아니오 | `allowed_for_project_authored_research_test_or_result_capture` | `rights_review_required` |
| `hira.inpatient_patient_experience.5th-2025` | `fixed_questionnaire` | 0 | 예 | `repository_research_source_only_rights_confirmation_pending` | `rights_review_required` |
| `kr.nhis.general.common` | `adaptive_preventive_question_group` | 7 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.general.age66.additional` | `adaptive_preventive_question_group` | 2 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.oral.general` | `adaptive_preventive_question_group` | 1 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.cancer.common` | `adaptive_preventive_question_group` | 3 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.cancer.gastric` | `adaptive_preventive_question_group` | 2 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.cancer.colorectal` | `adaptive_preventive_question_group` | 2 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.cancer.liver` | `adaptive_preventive_question_group` | 2 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.cancer.lung` | `adaptive_preventive_question_group` | 1 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.cancer.breast` | `adaptive_preventive_question_group` | 1 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr.nhis.cancer.cervical` | `adaptive_preventive_question_group` | 1 | 아니오 | `allowed_under_draft_limited_use_policy` | `documented_sources_only` |
| `kr-patient-experience-evaluation-5th-2025` | `fhir_fixed_questionnaire` | 26 | 예 | `repository_research_source_only_rights_confirmation_pending` | `rights_review_required` |
| `knowledge.shared.hira-pain-assessment` | `shared_assessment_component` | 2 | 아니오 | `allowed_under_draft_limited_use_policy` | `rights_review_required` |

## 외부 획득 후보

| 후보 | 현재 상태 | 저장소 문항 | 다음 단계 |
|---|---|:---:|---|
| `PROMIS` | `metadata_only_not_implemented` | 아니오 | Ask HealthMeasures whether the planned company-internal digital sandbox requires HEAP, then select one exact PROMIS measure for a controlled pilot. |
| `NIH Common Data Elements Repository` | `metadata_source_candidate` | 아니오 | Use CDE metadata to identify atomic concepts, but resolve the rights of every source instrument before copying an item or answer list. |
| `PhenX Toolkit` | `metadata_source_candidate` | 아니오 | Pilot concept and data-dictionary comparison without treating every hosted protocol as freely redistributable. |
| `CAHPS` | `metadata_source_candidate` | 아니오 | Request AHRQ permission before a Korean deployment and keep any comparison pilot distinct from the existing HIRA patient-experience questionnaire. |
| `지역사회건강조사 (Community Health Survey, CHS)` | `local_test_ingestion_supported_source_artifact_not_present` | 아니오 | Obtain the exact 2025 artifact through the official process, verify internal electronic-test rights, and register its local FHIR Questionnaire digest before enabling the restricted test loader. |
| `한국의료패널 (Korea Health Panel, KHP)` | `local_test_ingestion_supported_source_artifact_not_present` | 아니오 | Confirm the questionnaire appendix KOGL marker or written internal-test permission, then register the exact local FHIR Questionnaire and digest before enabling it. |
| `고령화연구패널조사 (Korean Longitudinal Study of Ageing, KLoSA)` | `local_test_ingestion_supported_declared_use_download_not_completed` | 아니오 | Complete the declared-use download workflow and embedded-scale rights review, then register the exact local FHIR Questionnaire and digest before enabling it. |

## 국내 자원 도입 순서

공개 페이지 접근은 문항 재사용 허가가 아니다. 아래 순서는 concept-level gap 분석 순서이며, 원문 문항·보기·채점 규칙은 권리 확인 전 Runtime에 넣지 않는다.

| 순서 | 자원 | 최신 확인본 | 현재 허용 | 현재 차단 |
|---:|---|---|---|---|
| 1 | `지역사회건강조사 (Community Health Survey, CHS)` | `2025` | source_metadata_registration, topic_and_variable_gap_discovery, independent_project_authored_atomic_question_design_with_separate_clinical_evidence, verified_user_supplied_or_licensed_FHIR_Questionnaire_in_restricted_test_store | verbatim_item_embedding, claiming_CHS_form_fidelity, automatic_LOINC_or_SNOMED_equivalence_from_survey_labels, runtime_scoring_or_population_norm_inference |
| 2 | `한국의료패널 (Korea Health Panel, KHP)` | `2025년 한국의료패널 조사표` | source_metadata_registration, concept_and_context_gap_discovery, independent_project_authored_atomic_question_design_with_separate_clinical_evidence, verified_user_supplied_or_licensed_FHIR_Questionnaire_in_restricted_test_store | verbatim_appendix_item_embedding, claiming_KHP_form_fidelity, reusing_embedded_third_party_scales_without_owner_review, using_population_associations_as_individual_clinical_rules |
| 3 | `고령화연구패널조사 (Korean Longitudinal Study of Ageing, KLoSA)` | `2024` | source_metadata_registration, older_adult_context_gap_discovery, independent_project_authored_atomic_question_design_with_separate_clinical_evidence, verified_user_supplied_or_licensed_FHIR_Questionnaire_in_restricted_test_store | automated_attachment_download_without_completing_the_declared_use_workflow, verbatim_item_embedding, claiming_KLoSA_form_fidelity, embedding_MMSE_or_other_third_party_scale_items, using_panel_associations_as_individual_clinical_rules |

## 우선 조치

1. Perform explicit rights review for the HIRA fixed patient-experience questionnaire before external distribution.
2. Obtain and verify the official NHIS questionnaire before claiming official-form fidelity or prepopulation compatibility.
3. Ask HealthMeasures whether the intended company-internal digital PROMIS sandbox requires HEAP and translation permission.
4. In order, compare CHS concepts, then KHP concepts, then KLoSA concepts against existing Facts without copying source-defined items.
5. For every domestic source, verify artifact-level rights and any embedded third-party scale rights before electronic administration.
6. Resolve unknown and restricted source statuses package-by-package before commercial deployment.
7. Add instrument owner, version, scoring, translation and electronic-administration rights to every future fixed questionnaire.

## 재생성 및 검증

```bash
python3 tools/inventory/build_questionnaire_source_rights_inventory.py
python3 tools/inventory/build_questionnaire_source_rights_inventory.py --check
python3 -m unittest tests.test_questionnaire_source_rights_inventory
```

기계 판독 원본: `coverage/questionnaire-source-rights-inventory-latest.json`
