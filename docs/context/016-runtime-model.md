# Runtime Model

Version: 0.1 (Draft)

---

# Purpose

This document defines the Interview Runtime.

Runtime executes a compiled Knowledge Package for one encounter.

Runtime is not the product.

Runtime is one consumer of repository knowledge.

---

# Core Principle

Runtime never learns.

Runtime never searches.

Runtime never discovers.

Runtime executes compiled knowledge.

---

# Runtime Inputs

Runtime accepts

- one compatible Knowledge Package
- Encounter Context
- Reason for Encounter
- available prior Clinical Memory
- patient or caregiver utterances
- approved structured clinical data
- Runtime configuration
- session policy

Runtime never accepts live medical-source content.

---

# Runtime Outputs

Runtime produces

- Clinical Memory
- active Clinical Intents
- active Interview Targets
- collected Facts
- contradictions
- safety state
- selected Question
- escalation transition
- stop reason
- Reasoning Trace
- optional FHIR Export

Runtime output is session knowledge.

It is not repository knowledge.

---

# Runtime Lifecycle

```text
Initialize
    ↓
Load Package
    ↓
Validate Compatibility
    ↓
Create Encounter
    ↓
Observe Input
    ↓
Update Clinical Memory
    ↓
Execute Rule Graph
    ↓
Select Action
    ↓
Persist Trace
    ↓
Continue / Escalate / Stop
```

---

# Initialization

Before interaction Runtime must

- verify package integrity
- verify package compatibility
- record package identity
- initialize Encounter Context
- initialize Reason for Encounter
- load permitted prior information
- establish privacy and retention policy
- create session provenance
- create initial Clinical Memory

Failure during initialization prevents interview execution.

---

# Package Isolation

A Runtime session is bound to one package version.

The active package cannot change during the encounter.

Package upgrade requires

- a new session
- or an explicit migration event
- compatibility validation
- provenance preservation

Silent package replacement is prohibited.

---

# Turn Processing

For every patient input Runtime performs

1. observe
2. extract supported Fact candidates
3. preserve evidence
4. normalize within compiled constraints
5. merge into Clinical Memory
6. validate state
7. detect contradictions
8. evaluate safety
9. update Clinical Intents
10. update Interview Targets
11. identify missing Facts
12. generate Question candidates
13. prioritize candidates
14. select one primary action
15. record Reasoning Trace

---

# Runtime Boundaries

Runtime may

- evaluate compiled rules
- update encounter state
- select approved Question Templates
- adapt wording within approved constraints
- create FHIR representations
- emit feedback events

Runtime may not

- edit the Knowledge Graph
- create repository Facts
- change rule weights
- query external medical sources
- promote generated knowledge
- infer diagnoses from active patterns
- learn new medical behavior from sessions
- modify the Knowledge Package

---

# Model Use

A model may assist with

- evidence span detection
- candidate Fact extraction
- language understanding
- approved Question wording
- summarization of traceable Facts

A model may not define

- allowed Fact identifiers
- safety precedence
- rule activation
- completion criteria
- package scope
- provenance requirements

All model output is validated against compiled knowledge.

---

# One Action at a Time

The default Runtime emits one primary interview action.

Examples

- ask one Question
- request one clarification
- provide one escalation instruction
- stop and hand off

Compound questions reduce traceability and are discouraged.

---

# Safety Behavior

Safety evaluation occurs after every state update.

When an escalation rule matches Runtime

- records the triggering evidence
- records the rule identifier and version
- suppresses incompatible routine actions
- performs only permitted clarification
- transitions to the compiled escalation action
- preserves the complete trace

Runtime never minimizes a safety signal.

---

# Failure Behavior

Runtime fails closed when

- package integrity fails
- package compatibility fails
- memory state is invalid
- a required rule is unsupported
- a safety action cannot execute
- provenance cannot be recorded

Failing closed means

- preserve existing Clinical Memory
- stop unsafe progression
- record a typed error
- request approved human handoff
- never invent replacement logic

---

# Persistence

Runtime state persistence must preserve

- append-only evidence
- turn order
- package identity
- rule versions
- state transitions
- contradictions
- corrections
- stop reason
- provenance

Persistence format is implementation-dependent.

Semantics are not.

---

# Concurrency

One encounter has one ordered event stream.

Concurrent inputs must be serialized before state evaluation.

Each event receives

- stable identifier
- timestamp
- actor
- source
- sequence number

Out-of-order events are retained and reconciled explicitly.

---

# Runtime Independence

The Runtime is independent from

- model provider
- database
- user interface
- deployment platform
- FHIR server
- terminology server
- programming language

A compliant Runtime produces equivalent decisions from the same package and state.

---

# Observability

Runtime exposes

- package version
- current turn
- active Intents
- active Targets
- Fact changes
- safety state
- selected action
- applied rules
- priority components
- stop reason
- errors

Observability never exposes secrets or unnecessary patient data.

---

# Runtime Provenance

Every Runtime artifact identifies

- Runtime version
- Knowledge Package version
- session identifier
- event identifier
- actor
- source evidence
- evaluated rule identifiers
- timestamps

---

# Repository Rules

Runtime

- executes compiled knowledge only
- does not access medical sources
- does not mutate packages
- preserves evidence
- evaluates safety every turn
- emits one traceable action
- fails closed
- records provenance
- exports only approved representations

---

# Final Principle

The Knowledge Factory becomes smarter.

Runtime becomes simpler.

Runtime is a deterministic executor of compiled interview knowledge.
