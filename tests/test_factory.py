from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from compiler.build_package import (
    CompilationError,
    compile_package,
    semantic_digest,
    validate_package,
)
from builder.build_knowledge import build as build_knowledge
from evaluation.run_evaluation import run as run_evaluation
from runtime.memory import ClinicalMemory
from runtime.package import (
    ABDOMINAL_PAIN_PACKAGE, BACK_PAIN_PACKAGE, BOWEL_SYMPTOMS_PACKAGE, CHEST_PAIN_PACKAGE, DEFAULT_PACKAGE,
    DIZZINESS_SYNCOPE_PACKAGE, DYSPNEA_PACKAGE, FEVER_PACKAGE, HEADACHE_PACKAGE,
    DIABETES_FOLLOW_UP_PACKAGE, EAR_HEARING_SYMPTOMS_PACKAGE, EDEMA_PACKAGE, EYE_SYMPTOMS_PACKAGE, FATIGUE_PACKAGE, FOCAL_WEAKNESS_NUMBNESS_PACKAGE, HYPERTENSION_FOLLOW_UP_PACKAGE, JOINT_LIMB_COMPLAINT_PACKAGE, MEDICATION_REVIEW_PACKAGE, MENTAL_HEALTH_SLEEP_PACKAGE, PALPITATIONS_PACKAGE, REPRODUCTIVE_GENITAL_SYMPTOMS_PACKAGE, SKIN_COMPLAINT_PACKAGE,
    ALLERGY_CONCERN_PACKAGE, ANEMIA_CONCERN_FOLLOW_UP_PACKAGE, ASTHMA_COPD_FOLLOW_UP_PACKAGE, BREAST_SYMPTOMS_PACKAGE, DYSPEPSIA_REFLUX_PACKAGE, THYROID_CONCERN_FOLLOW_UP_PACKAGE, KIDNEY_FUNCTION_CKD_FOLLOW_UP_PACKAGE, LIVER_FUNCTION_CHRONIC_FOLLOW_UP_PACKAGE, EPISTAXIS_PACKAGE, GAIT_FALLS_CONCERN_PACKAGE, LUMP_LYMPH_NODE_PACKAGE, MEMORY_COGNITIVE_CONCERN_PACKAGE, MENSTRUAL_UTERINE_BLEEDING_PACKAGE, NECK_PAIN_PACKAGE, ORAL_DENTAL_SYMPTOMS_PACKAGE, PEDIATRIC_GROWTH_DEVELOPMENT_PACKAGE, PREGNANCY_POSTPARTUM_CONCERN_PACKAGE, SEIZURE_EVENT_FOLLOW_UP_PACKAGE, TREMOR_MOVEMENT_CONCERN_PACKAGE, WOUND_MINOR_INJURY_PACKAGE, UPPER_RESPIRATORY_SYMPTOMS_PACKAGE, URINARY_SYMPTOMS_PACKAGE, WEIGHT_CONSTITUTIONAL_CHANGE_PACKAGE,
    VOMITING_DIARRHEA_PACKAGE,
    PackageLoadError, load_package,
)
from runtime.session import InterviewSession
from sources.check_refresh import due_sources
from tools.validator.audit_expansion_queue import run as run_expansion_audit


