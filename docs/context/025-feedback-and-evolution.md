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

This boundary does not prohibit a later Build-Time service upgrade.

---

# AI-Managed Research Service Upgrade

Resolution is not limited to answering the reporter.

When de-identified feedback exposes a reproducible defect or reusable gap, the AI Knowledge Factory should improve the service when it can do so safely and within scope.

An upgrade may change

- Question wording
- interview routing
- Fact definitions
- Knowledge Graph content
- Rule Graph content
- safety behavior
- reporting
- tests and Simulations
- the read-only GPT Knowledge API
- Custom GPT instructions or configuration

The automated research path is

```text
Additional Comment or Feedback
        ↓
Privacy-safe Generalization
        ↓
Reproduction Test
        ↓
Build-Time Change
        ↓
Regression + Privacy + Validation Gates
        ↓
New research_only/unreviewed Version
        ↓
Research Test Deployment
        ↓
Applied Upgrade Report
```

Human participation is optional for this research-only path.

Human review remains required before promotion to reviewed or Production knowledge.

The AI must report only the result for successfully applied upgrades. If it cannot upgrade because of missing evidence, unsafe ambiguity, external authority, licensing, permissions or a required clinical decision, it reports the unresolved item, reason and required human action.

Raw patient responses and direct identifiers never enter the repository. Regression fixtures derived from feedback must be synthetic and generalized.

---

# Consented Research Test Metrics

The public Custom GPT may optionally use a separate write-only feedback service after an interview has reached an explicit end state.

The service may receive only a fixed structured minimum dataset after the user gives separate current-session consent. Completion confirmation is not feedback consent.

Allowed fields include package and GPT configuration versions, up to three Reason for Encounter identifiers, flow and completion status, safety level, bounded event counts, terminology and Knowledge-load status, fixed issue tags, and an optional one-to-five rating.

The service must reject free text, answers, transcripts, files, demographics, contact data, direct identifiers, unexpected fields, and a request without current consent. It must use separate write and administrator credentials, bounded retention, server timestamps, idempotency, no request-body logging, and aggregate-only administrator reporting.

An explicitly declined submission causes no loss of interview function. Sessions closed before the end-of-session choice are not tracked, and the service must disclose that its completion statistics therefore exclude abandoned sessions.

Collected metrics remain feedback evidence. They never mutate active Runtime knowledge and never become Knowledge without privacy-safe generalization, reproduction, source review, Simulation, Evaluation and Compilation.

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

Only validated, simulated and compiled knowledge returns to Runtime.

Research Runtime may receive a new `unreviewed/research_only` package after automated gates pass.

Production Runtime may receive only appropriately reviewed knowledge.
