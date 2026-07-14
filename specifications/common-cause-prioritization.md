# Common-Cause Prioritization Specification

The interviewer must balance two duties:

1. detect time-sensitive warning signs;
2. efficiently explore likely, common explanations.

Safety precedence does not mean asking every rare-danger question before ordinary history. The runtime performs a **minimal safety gate**, then follows the most relevant common-cause branch unless a warning sign is present.

## Sequence

1. Establish duration if absent.
2. Ask a minimal respiratory safety question, normally breathing difficulty.
3. If safety remains routine, activate duration-appropriate common-cause patterns.
4. Ask the highest-value discriminator within those patterns.
5. Re-check safety whenever new evidence appears.
6. Explore less common patterns only after common branches are insufficient or contradicted.

## Duration branches

- acute: less than 3 weeks;
- subacute: 3 through 8 weeks;
- chronic: more than 8 weeks.

These boundaries are configurable knowledge, not hard-coded clinical truth.

## Acute cough branch

Prioritize common upper-respiratory features:

- runny or blocked nose;
- sore throat;
- sneezing;
- recent sick contact;
- fever or systemic symptoms;
- trajectory: improving, stable, or worsening.

The pattern represents an interview hypothesis such as `infectious.common_cold`, not a confirmed diagnosis.

## Chronic cough branch

Prioritize common explanatory patterns, potentially in parallel:

- upper-airway cough syndrome features;
- asthma-related features;
- reflux/GERD-related features;
- medication exposure such as ACE inhibitors;
- smoking and chronic airway exposure.

## Attribution rule

A matching pattern raises a hypothesis score. It never establishes causation or diagnosis.

For GERD-related cough specifically:

- record typical reflux symptoms when present;
- recognize that cough may occur without classic symptoms;
- do not attribute cough to GERD solely from temporal association;
- evaluate other common causes and preserve uncertainty.

## Question selection

Within the routine branch:

`score = safety_gate + commonness + branch_fit + discrimination + information_gain - burden - repetition`

A common-pattern discriminator should generally outrank a low-probability, non-urgent question.
