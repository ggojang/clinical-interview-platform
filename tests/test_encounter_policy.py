from datetime import date, timedelta
import json
from pathlib import Path
import unittest

from runtime.encounter_policy import (
    classify_result_follow_up_goal,
    context_review_due,
    result_follow_up_action,
)


class EncounterPolicyTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_institution_result_check_does_not_request_upload(self):
        goal = classify_result_follow_up_goal("병원에서 검사 결과 확인하러 왔어요")
        self.assertEqual(goal, "institution_result_check")
        self.assertEqual(
            result_follow_up_action(goal), "ask_additional_request_then_complete"
        )

    def test_interpretation_requests_result_content_only_once(self):
        goal = classify_result_follow_up_goal("이 검사결과를 판독하고 설명해 주세요")
        self.assertEqual(goal, "interpretation_request")
        self.assertEqual(result_follow_up_action(goal), "request_result_content_once")
        self.assertEqual(
            result_follow_up_action(goal, result_content_requested=True),
            "await_or_interpret_provided_result",
        )

    def test_abnormal_notice_or_new_concern_continues_targeted_interview(self):
        self.assertEqual(
            result_follow_up_action("institution_result_check", abnormal_notice=True),
            "continue_targeted_interview",
        )
        self.assertEqual(
            result_follow_up_action("institution_result_check", new_concern=True),
            "continue_targeted_interview",
        )

    def test_first_encounter_reviews_all_longitudinal_groups(self):
        result = context_review_due(
            is_first_encounter=True,
            as_of=date(2026, 7, 14),
            last_confirmed={},
        )
        self.assertTrue(all(item["due"] for item in result.values()))
        self.assertTrue(
            all(item["reason"] == "first_encounter" for item in result.values())
        )

    def test_follow_up_reviews_only_due_groups(self):
        today = date(2026, 7, 14)
        result = context_review_due(
            is_first_encounter=False,
            as_of=today,
            last_confirmed={
                "history.conditions": today - timedelta(days=100),
                "medication.current": today - timedelta(days=100),
                "history.family": today - timedelta(days=366),
                "social.alcohol": today - timedelta(days=20),
                "social.smoking": today - timedelta(days=365),
            },
        )
        self.assertFalse(result["history.conditions"]["due"])
        self.assertTrue(result["medication.current"]["due"])
        self.assertTrue(result["history.family"]["due"])
        self.assertFalse(result["social.alcohol"]["due"])
        self.assertTrue(result["social.smoking"]["due"])

    def test_synthetic_result_follow_up_simulations(self):
        fixture = json.loads(
            (
                self.ROOT
                / "simulation"
                / "workflows"
                / "encounter-policy-cases.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(fixture["contains_real_patient_data"])
        for case in fixture["cases"]:
            goal = classify_result_follow_up_goal(case["input"])
            self.assertEqual(goal, case["expected_goal"], case["id"])
            action = result_follow_up_action(
                goal,
                result_content_requested=case.get("result_content_requested", False),
                abnormal_notice=case.get("abnormal_notice", False),
                new_concern=case.get("new_concern", False),
            )
            self.assertEqual(action, case["expected_action"], case["id"])


if __name__ == "__main__":
    unittest.main()
