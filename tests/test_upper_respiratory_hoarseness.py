import json
from pathlib import Path
import unittest

from runtime.simulator import PatientSimulator
from evaluation.run_evaluation import run as run_evaluation


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class UpperRespiratoryHoarsenessTests(unittest.TestCase):
    def test_simulator_formats_shared_smoking_quantities_for_runtime_parser(self):
        simulator = PatientSimulator({
            "simulation_language": "en",
            "hidden_state": {
                "patient.smoking.duration_years": {
                    "value": {"amount": 25, "unit": "a"},
                },
                "patient.smoking.cigarettes_per_day": {
                    "value": {"amount": 10, "unit": "{cigarette}/d"},
                },
            },
        })
        self.assertEqual(
            simulator.answer("patient.smoking.duration_years"), "25 years."
        )
        self.assertEqual(
            simulator.answer("patient.smoking.cigarettes_per_day"),
            "10 cigarettes per day.",
        )

    def test_voice_branch_is_atomic_and_source_backed(self):
        fragment = load("knowledge/generated/upper-respiratory/upper-respiratory-symptoms.json")
        facts = {item["fact"]["id"]: item for item in fragment["entries"]}
        self.assertNotIn("symptom.neck_swelling_trismus_or_muffled_voice", facts)
        self.assertNotIn("symptom.persistent_mouth_ulcer_or_neck_lump", facts)
        self.assertNotIn("patient.smoking_or_inhaled_irritant", facts)
        self.assertNotIn("exposure.tobacco_nicotine_current", facts)
        self.assertNotIn("exposure.tobacco_nicotine_product", facts)
        for fact_id in (
            "symptom.unilateral_neck_swelling",
            "symptom.trismus",
            "symptom.muffled_voice",
            "symptom.hoarseness_persistent_four_weeks",
            "symptom.hoarseness_progressive",
            "symptom.persistent_mouth_ulcer_three_weeks",
            "symptom.persistent_neck_lump_three_weeks",
            "patient.smoking.status",
            "patient.smoking.product_types",
            "patient.smoking.cigarettes_per_day",
            "patient.smoking.duration_years",
            "exposure.inhaled_irritant_type",
            "exposure.inhaled_irritant_duration",
            "upper_respiratory.prior_laryngoscopy_and_results",
        ):
            self.assertIn(fact_id, facts)

        source_ids = set(fragment["provenance"]["source_refs"])
        self.assertIn("source.aao-hns.hoarseness-dysphonia.2018", source_ids)
        self.assertIn("source.nice.ng12.laryngeal-cancer.2026", source_ids)
        self.assertIn("source.stom.snomed-hoarse.20260801", source_ids)
        self.assertEqual(
            facts["exposure.inhaled_irritant_duration"]["fact"]["unit"], "a"
        )

    def test_persistent_hoarseness_has_time_sensitive_handoff_regression(self):
        rules = load("rules/primary-care-upper-respiratory-symptoms.json")
        rule_ids = {item["id"] for item in rules["rules"]}
        self.assertIn(
            "rule.upper-respiratory.safety.persistent-hoarseness-45-plus",
            rule_ids,
        )
        case = load(
            "simulation/patients/upper-respiratory/UPPER-PERSISTENT-HOARSENESS-HANDOFF-001.json"
        )
        self.assertEqual(case["expected"]["expected_safety_level"], "urgent")
        self.assertEqual(case["expected"]["expected_safety_action"], "human_handoff")
        self.assertIn(
            "diagnosis.laryngeal_cancer",
            case["expected"]["forbidden_assertions"],
        )

    def test_remote_routine_hoarseness_completes_without_repeated_fact(self):
        report = run_evaluation(
            ROOT
            / "packages/generated/primary-care-upper-respiratory-symptoms-0.1.0.json"
        )
        case = next(
            item
            for item in report["results"]
            if item["case_id"]
            == "UPPER-HOARSENESS-REMOTE-CONFLICT-DATA-ABSENT-001"
        )
        self.assertTrue(case["passed"], case["failures"])
        self.assertIsNotNone(case["clinician_handoff"])
        self.assertEqual(
            case["selected_facts"].count("patient.smoking.duration_years"), 1
        )
        self.assertEqual(
            case["selected_facts"].count("patient.smoking.cigarettes_per_day"),
            1,
        )
        self.assertEqual(
            case["selected_facts"].count("exposure.inhaled_irritant_duration"),
            1,
        )


if __name__ == "__main__":
    unittest.main()
