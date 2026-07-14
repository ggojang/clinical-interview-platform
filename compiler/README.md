# Compiler

Build the deterministic research package:

```bash
python3 compiler/build_package.py --profile cough
python3 compiler/build_package.py --profile fever
python3 compiler/build_package.py --profile dyspnea
python3 compiler/build_package.py --profile abdominal_pain
```

Validate a generated package:

```bash
python3 compiler/build_package.py --validate packages/generated/primary-care-cough-0.3.0.json
python3 compiler/build_package.py --validate packages/generated/primary-care-fever-0.1.0.json
python3 compiler/build_package.py --validate packages/generated/primary-care-dyspnea-0.1.0.json
python3 compiler/build_package.py --validate packages/generated/primary-care-abdominal-pain-0.1.0.json
```

Production compilation fails closed until source completeness, licensing, and
safety review gates are satisfied.
