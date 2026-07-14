#!/usr/bin/env python3
"""Record a completed official-source metadata check in research manifests."""
from __future__ import annotations

import argparse
import json
from datetime import date, timedelta
from pathlib import Path

from profile_support import ROOT, normalize_source_monitoring


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checked-on", required=True, type=date.fromisoformat)
    parser.add_argument("--source", required=True, action="append", dest="source_ids")
    parser.add_argument(
        "--result", default="current_official_source_confirmed",
        help="Non-clinical monitoring outcome recorded on each source artifact.",
    )
    args = parser.parse_args()

    requested = set(args.source_ids)
    found: set[str] = set()
    changed: list[str] = []
    for path in sorted((ROOT / "sources/manifests").glob("*-research.json")):
        original = path.read_text(encoding="utf-8")
        document = json.loads(original)
        touched = False
        for artifact in document.get("artifacts", []):
            if artifact.get("id") not in requested:
                continue
            found.add(artifact["id"])
            interval = artifact["monitor_interval_days"]
            artifact["last_monitored_at"] = args.checked_on.isoformat()
            artifact["next_monitor_at"] = (
                args.checked_on + timedelta(days=interval)
            ).isoformat()
            artifact["monitor_result"] = args.result
            touched = True
        if not touched:
            continue
        normalize_source_monitoring(document)
        compact = original.count("\n") <= 2
        rendered = json.dumps(
            document,
            ensure_ascii=False,
            separators=(",", ":") if compact else None,
            indent=None if compact else 2,
        ) + "\n"
        path.write_text(rendered, encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

    missing = sorted(requested - found)
    if missing:
        raise SystemExit(f"unknown source ids: {', '.join(missing)}")
    print(json.dumps({"updated_sources": sorted(found), "changed": changed}, indent=2))


if __name__ == "__main__":
    main()
