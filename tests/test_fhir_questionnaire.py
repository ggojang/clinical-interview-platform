from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QUESTIONNAIRE = ROOT / "fhir/r4/questionnaires/kr-patient-experience-evaluation-5th-2025.json"


class PatientExperienceQuestionnaireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resource = json.loads(QUESTIONNAIRE.read_text(encoding="utf-8"))

    def test_core_r4_identity_and_research_status(self):
        self.assertEqual(self.resource["resourceType"], "Questionnaire")
        self.assertEqual(self.resource["status"], "draft")
        self.assertTrue(self.resource["experimental"])
        tags = {(item["system"], item["code"]) for item in self.resource["meta"]["tag"]}
        self.assertTrue(any(code == "research-only" for _, code in tags))
        self.assertTrue(any(code == "unreviewed" for _, code in tags))

    def test_all_sections_questions_and_link_ids_are_preserved(self):
        sections = self.resource["item"]
        self.assertEqual(len(sections), 8)
        questions = [item for section in sections for item in section["item"] if item["type"] != "display"]
        self.assertEqual(len(questions), 26)
        link_ids = [section["linkId"] for section in sections]
        link_ids += [item["linkId"] for section in sections for item in section["item"]]
        self.assertEqual(len(link_ids), len(set(link_ids)))

    def test_source_specific_answer_sets_are_not_normalized_away(self):
        questions = {
            item["linkId"]: item
            for section in self.resource["item"]
            for item in section["item"]
            if item["type"] != "display"
        }
        q12 = {option["valueCoding"]["code"]: option["valueCoding"]["display"] for option in questions["q12"]["answerOption"]}
        self.assertEqual(q12["4"], "매우 그랬다")
        for link_id in ("q11", "q19", "q21"):
            self.assertIn("0", {option["valueCoding"]["code"] for option in questions[link_id]["answerOption"]})
        for link_id in ("q22", "q23"):
            limits = {extension["url"].rsplit("/", 1)[-1]: extension["valueInteger"] for extension in questions[link_id]["extension"]}
            self.assertEqual(limits, {"minValue": 0, "maxValue": 10})


if __name__ == "__main__":
    unittest.main()
