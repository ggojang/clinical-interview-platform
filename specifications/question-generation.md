# Question Generation Specification

Questions are generated from explicit information gaps, conflicts, or safety rules.

## Candidate classes

Priority order:

1. urgent safety clarification;
2. contradiction resolution;
3. required pattern fact;
4. high-value optional fact;
5. contextual refinement;
6. summary confirmation.

## Default score

The starter runtime uses:

`score = safety + contradiction + required + information_gain - burden - repetition`

Recommended weights:

- safety critical: +100
- contradiction: +90
- required fact: +70
- high information gain: +20
- repeated equivalent question: -80
- compound question: -15
- leading wording: -30

## Wording rules

- Ask one primary clinical question at a time.
- Prefer neutral, plain language.
- Avoid suggesting the expected answer.
- Do not expose hidden diagnostic hypotheses.
- Reuse patient wording where helpful.
- Offer examples only when the patient appears not to understand.
- Do not display Question sequence numbers; track Questions by stable identifier.
- Reserve numeric input for answer options in the immediately preceding Question.
- Use sequential `1=yes, 2=no, 3=unknown, 4=decline` only for binary yes/no Questions.
- For N enumerated domain choices, use `1..N`, followed by `N+1=unknown` and `N+2=decline`.
- Validate option-number uniqueness before display.
