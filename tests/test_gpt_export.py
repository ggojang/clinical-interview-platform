import json
import tempfile
import unittest
from pathlib import Path

from tools.gpt_export.build import build
from tools.privacy.check_repository import scan


ROOT = Path(__file__).resolve().parents[1]


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


class GptExportTests(unittest.TestCase):
    def test_export_is_deterministic_and_response_free(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_path = Path(first)
            second_path = Path(second)
            one = build(ROOT, first_path)
            two = build(ROOT, second_path)
            self.assertEqual(one, two)
            self.assertEqual(
                sorted(
                    (path.relative_to(first_path), path.read_bytes())
                    for path in first_path.rglob("*") if path.is_file()
                ),
                sorted(
                    (path.relative_to(second_path), path.read_bytes())
                    for path in second_path.rglob("*") if path.is_file()
                ),
            )
            forbidden = {
                "raw_text", "raw_input", "patient_response", "patient_responses",
                "questionnaire_response", "conversation", "transcript", "evidence",
            }
            for path in first_path.rglob("*.json"):
                document = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(forbidden & {key.lower() for key in walk_keys(document)})
                self.assertFalse(document.get("contains_patient_responses", False))

    def test_export_has_core_resources(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build(ROOT, output_path)
            names = {resource["name"] for resource in manifest["resources"]}
            self.assertTrue({
                "reason-for-encounters", "screening-kr",
                "rfe-cough-facts", "rfe-cough-questions", "rfe-cough-rules",
                "rfe-dyspnea-facts", "rfe-dyspnea-questions", "rfe-dyspnea-rules",
                "rfe-fever-facts", "rfe-fever-questions", "rfe-fever-rules",
            }.issubset(names))
            for resource in manifest["resources"]:
                self.assertEqual(len(resource["sha256"]), 64)
            for path in (output_path / "rfe").rglob("*.json"):
                self.assertLess(path.stat().st_size, 50_000, path)

    def test_rfe_catalog_and_bundles_are_consistent(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            build(ROOT, output_path)
            catalog = json.loads(
                (output_path / "reason-for-encounters.json").read_text(encoding="utf-8")
            )
            implemented = {
                entry["id"].removeprefix("rfe.")
                for entry in catalog["entries"]
                if entry.get("implementation_status") == "implemented"
                and entry["id"] != "rfe.preventive_care"
            }
            self.assertEqual(implemented, {"cough", "dyspnea", "fever"})
            for slug in implemented:
                for kind in ("facts", "questions", "rules"):
                    document = json.loads(
                        (output_path / "rfe" / slug / f"{kind}.json").read_text(
                            encoding="utf-8"
                        )
                    )
                    self.assertEqual(document["reason_for_encounter"], f"rfe.{slug}")
                    self.assertGreater(document["count"], 0)
                    self.assertFalse(document["contains_patient_responses"])

    def test_additional_comment_is_structured_and_upgrade_aware(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            build(ROOT, output_path)
            facts = json.loads((output_path / "facts.json").read_text(encoding="utf-8"))
            comment = next(
                item for item in facts["items"] if item["id"] == "interview.additional_comment"
            )
            self.assertTrue(comment["handling"]["resolution_includes_improvement"])
            self.assertTrue(comment["handling"]["never_publish_raw_response"])
            self.assertIn("improvement_status", comment["fields"])

    def test_privacy_scanner_detects_direct_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_identifier = "900101" + "-" + "1234567"
            (root / "bad.md").write_text(f"identifier {synthetic_identifier}", encoding="utf-8")
            findings = scan(root)
            self.assertTrue(any("resident registration" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
