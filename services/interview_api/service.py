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
import json
from pathlib import Path
import threading
import time
from typing import Any, Callable
from uuid import UUID, uuid4

from runtime.core import CoreInteractionSession
from runtime.service_modes import ServiceModeRegistry
from services.interview_api.llm import (
    LlmAdaptiveAnswerInterpreter,
    LlmChatbotInterviewRuntime,
    LlmChatbotRuntimeError,
    LlmClinicalInterpreter,
    LlmHealthInformationAdvisor,
    LlmInterviewPlanner,
    LlmProviderRegistry,
    LlmQuestionPresenter,
    LlmSelection,
    LlmSelectionError,
)
from services.interview_api.terminology import TerminologyClient, TerminologyError


MAX_MESSAGE_CHARACTERS = 10_000
MIN_SESSION_TTL_SECONDS = 60
MAX_SESSION_TTL_SECONDS = 86_400
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEMO_RESOURCE_PATHS = {
    "patient-experience-5th-2025": (
        REPOSITORY_ROOT
        / "fhir/r4/questionnaires/kr-patient-experience-evaluation-5th-2025.json"
    ),
    "national-health-screening-form-1-2025": (
        REPOSITORY_ROOT / "fhir/r4/questionnaires/kr-national-health-screening-form-1-2025.json"
    ),
    "national-health-screening-form-2-2025": (
        REPOSITORY_ROOT / "fhir/r4/questionnaires/kr-national-health-screening-form-2-2025.json"
    ),
}


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
    access_scope: str = "authenticated"
    lock: threading.RLock = field(default_factory=threading.RLock)


