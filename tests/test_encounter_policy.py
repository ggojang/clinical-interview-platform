from datetime import date, timedelta
import json
from pathlib import Path
import unittest

from runtime.encounter_policy import (
    classify_result_follow_up_goal,
    context_review_completion,
    context_review_due,
    preventive_immunization_review_due,
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
        self.assertEqual(
            set(result),
            {
                "history.conditions",
                "history.procedures",
                "medication.current",
                "allergy.current",
                "history.family",
                "occupation.current",
                "social.alcohol",
                "social.smoking",
            },
        )

    def test_follow_up_reviews_only_due_groups(self):
        today = date(2026, 7, 14)
        result = context_review_due(
            is_first_encounter=False,
            as_of=today,
            last_confirmed={
                "history.conditions": today - timedelta(days=100),
                "history.procedures": today - timedelta(days=366),
                "medication.current": today - timedelta(days=100),
                "allergy.current": today - timedelta(days=20),
                "history.family": today - timedelta(days=366),
                "occupation.current": today - timedelta(days=365),
                "social.alcohol": today - timedelta(days=20),
                "social.smoking": today - timedelta(days=365),
            },
        )
        self.assertFalse(result["history.conditions"]["due"])
        self.assertTrue(result["history.procedures"]["due"])
        self.assertTrue(result["medication.current"]["due"])
        self.assertFalse(result["allergy.current"]["due"])
        self.assertTrue(result["history.family"]["due"])
        self.assertTrue(result["occupation.current"]["due"])
        self.assertFalse(result["social.alcohol"]["due"])
        self.assertTrue(result["social.smoking"]["due"])

    def test_immunization_profile_is_not_activated_for_unrelated_symptom(self):
        result = preventive_immunization_review_due(
            encounter_type="new_encounter",
            as_of=date(2026, 7, 16),
            last_confirmed_at=None,
        )
        self.assertFalse(result["activated"])
        self.assertFalse(result["due"])
        self.assertEqual(result["reason"], "not_activated")
        self.assertFalse(result["vaccine_due_status_inferred"])

    def test_preventive_or_vaccination_context_activates_immunization_profile(self):
        for encounter_type in ("preventive_visit", "annual_review", "vaccination"):
            with self.subTest(encounter_type=encounter_type):
                result = preventive_immunization_review_due(
                    encounter_type=encounter_type,
                    as_of=date(2026, 7, 16),
                    last_confirmed_at=None,
                )
                self.assertTrue(result["activated"])
                self.assertTrue(result["due"])
                self.assertEqual(result["reason"], "never_confirmed")
                self.assertFalse(result["vaccine_due_status_inferred"])

        health_check = preventive_immunization_review_due(
            encounter_type="new_encounter",
            care_setting="health_checkup",
            as_of=date(2026, 7, 16),
            last_confirmed_at=None,
        )
        self.assertTrue(health_check["activated"])
        self.assertTrue(health_check["due"])

    def test_rfe_risk_rule_can_activate_recent_immunization_profile(self):
        result = preventive_immunization_review_due(
            encounter_type="new_encounter",
            as_of=date(2026, 7, 16),
            last_confirmed_at=date(2026, 6, 1),
            rfe_or_risk_relevant=True,
        )
        self.assertTrue(result["activated"])
        self.assertFalse(result["due"])
        self.assertEqual(result["reason"], "recently_confirmed")
        self.assertFalse(result["vaccine_due_status_inferred"])

    def test_architecture_text_preserves_rfe_and_runtime_stom_boundary(self):
        readme = (self.ROOT / "README.md").read_text(encoding="utf-8")
        foundation = (self.ROOT / "FOUNDATION.md").read_text(encoding="utf-8")
        context_foundation = (
            self.ROOT / "docs/context/000-foundation.md"
        ).read_text(encoding="utf-8")
        project_context = (self.ROOT / "PROJECT_CONTEXT.md").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("Chief complaint: cough", readme)
        self.assertIn("Initial Reason for Encounter (RFE) vertical slice: cough", readme)
        for document in (foundation, context_foundation):
            self.assertIn("Runtime never communicates with STOM.", document)
            self.assertIn("outside the Clinical Interview Runtime", document)
        self.assertNotIn("optional Runtime semantic-alignment service", foundation)
        self.assertIn("Adapter is not part of the Clinical Interview Runtime", project_context)

    def test_first_encounter_cannot_complete_with_unresolved_context(self):
        due = context_review_due(
            is_first_encounter=True,
            as_of=date(2026, 7, 14),
            last_confirmed={},
        )
        result = context_review_completion(
            due_groups=due,
            group_states={
                "history.conditions": "answered",
                "history.procedures": "answered",
                "medication.current": "current_existing",
                "allergy.current": "unknown",
                "history.family": "declined",
                "occupation.current": "answered",
                "social.smoking": "answered",
            },
        )
        self.assertFalse(result["complete"])
        self.assertEqual(result["unresolved_groups"], ["social.alcohol"])

    def test_first_encounter_accepts_explicit_outcome_for_every_group(self):
        due = context_review_due(
            is_first_encounter=True,
            as_of=date(2026, 7, 14),
            last_confirmed={},
        )
        result = context_review_completion(
            due_groups=due,
            group_states={group: "answered" for group in due},
        )
        self.assertTrue(result["complete"])
        self.assertEqual(result["unresolved_groups"], [])

    def test_safety_deferred_context_remains_incomplete(self):
        due = context_review_due(
            is_first_encounter=True,
            as_of=date(2026, 7, 14),
            last_confirmed={},
        )
        states = {group: "answered" for group in due}
        states["history.procedures"] = "deferred_safety"
        result = context_review_completion(due_groups=due, group_states=states)
        self.assertFalse(result["complete"])
        self.assertEqual(
            result["safety_deferred_groups"], ["history.procedures"]
        )

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

        for case in fixture["context_review_cases"]:
            due = context_review_due(
                is_first_encounter=case["is_first_encounter"],
                as_of=date(2026, 7, 14),
                last_confirmed={},
            )
            if "expected_due" in case:
                self.assertEqual(
                    sorted(group for group, item in due.items() if item["due"]),
                    sorted(case["expected_due"]),
                    case["id"],
                )
            if "group_states" in case:
                completion = context_review_completion(
                    due_groups=due,
                    group_states=case["group_states"],
                )
                self.assertEqual(
                    completion["complete"], case["expected_complete"], case["id"]
                )
                self.assertEqual(
                    completion["unresolved_groups"],
                    case["expected_unresolved"],
                    case["id"],
                )


if __name__ == "__main__":
    unittest.main()
