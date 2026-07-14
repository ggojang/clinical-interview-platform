# Knowledge Graph

Version: 0.1 (Draft)

---

# Purpose

This document defines the internal Knowledge Graph of the Clinical Interview Knowledge Platform.

The Knowledge Graph is the canonical internal representation of interview knowledge.

Everything else is derived from this graph.

Examples

- Clinical Intent
- Interview Target
- Question
- Simulation
- Coverage
- Runtime Package
- FHIR Mapping

are projections of the Knowledge Graph.

---

# Philosophy

The repository does not store knowledge as documents.

The repository stores knowledge as a graph.

Markdown, YAML, JSON, Python and FHIR are different representations of the same graph.

---

# Source of Truth

The Knowledge Graph is the single source of truth inside the repository.

Medical Sources

↓

Knowledge Acquisition

↓

Knowledge Graph

↓

Compiled Knowledge

↓

Runtime

Runtime never modifies the Knowledge Graph.

---

# Graph Principles

The graph is

Versioned

Deterministic

Reusable

Traceable

Composable

Every node has provenance.

Every edge has provenance.

---

# Node Types

The graph consists of reusable node types.

## Encounter Context

Represents the clinical environment.

Examples

Primary Care

Emergency

Telemedicine

Health Check

Medication Review

---

## Reason for Encounter

Represents why care is sought.

Examples

Cough

Chest pain

Vaccination

Medication refill

Health examination

---

## Clinical Intent

Represents the interview objective.

Examples

Characterize symptom

Screen red flags

Assess severity

Medication review

Preventive assessment

---

## Interview Target

Represents a unit of information required to satisfy an Intent.

Examples

Determine symptom duration

Determine smoking status

Determine fever

Determine occupational exposure

---

## Fact

Represents reusable clinical information.

Examples

symptom.duration

patient.age

medication.current

history.operation

---

## Question Template

Represents reusable wording.

Question Templates never own Facts.

Question Templates collect Facts.

---

## Clinical Group

Represents reusable interview grouping.

Examples

Upper airway

Lower airway

Medication related

Reflux related

Environmental exposure

---

## Simulation

Represents expected interview behaviour.

Simulation validates the graph.

---

## Coverage

Represents repository completeness.

Coverage is calculated from graph connectivity.

---

## Mapping

Represents interoperability.

Examples

SNOMED CT

FHIR

ICPC-2

LOINC

---

# Graph Relationships

Relationships are explicit.

Examples

Encounter Context

ACTIVATES

Clinical Intent

Clinical Intent

GENERATES

Interview Target

Interview Target

REQUIRES

Fact

Question Template

COLLECTS

Fact

Fact

SUPPORTS

Clinical Group

Clinical Group

CONTRIBUTES_TO

Coverage

Fact

MAPS_TO

FHIR Element

Fact

MAPS_TO

SNOMED Concept

Simulation

VALIDATES

Fact

Simulation

VALIDATES

Interview Target

Simulation

VALIDATES

Question Template

---

# Graph Rules

No node owns another node.

Nodes reference each other.

Knowledge is represented through relationships.

---

# Fact-Centric Design

Facts are the semantic center of the graph.

Everything ultimately exists because Facts exist.

Questions collect Facts.

Interview Targets require Facts.

Clinical Memory stores Facts.

FHIR exports Facts.

Simulation validates Facts.

Coverage measures Facts.

Facts are repository assets.

---

# Intent-Centric Planning

Clinical Intent determines planning.

Interview Target determines execution.

Fact determines completion.

Question determines interaction.

These are different responsibilities.

---

# Graph Layers

Layer 1

Medical Sources

Layer 2

Knowledge Acquisition

Layer 3

Knowledge Graph

Layer 4

Compilation

Layer 5

Runtime Package

Layer 6

Runtime Execution

Layer 7

Clinical Memory

Layer 8

FHIR Export

Each layer depends only on the previous layer.

---

# Knowledge Acquisition

Medical Sources never enter Runtime directly.

Medical Sources are transformed.

Transformation creates graph nodes.

Examples

SNOMED

↓

Fact Mapping

FHIR

↓

FHIR Mapping

Guideline

↓

Priority Rules

MRCM

↓

Semantic Constraints

ICPC

↓

Coverage

---

# Compilation

Compilation transforms the graph into runtime structures.

Examples

Question Graph

Intent Graph

Simulation Package

Coverage Report

FHIR Mapping Table

Priority Table

Compiled Runtime Package

Compilation is deterministic.

---

# Runtime

Runtime consumes the compiled graph.

Runtime never changes the graph.

Runtime never adds graph nodes.

Runtime may create

Clinical Memory

Reasoning Trace

FHIR Resources

These are runtime artifacts.

---

# Graph Evolution

The graph continuously evolves.

Medical Sources change.

Guidelines change.

Terminology changes.

Simulation improves.

The graph evolves.

Runtime Packages are regenerated.

---

# Graph Version

Every graph release has

Knowledge Version

Builder Version

Terminology Baseline

Guideline Baseline

Compilation Version

Coverage Report

Simulation Report

Regression Report

---

# Provenance

Every node has provenance.

Every edge has provenance.

Every compilation has provenance.

Every Runtime Package has provenance.

Graph lineage must be reconstructable.

---

# Coverage

Coverage is computed from graph completeness.

Coverage dimensions include

Encounter Context

Reason for Encounter

Clinical Intent

Interview Target

Fact

Question

Simulation

Mapping

Coverage is never estimated manually.

Coverage is computed.

---

# Graph Constraints

Nodes are immutable inside a released package.

Relationships are immutable inside a released package.

Changes create new graph versions.

---

# Graph is Independent

The graph is independent from

Programming language

Runtime

FHIR version

SNOMED version

Database

User Interface

LLM

The graph survives implementation changes.

---

# Final Principle

The Knowledge Graph is the canonical representation of interview knowledge.

The repository exists to create, validate, evolve and compile the Knowledge Graph.

Everything else is derived.
