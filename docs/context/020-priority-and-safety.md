# Priority and Safety

Version: 0.1 (Draft)

---

# Purpose

This document defines Runtime priority and safety behavior.

Priority selects the next action.

Safety constrains which actions are allowed.

Safety has precedence over routine completeness.

---

# Core Principle

Safety first.

Common conditions efficiently.

No unsupported diagnosis.

---

# Priority Inputs

Priority is influenced by

- safety level
- urgency
- Encounter Context
- Clinical Intent priority
- Target requirement
- contradiction
- information gain
- discrimination
- commonness
- patient burden
- repetition
- redundancy
- time constraint

Every component is explicit.

---

# Default Priority Classes

1. emergency escalation
2. urgent escalation
3. urgent safety clarification
4. contradiction affecting safety
5. required safety Target
6. required active Target
7. high-value optional Target
8. contextual refinement
9. summary confirmation
10. stop or handoff

A compiled context policy may refine this order.

---

# Minimal Safety Gate

Safety precedence does not mean asking every rare-danger Question before ordinary history.

The default approach is

1. establish essential temporal or severity context
2. perform the minimum safety screen required by scope
3. continue with high-value common Targets when routine
4. recheck safety after every new Fact
5. escalate immediately when a reviewed rule matches

---

# Safety Levels

Supported levels

- routine
- clarify
- urgent
- emergency

Each level declares

- allowed Questions
- maximum clarification
- escalation action
- routine suppression
- response time expectation
- handoff requirement

---

# Safety Rule

Every safety rule contains

- identifier
- trigger
- required Fact states
- evidence threshold
- safety level
- permitted clarification
- escalation action
- suppression behavior
- review status
- provenance
- version

---

# Review Boundary

Generated or unreviewed safety knowledge may be tested.

It must not be enabled in a production package.

Production enablement requires

- clinical review
- wording review
- jurisdiction review
- simulation pass
- governance approval
- release record

---

# Priority Formula

A package may use a transparent formula.

```text
score =
  safety
  + urgency
  + context_fit
  + required
  + information_gain
  + discrimination
  + commonness
  - burden
  - repetition
  - redundancy
```

Weights are versioned policy.

Runtime cannot change them.

---

# Tie Breaking

Tie breaking is deterministic.

Default order

1. higher safety level
2. higher Intent priority
3. required before optional
4. higher information gain
5. lower burden
6. stable identifier order

Random tie breaking is prohibited unless explicitly seeded and simulated.

---

# Contradictions

Contradictions receive high priority when they affect

- safety
- eligibility
- severity
- temporal order
- medication exposure
- completion

Routine contradictions may wait behind urgent safety action.

---

# Patient Burden

Burden includes

- sensitive topic
- repeated Question
- complex wording
- long response
- cognitive load
- emotional impact
- accessibility barrier

Burden reduces priority but never suppresses necessary emergency action.

---

# Escalation

When escalation triggers Runtime

1. records triggering evidence
2. records matched rule and version
3. stops incompatible routine planning
4. asks only permitted clarification
5. renders approved escalation wording
6. initiates the configured transition
7. records handoff or stop
8. preserves the complete trace

Runtime does not diagnose the cause of the safety signal.

---

# Safety Failure

If an escalation action cannot execute

- preserve Clinical Memory
- raise a Runtime safety error
- stop routine questioning
- request human handoff
- record provenance
- never substitute improvised advice

---

# Common Cause Differentiation

After the safety gate, routine priority may favor common explanatory groups.

Clinical Groups may guide discrimination.

Hypotheses never directly generate Questions.

The allowed path remains

```text
Clinical Intent
        ↓
Interview Target
        ↓
Fact
        ↓
Question
```

---

# Trace

Priority trace contains

- candidates
- component scores
- suppression reasons
- tie-breaking
- selected action
- safety state
- applicable policy
- package version

A reviewer must be able to reconstruct the decision.

---

# Simulation

Priority and safety Simulation includes

- emergency positive case
- emergency negative case
- ambiguous red flag
- conflicting red flag
- routine common case
- priority tie
- patient refusal
- escalation failure
- repeated safety Question
- context-specific behavior

---

# Final Principle

Safety restricts the action space.

Priority chooses within the permitted action space.

Both are compiled knowledge, not Runtime improvisation.
