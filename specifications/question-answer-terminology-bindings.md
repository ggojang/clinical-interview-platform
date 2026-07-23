# Question and Answer Terminology Bindings

Version: 0.1 (Draft)

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

A question that requests multiple observations in one sentence cannot inherit
one atomic LOINC code as an exact mapping. It keeps its local code until it is
split into atomic items or a matching standard item is verified. A partial
mapping may be recorded for search and gap analysis.

## Answers

Clinical choice answers use a verified SNOMED CT concept when possible. Every
remaining coded choice receives a context-qualified local answer code.

Boolean, numeric, quantity, date, date-time, and narrative answers are values,
not answer concepts. They use the matching FHIR R4 `value[x]` type. Quantity
units use UCUM when known. Boolean values may carry documented SNOMED semantic
equivalents, but a FHIR boolean Questionnaire item is answered with
`valueBoolean`.

Unknown, declined, and similar absence states are not negative clinical answers.
They are preserved as `dataAbsentReason` when applicable.

Official fixed instruments retain their source-defined question and answer
codes and normative answer lists. They are not silently replaced by SNOMED CT
or LOINC codes.

## Build-time boundary

STOM and official terminology services are used only to acquire and verify
mappings. Compiled packages contain the mappings needed by Runtime. Terminology
availability never controls safety, question selection, or interview
completion.

## FHIR R4 projection

- Question identity: `Questionnaire.item.linkId`
- Question codings: `Questionnaire.item.code`
- Coded option: `Questionnaire.item.answerOption.valueCoding`
- Coded response: `QuestionnaireResponse.item.answer.valueCoding`
- Literal response: the matching `QuestionnaireResponse.item.answer.value[x]`
- Questionnaire/response linkage: matching `linkId`

The local coding is retained with verified standard codings so round-trip
projection does not lose repository identity.
