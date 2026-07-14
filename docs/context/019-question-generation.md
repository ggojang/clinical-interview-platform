# Question Generation

Version: 0.1 (Draft)

---

# Purpose

This document defines Question Generation.

Questions are the patient-facing interface for collecting Facts required by Interview Targets.

Questions do not define knowledge.

Questions do not create Clinical Intent.

Questions are never generated directly from diagnosis.

---

# Relationship

```text
Clinical Intent
        ↓
Interview Target
        ↓
Missing Fact
        ↓
Question Template
        ↓
Rendered Question
```

---

# Core Principle

Questions exist because information is required.

Not because a diagnosis exists.

---

# Question Template

A Question Template contains

- identifier
- collected Fact
- supported Targets
- language
- mode
- wording
- reading level
- response type
- examples
- prohibited contexts
- repetition group
- provenance
- version

Templates are repository knowledge.

Rendered Questions are Runtime artifacts.

---

# Candidate Generation

A candidate Question may be created only when

- an active Target requires a Fact
- the Fact is unresolved
- the Fact is applicable
- no higher-priority action suppresses it
- an approved Template exists
- repetition policy permits it

Missing templates are package validation failures for required Targets.

---

# Candidate Classes

Default candidate order

1. urgent safety clarification
2. contradiction resolution
3. required Target Fact
4. high-value optional Fact
5. contextual refinement
6. summary confirmation

This ordering is refined by compiled priority rules.

---

# Wording Principles

Questions must

- ask one primary clinical concept
- use neutral language
- avoid suggesting the expected answer
- avoid exposing hidden Hypotheses
- preserve patient wording when useful
- match supported language and mode
- respect reading level
- allow uncertainty
- allow refusal

---

# Compound Questions

Compound Questions are discouraged.

Example

```text
Do you have fever, chest pain or shortness of breath?
```

This creates ambiguous response mapping.

A compound Question requires explicit structured response semantics and validation.

Safety policy may permit a brief grouped screen only when each response can be resolved independently.

---

# Leading Questions

Leading wording is prohibited.

Question Templates must not imply

- a preferred answer
- a diagnosis
- causation
- blame
- moral judgment

Leading wording receives a priority penalty and may be rejected.

---

# Confirmation Questions

Confirmation is required when

- a safety-critical value is ambiguous
- normalization changes meaning
- evidence conflicts
- a vague amount changes priority
- a structured source conflicts with patient report

Confirmation never erases original evidence.

---

# Context Adaptation

Encounter Context may affect

- formality
- brevity
- permitted examples
- mode
- time budget
- source actor
- accessibility requirements

Context does not change the Fact being collected.

---

# Language Adaptation

Translation preserves

- semantic target
- polarity
- temporality
- severity
- response options
- uncertainty

Language variants have independent provenance and review status.

Runtime does not freely translate safety instructions unless an approved mechanism exists.

---

# Question Selection

Question selection evaluates

- target priority
- safety value
- information gain
- discrimination
- burden
- repetition
- redundancy
- patient preference
- mode compatibility

The selected Question cites the chosen Template and Target.

---

# Repetition

Equivalent Questions belong to a repetition group.

Runtime avoids asking an equivalent Question when

- the Fact is already resolved
- the patient declined
- an adequate answer exists
- no new conflict requires clarification

A repeated Question must record its reason.

---

# Response Handling

A Question does not determine its answer.

Patient response returns to the ordinary Reasoning Loop.

Responses may be

- known
- explicitly negative
- uncertain
- refused
- irrelevant
- ambiguous
- conflicting

The system never coerces a value.

---

# Question Provenance

Every rendered Question records

- Template identifier and version
- Target identifier
- Fact identifier
- selection rule
- priority components
- Runtime version
- package version
- wording transformation
- timestamp

---

# Simulation

Question Simulation includes

- positive answers
- negative answers
- uncertain answers
- refusal
- misunderstanding
- leading-question sensitivity
- compound-question ambiguity
- repeated-question behavior
- language variants
- mode variants

---

# Coverage

Question Coverage measures

- required Facts with Templates
- supported languages
- supported modes
- reading levels
- response types
- safety wording review
- simulation coverage

---

# Final Principle

Interview Targets determine what information is needed.

Facts determine whether it is known.

Questions are only the interface used to collect it.
