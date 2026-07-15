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
DIZZINESS_SYNCOPE_PACKAGE = ROOT / "packages/generated/primary-care-dizziness-syncope-0.1.0.json"
VOMITING_DIARRHEA_PACKAGE = ROOT / "packages/generated/primary-care-vomiting-diarrhea-0.1.0.json"
URINARY_SYMPTOMS_PACKAGE = ROOT / "packages/generated/primary-care-urinary-symptoms-0.1.0.json"
FATIGUE_PACKAGE = ROOT / "packages/generated/primary-care-fatigue-0.1.0.json"
BACK_PAIN_PACKAGE = ROOT / "packages/generated/primary-care-back-pain-0.1.0.json"
SKIN_COMPLAINT_PACKAGE = ROOT / "packages/generated/primary-care-skin-complaint-0.1.0.json"
MEDICATION_REVIEW_PACKAGE = ROOT / "packages/generated/primary-care-medication-review-0.1.0.json"
UPPER_RESPIRATORY_SYMPTOMS_PACKAGE = ROOT / "packages/generated/primary-care-upper-respiratory-symptoms-0.1.0.json"
PALPITATIONS_PACKAGE = ROOT / "packages/generated/primary-care-palpitations-0.1.0.json"
BOWEL_SYMPTOMS_PACKAGE = ROOT / "packages/generated/primary-care-bowel-symptoms-0.1.0.json"
FOCAL_WEAKNESS_NUMBNESS_PACKAGE = ROOT / "packages/generated/primary-care-focal-weakness-numbness-0.1.0.json"
JOINT_LIMB_COMPLAINT_PACKAGE = ROOT / "packages/generated/primary-care-joint-limb-0.1.0.json"
MENTAL_HEALTH_SLEEP_PACKAGE = ROOT / "packages/generated/primary-care-mental-health-sleep-0.1.0.json"
EDEMA_PACKAGE = ROOT / "packages/generated/primary-care-edema-0.1.0.json"
HYPERTENSION_FOLLOW_UP_PACKAGE = ROOT / "packages/generated/primary-care-hypertension-follow-up-0.1.0.json"
WEIGHT_CONSTITUTIONAL_CHANGE_PACKAGE = ROOT / "packages/generated/primary-care-weight-constitutional-change-0.1.0.json"
REPRODUCTIVE_GENITAL_SYMPTOMS_PACKAGE = ROOT / "packages/generated/primary-care-reproductive-genital-symptoms-0.1.0.json"
EYE_SYMPTOMS_PACKAGE = ROOT / "packages/generated/primary-care-eye-symptoms-0.1.0.json"
EAR_HEARING_SYMPTOMS_PACKAGE = ROOT / "packages/generated/primary-care-ear-hearing-symptoms-0.1.0.json"
DIABETES_FOLLOW_UP_PACKAGE = ROOT / "packages/generated/primary-care-diabetes-follow-up-0.1.0.json"
ORAL_DENTAL_SYMPTOMS_PACKAGE = ROOT / "packages/generated/primary-care-oral-dental-symptoms-0.1.0.json"
WOUND_MINOR_INJURY_PACKAGE = ROOT / "packages/generated/primary-care-wound-minor-injury-0.1.0.json"
MEMORY_COGNITIVE_CONCERN_PACKAGE = ROOT / "packages/generated/primary-care-memory-cognitive-concern-0.1.0.json"
PREGNANCY_POSTPARTUM_CONCERN_PACKAGE = ROOT / "packages/generated/primary-care-pregnancy-postpartum-concern-0.1.0.json"
ALLERGY_CONCERN_PACKAGE = ROOT / "packages/generated/primary-care-allergy-concern-0.1.0.json"
ASTHMA_COPD_FOLLOW_UP_PACKAGE = ROOT / "packages/generated/primary-care-asthma-copd-follow-up-0.1.0.json"
LUMP_LYMPH_NODE_PACKAGE = ROOT / "packages/generated/primary-care-lump-lymph-node-0.1.0.json"
DYSPEPSIA_REFLUX_PACKAGE = ROOT / "packages/generated/primary-care-dyspepsia-reflux-0.1.0.json"
THYROID_CONCERN_FOLLOW_UP_PACKAGE = ROOT / "packages/generated/primary-care-thyroid-concern-follow-up-0.1.0.json"
ANEMIA_CONCERN_FOLLOW_UP_PACKAGE = ROOT / "packages/generated/primary-care-anemia-concern-follow-up-0.1.0.json"
KIDNEY_FUNCTION_CKD_FOLLOW_UP_PACKAGE = ROOT / "packages/generated/primary-care-kidney-function-ckd-follow-up-0.1.0.json"


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
