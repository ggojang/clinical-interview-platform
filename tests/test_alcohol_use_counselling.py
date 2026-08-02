from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import CompilationError, compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import ALCOHOL_USE_COUNSELLING_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class AlcoholUseCounsellingPackageTests(unittest.TestCase):
    def test_package_is_complete_research_only_and_safety_covered(self):
        package = compile_package(profile="alcohol_use_counselling")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(47, len(facts))
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(6, package["coverage"]["total_safety_rules"])
        self.assertEqual(6, package["coverage"]["safety_rules_with_simulations"])
        self.assertEqual([], package["coverage"]["uncovered_safety_rules"])
        self.assertGreaterEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        self.assertFalse(package["usage_policy"]["production_allowed"])
        with self.assertRaises(CompilationError):
            compile_package(profile="alcohol_use_counselling", production=True)

    def test_pattern_and_change_details_are_atomic_and_conditional(self):
        package = compile_package(profile="alcohol_use_counselling")
        policy = package["interview_completion_policy"]
        always = set(policy["required_facts"]["always"])
        self.assertNotIn("patient.alcohol.amount_per_occasion", always)
        current = next(
            item for item in policy["conditional_required_facts"]
            if item.get("when") == {"fact": "patient.alcohol.use_status", "equals": "current"}
        )
        required = set(current["required_facts"])
        self.assertTrue({
            "patient.alcohol.beverage_types", "patient.alcohol.frequency",
            "patient.alcohol.amount_per_occasion", "alcohol.largest_amount_in_one_day",
            "alcohol.heavy_day_frequency", "alcohol.last_use_time",
            "alcohol.prior_withdrawal_seizure", "alcohol.prior_delirium_tremens",
            "alcohol.injury_or_hazardous_use", "alcohol.readiness",
        } <= required)

    def test_stom_verified_loinc_and_instrument_boundary(self):
        mapping = json.loads(
            (ROOT / "mappings/terminology/snomed-mrcm-alcohol-use-counselling.json")
            .read_text(encoding="utf-8")
        )
        questions = {item["fact_id"]: item for item in mapping["verified_loinc_questions"]}
        self.assertEqual("68518-0", questions["patient.alcohol.frequency"]["code"])
        self.assertEqual("74014-2", questions["alcohol.last_use_time"]["code"])
        self.assertEqual("partial", questions["patient.alcohol.amount_per_occasion"]["relation"])
        self.assertEqual(
            {"72109-2", "72110-0", "75626-2"},
            {item["code"] for item in mapping["verified_instrument_references_excluded_from_dynamic_mapping"]},
        )
        self.assertFalse(mapping["atomicity"]["compound_exact_mapping_allowed"])

        package = compile_package(profile="alcohol_use_counselling")
        questions = {
            node["collects"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate"
        }
        frequency_codes = {
            (item["system"], item["code"], item["mapping_relation"])
            for item in questions["patient.alcohol.frequency"]
            ["semantic_binding"]["standard_mappings"]
        }
        self.assertIn(("http://loinc.org", "68518-0", "equivalent"), frequency_codes)
        amount_codes = {
            (item["system"], item["code"], item["mapping_relation"])
            for item in questions["patient.alcohol.amount_per_occasion"]
            ["semantic_binding"]["standard_mappings"]
        }
        self.assertIn(("http://loinc.org", "11287-0", "partial"), amount_codes)

    def test_clinician_minimum_preserves_raw_pattern_withdrawal_and_goal(self):
        package = compile_package(profile="alcohol_use_counselling")
        context = json.loads(
            (ROOT / package["clinician_submission_context"]["resource_ref"])
            .read_text(encoding="utf-8")
        )
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.alcohol_use_counselling"]
        )
        self.assertTrue({
            "patient.alcohol.beverage_types", "patient.alcohol.frequency",
            "patient.alcohol.amount_per_occasion", "alcohol.last_use_time",
            "alcohol.largest_amount_in_one_day", "alcohol.heavy_day_frequency",
            "alcohol.prior_withdrawal_seizure", "alcohol.prior_delirium_tremens",
            "alcohol.pregnancy_or_postpartum_status", "alcohol.patient_concern",
            "alcohol.expected_help",
        } <= minimum)

    def test_all_alcohol_simulations_pass(self):
        report = run_evaluation(ALCOHOL_USE_COUNSELLING_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        self.assertEqual(10, report["case_count"])
        routine = next(
            item for item in report["results"]
            if item["case_id"] == "ALCOHOL-VAGUE-REMOTE-FIRST-VISIT"
        )
        self.assertIn("patient.alcohol.frequency", routine["selected_facts"])
        self.assertIn("patient.alcohol.amount_per_occasion", routine["selected_facts"])
        self.assertIn("alcohol.heavy_day_frequency", routine["selected_facts"])


if __name__ == "__main__":
    unittest.main()
