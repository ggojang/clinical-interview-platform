from __future__ import annotations

import json
import unittest
from pathlib import Path

from compiler.build_package import compile_package
from evaluation.run_evaluation import run as run_evaluation
from runtime.package import EAR_HEARING_SYMPTOMS_PACKAGE
from runtime.package import DEFAULT_PACKAGE, load_package
from runtime.session import InterviewSession


class EarHearingSymptomsPackageTests(unittest.TestCase):
    def test_tinnitus_associations_are_atomic_and_safety_covered(self):
        package = compile_package(profile="ear_hearing_symptoms")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(50, len(facts))
        self.assertNotIn(
            "ear.pulsatile_tinnitus_with_neurological_or_visual_symptoms", facts
        )
        self.assertNotIn("ear.tinnitus_with_hearing_change_or_vertigo", facts)
        self.assertNotIn("ear.associated_tinnitus_vertigo_or_fullness", facts)
        self.assertTrue({
            "ear.tinnitus_pulse_synchronous",
            "ear.tinnitus_associated_hearing_change",
            "ear.associated_tinnitus",
            "ear.associated_vertigo",
            "ear.associated_fullness",
        } <= facts)
        self.assertEqual(13, package["coverage"]["total_safety_rules"])
        self.assertEqual(13, package["coverage"]["safety_rules_with_simulations"])
        self.assertEqual([], package["coverage"]["uncovered_safety_rules"])

    def test_prior_audiological_assessment_is_atomic_and_locally_coded(self):
        package = compile_package(profile="ear_hearing_symptoms")
        nodes = {
            node["id"]: node for node in package["knowledge_graph"]["nodes"]
        }
        fact_ids = {
            "ear.prior_audiological_assessment_performed",
            "ear.prior_audiological_assessment_date",
            "ear.prior_audiological_assessment_result",
        }
        self.assertTrue(fact_ids <= nodes.keys())
        for fact_id in fact_ids:
            question = next(
                node for node in nodes.values()
                if node.get("type") == "QuestionTemplate"
                and node.get("collects") == fact_id
            )
            self.assertNotIn("semantic_binding", question, fact_id)
        mapping = json.loads(
            (
                Path(__file__).resolve().parents[1]
                / "mappings/terminology/snomed-mrcm-ear-hearing-symptoms.json"
            ).read_text(encoding="utf-8")
        )
        concept = next(
            item for item in mapping["focus_concepts"] if item["code"] == "21727005"
        )
        self.assertEqual("Audiometric test (procedure)", concept["display"])
        self.assertEqual(
            "related_not_exact",
            mapping["validation"]["targeted_addition"]["mapping_relation_to_questions"],
        )

    def test_iso_date_answer_is_recorded_without_repeating_the_question(self):
        session = InterviewSession(
            "ear-prior-audiology-date", package_path=EAR_HEARING_SYMPTOMS_PACKAGE
        )
        fact_id = "ear.prior_audiological_assessment_date"
        session.last_question_fact = fact_id
        session.process("2025-11-03")
        record = session.memory.facts[fact_id]
        self.assertEqual("known", record["status"])
        self.assertEqual("2025-11-03", record["value"])

    def test_pulse_synchronous_tinnitus_has_urgent_protective_handoff(self):
        package = compile_package(profile="ear_hearing_symptoms")
        rule = next(
            item for item in package["rule_graph"]["rules"]
            if item["id"] == "rule.ear-hearing-symptoms.safety.pulse-synchronous-tinnitus"
        )
        self.assertEqual(
            {"fact": "ear.tinnitus_pulse_synchronous", "equals": True},
            rule["when"],
        )
        self.assertEqual("urgent", rule["then"]["safety_level"])
        self.assertEqual("human_handoff", rule["then"]["action"])

    def test_draft_package_is_limited_and_non_diagnostic(self):
        package = compile_package(profile="ear_hearing_symptoms")
        usage = package["usage_policy"]
        self.assertEqual("draft", package["release_state"])
        self.assertEqual("unreviewed", usage["review_status"])
        self.assertEqual("limited", usage["clinical_use_status"])
        self.assertIn("clinician_supervised_pilot", usage["allowed_modes"])
        self.assertFalse(usage["independent_diagnosis_authority"])
        self.assertFalse(usage["independent_treatment_authority"])
        self.assertTrue(usage["notify_when_red_flag_is_suspected"])
        self.assertTrue(
            usage["interview_completion_must_not_delay_safety_notification"]
        )
        legacy_package = load_package(
            DEFAULT_PACKAGE, execution_mode="clinician_supervised_pilot"
        )
        self.assertEqual("draft", legacy_package["release_state"])

    def test_all_ear_hearing_simulations_pass(self):
        report = run_evaluation(EAR_HEARING_SYMPTOMS_PACKAGE)
        self.assertTrue(report["passed"], report["results"])
        self.assertEqual(16, report["case_count"])
        for case_id in (
            "EAR-PULSE-SYNCHRONOUS-TINNITUS",
            "EAR-TINNITUS-ASSOCIATED-VERTIGO",
        ):
            result = next(
                item for item in report["results"] if item["case_id"] == case_id
            )
            self.assertTrue(result["passed"], result)
        handoff = next(
            item for item in report["results"]
            if item["case_id"] == "EAR-HEARING-PRIOR-AUDIOGRAM-HANDOFF"
        )
        self.assertTrue(handoff["passed"], handoff)


if __name__ == "__main__":
    unittest.main()
