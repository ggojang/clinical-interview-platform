# Reasoning Loop Specification

For every patient utterance, runtime performs:

1. `observe` — capture utterance and metadata;
2. `extract` — create fact candidates;
3. `normalize` — map only supported values;
4. `merge` — update Clinical Memory;
5. `validate` — detect conflicts and invalid states;
6. `activate` — update interview patterns;
7. `identify_gaps` — compare memory with active pattern needs;
8. `check_safety` — evaluate reviewed red-flag rules;
9. `generate` — produce question candidates;
10. `prioritize` — score candidates;
11. `ask` — select one primary question;
12. `trace` — persist the decision inputs and output.

## Determinism boundary

The model may propose facts and question wording. The repository must define:

- allowed fact identifiers;
- pattern requirements;
- safety precedence;
- scoring features;
- validation constraints.

## Stop conditions

The loop may stop when:

- an urgent escalation state requires transition;
- all required facts are known or explicitly unresolved;
- the patient declines;
- maximum-turn policy is reached;
- a human takes over.

A stop reason must be recorded.

When required Facts are explicitly unresolved, Runtime records
`required_targets_addressed_with_absent_data` rather than claiming that all
Targets were resolved. Each unresolved Fact retains a coded `dataAbsentReason`.
