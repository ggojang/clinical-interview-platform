from __future__ import annotations

import json
import re
import tempfile
import unittest
from datetime import date
from pathlib import Path

from compiler.build_package import PACKAGE_PROFILES, compile_package
from interoperability.fhir_r4_bindings import (
    questionnaire_item_projection,
    questionnaire_response_answer_projection,
)
from interoperability.question_answer import (
    LOCAL_ANSWER,
    LOCAL_ANSWER_DOMAIN,
    LOCAL_QUESTION,
    VALUESET_BASE,
    answer_valueset_id,
    assess_question_atomicity,
    enrich_clinician_context,
    load_answer_domains,
    load_documents,
)
from tools.fhir.build_answer_valuesets import (
    REPLACED_BY_EXTENSION,
    build as build_answer_valuesets,
    validate as validate_answer_valuesets,
)
from tools.fhir.build_question_answer_codesystems import (
    ANSWER_CODE_SYSTEM_VERSION,
    QUESTION_CODE_SYSTEM_VERSION,
    build,
    validate,
)
from tools.gpt_export.build import build as build_gpt_export
from tools.validator.audit_question_answer_terminology import run as run_audit


ROOT = Path(__file__).resolve().parents[1]


class QuestionAnswerTerminologyTest(unittest.TestCase):
    def test_complete_local_codesystems_have_explicit_release_versions(self):
        question_system, answer_system, domain_system = build()
        self.assertEqual(question_system["version"], QUESTION_CODE_SYSTEM_VERSION)
        self.assertEqual(answer_system["version"], ANSWER_CODE_SYSTEM_VERSION)
        self.assertEqual(QUESTION_CODE_SYSTEM_VERSION, "0.3.0")
        self.assertEqual(ANSWER_CODE_SYSTEM_VERSION, "0.3.0")
        self.assertEqual(
            question_system["id"], "clinical-interview-question-0-3-0"
        )
        self.assertEqual(
            answer_system["id"], "clinical-interview-answer-0-3-0"
        )
        self.assertEqual(
            domain_system["version"],
            load_answer_domains()["local_code_system"]["version"],
        )
        self.assertEqual(
            domain_system["id"], "clinical-interview-answer-domain-0-5-0"
        )

    def test_policy_and_registry_validate(self):
        policy, registry = load_documents()
        self.assertEqual(
            policy["question_binding"]["preferred_system_order"],
            ["http://loinc.org", "http://snomed.info/sct", LOCAL_QUESTION],
        )
        self.assertEqual(
            policy["answer_binding"]["preferred_system_order"],
            [
                "selected_KR_Core_V2_profile_element_ValueSet_when_applicable",
                "target_FHIR_R4_element_ValueSet_when_applicable",
                "http://snomed.info/sct",
                LOCAL_ANSWER,
            ],
        )
        self.assertEqual(registry["verification"]["loinc_version"], "2.82")
        snomed_version = registry["verification"]["snomed_version"]
        match = re.fullmatch(
            r"http://snomed\.info/sct/900000000000207008/version/(\d{8})",
            snomed_version,
        )
        self.assertIsNotNone(match)
        self.assertLessEqual(
            date.fromisoformat(
                f"{match.group(1)[:4]}-{match.group(1)[4:6]}-{match.group(1)[6:]}"
            ),
            date.fromisoformat(registry["verification"]["verified_at"]),
        )
        self.assertEqual(
            policy["fhir_r4_projection"]["resource_element_binding_policy"],
            "policy.fhir-r4-element-terminology-binding",
        )

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

    def test_contextual_both_is_not_mapped_to_bilateral_laterality(self):
        package = compile_package(profile="test_result_follow_up")
        fact = next(
            node
            for node in package["knowledge_graph"]["nodes"]
            if node.get("id") == "encounter.result_follow_up.goal"
        )
        binding = fact["answer_semantic_binding"]
        self.assertNotIn("both", binding.get("snomed_mappings", {}))
        self.assertEqual(binding["value_set_strategy"], "complete_local")

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
        question, answer, domain = build()
        validate(question)
        validate(answer)
        validate(domain)
        self.assertEqual(question["url"], LOCAL_QUESTION)
        self.assertEqual(answer["url"], LOCAL_ANSWER)
        self.assertEqual(domain["url"], LOCAL_ANSWER_DOMAIN)
        self.assertGreater(question["count"], 2500)
        self.assertGreater(answer["count"], 500)
        answer_codes = {concept["code"] for concept in answer["concept"]}
        self.assertTrue({"boolean--yes", "boolean--no"} <= answer_codes)
        domain_codes = {concept["code"] for concept in domain["concept"]}
        self.assertTrue({
            "pain-quality-burning",
            "pain-quality-sharp",
            "pain-quality-throbbing",
            "pain-quality-tightening",
            "source-reliability-reliable",
            "source-reliability-conflicting-sources",
            "information-source-patient",
            "information-source-record",
        } <= domain_codes)

    def test_pain_quality_uses_one_domain_with_context_preference(self):
        registry = load_answer_domains()
        pain = registry["domains"]["pain-quality"]
        self.assertTrue(pain["questionnaire"]["repeats"])
        self.assertTrue(pain["questionnaire"]["allow_free_text"])
        chest = compile_package(profile="chest_pain")
        fact = next(
            node for node in chest["knowledge_graph"]["nodes"]
            if node.get("id") == "symptom.chest_pain.quality"
        )
        binding = fact["answer_semantic_binding"]
        self.assertEqual(binding["answer_domain"], "pain-quality")
        self.assertTrue(binding["answer_value_set"].endswith("/a-local-pain-quality"))
        self.assertEqual(binding["fhir_item_type"], "open-choice")
        self.assertTrue(binding["fhir_item_repeats"])
        self.assertEqual(
            binding["internal_value_mappings"]["tightness"]["code"],
            "pain-quality-tightening",
        )
        self.assertNotIn("other", binding["internal_value_mappings"])
        item = questionnaire_item_projection(fact)
        self.assertEqual(item["type"], "open-choice")
        self.assertTrue(item["repeats"])
        self.assertEqual(
            questionnaire_response_answer_projection(fact, "tightness")[
                "valueCoding"
            ]["code"],
            "pain-quality-tightening",
        )
        self.assertEqual(
            questionnaire_response_answer_projection(fact, "other"),
            {"valueString": "other"},
        )

    def test_answer_valuesets_are_complete_named_and_valid(self):
        bundle = build_answer_valuesets()
        validate_answer_valuesets(bundle)
        resources = {
            entry["resource"]["id"]: entry["resource"]
            for entry in bundle["entry"]
        }
        self.assertIn("a-sct-yes-no", resources)
        self.assertIn("a-local-yes-no", resources)
        self.assertIn("a-local-pain-quality", resources)
        self.assertIn("a-sct-laterality", resources)
        self.assertTrue(any(key.startswith("a-mixed-") for key in resources))
        self.assertTrue(any(key.startswith("a-local-") for key in resources))
        yes_no_systems = {
            include["system"]
            for include in resources["a-sct-yes-no"]["compose"]["include"]
        }
        self.assertEqual(yes_no_systems, {"http://snomed.info/sct"})
        pain_systems = {
            include["system"]
            for include in resources["a-local-pain-quality"]["compose"]["include"]
        }
        self.assertEqual(pain_systems, {LOCAL_ANSWER_DOMAIN})
        laterality_codes = {
            concept["code"]
            for include in resources["a-sct-laterality"]["compose"]["include"]
            for concept in include["concept"]
        }
        self.assertEqual(laterality_codes, {"7771000", "24028007", "51440002"})
        self.assertLessEqual(
            len(answer_valueset_id("local", "x" * 200)), 64
        )

    def test_source_reliability_uses_one_domain_and_retains_retired_aliases(self):
        profiles = {
            "physical_activity_counselling": "activity.source_reliability",
            "alcohol_use_counselling": "alcohol.source_reliability",
            "swallowing_difficulty": "swallow.source_reliability",
            "tobacco_nicotine_counselling": "tobacco.source_reliability",
        }
        legacy_ids = {
            "a-local-activity-source-reliability-coded-reliable-pa-ae5948bc87",
            "a-local-alcohol-source-reliability-coded-reliable-par-364084eaff",
            "a-local-swallow-source-reliability-coded-reliable-par-d71fed0276",
            "a-local-tobacco-source-reliability-coded-reliable-par-a6689eafd6",
        }
        shared_url = f"{VALUESET_BASE}/a-local-information-source-reliability"
        for profile, fact_id in profiles.items():
            package = compile_package(profile=profile)
            fact = next(
                node for node in package["knowledge_graph"]["nodes"]
                if node.get("id") == fact_id
            )
            binding = fact["answer_semantic_binding"]
            self.assertEqual(binding["answer_domain"], "source-reliability")
            self.assertEqual(binding["answer_value_set"], shared_url)
            self.assertEqual(binding["fhir_item_type"], "open-choice")
            self.assertFalse(binding["fhir_item_repeats"])
            self.assertEqual(
                binding["data_absent_reason_mappings"],
                {"unknown": "asked-unknown"},
            )
            self.assertEqual(
                questionnaire_item_projection(fact)["answerValueSet"],
                shared_url,
            )
            self.assertEqual(
                questionnaire_response_answer_projection(fact, "reliable")[
                    "valueCoding"
                ]["code"],
                "source-reliability-reliable",
            )
            self.assertEqual(
                questionnaire_response_answer_projection(fact, "unknown"),
                {"dataAbsentReason": "asked-unknown"},
            )

        bundle = build_answer_valuesets()
        resources = {
            entry["resource"]["id"]: entry["resource"]
            for entry in bundle["entry"]
        }
        shared = resources["a-local-information-source-reliability"]
        shared_codes = {
            concept["code"]
            for include in shared["compose"]["include"]
            for concept in include["concept"]
        }
        self.assertEqual(shared_codes, {
            "source-reliability-reliable",
            "source-reliability-partly-reliable",
            "source-reliability-memory-uncertain",
            "source-reliability-conflicting-sources",
        })
        for legacy_id in legacy_ids:
            legacy = resources[legacy_id]
            self.assertEqual(legacy["status"], "retired")
            replacement = next(
                extension["valueCanonical"]
                for extension in legacy["extension"]
                if extension["url"] == REPLACED_BY_EXTENSION
            )
            self.assertEqual(replacement, shared_url)

        legacy_urls = {f"{VALUESET_BASE}/{identifier}" for identifier in legacy_ids}
        for profile in PACKAGE_PROFILES:
            package = compile_package(profile=profile)
            for node in package["knowledge_graph"]["nodes"]:
                binding = node.get("answer_semantic_binding", {})
                self.assertNotIn(binding.get("answer_value_set"), legacy_urls)

    def test_shared_snomed_answer_domain_counts_as_standard_coverage(self):
        package = compile_package(profile="epistaxis")
        coverage = package["question_answer_terminology"]["coverage"]
        self.assertGreaterEqual(coverage["coded_answer_snomed_count"], 3)
        self.assertGreater(coverage["coded_answer_snomed_percent"], 0)

    def test_information_source_type_uses_one_domain_and_retains_aliases(self):
        profiles = {
            "alcohol_use_counselling": "alcohol.information_source",
            "post_discharge_follow_up": "post_discharge.information_source",
            "swallowing_difficulty": "swallow.information_source",
            "tobacco_nicotine_counselling": "tobacco.information_source",
        }
        legacy_ids = {
            "a-local-alcohol-information-source-coded-patient-care-7d2a446eb4",
            "a-local-post-discharge-information-source-coded-patie-d435808b98",
            "a-local-swallow-information-source-coded-patient-care-bccf9b061d",
            "a-local-tobacco-information-source-coded-patient-care-fba045369b",
        }
        shared_url = f"{VALUESET_BASE}/a-local-information-source-type"
        for profile, fact_id in profiles.items():
            package = compile_package(profile=profile)
            fact = next(
                node for node in package["knowledge_graph"]["nodes"]
                if node.get("id") == fact_id
            )
            binding = fact["answer_semantic_binding"]
            self.assertEqual(binding["answer_domain"], "information-source-type")
            self.assertEqual(binding["answer_value_set"], shared_url)
            self.assertEqual(binding["fhir_item_type"], "open-choice")
            self.assertFalse(binding["fhir_item_repeats"])
            self.assertEqual(
                binding["data_absent_reason_mappings"],
                {"unknown": "asked-unknown"},
            )
            self.assertEqual(
                questionnaire_item_projection(fact)["answerValueSet"],
                shared_url,
            )
            self.assertEqual(
                questionnaire_response_answer_projection(fact, "caregiver")[
                    "valueCoding"
                ]["code"],
                "information-source-caregiver",
            )
            self.assertEqual(
                questionnaire_response_answer_projection(fact, "unknown"),
                {"dataAbsentReason": "asked-unknown"},
            )

        registry = load_answer_domains()
        activity = registry["domains"]["information-source-type"][
            "fact_bindings"
        ]["activity.information_source"]
        self.assertEqual(activity["status"], "refactoring_queued")
        self.assertIn("device_or_record", activity["reason"])

        bundle = build_answer_valuesets()
        resources = {
            entry["resource"]["id"]: entry["resource"]
            for entry in bundle["entry"]
        }
        shared_codes = {
            concept["code"]
            for include in resources["a-local-information-source-type"][
                "compose"
            ]["include"]
            for concept in include["concept"]
        }
        self.assertEqual(shared_codes, {
            "information-source-patient",
            "information-source-caregiver",
            "information-source-patient-and-caregiver",
            "information-source-record",
        })
        for legacy_id in legacy_ids:
            legacy = resources[legacy_id]
            self.assertEqual(legacy["status"], "retired")
            replacement = next(
                extension["valueCanonical"]
                for extension in legacy["extension"]
                if extension["url"] == REPLACED_BY_EXTENSION
            )
            self.assertEqual(replacement, shared_url)

        legacy_urls = {f"{VALUESET_BASE}/{identifier}" for identifier in legacy_ids}
        for profile in PACKAGE_PROFILES:
            package = compile_package(profile=profile)
            for node in package["knowledge_graph"]["nodes"]:
                binding = node.get("answer_semantic_binding", {})
                self.assertNotIn(binding.get("answer_value_set"), legacy_urls)

    def test_symptom_onset_mode_uses_one_mixed_domain_and_retains_aliases(self):
        profiles = {
            "neck_pain": "neck.onset_mode",
            "back_pain": "symptom.back_pain.onset",
            "bowel_symptoms": "symptom.bowel.sudden_or_gradual",
            "joint_limb_complaint": "symptom.joint_limb.onset",
            "skin_complaint": "symptom.skin_complaint.onset",
            "upper_respiratory_symptoms": "symptom.upper_respiratory.onset",
            "chest_pain": "symptom.chest_pain.onset",
            "dyspnea": "symptom.dyspnea_onset",
        }
        legacy_ids = {
            item["id"]
            for item in load_answer_domains()["domains"][
                "symptom-onset-mode"
            ]["migration"]["legacy_value_sets"]
        }
        shared_url = f"{VALUESET_BASE}/a-mixed-symptom-onset-mode"
        for profile, fact_id in profiles.items():
            package = compile_package(profile=profile)
            fact = next(
                node for node in package["knowledge_graph"]["nodes"]
                if node.get("id") == fact_id
            )
            binding = fact["answer_semantic_binding"]
            self.assertEqual(binding["answer_domain"], "symptom-onset-mode")
            self.assertEqual(binding["answer_value_set"], shared_url)
            self.assertEqual(binding["fhir_item_type"], "open-choice")
            self.assertFalse(binding["fhir_item_repeats"])
            self.assertEqual(
                questionnaire_item_projection(fact)["answerValueSet"],
                shared_url,
            )
            self.assertEqual(
                questionnaire_response_answer_projection(fact, "sudden")[
                    "valueCoding"
                ],
                {
                    "system": "http://snomed.info/sct",
                    "code": "385315009",
                    "display": "Sudden onset",
                },
            )
            if "unclear" in fact["allowed_values"]:
                unclear = questionnaire_response_answer_projection(
                    fact, "unclear"
                )["valueCoding"]
                self.assertEqual(unclear["system"], LOCAL_ANSWER_DOMAIN)
                self.assertEqual(
                    unclear["code"], "symptom-onset-mode-unclear"
                )

        domain = load_answer_domains()["domains"]["symptom-onset-mode"]
        for fact_id in (
            "ear.onset_and_progression",
            "eye.onset_and_progression",
            "oral.onset_and_progression",
            "symptom.palpitations.onset_offset",
        ):
            self.assertEqual(
                domain["fact_bindings"][fact_id]["status"],
                "refactoring_queued",
            )

        resources = {
            entry["resource"]["id"]: entry["resource"]
            for entry in build_answer_valuesets()["entry"]
        }
        shared_systems = {
            include["system"]
            for include in resources[
                "a-mixed-symptom-onset-mode"
            ]["compose"]["include"]
        }
        self.assertEqual(
            shared_systems,
            {"http://snomed.info/sct", LOCAL_ANSWER_DOMAIN},
        )
        for legacy_id in legacy_ids:
            legacy = resources[legacy_id]
            self.assertEqual(legacy["status"], "retired")
            replacement = next(
                extension["valueCanonical"]
                for extension in legacy["extension"]
                if extension["url"] == REPLACED_BY_EXTENSION
            )
            self.assertEqual(replacement, shared_url)

        legacy_urls = {
            f"{VALUESET_BASE}/{identifier}" for identifier in legacy_ids
        }
        for profile in PACKAGE_PROFILES:
            package = compile_package(profile=profile)
            for node in package["knowledge_graph"]["nodes"]:
                binding = node.get("answer_semantic_binding", {})
                self.assertNotIn(binding.get("answer_value_set"), legacy_urls)

    def test_tobacco_product_use_status_uses_one_local_domain_and_retains_aliases(self):
        fact_profiles = {
            "preoperative.vaping_use_status": "preoperative_assessment",
            "tobacco.cigar_status": "tobacco_nicotine_counselling",
            "tobacco.heated_tobacco_status": "tobacco_nicotine_counselling",
            "tobacco.nicotine_pouch_status": "tobacco_nicotine_counselling",
            "tobacco.overall_product_use_status": "tobacco_nicotine_counselling",
            "tobacco.pipe_hookah_status": "tobacco_nicotine_counselling",
            "tobacco.smokeless_tobacco_status": "tobacco_nicotine_counselling",
        }
        shared_url = f"{VALUESET_BASE}/a-local-tobacco-product-use-status"
        packages = {
            profile: compile_package(profile=profile)
            for profile in set(fact_profiles.values())
        }
        for fact_id, profile in fact_profiles.items():
            fact = next(
                node for node in packages[profile]["knowledge_graph"]["nodes"]
                if node.get("id") == fact_id
            )
            binding = fact["answer_semantic_binding"]
            self.assertEqual(binding["answer_domain"], "tobacco-product-use-status")
            self.assertEqual(binding["answer_value_set"], shared_url)
            self.assertEqual(binding["fhir_item_type"], "open-choice")
            self.assertFalse(binding["fhir_item_repeats"])
            self.assertTrue(binding["allow_free_text"])
            self.assertEqual(
                questionnaire_item_projection(fact)["answerValueSet"], shared_url
            )
            self.assertEqual(
                questionnaire_response_answer_projection(fact, "current")[
                    "valueCoding"
                ],
                {
                    "system": LOCAL_ANSWER_DOMAIN,
                    "code": "tobacco-product-use-status-current",
                    "display": "Current use",
                },
            )
            if "unknown" in fact["allowed_values"]:
                self.assertEqual(
                    questionnaire_response_answer_projection(fact, "unknown"),
                    {"dataAbsentReason": "asked-unknown"},
                )
            if "other" in fact["allowed_values"]:
                other = questionnaire_response_answer_projection(fact, "other")
                self.assertEqual(
                    other["valueCoding"]["code"],
                    "tobacco-product-use-status-other",
                )
                self.assertEqual(other["valueCoding"]["system"], LOCAL_ANSWER_DOMAIN)

        tobacco_nodes = {
            node["id"]: node
            for node in packages["tobacco_nicotine_counselling"][
                "knowledge_graph"
            ]["nodes"]
        }
        self.assertNotEqual(
            tobacco_nodes["tobacco.electronic_cigarette_status"][
                "answer_semantic_binding"
            ]["answer_value_set"],
            shared_url,
        )
        self.assertNotEqual(
            tobacco_nodes["patient.smoking.status"]["answer_semantic_binding"][
                "answer_value_set"
            ],
            shared_url,
        )

        domain = load_answer_domains()["domains"]["tobacco-product-use-status"]
        legacy_ids = {
            item["id"] for item in domain["migration"]["legacy_value_sets"]
        }
        resources = {
            entry["resource"]["id"]: entry["resource"]
            for entry in build_answer_valuesets()["entry"]
        }
        shared_codes = {
            concept["code"]
            for include in resources["a-local-tobacco-product-use-status"][
                "compose"
            ]["include"]
            for concept in include["concept"]
        }
        self.assertEqual(
            shared_codes,
            {
                "tobacco-product-use-status-current",
                "tobacco-product-use-status-former",
                "tobacco-product-use-status-never",
                "tobacco-product-use-status-other",
            },
        )
        for legacy_id in legacy_ids:
            legacy = resources[legacy_id]
            self.assertEqual(legacy["status"], "retired")
            replacement = next(
                extension["valueCanonical"]
                for extension in legacy["extension"]
                if extension["url"] == REPLACED_BY_EXTENSION
            )
            self.assertEqual(replacement, shared_url)

        legacy_urls = {
            f"{VALUESET_BASE}/{identifier}" for identifier in legacy_ids
        }
        for profile in PACKAGE_PROFILES:
            package = compile_package(profile=profile)
            for node in package["knowledge_graph"]["nodes"]:
                binding = node.get("answer_semantic_binding", {})
                self.assertNotIn(binding.get("answer_value_set"), legacy_urls)

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

    def test_atomicity_distinguishes_choice_lists_from_multi_attribute_prompts(self):
        _, registry = load_documents()
        fixture = json.loads(
            (
                ROOT
                / "simulation"
                / "workflows"
                / "question-answer-terminology-cases.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(fixture["contains_real_patient_data"])
        for case in fixture["cases"]:
            with self.subTest(case=case["id"]):
                result = assess_question_atomicity(
                    case["question"], case["fact"], registry
                )
                self.assertEqual(
                    result["status"], case["expected_atomicity"]
                )
                if case.get("expected_signal"):
                    self.assertIn(
                        case["expected_signal"], result["signals"]
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
        expected_retired = sum(
            len(domain.get("migration", {}).get("legacy_value_sets", []))
            for domain in load_answer_domains()["domains"].values()
        )
        self.assertEqual(
            report["answer_valuesets"][
                "retired_compatibility_resource_count"
            ],
            expected_retired,
        )
        self.assertEqual(
            report["answer_valuesets"]["counts_by_lifecycle"]["retired"],
            expected_retired,
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
                "/gpt/interoperability/answer-domains.json",
                "/gpt/interoperability/question-answer-coverage.json",
                "/gpt/interoperability/fhir-r4-element-binding-policy.json",
                "/gpt/interoperability/fhir-r4-fact-element-mappings.json",
                "/gpt/interoperability/fhir-r4-resource-element-bindings.json",
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
        self.assertIn("operationId: getFhirR4ElementBindingPolicy", schema)
        self.assertIn("operationId: getFhirR4FactElementMappings", schema)
        self.assertIn("operationId: getFhirR4ResourceElementBindings", schema)


if __name__ == "__main__":
    unittest.main()
