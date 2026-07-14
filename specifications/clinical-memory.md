# Clinical Memory Specification

Clinical Memory is the explicit, inspectable state accumulated during an interview.

## Required properties

A memory contains:

- session identifier;
- turn number;
- patient context;
- fact records;
- active interview patterns;
- unresolved contradictions;
- safety status;
- provenance and trace metadata.

## Fact states

Each fact record has one state:

- `known`: supported by patient or trusted source;
- `unknown`: explicitly asked but unresolved;
- `not_asked`: relevant but not yet explored;
- `conflicted`: two supported claims cannot both be accepted;
- `not_applicable`: excluded by a reviewed applicability rule.

When a value is missing, the Fact record carries `dataAbsentReason` using
`http://terminology.hl7.org/CodeSystem/data-absent-reason`. Runtime currently
uses `asked-unknown`, `asked-declined`, and `not-applicable`. A known Fact must
not carry `dataAbsentReason`; a missing value must not be represented as a
negative Fact.

`unknown` means the question was addressed but the value was not obtained. It
may close the question attempt, but it does not make the clinical Target
semantically satisfied. Target completion distinguishes resolved Facts from
Facts addressed with absent data.

Silence never creates a negative fact.

## Evidence

Every known or conflicted fact must point to evidence, normally:

- speaker;
- turn;
- exact or minimally normalized text;
- extraction method;
- confidence;
- provenance.

## Merge rules

1. New evidence does not overwrite old evidence.
2. Compatible evidence may increase confidence.
3. Incompatible evidence creates `conflicted`.
4. A correction may resolve a conflict only when the correcting statement is explicit.
5. Derived facts are stored separately from directly reported facts.
6. Pattern activation is not a diagnosis.

## Minimal turn output

After each patient turn, runtime must expose:

- facts added or changed;
- contradictions detected;
- active patterns;
- safety state;
- missing facts;
- selected next question;
- a concise machine-readable reasoning trace.
