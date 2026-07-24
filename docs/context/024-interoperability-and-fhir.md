# Interoperability and FHIR

Version: 0.1 (Draft)

---

# Purpose

This document defines interoperability boundaries.

FHIR, SNOMED CT, LOINC and ICPC-2 support exchange, terminology alignment and indexing.

They do not define internal interview semantics.

---

# Core Principle

Internal semantics first.

External mappings second.

Runtime behavior is never controlled by an interoperability format.

---

# Layering

```text
Repository Fact
        ↓
Semantic Mapping
        ↓
Compiled Mapping Package
        ↓
Clinical Memory
        ↓
FHIR Projection
```

FHIR Export is a projection of Clinical Memory.

---

# SNOMED CT

SNOMED CT may provide

- terminology identity
- hierarchy
- synonyms
- concept relationships
- semantic constraints
- reference sets

SNOMED CT does not determine

- Clinical Intent
- Question priority
- Runtime safety behavior
- completion

Terminology version and licensing are recorded.

---

# MRCM

MRCM supports semantic alignment and permissible attribute modeling.

MRCM is a Build-Time source.

Runtime never queries MRCM.

MRCM constraints do not replace repository validation.

---

# LOINC

LOINC may align observable Facts and structured measurements.

LOINC mapping includes

- code
- system
- version
- property
- scale
- method when applicable
- confidence
- provenance

For questionnaire projection, a verified LOINC code is the preferred external
code for an observable or assessment question. SNOMED CT is the secondary
question semantic when an appropriate observable or related clinical concept
is verified. Every question also retains a stable local code. Composite
questions do not receive an atomic LOINC code as an exact mapping and enter an
explicit atomic-refactoring queue. Exact or equivalent standard mapping is
permitted only after the question is verified to collect one answer-bearing
clinical data element.

Clinical coded answers prefer verified SNOMED CT concepts and otherwise use a
context-qualified local answer code. Reusable answer choices are published as
FHIR R4 ValueSets: `a-sct-*`, `a-loinc-*`, `a-local-*`, or `a-mixed-*`.
Partially mapped choices use a complete mixed ValueSet rather than an incomplete
SNOMED-only list. Numeric, date, narrative and UCUM quantity values are not
forced into artificial answer codes.

The generic SNOMED-first answer rule does not override a binding on the actual
target FHIR R4 element. A Build-Time registry generated from the official R4
base StructureDefinitions records required, extensible, preferred and example
bindings for all base resources. An exact or equivalent Fact-to-element mapping
activates the official canonical as the effective
`Questionnaire.item.answerValueSet`; candidate, partial and related mappings
remain annotations only. Required bindings use closed `choice`. Extensible,
preferred and example bindings use `open-choice` unless a verified profile
requires a narrower shape. The compiled package preserves the generic
SNOMED/local ValueSet as fallback metadata, and Runtime never downloads the
FHIR specification or a terminology expansion.

`history.family.relationship` is the initial active example. It maps to
`FamilyMemberHistory.relationship`, uses
`http://terminology.hl7.org/ValueSet/v3-FamilyMember`, and records prepared
answers with the HL7 v3 RoleCode system. The existing narrative family-history
Fact remains available for multiple conditions and details; the relationship
question is atomic and repeatable for future FamilyMemberHistory projection.

Official LOINC LL Answer Lists are reference ValueSets, not project-generated
`a-loinc-*` resources. They retain `http://loinc.org/vs/{LL-code}` and are
bound directly through `Questionnaire.item.answerValueSet` when applicable.
The `a-loinc-*` namespace is used only for project-owned LOINC-coded sets that
are not official LL lists.

Source-defined fixed questionnaires are excluded from automatic mapping. Their
official wording and answer lists remain authoritative unless an explicit
mapping request is verified against the source instrument.

Mapping search checks official LOINC panels and Answer Lists, HL7 FHIR and US
Core artifacts, NLM VSAC where access and licensing permit, SNOMED CT
implementation artifacts, and STOM before a new local code is accepted.

STOM FHIR R4 ValueSet services are used at Build Time. The initial primary
endpoint is `http://localhost:8088/fhir`; the remote fallback is
`https://stom.infoclinic.co/fhir`. External standard ValueSets are resolved by
canonical URL and optional version, expanded with `ValueSet/$expand`, and
candidate coded answers are checked with `ValueSet/$validate-code`.

The complete official LL collection exposed by STOM is indexed in
`sources/catalogs/loinc-answer-lists-stom.json`. Each entry preserves its LL
identifier, official canonical, display, observed member count and resolution
mode. STOM dynamically expands every indexed canonical, so the platform does
not create duplicate persisted ValueSet resources. The complete catalog and
all individual canonicals are audited at Build Time; only the selected
Answer Lists are referenced by a Questionnaire or compiled package.

