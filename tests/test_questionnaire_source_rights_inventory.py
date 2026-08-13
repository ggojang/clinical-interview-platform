import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.inventory.build_questionnaire_source_rights_inventory import build_report


class QuestionnaireSourceRightsInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report("2026-08-13")
        cls.assets = {asset["id"]: asset for asset in cls.report["assets"]}
        cls.candidates = {
            candidate["id"]: candidate
            for candidate in cls.report["acquisition_candidates"]
        }

    def test_inventory_covers_current_resource_families(self):
        self.assertEqual(self.report["validation_errors"], [])
        self.assertEqual(self.report["summary"]["asset_count"], 78)
        self.assertEqual(
            self.report["summary"]["asset_class_counts"],
            {
                "adaptive_preventive_question_group": 10,
                "assessment_program": 8,
                "dynamic_clinical_interview": 56,
                "fhir_fixed_questionnaire": 1,
                "fixed_questionnaire": 1,
                "fixed_standardized_instrument": 1,
                "shared_assessment_component": 1,
            },
        )

    def test_fixed_questionnaire_fails_closed_for_external_use(self):
        for asset in self.report["assets"]:
            if not asset["source_defined_fixed_items"]:
                continue
            self.assertEqual(
                asset["rights"]["external_distribution"],
                "blocked_pending_explicit_rights_review",
            )
            self.assertEqual(
                asset["rights"]["commercial_use"],
                "blocked_pending_explicit_rights_review",
            )

    def test_hira_research_programs_do_not_claim_unverified_official_items(self):
        depression = self.assets["hira.depression_outpatient"]
        self.assertFalse(depression["source_defined_fixed_items"])
        self.assertEqual(
            depression["source_fidelity"],
            "official_item_set_not_verified",
        )
        self.assertIn("공식 척도 문항 미탑재", depression["source_notice_ko"])
        referenced = {
            instrument["id"]: instrument
            for instrument in depression["referenced_external_instruments"]
        }
        self.assertIn("PHQ-9", referenced)
        self.assertFalse(referenced["PHQ-9"]["items_embedded"])
        self.assertEqual(
            referenced["PHQ-9"]["rights_status"],
            "instrument_specific_review_required",
        )

    def test_national_screening_draft_is_not_claimed_as_official_form(self):
        screening = self.assets["kr.nhis.general.common"]
        self.assertEqual(
            screening["source_fidelity"],
            "not_the_official_NHIS_questionnaire",
        )
        self.assertEqual(
            screening["rights"]["official_form_submission"],
            "blocked_pending_official_form_fidelity_verification",
        )

    def test_promis_is_metadata_only_until_permission_review(self):
        promis = self.candidates["candidate.healthmeasures.promis"]
        self.assertFalse(promis["content_in_repository"])
        self.assertEqual(
            promis["implementation_status"],
            "metadata_only_not_implemented",
        )
        self.assertEqual(
            promis["rights"]["internal_company_product_test"],
            "rights_confirmation_required",
        )
        self.assertIn(
            "obtain_HEAP_or_other_written_permission_when_required",
            promis["internal_pilot_gate"],
        )

    def test_domestic_sources_are_registered_in_requested_order(self):
        ordered = self.report["domestic_acquisition_order"]
        self.assertEqual(
            [candidate["id"] for candidate in ordered],
            [
                "candidate.kr.kdca.community-health-survey",
                "candidate.kr.khp.korea-health-panel",
                "candidate.kr.keis.klosa",
            ],
        )
        self.assertEqual(
            [candidate["acquisition_priority"] for candidate in ordered],
            [1, 2, 3],
        )

    def test_domestic_sources_are_metadata_only_and_fail_closed(self):
        for candidate in self.report["domestic_acquisition_order"]:
            self.assertFalse(candidate["content_in_repository"])
            self.assertTrue(candidate["official_sources"])
            self.assertTrue(candidate["runtime_adoption_boundary"]["allowed_now"])
            blocked = candidate["runtime_adoption_boundary"]["blocked_now"]
            self.assertTrue(any("verbatim" in item for item in blocked))

    def test_embedded_third_party_scales_require_separate_review(self):
        for candidate in self.report["domestic_acquisition_order"]:
            third_party_rights = [
                value
                for key, value in candidate["rights"].items()
                if "third_party" in key
            ]
            self.assertTrue(third_party_rights)
            self.assertTrue(all("review_required" in value for value in third_party_rights))

    def test_tracked_output_matches_deterministic_report(self):
        tracked = json.loads(
            (ROOT / "coverage/questionnaire-source-rights-inventory-latest.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(tracked, self.report)


if __name__ == "__main__":
    unittest.main()