class CompilerTests(unittest.TestCase):
    def test_fever_builder_does_not_absorb_nested_fatigue_fragment(self):
        report = build_knowledge("fever")
        self.assertEqual(
            [item["fragment"] for item in report["fragments"]],
            ["knowledge/generated/systemic/fever.json"],
        )

    def test_next_gap_queue_tracks_unimplemented_previsit_packages(self):
        root = Path(__file__).resolve().parents[1]
        queue = json.loads(
            (root / "knowledge/catalog/planned-package-work-queue-v0.4.json")
            .read_text(encoding="utf-8")
        )
        catalog = json.loads(
            (root / "knowledge/catalog/primary-care-rfe.json")
            .read_text(encoding="utf-8")
        )
        queued = {
            item["rfe"] for item in queue["order"]
            if item["state"] == "planned"
        }
        planned = {
            item["id"] for item in catalog["entries"]
            if item.get("implementation_status") == "planned"
        }
        self.assertEqual(queued, planned)
        self.assertEqual(
            next(item for item in queue["order"] if item["rfe"] == "rfe.seizure_event_follow_up")["state"],
            "implemented_unreviewed",
        )
        self.assertEqual(
            next(item for item in queue["order"] if item["rfe"] == "rfe.gait_falls_concern")["state"],
            "implemented_unreviewed",
        )
        self.assertEqual(
            next(item for item in queue["order"] if item["rfe"] == "rfe.epistaxis")["state"],
            "implemented_unreviewed",
        )
        self.assertEqual(
            next(item for item in queue["order"] if item["rfe"] == "rfe.pediatric_growth_development")["state"],
            "implemented_unreviewed",
        )
        self.assertEqual(
            next(item for item in queue["order"] if item["rfe"] == "rfe.tremor_movement_concern")["state"],
            "implemented_unreviewed",
        )
        self.assertEqual(
            next(item for item in queue["order"] if item["rfe"] == "rfe.neck_pain")["state"],
            "implemented_unreviewed",
        )
        self.assertEqual(
            next(item for item in queue["order"] if item["rfe"] == "rfe.menstrual_uterine_bleeding")["state"],
            "implemented_unreviewed",
        )
        self.assertIn(
            "clinician handoff includes collected required missing and conflicting package Facts",
            queue["definition_of_done"],
        )

    def test_grouped_expansion_queue_passes_release_gate_audit(self):
        report = run_expansion_audit()
        self.assertTrue(report["passed"])
        self.assertEqual(report["entry_count"], 10)
        self.assertEqual(report["queue_status"], "materialized_unreviewed")

    def test_compilation_is_deterministic(self):
        first = compile_package()
        second = compile_package()
        self.assertEqual(first["semantic_digest"], second["semantic_digest"])
        self.assertEqual(first, second)

    def test_production_rejects_unreviewed_safety(self):
        for profile in (
            "cough", "fever", "dyspnea", "abdominal_pain", "chest_pain",
            "headache",
            "dizziness_syncope",
            "vomiting_diarrhea",
            "urinary_symptoms",
            "fatigue",
            "back_pain",
            "skin_complaint",
            "medication_review",
            "upper_respiratory_symptoms",
            "palpitations",
            "bowel_symptoms",
            "focal_weakness_numbness",
            "joint_limb_complaint",
            "mental_health_sleep",
            "edema",
            "hypertension_follow_up",
            "weight_constitutional_change",
            "reproductive_genital_symptoms",
            "eye_symptoms",
            "ear_hearing_symptoms",
            "diabetes_follow_up",
            "oral_dental_symptoms",
            "wound_minor_injury",
            "memory_cognitive_concern",
            "pregnancy_postpartum_concern",
            "allergy_concern",
            "asthma_copd_follow_up",
            "lump_lymph_node",
            "dyspepsia_reflux",
            "thyroid_concern_follow_up",
            "anemia_concern_follow_up",
            "seizure_event_follow_up",
            "gait_falls_concern",
            "epistaxis",
            "pediatric_growth_development",
            "tremor_movement_concern",
            "neck_pain",
            "menstrual_uterine_bleeding",
            "kidney_function_ckd_follow_up",
            "liver_function_chronic_follow_up",
            "breast_symptoms",
        ):
            with self.subTest(profile=profile), self.assertRaises(CompilationError):
                compile_package(production=True, profile=profile)

    def test_tampered_package_is_rejected(self):
        package = compile_package()
        package["coverage"]["simulation_count"] = 999
        with self.assertRaises(CompilationError):
            validate_package(package)

    def test_hypothesis_never_targets_question(self):
        package = compile_package()
        nodes = {node["id"]: node for node in package["knowledge_graph"]["nodes"]}
        for edge in package["knowledge_graph"]["edges"]:
            self.assertFalse(
                nodes[edge["from"]]["type"] == "Hypothesis"
                and nodes[edge["to"]]["type"] == "QuestionTemplate"
            )

    def test_every_graph_object_has_provenance(self):
        package = compile_package()
        for node in package["knowledge_graph"]["nodes"]:
            self.assertIn("provenance", node)
        for edge in package["knowledge_graph"]["edges"]:
            self.assertIn("provenance", edge)
        for rule in package["rule_graph"]["rules"]:
            self.assertIn("provenance", rule)

    def test_source_artifacts_have_materialized_digests(self):
        package = compile_package()
        for artifact in package["source_manifest"]["artifacts"]:
            self.assertRegex(artifact["digest"], r"^sha256:[a-f0-9]{64}$")

    def test_generated_research_knowledge_is_question_complete(self):
        package = compile_package()
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 35)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        generated = [
            node for node in package["knowledge_graph"]["nodes"]
            if node.get("source_manifest") == "source-manifest.respiratory-cough-research"
        ]
        self.assertTrue(generated)
        self.assertTrue(all(node["status"] == "research_only" for node in generated))
        self.assertTrue(all(node["provenance"]["review_status"] == "unreviewed" for node in generated))

    def test_refresh_scheduler_uses_source_specific_cadence(self):
        root = Path(__file__).resolve().parents[1]
        cough_manifest = json.loads(
            (root / "sources/manifests/respiratory-cough-research.json").read_text(
                encoding="utf-8"
            )
        )
        artifacts = {item["id"]: item for item in cough_manifest["artifacts"]}
        daily_date = date.fromisoformat(
            artifacts["source.ers.chronic-cough.2020"]["next_monitor_at"]
        )
        daily = due_sources(daily_date)
        daily_ids = {item["source_id"] for item in daily["due"]}
        self.assertIn("source.ers.chronic-cough.2020", daily_ids)
        self.assertIn("source.gina.strategy.2026", daily_ids)
        self.assertNotIn("source.nice.ng120", daily_ids)
        weekly_date = date.fromisoformat(
            artifacts["source.nice.ng120"]["next_monitor_at"]
        )
        weekly = due_sources(weekly_date)
        weekly_ids = {item["source_id"] for item in weekly["due"]}
        self.assertIn("source.nice.ng120", weekly_ids)
        self.assertIn("source.cdc.common-cold.2026", weekly_ids)
        dyspnea_manifest = (
            Path(__file__).resolve().parents[1]
            / "sources/manifests/primary-care-dyspnea-research.json"
        )
        dyspnea_daily = due_sources(
            date.fromisoformat("2026-07-15"), dyspnea_manifest
        )
        dyspnea_daily_ids = {item["source_id"] for item in dyspnea_daily["due"]}
        self.assertNotIn("source.nice.ng158.vte", dyspnea_daily_ids)
        self.assertNotIn("source.nhs.shortness-of-breath", dyspnea_daily_ids)
        stom_manifest = (
            Path(__file__).resolve().parents[1]
            / "sources/manifests/stom-terminology.json"
        )
        stom = json.loads(stom_manifest.read_text(encoding="utf-8"))
        stom_due_date = date.fromisoformat(stom["artifacts"][0]["next_monitor_at"])
        stom_monthly = due_sources(stom_due_date, stom_manifest)
        self.assertEqual(
            {item["source_id"] for item in stom_monthly["due"]},
            {"source.stom.fhir-r4-terminology-server"},
        )
        self.assertEqual(stom_monthly["due"][0]["monitor_interval_days"], 30)

    def test_nice_sources_use_the_dedicated_weekly_monitor_profile(self):
        root = Path(__file__).resolve().parents[1]
        for path in (root / "sources/manifests").glob("*-research.json"):
            manifest = json.loads(path.read_text(encoding="utf-8"))
            for artifact in manifest.get("artifacts", []):
                if artifact.get("publisher") != "NICE":
                    continue
                with self.subTest(path=path.name, source=artifact["id"]):
                    self.assertEqual(artifact["monitor_profile"], "nice_guidance")
                    self.assertEqual(artifact["monitor_interval_days"], 7)
                    if artifact.get("last_monitored_at"):
                        expected = (
                            date.fromisoformat(artifact["last_monitored_at"])
                            + timedelta(days=7)
                        ).isoformat()
                        self.assertEqual(artifact["next_monitor_at"], expected)

    def test_fever_package_is_deterministic_and_question_complete(self):
        first = compile_package(profile="fever")
        second = compile_package(profile="fever")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 62)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(first["coverage"]["total_safety_rules"], 12)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

        mapping = json.loads(
            (Path(__file__).resolve().parents[1]
             / "mappings/terminology/snomed-mrcm-fever.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 3)
        self.assertEqual(mapping["quantitative_observation_binding"]["code"], "8310-5")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["fever_semantics"]["sepsis_score_calculated"])
        self.assertFalse(mapping["fever_semantics"]["news2_or_mews_calculated"])

    def test_fever_reuses_shared_fact_identity(self):
        cough = compile_package()
        fever = compile_package(profile="fever")
        cough_facts = {
            node["id"] for node in cough["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        fever_facts = {
            node["id"] for node in fever["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertTrue({
            "symptom.duration", "symptom.dyspnea",
            "patient.immunocompromised", "symptom.systemic_unwellness",
        } <= cough_facts & fever_facts)

    def test_dyspnea_package_is_deterministic_and_question_complete(self):
        first = compile_package(profile="dyspnea")
        second = compile_package(profile="dyspnea")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 74)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 13)
        self.assertEqual(first["coverage"]["total_safety_rules"], 13)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(first["coverage"]["data_absent_reason_simulations"], 1)

        mapping = json.loads(
            (Path(__file__).resolve().parents[1]
             / "mappings/terminology/snomed-mrcm-dyspnea.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 4)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["dyspnea_semantics"]["diagnosis_inferred"])
        self.assertFalse(mapping["dyspnea_semantics"]["wells_score_calculated"])
        self.assertFalse(mapping["dyspnea_semantics"]["runtime_terminology_query_required"])

    def test_dyspnea_reuses_cross_package_fact_identity(self):
        cough = compile_package()
        fever = compile_package(profile="fever")
        dyspnea = compile_package(profile="dyspnea")
        fact_sets = []
        for package in (cough, fever, dyspnea):
            fact_sets.append({
                node["id"] for node in package["knowledge_graph"]["nodes"]
                if node["type"] == "Fact"
            })
        self.assertTrue({"symptom.duration", "symptom.dyspnea"} <= set.intersection(*fact_sets))
        self.assertTrue({"symptom.chest_pain", "symptom.hemoptysis", "symptom.wheeze"} <= fact_sets[0] & fact_sets[2])

    def test_abdominal_pain_package_is_deterministic_and_question_complete(self):
        first = compile_package(profile="abdominal_pain")
        second = compile_package(profile="abdominal_pain")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 75)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 16)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 16)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_abdominal_pain_mrcm_is_build_time_metadata_only(self):
        package = compile_package(profile="abdominal_pain")
        facts = {
            node["id"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        location = facts["symptom.abdominal_pain.location"]
        self.assertEqual(
            location["terminology_binding"]["attribute_code"], "363698007"
        )
        self.assertEqual(
            location["mrcm_validation"]["status"], "provisional_pass"
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-abdominal-pain.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["validation"]["raw_response_cached"])

    def test_chest_pain_package_is_deterministic_and_question_complete(self):
        first = compile_package(profile="chest_pain")
        second = compile_package(profile="chest_pain")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 32)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 12)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_chest_pain_mrcm_is_build_time_metadata_only(self):
        package = compile_package(profile="chest_pain")
        facts = {
            node["id"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(
            facts["symptom.chest_pain.location"]["terminology_binding"]["focus_code"],
            "29857009",
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-chest-pain.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["validation"]["raw_response_cached"])

    def test_headache_package_is_deterministic_and_question_complete(self):
        first = compile_package(profile="headache")
        second = compile_package(profile="headache")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 32)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 10)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 10)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_headache_mrcm_is_build_time_metadata_only(self):
        package = compile_package(profile="headache")
        facts = {
            node["id"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(
            facts["symptom.headache.location"]["terminology_binding"]["focus_code"],
            "25064002",
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-headache.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_dizziness_syncope_package_is_complete_and_deterministic(self):
        first = compile_package(profile="dizziness_syncope")
        second = compile_package(profile="dizziness_syncope")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 73)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 20)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 20)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_dizziness_syncope_mrcm_preserves_unsupported_syncope_result(self):
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-dizziness-syncope.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(mapping["validation"]["result"], "partial_provisional_pass")
        self.assertEqual(mapping["unsupported_checks"][0]["focus_code"], "271594007")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_vomiting_diarrhea_package_is_complete_and_deterministic(self):
        first = compile_package(profile="vomiting_diarrhea")
        second = compile_package(profile="vomiting_diarrhea")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 74)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 16)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 16)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_vomiting_diarrhea_mrcm_is_build_time_metadata_only(self):
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-vomiting-diarrhea.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_urinary_symptoms_package_is_complete_and_deterministic(self):
        first = compile_package(profile="urinary_symptoms")
        second = compile_package(profile="urinary_symptoms")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 39)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 11)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 11)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_urinary_symptoms_mrcm_is_build_time_metadata_only(self):
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-urinary-symptoms.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 5)
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_fatigue_package_is_complete_and_deterministic(self):
        first = compile_package(profile="fatigue")
        second = compile_package(profile="fatigue")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 75)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 13)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 13)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_fatigue_mrcm_is_build_time_metadata_only(self):
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-fatigue.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 2)
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_back_pain_package_is_complete_and_deterministic(self):
        first = compile_package(profile="back_pain")
        second = compile_package(profile="back_pain")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 36)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 12)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_back_pain_mrcm_is_build_time_metadata_only(self):
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-back-pain.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 3)
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_skin_complaint_package_is_complete_and_deterministic(self):
        first = compile_package(profile="skin_complaint")
        second = compile_package(profile="skin_complaint")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 38)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 10)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 10)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_skin_complaint_mrcm_is_build_time_metadata_only(self):
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-skin-complaint.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 3)
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_medication_review_package_is_complete_and_deterministic(self):
        first = compile_package(profile="medication_review")
        second = compile_package(profile="medication_review")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 36)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 9)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 9)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_medication_review_mrcm_is_build_time_metadata_only(self):
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-medication-review.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 1)
        self.assertEqual(mapping["validation"]["attribute_count_returned"], 24)
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_upper_respiratory_package_is_complete_and_deterministic(self):
        first = compile_package(profile="upper_respiratory_symptoms")
        second = compile_package(profile="upper_respiratory_symptoms")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 41)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 10)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 10)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_upper_respiratory_mrcm_preserves_unsupported_nasal_discharge(self):
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-upper-respiratory-symptoms.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 5)
        self.assertEqual(mapping["validation"]["result"], "partial_provisional_pass")
        self.assertEqual(mapping["unsupported_checks"][0]["focus_code"], "64531003")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_palpitations_package_is_complete_and_deterministic(self):
        first = compile_package(profile="palpitations")
        second = compile_package(profile="palpitations")
        self.assertEqual(first, second)
        facts = {node["id"] for node in first["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(len(facts), 36)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 9)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 9)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_palpitations_mrcm_is_build_time_metadata_only(self):
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-palpitations.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 2)
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_bowel_symptoms_package_is_complete_and_deterministic(self):
        first = compile_package(profile="bowel_symptoms"); second = compile_package(profile="bowel_symptoms")
        self.assertEqual(first, second)
        facts = {node["id"] for node in first["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(len(facts), 35)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 9)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 9)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

    def test_bowel_symptoms_mrcm_preserves_unsupported_constipation(self):
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-bowel-symptoms.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 4)
        self.assertEqual(mapping["validation"]["result"], "partial_provisional_pass")
        self.assertEqual(mapping["unsupported_checks"][0]["focus_code"], "14760008")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_focal_neurology_package_is_complete(self):
        package = compile_package(profile="focal_weakness_numbness")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 32); self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 11)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 11)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])

    def test_joint_limb_package_is_complete(self):
        package = compile_package(profile="joint_limb_complaint")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 39); self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])

    def test_mental_health_sleep_package_is_complete(self):
        package = compile_package(profile="mental_health_sleep")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 39); self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 11)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 11)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])

    def test_edema_package_is_complete(self):
        package = compile_package(profile="edema")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 37)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 10)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 10)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])

    def test_edema_mrcm_is_build_time_metadata_only(self):
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-edema.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 5)
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_hypertension_follow_up_package_is_complete(self):
        package = compile_package(profile="hypertension_follow_up")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 38)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 9)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 9)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])

    def test_hypertension_mrcm_remains_terminology_only(self):
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-hypertension-follow-up.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 3)
        self.assertEqual(mapping["validation"]["result"], "partial_provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_weight_constitutional_package_is_complete(self):
        package = compile_package(profile="weight_constitutional_change")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 38)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 10)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 10)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])

    def test_weight_constitutional_mrcm_preserves_unsupported_weight_loss(self):
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-weight-constitutional-change.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 4)
        self.assertEqual(mapping["unsupported_checks"][0]["focus_code"], "89362005")
        self.assertEqual(mapping["validation"]["result"], "partial_provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_reproductive_genital_package_is_complete(self):
        package = compile_package(profile="reproductive_genital_symptoms")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 51)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 15)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 15)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "genital.primary_symptom_group")
        self.assertEqual(set(conditional["cases"]), {"vaginal_vulvar_pelvic", "penile_urethral", "testicular_scrotal"})

    def test_reproductive_genital_mrcm_is_build_time_only(self):
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-reproductive-genital-symptoms.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 4)
        self.assertEqual(mapping["validation"]["result"], "provisional_pass")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_eye_symptoms_package_is_complete_and_lateralizable(self):
        package = compile_package(profile="eye_symptoms")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 45)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 15)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 15)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "eye.primary_symptom_group")
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-eye-symptoms.json").read_text(encoding="utf-8"))
        self.assertTrue(mapping["laterality"]["member"])
        self.assertEqual(mapping["laterality"]["reference_set"], "723264001")
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_ear_hearing_symptoms_package_is_complete(self):
        package = compile_package(profile="ear_hearing_symptoms")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 46)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "ear.primary_symptom_group")
        self.assertEqual(set(conditional["cases"]), {"ear_pain_infection", "hearing_change", "discharge_trauma", "tinnitus", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-ear-hearing-symptoms.json").read_text(encoding="utf-8"))
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_diabetes_follow_up_package_is_complete(self):
        package = compile_package(profile="diabetes_follow_up")
        facts = {n["id"] for n in package["knowledge_graph"]["nodes"] if n["type"] == "Fact"}
        self.assertEqual(len(facts), 54)
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertEqual(package["coverage"]["total_safety_rules"], 11)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 11)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        type_conditional, focus_conditional = package["interview_completion_policy"]["conditional_required_facts"]
        self.assertEqual(type_conditional["selector_fact"], "diabetes.type_or_context")
        self.assertEqual(set(type_conditional["cases"]), {"type1", "type2", "gestational_or_pregnancy", "other", "unclear"})
        self.assertEqual(focus_conditional["selector_fact"], "diabetes.primary_follow_up_focus")
        self.assertEqual(set(focus_conditional["cases"]), {"glycemic_control", "medication_hypoglycemia", "complication_screening", "device_education", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-diabetes-follow-up.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 7)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_oral_dental_symptoms_package_is_complete(self):
        package = compile_package(profile="oral_dental_symptoms")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 60)
        self.assertEqual(package["coverage"]["total_safety_rules"], 20)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 20)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "oral.primary_symptom_group")
        self.assertEqual(
            set(conditional["cases"]),
            {"tooth_pain", "swelling_infection", "lesion_mucosa", "gum_periodontal", "trauma_procedure", "other_unclear"},
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-oral-dental-symptoms.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 10)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["laterality"]["postcoordination_asserted"])

    def test_wound_minor_injury_package_is_complete(self):
        package = compile_package(profile="wound_minor_injury")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 60)
        self.assertEqual(package["coverage"]["total_safety_rules"], 22)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 22)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "injury.primary_group")
        self.assertEqual(
            set(conditional["cases"]),
            {"open_wound", "burn", "blunt_sprain", "bite_puncture", "head_injury", "other_unclear"},
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-wound-minor-injury.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 10)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["laterality"]["postcoordination_asserted"])

    def test_memory_cognitive_concern_package_is_complete(self):
        package = compile_package(profile="memory_cognitive_concern")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 60)
        self.assertEqual(package["coverage"]["total_safety_rules"], 17)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 17)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "cognition.primary_concern_group")
        self.assertEqual(
            set(conditional["cases"]),
            {"memory", "acute_confusion", "executive_language", "behavior_perception", "function_safety", "other_unclear"},
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-memory-cognitive-concern.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 8)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_pregnancy_postpartum_concern_package_is_complete(self):
        package = compile_package(profile="pregnancy_postpartum_concern")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 60)
        self.assertTrue({
            "pregnancy.obstetric_gravidity_total",
            "pregnancy.obstetric_parity_total",
            "pregnancy.obstetric_parity_threshold_as_recorded",
            "pregnancy.obstetric_term_birth_count",
            "pregnancy.obstetric_preterm_birth_count",
            "pregnancy.obstetric_spontaneous_loss_count",
            "pregnancy.obstetric_induced_termination_count",
            "pregnancy.obstetric_ectopic_count",
            "pregnancy.obstetric_molar_pregnancy_count",
            "pregnancy.obstetric_living_children_count",
            "pregnancy.prior_delivery_modes_and_caesarean_count",
            "pregnancy.prior_obstetric_complications",
            "pregnancy.prior_fetal_neonatal_outcomes",
            "pregnancy.estimated_due_date_and_dating_method",
        }.issubset(facts))
        self.assertEqual(package["coverage"]["total_safety_rules"], 23)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 23)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "pregnancy.primary_concern_group")
        self.assertEqual(
            set(conditional["cases"]),
            {"early_pain_bleeding", "later_fetal_labour", "maternal_medical", "postpartum_physical", "mental_feeding", "other_unclear"},
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-pregnancy-postpartum-concern.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 10)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_allergy_concern_package_is_complete(self):
        package = compile_package(profile="allergy_concern")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 45)
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "allergy.primary_group")
        self.assertEqual(
            set(conditional["cases"]),
            {"acute_systemic", "skin_angioedema", "respiratory", "food", "drug", "sting_contact", "other_unclear"},
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-allergy-concern.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 10)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_asthma_copd_follow_up_package_is_complete(self):
        package = compile_package(profile="asthma_copd_follow_up")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 60)
        self.assertEqual(package["coverage"]["total_safety_rules"], 13)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 13)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "resp_followup.condition_group")
        self.assertEqual(
            set(conditional["cases"]),
            {"asthma", "copd", "asthma_copd_overlap", "uncertain", "other_unclear"},
        )
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-asthma-copd-follow-up.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(len(mapping["focus_concepts"]), 9)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_lump_lymph_node_package_is_complete(self):
        package = compile_package(profile="lump_lymph_node")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 55)
        self.assertEqual(package["coverage"]["total_safety_rules"], 15)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 15)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "lump.primary_group")
        self.assertEqual(set(conditional["cases"]), {"lymph_node", "skin_subcutaneous", "deep_soft_tissue", "breast_axilla", "neck", "groin_scrotal", "abdominal_pelvic", "bone", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-lump-lymph-node.json").read_text(encoding="utf-8"))
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["laterality"]["postcoordination_asserted"])
        pain = next(node for node in package["knowledge_graph"]["nodes"] if node["id"] == "lump.pain_nrs")
        self.assertEqual(pain["scale"]["type"], "NRS")
        self.assertIn("lump.pain_nrs", package["interview_completion_policy"]["must_be_known_facts"])

    def test_dyspepsia_reflux_package_is_complete(self):
        package = compile_package(profile="dyspepsia_reflux")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 45)
        self.assertEqual(package["coverage"]["total_safety_rules"], 13)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 13)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "dyspepsia.primary_group")
        self.assertEqual(set(conditional["cases"]), {"heartburn_reflux", "epigastric_pain_burning", "postprandial_fullness_early_satiety", "nausea_belching_bloating", "known_gord_or_ulcer_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-dyspepsia-reflux.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 6)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        pain = next(node for node in package["knowledge_graph"]["nodes"] if node["id"] == "dyspepsia.pain_nrs")
        self.assertEqual(pain["scale"]["type"], "NRS")
        self.assertIn("dyspepsia.pain_nrs", package["interview_completion_policy"]["must_be_known_facts"])

    def test_thyroid_concern_follow_up_package_is_complete(self):
        package = compile_package(profile="thyroid_concern_follow_up")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 45)
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "thyroid.primary_group")
        self.assertEqual(set(conditional["cases"]), {"suspected_hyperthyroid", "suspected_hypothyroid", "known_hyperthyroid_followup", "known_hypothyroid_followup", "thyroid_enlargement_or_nodule", "post_treatment_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-thyroid-concern-follow-up.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 8)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["laterality"]["postcoordination_asserted"])

    def test_anemia_concern_follow_up_package_is_complete(self):
        package = compile_package(profile="anemia_concern_follow_up")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 45)
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "anemia.primary_group")
        self.assertEqual(set(conditional["cases"]), {"suspected_symptomatic", "abnormal_blood_result", "iron_deficiency", "b12_folate_or_macrocytic", "chronic_disease_or_renal", "bleeding_related", "treatment_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-anemia-concern-follow-up.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 8)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_seizure_event_follow_up_package_is_complete(self):
        package = compile_package(profile="seizure_event_follow_up")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 50)
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 2)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "seizure.primary_group")
        self.assertEqual(set(conditional["cases"]), {"first_suspected_event", "recurrent_undiagnosed_events", "known_epilepsy_breakthrough", "medication_or_treatment_followup", "alternative_event_unclear", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-seizure-event-follow-up.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 6)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["event_semantics"]["diagnosis_inferred"])

    def test_gait_falls_concern_package_is_complete(self):
        package = compile_package(profile="gait_falls_concern")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 55)
        self.assertEqual(package["coverage"]["total_safety_rules"], 13)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 13)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "falls.primary_group")
        self.assertEqual(set(conditional["cases"]), {"recent_single_fall", "recurrent_falls", "gait_balance_change_without_fall", "fear_or_near_falls", "post_fall_injury_followup", "known_mobility_condition_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-gait-falls-concern.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 5)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["event_semantics"]["predictive_fall_risk_score_calculated"])

    def test_epistaxis_package_is_complete(self):
        package = compile_package(profile="epistaxis")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 40)
        self.assertEqual(package["coverage"]["total_safety_rules"], 10)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 10)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "epistaxis.primary_group")
        self.assertEqual(set(conditional["cases"]), {"active_current_bleeding", "single_resolved_episode", "recurrent_episodes", "post_trauma_or_procedure", "antithrombotic_or_bleeding_risk", "post_treatment_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-epistaxis.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 4)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["event_semantics"]["hypertension_causality_inferred"])

    def test_pediatric_growth_development_package_is_complete(self):
        package = compile_package(profile="pediatric_growth_development")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 55)
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "pediatric.primary_group")
        self.assertEqual(set(conditional["cases"]), {"growth_trajectory", "global_development", "speech_language", "motor_coordination", "social_behavioral", "learning_school", "established_condition_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-pediatric-growth-development.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 4)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["screening_semantics"]["age_norm_interpreted_by_runtime"])
        self.assertFalse(mapping["screening_semantics"]["licensed_tool_reproduced"])

    def test_tremor_movement_concern_package_is_complete(self):
        package = compile_package(profile="tremor_movement_concern")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 55)
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "movement.primary_group")
        self.assertEqual(set(conditional["cases"]), {"isolated_tremor", "slowness_stiffness_or_parkinsonian_features", "dystonia_or_abnormal_posture", "jerks_chorea_tics_or_other_involuntary_movement", "medicine_substance_or_metabolic_context", "established_movement_disorder_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-tremor-movement-concern.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 5)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["movement_semantics"]["diagnosis_inferred"])
        self.assertFalse(mapping["movement_semantics"]["patient_video_interpreted_by_runtime"])

    def test_neck_pain_package_is_complete(self):
        package = compile_package(profile="neck_pain")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 40)
        self.assertEqual(package["coverage"]["total_safety_rules"], 10)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 10)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "neck.primary_group")
        self.assertEqual(set(conditional["cases"]), {"axial_pain_or_stiffness", "arm_radiating_or_neurologic", "post_trauma", "headache_fever_or_systemic", "established_cervical_condition_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-neck-pain.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 3)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["neck_semantics"]["diagnosis_inferred"])
        self.assertFalse(mapping["neck_semantics"]["runtime_terminology_query_required"])
        self.assertTrue(NECK_PAIN_PACKAGE.exists())

    def test_menstrual_uterine_bleeding_package_is_complete(self):
        package = compile_package(profile="menstrual_uterine_bleeding")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 50)
        self.assertEqual(package["coverage"]["total_safety_rules"], 11)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 11)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "menstrual.primary_group")
        self.assertEqual(set(conditional["cases"]), {"heavy_or_prolonged_menses", "irregular_infrequent_or_absent_menses", "intermenstrual_or_postcoital_bleeding", "dysmenorrhea_or_pelvic_pain", "postmenopausal_bleeding", "possible_pregnancy_related_bleeding", "treatment_or_procedure_followup", "other_unclear"})
        self.assertIn("menstrual.pelvic_pain_nrs", package["interview_completion_policy"]["must_be_known_facts"])
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-menstrual-uterine-bleeding.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 4)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["bleeding_semantics"]["diagnosis_inferred"])
        self.assertFalse(mapping["bleeding_semantics"]["pregnancy_status_inferred"])
        self.assertTrue(MENSTRUAL_UTERINE_BLEEDING_PACKAGE.exists())

    def test_breast_symptoms_package_is_complete(self):
        package = compile_package(profile="breast_symptoms")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 50)
        self.assertEqual(package["coverage"]["total_safety_rules"], 10)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 10)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "breast.primary_group")
        self.assertEqual(set(conditional["cases"]), {"lump_or_thickening", "pain", "nipple_discharge", "nipple_or_skin_change", "inflammation_or_lactation", "injury_procedure_or_implant", "prior_test_or_treatment_followup", "other_unclear"})
        self.assertIn("breast.pain_nrs", package["interview_completion_policy"]["must_be_known_facts"])
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-breast-symptoms.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 5)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])
        self.assertFalse(mapping["breast_semantics"]["diagnosis_inferred"])
        self.assertFalse(mapping["laterality"]["postcoordination_asserted"])
        self.assertTrue(BREAST_SYMPTOMS_PACKAGE.exists())

    def test_breast_expansion_queue_passes_release_gate_audit(self):
        root = Path(__file__).resolve().parents[1]
        report = run_expansion_audit(root / "knowledge/catalog/planned-package-work-queue-v0.5.json")
        self.assertTrue(report["passed"])
        self.assertEqual(report["entry_count"], 1)
        self.assertEqual(report["queue_status"], "materialized_unreviewed")

    def test_kidney_function_ckd_follow_up_package_is_complete(self):
        package = compile_package(profile="kidney_function_ckd_follow_up")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 45)
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "kidney.primary_group")
        self.assertEqual(set(conditional["cases"]), {"abnormal_kidney_result", "known_ckd_followup", "acute_kidney_change", "proteinuria_or_hematuria", "dialysis_followup", "kidney_transplant_followup", "structural_or_hereditary", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-kidney-function-ckd-follow-up.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 7)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])

    def test_liver_function_chronic_follow_up_package_is_complete(self):
        package = compile_package(profile="liver_function_chronic_follow_up")
        facts = {node["id"] for node in package["knowledge_graph"]["nodes"] if node["type"] == "Fact"}
        self.assertEqual(facts, set(package["indexes"]["questions_by_fact"]))
        self.assertGreaterEqual(len(facts), 40)
        self.assertEqual(package["coverage"]["total_safety_rules"], 12)
        self.assertEqual(package["coverage"]["safety_rules_with_simulations"], 12)
        self.assertEqual(package["coverage"]["uncovered_safety_rules"], [])
        self.assertEqual(package["coverage"]["data_absent_reason_simulations"], 1)
        conditional = package["interview_completion_policy"]["conditional_required_facts"][0]
        self.assertEqual(conditional["selector_fact"], "liver.primary_group")
        self.assertEqual(set(conditional["cases"]), {"abnormal_liver_tests", "steatotic_metabolic_liver", "viral_hepatitis", "alcohol_related_liver", "cirrhosis_followup", "medicine_or_supplement_injury", "post_treatment_followup", "other_unclear"})
        mapping = json.loads((Path(__file__).resolve().parents[1] / "mappings/terminology/snomed-mrcm-liver-function-chronic-follow-up.json").read_text(encoding="utf-8"))
        self.assertEqual(len(mapping["focus_concepts"]), 8)
        self.assertFalse(mapping["validation"]["clinical_rule_authority"])


