from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import POST_DISCHARGE_FOLLOW_UP_PACKAGE


ROOT = Path(__file__).resolve().parents[1]


class PostDischargeAtomicHandoffTests(unittest.TestCase):
    def test_legacy_wound_device_composite_is_replaced_by_atomic_facts(self):
        package = compile_package(profile="post_discharge_follow_up")
        facts = {
            node["id"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertNotIn("post_discharge.wound_or_device_plan", facts)
        expected = {
            "post_discharge.wound_care_task_required",
            "post_discharge.wound_care_task_description",
            "post_discharge.wound_care_instructions_available",
            "post_discharge.wound_care_skill_difficulty",
            "post_discharge.wound_care_help_contact_known",
            "post_discharge.home_medical_device_or_equipment_required",
            "post_discharge.home_medical_device_or_equipment_type",
            "post_discharge.home_medical_device_or_equipment_received",
            "post_discharge.home_medical_device_or_equipment_use_training_received",
            "post_discharge.home_medical_device_or_equipment_use_difficulty",
            "post_discharge.home_medical_device_or_equipment_help_contact_known",
        }
        self.assertTrue(expected <= facts.keys())
        questions = {
            node["collects"]: node
            for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "QuestionTemplate" and node.get("collects") in expected
        }
        self.assertEqual(expected, questions.keys())

    def test_wound_and_equipment_followup_require_distinct_atomic_branches(self):
        package = compile_package(profile="post_discharge_follow_up")
        conditionals = {
            item["reason"]: item
            for item in package["interview_completion_policy"]["conditional_required_facts"]
        }
        wound = conditionals["post_discharge_wound_care_handoff"]
        equipment = conditionals["post_discharge_home_equipment_handoff"]
        use = conditionals["post_discharge_home_equipment_use_handoff"]
        self.assertEqual(
            "post_discharge.wound_care_task_required", wound["when"]["fact"]
        )
        self.assertNotIn(
            "post_discharge.home_medical_device_or_equipment_type",
            wound["required_facts"],
        )
        self.assertEqual(
            "post_discharge.home_medical_device_or_equipment_required",
            equipment["when"]["fact"],
        )
        self.assertEqual(
            "post_discharge.home_medical_device_or_equipment_received",
            use["when"]["fact"],
        )

    def test_stom_outage_does_not_create_unverified_exact_mapping(self):
        mapping = json.loads(
            (ROOT / "mappings/terminology/snomed-mrcm-post-discharge-follow-up.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(
            ["post_discharge.wound_or_device_plan"],
            mapping["atomic_refactoring"]["retired_composite_facts"],
        )
        self.assertEqual(0, mapping["question_mapping"]["exact_standard_question_count"])
        self.assertIn("connection_refused", mapping["validation"]["result"])

    def test_new_synthetic_handoff_cases_pass(self):
        report = run_evaluation(POST_DISCHARGE_FOLLOW_UP_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        by_id = {item["case_id"]: item for item in report["results"]}
        self.assertIn("POST-DISCHARGE-WOUND-CARE-SKILL-GAP", by_id)
        self.assertIn("POST-DISCHARGE-HOME-EQUIPMENT-NOT-RECEIVED", by_id)


if __name__ == "__main__":
    unittest.main()
