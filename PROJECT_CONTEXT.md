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

The public test exposes compact source identity for each compiled RFE package. Its host application or test orchestrator may invoke a separate read-only Terminology Verification Adapter backed by STOM; the Adapter is not part of the Clinical Interview Runtime. AI first converts Korean or English free text into a minimal de-identified normalized term, then retrieves and verifies provisional SNOMED CT, LOINC, KCD-8 or HIRA candidates. Adapter results never select Clinical Intent, Interview Target, Fact, Question, Safety Rule, urgency, hypothesis, diagnosis, completion state or any other Runtime behavior. Raw patient material is never sent, and failure falls back to preserved free text plus compiled knowledge.

Every test question and final report exposes its origin without conflating joint project work with model invention. Compiled project objects are marked as 공동 작업 지식, language-only adaptation as AI 표현, unsupported clarification or reasoning as AI 자체 생성, live coding as STOM 용어 조회, direct statements as 사용자 제공, and extracted file content as 첨부자료. Mixed origin remains visible and is retained for future FHIR Provenance projection.

When a user asks a different question while an interview question is pending, Runtime preserves the pending Fact as unanswered, processes the detour as a separate additional comment, and reassesses safety. A topic detour is followed by an explicit recovery choice to resume the same question, begin the normal completion handoff with missing information preserved, or stop the interview. A new Reason for Encounter never silently merges into the active interview.

Every numbered question must use one semantically consistent presentation pattern. A binary question asks one complete clinical proposition and offers yes, no, unknown and decline. A checklist explicitly permits multiple selections, exposes every clinical finding as a separate domain option, and only then appends none, unknown and decline with continuous numbering. Runtime rejects plural stems with a single clinical option, yes/no options attached to checklist stems, and trailing warning text that introduces findings the user was not able to select. The same validation applies to the initial safety gate.

Adaptive questioning is governed by clinical utility rather than by exhausting every loaded Fact. Before each new question, Runtime maintains a semantic coverage ledger across prompted answers, volunteered information and current uploaded material; one sufficiently precise answer may satisfy multiple overlapping symptom-specific and longitudinal Facts. A candidate question is skipped when it is a synonym, broader restatement, unnecessary confirmation or optional detail that cannot materially change safety, routing, required completion or clinician handoff. Reconfirmation is reserved for ambiguity, conflict, safety-critical details, due recency review and source disagreement. Once applicable safety, core Reason for Encounter characterization, relevant history and medicines, due baseline groups, patient goals and one final additional-comment opportunity are addressed, the interview enters numbered review instead of pursuing optional completeness.

An adaptive clinical RFE enters a structured interview, not a general medical consultation. While the interview is collecting information, each assistant turn displays exactly one `Q{positive_integer}` question with at most one stem and its answer options. Question references increase monotonically within the encounter, never restart after an answer, and remain stable when a question is repeated or clarified; answer-option numbers restart locally for each current question and are never edit identifiers. A multi-Fact user response may populate every explicit Fact, but Runtime still asks only one next missing Fact. Ranked disease likelihood, differential discussion, self-examination manoeuvres, investigations, management and treatment suggestions are withheld until explicit completion confirmation. The only mid-interview exception is a brief time-sensitive safety explanation and action. After confirmed completion, non-diagnostic differential considerations, clinician examination or test topics and general management information appear in distinct result sections.

Longitudinal background information is reviewed on the first encounter and thereafter by recency. The first-encounter baseline comprises current and past diagnoses, past surgery and major procedures, current medication including nonprescription products and supplements, known allergies, family history, current or recent occupation and important work exposures, smoking, and alcohol. Symptom irrelevance is not a valid reason to omit a baseline group. Research defaults are 90 days for current medication and 365 days for all other baseline groups. Runtime asks only due or change-relevant groups, reuses explicit current information, and records each group's last confirmation date. When no persistent confirmation timestamp is available, Runtime asks one combined first-use/recency gating question before repeating the background inventory. Every due group must end as answered, current-existing, unknown or declined before normal completion; safety-deferred groups remain unresolved and prevent a completed status.

Whenever the recency gate or at least one longitudinal baseline group is due, Runtime first explains that this review is limited to first completion, unknown confirmation time, interval expiry or reported change and is performed to provide current information to the clinician. The explanation distinguishes the 90-day medication interval from the 365-day interval for diagnoses, procedures, allergies, family history, occupation, smoking and alcohol, and states that recently confirmed groups will not be repeated. If no group is due, neither the explanation nor the baseline inventory is shown.

Immunization is maintained as a distinct reusable longitudinal preventive-care baseline rather than being forced into every ordinary symptom encounter. The preventive immunization profile is activated for preventive visits, health checks, annual reviews and vaccination encounters, or by an RFE-specific or risk-specific rule such as wound tetanus assessment. It preserves vaccine, dose and date details when known, partial or unknown history, evidence source and last confirmation. A 365-day research interval controls profile reconfirmation only; whether a vaccine is due requires current age-, risk- and jurisdiction-specific schedule Knowledge. The preventive profile remains separate from `history.immunization.relevant`, which captures only immunization information directly relevant to the active clinical problem.

