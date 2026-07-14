# Clinical Memory

Version: 0.1 (Draft)

---

# Purpose

This document defines Clinical Memory.

Clinical Memory is the explicit, inspectable session state accumulated during one clinical interview.

Clinical Memory is not the Knowledge Graph.

Clinical Memory is not a diagnosis list.

Clinical Memory is encounter-specific evidence and state.

---

# Position

```text
Knowledge Package
        ↓
Runtime
        ↓
Clinical Memory
        ↓
Reasoning Trace
        ↓
FHIR Export
```

The Knowledge Package defines allowed semantics.

Clinical Memory records encountered evidence.

---

# Core Principle

Nothing important remains only inside a prompt.

All clinically relevant state must be represented explicitly.

---

# Memory Contents

Clinical Memory contains

- session identity
- Encounter Context
- Reason for Encounter
- turn number
- participants
- patient context
- Fact records
- active Clinical Intents
- active Interview Targets
- contradictions
- safety state
- asked Questions
- declined Questions
- stop state
- provenance
- trace references

---

# Fact Record

Every Fact record contains

- Fact identifier
- state
- value
- raw evidence
- normalized evidence
- assertion
- certainty
- source actor
- source event
- extraction method
- package version
- provenance
- history

---

# Fact States

Allowed states are

- known
- unknown
- not_asked
- conflicted
- not_applicable

Silence never creates a negative Fact.

Missing is not the same as false.

Unknown is not the same as absent.

When an expected value is unavailable, Clinical Memory records a separate
`dataAbsentReason` coding. Examples include `asked-unknown` when the patient was
asked but does not know, `asked-declined` when the patient declines to answer,
and `not-applicable` when a reviewed rule excludes the Fact. The coding system
is `http://terminology.hl7.org/CodeSystem/data-absent-reason`.

A Fact with `dataAbsentReason` is addressed but not known. It may end repeated
questioning, but it never counts as positive or negative clinical evidence.

---

# Evidence

Evidence is append-only.

Evidence includes

- speaker or source
- event identifier
- turn
- exact or minimally transformed text
- structured source reference
- assertion status
- extraction method
- confidence
- timestamp
- provenance identifier

A normalized value never replaces raw evidence.

---

# Merge Rules

1. New evidence does not overwrite previous evidence.
2. Compatible evidence may strengthen a Fact.
3. Incompatible evidence creates a conflict.
4. Explicit correction may resolve a conflict.
5. Resolution preserves all prior evidence.
6. Derived Facts remain separate from directly reported Facts.
7. Pattern or Intent activation never creates a Fact.
8. Absence requires explicit negative evidence or a reviewed derivation rule.

---

# Corrections

A correction requires an explicit correction event.

Example

```text
Patient: It started five days ago.
Patient: Sorry, I meant five weeks ago.
```

Clinical Memory preserves both statements.

The second statement may supersede the current normalized value.

The first statement remains in history.

---

# Conflicts

A conflict record contains

- involved Fact
- incompatible evidence identifiers
- conflict type
- detected rule
- detection turn
- resolution status
- resolution evidence
- provenance

Conflicts generate clarification before routine completeness work unless safety overrides.

---

# Derived Facts

Derived Facts require

- derivation rule identifier
- source Fact identifiers
- source evidence identifiers
- derivation timestamp
- package version
- confidence policy
- provenance

Derived Facts are never presented as directly patient-reported.

---

# Intent State

Each Clinical Intent contains

- identifier
- lifecycle state
- activation evidence
- priority components
- active Targets
- satisfied Targets
- closure reason
- activation and closure turns
- provenance

Closed Intents remain in memory.

---

# Target State

Each Interview Target contains

- identifier
- lifecycle state
- required Facts
- optional Facts
- missing Facts
- completion result
- failure state
- priority
- provenance

A Target is satisfied by Facts, not by asking a Question.

---

# Question History

Question history records

- Question Template identifier
- rendered wording
- linked Target
- linked Fact
- turn
- response event
- outcome
- repetition group
- provenance

Question history is used to prevent repetition.

---

# Safety State

Safety state contains

- level
- active safety rules
- triggering evidence
- permitted clarification
- escalation action
- transition history
- resolution status
- provenance

Safety history is append-only.

---

# Stop State

Stop state contains

- stopped flag
- stop reason
- rule identifier
- actor
- timestamp
- handoff target
- unresolved Targets
- safety state
- provenance

---

# Memory Events

Clinical Memory evolves through events.

Examples

- encounter_started
- evidence_observed
- fact_candidate_created
- fact_merged
- conflict_detected
- conflict_resolved
- intent_activated
- target_activated
- question_asked
- safety_changed
- escalation_started
- interview_stopped

Events are ordered and immutable.

---

# Reconstruction

Current state must be reconstructable from

- initial state
- ordered events
- Knowledge Package version

Snapshot storage is permitted for performance.

Snapshots never replace the event history.

---

# Longitudinal Memory

Previous Clinical Memory may be imported into a new encounter.

Imported memory must preserve

- original encounter identity
- original package version
- original source
- original timestamps
- review status
- import event provenance

Prior Facts are not automatically current Facts.

Freshness and applicability rules determine reuse.

---

# Privacy

Clinical Memory may contain sensitive information.

Implementations must enforce

- minimum necessary collection
- access control
- encryption
- retention policy
- deletion policy
- audit logging
- jurisdictional requirements

Knowledge Acquisition never receives identifiable Clinical Memory.

---

# FHIR Export

FHIR Export is a projection.

Clinical Memory remains the session source of truth.

Export must preserve links to

- internal Fact identifiers
- evidence
- package version
- mapping version
- provenance

FHIR structure never controls internal memory semantics.

---

# Validation

Clinical Memory validation checks

- required identity
- valid Fact states
- resolved references
- ordered events
- immutable evidence
- valid lifecycle transitions
- valid safety state
- package compatibility
- provenance completeness

---

# Final Principle

Clinical Memory makes the interview state visible.

It preserves evidence, uncertainty, conflict and decision history without hiding them inside conversation text.
