# Builder Model

Version: 0.1 (Draft)

---

# Purpose

This document defines the Knowledge Builder.

The Builder is responsible for constructing the internal Knowledge Graph and Rule Graph.

Runtime never builds knowledge.

Runtime only executes compiled knowledge.

Builder is the only component allowed to generate repository knowledge.

---

# Philosophy

Medical knowledge is never handwritten directly into Runtime.

Medical knowledge is acquired.

normalized.

validated.

compiled.

versioned.

Builder performs this transformation.

---

# Builder Overview

Medical Sources

↓

Knowledge Acquisition

↓

Normalization

↓

Semantic Alignment

↓

Knowledge Graph

↓

Rule Graph

↓

Simulation

↓

Evaluation

↓

Compilation

↓

Runtime Package

---

# Builder Inputs

Builder accepts only structured inputs.

Inputs are divided into independent source types.

---

## Terminology Sources

Purpose

Provide semantic alignment.

Examples

SNOMED CT

LOINC

ICD

ICPC-2

FHIR Terminology

These sources never determine interview behaviour.

---

## Knowledge Sources

Purpose

Provide reusable medical knowledge.

Examples

NICE

CHEST

ERS

GINA

GOLD

CDC

USPSTF

Local Guidelines

Hospital Protocols

---

## Coverage Definition

Purpose

Define repository scope.

Examples

Primary Care

Respiratory

Medication Review

Vaccination

Administrative

Coverage defines

what Builder should build.

---

## Existing Repository

Builder reads

Facts

Interview Targets

Clinical Intents

Rules

Questions

Simulation

Builder always attempts reuse.

Builder never duplicates knowledge.

---

## Runtime Feedback

Runtime contributes

Simulation failures

Coverage failures

Missing Facts

Question redundancy

Incorrect priorities

Builder treats Runtime as feedback.

Runtime never modifies Knowledge directly.

---

# Builder Stages

Builder executes deterministic stages.

---

## Stage 1

Acquire

Collect all requested source material.

No transformation occurs.

---

## Stage 2

Normalize

Normalize terminology.

Normalize metadata.

Normalize provenance.

No semantics change.

---

## Stage 3

Align

Align concepts.

Examples

SNOMED

↓

Fact

FHIR

↓

Fact

ICPC

↓

Reason for Encounter

---

## Stage 4

Graph Construction

Generate

Knowledge Graph

Nodes

Edges

Mappings

Provenance

No runtime behaviour.

---

## Stage 5

Rule Construction

Generate

Activation Rules

Priority Rules

Dependency Rules

Completion Rules

Simulation Rules

Coverage Rules

---

## Stage 6

Simulation Generation

Generate

Positive Cases

Negative Cases

Boundary Cases

Contradictory Cases

Missing Information Cases

Declined Answer Cases

Simulation is mandatory.

---

## Stage 7

Validation

Schema

Terminology

Graph

Simulation

Coverage

Regression

All validation must succeed.

---

## Stage 8

Compilation

Compile

Knowledge Graph

↓

Runtime Package

Compilation is deterministic.

---

# Builder Outputs

Builder produces

Knowledge Graph

Rule Graph

Simulation Package

Coverage Report

Compiled Runtime Package

Provenance Graph

Validation Report

Builder never produces Runtime State.

---

# Builder Principles

Builder

never modifies Runtime.

never modifies Clinical Memory.

never creates diagnoses.

never creates patient data.

always produces provenance.

always produces simulation.

always produces coverage.

---

# Knowledge Acquisition

Knowledge acquisition is deterministic.

Builder never invents knowledge.

Builder transforms existing medical knowledge into reusable interview knowledge.

---

# Knowledge Transformation

Medical Source

↓

Repository Concept

↓

Interview Concept

↓

Fact

↓

Interview Target

↓

Question Template

↓

Simulation

Every transformation must be traceable.

---

# Reuse First

Builder attempts reuse before generation.

Priority

Reuse Fact

↓

Reuse Interview Target

↓

Reuse Question Template

↓

Generate New Object

Duplicate semantic concepts are prohibited.

---

# Provenance

Every generated object contains

Builder Version

Build Identifier

Source References

Transformation History

Review Status

Timestamp

No anonymous object exists.

---

# Builder Configuration

Builder is configurable.

Configuration includes

Coverage

Terminology Baseline

Guideline Baseline

Compilation Profile

Language

Jurisdiction

Target Runtime

---

# Incremental Build

Builder supports incremental generation.

Only changed objects are rebuilt.

Unchanged graph components remain immutable.

Incremental build must produce identical results.

---

# Bootstrap Build

Bootstrap creates

Primary Care Coverage

Knowledge Graph

Rule Graph

Simulation

Coverage

Compiled Package

Bootstrap occurs only once for each baseline.

---

# Continuous Build

Continuous Build responds to

Terminology Updates

Guideline Updates

Coverage Expansion

Simulation Feedback

Repository Improvement

Continuous Build never replaces released Runtime Packages.

---

# Build Baseline

Every build records

Terminology Version

Guideline Version

Coverage Version

Builder Version

Compiler Version

Simulation Version

Repository Version

Baseline guarantees reproducibility.

---

# Builder Constraints

Builder

must be deterministic.

must be reproducible.

must be traceable.

must be testable.

must be versioned.

must be idempotent.

must produce provenance.

must produce simulation.

must never bypass validation.

---

# Repository Rule

Builder is the only component allowed to create repository knowledge.

Every repository object originates from Builder.

Nothing enters Runtime without Builder.

---

# Final Principle

Builder transforms medical knowledge into executable interview knowledge.

Knowledge Builder is the heart of the Clinical Interview Knowledge Platform.

Everything else exists to support, execute, validate or evolve Builder output.
