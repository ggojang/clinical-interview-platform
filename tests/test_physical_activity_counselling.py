from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import CompilationError, compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import PHYSICAL_ACTIVITY_COUNSELLING_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class PhysicalActivityCounsellingPackageTests(unittest.TestCase):
    def test_package_is_complete_research_only_and_safety_covered(self):
        package = compile_package(profile="physical_activity_counselling")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(50, len(facts))
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(5, package["coverage"]["total_safety_rules"])
        self.assertEqual(5, package["coverage"]["safety_rules_with_simulations"])
        self.assertEqual([], package["coverage"]["uncovered_safety_rules"])
        self.assertGreaterEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        self.assertFalse(package["usage_policy"]["production_allowed"])
        with self.assertRaises(CompilationError):
            compile_package(profile="physical_activity_counselling", production=True)

    def test_activity_dose_and_capacity_are_atomic_and_conditional(self):
        package = compile_package(profile="physical_activity_counselling")
        policy = package["interview_completion_policy"]
        always = set(policy["required_facts"]["always"])
        self.assertTrue({
            "physical_activity.moderate_strenuous_days_last_7",
            "physical_activity.minutes_per_active_day",
            "physical_activity.muscle_strengthening_frequency",
            "physical_activity.sedentary_time_per_day",
        } <= always)
        inactive = next(
            item for item in policy["conditional_required_facts"]
            if item.get("when") == {"fact": "physical_activity.current_level", "in": ["inactive", "light_only"]}
        )
        self.assertTrue({
            "activity.exertional_chest_discomfort_history",
            "activity.exertional_breathlessness",
            "activity.exertional_dizziness_or_near_syncope",
            "activity.falls_or_balance_concern",
            "activity.prior_professional_restriction",
            "activity.readiness",
        } <= set(inactive["required_facts"]))

    def test_stom_verified_loinc_and_panel_boundary(self):
        mapping = json.loads(
            (ROOT / "mappings/terminology/snomed-mrcm-physical-activity-counselling.json")
            .read_text(encoding="utf-8")
        )
        questions = {item["fact_id"]: item for item in mapping["verified_loinc_questions"]}
        self.assertEqual("68515-6", questions["physical_activity.moderate_strenuous_days_last_7"]["code"])
        self.assertEqual("68516-4", questions["physical_activity.minutes_per_active_day"]["code"])
        self.assertEqual("82291-6", questions["physical_activity.muscle_strengthening_frequency"]["code"])
        self.assertEqual(
            {"89574-8", "82290-8"},
            {item["code"] for item in mapping["verified_panel_references_excluded_from_item_mapping"]},
        )
        self.assertFalse(mapping["atomicity"]["compound_exact_mapping_allowed"])

        package = compile_package(profile="physical_activity_counselling")
        question_nodes = {
            node["collects"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate"
        }
        codes = {
            (item["system"], item["code"], item["mapping_relation"])
            for item in question_nodes["physical_activity.moderate_strenuous_days_last_7"]
            ["semantic_binding"]["standard_mappings"]
        }
        self.assertIn(("http://loinc.org", "68515-6", "equivalent"), codes)

    def test_clinician_minimum_preserves_activity_dose_safety_and_goal(self):
        package = compile_package(profile="physical_activity_counselling")
        context = json.loads(
            (ROOT / package["clinician_submission_context"]["resource_ref"])
            .read_text(encoding="utf-8")
        )
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.physical_activity_counselling"]
        )
        self.assertTrue({
            "physical_activity.types", "physical_activity.contexts",
            "physical_activity.moderate_strenuous_days_last_7",
            "physical_activity.minutes_per_active_day",
            "physical_activity.muscle_strengthening_frequency",
            "physical_activity.sedentary_time_per_day",
            "activity.exertional_syncope", "activity.daily_function_limit",
            "activity.pregnancy_or_postpartum_status", "activity.patient_concern",
            "activity.expected_help",
        } <= minimum)

    def test_all_physical_activity_simulations_pass(self):
        report = run_evaluation(PHYSICAL_ACTIVITY_COUNSELLING_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        self.assertEqual(10, report["case_count"])
        routine = next(
            item for item in report["results"]
            if item["case_id"] == "ACTIVITY-VAGUE-REMOTE-FIRST-VISIT"
        )
        self.assertIn("physical_activity.moderate_strenuous_days_last_7", routine["selected_facts"])
        self.assertIn("physical_activity.minutes_per_active_day", routine["selected_facts"])
        self.assertIn("physical_activity.sedentary_time_per_day", routine["selected_facts"])


if __name__ == "__main__":
    unittest.main()
