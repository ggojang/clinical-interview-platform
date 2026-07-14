# Provenance

Version: 0.1 (Draft)

---

# Purpose

This document defines the Provenance Model of the Clinical Interview Knowledge Platform.

Provenance records

- where information originated,
- how it was transformed,
- who created it,
- when it was created,
- why it exists,
- and how it reached Runtime.

Every repository object has provenance.

No exceptions.

---

# Philosophy

Knowledge without provenance is not trustworthy.

The repository does not merely preserve medical knowledge.

The repository preserves the history of knowledge.

Every repository object must answer

- Where did this come from?
- How was it generated?
- Which Builder created it?
- Which version produced it?
- Which medical sources contributed?
- Which Runtime Package contains it?

---

# Scope

Provenance applies to

Medical Sources

Knowledge Acquisition

Normalization

Semantic Alignment

Knowledge Graph

Rule Graph

Simulation

Coverage

Compilation

Runtime Package

Clinical Memory

FHIR Export

Evaluation

Runtime Decisions

Everything.

---

# Provenance Layers

The repository defines six provenance layers.

---

## Layer 1

Medical Source Provenance

Examples

SNOMED CT

FHIR

ICPC-2

NICE

CHEST

ERS

GINA

GOLD

CDC

Local Guideline

This provenance answers

"What external source contributed?"

---

## Layer 2

Builder Provenance

Examples

Builder Version

Knowledge Package Version

Configuration

Coverage Definition

Build Identifier

This provenance answers

"How was repository knowledge created?"

---

## Layer 3

Knowledge Provenance

Every repository object

Fact

Interview Target

Clinical Intent

Question Template

Simulation

contains

Creation Time

Builder Version

Medical Sources

Transformation History

Review Status

Knowledge Version

---

## Layer 4

Compilation Provenance

Compilation records

Compiler Version

Input Graph Version

Output Package Version

Compilation Profile

Coverage Snapshot

Compilation Time

Compilation Hash

This provenance answers

"Which Runtime Package contains this knowledge?"

---

## Layer 5

Runtime Provenance

Runtime records

Question Generated

Interview Target Activated

Fact Updated

Clinical Intent Activated

Rule Executed

Reasoning Trace

Question Priority

Runtime Provenance never modifies Knowledge.

---

## Layer 6

Export Provenance

FHIR Export

Clinical Summary

Simulation Report

Coverage Report

Evaluation Report

Every exported artifact references the Runtime and Knowledge versions from which it originated.

---

# Provenance Identity

Every provenance record has

Identifier

Version

Activity

Agent

Timestamp

Repository Version

Builder Version

Status

Provenance identifiers are globally unique.

---

# Provenance Graph

Provenance is represented as a graph.

Example

Medical Source

↓

Knowledge Acquisition

↓

Normalization

↓

Semantic Alignment

↓

Knowledge Graph

↓

Compilation

↓

Runtime Package

↓

Question

↓

Patient Answer

↓

Clinical Memory

↓

FHIR Export

The graph is traversable in both directions.

---

# Provenance Activities

Repository activities include

Acquire

Normalize

Align

Generate

Validate

Review

Compile

Execute

Summarize

Export

Archive

Every activity has provenance.

---

# Provenance Agents

Agents include

Human

Builder

Compiler

Runtime

Simulation Engine

Reviewer

Import Tool

Terminology Server

FHIR Server

AI Model

Each activity records one or more agents.

---

# Source Provenance

Medical Source provenance records

Publisher

Version

Release Date

Jurisdiction

Language

License

Canonical URL

Source Identifier

Acquisition Method

Source Digest

Repository objects never reference only filenames.

---

# Builder Provenance

Builder records

Builder Version

Configuration

Knowledge Baseline

Coverage Baseline

Input Sources

Transformation Steps

Output Objects

Builder provenance is immutable.

---

# Object Provenance

Every repository object records

Creation Activity

Current Version

Review Status

Current Owner

Previous Version

Transformation History

No object is anonymous.

---

# Rule Provenance

Every Rule records

Medical Sources

Guideline

Simulation Validation

Review Status

Compiler Version

Rule Version

Safety Classification

---

# Question Provenance

Questions are generated.

Questions record

Interview Target

Required Facts

Question Template

Rule

Knowledge Package

Runtime Version

Questions never exist without provenance.

---

# Fact Provenance

Facts contain

Source

Evidence

Confidence

Extraction

Transformation

Review

Compilation

Runtime Usage

Fact provenance is preserved across every stage.

---

# Clinical Memory Provenance

Clinical Memory stores

Fact Value

Evidence

Source

Patient Turn

Extraction Version

Confidence

Rule History

Clinical Memory never stores anonymous facts.

---

# Runtime Decision Provenance

Every Runtime decision records

Current Clinical Intent

Interview Target

Missing Facts

Available Facts

Executed Rules

Priority Calculation

Selected Question

Reasoning Trace

The repository must be able to reconstruct why a question was asked.

---

# Export Provenance

FHIR exports record

Knowledge Package

Runtime Package

Clinical Memory Version

Fact Versions

Export Version

FHIR Profile

Terminology Version

This guarantees reproducibility.

---

# Version Chain

Every provenance object records

Previous Version

Current Version

Replacement

Deprecated Status

Repository evolution is explicit.

---

# Provenance Metadata

Minimum metadata

Identifier

Activity

Agent

Timestamp

Version

Repository Version

Knowledge Package

Status

Hash

Review

---

# Provenance Validation

Validation checks

Missing provenance

Broken lineage

Invalid timestamps

Unknown agent

Unknown source

Missing version

Broken references

Validation is mandatory.

---

# Provenance Storage

Provenance is stored independently.

Repository objects reference

provenance_id

The provenance graph stores detailed lineage.

Objects never duplicate provenance.

---

# Immutability

Released provenance never changes.

Corrections create

New Provenance

not

Updated Provenance.

History is preserved.

---

# Traceability

Every Runtime artifact must be traceable.

Question

↓

Interview Target

↓

Fact

↓

Knowledge Graph

↓

Builder

↓

Medical Source

The complete chain must be reconstructable.

---

# FHIR Alignment

Repository Provenance is independent.

FHIR Provenance Resource is one possible export.

Repository Provenance is richer than any single export format.

FHIR export is therefore a projection of Repository Provenance.

---

# Design Rules

Every object has provenance.

Every edge has provenance.

Every activity has provenance.

Every build has provenance.

Every Runtime decision has provenance.

Every export has provenance.

No exceptions.

---

# Final Principle

The repository does not merely preserve knowledge.

The repository preserves the complete lineage of knowledge.

Knowledge can be trusted only when its provenance can be reconstructed.
