# Rule Graph

Version: 0.1 (Draft)

---

# Purpose

This document defines the Rule Graph.

The Knowledge Graph describes **what exists**.

The Rule Graph describes **how knowledge is used**.

The Knowledge Graph is static.

The Rule Graph is executable.

The Runtime executes the Rule Graph.

---

# Why Rule Graph Exists

Knowledge alone is insufficient.

Example

Fact

```
symptom.fever.present
```

This fact does not explain

- when it should be collected
- why it is important
- what it supports
- what should happen after collection

These behaviours belong to the Rule Graph.

---

# Knowledge vs Rule

Knowledge Graph answers

```
What is this?
```

Rule Graph answers

```
What should happen?
```

Knowledge Graph

```
symptom.duration
```

Rule Graph

```
IF duration is unknown

THEN

Generate Interview Target
```

---

# Philosophy

Knowledge must never contain behaviour.

Rules must never redefine knowledge.

Knowledge is stable.

Rules evolve.

---

# Runtime

Runtime never invents rules.

Runtime executes compiled rules.

Every rule is generated during Knowledge Build.

---

# Rule Types

The repository defines reusable Rule Types.

## Activation Rule

Purpose

Determine when a node becomes active.

Example

```
Encounter Context

Primary Care

+

Reason for Encounter

Cough

↓

Activate

Characterize Symptom
```

---

## Completion Rule

Purpose

Determine when an Interview Target is satisfied.

Example

```
Fact

symptom.duration

↓

Target Completed
```

---

## Priority Rule

Purpose

Assign execution priority.

Example

```
Red Flag

↓

Priority

100
```

---

## Suppression Rule

Purpose

Prevent unnecessary questions.

Example

```
Smoking already known

↓

Do not ask again
```

---

## Dependency Rule

Purpose

Describe prerequisite relationships.

Example

```
Determine Duration

↓

before

Determine Progression
```

---

## Escalation Rule

Purpose

Change Clinical Intent.

Example

```
Hemoptysis

↓

Activate

Emergency Screening
```

---

## Coverage Rule

Purpose

Determine whether repository coverage is complete.

---

## Simulation Rule

Purpose

Describe expected simulation behaviour.

---

## Validation Rule

Purpose

Validate graph consistency.

---

# Rule Objects

Each rule contains

Identifier

Type

Trigger

Condition

Action

Priority

Version

Status

Provenance

---

# Trigger

Triggers start rule evaluation.

Examples

New Fact

Updated Fact

Encounter Created

Reason for Encounter Added

Clinical Intent Activated

Interview Target Completed

Question Answered

Simulation Started

---

# Condition

Conditions determine whether a rule executes.

Examples

```
symptom.duration

is unknown
```

```
patient.age > 65
```

```
Clinical Intent active
```

Conditions must be deterministic.

---

# Action

Actions never modify Knowledge.

Actions modify Runtime State.

Examples

Activate Interview Target

Close Interview Target

Generate Question

Increase Priority

Decrease Priority

Activate Clinical Intent

Generate Summary

Create Clinical Memory Entry

---

# Rule Evaluation

Rules are evaluated continuously.

```
Patient Response

↓

Fact Update

↓

Rule Evaluation

↓

Priority Update

↓

Question Generation
```

---

# Rule Independence

Rules are reusable.

Example

```
Unknown smoking status

↓

Ask smoking question
```

This rule applies to

Cough

Chest Pain

COPD

Health Check

Medication Review

---

# Rule Layer

Rule Graph is layered.

Layer 1

Activation

Layer 2

Dependency

Layer 3

Priority

Layer 4

Execution

Layer 5

Completion

Rules execute in order.

---

# Rule Priority

Rules themselves have priority.

Example

Emergency

↓

Red Flag

↓

Common Cause

↓

Health Maintenance

---

# Rule Metadata

Each rule contains

Builder Version

Knowledge Version

Compilation Version

Rule Version

Review Status

Provenance

---

# Rule Provenance

Rules always contain provenance.

Medical Sources

↓

Knowledge Builder

↓

Rule

↓

Compilation

↓

Runtime

Every rule must be traceable.

---

# Rule Compilation

Rules are not interpreted directly.

Knowledge Builder

↓

Rule Graph

↓

Compiler

↓

Executable Rule Package

↓

Runtime

Compilation is deterministic.

---

# Runtime State

Rules modify Runtime State only.

Runtime State contains

Active Clinical Intents

Interview Targets

Question Queue

Clinical Memory

Reasoning Trace

Rule Execution History

Rules never modify the Knowledge Graph.

---

# Rule Testing

Every rule requires

Simulation

Regression

Coverage

Validation

No rule enters Runtime without testing.

---

# Rule Constraints

Rules

must be deterministic.

must be versioned.

must have provenance.

must be testable.

must be reusable.

must not modify Knowledge.

must not query Medical Sources.

---

# Design Principle

Knowledge answers

"What exists?"

Rules answer

"What happens?"

Separating these two responsibilities keeps the repository stable, testable, and reusable.

The Runtime executes compiled rules.

The Knowledge Factory evolves those rules.
