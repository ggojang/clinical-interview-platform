"""Minimal transparent runtime for the cough vertical slice.

This is intentionally deterministic and incomplete. It demonstrates repository
contracts; it is not a clinical product.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import re

REQUIRED = [
    "symptom.duration",
    "symptom.fever",
    "symptom.dyspnea",
    "symptom.hemoptysis",
    "symptom.chest_pain",
]

QUESTIONS = {
    "symptom.duration": "How long have you had the cough?",
    "symptom.fever": "Have you had a fever or felt feverish?",
    "symptom.dyspnea": "Have you felt short of breath or had trouble breathing?",
    "symptom.hemoptysis": "Have you noticed any blood when you cough?",
    "symptom.chest_pain": "Have you had any chest pain or discomfort?",
}

def extract_demo_facts(text: str) -> dict[str, dict[str, Any]]:
    """Extract a tiny set of English/Korean demo facts without an LLM."""
    lower = text.lower()
    facts: dict[str, dict[str, Any]] = {}

    day_match = re.search(r"\b(?:about\s+)?(\d+)\s*days?\b", lower)
    ko_day_match = re.search(r"(\d+|닷새|사흘|이틀)\s*(?:일|정도)?\s*(?:전부터|동안)?", text)
    ko_nums = {"이틀": 2, "사흘": 3, "닷새": 5}
    if day_match:
        amount = int(day_match.group(1))
        facts["symptom.duration"] = _fact({"amount": amount, "unit": "day"}, text, 0.96)
    elif ko_day_match:
        raw = ko_day_match.group(1)
        amount = ko_nums.get(raw, int(raw) if raw.isdigit() else None)
        if amount:
            facts["symptom.duration"] = _fact({"amount": amount, "unit": "day"}, text, 0.90)
    elif "yesterday" in lower or "어제" in text:
        facts["symptom.duration"] = _fact({"amount": 1, "unit": "day"}, text, 0.92)

    if any(x in lower for x in ["phlegm", "sputum", "mucus"]) or "가래" in text:
        facts["symptom.sputum"] = _fact(True, text, 0.95)

    if any(x in lower for x in ["hard to breathe", "harder to breathe", "trouble breathing", "short of breath"]) or "숨쉬기" in text or "숨이" in text:
        severity = "severe" if any(x in lower for x in ["very hard", "severe", "can't breathe", "cannot breathe"]) or "더 힘든" in text else "mild"
        facts["symptom.dyspnea"] = _fact(severity, text, 0.78)

    if "no fever" in lower or "열은 없" in text:
        facts["symptom.fever"] = _fact(False, text, 0.95)
    elif "fever" in lower or "열이" in text:
        facts["symptom.fever"] = _fact(True, text, 0.85)

    return facts

def _fact(value: Any, raw_text: str, confidence: float) -> dict[str, Any]:
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
        triggered.append("respiratory.severe_breathing_difficulty")
        return "emergency", triggered
    if hemoptysis is True:
        triggered.append("respiratory.hemoptysis")
    if chest_pain is True and dyspnea in {"moderate", "severe"}:
        triggered.append("respiratory.chest_pain_with_dyspnea")
    return ("urgent" if triggered else "routine"), triggered

def choose_next_question(facts: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    missing = [fact_id for fact_id in REQUIRED if fact_id not in facts]
    if not missing:
        return None

    # Safety-relevant order within required cough facts.
    order = [
        "symptom.dyspnea",
        "symptom.hemoptysis",
        "symptom.chest_pain",
        "symptom.fever",
        "symptom.duration",
    ]
    selected = next(fid for fid in order if fid in missing)
    score = 100 if selected in {"symptom.dyspnea", "symptom.hemoptysis"} else 70
    return {"fact_id": selected, "text": QUESTIONS[selected], "score": score}

def run_turn(session_id: str, utterance: str) -> dict[str, Any]:
    facts = extract_demo_facts(utterance)
    level, rules = safety_level(facts)
    question = choose_next_question(facts)
    missing = [fid for fid in REQUIRED if fid not in facts]
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
