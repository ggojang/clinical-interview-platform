import json
import tempfile
import unittest
from pathlib import Path

from compiler.build_package import PACKAGE_PROFILES, compile_package
from runtime.session import InterviewSession, fact


class ClinicianSubmissionContextTest(unittest.TestCase):
    @staticmethod
    def _synthetic_answer(session: InterviewSession, fact_id: str) -> str:
        node = session._fact_node(fact_id)
        if node.get("value_type") == "boolean":
            return "2"
        if node.get("allowed_values"):
            return node["allowed_values"][0]
        if node.get("value_type") == "integer":
            return "1"
        if node.get("value_type") == "string":
            return "없음"
        return "3"

    def _session(self) -> InterviewSession:
        package = compile_package(profile="cough")
        temporary = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        temporary.close()
        path = Path(temporary.name)
        path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(path.unlink, missing_ok=True)
        return InterviewSession(
            "clinician-context-test",
            package_path=path,
            clinician_submission=True,
        )

    def test_every_package_embeds_reusable_context_without_graph_duplication(self):
        for profile in PACKAGE_PROFILES:
            with self.subTest(profile=profile):
                package = compile_package(profile=profile)
                context = package["clinician_submission_context"]
                self.assertEqual(context["status"], "research_only")
                self.assertEqual(context["review_status"], "unreviewed")
                self.assertEqual(
                    context["resource_ref"],
                    "knowledge/shared/clinician-submission-context.json",
                )
                self.assertTrue(context["semantic_digest"].startswith("sha256:"))
                module = json.loads(
                    (Path(__file__).resolve().parents[1] / context["resource_ref"])
                    .read_text(encoding="utf-8")
                )
                minimum = module["completion"]["clinician_rfe_minimum"]
                rfe = package["scope"]["reasons_for_encounter"][0]
                self.assertIn(rfe, minimum["audited_reason_for_encounters"])
                graph_facts = {
                    node["id"] for node in package["knowledge_graph"]["nodes"]
                    if node["type"] == "Fact"
                }
                graph_questions = set(package["indexes"]["questions_by_fact"])
                additions = set(
                    minimum["additional_required_facts_by_rfe"].get(rfe, [])
                )
                self.assertTrue(additions <= graph_facts)
                self.assertTrue(additions <= graph_questions)
                self.assertNotIn(
                    "encounter.context_review_state",
                    package["indexes"]["questions_by_fact"],
                )
                facts = {item["id"] for item in module["facts"]}
                self.assertIn("preventive.immunization.history", facts)
                sections = {
                    item["id"]: item
                    for item in module["clinician_handoff"]["sections"]
                }
                self.assertIn("preventive_history", sections)
                self.assertIn(
                    "preventive.immunization.history",
                    sections["preventive_history"]["fact_ids"],
                )

    def test_every_generated_package_loads_in_clinician_submission_mode(self):
        for profile, config in PACKAGE_PROFILES.items():
            with self.subTest(profile=profile):
                session = InterviewSession(
                    f"generated-clinician-{profile}",
                    package_path=config["output"],
                    clinician_submission=True,
                )
                handoff = session.clinician_handoff()
                self.assertEqual(
                    handoff["sections"][0]["id"],
                    "reason_for_encounter_clinical_facts",
                )

    def test_opt_in_mode_adds_context_requirements_and_numeric_mapping(self):
        session = self._session()
        required = session._required_facts(None, session._safety())
        self.assertIn("encounter.context_review_state", required)
        self.assertIn("encounter.information_source", required)
        self.assertIn("patient.age_years", required)
        self.assertIn("patient.sex_for_clinical_care", required)
        self.assertIn("interview.final_additional_comment", required)

        session.last_question_fact = "encounter.context_review_state"
        state = session.process("1")
        self.assertEqual(
            session.memory.value("encounter.context_review_state"),
            "first_encounter",
        )
        self.assertIn("history.condition.current", state["completion_status"]["required_facts"])
        self.assertIn(
            "patient.alcohol.use_status",
            state["completion_status"]["required_facts"],
        )
        self.assertNotIn(
            "patient.alcohol.amount_per_occasion",
            state["completion_status"]["required_facts"],
        )

    def test_social_history_details_are_atomic_and_conditionally_required(self):
        session = self._session()
        session.memory.merge(
            "encounter.context_review_state",
            fact("first_encounter", "합성 첫 문진", 1),
        )
        session.memory.merge(
            "patient.smoking.status", fact("current", "현재 흡연", 2)
        )
        session.memory.merge(
            "patient.alcohol.use_status", fact("current", "현재 음주", 3)
        )

        required = set(session._required_facts(None, session._safety()))

        self.assertTrue({
            "patient.smoking.product_types",
            "patient.smoking.cigarettes_per_day",
            "patient.smoking.duration_years",
            "patient.alcohol.beverage_types",
            "patient.alcohol.frequency",
            "patient.alcohol.amount_per_occasion",
        } <= required)
        self.assertNotIn("patient.smoking.exposure_detail", required)
        self.assertNotIn("patient.alcohol.pattern", required)

    def test_smoking_quantity_accepts_patient_wording_with_unit(self):
        session = self._session()
        session.last_question_fact = "patient.smoking.cigarettes_per_day"
        session.asked = ["patient.smoking.cigarettes_per_day"]

        state = session.process("하루 10개비")

        self.assertEqual(
            session.memory.value("patient.smoking.cigarettes_per_day"),
            {"amount": 10, "unit": "{cigarette}/d"},
        )
        self.assertIsNone(state["answer_clarification"])

    def test_smoking_quantity_does_not_accept_duration_unit(self):
        session = self._session()
        session.last_question_fact = "patient.smoking.cigarettes_per_day"
        session.asked = ["patient.smoking.cigarettes_per_day"]

        session.process("20년")

        self.assertIsNone(
            session.memory.value("patient.smoking.cigarettes_per_day")
        )

    def test_rich_smoking_answer_prefills_atomic_facts_without_reasking(self):
        session = self._session()
        rich_fact = "cough.smoking_vaping_cannabis_pack_years_last_use_and_change"
        session.last_question_fact = rich_fact
        session.asked = [rich_fact]

        state = session.process(
            "현재 일반담배를 하루 10개비씩 20년간 피우고 있습니다"
        )

        self.assertEqual(session.memory.value("patient.smoking.status"), "current")
        self.assertEqual(
            session.memory.value("patient.smoking.product_types"),
            "combustible_cigarette",
        )
        self.assertEqual(
            session.memory.value("patient.smoking.cigarettes_per_day"),
            {"amount": 10, "unit": "{cigarette}/d"},
        )
        self.assertEqual(
            session.memory.value("patient.smoking.duration_years"),
            {"amount": 20, "unit": "a"},
        )
        missing = set(state["completion_status"]["missing_facts"])
        self.assertFalse({
            "patient.smoking.product_types",
            "patient.smoking.cigarettes_per_day",
            "patient.smoking.duration_years",
        } & missing)

    def test_heated_tobacco_is_not_duplicated_as_liquid_e_cigarette(self):
        session = self._session()
        rich_fact = "cough.smoking_vaping_cannabis_pack_years_last_use_and_change"
        session.last_question_fact = rich_fact
        session.asked = [rich_fact]

        session.process("현재 궐련형 전자담배를 사용하고 있습니다")

        self.assertEqual(
            session.memory.value("patient.smoking.product_types"),
            "heated_tobacco",
        )

    def test_rich_alcohol_answer_prefills_beverage_frequency_and_amount(self):
        package = compile_package(profile="hypertension_follow_up")
        temporary = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        temporary.close()
        path = Path(temporary.name)
        path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(path.unlink, missing_ok=True)
        session = InterviewSession(
            "clinician-alcohol-prefill",
            package_path=path,
            clinician_submission=True,
        )
        session.last_question_fact = "lifestyle.alcohol_pattern"
        session.asked = ["lifestyle.alcohol_pattern"]

        session.process("현재 주 2회 소주 1병 정도 마십니다")

        self.assertEqual(session.memory.value("patient.alcohol.use_status"), "current")
        self.assertEqual(session.memory.value("patient.alcohol.beverage_types"), "soju")
        self.assertEqual(session.memory.value("patient.alcohol.frequency"), "주 2회")
        self.assertEqual(
            session.memory.value("patient.alcohol.amount_per_occasion"), "소주 1병"
        )

    def test_every_adaptive_question_exposes_free_text_guidance(self):
        session = self._session()
        choice = session._question_for_fact(
            "patient.smoking.status", "synthetic-guidance"
        )
        open_question = session._question_for_fact(
            "patient.alcohol.frequency", "synthetic-guidance"
        )

        self.assertEqual(
            choice["response_instruction_ko"],
            "번호로 답하거나, 보기에 없으면 내용을 직접 입력해 주세요. "
            "잘 모르겠거나 답변을 원하지 않는 경우 해당 항목을 선택할 수 있습니다.",
        )
        self.assertTrue(choice["allow_free_text"])
        self.assertIn("자유롭게 입력", open_question["response_instruction_ko"])
        self.assertTrue(open_question["allow_free_text"])

    def test_boolean_question_exposes_numbered_korean_shortcuts(self):
        session = self._session()
        question = session._question_for_fact("symptom.hemoptysis", "synthetic-binary")

        self.assertEqual(
            [(option["input"], option["display_ko"]) for option in question["answer_options"]],
            [("1", "예"), ("2", "아니오"), ("3", "잘 모르겠음"), ("4", "답변하지 않음")],
        )

    def test_duration_question_exposes_non_coded_runtime_shortcuts(self):
        session = self._session()
        question = session._question_for_fact("symptom.duration", "synthetic-duration")

        self.assertNotIn("answer_options", question)
        self.assertEqual(question["suggestion_semantics"], "input_shortcut_only")
        self.assertEqual(
            [(item["input"], item["display_ko"]) for item in question["display_suggestions"]],
            [("1", "오늘부터"), ("2", "3일 정도"), ("3", "1주일 정도"), ("4", "1개월 정도")],
        )
        self.assertEqual(
            [(item["input"], item["dataAbsentReason"]) for item in question["data_absent_actions"]],
            [("5", "asked-unknown"), ("6", "asked-declined")],
        )
        self.assertEqual(
            question["presentation_contract"]["intermediate_answer_commentary"],
            "prohibited",
        )

    def test_duration_shortcut_number_is_stored_as_semantic_duration(self):
        session = self._session()
        session.last_question_fact = "symptom.duration"
        session.asked = ["symptom.duration"]

        session.process("2")

        self.assertEqual(
            session.memory.value("symptom.duration"),
            {"amount": 3, "unit": "day"},
        )
        self.assertEqual(
            session.memory.facts["symptom.duration"]["raw_text"],
            "2",
        )

    def test_duration_data_absent_action_does_not_become_clinical_value(self):
        session = self._session()
        session.last_question_fact = "symptom.duration"
        session.asked = ["symptom.duration"]

        session.process("5")

        self.assertEqual(
            session.memory.facts["symptom.duration"]["status"],
            "unknown",
        )
        self.assertEqual(
            session.memory.facts["symptom.duration"]["dataAbsentReason"]["code"],
            "asked-unknown",
        )

    def test_inline_numbered_choices_are_split_into_stem_and_korean_labels(self):
        session = self._session()
        question = session._question_for_fact(
            "encounter.context_review_state", "synthetic-inline-choice"
        )

        self.assertEqual(
            question["stem_text"],
            "이 서비스에서 기본 건강정보를 처음 작성하시나요?",
        )
        self.assertEqual(
            [option["display_ko"] for option in question["answer_options"]],
            [
                "처음 작성함",
                "복용약만 90일 넘게 확인하지 않음",
                "전체 기본정보를 1년 넘게 확인하지 않음",
                "최근 확인하여 현재 정보임",
            ],
        )

    def test_natural_language_current_context_skips_baseline_history(self):
        for response in (
            "최근 확인했고 바뀐 내용이 없습니다",
            "최근 확인하여 현재 정보입니다",
        ):
            with self.subTest(response=response):
                session = self._session()
                session.last_question_fact = "encounter.context_review_state"
                session.asked = ["encounter.context_review_state"]

                state = session.process(response)

                self.assertEqual(
                    session.memory.value("encounter.context_review_state"),
                    "current",
                )
                self.assertIsNone(state["answer_clarification"])
                required = set(state["completion_status"]["required_facts"])
                package_required = set(
                    session._package_required_facts(None, session._safety())
                )
                baseline_only = {
                    fact_id
                    for fact_id in {
                        "history.condition.current",
                        "history.procedure.past",
                        "medication.current",
                        "allergy.current",
                        "history.family",
                        "occupation.current",
                        "patient.smoking.status",
                        "patient.smoking.exposure_detail",
                        "patient.alcohol.pattern",
                    }
                    if fact_id not in package_required
                }
                self.assertTrue(baseline_only)
                for fact_id in baseline_only:
                    self.assertNotIn(fact_id, required)

    def test_natural_language_context_review_options_map_to_codes(self):
        cases = {
            "처음 작성합니다": "first_encounter",
            "복용약만 90일 넘게 확인하지 않았습니다": "medication_due",
            "전체 기본정보를 1년 넘게 확인하지 않았습니다": "all_due",
            "최근 확인하여 현재 정보입니다": "current",
        }
        for response, expected in cases.items():
            with self.subTest(response=response):
                session = self._session()
                session.last_question_fact = "encounter.context_review_state"
                session.asked = ["encounter.context_review_state"]

                state = session.process(response)

                self.assertEqual(
                    session.memory.value("encounter.context_review_state"),
                    expected,
                )
                self.assertIsNone(state["answer_clarification"])

    def test_ambiguous_shared_coded_answer_clarifies_without_runtime_error(self):
        session = self._session()
        session.last_question_fact = "encounter.context_review_state"
        session.asked = ["encounter.context_review_state"]

        state = session.process("최근인 것 같기도 하고 오래된 것 같기도 합니다")

        self.assertEqual(
            state["answer_clarification"]["fact_id"],
            "encounter.context_review_state",
        )
        self.assertEqual(
            state["answer_clarification"]["value_type"],
            "coded",
        )
        self.assertNotIn(
            "binary_numeric_codes", state["answer_clarification"],
        )
        self.assertEqual(
            state["answer_clarification"]["coded_numeric_options"],
            {
                "1": "first_encounter",
                "2": "medication_due",
                "3": "all_due",
                "4": "current",
            },
        )

    def test_polite_unknown_response_is_resolved_without_repeat(self):
        session = self._session()
        session.last_question_fact = "encounter.context_review_state"
        session.asked = ["encounter.context_review_state"]

        state = session.process("잘 모르겠습니다")

        self.assertEqual(
            session.memory.state("encounter.context_review_state"),
            "unknown",
        )
        self.assertIsNone(state["answer_clarification"])
        self.assertNotEqual(
            state["selected_question"]["fact_id"],
            "encounter.context_review_state",
        )

    def test_initial_proxy_statement_preserves_age_and_additional_request(self):
        session = self._session()
        text = (
            "78세 아버지가 숨이 차고 기침도 해서 보호자가 대신 답합니다. "
            "회사 제출 서류 문의도 있습니다."
        )
        session.process(text)
        self.assertEqual(session.memory.value("patient.age_years"), 78)
        self.assertEqual(session.memory.value("interview.additional_comment"), text)

    def test_handoff_preserves_data_absent_reason_and_not_asked(self):
        session = self._session()
        session.memory.mark_absent(
            "allergy.current", "잘 모르겠어요", "asked-unknown"
        )
        handoff = session.clinician_handoff()
        self.assertIsNotNone(handoff)
        entries = {
            item["fact_id"]: item
            for section in handoff["sections"]
            for item in section["entries"]
        }
        self.assertEqual(
            entries["allergy.current"]["dataAbsentReason"]["code"],
            "asked-unknown",
        )
        self.assertEqual(entries["patient.height_cm"]["dataAbsentReason"], "not-asked")
        self.assertEqual(handoff["format"], "non_fhir_structured_summary")
        self.assertEqual(handoff["lifecycle_status"], "draft")
        self.assertEqual(handoff["review_status"], "unreviewed")
        self.assertEqual(handoff["clinical_use_status"], "limited")
        self.assertEqual(handoff["legacy_status_label"], "research_only")

    def test_required_fhir_valueset_choices_are_exposed_to_runtime(self):
        session = self._session()
        question = session._question_for_fact(
            "medication.statement.status",
            "synthetic_fhir_choice_test",
        )
        self.assertEqual(
            question["answer_value_set"],
            "http://hl7.org/fhir/ValueSet/medication-statement-status|4.0.1",
        )
        self.assertEqual(question["answer_binding_strength"], "required")
        self.assertFalse(question["allow_free_text"])
        self.assertEqual(
            [item["input"] for item in question["answer_options"]],
            [str(number) for number in range(1, 9)],
        )
        self.assertEqual(
            question["answer_options"][4]["coding"],
            {
                "system": (
                    "http://hl7.org/fhir/CodeSystem/"
                    "medication-statement-status"
                ),
                "code": "on-hold",
                "display": "On Hold",
            },
        )

    def test_required_fhir_valueset_still_rejects_unlisted_free_text(self):
        session = self._session()
        session.last_question_fact = "medication.statement.status"
        session.asked = ["medication.statement.status"]

        state = session.process("병원에서만 쓰는 별도 상태")

        self.assertIsNone(session.memory.value("medication.statement.status"))
        self.assertTrue(state["answer_clarification"]["required"])
        self.assertEqual(
            state["answer_clarification"]["fact_id"],
            "medication.statement.status",
        )

    def test_handoff_exposes_conflicts_across_package_and_shared_facts(self):
        session = self._session()
        session.memory.merge(
            "history.condition.current",
            fact("고혈압", "합성 응답 A", 1),
        )
        session.memory.merge(
            "history.condition.current",
            fact("고혈압 없음", "합성 응답 B", 2),
        )

        handoff = session.clinician_handoff()

        self.assertIn(
            "history.condition.current",
            handoff["conflicting_fact_ids"],
        )
        medical_history = next(
            section for section in handoff["sections"]
            if section["id"] == "medical_history"
        )
        entry = next(
            item for item in medical_history["entries"]
            if item["fact_id"] == "history.condition.current"
        )
        self.assertEqual(entry["status"], "conflicted")

    def test_legacy_runtime_remains_package_only_by_default(self):
        package = compile_package(profile="cough")
        temporary = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        temporary.close()
        path = Path(temporary.name)
        path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(path.unlink, missing_ok=True)
        session = InterviewSession("legacy-context-test", package_path=path)
        required = session._required_facts(None, session._safety())
        self.assertNotIn("encounter.context_review_state", required)
        self.assertIsNone(session.clinician_handoff())

    def test_autonomous_first_encounter_reaches_clinician_handoff(self):
        session = self._session()
        session.clinician_submission = False
        for fact_id in session._package_required_facts(None, session._safety()):
            session.memory.merge(fact_id, fact("synthetic-resolved", "합성 응답", 0))
        session.clinician_submission = True

        answers = {
            "encounter.context_review_state": "1",
            "encounter.information_source": "본인 진술과 복약 목록",
            "patient.age_years": "54",
            "patient.sex_for_clinical_care": "2",
            "encounter.rfe.prior_episode_and_evaluation": "처음",
            "encounter.rfe.treatment_attempt_and_response": "없음",
            "encounter.rfe.functional_impact": "잠을 조금 방해함",
            "encounter.rfe.patient_concern_and_expectation": "원인과 필요한 검사를 알고 싶음",
            "history.condition.current": "고혈압, 5년 전 진단, 치료 중",
            "history.procedure.past": "담낭 절제술, 10년 전, 합병증 없음",
            "medication.current": "암로디핀 5 mg 경구 하루 1회, 고혈압",
            "allergy.current": "없음",
            "history.family": "어머니 뇌졸중, 60대 발병",
            "occupation.current": "사무직 20년, 특이 노출 없음",
            "patient.smoking.status": "3",
            "patient.smoking.exposure_detail": "없음",
            "patient.alcohol.pattern": "주 1회 소주 1병",
            "interview.final_additional_comment": "없음",
        }
        state = session.process("의료인 제출용 문진을 계속합니다")
        selected = []
        for _ in range(session.max_turns):
            question = state["selected_question"]
            if question is None:
                break
            selected.append(question["fact_id"])
            answer = answers.get(question["fact_id"])
            if answer is None:
                answer = self._synthetic_answer(session, question["fact_id"])
            state = session.process(answer)

        self.assertTrue(state["completion_status"]["complete"])
        self.assertEqual(
            state["stop_reason"], "required_targets_addressed_with_absent_data"
        )
        self.assertEqual(len(selected), len(set(selected)))
        self.assertEqual(
            session.memory.value("patient.smoking.status"), "never"
        )
        self.assertEqual(
            state["clinician_handoff"]["reason_for_encounter"], "rfe.cough"
        )

    def test_cough_clinician_mode_adds_previously_optional_clinical_facts(self):
        session = self._session()
        required = set(session._package_required_facts(None, session._safety()))
        self.assertIn("symptom.sputum", required)
        self.assertIn("symptom.cough_nocturnal", required)
        self.assertIn("exposure.tuberculosis_risk", required)
        self.assertIn(
            "cough.prior_chest_xray_ct_spirometry_feno_and_result_source",
            required,
        )
        self.assertIn(
            "cough.information_source_witness_record_reliability_and_conflict",
            required,
        )
        self.assertIn(
            "cough.patient_goal_expectation_additional_comment_and_other_rfe",
            required,
        )
        self.assertNotIn("encounter.rfe.functional_impact", required)
        self.assertIn(
            "cough.sleep_work_school_voice_eating_activity_and_care_impact",
            required,
        )
        self.assertIn(
            "cough.smoking_vaping_cannabis_pack_years_last_use_and_change",
            required,
        )
        self.assertNotIn("encounter.rfe.patient_concern_and_expectation", required)

    def test_upper_respiratory_profile_has_previsit_handoff_and_branching(self):
        package = compile_package(profile="upper_respiratory_symptoms")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        for fact_id in {
            "upper_respiratory.information_source_and_reliability",
            "upper_respiratory.timeline_course_and_episode_pattern",
            "upper_respiratory.functional_impact_sleep_work_school_intake",
            "upper_respiratory.current_medicines_and_response",
            "upper_respiratory.patient_concern_goal_and_other_rfe",
            "upper_respiratory.conflicting_information_and_unverified_items",
        }:
            self.assertIn(fact_id, facts)
        completion = package["interview_completion_policy"]
        self.assertEqual(
            completion["conditional_required_facts"][0]["selector_fact"],
            "symptom.upper_respiratory.main_type",
        )
        self.assertLessEqual(
            len(completion["required_facts"]["always"])
            + len(completion["required_facts"]["routine"])
            + len(completion["conditional_required_facts"][0]["cases"]["sore_throat"]),
            completion["question_budget"]["routine"],
        )

    def test_skin_profile_has_detailed_clinician_handoff_and_regression_coverage(self):
        package = compile_package(profile="skin_complaint")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        minimum = package["clinician_submission_context"]
        module = json.loads(
            (Path(__file__).resolve().parents[1] / minimum["resource_ref"])
            .read_text(encoding="utf-8")
        )
        required = set(
            module["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.skin_complaint"]
        )
        rules = {item["id"] for item in package["rule_graph"]["rules"]}

        self.assertGreaterEqual(len(facts), 70)
        self.assertGreaterEqual(package["coverage"]["simulation_count"], 27)
        self.assertIn(
            "skin.count_dimensions_shape_border_colour_surface_and_measurement",
            required,
        )
        self.assertIn(
            "skin.suspected_medicine_product_strength_route_indication_start_last_dose_and_interval",
            required,
        )
        self.assertIn("pain.nrs_score", required)
        self.assertIn("rule.skin.safety.blistering-new-medicine", rules)
        self.assertIn("rule.skin.safety.near-eye-hot-swollen", rules)
        self.assertIn("hair.loss_pattern", facts)
        self.assertIn("hair.scalp_smooth_shiny_change", facts)
        self.assertIn("rule.skin.safety.hot-painful-swollen", rules)

    def test_weight_constitutional_profile_has_professional_handoff_and_regressions(self):
        package = compile_package(profile="weight_constitutional_change")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        minimum = package["clinician_submission_context"]
        module = json.loads(
            (Path(__file__).resolve().parents[1] / minimum["resource_ref"])
            .read_text(encoding="utf-8")
        )
        required = set(
            module["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.weight_constitutional_change"]
        )
        rules = {item["id"] for item in package["rule_graph"]["rules"]}

        self.assertGreaterEqual(len(facts), 78)
        self.assertGreaterEqual(package["coverage"]["simulation_count"], 32)
        self.assertIn(
            "weight.usual_current_low_high_date_scale_clothing_and_source",
            required,
        )
        self.assertIn(
            "constitutional.restriction_binge_vomit_laxative_diuretic_exercise_and_water_loading",
            required,
        )
        self.assertIn("pain.nrs_score", required)
        self.assertIn(
            "rule.weight-constitutional-change.safety.current-self-harm-danger",
            rules,
        )
        self.assertIn(
            "rule.weight-constitutional-change.safety.unintentional-loss-mass",
            rules,
        )

    def test_joint_limb_profile_has_professional_handoff_and_regressions(self):
        package = compile_package(profile="joint_limb_complaint")
        facts = {
            node["id"] for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        minimum = package["clinician_submission_context"]
        module = json.loads(
            (Path(__file__).resolve().parents[1] / minimum["resource_ref"])
            .read_text(encoding="utf-8")
        )
        required = set(
            module["completion"]["clinician_rfe_minimum"]
            ["additional_required_facts_by_rfe"]["rfe.joint_limb_complaint"]
        )
        rules = {item["id"] for item in package["rule_graph"]["rules"]}

        self.assertGreaterEqual(len(facts), 83)
        self.assertGreaterEqual(package["coverage"]["simulation_count"], 28)
        self.assertIn(
            "joint_limb.exact_structure_site_side_surface_depth_and_distribution",
            required,
        )
        self.assertIn(
            "joint_limb.prior_exam_clinical_test_laboratory_and_imaging_date_result_source_pending",
            required,
        )
        self.assertIn("pain.nrs_score", required)
        self.assertIn(
            "rule.joint-limb.safety.unilateral-leg-chest-pain", rules,
        )
        self.assertIn(
            "rule.joint-limb.safety.unilateral-leg-severe-dyspnea", rules,
        )

    def test_autonomous_clinician_minimum_completes_all_packages(self):
        for profile in PACKAGE_PROFILES:
            with self.subTest(profile=profile):
                package = compile_package(profile=profile)
                temporary = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
                temporary.close()
                path = Path(temporary.name)
                path.write_text(
                    json.dumps(package, ensure_ascii=False), encoding="utf-8"
                )
                try:
                    session = InterviewSession(
                        f"clinician-autonomous-{profile}",
                        package_path=path,
                        clinician_submission=True,
                    )
                    session.clinician_submission = False
                    for fact_id in session._package_required_facts(
                        None, session._safety()
                    ):
                        session.memory.merge(
                            fact_id, fact("synthetic-resolved", "합성 응답", 0)
                        )
                    session.clinician_submission = True
                    state = session.process("의료인 제출 문진을 계속합니다")
                    selected = []
                    for _ in range(session.max_turns):
                        question = state["selected_question"]
                        if question is None:
                            break
                        selected.append(question["fact_id"])
                        state = session.process(
                            self._synthetic_answer(session, question["fact_id"])
                        )
                    self.assertTrue(
                        state["completion_status"]["complete"],
                        state["completion_status"]["missing_facts"],
                    )
                    self.assertEqual(len(selected), len(set(selected)))
                    handoff = state["clinician_handoff"]
                    self.assertIsNotNone(handoff)
                    clinical_section = handoff["sections"][0]
                    self.assertEqual(
                        clinical_section["id"],
                        "reason_for_encounter_clinical_facts",
                    )
                    self.assertTrue(clinical_section["entries"])
                    self.assertFalse(
                        clinical_section["summary"]["missing_required_fact_ids"]
                    )
                    for entry in clinical_section["entries"]:
                        self.assertIn("status", entry)
                        self.assertIn("dataAbsentReason", entry)
                        self.assertIn("safety_relevant", entry)
                finally:
                    path.unlink(missing_ok=True)

    def test_incomplete_previsit_handoff_exposes_missing_symptom_facts(self):
        session = self._session()
        handoff = session.clinician_handoff()
        clinical_section = handoff["sections"][0]
        missing = set(clinical_section["summary"]["missing_required_fact_ids"])
        self.assertIn("symptom.sputum", missing)
        self.assertIn("symptom.duration", missing)
        self.assertTrue(any(
            entry["safety_relevant"] for entry in clinical_section["entries"]
        ))


if __name__ == "__main__":
    unittest.main()
