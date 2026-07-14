# Fact Extraction Specification

Fact extraction converts utterance evidence into candidate fact records.

## Rules

- Extract only what the utterance supports.
- Preserve uncertainty words such as “maybe,” “about,” and “I think.”
- Separate multiple facts from one sentence.
- Do not normalize beyond available evidence.
- Do not infer clinical absence from omission.
- Do not infer causality from temporal proximity.
- Patient self-diagnosis is recorded as a patient belief, not a confirmed condition.
- Negation must have an explicit linguistic trigger.
- Time expressions must retain raw text when exact normalization is uncertain.

## Candidate lifecycle

`candidate → validated → merged` or `candidate → rejected`

A candidate includes:

- proposed fact ID;
- proposed value;
- evidence span;
- assertion type;
- confidence;
- extractor identity.

## Confirmation

Ask a confirmation question when:

- the value is safety-critical and ambiguous;
- normalization would materially change meaning;
- the claim conflicts with memory;
- the patient used a vague quantifier that affects priority.
