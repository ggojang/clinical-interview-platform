"""Core interaction-purpose routing for all conversational service modes.

The router infers a mode from the first user message when possible.  The
existing Reason-for-Encounter interview is preserved as the execution engine
inside ``clinical_adaptive`` rather than remaining the platform entry point.
This registry stores no patient answers.
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
DEFAULT_RFE_CATALOG = (
    Path(__file__).resolve().parents[1]
    / "knowledge"
    / "catalog"
    / "primary-care-rfe.json"
)
GENERATED_PACKAGES = Path(__file__).resolve().parents[1] / "packages" / "generated"


class ServiceModeError(ValueError):
    """Raised when an explicit service-mode selection cannot be resolved."""


def _normalized(text: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]+", "", text.casefold())


class ServiceModeRegistry:
    """Read-only registry for the platform's purpose-first core entry."""

    def __init__(self, path: Path | str = DEFAULT_POLICY) -> None:
        self.document = json.loads(Path(path).read_text(encoding="utf-8"))
        self.modes = {item["id"]: item for item in self.document["modes"]}
        self.categories = {
            item["id"]: item for item in self.document["start_categories"]
        }
        rfe_catalog = json.loads(DEFAULT_RFE_CATALOG.read_text(encoding="utf-8"))
        self.rfe_entries = deepcopy(rfe_catalog["entries"])
        self.clinical_aliases = {
            _normalized(name)
            for entry in rfe_catalog["entries"]
            for name in [
                entry.get("display", ""),
                entry.get("display_ko", ""),
                *entry.get("aliases", []),
            ]
            if len(_normalized(name)) >= 2
        }
        compatibility = self.document["compatibility"]
        if compatibility.get("core_entry") != "interaction_purpose":
            raise ServiceModeError("interaction_purpose must be the core entry")
        if "clinical_adaptive" not in self.modes:
            raise ServiceModeError("clinical_adaptive execution mode is required")

    def catalog(self) -> dict[str, Any]:
        return {
            "resource_type": "InteractionServiceModeCatalog",
            "version": self.document["version"],
            "lifecycle_status": self.document["lifecycle_status"],
            "review_status": self.document["review_status"],
            "clinical_use_status": self.document["clinical_use_status"],
            "contains_patient_responses": False,
            "compatibility": deepcopy(self.document["compatibility"]),
            "core_entry": deepcopy(self.document["core_entry"]),
            "start_categories": deepcopy(self.document["start_categories"]),
            "modes": deepcopy(self.document["modes"]),
            "test_data_lifecycle": deepcopy(self.document["test_data_lifecycle"]),
            "screening_recommendation": deepcopy(
                self.document["screening_recommendation"]
            ),
            "prepopulation": deepcopy(self.document["prepopulation"]),
        }

    def resolve(self, selection: str | None = None) -> dict[str, Any]:
        """Resolve a mode or request one conversational purpose clarification."""
        if selection is None or not selection.strip():
            return {
                "status": "purpose_required",
                "explicit_selection": False,
                "core_entry": deepcopy(self.document["core_entry"]),
                "prompt_ko": self.document["core_entry"]["prompt_ko"],
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
            inferred = self._infer_from_message(selection)
            if inferred is not None:
                return self._resolved(inferred, explicit_selection=False)
            return {
                "status": "purpose_required" if not matches else "selection_required",
                "explicit_selection": False,
                "core_entry": deepcopy(self.document["core_entry"]),
                "prompt_ko": self.document["core_entry"]["prompt_ko"],
            }
        return self._resolved(matches[0]["id"])

    def _infer_from_message(self, selection: str) -> str | None:
        """Conservative deterministic intent routing before LLM interpretation."""
        text = selection.casefold().strip()
        normalized = _normalized(text)
        if not normalized:
            return None

        structured = any(
            token in text
            for token in ("questionnaire", "fhir questionnaire", "문진표 파일", "설문지 파일")
        )
        if structured:
            if any(token in text for token in ("진료", "문진", "병원")):
                return "clinical_structured"
            if any(token in text for token in ("설문", "평가")):
                return "survey_structured"

        if any(token in text for token in ("환자경험", "설문", "평가 목록", "설문 목록")):
            return "survey_conversational_fixed"
        if any(
            token in text
            for token in ("건강검진", "검진 패키지", "추가 검진", "검진 추천", "내게 맞는 검진")
        ):
            return "screening_addon_recommendation"
        if any(
            token in text
            for token in ("알려줘", "설명해", "정보", "무엇인가", "뭔가요", "상담")
        ) and any(
            token in text
            for token in ("건강", "질환", "병", "약", "치료", "진단", "검사")
        ):
            return "health_information"

        clinical_markers = (
            "아프", "아파", "통증", "기침", "열", "어지", "숨", "구토", "설사", "붓",
            "피", "가려", "불편", "증상", "복용", "약을", "검사결과", "재진",
            "진료", "문진", "두통", "목", "가슴", "배", "허리", "소변", "변비",
        )
        if any(alias in normalized for alias in self.clinical_aliases) or any(
            marker in normalized for marker in clinical_markers
        ):
            return "clinical_adaptive"
        return None

    def match_reason_for_encounter(self, message: str) -> dict[str, Any] | None:
        """Return one most-specific implemented catalog entry when unambiguous."""
        normalized = _normalized(message)
        candidates: list[tuple[int, dict[str, Any]]] = []
        for entry in self.rfe_entries:
            if entry.get("implementation_status") != "implemented":
                continue
            names = [
                entry.get("display", ""),
                entry.get("display_ko", ""),
                *entry.get("aliases", []),
            ]
            matched_lengths = [
                len(alias)
                for name in names
                if (alias := _normalized(name)) and alias in normalized
            ]
            if matched_lengths:
                candidates.append((max(matched_lengths), entry))
        if not candidates:
            return None
        longest = max(length for length, _ in candidates)
        best = [entry for length, entry in candidates if length == longest]
        unique = {entry["id"]: entry for entry in best}
        if len(unique) != 1:
            return None
        return deepcopy(next(iter(unique.values())))

    def reason_for_encounter_candidates(self) -> list[dict[str, Any]]:
        """Return the bounded, response-free RFE catalog for interpretation.

        The adapter receives only catalog labels and aliases.  Package content,
        medical sources, Rules, patient history, and session traces are not
        included in this routing context.
        """
        return [
            {
                "id": entry["id"],
                "display_ko": entry.get("display_ko") or entry.get("display"),
                "aliases": list(entry.get("aliases", [])),
            }
            for entry in self.rfe_entries
            if entry.get("implementation_status") == "implemented"
            and entry.get("package_id")
        ]

    def reason_for_encounter_by_id(self, rfe_id: str) -> dict[str, Any] | None:
        for entry in self.rfe_entries:
            if (
                entry.get("id") == rfe_id
                and entry.get("implementation_status") == "implemented"
                and entry.get("package_id")
            ):
                return deepcopy(entry)
        return None

    def package_path_for(self, entry: dict[str, Any]) -> Path:
        package_id = entry.get("package_id")
        if not package_id:
            raise ServiceModeError(f"RFE {entry.get('id')} has no package_id")
        stem = package_id.removeprefix("package.").replace(".", "-")
        matches = sorted(GENERATED_PACKAGES.glob(f"{stem}-*.json"))
        if not matches:
            raise ServiceModeError(f"compiled package not found for {package_id}")
        return matches[-1]

    def _resolved(self, mode_id: str, *, explicit_selection: bool = True) -> dict[str, Any]:
        mode = deepcopy(self.modes[mode_id])
        result = {
            "status": "resolved",
            "explicit_selection": explicit_selection,
            "core_entry": "interaction_purpose",
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
