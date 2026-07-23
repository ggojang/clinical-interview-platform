from __future__ import annotations

from copy import deepcopy
import unittest

from interoperability.fhir_valueset_reconcile import (
    ORIGIN_EXTENSION,
    VERIFICATION_SOURCE_EXTENSION,
    ValueSetReconciliationError,
    build_extended_valueset,
    membership_fingerprint,
    reconcile_reference,
)
from interoperability.fhir_valueset_publish import (
    FhirValueSetPublishError,
    FhirValueSetPublisher,
)


def reference_valueset() -> dict:
    return {
        "resourceType": "ValueSet",
        "id": "reference-example",
        "url": "https://example.org/fhir/ValueSet/reference-example",
        "version": "1.0.0",
        "name": "ReferenceExample",
        "title": "Reference example",
        "status": "active",
        "compose": {
            "include": [{
                "system": "http://snomed.info/sct",
                "version": "http://snomed.info/sct/version/example",
                "concept": [
                    {"code": "373066001", "display": "Yes"},
                    {"code": "373067005", "display": "No"},
                ],
            }]
        },
    }


class FhirValueSetReconciliationTest(unittest.TestCase):
    def test_membership_fingerprint_ignores_order_and_display(self):
        left = reference_valueset()
        right = deepcopy(left)
        right["compose"]["include"][0]["concept"] = [
            {"code": "373067005", "display": "Negative response"},
            {"code": "373066001", "display": "Affirmative response"},
        ]
        self.assertEqual(
            membership_fingerprint(left),
            membership_fingerprint(right),
        )

    def test_exact_reference_is_reused(self):
        reference = reference_valueset()
        decision = reconcile_reference(reference, [deepcopy(reference)])
        self.assertEqual(decision["action"], "reuse_exact_reference")
        self.assertFalse(decision["safe_to_write"])

    def test_same_content_with_other_canonical_does_not_replace_reference(self):
        reference = reference_valueset()
        existing = deepcopy(reference)
        existing["id"] = "existing-example"
        existing["url"] = "https://server.example/fhir/ValueSet/existing"
        decision = reconcile_reference(reference, [existing])
        self.assertEqual(decision["action"], "create_reference_unchanged")
        self.assertTrue(decision["safe_to_write"])
        self.assertEqual(decision["resource"], reference)
        self.assertEqual(
            decision["reference_canonical"],
            reference["url"] + "|" + reference["version"],
        )
        self.assertEqual(
            decision["content_equivalent_candidates"][0]["canonical"],
            existing["url"] + "|" + existing["version"],
        )

    def test_canonical_content_conflict_is_never_overwritten(self):
        reference = reference_valueset()
        conflict = deepcopy(reference)
        conflict["compose"]["include"][0]["concept"] = [
            {"code": "373066001", "display": "Yes"}
        ]
        decision = reconcile_reference(reference, [conflict])
        self.assertEqual(decision["action"], "canonical_content_conflict")
        self.assertFalse(decision["safe_to_write"])

    def test_absent_reference_is_returned_unchanged_for_creation(self):
        reference = reference_valueset()
        snapshot = deepcopy(reference)
        decision = reconcile_reference(reference, [])
        self.assertEqual(decision["action"], "create_reference_unchanged")
        self.assertEqual(decision["resource"], snapshot)
        self.assertEqual(reference, snapshot)
        self.assertIsNot(decision["resource"], reference)

    def test_extension_is_separate_and_imports_untouched_reference(self):
        reference = reference_valueset()
        snapshot = deepcopy(reference)
        derived = build_extended_valueset(
            reference,
            [{
                "system": "http://snomed.info/sct",
                "version": "http://snomed.info/sct/version/example",
                "code": "261665006",
                "display": "Unknown",
                "verification_source": "STOM CodeSystem $validate-code",
            }],
            semantic_name="reference-example-context",
            title="Extended reference example",
            description="Context-specific extended answers.",
            date="2026-07-23",
        )
        self.assertEqual(reference, snapshot)
        self.assertTrue(derived["id"].startswith("a-extended-"))
        self.assertNotEqual(derived["url"], reference["url"])
        self.assertEqual(
            derived["compose"]["include"][0]["valueSet"],
            [reference["url"] + "|" + reference["version"]],
        )
        self.assertEqual(
            derived["compose"]["include"][1]["concept"][0]["code"],
            "261665006",
        )
        self.assertEqual(
            derived["compose"]["include"][1]["concept"][0]["extension"][0][
                "url"
            ],
            VERIFICATION_SOURCE_EXTENSION,
        )
        self.assertEqual(derived["extension"][0]["url"], ORIGIN_EXTENSION)
        self.assertEqual(
            derived["extension"][0]["valueCanonical"],
            reference["url"] + "|" + reference["version"],
        )

    def test_extension_requires_verified_standard_code_by_default(self):
        reference = reference_valueset()
        with self.assertRaises(ValueSetReconciliationError):
            build_extended_valueset(
                reference,
                [{
                    "system": (
                        "https://ggojang.github.io/"
                        "clinical-interview-platform/fhir/"
                        "CodeSystem/clinical-interview-answer"
                    ),
                    "code": "local",
                    "verification_source": "local",
                }],
                semantic_name="invalid-local",
                title="Invalid local extension",
                description="Must require explicit local authorization.",
                date="2026-07-23",
            )
        with self.assertRaises(ValueSetReconciliationError):
            build_extended_valueset(
                reference,
                [{
                    "system": "http://snomed.info/sct",
                    "code": "261665006",
                }],
                semantic_name="unverified",
                title="Unverified extension",
                description="Missing verification provenance.",
                date="2026-07-23",
            )

    def test_publisher_never_overwrites_conflicting_reference_membership(self):
        reference = reference_valueset()
        conflict = deepcopy(reference)
        conflict["compose"]["include"][0]["concept"] = [
            {"code": "373066001", "display": "Yes"}
        ]

        class ReadService:
            def search_by_canonical(
                self, canonical, version=None, count=2
            ):
                return [conflict]

        publisher = FhirValueSetPublisher(
            base_url="http://localhost:8088/fhir",
            api_key="not-recorded",
            read_service=ReadService(),
        )
        with self.assertRaises(FhirValueSetPublishError):
            publisher.plan(reference)

    def test_publisher_apply_rejects_update_action(self):
        publisher = FhirValueSetPublisher(
            base_url="http://localhost:8088/fhir",
            api_key="not-recorded",
        )
        with self.assertRaises(FhirValueSetPublishError):
            publisher.apply({
                "action": "update",
                "server_id": "reference-example",
                "resource": reference_valueset(),
            })
