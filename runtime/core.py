"""Purpose-first orchestration for the Clinical Questionnaire Platform.

This state machine selects a service mode before handing control to the
existing specialized runtime. It keeps the proven adaptive interview engine
intact while making interaction purpose the platform's primary entry point.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Callable

from runtime.service_modes import ServiceModeRegistry
from runtime.health_information import HealthInformationSession
from runtime.session import InterviewSession


@dataclass
class CoreInteractionSession:
    session_id: str
    registry: ServiceModeRegistry = field(default_factory=ServiceModeRegistry)
    execution_mode: str = "research_test"
    clinician_submission: bool = False
    encounter_context: dict[str, Any] | None = None
    proactive_safety_questions: bool = False
    clinical_interpreter: Callable[[str], dict[str, Any]] | None = None
    question_planner: Callable[[dict[str, Any], list[dict[str, Any]]], str | None] | None = None
    mode_id: str | None = None
    adapter: InterviewSession | HealthInformationSession | None = None
    closed: bool = False

    def start(self) -> dict[str, Any]:
        self._ensure_open()
        return self.registry.resolve()

    def select_mode(self, selection: str) -> dict[str, Any]:
        """Apply an API/UI mode selection without consuming an answer turn.

        ``mode_selection`` is control-plane input, not patient clinical text.
        Keeping it separate prevents labels such as ``문진 시작`` from being
        interpreted as the Reason for Encounter and creating a phantom Q1.
        """
        self._ensure_open()
        if self.mode_id is not None:
            return {
                "status": "mode_already_selected",
                "mode_id": self.mode_id,
                "runtime_adapter": self.registry.modes[self.mode_id]["runtime_adapter"],
            }
        resolution = self.registry.resolve(selection)
        if resolution["status"] != "resolved":
            return resolution
        self.mode_id = resolution["mode"]["id"]
        if self.mode_id == "health_information":
            self.adapter = HealthInformationSession(self.session_id)
        next_step = resolution.get("next", {"entry": resolution["mode"]["entry"]})
        if self.mode_id == "clinical_adaptive":
            next_step = {
                "entry": "reason_for_encounter",
                "prompt_ko": (
                    "오늘 진료받으려는 이유나 의료진에게 미리 전달할 내용을 "
                    "자유롭게 말씀해 주세요."
                ),
            }
        return {
            **resolution,
            "explicit_selection": True,
            "status": "mode_ready",
            "runtime_adapter": resolution["mode"]["runtime_adapter"],
            "next": next_step,
        }

    def process(self, message: str) -> dict[str, Any]:
        self._ensure_open()
        if self.mode_id == "clinical_adaptive":
            if self.adapter is None:
                return self._activate_clinical(message)
            return self._wrap(self.adapter.process(message))
        if self.mode_id == "health_information":
            if self.adapter is None:
                self.adapter = HealthInformationSession(self.session_id)
            return self._wrap_health_information(self.adapter.process(message))
        if self.mode_id is not None:
            return {
                "status": "adapter_input_required",
                "mode_id": self.mode_id,
                "runtime_adapter": self.registry.modes[self.mode_id]["runtime_adapter"],
            }

        resolution = self.registry.resolve(message)
        if resolution["status"] != "resolved":
            return resolution
        self.mode_id = resolution["mode"]["id"]

        if self.mode_id == "clinical_adaptive":
            if resolution.get("explicit_selection"):
                # Direct conversational callers may use an exact mode alias.
                # API callers use ``select_mode`` so even inferred labels are
                # never consumed as clinical content.
                return self._selected_mode_ready(resolution)
            return self._activate_clinical(message, resolution=resolution)

        if self.mode_id == "health_information":
            self.adapter = HealthInformationSession(self.session_id)

        return {
            **resolution,
            "status": "mode_ready",
            "runtime_adapter": resolution["mode"]["runtime_adapter"],
            "next": resolution.get("next", {
                "entry": resolution["mode"]["entry"],
            }),
        }

    def _selected_mode_ready(self, resolution: dict[str, Any]) -> dict[str, Any]:
        return {
            **resolution,
            "explicit_selection": True,
            "status": "mode_ready",
            "runtime_adapter": resolution["mode"]["runtime_adapter"],
            "next": {
                "entry": "reason_for_encounter",
                "prompt_ko": (
                    "오늘 진료받으려는 이유나 의료진에게 미리 전달할 내용을 "
                    "자유롭게 말씀해 주세요."
                ),
            },
        }

    def _wrap_health_information(
        self, adapter_state: dict[str, Any]
    ) -> dict[str, Any]:
        return {
            "status": "active",
            "mode_id": "health_information",
            "core_entry": "interaction_purpose",
            "adapter_state": adapter_state,
        }

    def close(self) -> dict[str, Any]:
        if self.closed:
            return {"status": "closed", "response_state_purged": True}
        adapter_result = self.adapter.close() if self.adapter is not None else None
        self.adapter = None
        self.mode_id = None
        self.closed = True
        return {
            "status": "closed",
            "response_state_purged": True,
            "adapter_result": adapter_result,
        }

    def _wrap(
        self,
        adapter_state: dict[str, Any],
        *,
        resolution: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "status": "active",
            "mode_id": "clinical_adaptive",
            "core_entry": "interaction_purpose",
            "resolution": resolution,
            "adapter_state": adapter_state,
        }

    def _activate_clinical(
        self,
        message: str,
        *,
        resolution: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        rfe = self.registry.match_reason_for_encounter(message)
        interpretation = None
        if rfe is None and self.clinical_interpreter is not None:
            interpretation = self.clinical_interpreter(message)
            if interpretation.get("status") == "resolved":
                rfe_id = interpretation.get("rfe_id")
                if isinstance(rfe_id, str):
                    rfe = self.registry.reason_for_encounter_by_id(rfe_id)
        if rfe is None:
            candidates = (
                interpretation.get("candidates", [])
                if isinstance(interpretation, dict) else []
            )
            return {
                "status": "reason_for_encounter_clarification",
                "mode_id": "clinical_adaptive",
                "core_entry": "interaction_purpose",
                "prompt_ko": (
                    "말씀하신 내용을 어느 문진으로 진행할지 확인이 필요합니다. "
                    "가장 가까운 증상이나 상담 목적을 조금 더 구체적으로 알려주세요."
                ),
                "candidates": candidates,
                "clinical_interpretation": interpretation,
            }
        self.adapter = InterviewSession(
            self.session_id,
            package_path=self.registry.package_path_for(rfe),
            execution_mode=self.execution_mode,
            reason_for_encounter=rfe["id"],
            clinician_submission=self.clinician_submission,
            encounter_context=self.encounter_context or {
                "care_setting": "primary_care",
                "encounter_type": "new_encounter",
                "interview_initiator": "patient",
                "interview_mode": "chat",
                "available_information": ["scheduled_visit", "no_previous_records"],
                "time_constraint": "scheduled",
                "clinical_responsibility": "decision_support",
            },
            proactive_safety_questions=self.proactive_safety_questions,
            question_planner=self.question_planner,
        )
        wrapped = self._wrap(self.adapter.process(message), resolution=resolution)
        if interpretation is not None:
            wrapped["clinical_interpretation"] = interpretation
        return wrapped

    def _ensure_open(self) -> None:
        if self.closed:
            raise RuntimeError("core interaction session is closed")


# Backward-compatible deterministic cough-slice API.  This remains available
# for existing examples and tests; new multi-purpose callers use
# CoreInteractionSession above.
_LEGACY_REQUIRED = [
    "symptom.duration",
    "symptom.fever",
    "symptom.dyspnea",
    "symptom.hemoptysis",
    "symptom.chest_pain",
]
_LEGACY_QUESTIONS = {
    "symptom.duration": "How long have you had the cough?",
    "symptom.fever": "Have you had a fever or felt feverish?",
    "symptom.dyspnea": "Have you felt short of breath or had trouble breathing?",
    "symptom.hemoptysis": "Have you noticed any blood when you cough?",
    "symptom.chest_pain": "Have you had any chest pain or discomfort?",
}


def extract_demo_facts(text: str) -> dict[str, dict[str, Any]]:
    """Extract the original tiny set of demo facts without an LLM."""
    lower = text.lower()
    facts: dict[str, dict[str, Any]] = {}
    day_match = re.search(r"\b(?:about\s+)?(\d+)\s*days?\b", lower)
    ko_day_match = re.search(
        r"(\d+|닷새|사흘|이틀)\s*(?:일|정도)?\s*(?:전부터|동안)?", text
    )
    ko_nums = {"이틀": 2, "사흘": 3, "닷새": 5}
    if day_match:
        facts["symptom.duration"] = _demo_fact(
            {"amount": int(day_match.group(1)), "unit": "day"}, text, 0.96
        )
    elif ko_day_match:
        raw = ko_day_match.group(1)
        amount = ko_nums.get(raw, int(raw) if raw.isdigit() else None)
        if amount:
            facts["symptom.duration"] = _demo_fact(
                {"amount": amount, "unit": "day"}, text, 0.90
            )
    elif "yesterday" in lower or "어제" in text:
        facts["symptom.duration"] = _demo_fact(
            {"amount": 1, "unit": "day"}, text, 0.92
        )
    if any(x in lower for x in ["phlegm", "sputum", "mucus"]) or "가래" in text:
        facts["symptom.sputum"] = _demo_fact(True, text, 0.95)
    if any(
        x in lower
        for x in [
            "hard to breathe",
            "harder to breathe",
            "trouble breathing",
            "short of breath",
        ]
    ) or "숨쉬기" in text or "숨이" in text:
        severe = any(
            x in lower for x in ["very hard", "severe", "can't breathe", "cannot breathe"]
        ) or "더 힘든" in text
        facts["symptom.dyspnea"] = _demo_fact(
            "severe" if severe else "mild", text, 0.78
        )
    if "no fever" in lower or "열은 없" in text:
        facts["symptom.fever"] = _demo_fact(False, text, 0.95)
    elif "fever" in lower or "열이" in text:
        facts["symptom.fever"] = _demo_fact(True, text, 0.85)
    return facts


def _demo_fact(value: Any, raw_text: str, confidence: float) -> dict[str, Any]:
    return {
        "status": "known",
        "value": value,
        "raw_text": raw_text,
        "confidence": confidence,
        "evidence": [{"speaker": "patient", "turn": 1, "text": raw_text}],
    }


def safety_level(facts: dict[str, dict[str, Any]]) -> tuple[str, list[str]]:
    triggered: list[str] = []
    dyspnea = facts.get("symptom.dyspnea", {}).get("value")
    hemoptysis = facts.get("symptom.hemoptysis", {}).get("value")
    chest_pain = facts.get("symptom.chest_pain", {}).get("value")
    if dyspnea == "severe":
        return "emergency", ["respiratory.severe_breathing_difficulty"]
    if hemoptysis is True:
        triggered.append("respiratory.hemoptysis")
    if chest_pain is True and dyspnea in {"moderate", "severe"}:
        triggered.append("respiratory.chest_pain_with_dyspnea")
    return ("urgent" if triggered else "routine"), triggered


def choose_next_question(
    facts: dict[str, dict[str, Any]],
) -> dict[str, Any] | None:
    missing = [fact_id for fact_id in _LEGACY_REQUIRED if fact_id not in facts]
    if not missing:
        return None
    order = [
        "symptom.dyspnea",
        "symptom.hemoptysis",
        "symptom.chest_pain",
        "symptom.fever",
        "symptom.duration",
    ]
    selected = next(fact_id for fact_id in order if fact_id in missing)
    score = 100 if selected in {"symptom.dyspnea", "symptom.hemoptysis"} else 70
    return {"fact_id": selected, "text": _LEGACY_QUESTIONS[selected], "score": score}


def run_turn(session_id: str, utterance: str) -> dict[str, Any]:
    """Run the original single-turn cough demonstration unchanged."""
    facts = extract_demo_facts(utterance)
    level, rules = safety_level(facts)
    question = choose_next_question(facts)
    missing = [fact_id for fact_id in _LEGACY_REQUIRED if fact_id not in facts]
    return {
        "session_id": session_id,
        "turn": 1,
        "patient_context": {},
        "facts": facts,
        "active_patterns": ["respiratory.cough"],
        "contradictions": [],
        "safety_status": {"level": level, "triggered_rules": rules},
        "missing_facts": missing,
        "selected_question": question,
        "trace": [{
            "step": "prioritize",
            "inputs": {"missing_facts": missing, "safety_level": level},
            "output": question,
        }],
    }
