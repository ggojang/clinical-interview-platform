from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import CompilationError, compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import TOBACCO_NICOTINE_COUNSELLING_PACKAGE
from runtime.session import InterviewSession


ROOT = Path(__file__).resolve().parents[1]


class TobaccoNicotineCounsellingPackageTests(unittest.TestCase):
    def test_package_is_complete_draft_and_safety_covered(self):
        package = compile_package(profile="tobacco_nicotine_counselling")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(65, len(facts))
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(4, package["coverage"]["total_safety_rules"])
        self.assertEqual(4, package["coverage"]["safety_rules_with_simulations"])
        self.assertEqual([], package["coverage"]["uncovered_safety_rules"])
        self.assertGreaterEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        self.assertFalse(package["usage_policy"]["production_allowed"])
        self.assertEqual("draft", package["usage_policy"]["lifecycle_status"])
        self.assertEqual("limited", package["usage_policy"]["clinical_use_status"])
        with self.assertRaises(CompilationError):
            compile_package(profile="tobacco_nicotine_counselling", production=True)

    def test_product_details_are_atomic_and_conditionally_required(self):
        package = compile_package(profile="tobacco_nicotine_counselling")
        policy = package["interview_completion_policy"]
        always = set(policy["required_facts"]["always"])
        self.assertIn("tobacco.overall_product_use_status", always)
        self.assertNotIn("patient.smoking.cigarettes_per_day", always)
        self.assertNotIn("tobacco.electronic_cigarette_amount", always)
        product = next(
            item for item in policy["conditional_required_facts"]
            if item.get("selector_fact") == "patient.smoking.product_types"
        )
        self.assertEqual(
            ["patient.smoking.cigarettes_per_day", "patient.smoking.duration_years"],
            product["cases"]["combustible_cigarette"],
        )
        self.assertEqual(
            [
                "tobacco.electronic_cigarette_status",
                "tobacco.electronic_cigarette_nicotine_content",
                "tobacco.electronic_cigarette_amount",
                "tobacco.electronic_cigarette_duration",
            ],
            product["cases"]["electronic_cigarette"],
        )
        self.assertEqual(
            [
                "tobacco.nicotine_pouch_status",
                "tobacco.nicotine_pouch_product_name",
                "tobacco.nicotine_pouch_strength",
                "tobacco.nicotine_pouch_frequency",
                "tobacco.nicotine_pouch_amount_per_day",
                "tobacco.nicotine_pouch_duration",
            ],
            product["cases"]["nicotine_pouch"],
        )
        self.assertTrue(product["cases"]["cigar_or_pipe"])
        self.assertTrue(product["cases"]["smokeless_tobacco"])
        self.assertTrue(product["cases"]["other"])

    def test_stom_verified_question_and_answer_list_provenance(self):
        mapping = json.loads(
            (ROOT / "mappings/terminology/snomed-mrcm-tobacco-nicotine-counselling.json")
            .read_text(encoding="utf-8")
        )
        questions = {item["fact_id"]: item for item in mapping["verified_loinc_questions"]}
        self.assertEqual("72166-2", questions["patient.smoking.status"]["code"])
        self.assertEqual("105045-9", questions["tobacco.electronic_cigarette_status"]["code"])
        self.assertEqual(
            {"LL2201-3", "LL6587-1"},
            {item["id"] for item in mapping["verified_official_answer_lists"]},
        )
        self.assertTrue(all(item["preserve_original"] for item in mapping["verified_official_answer_lists"]))
        self.assertFalse(mapping["atomicity"]["compound_exact_mapping_allowed"])
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        concepts = {
            item["code"]: item for item in mapping["verified_snomed_product_concepts"]
        }
        self.assertEqual("related", concepts["584011000052107"]["relation"])
        self.assertTrue(mapping["terminology"]["snomed_ct_version"].endswith("/20260801"))

        package = compile_package(profile="tobacco_nicotine_counselling")
        questions = {
            node["collects"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate"
        }
        duration_codes = {
            (item["system"], item["code"], item["mapping_relation"])
            for item in questions["patient.smoking.duration_years"]
            ["semantic_binding"]["standard_mappings"]
        }
        self.assertIn(("http://loinc.org", "67741-9", "equivalent"), duration_codes)

    def test_clinician_minimum_has_product_exposure_and_goal_context(self):
        package = compile_package(profile="tobacco_nicotine_counselling")
        context = json.loads(
            (ROOT / package["clinician_submission_context"]["resource_ref"])
            .read_text(encoding="utf-8")
        )
        minimum = set(
            context["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.tobacco_nicotine_counselling"]
        )
        self.assertTrue({
            "tobacco.overall_product_use_status", "patient.smoking.status",
            "patient.smoking.product_types",
            "tobacco.home_secondhand_exposure", "tobacco.work_secondhand_exposure",
            "tobacco.pregnancy_or_postpartum_status", "tobacco.patient_concern",
            "tobacco.expected_help",
        } <= minimum)

    def test_open_choice_product_status_preserves_unlisted_free_text(self):
        session = InterviewSession(
            "tobacco-product-status-free-text",
            package_path=TOBACCO_NICOTINE_COUNSELLING_PACKAGE,
        )
        session.last_question_fact = "tobacco.nicotine_pouch_status"
        session.asked = ["tobacco.nicotine_pouch_status"]

        state = session.process("필요할 때만 간헐적으로 사용")

        self.assertEqual(
            session.memory.value("tobacco.nicotine_pouch_status"),
            "필요할 때만 간헐적으로 사용",
        )
        self.assertIsNone(state["answer_clarification"])
        self.assertNotEqual(
            (state.get("selected_question") or {}).get("fact_id"),
            "tobacco.nicotine_pouch_status",
        )

    def test_all_tobacco_simulations_pass(self):
        report = run_evaluation(TOBACCO_NICOTINE_COUNSELLING_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        self.assertEqual(10, report["case_count"])
        dual = next(
            item for item in report["results"]
            if item["case_id"] == "TOBACCO-DUAL-USE-REMOTE-FIRST-VISIT"
        )
        self.assertIn("patient.smoking.cigarettes_per_day", dual["selected_facts"])
        self.assertIn("tobacco.electronic_cigarette_amount", dual["selected_facts"])
        pouch = next(
            item for item in report["results"]
            if item["case_id"] == "TOBACCO-NICOTINE-POUCH-NONSMOKER"
        )
        self.assertIn("tobacco.nicotine_pouch_strength", pouch["selected_facts"])
        self.assertIn("tobacco.nicotine_pouch_amount_per_day", pouch["selected_facts"])
        self.assertIn("tobacco.craving_or_withdrawal", pouch["selected_facts"])
        self.assertIn("tobacco.readiness", pouch["selected_facts"])


if __name__ == "__main__":
    unittest.main()
