# Sources

## Questionnaire and interview rights inventory

Questionnaire, assessment and dynamic-interview assets are inventoried separately
from ordinary clinical evidence sources. The inventory distinguishes project-authored
dynamic questions, source-defined fixed questionnaires, result-capture-only assessment
programs and future instrument candidates. It does not treat public metadata access or
an internal test as permission to reproduce, translate, electronically administer or
commercially distribute an instrument.

```bash
python3 tools/inventory/build_questionnaire_source_rights_inventory.py
python3 tools/inventory/build_questionnaire_source_rights_inventory.py --check
```

The machine-readable report is written to
`coverage/questionnaire-source-rights-inventory-latest.json`; the human review is
written to `docs/QUESTIONNAIRE_INTERVIEW_SOURCE_RIGHTS_INVENTORY.md`. External
instrument candidates and their fail-closed acquisition gates are maintained in
`sources/inventory/questionnaire-instrument-candidates.json`. The ordered domestic
source review (CHS → KHP → KLoSA), concept-level gaps, and item-reuse boundaries are
documented in `docs/KOREAN_QUESTIONNAIRE_SOURCE_ACQUISITION.md`.

Build-Time Source Manifests live in `manifests/`.

Build-Time terminology reference indexes live in `catalogs/`. The complete
LOINC LL Answer List catalog preserves official canonicals and observed member
counts from STOM without duplicating those reference ValueSets on the server.
It is regenerated and audited with:

```bash
python3 tools/terminology/build_loinc_answer_list_catalog.py
python3 tools/validator/audit_loinc_answer_lists.py
```

A manifest records identity, version, path, digest, completeness, licensing status,
limitations, and provenance. Runtime never reads external sources or this directory
during an interview.

The cough, fever, and dyspnea manifests are research-only. External guideline artifacts
are not yet cached or license-verified.

Report monitoring work due under the refresh policy:

```bash
python3 sources/check_refresh.py --as-of 2026-07-20
python3 sources/check_refresh.py --manifest sources/manifests/primary-care-fever-research.json
python3 sources/check_refresh.py --manifest sources/manifests/primary-care-dyspnea-research.json
```

With no `--manifest`, the command checks every `*-research.json` manifest. Use
`--manifest` only when intentionally narrowing the report to one profile. The
command schedules checks only. It does not access the network or claim that an
upstream source was reviewed.
