#!/usr/bin/env python3
"""Plan or publish generated answer ValueSets to an authenticated FHIR server."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.fhir_valueset_publish import (  # noqa: E402
    FhirValueSetPublisher,
    load_env_value,
)
from interoperability.fhir_valueset_service import DEFAULT_BASE_URL  # noqa: E402
from tools.fhir.build_answer_valuesets import (  # noqa: E402
    OUTPUT,
    build,
    validate,
)


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
    bundle = build()
    validate(bundle)
    publisher = FhirValueSetPublisher(
        base_url=args.base_url,
        api_key=api_key,
    )
    results = []
    for entry in bundle["entry"]:
        plan = publisher.plan(entry["resource"])
        if args.apply:
            results.append(publisher.apply(plan))
        else:
            results.append({
                key: value for key, value in plan.items() if key != "resource"
            })
    counts = Counter(result["action"] for result in results)
    report = {
        "id": "clinical-interview-answer-valueset-publication",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry_run",
        "base_url": args.base_url.rstrip("/"),
        "source_bundle": str(OUTPUT.relative_to(ROOT)),
        "resource_count": len(results),
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