class ClinicalMemoryTests(unittest.TestCase):
    def setUp(self):
        self.memory = ClinicalMemory("memory-test", "package.test", "0.1.0")
        self.memory.next_turn()

    def candidate(self, value, text, correction=False):
        return {
            "value": value,
            "raw_text": text,
            "confidence": .9,
            "correction": correction,
            "evidence": [{"speaker": "patient", "turn": self.memory.turn, "text": text}],
        }

    def test_conflict_preserves_both_values(self):
        self.memory.merge("symptom.fever", self.candidate(True, "I have a fever."))
        self.memory.next_turn()
        outcome = self.memory.merge("symptom.fever", self.candidate(False, "No fever."))
        self.assertEqual(outcome, "conflicted")
        record = self.memory.facts["symptom.fever"]
        self.assertEqual(record["status"], "conflicted")
        self.assertEqual({item["value"] for item in record["alternatives"]}, {True, False})
        self.assertEqual(len(self.memory.contradictions), 1)

    def test_explicit_correction_resolves_conflict(self):
        self.memory.merge("symptom.duration", self.candidate({"amount": 5, "unit": "day"}, "5 days"))
        self.memory.next_turn()
        self.memory.merge("symptom.duration", self.candidate({"amount": 5, "unit": "week"}, "5 weeks"))
        self.memory.next_turn()
        outcome = self.memory.merge(
            "symptom.duration",
            self.candidate({"amount": 5, "unit": "week"}, "I meant 5 weeks", correction=True),
        )
        self.assertEqual(outcome, "corrected")
        self.assertEqual(self.memory.state("symptom.duration"), "known")
        self.assertEqual(self.memory.contradictions[0]["status"], "resolved")
        self.assertGreaterEqual(len(self.memory.facts["symptom.duration"]["history"]), 3)

    def test_data_absent_reason_is_coded_and_value_is_empty(self):
        self.memory.mark_absent(
            "symptom.dyspnea", "I am not sure.", "asked-unknown"
        )
        record = self.memory.facts["symptom.dyspnea"]
        self.assertEqual(record["status"], "unknown")
        self.assertIsNone(record["value"])
        self.assertEqual(
            record["dataAbsentReason"]["system"],
            "http://terminology.hl7.org/CodeSystem/data-absent-reason",
        )
        self.assertEqual(record["dataAbsentReason"]["code"], "asked-unknown")

    def test_data_absent_correction_preserves_prior_value(self):
        self.memory.merge("symptom.fever", self.candidate(True, "Yes"))
        self.memory.next_turn()
        outcome = self.memory.mark_absent(
            "symptom.fever", "잘 모르겠어요", "asked-unknown", correction=True
        )
        record = self.memory.facts["symptom.fever"]
        self.assertEqual(outcome, "corrected")
        self.assertEqual(record["status"], "unknown")
        self.assertEqual(record["dataAbsentReason"]["code"], "asked-unknown")
        self.assertEqual(record["corrected_from"]["value"], True)
        self.assertEqual(len(record["history"]), 2)


