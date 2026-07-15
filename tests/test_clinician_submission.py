import json
import tempfile
import unittest
from pathlib import Path

from compiler.build_package import PACKAGE_PROFILES, compile_package
from runtime.session import InterviewSession, fact


class ClinicianSubmissionContextTest(unittest.TestCase):
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
                self.assertNotIn(
                    "encounter.context_review_state",
                    package["indexes"]["questions_by_fact"],
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
        for fact_id in session._package_required_facts(None, session._safety()):
            session.memory.merge(fact_id, fact("synthetic-resolved", "합성 응답", 0))

        answers = {
            "encounter.context_review_state": "1",
            "encounter.information_source": "본인 진술과 복약 목록",
            "patient.age_years": "54",
            "patient.sex_for_clinical_care": "2",
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
        for _ in range(20):
            question = state["selected_question"]
            if question is None:
                break
            selected.append(question["fact_id"])
            state = session.process(answers[question["fact_id"]])

        self.assertTrue(state["completion_status"]["complete"])
        self.assertEqual(state["stop_reason"], "all_required_targets_resolved")
        self.assertEqual(len(selected), len(set(selected)))
        self.assertEqual(
            session.memory.value("patient.smoking.status"), "never"
        )
        self.assertEqual(
            state["clinician_handoff"]["reason_for_encounter"], "rfe.cough"
        )


if __name__ == "__main__":
    unittest.main()
