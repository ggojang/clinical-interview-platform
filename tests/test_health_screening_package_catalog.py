import json
from pathlib import Path
import re
import unittest

from runtime.screening_recommendation import ScreeningRecommendationSession


ROOT = Path(__file__).resolve().parents[1]
CATALOG = (
    ROOT / "docs" / "gpt" / "test-catalogs" / "health-screening-packages"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class HealthScreeningPackageCatalogTests(unittest.TestCase):
    @staticmethod
    def _answer_for(fact_id: str) -> str:
        return {
            "patient.age_years": "55",
            "patient.sex_for_clinical_care": "남성",
            "history.condition.current": "고혈압",
            "medication.current": "고혈압약",
            "history.family": "없음",
            "history.cancer.family": "아버지 대장암",
            "screening.current_symptom": "없음",
            "patient.smoking.status": "평생 비흡연",
            "patient.smoking.pack_years": "0 갑년",
            "screening.focus": "암 검진",
            "screening.region": "서울",
            "screening.budget_preference": "가장 저렴한 후보 우선",
            "screening.nhis_questionnaire_choice": "지금은 추가 문진만 진행",
        }.get(fact_id, "없음")

    def _finish(self, session, state):
        while state["phase"] != "recommendation":
            fact_id = state["selected_question"]["fact_id"]
            state = session.process(self._answer_for(fact_id))
        return state

    def test_local_recommendation_workflow_is_bounded_and_includes_lowest_candidate(self):
        session = ScreeningRecommendationSession("screening-test")
        state = session.process("가족 중 대장암이 있어 걱정됩니다")
        self.assertEqual(state["selected_question"]["fact_id"], "screening.focus")
        self.assertEqual(state["selected_question"]["answer_options"][0]["internal_value"], "cancer")
        self.assertEqual(session.answers["history.cancer.family"], "가족 중 대장암이 있어 걱정됩니다")
        state = self._finish(session, state)
        recommendation = state["recommendation"]
        self.assertEqual(state["phase"], "recommendation")
        self.assertEqual(recommendation["status"], "candidate_comparison_ready")
        self.assertLessEqual(len(recommendation["candidates"]), 4)
        self.assertTrue(any(item["lowest_price_candidate"] for item in recommendation["candidates"]))
        self.assertFalse(recommendation["selection_basis"]["medical_necessity_inferred"])
        self.assertFalse(
            recommendation["selection_basis"]["patient_profile_transmitted_to_catalog_action"]
        )
        self.assertIn(
            "knowledge.kr-national-health-screening.2026",
            recommendation["selection_basis"]["knowledge_sources"],
        )
        self.assertIn(
            "history.cancer.family",
            recommendation["selection_basis"]["reused_fact_ids"],
        )
        self.assertTrue(all(item["source_url"] for item in recommendation["candidates"]))
        self.assertTrue(all(item["match_reasons"] for item in recommendation["candidates"]))
        self.assertIn("해당 기관에 직접 확인", recommendation["limitations_ko"])
        closed = session.close()
        self.assertTrue(closed["response_state_purged"])
        self.assertFalse(session.answers)

    def test_invalid_region_is_reprompted_without_consuming_an_answer(self):
        session = ScreeningRecommendationSession("screening-invalid")
        state = session.process("특별히 걱정되는 문제는 없습니다")
        while state["selected_question"]["fact_id"] != "screening.region":
            state = session.process(self._answer_for(state["selected_question"]["fact_id"]))
        answer_count = state["answers_collected"]
        state = session.process("아무 지역")
        self.assertEqual(state["answers_collected"], answer_count)
        self.assertEqual(state["selected_question"]["fact_id"], "screening.region")

    def test_age_intent_reuses_shared_age_and_sex_questions_before_package_focus(self):
        session = ScreeningRecommendationSession("screening-age")
        state = session.process("나이에 적절한 검진을 추천받고 싶음")
        age_question = state["selected_question"]
        self.assertEqual(age_question["fact_id"], "patient.age_years")
        self.assertEqual(age_question["template_id"], "question.clinician-context.age")
        self.assertEqual(
            age_question["knowledge_source_id"],
            "knowledge.shared.clinician-submission-context",
        )
        state = session.process("55세")
        sex_question = state["selected_question"]
        self.assertEqual(sex_question["fact_id"], "patient.sex_for_clinical_care")
        self.assertEqual(sex_question["template_id"], "question.clinician-context.sex")
        self.assertEqual([item["display_ko"] for item in sex_question["answer_options"][:2]], ["여성", "남성"])
        state = session.process("2")
        self.assertEqual(state["selected_question"]["fact_id"], "screening.focus")
        self.assertEqual(session.answers["patient.age_years"], "55")
        self.assertEqual(session.answers["patient.sex_for_clinical_care"], "male")

    def test_family_sah_reuses_family_fact_and_routes_to_cardiovascular_focus(self):
        session = ScreeningRecommendationSession("screening-family-sah")
        state = session.process("어머님이 뇌출혈(SAH)로 돌아가심")
        self.assertEqual(session.answers["history.family"], "어머님이 뇌출혈(SAH)로 돌아가심")
        self.assertEqual(session.inferred_focus_from_concern, "cardiovascular")
        self.assertEqual(state["selected_question"]["fact_id"], "screening.focus")
        self.assertEqual(
            state["selected_question"]["answer_options"][0]["internal_value"],
            "cardiovascular",
        )
        self.assertIn("뇌·심혈관", state["selected_question"]["text"])

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

    def test_custom_gpt_runtime_openapi_stays_within_operation_limit(self):
        runtime = (ROOT / "docs/gpt/openapi-runtime.yaml").read_text(
            encoding="utf-8"
        )
        operation_ids = re.findall(
            r"^\s+operationId:\s+(\S+)\s*$", runtime, re.MULTILINE
        )
        self.assertLessEqual(len(operation_ids), 30)
        self.assertEqual(len(operation_ids), len(set(operation_ids)))
        self.assertIn("operationId: getHealthScreeningPackageCatalogRegistry", runtime)
        self.assertIn("operationId: getHealthScreeningPackageDetail", runtime)
        self.assertNotIn("/gpt/interoperability/uscdi-v6-core.json:", runtime)

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
