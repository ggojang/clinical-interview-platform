from __future__ import annotations

import unittest

from compiler.build_package import CompilationError, compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import TEST_RESULT_FOLLOW_UP_PACKAGE
from runtime.session import InterviewSession


class TestResultFollowUpPackageTests(unittest.TestCase):
    def test_package_is_complete_and_research_only(self):
        package = compile_package(profile="test_result_follow_up")
        facts = {
            node["id"]
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 30)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 4)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 4)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        self.assertFalse(package["usage_policy"]["production_allowed"])
        with self.assertRaises(CompilationError):
            compile_package(profile="test_result_follow_up", production=True)

    def test_completion_distinguishes_visit_goal_and_upload_policy(self):
        policy = compile_package(
            profile="test_result_follow_up"
        )["interview_completion_policy"]
        goal = policy["conditional_required_facts"][0]
        self.assertEqual(goal["selector_fact"], "encounter.result_follow_up.goal")
        self.assertEqual(
            set(goal["cases"]),
            {
                "institution_result_check",
                "interpretation_request",
                "both",
                "unknown",
            },
        )
        self.assertEqual(
            goal["cases"]["institution_result_check"],
            ["result.additional_comment"],
        )
        self.assertEqual(
            policy["upload_policy"]["institution_result_check"],
            "never_request",
        )
        self.assertEqual(
            policy["upload_policy"]["interpretation_request"],
            "request_once_only_if_not_already_available",
        )
        self.assertEqual(
            policy["upload_policy"]["unavailable_or_declined"],
            "preserve_dataAbsentReason_and_do_not_repeat",
        )

    def test_report_status_uses_diagnostic_report_required_binding(self):
        package = compile_package(profile="test_result_follow_up")
        status = next(
            node
            for node in package["knowledge_graph"]["nodes"]
            if node["id"] == "result.report.status"
        )
        binding = status["answer_semantic_binding"]
        self.assertEqual(
            binding["answer_value_set"],
            "http://hl7.org/fhir/ValueSet/diagnostic-report-status|4.0.1",
        )
        self.assertEqual(
            binding["fhir_element_binding"]["element_path"],
            "DiagnosticReport.status",
        )
        self.assertEqual(binding["fhir_element_binding"]["strength"], "required")
        self.assertNotIn("fhir_element_binding_conflict", binding)
        self.assertEqual(
            set(binding["fhir_bound_answer_mappings"]),
            {
                "registered",
                "partial",
                "preliminary",
                "final",
                "amended",
                "corrected",
                "appended",
                "cancelled",
                "entered-in-error",
                "unknown",
            },
        )

    def test_textual_fhir_shapes_are_accepted_without_question_repetition(self):
        session = InterviewSession(
            "result-textual-shapes",
            package_path=TEST_RESULT_FOLLOW_UP_PACKAGE,
        )
        for fact_id, answer in (
            ("result.test.name", "CBC"),
            ("result.test.performed_at", "2026-07-24"),
            ("result.report.issued_at", "2026-07-24 09:30"),
            ("result.performing_organization", "합성 의료기관"),
        ):
            with self.subTest(fact_id=fact_id):
                session.last_question_fact = fact_id
                session.process(answer)
                self.assertEqual(session.memory.state(fact_id), "known")
                self.assertEqual(session.memory.facts[fact_id]["value"], answer)

    def test_all_synthetic_result_follow_up_simulations_pass(self):
        report = run_evaluation(TEST_RESULT_FOLLOW_UP_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        self.assertEqual(report["case_count"], 9)


if __name__ == "__main__":
    unittest.main()
