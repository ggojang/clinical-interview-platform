# Custom GPT Test Interface

This directory is a static, read-only knowledge API for a Custom GPT test chatbot. It deliberately omits FHIR persistence and all patient responses.

## Resources

- `manifest.json`: version, counts, and SHA-256 digests
- `reason-for-encounters.json`: Korean/English Reason for Encounter catalog, aliases, and implementation status
- `common-facts.json`: compact shared interview Facts, including structured additional-comment handling
- `rfe/{cough|dyspnea|fever}/facts.json`: compact Facts for one implemented Reason for Encounter
- `rfe/{cough|dyspnea|fever}/questions.json`: compact Questions for one implemented Reason for Encounter
- `rfe/{cough|dyspnea|fever}/rules.json`: compact safety and routing rules for one implemented Reason for Encounter
- `facts.json`: reusable Fact definitions
- `question-groups.json`: question templates and screening groups
- `safety-rules.json`: deterministic safety and routing rules
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
