from __future__ import annotations

import json
import unittest

from runtime.core import CoreInteractionSession
from services.interview_api.llm import (
    LlmAdaptiveAnswerInterpreter,
    LlmProvider,
    LlmSelection,
)


def _clinical_session(
    session_id: str,
    chatbot_turn,
) -> CoreInteractionSession:
    session = CoreInteractionSession(session_id, chatbot_turn=chatbot_turn)
    session.select_mode("문진 시작")
    return session


class ChatbotTestRuntimeTests(unittest.TestCase):
    def test_headache_starts_with_concise_question_and_examples(self):
        observed = {}

        def turn(rfe_id, conversation):
            observed["rfe_id"] = rfe_id
            observed["conversation"] = conversation
            return (
                "Q1. 머리에서 가장 아픈 곳은 어디인가요?\n\n"
                "예: 이마·눈 주위, 관자놀이, 정수리, 뒤통수·목 위쪽\n\n"
                "내용을 자유롭게 입력해 주세요."
            )

        state = _clinical_session("chatbot-headache", turn).process("두통")[
            "adapter_state"
        ]
        question = state["selected_question"]

        self.assertEqual(observed["rfe_id"], "rfe.headache")
        self.assertEqual(observed["conversation"], [{"role": "user", "content": "두통"}])
        self.assertEqual(question["stem_text"], "머리에서 가장 아픈 곳은 어디인가요?")
        self.assertEqual(state["runtime"], "custom_gpt_conversation")
        self.assertFalse(state["interview_flow"]["legacy_deterministic_fallback"])

    def test_neck_pain_keeps_full_conversation_for_llm_semantic_coverage(self):
        calls = []

        def turn(rfe_id, conversation):
            calls.append((rfe_id, conversation))
            number = len([item for item in conversation if item["role"] == "user"])
            return f"Q{number}. 목 통증은 언제 시작했나요?"

        session = _clinical_session("chatbot-neck", turn)
        state = session.process("목통증")["adapter_state"]
        state = session.process("왼쪽 목덜미이고 어제 갑자기 시작했어요")
        self.assertEqual(state["adapter_state"]["selected_question"]["question_ref"], "Q2")
        self.assertEqual(calls[-1][0], "rfe.neck_pain")
        self.assertEqual(
            calls[-1][1][-1],
            {"role": "user", "content": "왼쪽 목덜미이고 어제 갑자기 시작했어요"},
        )

    def test_missing_conversation_llm_fails_instead_of_using_legacy_runtime(self):
        session = CoreInteractionSession("chatbot-no-fallback")
        session.select_mode("문진 시작")
        with self.assertRaisesRegex(RuntimeError, "conversation-native"):
            session.process("목통증")


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
