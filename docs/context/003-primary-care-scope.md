# Primary Care Scope

Version: 0.1 (Draft)

---

# Purpose

This document defines the scope of the Clinical Interview Knowledge Platform.

The objective is not to enumerate diseases.

The objective is to define the Primary Care interview universe.

Knowledge acquisition, coverage calculation, simulation generation,
and Runtime compilation all begin from this scope.

This scope defines what the repository intends to support.

Anything outside this scope is explicitly out of scope until introduced
through a new version.

---

# Scope Philosophy

Primary Care does not begin with diagnoses.

Primary Care begins with people seeking care.

Therefore the repository does not start from diseases.

The repository starts from encounters.

---

# Bootstrap Model

Knowledge Builder begins with

```
Encounter Context

+

Reason for Encounter

↓

Clinical Intent

↓

Interview Target

↓

Fact

↓

Question

↓

Simulation

↓

Compiled Knowledge
```

Neither Presentation nor Diagnosis is the primary entry point.

---

# Primary Care Coverage

Coverage is organized into Domains.

Each Domain contains multiple Reasons for Encounter.

Each Reason for Encounter activates one or more Clinical Intents.

Coverage is measured across all three dimensions.

---

# Domain Structure

The initial bootstrap covers the following domains.

## Respiratory

Examples

- cough
- dyspnea
- sore throat
- nasal symptoms
- fever
- wheezing

---

## Cardiovascular

Examples

- chest pain
- palpitations
- syncope
- hypertension follow-up
- edema

---

## Gastrointestinal

Examples

- abdominal pain
- nausea
- vomiting
- diarrhea
- constipation
- reflux symptoms
- rectal bleeding

---

## Neurological

Examples

- headache
- dizziness
- weakness
- numbness
- tremor

---

## Musculoskeletal

Examples

- back pain
- neck pain
- shoulder pain
- joint pain
- limb injury

---

## Dermatology

Examples

- rash
- itching
- skin lesion
- wound
- insect bite

---

## Genitourinary

Examples

- dysuria
- urinary frequency
- hematuria
- vaginal symptoms
- testicular symptoms

---

## Mental Health

Examples

- anxiety
- depression
- insomnia
- stress
- memory concern

---

## General

Examples

- fatigue
- weight loss
- weight gain
- night sweats
- generalized weakness

---

## Preventive Care

Examples

- vaccination
- cancer screening
- cardiovascular risk review
- smoking cessation
- alcohol counselling
- lifestyle review

---

## Medication

Examples

- medication refill
- medication review
- adverse effect
- adherence review
- interaction concern

---

## Administrative

Examples

- certificate
- referral
- health examination
- insurance form
- occupational assessment

---

# Encounter Matrix

Coverage is defined by the matrix

```
Encounter Context

×

Reason for Encounter

↓

Clinical Intent
```

Example

| Context | RFE | Intent |
|----------|-----|--------|
| Primary Care | cough | Characterize Symptom |
| Primary Care | cough | Red Flag Screening |
| Primary Care | cough | Common Cause Differentiation |
| Follow-up | cough | Response Assessment |
| Health Check | none | Preventive Care |

This matrix is the primary source for Interview generation.

---

# Presentation

Presentation is optional.

Some encounters have presentations.

Examples

- cough
- chest pain
- headache

Others do not.

Examples

- vaccination
- medication review
- annual health check
- smoking cessation

Presentation is therefore a secondary abstraction.

---

# Problem

Problems are independent from Reason for Encounter.

Reason for Encounter represents why care is sought.

Problem represents what becomes clinically relevant during care.

The repository keeps both.

Reason for Encounter

↓

Clinical Interview

↓

Problem Candidates

↓

Reviewed Problems

Problem generation is outside Version 0.1 Runtime.

---

# ICPC-2

ICPC-2 is used as a pragmatic Primary Care classification.

Its purposes include

- Coverage planning
- Coverage measurement
- Initial indexing
- Navigation

ICPC-2 does not define repository semantics.

The repository semantics are independent.

---

# SNOMED CT

SNOMED CT provides

- terminology alignment
- concept hierarchy
- semantic relationships
- terminology mapping

SNOMED CT does not define interview behavior.

---

# FHIR

FHIR provides interoperability.

FHIR Resources are generated after interview.

FHIR Resources do not define interview flow.

---

# Guideline Integration

Clinical Guidelines influence

- Clinical Intent
- Interview Target
- Safety Priority
- Follow-up Recommendation

Examples

NICE

CHEST

ERS

GINA

GOLD

CDC

USPSTF

Guidelines do not directly generate questions.

Knowledge Builder compiles guidance into Interview Knowledge.

---

# Coverage Levels

Coverage is measured separately.

## Domain Coverage

How many Primary Care domains exist.

---

## Encounter Coverage

How many Encounter Contexts are supported.

---

## Reason for Encounter Coverage

How many RFEs are supported.

---

## Clinical Intent Coverage

How many reusable intents exist.

---

## Interview Target Coverage

How many Interview Targets exist.

---

## Fact Coverage

How many reusable facts exist.

---

## Question Coverage

How many reusable question templates exist.

---

## Simulation Coverage

How many simulation scenarios exist.

---

# Bootstrap Strategy

Bootstrap proceeds incrementally.

Batch 1

Respiratory

General

Medication

Batch 2

Cardiovascular

Gastrointestinal

Batch 3

Neurological

Musculoskeletal

Batch 4

Dermatology

Mental Health

Genitourinary

Administrative

Each batch must complete

Coverage

Simulation

Evaluation

Compilation

before proceeding.

---

# Growth Principle

Repository growth is horizontal before vertical.

Support many Reasons for Encounter first.

Increase diagnostic depth later.

Primary Care breadth is prioritized over specialty depth.

---

# Immutable Principle

The repository grows according to Primary Care Coverage.

Not according to disease count.

Not according to file count.

Coverage determines progress.
