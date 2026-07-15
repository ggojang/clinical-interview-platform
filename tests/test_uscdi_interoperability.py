from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from compiler.build_package import PACKAGE_PROFILES, compile_package
from interoperability.uscdi import (
    CORE_MAPPING,
    PLUS_MAPPING,
    POLICY,
    SOURCE_MANIFEST,
    validate_overlay_documents,
)
from tools.validator.audit_uscdi_interoperability import run as run_audit
from tools.gpt_export.build import build as build_gpt_export


ROOT = Path(__file__).resolve().parents[1]


class UscdiInteroperabilityTest(unittest.TestCase):
    def test_overlay_sources_and_model_validate(self):
        result = validate_overlay_documents()
        self.assertEqual(result["core_element_count"], 21)
        self.assertEqual(result["domain_count"], 4)
        self.assertEqual(result["source_artifact_count"], 5)
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertFalse(policy["authority_boundary"]["clinical_question_authority"])
        self.assertFalse(policy["authority_boundary"]["clinical_safety_rule_authority"])
        self.assertFalse(policy["authority_boundary"]["completion_rule_authority"])
        self.assertEqual(policy["jurisdiction"]["deployment_jurisdiction"], "KR")

    def test_every_package_contains_non_clinical_uscdi_v6_coverage(self):
        for profile in PACKAGE_PROFILES:
            with self.subTest(profile=profile):
                package = compile_package(profile=profile)
                overlay = package["interoperability_coverage"]
                self.assertEqual(overlay["core"]["framework_version"], "v6")
                self.assertFalse(overlay["clinical_authority"])
                self.assertFalse(overlay["completion_authority"])
                self.assertEqual(
                    overlay["jurisdiction"], {"framework": "US", "deployment": "KR"}
                )
                self.assertGreater(overlay["core"]["mapped_element_count"], 0)
                self.assertLessEqual(
                    overlay["core"]["mapped_element_count"],
                    overlay["core"]["eligible_element_count"],
                )
                self.assertEqual(
                    package["coverage"]["interoperability"]["coverage_percent"],
                    overlay["core"]["coverage_percent"],
                )

    def test_record_only_uscdi_gaps_do_not_become_required_questions(self):
        package = compile_package(profile="cough")
        required = {
            fact_id
            for values in package["interview_completion_policy"]["required_facts"].values()
            for fact_id in values
        }
        record_only = {
            item["element_id"] for item in package["interoperability_coverage"]["core"]["elements"]
            if item["collection_role"] in {"record_or_provider", "output_generated"}
        }
        self.assertTrue({"uscdi.encounter", "uscdi.care_team", "uscdi.insurance", "uscdi.orders", "uscdi.clinical_notes"} <= record_only)
        self.assertFalse(any(item.startswith("uscdi.") for item in required))

    def test_domain_overlays_follow_encounter_scope(self):
        pregnancy = compile_package(profile="pregnancy_postpartum_concern")
        pregnancy_domains = {
            item["domain_id"]: item
            for item in pregnancy["interoperability_coverage"]["uscdi_plus_domains"]
        }
        self.assertIn("uscdi-plus.maternal-health", pregnancy_domains)
        self.assertIn("uscdi-plus.behavioral-health", pregnancy_domains)
        self.assertEqual(
            pregnancy_domains["uscdi-plus.maternal-health"]["unmapped_element_ids"], []
        )

        mental = compile_package(profile="mental_health_sleep")
        self.assertIn(
            "uscdi-plus.behavioral-health",
            {item["domain_id"] for item in mental["interoperability_coverage"]["uscdi_plus_domains"]},
        )
        fever = compile_package(profile="fever")
        self.assertIn(
            "uscdi-plus.public-health",
            {item["domain_id"] for item in fever["interoperability_coverage"]["uscdi_plus_domains"]},
        )

    def test_all_explicit_domain_fact_references_exist_in_repository(self):
        available = {
            fact["id"]
            for fact in json.loads(
                (ROOT / "knowledge/shared/clinician-submission-context.json")
                .read_text(encoding="utf-8")
            )["facts"]
        }
        for profile in PACKAGE_PROFILES:
            package = compile_package(profile=profile)
            available.update(
                node["id"] for node in package["knowledge_graph"]["nodes"]
                if node["type"] == "Fact"
            )
        plus = json.loads(PLUS_MAPPING.read_text(encoding="utf-8"))
        referenced = {
            fact_id
            for domain in plus["domains"]
            for element in domain["elements"]
            for fact_id in element.get("fact_ids", [])
        }
        self.assertEqual(referenced - available, set())

    def test_sources_have_weekly_refresh_metadata(self):
        manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(all(item["monitor_profile"] == "interoperability_standard" for item in manifest["artifacts"]))
        self.assertTrue(all(item["monitor_interval_days"] == 7 for item in manifest["artifacts"]))
        self.assertTrue(all(item["next_monitor_at"] == "2026-07-23" for item in manifest["artifacts"]))

    def test_repository_wide_uscdi_audit_passes(self):
        report = run_audit()
        self.assertTrue(report["passed"])
        self.assertEqual(report["package_count"], len(PACKAGE_PROFILES))

    def test_gpt_export_exposes_response_free_interoperability_resources(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build_gpt_export(ROOT, output_path)
            paths = {item["path"] for item in manifest["resources"]}
            self.assertTrue({
                "/gpt/interoperability/uscdi-v6-core.json",
                "/gpt/interoperability/uscdi-plus-domain-overlays.json",
                "/gpt/interoperability/uscdi-policy.json",
                "/gpt/interoperability/uscdi-coverage.json",
            } <= paths)
            for name in (
                "uscdi-v6-core.json", "uscdi-plus-domain-overlays.json",
                "uscdi-policy.json", "uscdi-coverage.json",
            ):
                resource = json.loads(
                    (output_path / "interoperability" / name).read_text(encoding="utf-8")
                )
                self.assertFalse(resource["contains_patient_responses"])
        schema = (ROOT / "docs/gpt/openapi.yaml").read_text(encoding="utf-8")
        self.assertIn("operationId: getUscdiV6CoreOverlay", schema)
        self.assertIn("operationId: getUscdiPlusDomainOverlays", schema)
        self.assertIn("operationId: getUscdiInteroperabilityPolicy", schema)
        self.assertIn("operationId: getUscdiInteroperabilityCoverage", schema)

    def test_interoperability_regression_matrix_covers_boundary_failures(self):
        matrix = json.loads(
            (ROOT / "simulation/workflows/uscdi-interoperability-cases.json")
            .read_text(encoding="utf-8")
        )
        self.assertFalse(matrix["contains_real_patient_data"])
        expected = {item for case in matrix["cases"] for item in case["expected"]}
        self.assertTrue({
            "no_automatic_question",
            "not_patient_collectable",
            "dataAbsentReason_preserved",
            "multiple_overlays_preserved",
            "deployment_jurisdiction_KR",
        } <= expected)


if __name__ == "__main__":
    unittest.main()
