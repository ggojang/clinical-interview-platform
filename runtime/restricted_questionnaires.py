"""Load source-defined questionnaires from a local, non-public test store.

The repository never contains the protected item text.  A registry may point to a
locally supplied FHIR R4 Questionnaire and records the exact source/version/hash
needed for a reproducible internal test.  This module does not score instruments,
rewrite their items, or persist QuestionnaireResponse resources.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class RestrictedQuestionnaireError(ValueError):
    """Raised when a restricted questionnaire fails closed."""


@dataclass(frozen=True)
class RestrictedQuestionnaireRecord:
    instrument_id: str
    title: str
    source_family: str
    source_version: str
    relative_path: str
    sha256: str
    rights_status: str
    enabled: bool
    test_only: bool


class RestrictedQuestionnaireStore:
    """Read verified local FHIR Questionnaires for explicit internal tests only."""

    def __init__(self, root: Path, registry_path: Path):
        self.root = root.resolve()
        self.registry_path = registry_path.resolve()
        self._records = self._load_registry()

    def _load_registry(self) -> dict[str, RestrictedQuestionnaireRecord]:
        data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        if data.get("test_only") is not True:
            raise RestrictedQuestionnaireError("registry must declare test_only=true")
        if data.get("contains_patient_responses") is not False:
            raise RestrictedQuestionnaireError(
                "registry must declare contains_patient_responses=false"
            )

        records: dict[str, RestrictedQuestionnaireRecord] = {}
        for raw in data.get("questionnaires", []):
            record = RestrictedQuestionnaireRecord(
                instrument_id=raw["instrument_id"],
                title=raw["title"],
                source_family=raw["source_family"],
                source_version=raw["source_version"],
                relative_path=raw["relative_path"],
                sha256=raw["sha256"],
                rights_status=raw["rights_status"],
                enabled=raw.get("enabled", False),
                test_only=raw.get("test_only", False),
            )
            if record.instrument_id in records:
                raise RestrictedQuestionnaireError(
                    f"duplicate instrument_id: {record.instrument_id}"
                )
            if not record.test_only:
                raise RestrictedQuestionnaireError(
                    f"{record.instrument_id}: every entry must be test_only"
                )
            if record.rights_status not in {
                "user_supplied_for_internal_test",
                "written_permission_for_internal_test",
                "artifact_license_allows_internal_test",
            }:
                raise RestrictedQuestionnaireError(
                    f"{record.instrument_id}: unsupported rights_status"
                )
            records[record.instrument_id] = record
        return records

    def list_records(self) -> list[RestrictedQuestionnaireRecord]:
        return [self._records[key] for key in sorted(self._records)]

    def load(self, instrument_id: str) -> dict[str, Any]:
        if instrument_id not in self._records:
            raise RestrictedQuestionnaireError(f"unknown instrument: {instrument_id}")
        record = self._records[instrument_id]
        if not record.enabled:
            raise RestrictedQuestionnaireError(f"instrument is disabled: {instrument_id}")

        path = (self.root / record.relative_path).resolve()
        if not path.is_relative_to(self.root):
            raise RestrictedQuestionnaireError(
                f"{instrument_id}: questionnaire path escapes restricted root"
            )
        if not path.is_file():
            raise RestrictedQuestionnaireError(
                f"{instrument_id}: questionnaire file is missing"
            )

        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != record.sha256:
            raise RestrictedQuestionnaireError(
                f"{instrument_id}: sha256 mismatch"
            )

        questionnaire = json.loads(payload.decode("utf-8"))
        if questionnaire.get("resourceType") != "Questionnaire":
            raise RestrictedQuestionnaireError(
                f"{instrument_id}: resourceType must be Questionnaire"
            )
        if questionnaire.get("status") not in {"draft", "active"}:
            raise RestrictedQuestionnaireError(
                f"{instrument_id}: Questionnaire status must be draft or active"
            )
        if questionnaire.get("version") != record.source_version:
            raise RestrictedQuestionnaireError(
                f"{instrument_id}: Questionnaire version does not match registry"
            )
        return questionnaire
