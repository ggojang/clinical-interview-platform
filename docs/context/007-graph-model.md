# Graph Model

Version: 0.1 (Draft)

---

# Purpose

This document defines the internal graph model of the Clinical Interview Knowledge Platform.

Unlike previous documents which define concepts, this document defines the actual graph structure used by the Knowledge Builder.

Every Builder, Compiler, Runtime and Evaluation component MUST use this graph model.

---

# Philosophy

The repository stores knowledge as a Property Graph.

The graph is implementation-independent.

Neo4j

NetworkX

RDF

Property Graph

Document Database

Relational Database

may all implement this model.

The logical model never changes.

---

# Graph Components

The graph consists of

Nodes

Edges

Properties

Constraints

Provenance

---

# Node

A node represents one reusable semantic object.

Every node

- has a globally unique identifier
- has a type
- has provenance
- has a version
- has metadata

Nodes never contain executable logic.

---

# Edge

Edges describe relationships.

Edges are directed.

Edges may contain metadata.

Edges may contain provenance.

Edges may contain weights.

Edges never duplicate node information.

---

# Property

Properties describe node attributes.

Examples

identifier

display

description

priority

version

status

language

Properties never replace graph relationships.

---

# Node Types

The repository defines the following node types.

## EncounterContext

Examples

PrimaryCare

EmergencyDepartment

Telemedicine

HealthCheck

MedicationReview

---

## ReasonForEncounter

Examples

Cough

ChestPain

MedicationRefill

Vaccination

Fatigue

HealthCheck

---

## ClinicalIntent

Examples

CharacterizeSymptom

AssessSeverity

ScreenRedFlags

MedicationReview

RiskAssessment

PreventiveCare

---

## InterviewTarget

Examples

DetermineDuration

DetermineSmokingStatus

DetermineFever

DetermineMedicationHistory

DetermineOccupation

---

## Fact

Examples

symptom.duration

patient.age

history.operation

medication.current

social.smoking

---

## QuestionTemplate

Examples

HowLong

SmokingQuestion

MedicationQuestion

OccupationQuestion

---

## ClinicalGroup

Examples

UpperAirway

LowerAirway

MedicationRelated

RefluxRelated

Cardiovascular

---

## Hypothesis

Examples

CommonCold

GERD

Asthma

COPD

Influenza

Hypothesis nodes never generate questions directly.

---

## Simulation

Examples

PatientScenario

ExpectedFacts

ExpectedQuestions

ExpectedCoverage

---

## Coverage

Examples

RespiratoryCoverage

PrimaryCareCoverage

MedicationCoverage

---

## Mapping

Examples

SNOMED Mapping

FHIR Mapping

ICPC Mapping

LOINC Mapping

---

## Guideline

Examples

NICE

CHEST

ERS

GINA

GOLD

CDC

USPSTF

---

# Core Relationships

The graph defines reusable edge types.

EncounterContext

ACTIVATES

ClinicalIntent

---

ReasonForEncounter

SUGGESTS

ClinicalIntent

---

ClinicalIntent

GENERATES

InterviewTarget

---

InterviewTarget

REQUIRES

Fact

---

QuestionTemplate

COLLECTS

Fact

---

Fact

SUPPORTS

ClinicalGroup

---

ClinicalGroup

SUPPORTS

Hypothesis

---

Fact

INCREASES

Hypothesis

---

Fact

DECREASES

Hypothesis

---

Simulation

VALIDATES

InterviewTarget

---

Simulation

VALIDATES

Fact

---

Simulation

VALIDATES

QuestionTemplate

---

Fact

MAPS_TO

FHIR

---

Fact

MAPS_TO

SNOMED

---

Fact

MAPS_TO

LOINC

---

ReasonForEncounter

CLASSIFIED_BY

ICPC

---

Guideline

SUPPORTS

ClinicalIntent

---

Guideline

SUPPORTS

InterviewTarget

---

Coverage

MEASURES

Fact

---

Coverage

MEASURES

Simulation

---

Coverage

MEASURES

QuestionTemplate

---

# Graph Constraints

## One Node

One Concept

One semantic meaning.

---

## No Duplicate Facts

Duplicate Facts are prohibited.

Builders must reuse existing Facts.

---

## No Duplicate Interview Targets

Interview Targets represent reusable objectives.

Duplicates are prohibited.

---

## Question Independence

Question Templates never own Interview Targets.

Question Templates are interchangeable.

---

## Runtime Independence

Runtime never changes graph nodes.

Runtime never creates graph nodes.

---

# Graph Metadata

Every node contains

identifier

type

display

description

version

status

language

provenance_id

created_at

updated_at

---

# Graph Edge Metadata

Edges may contain

priority

weight

confidence

activation_rule

builder_version

provenance_id

---

# Graph Version

The graph is immutable.

Updates create

Graph Version

rather than

Graph Mutation.

---

# Graph Traversal

Typical traversal

Encounter Context

↓

Reason for Encounter

↓

Clinical Intent

↓

Interview Target

↓

Fact

↓

Question Template

Another traversal

Fact

↓

Clinical Group

↓

Hypothesis

Traversal is deterministic.

---

# Builder Responsibility

Builder creates

Nodes

Edges

Mappings

Coverage

Simulation

Builder never creates Runtime objects.

---

# Compiler Responsibility

Compiler transforms the graph into

Question Graph

Priority Graph

Simulation Package

Coverage Report

FHIR Mapping Package

Runtime Package

Compiler never changes graph semantics.

---

# Runtime Responsibility

Runtime consumes compiled graphs.

Runtime creates

Clinical Memory

Reasoning Trace

FHIR Export

Runtime never edits the graph.

---

# Provenance

Every node

Every edge

Every compilation

Every runtime package

has provenance.

No anonymous graph objects are allowed.

---

# Design Principle

The repository is not document-centric.

The repository is graph-centric.

Markdown

JSON

YAML

FHIR

Python

are all projections of the same underlying graph.

The graph is the repository.
