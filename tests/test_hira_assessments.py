from __future__ import annotations

import json
import unittest
from pathlib import Path

from runtime.assessment import AssessmentContextError, HiraAssessmentRegistry


ROOT = Path(__file__).resolve().parents[1]


def context(program_id: str) -> dict[str, object]:
    return {
        "assessment_program_id": program_id,
        "assessment_cycle": "2026-cycle2-8",
        "care_setting": "long_term_care_hospital_inpatient",
        "target_period": "2026-07-01/2026-12-31",
        "institution_eligibility_status": "confirmed",
        "patient_eligibility_status": "confirmed",
        "information_source": "patient_report",
    }


class HiraAssessmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = HiraAssessmentRegistry()

    def test_registry_is_research_only_and_has_supported_programs(self):
        self.assertEqual(self.registry.document["status"], "research_only")
        self.assertEqual(self.registry.document["review_status"], "unreviewed")
        self.assertEqual(
            set(self.registry.programs),
            {
                "hira.long_term_care_hospital_inpatient.2026-cycle2-8",
                "hira.depression_outpatient",
                "hira.acute_stroke_event_history",
                "hira.rheumatoid_arthritis",
                "hira.inpatient_patient_experience.5th-2025",
            },
        )

    def test_program_cannot_activate_without_explicit_matching_context(self):
        program_id = "hira.long_term_care_hospital_inpatient.2026-cycle2-8"
        with self.assertRaises(AssessmentContextError):
            self.registry.activate(program_id, {})
        wrong = context(program_id)
        wrong["assessment_program_id"] = "rfe.abdominal_pain"
        with self.assertRaises(AssessmentContextError):
            self.registry.activate(program_id, wrong)

    def test_nursing_program_exposes_patient_questions_but_not_observations(self):
        program_id = "hira.long_term_care_hospital_inpatient.2026-cycle2-8"
        activated = self.registry.activate(program_id, context(program_id))
        interview = activated["patient_interview"]
        item_ids = {
            item["id"]
            for group in interview["question_groups"]
            for item in group["items"]
        }
        self.assertIn("hira.ltc.fall_last_30_days", item_ids)
        self.assertIn("hira.ltc.swallowing_difficulty", item_ids)
        self.assertNotIn("hira.ltc.activities_of_daily_living", item_ids)
        excluded = activated["excluded_from_patient_interview"]
        observation_ids = {item["id"] for item in excluded["structured_observation"]}
        self.assertIn("hira.ltc.activities_of_daily_living", observation_ids)
        self.assertIn("hira.ltc.skin_and_pressure_ulcer_current", observation_ids)
        pain = interview["reusable_modules"][0]
        self.assertEqual(pain["must_collect"], ["pain.frequency", "pain.nrs_score"])

    def test_patient_experience_routes_to_exact_fixed_questionnaire(self):
        program_id = "hira.inpatient_patient_experience.5th-2025"
        activated = self.registry.activate(program_id, context(program_id))
        interview = activated["patient_interview"]
        self.assertEqual(interview["mode"], "fixed_questionnaire")
        self.assertTrue(interview["preserve_source_items"])
        self.assertEqual(interview["section_count"], 8)
        self.assertEqual(interview["question_count"], 26)
        questionnaire = json.loads(
            (ROOT / interview["questionnaire_ref"]).read_text(encoding="utf-8")
        )
        self.assertEqual(questionnaire["resourceType"], "Questionnaire")

    def test_depression_requires_authorized_instrument_resource(self):
        program_id = "hira.depression_outpatient"
        activated = self.registry.activate(program_id, context(program_id))
        interview = activated["patient_interview"]
        self.assertEqual(interview["mode"], "authorized_instrument_required")
        self.assertFalse(interview["items_available"])
        self.assertTrue(interview["never_reconstruct_with_ai"])
        self.assertIn("PHQ-9", {item["id"] for item in interview["recognized_instruments"]})

    def test_ra_global_health_vas_is_not_pain_nrs(self):
        program_id = "hira.rheumatoid_arthritis"
        activated = self.registry.activate(program_id, context(program_id))
        item = activated["patient_interview"]["question_groups"][0]["items"][0]
        self.assertEqual((item["minimum"], item["maximum"]), (0, 100))
        self.assertFalse(item["is_pain_score"])

    def test_acute_stroke_collects_event_history_without_delaying_care(self):
        program_id = "hira.acute_stroke_event_history"
        activated = self.registry.activate(program_id, context(program_id))
        program = self.registry.programs[program_id]
        self.assertTrue(program["activation"]["must_not_delay_emergency_assessment_or_treatment"])
        item_ids = {
            item["id"]
            for group in activated["patient_interview"]["question_groups"]
            for item in group["items"]
        }
        self.assertIn("hira.stroke.symptom_onset_datetime", item_ids)
        self.assertIn("hira.stroke.last_known_well_datetime", item_ids)
        self.assertIn("hira.stroke.ambulance_use", item_ids)
        self.assertNotIn("hira.stroke.brain_imaging_datetime", item_ids)
        self.assertTrue(program["data_absent_policy"]["unknown_event_time_is_allowed"])


if __name__ == "__main__":
    unittest.main()