Adaptive RFE packages may opt into a reusable clinician-submission context after package-specific safety and required clinical Facts are resolved. This context records the information source, age, clinically relevant sex or anatomy context, due longitudinal history, detailed medication and allergy information, family and occupational exposure history, quantified smoking and alcohol history, available measurements and a final additional comment. It preserves known absence separately from unknown, declined, not applicable, conflicted and never asked states. Runtime can emit a non-FHIR structured clinician handoff grouped by encounter, demographics, history, medication and allergy, family and social history, measurements and additional comments. Fixed questionnaires and FHIR R4 projection remain separate deferred workflows and do not control this internal model.

Clinician submission also strengthens the active Reason-for-Encounter package rather than relying on common history alone. Each adaptive RFE is compiler-audited for presentation, onset and course, anatomical site and laterality when applicable, character and severity, temporal pattern and triggers, functional impact, associated positive and pertinent negative findings, safety red flags, prior episodes and evaluation, attempted treatment and response, relevant clinical risk context, and the person's concern and expected help. Existing package Facts that are optional in ordinary research mode may become required only in clinician-submission mode. Conditional branches retain applicability and may resolve as not applicable; they are never silently converted to negative findings.

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

When a clinical finding has an anatomical Finding site, laterality is collected and post-coordinated only if the versioned body-structure concept is a verified member of `723264001 |Lateralizable body structure reference set|`. The classifiable expression nests `272741003 |Laterality|` on the value of `363698007 |Finding site|`; it does not add Laterality as a parallel attribute to the focus finding. Bilateral input is expanded into separate left and right Finding-site role groups. If membership, MRCM, normal-form compatibility, or terminology service availability cannot be verified, Finding site and laterality remain separate Facts and no post-coordinated expression is asserted.

LOINC supports observable alignment.

Dynamic question terminology follows `LOINC → SNOMED CT → local question
code`. A verified exact or equivalent LOINC code is the preferred external
question coding. A verified SNOMED CT observable or related clinical concept is
secondary. Every Question Template identifier is also a stable code in the
local Clinical Interview Question CodeSystem, so an unmapped question is never
left without round-trip identity. Composite questions do not inherit one
atomic LOINC code as an exact mapping; broader, narrower, partial and related
mappings remain explicit metadata. A question must collect one answer-bearing
clinical data element before an exact or equivalent standard mapping can be
selected. Terminology audits repeatedly identify composite candidates and
place them in an atomic-refactoring queue.

Coded clinical answers follow `SNOMED CT → local answer code` and every dynamic
coded answer set has a complete FHIR R4 ValueSet. ValueSet ids follow
`a-{sct|loinc|local|mixed}-{semantic-name}`. A complete SNOMED set uses
`a-sct-*`; a partial mapping uses `a-mixed-*`; every coded Fact also has an
`a-local-*` companion. Official LOINC LL Answer Lists use `a-loinc-*`.
Clinical yes/no interoperability projection uses the SNOMED-coded
`a-sct-yes-no` ValueSet, while a receiving profile may still explicitly require
a primitive FHIR boolean. Numeric, quantity, date, date-time and narrative
answers use their FHIR R4 primitive value types, with UCUM for known units,
rather than invented answer concepts. Unknown and declined states are never
encoded as negative answers.

Source-defined fixed instruments, including the patient-experience
questionnaire, are excluded from automatic question and answer mapping unless
an explicit instruction requests it and the official artifact is verified.
Before creating a local mapping, Build Time searches official LOINC panels and
Answer Lists, HL7 FHIR and US Core artifacts, NLM VSAC when access and licensing
allow, SNOMED CT implementation artifacts, and STOM. All terminology lookup and
verification occurs at Build Time; compiled Runtime behavior remains
terminology-service independent.

STOM FHIR R4 ValueSet integration initially uses
`http://localhost:8088/fhir` as the primary Build-Time endpoint and
`https://stom.infoclinic.co/fhir` as the remote fallback. External standard
ValueSets are resolved by canonical URL, expanded and code-validated. Project
answer ValueSets are generated as `a-sct-*`, `a-loinc-*`, `a-local-*` or
`a-mixed-*`, then published only through an explicit authenticated deployment
step after canonical duplicate and resource-id collision checks. Runtime never
depends on either endpoint.

Korean claim-code alignment is a separate, reactive interoperability projection. It is activated only when a user supplies a claim code, claim-catalog name or medication product name, requests verification, or provides a document or scan containing an explicit code or name. Routine symptoms, Clinical Facts, AI-generated differentials, and suggested tests or treatments never trigger proactive claim lookup. Diagnosis candidates bind to a versioned KCD-8 or KCD-9 classification while retaining the original SNOMED CT and Clinical Memory semantics. Procedures, medications and therapeutic materials bind only to their matching HIRA EDI code systems. A claim code never establishes a diagnosis or controls question priority, safety, differential diagnosis or escalation. Ambiguous search results remain unresolved, and group-level therapeutic-material results are not treated as final item codes.

When the allowed claim-input flow yields both a verified SNOMED CT coding and a verified KCD/HIRA coding for the same information, both are retained in `terminology.semantic_claim_binding`. Their system, version, code, display, source and verification provenance remain independent, and the mapping is labeled exact, equivalent, broader, narrower, related or unresolved. Name similarity alone never establishes equivalence. Only verified exact or equivalent codings may be projected together as equivalent codings in one FHIR `CodeableConcept`.

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

