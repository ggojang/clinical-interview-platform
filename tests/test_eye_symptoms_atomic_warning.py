from __future__ import annotations

import unittest

from compiler.build_package import compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import EYE_SYMPTOMS_PACKAGE


class EyeSymptomsAtomicWarningTests(unittest.TestCase):
    def test_halo_warning_is_split_into_atomic_facts(self):
        package = compile_package(profile="eye_symptoms")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        expected = {
            "eye.halos_around_lights",
            "eye.severe_headache_with_eye_symptoms",
            "eye.nausea_with_eye_symptoms",
            "eye.vomiting_with_eye_symptoms",
        }
        self.assertTrue(expected <= set(facts))
        self.assertNotIn("eye.halos_headache_nausea_or_vomiting", facts)
        self.assertTrue(all(facts[fact_id]["value_type"] == "boolean" for fact_id in expected))

    def test_halo_rule_requires_halo_and_one_associated_finding(self):
        package = compile_package(profile="eye_symptoms")
        rules = {rule["id"]: rule for rule in package["rule_graph"]["rules"]}
        condition = rules["rule.eye-symptoms.safety.halos-systemic-warning"]["when"]
        self.assertEqual("eye.halos_around_lights", condition["all"][0]["fact"])
        self.assertEqual(
            {
                "eye.severe_headache_with_eye_symptoms",
                "eye.nausea_with_eye_symptoms",
                "eye.vomiting_with_eye_symptoms",
            },
            {item["fact"] for item in condition["all"][1]["any"]},
        )

    def test_atomic_associated_findings_use_verified_snomed_related_mappings(self):
        package = compile_package(profile="eye_symptoms")
        questions = {
            node["collects"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate" and "collects" in node
        }
        expected_codes = {
            "eye.severe_headache_with_eye_symptoms": "25064002",
            "eye.nausea_with_eye_symptoms": "422587007",
            "eye.vomiting_with_eye_symptoms": "422400008",
        }
        for fact_id, code in expected_codes.items():
            self.assertEqual(
                [{
                    "system": "http://snomed.info/sct",
                    "code": code,
                    "mapping_relation": "related",
                }],
                questions[fact_id]["semantic_binding"]["standard_mappings"],
            )
            self.assertNotIn(
                "fhir_standard_item_codes", questions[fact_id]["semantic_binding"]
            )
        self.assertNotIn("semantic_binding", questions["eye.halos_around_lights"])

    def test_atomic_boolean_answers_are_value_set_bound(self):
        package = compile_package(profile="eye_symptoms")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        for fact_id in {
            "eye.halos_around_lights",
            "eye.severe_headache_with_eye_symptoms",
            "eye.nausea_with_eye_symptoms",
            "eye.vomiting_with_eye_symptoms",
        }:
            binding = facts[fact_id]["answer_semantic_binding"]
            self.assertTrue(binding["answer_value_set"].endswith("/a-sct-yes-no"))
            self.assertEqual("valueCoding", binding["fhir_response_type"])

    def test_atomic_warning_facts_reach_clinician_handoff_minimum(self):
        package = compile_package(profile="eye_symptoms")
        minimum = set(
            package["interview_completion_policy"]["required_facts"]["always"]
        )
        self.assertTrue(
            {
                "eye.halos_around_lights",
                "eye.severe_headache_with_eye_symptoms",
                "eye.nausea_with_eye_symptoms",
                "eye.vomiting_with_eye_symptoms",
            }
            <= minimum
        )

    def test_halo_cluster_positive_and_negative_simulations_pass(self):
        report = run_evaluation(EYE_SYMPTOMS_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        by_id = {result["case_id"]: result for result in report["results"]}
        self.assertEqual("routine", by_id["EYE-HALOS-ONLY-NO-CLUSTER"]["safety_level"])
        self.assertNotIn(
            "rule.eye-symptoms.safety.halos-systemic-warning",
            by_id["EYE-HALOS-ONLY-NO-CLUSTER"]["triggered_rules"],
        )
        self.assertEqual("emergency", by_id["EYE-HALOS-VOMITING-CLUSTER"]["safety_level"])
        self.assertIn(
            "rule.eye-symptoms.safety.halos-systemic-warning",
            by_id["EYE-HALOS-VOMITING-CLUSTER"]["triggered_rules"],
        )


if __name__ == "__main__":
    unittest.main()
