# Custom GPT Test Interface

This directory is a static, read-only knowledge API for a Custom GPT test chatbot. It deliberately omits FHIR persistence and all patient responses.

## Resources

- `manifest.json`: version, counts, and SHA-256 digests
- `facts.json`: reusable Fact definitions
- `question-groups.json`: question templates and screening groups
- `safety-rules.json`: deterministic safety and routing rules
- `screening-kr.json`: Korean national screening candidate rules
- `openapi.yaml`: Custom GPT Action definition
- `GPT_INSTRUCTIONS.md`: instructions to paste into GPT Builder
- `privacy-policy.html`: public privacy notice required for a shared GPT Action

Run `python3 tools/gpt_export/build.py` after changing Knowledge or Facts. The generated resources are deterministic and contain no simulation or response data.
