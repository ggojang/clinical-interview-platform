# Multi-purpose interaction modes and legacy Chatbot compatibility

Status: Draft, unreviewed
Version: 0.1.0

## Decision

The Clinical Interview Platform remains the adaptive clinical-knowledge core. A host application may expose additional clinical-form, survey, screening-recommendation, and health-information modes through a separate service-mode router. This overlay does not change the existing public Chatbot's Reason-for-Encounter-first entry or its compiled Knowledge Package execution.

No mode is selected implicitly from demographics, an uploaded file, or an unrelated answer. With no explicit service-mode selection, `clinical_adaptive` is selected and the existing RFE workflow continues unchanged.

## User-facing grouping

The preferred application start groups the six execution modes under four familiar choices:

- `진료 준비`: adaptive clinical interview or a supplied clinical FHIR Questionnaire;
- `설문 참여`: a verified fixed conversational instrument or a supplied non-clinical Questionnaire;
- `추가 검진 추천받기`: supplemental screening interview and deterministic package comparison;
- `건강정보 묻기`: general informational support without independent diagnosis or treatment.

The current Custom GPT may continue to show its existing conversation starters. The four-choice start is a host-application concern, not a breaking requirement for the legacy Chatbot.

## Questionnaire authority and output

Adaptive clinical questions are generated from compiled atomic Facts and Rules. Source-defined fixed questionnaires and supplied FHIR Questionnaires control their own wording, order, answer options, and scoring. The LLM may explain or present those items but must not rewrite their clinical meaning. Automatic question terminology mapping remains excluded for fixed questionnaires unless the official source and mapping were explicitly verified.

Clinical adaptive output may project to a session-specific FHIR R4 Questionnaire and QuestionnaireResponse. Clinical structured forms produce a QuestionnaireResponse and may use SDC extraction only when the Questionnaire declares a verified extraction mapping. Non-clinical structured surveys do not extract clinical resources by default.

## Additional screening recommendation

The goal is to compare screening-center add-ons beyond the nationally provided screening baseline. The default entry is a short supplemental adaptive interview. The official NHIS questionnaire is offered only when the user wants it; it is not a mandatory gate.

If supplemental Facts already exist, a versioned mapping may prepopulate an official QuestionnaireResponse. Only exact or equivalent mappings may populate automatically. A compound official item is populated only when every required atomic source Fact is known. Partial and related mappings remain review candidates. The prepopulated response remains `in-progress` until the user reviews it.

The official Questionnaire/QuestionnaireResponse and the supplemental Questionnaire/QuestionnaireResponse remain separate. A FHIR Bundle may reference both. Recommendation output also records the package-catalog and policy versions. Candidate selection is deterministic; the LLM explains the comparison and uncertainty. The lowest-cost suitable option is always shown, duplicated national items are disclosed, and economic capacity is never inferred.

## Current test privacy boundary

The Runtime may hold necessary personal or health information in current-process memory to ask and answer relevant questions. It does not persist those answers to the repository, public Knowledge Action, database, raw logs, or analytics. Previewed FHIR resources and temporary uploads are discarded when the session closes or expires. ChatGPT or another model provider may have a separate retention policy outside this repository, so the existing public-test notice remains required.

## Implementation boundary

`runtime/service_modes.py` provides explicit routing while preserving the legacy default. `runtime/questionnaire_prepopulation.py` provides a source-immutable, review-required FHIR R4 prepopulation primitive. `preventive/package_recommendation.py` compares a supplied, versioned center catalog and cannot invent a recommendation when that catalog is absent.

The official 2026 NHIS Questionnaire resource and its linkId mapping are not asserted by this overlay until the official source is converted and verified. The prepopulation primitive is regression-tested with synthetic resources in the meantime.
