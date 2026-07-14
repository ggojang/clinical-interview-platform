import json
import re
import tempfile
import unittest
from pathlib import Path

from tools.gpt_export.build import build, number_answer_options
from tools.privacy.check_repository import scan


ROOT = Path(__file__).resolve().parents[1]


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


class GptExportTests(unittest.TestCase):
    def test_export_is_deterministic_and_response_free(self):
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            first_path = Path(first)
            second_path = Path(second)
            one = build(ROOT, first_path)
            two = build(ROOT, second_path)
            self.assertEqual(one, two)
            self.assertEqual(
                sorted(
                    (path.relative_to(first_path), path.read_bytes())
                    for path in first_path.rglob("*") if path.is_file()
                ),
                sorted(
                    (path.relative_to(second_path), path.read_bytes())
                    for path in second_path.rglob("*") if path.is_file()
                ),
            )
            forbidden = {
                "raw_text", "raw_input", "patient_response", "patient_responses",
                "questionnaire_response", "conversation", "transcript", "evidence",
            }
            for path in first_path.rglob("*.json"):
                document = json.loads(path.read_text(encoding="utf-8"))
                self.assertFalse(forbidden & {key.lower() for key in walk_keys(document)})
                self.assertFalse(document.get("contains_patient_responses", False))

    def test_export_has_core_resources(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build(ROOT, output_path)
            names = {resource["name"] for resource in manifest["resources"]}
            self.assertTrue({
                "common-facts", "reason-for-encounters", "screening-kr",
                "terminology-source",
                "rfe-cough-facts", "rfe-cough-questions", "rfe-cough-rules",
                "rfe-dyspnea-facts", "rfe-dyspnea-questions", "rfe-dyspnea-rules",
                "rfe-fever-facts", "rfe-fever-questions", "rfe-fever-rules",
                "rfe-abdominal_pain-facts", "rfe-abdominal_pain-questions",
                "rfe-abdominal_pain-rules",
                "rfe-chest_pain-facts", "rfe-chest_pain-questions",
                "rfe-chest_pain-rules",
                "rfe-headache-facts", "rfe-headache-questions",
                "rfe-headache-rules",
                "rfe-dizziness_syncope-facts", "rfe-dizziness_syncope-questions",
                "rfe-dizziness_syncope-rules",
                "rfe-vomiting_diarrhea-facts", "rfe-vomiting_diarrhea-questions",
                "rfe-vomiting_diarrhea-rules",
                "rfe-urinary_symptoms-facts", "rfe-urinary_symptoms-questions",
                "rfe-urinary_symptoms-rules",
                "rfe-fatigue-facts", "rfe-fatigue-questions", "rfe-fatigue-rules",
                "rfe-back_pain-facts", "rfe-back_pain-questions",
                "rfe-back_pain-rules",
                "rfe-skin_complaint-facts", "rfe-skin_complaint-questions",
                "rfe-skin_complaint-rules",
                "rfe-medication_review-facts", "rfe-medication_review-questions",
                "rfe-medication_review-rules",
                "rfe-upper_respiratory_symptoms-facts",
                "rfe-upper_respiratory_symptoms-questions",
                "rfe-upper_respiratory_symptoms-rules",
                "rfe-palpitations-facts", "rfe-palpitations-questions",
                "rfe-palpitations-rules",
                "rfe-bowel_symptoms-facts", "rfe-bowel_symptoms-questions",
                "rfe-bowel_symptoms-rules",
                "rfe-focal_weakness_numbness-facts", "rfe-focal_weakness_numbness-questions", "rfe-focal_weakness_numbness-rules",
                "rfe-joint_limb_complaint-facts", "rfe-joint_limb_complaint-questions", "rfe-joint_limb_complaint-rules",
                "rfe-mental_health_sleep-facts", "rfe-mental_health_sleep-questions", "rfe-mental_health_sleep-rules",
                "rfe-edema-facts", "rfe-edema-questions", "rfe-edema-rules",
                "rfe-hypertension_follow_up-facts", "rfe-hypertension_follow_up-questions", "rfe-hypertension_follow_up-rules",
                "rfe-weight_constitutional_change-facts", "rfe-weight_constitutional_change-questions", "rfe-weight_constitutional_change-rules",
                "rfe-reproductive_genital_symptoms-facts", "rfe-reproductive_genital_symptoms-questions", "rfe-reproductive_genital_symptoms-rules",
            }.issubset(names))
            for resource in manifest["resources"]:
                self.assertEqual(len(resource["sha256"]), 64)
            for path in (output_path / "rfe").rglob("*.json"):
                self.assertLess(path.stat().st_size, 50_000, path)

    def test_rfe_catalog_and_bundles_are_consistent(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            build(ROOT, output_path)
            catalog = json.loads(
                (output_path / "reason-for-encounters.json").read_text(encoding="utf-8")
            )
            implemented = {
                entry["id"].removeprefix("rfe.")
                for entry in catalog["entries"]
                if entry.get("implementation_status") == "implemented"
                and entry["id"] != "rfe.preventive_care"
            }
            self.assertEqual(
                implemented,
                {
                    "abdominal_pain", "back_pain", "bowel_symptoms", "chest_pain", "cough", "dizziness_syncope",
                    "dyspnea", "edema", "fatigue", "fever", "focal_weakness_numbness", "headache", "hypertension_follow_up", "joint_limb_complaint", "medication_review", "mental_health_sleep",
                    "palpitations", "reproductive_genital_symptoms", "skin_complaint", "upper_respiratory_symptoms", "urinary_symptoms",
                    "vomiting_diarrhea", "weight_constitutional_change",
                },
            )
            abdominal = json.loads(
                (output_path / "rfe/abdominal_pain/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(abdominal["count"], 28)
            location = next(
                item for item in abdominal["items"]
                if item["id"] == "symptom.abdominal_pain.location"
            )
            self.assertEqual(
                location["mrcm_validation"]["status"], "provisional_pass"
            )
            chest = json.loads(
                (output_path / "rfe/chest_pain/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(chest["count"], 30)
            headache = json.loads(
                (output_path / "rfe/headache/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(headache["count"], 30)
            dizziness = json.loads(
                (output_path / "rfe/dizziness_syncope/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(dizziness["count"], 31)
            vomiting_diarrhea = json.loads(
                (output_path / "rfe/vomiting_diarrhea/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(vomiting_diarrhea["count"], 30)
            urinary = json.loads(
                (output_path / "rfe/urinary_symptoms/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(urinary["count"], 37)
            fatigue = json.loads(
                (output_path / "rfe/fatigue/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(fatigue["count"], 34)
            back_pain = json.loads(
                (output_path / "rfe/back_pain/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(back_pain["count"], 34)
            skin = json.loads(
                (output_path / "rfe/skin_complaint/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(skin["count"], 36)
            medication = json.loads(
                (output_path / "rfe/medication_review/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(medication["count"], 36)
            upper = json.loads(
                (output_path / "rfe/upper_respiratory_symptoms/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(upper["count"], 39)
            palpitations = json.loads(
                (output_path / "rfe/palpitations/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(palpitations["count"], 36)
            bowel = json.loads(
                (output_path / "rfe/bowel_symptoms/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(bowel["count"], 35)
            focal = json.loads((output_path / "rfe/focal_weakness_numbness/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(focal["count"], 32)
            joint = json.loads((output_path / "rfe/joint_limb_complaint/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(joint["count"], 37)
            mental = json.loads((output_path / "rfe/mental_health_sleep/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(mental["count"], 39)
            edema = json.loads((output_path / "rfe/edema/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(edema["count"], 35)
            hypertension = json.loads((output_path / "rfe/hypertension_follow_up/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(hypertension["count"], 38)
            constitutional = json.loads((output_path / "rfe/weight_constitutional_change/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(constitutional["count"], 38)
            genital = json.loads((output_path / "rfe/reproductive_genital_symptoms/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(genital["count"], 49)
            for slug in implemented:
                for kind in ("facts", "questions", "rules"):
                    document = json.loads(
                        (output_path / "rfe" / slug / f"{kind}.json").read_text(
                            encoding="utf-8"
                        )
                    )
                    self.assertEqual(document["reason_for_encounter"], f"rfe.{slug}")
                    self.assertGreater(document["count"], 0)
                    self.assertFalse(document["contains_patient_responses"])
                    self.assertTrue(document["knowledge_sources"])
                    self.assertTrue(
                        document["knowledge_source_status"][
                            "clinical_sources_are_compiled_not_queried_live"
                        ]
                    )

    def test_additional_comment_is_structured_and_upgrade_aware(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            build(ROOT, output_path)
            facts = json.loads((output_path / "common-facts.json").read_text(encoding="utf-8"))
            comment = next(
                item for item in facts["items"] if item["id"] == "interview.additional_comment"
            )
            self.assertTrue(comment["handling"]["resolution_includes_improvement"])
            self.assertTrue(comment["handling"]["never_publish_raw_response"])
            self.assertIn("improvement_status", comment["fields"])

    def test_backward_compatible_action_payloads_stay_below_limit(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build(ROOT, output_path)
            self.assertEqual(manifest["interview_entry"]["type"], "reason_for_encounter")
            source_catalog = json.loads(
                (ROOT / "knowledge/catalog/primary-care-rfe.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                len(manifest["interview_entry"]["catalog"]),
                len(source_catalog["entries"]),
            )
            self.assertTrue(
                manifest["additional_comment_policy"][
                    "resolution_includes_service_improvement"
                ]
            )
            numbering = manifest["numbering_policy"]
            self.assertFalse(numbering["display_question_sequence"])
            self.assertTrue(numbering["option_numbers_must_be_unique_within_question"])
            self.assertEqual(
                set(numbering["binary_question_only_codes"]), {"1", "2", "3", "5"}
            )
            alignment = manifest["question_choice_semantic_alignment_policy"]
            self.assertTrue(alignment["pre_send_validation_required"])
            self.assertTrue(alignment["exactly_one_presentation_pattern"])
            binary = alignment["binary_single_proposition"]
            self.assertEqual(
                [option["code"] for option in binary["domain_options"]],
                ["yes", "no"],
            )
            self.assertIn("다음 중", binary["forbidden_stem_phrases"])
            self.assertTrue(binary["options_answer_the_whole_proposition"])
            multiple = alignment["multiple_clinical_choices"]
            self.assertTrue(
                multiple["every_clinical_finding_must_be_a_displayed_domain_option"]
            )
            self.assertTrue(multiple["do_not_use_yes_or_no_as_domain_options"])
            self.assertEqual(
                multiple["append_order"],
                ["none_of_the_above", "unknown", "decline"],
            )
            self.assertEqual(
                multiple["exclusive_options"],
                ["none_of_the_above", "unknown", "decline"],
            )
            self.assertTrue(
                alignment["safety_gate"]["same_alignment_rules_apply"]
            )
            result_policy = manifest["result_follow_up_policy"]
            self.assertFalse(
                result_policy["institution_result_check"]["request_upload"]
            )
            self.assertTrue(
                result_policy["interpretation_request"]["request_upload_once"]
            )
            upload_policy = manifest["uploaded_clinical_material_policy"]
            self.assertTrue(upload_policy["extract_only_explicit_information"])
            self.assertTrue(
                upload_policy["reuse_explicit_current_facts_to_avoid_duplicate_questions"]
            )
            self.assertEqual(
                upload_policy["conflict_handling"],
                "preserve_both_sources_and_ask_targeted_clarification",
            )
            self.assertTrue(upload_policy["do_not_send_patient_material_to_actions"])
            completion_policy = manifest["completion_handoff_policy"]
            self.assertTrue(
                completion_policy["requires_explicit_user_confirmation"]
            )
            self.assertTrue(
                completion_policy["do_not_mark_completed_before_confirmation"]
            )
            option_numbers = [
                option["number"] for option in completion_policy["options"]
            ]
            self.assertEqual(option_numbers, [1, 2, 3, 4, 5])
            self.assertEqual(len(option_numbers), len(set(option_numbers)))
            fhir_status = completion_policy[
                "future_fhir_r4_questionnaire_response_status"
            ]
            self.assertEqual(fhir_status["awaiting_user_confirmation"], "in-progress")
            self.assertEqual(fhir_status["user_completed"], "completed")
            self.assertEqual(fhir_status["user_stopped"], "stopped")
            self.assertEqual(fhir_status["corrected_after_completion"], "amended")
            self.assertTrue(
                completion_policy["completion_confirmation_is_not_consent"]
            )
            revision = manifest["answer_revision_policy"]
            self.assertEqual(revision["edit_reference_format"], "E{positive_integer}")
            self.assertTrue(
                revision["never_use_bare_question_option_number_as_edit_reference"]
            )
            self.assertTrue(
                revision["audit"]["never_delete_or_silently_overwrite_prior_answer"]
            )
            self.assertTrue(
                revision["value_entry"]["do_not_apply_replacement_to_any_other_fact"]
            )
            self.assertTrue(
                revision["conditional_branch_change"]["new_branch_facts_become_required_when_applicable"]
            )
            self.assertTrue(
                revision["after_completion"]["require_completion_reconfirmation_after_recalculation"]
            )
            self.assertTrue(
                revision["safety"]["new_urgent_or_emergency_result_interrupts_revision_flow"]
            )
            clarification = manifest["answer_understanding_clarification_policy"]
            self.assertTrue(clarification["preserve_current_question_as_unanswered"])
            self.assertTrue(clarification["do_not_advance_to_next_question"])
            self.assertTrue(
                clarification["do_not_store_suggested_interpretation_as_fact_before_confirmation"]
            )
            self.assertEqual(
                clarification["likely_typo_flow"]["auto_accept_threshold"], "never"
            )
            self.assertTrue(
                clarification["safety"]["urgent_or_emergency_routing_precedes_clarification"]
            )
            self.assertTrue(
                clarification["retry_policy"]["never_force_data_absent_reason_without_explicit_user_choice"]
            )
            limit_notice = manifest["test_access_limit_notice_policy"]
            self.assertEqual(
                limit_notice["timing"],
                "after_reason_for_encounter_before_first_question",
            )
            self.assertTrue(
                limit_notice["must_not_replace_reason_for_encounter_entry"]
            )
            self.assertTrue(limit_notice["do_not_claim_fixed_quota_or_reset_time"])
            self.assertEqual(
                limit_notice["rate_limit_interruption_status"], "in-progress"
            )
            terminology = manifest["terminology_lookup_policy"]
            self.assertEqual(
                terminology["runtime_use"], "optional_semantic_alignment_only"
            )
            self.assertFalse(
                terminology["clinical_rule_selection_from_live_terminology"]
            )
            self.assertFalse(terminology["send_raw_patient_response"])
            self.assertTrue(
                terminology["send_only_minimal_normalized_term_or_code"]
            )
            self.assertIn(
                "verify_finding_site_membership_in_723264001_before_laterality",
                terminology["mapping_flow"],
            )
            self.assertIn("stom-openapi.yaml", terminology["action_schema_url"])
            laterality = manifest["snomed_laterality_postcoordination_policy"]
            self.assertEqual(
                laterality["codes"]["lateralizable_body_structure_refset"],
                "723264001",
            )
            self.assertEqual(laterality["codes"]["finding_site_attribute"], "363698007")
            self.assertEqual(laterality["codes"]["laterality_attribute"], "272741003")
            self.assertTrue(
                laterality["expression_model"]["nest_laterality_on_finding_site_value"]
            )
            self.assertTrue(
                laterality["expression_model"]["never_emit_single_nested_right_and_left_as_final_classifiable_form"]
            )
            self.assertTrue(
                laterality["normal_form_preconditions"]["reject_already_lateralized_anatomical_value"]
            )
            provenance_display = manifest["response_provenance_display_policy"]
            self.assertTrue(
                provenance_display["compact_marker_required_for_every_question"]
            )
            self.assertTrue(
                provenance_display[
                    "never_label_ai_generated_content_as_project_knowledge"
                ]
            )
            self.assertTrue(provenance_display["never_hide_mixed_origin"])
            self.assertEqual(
                provenance_display["source_classes"]["project_knowledge"]["display_ko"],
                "공동 작업 지식",
            )
            self.assertEqual(
                provenance_display["source_classes"]["ai_generated"]["display_ko"],
                "AI 자체 생성",
            )
            self.assertEqual(
                provenance_display["final_report_section_ko"],
                "출처 및 생성 구분",
            )
            off_path = manifest["off_path_recovery_policy"]
            self.assertTrue(off_path["preserve_current_question_as_unanswered"])
            self.assertTrue(
                off_path["safety_reassessment_precedes_detour_response"]
            )
            recovery_numbers = [option["number"] for option in off_path["options"]]
            self.assertEqual(recovery_numbers, [1, 2, 3, 4, 5])
            self.assertEqual(len(recovery_numbers), len(set(recovery_numbers)))
            self.assertEqual(
                off_path["route"]["begin_completion"],
                "summarize_missing_facts_then_use_completion_handoff",
            )
            self.assertEqual(
                off_path["data_absent_on_completion_after_detour"][
                    "current_question_explicitly_left_unanswered"
                ],
                "asked-declined",
            )
            review_policy = manifest["longitudinal_context_review_policy"]
            self.assertEqual(
                review_policy["unknown_last_confirmed_at"],
                "ask_single_recency_gate_then_due_if_still_unknown",
            )
            self.assertTrue(
                review_policy["do_not_ask_separate_recency_question_per_group"]
            )
            self.assertTrue(review_policy["new_chat_is_not_proof_of_first_encounter"])
            self.assertEqual(
                review_policy["first_encounter_required_group_order"],
                [
                    "history.conditions",
                    "history.procedures",
                    "medication.current",
                    "allergy.current",
                    "history.family",
                    "occupation.current",
                    "social.smoking",
                    "social.alcohol",
                ],
            )
            self.assertTrue(
                review_policy["completion_requires_every_due_group_resolved"]
            )
            self.assertTrue(
                review_policy["symptom_irrelevance_is_not_valid_first_encounter_omission"]
            )
            self.assertEqual(
                review_policy["groups"]["medication.current"]["interval_days"], 90
            )
            self.assertEqual(
                review_policy["groups"]["history.conditions"]["interval_days"], 365
            )
            self.assertEqual(
                review_policy["groups"]["history.procedures"]["fact_ids"],
                ["history.procedure.past"],
            )
            common = json.loads(
                (output_path / "common-facts.json").read_text(encoding="utf-8")
            )
            common_ids = {item["id"] for item in common["items"]}
            self.assertTrue(
                {
                    "history.condition.current",
                    "history.procedure.past",
                    "medication.current",
                    "allergy.current",
                    "history.family",
                    "occupation.current",
                    "patient.smoking.status",
                    "patient.alcohol.pattern",
                    "finding.site_laterality",
                    "encounter.is_first",
                    "context.last_confirmed_at",
                }.issubset(common_ids)
            )
            self.assertEqual(
                review_policy["data_absent_reason_by_state"]["unknown"],
                "asked-unknown",
            )
            self.assertEqual(
                review_policy["data_absent_reason_by_state"]["declined"],
                "asked-declined",
            )
            self.assertTrue(
                review_policy["known_absence_is_answered_not_data_absent"]
            )
            for name in ("facts.json", "question-groups.json", "safety-rules.json"):
                self.assertLess((output_path / name).stat().st_size, 100_000, name)
            questions = json.loads(
                (output_path / "question-groups.json").read_text(encoding="utf-8")
            )
            for question in questions["items"]:
                if question.get("type") != "QuestionTemplate":
                    continue
                self.assertIsInstance(question.get("text") or question.get("wording"), str)
                if "fact_id" in question:
                    self.assertTrue(
                        question["fact_id"] is None or isinstance(question["fact_id"], str)
                    )

    def test_stom_action_is_read_only_and_minimized(self):
        schema = (ROOT / "docs" / "gpt" / "stom-openapi.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn("https://stom.infoclinic.co", schema)
        self.assertIn("operationId: searchSnomedMappingCandidates", schema)
        self.assertIn("operationId: lookupTerminologyCode", schema)
        self.assertIn("operationId: checkSnomedReferenceSetMembership", schema)
        self.assertIn("723264001", schema)
        self.assertIn("operationId: searchLoinc", schema)
        self.assertIn("operationId: searchHiraDrug", schema)
        self.assertNotIn("\n    put:", schema.lower())
        self.assertNotIn("\n    delete:", schema.lower())
        self.assertIn("maxLength: 80", schema)

    def test_question_text_does_not_embed_display_sequence(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            build(ROOT, output_path)
            paths = [output_path / "question-groups.json"]
            paths.extend((output_path / "rfe").glob("*/questions.json"))
            prefix = re.compile(r"^\s*(?:질문\s*)?\d+\s*(?:번|[.)：:])")
            for path in paths:
                document = json.loads(path.read_text(encoding="utf-8"))
                for question in document["items"]:
                    text = question.get("text") or question.get("wording")
                    if isinstance(text, str):
                        self.assertIsNone(prefix.match(text), (path, question.get("id")))

    def test_enumerated_option_numbering_never_collides(self):
        options = number_answer_options([
            "피곤하거나 잠을 잘 못 잤음",
            "스트레스가 많았음",
            "입안을 씹었거나 상처가 있었음",
            "감기·몸살 같은 증상이 있었음",
            "해당 없음",
        ])
        numbers = [option["number"] for option in options]
        self.assertEqual(numbers, [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(len(numbers), len(set(numbers)))
        self.assertEqual(options[-2]["code"], "unknown")
        self.assertEqual(options[-1]["code"], "decline")

    def test_binary_shortcuts_remain_stable(self):
        options = number_answer_options(["예", "아니오"])
        self.assertEqual([option["number"] for option in options], [1, 2, 3, 5])

    def test_privacy_scanner_detects_direct_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            synthetic_identifier = "900101" + "-" + "1234567"
            (root / "bad.md").write_text(f"identifier {synthetic_identifier}", encoding="utf-8")
            findings = scan(root)
            self.assertTrue(any("resident registration" in finding for finding in findings))

    def test_privacy_scanner_does_not_treat_sha256_as_identifier(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manifest.json").write_text(
                '{"sha256":"c8570274866163bc0b79b24a3b170ee7356a48cfecf22bbca18564227eb6ca2c"}',
                encoding="utf-8",
            )
            self.assertEqual(scan(root), [])


if __name__ == "__main__":
    unittest.main()
