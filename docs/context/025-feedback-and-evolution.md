# Feedback and Knowledge Evolution

Version: 0.1 (Draft)

---

# Purpose

This document defines how Runtime experience returns to the Knowledge Factory.

Feedback informs Build-Time work.

Feedback never changes active Runtime knowledge directly.

---

# Core Loop

```text
Knowledge Acquisition
        ↓
Knowledge Graph
        ↓
Knowledge Package
        ↓
Runtime
        ↓
De-identified Feedback
        ↓
Evaluation
        ↓
Knowledge Acquisition
```

---

# Core Principle

Runtime never learns.

The Knowledge Factory learns.

---

# Feedback Types

Feedback may include

- unresolved Interview Target
- repeated Question
- misunderstood wording
- missing Fact candidate
- unexpected conflict
- safety near miss
- false escalation
- mapping failure
- unsupported Reason for Encounter
- unsupported language
- patient burden signal
- clinician review
- Runtime error
- Coverage gap

---

# Feedback Event

Every feedback event contains

- identifier
- type
- Runtime version
- package version
- Encounter Context
- affected object identifiers
- de-identified evidence
- severity
- reporter
- timestamp
- provenance
- review state

---

# Privacy Boundary

Feedback entering the Knowledge Factory must be

- de-identified
- synthetic
- explicitly consented
- or governed by an approved data process

Patient-identifiable data never enters ordinary Knowledge Acquisition.

Secrets and direct identifiers are prohibited.

---

# Triage

Feedback is classified as

- safety critical
- correctness
- semantic gap
- usability
- efficiency
- interoperability
- implementation defect
- evaluation defect
- out of scope

Safety-critical feedback receives immediate governance review.

---

# Feedback is not Knowledge

A feedback event is evidence of a possible gap.

It does not automatically create

- Fact
- Rule
- Question
- Intent
- Target
- mapping
- guideline interpretation

The Builder process must validate and transform it.

---

# Evolution Workflow

1. Receive feedback.
2. Validate provenance and privacy.
3. Classify the issue.
4. Reproduce with Simulation.
5. Identify responsible knowledge layer.
6. Acquire supporting source evidence.
7. update or create graph knowledge.
8. add regression Simulation.
9. evaluate affected scope.
10. compile a new package.
11. perform review.
12. release through governance.

---

# Regression First

Every confirmed defect creates a failing Simulation before the fix.

The fix is complete only when

- the new case passes
- affected existing cases pass
- Coverage is recomputed
- provenance is complete
- review gates pass

---

# No Live Mutation

Feedback must never

- change an active package
- change priority weights during a session
- create a local medical exception
- promote model output to reviewed knowledge
- bypass Compilation
- bypass Simulation

---

# Knowledge Deprecation

Knowledge may become

- superseded
- deprecated
- rejected
- withdrawn
- jurisdiction-limited

Deprecation preserves

- previous version
- reason
- effective date
- replacement
- affected packages
- provenance

---

# Guideline Change

A guideline change triggers

- new source acquisition
- baseline comparison
- impact analysis
- graph revision
- rule revision where needed
- simulation update
- regression evaluation
- package release

Runtime never reads the new guideline directly.

---

# Terminology Change

Terminology updates trigger

- new baseline
- mapping validation
- identifier impact analysis
- graph alignment
- package rebuild
- regression tests

Stable internal identifiers should remain stable when semantics do not change.

---

# Metrics

Evolution metrics include

- feedback-to-triage time
- safety remediation time
- reproduced feedback rate
- regression case creation
- knowledge reuse
- package adoption
- repeated defect rate
- Coverage improvement

---

# Final Principle

Feedback is routed back to the Knowledge Factory.

Only reviewed, simulated and compiled knowledge returns to Runtime.
