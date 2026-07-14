# Knowledge Package

Version: 0.1 (Draft)

---

# Purpose

This document defines the Knowledge Package.

A Knowledge Package is the deployable unit produced by the Knowledge Factory.

The Builder creates Knowledge.

The Compiler transforms Knowledge into a Knowledge Package.

The Runtime executes a Knowledge Package.

---

# Philosophy

Knowledge exists independently.

Runtime consumes packaged knowledge.

The package is immutable.

Runtime never modifies a package.

Builder never executes a package.

---

# Package Pipeline

Medical Sources

↓

Knowledge Acquisition

↓

Knowledge Graph

↓

Rule Graph

↓

Simulation

↓

Validation

↓

Compilation

↓

Knowledge Package

↓

Interview Runtime

---

# Package Identity

Every Knowledge Package contains

Package Identifier

Package Version

Knowledge Version

Compiler Version

Builder Version

Coverage Version

Simulation Version

Terminology Baseline

Guideline Baseline

FHIR Baseline

Repository Version

Build Timestamp

Compilation Hash

Provenance Identifier

---

# Package Scope

A package always declares its scope.

Examples

Primary Care

Primary Care v1

Respiratory

Vaccination

Medication Review

Pediatric Primary Care

Occupational Health

A Runtime always knows which package it is executing.

---

# Package Structure

Knowledge Package contains

Knowledge Graph

Rule Graph

Coverage

Simulation

Mappings

Metadata

Provenance

Validation

No Runtime State exists inside a package.

---

# Knowledge Graph

Package contains a read-only graph.

Nodes

Edges

Metadata

Versions

Mappings

The graph is immutable.

---

# Rule Graph

Package contains compiled rules.

Examples

Activation Rules

Priority Rules

Completion Rules

Dependency Rules

Escalation Rules

Suppression Rules

Rules are executable.

---

# Coverage

Coverage includes

Supported Domains

Supported RFEs

Supported Clinical Intents

Supported Interview Targets

Supported Facts

Simulation Coverage

Coverage Metrics

Coverage allows Runtime to understand package limitations.

---

# Simulation

Simulation Package contains

Patient Scenarios

Expected Facts

Expected Questions

Expected Rule Activation

Expected Coverage

Simulation Metadata

Simulation Provenance

Simulation is always included.

---

# Validation Report

Each package records validation.

Examples

Schema Validation

Terminology Validation

Simulation Validation

Coverage Validation

Regression Validation

Compiler Validation

Validation Status

Package without validation is incomplete.

---

# Terminology Baseline

Package records

SNOMED Version

LOINC Version

ICPC Version

FHIR Version

Terminology Server

Package never depends on "latest".

---

# Guideline Baseline

Package records

Guideline

Version

Jurisdiction

Publication Date

Review Date

Every recommendation used by Builder is traceable.

---

# Package Metadata

Metadata contains

Identifier

Display

Description

Scope

Language

Jurisdiction

License

Version

Status

Compilation Time

Build Time

Builder Version

Compiler Version

Repository Version

---

# Package Provenance

Package provenance records

Builder

Compiler

Input Graph

Output Package

Medical Sources

Coverage

Simulation

Validation

Package Hash

Nothing inside a package lacks provenance.

---

# Package Constraints

Packages are immutable.

Packages are reproducible.

Packages are deterministic.

Packages are versioned.

Packages are traceable.

Packages are testable.

---

# Incremental Packages

Builder may create

Patch Packages

Minor Packages

Major Packages

Example

Primary Care

1.0.0

↓

1.0.1

↓

1.1.0

↓

2.0.0

Package compatibility must be explicit.

---

# Runtime Compatibility

Runtime executes

one

Knowledge Package.

Runtime never mixes packages.

Example

Invalid

Knowledge Graph

1.2

+

Rule Graph

1.4

+

Simulation

1.1

Valid

Knowledge Package

1.4.0

Everything inside a package belongs to the same build.

---

# Package Independence

Package never depends on

Internet

STOM

SNOMED Server

FHIR Server

Builder

Compiler

Guideline Website

Everything required by Runtime is inside the package.

---

# Package Serialization

Knowledge Package may be serialized as

JSON

YAML

Binary

SQLite

Graph Database Snapshot

The serialization format is implementation-specific.

The package semantics remain identical.

---

# Runtime Loading

Runtime performs

Load Package

↓

Verify Hash

↓

Verify Version

↓

Load Graph

↓

Load Rules

↓

Initialize Runtime

↓

Begin Interview

Runtime never rebuilds the package.

---

# Package Validation

Package validation verifies

Hash

Version

Graph Integrity

Rule Integrity

Coverage

Simulation

Mappings

Provenance

Validation Report

Package Signature (optional)

---

# Package Lifecycle

Draft

↓

Generated

↓

Validated

↓

Reviewed

↓

Compiled

↓

Released

↓

Deprecated

↓

Archived

Only Released packages may be used by Runtime.

---

# Release

Every Release records

Package Version

Knowledge Version

Coverage Version

Simulation Version

FHIR Version

Terminology Version

Repository Commit

Release Notes

---

# Repository Rules

Every Runtime requires exactly one released Knowledge Package.

Every Knowledge Package must contain

Knowledge Graph

Rule Graph

Coverage

Simulation

Mappings

Validation

Provenance

No Runtime executes incomplete packages.

---

# Final Principle

Knowledge Packages are the deployment artifacts of the Clinical Interview Knowledge Factory.

Builder creates knowledge.

Compiler creates packages.

Runtime executes packages.

Each package is complete, deterministic, immutable and reproducible.