class PackageRuntimeTests(unittest.TestCase):
    def test_off_path_comment_is_preserved_without_forcing_pending_answer(self):
        fixture = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "simulation/workflows/off-path-runtime-cases.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(fixture["contains_real_patient_data"])
        case = fixture["cases"][0]
        self.assertEqual(case["package_profile"], "cough")
        package = load_package(DEFAULT_PACKAGE)
        self.assertEqual(
            [
                item["id"]
                for item in package["clinician_submission_context"]["session_facts"]
            ],
            ["interview.additional_comment"],
        )
        session = InterviewSession(
            case["id"], package_path=DEFAULT_PACKAGE
        )
        first = session.process(case["initial_statement"])
        pending = first["selected_question"]
        detour = session.process(case["detour_text"])

        comment = detour["facts"]["interview.additional_comment"]
        self.assertEqual(comment["status"], "known")
        self.assertEqual(comment["value"], case["detour_text"])
        self.assertEqual(session.memory.state(pending["fact_id"]), "not_asked")
        self.assertEqual(
            detour["selected_question"]["fact_id"], pending["fact_id"]
        )
        self.assertEqual(
            detour["selected_question"]["question_ref"], pending["question_ref"]
        )
        self.assertEqual(
            detour["answer_clarification"]["reason"],
            case["expected"]["clarification_reason"],
        )

    def test_scoped_answer_does_not_conflict_with_known_duration(self):
        session = InterviewSession("scoped-cross-fact", package_path=FEVER_PACKAGE)
        session.memory.merge("symptom.duration", {
            "value": {"amount": 1, "unit": "day"},
            "raw_text": "1 day",
            "confidence": .97,
            "evidence": [{"speaker": "patient", "turn": 0, "text": "1 day"}],
        })
        session.last_question_fact = "fever.travel_destinations_dates_onset_and_healthcare"
        session.process("2026-07-10 귀국 후 3일 뒤 발열 시작")
        self.assertEqual(
            session.memory.facts["symptom.duration"]["value"],
            {"amount": 1, "unit": "day"},
        )
        self.assertEqual(session.memory.facts["symptom.duration"]["status"], "known")
        self.assertEqual(
            session.memory.facts["fever.travel_destinations_dates_onset_and_healthcare"]["value"],
            "2026-07-10 귀국 후 3일 뒤 발열 시작",
        )

    def test_not_measured_is_preserved_as_data_absent_reason(self):
        session = InterviewSession("not-performed-temperature", package_path=FEVER_PACKAGE)
        session.last_question_fact = "observation.body_temperature"
        session.process("측정하지 않았어요.")
        record = session.memory.facts["observation.body_temperature"]
        self.assertEqual(record["status"], "unknown")
        self.assertEqual(record["dataAbsentReason"]["code"], "not-performed")

    def test_not_measured_overrides_provisional_string_extraction(self):
        session = InterviewSession("not-performed-oximetry", package_path=DYSPNEA_PACKAGE)
        fact_id = "dyspnea.oxygen_saturation_device_time_oxygen_and_reliability"
        session.last_question_fact = fact_id
        session.process("측정하지 않았어요.")
        record = session.memory.facts[fact_id]
        self.assertEqual(record["status"], "unknown")
        self.assertEqual(record["dataAbsentReason"]["code"], "not-performed")

    def test_question_references_are_monotonic_and_do_not_reset(self):
        session = InterviewSession("stable-question-references")
        first = session.process("기침이 4일째입니다")
        self.assertEqual(first["selected_question"]["question_ref"], "Q1")
        first_fact = first["selected_question"]["fact_id"]

        clarification = session.process("무슨 뜻인지 애매해요")
        self.assertEqual(
            clarification["selected_question"]["question_ref"], "Q1"
        )
        self.assertEqual(clarification["selected_question"]["fact_id"], first_fact)

        second = session.process("2")
        self.assertEqual(second["selected_question"]["question_ref"], "Q2")
        self.assertNotEqual(second["selected_question"]["fact_id"], first_fact)

    def test_revision_menu_uses_question_references_and_unprompted_fact_refs(self):
        session = InterviewSession("question-reference-revision")
        first = session.process("I have had a cough for 4 days and no blood.")
        prompted_fact = first["selected_question"]["fact_id"]
        session.process("2")
        menu = session.process("수정")
        references = {
            item["fact_id"]: item["edit_ref"]
            for item in menu["edit_menu"]["items"]
        }
        self.assertTrue(references[prompted_fact].startswith("Q"))
        self.assertTrue(references["symptom.hemoptysis"].startswith("U"))
        self.assertNotIn("E", "".join(references.values()))
        self.assertIn("수정 Q2", menu["edit_menu"]["instruction_ko"])

    def test_answer_revision_menu_preserves_unanswered_question_and_history(self):
        session = InterviewSession("answer-revision")
        first = session.process("I have had a cough for 4 days and no blood.")
        current_fact = first["selected_question"]["fact_id"]
        menu = session.process("수정")
        hemoptysis = next(
            item for item in menu["edit_menu"]["items"]
            if item["fact_id"] == "symptom.hemoptysis"
        )
        self.assertEqual(menu["selected_question"]["fact_id"], current_fact)
        prompt = session.process(f"수정 {hemoptysis['edit_ref']}")
        self.assertEqual(prompt["edit_prompt"]["fact_id"], "symptom.hemoptysis")
        amended = session.process("1")
        record = amended["facts"]["symptom.hemoptysis"]
        self.assertTrue(record["value"])
        self.assertEqual(record["corrected_from"], False)
        self.assertEqual(len(record["history"]), 2)
        self.assertEqual(amended["safety_status"]["level"], "urgent")
        self.assertEqual(amended["stop_reason"], "urgent_escalation")
        self.assertTrue(any(event["type"] == "answer_revised" for event in amended["events"]))

    def test_answer_revision_can_replace_data_absent_reason(self):
        session = InterviewSession("answer-revision-absent")
        session.process("I have had a cough for 4 days.")
        session.process("3")
        menu = session.process("수정")
        dyspnea = next(
            item for item in menu["edit_menu"]["items"]
            if item["fact_id"] == "symptom.dyspnea"
        )
        self.assertEqual(dyspnea["dataAbsentReason"]["code"], "asked-unknown")
        amended = session.process(f"수정 {dyspnea['edit_ref']}: 2")
        record = amended["facts"]["symptom.dyspnea"]
        self.assertEqual(record["status"], "known")
        self.assertEqual(record["value"], "none")
        self.assertEqual(record["corrected_from"], None)

    def test_post_completion_revision_reopens_new_conditional_branch(self):
        session = InterviewSession(
            "answer-revision-complete",
            package_path=REPRODUCTIVE_GENITAL_SYMPTOMS_PACKAGE,
        )
        session.memory.next_turn()
        session.memory.merge(
            "genital.primary_symptom_group",
            {
                "value": "vaginal_vulvar_pelvic",
                "raw_text": "vaginal symptoms",
                "confidence": .9,
            },
        )
        initial_required = session._required_facts(None, session._safety())
        for fact_id in initial_required:
            if fact_id != "genital.primary_symptom_group":
                session.memory.mark_absent(fact_id, "not known", "asked-unknown")
        complete = session.process("검토 완료")
        self.assertTrue(complete["completion_status"]["complete"])
        menu = session.process("수정")
        selector = next(
            item for item in menu["edit_menu"]["items"]
            if item["fact_id"] == "genital.primary_symptom_group"
        )
        reopened = session.process(
            f"수정 {selector['edit_ref']}: testicular_scrotal"
        )
        self.assertFalse(reopened["completion_status"]["complete"])
        self.assertTrue(reopened["revision_status"]["amended_after_completion"])
        self.assertIn(
            "testicular.sudden_severe_unilateral_pain",
            reopened["completion_status"]["required_facts"],
        )
        self.assertNotIn(
            "vaginal.discharge_changed",
            reopened["completion_status"]["required_facts"],
        )

    def test_unrecognized_answer_repeats_same_question_for_clarification(self):
        session = InterviewSession("answer-clarification")
        first = session.process("I have had a cough for 4 days.")
        expected = first["selected_question"]["fact_id"]
        clarified = session.process("9")
        self.assertEqual(clarified["selected_question"]["fact_id"], expected)
        self.assertEqual(
            clarified["selected_question"]["reason"],
            "answer_not_understood_reconfirmation",
        )
        self.assertTrue(clarified["answer_clarification"]["required"])
        self.assertEqual(clarified["answer_clarification"]["raw_response"], "9")
        self.assertTrue(
            clarified["answer_clarification"]["confirmation_required_before_fact_merge"]
        )
        self.assertEqual(session.memory.state(expected), "not_asked")
        resolved = session.process("2")
        self.assertIsNone(resolved["answer_clarification"])
        self.assertEqual(session.memory.state(expected), "known")
        self.assertNotEqual(resolved["selected_question"]["fact_id"], expected)

    def test_safety_reassessment_precedes_answer_clarification(self):
        session = InterviewSession("answer-clarification-safety")
        session.process("I have had a cough for 4 days.")
        state = session.process("피가 섞여 나오는데 질문이 뭐였죠")
        self.assertEqual(state["safety_status"]["level"], "urgent")
        self.assertEqual(state["stop_reason"], "urgent_escalation")
        self.assertIsNone(state["selected_question"])
        self.assertIsNone(state["answer_clarification"])

    def test_korean_modified_hemoptysis_phrase_triggers_urgent_path(self):
        session = InterviewSession("korean-hemoptysis-modifier")
        state = session.process("기침할 때 피가 조금 섞여 보여요.")
        self.assertTrue(state["facts"]["symptom.hemoptysis"]["value"])
        self.assertEqual(state["safety_status"]["level"], "urgent")
        self.assertEqual(state["stop_reason"], "urgent_escalation")

    def test_runtime_exposes_package_and_trace(self):
        session = InterviewSession("package-runtime")
        state = session.process("I have had a cough for 4 days.")
        package = load_package(DEFAULT_PACKAGE)
        self.assertEqual(state["package"]["id"], package["package_id"])
        self.assertEqual(state["selected_question"]["fact_id"], "symptom.dyspnea")
        self.assertTrue(state["events"])
        self.assertIn("active_intents", state)
        self.assertIn("active_targets", state)
        self.assertTrue(state["knowledge_warnings"])

    def test_emergency_stops_routine_questioning(self):
        session = InterviewSession("emergency")
        state = session.process("I have a cough and it is very hard to breathe.")
        self.assertEqual(state["safety_status"]["level"], "emergency")
        self.assertIsNone(state["selected_question"])
        self.assertEqual(state["stop_reason"], "emergency_escalation")

    def test_package_simulation_evaluation_passes(self):
        report = run_evaluation(DEFAULT_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 15)
        for result in report["results"]:
            self.assertIn(
                result["stop_reason"],
                {
                    "all_required_targets_resolved",
                    "required_targets_addressed_with_absent_data",
                    "urgent_escalation",
                    "emergency_escalation",
                },
            )

    def test_simulation_turns_are_bounded(self):
        report = run_evaluation(DEFAULT_PACKAGE)
        non_escalated = [
            item["turns"] for item in report["results"]
            if item["safety_level"] not in {"urgent", "emergency"}
        ]
        self.assertLessEqual(max(non_escalated), 12)

    def test_research_package_is_rejected_in_production_runtime(self):
        with self.assertRaises(PackageLoadError):
            load_package(DEFAULT_PACKAGE, execution_mode="production")

    def test_fever_package_simulation_evaluation_passes(self):
        report = run_evaluation(FEVER_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 19)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 75)

    def test_fever_runtime_uses_fever_rfe(self):
        session = InterviewSession("fever-runtime", package_path=FEVER_PACKAGE)
        state = session.process("I have had a fever for 2 days and measured 39.0°C.")
        self.assertIn("systemic.fever", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-fever")

    def test_fever_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(FEVER_PACKAGE, execution_mode="production")

    def test_dyspnea_package_simulation_evaluation_passes(self):
        report = run_evaluation(DYSPNEA_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 20)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 80)

    def test_dyspnea_runtime_uses_dyspnea_rfe(self):
        session = InterviewSession("dyspnea-runtime", package_path=DYSPNEA_PACKAGE)
        state = session.process("I have been mildly short of breath for 3 days with wheezing.")
        self.assertIn("respiratory.dyspnea", state["active_patterns"])
        self.assertIn("dyspnea.airway_features", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-dyspnea")

    def test_dyspnea_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(DYSPNEA_PACKAGE, execution_mode="production")

    def test_abdominal_pain_package_simulation_evaluation_passes(self):
        report = run_evaluation(ABDOMINAL_PAIN_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 23)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 55)

    def test_abdominal_pain_runtime_uses_abdominal_rfe(self):
        session = InterviewSession(
            "abdominal-runtime", package_path=ABDOMINAL_PAIN_PACKAGE
        )
        state = session.process("I have had abdominal pain for 2 days.")
        self.assertIn("gastrointestinal.abdominal_pain", state["active_patterns"])
        self.assertEqual(
            state["package"]["id"], "package.primary-care-abdominal-pain"
        )

    def test_abdominal_pain_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(ABDOMINAL_PAIN_PACKAGE, execution_mode="production")

    def test_chest_pain_package_simulation_evaluation_passes(self):
        report = run_evaluation(CHEST_PAIN_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 13)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 33)

    def test_chest_pain_runtime_uses_chest_pain_rfe(self):
        session = InterviewSession("chest-runtime", package_path=CHEST_PAIN_PACKAGE)
        state = session.process("I have chest pain.")
        self.assertIn("cardiovascular.chest_pain", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-chest-pain")

    def test_chest_pain_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(CHEST_PAIN_PACKAGE, execution_mode="production")

    def test_headache_package_simulation_evaluation_passes(self):
        report = run_evaluation(HEADACHE_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 11)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 33)

    def test_headache_runtime_uses_headache_rfe(self):
        session = InterviewSession("headache-runtime", package_path=HEADACHE_PACKAGE)
        state = session.process("I have a headache.")
        self.assertIn("neurological.headache", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-headache")

    def test_headache_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(HEADACHE_PACKAGE, execution_mode="production")

    def test_dizziness_syncope_simulation_evaluation_passes(self):
        report = run_evaluation(DIZZINESS_SYNCOPE_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 28)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 55)

    def test_dizziness_syncope_runtime_uses_combined_rfe(self):
        session = InterviewSession(
            "dizziness-runtime", package_path=DIZZINESS_SYNCOPE_PACKAGE
        )
        state = session.process("I feel dizzy.")
        self.assertIn("neurological.dizziness_or_syncope", state["active_patterns"])
        self.assertEqual(
            state["package"]["id"], "package.primary-care-dizziness-syncope"
        )

    def test_dizziness_syncope_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(DIZZINESS_SYNCOPE_PACKAGE, execution_mode="production")

    def test_vomiting_diarrhea_simulation_evaluation_passes(self):
        report = run_evaluation(VOMITING_DIARRHEA_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 23)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 45)

    def test_vomiting_diarrhea_runtime_uses_combined_rfe(self):
        session = InterviewSession(
            "vomiting-diarrhea-runtime", package_path=VOMITING_DIARRHEA_PACKAGE
        )
        state = session.process("I have vomiting and diarrhea.")
        self.assertIn("gastrointestinal.vomiting_or_diarrhea", state["active_patterns"])
        self.assertEqual(
            state["package"]["id"], "package.primary-care-vomiting-diarrhea"
        )

    def test_vomiting_diarrhea_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(VOMITING_DIARRHEA_PACKAGE, execution_mode="production")

    def test_urinary_symptoms_simulation_evaluation_passes(self):
        report = run_evaluation(URINARY_SYMPTOMS_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 12)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 39)

    def test_urinary_symptoms_runtime_uses_urinary_rfe(self):
        session = InterviewSession(
            "urinary-runtime", package_path=URINARY_SYMPTOMS_PACKAGE
        )
        state = session.process("I have urinary symptoms.")
        self.assertIn("genitourinary.urinary_symptoms", state["active_patterns"])
        self.assertEqual(
            state["package"]["id"], "package.primary-care-urinary-symptoms"
        )

    def test_urinary_symptoms_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(URINARY_SYMPTOMS_PACKAGE, execution_mode="production")

    def test_fatigue_simulation_evaluation_passes(self):
        report = run_evaluation(FATIGUE_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 22)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 50)

    def test_fatigue_runtime_uses_fatigue_rfe(self):
        session = InterviewSession("fatigue-runtime", package_path=FATIGUE_PACKAGE)
        state = session.process("I feel tired all the time.")
        self.assertIn("systemic.fatigue", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-fatigue")

    def test_fatigue_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(FATIGUE_PACKAGE, execution_mode="production")

    def test_back_pain_simulation_evaluation_passes(self):
        report = run_evaluation(BACK_PAIN_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 13)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 36)

    def test_back_pain_runtime_uses_back_pain_rfe(self):
        session = InterviewSession("back-pain-runtime", package_path=BACK_PAIN_PACKAGE)
        state = session.process("I have low back pain.")
        self.assertIn("musculoskeletal.back_pain", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-back-pain")

    def test_back_pain_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(BACK_PAIN_PACKAGE, execution_mode="production")

    def test_skin_complaint_simulation_evaluation_passes(self):
        report = run_evaluation(SKIN_COMPLAINT_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 11)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 40)

    def test_skin_complaint_runtime_uses_skin_rfe(self):
        session = InterviewSession("skin-runtime", package_path=SKIN_COMPLAINT_PACKAGE)
        state = session.process("피부에 발진이 생겼어요.")
        self.assertIn("dermatological.skin_complaint", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-skin-complaint")

    def test_skin_complaint_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(SKIN_COMPLAINT_PACKAGE, execution_mode="production")

    def test_medication_review_simulation_evaluation_passes(self):
        report = run_evaluation(MEDICATION_REVIEW_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 10)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 40)

    def test_medication_review_runtime_uses_medication_rfe(self):
        session = InterviewSession(
            "medication-review-runtime", package_path=MEDICATION_REVIEW_PACKAGE
        )
        state = session.process("복용약을 검토하고 싶어요.")
        self.assertIn("medication.review", state["active_patterns"])
        self.assertEqual(
            state["package"]["id"], "package.primary-care-medication-review"
        )

    def test_medication_review_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(MEDICATION_REVIEW_PACKAGE, execution_mode="production")

    def test_upper_respiratory_simulation_evaluation_passes(self):
        report = run_evaluation(UPPER_RESPIRATORY_SYMPTOMS_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 11)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 40)

    def test_upper_respiratory_runtime_uses_grouped_rfe(self):
        session = InterviewSession(
            "upper-respiratory-runtime",
            package_path=UPPER_RESPIRATORY_SYMPTOMS_PACKAGE,
        )
        state = session.process("목이 아프고 코가 막혀요.")
        self.assertIn("upper_respiratory.symptoms", state["active_patterns"])
        self.assertEqual(
            state["package"]["id"],
            "package.primary-care-upper-respiratory-symptoms",
        )

    def test_upper_respiratory_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(UPPER_RESPIRATORY_SYMPTOMS_PACKAGE, execution_mode="production")

    def test_palpitations_simulation_evaluation_passes(self):
        report = run_evaluation(PALPITATIONS_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 10)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 38)

    def test_palpitations_runtime_uses_grouped_rfe(self):
        session = InterviewSession("palpitations-runtime", package_path=PALPITATIONS_PACKAGE)
        state = session.process("심장이 두근거려요.")
        self.assertIn("cardiovascular.palpitations", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-palpitations")

    def test_palpitations_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(PALPITATIONS_PACKAGE, execution_mode="production")

    def test_bowel_symptoms_simulation_evaluation_passes(self):
        report = run_evaluation(BOWEL_SYMPTOMS_PACKAGE)
        self.assertTrue(report["passed"]); self.assertEqual(report["case_count"], 10)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 37)

    def test_bowel_symptoms_runtime_uses_grouped_rfe(self):
        session = InterviewSession("bowel-runtime", package_path=BOWEL_SYMPTOMS_PACKAGE)
        state = session.process("변비가 생기고 피가 보여요.")
        self.assertIn("gastrointestinal.bowel_symptoms", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-bowel-symptoms")

    def test_bowel_symptoms_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(BOWEL_SYMPTOMS_PACKAGE, execution_mode="production")

    def test_focal_neurology_simulation_and_runtime(self):
        report = run_evaluation(FOCAL_WEAKNESS_NUMBNESS_PACKAGE)
        self.assertTrue(report["passed"]); self.assertEqual(report["case_count"], 12)
        session = InterviewSession("focal-runtime", package_path=FOCAL_WEAKNESS_NUMBNESS_PACKAGE)
        state = session.process("한쪽 팔이 저리고 힘이 빠져요.")
        self.assertIn("neurological.focal_weakness_numbness", state["active_patterns"])
        with self.assertRaises(PackageLoadError): load_package(FOCAL_WEAKNESS_NUMBNESS_PACKAGE, execution_mode="production")

    def test_joint_limb_simulation_and_runtime(self):
        report = run_evaluation(JOINT_LIMB_COMPLAINT_PACKAGE)
        self.assertTrue(report["passed"]); self.assertEqual(report["case_count"], 13)
        session = InterviewSession("joint-runtime", package_path=JOINT_LIMB_COMPLAINT_PACKAGE)
        state = session.process("무릎이 붓고 아파요.")
        self.assertIn("musculoskeletal.joint_limb_complaint", state["active_patterns"])
        with self.assertRaises(PackageLoadError): load_package(JOINT_LIMB_COMPLAINT_PACKAGE, execution_mode="production")

    def test_mental_health_sleep_simulation_and_runtime(self):
        report = run_evaluation(MENTAL_HEALTH_SLEEP_PACKAGE)
        self.assertTrue(report["passed"]); self.assertEqual(report["case_count"], 12)
        session = InterviewSession("mental-runtime", package_path=MENTAL_HEALTH_SLEEP_PACKAGE)
        state = session.process("걱정이 많고 잠을 못 자요.")
        self.assertIn("mental_health.sleep_concern", state["active_patterns"])
        with self.assertRaises(PackageLoadError): load_package(MENTAL_HEALTH_SLEEP_PACKAGE, execution_mode="production")

    def test_edema_simulation_and_runtime(self):
        report = run_evaluation(EDEMA_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 11)
        session = InterviewSession("edema-runtime", package_path=EDEMA_PACKAGE)
        state = session.process("다리가 붓고 숨이 차요.")
        self.assertIn("cardiovascular.edema", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-edema")
        with self.assertRaises(PackageLoadError):
            load_package(EDEMA_PACKAGE, execution_mode="production")

    def test_hypertension_follow_up_simulation_and_runtime(self):
        report = run_evaluation(HYPERTENSION_FOLLOW_UP_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 10)
        session = InterviewSession("hypertension-runtime", package_path=HYPERTENSION_FOLLOW_UP_PACKAGE)
        state = session.process("고혈압 추적 진료를 받으러 왔어요.")
        self.assertIn("cardiovascular.hypertension_follow_up", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-hypertension-follow-up")
        with self.assertRaises(PackageLoadError):
            load_package(HYPERTENSION_FOLLOW_UP_PACKAGE, execution_mode="production")

    def test_weight_constitutional_simulation_and_runtime(self):
        report = run_evaluation(WEIGHT_CONSTITUTIONAL_CHANGE_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 11)
        session = InterviewSession("constitutional-runtime", package_path=WEIGHT_CONSTITUTIONAL_CHANGE_PACKAGE)
        state = session.process("이유 없이 체중이 줄고 밤에 땀이 나요.")
        self.assertIn("general.weight_constitutional_change", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-weight-constitutional-change")
        with self.assertRaises(PackageLoadError):
            load_package(WEIGHT_CONSTITUTIONAL_CHANGE_PACKAGE, execution_mode="production")

    def test_reproductive_genital_simulation_and_conditional_runtime(self):
        report = run_evaluation(REPRODUCTIVE_GENITAL_SYMPTOMS_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 16)
        vaginal = next(item for item in report["results"] if item["case_id"] == "GEN-VAGINAL-DATA-ABSENT")
        self.assertTrue(any(fact_id.startswith("vaginal.") for fact_id in vaginal["selected_facts"]))
        self.assertFalse(any(fact_id.startswith("penile.") for fact_id in vaginal["selected_facts"]))
        self.assertFalse(any(fact_id.startswith("testicular.") for fact_id in vaginal["selected_facts"]))
        session = InterviewSession("genital-runtime", package_path=REPRODUCTIVE_GENITAL_SYMPTOMS_PACKAGE)
        state = session.process("고환이 갑자기 아파요.")
        self.assertIn("genitourinary.reproductive_genital_symptoms", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-reproductive-genital-symptoms")
        with self.assertRaises(PackageLoadError):
            load_package(REPRODUCTIVE_GENITAL_SYMPTOMS_PACKAGE, execution_mode="production")

    def test_eye_simulation_and_conditional_runtime(self):
        report = run_evaluation(EYE_SYMPTOMS_PACKAGE)
        self.assertTrue(report["passed"])
        self.assertEqual(report["case_count"], 16)
        red = next(item for item in report["results"] if item["case_id"] == "EYE-RED-DATA-ABSENT")
        self.assertIn("eye.redness_present", red["selected_facts"])
        self.assertNotIn("eye.injury_mechanism_and_time", red["selected_facts"])
        session = InterviewSession("eye-runtime", package_path=EYE_SYMPTOMS_PACKAGE)
        session.memory.next_turn()
        session.memory.merge("eye.primary_symptom_group", {"value": "visual_disturbance", "raw_text": "시야가 흐려요", "confidence": .9})
        state = session.process("시야에 검은 커튼이 보여요")
        self.assertIn("ophthalmic.eye_symptoms", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-eye-symptoms")
        with self.assertRaises(PackageLoadError):
            load_package(EYE_SYMPTOMS_PACKAGE, execution_mode="production")


if __name__ == "__main__":
    unittest.main()
