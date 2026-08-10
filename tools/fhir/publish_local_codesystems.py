#!/usr/bin/env python3
"""Plan or publish the two generated local CodeSystems to FHIR R4."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.fhir_codesystem_publish import (  # noqa: E402
    FhirCodeSystemPublisher,
)
from interoperability.fhir_valueset_publish import load_env_value  # noqa: E402
from interoperability.fhir_valueset_service import DEFAULT_BASE_URL  # noqa: E402
from tools.fhir.build_question_answer_codesystems import (  # noqa: E402
    build,
    validate,
)


OUTPUTS = [
    ROOT / "fhir/r4/codesystems/clinical-interview-question.json",
    ROOT / "fhir/r4/codesystems/clinical-interview-answer.json",
]


def generated_resources() -> list[dict]:
    question, answer = build()
    resources = [question, answer]
    for resource in resources:
        validate(resource)
    for path, resource in zip(OUTPUTS, resources):
        if not path.is_file():
            raise RuntimeError(f"generated CodeSystem file is missing: {path}")
        persisted = json.loads(path.read_text(encoding="utf-8"))
        if persisted != resource:
            raise RuntimeError(
                f"generated CodeSystem is stale; rebuild before publication: {path}"
            )
    return resources


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--token-variable", default="TERM_ADMIN_TOKEN")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform authenticated writes. Without this flag only a plan is produced.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.apply and not args.env_file:
        parser.error("--env-file is required with --apply")
    api_key = (
        load_env_value(args.env_file.expanduser(), args.token_variable)
        if args.apply
        else "dry-run-placeholder"
    )
    publisher = FhirCodeSystemPublisher(
        base_url=args.base_url,
        api_key=api_key,
    )
    results = []
    for resource in generated_resources():
        plan = publisher.plan(resource)
        if args.apply:
            results.append(publisher.apply(plan))
        else:
            results.append({
                key: value for key, value in plan.items() if key != "resource"
            })
    counts = Counter(result["action"] for result in results)
    report = {
        "id": "clinical-interview-local-codesystem-publication",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry_run",
        "base_url": args.base_url.rstrip("/"),
        "source_resources": [str(path.relative_to(ROOT)) for path in OUTPUTS],
        "resource_count": len(results),
        "concept_count": sum(result["concept_count"] for result in results),
        "action_counts": dict(sorted(counts.items())),
        "authentication": {
            "header": "X-API-Key",
            "token_variable": args.token_variable,
            "secret_recorded": False,
        },
        "results": results,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        try:
            print(output.relative_to(ROOT))
        except ValueError:
            print(output)
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
