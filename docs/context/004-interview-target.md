# Interview Target

Version: 0.1 (Draft)

---

# Purpose

This document defines Interview Target.

Interview Target is the executable unit of the Clinical Interview Knowledge Platform.

Clinical Intent defines **why** the interview should proceed.

Interview Target defines **what information must be obtained**.

Questions are generated from Interview Targets.

Facts are collected to satisfy Interview Targets.

---

# Definition

Interview Target is an atomic clinical objective.

An Interview Target is considered complete when sufficient information has been collected to satisfy its completion criteria.

Interview Targets are reusable across multiple

- Encounter Contexts
- Reasons for Encounter
- Clinical Intents
- Clinical Groups
- Presentations

Interview Targets never belong to a diagnosis.

---

# Relationship

```
Encounter Context

+

Reason for Encounter

↓

Clinical Intent

↓

Interview Target

↓

Fact

↓

Question
```

Clinical Intent creates Interview Targets.

Interview Targets consume Facts.

Questions collect Facts.

---

# Design Principles

Interview Targets must be

- Atomic
- Reusable
- Observable
- Testable
- Measurable

Interview Targets must never contain multiple unrelated objectives.

---

# Atomicity

Good

```
Determine symptom duration
```

Bad

```
Assess cough history
```

Good

```
Determine smoking status
```

Bad

```
Assess social history
```

Large objectives are decomposed into smaller Interview Targets.

---

# Examples

Examples include

Determine symptom duration

Determine symptom onset

Determine symptom severity

Determine symptom progression

Determine fever presence

Determine dyspnea severity

Determine sputum characteristics

Determine hemoptysis

Determine smoking status

Determine alcohol consumption

Determine occupational exposure

Determine medication use

Determine vaccination status

Determine allergy history

Determine previous episodes

Determine family history

Determine functional limitation

Determine patient concern

Determine patient expectation

---

# Interview Target Lifecycle

```
Inactive

↓

Generated

↓

Prioritized

↓

Question Generated

↓

Information Collected

↓

Satisfied

↓

Closed
```

Interview Targets remain visible after completion.

Closed Interview Targets contribute to Clinical Memory.

---

# Target Priority

Each Interview Target has a dynamic priority.

Priority depends upon

Clinical Intent

Safety

Urgency

Missing information

Information gain

Interview burden

Redundancy

Target priority changes continuously.

---

# Required Facts

Each Interview Target defines required Facts.

Example

Interview Target

```
Determine symptom duration
```

Required Facts

```
symptom.duration.value

symptom.duration.unit
```

Example

Interview Target

```
Determine smoking status
```

Required Facts

```
patient.smoking.current

patient.smoking.previous
```

---

# Optional Facts

Interview Targets may define optional Facts.

Optional Facts increase confidence but are not mandatory.

Example

Determine smoking status

Optional

Pack-years

Quit date

Passive exposure

---

# Completion Rules

Every Interview Target contains explicit completion criteria.

Example

Determine fever

Completed when

```
Present

OR

Absent

OR

Unknown after clarification
```

Completion must be deterministic.

---

# Failure States

Interview Targets may fail.

Examples

Patient declined

Information unavailable

Communication barrier

Insufficient evidence

Contradictory information

Failures remain visible.

Failures never silently disappear.

---

# Clinical Memory

Interview Targets never store data.

Clinical Memory stores Facts.

Interview Targets consume Clinical Memory.

Example

Clinical Memory

```
symptom.duration = 3 days
```

Interview Target

```
Determine symptom duration

↓

Satisfied
```

---

# Question Generation

Questions are generated from Interview Targets.

Interview Targets never define exact wording.

Instead they define

Purpose

Required Facts

Optional Facts

Completion Rules

Question Templates produce the final wording.

---

# Question Selection

Multiple Interview Targets may be active simultaneously.

Question selection attempts to maximize

Clinical usefulness

Safety

Information gain

Coverage

while minimizing

Patient burden

Repeated questioning

Question wording is independent from Interview Target.

---

# Reusability

Interview Targets are reused.

Example

Determine smoking status

is applicable to

Cough

Chest pain

COPD follow-up

Health check

Medication review

Smoking cessation

No duplication is permitted.

---

# Mapping

Interview Targets may contain mappings.

Examples

SNOMED CT

FHIR

ICPC-2

Mappings never define Interview behavior.

Mappings support interoperability.

---

# Simulation

Every Interview Target requires Simulation coverage.

Simulation includes

Positive

Negative

Unknown

Declined

Contradictory

Missing

Simulation is mandatory.

---

# Evaluation

Every Interview Target is evaluated.

Metrics include

Completion rate

Question efficiency

Information gain

Simulation coverage

Fact completeness

Reasoning consistency

---

# Provenance

Every Interview Target requires provenance.

Minimum provenance

Builder

Knowledge Package

Medical Sources

Review Status

Version

Timestamp

---

# Repository Rules

Interview Targets are stored independently.

Interview Targets must not reference diagnoses.

Interview Targets must not contain patient-specific information.

Interview Targets must be reusable.

Interview Targets are immutable within a released Knowledge Package.

---

# Examples

Example

Interview Target

```
Determine symptom duration
```

Required Facts

```
symptom.duration.value

symptom.duration.unit
```

Possible Questions

```
When did it start?

How long have you had it?

Did it begin today?

Did it start gradually?
```

---

Example

Interview Target

```
Determine smoking status
```

Required Facts

```
patient.smoking.current
```

Optional Facts

```
pack_year

quit_date

passive_smoking
```

Possible Questions

```
Do you currently smoke?

Have you ever smoked?

When did you stop?

Approximately how much did you smoke?
```

---

# Coverage

Coverage is measured at the Interview Target level.

Repository maturity depends upon

Number of reusable Interview Targets

Simulation coverage

Fact reuse

Question reuse

Knowledge completeness

Interview Targets are one of the primary units of repository growth.

---

# Final Principle

Interview Targets are the execution layer of the Clinical Interview Knowledge Platform.

Clinical Intent determines why.

Interview Targets determine what.

Facts determine whether the objective has been achieved.

Questions are only the interface presented to the patient.
