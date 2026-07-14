import unittest

from tools.terminology.semantic_claim_binding import build_semantic_claim_binding


class SemanticClaimBindingTests(unittest.TestCase):
    def test_verified_snomed_and_kcd_are_both_preserved(self):
        result = build_semantic_claim_binding(
            domain="diagnosis_kcd9",
            semantic_coding={"system": "http://snomed.info/sct", "code": "59621000", "display": "Essential hypertension"},
            claim_coding={"system": "http://www.hl7korea.or.kr/CodeSystem/kostat-kcd-9", "code": "I10", "display": "본태성(원발성) 고혈압"},
            mapping_relation="equivalent",
            activation_trigger="uploaded_document_contains_explicit_claim_code_or_name",
            verification_method="terminology_lookup_and_mapping_review",
            source_type="uploaded_document",
        )
        self.assertTrue(result["preserve_both_codings"])
        self.assertEqual(result["semantic_coding"]["code"], "59621000")
        self.assertEqual(result["claim_coding"]["code"], "I10")
        self.assertTrue(result["single_codeable_concept_eligible"])

    def test_related_product_and_semantic_drug_are_not_collapsed(self):
        result = build_semantic_claim_binding(
            domain="medication",
            semantic_coding={"system": "http://snomed.info/sct", "code": "386864001", "display": "Amlodipine"},
            claim_coding={"system": "http://www.hl7korea.or.kr/CodeSystem/hira-edi-medication", "code": "052400890", "display": "로바스크정"},
            mapping_relation="narrower",
            activation_trigger="user_provided_medication_product_name",
            verification_method="hira_product_detail_and_snomed_ingredient_lookup",
            source_type="user_text",
        )
        self.assertTrue(result["preserve_both_codings"])
        self.assertFalse(result["single_codeable_concept_eligible"])

    def test_name_similarity_cannot_assert_equivalence(self):
        with self.assertRaises(ValueError):
            build_semantic_claim_binding(
                domain="procedure",
                semantic_coding={"system": "http://snomed.info/sct", "code": "241615005"},
                claim_coding={"system": "http://www.hl7korea.or.kr/CodeSystem/hira-edi-procedure", "code": "EB421"},
                mapping_relation="equivalent",
                activation_trigger="user_provided_claim_catalog_name",
                verification_method="name_similarity_only",
                source_type="user_text",
            )

    def test_routine_clinical_fact_cannot_activate_binding(self):
        with self.assertRaises(ValueError):
            build_semantic_claim_binding(
                domain="diagnosis_kcd8",
                semantic_coding={"system": "http://snomed.info/sct", "code": "59621000"},
                claim_coding={"system": "http://www.hl7korea.or.kr/CodeSystem/kostat-kcd-8", "code": "I10"},
                mapping_relation="equivalent",
                activation_trigger="routine_clinical_fact_collection",
                verification_method="terminology_lookup_and_mapping_review",
                source_type="runtime_fact",
            )


if __name__ == "__main__":
    unittest.main()
