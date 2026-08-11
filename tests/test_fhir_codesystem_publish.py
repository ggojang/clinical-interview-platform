from __future__ import annotations

from copy import deepcopy
import unittest

from interoperability.fhir_codesystem_publish import (
    FhirCodeSystemPublishError,
    FhirCodeSystemService,
    FhirCodeSystemPublisher,
    codesystem_fingerprint,
    validate_complete_codesystem,
)


def local_codesystem() -> dict:
    return {
        "resourceType": "CodeSystem",
        "id": "local-answer",
        "url": "https://example.org/fhir/CodeSystem/local-answer",
        "version": "0.1.0",
        "status": "draft",
        "experimental": True,
        "caseSensitive": True,
        "content": "complete",
        "count": 2,
        "concept": [
            {"code": "answer--yes", "display": "yes"},
            {"code": "answer--no", "display": "no"},
        ],
    }


class FakeReadService:
    def __init__(self, matches=None, collision=None) -> None:
        self.matches = matches or []
        self.collision = collision
        self.validated = []

    def search_by_canonical(self, canonical, *, version=None, count=2):
        return deepcopy(self.matches)

    def read_by_id(self, identifier):
        return deepcopy(self.collision)

    def validate_code(self, canonical, code):
        self.validated.append((canonical, code))
        return {"result": True, "display": code}


class FhirCodeSystemPublisherTests(unittest.TestCase):
    def test_service_filters_servers_that_ignore_version_search(self):
        older = local_codesystem()
        newer = deepcopy(older)
        newer["id"] = "local-answer-0-2-0"
        newer["version"] = "0.2.0"

        def transport(url, timeout):
            return 200, {
                "resourceType": "Bundle",
                "entry": [
                    {"resource": older},
                    {"resource": newer},
                ],
            }

        service = FhirCodeSystemService(
            "http://localhost:8088/fhir", transport=transport
        )
        self.assertEqual(
            service.search_by_canonical(
                older["url"], version="0.2.0", count=2
            ),
            [newer],
        )

    def test_complete_codesystem_validation_and_fingerprint(self):
        resource = local_codesystem()
        self.assertEqual(
            validate_complete_codesystem(resource),
            ["answer--yes", "answer--no"],
        )
        reordered = deepcopy(resource)
        reordered["concept"].reverse()
        self.assertEqual(
            codesystem_fingerprint(resource),
            codesystem_fingerprint(reordered),
        )

    def test_exact_canonical_version_is_reused_and_codes_are_validated(self):
        resource = local_codesystem()
        service = FakeReadService(matches=[resource])
        publisher = FhirCodeSystemPublisher(
            base_url="http://localhost:8088/fhir",
            api_key="not-recorded",
            read_service=service,
        )
        result = publisher.apply(publisher.plan(resource))
        self.assertEqual(result["action"], "reuse_exact_codesystem")
        self.assertTrue(result["post_write_content_verified"])
        self.assertEqual(len(service.validated), 2)

    def test_conflicting_canonical_version_is_never_overwritten(self):
        resource = local_codesystem()
        conflict = deepcopy(resource)
        conflict["concept"][0]["display"] = "affirmative"
        service = FakeReadService(matches=[conflict])
        publisher = FhirCodeSystemPublisher(
            base_url="http://localhost:8088/fhir",
            api_key="not-recorded",
            read_service=service,
        )
        with self.assertRaises(FhirCodeSystemPublishError):
            publisher.plan(resource)

    def test_identifier_collision_is_rejected(self):
        resource = local_codesystem()
        collision = deepcopy(resource)
        collision["url"] = "https://other.example/CodeSystem/local-answer"
        service = FakeReadService(collision=collision)
        publisher = FhirCodeSystemPublisher(
            base_url="http://localhost:8088/fhir",
            api_key="not-recorded",
            read_service=service,
        )
        with self.assertRaises(FhirCodeSystemPublishError):
            publisher.plan(resource)

    def test_create_uses_authenticated_put_and_post_write_verification(self):
        resource = local_codesystem()
        service = FakeReadService()
        calls = []

        def write_transport(method, url, body, headers, timeout):
            calls.append((method, url, body, headers, timeout))
            service.matches = [deepcopy(body)]
            return 201, deepcopy(body), {}

        publisher = FhirCodeSystemPublisher(
            base_url="http://localhost:8088/fhir",
            api_key="secret-not-logged",
            read_service=service,
            write_transport=write_transport,
        )
        result = publisher.apply(publisher.plan(resource))
        self.assertEqual(result["action"], "create")
        self.assertEqual(result["http_status"], 201)
        self.assertEqual(calls[0][0], "PUT")
        self.assertTrue(calls[0][1].endswith("/CodeSystem/local-answer"))
        self.assertEqual(calls[0][3], {"X-API-Key": "secret-not-logged"})

    def test_rejects_incomplete_or_duplicate_content(self):
        resource = local_codesystem()
        resource["content"] = "fragment"
        with self.assertRaises(FhirCodeSystemPublishError):
            validate_complete_codesystem(resource)
        resource = local_codesystem()
        resource["concept"][1]["code"] = resource["concept"][0]["code"]
        with self.assertRaises(FhirCodeSystemPublishError):
            validate_complete_codesystem(resource)


if __name__ == "__main__":
    unittest.main()
