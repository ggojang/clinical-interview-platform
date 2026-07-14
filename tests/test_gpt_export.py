import json
import re
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
                "common-facts", "reason-for-encounters", "screening-kr",
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
            facts = json.loads((output_path / "common-facts.json").read_text(encoding="utf-8"))
            comment = next(
                item for item in facts["items"] if item["id"] == "interview.additional_comment"
            )
            self.assertTrue(comment["handling"]["resolution_includes_improvement"])
            self.assertTrue(comment["handling"]["never_publish_raw_response"])
            self.assertIn("improvement_status", comment["fields"])

    def test_backward_compatible_action_payloads_stay_below_limit(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build(ROOT, output_path)
            self.assertEqual(manifest["interview_entry"]["type"], "reason_for_encounter")
            self.assertEqual(len(manifest["interview_entry"]["catalog"]), 14)
            self.assertTrue(
                manifest["additional_comment_policy"][
                    "resolution_includes_service_improvement"
                ]
            )
            numbering = manifest["numbering_policy"]
            self.assertFalse(numbering["display_question_sequence"])
            self.assertTrue(numbering["option_numbers_must_be_unique_within_question"])
            self.assertEqual(
                set(numbering["boolean_unknown_decline_codes"]), {"1", "2", "3", "5"}
            )
            for name in ("facts.json", "question-groups.json", "safety-rules.json"):
                self.assertLess((output_path / name).stat().st_size, 100_000, name)
            questions = json.loads(
                (output_path / "question-groups.json").read_text(encoding="utf-8")
            )
            for question in questions["items"]:
                if question.get("type") != "QuestionTemplate":
                    continue
                self.assertIsInstance(question.get("text") or question.get("wording"), str)
                if "fact_id" in question:
                    self.assertTrue(
                        question["fact_id"] is None or isinstance(question["fact_id"], str)
                    )

    def test_question_text_does_not_embed_display_sequence(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            build(ROOT, output_path)
            paths = [output_path / "question-groups.json"]
            paths.extend((output_path / "rfe").glob("*/questions.json"))
            prefix = re.compile(r"^\s*(?:질문\s*)?\d+\s*(?:번|[.)：:])")
            for path in paths:
                document = json.loads(path.read_text(encoding="utf-8"))
                for question in document["items"]:
                    text = question.get("text") or question.get("wording")
                    if isinstance(text, str):
                        self.assertIsNone(prefix.match(text), (path, question.get("id")))

    def test_privacy_scanner_detects_direct_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_identifier = "900101" + "-" + "1234567"
            (root / "bad.md").write_text(f"identifier {synthetic_identifier}", encoding="utf-8")
            findings = scan(root)
            self.assertTrue(any("resident registration" in finding for finding in findings))


if __name__ == "__main__":
    unittest.main()
