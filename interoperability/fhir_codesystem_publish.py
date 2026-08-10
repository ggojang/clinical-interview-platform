"""Explicit authenticated publication of project CodeSystems to FHIR R4.

This module is Build-Time deployment infrastructure. Local terminology is
published separately from the read-only terminology adapter and Interview
Runtime. Existing canonical/version content is never overwritten.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from interoperability.fhir_valueset_publish import (
    WriteTransport,
    _urllib_write_transport,
)


ReadTransport = Callable[[str, int], tuple[int, dict[str, Any]]]


class FhirCodeSystemPublishError(RuntimeError):
    """Raised when a CodeSystem cannot be safely published or verified."""


def _urllib_read_transport(url: str, timeout: int) -> tuple[int, dict[str, Any]]:
    request = Request(
        url,
        method="GET",
        headers={"Accept": "application/fhir+json, application/json"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read())
    except HTTPError as exc:
        if exc.code == 404:
            return 404, {}
        try:
            outcome = json.loads(exc.read())
        except (json.JSONDecodeError, UnicodeDecodeError):
            outcome = {"resourceType": "OperationOutcome"}
        diagnostics = "; ".join(
            issue.get("diagnostics", "")
            for issue in outcome.get("issue", [])
            if issue.get("diagnostics")
        )
        raise FhirCodeSystemPublishError(
            f"FHIR read returned HTTP {exc.code}: {diagnostics}"
        ) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise FhirCodeSystemPublishError(f"FHIR read failed: {exc}") from exc


def _normalized_concepts(concepts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for concept in concepts:
        item = {
            key: deepcopy(value)
            for key, value in concept.items()
            if key != "concept"
        }
        if concept.get("concept"):
            item["concept"] = _normalized_concepts(concept["concept"])
        normalized.append(item)
    return sorted(normalized, key=lambda item: item.get("code", ""))


def codesystem_fingerprint(resource: dict[str, Any]) -> str:
    """Return a deterministic semantic-content fingerprint for a CodeSystem."""
    if resource.get("resourceType") != "CodeSystem":
        raise FhirCodeSystemPublishError("not a CodeSystem resource")
    normalized = {
        "url": resource.get("url"),
        "version": resource.get("version"),
        "caseSensitive": resource.get("caseSensitive"),
        "hierarchyMeaning": resource.get("hierarchyMeaning"),
        "compositional": resource.get("compositional"),
        "versionNeeded": resource.get("versionNeeded"),
        "content": resource.get("content"),
        "concept": _normalized_concepts(resource.get("concept", [])),
    }
    rendered = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()


def _flatten_codes(concepts: list[dict[str, Any]]) -> list[str]:
    codes = []
    for concept in concepts:
        if concept.get("code"):
            codes.append(concept["code"])
        codes.extend(_flatten_codes(concept.get("concept", [])))
    return codes


def validate_complete_codesystem(resource: dict[str, Any]) -> list[str]:
    """Validate the minimum complete local CodeSystem publication contract."""
    if resource.get("resourceType") != "CodeSystem":
        raise FhirCodeSystemPublishError("only CodeSystem resources are supported")
    if not resource.get("id") or not resource.get("url") or not resource.get("version"):
        raise FhirCodeSystemPublishError(
            "CodeSystem requires id, canonical url and version"
        )
    if resource.get("content") != "complete":
        raise FhirCodeSystemPublishError(
            "project local CodeSystem content must be complete"
        )
    codes = _flatten_codes(resource.get("concept", []))
    if len(codes) != len(set(codes)):
        raise FhirCodeSystemPublishError("CodeSystem contains duplicate codes")
    if resource.get("count") != len(codes):
        raise FhirCodeSystemPublishError("CodeSystem count does not match concepts")
    return codes


class FhirCodeSystemService:
    """Small read-only service used to reconcile and verify CodeSystems."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout_seconds: int = 30,
        transport: ReadTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._transport = transport or _urllib_read_transport

    def _get(self, path: str, parameters: dict[str, Any] | None = None) -> dict:
        query = {"_format": "json", **(parameters or {})}
        url = f"{self.base_url}/{path}?{urlencode(query)}"
        status, resource = self._transport(url, self.timeout_seconds)
        if status == 404:
            return {}
        if status != 200:
            raise FhirCodeSystemPublishError(
                f"FHIR read returned unexpected HTTP {status}"
            )
        return resource

    def search_by_canonical(
        self,
        canonical: str,
        *,
        version: str | None = None,
        count: int = 2,
    ) -> list[dict[str, Any]]:
        parameters: dict[str, Any] = {"url": canonical, "_count": count}
        if version:
            parameters["version"] = version
        bundle = self._get("CodeSystem", parameters)
        if bundle.get("resourceType") != "Bundle":
            raise FhirCodeSystemPublishError(
                "CodeSystem canonical search did not return a Bundle"
            )
        return [
            entry["resource"]
            for entry in bundle.get("entry", [])
            if entry.get("resource", {}).get("resourceType") == "CodeSystem"
        ]

    def read_by_id(self, identifier: str) -> dict[str, Any] | None:
        resource = self._get(f"CodeSystem/{quote(identifier, safe='')}")
        if not resource:
            return None
        if resource.get("resourceType") != "CodeSystem":
            raise FhirCodeSystemPublishError(
                f"CodeSystem/{identifier} returned a non-CodeSystem resource"
            )
        return resource

    def validate_code(self, canonical: str, code: str) -> dict[str, Any]:
        parameters = self._get(
            "CodeSystem/$validate-code",
            {"url": canonical, "code": code},
        )
        if parameters.get("resourceType") != "Parameters":
            raise FhirCodeSystemPublishError(
                "CodeSystem/$validate-code did not return Parameters"
            )
        values = {
            parameter.get("name"): next(
                (
                    value
                    for key, value in parameter.items()
                    if key.startswith("value")
                ),
                None,
            )
            for parameter in parameters.get("parameter", [])
        }
        return values


