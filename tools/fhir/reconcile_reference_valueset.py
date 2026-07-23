#!/usr/bin/env python3
"""Reconcile one reference ValueSet without altering its source content."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.fhir_valueset_publish import (  # noqa: E402
    FhirValueSetPublisher,
    load_env_value,
)
from interoperability.fhir_valueset_reconcile import (  # noqa: E402
    reconcile_reference,
)
from interoperability.fhir_valueset_service import (  # noqa: E402
    DEFAULT_BASE_URL,
    FhirValueSetService,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-file", type=Path, required=True)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--token-variable", default="TERM_ADMIN_TOKEN")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.apply and not args.env_file:
        parser.error("--env-file is required with --apply")

    source_bytes = args.reference_file.read_bytes()
    reference = json.loads(source_bytes)
    service = FhirValueSetService(args.base_url)
    catalog = service.list_valuesets(full=True)
    decision = reconcile_reference(reference, catalog)
    publication = None
    if args.apply and decision["action"] == "create_reference_unchanged":
        publisher = FhirValueSetPublisher(
            base_url=args.base_url,
            api_key=load_env_value(
                args.env_file.expanduser(),
                args.token_variable,
            ),
            read_service=service,
        )
        plan = publisher.plan(reference, catalog=catalog)
        publication = publisher.apply(plan)
    if args.reference_file.read_bytes() != source_bytes:
        raise RuntimeError("reference ValueSet file changed during reconciliation")
    report = {
        "id": "reference-valueset-reconciliation",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url.rstrip("/"),
        "mode": "apply" if args.apply else "dry_run",
        "reference_file_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "reference_file_mutated": False,
        "catalog_valueset_count": len(catalog),
        "decision": {
            key: value
            for key, value in decision.items()
            if key != "resource"
        },
        "publication": publication,
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
    return 1 if decision["action"] == "canonical_content_conflict" else 0


if __name__ == "__main__":
    raise SystemExit(main())
