# Versioning and Release

Version: 0.1 (Draft)

---

# Purpose

This document defines versioning and release.

Every source, graph object, rule, package, simulation, evaluation and Runtime artifact is versioned.

---

# Version Layers

The platform distinguishes

- Source Version
- Normalization Version
- Semantic Alignment Version
- Knowledge Graph Version
- Rule Graph Version
- Simulation Version
- Coverage Version
- Mapping Version
- Compiler Version
- Knowledge Package Version
- Runtime Version
- Clinical Memory Schema Version

These versions must not be collapsed into one number.

---

# Semantic Versioning

Where applicable

- major: breaking semantic or compatibility change
- minor: backward-compatible capability expansion
- patch: compatible correction

Safety-critical corrections may require accelerated release regardless of numeric size.

---

# Immutable Releases

Released artifacts are immutable.

Changes create new versions.

Mutable latest references may exist for discovery.

They never replace exact version identifiers in provenance.

---

# Package Release

A package release requires

- complete manifest
- integrity digest
- compatible Runtime declaration
- passing required Simulation
- passing Evaluation gates
- current Coverage report
- valid review states
- known limitations
- rollback artifact
- release provenance

---

# Pre-release States

Suggested states

- draft
- generated
- validation
- review
- release_candidate
- released
- deprecated
- withdrawn

Runtime production policy accepts only permitted states.

---

# Compatibility

Compatibility is declared for

- Runtime
- rule language
- Clinical Memory schema
- mapping package
- FHIR baseline
- terminology baseline
- Encounter Context scope

Compatibility is tested.

It is not assumed.

---

# Migration

Breaking change migration documents

- affected identifiers
- semantic changes
- state transformation
- package transition
- Clinical Memory impact
- FHIR impact
- Simulation updates
- rollback

Silent migration is prohibited.

---

# Rollback

Every production release has a tested rollback path.

Rollback preserves

- session provenance
- prior package identity
- state compatibility
- safety audit
- release reason

An active session does not silently change package during rollback.

---

# Withdrawal

A package may be withdrawn for

- safety defect
- corrupted artifact
- invalid provenance
- licensing issue
- critical semantic error
- security issue

Withdrawal records scope, reason, authority and replacement.

---

# Release Notes

Release notes include

- scope
- new Coverage
- changed knowledge
- changed behavior
- safety changes
- mapping changes
- resolved defects
- known limitations
- migration
- provenance

---

# Reproducibility

A release must be rebuildable from

- source manifests
- cached sources
- repository revision
- Builder version
- Compiler version
- configuration
- terminology baseline
- guideline baseline

---

# Final Principle

Every executable behavior belongs to an exact, immutable and reproducible release lineage.
