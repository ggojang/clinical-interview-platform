from __future__ import annotations

import json
import unittest
from pathlib import Path

from runtime.encounter_context import normalize_encounter_context
from runtime.session import InterviewSession


ROOT = Path(__file__).resolve().parents[1]


class EncounterContextTests(unittest.TestCase):
    def test_synthetic_environment_matrix(self):
        matrix = json.loads(
            (ROOT / "simulation/workflows/encounter-context-cases.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(matrix["contains_real_patient_data"])
        for case in matrix["cases"]:
            with self.subTest(case=case["id"]):
                context = normalize_encounter_context(case["context"])
                expected = case["expected"]
                for key in (
                    "safety_first", "response_source", "source_attribution_required",
                    "physical_examination_available", "remote_assessment_limitations_apply",
                    "question_budget_cap",
                ):
                    if key in expected:
                        self.assertEqual(context[key], expected[key])
                if "candidate_intent" in expected:
                    self.assertIn(expected["candidate_intent"], context["candidate_intents"])
                if "intent_modifier" in expected:
                    self.assertIn(expected["intent_modifier"], context["intent_modifiers"])
                self.assertTrue(context["diagnosis_independent"])
                self.assertEqual(context["status"], "research_only")

    def test_runtime_exposes_context_and_applies_emergency_budget(self):
        session = InterviewSession(
            "synthetic-ed-context",
            encounter_context={
                "care_setting": "emergency_department",
                "encounter_type": "new_encounter",
                "interview_initiator": "clinician",
                "interview_mode": "face_to_face",
                "available_information": ["previous_clinical_memory"],
                "time_constraint": "emergency",
                "clinical_responsibility": "independent_assessment",
            },
        )
        state = session.process("기침 때문에 왔어요")
        self.assertEqual(state["patient_context"]["care_setting"], "emergency_department")
        self.assertTrue(state["patient_context"]["safety_first"])
        self.assertLessEqual(session._question_budget("routine"), 12)
        self.assertIn("intent.screen_red_flags", session.active_intents)

    def test_proxy_context_is_preserved_in_clinician_handoff(self):
        session = InterviewSession(
            "synthetic-proxy-context",
            clinician_submission=True,
            encounter_context={
                "care_setting": "home_visit",
                "encounter_type": "follow_up",
                "interview_initiator": "caregiver",
                "interview_mode": "face_to_face",
                "available_information": ["previous_clinical_memory"],
                "time_constraint": "scheduled",
                "clinical_responsibility": "shared_care",
            },
        )
        handoff = session.process("기침 문진을 시작합니다")["clinician_handoff"]
        self.assertEqual(handoff["encounter_context"]["response_source"], "proxy_report")

    def test_invalid_context_fails_closed(self):
        with self.assertRaises(ValueError):
            normalize_encounter_context({"care_setting": "unknown_place"})
        with self.assertRaises(ValueError):
            normalize_encounter_context({"diagnosis": "asthma"})


if __name__ == "__main__":
    unittest.main()
