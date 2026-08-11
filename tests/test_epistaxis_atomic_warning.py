from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import EPISTAXIS_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class EpistaxisAtomicWarningTests(unittest.TestCase):
    def test_recurrent_unilateral_pattern_is_split_into_atomic_handoff_facts(self):
        package = compile_package(profile="epistaxis")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertNotIn("epistaxis.laterality_and_apparent_source", facts)
        self.assertEqual(facts["epistaxis.bleeding_start_side"]["value_type"], "coded")
        self.assertEqual(facts["epistaxis.recurrent_same_side"]["value_type"], "boolean")
        side_binding = facts["epistaxis.bleeding_start_side"]["answer_semantic_binding"]
        self.assertEqual(side_binding["answer_domain"], "laterality")
        self.assertTrue(side_binding["answer_value_set"].endswith("/a-sct-laterality"))
        self.assertEqual(side_binding["internal_value_mappings"]["right"]["code"], "24028007")

    def test_haemodynamic_warning_is_split_into_atomic_facts(self):
        package = compile_package(profile="epistaxis")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        expected = {
            "epistaxis.syncope",
            "epistaxis.dizziness_or_lightheadedness",
            "epistaxis.clouded_consciousness",
            "epistaxis.chest_pain",
            "epistaxis.dyspnea",
        }
        self.assertTrue(expected <= set(facts))
        self.assertNotIn("epistaxis.weak_faint_confused_or_shock_features", facts)
        self.assertTrue(all(facts[fact_id]["value_type"] == "boolean" for fact_id in expected))

    def test_each_atomic_warning_has_an_independent_safety_rule(self):
        package = compile_package(profile="epistaxis")
        rules = {rule["id"]: rule for rule in package["rule_graph"]["rules"]}
        expected = {
            "rule.epistaxis.safety.syncope": "epistaxis.syncope",
            "rule.epistaxis.safety.dizziness": "epistaxis.dizziness_or_lightheadedness",
            "rule.epistaxis.safety.clouded-consciousness": "epistaxis.clouded_consciousness",
            "rule.epistaxis.safety.chest-pain": "epistaxis.chest_pain",
            "rule.epistaxis.safety.dyspnea": "epistaxis.dyspnea",
        }
        for rule_id, fact_id in expected.items():
            self.assertEqual(fact_id, rules[rule_id]["when"]["fact"])

    def test_atomic_findings_use_verified_snomed_question_bindings(self):
        package = compile_package(profile="epistaxis")
        questions = {
            node["collects"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate" and "collects" in node
        }
        expected_codes = {
            "epistaxis.syncope": "271594007",
            "epistaxis.dizziness_or_lightheadedness": "404640003",
            "epistaxis.clouded_consciousness": "40917007",
            "epistaxis.chest_pain": "29857009",
            "epistaxis.dyspnea": "267036007",
        }
        for fact_id, code in expected_codes.items():
            self.assertEqual(
                [{"system": "http://snomed.info/sct", "code": code}],
                questions[fact_id]["semantic_binding"]["fhir_standard_item_codes"],
            )

    def test_atomic_warnings_reach_clinician_handoff_minimum(self):
        package = compile_package(profile="epistaxis")
        context = json.loads(
            (ROOT / package["clinician_submission_context"]["resource_ref"]).read_text(
                encoding="utf-8"
            )
        )
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.epistaxis"]
        )
        self.assertTrue(
            {
                "epistaxis.syncope",
                "epistaxis.dizziness_or_lightheadedness",
                "epistaxis.clouded_consciousness",
                "epistaxis.chest_pain",
                "epistaxis.dyspnea",
            }
            <= minimum
        )

    def test_atomic_dizziness_handoff_simulation_passes(self):
        report = run_evaluation(EPISTAXIS_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        by_id = {result["case_id"]: result for result in report["results"]}
        case = by_id["EPISTAXIS-ATOMIC-DIZZINESS-HANDOFF"]
        self.assertEqual("urgent", case["safety_level"])
        self.assertIn("rule.epistaxis.safety.dizziness", case["triggered_rules"])

    def test_recurrent_unilateral_handoff_simulation_passes_without_overtriage(self):
        report = run_evaluation(EPISTAXIS_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        by_id = {result["case_id"]: result for result in report["results"]}
        case = by_id["EPISTAXIS-RECURRENT-UNILATERAL-HANDOFF"]
        self.assertEqual("routine", case["safety_level"])
        self.assertIsNotNone(case["clinician_handoff"])


if __name__ == "__main__":
    unittest.main()
