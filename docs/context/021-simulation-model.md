# Simulation Model

Version: 0.1 (Draft)

---

# Purpose

This document defines Simulation.

Simulation is a first-class repository component used to validate interview knowledge before release.

Every interview capability requires Simulation.

---

# Core Principle

No Simulation.

No release.

Knowledge that cannot be tested is incomplete.

---

# Position

```text
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
Knowledge Package
```

Simulation precedes deployment.

---

# Simulation Scope

Simulation validates

- Encounter Context
- Reason for Encounter
- Clinical Intent activation
- Interview Target generation
- Fact collection
- Question selection
- priority
- safety
- contradiction handling
- completion
- stop behavior
- mapping
- Coverage

---

# Simulation Object

Every Simulation contains

- identifier
- version
- purpose
- package scope
- Encounter Context
- Reason for Encounter
- persona
- initial statement
- hidden state
- disclosure behavior
- response behavior
- expected state transitions
- expected Facts
- expected Questions
- forbidden assertions
- expected stop state
- provenance

---

# Hidden State

Hidden state represents information known to the simulator but not initially known to Runtime.

Each hidden Fact declares

- value
- state
- disclosure conditions
- uncertainty
- consistency behavior
- correction behavior
- provenance

Runtime never reads hidden state directly.

---

# Disclosure Behavior

A simulated patient may disclose information

- in the open narrative
- only when asked directly
- when asked neutrally
- after clarification
- after trust conditions
- never
- with uncertainty
- with contradiction
- through correction

This tests Question quality and sequence.

---

# Simulation Categories

Mandatory categories include

- positive
- negative
- ambiguous
- conflicting
- missing information
- explicit refusal
- correction
- boundary value
- multilingual
- mode-specific
- safety escalation
- ordinary routine case
- long interview
- maximum-turn stop
- human handoff

---

# Positive Case

A positive case demonstrates that expected knowledge activates and completes.

It does not prove diagnosis.

---

# Negative Case

A negative case ensures unrelated rules do not activate.

Negative tests are required for safety and Hypothesis boundaries.

---

# Ambiguous Case

An ambiguous case tests whether Runtime preserves uncertainty and requests clarification.

Runtime must not normalize beyond evidence.

---

# Conflicting Case

A conflicting case tests

- evidence preservation
- conflict creation
- clarification priority
- explicit resolution
- history retention

---

# Missing Information Case

A missing information case tests whether Runtime can stop with unresolved Targets without inventing Facts.

---

# Safety Case

A safety case declares

- triggering Fact
- expected safety level
- permitted clarification
- expected escalation
- forbidden routine Questions
- expected stop or handoff

Safety cases require reviewed expected behavior for production packages.

---

# Forbidden Assertions

Every Simulation may list outputs that must never occur.

Examples

- unsupported diagnosis
- unsupported causation
- absence inferred from silence
- hidden Hypothesis exposure
- treatment recommendation outside scope
- fabricated Fact

Forbidden assertion failure blocks release.

---

# Expected Trace

Simulation may validate not only output but decision path.

Expected trace may include

- rule matched
- Intent activated
- Target selected
- priority reason
- suppression reason
- safety transition
- stop reason

Exact wording should be tested separately from semantic behavior.

---

# Determinism

Given the same

- Simulation
- Knowledge Package
- Runtime version
- seeded model configuration

semantic results must be reproducible.

Probabilistic components require fixed seeds and tolerance policies.

---

# Simulation Independence

Simulation definitions belong to the repository.

They do not belong to one Runtime implementation.

Any compliant Runtime should be able to execute the same Simulation contract.

---

# Generated Simulation

AI-generated Simulation defaults to unreviewed.

Generated cases may expand coverage.

They cannot replace reviewed clinical safety cases.

---

# Simulation Provenance

Every case records

- creator
- creation time
- source knowledge
- linked graph objects
- review status
- package version
- generator and prompt when applicable
- revision history

---

# Final Principle

Simulation is executable evidence that interview knowledge behaves as intended.

Every capability must be demonstrable before it becomes deployable.
