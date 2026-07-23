from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from interoperability.fhir_valueset_publish import (
    FhirValueSetPublisher,
    load_env_value,
)
from interoperability.fhir_valueset_service import (
    DEFAULT_BASE_URL,
    FhirValueSetService,
    FhirValueSetServiceError,
)


CANONICAL = (
    "http://terminology.hl7.org/ValueSet/"
    "yes-no-unknown-not-applicable"
)
SYSTEM = "http://terminology.hl7.org/CodeSystem/v2-0532"


class FakeTransport:
    def __init__(self) -> None:
        self.urls: list[str] = []

    def __call__(self, url: str, timeout: int):
        self.urls.append(url)
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        if parsed.path.endswith("/metadata"):
            return 200, {
                "resourceType": "CapabilityStatement",
                "fhirVersion": "4.0.1",
                "software": {
                    "name": "STOM Terminology Server",
                    "version": "1.0.0",
                },
                "rest": [{
                    "resource": [{
                        "type": "ValueSet",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                        ],
                        "operation": [
                            {"name": "$expand"},
                            {"name": "$validate-code"},
                        ],
                    }]
                }],
            }
        if parsed.path.endswith("/ValueSet"):
            return 200, {
                "resourceType": "Bundle",
                "type": "searchset",
                "total": 1,
                "entry": [{
                    "resource": {
                        "resourceType": "ValueSet",
                        "id": "yes-no-unknown-not-applicable",
                        "url": query["url"][0],
                        "status": "active",
                    }
                }],
            }
        if parsed.path.endswith("/ValueSet/$expand"):
            return 200, {
                "resourceType": "ValueSet",
                "url": query["url"][0],
                "expansion": {
                    "contains": [
                        {"system": SYSTEM, "code": "Y", "display": "Yes"},
                        {"system": SYSTEM, "code": "N", "display": "No"},
                    ]
                },
            }
        if parsed.path.endswith("/ValueSet/$validate-code"):
            valid = query["code"][0] in {"Y", "N"}
            return 200, {
                "resourceType": "Parameters",
                "parameter": [
                    {"name": "result", "valueBoolean": valid},
                    {"name": "display", "valueString": "Yes" if valid else ""},
                ],
            }
        raise AssertionError(f"unexpected URL: {url}")


class FhirValueSetServiceTest(unittest.TestCase):
    def setUp(self):
        self.transport = FakeTransport()
        self.service = FhirValueSetService(
            DEFAULT_BASE_URL + "/",
            transport=self.transport,
        )

    def test_capability_search_expand_and_validate(self):
        capability = self.service.valueset_capabilities()
        self.assertEqual(capability["fhir_version"], "4.0.1")
        self.assertEqual(
            capability["software"]["name"],
            "STOM Terminology Server",
        )
        self.assertEqual(
            capability["operations"],
            ["$expand", "$validate-code"],
        )
        matches = self.service.search_by_canonical(CANONICAL)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["url"], CANONICAL)
        expansion = self.service.expand(CANONICAL, count=20)
        self.assertEqual(
            expansion["expansion"]["contains"][0]["code"],
            "Y",
        )
        self.assertTrue(
            self.service.validate_code(
                CANONICAL,
                system=SYSTEM,
                code="Y",
            )["result"]
        )
        self.assertFalse(
            self.service.validate_code(
                CANONICAL,
                system=SYSTEM,
                code="invalid",
            )["result"]
        )

    def test_all_requests_are_get_query_operations(self):
        self.service.search_by_canonical(CANONICAL)
        self.service.expand(CANONICAL)
        self.service.validate_code(CANONICAL, system=SYSTEM, code="Y")
        for url in self.transport.urls:
            self.assertIn("_format=json", url)
            self.assertNotIn("/_history", url)

    def test_validate_code_requires_boolean_result(self):
        def invalid_transport(url: str, timeout: int):
            return 200, {"resourceType": "Parameters", "parameter": []}

        service = FhirValueSetService(transport=invalid_transport)
        with self.assertRaises(FhirValueSetServiceError):
            service.validate_code(CANONICAL, system=SYSTEM, code="Y")

    def test_policy_keeps_local_endpoint_first_and_runtime_offline(self):
        root = Path(__file__).resolve().parents[1]
        policy = json.loads(
            (root / "policies/fhir-valueset-service.json").read_text()
        )
        self.assertEqual(
            policy["endpoint_order"][0]["base_url"],
            "http://localhost:8088/fhir",
        )
        self.assertTrue(
            policy["configuration"]["read_only_terminology_adapter"]
        )
        self.assertFalse(
            policy["safety_boundaries"]["runtime_terminology_lookup_required"]
        )

    def test_publication_accepts_empty_success_body_then_verifies_canonical(self):
        resource = {
            "resourceType": "ValueSet",
            "id": "a-local-test",
            "url": "https://example.org/fhir/ValueSet/a-local-test",
            "status": "draft",
            "compose": {
                "include": [{
                    "system": "https://example.org/fhir/CodeSystem/local",
                    "concept": [{"code": "one", "display": "One"}],
                }]
            },
        }

        class ReadService:
            def search_by_canonical(self, canonical, count=2):
                return [{**resource, "url": canonical}]

        captured = {}

        def writer(method, url, payload, headers, timeout):
            captured.update({
                "method": method,
                "url": url,
                "headers": headers,
            })
            return 201, {}, {}

        publisher = FhirValueSetPublisher(
            base_url=DEFAULT_BASE_URL,
            api_key="not-recorded",
            read_service=ReadService(),
            write_transport=writer,
        )
        result = publisher.apply({
            "action": "create",
            "canonical": resource["url"],
            "local_id": resource["id"],
            "server_id": resource["id"],
            "server_version_id": None,
            "resource": resource,
        })
        self.assertEqual(captured["method"], "PUT")
        self.assertIn("X-API-Key", captured["headers"])
        self.assertFalse(result["response_body_present"])
        self.assertTrue(result["post_write_canonical_verified"])
        self.assertNotIn("not-recorded", json.dumps(result))

    def test_dotenv_token_is_loaded_without_logging_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.local"
            path.write_text(
                "OTHER=value\nTERM_ADMIN_TOKEN='secret-value'\n",
                encoding="utf-8",
            )
            self.assertEqual(
                load_env_value(path, "TERM_ADMIN_TOKEN"),
                "secret-value",
            )
