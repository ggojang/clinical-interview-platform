"""Report source-monitoring work due under the Knowledge Refresh Policy."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "sources/manifests/respiratory-cough-research.json"


def due_sources(as_of: date, manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    due = []
    upcoming = []
    for artifact in manifest.get("artifacts", []):
        next_monitor = date.fromisoformat(artifact["next_monitor_at"])
        item = {
            "source_id": artifact["id"],
            "monitor_profile": artifact["monitor_profile"],
            "monitor_interval_days": artifact["monitor_interval_days"],
            "next_monitor_at": artifact["next_monitor_at"],
            "action": "metadata_version_and_digest_check",
        }
        (due if next_monitor <= as_of else upcoming).append(item)
    return {
        "policy_id": "policy.knowledge-refresh",
        "policy_version": "0.2.0",
        "as_of": as_of.isoformat(),
        "due": sorted(due, key=lambda item: (item["next_monitor_at"], item["source_id"])),
        "upcoming": sorted(upcoming, key=lambda item: (item["next_monitor_at"], item["source_id"])),
        "network_actions_executed": False,
        "review_status": "unreviewed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = due_sources(args.as_of, args.manifest.resolve())
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()

