"""Independent, append-only consent records for screening workflows."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConsentLedger:
    session_id: str
    subject_ref: str
    records: list[dict[str, Any]] = field(default_factory=list)

    def capture(
        self,
        *,
        scope: str,
        purpose: str,
        decision: str,
        raw_input: str,
        policy_uri: str,
        policy_version: str,
        method: str = "chat",
        captured_at: str = "2026-07-14T00:00:00+09:00",
        data_absent_reason: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if decision not in {"accepted", "declined", "unknown", "asked-declined"}:
            raise ValueError("unsupported consent decision")
        record = {
            "consent_id": f"{self.session_id}.consent.{len(self.records) + 1:04d}",
            "subject_ref": self.subject_ref,
            "scope": scope,
            "purpose": purpose,
            "decision": decision,
            "lifecycle_status": "active" if decision == "accepted" else "inactive",
            "raw_input": raw_input,
            "method": method,
            "captured_at": captured_at,
            "policy": {"uri": policy_uri, "version": policy_version},
            "provenance": {
                "actor": "patient",
                "recorded_by": "adaptive-interview-runtime",
                "knowledge_status": "research_only",
            },
        }
        if data_absent_reason:
            record["dataAbsentReason"] = deepcopy(data_absent_reason)
        self.records.append(record)
        return deepcopy(record)

    def withdraw(
        self,
        consent_id: str,
        *,
        raw_input: str,
        withdrawn_at: str = "2026-07-14T00:00:00+09:00",
    ) -> dict[str, Any]:
        current = next((item for item in self.records if item["consent_id"] == consent_id), None)
        if not current:
            raise ValueError("consent record not found")
        if current["decision"] != "accepted" or current["lifecycle_status"] != "active":
            raise ValueError("only active accepted consent can be withdrawn")
        current["lifecycle_status"] = "withdrawn"
        current["withdrawn_at"] = withdrawn_at
        current["withdrawal_raw_input"] = raw_input
        return deepcopy(current)

    def latest_for_scope(self, scope: str) -> dict[str, Any] | None:
        matches = [item for item in self.records if item["scope"] == scope]
        return deepcopy(matches[-1]) if matches else None

    def snapshot(self) -> list[dict[str, Any]]:
        return deepcopy(self.records)
