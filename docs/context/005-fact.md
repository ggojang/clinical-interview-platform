# Fact Model

Version: 0.1 (Draft)

---

# Purpose

Facts are the fundamental reusable knowledge units of the Clinical Interview Knowledge Platform.

Facts describe observable, reportable, measurable, or inferable clinical information.

Facts are independent of

- diagnoses
- presentations
- interview flow
- question wording

Facts are reusable across the entire repository.

---

# Fact Philosophy

Facts are repository assets.

Facts are never owned by

- Reason for Encounter
- Presentation
- Clinical Group
- Interview Target
- Question

Instead

those objects consume Facts.

---

# Knowledge Hierarchy

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

Clinical Memory

↓

FHIR

Facts are the bridge between interview and structured knowledge.

---

# Definition

A Fact represents one atomic clinical statement.

A Fact must satisfy all of the following.

• Clinically meaningful

• Independently reusable

• Machine identifiable

• Versioned

• Provenance-aware

• Simulation testable

---

# Atomic Facts

Good

symptom.duration

Good

symptom.fever.present

Good

patient.smoking.current

Bad

patient.history

Bad

respiratory_assessment

Bad

general_information

Facts should never bundle unrelated information.

---

# Fact Categories

The repository organizes Facts into reusable domains.

## Patient

Examples

patient.age

patient.sex

patient.language

patient.pregnancy

patient.height

patient.weight

---

## Symptoms

Examples

symptom.duration

symptom.onset

symptom.progression

symptom.severity

symptom.location

symptom.frequency

symptom.character

---

## Associated Symptoms

Examples

symptom.fever.present

symptom.dyspnea.present

symptom.hemoptysis.present

symptom.weight_loss.present

---

## Exposure

Examples

travel.history

occupation.exposure

animal.exposure

chemical.exposure

contact.history

---

## Medication

Examples

medication.current

medication.previous

medication.adherence

medication.side_effect

---

## Past Medical History

Examples

history.condition

history.operation

history.hospitalization

history.immunization

history.allergy

---

## Family History

Examples

family.cancer

family.cardiovascular

family.diabetes

family.genetic

---

## Social History

Examples

smoking.current

alcohol.use

exercise

occupation

living_alone

---

## Functional Status

Examples

adl.walking

adl.sleep

adl.eating

adl.work

adl.exercise

---

## Patient Perspective

Examples

patient.concern

patient.expectation

patient.goal

patient.additional_information

---

# Fact States

A Fact stored in Clinical Memory may exist in one of several states.

Known

Unknown

Not Asked

Declined

Contradictory

Not Applicable

Derived

Fact state is independent from Fact definition.

---

# Fact Value

Every Fact contains

Identifier

Value

Unit (optional)

Timestamp (optional)

Confidence

Evidence

Status

Provenance

---

# Fact Source

Facts may originate from

Patient

Caregiver

Clinician

Medical Record

FHIR Import

Simulation

Knowledge Rule

Derived Facts

Every origin must be preserved.

---

# Fact Evidence

Evidence is separate from value.

Example

Fact

```
symptom.duration = 3 days
```

Evidence

```
Patient

Turn 3

"I started coughing about three days ago."
```

Evidence is immutable.

---

# Fact Confidence

Facts may include confidence.

Confidence is assigned to extraction.

Not to patient truth.

Example

Patient

"I think maybe around three days."

Extraction confidence

0.82

The repository distinguishes

Patient uncertainty

↓

Extraction uncertainty

These are not equivalent.

---

# Fact Provenance

Every Fact requires provenance.

Minimum fields

Builder

Knowledge Package

Version

Medical Sources

Review Status

Creation Time

Update Time

---

# Fact Reuse

Facts are reused.

Example

symptom.duration

appears in

Cough

Headache

Chest Pain

Abdominal Pain

Fatigue

No duplicate Facts are permitted.

---

# Fact Relationships

Facts may reference other Facts.

Example

symptom.duration

↓

supports

↓

common_cause_differentiation

Fact relationships are stored in the Knowledge Graph.

Facts never embed other Facts.

---

# Fact Validation

Every Fact is validated.

Validation includes

Schema

Semantic consistency

Terminology mapping

Simulation

Coverage

Regression

Validation is mandatory.

---

# Fact Mapping

Facts may map to

SNOMED CT

FHIR

LOINC

ICPC-2

Mappings are optional metadata.

Mappings never define interview behavior.

---

# FHIR

Facts do not represent FHIR Resources.

Instead

Facts populate FHIR Resources.

Example

Facts

```
symptom.duration

symptom.severity

symptom.location
```

↓

FHIR Condition

onset

severity

bodySite

Facts remain independent.

---

# SNOMED CT

Facts are not SNOMED Concepts.

Facts may align with

Concepts

Attributes

Reference Sets

MRCM

SNOMED assists semantic alignment.

It never replaces Fact definitions.

---

# MRCM

MRCM is used during Knowledge Build.

MRCM may contribute

Allowed attributes

Attribute domains

Attribute ranges

Semantic consistency

Runtime never executes MRCM.

---

# Guideline Integration

Facts are not created directly from Guidelines.

Guidelines influence

Importance

Priority

Safety

Evidence

Builder compiles this information.

---

# Simulation

Every Fact requires simulation.

Simulation scenarios

Positive

Negative

Unknown

Declined

Contradictory

Derived

Facts without simulation are incomplete.

---

# Coverage

Coverage includes

Fact definition

Fact validation

Fact mapping

Fact simulation

Fact provenance

Fact reuse

Coverage is measured separately.

---

# Design Rules

Facts

must be atomic.

must be reusable.

must be versioned.

must have provenance.

must be simulation tested.

must not contain interview logic.

must not contain diagnosis logic.

must not contain question wording.

---

# Final Principle

Facts are the smallest reusable semantic units of the Clinical Interview Knowledge Platform.

Questions collect Facts.

Interview Targets require Facts.

Clinical Memory stores Facts.

Knowledge Graph connects Facts.

FHIR exports Facts.

Facts are never owned by any single Presentation.
