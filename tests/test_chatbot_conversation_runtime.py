from pathlib import Path
import json
import unittest

from runtime.chatbot_session import ChatbotInterviewSession
from runtime.core import CoreInteractionSession
from runtime.service_modes import ServiceModeRegistry
from services.interview_api.llm import (
    LlmChatbotInterviewRuntime,
    LlmChatbotRuntimeError,
    LlmProvider,
    LlmSelection,
    _resolve_last_numbered_answer,
)


ROOT = Path(__file__).resolve().parents[1]


class ChatbotConversationRuntimeTest(unittest.TestCase):
    def test_numbered_answer_label_is_resolved_for_action_retrieval_only(self):
        self.assertEqual(
            _resolve_last_numbered_answer([
                {"role": "user", "content": "왼쪽 발목 통증"},
                {
                    "role": "assistant",
                    "content": "Q1. 다친 뒤 시작했나요?\n\n1 예\n2 아니오\n3 잘 모르겠음",
                },
                {"role": "user", "content": "2"},
            ]),
            {"input": "2", "display": "아니오"},
        )

    def test_chatbot_session_preserves_opening_semantics_and_visible_turn(self):
        calls = []

        def turn(rfe_id, conversation):
            calls.append((rfe_id, conversation))
            return (
                "왼쪽 발목 통증으로 문진을 진행하겠습니다.\n\n"
                "**Q1.** 왼쪽 발목 통증은 넘어짐, 충돌, 비틀림 또는 직접 충격 뒤 시작했나요?\n\n"
                "1 예\n2 아니오\n3 잘 모르겠음\n4 답변하지 않음\n\n"
                "번호로 답하거나, 보기에 없으면 내용을 직접 입력해 주세요.\n\n"
                "출처: [공동 작업 지식] package.primary-care-joint-limb"
            )

        session = ChatbotInterviewSession(
            "session-1", "rfe.joint_limb_complaint", turn
        )
        state = session.process("왼쪽 발목 통증")

        self.assertEqual(calls[0][1], [{"role": "user", "content": "왼쪽 발목 통증"}])
        self.assertEqual(state["runtime"], "custom_gpt_conversation")
        self.assertFalse(state["interview_flow"]["legacy_deterministic_fallback"])
        self.assertEqual(state["selected_question"]["question_ref"], "Q1")
        self.assertIn("넘어짐", state["selected_question"]["text"])
        self.assertEqual(
            [item["display_ko"] for item in state["selected_question"]["answer_options"]],
            ["예", "아니오", "잘 모르겠음", "답변하지 않음"],
        )

    def test_core_uses_conversation_runtime_not_legacy_interview_session(self):
        core = CoreInteractionSession("core-chatbot")
        core.chatbot_turn = lambda rfe_id, conversation: (
            "**Q1.** 관절 통증은 다친 뒤 시작했나요?\n\n"
            "1 예\n2 아니오\n3 잘 모르겠음\n4 답변하지 않음"
        )
        core.select_mode("문진 시작 (예: 기침이 나요)")
        state = core.process("관절 통증")

        self.assertEqual(state["adapter_state"]["runtime"], "custom_gpt_conversation")
        self.assertEqual(state["adapter_state"]["selected_question"]["question_ref"], "Q1")
        self.assertFalse(state["adapter_state"]["interview_flow"]["legacy_deterministic_fallback"])

    def test_ankle_pain_does_not_substring_route_to_neck(self):
        matched = ServiceModeRegistry().match_reason_for_encounter("왼쪽 발목 통증")
        self.assertIsNotNone(matched)
        self.assertEqual(matched["id"], "rfe.joint_limb_complaint")

    def test_llm_runtime_sends_repository_gpt_instructions_verbatim(self):
        captured = {"retrieval": [], "generation": []}

        def retrieval_transport(provider, messages, timeout):
            captured["retrieval"].append(messages)
            return (
                '{"question_ids":["question.joint-limb.recent-injury"],'
                '"fact_ids":["event.joint_limb.recent_injury"],'
                '"priority_rule_ids":["rule.joint-limb.safety.cannot-use",'
                '"rule.generated.priority.any.recent-injury"]}'
            )

        def generation_transport(provider, messages, timeout):
            captured["generation"].append(messages)
            return "**Q1.** 다친 뒤 시작했나요?\n\n1 예\n2 아니오"

        runtime = LlmChatbotInterviewRuntime(
            transport=generation_transport,
            retrieval_transport=retrieval_transport,
            repository_root=ROOT,
        )
        provider = LlmProvider(
            provider_id="local_vllm",
            display_name="Local",
            adapter="openai_compatible_chat",
            base_url="http://127.0.0.1:8000/v1",
            model="qwen3-27b",
            external_processing=False,
        )
        selection = LlmSelection(
            provider=provider,
            selected_by="platform_default",
            external_processing_consent=False,
            allowed_provider_ids=("local_vllm",),
            participant_may_choose=False,
        )

        runtime.respond(
            "rfe.joint_limb_complaint",
            [{"role": "user", "content": "왼쪽 발목 통증"}],
            selection,
        )

        messages = captured["generation"][0]
        self.assertEqual(
            messages[0]["content"],
            (ROOT / "docs/gpt/GPT_INSTRUCTIONS.md").read_text(encoding="utf-8"),
        )
        self.assertIn("selected_rules", messages[1]["content"])
        self.assertIn(
            '"id":"question.joint-limb.recent-injury"',
            messages[1]["content"],
        )
        self.assertIn(
            '"id":"event.joint_limb.recent_injury"',
            messages[1]["content"],
        )
        self.assertIn(
            "Do not ask the core-purpose question",
            messages[1]["content"],
        )
        self.assertEqual(
            messages[-1],
            {"role": "user", "content": "왼쪽 발목 통증"},
        )
        retrieval_request = json.loads(captured["retrieval"][0][-1]["content"])
        self.assertIn("package_index", retrieval_request)
        self.assertNotIn(
            (ROOT / "docs/gpt/GPT_INSTRUCTIONS.md").read_text(encoding="utf-8")[:100],
            captured["retrieval"][0][0]["content"],
        )

    def test_llm_runtime_has_no_question_fallback_when_retrieval_is_invalid(self):
        runtime = LlmChatbotInterviewRuntime(
            transport=lambda *_args: "**Q1.** 이 응답은 호출되면 안 됩니다.",
            retrieval_transport=lambda *_args: '{"question_ids":["invented"]}',
            repository_root=ROOT,
        )
        provider = LlmProvider(
            provider_id="local_vllm",
            display_name="Local",
            adapter="openai_compatible_chat",
            base_url="http://127.0.0.1:8000/v1",
            model="qwen3-27b",
            external_processing=False,
        )
        selection = LlmSelection(
            provider=provider,
            selected_by="platform_default",
            external_processing_consent=False,
            allowed_provider_ids=("local_vllm",),
            participant_may_choose=False,
        )
        with self.assertRaises(LlmChatbotRuntimeError):
            runtime.respond(
                "rfe.joint_limb_complaint",
                [{"role": "user", "content": "왼쪽 발목 통증"}],
                selection,
            )


if __name__ == "__main__":
    unittest.main()
