"""Report source-monitoring work due under the Knowledge Refresh Policy."""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "sources/manifests/respiratory-cough-research.json"


def due_sources(
    as_of: date,
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    network_actions_executed: bool = False,
) -> dict[str, Any]:
    return due_sources_from_manifests(
        as_of,
        [manifest_path],
        network_actions_executed=network_actions_executed,
    )


def due_sources_from_manifests(
    as_of: date,
    manifest_paths: list[Path],
    *,
    network_actions_executed: bool = False,
) -> dict[str, Any]:
    due = []
    upcoming = []
    for manifest_path in manifest_paths:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for artifact in manifest.get("artifacts", []):
            next_monitor = date.fromisoformat(artifact["next_monitor_at"])
            item = {
                "source_id": artifact["id"],
                "source_manifest": manifest["id"],
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
        "network_actions_executed": network_actions_executed,
        "review_status": "unreviewed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--all", action="store_true",
        help="Report every research source manifest instead of one manifest.",
    )
    parser.add_argument("--network-actions-executed", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    paths = (
        sorted((ROOT / "sources/manifests").glob("*-research.json"))
        if args.all else [args.manifest.resolve()]
    )
    report = due_sources_from_manifests(
        args.as_of,
        paths,
        network_actions_executed=args.network_actions_executed,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