The STOM aggregate LL resource and LOINC CodeSystem may report different
release versions. Both observed versions remain in provenance and the
difference is a visible quality warning. It is never normalized away or used
to claim false release alignment.

Project-owned `a-sct-*`, `a-loinc-*`, `a-local-*`, and `a-mixed-*` ValueSets are
generated and validated in the repository. They are not assumed to exist on
STOM and are never silently uploaded. Server registration is a separate,
explicitly invoked deployment action using `TERM_ADMIN_TOKEN` as an
`X-API-Key`. Publication first checks canonical duplicates and resource-id
collisions. An existing identical canonical/version is reused without a write,
and an existing canonical/version with different membership is rejected. The
reconciliation publisher only creates absent ValueSets and never updates an
existing ValueSet. It verifies the returned canonical after creation. A
terminology-server failure cannot block an interview or change a clinical
safety decision.

Reference ValueSets are reconciled before creation. The Builder first checks
canonical URL and version, then compares an order- and display-insensitive
fingerprint of `compose` or a materialized `expansion`. An identical existing
ValueSet with the same canonical/version is reused. Matching membership under a
different canonical is reported as a duplicate-content candidate, but never
substituted because canonical identity is semantically significant. If the
requested canonical/version is absent, the reference ValueSet is published
without semantic modification. A canonical/version collision with different
membership is an error and is never overwritten.

An application-specific extension never edits the reference. It creates a
separate `a-extended-*` ValueSet whose first `compose.include.valueSet` imports
the versioned reference canonical and whose remaining includes contain only
needed, individually verified additional codes. Every additional code records
its verification source; local codes require an explicit exception. Dynamic
extensible items project as FHIR R4 `open-choice`. Required closed items and
source-defined instruments remain `choice` and retain their official answer
sets.

The complete policy is defined in
`policies/question-answer-terminology-binding.json` and
`policies/fhir-valueset-service.json`.

---

# ICPC-2

ICPC-2 is a pragmatic Primary Care classification and indexing system.

It may classify

- Reason for Encounter
- Problem
- process of care
- coverage domains

ICPC-2 does not define internal Fact or Intent semantics.

---

# FHIR

FHIR provides exchange structure.

Potential resources include

- Questionnaire
- QuestionnaireResponse
- Observation
- Condition
- MedicationStatement
- AllergyIntolerance
- FamilyMemberHistory
- Encounter
- Provenance
- Bundle

Resource selection depends on mapping policy.

---

# FHIR Baseline

Every mapping package declares

- FHIR version
- profiles
- extensions
- ValueSets
- CodeSystems
- ConceptMaps
- validation tooling
- jurisdiction

The baseline is immutable within a package release.

---

# Mapping Object

Every mapping contains

- internal object identifier
- external system
- external identifier or path
- mapping relation
- confidence
- conditions
- version
- review status
- provenance

Mapping relations distinguish

- equivalent
- narrower
- broader
- related
- no map

---

# Export Rules

Export must

- preserve internal identifier
- preserve evidence linkage
- preserve assertion and uncertainty
- preserve encounter identity
- identify mapping version
- identify package version
- include provenance where supported
- validate against declared profile

Export must not

- convert a Hypothesis to confirmed Condition
- omit clinically relevant uncertainty
- infer absent data
- overwrite internal Clinical Memory
- silently drop mapping failures

When an expected value is missing, export preserves Clinical Memory's
`dataAbsentReason` using the FHIR DataAbsentReason code system. A coded absent
reason and a populated value are mutually exclusive. `asked-unknown` and
`asked-declined` must never be converted into `false`.

---

# Import Rules

Imported FHIR data is source evidence.

It is not automatically accepted as current patient truth.

Import records

- Resource identity
- source system
- authored time
- encounter
- status
- coding
- mapping result
- provenance

Applicability and freshness are evaluated.

---

# STOM

STOM is a Build-Time terminology provider.

Runtime never communicates with STOM.

Acquired terminology content is cached, versioned and licensed before use.

The ValueSet adapter is GET-only and supports capability discovery, canonical
search, expansion and code validation. Although the server may advertise
create, update and delete interactions, those interactions are outside this
adapter's authority.

---

# Validation

Interoperability validation includes

- identifier resolution
- code validity
- ValueSet binding
- profile validation
- mapping relation
- version compatibility
- round-trip semantic checks
- provenance completeness

Structural FHIR validity is not clinical validation.

---

# Mapping Evolution

A mapping change may occur without changing internal Fact identity.

Mapping changes create

- new mapping version
- new package version
- migration note
- regression result

Internal semantics change only through the normal Knowledge Graph process.

---

# Final Principle

FHIR is an interoperability representation.

Terminologies are alignment sources.

The Knowledge Graph remains the canonical internal representation.
