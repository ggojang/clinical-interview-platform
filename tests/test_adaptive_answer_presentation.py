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
                with self.subTest(package=package["package_id"], fact_id=fact_id):
                    self.assertEqual(
                        len(options), len(nodes[fact_id].get("allowed_values", []))
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


if __name__ == "__main__":
    unittest.main()
