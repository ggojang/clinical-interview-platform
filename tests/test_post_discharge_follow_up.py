from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import CompilationError, compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import POST_DISCHARGE_FOLLOW_UP_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class PostDischargeFollowUpPackageTests(unittest.TestCase):
    def test_package_is_complete_and_research_only(self):
        package = compile_package(profile="post_discharge_follow_up")
        facts = {
            node["id"]
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(58, len(facts))
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(8, package["coverage"]["total_safety_rules"])
        self.assertEqual(8, package["coverage"]["safety_rules_with_simulations"])
        self.assertEqual([], package["coverage"]["uncovered_safety_rules"])
        self.assertGreaterEqual(
            package["coverage"]["data_absent_reason_simulations"], 1
        )
        self.assertFalse(package["usage_policy"]["production_allowed"])
        with self.assertRaises(CompilationError):
            compile_package(profile="post_discharge_follow_up", production=True)

    def test_questions_are_atomic_and_conditional_details_are_not_always_required(self):
        package = compile_package(profile="post_discharge_follow_up")
        questions = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate"
        }
        self.assertIn(
            "question.post-discharge-follow-up.emergency-instruction-received",
            questions,
        )
        self.assertIn(
            "question.post-discharge-follow-up.instructed-warning-present",
            questions,
        )
        policy = package["interview_completion_policy"]
        always = set(policy["required_facts"]["always"])
        self.assertNotIn("post_discharge.service", always)
        self.assertNotIn("post_discharge.major_treatment_or_procedure", always)
        self.assertNotIn("post_discharge.current_pain_present", always)
        conditionals = {
            item["reason"]: item for item in policy["conditional_required_facts"]
        }
        self.assertEqual(
            conditionals["incomplete_discharge_document_context"]["when"]["in"],
            ["available_partial", "not_available", "unreadable", "unknown"],
        )
        self.assertIn(
            "post_discharge.current_pain_present",
            conditionals["new_or_worsened_post_discharge_symptom"][
                "required_facts"
            ],
        )

    def test_record_title_is_not_misrepresented_as_an_exact_question_code(self):
        mapping = json.loads(
            (
                ROOT
                / "mappings/terminology/snomed-mrcm-post-discharge-follow-up.json"
            ).read_text(encoding="utf-8")
        )
        title = mapping["verified_loinc_record_titles"][0]
        self.assertEqual("11544-4", title["code"])
        self.assertEqual("record_title_not_question_exact", title["relation"])
        self.assertEqual(
            0, mapping["question_mapping"]["exact_standard_question_count"]
        )
        self.assertFalse(
            mapping["question_mapping"]["compound_question_exact_mapping_allowed"]
        )
        self.assertFalse(mapping["validation"]["question_equivalence_inferred"])

    def test_clinician_minimum_contains_transition_handoff_essentials(self):
        package = compile_package(profile="post_discharge_follow_up")
        context = json.loads(
            (ROOT / package["clinician_submission_context"]["resource_ref"])
            .read_text(encoding="utf-8")
        )
        minimum = set(
            context["completion"]
            ["clinician_rfe_minimum"]["additional_required_facts_by_rfe"]
            ["rfe.post_discharge_follow_up"]
        )
        self.assertTrue(
            {
                "post_discharge.discharge_summary_available",
                "post_discharge.actual_current_medicines",
                "post_discharge.medicine_discrepancy",
                "post_discharge.pending_tests_present",
                "post_discharge.follow_up_appointment_present",
                "post_discharge.caregiver_support",
                "post_discharge.plan_understanding",
                "post_discharge.patient_concern",
            }
            <= minimum
        )

    def test_all_post_discharge_simulations_pass_without_date_repetition(self):
        report = run_evaluation(POST_DISCHARGE_FOLLOW_UP_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        self.assertEqual(14, report["case_count"])
        routine = next(
            item
            for item in report["results"]
            if item["case_id"] == "POST-DISCHARGE-ROUTINE-DOCUMENT-CONFIRMED"
        )
        self.assertEqual(
            1, routine["selected_facts"].count("post_discharge.discharge_date")
        )
        self.assertLessEqual(routine["turns"], 38)


if __name__ == "__main__":
    unittest.main()
