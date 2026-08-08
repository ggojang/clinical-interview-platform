import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CATALOG = (
    ROOT / "docs" / "gpt" / "test-catalogs" / "health-screening-packages"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class HealthScreeningPackageCatalogTests(unittest.TestCase):
    def test_test_catalog_is_versioned_isolated_and_response_free(self):
        registry = load(CATALOG / "registry.json")
        self.assertEqual(
            registry["catalog_id"], "test.kr-health-screening-center-packages"
        )
        self.assertEqual(registry["lifecycle_status"], "test")
        self.assertEqual(registry["review_status"], "unreviewed")
        self.assertEqual(registry["clinical_use_status"], "limited")
        self.assertTrue(registry["test_only"])
        self.assertFalse(registry["contains_patient_responses"])
        version = registry["current_version"]
        self.assertTrue(version)
        self.assertEqual(
            sum(item["status"] == "active" for item in registry["versions"]), 1
        )
        self.assertTrue(registry["privacy_boundary"]["forbidden_action_payloads"])

        version_dir = CATALOG / "versions" / version
        metadata = load(version_dir / "metadata.json")
        self.assertEqual(metadata["catalog_version"], version)
        self.assertEqual(metadata["counts"]["regions"], 17)
        self.assertGreater(metadata["counts"]["packages"], 0)
        self.assertFalse(metadata["contains_patient_responses"])
        self.assertRegex(metadata["source"]["sha256"], r"^[0-9a-f]{64}$")

    def test_catalog_region_pages_are_bounded_and_all_details_resolve(self):
        registry = load(CATALOG / "registry.json")
        version = registry["current_version"]
        version_dir = CATALOG / "versions" / version
        metadata = load(version_dir / "metadata.json")
        seen = set()
        for region in metadata["regions"]:
            region_index = load(ROOT / "docs" / region["path"].lstrip("/"))
            self.assertEqual(
                region_index["package_count"], region["package_count"]
            )
            self.assertEqual(
                region_index["page_count"], len(region_index["pages"])
            )
            page_total = 0
            for page_ref in region_index["pages"]:
                page_path = ROOT / "docs" / page_ref["path"].lstrip("/")
                page = load(page_path)
                self.assertLessEqual(page["package_count"], 50)
                self.assertLess(page_path.stat().st_size, 90_000)
                page_total += page["package_count"]
                for summary in page["packages"]:
                    package_id = summary["package_id"]
                    self.assertRegex(package_id, r"^pkg-[0-9a-f]{16}$")
                    self.assertNotIn(package_id, seen)
                    seen.add(package_id)
                    detail = load(
                        version_dir / "packages" / f"{package_id}.json"
                    )
                    self.assertEqual(detail["package_id"], package_id)
                    self.assertTrue(detail["variants"])
                    self.assertTrue(
                        detail["use_boundary"]["candidate_comparison_only"]
                    )
                    self.assertTrue(
                        detail["use_boundary"][
                            "confirm_current_items_price_and_eligibility_with_institution"
                        ]
                    )
                    self.assertTrue(
                        all(
                            "row" in variant["source"]
                            and "url" in variant["source"]
                            for variant in detail["variants"]
                        )
                    )
            self.assertEqual(page_total, region_index["package_count"])
        self.assertEqual(len(seen), metadata["counts"]["packages"])

    def test_catalog_action_and_gpt_instruction_privacy_contract(self):
        openapi = (ROOT / "docs/gpt/openapi.yaml").read_text(encoding="utf-8")
        for operation in (
            "getHealthScreeningPackageCatalogRegistry",
            "getHealthScreeningPackageCatalogMetadata",
            "getHealthScreeningPackageRegionMetadata",
            "getHealthScreeningPackageRegionPage",
            "getHealthScreeningPackageDetail",
        ):
            self.assertIn(f"operationId: {operation}", openapi)
        instructions = (ROOT / "docs/gpt/GPT_INSTRUCTIONS.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("never send age, sex or gender", instructions)
        self.assertIn("isolated test data, not Clinical Knowledge", instructions)
        self.assertIn("must be confirmed directly with the institution", instructions)

    def test_synthetic_catalog_action_simulation_keeps_matching_local(self):
        simulation = load(
            ROOT
            / "simulation/workflows/health-screening-package-catalog-action-cases.json"
        )
        self.assertFalse(simulation["contains_real_patient_data"])
        case = simulation["cases"][0]
        self.assertEqual(
            case["expected_action_parameters_only"],
            ["catalogVersion", "regionId", "page", "packageId"],
        )
        self.assertIn("patient_answers", case["forbidden_action_payloads"])
        self.assertIn("budget", case["forbidden_action_payloads"])
        self.assertTrue(
            case["expected_local_processing"][
                "clinical_and_budget_matching_occurs_in_conversation_state"
            ]
        )
        self.assertTrue(
            case["expected_local_processing"][
                "all_declared_region_pages_are_considered_before_claiming_lowest_price"
            ]
        )
        self.assertFalse(
            case["failure_behavior"]["invented_fallback_package"]
        )
