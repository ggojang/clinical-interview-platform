#!/usr/bin/env python3
"""Audit computable-knowledge reference boundaries and Rule Graph coverage."""
from __future__ import annotations

import json
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.computable_knowledge import (  # noqa: E402
    EXPECTED_RULE_TYPES,
    validate_overlay_documents,
)


def run() -> dict[str, object]:
    documents = validate_overlay_documents()
    repository_rule_types: set[str] = set()
    rule_count = 0
    for path in sorted((ROOT / "rules").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rules = data.get("rules", [])
        rule_count += len(rules)
        repository_rule_types.update(
            rule["type"] for rule in rules if rule.get("type")
        )
    unknown = repository_rule_types - EXPECTED_RULE_TYPES
    return {
        "passed": not unknown,
        "framework_count": documents["framework_count"],
        "source_artifact_count": documents["source_artifact_count"],
        "projection_profile_count": documents["rule_projection_type_count"],
        "simulation_count": documents["simulation_count"],
        "repository_rule_count": rule_count,
        "repository_rule_types": sorted(repository_rule_types),
        "unknown_rule_types": sorted(unknown),
        "runtime_external_lookup": False,
        "clinical_authority": False,
        "projection_emission": "metadata_only_not_emitted",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run()
    rendered = json.dumps(
        report, ensure_ascii=False, indent=2, sort_keys=True
    ) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
