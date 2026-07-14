# Governance and Review

Version: 0.1 (Draft)

---

# Purpose

This document defines governance and review.

Governance controls how knowledge moves from generated or acquired material into released packages.

---

# Core Principle

No object becomes trusted because it exists.

Trust is an explicit, provenance-backed review state.

---

# Review States

Supported states

- unreviewed
- in_review
- reviewed
- rejected
- deprecated

State transitions are recorded.

AI-generated content defaults to unreviewed.

---

# Review Domains

Separate review may be required for

- clinical meaning
- safety behavior
- question wording
- terminology mapping
- FHIR mapping
- licensing
- privacy
- security
- jurisdiction
- accessibility
- simulation expectations

One approval does not imply all domains are approved.

---

# Reviewer Roles

Roles may include

- clinical reviewer
- terminology reviewer
- interoperability reviewer
- safety reviewer
- privacy reviewer
- security reviewer
- language reviewer
- repository maintainer
- release authority

Reviewer identity and scope are provenance.

---

# Conflict of Review

Generated content should not be approved solely by the same automated agent that created it.

Safety-critical knowledge requires qualified human review.

Reviewer independence requirements are package policy.

---

# Review Object

Every review records

- review identifier
- object identifier and version
- review domain
- reviewer
- decision
- rationale
- evidence
- conditions
- timestamp
- expiration
- provenance

---

# Safety Governance

Production safety knowledge requires

- clinical validation
- escalation wording review
- jurisdiction applicability
- positive and negative Simulation
- ambiguous case Simulation
- Runtime capability validation
- release approval

Unreviewed safety rules remain research-only.

---

# Change Classification

Changes are classified as

- editorial
- semantic
- behavioral
- safety-critical
- interoperability
- breaking
- deprecation
- security
- privacy

Classification determines required reviewers and regression scope.

---

# Architecture Decision Record

Changing an immutable FOUNDATION principle requires an ADR.

The ADR contains

- decision
- context
- alternatives
- consequences
- migration
- affected packages
- reviewer approval
- effective version

No lower-level document may silently override FOUNDATION.

---

# Promotion

Promotion into reviewed knowledge requires

1. valid schema
2. complete provenance
3. source evidence
4. semantic validation
5. required Simulation
6. passing Evaluation
7. required reviewer decisions
8. Coverage update
9. version update

---

# Rejection

Rejected knowledge remains traceable.

Rejection records

- reason
- reviewer
- evidence
- date
- replacement when applicable

Rejected objects are excluded from release packages.

---

# Deprecation

Deprecation does not delete history.

A deprecated object records

- effective date
- reason
- successor
- affected references
- migration
- package impact

---

# Release Authority

Release authority verifies

- package manifest
- integrity
- review state
- Simulation report
- Evaluation report
- Coverage report
- known limitations
- compatibility
- rollback package

Release approval is immutable provenance.

---

# Audit

Governance must answer

- who created the knowledge
- which source supported it
- who reviewed it
- which simulations passed
- which package included it
- which Runtime executed it
- why it changed
- what replaced it

---

# Final Principle

Governance makes trust explicit.

Review, evidence, Simulation and provenance determine what may be released.
