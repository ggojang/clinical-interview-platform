import json
import tempfile
import unittest
from pathlib import Path

from compiler.build_package import compile_package
from runtime.session import InterviewSession, fact


class PainAssessmentTest(unittest.TestCase):
    def _session(self, profile: str = "abdominal_pain") -> InterviewSession:
        package = compile_package(profile=profile)
        temporary = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        temporary.close()
        path = Path(temporary.name)
        path.write_text(json.dumps(package, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(path.unlink, missing_ok=True)
        return InterviewSession("pain-assessment-test", package_path=path)

    def test_primary_pain_profile_requires_frequency_and_known_nrs(self):
        package = compile_package(profile="abdominal_pain")
        facts = {
            node["id"]: node for node in package["knowledge_graph"]["nodes"]
            if node["type"] == "Fact"
        }
        self.assertEqual(facts["pain.nrs_score"]["minimum"], 0)
        self.assertEqual(facts["pain.nrs_score"]["maximum"], 10)
        self.assertEqual(facts["pain.nrs_score"]["scale"]["type"], "NRS")
        policy = package["interview_completion_policy"]
        self.assertIn("pain.frequency", policy["required_facts"]["always"])
        self.assertIn("pain.nrs_score", policy["required_facts"]["always"])
        self.assertIn("pain.frequency", policy["must_be_known_facts"])
        self.assertIn("pain.nrs_score", policy["must_be_known_facts"])

        questions = package["indexes"]["questions_by_fact"]
        for fact_id in ("pain.frequency", "pain.nrs_score"):
            wording = questions[fact_id]["wording"]
            self.assertIn("[필수]", wording)
            self.assertNotIn("잘 모르겠음", wording)
            self.assertNotIn("답변하지 않음", wording)

    def test_conditional_profile_activates_only_after_pain_is_present(self):
        session = self._session("skin_complaint")
        before = set(session._required_facts(None, session._safety()))
        self.assertNotIn("pain.nrs_score", before)
        session.memory.merge(
            "symptom.skin_complaint.pain", fact("moderate", "중등도", 1)
        )
        after = set(session._required_facts(None, session._safety()))
        self.assertIn("pain.frequency", after)
        self.assertIn("pain.nrs_score", after)

    def test_nrs_rejects_out_of_range_and_requests_reconfirmation(self):
        session = self._session()
        session.last_question_fact = "pain.nrs_score"
        state = session.process("11")
        self.assertIsNone(session.memory.value("pain.nrs_score"))
        self.assertEqual(
            state["answer_clarification"]["reason"],
            "possible_typo_invalid_option_or_ambiguous_meaning",
        )
        self.assertEqual(state["selected_question"]["fact_id"], "pain.nrs_score")

    def test_unknown_mandatory_nrs_is_reasked_with_required_notice(self):
        session = self._session()
        session.last_question_fact = "pain.nrs_score"
        state = session.process("잘 모르겠어요")
        self.assertEqual(
            state["answer_clarification"]["reason"],
            "mandatory_answer_required",
        )
        self.assertTrue(
            state["answer_clarification"]["completion_blocked_until_known"]
        )
        self.assertFalse(
            state["answer_clarification"]["unknown_or_declined_options_offered"]
        )
        self.assertEqual(state["selected_question"]["fact_id"], "pain.nrs_score")
        self.assertIn("[필수]", state["selected_question"]["text"])

        second = session.process("답하고 싶지 않아요")
        self.assertIsNone(second["answer_clarification"])
        self.assertNotEqual(
            second.get("selected_question", {}).get("fact_id")
            if second.get("selected_question") else None,
            "pain.nrs_score",
        )

    def test_data_absent_reason_is_preserved_but_does_not_complete_nrs(self):
        session = self._session()
        required = session._required_facts(None, session._safety())
        for fact_id in required:
            session.memory.merge(fact_id, fact(0, "합성 응답", 0))
        session.memory.mark_absent(
            "pain.nrs_score", "잘 모르겠어요", "asked-unknown", correction=True
        )
        completion = session._completion(None, session._safety())
        self.assertFalse(completion["complete"])
        self.assertIn("pain.nrs_score", completion["required_known_missing_facts"])
        self.assertEqual(
            session.memory.facts["pain.nrs_score"]["dataAbsentReason"]["code"],
            "asked-unknown",
        )

    def test_existing_zero_to_ten_fact_is_bound_as_nrs(self):
        package = compile_package(profile="oral_dental_symptoms")
        fact_node = next(
            node for node in package["knowledge_graph"]["nodes"]
            if node["id"] == "oral.pain_score_zero_to_ten"
        )
        self.assertEqual(fact_node["scale"]["type"], "NRS")
        self.assertEqual((fact_node["minimum"], fact_node["maximum"]), (0, 10))
        self.assertIn(
            "oral.pain_score_zero_to_ten",
            package["interview_completion_policy"]["must_be_known_facts"],
        )


if __name__ == "__main__":
    unittest.main()
