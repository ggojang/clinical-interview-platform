"""Source-aware activation for HIRA adequacy-assessment interviews."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY = (
    Path(__file__).resolve().parents[1]
    / "knowledge"
    / "assessments"
    / "hira-adequacy-assessment-interviews-2026.json"
)


class AssessmentContextError(ValueError):
    """Raised when an assessment is requested without its required context."""


class HiraAssessmentRegistry:
    """Expose only questions appropriate for a patient or proxy interview."""

    def __init__(self, path: Path = DEFAULT_REGISTRY) -> None:
        self.document = json.loads(path.read_text(encoding="utf-8"))
        self.programs = {
            program["id"]: program for program in self.document.get("programs", [])
        }
        self.entries = {
            entry["program_id"]: entry
            for entry in self.document.get("entry_catalog", [])
        }

    @staticmethod
    def _normalize_entry_text(text: str) -> str:
        return re.sub(r"[^0-9a-z가-힣]+", "", text.casefold())

    def resolve_entry(self, text: str) -> dict[str, Any]:
        """Resolve an explicit assessment/questionnaire request at the RFE boundary."""
        normalized = self._normalize_entry_text(text)
        policy = self.document["entry_policy"]
        for prefix in policy["search_command_prefixes_ko"]:
            normalized_prefix = self._normalize_entry_text(prefix)
            if normalized.startswith(normalized_prefix):
                query = normalized[len(normalized_prefix):]
                if not query:
                    return {
                        "status": "search_term_required",
                        "workflow_state": "entry_unresolved",
                        "prompt_ko": policy["search_prompt_ko"],
                    }
                return self.search_entries(query)
        generic_aliases = {
            self._normalize_entry_text(alias)
            for alias in policy["generic_aliases_ko"]
        }
        if normalized in generic_aliases:
            return {
                "status": "selection_required",
                "workflow_state": "entry_unresolved",
                "prompt_ko": policy["generic_prompt_ko"],
                "options": [
                    {
                        "number": entry["selection_number"],
                        "program_id": entry["program_id"],
                        "display_ko": entry["display_ko"],
                    }
                    for entry in self.document["entry_catalog"]
                ],
            }

        matches = []
        for entry in self.document["entry_catalog"]:
            for alias in entry["aliases_ko"]:
                candidate = self._normalize_entry_text(alias)
                if normalized == candidate or candidate in normalized:
                    matches.append(entry)
                    break
        unique = {entry["program_id"]: entry for entry in matches}
        if len(unique) != 1:
            return {
                "status": "no_match" if not unique else "selection_required",
                "workflow_state": "entry_unresolved",
                "requested_text": text,
                "preserve_requested_title": True,
            }
        entry = next(iter(unique.values()))
        return self.entry_confirmation(entry["program_id"])

    def search_entries(self, query: str) -> dict[str, Any]:
        normalized_query = self._normalize_entry_text(query)
        matches = []
        for entry in self.document["entry_catalog"]:
            searchable = [entry["display_ko"], *entry["aliases_ko"]]
            if any(
                normalized_query in self._normalize_entry_text(value)
                for value in searchable
            ):
                matches.append({
                    "number": entry["selection_number"],
                    "program_id": entry["program_id"],
                    "display_ko": entry["display_ko"],
                    "entry_type": entry["entry_type"],
                    "runtime_readiness": entry["runtime_readiness"],
                })
        policy = self.document["entry_policy"]
        return {
            "status": "search_results" if matches else "no_search_result",
            "workflow_state": "entry_unresolved",
            "query": query,
            "prompt_ko": (
                "검색 결과에서 작성할 항목을 선택해 주세요."
                if matches else policy["no_search_result_ko"]
            ),
            "options": matches,
        }

    def select_entry(self, selection_number: int) -> dict[str, Any]:
        for entry in self.document["entry_catalog"]:
            if entry["selection_number"] == selection_number:
                return self.entry_confirmation(entry["program_id"])
        raise AssessmentContextError(f"unknown assessment selection: {selection_number}")

    def entry_confirmation(self, program_id: str) -> dict[str, Any]:
        if program_id not in self.entries:
            raise AssessmentContextError(f"unknown assessment program: {program_id}")
        entry = self.entries[program_id]
        program = self.programs[program_id]
        return {
            "status": "matched",
            "workflow_state": "awaiting_start_confirmation",
            "program_id": program_id,
            "display_ko": entry["display_ko"],
            "prompt_ko": entry["start_prompt_ko"],
            "options": self.document["entry_policy"]["start_confirmation_options"],
            "runtime_readiness": entry["runtime_readiness"],
            "safety_action_precedes_confirmation": program.get("activation", {}).get(
                "must_not_delay_emergency_assessment_or_treatment", False
            ),
        }

    def activate(self, program_id: str, context: dict[str, Any]) -> dict[str, Any]:
        if program_id not in self.programs:
            raise AssessmentContextError(f"unknown assessment program: {program_id}")
        if context.get("assessment_program_id") != program_id:
            raise AssessmentContextError("explicit matching assessment_program_id is required")

        program = self.programs[program_id]
        missing = [
            key for key in self.document["assessment_context"]["required_fields"]
            if context.get(key) in (None, "")
        ]
        if missing:
            raise AssessmentContextError(
                "missing assessment context: " + ", ".join(missing)
            )

        return {
            "program_id": program_id,
            "status": self.document["status"],
            "review_status": self.document["review_status"],
            "assessment_type": program["assessment_type"],
            "patient_interview": self._patient_interview(program),
            "excluded_from_patient_interview": self._excluded(program),
            "official_submission_requires_clinician_or_record_confirmation": program.get(
                "official_submission_requires_clinician_or_record_confirmation", True
            ),
        }

    @staticmethod
    def _patient_interview(program: dict[str, Any]) -> dict[str, Any]:
        assessment_type = program["assessment_type"]
        if assessment_type == "fixed_questionnaire":
            return {
                "mode": "fixed_questionnaire",
                "questionnaire_ref": program["questionnaire_ref"],
                "preserve_source_items": True,
                "section_count": program["section_count"],
                "question_count": program["question_count"],
            }
        if assessment_type == "fixed_standardized_instrument":
            return {
                "mode": "authorized_instrument_result_capture",
                "recognized_instruments": program["recognized_instruments"],
                "instrument_items_available": False,
                "result_capture_available": bool(program.get("result_capture_items")),
                "result_capture_items": program.get("result_capture_items", []),
                "reason": (
                    "exact authorized Korean instrument resource is required to "
                    "administer items; an existing named instrument result may be captured"
                ),
                "never_reconstruct_with_ai": True,
            }

        groups = []
        for group in program.get("patient_or_proxy_question_groups", []):
            groups.append({
                "id": group["id"],
                "display_ko": group.get("display_ko"),
                "items": [
                    item for item in group.get("items", [])
                    if {"patient_report", "proxy_report"} & set(item.get("source", []))
                ],
            })
        if program.get("patient_report_items"):
            groups.append({
                "id": f"{program['id']}.patient_report",
                "display_ko": "환자 보고 항목",
                "items": program["patient_report_items"],
            })
        return {
            "mode": "source_aware_structured_interview",
            "question_groups": groups,
            "reusable_modules": program.get("reusable_modules", []),
        }

    @staticmethod
    def _excluded(program: dict[str, Any]) -> dict[str, Any]:
        return {
            "structured_observation": program.get(
                "structured_observation_not_patient_questions", []
            ),
            "measurement_test_or_record": program.get(
                "measurement_test_or_record_requirements", []
            ),
            "clinician_test_components": program.get("clinician_test_components", []),
        }
