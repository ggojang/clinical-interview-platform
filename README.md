# Clinical Interview Knowledge Platform

An AI-native Knowledge Factory for generating, validating, compiling, evaluating, and evolving reusable clinical interview knowledge for Primary Care.

> Version 0.1 asks one narrow question:  
> **Can an AI conduct a safe, traceable, clinically useful interview for a patient presenting with cough?**

This repository is organized for both AI agents and human reviewers. The source-of-truth order is:

1. `FOUNDATION.md`
2. `PROJECT_CONTEXT.md`
3. `docs/context/`
4. `specifications/`
5. `schemas/`
6. reviewed knowledge
7. generated knowledge
8. compiled packages
9. runtime implementation
10. examples and playground outputs

## What this project is

- A Clinical Interview Knowledge Factory
- A canonical Knowledge Graph and executable Rule Graph
- A structured, provenance-complete interview knowledge repository
- A simulation, evaluation, coverage, and compilation framework
- A producer of immutable Knowledge Packages
- A runtime prototype for executing compiled interview knowledge

## What this project is not

- A diagnostic device
- A substitute for a clinician
- A production patient service
- A complete FHIR implementation
- A comprehensive medical knowledge base

Runtime is one consumer of the knowledge produced by this repository. Knowledge is the product.

## Version 0.1 vertical slice

The first end-to-end slice covers:

- Chief complaint: cough
- Core facts: duration, onset, fever, dyspnea, sputum, hemoptysis, smoking
- Respiratory red-flag screening
- Clinical Memory updates
- Missing-fact analysis
- Question prioritization
- Deterministic validation of schemas and knowledge references

## Quick start

Python 3.11+ is recommended. No third-party package is required for the starter validator.

```bash
python tools/validator/validate.py
python tools/validator/audit_uscdi_interoperability.py --output coverage/uscdi-interoperability-latest.json
python builder/build_knowledge.py --profile cough --report builder/latest-report.json
python builder/build_knowledge.py --profile fever --report builder/latest-fever-report.json
python builder/build_knowledge.py --profile dyspnea --report builder/latest-dyspnea-report.json
python compiler/build_package.py --profile cough
python compiler/build_package.py --profile fever
python compiler/build_package.py --profile dyspnea
python -m unittest discover -s tests -p 'test_*.py'
python evaluation/run_evaluation.py
python coverage/report.py
python sources/check_refresh.py
python tools/privacy/check_repository.py
python tools/gpt_export/build.py
python tools/interview-runner/run_demo.py
python tools/interview-runner/run_multiturn_demo.py
```

## Repository map

- `FOUNDATION.md`: immutable architectural principles
- `PROJECT_CONTEXT.md`: master repository context and reading order
- `docs/context/`: complete conceptual architecture
- `specifications/`: behavioral contracts; the effective API of the project
- `schemas/`: machine-validatable data shapes
- `knowledge/`: facts, patterns, red flags, and provenance
- `simulation/`: synthetic patients and expected interview behavior
- `runtime/`: executable logic and prompts
- `compiler/`: deterministic Knowledge Package compilation
- `packages/`: generated immutable Knowledge Packages
- `evaluation/`: package-level Simulation evaluation
- `coverage/`: computed Coverage reports
- `sources/`: versioned Source Manifests
- `rules/`: canonical Rule Graph source
- `playground/`: transparent experiments and traces
- `examples/`: regression fixtures
- `tests/`: automated checks
- `tools/`: repository maintenance and execution tools
- `docs/gpt/`: response-free static Knowledge/Fact API for a Custom GPT Action

## Patient-data boundary

Real patient responses and personal or medical information are local-only inputs. They may be used to identify missing Knowledge and Facts, but they must not be committed or published. Only generalized, non-quoting, de-identified aggregate candidates may enter the repository, and they remain `unreviewed/research_only`. See `docs/LOCAL_FEEDBACK_PRIVACY.md`.

The public GPT resources are built only from `knowledge/` and `rules/`. They never include `simulation/`, examples, session traces, or response exports.

## Safety

All content is research and development material. Runtime outputs must preserve uncertainty, avoid unsupported diagnoses, and escalate urgent warning signs according to reviewed safety rules.

## Version 0.2

Adds a multi-turn InterviewSession, Patient Simulator, duration branching, and safety-gated prioritization of common acute and chronic cough patterns, including Common Cold and GERD-related features.

## Version 0.3 research package

Adds evidence-based pattern activation, package-defined completion and
clarification policy, coded `dataAbsentReason`, bounded question selection, and
fourteen simulations covering routine, clarify, urgent, emergency, Korean, and
absent-data behavior. It remains `unreviewed/research_only` and is rejected in
production mode.

## Fever 0.1 research package

Adds the Primary Care Reason for Encounter catalog and an independently compiled
adult fever interview slice with 19 Facts, 19 Questions, six safety rules, eight
Simulations, shared Fact reuse, source-specific refresh metadata, and explicit
`dataAbsentReason`. It remains `unreviewed/research_only` and is not a diagnostic
or production clinical protocol.

## Dyspnea 0.1 research package

Adds an independently compiled Primary Care breathing-difficulty slice with 24
Facts, 24 Questions, eight safety rules, and eleven Simulations. It covers
severity and functional impact, airway features, congestion-associated features,
and thromboembolic warning context without asserting diagnoses. Every safety rule
has a Simulation, `dataAbsentReason` is exercised, and the package remains
`unreviewed/research_only` and production-blocked.