Planned Primary Care packages are implemented through the versioned queue in `knowledge/catalog/planned-package-work-queue.json`. Catalog promotion occurs only after deterministic compilation, complete Fact-to-Question coverage, safety-rule simulation coverage, privacy validation and public bundle generation. Abdominal pain, chest pain, headache, dizziness or syncope, vomiting or diarrhoea, urinary symptoms, fatigue, back pain, skin complaints, and medication review are implemented as unreviewed research packages. The current planned queue is fully materialized; future entries must meet the same definition of done before catalog promotion.

The grouped expansion governed by `knowledge/catalog/planned-package-work-queue-v0.2.json` is fully materialized as unreviewed research content. It prioritizes reusable question groups rather than disease enumeration: upper-respiratory symptoms, palpitations, bowel symptoms, focal weakness or numbness, joint or limb complaints, mental-health or sleep concerns, edema, hypertension follow-up, weight or constitutional change, and reproductive or genital symptoms. Each grouped RFE preserves symptom-specific safety branches and does not collapse distinct Facts merely because their wording is similar. `tools/validator/audit_expansion_queue.py` verifies the definition of done for every queue entry.

The next expansion queue, `knowledge/catalog/planned-package-work-queue-v0.3.json`, is active. Its materialized slices are grouped eye symptoms, grouped ear or hearing symptoms, diabetes follow-up, grouped oral or dental symptoms, grouped wounds, burns or minor injuries, memory or cognitive concerns, and pregnancy or postpartum concerns. Eye coverage includes red eye or ocular-surface discomfort, vision change, eyelid or periorbital symptoms, and trauma or foreign body. Ear and hearing coverage includes ear pain or infection features, hearing change, discharge or trauma, and tinnitus. Diabetes follow-up covers glycaemic review, medication and hypoglycaemia, hyperglycaemic crises, kidney-eye-foot complication surveillance, cardiovascular risk and self-management, with type-specific insulin and sick-day questions. Oral and dental coverage includes tooth pain or sensitivity, oral or facial swelling and infection, oral mucosal lesions, gum or periodontal symptoms, and trauma or post-procedure problems. Its safety branches distinguish airway or swallowing compromise, deep or eye-threatening spread, severe systemic illness, uncontrolled oral bleeding, significant trauma, permanent-tooth avulsion, severe pain, high-risk infection and persistent oral-cancer warning features. Wound and minor-injury coverage includes open wounds and bleeding, burns, blunt injury or sprain, bites or punctures, and minor head injury. Its safety branches distinguish uncontrolled bleeding, neurovascular compromise, amputation, open fracture or deformity, embedded objects, high-energy injury, serious eye injury, major or special-site burns, head-injury warning features, severe infection and safeguarding concerns. Memory and cognitive coverage includes memory, acute confusion, executive or language change, behaviour or perception, and daily function or safety. It separates hours-to-days confusion and stroke, reduced consciousness, seizure, systemic illness, hypoglycaemia, toxic exposure and immediate behavioural danger from gradual cognitive change. It records both the person's and an informant's observations and references validated cognitive or delirium instruments without reproducing or replacing them. Pregnancy and postpartum coverage branches early-pregnancy pain or bleeding, later-pregnancy fetal movement and labour concerns, maternal medical warning features, postpartum physical recovery, and perinatal mental health or feeding. Safety routing covers haemodynamic instability, ectopic warning features, severe pain or bleeding, pre-eclampsia and seizure features, reduced fetal movement, membrane rupture or preterm labour, postpartum haemorrhage or infection, venous thromboembolism, wound or breast infection, and immediate self-harm, infant-harm or psychosis risk. The packages use conditional completion and build-time STOM terminology mapping; laterality is applied only when the selected finding site is verified in `723264001 |Lateralizable body structure reference set|`. Oral, dental and injury packages therefore retain anatomical site and side as separate Facts and do not assert post-coordination until the selected anatomical structure is individually verified. All content remains `unreviewed/research_only`; MRCM and reference-set results constrain terminology representation only and never create clinical safety rules.

The fixed 2025 fifth inpatient patient-experience instrument is represented as a FHIR R4 `Questionnaire` with eight sections and twenty-six questions. A mechanically generated standalone Markdown projection is also maintained for upload to Custom GPT Knowledge. The chatbot maps an exact patient-experience alias to `rfe.patient_experience_evaluation`. The existing opening screen and a concise explanation may be shown, but the final actionable question before the survey asks only whether the user wants to complete it. The public metadata exposes this as a top-level mandatory `activation_gate`, and every section requires workflow state `activation_confirmed`; section items must therefore remain hidden until an affirmative answer. An affirmative answer retrieves the standalone Knowledge file and enters its first source item immediately without another explanation or confirmation. Split public Action sections are the fallback when that Knowledge file is unavailable. Only source Questionnaire answer options and declared integer ranges are displayed; unknown or declined responses may be retained as absent-answer state only when independently entered and are never added as synthetic numbered choices. Source response codes, not-applicable choices, 0–10 integer ranges, edit references, absent-answer states, and explicit completion status are preserved. Patient answers remain in the conversation and are never sent to the read-only Knowledge Action.

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
- docs/context/032-clinician-submission-context.md — reusable clinician pre-visit minimum dataset and handoff
- docs/context/033-uscdi-interoperability-overlay.md — USCDI v6 and USCDI+ as non-clinical interoperability Coverage overlays

