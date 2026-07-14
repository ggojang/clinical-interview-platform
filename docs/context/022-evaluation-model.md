# Evaluation Model

Version: 0.1 (Draft)

---

# Purpose

This document defines Evaluation.

Evaluation measures whether the Knowledge Factory and Runtime satisfy explicit interview behavior.

Evaluation is evidence.

It is not subjective demo approval.

---

# Evaluation Layers

Evaluation occurs at

- source acquisition
- normalization
- semantic alignment
- graph construction
- rule construction
- Simulation
- compilation
- Runtime execution
- FHIR Export
- release regression

Each layer has separate metrics.

---

# Core Dimensions

Evaluation measures

Safety

Correctness

Traceability

Coverage

Efficiency

Consistency

Interoperability

Patient burden

Robustness

---

# Safety Metrics

Examples

- red-flag recall
- missed escalation rate
- false escalation rate
- escalation latency
- unsafe routine continuation
- unreviewed safety activation
- forbidden advice rate

Safety metrics are reported separately from aggregate scores.

A high aggregate score cannot hide a safety failure.

---

# Fact Metrics

Examples

- supported extraction precision
- supported extraction recall
- negation accuracy
- uncertainty preservation
- normalization accuracy
- conflict detection
- correction handling
- evidence linkage
- hallucinated Fact rate

---

# Intent Metrics

Examples

- activation precision
- activation recall
- priority correctness
- premature closure
- unnecessary activation
- context sensitivity

Intent activation is evaluated independently from diagnosis.

---

# Target Metrics

Examples

- required Target coverage
- Target completion correctness
- duplicate Target rate
- unresolved Target handling
- unnecessary Target rate
- Target-to-Fact integrity

---

# Question Metrics

Examples

- relevance
- neutrality
- atomicity
- readability
- mode compatibility
- repetition
- information gain
- burden
- hidden Hypothesis exposure
- semantic equivalence across languages

---

# Efficiency Metrics

Examples

- turns to required completion
- Questions per resolved Fact
- repeated Question rate
- unnecessary optional Questions
- time to safety action
- target reuse
- branch efficiency

Efficiency never overrides safety.

---

# Traceability Metrics

Examples

- Facts with evidence
- decisions with rule references
- objects with provenance
- exports with source linkage
- reproducible priority decisions
- complete stop reasons

---

# Interoperability Metrics

Examples

- mapping completeness
- FHIR profile validation
- terminology binding validity
- round-trip semantic preservation
- unmapped Fact rate
- mapping version traceability

FHIR validity does not imply clinical correctness.

---

# Evaluation Dataset

An evaluation dataset declares

- scope
- package version
- case identifiers
- language
- Encounter Context distribution
- RFE distribution
- safety distribution
- expected outputs
- prohibited outputs
- provenance

Training or builder-generation cases must be separated from held-out evaluation cases.

---

# Baselines

Every release records

- previous package baseline
- previous Runtime baseline
- terminology baseline
- guideline baseline
- evaluation configuration
- metric thresholds

Regression comparison is mandatory.

---

# Acceptance Gates

A release gate may require

- zero critical safety failures
- complete provenance
- all required Simulations passing
- minimum Fact accuracy
- maximum hallucination rate
- minimum Coverage
- no unexplained regression
- valid package integrity
- compatible Runtime result

Thresholds are versioned and scope-specific.

---

# Failure Analysis

Every failure is classified.

Categories include

- source error
- normalization error
- alignment error
- graph error
- rule error
- template error
- Runtime error
- mapping error
- evaluation-data error

Failures return to the responsible Build-Time stage.

Runtime is not patched with hidden exceptions.

---

# Human Review

Human clinical review is required for

- safety failures
- guideline interpretation
- ambiguous clinical meaning
- escalation language
- release blocking disagreements

Reviewer identity and decision are provenance.

---

# Reproducibility

Evaluation records

- package version
- Runtime version
- dataset version
- configuration
- model version
- seeds
- environment
- timestamps
- result digest

---

# Reporting

Evaluation reports contain

- scope
- metrics
- thresholds
- pass or fail
- regression comparison
- known limitations
- unresolved failures
- reviewer decisions
- provenance

Reports are immutable release artifacts.

---

# Final Principle

Evaluation determines whether knowledge is ready.

File count, demo quality and model fluency do not.
