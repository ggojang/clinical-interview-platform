# AI Agent Operating Manual

This repository is designed to be edited by AI agents under explicit contracts.

## Required read order

Before changing any file, read:

1. `FOUNDATION.md`
2. `PROJECT_CONTEXT.md`
3. the relevant files in `docs/context/`
4. `MISSION.md`
5. `AI.md`
6. `specifications/README.md`
7. the relevant specification files
8. the relevant schemas
9. related knowledge, simulations, evaluation, and tests

## Source-of-truth hierarchy

`FOUNDATION > PROJECT_CONTEXT > context documents > specifications > schemas > reviewed knowledge > generated knowledge > compiled packages > runtime > examples/playground`

When implementation conflicts with a specification, change the implementation or propose a specification change. Do not silently reinterpret the specification.

## Edit boundaries

AI agents may create or modify:

- `knowledge/generated/`
- `simulation/`
- `playground/`
- `runtime/`
- `compiler/`
- `rules/`
- `sources/`
- `evaluation/`
- `coverage/`
- `packages/generated/`
- `tools/`
- `tests/`
- documentation through an explicit change

AI agents must not promote content into `knowledge/reviewed/` without recorded human review.

## Required workflow for a new Fact

1. Define the semantic need.
2. Add or reuse a schema-compliant fact item.
3. Include extraction cues, neutral question forms, applicability, and provenance.
4. Reference it from at least one pattern or explain why it is standalone.
5. Add validation and at least one simulation or regression fixture.
6. Run `python tools/validator/validate.py`.

## Required workflow for a new Pattern

1. State its clinical interview purpose, not a diagnosis claim.
2. Declare entry cues and required/optional facts.
3. Declare safety rules and stop conditions.
4. Ensure all fact references exist.
5. Add simulations with expected and forbidden behavior.
6. Run validation.

## Medical safety constraints

- Never convert an unsupported possibility into a confirmed fact.
- Never infer absence from silence.
- Never assert a diagnosis merely because a pattern is active.
- Ask safety-critical questions before routine completeness questions.
- Preserve patient wording when normalization is uncertain.
- Mark model-generated knowledge as unreviewed.
- Escalation language must be reviewed before production use.

## Naming conventions

- Stable identifiers use lowercase dotted namespaces: `symptom.duration`
- Filenames use lowercase kebab case: `symptom-duration.yaml`
- Patterns use domain prefixes: `respiratory.cough`
- Simulation IDs use uppercase category plus number: `COUGH-001`

## Expected change report

Every meaningful AI change should report:

- files created or changed;
- assumptions;
- validation performed;
- known gaps;
- whether medical review is required.