---

# 25. Current Repository State

The current implementation is an early multi-RFE executable Knowledge Factory with forty-six independently compiled Primary Care Knowledge Package profiles. Every dynamic question now has a complete local CodeSystem identity, verified LOINC and secondary SNOMED CT mappings are compiled where available, and coded answer choices use verified SNOMED CT or a context-qualified local fallback. Complete answer ValueSets are generated for SNOMED-only, mixed SNOMED/local and local-only choices, and a repository-wide atomicity gate prevents composite candidates from receiving exact or equivalent standard question mappings. Repository-wide mapping Coverage is computed rather than inferred. The gait and falls profile distinguishes an acute fall, recurrent falls, gait or balance change, fear or near-falls, post-injury follow-up and known mobility-condition follow-up. The epistaxis profile records current bleeding, pressure response, observable amount, duration, frequency, laterality, trauma, antithrombotic and bleeding history. The paediatric growth and development profile preserves dated raw growth measurements and their source, corrected-age context, skills never acquired versus lost, development across domains and settings, feeding, sensory, perinatal, family, education, social, standardized-screen provenance, intervention and family goals. It does not calculate centiles, reproduce licensed screening instruments or infer a diagnosis. The tremor and movement-concern profile records body distribution and side, rest-posture-action-task relationship, rhythm and modifiability, slowness, stiffness, gait, other involuntary movements, bulbar and non-motor features, medicines, stimulants, alcohol, metabolic and toxin context, prior evaluation, function and hazardous-activity safety. It preserves movement classification and diagnostic uncertainty, does not interpret patient video, and does not recommend medication changes.

The dedicated breast-symptom profile separates breast lump, pain, nipple discharge, nipple or skin change, inflammatory or lactation concern, injury or implant concern and prior-test or treatment follow-up from the generic lump workflow. It records exact site and laterality as separate Facts, requires a raw 0–10 NRS when breast pain is present, captures professional reproductive, lactation, personal and family cancer-risk, medicine, procedure, implant, imaging and treatment history, and preserves patient-observed lump features as distinct from a clinician examination. Severe systemic illness, uncontrolled bleeding, rapidly progressive infection, abscess concern and implant or trauma warning features can trigger escalation; new unexplained lump, concerning spontaneous discharge and new nipple or skin change remain time-sensitive clarification signals rather than inferred diagnoses. Its STOM and MRCM results are Build-Time metadata only, and inconclusive laterality reference-set status prevents asserted post-coordination.

The strengthened fever profile records measured and subjective fever context, measurement site, device and time, peak and trend, antipyretic response, hydration and urine output, age and life stage, pregnancy or postpartum context, immune vulnerability, recent procedures and devices, travel and exposure history, prior testing and treatment response, functional decline and patient goals. It requires a raw 0–10 NRS whenever pain accompanies fever and preserves proxy source, reliability, conflict and coded absent-data state. Age-specific, neurologic, respiratory, circulatory, dehydration, meningitis-combination, rash, cancer-treatment, pregnancy, travel and post-procedure warning features are explicit research-only escalation rules. The Runtime does not diagnose infection, calculate sepsis, NEWS2 or MEWS scores, or use STOM or MRCM as clinical authority.

The strengthened fatigue profile distinguishes sudden or acute change, sleep and daytime sleepiness, post-exertional worsening, mood or stress, systemic or weight change, cardiopulmonary or bleeding context, endocrine or metabolic symptoms, pregnancy or postpartum context, medicine or substance effects and child or adolescent proxy reporting. Its professional handoff records exact onset and pattern, physical versus cognitive fatigue, baseline and functional change, activity-response timing, sleep and driving risk, mood and suicide risk, bleeding, infection and exposure, obstetric context, complete medicines and allergies, prior testing and treatment response, information reliability and patient goals. Neurologic, consciousness, respiratory, bleeding, poisoning, immune, pregnancy or postpartum and paediatric warning features are research-only escalation rules. It does not diagnose anaemia, diabetes, depression, ME/CFS or cancer, and it does not select investigations.

The strengthened dizziness and syncope profile separates acute continuous dizziness, positional vertigo-like symptoms, postural presyncope, transient loss of consciousness, hearing or headache context, medicine or metabolic context, child proxy reporting and unresolved presentations. Its professional handoff preserves exact onset, posture and activity, episode pattern, function and driving risk, information source and witness reliability, pre-event sequence, appearance, colour, eye state, breathing, responsiveness, movement timing and distribution, tongue-bite site, event duration, injury and recovery, relevant cardiac, neurological, ear, metabolic, reproductive, medicine, occupational, family, prior-test and treatment context, and patient goals. Neurologic, acute vestibular, cardiorespiratory, injury, bleeding, toxic exposure, pregnancy or postpartum, paediatric and cardiac-syncope warning features are explicit research-only escalation rules. It records a raw 0–10 NRS when pain applies, but does not diagnose stroke, epilepsy, arrhythmia, benign positional vertigo or reflex syncope, calculate a diagnostic score, select a test or use Runtime terminology lookup as clinical authority.

