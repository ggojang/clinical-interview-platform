# Security and Privacy

Version: 0.1 (Draft)

---

# Purpose

This document defines security and privacy boundaries.

Knowledge Factory data and patient encounter data are separate security domains.

---

# Data Domains

## Public or Licensed Medical Sources

Build-Time source material subject to licensing and integrity controls.

## Repository Knowledge

Versioned graph, rules, mappings, simulations and provenance.

## Compiled Packages

Immutable executable artifacts.

## Clinical Memory

Sensitive encounter-specific data.

## Feedback

De-identified, synthetic or governed operational evidence.

Each domain has separate access and retention policy.

---

# Core Principle

Collect the minimum necessary data.

Preserve integrity.

Separate knowledge from patient data.

---

# Runtime Privacy

Runtime must support

- explicit session identity
- minimum necessary collection
- access control
- encryption in transit
- encryption at rest
- audit logging
- retention policy
- deletion policy
- consent or lawful basis
- jurisdictional requirements

---

# Knowledge Acquisition Privacy

Knowledge Acquisition must not collect identifiable patient data.

Clinical records are not ordinary medical-source inputs.

Any use of clinical datasets requires a separate governed pipeline.

---

# Secrets

Credentials must be supplied through

- environment variables
- secret managers
- protected configuration

Secrets must not appear in

- source files
- package artifacts
- logs
- traces
- simulations
- feedback events

---

# Supply Chain

Build security includes

- pinned tool versions
- source digests
- package digests
- dependency review
- reproducible builds
- artifact signing
- protected release authority
- vulnerability response

---

# Package Integrity

Runtime verifies

- artifact digest
- manifest
- signature when required
- compatibility
- release state
- withdrawal status

Invalid packages are rejected.

---

# Prompt and Model Boundary

Patient text is untrusted input.

Model output is untrusted candidate data.

Both are validated before state mutation.

Prompts must not contain unnecessary patient history or secrets.

---

# Injection Resistance

Runtime never treats patient text as

- package configuration
- rule definition
- system instruction
- source citation
- review approval

Patient text may only become evidence through the Fact candidate process.

---

# Audit

Audit records

- access
- package load
- state change
- export
- handoff
- deletion
- administrative action
- security failure

Audit data follows minimum necessary principles.

---

# De-identification

Feedback de-identification removes or transforms

- direct identifiers
- quasi-identifiers
- free-text identifiers
- precise unnecessary dates
- source-system identifiers

De-identification itself is versioned and evaluated.

---

# Simulation Data

Simulation should be synthetic.

A simulation derived from real data requires documented authorization and de-identification provenance.

---

# Incident Response

Security or privacy incidents trigger

- containment
- evidence preservation
- affected package or Runtime identification
- governance notification
- impact analysis
- withdrawal when needed
- remediation
- regression testing
- documented closure

---

# Final Principle

Clinical Memory is protected encounter data.

Repository knowledge is versioned product data.

The platform must never blur this boundary.
