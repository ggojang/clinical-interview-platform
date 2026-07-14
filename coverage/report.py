"""Emit computed Knowledge Package coverage and enforce research gates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.package import DEFAULT_PACKAGE, load_package


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    package = load_package(args.package.resolve())
    try:
        package_ref = str(args.package.resolve().relative_to(ROOT))
    except ValueError:
        package_ref = str(args.package.resolve())
    report = {
        "coverage_id": "coverage." + package["package_id"].removeprefix("package."),
        "version": "0.1.0",
        "package_id": package["package_id"],
        "package_version": package["package_version"],
        "semantic_digest": package["semantic_digest"],
        **package["coverage"],
        "provenance": {
            "created_by": {"type": "compiler", "id": "coverage.report"},
            "created_at": "2026-07-14T00:00:00Z",
            "source_refs": [package_ref],
            "review_status": "unreviewed",
            "version": "0.1.0",
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
