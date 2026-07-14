from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from compiler.build_package import (
    CompilationError,
    compile_package,
    semantic_digest,
    validate_package,
)
from evaluation.run_evaluation import run as run_evaluation
from runtime.memory import ClinicalMemory
from runtime.package import (
    ABDOMINAL_PAIN_PACKAGE, CHEST_PAIN_PACKAGE, DEFAULT_PACKAGE,
    DYSPNEA_PACKAGE, FEVER_PACKAGE, HEADACHE_PACKAGE,
    PackageLoadError, load_package,
)
from runtime.session import InterviewSession
from sources.check_refresh import due_sources


class CompilerTests(unittest.TestCase):
    def test_compilation_is_deterministic(self):
        first = compile_package()
        second = compile_package()
        self.assertEqual(first["semantic_digest"], second["semantic_digest"])
        self.assertEqual(first, second)

    def test_production_rejects_unreviewed_safety(self):
        for profile in (
            "cough", "fever", "dyspnea", "abdominal_pain", "chest_pain",
            "headache",
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
        daily = due_sources(date.fromisoformat("2026-07-14"))
        daily_ids = {item["source_id"] for item in daily["due"]}
        self.assertIn("source.ers.chronic-cough.2020", daily_ids)
        self.assertIn("source.gina.summary.2025", daily_ids)
        self.assertNotIn("source.nice.ng120", daily_ids)
        weekly = due_sources(date.fromisoformat("2026-07-20"))
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
        self.assertIn("source.nice.ng158.vte", dyspnea_daily_ids)
        self.assertNotIn("source.nhs.shortness-of-breath", dyspnea_daily_ids)
        stom_manifest = (
            Path(__file__).resolve().parents[1]
            / "sources/manifests/stom-terminology.json"
        )
        stom_monthly = due_sources(
            date.fromisoformat("2026-08-13"), stom_manifest
        )
        self.assertEqual(
            {item["source_id"] for item in stom_monthly["due"]},
            {"source.stom.fhir-r4-terminology-server"},
        )
        self.assertEqual(stom_monthly["due"][0]["monitor_interval_days"], 30)

    def test_fever_package_is_deterministic_and_question_complete(self):
        first = compile_package(profile="fever")
        second = compile_package(profile="fever")
        self.assertEqual(first, second)
        facts = {
            node["id"] for node in first["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(len(facts), 19)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 6)
        self.assertEqual(first["coverage"]["total_safety_rules"], 6)

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
        self.assertEqual(len(facts), 24)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 8)
        self.assertEqual(first["coverage"]["total_safety_rules"], 8)
        self.assertEqual(first["coverage"]["uncovered_safety_rules"], [])

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
        self.assertEqual(len(facts), 28)
        self.assertEqual(facts, set(first["indexes"]["questions_by_fact"]))
        self.assertEqual(first["coverage"]["total_safety_rules"], 12)
        self.assertEqual(first["coverage"]["safety_rules_with_simulations"], 12)
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
        self.assertEqual(len(facts), 30)
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
        self.assertEqual(len(facts), 30)
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


class PackageRuntimeTests(unittest.TestCase):
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
        self.assertEqual(report["case_count"], 14)
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
        self.assertEqual(report["case_count"], 8)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 14)

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
        self.assertEqual(report["case_count"], 11)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 18)

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
        self.assertEqual(report["case_count"], 13)
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 29)

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
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 31)

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
        self.assertLessEqual(max(item["turns"] for item in report["results"]), 31)

    def test_headache_runtime_uses_headache_rfe(self):
        session = InterviewSession("headache-runtime", package_path=HEADACHE_PACKAGE)
        state = session.process("I have a headache.")
        self.assertIn("neurological.headache", state["active_patterns"])
        self.assertEqual(state["package"]["id"], "package.primary-care-headache")

    def test_headache_research_package_is_rejected_in_production(self):
        with self.assertRaises(PackageLoadError):
            load_package(HEADACHE_PACKAGE, execution_mode="production")


if __name__ == "__main__":
    unittest.main()
