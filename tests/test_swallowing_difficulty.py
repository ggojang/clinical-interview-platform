from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import CompilationError, compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import SWALLOWING_DIFFICULTY_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class SwallowingDifficultyPackageTests(unittest.TestCase):
    def test_package_is_complete_research_only_and_safety_covered(self):
        package = compile_package(profile="swallowing_difficulty")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(60, len(facts))
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(8, package["coverage"]["total_safety_rules"])
        self.assertEqual(8, package["coverage"]["safety_rules_with_simulations"])
        self.assertEqual([], package["coverage"]["uncovered_safety_rules"])
        self.assertGreaterEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        self.assertFalse(package["usage_policy"]["production_allowed"])
        with self.assertRaises(CompilationError):
            compile_package(profile="swallowing_difficulty", production=True)

    def test_food_consistency_and_pain_questions_are_atomic(self):
        package = compile_package(profile="swallowing_difficulty")
        always = set(package["interview_completion_policy"]["required_facts"]["always"])
        self.assertTrue({
            "swallow.solid_food_difficulty_last_7_days",
            "swallow.soft_food_difficulty_last_7_days",
            "swallow.liquid_difficulty_last_7_days",
            "swallow.painful_swallowing",
        } <= always)
        painful = next(
            item for item in package["interview_completion_policy"]["conditional_required_facts"]
            if item.get("when") == {"fact": "swallow.painful_swallowing", "equals": True}
        )
        self.assertEqual(
            {"swallow.pain_location", "swallow.pain_nrs"},
            set(painful["required_facts"]),
        )

    def test_source_defined_loinc_items_remain_related_not_equivalent(self):
        package = compile_package(profile="swallowing_difficulty")
        questions = {
            node["collects"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate"
        }
        pain = questions["swallow.pain_nrs"]["semantic_binding"]
        self.assertEqual(
            [{"system": "http://loinc.org", "code": "72514-3"}],
            pain["fhir_standard_item_codes"],
        )
        for fact_id, code in (
            ("swallow.solid_food_difficulty_last_7_days", "70367-8"),
            ("swallow.soft_food_difficulty_last_7_days", "70368-6"),
            ("swallow.liquid_difficulty_last_7_days", "70369-4"),
        ):
            binding = questions[fact_id]["semantic_binding"]
            self.assertNotIn("fhir_standard_item_codes", binding)
            self.assertEqual("related", binding["standard_mappings"][0]["mapping_relation"])
            self.assertEqual(code, binding["standard_mappings"][0]["code"])

    def test_clinician_minimum_preserves_pattern_impact_context_and_goal(self):
        package = compile_package(profile="swallowing_difficulty")
        context = json.loads(
            (ROOT / package["clinician_submission_context"]["resource_ref"])
            .read_text(encoding="utf-8")
        )
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.swallowing_difficulty"]
        )
        self.assertTrue({
            "swallow.first_onset", "swallow.course",
            "swallow.difficulty_initiating", "swallow.perceived_sticking_location",
            "swallow.solid_food_difficulty_last_7_days",
            "swallow.liquid_difficulty_last_7_days", "swallow.pain_nrs",
            "swallow.cough_during_or_after", "swallow.wet_voice_after",
            "swallow.intake_reduction", "swallow.unintentional_weight_change",
            "swallow.daily_function_and_social_impact", "swallow.neurologic_history",
            "swallow.current_medicines", "swallow.previous_assessment_or_test",
            "swallow.accessibility_need", "swallow.patient_concern",
            "swallow.expected_help",
        } <= minimum)

    def test_all_swallowing_simulations_pass(self):
        report = run_evaluation(SWALLOWING_DIFFICULTY_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        self.assertEqual(12, report["case_count"])
        routine = next(
            item for item in report["results"]
            if item["case_id"] == "SWALLOW-VAGUE-REMOTE-FIRST-VISIT"
        )
        self.assertIn("swallow.solid_food_difficulty_last_7_days", routine["selected_facts"])
        self.assertIn("swallow.soft_food_difficulty_last_7_days", routine["selected_facts"])
        self.assertIn("swallow.liquid_difficulty_last_7_days", routine["selected_facts"])


if __name__ == "__main__":
    unittest.main()
