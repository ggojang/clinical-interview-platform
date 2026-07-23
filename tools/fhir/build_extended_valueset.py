#!/usr/bin/env python3
"""Build a separate derived ValueSet from an unchanged reference ValueSet."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from interoperability.fhir_valueset_reconcile import (  # noqa: E402
    build_extended_valueset,
)
from interoperability.fhir_valueset_service import (  # noqa: E402
    DEFAULT_BASE_URL,
    FhirValueSetService,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference-file", type=Path, required=True)
    parser.add_argument("--additions-file", type=Path, required=True)
    parser.add_argument("--semantic-name", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--allow-local-codes", action="store_true")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    reference = json.loads(args.reference_file.read_text(encoding="utf-8"))
    additions = json.loads(args.additions_file.read_text(encoding="utf-8"))
    if not isinstance(additions, list):
        parser.error("--additions-file must contain a JSON array")
    service = FhirValueSetService(args.base_url)
    verified_at = datetime.now(timezone.utc).isoformat()
    verified_additions = []
    for addition in additions:
        if not isinstance(addition, dict):
            parser.error("each addition must be a JSON object")
        candidate = dict(addition)
        if not candidate.get("system") or not candidate.get("code"):
            parser.error("each addition requires system and code")
        if (
            not candidate.get("system", "").startswith(
                "https://ggojang.github.io/"
                "clinical-interview-platform/fhir/CodeSystem/"
            )
        ):
            result = service.validate_codesystem_code(
                candidate["system"],
                code=candidate["code"],
                version=candidate.get("version"),
                display=candidate.get("display"),
            )
            if result["result"] is not True:
                raise ValueError(
                    f"standard code validation failed: "
                    f"{candidate['system']}|{candidate['code']}"
                )
            candidate["display"] = (
                result.get("display")
                or candidate.get("display")
            )
            candidate["verification_source"] = (
                args.base_url.rstrip("/")
                + "/CodeSystem/$validate-code"
            )
            candidate["verified_at"] = verified_at
        verified_additions.append(candidate)
    derived = build_extended_valueset(
        reference,
        verified_additions,
        semantic_name=args.semantic_name,
        title=args.title,
        description=args.description,
        version=args.version,
        date=args.date,
        allow_local_codes=args.allow_local_codes,
    )
    output = args.output
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(derived, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        print(output.relative_to(ROOT))
    except ValueError:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
