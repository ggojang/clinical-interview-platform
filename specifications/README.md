# Specifications

Specifications define behavior and meaning. Schemas define only structure.

A valid JSON or YAML object may still violate a specification. Runtime code, tests, prompts, and knowledge must conform to both.

## Core contracts

- `clinical-memory.md`: state model
- `fact-extraction.md`: evidence and uncertainty rules
- `reasoning-loop.md`: turn-by-turn processing
- `question-generation.md`: candidate and priority rules
- `interview-pattern.md`: reusable interview plans
- `provenance.md`: traceability requirements
- `safety-escalation.md`: urgent-information behavior
- `common-cause-prioritization.md`: safety-gated common-cause ordering

## Change policy

Specification changes are breaking unless demonstrated otherwise. A specification pull request must include affected schemas, tests, knowledge items, and migration notes.
