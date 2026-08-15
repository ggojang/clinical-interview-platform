from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import ALLERGY_CONCERN_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class AllergyFollowupAtomicTests(unittest.TestCase):
    def test_composite_followup_fact_is_replaced_by_atomic_facts(self):
        package = compile_package(profile="allergy_concern")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertNotIn("allergy.specialist_testing_and_emergency_plan", facts)
        expected = {
            "allergy.adrenaline_autoinjector_prescribed",
            "allergy.anaphylaxis_follow_up_context",
            "allergy.adrenaline_autoinjector_currently_available",
            "allergy.adrenaline_autoinjector_count_available",
            "allergy.adrenaline_autoinjector_in_date_confirmed",
            "allergy.adrenaline_autoinjector_earliest_expiry_date",
            "allergy.adrenaline_autoinjector_device_name_or_brand",
            "allergy.adrenaline_autoinjector_training_received",
            "allergy.adrenaline_autoinjector_technique_confidence_or_gap",
            "allergy.written_emergency_action_plan_available",
            "allergy.specialist_allergy_referral_status",
            "allergy.specialist_allergy_testing_result",
        }
        self.assertTrue(expected <= set(facts))
        self.assertEqual(
            facts["allergy.adrenaline_autoinjector_count_available"]["value_type"],
            "integer",
        )

    def test_contextual_followup_questions_remain_local(self):
        package = compile_package(profile="allergy_concern")
        questions = {
            node["collects"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate" and "collects" in node
        }
        for fact_id in (
            "allergy.adrenaline_autoinjector_currently_available",
            "allergy.adrenaline_autoinjector_count_available",
            "allergy.adrenaline_autoinjector_in_date_confirmed",
            "allergy.specialist_allergy_referral_status",
        ):
            self.assertNotIn("semantic_binding", questions[fact_id])
        mapping = json.loads(
            (ROOT / "mappings/terminology/snomed-mrcm-allergy-concern.json")
            .read_text(encoding="utf-8")
        )
        self.assertFalse(
            mapping["atomic_refactoring"]
            ["exact_mapping_for_new_contextual_questions"]
        )
        self.assertEqual(
            {item["relation"] for item in mapping["related_concept_candidates"]},
            {"related_not_exact"},
        )

    def test_clinician_minimum_keeps_branch_facts_conditional(self):
        package = compile_package(profile="allergy_concern")
        context = json.loads(
            (ROOT / package["clinician_submission_context"]["resource_ref"])
            .read_text(encoding="utf-8")
        )
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.allergy_concern"]
        )
        self.assertIn("allergy.suspected_trigger_and_latency", minimum)
        self.assertNotIn("allergy.drug_generic_name", minimum)
        self.assertNotIn(
            "allergy.adrenaline_autoinjector_count_available", minimum
        )

    def test_autoinjector_followup_simulations_pass(self):
        report = run_evaluation(ALLERGY_CONCERN_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        results = {item["case_id"]: item for item in report["results"]}
        prepared = results["ALLERGY-AAI-PREPAREDNESS-FOLLOWUP"]
        gap = results["ALLERGY-AAI-EXPIRY-TRAINING-GAPS"]
        self.assertEqual(prepared["safety_level"], "routine")
        self.assertTrue(prepared["clinician_handoff"])
        self.assertEqual(gap["safety_level"], "routine")
        self.assertTrue(gap["clinician_handoff"])
        self.assertLessEqual(max(prepared["turns"], gap["turns"]), 72)


if __name__ == "__main__":
    unittest.main()
