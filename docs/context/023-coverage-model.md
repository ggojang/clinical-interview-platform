# Coverage Model

Version: 0.1 (Draft)

---

# Purpose

This document defines Coverage.

Coverage measures repository completeness.

Coverage determines development progress.

---

# Core Principle

Progress is not measured by file count.

Progress is measured by connected, validated and simulated knowledge.

---

# Coverage Dimensions

Coverage includes

- Encounter Context
- Reason for Encounter
- Clinical Intent
- Interview Target
- Fact
- Question Template
- Rule
- Simulation
- mapping
- language
- mode
- provenance
- review status

---

# Coverage Unit

A covered unit is not merely present.

It must be

- uniquely identified
- semantically defined
- connected to required graph objects
- validated
- provenance-complete
- simulated
- included in a package
- evaluated

Presence without connectivity is inventory.

Not Coverage.

---

# Coverage Chain

The primary chain is

```text
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
        ↓
Simulation
```

A broken link reduces Coverage.

---

# Primary Care Coverage

Primary Care Coverage grows by Reason for Encounter and Encounter Context.

Coverage expansion proceeds across domains before deep specialization.

Examples

- respiratory
- cardiovascular
- gastrointestinal
- neurological
- musculoskeletal
- dermatological
- genitourinary
- mental health
- preventive care
- administrative care

---

# Coverage Levels

Suggested levels

## Defined

The semantic object exists.

## Connected

Required graph relationships exist.

## Validated

Schema and semantic validation pass.

## Simulated

Required Simulation exists and passes.

## Reviewed

Required human review is complete.

## Packaged

The object is present in a released Knowledge Package.

## Evaluated

Release metrics meet threshold.

Coverage reports distinguish each level.

---

# Safety Coverage

Safety Coverage measures

- relevant safety rules
- positive cases
- negative cases
- ambiguous cases
- escalation actions
- wording review
- jurisdiction review
- Runtime support

Safety Coverage is never averaged away.

---

# Fact Coverage

Fact Coverage includes

- value model
- extraction cues
- Interview Target links
- Question Templates
- mappings
- provenance
- simulation
- languages
- contexts

---

# Intent Coverage

Intent Coverage includes

- activation rules
- priority rules
- Targets
- completion rules
- context variations
- simulation
- review

---

# Question Coverage

Question Coverage includes

- Fact coverage
- language
- interview mode
- reading level
- neutral wording
- response type
- safety review
- simulation

---

# Mapping Coverage

Mapping Coverage reports

- mapped Facts
- unmapped Facts
- mapping confidence
- terminology baseline
- FHIR profile coverage
- validation status

Mapping gaps do not invalidate internal semantics.

They remain visible limitations.

---

# Weighted Coverage

Coverage may use weights.

High-impact units may receive greater weight.

Examples

- common RFE
- high-risk safety Target
- frequently reused Fact
- required preventive Intent

Weights must be explicit, versioned and provenance-linked.

---

# Coverage Calculation

Coverage is computed from graph connectivity and validation artifacts.

Manual estimates are prohibited.

A report identifies

- numerator
- denominator
- inclusion criteria
- exclusions
- weighting
- package version
- calculation version

---

# Coverage Gaps

Every gap is typed.

Examples

- missing semantic definition
- missing edge
- missing Question
- missing Simulation
- missing mapping
- unreviewed safety content
- failed evaluation
- unsupported language
- unsupported context

Gaps drive Builder work.

---

# Coverage and Roadmap

Roadmap priority considers

- Coverage gap
- Primary Care prevalence
- safety impact
- reuse potential
- evidence availability
- implementation cost
- review capacity

Coverage is the planning interface of the Knowledge Factory.

---

# Final Principle

Coverage is computed proof of repository completeness.

The repository advances only when connected knowledge passes its gates.
