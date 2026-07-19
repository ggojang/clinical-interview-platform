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
    def test_adaptive_interview_turn_contract_regression_fixture(self):
        fixture = json.loads(
            (
                ROOT
                / "simulation/workflows/adaptive-interview-turn-contract-cases.json"
            ).read_text(encoding="utf-8")
        )
        self.assertFalse(fixture["contains_real_patient_data"])
        case = fixture["cases"][0]
        collecting = case["collecting_phase_expectations"]
        self.assertEqual(collecting["maximum_question_stems_per_assistant_turn"], 1)
        self.assertFalse(collecting["question_reference_resets_after_answer"])
        self.assertTrue(
            collecting["numbered_options_are_shortcuts_not_a_closed_answer_set"]
        )
        self.assertTrue(collecting["unlisted_free_text_is_accepted"])
        self.assertEqual(
            collecting["choice_guidance_ko"],
            "번호로 답하거나, 보기에 없으면 내용을 직접 입력해 주세요.",
        )
        self.assertEqual(
            collecting["ambiguous_free_text_clarification_reference"], "Q1"
        )
        self.assertFalse(collecting["ranked_differential_allowed"])
        self.assertFalse(collecting["management_or_self_test_advice_allowed"])
        completion = case["completion_phase_expectations"]
        self.assertTrue(completion["requires_explicit_confirmation"])
        self.assertTrue(completion["requires_separate_numbered_review_turn"])
        self.assertTrue(completion["review_rows_include_stable_q_or_u_reference"])
        self.assertEqual(completion["review_number_edit_command_example"], "수정 2")
        self.assertEqual(completion["review_complete_command"], "종료 확인")
        self.assertFalse(completion["completion_options_share_review_turn"])
        self.assertTrue(
            completion["first_or_unknown_encounter_baseline_must_be_resolved_before_review"]
        )
        self.assertTrue(completion["another_chat_is_not_reusable_clinical_memory"])
        self.assertFalse(completion["diagnosis_claim_allowed"])

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
                "hira-adequacy-assessments",
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
                "rfe-eye_symptoms-facts", "rfe-eye_symptoms-questions", "rfe-eye_symptoms-rules",
                "rfe-ear_hearing_symptoms-facts", "rfe-ear_hearing_symptoms-questions", "rfe-ear_hearing_symptoms-rules",
                "rfe-diabetes_follow_up-facts", "rfe-diabetes_follow_up-questions", "rfe-diabetes_follow_up-rules",
                "rfe-oral_dental_symptoms-facts", "rfe-oral_dental_symptoms-questions", "rfe-oral_dental_symptoms-rules",
                "rfe-oral_dental_symptoms-rules-completion", "rfe-oral_dental_symptoms-rules-priority",
                "rfe-wound_minor_injury-facts", "rfe-wound_minor_injury-questions", "rfe-wound_minor_injury-rules",
                "rfe-wound_minor_injury-rules-completion", "rfe-wound_minor_injury-rules-priority",
                "rfe-memory_cognitive_concern-facts", "rfe-memory_cognitive_concern-questions", "rfe-memory_cognitive_concern-rules",
                "rfe-memory_cognitive_concern-rules-completion", "rfe-memory_cognitive_concern-rules-priority",
                "rfe-pregnancy_postpartum_concern-facts", "rfe-pregnancy_postpartum_concern-questions", "rfe-pregnancy_postpartum_concern-rules",
                "rfe-pregnancy_postpartum_concern-rules-completion", "rfe-pregnancy_postpartum_concern-rules-priority",
                "rfe-allergy_concern-facts", "rfe-allergy_concern-questions", "rfe-allergy_concern-rules",
                "rfe-asthma_copd_follow_up-facts", "rfe-asthma_copd_follow_up-questions", "rfe-asthma_copd_follow_up-rules",
                "rfe-lump_lymph_node-facts", "rfe-lump_lymph_node-questions", "rfe-lump_lymph_node-rules",
                "rfe-dyspepsia_reflux-facts", "rfe-dyspepsia_reflux-questions", "rfe-dyspepsia_reflux-rules",
                "rfe-thyroid_concern_follow_up-facts", "rfe-thyroid_concern_follow_up-questions", "rfe-thyroid_concern_follow_up-rules",
                "rfe-anemia_concern_follow_up-facts", "rfe-anemia_concern_follow_up-questions", "rfe-anemia_concern_follow_up-rules",
                "rfe-seizure_event_follow_up-facts", "rfe-seizure_event_follow_up-questions", "rfe-seizure_event_follow_up-rules",
                "rfe-gait_falls_concern-facts", "rfe-gait_falls_concern-questions", "rfe-gait_falls_concern-rules",
                "rfe-epistaxis-facts", "rfe-epistaxis-questions", "rfe-epistaxis-rules",
                "rfe-pediatric_growth_development-facts", "rfe-pediatric_growth_development-questions", "rfe-pediatric_growth_development-rules",
                "rfe-tremor_movement_concern-facts", "rfe-tremor_movement_concern-questions", "rfe-tremor_movement_concern-rules",
                "rfe-neck_pain-facts", "rfe-neck_pain-questions", "rfe-neck_pain-rules",
                "rfe-menstrual_uterine_bleeding-facts", "rfe-menstrual_uterine_bleeding-questions", "rfe-menstrual_uterine_bleeding-rules",
                "rfe-kidney_function_ckd_follow_up-facts", "rfe-kidney_function_ckd_follow_up-questions", "rfe-kidney_function_ckd_follow_up-rules",
                "rfe-liver_function_chronic_follow_up-facts", "rfe-liver_function_chronic_follow_up-questions", "rfe-liver_function_chronic_follow_up-rules",
                "rfe-breast_symptoms-facts", "rfe-breast_symptoms-questions", "rfe-breast_symptoms-rules",
                "questionnaires-patient-experience-5th-2025-metadata",
                "questionnaires-patient-experience-5th-2025-sections-1",
                "questionnaires-patient-experience-5th-2025-sections-8",
            }.issubset(names))
            for resource in manifest["resources"]:
                self.assertEqual(len(resource["sha256"]), 64)
            for path in (output_path / "rfe").rglob("*.json"):
                self.assertLess(path.stat().st_size, 50_000, path)

    def test_patient_experience_questionnaire_is_split_and_chatbot_ready(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build(ROOT, output_path)
            base = output_path / "questionnaires/patient-experience-5th-2025"
            metadata = json.loads((base / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["reason_for_encounter"], "rfe.patient_experience_evaluation")
            self.assertEqual(metadata["section_count"], 8)
            self.assertEqual(metadata["question_count"], 26)
            self.assertIn("환자경험평가", metadata["activation_aliases_ko"])
            gate = metadata["activation_gate"]
            self.assertEqual(gate["workflow_state"], "awaiting_activation_confirmation")
            self.assertEqual(
                gate["required_next_question_ko"],
                "환자경험평가 설문을 작성하시겠습니까?",
            )
            self.assertEqual(
                gate["section_loading_precondition"],
                "affirmative_activation_answer",
            )
            self.assertEqual(list(gate["required_options"]), ["1", "2", "3", "4"])
            presentation = metadata["presentation_policy"]
            self.assertEqual(
                presentation["activation_prompt_ko"],
                "환자경험평가 설문을 작성하시겠습니까?",
            )
            self.assertEqual(
                presentation["activation_options"],
                {"1": "예", "2": "아니오", "3": "잘 모르겠음", "4": "답변하지 않음"},
            )
            self.assertTrue(presentation["opening_screen_and_explanation_allowed"])
            self.assertTrue(
                presentation["activation_prompt_is_final_actionable_question_before_start"]
            )
            self.assertTrue(
                presentation["affirmative_answer_enters_first_item_without_reconfirmation"]
            )
            self.assertTrue(presentation["display_only_source_answer_options"])
            self.assertTrue(presentation["do_not_append_unknown_or_decline_options"])
            self.assertTrue(metadata["loading_policy"]["load_one_section_at_a_time"])
            self.assertTrue(metadata["loading_policy"]["never_send_answers_to_knowledge_action"])
            sections = []
            for number in range(1, 9):
                path = base / "sections" / f"{number}.json"
                self.assertLess(path.stat().st_size, 12_000, path)
                section = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(section["section_number"], number)
                self.assertFalse(section["contains_patient_responses"])
                self.assertEqual(section["required_workflow_state"], "activation_confirmed")
                self.assertTrue(
                    section["if_activation_not_confirmed"]["do_not_present_section_items"]
                )
                self.assertEqual(
                    list(section["if_activation_not_confirmed"]["required_options"]),
                    ["1", "2", "3", "4"],
                )
                sections.append(section)
            self.assertEqual(sum(item["question_count"] for item in sections), 26)
            self.assertEqual(
                manifest["patient_experience_questionnaire_policy"]["question_count"],
                26,
            )
            self.assertEqual(
                manifest["preferred_loading"]["questionnaire_operations"],
                ["getPatientExperienceQuestionnaire", "getPatientExperienceQuestionnaireSection"],
            )

    def test_patient_experience_instructions_require_confirmation_then_direct_entry(self):
        instructions = (ROOT / "docs/gpt/GPT_INSTRUCTIONS.md").read_text(encoding="utf-8")
        self.assertIn("환자경험평가 설문을 작성하시겠습니까?", instructions)
        self.assertIn("existing opening screen may remain visible", instructions)
        self.assertIn("End that response with exactly one actionable question", instructions)
        self.assertIn("Present `section-1` item `q01` immediately", instructions)
        self.assertIn("or add an introductory sentence", instructions)

    def test_patient_experience_standalone_knowledge_file_is_complete(self):
        from tools.gpt_export.build_patient_experience_knowledge_file import build

        rendered = build()
        path = ROOT / "docs/gpt/knowledge-files/patient-experience-evaluation-5th-2025-chatbot.md"
        self.assertEqual(path.read_text(encoding="utf-8"), rendered)
        self.assertEqual(len(re.findall(r"^### `q\d{2}`$", rendered, re.MULTILINE)), 26)
        self.assertEqual(len(re.findall(r"^## 섹션 \d/8", rendered, re.MULTILINE)), 8)
        self.assertIn("### `q01`", rendered)
        self.assertIn("### `q26`", rendered)
        q01 = rendered.split("### `q01`", 1)[1].split("### `q02`", 1)[0]
        self.assertIn("- `4 항상 그랬다`", q01)
        self.assertNotIn("5 잘 모르겠음", q01)
        self.assertNotIn("6 답변하지 않음", q01)
        q24 = rendered.split("### `q24`", 1)[1].split("### `q25`", 1)[0]
        self.assertIn("- `1 예`", q24)
        self.assertIn("- `2 아니오`", q24)
        self.assertNotIn("잘 모르겠음", q24)
        self.assertNotIn("답변하지 않음", q24)

    def test_knowledge_action_exposes_patient_experience_operations(self):
        schema = (ROOT / "docs/gpt/openapi.yaml").read_text(encoding="utf-8")
        self.assertIn("operationId: getPatientExperienceQuestionnaire", schema)
        self.assertIn("operationId: getPatientExperienceQuestionnaireSection", schema)
        self.assertIn("ask its required confirmation question", schema)
        self.assertIn("only after affirmative activation confirmation", schema)
        self.assertIn("enum: [1, 2, 3, 4, 5, 6, 7, 8]", schema)
        self.assertIn("eye_symptoms", schema)
        self.assertIn("ear_hearing_symptoms", schema)
        self.assertIn("diabetes_follow_up", schema)
        self.assertIn("oral_dental_symptoms", schema)
        self.assertIn("wound_minor_injury", schema)
        self.assertIn("memory_cognitive_concern", schema)
        self.assertIn("pregnancy_postpartum_concern", schema)
        self.assertIn("allergy_concern", schema)
        self.assertIn("asthma_copd_follow_up", schema)
        self.assertIn("lump_lymph_node", schema)
        self.assertIn("dyspepsia_reflux", schema)
        self.assertIn("thyroid_concern_follow_up", schema)
        self.assertIn("anemia_concern_follow_up", schema)
        self.assertIn("seizure_event_follow_up", schema)
        self.assertIn("gait_falls_concern", schema)
        self.assertIn("epistaxis", schema)
        self.assertIn("pediatric_growth_development", schema)
        self.assertIn("tremor_movement_concern", schema)
        self.assertIn("neck_pain", schema)
        self.assertIn("menstrual_uterine_bleeding", schema)
        self.assertIn("kidney_function_ckd_follow_up", schema)
        self.assertIn("liver_function_chronic_follow_up", schema)
        self.assertIn("breast_symptoms", schema)
        self.assertIn("operationId: getReasonForEncounterRulePartition", schema)
        self.assertIn("operationId: getHiraAdequacyAssessmentInterviews", schema)
        self.assertIn(
            "operationId: getHiraAdequacyAssessmentInterviewProgram", schema
        )

    def test_hira_assessment_registry_is_exported_with_source_boundaries(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build(ROOT, output_path)
            registry = json.loads(
                (output_path / "hira-adequacy-assessments.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(
                registry["resource_type"],
                "HiraAdequacyAssessmentInterviewRegistry",
            )
            self.assertFalse(registry["contains_patient_responses"])
            self.assertNotIn("programs", registry)
            self.assertTrue(
                registry["program_payload_policy"][
                    "catalog_excludes_program_payloads"
                ]
            )
            self.assertTrue(
                registry["program_payload_policy"][
                    "prefetch_selected_program_before_start_confirmation"
                ]
            )
            self.assertTrue(
                registry["program_payload_policy"][
                    "do_not_display_items_before_affirmative_confirmation"
                ]
            )
            policy = manifest["hira_adequacy_assessment_policy"]
            self.assertTrue(policy["requires_explicit_program_and_current_cycle_context"])
            self.assertTrue(policy["patient_or_proxy_questions_only"])
            self.assertEqual(policy["entry_point"], "reason_for_encounter")
            self.assertTrue(policy["generic_request_returns_numbered_program_selection"])
            self.assertTrue(policy["specific_alias_requires_single_start_confirmation"])
            self.assertIn(
                "평가/설문 목록",
                manifest["interview_entry"]["discovery_hint_ko"],
            )
            self.assertIn(
                "설문 검색",
                manifest["interview_entry"]["discovery_commands"]["search_prefixes"],
            )
            self.assertEqual(
                manifest["interview_entry"]["conversation_starters"][0],
                "평가/설문 목록",
            )
            entries = registry["entry_catalog"]
            self.assertEqual(
                [entry["selection_number"] for entry in entries],
                list(range(1, 11)),
            )
            self.assertTrue(all(entry["aliases_ko"] for entry in entries))
            self.assertTrue(all(entry["start_prompt_ko"] for entry in entries))
            self.assertTrue(all(entry["source_notice_ko"] for entry in entries))
            self.assertEqual(
                sum(
                    entry["source_fidelity"]
                    == "official_source_questionnaire_verified"
                    for entry in entries
                ),
                1,
            )
            self.assertTrue(all(entry["program_resource"] for entry in entries))
            self.assertTrue(all(
                entry["program_operation"]
                == "getHiraAdequacyAssessmentInterviewProgram"
                for entry in entries
            ))
            for entry in entries:
                program_resource = json.loads(
                    (
                        output_path
                        / "assessments"
                        / f"{entry['program_id']}.json"
                    ).read_text(encoding="utf-8")
                )
                self.assertEqual(program_resource["id"], entry["program_id"])
                self.assertEqual(
                    program_resource["resource_type"],
                    "HiraAdequacyAssessmentInterviewProgram",
                )
                self.assertFalse(program_resource["contains_patient_responses"])
                self.assertEqual(
                    program_resource["program"]["id"], entry["program_id"]
                )
            self.assertEqual(
                manifest["preferred_loading"]["assessment_operation"],
                "getHiraAdequacyAssessmentInterviews",
            )
            self.assertEqual(
                manifest["preferred_loading"]["assessment_program_operation"],
                "getHiraAdequacyAssessmentInterviewProgram",
            )

    def test_custom_gpt_config_requires_clickable_assessment_catalog_starter(self):
        config = json.loads(
            (ROOT / "docs/gpt/custom-gpt-config.json").read_text(encoding="utf-8")
        )
        self.assertEqual(config["conversation_starters"][0], "평가/설문 목록")
        policy = config["conversation_starter_policy"]
        self.assertTrue(policy["primary_is_required"])
        self.assertTrue(policy["selection_opens_catalog_without_activation"])
        self.assertTrue(
            config["editor_application"]["requires_editor_save_or_update"]
        )

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
                    "abdominal_pain", "back_pain", "bowel_symptoms", "chest_pain", "cough", "diabetes_follow_up", "dizziness_syncope",
                    "dyspnea", "ear_hearing_symptoms", "edema", "eye_symptoms", "fatigue", "fever", "focal_weakness_numbness", "headache", "hypertension_follow_up", "joint_limb_complaint", "medication_review", "mental_health_sleep",
                    "allergy_concern", "anemia_concern_follow_up", "asthma_copd_follow_up", "breast_symptoms", "dyspepsia_reflux", "thyroid_concern_follow_up", "kidney_function_ckd_follow_up", "liver_function_chronic_follow_up", "epistaxis", "gait_falls_concern", "lump_lymph_node", "memory_cognitive_concern", "menstrual_uterine_bleeding", "neck_pain", "oral_dental_symptoms", "palpitations", "pediatric_growth_development", "pregnancy_postpartum_concern", "reproductive_genital_symptoms", "seizure_event_follow_up", "skin_complaint", "tremor_movement_concern", "upper_respiratory_symptoms", "urinary_symptoms", "wound_minor_injury",
                    "vomiting_diarrhea", "weight_constitutional_change",
                },
            )
            planned = {
                entry["id"] for entry in catalog["entries"]
                if entry.get("implementation_status") == "planned"
            }
            self.assertEqual(planned, set())
            self.assertTrue(all(
                "package_id" not in entry
                for entry in catalog["entries"]
                if entry["id"] in planned
            ))

            dysphagia = next(
                entry for entry in catalog["entries"]
                if entry["id"] == "rfe.dyspepsia_reflux"
            )
            self.assertIn("연하곤란", dysphagia["aliases"])
            self.assertIn("dysphagia", dysphagia["aliases"])
            abdominal = json.loads(
                (output_path / "rfe/abdominal_pain/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(abdominal["count"], 75)
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
            self.assertEqual(chest["count"], 73)
            headache = json.loads(
                (output_path / "rfe/headache/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(headache["count"], 76)
            dizziness = json.loads(
                (output_path / "rfe/dizziness_syncope/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(dizziness["count"], 73)
            vomiting_diarrhea = json.loads(
                (output_path / "rfe/vomiting_diarrhea/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(vomiting_diarrhea["count"], 74)
            urinary = json.loads(
                (output_path / "rfe/urinary_symptoms/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(urinary["count"], 39)
            fatigue = json.loads(
                (output_path / "rfe/fatigue/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(fatigue["count"], 75)
            cough = json.loads(
                (output_path / "rfe/cough/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(cough["count"], 70)
            back_pain = json.loads(
                (output_path / "rfe/back_pain/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(back_pain["count"], 36)
            skin = json.loads(
                (output_path / "rfe/skin_complaint/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(skin["count"], 38)
            medication = json.loads(
                (output_path / "rfe/medication_review/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(medication["count"], 67)
            upper = json.loads(
                (output_path / "rfe/upper_respiratory_symptoms/facts.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(upper["count"], 41)
            palpitations = json.loads(
                (output_path / "rfe/palpitations/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(palpitations["count"], 69)
            bowel = json.loads(
                (output_path / "rfe/bowel_symptoms/facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(bowel["count"], 67)
            focal = json.loads((output_path / "rfe/focal_weakness_numbness/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(focal["count"], 67)
            joint = json.loads((output_path / "rfe/joint_limb_complaint/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(joint["count"], 39)
            mental = json.loads((output_path / "rfe/mental_health_sleep/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(mental["count"], 39)
            edema = json.loads((output_path / "rfe/edema/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(edema["count"], 37)
            hypertension = json.loads((output_path / "rfe/hypertension_follow_up/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(hypertension["count"], 38)
            constitutional = json.loads((output_path / "rfe/weight_constitutional_change/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(constitutional["count"], 38)
            genital = json.loads((output_path / "rfe/reproductive_genital_symptoms/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(genital["count"], 51)
            eye = json.loads((output_path / "rfe/eye_symptoms/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(eye["count"], 45)
            ear = json.loads((output_path / "rfe/ear_hearing_symptoms/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(ear["count"], 46)
            diabetes = json.loads((output_path / "rfe/diabetes_follow_up/facts.json").read_text(encoding="utf-8"))
            self.assertEqual(diabetes["count"], 54)
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

    def test_manifest_declares_optional_consent_gated_feedback_boundary(self):
        with tempfile.TemporaryDirectory() as output:
            output_path = Path(output)
            manifest = build(ROOT, output_path)
            policy = manifest["anonymous_test_feedback_policy"]
            self.assertEqual(policy["consent_version"], "feedback-consent.v1")
            self.assertTrue(policy["completion_confirmation_is_not_feedback_consent"])
            self.assertTrue(policy["abandoned_after_first_message_observable_as_start_only"])
            self.assertFalse(policy["literal_page_open_observable"])
            self.assertIn("transcript", policy["forbidden_payloads"])
            self.assertIn("free_text", policy["forbidden_payloads"])
            start_policy = manifest["anonymous_test_session_analytics_policy"]
            self.assertEqual(start_policy["record_operation"], "recordAnonymousTestSessionStart")
            self.assertEqual(start_policy["trigger"], "once_after_first_user_message")
            self.assertIn("reason_for_encounter", start_policy["forbidden_payloads"])
            self.assertIn("ip_address", start_policy["forbidden_payloads"])

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
            self.assertTrue(numbering["display_question_sequence"])
            self.assertEqual(
                numbering["question_reference_format"], "Q{positive_integer}"
            )
            self.assertTrue(
                numbering["question_reference_never_resets_within_encounter"]
            )
            self.assertTrue(numbering["clarification_reuses_question_reference"])
            self.assertTrue(numbering["option_numbers_must_be_unique_within_question"])
            self.assertEqual(
                set(numbering["binary_question_only_codes"]), {"1", "2", "3", "4"}
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
            context_policy = manifest["encounter_context_policy"]
            self.assertTrue(context_policy["diagnosis_independent"])
            self.assertTrue(
                context_policy["emergency_or_urgent_context"]["safety_first"]
            )
            self.assertFalse(
                context_policy["remote_mode"]["physical_examination_available"]
            )
            self.assertEqual(
                context_policy["caregiver_initiated"]["response_source"],
                "proxy_report",
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
            review_phase = completion_policy["review_phase"]
            self.assertTrue(review_phase["must_precede_completion_confirmation"])
            self.assertTrue(
                review_phase["every_editable_row_has_continuous_review_number"]
            )
            self.assertTrue(
                review_phase["do_not_show_completion_options_in_same_turn_as_review_rows"]
            )
            self.assertEqual(review_phase["review_complete_command_ko"], "종료 확인")
            self.assertIn("수정 {review_number}", review_phase["edit_commands"])
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
            self.assertEqual(revision["edit_reference_format"], "Q{positive_integer}")
            self.assertEqual(
                revision["unprompted_fact_reference_format"],
                "U{positive_integer}",
            )
            self.assertEqual(
                revision["legacy_edit_reference_accepted_but_not_displayed"],
                "E{positive_integer}",
            )
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
            turn_contract = manifest["adaptive_interview_turn_contract"]
            self.assertTrue(
                turn_contract["collecting_phase"][
                    "exactly_one_question_per_assistant_turn"
                ]
            )
            self.assertTrue(
                turn_contract["collecting_phase"][
                    "forbid_ranked_differential_or_most_likely_disease"
                ]
            )
            self.assertTrue(
                turn_contract["completion_phase"]["final_guidance_only_after_confirmation"]
            )
            question_identity = turn_contract["question_identity"]
            self.assertTrue(
                question_identity["every_displayed_answer_option_has_visible_number"]
            )
            self.assertTrue(
                question_identity[
                    "numbered_options_are_shortcuts_not_a_closed_answer_set"
                ]
            )
            self.assertEqual(
                question_identity["choice_question_guidance_ko"],
                "번호로 답하거나, 보기에 없으면 내용을 직접 입력해 주세요.",
            )
            self.assertTrue(
                question_identity["accept_unlisted_korean_or_english_free_text"]
            )
            self.assertTrue(
                question_identity[
                    "ambiguous_free_text_reuses_same_question_reference_for_clarification"
                ]
            )
            self.assertTrue(
                question_identity[
                    "enumerated_unknown_and_decline_follow_global_option_policy"
                ]
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
                terminology["runtime_use"], "prohibited"
            )
            self.assertEqual(
                terminology["architectural_location"],
                "external_terminology_verification_adapter",
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
            claim = manifest["korean_claim_code_binding_policy"]
            self.assertFalse(claim["activation"]["proactive_claim_lookup"])
            self.assertTrue(
                claim["activation"]["lookup_only_when_supplied_input_or_explicit_user_goal_exists"]
            )
            self.assertIn(
                "uploaded_document_contains_explicit_claim_code_or_name",
                claim["activation"]["allowed_triggers"],
            )
            self.assertFalse(
                claim["domains"]["diagnosis"]["kcd9_general_search_currently_exposed"]
            )
            self.assertTrue(
                claim["domains"]["diagnosis"]["kcd9_morphology_search_is_not_general_diagnosis_search"]
            )
            self.assertEqual(
                claim["domains"]["procedure"]["system"],
                "http://www.hl7korea.or.kr/CodeSystem/hira-edi-procedure",
            )
            self.assertTrue(
                claim["domains"]["material"]["group_result_is_not_final_item_code"]
            )
            self.assertEqual(
                claim["semantic_claim_multi_coding"]["when_snomed_and_claim_code_are_both_known"],
                "preserve_both_as_information",
            )
            self.assertTrue(
                claim["fhir_r4_projection"]["same_codeable_concept_only_for_verified_exact_or_equivalent_meaning"]
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
            self.assertTrue(review_policy["ask_one_due_baseline_group_per_question"])
            self.assertTrue(
                review_policy[
                    "do_not_merge_diagnosis_and_procedure_history_into_one_binary_question"
                ]
            )
            self.assertTrue(review_policy["new_chat_is_not_proof_of_first_encounter"])
            self.assertTrue(review_policy["no_cross_chat_clinical_memory_in_test_gpt"])
            self.assertTrue(
                review_policy["never_assume_another_chat_answered_baseline_history"]
            )
            self.assertTrue(
                review_policy[
                    "only_reuse_baseline_facts_explicit_in_current_conversation_or_current_upload"
                ]
            )
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
            preventive_policy = manifest["preventive_context_review_policy"]
            self.assertTrue(
                preventive_policy["separate_from_general_first_encounter_baseline"]
            )
            self.assertEqual(
                preventive_policy["fact_ids"],
                ["preventive.immunization.history"],
            )
            self.assertTrue(
                preventive_policy[
                    "do_not_activate_for_unrelated_ordinary_symptom_encounter"
                ]
            )
            self.assertTrue(
                preventive_policy[
                    "vaccine_due_status_requires_age_risk_jurisdiction_and_current_schedule"
                ]
            )
            self.assertEqual(
                manifest["terminology_lookup_policy"]["architectural_location"],
                "external_terminology_verification_adapter",
            )
            self.assertEqual(
                manifest["terminology_lookup_policy"]["runtime_use"],
                "prohibited",
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
                    "claim.diagnosis.code",
                    "claim.procedure.code",
                    "claim.medication.code",
                    "claim.material.code",
                    "terminology.semantic_claim_binding",
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
            safety_index = json.loads(
                (output_path / "safety-rules.json").read_text(encoding="utf-8")
            )
            self.assertEqual(safety_index["default_action"], "human_handoff")
            self.assertTrue(safety_index["default_equals"])
            self.assertEqual(
                safety_index["returned_count"], len(safety_index["items"])
            )
            self.assertEqual(
                safety_index["truncated"],
                safety_index["returned_count"] < safety_index["count"],
            )
            self.assertEqual(
                safety_index["complete_rule_payloads"],
                "/gpt/rfe/{rfe}/rules.json",
            )
            fact_index = json.loads(
                (output_path / "facts.json").read_text(encoding="utf-8")
            )
            self.assertEqual(fact_index["payload_role"], "legacy_discovery_index")
            self.assertTrue(all("id" in item for item in fact_index["items"]))
            self.assertEqual(fact_index["returned_count"], len(fact_index["items"]))
            self.assertEqual(fact_index["truncated"], fact_index["returned_count"] < fact_index["count"])
            self.assertEqual(fact_index["complete_fact_payloads"], "/gpt/rfe/{rfe}/facts.json")
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
        self.assertIn("operationId: searchHiraProcedure", schema)
        self.assertIn("operationId: searchHiraTherapeuticMaterial", schema)
        self.assertIn("operationId: getHiraProcedureByCode", schema)
        self.assertIn("operationId: getHiraMedicationByCode", schema)
        self.assertIn("operationId: getHiraTherapeuticMaterialByCode", schema)
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
        self.assertEqual([option["number"] for option in options], [1, 2, 3, 4])

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
