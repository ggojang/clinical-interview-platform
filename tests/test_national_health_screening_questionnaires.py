from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
QUESTIONNAIRE_DIR = ROOT / "fhir/r4/questionnaires"
FORM_1 = QUESTIONNAIRE_DIR / "kr-national-health-screening-form-1-2025.json"
FORM_2 = QUESTIONNAIRE_DIR / "kr-national-health-screening-form-2-2025.json"
MANIFEST = ROOT / "sources/manifests/kr-national-health-screening.json"


def walk(items):
    for item in items or []:
        yield item
        yield from walk(item.get("item"))


class NationalHealthScreeningQuestionnaireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.form_1 = json.loads(FORM_1.read_text(encoding="utf-8"))
        cls.form_2 = json.loads(FORM_2.read_text(encoding="utf-8"))

    def test_official_forms_are_separate_source_defined_fixed_questionnaires(self):
        self.assertEqual(self.form_1["resourceType"], "Questionnaire")
        self.assertEqual(self.form_1["title"], "건강검진 문진표")
        self.assertEqual(self.form_2["title"], "건강검진 추가 문진표")
        for resource in (self.form_1, self.form_2):
            tags = {tag["code"] for tag in resource["meta"]["tag"]}
            self.assertIn("source-defined-fixed", tags)
            self.assertIn("unreviewed", tags)
            self.assertTrue(resource["experimental"])
            self.assertEqual(len(resource["derivedFrom"]), 1)

    def test_form_1_preserves_official_core_wording_choices_and_order(self):
        items = list(walk(self.form_1["item"]))
        by_id = {item["linkId"]: item for item in items}
        self.assertEqual(
            by_id["q1"]["text"],
            "다음과 같은 질병으로 진단을 받았거나, 현재 약물 치료 중이십니까?",
        )
        self.assertEqual(
            by_id["q4-ever-cigarettes"]["text"],
            "지금까지 평생 총 5갑(100개비) 이상의 일반담배(궐련)를 피운 적이 있습니까?",
        )
        self.assertEqual(
            [option["valueString"] for option in by_id["q6-1-recent-liquid-ecigarette"]["answerOption"]],
            ["아니요", "월 1-2일", "월 3-9일", "월 10-29일", "매일"],
        )
        self.assertEqual(by_id["q10-strength-days"]["prefix"], "10.")
        all_text = "\n".join(item.get("text", "") for item in items)
        self.assertNotIn("현재 불편한 증상이 있나요?", all_text)
        self.assertNotIn("현재 또는 과거의 주요 질환을 알려주세요.", all_text)

    def test_additional_form_declares_age_scope_and_exact_activity_items(self):
        items = list(walk(self.form_2["item"]))
        by_id = {item["linkId"]: item for item in items}
        self.assertIn("66세, 70세, 80세", by_id["age-scope"]["text"])
        self.assertEqual(
            by_id["q3-1-eating"]["text"],
            "음식을 차려주면 남의 도움 없이 혼자서 식사하십니까?",
        )
        self.assertEqual(
            [option["valueString"] for option in by_id["q5-urination"]["answerOption"]],
            ["예", "아니요"],
        )

    def test_manifest_registers_complete_official_sources_with_hashes(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        official = manifest["artifacts"][:2]
        self.assertTrue(all(item["complete"] for item in official))
        self.assertTrue(all(item["digest"].startswith("sha256:") for item in official))
        self.assertTrue(all(item["kind"] == "source_defined_fixed_questionnaire" for item in official))
        archive = manifest["binary_archive"]
        self.assertEqual(archive["storage"], "private_server_only")
        self.assertEqual(archive["repository_distribution"], "metadata_only")
        self.assertEqual(
            {item["digest"] for item in archive["files"]},
            {item["digest"] for item in official},
        )


if __name__ == "__main__":
    unittest.main()