The strengthened headache profile separates sudden or acute new headache, recurrent migraine-like features, pressure or tension-like symptoms, unilateral autonomic features, infection or systemic context, medicine or frequent acute-treatment exposure, pregnancy or postpartum context, child or proxy reporting and unresolved presentations. Its professional handoff preserves exact onset and speed to peak, first/worst/new or changed status, episode pattern, site and laterality, quality, mandatory raw 0–10 NRS, monthly headache and acute-medicine days, functional impact, associated and neurological symptom timing, autonomic features, menstrual relationship, medicine and substance exposure, pregnancy and professional obstetric history, child development and proxy reliability, previous emergency care, examinations, tests, treatment response, information conflict and patient goals. Sudden peak, focal neurological or consciousness change, meningeal combination, non-blanching rash, severe head injury, toxic exposure, painful red eye or vision loss, progressive or triggered headache, immune or malignancy context, pregnancy or postpartum warning features and paediatric warning features are explicit research-only escalation rules. The profile does not diagnose migraine, cluster headache, meningitis, subarachnoid haemorrhage, stroke, glaucoma, giant cell arteritis or pre-eclampsia, calculate a diagnostic score, select a test or use Runtime terminology lookup as clinical authority.

The strengthened focal weakness and numbness profile separates sudden unilateral symptoms, recurrent transient sensory events, progressive symmetric or single-limb change, spine or radiating-pain context, distal symmetric sensory change, position or compression-related symptoms, child or proxy reporting and unresolved presentations. Its professional handoff preserves last known well and exact onset circumstances, symptom sequence, recovery and trend, exact side and anatomical boundary, proximal or distal distribution, concrete motor-task loss, sensory quality, balance and dexterity, conditional mandatory raw 0–10 pain NRS, spine and compression context, medicine and occupational exposure, pregnancy or postpartum context, child development or regression, prior neurological episodes, examinations, tests, treatment response, source reliability, conflicts and patient goals. Sudden focal, face-arm-speech, vision, gait or consciousness change, resolved acute symptoms, seizure with persistent deficit, trauma-associated deficit, rapidly progressive symmetric weakness with respiratory or bulbar context, radiating back pain with bladder, bowel, sexual or saddle sensory change, rapid single-limb progression, fixed brief sensory events, and paediatric or infant warning features are explicit research-only escalation rules. The profile does not diagnose stroke, TIA, epilepsy, migraine, acute polyneuropathy, cauda equina syndrome, radiculopathy or peripheral neuropathy, calculate a diagnostic score, select a test or use Runtime terminology lookup as clinical authority.

The strengthened chest-pain profile separates acute or recent symptoms, recurrent exertional discomfort, pleuritic or respiratory context, positional or reproducible pain, meal or swallowing relationships, palpitations or collapse, pregnancy or thromboembolic context, child or proxy reporting and unresolved presentations. Its professional handoff preserves exact onset and last episode timing, episode frequency and trend, mandatory raw 0–10 NRS and pain frequency, exact site and radiation route, exertional threshold and relief timing, associated-symptom sequence, functional impact, cardiovascular and non-cardiac history, medicines and substances, pregnancy or postpartum context, prior emergency care, ECG, troponin, imaging and treatment response, reported observation provenance, information reliability, accessibility needs and patient goals. Current respiratory or consciousness compromise, persistent or pressure-like current pain, radiation, systemic features, syncope, sudden severe pain, neurological or limb-perfusion change, pleuritic pain with respiratory compromise, haemoptysis, high-risk aortic context, recent trauma or procedure, pregnancy or postpartum warning features, recent rest or minimal-exertion escalation and paediatric exertional or family warning features are explicit research-only escalation rules. The profile does not diagnose acute coronary syndrome, myocardial infarction, pulmonary embolism, acute aortic syndrome, pneumothorax, pericarditis or panic disorder, calculate a diagnostic score, select a test or use Runtime terminology lookup as clinical authority.

The strengthened bowel-symptom profile separates constipation or difficult passage, loose frequent or urgent stool, rectal bleeding or blood in stool, pain or distension, persistent change or systemic context, child or proxy reporting, medicine or post-procedure context and unresolved presentations. Its professional handoff preserves exact onset and baseline change, frequency and detailed stool form, urgency, nocturnal symptoms and incontinence, conditional mandatory pain frequency and raw 0–10 NRS, bleeding amount and relationship to stool, anal symptoms, hydration and intake, infection and antibiotic exposure, current medicines and bowel treatments, pregnancy or pelvic context, child meconium, growth, withholding and soiling history, prior episodes, examination, FIT, blood, stool, endoscopy and imaging results, treatment response, functional impact, information reliability and patient goals. Continuous or large-volume bleeding, collapse, acute severe abdominal pain, stool-and-flatus obstruction with distension and vomiting, black tarry stool, bloody diarrhoea, systemic inflammatory features, dehydration, persistent bleeding with weight loss and paediatric onset, growth, neurological or gross-distension warning features are explicit research-only escalation rules. The profile does not diagnose colorectal cancer, bowel obstruction, inflammatory bowel disease, infection or functional bowel disease, calculate referral eligibility, select a test or treatment, or use Runtime terminology lookup as clinical authority.

