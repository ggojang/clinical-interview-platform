# Evaluation

Run package-level Simulation evaluation:

```bash
python3 evaluation/run_evaluation.py --output evaluation/latest-report.json
```

The report checks expected patterns, safety level, stop behavior, forbidden
assertions, repeated Fact questions, turn budgets, safety actions, triggered
Rules, known Facts, and `dataAbsentReason`. Results remain `unreviewed` until
the required human review is recorded.
