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
        self.assertIn("patient.alcohol.pattern", state["completion_status"]["required_facts"])

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
        for _ in range(60):
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
        self.assertIn("encounter.rfe.functional_impact", required)
        self.assertIn("encounter.rfe.patient_concern_and_expectation", required)

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
