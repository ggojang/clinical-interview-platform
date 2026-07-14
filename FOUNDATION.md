# FOUNDATION

Version: 0.1 (Draft)

---

# Purpose

This document defines the immutable architectural principles of the Clinical Interview Knowledge Platform.

Every AI agent participating in this repository MUST read this document before reading any other document.

This document changes rarely.

If any other document conflicts with FOUNDATION.md, FOUNDATION.md always takes precedence.

---

# 1. Project Identity

This project is an AI-native Clinical Interview Knowledge Factory.

The objective is NOT to build an AI chatbot.

The objective is NOT to build a diagnosis engine.

The objective is NOT to build a FHIR server.

The objective is NOT to build a questionnaire generator.

The objective is to continuously generate, validate, compile, evaluate, and evolve reusable interview knowledge for Primary Care.

Interview Runtime is only one consumer of this knowledge.

Knowledge is the product.

Runtime is the executor.

---

# 2. Primary Philosophy

The repository exists to build knowledge.

Not prompts.

Not conversations.

Not models.

Knowledge.

Every component inside this repository exists because it contributes to the creation, validation, execution, or evolution of interview knowledge.

---

# 3. Knowledge Factory

The repository is organized as a Knowledge Factory.

Medical Sources

↓

Knowledge Acquisition

↓

Knowledge Graph

↓

Simulation

↓

Evaluation

↓

Compilation

↓

Compiled Knowledge Package

↓

Interview Runtime

↓

Feedback

↓

Knowledge Acquisition

Knowledge continuously evolves.

Runtime should continuously simplify.

---

# 4. Runtime Philosophy

Runtime never learns.

Runtime never searches.

Runtime never discovers.

Runtime executes compiled knowledge.

The Knowledge Factory becomes smarter.

Runtime becomes simpler.

---

# 5. Source of Truth

The repository has multiple truth layers.

Medical Sources

↓

Knowledge Graph

↓

Compiled Package

↓

Clinical Memory

↓

FHIR Export

Definitions

Medical Sources

External medical knowledge.

Knowledge Graph

Repository knowledge.

Compiled Package

Runtime knowledge.

Clinical Memory

Session knowledge.

FHIR Export

Interoperability representation.

Runtime is never the source of truth.

---

# 6. Build-time vs Runtime

Knowledge generation occurs before Runtime.

Compile once.

Execute many.

Runtime MUST NOT query external medical evidence sources or generate clinical rules from live external content.

Examples include

- SNOMED CT
- STOM
- FHIR Specification
- NICE
- CHEST
- ERS
- GINA
- GOLD
- CDC
- USPSTF
- PubMed

These resources belong to Knowledge Acquisition.

An approved terminology server is the only Runtime exception, and only for optional read-only semantic alignment of a minimal de-identified normalized term or code. It never determines Clinical Intent, Question selection, safety, diagnosis, or completion. Runtime remains functional when it is unavailable.

---

# 7. Reason for Encounter

The repository begins from Reason for Encounter.

Chief Complaint is only one type of Reason for Encounter.

Presentation may or may not exist.

Examples

Reason for Encounter

↓

Clinical Intent

↓

Presentation (optional)

↓

Clinical Group

↓

Interview Target

↓

Fact

↓

Question

↓

Hypothesis

↓

Simulation

Reason for Encounter is the entry point.

Diagnosis is never the entry point.

---

# 8. Clinical Intent

Clinical Intent determines interview behavior.

Questions are generated to satisfy Clinical Intent.

Questions are never generated directly from diagnoses.

Examples

Red Flag Screening

Common Cause Differentiation

Risk Assessment

Medication Review

Follow-up Assessment

Health Maintenance

Preventive Care

Counselling

Referral Assessment

Clinical Intent is independent from diagnosis.

---

# 9. Knowledge Graph

Knowledge Graph is the central artifact of this repository.

Everything else is derived.

Examples

Questions

Interview Patterns

Simulation Patients

Coverage

