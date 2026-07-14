"""Korean national health-screening questionnaire orchestration.

This module evaluates repository knowledge only. Official NHIS entitlement is
external state and must be confirmed separately; a computed match is a
questionnaire candidate, not a promise of funded screening.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json

from runtime.memory import data_absent_reason
from preventive.consent import ConsentLedger


DEFAULT_KNOWLEDGE = (
    Path(__file__).resolve().parents[1]
    / "knowledge/preventive/kr-national-health-screening-2026.json"
)


def load_knowledge(path: Path | str = DEFAULT_KNOWLEDGE) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        knowledge = json.load(handle)
    if knowledge.get("status") != "research_only":
        raise ValueError("national screening knowledge must remain research_only")
    if knowledge.get("review_status") != "unreviewed":
        raise ValueError("generated national screening knowledge must be unreviewed")
    return knowledge


def _value(context: dict[str, Any], path: str) -> Any:
    current: Any = context
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _matches(condition: dict[str, Any], context: dict[str, Any]) -> bool:
    if "all" in condition:
        return all(_matches(item, context) for item in condition["all"])
    if "any" in condition:
        return any(_matches(item, context) for item in condition["any"])
    value = _value(context, condition["fact"])
    if "equals" in condition:
        return value == condition["equals"]
    if "in" in condition:
        return value in condition["in"]
    if "minimum" in condition:
        return isinstance(value, (int, float)) and value >= condition["minimum"]
    if "maximum" in condition:
        return isinstance(value, (int, float)) and value <= condition["maximum"]
    return False


def _consent_value(answer: str | int) -> tuple[str, str]:
    normalized = str(answer).strip().lower()
    if normalized in {"1", "yes", "y", "예", "네", "동의", "진행"}:
        return "accepted", normalized
    if normalized in {"2", "no", "n", "아니오", "아니요", "거절"}:
        return "declined", normalized
    if normalized in {"3", "unknown", "모름", "잘 모르겠음"}:
        return "unknown", normalized
    if normalized in {"4", "asked-declined", "답변 거부", "답변하고 싶지 않음"}:
        return "asked-declined", normalized
    raise ValueError("consent answer must be yes/no/unknown/declined or 1/2/3/4")


@dataclass
class NationalScreeningSession:
    session_id: str
    patient_context: dict[str, Any]
    knowledge_path: Path | str = DEFAULT_KNOWLEDGE
    knowledge: dict[str, Any] = field(init=False)
    consent_decisions: dict[str, dict[str, Any]] = field(default_factory=dict)
    active_groups: list[str] = field(default_factory=list)
    answers: dict[str, dict[str, Any]] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)
    consent_ledger: ConsentLedger = field(init=False)

    def __post_init__(self) -> None:
        self.knowledge = load_knowledge(self.knowledge_path)
        self.consent_ledger = ConsentLedger(
            self.session_id,
            self.patient_context.get("subject_ref", f"Patient/{self.session_id}"),
        )

    @property
    def groups(self) -> dict[str, dict[str, Any]]:
        return {item["id"]: item for item in self.knowledge["question_groups"]}

    def _base_eligible(self) -> set[str]:
        eligible = set()
        for group in self.knowledge["question_groups"]:
            condition = group.get("eligibility")
            if condition and "any_group_eligible" not in condition:
                if _matches(condition, self.patient_context):
                    eligible.add(group["id"])
        return eligible

    def eligible_group_ids(self) -> list[str]:
        eligible = self._base_eligible()
        for group in self.knowledge["question_groups"]:
            dependencies = group.get("eligibility", {}).get("any_group_eligible", [])
            if dependencies and eligible.intersection(dependencies):
                eligible.add(group["id"])
        return [
            group["id"] for group in self.knowledge["question_groups"]
            if group["id"] in eligible
        ]

    def offers(self) -> list[dict[str, Any]]:
        offers = []
        for group_id in self.eligible_group_ids():
            group = self.groups[group_id]
            offers.append({
                "offer_id": f"{self.session_id}.offer.{group_id}",
                "question_group_id": group_id,
                "title": deepcopy(group["title"]),
                "explanation": deepcopy(group["offer_explanation"]),
                "eligibility_certainty": "candidate",
                "official_entitlement_confirmation": "required",
                "official_confirmation_authority": "NHIS",
                "consent_required": True,
                "consent_shortcuts": {"1": "accept", "2": "decline", "3": "unknown", "4": "asked-declined"},
                "source_refs": deepcopy(group["source_refs"]),
            })
        return offers

    def decide(self, group_id: str, answer: str | int) -> dict[str, Any]:
        if group_id not in self.eligible_group_ids():
            raise ValueError(f"question group is not eligible: {group_id}")
        decision, raw = _consent_value(answer)
        record: dict[str, Any] = {
            "question_group_id": group_id,
            "decision": decision,
            "raw_input": raw,
        }
        if decision in {"unknown", "asked-declined"}:
            code = "asked-unknown" if decision == "unknown" else "asked-declined"
            record["dataAbsentReason"] = data_absent_reason(code)
        consent = self.consent_ledger.capture(
            scope=f"questionnaire-group:{group_id}",
            purpose="national-health-screening-questionnaire-participation",
            decision=decision,
            raw_input=raw,
            policy_uri="https://infoclinic.co/policy/screening-questionnaire-participation",
            policy_version="0.1.0-research",
            data_absent_reason=record.get("dataAbsentReason"),
        )
        record["consent_id"] = consent["consent_id"]
        self.consent_decisions[group_id] = record
        if decision == "accepted" and group_id not in self.active_groups:
            self.active_groups.append(group_id)
        elif decision != "accepted" and group_id in self.active_groups:
            self.active_groups.remove(group_id)
        self.events.append({"type": "questionnaire_consent_decided", **deepcopy(record)})
        return deepcopy(record)

    def active_questions(self) -> list[dict[str, Any]]:
        questions: list[dict[str, Any]] = []
        for group_id in self.active_groups:
            questions.extend(deepcopy(self.groups[group_id]["questions"]))
        return questions

    def answer(self, question_id: str, raw_input: Any, value: Any = None) -> dict[str, Any]:
        question = next(
            (item for item in self.active_questions() if item["id"] == question_id),
            None,
        )
        if not question:
            raise ValueError("question must belong to an accepted active group")
        raw = str(raw_input).strip()
        absent_map = {
            "3": "asked-unknown", "모름": "asked-unknown", "잘 모르겠음": "asked-unknown",
            "4": "not-applicable", "해당 없음": "not-applicable",
            "5": "asked-declined", "답변하고 싶지 않음": "asked-declined",
        }
        record: dict[str, Any] = {
            "question_id": question_id,
            "fact_id": question["fact_id"],
            "raw_input": raw,
            "status": "known",
            "value": raw_input if value is None else value,
        }
        if raw in absent_map:
            record.update({
                "status": "not_applicable" if absent_map[raw] == "not-applicable" else "unknown",
                "value": None,
                "dataAbsentReason": data_absent_reason(absent_map[raw]),
            })
        self.answers[question_id] = record
        self.events.append({"type": "screening_answer_recorded", **deepcopy(record)})
        return deepcopy(record)

    def snapshot(self, completed: bool = False) -> dict[str, Any]:
        return {
            "resource_type": "NationalHealthScreeningResponse",
            "schema_version": "0.1.0",
            "session_id": self.session_id,
            "jurisdiction": "KR",
            "program": "NHIS-national-health-screening",
            "knowledge_version": self.knowledge["version"],
            "status": "completed" if completed else "in_progress",
            "knowledge_status": "research_only",
            "review_status": "unreviewed",
            "patient_context": deepcopy(self.patient_context),
            "official_entitlement": "unverified",
            "eligible_question_groups": self.eligible_group_ids(),
            "consent_decisions": deepcopy(self.consent_decisions),
            "consents": self.consent_ledger.snapshot(),
            "active_question_groups": deepcopy(self.active_groups),
            "answers": deepcopy(self.answers),
            "events": deepcopy(self.events),
        }
