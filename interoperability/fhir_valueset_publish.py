"""Explicit authenticated publication of project ValueSets to FHIR R4.

This module is Build-Time deployment infrastructure. It is intentionally
separate from the read-only terminology adapter and Interview Runtime.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from interoperability.fhir_valueset_service import FhirValueSetService
from interoperability.fhir_valueset_reconcile import reconcile_reference


WriteTransport = Callable[
    [str, str, dict[str, Any], dict[str, str], int],
    tuple[int, dict[str, Any], dict[str, str]],
]


class FhirValueSetPublishError(RuntimeError):
    """Raised when a ValueSet cannot be safely published."""


def load_env_value(path: Path, key: str) -> str:
    """Read one dotenv value without placing it in logs or reports."""
    if not path.is_file():
        raise FhirValueSetPublishError(f"environment file not found: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() != key:
            continue
        value = value.strip()
        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            value = value[1:-1]
        if not value:
            break
        return value
    raise FhirValueSetPublishError(f"{key} is not configured in {path}")


def _urllib_write_transport(
    method: str,
    url: str,
    resource: dict[str, Any],
    headers: dict[str, str],
    timeout: int,
) -> tuple[int, dict[str, Any], dict[str, str]]:
    request = Request(
        url,
        data=json.dumps(resource, ensure_ascii=False).encode("utf-8"),
        method=method,
        headers={
            "Accept": "application/fhir+json, application/json",
            "Content-Type": "application/fhir+json",
            **headers,
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw_body = response.read()
            body = json.loads(raw_body) if raw_body.strip() else {}
            return response.status, body, dict(response.headers)
    except HTTPError as exc:
        try:
            outcome = json.loads(exc.read())
        except (json.JSONDecodeError, UnicodeDecodeError):
            outcome = {"resourceType": "OperationOutcome"}
        diagnostics = "; ".join(
            issue.get("diagnostics", "")
            for issue in outcome.get("issue", [])
            if issue.get("diagnostics")
        )
        raise FhirValueSetPublishError(
            f"FHIR write returned HTTP {exc.code}: {diagnostics}"
        ) from exc
    except (URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise FhirValueSetPublishError(f"FHIR write failed: {exc}") from exc


class FhirValueSetPublisher:
    """Idempotently publish ValueSets with an explicit administrator token."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        timeout_seconds: int = 30,
        read_service: FhirValueSetService | None = None,
        write_transport: WriteTransport | None = None,
    ) -> None:
        if not api_key:
            raise FhirValueSetPublishError("an API key is required")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.api_key = api_key
        self.read_service = read_service or FhirValueSetService(
            self.base_url,
            timeout_seconds=timeout_seconds,
        )
        self._write_transport = write_transport or _urllib_write_transport

    def _read_by_id(self, identifier: str) -> dict[str, Any] | None:
        url = (
            f"{self.base_url}/ValueSet/"
            f"{quote(identifier, safe='')}?_format=json"
        )
        request = Request(
            url,
            method="GET",
            headers={"Accept": "application/fhir+json, application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                resource = json.loads(response.read())
        except HTTPError as exc:
            if exc.code == 404:
                return None
            raise FhirValueSetPublishError(
                f"FHIR read-by-id returned HTTP {exc.code}"
            ) from exc
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise FhirValueSetPublishError(
                f"FHIR read-by-id failed: {exc}"
            ) from exc
        if resource.get("resourceType") != "ValueSet":
            raise FhirValueSetPublishError(
                f"ValueSet/{identifier} returned a non-ValueSet resource"
            )
        return resource

    def plan(
        self,
        resource: dict[str, Any],
        *,
        catalog: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if resource.get("resourceType") != "ValueSet":
            raise FhirValueSetPublishError("only ValueSet resources are supported")
        canonical = resource.get("url")
        identifier = resource.get("id")
        if not canonical or not identifier:
            raise FhirValueSetPublishError("ValueSet requires id and canonical url")
        matches = self.read_service.search_by_canonical(
            canonical,
            version=resource.get("version"),
            count=2,
        )
        if len(matches) > 1:
            raise FhirValueSetPublishError(
                f"multiple server ValueSets use canonical {canonical}"
            )
        if matches:
            current = matches[0]
            server_id = current.get("id")
            if not server_id:
                raise FhirValueSetPublishError(
                    f"server ValueSet has no id: {canonical}"
                )
            reconciliation = reconcile_reference(resource, matches)
            if reconciliation["action"] == "canonical_content_conflict":
                raise FhirValueSetPublishError(
                    "refusing to overwrite canonical/version with different "
                    f"membership: {canonical}|{resource.get('version')}"
                )
            return {
                "action": "reuse_exact_reference",
                "canonical": canonical,
                "local_id": identifier,
                "server_id": server_id,
                "server_version_id": current.get("meta", {}).get("versionId"),
                "membership_fingerprint": reconciliation[
                    "membership_fingerprint"
                ],
                "resource": deepcopy(resource),
            }
        if catalog is not None:
            reconciliation = reconcile_reference(resource, catalog)
            if reconciliation["action"] == "canonical_content_conflict":
                raise FhirValueSetPublishError(
                    "refusing to overwrite canonical/version with different "
                    f"membership: {canonical}|{resource.get('version')}"
                )
            if reconciliation["action"] == "reuse_exact_reference":
                return {
                    "action": "reuse_exact_reference",
                    "canonical": canonical,
                    "local_id": identifier,
                    "server_id": reconciliation.get("server_id"),
                    "membership_fingerprint": reconciliation[
                        "membership_fingerprint"
                    ],
                    "resource": deepcopy(resource),
                }
        collision = self._read_by_id(identifier)
        if collision is not None:
            raise FhirValueSetPublishError(
                f"ValueSet/{identifier} already uses canonical "
                f"{collision.get('url')!r}, not {canonical!r}"
            )
        return {
            "action": "create",
            "canonical": canonical,
            "local_id": identifier,
            "server_id": identifier,
            "server_version_id": None,
            **(
                {
                    "membership_fingerprint": reconciliation[
                        "membership_fingerprint"
                    ],
                    "content_equivalent_candidates": reconciliation.get(
                        "content_equivalent_candidates", []
                    ),
                }
                if catalog is not None
                else {}
            ),
            "resource": deepcopy(resource),
        }

    def apply(self, plan: dict[str, Any]) -> dict[str, Any]:
        action = plan["action"]
        if action in {
            "unchanged",
            "reuse_exact_reference",
        }:
            return {
                key: value
                for key, value in plan.items()
                if key != "resource"
            }
        if action != "create":
            raise FhirValueSetPublishError(f"unsupported action: {action}")
        server_id = plan["server_id"]
        headers = {"X-API-Key": self.api_key}
        status, response, _ = self._write_transport(
            "PUT",
            f"{self.base_url}/ValueSet/{quote(server_id, safe='')}",
            plan["resource"],
            headers,
            self.timeout_seconds,
        )
        if status not in {200, 201}:
            raise FhirValueSetPublishError(
                f"unexpected FHIR write response: HTTP {status} "
                f"{response.get('resourceType')}"
            )
        if response and response.get("resourceType") != "ValueSet":
            raise FhirValueSetPublishError(
                f"FHIR write returned {response.get('resourceType')}, not ValueSet"
            )
        version = plan["resource"].get("version")
        if version:
            matches = self.read_service.search_by_canonical(
                plan["canonical"],
                version=version,
                count=2,
            )
        else:
            matches = self.read_service.search_by_canonical(
                plan["canonical"],
                count=2,
            )
        if len(matches) != 1:
            raise FhirValueSetPublishError(
                f"canonical verification returned {len(matches)} matches "
                f"after writing ValueSet/{server_id}"
            )
        verified = matches[0]
        if verified.get("url") != plan["canonical"]:
            raise FhirValueSetPublishError(
                f"canonical mismatch after writing ValueSet/{server_id}"
            )
        return {
            "action": action,
            "canonical": plan["canonical"],
            "local_id": plan["local_id"],
            "server_id": verified.get("id", server_id),
            "server_version_id": verified.get("meta", {}).get("versionId"),
            "http_status": status,
            "response_body_present": bool(response),
            "post_write_canonical_verified": True,
        }
