import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from runtime.restricted_questionnaires import (
    RestrictedQuestionnaireError,
    RestrictedQuestionnaireStore,
)


class RestrictedQuestionnaireStoreTest(unittest.TestCase):
    def make_store(self, *, enabled=True, digest=None, rights_status=None):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        content = root / "content"
        content.mkdir()
        questionnaire = {
            "resourceType": "Questionnaire",
            "id": "synthetic-test-only",
            "version": "test-1",
            "status": "draft",
            "item": [
                {
                    "linkId": "synthetic-1",
                    "text": "Synthetic fixture, not a source questionnaire",
                    "type": "string",
                }
            ],
        }
        path = content / "questionnaire.json"
        payload = json.dumps(questionnaire, ensure_ascii=False).encode("utf-8")
        path.write_bytes(payload)
        registry = {
            "test_only": True,
            "contains_patient_responses": False,
            "questionnaires": [
                {
                    "instrument_id": "synthetic.test",
                    "title": "Synthetic test questionnaire",
                    "source_family": "test fixture",
                    "source_version": "test-1",
                    "relative_path": "content/questionnaire.json",
                    "sha256": digest or hashlib.sha256(payload).hexdigest(),
                    "rights_status": rights_status or "user_supplied_for_internal_test",
                    "test_only": True,
                    "enabled": enabled,
                }
            ],
        }
        registry_path = root / "registry.json"
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        try:
            store = RestrictedQuestionnaireStore(root, registry_path)
        except Exception:
            temp.cleanup()
            raise
        return temp, store

    def test_loads_verified_local_fhir_questionnaire(self):
        temp, store = self.make_store()
        self.addCleanup(temp.cleanup)
        questionnaire = store.load("synthetic.test")
        self.assertEqual(questionnaire["resourceType"], "Questionnaire")
        self.assertEqual(questionnaire["version"], "test-1")

    def test_disabled_instrument_fails_closed(self):
        temp, store = self.make_store(enabled=False)
        self.addCleanup(temp.cleanup)
        with self.assertRaisesRegex(RestrictedQuestionnaireError, "disabled"):
            store.load("synthetic.test")

    def test_digest_mismatch_fails_closed(self):
        temp, store = self.make_store(digest="0" * 64)
        self.addCleanup(temp.cleanup)
        with self.assertRaisesRegex(RestrictedQuestionnaireError, "sha256 mismatch"):
            store.load("synthetic.test")

    def test_unverified_rights_status_is_rejected(self):
        with self.assertRaisesRegex(RestrictedQuestionnaireError, "rights_status"):
            temp, _ = self.make_store(rights_status="public_download_assumed")
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
