from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import CompilationError, compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import JAUNDICE_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class JaundicePackageTests(unittest.TestCase):
    def test_package_is_complete_research_only_and_safety_covered(self):
        package = compile_package(profile="jaundice")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(75, len(facts))
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(11, package["coverage"]["total_safety_rules"])
        self.assertEqual(11, package["coverage"]["safety_rules_with_simulations"])
        self.assertEqual([], package["coverage"]["uncovered_safety_rules"])
        self.assertGreaterEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        self.assertFalse(package["usage_policy"]["production_allowed"])
        with self.assertRaises(CompilationError):
            compile_package(profile="jaundice", production=True)

    def test_newborn_unwell_rule_precedes_stable_newborn_handoff(self):
        report = run_evaluation(JAUNDICE_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        unwell = next(item for item in report["results"] if item["case_id"] == "JAUNDICE-NEWBORN-UNWELL")
        stable = next(item for item in report["results"] if item["case_id"] == "JAUNDICE-NEWBORN")
        self.assertEqual("emergency", unwell["safety_level"])
        self.assertIn("rule.jaundice.safety.newborn-unwell", unwell["triggered_rules"])
        self.assertEqual("urgent", stable["safety_level"])
        self.assertIn("rule.jaundice.safety.newborn-jaundice", stable["triggered_rules"])

    def test_bilirubin_and_pain_questions_have_verified_atomic_loinc_bindings(self):
        package = compile_package(profile="jaundice")
        questions = {
            node["collects"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate"
        }
        expected = {
            "jaundice.latest_total_bilirubin": "1975-2",
            "jaundice.latest_direct_bilirubin": "1968-7",
            "jaundice.pain_nrs": "72514-3",
        }
        for fact_id, code in expected.items():
            self.assertEqual(
                [{"system": "http://loinc.org", "code": code}],
                questions[fact_id]["semantic_binding"]["fhir_standard_item_codes"],
            )

    def test_catalog_routes_jaundice_separately_from_chronic_liver_follow_up(self):
        catalog = json.loads((ROOT / "knowledge/catalog/primary-care-rfe.json").read_text(encoding="utf-8"))
        jaundice = next(item for item in catalog["entries"] if item["id"] == "rfe.jaundice")
        chronic = next(item for item in catalog["entries"] if item["id"] == "rfe.liver_function_chronic_follow_up")
        self.assertIn("황달", jaundice["aliases"])
        self.assertNotIn("황달", chronic["aliases"])
        self.assertEqual("package.primary-care-jaundice", jaundice["package_id"])

    def test_clinician_minimum_preserves_observation_context_results_and_goals(self):
        package = compile_package(profile="jaundice")
        context = json.loads((ROOT / package["clinician_submission_context"]["resource_ref"]).read_text(encoding="utf-8"))
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.jaundice"]
        )
        self.assertTrue({
            "jaundice.first_onset", "jaundice.course", "jaundice.scleral_yellowing",
            "jaundice.skin_yellowing", "jaundice.observation_conditions",
            "jaundice.dark_urine", "jaundice.pale_stool", "jaundice.itching",
            "jaundice.pain_nrs", "jaundice.current_medicines",
            "jaundice.latest_total_bilirubin", "jaundice.latest_direct_bilirubin",
            "jaundice.prior_imaging", "jaundice.accessibility_need",
            "jaundice.patient_concern", "jaundice.expected_help",
        } <= minimum)


if __name__ == "__main__":
    unittest.main()
