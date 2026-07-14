# Custom GPT Test Interface

This directory is a static, read-only knowledge API for a Custom GPT test chatbot. It deliberately omits FHIR persistence and all patient responses.

## Resources

- `manifest.json`: version, counts, and SHA-256 digests
- `reason-for-encounters.json`: Korean/English Reason for Encounter catalog, aliases, and implementation status
- `common-facts.json`: compact shared interview Facts, including structured additional-comment handling
- `rfe/{slug}/facts.json`: compact Facts for one implemented Reason for Encounter, including grouped eye symptoms
- `rfe/{slug}/questions.json`: compact Questions for one implemented Reason for Encounter
- `rfe/{slug}/rules.json`: compact safety and routing rules for one implemented Reason for Encounter
- `facts.json`: reusable Fact definitions
- `question-groups.json`: compact common QuestionGroup index; complete QuestionTemplates are provided in each RFE question resource
- `safety-rules.json`: compact cross-RFE safety rules; complete routing and priority rules are provided in each `rfe/{slug}/rules.json`
- `screening-kr.json`: Korean national screening candidate rules
- `questionnaires/patient-experience-5th-2025/metadata.json`: activation, section index, answer semantics, and completion policy for the 2025 fifth inpatient patient-experience questionnaire
- `questionnaires/patient-experience-5th-2025/sections/{1..8}.json`: one compact source-preserving Questionnaire section per Action response
- `terminology-source.json`: STOM identity, observed versions, cadence, and limitations
- `openapi.yaml`: compiled Knowledge Custom GPT Action definition
- `stom-openapi.yaml`: separate read-only STOM terminology Action definition
- `GPT_INSTRUCTIONS.md`: instructions to paste into GPT Builder
- `privacy-policy.html`: public privacy notice required for a shared GPT Action

Run `python3 tools/gpt_export/build.py` after changing Knowledge or Facts. The generated resources are deterministic and contain no simulation or response data.

The GPT must start from Reason for Encounter, then load only the matching compact RFE resources. The large aggregate files remain available for offline inspection and backward compatibility but are intentionally absent from the Action schema.

When an exact patient-experience activation alias is entered, the existing opening screen and a concise explanation may be shown, but the GPT's final actionable question before the survey asks only whether the user wants to complete it. An affirmative answer enters the first source item immediately without another explanation or confirmation. The GPT then loads the questionnaire metadata and exactly one of the eight sections at a time. This avoids Action response-size failures while preserving all 26 FHIR-linked source questions.

Manifest policy also distinguishes institutional result checking from an interpretation request, and carries recency rules for all longitudinal baseline groups.

The answer-revision policy supports `수정` throughout collection and before confirmation. It uses nonnumeric `E1`, `E2` edit references, preserves prior evidence and `dataAbsentReason`, and reruns safety, conditional branching, and completion checks after every correction. Same-encounter post-completion corrections are recorded as amendments and require confirmation again.

The answer-understanding policy keeps the current question open when a response appears mistyped, uses an invalid choice, or remains ambiguous. A likely interpretation is proposed for confirmation but is never committed automatically; safety-relevant content is evaluated before the retry.

The common Fact resource and manifest jointly expose the first-encounter baseline: diagnoses, procedures, medication, allergies, family history, occupation, smoking, and alcohol, together with first-use and per-group last-confirmed state. A confirmed first encounter cannot complete until every due group has an explicit answer, current reusable value, unknown state, or refusal.

The STOM Action is intentionally separate from the compiled Knowledge Action. It accepts only a short de-identified normalized term or terminology code and provides provisional SNOMED CT, LOINC, KCD-8, HIRA, and FHIR lookup results. It must never receive raw patient answers or control clinical rules.

For anatomical Finding sites, the STOM Action can check membership in `723264001 |Lateralizable body structure reference set|`. The manifest then governs nested Finding-site/Laterality post-coordination, including separate left and right role groups for bilateral findings.

Korean reimbursement binding is reactive and domain-specific. It runs only for a user-supplied code or catalog/product name, an explicit verification request, or an explicit value extracted from an uploaded document. Diagnoses use KCD-8/9, while procedures, medications, and therapeutic materials use their separate HIRA EDI catalogs. Routine clinical content never triggers proactive claim lookup; every result remains provisional until verified.

When the activated flow can verify both SNOMED CT and KCD/HIRA representations, the bundle preserves both and records their mapping relation. Only verified exact or equivalent meanings are eligible to share one FHIR `CodeableConcept`.

Verify the approved live read operations with synthetic normalized terms:

```bash
python3 tools/terminology/probe_stom.py
```
