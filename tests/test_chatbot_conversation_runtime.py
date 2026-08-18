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
    _adapt_chatbot_channel_notice,
    _ensure_question_provenance,
    _question_answer_states,
    _question_id_key,
    _response_has_unsupported_question_id,
    _resolve_last_numbered_answer,
)


ROOT = Path(__file__).resolve().parents[1]


class ChatbotConversationRuntimeTest(unittest.TestCase):
    def test_ciai_channel_replaces_chatgpt_plan_notice(self):
        adapted = _adapt_chatbot_channel_notice(
            "익명 테스트 안내입니다.\n\n"
            "테스트 안내: ChatGPT 무료 플랜에서는 GPT 사용량 또는 "
            "파일·이미지 업로드 한도가 있습니다.\n\n"
            "Q1. 언제 시작했나요?"
        )
        self.assertNotIn("ChatGPT", adapted)
        self.assertIn("CIAI 데모", adapted)
        self.assertIn("Q1. 언제 시작했나요?", adapted)

    def test_ciai_channel_removes_literal_backticks_from_binary_answer_lines(self):
        adapted = _adapt_chatbot_channel_notice(
            "Q1. 숨이 차나요?\n\n`응답`\n\n`1 예`\n\n`2 아니오`\n\n"
            "`3 잘 모르겠음`\n\n`4 답변하지 않음`"
        )
        self.assertNotIn("`응답`", adapted)
        self.assertNotIn("`1 예`", adapted)
        self.assertIn("\n응답\n", adapted)
        self.assertIn("\n1 예\n", adapted)

    def test_retrieval_index_links_facts_and_priority_without_duplicate_catalogs(self):
        runtime = LlmChatbotInterviewRuntime(enabled=False, repository_root=ROOT)
        index = runtime._load_package("rfe.joint_limb_complaint")["index"]
        self.assertNotIn("facts", index)
        self.assertNotIn("priority_rules", index)
        recent_injury = next(
            item
            for item in index["questions"]
            if item["id"] == "question.joint-limb.recent-injury"
        )
        self.assertEqual(recent_injury["fact_id"], "event.joint_limb.recent_injury")
        self.assertIn(
            "rule.generated.priority.any.recent-injury",
            recent_injury["priority_rule_ids"],
        )

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

    def test_llm_runtime_uses_compiled_runtime_instructions_and_exact_objects(self):
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
            knowledge_delivery="action_two_stage_exact_objects",
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
            (ROOT / "docs/gpt/CLINICAL_ADAPTIVE_RUNTIME_INSTRUCTIONS.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertLess(
            len(messages[0]["content"]),
            len((ROOT / "docs/gpt/GPT_INSTRUCTIONS.md").read_text(encoding="utf-8")),
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

    def test_llm_runtime_keeps_explicit_verbatim_editor_regression_profile(self):
        captured = []
        runtime = LlmChatbotInterviewRuntime(
            transport=lambda _provider, messages, _timeout: captured.append(messages)
            or "Q1. 다친 뒤 시작했나요?",
            retrieval_transport=lambda *_args: (
                '{"question_ids":["question.joint-limb.recent-injury"],'
                '"fact_ids":["event.joint_limb.recent_injury"],'
                '"priority_rule_ids":[]}'
            ),
            instruction_profile="verbatim_gpt_editor",
            repository_root=ROOT,
        )
        provider = LlmProvider(
            provider_id="local_vllm", display_name="Local",
            adapter="openai_compatible_chat", base_url="http://127.0.0.1:8000/v1",
            model="qwen3-27b", external_processing=False,
        )
        selection = LlmSelection(
            provider=provider, selected_by="platform_default",
            external_processing_consent=False, allowed_provider_ids=("local_vllm",),
            participant_may_choose=False,
        )
        runtime.respond(
            "rfe.joint_limb_complaint",
            [{"role": "user", "content": "왼쪽 발목 통증"}],
            selection,
        )
        self.assertEqual(
            captured[0][0]["content"],
            (ROOT / "docs/gpt/GPT_INSTRUCTIONS.md").read_text(encoding="utf-8"),
        )

    def test_llm_runtime_has_no_question_fallback_when_retrieval_is_invalid(self):
        runtime = LlmChatbotInterviewRuntime(
            transport=lambda *_args: "**Q1.** 이 응답은 호출되면 안 됩니다.",
            retrieval_transport=lambda *_args: '{"question_ids":["invented"]}',
            knowledge_delivery="action_two_stage_exact_objects",
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

    def test_compiled_candidate_window_skips_second_llm_and_already_shown_question(self):
        captured = []
        runtime = LlmChatbotInterviewRuntime(
            transport=lambda _provider, messages, _timeout: captured.append(messages)
            or "Q1. 다친 뒤 시작했나요?",
            retrieval_transport=lambda *_args: self.fail("retrieval LLM must not run"),
            knowledge_delivery="compiled_candidate_window",
            repository_root=ROOT,
        )
        provider = LlmProvider(
            provider_id="local_vllm", display_name="Local",
            adapter="openai_compatible_chat", base_url="http://127.0.0.1:8000/v1",
            model="qwen3-27b", external_processing=False,
        )
        selection = LlmSelection(
            provider=provider, selected_by="platform_default",
            external_processing_consent=False, allowed_provider_ids=("local_vllm",),
            participant_may_choose=False,
        )
        runtime.respond(
            "rfe.joint_limb_complaint",
            [{"role": "user", "content": "왼쪽 발목 통증"}],
            selection,
        )
        self.assertIn('"question.joint-limb.recent-injury"', captured[0][1]["content"])
        self.assertNotIn('"question.joint-limb.primary-context"', captured[0][1]["content"])

        runtime.respond(
            "rfe.joint_limb_complaint",
            [
                {"role": "user", "content": "왼쪽 발목 통증"},
                {"role": "assistant", "content": "Q1. 다친 뒤 시작했나요?\n출처: question.joint-limb.recent-injury"},
                {"role": "user", "content": "2 아니오"},
            ],
            selection,
        )
        manifest = captured[1][1]["content"].split("<action_retrieval_manifest>", 1)[1].split("</action_retrieval_manifest>", 1)[0]
        self.assertNotIn("question.joint-limb.recent-injury", manifest)

    def test_compiled_candidate_window_uses_single_exact_question(self):
        runtime = LlmChatbotInterviewRuntime(
            enabled=False,
            knowledge_delivery="compiled_candidate_window",
            repository_root=ROOT,
        )
        package = runtime._load_package("rfe.cough")
        retrieval = runtime._compiled_candidate_retrieval(
            "rfe.cough", [{"role": "user", "content": "기침"}], package
        )
        self.assertEqual(retrieval["question_ids"], ["question.symptom_onset"])
        self.assertNotIn("question.cough.frequency-bouts", retrieval["question_ids"])

    def test_cough_sudden_onset_positive_prioritizes_swallowing_context(self):
        runtime = LlmChatbotInterviewRuntime(
            enabled=False,
            knowledge_delivery="compiled_candidate_window",
            repository_root=ROOT,
        )
        package = runtime._load_package("rfe.cough")
        conversation = [
            {"role": "user", "content": "기침"},
            {
                "role": "assistant",
                "content": (
                    "Q1. 언제 시작했나요?\n"
                    "출처: question.symptom_onset"
                ),
            },
            {"role": "user", "content": "어제"},
            {
                "role": "assistant",
                "content": (
                    "Q2. 매우 갑자기 시작했나요?\n\n"
                    "1 예\n2 아니오\n3 잘 모르겠음\n4 답변하지 않음\n\n"
                    "출처: question.symptom_cough_sudden_onset"
                ),
            },
            {"role": "user", "content": "1"},
        ]
        retrieval = runtime._compiled_candidate_retrieval(
            "rfe.cough", conversation, package
        )
        self.assertEqual(
            retrieval["question_ids"], ["question.cough.swallowing-context"]
        )

    def test_negative_cough_gate_suppresses_conditional_detail(self):
        runtime = LlmChatbotInterviewRuntime(enabled=False, repository_root=ROOT)
        package = runtime._load_package("rfe.cough")
        conversation = [
            {"role": "user", "content": "기침"},
            {
                "role": "assistant",
                "content": (
                    "Q3. 숨이 차나요?\n\n1 예\n2 아니오\n"
                    "출처: question.symptom_dyspnea"
                ),
            },
            {"role": "user", "content": "2"},
        ]
        states = _question_answer_states(conversation, package)
        self.assertEqual(
            states[_question_id_key("question.symptom_dyspnea")], "negative"
        )
        retrieval = runtime._compiled_candidate_retrieval(
            "rfe.cough", conversation, package
        )
        self.assertNotEqual(
            retrieval["question_ids"], ["question.cough.dyspnea-detail"]
        )

    def test_invalid_generated_question_id_is_retried_and_canonicalized(self):
        responses = iter([
            (
                "Q1. 웃다가 기침이 시작됐나요?\n\n1 예\n2 아니오\n\n"
                "출처: [공동 작업 지식] question.cough.invented-trigger"
            ),
            (
                "Q1. 기침은 언제 처음 시작되었나요?\n\n"
                "시작 시점을 입력해 주세요.\n\n"
                "출처: [공동 작업 지식] question.symptom_onset · [AI 표현] 문장"
            ),
        ])
        captured = []

        def generation_transport(_provider, messages, _timeout):
            captured.append(messages)
            return next(responses)

        runtime = LlmChatbotInterviewRuntime(
            transport=generation_transport,
            retrieval_transport=lambda *_args: self.fail("retrieval LLM must not run"),
            knowledge_delivery="compiled_candidate_window",
            repository_root=ROOT,
        )
        provider = LlmProvider(
            provider_id="local_vllm", display_name="Local",
            adapter="openai_compatible_chat", base_url="http://127.0.0.1:8000/v1",
            model="qwen3-27b", external_processing=False,
        )
        selection = LlmSelection(
            provider=provider, selected_by="platform_default",
            external_processing_consent=False, allowed_provider_ids=("local_vllm",),
            participant_may_choose=False,
        )
        response = runtime.respond(
            "rfe.cough", [{"role": "user", "content": "기침"}], selection
        )
        self.assertEqual(len(captured), 2)
        self.assertIn("question.symptom_onset", response)
        self.assertNotIn("invented-trigger", response)
        self.assertIn("outside the Action retrieval manifest", captured[1][-1]["content"])

    def test_equivalent_question_namespace_alias_is_canonicalized_without_retry(self):
        response = (
            "Q4. 기침은 한 번 시작하면 얼마나 지속되나요?\n\n"
            "출처: [공동 작업 지식] question.cough.duration · [AI 표현] 문장"
        )
        allowed = ["question.symptom_duration"]
        self.assertFalse(_response_has_unsupported_question_id(response, allowed))
        canonical = _ensure_question_provenance(response, allowed[0])
        self.assertIn("question.symptom_duration", canonical)
        self.assertNotIn("question.cough.duration", canonical)

    def test_added_semantic_token_is_not_accepted_as_question_alias(self):
        response = (
            "Q15. 웃다가 기침이 시작되나요?\n\n"
            "출처: question.cough.paroxysmal_trigger"
        )
        self.assertTrue(
            _response_has_unsupported_question_id(
                response, ["question.symptom_cough_paroxysmal"]
            )
        )

    def test_inline_delivery_uses_one_generation_call_and_linked_index(self):
        captured = []

        def generation_transport(_provider, messages, _timeout):
            captured.append(messages)
            return "Q1. 다친 뒤 시작했나요?\n\n1 예\n2 아니오"

        runtime = LlmChatbotInterviewRuntime(
            transport=generation_transport,
            retrieval_transport=lambda *_args: self.fail("retrieval call must not run"),
            knowledge_delivery="inline_linked_index",
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
        self.assertEqual(len(captured), 1)
        self.assertEqual(
            captured[0][0]["content"],
            (ROOT / "docs/gpt/CLINICAL_ADAPTIVE_RUNTIME_INSTRUCTIONS.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn("linked_package_index", captured[0][1]["content"])
        self.assertIn("question.joint-limb.recent-injury", captured[0][1]["content"])


if __name__ == "__main__":
    unittest.main()
