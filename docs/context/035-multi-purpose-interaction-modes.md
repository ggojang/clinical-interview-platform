# Purpose-first multi-purpose interaction core

Status: Draft, unreviewed
Version: 0.4.0

## Decision

The platform entry is now an interaction-purpose router. Clinical-form, survey, screening-recommendation, health-information, and adaptive clinical-interview modes are peers at the platform boundary. The existing Reason-for-Encounter engine remains intact inside `clinical_adaptive` and continues to execute compiled Knowledge Packages.

The first substantive message is routed when intent is clear. A symptom or follow-up statement enters `clinical_adaptive` immediately; a fixed-assessment alias opens that catalog or instrument; a supplied Questionnaire context selects the matching structured runner; and screening-add-on or health-information intent selects its own mode. Missing purpose does not default to clinical interview. The system asks one conversational purpose question and does not require a visual menu.

## User-facing grouping

The preferred application start groups the six execution modes under four familiar choices:

- `진료 준비`: adaptive clinical interview or a supplied clinical FHIR Questionnaire;
- `설문 참여`: a verified fixed conversational instrument or a supplied non-clinical Questionnaire;
- `추가 검진 추천받기`: supplemental screening interview and deterministic package comparison;
- `건강정보 묻기`: general informational support without independent diagnosis or treatment.

The current Custom GPT keeps its four existing conversation starters so the same deployed test surface remains usable. They are shortcuts into the purpose router rather than evidence that RFE is still the platform default.

For `clinical_adaptive`, the test context assumes that the user already has a scheduled visit unless the conversation says otherwise. The Runtime therefore does not ask a blanket initial red-flag questionnaire. It still evaluates every reported Fact and additional comment against compiled Safety Rules and interrupts the routine interview when a red flag is reported or suspected.

## Questionnaire authority and output

Adaptive clinical questions are generated from compiled atomic Facts and Rules. Source-defined fixed questionnaires and supplied FHIR Questionnaires control their own wording, order, answer options, and scoring. The LLM may explain or present those items but must not rewrite their clinical meaning. Automatic question terminology mapping remains excluded for fixed questionnaires unless the official source and mapping were explicitly verified.

Within `clinical_adaptive`, the patient-facing default follows the Custom GPT
test interaction contract rather than exposing the compiled authoring graph as
a Fact-by-Fact checklist. It asks one short question at a time, prints audited
answer shortcuts or non-coded examples when available, accepts free text, and
uses a semantic coverage ledger so one answer may satisfy several allowlisted
Facts. The ordinary scheduled-visit flow has an 18-question soft budget within
the GPT policy's 12–24 range. It may continue only for unresolved safety or a
value explicitly declared mandatory; unasked compiled Facts remain visible as
`not-asked` in the clinician handoff instead of being disguised as negative.

An enabled LLM adapter may map the opening free text to one implemented RFE and
extract several explicitly stated, allowlisted Facts from the current answer.
The model receives no prior answer values for this operation. Runtime validates
every Fact identifier, value type, allowed token, unit and numeric range before
merge. The model may also choose only among already eligible candidates. It
cannot invent identifiers, Rules, safety levels, completion conditions,
diagnoses, or treatments. Low-confidence, invalid, or unavailable output falls
back to deterministic extraction and presentation. Compiled Rules remain the
only authority for safety and routing.

Clinical adaptive output may project to a session-specific FHIR R4 Questionnaire and QuestionnaireResponse. Clinical structured forms produce a QuestionnaireResponse and may use SDC extraction only when the Questionnaire declares a verified extraction mapping. Non-clinical structured surveys do not extract clinical resources by default.

## Additional screening recommendation

The goal is to compare screening-center add-ons beyond the nationally provided screening baseline. The default entry is a short supplemental adaptive interview. The official NHIS questionnaire is offered only when the user wants it; it is not a mandatory gate.

If supplemental Facts already exist, a versioned mapping may prepopulate an official QuestionnaireResponse. Only exact or equivalent mappings may populate automatically. A compound official item is populated only when every required atomic source Fact is known. Partial and related mappings remain review candidates. The prepopulated response remains `in-progress` until the user reviews it.

The official Questionnaire/QuestionnaireResponse and the supplemental Questionnaire/QuestionnaireResponse remain separate. A FHIR Bundle may reference both. Recommendation output also records the package-catalog and policy versions. Candidate selection is deterministic; the LLM explains the comparison and uncertainty. The lowest-cost suitable option is always shown, duplicated national items are disclosed, and economic capacity is never inferred.

## Current test privacy boundary

The Runtime may hold necessary personal or health information in current-process memory to ask and answer relevant questions. It does not persist those answers to the repository, public Knowledge Action, database, raw logs, or analytics. The opening message and each current answer may be sent to the selected LLM only for bounded RFE interpretation or current-turn semantic extraction. Historical answer values are not included in planning payloads. External providers require explicit consent; the anonymous demo is restricted to the platform-local provider. Previewed FHIR resources and temporary uploads are discarded when the session closes or expires. ChatGPT or another model provider may have a separate retention policy outside this repository, so the existing public-test notice remains required.

## Implementation boundary

`runtime/service_modes.py` resolves explicit and conservatively inferred purpose and exposes the allowlisted RFE catalog. `services/interview_api/llm.py` implements bounded RFE interpretation, current-turn multi-Fact extraction, eligible-candidate question planning, and optional presentation. `runtime/question_presentation.py` owns concise stems and response shortcuts; `runtime/question_planning.py` owns the Chatbot-test order and soft budget. `runtime/core.py` validates the proposed RFE and hands clinical input to `InterviewSession`; `runtime/session.py` retains authority over eligible Facts, validation, safety, missingness and deterministic fallback. `runtime/questionnaire_prepopulation.py` provides a source-immutable, review-required FHIR R4 prepopulation primitive. `preventive/package_recommendation.py` compares a supplied, versioned center catalog and cannot invent a recommendation when that catalog is absent.

API `mode_selection` is control-plane input and never consumes an interview
turn or becomes patient evidence. Only `initial_message` and later message
payloads may enter the clinical adapter.

The official 2026 NHIS Questionnaire resource and its linkId mapping are not asserted by this overlay until the official source is converted and verified. The prepopulation primitive is regression-tested with synthetic resources in the meantime.