class InterviewApi:
    """Manage bounded, short-lived CoreInteractionSession instances."""

    def __init__(
        self,
        *,
        session_ttl_seconds: int = 1_800,
        max_sessions: int = 1_000,
        max_anonymous_demo_sessions: int | None = None,
        anonymous_demo_ttl_seconds: int | None = None,
        execution_mode: str = "research_test",
        clock: Callable[[], float] = time.time,
        session_factory: Callable[[str], CoreInteractionSession] | None = None,
        llm_registry: LlmProviderRegistry | None = None,
        llm_presenter: LlmQuestionPresenter | None = None,
        clinical_interpreter: LlmClinicalInterpreter | None = None,
        interview_planner: LlmInterviewPlanner | None = None,
        answer_interpreter: LlmAdaptiveAnswerInterpreter | None = None,
        health_information_advisor: LlmHealthInformationAdvisor | None = None,
        chatbot_runtime: LlmChatbotInterviewRuntime | None = None,
        terminology_client: TerminologyClient | None = None,
    ) -> None:
        if not MIN_SESSION_TTL_SECONDS <= session_ttl_seconds <= MAX_SESSION_TTL_SECONDS:
            raise ValueError(
                f"session_ttl_seconds must be between {MIN_SESSION_TTL_SECONDS} "
                f"and {MAX_SESSION_TTL_SECONDS}"
            )
        if max_sessions < 1:
            raise ValueError("max_sessions must be positive")
        if max_anonymous_demo_sessions is None:
            max_anonymous_demo_sessions = min(50, max_sessions)
        if anonymous_demo_ttl_seconds is None:
            anonymous_demo_ttl_seconds = min(600, session_ttl_seconds)
        if max_anonymous_demo_sessions < 1 or max_anonymous_demo_sessions > max_sessions:
            raise ValueError("max_anonymous_demo_sessions must be positive and not exceed max_sessions")
        if not MIN_SESSION_TTL_SECONDS <= anonymous_demo_ttl_seconds <= session_ttl_seconds:
            raise ValueError("anonymous_demo_ttl_seconds must be between 60 and session_ttl_seconds")
        if execution_mode not in {"research_test", "clinician_supervised_pilot"}:
            raise ValueError(
                "the API may run only in research_test or clinician_supervised_pilot mode"
            )
        self.session_ttl_seconds = session_ttl_seconds
        self.max_sessions = max_sessions
        self.max_anonymous_demo_sessions = max_anonymous_demo_sessions
        self.anonymous_demo_ttl_seconds = anonymous_demo_ttl_seconds
        self.execution_mode = execution_mode
        self.clock = clock
        self.registry = ServiceModeRegistry()
        self.llm_registry = llm_registry or LlmProviderRegistry.from_env()
        self.llm_presenter = llm_presenter or LlmQuestionPresenter.from_env()
        self.clinical_interpreter = (
            clinical_interpreter or LlmClinicalInterpreter.from_env()
        )
        self.interview_planner = interview_planner or LlmInterviewPlanner.from_env()
        self.answer_interpreter = (
            answer_interpreter or LlmAdaptiveAnswerInterpreter.from_env()
        )
        self.health_information_advisor = (
            health_information_advisor or LlmHealthInformationAdvisor.from_env()
        )
        self.chatbot_runtime = (
            chatbot_runtime or LlmChatbotInterviewRuntime.from_env()
        )
        self.terminology_client = terminology_client or TerminologyClient.from_env()
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
                "interpretation_enabled": self.clinical_interpreter.enabled,
                "planning_enabled": False,
                "answer_interpretation_enabled": False,
                "runtime_role": "custom_gpt_conversation_runtime",
                "conversation_runtime_enabled": self.chatbot_runtime.enabled,
                "instructions": self.chatbot_runtime.instructions_source,
                "health_information_instructions": (
                    self.chatbot_runtime.health_instructions_source
                ),
                "instruction_profile": self.chatbot_runtime.instruction_profile,
                "knowledge_delivery": self.chatbot_runtime.knowledge_delivery,
                "legacy_deterministic_fallback": False,
                "health_information_enabled": self.health_information_advisor.enabled,
            },
            "terminology": self.terminology_client.configuration(),
        }

    def catalog(self) -> dict[str, Any]:
        catalog = self.registry.catalog()
        catalog["api_capabilities"] = {
            "implemented_mode_ids": ["clinical_adaptive", "health_information"],
            "pending_mode_ids": sorted(
                mode_id
                for mode_id in self.registry.modes
                if mode_id not in {"clinical_adaptive", "health_information"}
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

    def terminology_status(self) -> dict[str, Any]:
        try:
            return self.terminology_client.status()
        except TerminologyError as exc:
            raise ServiceError(exc.status, exc.code, exc.message) from exc

    def expand_valueset(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ServiceError(400, "invalid_request", "request body must be an object")
        unknown = sorted(set(payload) - {"url", "filter", "count"})
        if unknown:
            raise ServiceError(
                400,
                "invalid_request",
                "terminology expansion request contains unsupported fields",
                details={"unsupported_fields": unknown},
            )
        try:
            return self.terminology_client.expand(
                payload.get("url"),
                filter_text=payload.get("filter"),
                count=payload.get("count", 50),
            )
        except TerminologyError as exc:
            raise ServiceError(exc.status, exc.code, exc.message) from exc

    def demo_resources(self) -> dict[str, Any]:
        """List allowlisted, non-response-bearing resources used by the demo UI."""
        return {
            "resources": [
                {
                    "id": "patient-experience-5th-2025",
                    "title": "2025년(5차) 환자경험평가 설문지",
                    "kind": "fhir_questionnaire",
                    "fhir_version": "R4",
                    "source_defined": True,
                    "use": "internal_research_test",
                },
                {
                    "id": "national-health-screening-form-1-2025",
                    "title": "건강검진 문진표 (별지 제1호 서식, 개정 2025. 1. 1.)",
                    "kind": "fhir_questionnaire",
                    "fhir_version": "R4",
                    "source_defined": True,
                    "use": "internal_research_test",
                },
                {
                    "id": "national-health-screening-form-2-2025",
                    "title": "건강검진 추가 문진표 (별지 제2호 서식)",
                    "kind": "fhir_questionnaire",
                    "fhir_version": "R4",
                    "source_defined": True,
                    "use": "internal_research_test",
                },
            ],
            "contains_patient_responses": False,
            "response_storage": "none",
        }

    def demo_resource(self, resource_id: str) -> dict[str, Any]:
        """Read one repository resource from a strict allowlist."""
        path = DEMO_RESOURCE_PATHS.get(resource_id)
        if path is None:
            raise ServiceError(404, "demo_resource_not_found", "demo resource was not found")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ServiceError(
                500,
                "demo_resource_unavailable",
                "demo resource could not be loaded",
            ) from exc
        if not isinstance(payload, dict):
            raise ServiceError(
                500,
                "demo_resource_invalid",
                "demo resource must be a JSON object",
            )
        return deepcopy(payload)

    def anonymous_demo_configuration(self) -> dict[str, Any]:
        provider = self.llm_registry.providers[self.llm_registry.default_provider_id]
        if provider.external_processing:
            raise ServiceError(
                503,
                "anonymous_demo_provider_unavailable",
                "anonymous demo requires a local LLM provider",
            )
        return {
            "anonymous_demo": True,
            "authentication_required": False,
            "execution_mode": self.execution_mode,
            "response_storage": "memory_only",
            "session_ttl_seconds": self.anonymous_demo_ttl_seconds,
            "provider_policy": "platform_local_only",
            "providers": [
                provider.public_document(
                    is_default=True,
                )
            ],
            "terminology": self.terminology_client.configuration(),
            "real_personal_information_allowed": False,
            "synthetic_test_information_required": True,
        }

    def create_anonymous_demo_session(
        self, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        payload = payload or {}
        if not isinstance(payload, dict):
            raise ServiceError(400, "invalid_request", "request body must be an object")
        allowed = {"mode_selection", "initial_message"}
        unknown = sorted(set(payload) - allowed)
        if unknown:
            raise ServiceError(
                400,
                "invalid_request",
                "anonymous demo accepts only mode_selection and initial_message",
                details={"unsupported_fields": unknown},
            )
        provider_id = self.llm_registry.default_provider_id
        return self._create_session(
            {
                **payload,
                "llm_policy": {
                    "allowed_provider_ids": [provider_id],
                    "default_provider_id": provider_id,
                    "participant_may_choose": False,
                },
            },
            access_scope="anonymous_demo",
        )

    def send_anonymous_demo_message(
        self, session_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self.send_message(
            session_id, payload, required_access_scope="anonymous_demo"
        )

    def complete_anonymous_demo_session(self, session_id: str) -> dict[str, Any]:
        return self.complete(session_id, required_access_scope="anonymous_demo")

    def delete_anonymous_demo_session(self, session_id: str) -> dict[str, Any]:
        return self.delete_session(session_id, required_access_scope="anonymous_demo")

    def create_session(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._create_session(payload, access_scope="authenticated")

    def _create_session(
        self,
        payload: dict[str, Any] | None,
        *,
        access_scope: str,
    ) -> dict[str, Any]:
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
            if access_scope == "anonymous_demo" and sum(
                record.access_scope == "anonymous_demo"
                for record in self._sessions.values()
            ) >= self.max_anonymous_demo_sessions:
                raise ServiceError(
                    503,
                    "anonymous_demo_capacity_reached",
                    "temporary anonymous demo capacity has been reached",
                )
            session_id = str(uuid4())
            core = self._session_factory(session_id)
            if isinstance(core, CoreInteractionSession):
                core.clinical_interpreter = lambda message: (
                    self.clinical_interpreter.interpret(
                        message,
                        core.registry.reason_for_encounter_candidates(),
                        llm_selection,
                    )
                )
                core.chatbot_turn = lambda rfe_id, conversation: (
                    self.chatbot_runtime.respond(
                        rfe_id,
                        conversation,
                        llm_selection,
                        interaction_purpose="clinical_adaptive",
                    )
                )
                core.health_chatbot_turn = lambda rfe_id, conversation: (
                    self.chatbot_runtime.respond(
                        rfe_id,
                        conversation,
                        llm_selection,
                        interaction_purpose="health_information",
                    )
                )
                core.health_safety_assessor = (
                    lambda rfe_id, answer, question: (
                        self.chatbot_runtime.assess_health_information_answer(
                            rfe_id,
                            answer,
                            question,
                        )
                    )
                )
            try:
                state = core.start()
                if mode_selection is not None:
                    select_mode = getattr(core, "select_mode", None)
                    state = (
                        select_mode(mode_selection)
                        if callable(select_mode)
                        else core.process(mode_selection)
                    )
                if initial_message is not None:
                    state = core.process(initial_message)
                presentation = self._render_llm_output(core, state, llm_selection)
            except LlmChatbotRuntimeError as exc:
                core.close()
                raise ServiceError(
                    503,
                    "chatbot_runtime_unavailable",
                    "Chatbot test 방식의 문진 LLM을 현재 사용할 수 없습니다.",
                ) from exc
            except Exception:
                core.close()
                raise
            record = SessionRecord(
                core=core,
                created_at=now,
                touched_at=now,
                expires_at=now + (
                    self.anonymous_demo_ttl_seconds
                    if access_scope == "anonymous_demo"
                    else self.session_ttl_seconds
                ),
                last_state=deepcopy(state),
                llm_selection=llm_selection,
                llm_presentation=deepcopy(presentation),
                access_scope=access_scope,
            )
            self._sessions[session_id] = record
        return self._session_document(session_id, record)

    def get_session(self, session_id: str) -> dict[str, Any]:
        session_id, record = self._record(session_id)
        with record.lock:
            self._touch(record)
            return self._session_document(session_id, record)

    def send_message(
        self,
        session_id: str,
        payload: dict[str, Any],
        *,
        required_access_scope: str | None = None,
    ) -> dict[str, Any]:
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
        session_id, record = self._record(
            session_id, required_access_scope=required_access_scope
        )
        with record.lock:
            try:
                state = record.core.process(message)
            except LlmChatbotRuntimeError as exc:
                raise ServiceError(
                    503,
                    "chatbot_runtime_unavailable",
                    "Chatbot test 방식의 문진 LLM을 현재 사용할 수 없습니다.",
                ) from exc
            except RuntimeError as exc:
                raise ServiceError(409, "session_closed", "session is closed") from exc
            record.last_state = deepcopy(state)
            record.llm_presentation = self._render_llm_output(
                record.core, state, record.llm_selection
            )
            self._touch(record)
            return self._session_document(session_id, record)

    def result(self, session_id: str) -> dict[str, Any]:
        session_id, record = self._record(session_id)
        with record.lock:
            self._touch(record)
            return self._result_document(session_id, record)

    def complete(
        self, session_id: str, *, required_access_scope: str | None = None
    ) -> dict[str, Any]:
        session_id, record = self._record(
            session_id, required_access_scope=required_access_scope
        )
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

    def delete_session(
        self, session_id: str, *, required_access_scope: str | None = None
    ) -> dict[str, Any]:
        session_id = _validate_session_id(session_id)
        with self._lock:
            record = self._sessions.get(session_id)
            if record is not None and (
                required_access_scope is None
                or record.access_scope == required_access_scope
            ):
                self._sessions.pop(session_id, None)
            else:
                record = None
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

    def _record(
        self,
        session_id: str,
        *,
        required_access_scope: str | None = None,
    ) -> tuple[str, SessionRecord]:
        session_id = _validate_session_id(session_id)
        self.purge_expired()
        with self._lock:
            record = self._sessions.get(session_id)
        if record is None or (
            required_access_scope is not None
            and record.access_scope != required_access_scope
        ):
            raise ServiceError(404, "session_not_found", "session was not found or expired")
        return session_id, record

    def _touch(self, record: SessionRecord) -> None:
        now = self.clock()
        record.touched_at = now
        record.expires_at = now + (
            self.anonymous_demo_ttl_seconds
            if record.access_scope == "anonymous_demo"
            else self.session_ttl_seconds
        )

    def _session_document(self, session_id: str, record: SessionRecord) -> dict[str, Any]:
        return {
            "session_id": session_id,
            "status": "active",
            "mode_id": record.core.mode_id,
            "access_scope": record.access_scope,
            "created_at": _utc_iso(record.created_at),
            "expires_at": _utc_iso(record.expires_at),
            "retention": {
                "storage": "memory_only",
                "ttl_seconds": (
                    self.anonymous_demo_ttl_seconds
                    if record.access_scope == "anonymous_demo"
                    else self.session_ttl_seconds
                ),
                "delete_endpoint": (
                    f"/demo-api/sessions/{session_id}"
                    if record.access_scope == "anonymous_demo"
                    else f"/v1/sessions/{session_id}"
                ),
            },
            "llm": record.llm_selection.public_document(
                presentation_enabled=self.llm_presenter.enabled
            ),
            "presentation": deepcopy(record.llm_presentation),
            "state": deepcopy(record.last_state),
        }

    def _render_llm_output(
        self,
        core: CoreInteractionSession,
        state: dict[str, Any],
        selection: LlmSelection,
    ) -> dict[str, Any]:
        if core.mode_id == "health_information":
            adapter_state = state.get("adapter_state") if isinstance(state, dict) else None
            assistant_message = (
                adapter_state.get("assistant_message")
                if isinstance(adapter_state, dict)
                else None
            )
            if isinstance(assistant_message, str) and assistant_message.strip():
                return {
                    "status": "generated",
                    "purpose": "health_information_conversation_turn",
                    "provider_id": selection.provider.provider_id,
                    "model": selection.provider.model,
                    "text": assistant_message,
                    "patient_input_transmitted": True,
                    "processing_location": (
                        "external_vendor"
                        if selection.provider.external_processing
                        else "banttas_ai_local"
                    ),
                    "clinical_authority": False,
                }
            return self.health_information_advisor.answer(state, selection)
        adapter_state = state.get("adapter_state") if isinstance(state, dict) else None
        assistant_message = (
            adapter_state.get("assistant_message")
            if isinstance(adapter_state, dict)
            else None
        )
        if isinstance(assistant_message, str) and assistant_message.strip():
            return {
                "status": "generated",
                "purpose": "custom_gpt_conversation_turn",
                "provider_id": selection.provider.provider_id,
                "model": selection.provider.model,
                "text": assistant_message,
                "patient_input_transmitted": True,
                "processing_location": (
                    "external_vendor"
                    if selection.provider.external_processing
                    else "banttas_ai_local"
                ),
                "clinical_authority": False,
                "instructions": self.chatbot_runtime.instructions_source,
                "instruction_profile": self.chatbot_runtime.instruction_profile,
                "legacy_deterministic_fallback": False,
            }
        return {
            "status": "not_applicable",
            "purpose": "custom_gpt_conversation_turn",
            "provider_id": selection.provider.provider_id,
            "patient_input_transmitted": False,
        }

    def _result_document(self, session_id: str, record: SessionRecord) -> dict[str, Any]:
        if record.core.mode_id == "health_information" and record.core.adapter is not None:
            adapter_result = record.core.adapter.result()
            return {
                "session_id": session_id,
                "mode_id": "health_information",
                "lifecycle_status": "draft",
                "review_status": "unreviewed",
                "clinical_use_status": "limited",
                "independent_diagnosis_or_treatment": False,
                "llm": record.llm_selection.public_document(
                    presentation_enabled=self.health_information_advisor.enabled
                ),
                "available_formats": ["health_information_json"],
                "informational_answer": deepcopy(record.llm_presentation),
                "consultation": deepcopy(adapter_result),
                "response_storage": "memory_only",
            }
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
