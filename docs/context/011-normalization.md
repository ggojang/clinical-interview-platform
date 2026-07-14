# Normalization

Version: 0.1 (Draft)

---

# Purpose

Normalization converts heterogeneous medical information into a stable,
canonical internal representation.

Normalization occurs after Knowledge Acquisition and before Semantic Alignment.

Normalization does not create new medical knowledge.

Normalization only standardizes representation.

---

# Philosophy

Different medical sources describe identical concepts differently.

Normalization guarantees that the repository treats semantically equivalent
information consistently.

Normalization never changes clinical meaning.

Normalization never introduces interpretation.

Normalization preserves the original source.

---

# Pipeline

```
Medical Sources

↓

Raw Source

↓

Normalization

↓

Normalized Source

↓

Semantic Alignment
```

---

# Objectives

Normalization has six objectives.

1. Preserve original information.

2. Remove representation differences.

3. Produce deterministic internal structures.

4. Preserve provenance.

5. Enable semantic alignment.

6. Enable reproducible builds.

---

# Scope

Normalization applies to

Terminology

Guidelines

FHIR

Evidence

Local Rules

Repository Objects

Simulation

Coverage

---

# Levels

The repository performs normalization at several levels.

---

## Structure Normalization

Purpose

Create a consistent document structure.

Examples

FHIR Parameters

↓

Internal Parameter Model

JSON

↓

Canonical JSON

XML

↓

Canonical JSON

Markdown

↓

Structured Sections

---

## Terminology Normalization

Purpose

Standardize terminology identifiers.

Examples

SNOMED URI

↓

Canonical URI

FHIR canonical URL

↓

Canonical URL

ICPC Code

↓

Canonical Code

No aliases remain after normalization.

---

## Identifier Normalization

Identifiers must be globally unique.

Example

Good

```
fact.symptom.duration
```

Bad

```
duration

Duration

symptomDuration
```

Builder always uses canonical identifiers.

---

## Language Normalization

Every text element contains

Language

Display

Preferred Term

Alternative Terms

FSN (if applicable)

Normalization never removes multilingual information.

---

## Unit Normalization

Units are normalized.

Examples

days

day

d

↓

day

weeks

↓

week

Normalization never changes value semantics.

---

## Time Normalization

Time expressions are normalized.

Examples

Yesterday

↓

relative time

Three days ago

↓

relative duration

2026-07-15

↓

absolute date

Original expression is preserved.

---

## Metadata Normalization

Metadata becomes consistent.

Examples

Version

Timestamp

Publisher

Jurisdiction

License

Language

Review Status

All metadata uses canonical formats.

---

## Provenance Normalization

Every normalized object references

Original Source

Acquisition Event

Normalization Event

Builder Version

Timestamp

Nothing loses provenance.

---

# Original Preservation

Raw source is immutable.

Normalization never overwrites original material.

```
Raw Source

↓

Normalized Source
```

Both coexist.

---

# Canonical Representation

Every object has one canonical representation.

Examples

Identifier

Display

Description

Language

Version

Status

Metadata

Canonical representation is deterministic.

---

# Determinism

Given identical input

Normalization always produces identical output.

Normalization must not depend upon

Runtime

Time

Network

Randomness

LLM sampling

---

# Terminology Normalization

Terminology normalization standardizes

Concept identifiers

Version URIs

Reference Set identifiers

MRCM identifiers

Canonical URIs

Display Language

Designation Types

---

# Guideline Normalization

Guidelines are normalized into

Publisher

Guideline Identifier

Version

Section

Recommendation

Evidence Strength

Recommendation Strength

Jurisdiction

Publication Date

Revision Date

Builder never references page numbers directly.

---

# FHIR Normalization

FHIR resources become canonical internal objects.

Normalization preserves

Canonical URL

Version

Resource Type

Element Paths

Bindings

Data Types

Profiles

FHIR remains an interoperability layer.

---

# ICPC Normalization

ICPC-2 is normalized into

Code

Axis

Display

Category

Classification Type

Version

ICPC remains a classification source.

---

# Simulation Normalization

Simulation objects become

Canonical Patient

Canonical Scenario

Canonical Expected Facts

Canonical Expected Questions

Simulation normalization removes formatting differences only.

---

# Fact Normalization

Facts are normalized into

Identifier

Value Type

Allowed Values

Metadata

Mappings

Provenance

Facts are not merged during normalization.

---

# Rule Normalization

Rules are normalized into

Trigger

Condition

Action

Priority

Version

Provenance

Behavior is unchanged.

---

# Coverage Normalization

Coverage objects become

Coverage Domain

Coverage Item

Coverage Status

Coverage Metrics

Coverage Version

Coverage remains independent from Runtime.

---

# Validation

Normalization validates

Identifiers

Structure

Metadata

Language

Terminology Version

Canonical URIs

Missing mandatory fields

Normalization does not perform semantic validation.

---

# Error Handling

Normalization failures are explicit.

Examples

Unknown identifier

Invalid URI

Invalid language

Missing version

Malformed FHIR resource

Malformed terminology response

Normalization never silently repairs unknown data.

---

# Output

Normalization produces

Normalized Sources

Normalized Metadata

Canonical Identifiers

Canonical Terminology

Canonical Repository Objects

Everything remains traceable to the original source.

---

# Provenance

Every normalization event records

Normalization Identifier

Builder Version

Input Object

Output Object

Timestamp

Operator

Transformation Type

No normalization step is anonymous.

---

# Repository Rules

Normalization

must preserve meaning.

must preserve provenance.

must preserve source.

must be deterministic.

must be reproducible.

must not perform reasoning.

must not create Facts.

must not create Questions.

must not modify Clinical Intent.

Normalization is representation transformation only.

---

# Final Principle

Normalization creates a consistent representation of external medical knowledge.

Normalization never creates new knowledge.

Its purpose is to prepare trustworthy input for Semantic Alignment.
