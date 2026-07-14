# Simulation

Synthetic patients provide hidden facts, disclosure rules, expected coverage, and forbidden assertions.

A simulation is not merely a list of answers. It should model how information is revealed depending on question quality.

All included cases are generated and unreviewed.

Simulation response behavior may carry `dataAbsentReason`. The current Runtime
supports `asked-unknown`, `asked-declined`, and `not-applicable` without turning
missing data into a negative Fact. Cases may also assert maximum turns, safety
actions, triggered Rules, required stop reasons, and expected absent-data codes.
