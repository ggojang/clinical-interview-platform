# Coverage

Generate computed package Coverage:

```bash
python3 coverage/report.py --output coverage/latest-report.json
```

Coverage distinguishes graph inventory from connected Facts, Targets, Questions,
and Simulations. It also reports safety Rules with Simulation coverage and
explicit absent-data scenarios. The current report is a research baseline, not
a production gate.
