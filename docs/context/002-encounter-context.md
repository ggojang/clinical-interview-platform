# Encounter Context

Version: 0.1 (Draft)

---

# Purpose

This document defines Encounter Context.

Encounter Context describes the environment in which the interview occurs.

Reason for Encounter alone is insufficient to determine interview behavior.

The same Reason for Encounter may require different Clinical Intents depending on the Encounter Context.

Encounter Context therefore precedes Clinical Intent generation.

---

# Relationship

Interview begins with

```
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

Question
```

Encounter Context modifies the interpretation of every subsequent step.

---

# Why Encounter Context Exists

Consider the Reason for Encounter

```
"I have a cough."
```

Scenario A

Primary Care

↓

Intent

- Characterize symptom
- Differentiate common causes
- Screen red flags

Scenario B

Pulmonology Follow-up

↓

Intent

- Evaluate treatment response
- Medication adherence
- Disease progression

Scenario C

Emergency Department

↓

Intent

- Immediate safety
- Emergency screening

Same patient statement.

Different interview.

---

# Encounter Context Components

Every encounter has contextual attributes.

## Care Setting

Examples

Primary Care

Emergency Department

Specialist Clinic

Telemedicine

Home Visit

Occupational Health

Health Check-up

Community Screening

---

## Encounter Type

Examples

New encounter

Follow-up

Annual review

Medication review

Preventive visit

Administrative visit

Vaccination

Referral consultation

---

## Interview Initiator

Examples

Patient

Caregiver

Clinician

Health System

Employer

School

Public Health Program

---

## Interview Mode

Examples

Face-to-face

Telephone

Video

Chat

Asynchronous questionnaire

AI-assisted interview

---

## Available Information

Examples

No previous records

Previous Clinical Memory

Medication history

Laboratory data

Referral letter

Health examination

FHIR Bundle

---

## Time Constraints

Examples

Emergency

Routine

Scheduled

Screening

Self-paced

---

## Clinical Responsibility

Examples

Independent assessment

Shared care

Referral support

Follow-up support

Decision support

Education

---

# Context Determines Intent

Encounter Context activates Clinical Intent.

Example

Encounter

```
Annual Health Check
```

Reason for Encounter

```
"I'm here for my health check."
```

Activated Intents

- Preventive Care
- Cancer Screening
- Vaccination Review
- Cardiovascular Risk Assessment

Presentation does not exist.

---

Example

Encounter

```
Primary Care
```

Reason for Encounter

```
"I've had chest pain."
```

Activated Intents

- Safety Assessment
- Symptom Characterization
- Common Cause Differentiation

---

# Context is Independent from Diagnosis

Encounter Context never contains diagnosis.

It only describes interview conditions.

---

# Context Metadata

Every Encounter Context contains

Identifier

Display Name

Description

Typical Care Setting

Typical Workflow

Supported Interview Modes

Default Clinical Intents

Default Priority Rules

Associated Coverage Domain

FHIR Mapping (optional)

SNOMED Mapping (optional)

Provenance

---

# Context Inheritance

Encounter Context may inherit properties.

Example

```
Primary Care

↓

Follow-up

↓

Medication Review
```

The child context inherits

- Care setting
- Available information

while adding

- Medication adherence
- Side effect assessment

---

# Context Priority

Context modifies

Intent Priority

Question Priority

Coverage Priority

Simulation Priority

Runtime Behavior

---

# Examples

## Primary Care

Characteristics

- Broad differential
- Common conditions first
- Prevention included
- Longitudinal care

Typical Intents

- Characterization
- Common Cause Differentiation
- Prevention
- Follow-up

---

## Emergency Department

Characteristics

- Safety first
- Limited time
- Immediate escalation

Typical Intents

- Red Flag Screening
- Severity Assessment
- Stabilization

---

## Health Check-up

Characteristics

- No presentation required
- Prevention
- Risk assessment

Typical Intents

- Screening
- Lifestyle
- Vaccination
- Family history

---

## Medication Review

Characteristics

- Existing diagnosis
- Existing medication

Typical Intents

- Reconciliation
- Adherence
- Side effects
- Drug interactions

---

# Encounter Context is Reusable

Encounter Context is reusable across all Reason for Encounter.

It should never be duplicated.

---

# Design Principles

Encounter Context

- exists before Clinical Intent
- is independent from diagnosis
- modifies interview behavior
- is reusable
- is measurable
- contributes to Coverage
- has provenance

Encounter Context is one of the core abstractions of the Clinical Interview Knowledge Platform.
