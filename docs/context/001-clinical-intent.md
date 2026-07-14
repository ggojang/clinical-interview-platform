# Clinical Intent

Version: 0.1 (Draft)

---

# Purpose

This document defines the concept of Clinical Intent.

Clinical Intent is one of the core concepts of the Clinical Interview Knowledge Platform.

Clinical Intent determines **why** the interview asks questions.

Clinical Intent does **not** represent a diagnosis.

Clinical Intent does **not** represent a disease.

Clinical Intent represents the immediate clinical objective that should be satisfied during the interview.

---

# Why Clinical Intent Exists

Traditional interview systems often generate questions directly from diagnoses.

Example

```
Cough

↓

Pneumonia

↓

Questions
```

This repository intentionally rejects that model.

Diagnosis should never be the primary driver of questioning.

Instead

```
Reason for Encounter

↓

Clinical Intent

↓

Interview Target

↓

Question
```

The interview attempts to satisfy one or more Clinical Intents.

Only after enough evidence exists may hypotheses become stronger.

---

# Relationship with Reason for Encounter

Reason for Encounter (RFE) is supplied by the patient.

Examples

"I've been coughing."

"I need a health check."

"I need a vaccination."

"My blood pressure medication is not working."

"I'm worried about my father having colon cancer."

Clinical Intent is derived from the Reason for Encounter.

The same RFE may activate multiple Clinical Intents.

Example

Reason for Encounter

```
"I've been coughing."
```

Possible Clinical Intents

- Characterize symptom
- Identify common causes
- Screen for red flags
- Assess severity
- Determine urgency
- Review risk factors

---

# Clinical Intent is Dynamic

Clinical Intent changes during the interview.

New patient information may

- activate new intents
- satisfy existing intents
- remove unnecessary intents
- change priority

Example

Initial Intent

```
Common Cause Differentiation
```

Patient later reports

```
Hemoptysis
```

Immediately

```
Red Flag Screening
```

becomes highest priority.

Clinical Intent is continuously re-evaluated.

---

# Intent is Independent from Diagnosis

The same diagnosis may require different Clinical Intents.

Example

Asthma

Scenario A

Routine follow-up

Intent

- Medication review
- Symptom control

Scenario B

Acute dyspnea

Intent

- Severity assessment
- Emergency screening

Same diagnosis

Different Clinical Intent.

Likewise

One Clinical Intent may relate to many diagnoses.

Example

```
Assess fever
```

may contribute to

- Common cold
- Influenza
- COVID
- Pneumonia
- Urinary infection
- Appendicitis

Clinical Intent is diagnosis-independent.

---

# Categories of Clinical Intent

The repository organizes Clinical Intent into reusable categories.

## Safety

Purpose

Determine whether immediate intervention or escalation is required.

Examples

- Red flag screening
- Emergency assessment
- Severity assessment

---

## Characterization

Purpose

Understand the presenting concern.

Examples

- Onset
- Duration
- Severity
- Progression
- Associated symptoms

---

## Differentiation

Purpose

Distinguish between common clinical groups.

Examples

Upper airway

↓

Lower airway

↓

Reflux-related

↓

Medication-related

This is **not** diagnosis.

This is interview differentiation.

---

## Risk Assessment

Purpose

Identify factors influencing probability or management.

Examples

Smoking

Occupation

Travel

Exposure

Family history

Medication

Vaccination

---

## Past Medical Context

Purpose

Collect information relevant to current assessment.

Examples

Past diseases

Operations

Pregnancy

Allergy

Medication

Previous episodes

---

## Functional Assessment

Purpose

Understand impact on daily life.

Examples

Exercise tolerance

Sleep disturbance

Eating

Walking

Work

School

Activities of daily living

---

## Preventive Care

Purpose

Support health maintenance.

Examples

Vaccination

Cancer screening

Lifestyle

Smoking cessation

Alcohol

Weight

Exercise

---

## Follow-up

Purpose

Determine evolution after previous encounter.

Examples

Improved

Worse

No change

Medication adherence

Side effects

---

## Shared Decision Support

Purpose

Collect information required for collaborative planning.

Examples

Patient preference

Concerns

Goals

Ability to follow treatment

Support system

---

# Clinical Intent Lifecycle

Each Clinical Intent has a lifecycle.

```
Inactive

↓

Activated

↓

Prioritized

↓

Interview Target Generated

↓

Satisfied

↓

Closed
```

Closed intents remain in Clinical Memory.

---

# Clinical Intent Priority

Every active intent has a priority.

Priority is dynamic.

Priority is influenced by

Safety

↓

Urgency

↓

Information gain

↓

Missing information

↓

Interview burden

↓

Redundancy

The highest-priority intent determines the next interview target.

---

# Intent does not generate Questions directly

Clinical Intent

↓

Interview Target

↓

Fact

↓

Question

Questions are generated from missing Interview Targets.

Never directly from diagnoses.

---

# Intent Graph

Clinical Intents form a graph.

They are not isolated objects.

Example

```
Characterize Symptom

↓

Common Cause Differentiation

↓

Risk Assessment

↓

Follow-up Planning
```

Another example

```
Medication Review

↓

Side Effect Assessment

↓

Adherence Assessment
```

The graph evolves during Runtime.

---

# Intent and Coverage

Coverage is measured partly by Clinical Intent.

Repository completeness requires

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

Each level must be measurable.

---

# Clinical Intent Metadata

Every Clinical Intent contains

Identifier

Name

Description

Priority Rules

Activation Rules

Completion Rules

Associated Interview Targets

Associated Safety Rules

Associated Presentations (optional)

Associated Clinical Groups (optional)

FHIR Mapping (optional)

SNOMED Mapping (optional)

ICPC Reference (optional)

Provenance

---

# Clinical Intent is not Classification

Clinical Intent is an operational concept.

It is not

- SNOMED CT
- ICPC-2
- ICD
- FHIR

Those systems may reference or support Clinical Intent.

They do not define it.

---

# Examples

## Cough

Reason for Encounter

```
"I've had a cough."
```

Possible Intents

- Characterize symptom
- Identify common causes
- Assess severity
- Screen red flags
- Assess smoking history
- Review medication exposure

---

## Vaccination

Reason for Encounter

```
"I need a flu vaccine."
```

Possible Intents

- Vaccination eligibility
- Allergy review
- Contraindication assessment
- Previous vaccination history

---

## Medication Review

Reason for Encounter

```
"My medication is not helping."
```

Possible Intents

- Medication reconciliation
- Adherence assessment
- Side effect assessment
- Disease progression assessment

---

# Design Principles

Clinical Intent

- is reusable
- is measurable
- is diagnosis-independent
- evolves during interview
- determines Interview Targets
- never directly determines diagnosis
- exists before Question Generation

Clinical Intent is one of the fundamental abstractions of the Clinical Interview Knowledge Platform.
