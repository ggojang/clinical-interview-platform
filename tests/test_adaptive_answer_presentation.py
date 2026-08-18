from __future__ import annotations

import json
from pathlib import Path
import unittest

from compiler.build_package import PACKAGE_PROFILES
from runtime.adaptive_answer_presentation import (
    patient_answer_options,
    selector_fact_ids,
)
from runtime.package import ABDOMINAL_PAIN_PACKAGE
from runtime.session import InterviewSession


class AdaptiveAnswerPresentationTests(unittest.TestCase):
    def test_every_completion_selector_has_complete_patient_labels(self):
        occurrences = 0
        for config in PACKAGE_PROFILES.values():
            package = json.loads(Path(config["output"]).read_text(encoding="utf-8"))
            nodes = {
                node["id"]: node for node in package["knowledge_graph"]["nodes"]
            }
            questions = package["indexes"]["questions_by_fact"]
            policy = package["interview_completion_policy"]
            for fact_id in selector_fact_ids(policy):
                occurrences += 1
                options = patient_answer_options(
                    fact_id,
                    nodes[fact_id],
                    questions[fact_id],
                    policy,
                    package["question_answer_terminology"].get(
                        "local_answer_code_system"
                    ),
                )
                absent_values = set(
                    nodes[fact_id].get("answer_semantic_binding", {})
                    .get("data_absent_reason_mappings", {})
                )
                expected_values = [
                    value for value in nodes[fact_id].get("allowed_values", [])
                    if str(value) not in absent_values
                ]
                with self.subTest(package=package["package_id"], fact_id=fact_id):
                    self.assertEqual(
                        len(options), len(expected_values)
                    )
                    self.assertTrue(options)
                    self.assertEqual(
                        [option["input"] for option in options],
                        [str(index) for index in range(1, len(options) + 1)],
                    )
                    for option in options:
                        self.assertTrue(option["display_ko"])
                        self.assertNotEqual(
                            option["display_ko"], option["internal_value"]
                        )
                        self.assertNotIn("_", option["display_ko"])
        self.assertGreaterEqual(occurrences, 59)

    def test_abdominal_pain_selector_is_short_localized_and_coded(self):
        session = InterviewSession(
            "abdominal-presentation",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )
        question = session._question_for_fact(
            "abdominal_pain.primary_group", "presentation-regression"
        )

        self.assertEqual(question["stem_text"], "이번 복통은 어떤 상황에 가장 가깝나요?")
        self.assertEqual(len(question["answer_options"]), 10)
        self.assertEqual(
            question["answer_options"][1]["display_ko"],
            "윗배·식사 관련 또는 등으로 퍼짐",
        )
        self.assertEqual(
            question["answer_options"][1]["coding"]["code"],
            "abdominal_pain.primary_group--upper_meal_or_back",
        )
        self.assertEqual(
            question["answer_options"][1]["coding"]["display"],
            "윗배·식사 관련 또는 등으로 퍼짐",
        )
        self.assertEqual(
            [(item["input"], item["dataAbsentReason"])
             for item in question["data_absent_actions"]],
            [("11", "asked-unknown"), ("12", "asked-declined")],
        )

    def test_selector_number_resolves_before_global_absence_shortcuts(self):
        session = InterviewSession(
            "abdominal-selector-input",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )
        session.last_question_fact = "abdominal_pain.primary_group"
        session.asked = ["abdominal_pain.primary_group"]

        session.process("3")

        self.assertEqual(
            session.memory.value("abdominal_pain.primary_group"),
            "right_lower_or_localized",
        )

    def test_selector_absence_is_separate_from_clinical_options(self):
        session = InterviewSession(
            "abdominal-selector-absence",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )
        session.last_question_fact = "abdominal_pain.primary_group"
        session.asked = ["abdominal_pain.primary_group"]

        session.process("11")

        self.assertEqual(
            session.memory.facts["abdominal_pain.primary_group"]["status"],
            "unknown",
        )
        self.assertEqual(
            session.memory.facts["abdominal_pain.primary_group"]
            ["dataAbsentReason"]["code"],
            "asked-unknown",
        )

    def test_non_selector_severity_axis_is_localized_and_coded(self):
        session = InterviewSession(
            "abdominal-severity-presentation",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )

        question = session._question_for_fact(
            "symptom.abdominal_pain.severity", "presentation-regression"
        )

        self.assertEqual(
            [option["display_ko"] for option in question["answer_options"]],
            ["가벼움", "중간", "심함"],
        )
        self.assertEqual(
            question["answer_options"][1]["coding"],
            {
                "system": "http://snomed.info/sct",
                "code": "6736007",
                "display": "중간",
            },
        )
        self.assertEqual(
            [(item["input"], item["dataAbsentReason"])
             for item in question["data_absent_actions"]],
            [("4", "asked-unknown"), ("5", "asked-declined")],
        )

    def test_shared_answer_domain_uses_localized_standard_coding(self):
        eye_package = PACKAGE_PROFILES["eye_symptoms"]["output"]
        session = InterviewSession(
            "eye-composite-onset-presentation",
            package_path=eye_package,
            proactive_safety_questions=False,
        )

        question = session._question_for_fact(
            "eye.onset_and_progression", "presentation-regression"
        )

        # Onset and progression are two answer-bearing meanings. Their legacy
        # combined tokens stay free text until the Fact is atomically split.
        self.assertNotIn("answer_options", question)

    def test_non_selector_number_records_internal_value(self):
        session = InterviewSession(
            "abdominal-severity-input",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )
        session.last_question_fact = "symptom.abdominal_pain.severity"
        session.asked = ["symptom.abdominal_pain.severity"]

        session.process("2")

        self.assertEqual(
            session.memory.value("symptom.abdominal_pain.severity"), "moderate"
        )

    def test_data_absent_value_is_not_emitted_as_clinical_coding(self):
        session = InterviewSession(
            "tobacco-status-presentation",
            package_path=PACKAGE_PROFILES["tobacco_nicotine_counselling"]["output"],
            proactive_safety_questions=False,
        )
        question = session._question_for_fact(
            "tobacco.cigar_status", "presentation-regression"
        )

        self.assertNotIn(
            "unknown",
            [option["internal_value"] for option in question["answer_options"]],
        )
        self.assertIn(
            "asked-unknown",
            [action["dataAbsentReason"] for action in question["data_absent_actions"]],
        )

    def test_boolean_absence_actions_are_not_clinical_answer_options(self):
        session = InterviewSession(
            "abdominal-boolean-presentation",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )
        question = session._question_for_fact(
            "symptom.abdominal_pain.onset", "presentation-regression"
        )

        self.assertEqual(
            [option["internal_value"] for option in question["answer_options"]],
            [True, False],
        )
        self.assertEqual(
            [(item["input"], item["dataAbsentReason"])
             for item in question["data_absent_actions"]],
            [("3", "asked-unknown"), ("4", "asked-declined")],
        )

    def test_non_selector_expansion_has_audited_minimum_coverage(self):
        unique_facts: set[str] = set()
        localized_facts: set[str] = set()
        for config in PACKAGE_PROFILES.values():
            package = json.loads(Path(config["output"]).read_text(encoding="utf-8"))
            nodes = {
                node["id"]: node for node in package["knowledge_graph"]["nodes"]
                if node.get("type") == "Fact"
            }
            questions = package["indexes"]["questions_by_fact"]
            policy = package["interview_completion_policy"]
            selectors = selector_fact_ids(policy)
            for fact_id, node in nodes.items():
                if (
                    node.get("value_type") != "coded"
                    or fact_id in selectors
                    or not node.get("allowed_values")
                    or fact_id not in questions
                ):
                    continue
                unique_facts.add(fact_id)
                options = patient_answer_options(
                    fact_id, node, questions[fact_id], policy,
                    package["question_answer_terminology"].get(
                        "local_answer_code_system"
                    ),
                )
                if options:
                    localized_facts.add(fact_id)
                    for option in options:
                        self.assertNotIn("_", option["display_ko"])
                        self.assertEqual(
                            option["coding"]["display"], option["display_ko"]
                        )
        self.assertGreaterEqual(len(unique_facts), 240)
        self.assertGreaterEqual(len(localized_facts), 75)


if __name__ == "__main__":
    unittest.main()
