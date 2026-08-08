"""Explicit service-mode routing around the legacy clinical interview runtime.

The existing Chatbot remains Reason-for-Encounter first.  This module is used
only when a host application or an explicit user request selects another mode.
It never stores patient answers and never changes an InterviewSession package.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any


DEFAULT_POLICY = (
    Path(__file__).resolve().parents[1]
    / "policies"
    / "interaction-service-modes.json"
)


class ServiceModeError(ValueError):
    """Raised when an explicit service-mode selection cannot be resolved."""


def _normalized(text: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]+", "", text.casefold())


class ServiceModeRegistry:
    """Read-only registry that preserves the legacy mode as the default."""

    def __init__(self, path: Path | str = DEFAULT_POLICY) -> None:
        self.document = json.loads(Path(path).read_text(encoding="utf-8"))
        self.modes = {item["id"]: item for item in self.document["modes"]}
        self.categories = {
            item["id"]: item for item in self.document["start_categories"]
        }
        default = self.document["compatibility"]["default_mode"]
        if default != "clinical_adaptive" or default not in self.modes:
            raise ServiceModeError("legacy clinical_adaptive mode must remain default")

    def catalog(self) -> dict[str, Any]:
        return {
            "resource_type": "InteractionServiceModeCatalog",
            "version": self.document["version"],
            "lifecycle_status": self.document["lifecycle_status"],
            "review_status": self.document["review_status"],
            "clinical_use_status": self.document["clinical_use_status"],
            "contains_patient_responses": False,
            "compatibility": deepcopy(self.document["compatibility"]),
            "start_categories": deepcopy(self.document["start_categories"]),
            "modes": deepcopy(self.document["modes"]),
            "test_data_lifecycle": deepcopy(self.document["test_data_lifecycle"]),
            "screening_recommendation": deepcopy(
                self.document["screening_recommendation"]
            ),
            "prepopulation": deepcopy(self.document["prepopulation"]),
        }

    def resolve(self, selection: str | None = None) -> dict[str, Any]:
        """Resolve an explicit selection; no selection preserves legacy entry."""
        if selection is None or not selection.strip():
            mode = deepcopy(self.modes["clinical_adaptive"])
            return {
                "status": "resolved",
                "explicit_selection": False,
                "compatibility_default": True,
                "mode": mode,
            }

        normalized = _normalized(selection)
        category_matches = [
            category
            for category in self.categories.values()
            if normalized in {
                _normalized(category["id"]),
                _normalized(category["display_ko"]),
            }
        ]
        if len(category_matches) == 1:
            category = category_matches[0]
            if len(category["mode_ids"]) == 1:
                return self._resolved(category["mode_ids"][0])
            return {
                "status": "selection_required",
                "explicit_selection": True,
                "category": deepcopy(category),
                "options": [
                    deepcopy(self.modes[mode_id])
                    for mode_id in category["mode_ids"]
                ],
            }

        matches: list[dict[str, Any]] = []
        for mode in self.modes.values():
            names = [mode["id"], mode["display_ko"], *mode.get("aliases_ko", [])]
            if any(normalized == _normalized(name) for name in names):
                matches.append(mode)
        if len(matches) != 1:
            return {
                "status": "no_match" if not matches else "selection_required",
                "explicit_selection": True,
                "preserve_legacy_session": True,
            }
        return self._resolved(matches[0]["id"])

    def _resolved(self, mode_id: str) -> dict[str, Any]:
        mode = deepcopy(self.modes[mode_id])
        result = {
            "status": "resolved",
            "explicit_selection": True,
            "compatibility_default": mode_id == "clinical_adaptive",
            "mode": mode,
        }
        if mode_id == "screening_addon_recommendation":
            result["next"] = {
                "workflow": "supplemental_adaptive_interview",
                "prompt_ko": mode["opening_prompt_ko"],
                "official_nhis_questionnaire": "offer_as_optional_choice",
            }
        return result


def resolve_service_mode(selection: str | None = None) -> dict[str, Any]:
    return ServiceModeRegistry().resolve(selection)
