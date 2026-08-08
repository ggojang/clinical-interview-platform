# Knowledge Builder

The Builder merges `knowledge/base/` with versioned fragments under
`knowledge/generated/` and writes canonical Knowledge and Rule Graphs.

```bash
python3 builder/build_knowledge.py --profile cough --report builder/latest-report.json
python3 builder/build_knowledge.py --profile fever --report builder/latest-fever-report.json
python3 builder/build_knowledge.py --profile dyspnea --report builder/latest-dyspnea-report.json
```

Generated fragments remain `draft/unreviewed/limited`. The legacy
`research_only` field is retained for schema compatibility. Fragments may
declare `research_test`, `simulation`, and `clinician_supervised_pilot` usage
modes, but never gain independent diagnosis or treatment authority.

Profiles compile independently. Shared Fact identity is resolved through
`knowledge/shared/primary-care-facts.json`; a new Reason for Encounter must not
be merged into an unrelated canonical graph.
