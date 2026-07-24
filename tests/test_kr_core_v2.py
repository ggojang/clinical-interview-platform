from __future__ import annotations

import unittest
from pathlib import Path

from compiler.build_package import compile_package, validate_package
from interoperability.fhir_r4_bindings import apply_element_bindings
from interoperability.kr_core_v2 import (
    binding_for_profile_element,
    binding_for_selected_profiles,
    load_documents,
    profiles_for_resource,
    projection_requirements,
)
from tools.validator.audit_kr_core_v2 import run as run_audit


BASE = "http://www.hl7korea.or.kr/fhir/krcore"
ROOT = Path(__file__).resolve().parents[1]
ENCOUNTER_DIAGNOSIS = (
    f"{BASE}/StructureDefinition/krcore-condition-encounter-diagnosis"
)
CHIEF_COMPLAINT = (
    f"{BASE}/StructureDefinition/krcore-condition-chief-complaint"
)
LAB_REPORT = (
    f"{BASE}/StructureDefinition/"
    "krcore-diagnosticreport-laboratory-results"
)
IMAGING_REPORT = (
    f"{BASE}/StructureDefinition/"
    "krcore-diagnosticreport-diagnostic-imaging"
)
INSURANCE_EXTENSION = (
    f"{BASE}/StructureDefinition/krcore-insuranceTypes"
)
KCD8 = f"{BASE}/ValueSet/krcore-kcd8-codes"
LAB_CODES = f"{BASE}/ValueSet/krcore-laboratory-codes"


class KrCoreV2Test(unittest.TestCase):
    def test_registry_retains_profiles_without_terminology_duplication(self):
        policy, registry = load_documents()
        self.assertEqual(policy["package"], "hl7.fhir.kr.core#2.0.0")
        self.assertEqual(registry["profile_count"], 31)
        self.assertEqual(registry["extension_count"], 4)
        self.assertEqual(registry["structure_definition_count"], 35)
        self.assertEqual(registry["binding_count"], 406)
        self.assertEqual(registry["defined_value_set_count"], 20)
        self.assertFalse(
            registry["terminology_storage"]["duplicate_value_set_content"]
        )
        self.assertTrue(
            all(
                "compose" not in item and "expansion" not in item
                for item in registry["defined_value_sets"]
            )
        )
        self.assertFalse(policy["runtime"]["live_stom_lookup"])

    def test_compiled_package_declares_non_clinical_kr_core_overlay(self):
        package = compile_package(profile="cough")
        validate_package(package)
        overlay = package["interoperability_coverage"]["kr_core_v2"]
        self.assertEqual(overlay["package"], "hl7.fhir.kr.core#2.0.0")
        self.assertEqual(overlay["profile_count"], 31)
        self.assertEqual(overlay["extension_count"], 4)
        self.assertFalse(overlay["terminology_content_embedded"])
        self.assertFalse(overlay["questionnaire_profile_defined"])
        self.assertFalse(overlay["clinical_authority"])
        self.assertFalse(overlay["completion_authority"])

    def test_korean_condition_profiles_keep_rfe_and_diagnosis_distinct(self):
        diagnosis = binding_for_profile_element(
            ENCOUNTER_DIAGNOSIS,
            "Condition.code",
        )
        self.assertEqual(diagnosis["binding"]["strength"], "required")
        self.assertEqual(diagnosis["binding"]["value_set"], KCD8)

        chief_complaint = binding_for_profile_element(
            CHIEF_COMPLAINT,
            "Condition.code",
        )
        self.assertEqual(chief_complaint["binding"]["strength"], "example")
        self.assertEqual(
            chief_complaint["binding"]["value_set"],
            "http://hl7.org/fhir/ValueSet/condition-code|4.0.1",
        )

    def test_kr_core_extension_binding_is_retained(self):
        insurance = binding_for_profile_element(
            INSURANCE_EXTENSION,
            "Extension.value[x]",
        )
        self.assertEqual(insurance["binding"]["strength"], "required")
        self.assertEqual(
            insurance["binding"]["value_set"],
            f"{BASE}/ValueSet/krcore-insurance-types-codes",
        )

    def test_sliced_binding_requires_explicit_element_id(self):
        with self.assertRaisesRegex(ValueError, "sliced KR Core binding"):
            binding_for_profile_element(
                ENCOUNTER_DIAGNOSIS,
                "Condition.category",
            )
        category = binding_for_profile_element(
            ENCOUNTER_DIAGNOSIS,
            "Condition.category",
            element_id="Condition.category:EnctrDiag",
        )
        self.assertEqual(
            category["binding"]["value_set"],
            f"{BASE}/ValueSet/krcore-condition-category-codes",
        )

    def test_incompatible_profile_bindings_require_projection_split(self):
        with self.assertRaisesRegex(ValueError, "split the projection"):
            binding_for_selected_profiles(
                [LAB_REPORT, IMAGING_REPORT],
                "DiagnosticReport",
                "DiagnosticReport.code",
            )

    def test_selected_kr_profile_precedes_base_fhir_candidate_binding(self):
        generic = {
            "strategy": "SNOMED_CT_then_local_coded_fallback",
            "answer_value_set": "https://example.org/ValueSet/generic",
        }
        effective, targets = apply_element_bindings(
            {
                "id": "synthetic.test.name",
                "type": "Fact",
                "value_type": "coded_or_string",
                "fhir_r4_targets": ["DiagnosticReport.code"],
            },
            generic,
            selected_kr_core_profiles=[LAB_REPORT],
        )
        self.assertEqual(effective, generic)
        self.assertEqual(targets[0]["binding_source"], "kr_core_v2_profile")
        self.assertEqual(targets[0]["jurisdiction"], "KR")
        self.assertEqual(targets[0]["binding_strength"], "extensible")
        self.assertEqual(targets[0]["value_set"], LAB_CODES)
        self.assertEqual(targets[0]["selected_profiles"], [LAB_REPORT])

    def test_requirements_and_audit_expose_profile_projection_gaps(self):
        requirements = projection_requirements(LAB_REPORT)
        self.assertTrue(
            any(
                item["element_path"] == "DiagnosticReport.status"
                and item["must_support"]
                for item in requirements
            )
        )
        self.assertGreaterEqual(
            len(profiles_for_resource("DiagnosticReport")), 4
        )
        report = run_audit()
        self.assertTrue(report["passed"])
        self.assertEqual(report["profile_count"], 31)
        self.assertEqual(report["extension_count"], 4)
        self.assertEqual(report["binding_count"], 406)
        self.assertFalse(
            report["questionnaire"]["profile_defined_in_kr_core_v2"]
        )
        self.assertFalse(report["terminology"]["service_checked"])

    def test_public_gpt_schema_exposes_kr_core_resources(self):
        schema = (ROOT / "docs/gpt/openapi.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "operationId: getKrCoreV2InteroperabilityPolicy", schema
        )
        self.assertIn(
            "operationId: getKrCoreV2InteroperabilityCoverage", schema
        )
        self.assertIn(
            "operationId: getKrCoreV2ProfileElementBindings", schema
        )


if __name__ == "__main__":
    unittest.main()
