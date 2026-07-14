# Roadmap and Definition of Done

Version: 0.1 (Draft)

---

# Purpose

This document defines development order and completion gates.

The repository grows through Primary Care Coverage.

It does not grow through file count.

---

# Phase 0 — Architecture

Deliverables

- FOUNDATION
- Context model
- graph model
- rule model
- provenance model
- package model
- Runtime boundary
- Simulation and Evaluation contracts
- Coverage model

Gate

All immutable principles and layer responsibilities are explicit.

---

# Phase 1 — Bootstrap Vertical Slice

Deliverables

- one Encounter Context
- representative Reasons for Encounter
- reusable Clinical Intents
- reusable Interview Targets
- shared Facts
- reviewed Question Templates
- safety rules
- simulations
- compiled package
- transparent Runtime

Gate

The complete knowledge-to-runtime loop is reproducible and traceable.

---

# Phase 2 — Primary Care Breadth

Deliverables

- respiratory
- cardiovascular
- gastrointestinal
- neurological
- musculoskeletal
- dermatological
- genitourinary
- mental health
- preventive care
- administrative care

Gate

Coverage targets pass across common Primary Care RFEs.

---

# Phase 3 — Evaluation Depth

Deliverables

- positive, negative and ambiguous cases
- contradiction and correction cases
- safety regression suite
- multilingual cases
- patient-burden metrics
- held-out evaluation
- release thresholds

Gate

Safety, correctness, efficiency and traceability thresholds pass.

---

# Phase 4 — Terminology and Interoperability

Deliverables

- terminology baselines
- SNOMED CT alignment
- LOINC alignment
- ICPC-2 indexing
- FHIR mappings
- profile validation
- mapping coverage

Gate

Internal semantics survive export and import projections.

---

# Phase 5 — Governed Pilot

Deliverables

- clinical review workflow
- privacy and security controls
- package signing
- deployment governance
- prospective evaluation
- incident and rollback process
- clinician-facing environment

Gate

Governance authority approves a bounded pilot scope.

---

# Knowledge Object Definition of Done

A knowledge object is complete when

- identifier is stable
- semantic meaning is explicit
- no duplicate exists
- graph relationships resolve
- provenance is complete
- review state is correct
- required Simulation passes
- Coverage is updated
- package compilation succeeds

---

# Behavior Definition of Done

A behavior is complete when

- governing rule is explicit
- priority is traceable
- safety effect is known
- positive test passes
- negative test passes
- ambiguity test passes
- regression test passes
- failure behavior is defined
- Runtime trace is reconstructable

---

# Release Definition of Done

A release is complete when

- manifest is complete
- all required validations pass
- required Simulations pass
- Evaluation gates pass
- Coverage report is generated
- review approvals exist
- integrity is verified
- compatibility is tested
- rollback exists
- known limitations are published
- provenance is complete

---

# Non-Completion

The following do not mean complete

- a Markdown file exists
- a schema accepts the object
- a demo looks plausible
- an LLM produced an answer
- a Fact count increased
- a package built without Simulation
- a reviewer gave undocumented verbal approval

---

# Priority Order

Development priority considers

1. safety gaps
2. common Primary Care RFEs
3. highly reusable Facts and Targets
4. missing Simulation
5. missing provenance
6. interoperability gaps
7. efficiency improvement
8. specialized depth

---

# Final Principle

A phase advances only when its acceptance gates pass.

Coverage and evidence determine progress.
