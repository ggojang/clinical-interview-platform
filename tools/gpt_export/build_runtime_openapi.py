#!/usr/bin/env python3
"""Build the Custom GPT runtime Action schema from the public OpenAPI document.

The Custom GPT editor accepts at most 30 operations. The public schema also
contains build-time interoperability reference endpoints, so the runtime
schema intentionally stops before that section.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/gpt/openapi.yaml"
TARGET = ROOT / "docs/gpt/openapi-runtime.yaml"
INTEROPERABILITY_MARKER = "  /gpt/interoperability/uscdi-v6-core.json:\n"
MAX_CUSTOM_GPT_OPERATIONS = 30


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if INTEROPERABILITY_MARKER not in source:
        raise SystemExit("interoperability path marker not found")

    runtime = source.split(INTEROPERABILITY_MARKER, 1)[0]
    runtime = runtime.replace(
        "title: Clinical Interview Research Knowledge",
        "title: Clinical Interview Runtime Knowledge",
        1,
    ).replace(
        "description: Read-only draft Knowledge, Fact, and isolated test-catalog resources. No patient answers are accepted.",
        "description: Read-only runtime Knowledge, Fact, and isolated test-catalog resources. No patient answers are accepted.",
        1,
    )

    operation_ids = re.findall(r"^\s+operationId:\s+(\S+)\s*$", runtime, re.MULTILINE)
    if len(operation_ids) > MAX_CUSTOM_GPT_OPERATIONS:
        raise SystemExit(
            f"runtime schema has {len(operation_ids)} operations; "
            f"Custom GPT allows at most {MAX_CUSTOM_GPT_OPERATIONS}"
        )
    if len(operation_ids) != len(set(operation_ids)):
        raise SystemExit("runtime schema contains duplicate operationId values")

    TARGET.write_text(runtime.rstrip() + "\n", encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT)} with {len(operation_ids)} operations")


if __name__ == "__main__":
    main()
