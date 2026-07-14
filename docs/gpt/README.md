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
- `openapi.yaml`: Custom GPT Action definition
- `GPT_INSTRUCTIONS.md`: instructions to paste into GPT Builder
- `privacy-policy.html`: public privacy notice required for a shared GPT Action

Run `python3 tools/gpt_export/build.py` after changing Knowledge or Facts. The generated resources are deterministic and contain no simulation or response data.

The GPT must start from Reason for Encounter, then load only the matching compact RFE resources. The large aggregate files remain available for offline inspection and backward compatibility but are intentionally absent from the Action schema.

Manifest policy also distinguishes institutional result checking from an interpretation request, and carries recency rules for longitudinal conditions, medications, family history, alcohol, and smoking review.
