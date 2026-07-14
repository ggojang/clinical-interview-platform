# Reasoning Loop

Version: 0.1 (Draft)

---

# Purpose

This document defines the Runtime Reasoning Loop.

The Reasoning Loop applies compiled knowledge to Clinical Memory after every encounter event.

It does not perform open-ended diagnosis.

It does not search for medical knowledge.

---

# Core Loop

```text
Observe
  ↓
Extract
  ↓
Normalize
  ↓
Merge
  ↓
Validate
  ↓
Check Safety
  ↓
Activate Intent
  ↓
Generate Target
  ↓
Identify Gaps
  ↓
Generate Candidate Actions
  ↓
Prioritize
  ↓
Act
  ↓
Trace
```

---

# 1. Observe

Runtime captures

- actor
- exact input
- mode
- timestamp
- event identifier
- turn
- source metadata

Observation does not interpret meaning.

---

# 2. Extract

Extraction proposes Fact candidates.

A candidate contains

- proposed Fact identifier
- proposed value
- evidence span
- assertion type
- certainty
- extractor identity
- extraction version

Extraction never merges state directly.

---

# 3. Normalize

Normalization maps supported evidence into canonical representation.

Normalization preserves

- raw wording
- uncertainty
- temporal precision
- negation
- units
- source language

Unsupported normalization creates clarification, not invented precision.

---

# 4. Merge

Validated candidates are merged into Clinical Memory.

Merge is evidence-preserving.

Compatible evidence accumulates.

Incompatible evidence creates conflict.

---

# 5. Validate

Validation checks

- Fact identifier exists
- value type is allowed
- state transition is valid
- provenance exists
- package version matches
- evidence is present
- applicability is valid

Invalid candidates are rejected with a reason.

---

# 6. Check Safety

Safety rules run after every memory change.

Safety may

- raise priority
- request bounded clarification
- suppress routine Targets
- initiate escalation
- stop the interview

Safety decisions cite triggering evidence and rule version.

---

# 7. Activate Clinical Intent

Encounter Context, Reason for Encounter and new Facts may activate Intents.

Activation is dynamic.

One encounter may have multiple active Intents.

Intent activation is not diagnosis.

---

# 8. Generate Interview Targets

Active Intents generate reusable Interview Targets.

Targets are deduplicated by semantic identifier.

The same Target may satisfy multiple Intents.

---

# 9. Identify Gaps

Runtime compares Target requirements with Clinical Memory.

A gap may be

- missing Fact
- unresolved Fact
- conflicted Fact
- insufficient precision
- expired prior Fact
- unavailable source

Each gap has a typed reason.

---

# 10. Generate Candidate Actions

Candidate actions include

- ask Question
- request clarification
- confirm summary
- perform escalation
- stop
- hand off

Every candidate references

- Clinical Intent
- Interview Target
- Fact
- rule
- expected information gain

---

# 11. Prioritize

Priority considers

- safety
- urgency
- Encounter Context
- required status
- information gain
- discrimination
- patient burden
- repetition
- redundancy
- time budget

Priority components remain visible.

---

# 12. Act

Runtime selects one primary action.

The action must be valid for the current state.

Question wording may be rendered for language and mode.

Semantic purpose does not change.

---

# 13. Trace

Runtime records

- input event
- Fact changes
- conflicts
- rules evaluated
- rules matched
- Intents changed
- Targets changed
- candidate actions
- scores
- selected action
- safety state
- stop state

---

# Determinism Boundary

Models may propose

- Fact candidates
- evidence spans
- approved wording variants
- patient-facing summaries

Compiled knowledge determines

- allowed Facts
- rule logic
- safety precedence
- target requirements
- completion
- priority policy
- stop policy

---

# Re-evaluation

The entire active decision state is re-evaluated after every event.

Previous results may remain valid.

They are never blindly reused.

New evidence may

- activate an Intent
- close an Intent
- reopen a Target
- create conflict
- change priority
- trigger safety escalation

---

# Idempotency

Reprocessing the same event with the same state and package must produce the same result.

Duplicate event identifiers must not create duplicate evidence or Questions.

---

# Maximum Turn Policy

Maximum turn is a compiled or session policy.

Reaching the limit creates a stop candidate.

Safety may override ordinary turn limits.

The stop reason records unresolved Targets.

---

# Human Handoff

A human may take over at any point.

Handoff records

- reason
- current safety state
- unresolved Targets
- latest evidence
- package version
- trace reference

Runtime does not continue autonomously after completed handoff.

---

# Final Principle

The Reasoning Loop is a transparent state transition system.

Every action begins with evidence and ends with a trace.
