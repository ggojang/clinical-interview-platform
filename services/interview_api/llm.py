"""Governed LLM selection and question-presentation adapter.

The compiled runtime remains authoritative for clinical routing, safety,
question selection, and completion.  This module may only render an already
selected question into patient-friendly language.  It never receives patient
answers, files, Facts, traces, or clinician handoff content.
"""
from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from dataclasses import dataclass
import json
import os
import re
import threading
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


DEFAULT_LOCAL_PROVIDER_ID = "local_vllm"
PROVIDER_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
MAX_PROVIDER_CONFIG_BYTES = 32_768
MAX_PRESENTATION_CHARACTERS = 1_000
MAX_PRESENTATION_CACHE_ENTRIES = 2_048


class LlmConfigurationError(ValueError):
    """Raised for unsafe or malformed server-side provider configuration."""


class LlmSelectionError(ValueError):
    """A client-safe provider policy or selection error."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class LlmProvider:
    provider_id: str
    display_name: str
    adapter: str
    base_url: str
    model: str
    external_processing: bool
    enabled: bool = True
    api_key_env: str | None = None

    @property
    def configured(self) -> bool:
        if not self.enabled:
            return False
        if self.api_key_env is None:
            return True
        return bool((os.getenv(self.api_key_env) or "").strip())

    def public_document(self, *, is_default: bool) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "display_name": self.display_name,
            "model": self.model,
            "processing_location": (
                "external_vendor" if self.external_processing else "banttas_ai_local"
            ),
            "external_processing": self.external_processing,
            "configured": self.configured,
            "selectable": self.configured,
            "default": is_default,
        }


@dataclass(frozen=True)
class LlmSelection:
    provider: LlmProvider
    selected_by: str
    external_processing_consent: bool
    allowed_provider_ids: tuple[str, ...]
    participant_may_choose: bool

    def public_document(self, *, presentation_enabled: bool) -> dict[str, Any]:
        return {
            "provider_id": self.provider.provider_id,
            "display_name": self.provider.display_name,
            "model": self.provider.model,
            "selected_by": self.selected_by,
            "processing_location": (
                "external_vendor"
                if self.provider.external_processing
                else "banttas_ai_local"
            ),
            "external_processing": self.provider.external_processing,
            "external_processing_consent": self.external_processing_consent,
            "allowed_provider_ids": list(self.allowed_provider_ids),
            "participant_may_choose": self.participant_may_choose,
            "runtime_role": "question_presentation_only",
            "presentation_enabled": presentation_enabled,
            "clinical_authority": False,
        }


class LlmProviderRegistry:
    """Server-side allowlist for local and optional commercial providers."""

    def __init__(
        self,
        providers: list[LlmProvider],
        *,
        default_provider_id: str = DEFAULT_LOCAL_PROVIDER_ID,
    ) -> None:
        providers = [_validate_provider(provider) for provider in providers]
        provider_map = {provider.provider_id: provider for provider in providers}
        if len(provider_map) != len(providers):
            raise LlmConfigurationError("LLM provider ids must be unique")
        if default_provider_id not in provider_map:
            raise LlmConfigurationError("default LLM provider is not configured")
        if not provider_map[default_provider_id].configured:
            raise LlmConfigurationError("default LLM provider is not selectable")
        self.providers = provider_map
        self.default_provider_id = default_provider_id

    @classmethod
    def from_env(cls) -> "LlmProviderRegistry":
        local = LlmProvider(
            provider_id=DEFAULT_LOCAL_PROVIDER_ID,
            display_name=os.getenv("CLINICAL_LLM_LOCAL_DISPLAY_NAME", "Banttas AI local LLM"),
            adapter="openai_compatible_chat",
            base_url=os.getenv(
                "CLINICAL_LLM_LOCAL_BASE_URL", "http://127.0.0.1:8000/v1"
            ),
            model=os.getenv("CLINICAL_LLM_LOCAL_MODEL", "qwen3-27b"),
            external_processing=False,
            enabled=_env_bool("CLINICAL_LLM_LOCAL_ENABLED", True),
            api_key_env=(
                "CLINICAL_LLM_LOCAL_API_KEY"
                if os.getenv("CLINICAL_LLM_LOCAL_API_KEY")
                else None
            ),
        )
        providers = [_validate_provider(local)]
        raw = os.getenv("CLINICAL_LLM_PROVIDERS_JSON", "[]")
        if len(raw.encode("utf-8")) > MAX_PROVIDER_CONFIG_BYTES:
            raise LlmConfigurationError("CLINICAL_LLM_PROVIDERS_JSON is too large")
        try:
            documents = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LlmConfigurationError(
                "CLINICAL_LLM_PROVIDERS_JSON must be valid JSON"
            ) from exc
        if not isinstance(documents, list):
            raise LlmConfigurationError("CLINICAL_LLM_PROVIDERS_JSON must be an array")
        for document in documents:
            providers.append(_provider_from_document(document))
        default_id = os.getenv(
            "CLINICAL_LLM_DEFAULT_PROVIDER", DEFAULT_LOCAL_PROVIDER_ID
        ).strip()
        return cls(providers, default_provider_id=default_id)

    def catalog(self, *, presentation_enabled: bool) -> dict[str, Any]:
        return {
            "default_provider_id": self.default_provider_id,
            "selection_scope": "server_configured_allowlist",
            "participant_selection_supported": True,
            "requester_policy_supported": True,
            "credentials_in_request_body": "prohibited",
            "external_processing_requires_explicit_consent": True,
            "runtime_role": "question_presentation_only",
            "presentation_enabled": presentation_enabled,
            "clinical_routing_and_safety": "compiled_runtime_only",
            "providers": [
                provider.public_document(
                    is_default=provider.provider_id == self.default_provider_id
                )
                for provider in self.providers.values()
            ],
        }

    def select(
        self,
        policy: dict[str, Any] | None,
        selection: dict[str, Any] | None,
    ) -> LlmSelection:
        policy = deepcopy(policy or {})
        selection = deepcopy(selection or {})
        if not isinstance(policy, dict) or not isinstance(selection, dict):
            raise LlmSelectionError(
                "invalid_llm_selection", "llm_policy and llm_selection must be objects"
            )
        _reject_unknown(
            policy,
            {"allowed_provider_ids", "default_provider_id", "participant_may_choose"},
            "llm_policy",
        )
        _reject_unknown(
            selection,
            {"provider_id", "selected_by", "external_processing_consent"},
            "llm_selection",
        )

        raw_allowed = policy.get("allowed_provider_ids")
        if raw_allowed is None:
            allowed = tuple(
                provider_id
                for provider_id, provider in self.providers.items()
                if provider.configured
            )
        elif (
            not isinstance(raw_allowed, list)
            or not raw_allowed
            or not all(isinstance(item, str) and item for item in raw_allowed)
        ):
            raise LlmSelectionError(
                "invalid_llm_policy",
                "llm_policy.allowed_provider_ids must be a non-empty string array",
            )
        else:
            allowed = tuple(dict.fromkeys(raw_allowed))

        for provider_id in allowed:
            provider = self.providers.get(provider_id)
            if provider is None:
                raise LlmSelectionError(
                    "llm_provider_not_allowed",
                    f"LLM provider '{provider_id}' is not in the server allowlist",
                )
            if not provider.configured:
                raise LlmSelectionError(
                    "llm_provider_unavailable",
                    f"LLM provider '{provider_id}' is not configured on the server",
                )

        participant_may_choose = policy.get("participant_may_choose", True)
        if not isinstance(participant_may_choose, bool):
            raise LlmSelectionError(
                "invalid_llm_policy",
                "llm_policy.participant_may_choose must be a boolean",
            )
        default_id = policy.get("default_provider_id", self.default_provider_id)
        if not isinstance(default_id, str) or default_id not in allowed:
            raise LlmSelectionError(
                "invalid_llm_policy",
                "llm_policy.default_provider_id must be in allowed_provider_ids",
            )

        provider_id = selection.get("provider_id", default_id)
        selected_by = selection.get(
            "selected_by",
            "requester" if selection or policy else "platform_default",
        )
        if selected_by not in {"platform_default", "requester", "participant"}:
            raise LlmSelectionError(
                "invalid_llm_selection",
                "llm_selection.selected_by must be platform_default, requester, or participant",
            )
        if selected_by == "participant" and not participant_may_choose:
            raise LlmSelectionError(
                "participant_llm_selection_disabled",
                "the requester policy does not permit participant LLM selection",
            )
        if provider_id not in allowed:
            raise LlmSelectionError(
                "llm_provider_not_allowed",
                "the selected LLM provider is outside the requester allowlist",
            )
        provider = self.providers[provider_id]
        consent = selection.get("external_processing_consent", False)
        if not isinstance(consent, bool):
            raise LlmSelectionError(
                "invalid_llm_selection",
                "external_processing_consent must be a boolean",
            )
        if provider.external_processing and not consent:
            raise LlmSelectionError(
                "external_processing_consent_required",
                "explicit consent is required before selecting an external LLM provider",
            )
        return LlmSelection(
            provider=provider,
            selected_by=selected_by,
            external_processing_consent=consent,
            allowed_provider_ids=allowed,
            participant_may_choose=participant_may_choose,
        )


CompletionTransport = Callable[[LlmProvider, list[dict[str, str]], float], str]


class LlmQuestionPresenter:
    """Render one compiled question, with deterministic fallback on any failure."""

    def __init__(
        self,
        *,
        enabled: bool = False,
        timeout_seconds: float = 12.0,
        transport: CompletionTransport | None = None,
    ) -> None:
        self.enabled = enabled
        self.timeout_seconds = timeout_seconds
        self._transport = transport or _openai_compatible_completion
        self._cache: OrderedDict[tuple[str, str, str], str] = OrderedDict()
        self._lock = threading.RLock()

    @classmethod
    def from_env(cls) -> "LlmQuestionPresenter":
        return cls(
            enabled=_env_bool("CLINICAL_LLM_PRESENTATION_ENABLED", False),
            timeout_seconds=float(os.getenv("CLINICAL_LLM_TIMEOUT_SECONDS", "12")),
        )

    def present(
        self, state: dict[str, Any], selection: LlmSelection
    ) -> dict[str, Any]:
        question = _selected_question_text(state)
        if question is None:
            return {
                "status": "not_applicable",
                "purpose": "question_presentation_only",
                "provider_id": selection.provider.provider_id,
                "patient_response_transmitted": False,
            }
        if not self.enabled:
            return _fallback_presentation(
                question, selection, "llm_presentation_disabled"
            )
        cache_key = (
            selection.provider.provider_id,
            selection.provider.model,
            question,
        )
        with self._lock:
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._cache.move_to_end(cache_key)
                return _generated_presentation(cached, selection, cached=True)
        messages = [
            {
                "role": "system",
                "content": (
                    "Translate or rephrase exactly one already-approved clinical interview "
                    "question into clear, respectful Korean for a patient. Preserve the "
                    "clinical meaning and answer scope. Do not add diagnosis, treatment, "
                    "urgency, explanation, or another question. Output only the question."
                ),
            },
            {"role": "user", "content": question},
        ]
        try:
            raw_rendered = self._transport(
                selection.provider, messages, self.timeout_seconds
            )
            if not isinstance(raw_rendered, str):
                raise ValueError("invalid LLM presentation type")
            rendered = raw_rendered.strip()
            if not rendered or len(rendered) > MAX_PRESENTATION_CHARACTERS:
                raise ValueError("invalid LLM presentation length")
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError):
            return _fallback_presentation(question, selection, "provider_unavailable")
        with self._lock:
            self._cache[cache_key] = rendered
            self._cache.move_to_end(cache_key)
            while len(self._cache) > MAX_PRESENTATION_CACHE_ENTRIES:
                self._cache.popitem(last=False)
        return _generated_presentation(rendered, selection, cached=False)


def _provider_from_document(document: Any) -> LlmProvider:
    if not isinstance(document, dict):
        raise LlmConfigurationError("each LLM provider configuration must be an object")
    allowed = {
        "provider_id",
        "display_name",
        "adapter",
        "base_url",
        "model",
        "external_processing",
        "enabled",
        "api_key_env",
    }
    unknown = sorted(set(document) - allowed)
    if unknown:
        raise LlmConfigurationError(f"unsupported LLM provider fields: {unknown}")
    required = {
        "provider_id",
        "display_name",
        "base_url",
        "model",
        "external_processing",
    }
    missing = sorted(required - set(document))
    if missing:
        raise LlmConfigurationError(f"missing LLM provider fields: {missing}")
    provider = LlmProvider(
        provider_id=document["provider_id"],
        display_name=document["display_name"],
        adapter=document.get("adapter", "openai_compatible_chat"),
        base_url=document["base_url"],
        model=document["model"],
        external_processing=document["external_processing"],
        enabled=document.get("enabled", True),
        api_key_env=document.get("api_key_env"),
    )
    return _validate_provider(provider)


def _validate_provider(provider: LlmProvider) -> LlmProvider:
    if not PROVIDER_ID_RE.fullmatch(provider.provider_id):
        raise LlmConfigurationError(f"invalid LLM provider id: {provider.provider_id}")
    if not provider.display_name.strip() or not provider.model.strip():
        raise LlmConfigurationError("LLM provider display_name and model are required")
    if provider.adapter != "openai_compatible_chat":
        raise LlmConfigurationError("only openai_compatible_chat is currently supported")
    if not isinstance(provider.external_processing, bool) or not isinstance(
        provider.enabled, bool
    ):
        raise LlmConfigurationError("LLM provider boolean fields are invalid")
    parsed = urlsplit(provider.base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise LlmConfigurationError("LLM provider base_url must be HTTP(S)")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise LlmConfigurationError("LLM provider base_url must not contain credentials or query")
    if provider.external_processing and parsed.scheme != "https":
        raise LlmConfigurationError("external LLM providers must use HTTPS")
    if provider.external_processing and not provider.api_key_env:
        raise LlmConfigurationError(
            "external LLM providers must reference a server-side API key environment variable"
        )
    if provider.api_key_env is not None and not re.fullmatch(
        r"[A-Z][A-Z0-9_]{2,127}", provider.api_key_env
    ):
        raise LlmConfigurationError("LLM provider api_key_env is invalid")
    return provider


def _openai_compatible_completion(
    provider: LlmProvider,
    messages: list[dict[str, str]],
    timeout_seconds: float,
) -> str:
    payload = json.dumps(
        {
            "model": provider.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 180,
            "stream": False,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if provider.api_key_env:
        api_key = (os.getenv(provider.api_key_env) or "").strip()
        if not api_key:
            raise ValueError("provider credential is unavailable")
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(
        f"{provider.base_url.rstrip('/')}/chat/completions",
        data=payload,
        headers=headers,
        method="POST",
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        if response.status != 200:
            raise ValueError("LLM provider returned a non-success response")
        raw = response.read(262_145)
    if len(raw) > 262_144:
        raise ValueError("LLM provider response is too large")
    document = json.loads(raw.decode("utf-8"))
    return document["choices"][0]["message"]["content"]


def _selected_question_text(state: dict[str, Any]) -> str | None:
    candidate = state
    if isinstance(state.get("adapter_state"), dict):
        candidate = state["adapter_state"]
    question = candidate.get("selected_question")
    if not isinstance(question, dict):
        return None
    text = question.get("text")
    return text.strip() if isinstance(text, str) and text.strip() else None


def _generated_presentation(
    text: str, selection: LlmSelection, *, cached: bool
) -> dict[str, Any]:
    return {
        "status": "generated",
        "purpose": "question_presentation_only",
        "provider_id": selection.provider.provider_id,
        "model": selection.provider.model,
        "text": text,
        "cached": cached,
        "patient_response_transmitted": False,
        "clinical_authority": False,
    }


def _fallback_presentation(
    text: str, selection: LlmSelection, reason: str
) -> dict[str, Any]:
    return {
        "status": "deterministic_fallback",
        "purpose": "question_presentation_only",
        "provider_id": selection.provider.provider_id,
        "model": selection.provider.model,
        "text": text,
        "reason": reason,
        "patient_response_transmitted": False,
        "clinical_authority": False,
    }


def _reject_unknown(document: dict[str, Any], allowed: set[str], name: str) -> None:
    unknown = sorted(set(document) - allowed)
    if unknown:
        raise LlmSelectionError(
            "invalid_llm_selection",
            f"{name} contains unsupported fields: {', '.join(unknown)}",
        )


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    normalized = raw.strip().casefold()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise LlmConfigurationError(f"{name} must be a boolean")