class FhirCodeSystemPublisher:
    """Create absent complete CodeSystems and verify canonical/code behavior."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_seconds: int = 30,
        read_service: FhirCodeSystemService | None = None,
        write_transport: WriteTransport | None = None,
    ) -> None:
        if not api_key:
            raise FhirCodeSystemPublishError("an API key is required")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.api_key = api_key
        self.read_service = read_service or FhirCodeSystemService(
            self.base_url,
            timeout_seconds=timeout_seconds,
        )
        self._write_transport = write_transport or _urllib_write_transport

    def plan(self, resource: dict[str, Any]) -> dict[str, Any]:
        codes = validate_complete_codesystem(resource)
        canonical = resource["url"]
        identifier = resource["id"]
        version = resource["version"]
        fingerprint = codesystem_fingerprint(resource)
        matches = self.read_service.search_by_canonical(
            canonical,
            version=version,
            count=2,
        )
        if len(matches) > 1:
            raise FhirCodeSystemPublishError(
                f"multiple server CodeSystems use canonical/version {canonical}|{version}"
            )
        if matches:
            current = matches[0]
            if codesystem_fingerprint(current) != fingerprint:
                raise FhirCodeSystemPublishError(
                    "refusing to overwrite canonical/version with different "
                    f"CodeSystem content: {canonical}|{version}"
                )
            return {
                "action": "reuse_exact_codesystem",
                "canonical": canonical,
                "version": version,
                "local_id": identifier,
                "server_id": current.get("id"),
                "server_version_id": current.get("meta", {}).get("versionId"),
                "concept_count": len(codes),
                "content_fingerprint": fingerprint,
                "resource": deepcopy(resource),
            }
        collision = self.read_service.read_by_id(identifier)
        if collision is not None:
            raise FhirCodeSystemPublishError(
                f"CodeSystem/{identifier} already uses canonical/version "
                f"{collision.get('url')}|{collision.get('version')}, not "
                f"{canonical}|{version}"
            )
        return {
            "action": "create",
            "canonical": canonical,
            "version": version,
            "local_id": identifier,
            "server_id": identifier,
            "server_version_id": None,
            "concept_count": len(codes),
            "content_fingerprint": fingerprint,
            "resource": deepcopy(resource),
        }

    @staticmethod
    def _sample_codes(codes: list[str]) -> list[str]:
        if not codes:
            return []
        return list(dict.fromkeys((codes[0], codes[len(codes) // 2], codes[-1])))

    def _verify(self, plan: dict[str, Any]) -> dict[str, Any]:
        matches = self.read_service.search_by_canonical(
            plan["canonical"],
            version=plan["version"],
            count=2,
        )
        if len(matches) != 1:
            raise FhirCodeSystemPublishError(
                f"canonical verification returned {len(matches)} matches for "
                f"{plan['canonical']}|{plan['version']}"
            )
        verified = matches[0]
        if codesystem_fingerprint(verified) != plan["content_fingerprint"]:
            raise FhirCodeSystemPublishError(
                f"content mismatch after publishing {plan['canonical']}"
            )
        codes = validate_complete_codesystem(plan["resource"])
        validation_results = []
        for code in self._sample_codes(codes):
            result = self.read_service.validate_code(plan["canonical"], code)
            if result.get("result") is not True:
                raise FhirCodeSystemPublishError(
                    f"CodeSystem/$validate-code rejected {plan['canonical']}#{code}"
                )
            validation_results.append({
                "code": code,
                "result": True,
                "display": result.get("display"),
            })
        return {
            "server_id": verified.get("id", plan["server_id"]),
            "server_version_id": verified.get("meta", {}).get("versionId"),
            "post_write_canonical_verified": True,
            "post_write_content_verified": True,
            "representative_code_validation": validation_results,
        }

    def apply(self, plan: dict[str, Any]) -> dict[str, Any]:
        action = plan["action"]
        status = None
        response: dict[str, Any] = {}
        if action == "create":
            status, response, _ = self._write_transport(
                "PUT",
                (
                    f"{self.base_url}/CodeSystem/"
                    f"{quote(plan['server_id'], safe='')}"
                ),
                plan["resource"],
                {"X-API-Key": self.api_key},
                self.timeout_seconds,
            )
            if status not in {200, 201}:
                raise FhirCodeSystemPublishError(
                    f"unexpected FHIR write response: HTTP {status}"
                )
            if response and response.get("resourceType") != "CodeSystem":
                raise FhirCodeSystemPublishError(
                    f"FHIR write returned {response.get('resourceType')}, not CodeSystem"
                )
        elif action != "reuse_exact_codesystem":
            raise FhirCodeSystemPublishError(f"unsupported action: {action}")
        verified = self._verify(plan)
        result = {
            key: value
            for key, value in plan.items()
            if key != "resource"
        }
        result.update(verified)
        if status is not None:
            result.update({
                "http_status": status,
                "response_body_present": bool(response),
            })
        return result
