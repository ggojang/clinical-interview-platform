from __future__ import annotations

import json
import unittest

from runtime.core import CoreInteractionSession
from services.interview_api.llm import (
    LlmAdaptiveAnswerInterpreter,
    LlmProvider,
    LlmSelection,
)


def _clinical_session(session_id: str, **kwargs) -> CoreInteractionSession:
    session = CoreInteractionSession(session_id, **kwargs)
    session.select_mode("문진 시작")
    return session


class ChatbotTestRuntimeTests(unittest.TestCase):
    def test_headache_starts_with_concise_question_and_examples(self):
        state = _clinical_session("chatbot-headache").process("두통")["adapter_state"]
        question = state["selected_question"]

        self.assertEqual(question["fact_id"], "symptom.headache.location")
        self.assertEqual(question["stem_text"], "머리에서 가장 아픈 곳은 어디인가요?")
        self.assertEqual(
            [item["display_ko"] for item in question["display_suggestions"]],
            ["이마·눈 주위", "관자놀이", "정수리", "뒤통수·목 위쪽"],
        )
        self.assertEqual(
            question["presentation_contract"]["interaction_style"], "chatbot_test"
        )
        self.assertFalse(
            question["presentation_contract"]["compiled_authoring_question_exposed"]
        )

    def test_neck_pain_never_exposes_long_authoring_stem_and_stops_at_soft_budget(self):
        session = _clinical_session("chatbot-neck")
        state = session.process("목통증")["adapter_state"]
        self.assertEqual(state["active_patterns"], ["encounter.neck_pain"])
        shown = []
        for _ in range(24):
            question = state.get("selected_question")
            if question is None:
                break
            stem = question.get("stem_text")
            self.assertIsInstance(stem, str)
            self.assertLessEqual(len(stem), 80)
            shown.append(question)
            options = question.get("answer_options") or question.get(
                "display_suggestions"
            )
            if options:
                answer = str(options[0]["input"])
            elif "0~10" in stem:
                answer = "4"
            else:
                answer = "없음"
            state = session.process(answer)["adapter_state"]

        self.assertEqual(len(shown), 18)
        self.assertEqual(state["stop_reason"], "question_budget_reached")
        self.assertEqual(shown[0]["stem_text"], "목에서 가장 아픈 곳은 어디인가요?")
        self.assertTrue(any("가장 확인하고 싶은 점" in item["stem_text"] for item in shown))

    def test_one_answer_can_satisfy_multiple_allowlisted_facts(self):
        observed = {}

        def interpret(context, message, candidates):
            observed["context"] = context
            observed["message"] = message
            observed["candidate_ids"] = {item["fact_id"] for item in candidates}
            return {
                "neck.onset_date_time": {"value": "어제", "confidence": 0.91},
                "neck.onset_mode": {"value": "sudden", "confidence": 0.90},
            }

        session = _clinical_session(
            "chatbot-multifact", answer_interpreter=interpret
        )
        session.process("목통증")
        state = session.process("왼쪽 목덜미이고 어제 갑자기 시작했어요")
        adapter = state["adapter_state"]

        self.assertEqual(observed["context"]["expected_fact_id"], "neck.exact_site_laterality_and_extent")
        self.assertIn("neck.onset_date_time", observed["candidate_ids"])
        self.assertEqual(adapter["facts"]["neck.onset_date_time"]["value"], "어제")
        self.assertEqual(adapter["facts"]["neck.onset_mode"]["value"], "sudden")
        self.assertNotIn(
            adapter["selected_question"]["fact_id"],
            {"neck.onset_date_time", "neck.onset_mode"},
        )


class AdaptiveAnswerInterpreterTests(unittest.TestCase):
    def test_interpreter_accepts_only_valid_allowlisted_values(self):
        def transport(_provider, _messages, _timeout):
            return json.dumps(
                {
                    "fact_updates": [
                        {"fact_id": "neck.onset_mode", "value": "sudden", "confidence": 0.9},
                        {"fact_id": "neck.current_pain_nrs", "value": 99, "confidence": 0.99},
                        {"fact_id": "invented.fact", "value": True, "confidence": 0.99},
                    ]
                }
            )

        adapter = LlmAdaptiveAnswerInterpreter(enabled=True, transport=transport)
        provider = LlmProvider(
            provider_id="local_vllm",
            display_name="Local",
            adapter="openai_compatible_chat",
            base_url="http://127.0.0.1:8000/v1",
            model="test",
            external_processing=False,
        )
        selection = LlmSelection(provider, "platform_default", False, ("local_vllm",), True)
        result = adapter.interpret(
            {"expected_fact_id": "neck.onset_mode"},
            "어제 갑자기 시작했고 통증은 7점이에요",
            [
                {
                    "fact_id": "neck.onset_mode",
                    "value_type": "coded",
                    "allowed_values": ["sudden", "gradual", "unclear"],
                },
                {
                    "fact_id": "neck.current_pain_nrs",
                    "value_type": "integer",
                    "minimum": 0,
                    "maximum": 10,
                },
            ],
            selection,
        )

        self.assertEqual(set(result), {"neck.onset_mode"})
        self.assertEqual(result["neck.onset_mode"]["value"], "sudden")


if __name__ == "__main__":
    unittest.main()
