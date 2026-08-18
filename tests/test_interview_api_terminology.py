from __future__ import annotations

import unittest

from services.interview_api.terminology import TerminologyClient, TerminologyError


class _PayloadTerminologyClient(TerminologyClient):
    def __init__(self, payload):
        super().__init__("https://terminology.example/fhir")
        self.payload = payload
        self.requested_url = None

    def _get_json(self, url, *, not_found_code="terminology_unavailable"):
        self.requested_url = url
        return self.payload


class TerminologyClientTests(unittest.TestCase):
    def test_expand_uses_fixed_server_and_flattens_nested_concepts(self):
        client = _PayloadTerminologyClient(
            {
                "resourceType": "ValueSet",
                "expansion": {
                    "total": 2,
                    "contains": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "1",
                            "display": "First",
                            "contains": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "code": "2",
                                    "display": "Second",
                                }
                            ],
                        }
                    ],
                },
            }
        )
        result = client.expand("https://example.org/fhir/ValueSet/test", count=10)
        self.assertEqual([item["code"] for item in result["contains"]], ["1", "2"])
        self.assertIn("terminology.example/fhir/ValueSet/$expand", client.requested_url)
        self.assertIn("url=https%3A%2F%2Fexample.org", client.requested_url)

    def test_expand_rejects_non_http_canonical_without_network_access(self):
        client = _PayloadTerminologyClient({})
        with self.assertRaises(TerminologyError) as context:
            client.expand("file:///etc/passwd")
        self.assertEqual(context.exception.code, "invalid_terminology_request")
        self.assertIsNone(client.requested_url)

    def test_operation_outcome_is_not_treated_as_answer_options(self):
        client = _PayloadTerminologyClient(
            {"resourceType": "OperationOutcome", "issue": [{"diagnostics": "missing"}]}
        )
        with self.assertRaises(TerminologyError) as context:
            client.expand("https://example.org/fhir/ValueSet/missing")
        self.assertEqual(context.exception.code, "valueset_not_found")
        self.assertEqual(context.exception.status, 404)

    def test_unconfigured_status_is_explicit_and_safe(self):
        client = TerminologyClient(None)
        status = client.status()
        self.assertFalse(status["configured"])
        self.assertFalse(status["available"])
        self.assertFalse(status["patient_data_transmitted"])


if __name__ == "__main__":
    unittest.main()
