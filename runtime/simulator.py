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
                "not-performed": {"en": "It was not measured.", "ko": "측정하지 않았어요."},
            }
            return responses.get(absent_reason, responses["asked-unknown"]).get(
                language, responses["asked-unknown"]["en"]
            )
        state = self.case["hidden_state"].get(fact_id)
        if not state and fact_id in {"pain.frequency", "pain.nrs_score"}:
            # Shared pain Facts are composed at package Build Time and may not
            # exist in older synthetic fixtures. Derive deterministic test-only
            # answers from an explicit fixture severity. This is never used to
            # infer clinical patient data.
            pain_severity_facts = {
                "symptom.abdominal_pain.severity",
                "symptom.back_pain.severity",
                "symptom.chest_pain.severity",
                "symptom.headache.severity",
                "symptom.joint_limb.pain_severity",
                "symptom.skin_complaint.pain",
                "symptom.edema.pain",
                "symptom.throat_pain",
                "symptom.dysuria.severity",
                "ear.pain_severity",
                "eye.pain_severity",
            }
            severity = next((
                item.get("value")
                for key, item in self.case["hidden_state"].items()
                if key in pain_severity_facts
                and item.get("value") in {"none", "mild", "moderate", "severe"}
            ), None)
            if severity is None:
                existing_nrs = next((
                    item.get("value")
                    for key, item in self.case["hidden_state"].items()
                    if key in {
                        "oral.pain_score_zero_to_ten",
                        "injury.pain_zero_to_ten",
                        "lump.pain_nrs",
                        "dyspepsia.pain_nrs",
                        "thyroid.pain_nrs",
                    }
                    and isinstance(item.get("value"), int)
                    and 0 <= item["value"] <= 10
                ), None)
                if existing_nrs is not None:
                    if fact_id == "pain.nrs_score":
                        state = {"value": existing_nrs}
                    else:
                        state = {
                            "value": "none" if existing_nrs == 0 else "less_than_daily"
                        }
            if severity is None and state is None:
                initial_text = " ".join(
                    str(value)
                    for value in self.case.get("initial_statement", {}).values()
                ).lower()
                if any(term in initial_text for term in (
                    "pain", "ache", "아파", "통증", "두통"
                )):
                    severity = "moderate"
            if severity is not None and state is None:
                if fact_id == "pain.frequency":
                    state = {
                        "value": "none" if severity == "none" else "less_than_daily"
                    }
                else:
                    state = {"value": {
                        "none": 0, "mild": 2, "moderate": 5, "severe": 8,
                    }[severity]}
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