The strengthened medication-review profile separates reconciliation, effectiveness, suspected adverse effects, administration instructions, change requests, post-discharge reconciliation and unresolved review purposes. Its professional handoff preserves structured product identity, strength, formulation, dose, route, frequency, timing, indication, start date, prescriber and pharmacy, actual last use, stopped medicines and remaining stock, information source and conflict, adherence barriers and caregiver support, device technique and accessibility, allergy versus intolerance uncertainty, reaction and adverse-effect timing, dechallenge or re-exposure, benefit and monitoring targets, renal and hepatic context, opioid-sedative and respiratory risk, anticoagulant and diabetes-medicine context, sedation, falls, driving and work impact, care-transition changes, supply constraints, pregnancy or breastfeeding context and patient priorities. Existing research-only emergency rules continue to cover poisoning or extra dose, intentional overdose, airway or breathing compromise, opioid-associated reduced consciousness or slow breathing, severe anticoagulant bleeding, severe hypoglycaemia and blistering mucosal reactions without diagnosing a medication cause, selecting a medicine, recommending cessation or dose change, or prescribing naloxone.

The strengthened palpitations profile separates current or persistent symptoms, recurrent episodes, wearable or pulse records, exertional and postural contexts, medicine or substance timing, pregnancy, anaemia, thyroid or systemic contexts and unresolved presentations. Its professional handoff preserves the patient's perceived rhythm and location, first and latest episode timeline, frequency and duration range, abrupt or gradual onset and termination, pulse-measurement method and reliability, wearable ECG timestamp and symptom correlation, associated-symptom sequence and recovery, conditional mandatory chest-pain frequency and raw NRS, dyspnoea and syncope detail, exertional threshold, postural hydration and blood pressure context, stimulant and medicine timing, prior arrhythmia procedures or devices, structural heart history, relevant laboratory and obstetric context, detailed family history, prior ECG, ambulatory monitor, echo and emergency-care results, functional and occupational safety impact, information conflict and patient goals. Existing research-only escalation rules cover current palpitations with chest pain, severe dyspnoea, presyncope or persistence, syncope, focal neurological change, exertional syncope, worsening symptoms with known heart disease and young family sudden death without assigning a rhythm diagnosis, interpreting a wearable tracing, calculating a score or selecting treatment.

The strengthened cough profile separates acute, post-infectious or subacute, chronic or recurrent, productive or recurrent-infection, trigger or exposure, medicine, child or proxy, follow-up or result-review and unresolved contexts. Its professional handoff preserves patient-described dry or productive character, exact first and latest timeline, daily frequency and bout recovery, rapid worsening, day and night variation, sputum and haemoptysis detail, dyspnoea measurements and recovery, conditional mandatory chest-pain frequency and raw NRS, fever and associated-symptom sequence, cough triggers, swallowing and aspiration context, home and occupational exposures, inhaled substances and infectious contacts, medicine timing, relevant medical and recurrent-episode history, pregnancy, paediatric and older-adult context, prior imaging, respiratory testing, laboratory and microbiology results, treatment response, relevant vaccination status, functional impact, accessibility, information conflict and patient goals. Research-only escalation adds rapid significant worsening and severe systemic illness to the existing breathing, haemoptysis and chest-pain safety paths without assigning a cause, selecting a test or recommending treatment during collection.

The strengthened back-pain profile separates acute mechanical, radicular or neurological, trauma or fracture-risk, infection or systemic, night or persistent, urinary or pelvic, chronic follow-up, pregnancy or postpartum, child or proxy and unresolved contexts. Its professional handoff preserves the patient's wording, exact first and latest timeline, episode pattern, exact site and side, radiation, pain quality, mandatory frequency and raw 0–10 NRS, movement, posture, load, cough or strain and day or night pattern, concrete mobility, self-care, sleep, work and driving impact, neurological distribution and sequence, bladder, bowel, saddle and sexual-function baseline change, trauma mechanism, systemic and infection timeline, cancer, immune, bone-fragility, medicine and pregnancy context, previous spine history, examinations, imaging and laboratory result provenance, treatment response, occupational exposure, child or older-adult observations, accessibility, source reliability and patient goals. Existing research-only escalation rules remain authoritative for bilateral leg neurological symptoms, saddle sensory loss, new bladder, bowel or sexual change, progressive weakness, serious trauma, chest pain, fever with systemic or immune vulnerability, sudden severe pain and rapid worsening. The profile does not diagnose cauda equina syndrome, infection, malignancy or fracture, calculate a score, select imaging or treatment, or use Runtime terminology lookup as clinical authority.

