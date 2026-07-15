# USCDI Interoperability Overlay

Version: 0.1 (Draft)

---

# Purpose

This document defines how USCDI and USCDI+ contribute to the Clinical Interview Knowledge Platform.

USCDI and USCDI+ are interoperability Coverage frameworks.

They are not clinical interview guidelines.

They do not determine which questions are clinically necessary.

They do not create Safety Rules.

They do not replace Korean terminology, reimbursement, consent, privacy, or reporting requirements.

---

# Relationship

```text
Clinical Guideline and Textbook
        ↓
Clinical Intent and Interview Target
        ↓
Fact and Question
        ↓
USCDI / USCDI+ Interoperability Overlay
        ↓
FHIR R4, openEHR or other export projection
```

Clinical evidence determines what should be collected.

The interoperability overlay measures what the collected Facts can populate.

FHIR and openEHR determine how the result may be projected.

---

# Core Principle

USCDI Coverage must never become interview completion authority.

An unmapped USCDI element does not automatically create a patient question.

A question may be added only when Encounter Context, Clinical Intent, clinical evidence and patient safety justify collecting the Fact.

Record-only, provider-authored and system-generated elements remain outside the patient interview unless an independent clinical reason exists.

---

# Baseline

The current research baseline is USCDI Version 6.

The baseline is versioned and jurisdiction-limited to the United States.

Draft USCDI versions may be monitored as candidates but are not binding mappings.

USCDI+ domain maturity is preserved explicitly.

Examples include

- published data element list
- pilot-validated use case
- official domain program
- use-case development

---

# Jurisdiction Boundary

The platform deployment context is Korean primary care.

Primary semantic and operational bindings remain

- SNOMED CT International through STOM
- LOINC
- KCD-8/9
- HIRA EDI
- Korean consent, privacy and reporting policy

US-specific vocabularies, profiles and regulatory requirements are crosswalk candidates only unless a separate United States deployment profile is activated.

USCDI Coverage is not a certification claim.

---

# Mapping Model

Every mapping preserves

- framework
- framework version
- data class
- data element
- jurisdiction
- collection role
- mapping status
- matched Fact identifiers
- limitations
- provenance

Mapping status is one of

- exact
- partial
- broader
- narrower
- contextual
- unmapped
- not_patient_collectable

Collection role is one of

- patient_collectable
- patient_or_record
- record_or_provider
- output_generated

---

# Coverage

USCDI Coverage is calculated for every compiled Knowledge Package.

Coverage reports

- eligible patient-collectable elements
- mapped elements
- exact mappings
- unmapped elements
- elements that must not be collected from the patient solely for interoperability
- applicable USCDI+ domains
- supported and unsupported domain elements

Coverage is a gap-discovery metric.

It is not a clinical completeness score.

It is not a production readiness score.

---

# USCDI+ Domains

Initial domain overlays are

## Maternal Health

Applied to pregnancy and postpartum encounters.

It assesses pregnancy timing, obstetric history, delivery, antenatal results, hypertension and diabetes, lactation, postpartum mental health and social context.

## Quality

Applied across implemented Reasons for Encounter.

It assesses patient goals, functional impact, pain measurement when applicable, information source and explicit missing-data representation.

## Behavioral Health

Applied to mental-health, sleep, pregnancy and postpartum contexts where relevant.

It assesses symptoms, suicide safety, substance context, treatment, function and support.

## Public Health

Applied to selected infectious and respiratory presentations.

It assesses symptom onset, exposure, immunization and laboratory context without creating public-health reporting claims.

---

# dataAbsentReason

USCDI mapping never converts missing information into a negative clinical statement.

Unknown, declined, not applicable and not asked remain distinct.

The information source remains explicit.

Coverage may recognize the Runtime capability to preserve `dataAbsentReason`, but it must not count missing clinical content as known content.

---

# Source and Refresh

USCDI and USCDI+ official sources have independent provenance and refresh metadata.

The default monitoring interval is seven days.

A detected source change triggers

1. version comparison;
2. mapping impact analysis;
3. Coverage recomputation;
4. affected package simulation;
5. review of jurisdiction and terminology implications.

It does not directly change Runtime behavior.

---

# Design Principles

USCDI and USCDI+

- extend interoperability assessment;
- do not control clinical questions;
- do not control Safety Rules;
- do not control completion;
- preserve jurisdiction;
- preserve domain maturity;
- preserve provenance;
- identify but do not silently fill gaps;
- distinguish patient-collectable from record-only information;
- remain `unreviewed/research_only` until reviewed.

USCDI is a Coverage lens over Facts, not a replacement for the Clinical Interview Knowledge Graph.
