# Custom GPT Test Interface

This directory is a static, read-only knowledge API for a Custom GPT test chatbot. It deliberately omits FHIR persistence and all patient responses.

## Resources

- `manifest.json`: version, counts, and SHA-256 digests
- `reason-for-encounters.json`: Korean/English Reason for Encounter catalog, aliases, and implementation status
- `common-facts.json`: compact shared interview Facts, including structured additional-comment handling
- `rfe/{abdominal_pain|back_pain|bowel_symptoms|chest_pain|cough|dizziness_syncope|dyspnea|fatigue|fever|headache|medication_review|palpitations|skin_complaint|upper_respiratory_symptoms|urinary_symptoms|vomiting_diarrhea}/facts.json`: compact Facts for one implemented Reason for Encounter
- `rfe/{abdominal_pain|back_pain|bowel_symptoms|chest_pain|cough|dizziness_syncope|dyspnea|fatigue|fever|headache|medication_review|palpitations|skin_complaint|upper_respiratory_symptoms|urinary_symptoms|vomiting_diarrhea}/questions.json`: compact Questions for one implemented Reason for Encounter
- `rfe/{abdominal_pain|back_pain|bowel_symptoms|chest_pain|cough|dizziness_syncope|dyspnea|fatigue|fever|headache|medication_review|palpitations|skin_complaint|upper_respiratory_symptoms|urinary_symptoms|vomiting_diarrhea}/rules.json`: compact safety and routing rules for one implemented Reason for Encounter
- `facts.json`: reusable Fact definitions
- `question-groups.json`: compact common QuestionGroup index; complete QuestionTemplates are provided in each RFE question resource
- `safety-rules.json`: compact cross-RFE safety rules; complete routing and priority rules are provided in each `rfe/{slug}/rules.json`
- `screening-kr.json`: Korean national screening candidate rules
- `terminology-source.json`: STOM identity, observed versions, cadence, and limitations
- `openapi.yaml`: compiled Knowledge Custom GPT Action definition
- `stom-openapi.yaml`: separate read-only STOM terminology Action definition
- `GPT_INSTRUCTIONS.md`: instructions to paste into GPT Builder
- `privacy-policy.html`: public privacy notice required for a shared GPT Action

Run `python3 tools/gpt_export/build.py` after changing Knowledge or Facts. The generated resources are deterministic and contain no simulation or response data.

The GPT must start from Reason for Encounter, then load only the matching compact RFE resources. The large aggregate files remain available for offline inspection and backward compatibility but are intentionally absent from the Action schema.

Manifest policy also distinguishes institutional result checking from an interpretation request, and carries recency rules for all longitudinal baseline groups.

The common Fact resource and manifest jointly expose the first-encounter baseline: diagnoses, procedures, medication, allergies, family history, occupation, smoking, and alcohol, together with first-use and per-group last-confirmed state. A confirmed first encounter cannot complete until every due group has an explicit answer, current reusable value, unknown state, or refusal.

The STOM Action is intentionally separate from the compiled Knowledge Action. It accepts only a short de-identified normalized term or terminology code and provides provisional SNOMED CT, LOINC, KCD-8, HIRA, and FHIR lookup results. It must never receive raw patient answers or control clinical rules.

Verify the approved live read operations with synthetic normalized terms:

```bash
python3 tools/terminology/probe_stom.py
```
