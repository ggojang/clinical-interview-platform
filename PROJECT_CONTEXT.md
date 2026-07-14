# PROJECT CONTEXT

Version: 0.2 (Draft)

---

# Purpose

This document is the master context for the Clinical Interview Knowledge Platform repository.

It defines project identity, authority, architecture, lifecycle, complete Context document order, current implementation status and completion gates.

Every human and AI agent must read FOUNDATION.md first and this document second.

---

# 1. Project Identity

This repository is an AI-native Clinical Interview Knowledge Factory for Primary Care.

The product is reusable, traceable and executable interview knowledge.

The product is not a chatbot.

The product is not a diagnosis engine.

The product is not a FHIR server.

The product is not a collection of prompts.

Runtime is one executor of compiled knowledge.

Knowledge is the product.

---

# 2. Immutable Foundation

FOUNDATION.md has the highest authority.

Its immutable principles include:

- Runtime never queries external medical knowledge.
- Knowledge Graph is the canonical internal representation.
- Every object has provenance.
- Simulation is mandatory.
- Coverage determines progress.
- Reason for Encounter is an entry point.
- Clinical Intent drives questioning.
- Runtime executes compiled knowledge only.
- Medical Sources are Build-Time only.
- Knowledge Factory is the primary product.

Changing an immutable principle requires an Architecture Decision Record.

No lower-level document may silently override FOUNDATION.

---

# 3. Authority Order

Authority flows in this order:

FOUNDATION.md

↓

PROJECT_CONTEXT.md

↓

docs/context/

↓

specifications/

↓

schemas/

↓

reviewed Knowledge Graph content

↓

generated knowledge

↓

compiled packages

↓

Runtime implementation

↓

examples and playground output

Implementation is never the source of clinical truth.

A structurally valid object may still violate semantic or behavioral specifications.

---

# 4. Required Reading Order

Before changing repository knowledge:

1. Read FOUNDATION.md.
2. Read PROJECT_CONTEXT.md.
3. Read relevant documents in docs/context/.
4. Read relevant behavioral specifications.
5. Read relevant schemas.
6. Inspect related graph objects and provenance.
7. Inspect related Simulations and Evaluation.
8. Inspect Runtime implementation last.

---

# 5. Primary Architecture

External Medical Sources

↓

Knowledge Acquisition

↓

Source Cache

↓

Normalization

↓

Semantic Alignment

↓

Knowledge Builder

↓

Knowledge Graph

↓

Rule Graph

↓

Simulation

↓

Evaluation

↓

Compilation

↓

Immutable Knowledge Package

↓

Interview Runtime

↓

Clinical Memory

↓

FHIR Export

↓

De-identified Feedback

↓

Knowledge Acquisition

The Knowledge Factory evolves.

Runtime remains simple.

---

# 6. Build-Time Boundary

Build Time may:

- acquire external medical sources;
- use terminology services such as STOM;
- interpret guidelines;
- normalize heterogeneous sources;
- align repository semantics;
- create graph nodes and edges;
- create rules;
- create Simulations;
- evaluate behavior;
- calculate Coverage;
- compile packages;
- produce provenance.

Build Time must preserve source versions, licensing, digests and lineage.

Build Time must be reproducible from cached source artifacts.

---

# 7. Runtime Boundary

Runtime may:

- load one compatible immutable Knowledge Package;
- accept Encounter Context and Reason for Encounter;
- observe patient or caregiver input;
- create validated Fact candidates;
- update Clinical Memory;
- execute compiled rules;
- activate Clinical Intents;
- generate Interview Targets;
- select approved Question Templates;
- evaluate safety;
- record Reasoning Trace;
- create approved FHIR projections;
- emit governed feedback events.

Runtime must never:

- search external medical sources;
- query STOM or terminology servers;
- interpret new guidelines;
- create repository knowledge;
- edit graph nodes;
- change rule priority;
- learn medical behavior from a session;
- silently upgrade a package;
- infer diagnosis from an active Hypothesis;
- hide important state inside a prompt.

---

# 8. Interview Planning Model

The canonical planning chain is:

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

Question

Encounter Context modifies downstream behavior.