FHIR Mapping

Clinical Memory Structure

Reasoning Rules

Compiled Runtime Package

Knowledge Graph is the canonical internal representation.

---

# 10. Facts

Facts are reusable.

Facts belong to the repository.

Facts never belong to individual presentations.

Examples

symptom.duration

symptom.onset

symptom.severity

patient.age

patient.sex

patient.medication

patient.smoking

These facts are shared across multiple presentations.

Fact duplication is prohibited.

---

# 11. Questions

Questions are generated from Interview Targets.

Questions are not manually tied to diagnoses.

Questions exist because information is required.

Not because a diagnosis exists.

---

# 12. Simulation

Simulation is mandatory.

Every interview capability must be testable.

Every Knowledge Package requires Simulation.

Simulation includes

Positive Cases

Negative Cases

Ambiguous Cases

Conflicting Cases

Missing Information Cases

Simulation is a first-class component.

---

# 13. Provenance

Everything has provenance.

Every Fact.

Every Question.

Every Knowledge Item.

Every Simulation.

Every Clinical Memory.

Every Export.

No exceptions.

Unknown provenance is unacceptable.

---

# 14. Coverage

Repository progress is measured by Coverage.

Not by file count.

Coverage dimensions

Reason for Encounter

Clinical Intent

Presentation

Clinical Group

Interview Target

Fact

Question

Simulation

Coverage drives development.

---

# 15. Terminology

SNOMED CT

FHIR

LOINC

ICPC-2

are build-time knowledge sources.

ICPC-2 is used as a pragmatic Primary Care classification and indexing system.

It does not define the internal semantics of the Interview Engine.

SNOMED CT provides terminology alignment.

FHIR provides interoperability.

Neither controls Runtime.

---

# 16. STOM

STOM is the build-time terminology provider and an optional Runtime semantic-alignment service.

At Runtime, STOM receives only a minimal de-identified normalized term or code through approved read-only operations. Raw patient responses, identifiers, files, full narratives and combinations of clinical facts are prohibited.

STOM results are provisional coding candidates. Selected codes require active-state verification and retain server version, provenance and uncertainty.

Knowledge Builder may use the broader terminology API. Runtime may not use STOM to create clinical knowledge or rules.

Compiled Runtime Packages never require STOM and remain functional when it is unavailable.

---

# 17. Guideline Integration

Guidelines are evidence sources.

Examples

NICE

CHEST

ERS

GINA

GOLD

CDC

USPSTF

Guidelines contribute to

Clinical Intent

Priority

Interview Targets

Safety Rules

Question Ordering

Guidelines never execute during Runtime.

---

# 18. Primary Care First

Development proceeds according to Primary Care coverage.

The repository expands by Reason for Encounter.

Coverage expansion follows

Respiratory

Cardiovascular

Gastrointestinal

Neurological

Musculoskeletal

Dermatological

Genitourinary

Mental Health

Preventive Care

Administrative Care

The repository grows horizontally before vertically.

---

# 19. AI-first Repository

The repository is designed for AI Agents.

Specifications precede implementation.

Knowledge precedes Runtime.

Compilation precedes execution.

Simulation precedes deployment.

Evaluation precedes release.

AI agents are expected to read repository documents in order.

---

# 20. Immutable Principles

The following principles require Architecture Decision Records (ADR) before modification.

• Runtime never queries external medical knowledge.

• Knowledge Graph is the canonical internal representation.

• Every object has provenance.

• Simulation is mandatory.

• Coverage determines repository progress.

• Reason for Encounter is the entry point.

• Clinical Intent drives questioning.

• Runtime executes compiled knowledge only.

• Medical Sources are build-time only.

• Knowledge Factory is the primary product.

---

# Final Statement

The purpose of this repository is not to create a smarter Runtime.

The purpose of this repository is to create a continuously evolving Clinical Interview Knowledge Factory capable of producing trustworthy interview knowledge for Primary Care.

Everything else is derived from that decision.
