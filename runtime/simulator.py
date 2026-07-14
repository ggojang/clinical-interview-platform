"""Deterministic synthetic patient for automated multi-turn demos."""
from __future__ import annotations
from typing import Any

class PatientSimulator:
    def __init__(self, case: dict[str, Any]):
        self.case = case

    def initial(self, language: str = "en") -> str:
        return self.case["initial_statement"].get(language) or next(iter(self.case["initial_statement"].values()))

    def answer(self, fact_id: str) -> str:
        language = self.case.get("simulation_language", "en")
        behavior = self.case.get("response_behavior", {}).get(fact_id, {})
        absent_reason = behavior.get("dataAbsentReason")
        if absent_reason:
            responses = {
                "asked-unknown": {"en": "I am not sure.", "ko": "잘 모르겠어요."},
                "asked-declined": {"en": "I prefer not to answer.", "ko": "답하고 싶지 않아요."},
                "not-applicable": {"en": "Not applicable.", "ko": "해당되지 않아요."},
            }
            return responses.get(absent_reason, responses["asked-unknown"]).get(
                language, responses["asked-unknown"]["en"]
            )
        state = self.case["hidden_state"].get(fact_id)
        if not state:
            return "잘 모르겠어요." if language == "ko" else "I am not sure."
        value = state["value"]
        if isinstance(value, bool):
            if language == "ko":
                return "네." if value else "아니요."
            return "Yes." if value else "No."
        if isinstance(value, dict) and {"amount", "unit"} <= set(value):
            if fact_id == "observation.body_temperature":
                suffix = "°C" if value["unit"] == "Cel" else "°F"
                return f"{value['amount']}{suffix}"
            return f"{value['amount']} {value['unit']}{'' if value['amount'] == 1 else 's'}."
        if fact_id == "symptom.dyspnea":
            if language == "ko":
                return {
                    "none": "아니요.",
                    "mild": "네, 조금 숨이 차요.",
                    "moderate": "네, 숨쉬기가 꽤 힘들어요.",
                    "severe": "네, 숨쉬기가 매우 힘들어요.",
                }.get(value, str(value))
            return {
                "none": "No.",
                "mild": "Yes, a little.",
                "moderate": "Yes, it is noticeable.",
                "severe": "Yes, it is very hard to breathe.",
            }.get(value, str(value))
        return str(value)
