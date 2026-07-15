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
                "hira.medical_aid_psychiatry_patient_experience",
                "hira.mental_health_inpatient_patient_experience",
                "hira.anesthesia_patient_assessment",
                "hira.imaging_pre_examination_assessment",
                "hira.dementia_patient_proxy_assessment",
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

    def test_generic_assessment_entry_returns_unique_numbered_catalog(self):
        result = self.registry.resolve_entry("정형 설문")
        self.assertEqual(result["status"], "selection_required")
        self.assertEqual(result["workflow_state"], "entry_unresolved")
        numbers = [option["number"] for option in result["options"]]
        self.assertEqual(numbers, list(range(1, 11)))
        self.assertEqual(len(numbers), len(set(numbers)))
        registration = self.registry.document["fixed_questionnaire_registration_policy"]
        self.assertIn("resource_ref", registration["required_metadata"])
        self.assertTrue(
            registration["registration_rules"]["missing_source_must_not_be_reconstructed_by_ai"]
        )

    def test_opening_discovery_commands_list_or_search_without_activation(self):
        policy = self.registry.document["entry_policy"]
        self.assertIn("평가/설문 목록", policy["opening_discovery_hint_ko"])
        listed = self.registry.resolve_entry("평가/설문 목록")
        self.assertEqual(listed["status"], "selection_required")
        searched = self.registry.resolve_entry("설문 검색: 환자경험")
        self.assertEqual(searched["status"], "search_results")
        self.assertEqual(
            {option["program_id"] for option in searched["options"]},
            {
                "hira.inpatient_patient_experience.5th-2025",
                "hira.medical_aid_psychiatry_patient_experience",
                "hira.mental_health_inpatient_patient_experience",
            },
        )
        self.assertEqual(searched["workflow_state"], "entry_unresolved")

    def test_search_handles_missing_term_and_no_result(self):
        missing = self.registry.resolve_entry("설문 검색")
        self.assertEqual(missing["status"], "search_term_required")
        absent = self.registry.resolve_entry("평가 검색: 존재하지않는설문")
        self.assertEqual(absent["status"], "no_search_result")
        self.assertEqual(absent["options"], [])

    def test_specific_alias_enters_single_start_confirmation(self):
        result = self.registry.resolve_entry("환자경험평가를 작성하고 싶어요")
        self.assertEqual(result["status"], "matched")
        self.assertEqual(
            result["program_id"],
            "hira.inpatient_patient_experience.5th-2025",
        )
        self.assertEqual(result["workflow_state"], "awaiting_start_confirmation")
        self.assertEqual(result["prompt_ko"], "환자경험평가 설문을 작성하시겠습니까?")
        self.assertEqual(result["options"], {"1": "예", "2": "아니오", "3": "잘 모르겠음", "4": "답변하지 않음"})

    def test_diagnosis_name_alone_does_not_activate_assessment(self):
        self.assertEqual(self.registry.resolve_entry("우울증")["status"], "no_match")
        self.assertEqual(self.registry.resolve_entry("류마티스관절염")["status"], "no_match")

    def test_stroke_entry_marks_safety_as_preceding_confirmation(self):
        result = self.registry.resolve_entry("급성기 뇌졸중 평가")
        self.assertTrue(result["safety_action_precedes_confirmation"])

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
        self.assertEqual(interview["mode"], "authorized_instrument_result_capture")
        self.assertFalse(interview["instrument_items_available"])
        self.assertTrue(interview["result_capture_available"])
        self.assertTrue(interview["never_reconstruct_with_ai"])
        self.assertIn("PHQ-9", {item["id"] for item in interview["recognized_instruments"]})
        self.assertIn(
            "hira.depression.total_score",
            {item["id"] for item in interview["result_capture_items"]},
        )

    def test_all_ten_catalog_entries_are_writable_in_research_test_mode(self):
        self.assertEqual(len(self.registry.entries), 10)
        for program_id in self.registry.entries:
            activated = self.registry.activate(program_id, context(program_id))
            interview = activated["patient_interview"]
            if interview["mode"] == "fixed_questionnaire":
                self.assertGreater(interview["question_count"], 0)
            elif interview["mode"] == "authorized_instrument_result_capture":
                self.assertTrue(interview["result_capture_items"])
            else:
                self.assertTrue(interview["question_groups"], program_id)
                self.assertTrue(
                    any(group["items"] for group in interview["question_groups"]),
                    program_id,
                )

        response_policy = self.registry.document["response_state_policy"]
        self.assertIn("asked-unknown", response_policy["supported_data_absent_reasons"])
        self.assertIn("asked-declined", response_policy["supported_data_absent_reasons"])
        self.assertTrue(response_policy["unknown_is_never_negative"])
        self.assertIn(
            "hira.anesthesia.recovery_pain_nrs",
            response_policy["mandatory_numeric_items"],
        )

    def test_new_clinician_confirmation_modules_expose_patient_questions(self):
        expectations = {
            "hira.medical_aid_psychiatry_patient_experience": "hira.medical_aid_psychiatry.survey_completed",
            "hira.mental_health_inpatient_patient_experience": "hira.mental_health_inpatient.survey_completed",
            "hira.anesthesia_patient_assessment": "hira.anesthesia.recovery_pain_nrs",
            "hira.imaging_pre_examination_assessment": "hira.imaging.prior_contrast_reaction",
            "hira.dementia_patient_proxy_assessment": "hira.dementia.safety_risk",
        }
        for program_id, expected_item in expectations.items():
            activated = self.registry.activate(program_id, context(program_id))
            item_ids = {
                item["id"]
                for group in activated["patient_interview"]["question_groups"]
                for item in group["items"]
            }
            self.assertIn(expected_item, item_ids)
            self.assertTrue(
                activated["official_submission_requires_clinician_or_record_confirmation"]
            )

        anesthesia = self.registry.programs["hira.anesthesia_patient_assessment"]
        pain = next(
            item
            for group in anesthesia["patient_or_proxy_question_groups"]
            for item in group["items"]
            if item["id"] == "hira.anesthesia.recovery_pain_nrs"
        )
        self.assertEqual((pain["minimum"], pain["maximum"]), (0, 10))
        self.assertFalse(pain["unknown_or_decline_options_visible"])

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
