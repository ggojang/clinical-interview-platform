# Computable Knowledge Standards Overlay

Version: 0.1 (Draft)

---

# Purpose

This document defines how Australian FHIR artifacts, openEHR clinical models
and HL7 or openEHR computable-rule standards support the Clinical Interview
Knowledge Factory.

These artifacts are Build-Time references. They do not replace the Knowledge
Graph, Rule Graph, Clinical Memory or compiled Knowledge Package. They do not
independently create questions, change priority, trigger safety, declare
completion, infer diagnosis or generate an order.

All resulting candidates remain `unreviewed/research_only`.

---

# Core Boundary

```text
Official External Artifact
        ↓
Acquisition, Version and License Check
        ↓
Structural or Semantic Crosswalk
        ↓
Internal Knowledge Graph and Rule Graph
        ↓
Simulation and Semantic-Diff Validation
        ↓
Compiled Knowledge Package
        ↓
Runtime
```

Runtime never downloads, compiles or interprets AU Base, AU Core, AUCDI,
openEHR archetypes or templates, CQL, ELM, PlanDefinition, ActivityDefinition,
CDS Hooks or GDL2.

Rule Graph remains the behavior source of truth.

---

# Korean Deployment Precedence

Interoperability is applied in this order:

1. internal Fact and Rule identity;
2. FHIR R4;
3. explicitly selected KR Core V2 profile;
4. verified international terminology binding;
5. verified foreign structural reference;
6. stable local fallback.

Australian jurisdictional identifiers, Medicare rules, PBS rules, AMT codes
and Australia-specific clinical workflows do not become Korean Runtime
behavior.

---

# AU Base, Sparked AUCDI and AU Core

AU Base provides reusable Australian FHIR R4 constraints. AUCDI provides a
data-group and data-element reference. AU Core provides an FHIR R4 projection
of Australian core exchange requirements.

The Builder may use them to compare Fact shape, datatype, provenance,
cardinality, terminology, clinician handoff Coverage and FHIR paths.

An Australian reference gap is an interoperability Coverage gap. It is not, by
itself, a reason to ask the patient another question. AU Base is not a
standalone Korean conformance target, AU Core does not replace KR Core V2, and
Australian regulatory assumptions are not imported.

---

# Australian Smart Forms

Australian Smart Health Checks and Smart Forms may inform FHIR Questionnaire,
QuestionnaireResponse, Structured Data Capture, prepopulation, `enableWhen`,
repeatable groups and extraction patterns.

Continuous-integration artifacts are non-binding research references.
Australian fixed wording, Indigenous-specific content, Medicare-specific
content and Australian terminology bindings are not imported automatically.
Source-defined fixed questionnaires remain outside automatic dynamic mapping.

---

# openEHR CKM, Archetypes and Templates

An openEHR archetype may help test the structure of a reusable clinical
concept. A template may help test use-case assembly and optionality. An
Operational Template is a useful analogy for a flattened Build-Time artifact.

Every template field must be classified before it affects collection:

- patient askable;
- clinician observed;
- derived;
- record prepopulated.

A required template field does not automatically become a required patient
question.

openEHR `at` and `ac` codes are local model identifiers. They are not LOINC,
SNOMED CT or other external terminology mappings. Every CKM artifact requires
lifecycle, version, namespace, license and embedded terminology-license
verification before content is cached or transformed.

---

# HL7 CPG, CQL and FHIR Clinical Reasoning

The HL7 Clinical Practice Guidelines Implementation Guide is a knowledge
engineering reference. It may inform artifact identity, dependency, expression,
action, evidence, provenance and packaging, but does not make a guideline
clinically applicable.

CQL is the preferred future standards projection for reviewed logical
expressions. ELM is its machine-oriented representation. A future projection
must preserve absent-data semantics, time boundaries, terminology versions,
priority, suppression, conflict and stop behavior, and must pass bidirectional
semantic-diff and named engine-conformance tests.

FHIR R4 resources have prospective roles:

| Internal object | FHIR projection |
|---|---|
| reviewed expression library | `Library` |
| coordinated action or decision structure | `PlanDefinition` |
| atomic definitional activity | `ActivityDefinition` |
| interview instrument | `Questionnaire` |
| completed interview | `QuestionnaireResponse` |

`PlanDefinition` and `ActivityDefinition` are definitions. Their presence does
not mean an action was ordered, recommended for a particular patient or
performed. Interview packages cannot create clinical orders.

The current package records projection readiness only. It emits and executes
none of these artifacts.

---

# CDS Hooks

CDS Hooks is an optional future external clinical-workflow adapter. It is not
the internal rule language, a Runtime dependency, a source of interview safety
or a substitute for a compiled package.

If an external CDS Hooks service is unavailable, the interview continues with
the locally compiled package and safety behavior is unchanged.

---

# openEHR GDL2

GDL2 may represent preconditions, `when` conditions, actions, terminology
bindings, output templates and test fixtures. It is useful as a secondary
research cross-validation model.

It is not the primary projection because its specification status is trial, no
repository GDL2 engine is qualified and no semantic-equivalence suite has been
completed. No GDL2 guide is emitted or executed in the current phase.

---

# Rule Projection Crosswalk

The reference registry covers every allowed Rule Graph type:

- activation and applicability become Boolean applicability expressions;
- requirement and completion become missing-data and completion expressions;
- priority becomes ordinal derivation and action priority;
- suppression and conflict become explicit exclusion or contradiction logic;
- safety becomes advisory logic without order authority;
- transition becomes related-action or state-transition structure;
- stop becomes an explicit terminal condition;
- mapping becomes a derived transform or output binding.

This crosswalk is metadata, not executable output.

---

# Simulation and Release Gates

Simulation covers Australian gaps that do not create questions, KR Core V2
precedence, CI-build boundaries, non-patient-askable template nodes, local
archetype codes, CQL or GDL semantic mismatch, `dataAbsentReason`,
definition-versus-order distinction, CDS Hooks outage, fixed questionnaire
exclusion and unresolved licenses.

A projection mismatch blocks the projection. It does not weaken the internal
clinical rule.

The current implementation provides a source manifest, reference registry,
authority policy, package readiness metadata, validators and synthetic
regression cases. It does not provide executable CQL/ELM or GDL2, released FHIR
Clinical Reasoning artifacts, CDS Hooks Runtime integration, AU Core
conformance, imported CKM clinical content or production-reviewed computable
clinical knowledge.
