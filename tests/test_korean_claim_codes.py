import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class KoreanClaimCodePolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(
            (ROOT / "policies/korean-claim-code-binding.json").read_text(encoding="utf-8")
        )

    def test_domains_use_distinct_code_systems(self):
        domains = self.policy["domains"]
        systems = {
            domains["procedure"]["system"],
            domains["medication"]["system"],
            domains["material"]["system"],
        }
        self.assertEqual(len(systems), 3)
        self.assertTrue(all("hira-edi-" in system for system in systems))
        diagnosis_systems = {
            item["system"] for item in domains["diagnosis"]["classification_systems"]
        }
        self.assertEqual(
            diagnosis_systems,
            {
                "http://www.hl7korea.or.kr/CodeSystem/kostat-kcd-8",
                "http://www.hl7korea.or.kr/CodeSystem/kostat-kcd-9",
            },
        )
        self.assertTrue(diagnosis_systems.isdisjoint(systems))

    def test_kcd9_and_material_limitations_are_explicit(self):
        diagnosis = self.policy["domains"]["diagnosis"]
        self.assertFalse(diagnosis["kcd9_general_search_currently_exposed"])
        self.assertTrue(diagnosis["kcd9_morphology_search_is_not_general_diagnosis_search"])
        self.assertTrue(diagnosis["never_assume_kcd8_code_is_unchanged_in_kcd9"])
        self.assertTrue(self.policy["domains"]["material"]["group_result_is_not_final_item_code"])

    def test_lookup_is_reactive_to_user_or_document_supplied_content(self):
        activation = self.policy["activation"]
        self.assertFalse(activation["proactive_claim_lookup"])
        self.assertTrue(activation["do_not_ask_for_claim_code_during_routine_questionnaire"])
        self.assertIn("uploaded_document_contains_explicit_claim_code_or_name", activation["allowed_triggers"])
        self.assertIn("user_provided_medication_product_name", activation["allowed_triggers"])
        self.assertIn("ai_generated_differential_diagnosis", activation["forbidden_triggers"])
        self.assertIn("automatic_enrichment_of_every_clinical_fact", activation["forbidden_triggers"])
        self.assertIn(
            "never_send_the_file_image_or_surrounding_patient_narrative_to_stom",
            self.policy["input_handling"]["uploaded_scan_or_document"],
        )

    def test_claim_codes_have_no_clinical_rule_authority(self):
        boundary = self.policy["clinical_boundary"]
        self.assertTrue(boundary["claim_code_does_not_establish_diagnosis"])
        self.assertTrue(boundary["do_not_bind_possible_differential_as_final_claim_diagnosis"])
        self.assertTrue(boundary["claim_code_never_controls_interview_priority_safety_or_differential"])
        self.assertTrue(boundary["terminology_service_failure_does_not_block_interview"])

    def test_verified_snomed_and_claim_codings_are_both_retained(self):
        multi = self.policy["semantic_claim_multi_coding"]
        self.assertEqual(
            multi["when_snomed_and_claim_code_are_both_known"],
            "preserve_both_as_information",
        )
        self.assertTrue(multi["never_replace_snomed_with_claim_code"])
        self.assertTrue(multi["never_replace_claim_code_with_snomed"])
        self.assertTrue(multi["name_similarity_alone_cannot_establish_equivalence"])
        self.assertEqual(multi["reusable_fact_id"], "terminology.semantic_claim_binding")


if __name__ == "__main__":
    unittest.main()