The strengthened skin-complaint profile separates acute widespread or rapidly changing skin findings, local inflammatory or wound contexts, medicine or allergic timing, recurrent itch or rash, pigmented or persistent lesions, child or proxy reporting, follow-up or result review and unresolved presentations. Its professional handoff preserves the patient's wording, exact first and latest timeline, site, side and spread sequence, lesion count and reproducible dimensions, morphology and patient-described colour across skin tones, photo date, scale, lighting, focus and source, conditional mandatory pain frequency and raw 0–10 NRS, systemic and mucosal symptom sequence, structured medicine exposure and reaction interval, topical, occupational, travel, water, bite and contact exposures, drainage and open-skin detail, previous skin diagnosis, biopsy and cancer history, UV and family risk, pregnancy or hormone context, prior examination, dermoscopy, pathology and treatment response, function, accessibility, information conflict and patient goals. Research-only escalation adds new-medicine blistering or mucosal change, systemic circulatory warning features and hot swollen skin near the eye or nose to the existing airway, breathing, collapse, non-blanching rash, severe skin reaction, systemic infection and disproportionate-pain paths. The profile does not diagnose drug allergy, cellulitis, Stevens-Johnson syndrome, melanoma or another skin disease, interpret an image, select treatment or use Runtime terminology lookup as clinical authority.

The strengthened weight and constitutional-change profile separates unintentional or intentional weight loss, weight gain or fluid change, night sweats or fever, generalized weakness or function loss, eating or intake concern, child or proxy reporting, pregnancy or postpartum context, follow-up or result review and unresolved presentations. Its professional handoff preserves the patient's wording, exact first and latest timeline, usual, current, lowest and highest weight with date, scale, clothing and estimate provenance, reported height and BMI source without Runtime calculation, change rate and measurement context, weakness versus fatigue and concrete task loss, detailed intake, chewing and swallowing, upper and lower gastrointestinal symptoms, respiratory and systemic symptom sequence, conditional mandatory pain frequency and raw 0–10 NRS, structured medicine and substance timing, restriction, bingeing, vomiting, laxative, diuretic, excessive-exercise and water-loading behaviour, food access, medical, surgical, dental and family history, child growth source, pregnancy, puberty and older-adult context, previous test and treatment provenance, function, accessibility, information conflict and patient goals. Research-only escalation adds current self-harm or suicide danger, inability to swallow liquids or saliva, purging with physical instability, and unintentional weight loss with an unexplained mass or blood loss to the existing neurological, cardiopulmonary, dehydration and low-intake paths. The profile does not diagnose cancer, tuberculosis, an eating disorder, endocrine disease or malnutrition, calculate BMI or a screening score, select tests or nutrition treatment, or use Runtime terminology lookup as clinical authority.

The strengthened joint and limb complaint profile separates acute injury, a hot swollen single joint, mechanical or repetitive-load symptoms, multiple or inflammatory joints, calf or circulatory symptoms, child or proxy reporting, pregnancy or postpartum context, follow-up or result review and unresolved presentations. Its professional handoff preserves the patient's wording, exact anatomical structure and laterality, first and latest timeline, episode pattern, mandatory pain frequency and raw 0–10 NRS when pain applies, swelling and inflammatory sequence, active and assisted movement, mechanical features, structured injury mechanism and immediate function, wound and contamination context, neurological and distal circulation observations, unilateral-leg and cardiopulmonary sequence, infection, procedure, prosthesis and systemic context, multi-joint distribution, associated features, prior injury, diagnosis, surgery and rehabilitation, medicine timing, occupational and sports exposure, family and life-stage history, falls and baseline mobility, dated clinical-test, laboratory and imaging provenance, detailed function, accessibility, information conflict and patient goals. Research-only escalation adds acute unilateral calf or thigh symptoms with chest pain or severe dyspnoea to the existing deformity, open wound, inability to use the limb, post-injury sensory loss, distal vascular change, compartment, spinal, cardiopulmonary and hot-joint paths. The profile does not diagnose fracture, septic or inflammatory arthritis, venous thromboembolism, malignancy or another musculoskeletal condition, calculate a clinical score, interpret imaging or laboratory results, select treatment, or use Runtime terminology lookup as clinical authority.

The strengthened edema profile separates acute unilateral-leg, bilateral dependent, generalized fluid-change, face or upper-body, local inflammatory or wound, pregnancy or postpartum, medicine-related, chronic venous or lymphatic, child or proxy, follow-up or result-review and unresolved contexts. Its professional handoff preserves the patient's wording, exact onset and course, anatomical distribution and asymmetry, reproducible circumference, weight and vital-measurement provenance, observed pitting and skin change, conditional mandatory pain frequency and raw 0–10 NRS, cardiopulmonary symptom sequence, orthopnoea and nocturnal symptoms, unilateral-leg progression, immobility, surgery and travel timing, thromboembolic risk context, urine and abdominal changes, heart, kidney, liver, venous and lymphatic history, medicine timing, pregnancy details, previous episodes, examination, ECG, echo, ultrasound, imaging and laboratory result provenance, treatment response, function, child or older-adult observations, accessibility, source reliability and patient goals. Existing research-only escalation rules remain authoritative for severe dyspnoea, chest pain, haemoptysis, collapse or confusion, sudden face, tongue or throat swelling, pregnancy warning features, painful unilateral swelling, red-hot swelling with fever, rapid generalized swelling with markedly reduced urine and sudden severe swelling. The profile does not diagnose venous thromboembolism, heart, kidney or liver failure, pre-eclampsia, infection or lymphatic disease, calculate a score, interpret a test or recommend treatment during collection.

