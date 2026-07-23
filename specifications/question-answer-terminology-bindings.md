# Question and Answer Terminology Bindings

Version: 0.2 (Draft)

Status: `research_only`

Review status: `unreviewed`

## Binding order

Every dynamic question has a stable local code. A verified LOINC code is the
preferred external question code. A verified SNOMED CT observable or related
clinical concept is secondary. The local question code remains present for
round-trip identity even when a standard code exists.

```text
Question: LOINC -> SNOMED CT -> local question code
Coded answer: SNOMED CT -> local answer code
Literal answer: FHIR primitive + UCUM where applicable
```

The order is a mapping preference, not permission to guess a code. Exact or
equivalent mappings require terminology lookup, version, provenance, confidence,
and review status. Broader, narrower, partial, or related mappings remain
mapping metadata and are not represented as equivalent
`Questionnaire.item.code` codings.

## Composite questions

A standard-mapped question collects exactly one answer-bearing clinical data
element. A question that requests multiple observations in one sentence cannot
inherit one atomic LOINC code as an exact mapping. It keeps its local code and
enters the atomic refactoring queue until it is split into separate items. A
partial mapping may be recorded for search and gap analysis, but is never
projected as an equivalent `Questionnaire.item.code`.

Every terminology audit re-runs the atomicity gate. The audit intentionally
tests atomic, composite, fixed-instrument, standard-answer, mixed-answer,
local-answer and absent-answer cases in the same way that clinical simulation
tests Runtime behavior.

## Answers

Clinical choice answers use a verified SNOMED CT concept when possible. Every
remaining coded choice receives a context-qualified local answer code.

Numeric, quantity, date, date-time, and narrative answers use the matching FHIR
R4 `value[x]` type. Quantity units use UCUM when known. The interoperability
projection represents clinical yes/no as a coded `choice` using
`a-sct-yes-no`; `valueBoolean` remains available only when a receiving profile
explicitly requires a primitive boolean.

Every coded dynamic answer set has a FHIR R4 `ValueSet`:

- `a-sct-{semantic-name}` contains only verified SNOMED CT concepts.
- `a-loinc-{LL-code-or-semantic-name}` preserves an official LOINC answer list.
- `a-local-{fact-name}` contains only local fallback codes.
- `a-mixed-{fact-name}` uses SNOMED CT where verified and local codes for the
  remaining choices.

Every coded Fact has a complete local companion ValueSet. A fully mapped set
uses an `a-sct-*` ValueSet as the preferred `answerValueSet`; a partially mapped
set uses a complete `a-mixed-*` ValueSet; an unmapped set uses `a-local-*`.
FHIR ids are limited to 64 characters. Long semantic names are truncated and
receive a stable SHA-256 suffix. Terminology versions belong in resource
metadata, not in the id.

Unknown, declined, and similar absence states are not negative clinical answers.
They are preserved as `dataAbsentReason` when applicable.

Source-defined fixed instruments, including the patient-experience
questionnaire, are excluded from automatic mapping. They retain their official
wording, source-defined question and answer codes, and normative answer lists.
Mapping occurs only after an explicit instruction and verification against the
official instrument or standard artifact.

Before creating a local mapping, Build Time searches official LOINC panels and
answer lists, HL7 FHIR and US Core artifacts, NLM VSAC when licensing and access
allow, SNOMED CT implementation artifacts and STOM.

## Build-time boundary

STOM and official terminology services are used only to acquire and verify
mappings. Compiled packages contain the mappings needed by Runtime. Terminology
availability never controls safety, question selection, or interview
completion.

## FHIR R4 projection

- Question identity: `Questionnaire.item.linkId`
- Question codings: `Questionnaire.item.code`
- Coded option: `Questionnaire.item.answerOption.valueCoding`
- Reusable coded option set: `Questionnaire.item.answerValueSet`
- Coded response: `QuestionnaireResponse.item.answer.valueCoding`
- Literal response: the matching `QuestionnaireResponse.item.answer.value[x]`
- Questionnaire/response linkage: matching `linkId`

The local coding is retained with verified standard codings so round-trip
projection does not lose repository identity.
