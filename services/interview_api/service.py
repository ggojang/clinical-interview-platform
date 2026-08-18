"""Transport-independent application service for interview sessions.

The service deliberately keeps response-bearing state in memory.  It never
writes patient messages, Facts, traces, or handoff results to disk.  A caller
must explicitly export the final result before completing or deleting a
session.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
import time
from typing import Any, Callable
from uuid import UUID, uuid4

from runtime.core import CoreInteractionSession
from runtime.service_modes import ServiceModeRegistry
from services.interview_api.llm import (
    LlmProviderRegistry,
    LlmQuestionPresenter,
    LlmSelection,
    LlmSelectionError,
)


MAX_MESSAGE_CHARACTERS = 10_000
MIN_SESSION_TTL_SECONDS = 60
MAX_SESSION_TTL_SECONDS = 86_400


class ServiceError(Exception):
    """A stable, client-safe API error."""

    def __init__(
        self,
        status: int,
        code: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.details = details or {}

    def as_dict(self, request_id: str) -> dict[str, Any]:
        error: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "request_id": request_id,
        }
        if self.details:
            error["details"] = deepcopy(self.details)
        return {"error": error}


def _utc_iso(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )


def _validate_session_id(session_id: str) -> str:
    try:
        return str(UUID(session_id))
    except (ValueError, TypeError, AttributeError) as exc:
        raise ServiceError(400, "invalid_session_id", "session_id must be a UUID") from exc


def _optional_text(
    value: Any,
    field_name: str,
    *,
    max_characters: int = MAX_MESSAGE_CHARACTERS,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ServiceError(
            400,
            "invalid_request",
            f"{field_name} must be a string",
        )
    normalized = value.strip()
    if not normalized:
        raise ServiceError(
            400,
            "invalid_request",
            f"{field_name} must not be empty",
        )
    if len(normalized) > max_characters:
        raise ServiceError(
            413,
            "input_too_large",
            f"{field_name} exceeds {max_characters} characters",
        )
    return normalized


@dataclass
class SessionRecord:
    core: CoreInteractionSession
    created_at: float
    touched_at: float
    expires_at: float
    last_state: dict[str, Any]
    llm_selection: LlmSelection
    llm_presentation: dict[str, Any]
    lock: threading.RLock = field(default_factory=threading.RLock)


class InterviewApi:
    """Manage bounded, short-lived CoreInteractionSession instances."""

    def __init__(
        self,
        *,
        session_ttl_seconds: int = 1_800,
        max_sessions: int = 1_000,
        execution_mode: str = "research_test",
        clock: Callable[[], float] = time.time,
        session_factory: Callable[[str], CoreInteractionSession] | None = None,
        llm_registry: LlmProviderRegistry | None = None,
        llm_presenter: LlmQuestionPresenter | None = None,
    ) -> None:
        if not MIN_SESSION_TTL_SECONDS <= session_ttl_seconds <= MAX_SESSION_TTL_SECONDS:
            raise ValueError(
                f"session_ttl_seconds must be between {MIN_SESSION_TTL_SECONDS} "
                f"and {MAX_SESSION_TTL_SECONDS}"
            )
        if max_sessions < 1:
            raise ValueError("max_sessions must be positive")
        if execution_mode not in {"research_test", "clinician_supervised_pilot"}:
            raise ValueError(
                "the API may run only in research_test or clinician_supervised_pilot mode"
            )
        self.session_ttl_seconds = session_ttl_seconds
        self.max_sessions = max_sessions
        self.execution_mode = execution_mode
        self.clock = clock
        self.registry = ServiceModeRegistry()
        self.llm_registry = llm_registry or LlmProviderRegistry.from_env()
        self.llm_presenter = llm_presenter or LlmQuestionPresenter.from_env()
        self._session_factory = session_factory or (
            lambda session_id: CoreInteractionSession(
                session_id,
                execution_mode=execution_mode,
                clinician_submission=True,
                proactive_safety_questions=False,
            )
        )
        self._sessions: dict[str, SessionRecord] = {}
        self._lock = threading.RLock()

    def health(self) -> dict[str, Any]:
        self.purge_expired()
        with self._lock:
            active_sessions = len(self._sessions)
        return {
            "status": "ok",
            "service": "clinical-interview-api",
            "api_version": "v1",
            "execution_mode": self.execution_mode,
            "response_storage": "memory_only",
            "active_sessions": active_sessions,
            "llm": {
                "default_provider_id": self.llm_registry.default_provider_id,
                "presentation_enabled": self.llm_presenter.enabled,
                "runtime_role": "question_presentation_only",
            },
        }

    def catalog(self) -> dict[str, Any]:
        catalog = self.registry.catalog()
        catalog["api_capabilities"] = {
            "implemented_mode_ids": ["clinical_adaptive"],
            "pending_mode_ids": sorted(
                mode_id
                for mode_id in self.registry.modes
                if mode_id != "clinical_adaptive"
            ),
            "result_formats": {
                "clinical_handoff_json": "implemented",
                "fhir_questionnaire": "not_implemented",
                "fhir_questionnaire_response": "not_implemented",
                "sdc_extraction": "not_implemented",
            },
            "llm": self.llm_registry.catalog(
                presentation_enabled=self.llm_presenter.enabled
            ),
        }
        return catalog

    def llm_providers(self) -> dict[str, Any]:
        return self.llm_registry.catalog(
            presentation_enabled=self.llm_presenter.enabled
        )

    def create_session(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = payload or {}
        if not isinstance(payload, dict):
            raise ServiceError(400, "invalid_request", "request body must be an object")
        allowed = {
            "mode_selection",
            "initial_message",
            "llm_policy",
            "llm_selection",
        }
        unknown = sorted(set(payload) - allowed)
        if unknown:
            raise ServiceError(
                400,
                "invalid_request",
                "request body contains unsupported fields",
                details={"unsupported_fields": unknown},
            )
        mode_selection = _optional_text(payload.get("mode_selection"), "mode_selection")
        initial_message = _optional_text(payload.get("initial_message"), "initial_message")
        try:
            llm_selection = self.llm_registry.select(
                payload.get("llm_policy"), payload.get("llm_selection")
            )
        except LlmSelectionError as exc:
            raise ServiceError(400, exc.code, exc.message) from exc

        self.purge_expired()
        now = self.clock()
        with self._lock:
            if len(self._sessions) >= self.max_sessions:
                raise ServiceError(
                    503,
                    "session_capacity_reached",
                    "temporary session capacity has been reached",
                )
            session_id = str(uuid4())
            core = self._session_factory(session_id)
            try:
                state = core.start()
                if mode_selection is not None:
                    state = core.process(mode_selection)
                if initial_message is not None:
                    state = core.process(initial_message)
                presentation = self.llm_presenter.present(state, llm_selection)
            except Exception:
                core.close()
                raise
            record = SessionRecord(
                core=core,
                created_at=now,
                touched_at=now,
                expires_at=now + self.session_ttl_seconds,
                last_state=deepcopy(state),
                llm_selection=llm_selection,
                llm_presentation=deepcopy(presentation),
            )
            self._sessions[session_id] = record
        return self._session_document(session_id, record)

    def get_session(self, session_id: str) -> dict[str, Any]:
        session_id, record = self._record(session_id)
        with record.lock:
            self._touch(record)
            return self._session_document(session_id, record)

    def send_message(self, session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ServiceError(400, "invalid_request", "request body must be an object")
        unknown = sorted(set(payload) - {"message"})
        if unknown:
            raise ServiceError(
                400,
                "invalid_request",
                "request body contains unsupported fields",
                details={"unsupported_fields": unknown},
            )
        message = _optional_text(payload.get("message"), "message")
        if message is None:
            raise ServiceError(400, "invalid_request", "message is required")
        session_id, record = self._record(session_id)
        with record.lock:
            try:
                state = record.core.process(message)
            except RuntimeError as exc:
                raise ServiceError(409, "session_closed", "session is closed") from exc
            record.last_state = deepcopy(state)
            record.llm_presentation = self.llm_presenter.present(
                state, record.llm_selection
            )
            self._touch(record)
            return self._session_document(session_id, record)

    def result(self, session_id: str) -> dict[str, Any]:
        session_id, record = self._record(session_id)
        with record.lock:
            self._touch(record)
            return self._result_document(session_id, record)

    def complete(self, session_id: str) -> dict[str, Any]:
        session_id, record = self._record(session_id)
        with record.lock:
            result = self._result_document(session_id, record)
            closure = record.core.close()
        with self._lock:
            self._sessions.pop(session_id, None)
        return {
            "session_id": session_id,
            "status": "completed",
            "response_state_purged": True,
            "result": result,
            "closure": closure,
        }

    def delete_session(self, session_id: str) -> dict[str, Any]:
        session_id = _validate_session_id(session_id)
        with self._lock:
            record = self._sessions.pop(session_id, None)
        if record is None:
            raise ServiceError(404, "session_not_found", "session was not found or expired")
        with record.lock:
            closure = record.core.close()
        return {
            "session_id": session_id,
            "status": "deleted",
            "response_state_purged": True,
            "closure": closure,
        }

    def purge_expired(self) -> int:
        now = self.clock()
        expired: list[SessionRecord] = []
        with self._lock:
            for session_id, record in list(self._sessions.items()):
                if record.expires_at <= now:
                    expired.append(record)
                    self._sessions.pop(session_id, None)
        for record in expired:
            with record.lock:
                record.core.close()
        return len(expired)

    def purge_all(self) -> int:
        """Close every live session, for graceful shutdown and test cleanup."""
        with self._lock:
            records = list(self._sessions.values())
            self._sessions.clear()
        for record in records:
            with record.lock:
                record.core.close()
        return len(records)

    def _record(self, session_id: str) -> tuple[str, SessionRecord]:
        session_id = _validate_session_id(session_id)
        self.purge_expired()
        with self._lock:
            record = self._sessions.get(session_id)
        if record is None:
            raise ServiceError(404, "session_not_found", "session was not found or expired")
        return session_id, record

    def _touch(self, record: SessionRecord) -> None:
        now = self.clock()
        record.touched_at = now
        record.expires_at = now + self.session_ttl_seconds

    def _session_document(self, session_id: str, record: SessionRecord) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "status": "active",
            "mode_id": record.core.mode_id,
            "created_at": _utc_iso(record.created_at),
            "expires_at": _utc_iso(record.expires_at),
            "retention": {
                "storage": "memory_only",
                "ttl_seconds": self.session_ttl_seconds,
                "delete_endpoint": f"/v1/sessions/{session_id}",
            },
            "llm": record.llm_selection.public_document(
                presentation_enabled=self.llm_presenter.enabled
            ),
            "presentation": deepcopy(record.llm_presentation),
            "state": deepcopy(record.last_state),
        }

    def _result_document(self, session_id: str, record: SessionRecord) -> dict[str, Any]:
        if record.core.mode_id != "clinical_adaptive" or record.core.adapter is None:
            raise ServiceError(
                409,
                "result_not_ready",
                "this session does not yet have a completed runtime adapter result",
            )
        handoff = record.core.adapter.clinician_handoff()
        return {
            "session_id": session_id,
            "mode_id": record.core.mode_id,
            "lifecycle_status": "draft",
            "review_status": "unreviewed",
            "clinical_use_status": "limited",
            "independent_diagnosis_or_treatment": False,
            "llm": record.llm_selection.public_document(
                presentation_enabled=self.llm_presenter.enabled
            ),
            "available_formats": ["clinical_handoff_json"],
            "clinical_handoff": deepcopy(handoff),
            "fhir": {
                "status": "not_implemented",
                "planned_resources": ["Questionnaire", "QuestionnaireResponse"],
                "sdc_extraction": "not_implemented",
            },
        }