Reason for Encounter explains why care is sought.

Clinical Intent explains why information is needed.

Interview Target defines the immediate information objective.

Fact represents reusable clinical information.

Question is only the interface used to collect a Fact.

Diagnosis is never the direct source of Questions.

For a test-result follow-up Reason for Encounter, Runtime distinguishes institutional result checking from a request for interpretation. Result content is requested only for interpretation and only once. A routine institutional result-check encounter with no abnormal notice, new symptom or additional request may complete without collecting the report.

When a user voluntarily uploads a report, prescription, screening form, image or scanned document, Runtime may extract explicit interview Facts into conversation state with document provenance, date and uncertainty. It reuses current explicit Facts to avoid duplicate questions, preserves conflicts with patient-reported information for clarification, never treats unreadable or absent document content as negative, and does not persist or publish the material in the public test version.

Runtime never infers completion merely because no further question is selected. After the final free-text concern and required safety follow-up, it presents a distinct completion handoff for user confirmation. Until confirmed, the response remains in progress. Confirmed completion, user stop, post-completion correction and administrative invalidation remain distinguishable for future FHIR R4 `QuestionnaireResponse.status` mapping, and completion confirmation never substitutes for Consent.

The public ChatGPT test preserves Reason for Encounter as the first interview input, then gives a one-time notice before the first questionnaire item that Free-tier GPT use and file or image uploads may be rate-limited. It never promises a fixed quota or reset time, and interruption before explicit completion remains in progress rather than completed.

The public test exposes compact source identity for each compiled RFE package and may use STOM through a separate read-only terminology Action. AI first converts Korean or English free text into a minimal de-identified normalized term, then retrieves and verifies provisional SNOMED CT, LOINC, KCD-8 or HIRA candidates. Live terminology never creates clinical rules or selects safety behavior, raw patient material is never sent, and failure falls back to preserved free text plus compiled knowledge.

Every test question and final report exposes its origin without conflating joint project work with model invention. Compiled project objects are marked as 공동 작업 지식, language-only adaptation as AI 표현, unsupported clarification or reasoning as AI 자체 생성, live coding as STOM 용어 조회, direct statements as 사용자 제공, and extracted file content as 첨부자료. Mixed origin remains visible and is retained for future FHIR Provenance projection.

When a user asks a different question while an interview question is pending, Runtime preserves the pending Fact as unanswered, processes the detour as a separate additional comment, and reassesses safety. A topic detour is followed by an explicit recovery choice to resume the same question, begin the normal completion handoff with missing information preserved, or stop the interview. A new Reason for Encounter never silently merges into the active interview.

Every numbered question must use one semantically consistent presentation pattern. A binary question asks one complete clinical proposition and offers yes, no, unknown and decline. A checklist explicitly permits multiple selections, exposes every clinical finding as a separate domain option, and only then appends none, unknown and decline with continuous numbering. Runtime rejects plural stems with a single clinical option, yes/no options attached to checklist stems, and trailing warning text that introduces findings the user was not able to select. The same validation applies to the initial safety gate.

Longitudinal background information is reviewed on the first encounter and thereafter by recency. The first-encounter baseline comprises current and past diagnoses, past surgery and major procedures, current medication including nonprescription products and supplements, known allergies, family history, current or recent occupation and important work exposures, smoking, and alcohol. Symptom irrelevance is not a valid reason to omit a baseline group. Research defaults are 90 days for current medication and 365 days for all other baseline groups. Runtime asks only due or change-relevant groups, reuses explicit current information, and records each group's last confirmation date. When no persistent confirmation timestamp is available, Runtime asks one combined first-use/recency gating question before repeating the background inventory. Every due group must end as answered, current-existing, unknown or declined before normal completion; safety-deferred groups remain unresolved and prevent a completed status.

---

# 9. Hypothesis Boundary

Facts may support Clinical Groups.

Clinical Groups may support Hypotheses.

Hypotheses may influence differentiation only through an explicit Clinical Intent and Interview Target.

The allowed path begins with Clinical Intent, passes through Interview Target and Fact, and may then reach Clinical Group and Hypothesis.

The prohibited path begins with Hypothesis and directly generates a Question.

