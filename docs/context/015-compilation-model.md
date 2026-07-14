# Compilation Model

Version: 0.1 (Draft)

---

# Purpose

This document defines Compilation.

Compilation transforms reviewed repository knowledge into an immutable Knowledge Package that Runtime can execute.

Compilation does not discover medical knowledge.

Compilation does not reinterpret guidelines.

Compilation does not create new Facts, Clinical Intents or Interview Targets.

---

# Position in the Pipeline

```text
Knowledge Graph
        ↓
Rule Graph
        ↓
Simulation
        ↓
Validation
        ↓
Compiler
        ↓
Knowledge Package
        ↓
Runtime
```

Compilation is the final Build-Time boundary.

---

# Core Principle

Compile once.

Execute many.

The Compiler may optimize representation.

It must never change semantics.

---

# Compiler Inputs

The Compiler accepts only versioned inputs.

- Knowledge Graph
- Rule Graph
- Question Templates
- Mapping Graph
- Simulation Package
- Coverage Definition
- Terminology Baseline
- Guideline Baseline
- Package Configuration
- Provenance Graph

Unversioned input is rejected.

---

# Compiler Outputs

The Compiler produces

- immutable Knowledge Package
- Runtime indexes
- Intent activation table
- Interview Target dependency table
- Fact definition table
- Question selection table
- Rule execution plan
- safety escalation table
- mapping package
- package manifest
- validation report
- coverage report
- simulation report
- integrity digest

No patient or session state exists in Compiler output.

---

# Compilation Stages

1. Load all declared inputs.
2. Validate identifiers and versions.
3. Validate graph constraints.
4. Resolve all references.
5. Detect duplicate semantic objects.
6. Validate rule dependencies.
7. Detect prohibited cycles.
8. Verify provenance.
9. Verify review status.
10. Verify safety enablement.
11. Build deterministic Runtime indexes.
12. Execute required Simulations.
13. Compute Coverage.
14. Serialize package artifacts.
15. Generate integrity digests.
16. emit the Package Manifest.

Every stage is deterministic.

---

# Semantic Preservation

The Compiler may

- sort identifiers
- construct indexes
- remove unreachable compiled records
- precompute dependency traversal
- precompute priority components
- compress repeated structures
- serialize graph projections

The Compiler may not

- merge semantically different Facts
- invent missing provenance
- convert a Hypothesis into a diagnosis
- create a Question without an Interview Target
- enable an unreviewed safety rule
- change a guideline interpretation
- infer a negative Fact from missing knowledge

---

# Reference Resolution

Every compiled reference must resolve.

Examples

Clinical Intent → Interview Target

Interview Target → Fact

Question Template → Fact

Rule → Graph Object

Simulation → Expected Object

Fact → Mapping

Missing references cause compilation failure.

Fallback identifiers are prohibited.

---

# Dependency Graph

The Compiler builds a directed dependency graph.

Typical dependency

```text
Encounter Context
        ↓
Clinical Intent
        ↓
Interview Target
        ↓
Fact
        ↓
Question Template
```

Safety dependencies may interrupt routine traversal.

Circular dependencies are rejected unless an explicit bounded fixed-point policy exists.

The default policy rejects all cycles.

---

# Determinism

Given identical

- source manifests
- Knowledge Graph version
- Rule Graph version
- compiler version
- package configuration
- terminology baseline
- guideline baseline

the Compiler must produce semantically identical output.

Build timestamps and signatures may differ.

The semantic digest must not.

---

# Reproducibility

A package must be reproducible without live network access.

All external sources must already exist in the validated Source Cache.

Compilation never calls

- STOM
- SNOMED services
- FHIR terminology servers
- guideline websites
- search engines
- model providers

---

# Validation Gates

Compilation fails when

- a required object lacks provenance
- a reference is unresolved
- a duplicate identifier exists
- graph constraints fail
- a required simulation fails
- safety knowledge lacks the required review state
- package scope and Coverage disagree
- Runtime compatibility is unknown
- integrity generation fails

A failed build never produces a releasable package.

---

# Runtime Compatibility

Every package declares

- minimum Runtime version
- maximum tested Runtime version
- supported rule language version
- supported memory schema version
- supported mapping versions
- required capabilities

Runtime rejects an incompatible package before an interview starts.

---

# Incremental Compilation

Incremental compilation may rebuild only affected graph regions.

However

- dependency impact must be computed
- all affected simulations must rerun
- Coverage must be recomputed
- the package receives a new version
- unchanged objects preserve identity and provenance

Incremental compilation must produce the same result as a clean full build.

---

# Package Integrity

Every compiled artifact has a digest.

The Package Manifest includes

- artifact path
- artifact type
- content digest
- semantic version
- provenance identifier
- dependency identifiers

Runtime verifies integrity before loading.

---

# Compiler Provenance

Every compilation records

- compiler identity
- compiler version
- repository revision
- input versions
- configuration digest
- start and completion time
- validation result
- simulation result
- output digest

Compilation lineage must be reconstructable.

---

# Repository Rules

Compilation

- occurs only at Build Time
- consumes only versioned inputs
- is deterministic
- is offline-capable
- preserves semantics
- runs mandatory Simulation
- computes Coverage
- emits an immutable package
- records complete provenance

---

# Final Principle

The Compiler is a semantic-preserving boundary.

It converts reviewed graph knowledge into a Runtime-executable package without adding medical meaning.
