"""Read-only Build-Time FHIR ValueSet terminology service adapter.

The adapter is deliberately outside Interview Runtime. It discovers and
verifies terminology artifacts, but it never selects questions, changes safety
behavior, or writes resources to a terminology server.
"""
from __future__ import annotations

import json
import os
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "http://localhost:8088/fhir"
REMOTE_STOM_BASE_URL = "https://stom.infoclinic.co/fhir"
DEFAULT_TIMEOUT_SECONDS = 20


class FhirValueSetServiceError(RuntimeError):
    """Raised when a terminology response is unavailable or not valid FHIR."""


Transport = Callable[[str, int], tuple[int, dict[str, Any]]]


def _urllib_transport(url: str, timeout: int) -> tuple[int, dict[str, Any]]:
    request = Request(
        url,
        method="GET",
        headers={"Accept": "application/fhir+json, application/json"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
            return response.status, payload
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise FhirValueSetServiceError(f"FHIR request failed: {exc}") from exc


class FhirValueSetService:
    """Small, GET-only client for FHIR R4 ValueSet discovery and QA."""

    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        transport: Transport | None = None,
    ) -> None:
        configured = (
            base_url
            or os.getenv("CLINICAL_INTERVIEW_FHIR_TERMINOLOGY_BASE_URL")
            or DEFAULT_BASE_URL
        )
        self.base_url = configured.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._transport = transport or _urllib_transport

    def _get(
        self,
        path: str,
        params: dict[str, str] | None = None,
        *,
        expected: set[str],
    ) -> dict[str, Any]:
        query = {"_format": "json"}
        query.update(params or {})
        url = f"{self.base_url}/{path.lstrip('/')}?{urlencode(query)}"
        status, resource = self._transport(url, self.timeout_seconds)
        if status < 200 or status >= 300:
            raise FhirValueSetServiceError(f"FHIR server returned HTTP {status}")
        resource_type = resource.get("resourceType")
        if resource_type == "OperationOutcome":
            diagnostics = [
                issue.get("diagnostics", "")
                for issue in resource.get("issue", [])
            ]
            raise FhirValueSetServiceError(
                "FHIR OperationOutcome: " + "; ".join(filter(None, diagnostics))
            )
        if resource_type not in expected:
            raise FhirValueSetServiceError(
                f"expected {sorted(expected)}, received {resource_type!r}"
            )
        return resource

    def capability_statement(self) -> dict[str, Any]:
        return self._get("metadata", expected={"CapabilityStatement"})

    def valueset_capabilities(self) -> dict[str, Any]:
        statement = self.capability_statement()
        interactions: set[str] = set()
        operations: set[str] = set()
        for rest in statement.get("rest", []):
            for resource in rest.get("resource", []):
                if resource.get("type") != "ValueSet":
                    continue
                interactions.update(
                    item.get("code")
                    for item in resource.get("interaction", [])
                    if item.get("code")
                )
                operations.update(
                    item.get("name")
                    for item in resource.get("operation", [])
                    if item.get("name")
                )
        return {
            "fhir_version": statement.get("fhirVersion"),
            "software": statement.get("software", {}),
            "interactions": sorted(interactions),
            "operations": sorted(operations),
        }

    def search_by_canonical(
        self,
        canonical_url: str,
        *,
        version: str | None = None,
        count: int = 20,
    ) -> list[dict[str, Any]]:
        params = {"url": canonical_url, "_count": str(count)}
        if version:
            params["version"] = version
        bundle = self._get("ValueSet", params, expected={"Bundle"})
        return [
            entry["resource"]
            for entry in bundle.get("entry", [])
            if entry.get("resource", {}).get("resourceType") == "ValueSet"
            and entry["resource"].get("url") == canonical_url
            and (version is None or entry["resource"].get("version") == version)
        ]

    def expand(
        self,
        canonical_url: str,
        *,
        version: str | None = None,
        filter_text: str | None = None,
        count: int | None = None,
    ) -> dict[str, Any]:
        params = {"url": canonical_url}
        if version:
            params["valueSetVersion"] = version
        if filter_text:
            params["filter"] = filter_text
        if count is not None:
            params["count"] = str(count)
        return self._get(
            "ValueSet/$expand",
            params,
            expected={"ValueSet"},
        )

    def validate_code(
        self,
        canonical_url: str,
        *,
        system: str,
        code: str,
        version: str | None = None,
        display: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "url": canonical_url,
            "system": system,
            "code": code,
        }
        if version:
            params["valueSetVersion"] = version
        if display:
            params["display"] = display
        response = self._get(
            "ValueSet/$validate-code",
            params,
            expected={"Parameters"},
        )
        result: dict[str, Any] = {"resource": response}
        for parameter in response.get("parameter", []):
            name = parameter.get("name")
            if not name:
                continue
            value_key = next(
                (key for key in parameter if key.startswith("value")),
                None,
            )
            if value_key:
                result[name] = parameter[value_key]
        if not isinstance(result.get("result"), bool):
            raise FhirValueSetServiceError(
                "ValueSet $validate-code did not return a boolean result"
            )
        return result