Pattern activation and Hypothesis support are not diagnosis.

Temporal association is not causation.

---

# 10. Fact-Centric Semantics

Facts are reusable repository assets.

Facts do not belong to one presentation.

Questions collect Facts.

Interview Targets require Facts.

Clinical Memory stores Facts.

Simulation validates Facts.

Coverage measures Facts.

FHIR exports Facts through mappings.

Duplicate Facts are prohibited.

---

# 11. Clinical Memory

Clinical Memory is explicit encounter state.

It contains:

- Encounter Context;
- Reason for Encounter;
- Facts and evidence;
- active Clinical Intents;
- active Interview Targets;
- contradictions;
- safety state;
- Question history;
- stop state;
- provenance;
- Reasoning Trace references.

Evidence is append-only.

New evidence never silently overwrites old evidence.

Silence never creates a negative Fact.

Missing, unknown, explicitly negative, conflicted and not applicable are different states.

---

# 12. Rule Execution

The Knowledge Graph defines what exists.

The Rule Graph defines what should happen.

Runtime executes compiled rules.

Rule types include activation, applicability, requirement, completion, priority, suppression, conflict, safety, transition, stop and mapping.

Rules never redefine Fact semantics.

Runtime never invents rules.

---

# 13. Safety Model

Safety has precedence over routine completeness.

Safety precedence does not require every rare-danger Question to precede all common history.

The default strategy is:

1. establish essential context;
2. perform a minimal safety gate;
3. continue with high-value common Targets when routine;
4. re-evaluate safety after every new Fact;
5. escalate immediately when a reviewed rule matches.

Generated or unreviewed safety rules may be tested.

They must not be enabled in production.

Runtime records triggering evidence, rule version, permitted clarification, escalation action and stop or handoff.

---

# 14. Question Model

Questions are generated only from unresolved Interview Targets and Facts.

Questions must:

- ask one primary concept;
- use neutral language;
- avoid leading wording;
- avoid exposing hidden Hypotheses;
- preserve uncertainty;
- permit refusal;
- support the current language and mode;
- carry Template provenance.

A Question being asked does not mean its Target is satisfied.

Facts determine completion.

---

# 15. Provenance

Everything has provenance.

No exceptions.

Provenance applies to source artifacts, normalized artifacts, graph nodes, graph edges, rules, Questions, Facts, Simulations, Evaluation reports, Coverage reports, compilation, packages, Clinical Memory, Runtime decisions, FHIR exports and feedback events.

Unknown provenance is unacceptable.

AI-generated content defaults to unreviewed.

---

# 16. Simulation

Simulation is mandatory.

Required case types include positive, negative, ambiguous, conflicting, missing information, refusal, correction, boundary value, multilingual, safety escalation, routine common case, stop, handoff and regression.

Every capability must be testable.

No Simulation means no release.

---

# 17. Evaluation

Evaluation separately measures safety, Fact correctness, Intent activation, Target completion, Question quality, efficiency, traceability, Coverage, interoperability, patient burden and robustness.

A high aggregate score cannot hide a critical safety failure.

File count, plausible demos and model fluency are not acceptance evidence.

---

# 18. Coverage

Coverage determines repository progress.

The primary Coverage chain is:

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

Question

↓

Simulation

A unit is covered only when it is defined, connected, validated, simulated, provenance-complete and included in an appropriate package.

Coverage is computed from graph connectivity and execution results.

It is never estimated manually.

---

# 19. Terminology and Interoperability

SNOMED CT, MRCM, LOINC, ICPC-2 and FHIR are Build-Time alignment or interoperability resources.

They do not control Runtime.

ICPC-2 supports pragmatic Primary Care classification and indexing.

SNOMED CT supports terminology alignment.

MRCM is acquired and summarized only at Build Time. A Fact may retain a versioned provisional MRCM validation reference for permitted SNOMED CT attributes, domains, ranges and cardinality. Runtime never executes MRCM, and an MRCM result never creates a clinical Rule or determines question priority, diagnosis or safety. The abdominal-pain research package is the first package to retain such a validation reference for Finding site and Severity.

LOINC supports observable alignment.

