from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from compiler.build_package import PACKAGE_PROFILES, compile_package
from interoperability.question_answer import (
    LOCAL_ANSWER,
    LOCAL_QUESTION,
    VALUESET_BASE,
    answer_valueset_id,
    assess_question_atomicity,
    enrich_clinician_context,
    load_documents,
)
from tools.fhir.build_answer_valuesets import (
    build as build_answer_valuesets,
    validate as validate_answer_valuesets,
)
from tools.fhir.build_question_answer_codesystems import build, validate
from tools.gpt_export.build import build as build_gpt_export
from tools.validator.audit_question_answer_terminology import run as run_audit


ROOT = Path(__file__).resolve().parents[1]


class QuestionAnswerTerminologyTest(unittest.TestCase):
    def test_policy_and_registry_validate(self):
        policy, registry = load_documents()
        self.assertEqual(
            policy["question_binding"]["preferred_system_order"],
            ["http://loinc.org", "http://snomed.info/sct", LOCAL_QUESTION],
        )
        self.assertEqual(
            policy["answer_binding"]["preferred_system_order"],
            ["http://snomed.info/sct", LOCAL_ANSWER],
        )
        self.assertEqual(registry["verification"]["loinc_version"], "2.82")
        self.assertIn("/version/20260701", registry["verification"]["snomed_version"])

    def test_every_dynamic_question_has_local_code_and_answer_strategy(self):
        for profile in PACKAGE_PROFILES:
            with self.subTest(profile=profile):
                package = compile_package(profile=profile)
                graph = package["knowledge_graph"]
                nodes = {node["id"]: node for node in graph["nodes"]}
                terminology = package["question_answer_terminology"]
                self.assertEqual(
                    terminology["local_question_code_system"], LOCAL_QUESTION
                )
                self.assertTrue(terminology["local_question_code_is_template_id"])
                for edge in graph["edges"]:
                    if edge.get("type") != "COLLECTS":
                        continue
                    question = nodes[edge["from"]]
                    fact = nodes[edge["to"]]
                    self.assertTrue(question["id"].startswith("question."))
                    for mapping in question.get(
                        "semantic_binding", {}
                    ).get("standard_mappings", []):
                        self.assertIn(
                            mapping["mapping_relation"],
                            {"exact", "equivalent", "broader", "narrower", "partial", "related"},
                        )

    def test_verified_loinc_and_snomed_answer_examples_are_projected(self):
        pregnancy = compile_package(profile="pregnancy_postpartum_concern")
        nodes = {node["id"]: node for node in pregnancy["knowledge_graph"]["nodes"]}
        gravida_question = next(
            node for node in nodes.values()
            if node.get("type") == "QuestionTemplate"
            and node.get("collects") == "pregnancy.obstetric_gravidity_total"
        )
        loinc_codes = {
            item["code"]
            for item in gravida_question["semantic_binding"]["fhir_standard_item_codes"]
            if item["system"] == "http://loinc.org"
        }
        self.assertEqual(loinc_codes, {"11996-6"})

        dyspepsia = compile_package(profile="dyspepsia_reflux")
        dyspepsia_nodes = {
            node["id"]: node for node in dyspepsia["knowledge_graph"]["nodes"]
        }
        binding = dyspepsia_nodes[
            "dyspepsia.pregnancy_status"
        ]["answer_semantic_binding"]
        by_value = binding["snomed_mappings"]
        self.assertEqual(
            by_value["pregnant"]["code"], "77386006"
        )
        self.assertEqual(
            by_value["not_pregnant"]["code"], "60001007"
        )
        self.assertNotIn("unclear", by_value)
        self.assertEqual(
            dyspepsia["question_answer_terminology"]["local_answer_code_pattern"],
            "{fact_id}--{internal_value}",
        )

    def test_unknown_is_data_absent_not_negative(self):
        package = compile_package(profile="diabetes_follow_up")
        fact = next(
            node for node in package["knowledge_graph"]["nodes"]
            if node.get("id") == "lifestyle.tobacco_current"
        )
        self.assertEqual(
            fact["answer_semantic_binding"]["data_absent_reason_mappings"][
                "unknown"
            ],
            "asked-unknown",
        )

    def test_boolean_supports_profile_primitive_and_prefers_coded_yes_no(self):
        package = compile_package(profile="headache")
        binding = package["question_answer_terminology"]
        self.assertIn(
            "valueBoolean_only_when",
            binding["primitive_answer_projection"]["boolean"],
        )
        self.assertEqual(
            binding["boolean_snomed_semantic_equivalents"]["true"]["code"],
            "373066001",
        )
        self.assertEqual(
            binding["boolean_snomed_semantic_equivalents"]["false"]["code"],
            "373067005",
        )
        boolean_fact = next(
            node for node in package["knowledge_graph"]["nodes"]
            if node.get("type") == "Fact"
            and node.get("value_type") == "boolean"
        )
        self.assertEqual(
            boolean_fact["answer_semantic_binding"]["answer_value_set"],
            f"{VALUESET_BASE}/a-sct-yes-no",
        )
        self.assertEqual(
            boolean_fact["answer_semantic_binding"]["fhir_response_type"],
            "valueCoding",
        )

    def test_clinician_submission_questions_are_bound_for_gpt_export(self):
        source = json.loads(
            (
                ROOT / "knowledge/shared/clinician-submission-context.json"
            ).read_text(encoding="utf-8")
        )
        context, coverage = enrich_clinician_context(source)
        self.assertEqual(coverage["question_count"], len(context["questions"]))
        self.assertEqual(
            coverage["question_local_code_count"], coverage["question_count"]
        )
        age = next(
            item for item in context["questions"]
            if item["fact_id"] == "patient.age_years"
        )
        self.assertIn(
            "30525-0",
            {
                item["code"]
                for item in age["semantic_binding"]["fhir_standard_item_codes"]
                if item["system"] == "http://loinc.org"
            },
        )

    def test_local_fallback_code_systems_are_complete_and_valid(self):
        question, answer = build()
        validate(question)
        validate(answer)
        self.assertEqual(question["url"], LOCAL_QUESTION)
        self.assertEqual(answer["url"], LOCAL_ANSWER)
        self.assertGreater(question["count"], 2500)
        self.assertGreater(answer["count"], 500)
        answer_codes = {concept["code"] for concept in answer["concept"]}
        self.assertTrue({"boolean--yes", "boolean--no"} <= answer_codes)

    def test_answer_valuesets_are_complete_named_and_valid(self):
        bundle = build_answer_valuesets()
        validate_answer_valuesets(bundle)
        resources = {
            entry["resource"]["id"]: entry["resource"]
            for entry in bundle["entry"]
        }
        self.assertIn("a-sct-yes-no", resources)
        self.assertIn("a-local-yes-no", resources)
        self.assertTrue(any(key.startswith("a-mixed-") for key in resources))
        self.assertTrue(any(key.startswith("a-local-") for key in resources))
        yes_no_systems = {
            include["system"]
            for include in resources["a-sct-yes-no"]["compose"]["include"]
        }
        self.assertEqual(yes_no_systems, {"http://snomed.info/sct"})
        self.assertLessEqual(
            len(answer_valueset_id("local", "x" * 200)), 64
        )

    def test_exact_standard_mappings_require_verified_atomic_questions(self):
        _, registry = load_documents()
        for profile in PACKAGE_PROFILES:
            package = compile_package(profile=profile)
            graph = package["knowledge_graph"]
            nodes = {node["id"]: node for node in graph["nodes"]}
            for edge in graph["edges"]:
                if edge.get("type") != "COLLECTS":
                    continue
                question = nodes[edge["from"]]
                fact = nodes[edge["to"]]
                selected = any(
                    mapping["mapping_relation"] in {"exact", "equivalent"}
                    for mapping in question.get(
                        "semantic_binding", {}
                    ).get("standard_mappings", [])
                )
                if selected:
                    atomicity = assess_question_atomicity(
                        question, fact, registry
                    )
                    self.assertEqual(
                        atomicity["status"], "atomic_verified"
                    )

    def test_repository_wide_audit_passes(self):
        report = run_audit()
        self.assertTrue(report["passed"])
        self.assertEqual(report["package_count"], len(PACKAGE_PROFILES))
        totals = report["totals_by_package_occurrence"]
        self.assertEqual(
            totals["question_count"], totals["question_local_code_count"]
        )
        self.assertEqual(
            totals["coded_answer_value_count"],
            totals["coded_answer_local_fallback_count"],
        )
        self.assertGreater(totals["question_loinc_exact_or_equivalent_count"], 0)
        self.assertGreater(totals["coded_answer_snomed_count"], 0)
        self.assertEqual(
            report["question_atomicity"][
                "invalid_exact_or_equivalent_mapping_count"
            ],
            0,
        )
        self.assertGreater(
            report["question_atomicity"][
                "composite_refactoring_queue_count"
            ],
            0,
        )
        self.assertGreater(
            report["answer_valuesets"]["resource_count"], 100
        )
        self.assertTrue(report["mapping_quality_simulation"]["passed"])

    def test_gpt_export_exposes_binding_resources_and_enriched_questions(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build_gpt_export(ROOT, output_path)
            paths = {item["path"] for item in manifest["resources"]}
            self.assertTrue({
                "/gpt/interoperability/question-answer-policy.json",
                "/gpt/interoperability/question-answer-bindings.json",
                "/gpt/interoperability/question-answer-coverage.json",
            } <= paths)
            context = json.loads(
                (output_path / "clinician-submission-context.json")
                .read_text(encoding="utf-8")
            )
            self.assertTrue(
                context["question_answer_terminology"][
                    "local_question_code_is_template_id"
                ]
            )
            headache = json.loads(
                (output_path / "rfe/headache/questions.json")
                .read_text(encoding="utf-8")
            )
            self.assertTrue(
                any("semantic_binding" in item for item in headache["items"])
            )
        schema = (ROOT / "docs/gpt/openapi.yaml").read_text(encoding="utf-8")
        self.assertIn("operationId: getQuestionAnswerTerminologyPolicy", schema)
        self.assertIn("operationId: getQuestionAnswerTerminologyBindings", schema)
        self.assertIn("operationId: getQuestionAnswerTerminologyCoverage", schema)


if __name__ == "__main__":
    unittest.main()