The strengthened hypertension follow-up profile separates blood-pressure or home-log review, medicine effectiveness or adherence, adverse-effect or postural symptoms, cardiovascular-risk and monitoring review, pregnancy or postpartum, child or proxy, result or plan follow-up and unresolved purposes. Its professional handoff preserves diagnosis and agreed-target provenance, recent reading series, arm, posture, rest, cuff, device and repeat-measurement method, home-log completeness and trend, symptom sequence, actual medicine regimen and last dose, missed or extra dose timing and access barriers, suspected adverse-effect chronology, nonprescription and stimulant exposure, cardiovascular, kidney, metabolic, sleep and family risk context, professional obstetric history, dated laboratory, ECG, eye and imaging result provenance, previous treatment response, functional and occupational impact, proxy reliability, information conflict, accessibility and patient goals. Existing research-only escalation rules remain authoritative for repeated severe blood pressure with neurological, cardiopulmonary or renal warning features, pregnancy or postpartum warning features, current syncope and paroxysmal symptom clusters. The profile does not diagnose hypertensive emergency or a secondary cause, calculate cardiovascular risk, interpret tests, set an individual treatment target or recommend starting, stopping or changing a medicine during collection.

It includes a profile-driven deterministic Builder, a Primary Care Reason for Encounter catalog, complete Fact-to-Question linkage within every package, shared Fact identity, versioned Source Manifests, source-specific refresh scheduling, deterministic Compiler, integrity-checked draft Knowledge Packages, evidence-preserving Clinical Memory with coded `dataAbsentReason`, package-driven and conditionally branched multi-turn Runtime, multi-domain warning-feature examples, limited English and Korean extraction, synthetic JSON Simulations, Evaluation, computed Coverage and automated validation. Pregnancy and postpartum history includes professional obstetric history and outcome details while preserving source notation and jurisdictional uncertainty. The dyspnea profile includes professional pre-visit handoff for onset and episode course, rest and exertional limitation, speaking/eating/sleep/self-care impact, respiratory observation and pulse-oximetry context, airway and infection features, orthopnoea and nocturnal symptoms, chest pain NRS, thromboembolic risk, cardiopulmonary and pregnancy history, medicines and inhaler technique, occupational or travel exposure, prior tests and treatment response. Its safety routing does not calculate Wells, PERC, NEWS2 or MEWS and does not infer a diagnosis. The abdominal-pain profile includes exact onset and episode course, anatomical site and side, radiation or migration, mandatory NRS and pain character, meal-bowel-urinary-movement-menstrual relationships, gastrointestinal and reproductive features, surgery and medicine history, prior tests and treatment response, functional impact, paediatric caregiver observations and patient goals. Its safety routing covers shock, sudden severe pain, rigid or distended abdomen, bleeding, obstruction, urinary retention, cardiopulmonary, pregnancy, testicular, vascular, post-procedure and paediatric warning features without calculating a diagnostic score, assigning a diagnosis or selecting imaging. The vomiting or diarrhoea profile includes professional handoff for onset and sequence, episode and 24-hour counts, vomit and stool characteristics, mandatory abdominal-pain NRS when pain is present, oral intake and urine context, functional impact, food-water-cluster and travel exposure, antibiotic timing, gastrointestinal and high-risk conditions, pregnancy or postpartum context, and caregiver-reported paediatric feeding, responsiveness and wet-nappy observations. Its safety routing covers bleeding, green vomit, poisoning, acute abdominal, neurologic, dehydration, pregnancy and paediatric warning features without inferring gastroenteritis, a pathogen, C. difficile infection or a dehydration score. Every compiled package also contains a research-only USCDI v6 interoperability Coverage result and applicable USCDI+ domain overlays. These overlays identify exchange gaps but never control clinical questions, completion or Safety Rules, and they do not replace Korean SNOMED CT, LOINC, KCD or HIRA bindings.

The public GitHub Pages Knowledge Action remains read-only. An optional separately deployed research-feedback Action accepts a fixed structured minimum dataset only after a distinct end-of-session agreement. It rejects answers, transcripts, files, free text, demographics, contact data, direct identifiers and unexpected fields; uses separate write and administrator credentials; applies bounded retention; and exposes aggregate statistics only. It cannot observe sessions abandoned before the feedback choice. Feedback remains evidence for Build-Time reproduction and never mutates Runtime knowledge.

This implementation demonstrates parts of the intended architecture.

It does not yet implement the complete Knowledge Factory.

Known gaps include:

- no live external Knowledge Acquisition connector or complete multi-domain Builder pipeline;
- no persistent graph database or general-purpose graph authoring workflow;
- Compiler and Knowledge Packages currently cover forty-six materialized Primary Care profiles and not the full Primary Care scope;
- no signed or production-approved Knowledge Package;
- Clinical Memory merge supports evidence and conflict but not the complete longitudinal policy;
- Runtime provenance is present but not yet production-grade;
- Simulation and Evaluation cover only the forty-six currently compiled profiles and not the full Primary Care scope;
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
