from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from compiler.build_package import PACKAGE_PROFILES, compile_package
from interoperability.computable_knowledge import (
    POLICY,
    REGISTRY,
    SIMULATION,
    SOURCE_MANIFEST,
    validate_overlay_documents,
)
from tools.validator.audit_computable_knowledge import run as run_audit
from tools.gpt_export.build import build as build_gpt_export


ROOT = Path(__file__).resolve().parents[1]


class ComputableKnowledgeStandardsTest(unittest.TestCase):
    def test_overlay_documents_and_sources_validate(self):
        result = validate_overlay_documents()
        self.assertEqual(result["framework_count"], 10)
        self.assertEqual(result["source_artifact_count"], 11)
        self.assertEqual(result["rule_projection_type_count"], 11)
        self.assertEqual(result["simulation_count"], 10)

    def test_foreign_and_external_standards_have_no_clinical_authority(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(policy["deployment_jurisdiction"], "KR")
        self.assertTrue(
            all(
                value is False
                for key, value in policy["authority_boundary"].items()
                if key.endswith("_authority")
            )
        )
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        frameworks = {item["id"]: item for item in registry["frameworks"]}
        self.assertEqual(frameworks["hl7-au-core"]["adoption"], "reference_only")
        self.assertEqual(frameworks["openehr-gdl2"]["adoption"], "secondary_research")
        self.assertEqual(
            frameworks["hl7-cds-hooks"]["adoption"], "external_adapter_only"
        )

    def test_all_sources_are_weekly_monitored_and_license_gaps_visible(self):
        manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
        self.assertTrue(
            all(item["monitor_interval_days"] == 7 for item in manifest["artifacts"])
        )
        self.assertTrue(
            all(item["next_monitor_at"] == "2026-08-01" for item in manifest["artifacts"])
        )
        ckm = next(
            item
            for item in manifest["artifacts"]
            if item["id"] == "source.openehr.ckm.observed-2026-07-25"
        )
        self.assertTrue(ckm["artifact_level_license_required"])
        gdl = next(
            item
            for item in manifest["artifacts"]
            if item["id"] == "source.openehr.gdl2.2.0.0"
        )
        self.assertEqual(gdl["specification_status"], "TRIAL")

    def test_every_package_has_non_executable_reference_metadata(self):
        for profile in PACKAGE_PROFILES:
            with self.subTest(profile=profile):
                package = compile_package(profile=profile)
                overlay = package["computable_knowledge"]
                self.assertEqual(overlay["source_of_truth"]["behavior"], "Rule Graph")
                self.assertFalse(overlay["runtime_external_lookup"])
                self.assertTrue(all(value is False for value in overlay["authority"].values()))
                self.assertTrue(
                    all(value is False for value in overlay["projection_outputs"].values())
                )
                self.assertFalse(overlay["fixed_questionnaire_automatic_mapping"])

    def test_simulation_covers_semantic_and_runtime_boundaries(self):
        matrix = json.loads(SIMULATION.read_text(encoding="utf-8"))
        self.assertFalse(matrix["contains_real_patient_data"])
        expected = {
            token for case in matrix["cases"] for token in case["expected"]
        }
        self.assertTrue(
            {
                "no_automatic_question",
                "kr_core_precedence_preserved",
                "at_code_retained_as_local",
                "rule_graph_remains_authoritative",
                "definition_not_order",
                "runtime_continues_with_compiled_package",
                "fixed_questionnaire_excluded",
            }
            <= expected
        )

    def test_repository_audit_passes(self):
        report = run_audit()
        self.assertTrue(report["passed"])
        self.assertEqual(report["framework_count"], 10)
        self.assertEqual(report["projection_profile_count"], 11)
        self.assertEqual(report["projection_emission"], "metadata_only_not_emitted")

    def test_gpt_export_exposes_response_free_reference_metadata(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build_gpt_export(ROOT, output_path)
            paths = {item["path"] for item in manifest["resources"]}
            expected = {
                "/gpt/interoperability/computable-knowledge-policy.json",
                "/gpt/interoperability/computable-knowledge-registry.json",
                "/gpt/interoperability/computable-knowledge-coverage.json",
            }
            self.assertTrue(expected <= paths)
            for path in expected:
                resource = json.loads(
                    (output_path / path.removeprefix("/gpt/")).read_text(
                        encoding="utf-8"
                    )
                )
                self.assertFalse(resource["contains_patient_responses"])
        openapi = (ROOT / "docs/gpt/openapi.yaml").read_text(encoding="utf-8")
        self.assertIn("operationId: getComputableKnowledgeStandardsPolicy", openapi)
        self.assertIn("operationId: getComputableKnowledgeStandardsRegistry", openapi)
        self.assertIn("operationId: getComputableKnowledgeStandardsCoverage", openapi)


if __name__ == "__main__":
    unittest.main()
