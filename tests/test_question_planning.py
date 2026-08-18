from __future__ import annotations

import glob
import json
import unittest
from pathlib import Path

from runtime.package import ABDOMINAL_PAIN_PACKAGE
from runtime.question_planning import internal_routing_fact_ids
from runtime.session import InterviewSession


ROOT = Path(__file__).resolve().parents[1]


class QuestionPlanningTests(unittest.TestCase):
    def test_bounded_planner_can_select_only_an_eligible_compiled_fact(self):
        observed = {}

        def planner(context, candidates):
            observed["context"] = context
            observed["candidate_ids"] = [item["fact_id"] for item in candidates]
            return "symptom.abdominal_pain.severity"

        session = InterviewSession(
            "abdominal-bounded-planner",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
            question_planner=planner,
        )
        state = session.process("아랫배 통증")
        question = state["selected_question"]

        self.assertEqual(question["fact_id"], "symptom.abdominal_pain.severity")
        self.assertEqual(question["planner"], "bounded_llm_candidate_selection")
        self.assertNotIn(
            "symptom.abdominal_pain.location", observed["candidate_ids"]
        )
        self.assertEqual(
            observed["context"]["reason_for_encounter"], "rfe.abdominal_pain"
        )

    def test_invalid_planner_choice_falls_back_to_deterministic_plan(self):
        session = InterviewSession(
            "abdominal-invalid-planner",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
            question_planner=lambda _context, _candidates: "invented.fact",
        )
        state = session.process("배가 아파요")
        self.assertEqual(
            state["selected_question"]["fact_id"],
            "symptom.abdominal_pain.location",
        )

    def test_scheduled_abdominal_history_starts_with_atomic_core_axes(self):
        session = InterviewSession(
            "abdominal-atomic-order",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )

        state = session.process("배가 아파요")
        question = state["selected_question"]
        self.assertEqual(question["fact_id"], "symptom.abdominal_pain.location")
        self.assertEqual(question["stem_text"], "통증이 가장 심한 곳은 어디인가요?")
        self.assertEqual(
            [option["display_ko"] for option in question["answer_options"]],
            [
                "윗배 중앙", "오른쪽 윗배", "왼쪽 윗배", "배꼽 주위",
                "오른쪽 아랫배", "왼쪽 아랫배", "아랫배 중앙·골반",
                "옆구리", "전반적·이동성",
            ],
        )

        state = session.process("5")
        self.assertEqual(
            state["selected_question"]["fact_id"],
            "symptom.abdominal_pain.severity",
        )
        self.assertEqual(
            state["selected_question"]["stem_text"], "복통은 어느 정도인가요?"
        )

        state = session.process("2")
        self.assertEqual(
            state["selected_question"]["fact_id"],
            "symptom.abdominal_pain.onset",
        )

    def test_observed_atomic_red_flag_combination_still_escalates(self):
        session = InterviewSession(
            "abdominal-observed-red-flag",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )
        session.process("배가 아파요")
        session.process("5")
        session.process("3")
        state = session.process("1")

        self.assertEqual(state["safety_status"]["level"], "emergency")
        self.assertEqual(state["stop_reason"], "emergency_escalation")
        self.assertIsNone(state["selected_question"])

    def test_internal_routing_selector_is_reported_but_not_patient_facing(self):
        session = InterviewSession(
            "abdominal-routing-gap",
            package_path=ABDOMINAL_PAIN_PACKAGE,
            proactive_safety_questions=False,
        )
        state = session.process("배가 아파요")
        self.assertNotEqual(
            state["selected_question"]["fact_id"], "abdominal_pain.primary_group"
        )
        self.assertIn(
            "abdominal_pain.primary_group",
            state["completion_status"]["deferred_internal_routing_facts"],
        )

    def test_no_compiled_package_opens_with_internal_routing_selector(self):
        for package_name in glob.glob(str(ROOT / "packages" / "generated" / "*.json")):
            package = json.loads(Path(package_name).read_text(encoding="utf-8"))
            internal = internal_routing_fact_ids(
                package.get("interview_completion_policy", {})
            )
            if not internal:
                continue
            with self.subTest(package=package["package_id"]):
                session = InterviewSession(
                    f"routing-{package['package_id']}",
                    package_path=package_name,
                    proactive_safety_questions=False,
                )
                state = session.process("상담을 시작하고 싶어요")
                question = state["selected_question"]
                if question is not None:
                    self.assertNotIn(question["fact_id"], internal)


if __name__ == "__main__":
    unittest.main()
