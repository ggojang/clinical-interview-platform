from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import NECK_PAIN_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class NeckPainPackageTests(unittest.TestCase):
    def test_cord_and_elimination_warnings_are_atomic_facts(self):
        package = compile_package(profile="neck_pain")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        expected = {
            "neck.gait_or_balance_change",
            "neck.hand_clumsiness",
            "neck.progressive_limb_weakness",
            "neck.new_bladder_function_change",
            "neck.new_bowel_function_change",
            "neck.new_saddle_sensory_change",
            "neck.electric_shock_sensation",
        }
        self.assertTrue(expected <= set(facts))
        self.assertNotIn(
            "neck.gait_disturbance_clumsy_hands_or_progressive_weakness", facts
        )
        self.assertNotIn("neck.new_bladder_bowel_or_saddle_change", facts)
        self.assertTrue(all(facts[fact_id]["value_type"] == "boolean" for fact_id in expected))

    def test_atomic_warning_facts_feed_grouped_safety_rules(self):
        package = compile_package(profile="neck_pain")
        rules = {rule["id"]: rule for rule in package["rule_graph"]["rules"]}
        cord = rules["rule.neck-pain.safety.cord-warning"]
        elimination = rules["rule.neck-pain.safety.bladder-bowel-saddle-warning"]
        self.assertEqual(
            {
                "neck.gait_or_balance_change",
                "neck.hand_clumsiness",
                "neck.progressive_limb_weakness",
            },
            {condition["fact"] for condition in cord["when"]["any"]},
        )
        self.assertEqual(
            {
                "neck.new_bladder_function_change",
                "neck.new_bowel_function_change",
                "neck.new_saddle_sensory_change",
            },
            {condition["fact"] for condition in elimination["when"]["any"]},
        )
        self.assertTrue(
            all(
                rule["refresh"]["last_assessed_at"] == "2026-08-05"
                for rule in rules.values()
                if rule["id"].startswith("rule.neck-pain.safety.")
            )
        )

    def test_current_pain_is_atomic_loinc_and_worst_pain_stays_local(self):
        package = compile_package(profile="neck_pain")
        questions = {
            node["collects"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate" and "collects" in node
        }
        current = questions["neck.current_pain_nrs"]["semantic_binding"]
        self.assertEqual(
            [{"system": "http://loinc.org", "code": "72514-3"}],
            current["fhir_standard_item_codes"],
        )
        self.assertNotIn("semantic_binding", questions["neck.worst_pain_nrs"])

    def test_shared_pain_frequency_and_accessibility_reach_handoff(self):
        package = compile_package(profile="neck_pain")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertIn("pain.frequency", facts)
        self.assertIn("answer_value_set", facts["pain.frequency"]["answer_semantic_binding"])
        context = json.loads(
            (ROOT / package["clinician_submission_context"]["resource_ref"]).read_text(
                encoding="utf-8"
            )
        )
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.neck_pain"]
        )
        self.assertTrue(
            {
                "pain.frequency",
                "neck.current_pain_nrs",
                "neck.worst_pain_nrs",
                "neck.accessibility_or_communication_need",
                "neck.hand_clumsiness",
                "neck.gait_or_balance_change",
            }
            <= minimum
        )

    def test_new_electric_shock_and_accessibility_simulations_pass(self):
        report = run_evaluation(NECK_PAIN_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        by_id = {result["case_id"]: result for result in report["results"]}
        electric = by_id["NECK-ELECTRIC-SHOCK-WARNING"]
        self.assertEqual("urgent", electric["safety_level"])
        self.assertIn(
            "rule.neck-pain.safety.electric-shock-warning",
            electric["triggered_rules"],
        )
        accessibility = by_id["NECK-ACCESSIBILITY-CLINICIAN-HANDOFF"]
        self.assertEqual("routine", accessibility["safety_level"])


if __name__ == "__main__":
    unittest.main()
