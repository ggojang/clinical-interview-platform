from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import CompilationError, compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import ACUTE_CONFUSION_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class AcuteConfusionPackageTests(unittest.TestCase):
    def test_package_is_complete_research_only_and_safety_covered(self):
        package = compile_package(profile="acute_confusion")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(64, len(facts))
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(11, package["coverage"]["total_safety_rules"])
        self.assertEqual(11, package["coverage"]["safety_rules_with_simulations"])
        self.assertEqual([], package["coverage"]["uncovered_safety_rules"])
        self.assertGreaterEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        self.assertFalse(package["usage_policy"]["production_allowed"])
        with self.assertRaises(CompilationError):
            compile_package(profile="acute_confusion", production=True)

    def test_time_sensitive_safety_facts_are_asked_before_routine_pattern(self):
        report = run_evaluation(ACUTE_CONFUSION_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        for case_id, rule_id in {
            "ACUTE-CONFUSION-SEVERE-ILLNESS": "rule.acute_confusion.safety.severe-illness",
            "ACUTE-CONFUSION-NO-SUPERVISION": "rule.acute_confusion.safety.no-safe-supervision",
        }.items():
            result = next(item for item in report["results"] if item["case_id"] == case_id)
            self.assertIn(rule_id, result["triggered_rules"])
            self.assertLessEqual(result["turns"], 24)

    def test_only_pain_nrs_uses_verified_exact_loinc_mapping(self):
        package = compile_package(profile="acute_confusion")
        questions = {
            node["collects"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate"
        }
        self.assertEqual(
            [{"system": "http://loinc.org", "code": "72514-3"}],
            questions["acute_confusion.pain_nrs"]["semantic_binding"]["fhir_standard_item_codes"],
        )
        for fact_id in (
            "acute_confusion.acute_change_from_baseline",
            "acute_confusion.attention_change",
            "acute_confusion.disorganized_thinking_or_speech",
            "acute_confusion.current_reduced_consciousness",
        ):
            self.assertEqual(
                [],
                questions[fact_id].get("semantic_binding", {}).get(
                    "fhir_standard_item_codes", []
                ),
            )

    def test_catalog_routes_sudden_confusion_separately_from_memory_concern(self):
        catalog = json.loads((ROOT / "knowledge/catalog/primary-care-rfe.json").read_text(encoding="utf-8"))
        acute = next(item for item in catalog["entries"] if item["id"] == "rfe.acute_confusion")
        memory = next(item for item in catalog["entries"] if item["id"] == "rfe.memory_cognitive_concern")
        self.assertIn("갑자기 혼란스러워요", acute["aliases"])
        self.assertNotIn("갑자기 혼란스러워요", memory["aliases"])
        self.assertEqual("package.primary-care-acute-confusion", acute["package_id"])

    def test_clinician_minimum_preserves_baseline_timeline_context_and_goals(self):
        package = compile_package(profile="acute_confusion")
        context = json.loads((ROOT / package["clinician_submission_context"]["resource_ref"]).read_text(encoding="utf-8"))
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.acute_confusion"]
        )
        self.assertTrue({
            "acute_confusion.baseline_informant",
            "acute_confusion.acute_change_from_baseline",
            "acute_confusion.last_known_normal",
            "acute_confusion.fluctuation_timing",
            "acute_confusion.attention_change",
            "acute_confusion.current_medicines",
            "acute_confusion.safe_supervision_available",
            "acute_confusion.previous_tests",
            "acute_confusion.accessibility_need",
            "acute_confusion.patient_or_caregiver_concern",
            "acute_confusion.expected_help",
        } <= minimum)


if __name__ == "__main__":
    unittest.main()
