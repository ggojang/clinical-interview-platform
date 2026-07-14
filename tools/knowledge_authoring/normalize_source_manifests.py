#!/usr/bin/env python3
"""Normalize existing research Source Manifests to the refresh policy."""
from __future__ import annotations

import json
from pathlib import Path

from profile_support import ROOT, normalize_source_monitoring


def render(document: dict, compact: bool) -> str:
    if compact:
        return json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n"
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    changed = []
    for path in sorted((ROOT / "sources/manifests").glob("*-research.json")):
        original = path.read_text(encoding="utf-8")
        document = json.loads(original)
        normalized = normalize_source_monitoring(document)
        output = render(normalized, compact=original.count("\n") <= 2)
        if output != original:
            path.write_text(output, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(json.dumps({"changed_count": len(changed), "changed": changed}, indent=2))


if __name__ == "__main__":
    main()