FHIR supports exchange.

The Knowledge Graph remains the canonical internal representation.

FHIR Export is a projection of Clinical Memory.

---

# 20. Knowledge Package

The Compiler produces an immutable Knowledge Package.

A package contains:

- Knowledge Graph projection;
- Rule Graph;
- Question Templates;
- mappings;
- Simulation metadata;
- Coverage;
- validation reports;
- terminology baseline;
- guideline baseline;
- provenance;
- manifest;
- integrity digests;
- Runtime compatibility.

No patient state exists inside a package.

Runtime binds a session to one exact package version.

Planned Primary Care packages are implemented through the versioned queue in `knowledge/catalog/planned-package-work-queue.json`. Catalog promotion occurs only after deterministic compilation, complete Fact-to-Question coverage, safety-rule simulation coverage, privacy validation and public bundle generation. Abdominal pain, chest pain and headache are implemented as unreviewed research packages; the queue continues with dizziness or syncope, vomiting or diarrhoea, urinary symptoms, fatigue, back pain, skin complaints and medication review.

---

# 21. Feedback and Evolution

Runtime does not learn.

De-identified or governed feedback returns to the Knowledge Factory.

Feedback may identify unsupported Reason for Encounter, missing Target, missing Fact, misunderstood Question, repeated Question, safety near miss, false escalation, mapping failure or Coverage gap.

Feedback is not automatically knowledge and never mutates the active Runtime package.

Resolution includes service improvement, not only a conversational answer. The AI Knowledge Factory may generalize de-identified feedback, reproduce the gap, update Questions, routing, Facts, Knowledge, Rules, tests, API resources or GPT configuration, and deploy a new `unreviewed/research_only` version after privacy, validation, Simulation, Evaluation and compilation gates pass.

Human participation is optional for research-only upgrades but remains required for promotion to reviewed or Production knowledge. Applied upgrades are reported by result. Items blocked by evidence, safety, authority, licensing, permissions or required clinical judgment are reported as unresolved with the required human action.

---

# 22. Governance

Trust is an explicit review state.

Supported states include unreviewed, in_review, reviewed, rejected and deprecated.

Separate review may be required for clinical meaning, safety, wording, terminology, FHIR, licensing, privacy, security, language and jurisdiction.

Safety-critical production knowledge requires qualified human review.

---

# 23. Primary Care Scope

Development begins with Primary Care.

Coverage expands horizontally across common Reasons for Encounter before deep specialty expansion.

Priority domains include respiratory, cardiovascular, gastrointestinal, neurological, musculoskeletal, dermatological, genitourinary, mental health, preventive care and administrative care.

Chief Complaint is only one Reason for Encounter type.

A presentation may not exist for vaccination, health checks, medication review or administrative care.

---

# 24. Context Document Index

## Foundation and Planning

- docs/context/000-foundation.md — immutable architecture
- docs/context/001-clinical-intent.md — why the interview seeks information
- docs/context/002-encounter-context.md — environment modifying behavior
- docs/context/003-primary-care-scope.md — Primary Care Coverage boundary
- docs/context/004-interview-target.md — immediate information objective
- docs/context/005-fact.md — reusable semantic information unit

## Knowledge Architecture

- docs/context/006-knowledge-graph.md — canonical internal representation
- docs/context/007-graph-model.md — nodes, edges, properties and constraints
- docs/context/008-rule-graph.md — executable behavior
- docs/context/009-builder-model.md — graph and rule construction
- docs/context/010-knowledge-acquisition.md — external source acquisition
- docs/context/011-normalization.md — canonical source representation
- docs/context/012-semantic-alignment.md — repository semantic identity
- docs/context/013-provenance.md — complete lineage
- docs/context/014-knowledge-package.md — deployable knowledge unit

## Compilation and Runtime

- docs/context/015-compilation-model.md — deterministic package compilation
- docs/context/016-runtime-model.md — compiled knowledge executor
- docs/context/017-clinical-memory.md — explicit encounter state
- docs/context/018-reasoning-loop.md — turn-by-turn state transition
- docs/context/019-question-generation.md — Target-to-Fact-to-Question interface
- docs/context/020-priority-and-safety.md — action ordering and safety constraint

