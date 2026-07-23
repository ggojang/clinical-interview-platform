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
    LOINC_ANSWER_LIST_AGGREGATE_URL,
)
from interoperability.loinc_answer_list_catalog import (
    LoincAnswerListCatalogError,
    answer_list_canonical,
    validate_catalog,
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
            if query["url"][0] == LOINC_ANSWER_LIST_AGGREGATE_URL:
                return 200, {
                    "resourceType": "ValueSet",
                    "url": query["url"][0],
                    "expansion": {
                        "total": 2,
                        "contains": [
                            {
                                "system": "http://loinc.org",
                                "code": "LL1-9",
                                "display": "Yes/no",
                            },
                            {
                                "system": "http://loinc.org",
                                "code": "LL2201-3",
                                "display": "Smoking status",
                            },
                        ],
                    },
                }
            if query["url"][0].startswith("http://loinc.org/vs/LL"):
                return 200, {
                    "resourceType": "ValueSet",
                    "url": query["url"][0],
                    "expansion": {
                        "total": 2,
                        "contains": [
                            {
                                "system": "http://loinc.org",
                                "code": "LA32-8",
                                "display": "No",
                            },
                            {
                                "system": "http://loinc.org",
                                "code": "LA33-6",
                                "display": "Yes",
                            },
                        ],
                    },
                }
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
        if parsed.path.endswith("/CodeSystem/$lookup"):
            return 200, {
                "resourceType": "Parameters",
                "parameter": [
                    {"name": "name", "valueString": "LOINC"},
                    {"name": "version", "valueString": "2.82"},
                    {
                        "name": "display",
                        "valueString": "Current smoking status answer list",
                    },
                ],
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
        if parsed.path.endswith("/CodeSystem/$validate-code"):
            valid = query["code"][0] == "261665006"
            return 200, {
                "resourceType": "Parameters",
                "parameter": [
                    {"name": "result", "valueBoolean": valid},
                    {
                        "name": "display",
                        "valueString": "Unknown (qualifier value)",
                    },
                    {"name": "system", "valueUri": query["url"][0]},
                    {"name": "code", "valueCode": query["code"][0]},
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

    def test_out_of_reference_standard_code_uses_codesystem_validation(self):
        result = self.service.validate_codesystem_code(
            "http://snomed.info/sct",
            code="261665006",
        )
        self.assertTrue(result["result"])
        self.assertEqual(result["display"], "Unknown (qualifier value)")

    def test_complete_loinc_answer_list_discovery_and_resolution(self):
        members = self.service.list_loinc_answer_lists()
        self.assertEqual([item["code"] for item in members], [
            "LL1-9",
            "LL2201-3",
        ])
        expansion = self.service.expand_loinc_answer_list(
            "LL2201-3",
            count=0,
        )
        self.assertEqual(expansion["expansion"]["total"], 2)
        metadata = self.service.lookup_codesystem_code(
            "http://loinc.org",
            code="LL2201-3",
        )
        self.assertEqual(metadata["version"], "2.82")

    def test_invalid_loinc_answer_list_identifier_is_rejected(self):
        with self.assertRaises(ValueError):
            self.service.expand_loinc_answer_list("not-an-LL-code")

    def test_loinc_answer_list_catalog_validation(self):
        entries = [
            {
                "code": "LL1-9",
                "canonical": answer_list_canonical("LL1-9"),
                "display": "Yes/no",
                "member_count": 2,
                "resolution": "stom_dynamic_expand",
            },
            {
                "code": "LL2201-3",
                "canonical": answer_list_canonical("LL2201-3"),
                "display": "Smoking status",
                "member_count": 8,
                "resolution": "stom_dynamic_expand",
            },
        ]
        catalog = {
            "id": "catalog.loinc-answer-lists",
            "status": "research_only",
            "review_status": "unreviewed",
            "aggregate_canonical": LOINC_ANSWER_LIST_AGGREGATE_URL,
            "total": 2,
            "membership_total": 10,
            "entries": entries,
        }
        self.assertEqual(
            validate_catalog(catalog),
            {"answer_list_count": 2, "membership_total": 10},
        )
        catalog["entries"].append(dict(entries[0]))
        catalog["total"] = 3
        catalog["membership_total"] = 12
        with self.assertRaises(LoincAnswerListCatalogError):
            validate_catalog(catalog)

    def test_repository_contains_complete_loinc_answer_list_catalog(self):
        root = Path(__file__).resolve().parents[1]
        catalog = json.loads(
            (
                root
                / "sources"
                / "catalogs"
                / "loinc-answer-lists-stom.json"
            ).read_text(encoding="utf-8")
        )
        result = validate_catalog(catalog)
        self.assertEqual(result["answer_list_count"], 4955)
        self.assertEqual(result["membership_total"], 33944)
        self.assertEqual(catalog["server_resources_created"], 0)
        self.assertFalse(catalog["runtime_dependency"])
        self.assertEqual(catalog["version_alignment"], "metadata_mismatch")

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

    def test_publication_verifies_the_created_version(self):
        resource = {
            "resourceType": "ValueSet",
            "id": "versioned-reference",
            "url": "https://example.org/fhir/ValueSet/versioned-reference",
            "version": "2.0.0",
            "status": "active",
            "compose": {
                "include": [{
                    "system": "http://snomed.info/sct",
                    "concept": [{"code": "373066001"}],
                }]
            },
        }
        observed = {}

        class ReadService:
            def search_by_canonical(
                self, canonical, version=None, count=2
            ):
                observed["version"] = version
                return [{**resource, "url": canonical}]

        publisher = FhirValueSetPublisher(
            base_url=DEFAULT_BASE_URL,
            api_key="not-recorded",
            read_service=ReadService(),
            write_transport=lambda *args: (201, {}, {}),
        )
        publisher.apply({
            "action": "create",
            "canonical": resource["url"],
            "local_id": resource["id"],
            "server_id": resource["id"],
            "server_version_id": None,
            "resource": resource,
        })
        self.assertEqual(observed["version"], "2.0.0")

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
