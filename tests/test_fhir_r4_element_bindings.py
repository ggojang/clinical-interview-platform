from __future__ import annotations

import json
import unittest
from pathlib import Path

from interoperability.fhir_r4_bindings import (
    apply_element_bindings,
    binding_for_element,
    load_documents,
    questionnaire_item_projection,
    questionnaire_response_answer_projection,
)
from interoperability.question_answer import enrich_clinician_context
from tools.validator.audit_question_answer_terminology import run as run_audit


ROOT = Path(__file__).resolve().parents[1]
FAMILY_VALUE_SET = (
    "http://terminology.hl7.org/ValueSet/v3-FamilyMember"
)
ROLE_CODE = "http://terminology.hl7.org/CodeSystem/v3-RoleCode"
MEDICATION_STATUS_VALUE_SET = (
    "http://hl7.org/fhir/ValueSet/medication-statement-status|4.0.1"
)
MEDICATION_STATUS_CODE = (
    "http://hl7.org/fhir/CodeSystem/medication-statement-status"
)


class FhirR4ElementBindingsTest(unittest.TestCase):
    def test_offline_registry_covers_all_base_r4_resources(self):
        policy, registry, mappings = load_documents()
        self.assertEqual(policy["fhir_version"], "4.0.1")
        self.assertEqual(registry["fhir_version"], "4.0.1")
        self.assertEqual(registry["resource_count"], 147)
        self.assertGreaterEqual(registry["binding_count"], 1000)
        self.assertEqual(
            {row["binding"]["strength"] for row in registry["bindings"]},
            {"required", "extensible", "preferred", "example"},
        )
        self.assertTrue(mappings["mappings"])
        self.assertTrue(policy["runtime"]["uses_compiled_registry_only"])
        self.assertFalse(policy["runtime"]["live_fhir_spec_lookup"])

    def test_family_relationship_uses_official_element_valueset(self):
        row = binding_for_element(
            "FamilyMemberHistory.relationship",
            resource="FamilyMemberHistory",
        )
        self.assertIsNotNone(row)
        self.assertEqual(row["binding"]["strength"], "example")
        self.assertEqual(row["binding"]["value_set"], FAMILY_VALUE_SET)

        source = json.loads(
            (
                ROOT / "knowledge/shared/clinician-submission-context.json"
            ).read_text(encoding="utf-8")
        )
        context, coverage = enrich_clinician_context(source)
        fact = next(
            item for item in context["facts"]
            if item["id"] == "history.family.relationship"
        )
        binding = fact["answer_semantic_binding"]
        self.assertEqual(binding["answer_value_set"], FAMILY_VALUE_SET)
        self.assertEqual(binding["fhir_item_type"], "open-choice")
        self.assertEqual(
            binding["fhir_element_binding"]["element_path"],
            "FamilyMemberHistory.relationship",
        )
        self.assertEqual(
            binding["fhir_bound_answer_mappings"]["mother"],
            {
                "system": ROLE_CODE,
                "code": "MTH",
                "display": "mother",
            },
        )
        self.assertIn("generic_answer_value_set", binding)
        self.assertIn("local_answer_value_set", binding)
        item = questionnaire_item_projection(fact)
        self.assertEqual(item["type"], "open-choice")
        self.assertEqual(item["answerValueSet"], FAMILY_VALUE_SET)
        response = questionnaire_response_answer_projection(fact, "mother")
        self.assertEqual(
            response,
            {
                "valueCoding": {
                    "system": ROLE_CODE,
                    "code": "MTH",
                    "display": "mother",
                }
            },
        )
        self.assertEqual(
            coverage["fhir_r4_element_bound_question_count"], 2
        )

    def test_candidate_target_is_annotation_only(self):
        fact = {
            "id": "synthetic.interpretation",
            "type": "Fact",
            "value_type": "coded",
            "fhir_r4_targets": ["Observation.interpretation"],
        }
        generic = {
            "strategy": "SNOMED_CT_then_local_coded_fallback",
            "answer_value_set": "https://example.org/ValueSet/generic",
        }
        effective, targets = apply_element_bindings(fact, generic)
        self.assertEqual(effective, generic)
        self.assertEqual(targets[0]["binding_status"], "annotation_only")
        self.assertEqual(targets[0]["mapping_relation"], "candidate")

    def test_required_medication_status_binding_is_closed_and_coded(self):
        source = json.loads(
            (
                ROOT / "knowledge/shared/clinician-submission-context.json"
            ).read_text(encoding="utf-8")
        )
        context, coverage = enrich_clinician_context(source)
        fact = next(
            item for item in context["facts"]
            if item["id"] == "medication.statement.status"
        )
        binding = fact["answer_semantic_binding"]
        self.assertEqual(binding["answer_value_set"], MEDICATION_STATUS_VALUE_SET)
        self.assertEqual(binding["fhir_item_type"], "choice")
        self.assertFalse(
            binding["fhir_element_binding"]["allow_outside_code"]
        )
        self.assertEqual(
            set(binding["fhir_bound_answer_mappings"]),
            set(fact["allowed_values"]),
        )
        self.assertEqual(
            questionnaire_response_answer_projection(fact, "on_hold"),
            {
                "valueCoding": {
                    "system": MEDICATION_STATUS_CODE,
                    "code": "on-hold",
                    "display": "On Hold",
                }
            },
        )
        with self.assertRaisesRegex(ValueError, "cannot be projected outside"):
            questionnaire_response_answer_projection(fact, "paused_by_patient")
        self.assertEqual(
            coverage["fhir_r4_element_bound_question_count"], 2
        )

    def test_required_binding_rejects_incomplete_internal_mapping(self):
        with self.assertRaisesRegex(
            ValueError, "required FHIR element binding has no answer coding"
        ):
            apply_element_bindings(
                {
                    "id": "medication.statement.status",
                    "type": "Fact",
                    "value_type": "coded",
                    "allowed_values": ["active", "unmapped_internal_status"],
                },
                {
                    "answer_value_set": "https://example.org/ValueSet/generic",
                },
            )

    def test_incompatible_multi_resource_bindings_require_split(self):
        fact = {
            "id": "result.report.status",
            "type": "Fact",
            "value_type": "coded",
        }
        effective, targets = apply_element_bindings(fact, {
            "answer_value_set": "https://example.org/ValueSet/generic"
        })
        self.assertEqual(len(targets), 2)
        conflict = effective["fhir_element_binding_conflict"]
        self.assertEqual(conflict["status"], "projection_split_required")
        self.assertEqual(
            {row["value_set"] for row in conflict["targets"]},
            {
                "http://hl7.org/fhir/ValueSet/diagnostic-report-status|4.0.1",
                "http://hl7.org/fhir/ValueSet/observation-status|4.0.1",
            },
        )

    def test_terminology_audit_reports_fhir_element_binding_quality(self):
        report = run_audit()
        section = report["fhir_r4_element_bindings"]
        self.assertTrue(section["passed"])
        self.assertEqual(section["resource_count"], 147)
        self.assertGreaterEqual(section["element_binding_count"], 1000)
        self.assertIn(
            "history.family.relationship",
            section["effective_fact_ids"],
        )
        kr_core = report["kr_core_v2_overlay"]
        self.assertTrue(kr_core["passed"])
        self.assertEqual(kr_core["package"], "hl7.fhir.kr.core#2.0.0")
        self.assertEqual(kr_core["profile_count"], 31)
        self.assertEqual(kr_core["defined_value_set_count"], 20)
        self.assertFalse(kr_core["terminology_content_embedded"])


if __name__ == "__main__":
    unittest.main()
