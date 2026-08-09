from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import ANEMIA_CONCERN_FOLLOW_UP_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class AnemiaB12NeurologicTests(unittest.TestCase):
    def test_b12_neurologic_handoff_uses_atomic_facts(self):
        package = compile_package(profile="anemia_concern_follow_up")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        expected = {
            "anemia.b12_paresthesia_or_numbness",
            "anemia.b12_gait_change",
            "anemia.b12_balance_impairment",
            "anemia.b12_falls",
            "anemia.b12_short_term_memory_change",
            "anemia.b12_concentration_change",
            "anemia.b12_visual_change",
            "anemia.b12_glossitis",
            "anemia.b12_rapid_gait_deterioration",
        }
        self.assertTrue(expected <= set(facts))
        self.assertEqual("boolean", facts["anemia.b12_rapid_gait_deterioration"]["value_type"])

    def test_b12_branch_collects_neurologic_exposure_and_test_context(self):
        package = compile_package(profile="anemia_concern_follow_up")
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        required = set(conditional["cases"]["b12_folate_or_macrocytic"])
        self.assertTrue(
            {
                "anemia.b12_paresthesia_or_numbness",
                "anemia.b12_gait_change",
                "anemia.b12_balance_impairment",
                "anemia.b12_risk_medicines",
                "anemia.nitrous_oxide_use",
                "anemia.b12_supplement_before_testing",
                "anemia.autoimmune_gastritis_workup",
            }
            <= required
        )

    def test_stom_verification_is_representational_not_diagnostic(self):
        mapping = json.loads(
            (ROOT / "mappings/terminology/snomed-mrcm-anemia-concern-follow-up.json").read_text(
                encoding="utf-8"
            )
        )
        codes = {concept["code"] for concept in mapping["focus_concepts"]}
        self.assertTrue(
            {"91019004", "22325002", "387603000", "247592009", "45534005", "1268384001"}
            <= codes
        )
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_progressive_gait_case_escalates_without_diagnosis(self):
        report = run_evaluation(ANEMIA_CONCERN_FOLLOW_UP_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        by_id = {result["case_id"]: result for result in report["results"]}
        case = by_id["ANEMIA-B12-RAPID-GAIT-DETERIORATION"]
        self.assertEqual("urgent", case["safety_level"])
        self.assertIn(
            "rule.anemia-concern-follow-up.safety.b12-rapid-gait-deterioration",
            case["triggered_rules"],
        )

    def test_b12_context_reaches_clinician_handoff(self):
        report = run_evaluation(ANEMIA_CONCERN_FOLLOW_UP_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        by_id = {result["case_id"]: result for result in report["results"]}
        case = by_id["ANEMIA-B12-NEUROLOGIC-HANDOFF"]
        self.assertIsNotNone(case["clinician_handoff"])
        collected = {
            entry["fact_id"]
            for section in case["clinician_handoff"]["sections"]
            for entry in section["entries"]
            if entry["status"] == "known"
        }
        self.assertTrue(
            {
                "anemia.b12_paresthesia_or_numbness",
                "anemia.b12_gait_change",
                "anemia.b12_balance_impairment",
                "anemia.b12_risk_medicines",
                "anemia.b12_supplement_before_testing",
            }
            <= collected
        )


if __name__ == "__main__":
    unittest.main()
