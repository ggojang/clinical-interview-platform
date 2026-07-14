"""Evidence-preserving Clinical Memory for one interview session."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


DATA_ABSENT_REASON_SYSTEM = (
    "http://terminology.hl7.org/CodeSystem/data-absent-reason"
)
DATA_ABSENT_REASON_DISPLAYS = {
    "unknown": "Unknown",
    "asked-unknown": "Asked But Unknown",
    "temp-unknown": "Temporarily Unknown",
    "not-asked": "Not Asked",
    "asked-declined": "Asked But Declined",
    "masked": "Masked",
    "not-applicable": "Not Applicable",
    "unsupported": "Unsupported",
    "as-text": "As Text",
    "error": "Error",
    "not-a-number": "Not a Number",
    "negative-infinity": "Negative Infinity",
    "positive-infinity": "Positive Infinity",
    "not-performed": "Not Performed",
}


def data_absent_reason(code: str) -> dict[str, str]:
    if code not in DATA_ABSENT_REASON_DISPLAYS:
        raise ValueError(f"unsupported dataAbsentReason code: {code}")
    return {
        "system": DATA_ABSENT_REASON_SYSTEM,
        "code": code,
        "display": DATA_ABSENT_REASON_DISPLAYS[code],
    }


@dataclass
class ClinicalMemory:
    session_id: str
    package_id: str
    package_version: str
    turn: int = 0
    facts: dict[str, dict[str, Any]] = field(default_factory=dict)
    contradictions: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)

    def next_turn(self) -> int:
        self.turn += 1
        return self.turn

    def _event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = {
            "event_id": f"{self.session_id}.event.{len(self.events) + 1:04d}",
            "session_id": self.session_id,
            "sequence": len(self.events) + 1,
            "type": event_type,
            "actor": payload.get("actor", "runtime"),
            "created_at": payload.get("created_at", "2026-07-13T00:00:00Z"),
            "package_id": self.package_id,
            "package_version": self.package_version,
            "payload": deepcopy(payload),
        }
        self.events.append(event)
        return event

    def observe(self, text: str, actor: str = "patient") -> dict[str, Any]:
        return self._event("evidence_observed", {
            "actor": actor,
            "turn": self.turn,
            "text": text,
        })

    def record_event(self, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Record a non-clinical workflow event in the session audit trail."""
        return self._event(event_type, payload)

    def merge(self, fact_id: str, candidate: dict[str, Any]) -> str:
        """Merge one supported candidate without overwriting prior evidence."""
        evidence = deepcopy(candidate.get("evidence", []))
        if not evidence:
            evidence = [{
                "speaker": candidate.get("speaker", "patient"),
                "turn": self.turn,
                "text": candidate.get("raw_text", ""),
            }]
        incoming_value = deepcopy(candidate.get("value"))
        incoming = {
            "value": incoming_value,
            "raw_text": candidate.get("raw_text", ""),
            "confidence": candidate.get("confidence", 0.0),
            "evidence": evidence,
            "turn": self.turn,
            "correction": bool(candidate.get("correction", False)),
        }
        current = self.facts.get(fact_id)

        if current is None:
            prior_history = deepcopy(current.get("history", [])) if current else []
            self.facts[fact_id] = {
                "status": "known",
                "value": incoming_value,
                "raw_text": incoming["raw_text"],
                "confidence": incoming["confidence"],
                "evidence": evidence,
                "history": prior_history + [incoming],
            }
            outcome = "added"
        elif candidate.get("correction"):
            prior = deepcopy(current)
            self.facts[fact_id] = {
                "status": "known",
                "value": incoming_value,
                "raw_text": incoming["raw_text"],
                "confidence": incoming["confidence"],
                "evidence": deepcopy(current.get("evidence", [])) + evidence,
                "history": deepcopy(current.get("history", [])) + [incoming],
                "corrected_from": prior.get("value"),
            }
            for conflict in reversed(self.contradictions):
                if conflict["fact_id"] == fact_id and conflict["status"] == "unresolved":
                    conflict["status"] = "resolved"
                    conflict["resolution_turn"] = self.turn
                    conflict["resolution_value"] = incoming_value
                    break
            outcome = "corrected"
        elif current.get("status") in {"unknown", "not_asked", "not_applicable"}:
            prior_history = deepcopy(current.get("history", []))
            self.facts[fact_id] = {
                "status": "known",
                "value": incoming_value,
                "raw_text": incoming["raw_text"],
                "confidence": incoming["confidence"],
                "evidence": deepcopy(current.get("evidence", [])) + evidence,
                "history": prior_history + [incoming],
            }
            outcome = "added"
        elif current.get("status") == "known" and current.get("value") == incoming_value:
            current.setdefault("evidence", []).extend(evidence)
            current.setdefault("history", []).append(incoming)
            current["confidence"] = max(current.get("confidence", 0.0), incoming["confidence"])
            outcome = "reinforced"
        else:
            alternatives = []
            if current.get("status") == "conflicted":
                alternatives.extend(deepcopy(current.get("alternatives", [])))
            else:
                alternatives.append({
                    "value": deepcopy(current.get("value")),
                    "evidence": deepcopy(current.get("evidence", [])),
                })
            if not any(item.get("value") == incoming_value for item in alternatives):
                alternatives.append({"value": incoming_value, "evidence": evidence})
            history = deepcopy(current.get("history", [])) + [incoming]
            self.facts[fact_id] = {
                "status": "conflicted",
                "value": None,
                "raw_text": incoming["raw_text"],
                "confidence": min(current.get("confidence", 0.0), incoming["confidence"]),
                "evidence": deepcopy(current.get("evidence", [])) + evidence,
                "history": history,
                "alternatives": alternatives,
            }
            conflict = {
                "id": f"{self.session_id}.conflict.{len(self.contradictions) + 1:03d}",
                "fact_id": fact_id,
                "status": "unresolved",
                "detected_turn": self.turn,
                "values": [item["value"] for item in alternatives],
                "package_id": self.package_id,
                "package_version": self.package_version,
            }
            self.contradictions.append(conflict)
            outcome = "conflicted"

        self._event("fact_merged", {
            "actor": "runtime",
            "turn": self.turn,
            "fact_id": fact_id,
            "outcome": outcome,
            "candidate": incoming,
        })
        return outcome

    def mark_absent(
        self,
        fact_id: str,
        raw_text: str,
        reason_code: str,
        *,
        correction: bool = False,
    ) -> str:
        evidence = [{
            "speaker": "patient",
            "turn": self.turn,
            "text": raw_text,
        }]
        reason = data_absent_reason(reason_code)
        status = "not_applicable" if reason_code == "not-applicable" else "unknown"
        current = self.facts.get(fact_id)
        prior_history = deepcopy(current.get("history", [])) if current else []
        history_entry = {
            "value": None,
            "dataAbsentReason": reason,
            "raw_text": raw_text,
            "confidence": 1.0,
            "evidence": evidence,
            "turn": self.turn,
            "correction": correction,
        }
        record = {
            "status": status,
            "value": None,
            "dataAbsentReason": reason,
            "raw_text": raw_text,
            "confidence": 1.0,
            "evidence": evidence,
            "history": prior_history + [history_entry],
        }
        if correction and current:
            record["corrected_from"] = {
                "status": current.get("status"),
                "value": deepcopy(current.get("value")),
                "dataAbsentReason": deepcopy(current.get("dataAbsentReason")),
            }
            record["evidence"] = deepcopy(current.get("evidence", [])) + evidence
            for conflict in reversed(self.contradictions):
                if conflict["fact_id"] == fact_id and conflict["status"] == "unresolved":
                    conflict["status"] = "resolved"
                    conflict["resolution_turn"] = self.turn
                    conflict["resolution_dataAbsentReason"] = deepcopy(reason)
                    break
        self.facts[fact_id] = record
        self._event("fact_marked_data_absent", {
            "actor": "runtime",
            "turn": self.turn,
            "fact_id": fact_id,
            "raw_text": raw_text,
            "dataAbsentReason": reason,
            "correction": correction,
        })
        return "corrected" if correction and current else reason_code

    def mark_unknown(self, fact_id: str, raw_text: str) -> None:
        self.mark_absent(fact_id, raw_text, "asked-unknown")

    def state(self, fact_id: str) -> str:
        return self.facts.get(fact_id, {}).get("status", "not_asked")

    def value(self, fact_id: str) -> Any:
        record = self.facts.get(fact_id)
        return record.get("value") if record and record.get("status") == "known" else None

    def absent_reason(self, fact_id: str) -> str | None:
        return self.facts.get(fact_id, {}).get("dataAbsentReason", {}).get("code")

    def snapshot(self) -> dict[str, Any]:
        absent = {
            fact_id: deepcopy(record["dataAbsentReason"])
            for fact_id, record in self.facts.items()
            if "dataAbsentReason" in record
        }
        return {
            "session_id": self.session_id,
            "turn": self.turn,
            "facts": deepcopy(self.facts),
            "data_absent_facts": absent,
            "contradictions": deepcopy(self.contradictions),
            "events": deepcopy(self.events),
            "package": {
                "id": self.package_id,
                "version": self.package_version,
            },
        }
