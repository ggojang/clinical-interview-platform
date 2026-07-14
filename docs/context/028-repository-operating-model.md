# Repository Operating Model

Version: 0.1 (Draft)

---

# Purpose

This document defines how humans and AI agents work in the repository.

The repository is AI-first and specification-first.

Knowledge is the product.

---

# Required Reading Order

Before changing repository knowledge, read

1. FOUNDATION
2. PROJECT_CONTEXT
3. relevant Context documents
4. relevant specifications
5. relevant schemas
6. relevant graph objects
7. related simulations
8. related tests
9. Runtime implementation last

---

# Authority

Authority order

```text
FOUNDATION
    ↓
Context Documents
    ↓
Specifications
    ↓
Schemas
    ↓
Reviewed Knowledge
    ↓
Generated Knowledge
    ↓
Compiled Artifacts
    ↓
Runtime
    ↓
Examples
```

A lower layer never silently overrides a higher layer.

---

# Repository Responsibilities

Suggested top-level structure

```text
docs/context/          architectural concepts
specifications/        behavioral contracts
schemas/               structural contracts
sources/               source manifests and cached metadata
knowledge/             graph knowledge
rules/                 rule definitions
simulation/            executable cases
evaluation/            datasets and reports
coverage/              coverage definitions and reports
mappings/              terminology and FHIR mappings
compiler/              compilation
packages/              generated immutable packages
runtime/               package executor
tools/                 validation and build tooling
tests/                 implementation tests
decisions/             ADRs
```

Generated artifacts should be distinguishable from authored source.

---

# Change Workflow

1. Identify affected semantic object.
2. Read authoritative documents.
3. acquire or cite source evidence.
4. reuse existing objects.
5. change knowledge at the correct layer.
6. preserve provenance.
7. add or update Simulation.
8. run validation.
9. run Evaluation.
10. recompute Coverage.
11. compile package when required.
12. report assumptions and gaps.

---

# Reuse First

Before creating a Fact, Target, Intent, Question or Rule

- search by identifier
- search by meaning
- inspect mappings
- inspect graph relationships
- inspect deprecated successors

Duplicate semantic objects are prohibited.

---

# AI Agent Rules

AI agents

- follow FOUNDATION
- preserve provenance
- default generated content to unreviewed
- do not promote content to reviewed
- do not invent source citations
- do not reinterpret safety rules silently
- do not place medical knowledge in Runtime
- add Simulation for behavior changes
- report known uncertainty

---

# Human Review

Humans retain authority for

- clinical review
- safety enablement
- architecture principle changes
- jurisdiction decisions
- release approval
- review promotion

Automation may assist but cannot falsify review identity.

---

# Validation Commands

The repository should expose stable commands for

- schema validation
- graph validation
- rule validation
- provenance validation
- simulation
- evaluation
- Coverage calculation
- compilation
- package integrity
- Runtime compatibility

Command names may vary.

Required gates do not.

---

# Dirty Worktree

Existing unrelated changes are preserved.

Automation modifies only files within task scope.

Destructive replacement requires explicit intent.

---

# Change Report

Every meaningful change reports

- files changed
- objects changed
- source evidence
- assumptions
- validation performed
- Simulation performed
- Coverage impact
- known gaps
- review required

---

# Final Principle

Repository operations exist to evolve trustworthy knowledge.

Implementation convenience never overrides semantic and safety contracts.