## Quality and Evolution

- docs/context/021-simulation-model.md — mandatory executable cases
- docs/context/022-evaluation-model.md — quality metrics and release gates
- docs/context/023-coverage-model.md — computed completeness
- docs/context/024-interoperability-and-fhir.md — terminology and exchange boundary
- docs/context/025-feedback-and-evolution.md — governed improvement loop
- docs/context/026-governance-and-review.md — review and trust
- docs/context/027-versioning-and-release.md — immutable release lineage

## Repository and Delivery

- docs/context/028-repository-operating-model.md — human and AI workflow
- docs/context/029-security-and-privacy.md — data-domain protection
- docs/context/030-roadmap-and-definition-of-done.md — phases and gates
- docs/context/031-knowledge-refresh-policy.md — source monitoring and knowledge re-review cadence

---

# 25. Current Repository State

The current implementation is an early multi-RFE executable Knowledge Factory with cough, fever, breathing-difficulty, abdominal-pain, chest-pain and headache vertical slices.

It includes a profile-driven deterministic Builder, a Primary Care Reason for Encounter catalog, 127 unique research Facts across six independently compiled packages, complete Fact-to-Question linkage within every package, shared Fact identity, versioned Source Manifests, source-specific refresh scheduling, deterministic Compiler, integrity-checked draft Knowledge Packages, evidence-preserving Clinical Memory with coded `dataAbsentReason`, package-driven multi-turn Runtime, multi-domain warning-feature examples, limited English and Korean extraction, 70 synthetic JSON Simulations, Evaluation, computed Coverage, validation and tests.

This implementation demonstrates parts of the intended architecture.

It does not yet implement the complete Knowledge Factory.

Known gaps include:

- no live external Knowledge Acquisition connector or complete multi-domain Builder pipeline;
- no persistent graph database or general-purpose graph authoring workflow;
- Compiler and Knowledge Packages currently cover only cough, adult fever, breathing difficulty, abdominal pain, chest pain and headache vertical slices;
- no signed or production-approved Knowledge Package;
- Clinical Memory merge supports evidence and conflict but not the complete longitudinal policy;
- Runtime provenance is present but not yet production-grade;
- Simulation and Evaluation remain limited to cough, adult fever, and breathing-difficulty vertical slices;
- Coverage calculation is complete for the current Fact-to-Question package dimension but incomplete across Primary Care domains;
- no governed production safety package;
- no production privacy, security or deployment controls.

When implementation conflicts with the Context architecture, implementation changes.

The architecture is not silently weakened to match the prototype.

---

# 26. Repository Change Workflow

For every semantic or behavioral change:

1. identify the affected Context and specification;
2. identify source evidence;
3. reuse existing graph objects;
4. change knowledge at the correct layer;
5. preserve provenance;
6. add positive, negative and ambiguous Simulation;
7. validate graph and rules;
8. run Evaluation;
9. recompute Coverage;
10. compile a new package when applicable;
11. obtain required review;
12. record assumptions, gaps and migration.

Medical knowledge is never patched directly into Runtime.

---

# 27. Definition of Done

A knowledge object is complete when its identity and meaning are stable, duplicates are absent, graph relationships resolve, provenance is complete, review state is correct, Simulation passes, Coverage is updated and package compilation succeeds.

A behavior is complete when its rule is explicit, priority is traceable, safety effect is known, positive, negative, ambiguity and regression tests pass, failure behavior is defined and Runtime trace is reconstructable.

A release is complete when manifest and integrity are valid, Simulation and Evaluation gates pass, Coverage is reported, review approvals exist, compatibility is tested, rollback exists, limitations are published and provenance is complete.

---

# 28. Final Statement

The purpose of this repository is not to create a smarter Runtime.

The purpose is to create a continuously evolving Clinical Interview Knowledge Factory capable of producing trustworthy interview knowledge for Primary Care.

Knowledge is acquired, normalized, aligned, built, simulated, evaluated, compiled, packaged and governed.

Runtime executes.

Clinical Memory records.

FHIR projects.

Feedback returns to the Factory.

Coverage and evidence determine progress.
