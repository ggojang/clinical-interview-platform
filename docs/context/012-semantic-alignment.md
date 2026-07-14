# Semantic Alignment

Version: 0.1 (Draft)

---

# Purpose

Semantic Alignment transforms normalized medical information into repository
knowledge.

Normalization standardizes representation.

Semantic Alignment establishes meaning.

Semantic Alignment is the first stage where repository semantics are created.

---

# Philosophy

Medical sources describe medicine.

The repository describes interviews.

Semantic Alignment bridges these two domains.

Builder does not copy medical terminology.

Builder creates Interview Knowledge.

---

# Pipeline

```
Medical Sources

↓

Knowledge Acquisition

↓

Normalization

↓

Semantic Alignment

↓

Knowledge Graph
```

Semantic Alignment is the boundary between external knowledge and repository knowledge.

---

# Objectives

Semantic Alignment has six objectives.

1. Identify reusable concepts.

2. Remove source-specific semantics.

3. Create repository semantics.

4. Establish graph relationships.

5. Preserve traceability.

6. Enable deterministic compilation.

---

# Source Independence

Different medical sources may describe the same concept.

Example

SNOMED CT

↓

Cough

ICPC-2

↓

Reason for Encounter

Guideline

↓

Persistent cough assessment

Repository

↓

Reason for Encounter

Clinical Intent

Interview Target

Fact

Question

The repository never stores duplicated concepts simply because they originate
from different sources.

---

# Repository Semantics

Repository semantics are independent.

Examples

Clinical Intent

Interview Target

Coverage

Simulation

Question Template

These concepts do not exist in SNOMED CT.

They are repository concepts.

---

# Alignment Domains

Semantic Alignment operates on several domains.

---

## Terminology Alignment

Maps external terminology into repository identifiers.

Examples

SNOMED CT

↓

Repository Fact

LOINC

↓

Repository Observation Target

FHIR

↓

Repository Mapping

Terminology alignment never determines interview behavior.

---

## Classification Alignment

Maps classification systems.

Examples

ICPC-2

↓

Reason for Encounter

Problem

↓

Coverage

Classification supports navigation.

Not interview logic.

---

## Guideline Alignment

Guidelines contribute

Clinical Intent

Interview Target

Priority

Safety

Follow-up

Guidelines never generate repository objects directly.

Builder extracts reusable concepts.

---

## FHIR Alignment

FHIR contributes

Element Mapping

Data Types

Profiles

Bindings

FHIR is not an interview model.

FHIR is an interoperability model.

---

## Simulation Alignment

Simulation validates repository semantics.

Simulation never defines repository semantics.

---

# Alignment Objects

Alignment produces

Repository Nodes

Repository Relationships

Mappings

Constraints

Coverage Links

Rule Candidates

Simulation Candidates

---

# Alignment Process

Stage 1

Identify source concepts.

↓

Stage 2

Identify repository concept.

↓

Stage 3

Determine relationships.

↓

Stage 4

Create graph nodes.

↓

Stage 5

Create graph edges.

↓

Stage 6

Record provenance.

↓

Stage 7

Validate.

---

# Semantic Identity

One semantic concept

↓

One repository object.

Examples

symptom.duration

Exists once.

Not once per Presentation.

Not once per Guideline.

Not once per terminology.

Repository semantics eliminate duplication.

---

# Fact Alignment

Facts are aligned before generation.

Example

Source

```
Duration of cough
```

```
Symptom duration
```

```
Length of illness
```

Repository

```
fact.symptom.duration
```

Only one Fact is created.

---

# Interview Target Alignment

Interview Targets are aligned from multiple sources.

Example

Guideline

```
Assess smoking
```

Guideline

```
Review smoking history
```

Guideline

```
Smoking status
```

Repository

```
Determine Smoking Status
```

One Interview Target.

---

# Question Alignment

Questions are aligned by purpose.

Different wording.

Same objective.

Repository stores

Question Template

↓

Collects

↓

Fact

Question wording never defines repository semantics.

---

# Clinical Intent Alignment

Clinical Intents are repository abstractions.

Examples

Safety Assessment

Symptom Characterization

Common Cause Differentiation

Medication Review

Preventive Assessment

These are independent from

SNOMED

FHIR

ICPC

Guidelines

---

# Relationship Alignment

Builder creates reusable graph relationships.

Examples

ReasonForEncounter

SUGGESTS

ClinicalIntent

ClinicalIntent

GENERATES

InterviewTarget

InterviewTarget

REQUIRES

Fact

Fact

SUPPORTS

ClinicalGroup

ClinicalGroup

SUPPORTS

Hypothesis

Relationship semantics belong to the repository.

---

# Conflict Resolution

Different sources may disagree.

Repository never silently resolves conflicts.

Conflict resolution creates

Candidate

↓

Review

↓

Decision

↓

Knowledge

Rejected candidates remain traceable.

---

# Ambiguity

Semantic ambiguity is preserved.

Example

```
Cold
```

May represent

Temperature

Common Cold

Repository never guesses.

Builder records ambiguity.

---

# MRCM Alignment

MRCM contributes

Allowed attributes

Domain constraints

Attribute ranges

Semantic consistency

Builder uses MRCM during alignment.

Runtime never executes MRCM.

---

# Guideline Alignment Rules

Guidelines influence

Priority

Safety

Intent

Interview Target

They do not directly create Questions.

Builder converts recommendations into reusable repository concepts.

---

# Coverage Alignment

Coverage is aligned after graph construction.

Coverage references

Reason for Encounter

Clinical Intent

Interview Target

Fact

Simulation

Coverage never references diagnoses directly.

---

# Provenance

Every alignment creates provenance.

Source

↓

Normalized Object

↓

Repository Object

↓

Knowledge Graph

↓

Compiled Package

Lineage must be reconstructable.

---

# Validation

Alignment validates

Duplicate concepts

Duplicate identifiers

Broken mappings

Broken relationships

Missing provenance

Unresolved ambiguity

Invalid graph references

Validation is mandatory.

---

# Repository Rules

Semantic Alignment

must create repository semantics.

must preserve provenance.

must preserve source identity.

must eliminate duplication.

must not create Runtime state.

must not execute interview logic.

must not perform diagnosis.

must be deterministic.

---

# Final Principle

Semantic Alignment is the process that transforms external medical knowledge
into repository knowledge.

Medical sources describe medicine.

The repository describes reusable interview knowledge.

Semantic Alignment connects these two worlds.
