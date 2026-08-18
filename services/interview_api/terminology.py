"""Small, fixed-upstream FHIR terminology client for the demo API.

Only ValueSet canonical URLs are accepted from callers.  All network requests
are sent to the administrator-configured terminology server, so this module
does not turn the API into a general-purpose URL fetcher.
"""
from __future__ import annotations

import json
import os
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen


class TerminologyError(Exception):
    """A client-safe terminology lookup failure."""

    def __init__(self, code: str, message: str, *, status: int = 502) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


class TerminologyClient:
    """Query a single administrator-controlled FHIR terminology endpoint."""

    def __init__(
        self,
        base_url: str | None,
        *,
        timeout_seconds: float = 5.0,
        max_expansion_count: int = 100,
    ) -> None:
        self.base_url = (base_url or "").strip().rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_expansion_count = max_expansion_count
        if self.base_url:
            parsed = urlsplit(self.base_url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("terminology base URL must be an http(s) URL")
        if timeout_seconds <= 0 or timeout_seconds > 30:
            raise ValueError("terminology timeout must be between 0 and 30 seconds")
        if max_expansion_count < 1 or max_expansion_count > 500:
            raise ValueError("terminology expansion limit must be between 1 and 500")

    @classmethod
    def from_env(cls) -> "TerminologyClient":
        return cls(
            os.getenv("CLINICAL_TERMINOLOGY_BASE_URL"),
            timeout_seconds=float(
                os.getenv("CLINICAL_TERMINOLOGY_TIMEOUT_SECONDS", "5")
            ),
        )

    @property
    def configured(self) -> bool:
        return bool(self.base_url)

    def configuration(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "base_url": self.base_url or None,
            "operations": ["ValueSet/$expand"] if self.configured else [],
            "patient_data_transmitted": False,
        }

    def status(self) -> dict[str, Any]:
        if not self.configured:
            return {**self.configuration(), "available": False}
        payload = self._get_json(f"{self.base_url}/metadata?_summary=true")
        if payload.get("resourceType") != "CapabilityStatement":
            raise TerminologyError(
                "terminology_invalid_response",
                "terminology server did not return a FHIR CapabilityStatement",
            )
        software = payload.get("software") if isinstance(payload.get("software"), dict) else {}
        return {
            **self.configuration(),
            "available": True,
            "fhir_version": payload.get("fhirVersion"),
            "software_name": software.get("name"),
        }

    def expand(
        self,
        canonical_url: str,
        *,
        filter_text: str | None = None,
        count: int = 50,
    ) -> dict[str, Any]:
        if not self.configured:
            raise TerminologyError(
                "terminology_not_configured",
                "terminology server is not configured",
                status=503,
            )
        canonical_url = self._validate_canonical(canonical_url)
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise TerminologyError(
                "invalid_terminology_request",
                "count must be a positive integer",
                status=400,
            )
        count = min(count, self.max_expansion_count)
        params: dict[str, Any] = {"url": canonical_url, "count": count}
        if filter_text is not None:
            if not isinstance(filter_text, str) or len(filter_text) > 200:
                raise TerminologyError(
                    "invalid_terminology_request",
                    "filter must be a string of at most 200 characters",
                    status=400,
                )
            if filter_text.strip():
                params["filter"] = filter_text.strip()
        payload = self._get_json(
            f"{self.base_url}/ValueSet/$expand?{urlencode(params)}",
            not_found_code="valueset_not_found",
        )
        if payload.get("resourceType") == "OperationOutcome":
            raise TerminologyError(
                "valueset_not_found",
                "ValueSet could not be expanded by the configured terminology server",
                status=404,
            )
        if payload.get("resourceType") != "ValueSet":
            raise TerminologyError(
                "terminology_invalid_response",
                "terminology server did not return a FHIR ValueSet",
            )
        expansion = payload.get("expansion")
        if not isinstance(expansion, dict):
            raise TerminologyError(
                "terminology_invalid_response",
                "expanded ValueSet did not contain an expansion",
            )
        concepts: list[dict[str, str]] = []
        self._flatten_contains(expansion.get("contains"), concepts, count)
        total = expansion.get("total")
        if not isinstance(total, int):
            total = len(concepts)
        return {
            "url": canonical_url,
            "total": total,
            "contains": concepts,
            "truncated": total > len(concepts),
        }

    @staticmethod
    def _validate_canonical(value: Any) -> str:
        if not isinstance(value, str):
            raise TerminologyError(
                "invalid_terminology_request",
                "url must be a ValueSet canonical URL",
                status=400,
            )
        normalized = value.strip()
        if not normalized or len(normalized) > 512:
            raise TerminologyError(
                "invalid_terminology_request",
                "url must be a ValueSet canonical URL of at most 512 characters",
                status=400,
            )
        canonical_base = normalized.split("|", 1)[0]
        parsed = urlsplit(canonical_base)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise TerminologyError(
                "invalid_terminology_request",
                "url must be an http(s) ValueSet canonical URL",
                status=400,
            )
        return normalized

    @classmethod
    def _flatten_contains(
        cls,
        values: Any,
        output: list[dict[str, str]],
        limit: int,
    ) -> None:
        if not isinstance(values, list):
            return
        for value in values:
            if len(output) >= limit:
                return
            if not isinstance(value, dict):
                continue
            system = value.get("system")
            code = value.get("code")
            if isinstance(system, str) and isinstance(code, str):
                concept = {"system": system, "code": code}
                if isinstance(value.get("display"), str):
                    concept["display"] = value["display"]
                output.append(concept)
            cls._flatten_contains(value.get("contains"), output, limit)

    def _get_json(
        self,
        url: str,
        *,
        not_found_code: str = "terminology_unavailable",
    ) -> dict[str, Any]:
        request = Request(
            url,
            headers={"Accept": "application/fhir+json, application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.load(response)
        except HTTPError as exc:
            if exc.code == 404:
                raise TerminologyError(
                    not_found_code,
                    "requested terminology resource was not found",
                    status=404,
                ) from exc
            raise TerminologyError(
                "terminology_unavailable",
                "terminology server request failed",
            ) from exc
        except (URLError, TimeoutError, socket.timeout, OSError, ValueError, json.JSONDecodeError) as exc:
            raise TerminologyError(
                "terminology_unavailable",
                "terminology server is temporarily unavailable",
            ) from exc
        if not isinstance(payload, dict):
            raise TerminologyError(
                "terminology_invalid_response",
                "terminology server response was not a JSON object",
            )
        return payload
