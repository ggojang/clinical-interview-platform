# Knowledge Builder

The Builder merges `knowledge/base/` with versioned fragments under
`knowledge/generated/` and writes canonical Knowledge and Rule Graphs.

```bash
python3 builder/build_knowledge.py --profile cough --report builder/latest-report.json
python3 builder/build_knowledge.py --profile fever --report builder/latest-fever-report.json
python3 builder/build_knowledge.py --profile dyspnea --report builder/latest-dyspnea-report.json
```

Generated fragments must remain `unreviewed/research_only` and may declare only
`research_test` and `simulation` usage modes.

Profiles compile independently. Shared Fact identity is resolved through
`knowledge/shared/primary-care-facts.json`; a new Reason for Encounter must not
be merged into an unrelated canonical graph.
