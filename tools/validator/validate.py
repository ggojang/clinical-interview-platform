from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
errors = []

# JSON syntax and required top-level keys
for path in ROOT.rglob("*.json"):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        continue
    if path.name.endswith(".schema.json") and "$schema" not in data:
        errors.append(f"{path.relative_to(ROOT)}: schema lacks $schema")

# Collect fact IDs from YAML text
fact_ids = set()
for path in (ROOT / "knowledge/semantic/facts").glob("*.yaml"):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^id:\s*([^\s]+)", text, re.M)
    if not m:
        errors.append(f"{path.relative_to(ROOT)}: missing id")
    else:
        fact_ids.add(m.group(1))
    if "review_status:" not in text:
        errors.append(f"{path.relative_to(ROOT)}: missing provenance review_status")

# Pattern references
pattern = (ROOT / "knowledge/semantic/patterns/cough.yaml").read_text(encoding="utf-8")
refs = re.findall(r"^\s+-\s+((?:symptom|patient)\.[a-zA-Z0-9_.-]+)\s*$", pattern, re.M)
for ref in refs:
    if ref not in fact_ids:
        errors.append(f"cough pattern references missing fact: {ref}")

# Required repository files
required = [
    "README.md", "MISSION.md", "AI.md",
    "specifications/clinical-memory.md",
    "schemas/clinical-memory.schema.json",
    "simulation/patients/respiratory/COUGH-001.yaml",
    "runtime/core.py",
]
for rel in required:
    if not (ROOT / rel).exists():
        errors.append(f"missing required file: {rel}")

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

# Check all pattern fact references
for path in (ROOT / "knowledge/semantic/patterns").glob("*.yaml"):
    text = path.read_text(encoding="utf-8")
    for ref in re.findall(r"^\s+-\s+((?:symptom|patient|exposure)\.[a-zA-Z0-9_.-]+)\s*$", text, re.M):
        if ref not in fact_ids:
            errors.append(f"{path.name} references missing fact: {ref}")

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

try:
    from compiler.build_package import load_json, validate_package
    package_paths = [
        ROOT / "packages/generated/primary-care-cough-0.3.0.json",
        ROOT / "packages/generated/primary-care-fever-0.1.0.json",
        ROOT / "packages/generated/primary-care-dyspnea-0.1.0.json",
        ROOT / "packages/generated/primary-care-abdominal-pain-0.1.0.json",
    ]
    package_fact_counts = {}
    for package_path in package_paths:
        package = load_json(package_path)
        validate_package(package)
        package_fact_counts[package["package_id"]] = sum(
            node.get("type") == "Fact"
            for node in package["knowledge_graph"]["nodes"]
        )
except Exception as exc:
    errors.append(f"Knowledge Package validation failed: {exc}")

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print(
    f"VALIDATION PASSED: {len(fact_ids)} legacy facts, "
    f"packages={package_fact_counts}"
)
