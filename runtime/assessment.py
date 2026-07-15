"""Source-aware activation for HIRA adequacy-assessment interviews."""
from __future__ import annotations

import json
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
                "mode": "authorized_instrument_required",
                "recognized_instruments": program["recognized_instruments"],
                "items_available": False,
                "reason": "exact authorized Korean instrument resource is required",
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
