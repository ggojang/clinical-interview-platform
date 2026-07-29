import unittest
from types import SimpleNamespace

from interoperability.fhir_valueset_service import FhirValueSetServiceError
from tools.fhir.publish_answer_valuesets import readable_catalog


class _CatalogService:
    def __init__(self, failure):
        self.failure = failure

    def list_valuesets(self):
        return [{"id": "good"}, {"id": "stale"}]

    def read_valueset(self, identifier):
        if identifier == "stale":
            raise self.failure
        return {"resourceType": "ValueSet", "id": identifier}


class PublishAnswerValueSetsTests(unittest.TestCase):
    def test_stale_list_row_is_reported_without_blocking_catalog(self):
        publisher = SimpleNamespace(read_service=_CatalogService(
            FhirValueSetServiceError("FHIR request failed: HTTP Error 404: Not Found")
        ))
        catalog, missing = readable_catalog(publisher)
        self.assertEqual([resource["id"] for resource in catalog], ["good"])
        self.assertEqual(missing, ["stale"])

    def test_non_404_catalog_failure_is_not_hidden(self):
        publisher = SimpleNamespace(read_service=_CatalogService(
            FhirValueSetServiceError("FHIR server returned HTTP 500")
        ))
        with self.assertRaises(FhirValueSetServiceError):
            readable_catalog(publisher)


if __name__ == "__main__":
    unittest.main()
