"""Knowledge Package loading and integrity validation."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from compiler.build_package import CompilationError, validate_package

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = ROOT / "packages/generated/primary-care-cough-0.3.0.json"
FEVER_PACKAGE = ROOT / "packages/generated/primary-care-fever-0.1.0.json"
DYSPNEA_PACKAGE = ROOT / "packages/generated/primary-care-dyspnea-0.1.0.json"
ABDOMINAL_PAIN_PACKAGE = ROOT / "packages/generated/primary-care-abdominal-pain-0.1.0.json"
CHEST_PAIN_PACKAGE = ROOT / "packages/generated/primary-care-chest-pain-0.1.0.json"
HEADACHE_PACKAGE = ROOT / "packages/generated/primary-care-headache-0.1.0.json"


class PackageLoadError(RuntimeError):
    pass


def refresh_warnings(package: dict[str, Any], as_of: date | None = None) -> list[str]:
    current = as_of or date.today()
    warnings: list[str] = []
    for manifest in package.get("research_source_manifests", []):
        for artifact in manifest.get("artifacts", []):
            raw_date = artifact.get("next_monitor_at")
            if raw_date and date.fromisoformat(raw_date) < current:
                warnings.append(
                    f"{artifact['id']}: source monitoring overdue since {raw_date}"
                )
    return warnings


def load_package(
    path: Path | str = DEFAULT_PACKAGE,
    execution_mode: str = "research_test",
) -> dict[str, Any]:
    package_path = Path(path)
    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
        validate_package(package)
    except (OSError, json.JSONDecodeError, CompilationError) as exc:
        raise PackageLoadError(f"cannot load Knowledge Package {package_path}: {exc}") from exc
    if package.get("release_state") not in {"draft", "release_candidate", "released"}:
        raise PackageLoadError(f"unsupported package release state: {package.get('release_state')}")
    usage = package.get("usage_policy", {})
    if execution_mode == "production" and not usage.get("production_allowed", False):
        raise PackageLoadError("draft research package is not allowed in production mode")
    if execution_mode not in usage.get("allowed_modes", []):
        raise PackageLoadError(
            f"package does not allow execution mode {execution_mode!r}"
        )
    package["_runtime_warnings"] = [
        "Package contains unreviewed/research_only medical knowledge.",
        *refresh_warnings(package),
    ]
    return package
