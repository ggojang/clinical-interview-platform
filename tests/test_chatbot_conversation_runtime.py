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
    _response_repeats_prior_question,
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

    def test_parenthesized_question_provenance_is_preserved_for_safety_mapping(self):
        session = ChatbotInterviewSession(
            "source-id",
            "rfe.abdominal_pain",
            lambda _rfe, _conversation: (
                "Q1. 쓰러질 듯한 상태가 있나요?\n\n"
                "1 예\n2 아니오\n3 잘 모르겠음\n4 답변하지 않음\n\n"
                "(question.abdominal_pain.collapse-shock)"
            ),
        )

        state = session.process("배가 아파요")

        self.assertEqual(
            state["selected_question"]["source_question_id"],
            "question.abdominal_pain.collapse-shock",
        )

    def test_same_line_source_marker_is_not_exposed_as_question_text(self):
        session = ChatbotInterviewSession(
            "same-line-source",
            "rfe.abdominal_pain",
            lambda _rfe, _conversation: (
                "**Q1. 통증이 갑자기 시작했나요?** "
                "[공동 작업 지식] question.abdominal_pain.sudden-onset\n\n"
                "1 예\n2 아니오"
            ),
        )

        state = session.process("배가 아파요")

        self.assertEqual(
            state["selected_question"]["text"],
            "통증이 갑자기 시작했나요?",
        )
        self.assertNotIn(
            "공동 작업 지식", state["selected_question"]["text"]
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

    def test_previsit_session_stops_questioning_at_eight_and_enters_review(self):
        calls = []

        def turn(_rfe_id, _conversation):
            number = len(calls) + 1
            calls.append(number)
            return f"Q{number}. 필수 정보 {number}을 알려주세요?"

        session = ChatbotInterviewSession("budget", "rfe.cough", turn)
        state = session.process("기침")
        for _ in range(8):
            state = session.process("답변")

        self.assertEqual(calls, list(range(1, 9)))
        self.assertEqual(state["interview_flow"]["status"], "review")
        self.assertIn("응답 검토", state["assistant_message"])
        self.assertEqual(state["interview_flow"]["questions_asked"], 8)

    def test_health_consultation_uses_six_questions_then_requests_advice(self):
        calls = []

        def turn(_rfe_id, _conversation):
            number = len(calls) + 1
            calls.append(number)
            return f"Q{number}. 안전 확인 {number}이 있나요?"

        session = ChatbotInterviewSession(
            "health-budget",
            "rfe.abdominal_pain",
            turn,
            interaction_purpose="health_information",
            question_budget=6,
        )
        session.process("배가 아파요")
        for _ in range(6):
            state = session.process("아니오")

        self.assertEqual(calls, list(range(1, 7)))
        self.assertEqual(state["interview_flow"]["status"], "information_ready")
        self.assertEqual(state["interview_flow"]["phase"], "advice")
        self.assertIsNone(state["assistant_message"])

    def test_numbered_yes_to_direct_health_safety_question_triggers_action(self):
        runtime = LlmChatbotInterviewRuntime(enabled=False, repository_root=ROOT)
        assessment = runtime.assess_health_information_answer(
            "rfe.abdominal_pain",
            "1",
            {
                "source_question_id": "question.abdominal_pain.collapse-shock",
                "answer_options": [
                    {"input": "1", "display_ko": "예"},
                    {"input": "2", "display_ko": "아니오"},
                ],
            },
        )

        self.assertIsNotNone(assessment)
        self.assertEqual(assessment["level"], "emergency_suspected")
        self.assertIn("rule.abdominal_pain.safety.collapse-shock", assessment["matched_signals"])
        self.assertIn("119", assessment["action_ko"])

    def test_numbered_no_does_not_trigger_compiled_health_safety_rule(self):
        runtime = LlmChatbotInterviewRuntime(enabled=False, repository_root=ROOT)
        assessment = runtime.assess_health_information_answer(
            "rfe.abdominal_pain",
            "2",
            {
                "source_question_id": "question.abdominal_pain.collapse-shock",
                "answer_options": [
                    {"input": "1", "display_ko": "예"},
                    {"input": "2", "display_ko": "아니오"},
                ],
            },
        )

        self.assertIsNone(assessment)

    def test_previsit_and_health_consultation_rank_safety_differently(self):
        runtime = LlmChatbotInterviewRuntime(enabled=False, repository_root=ROOT)
        package = runtime._load_package("rfe.abdominal_pain")
        opening = [{"role": "user", "content": "배가 아파요"}]

        first = runtime._compiled_candidate_retrieval(
            "rfe.abdominal_pain", opening, package,
            interaction_purpose="clinical_adaptive",
        )["question_ids"][0]
        conversation = [
            *opening,
            {"role": "assistant", "content": f"Q1. 갑자기 시작했나요?\n1 예\n2 아니오\n출처: {first}"},
            {"role": "user", "content": "2"},
        ]
        previsit_second = runtime._compiled_candidate_retrieval(
            "rfe.abdominal_pain", conversation, package,
            interaction_purpose="clinical_adaptive",
        )["question_ids"][0]
        health_second = runtime._compiled_candidate_retrieval(
            "rfe.abdominal_pain", conversation, package,
            interaction_purpose="health_information",
        )["question_ids"][0]

        previsit_third = runtime._compiled_candidate_retrieval(
            "rfe.abdominal_pain",
            [
                *conversation,
                {"role": "assistant", "content": f"Q2. 두 번째 질문?\n1 예\n2 아니오\n출처: {previsit_second}"},
                {"role": "user", "content": "2"},
            ],
            package,
            interaction_purpose="clinical_adaptive",
        )["question_ids"][0]
        health_third = runtime._compiled_candidate_retrieval(
            "rfe.abdominal_pain",
            [
                *conversation,
                {"role": "assistant", "content": f"Q2. 두 번째 질문?\n1 예\n2 아니오\n출처: {health_second}"},
                {"role": "user", "content": "2"},
            ],
            package,
            interaction_purpose="health_information",
        )["question_ids"][0]

        self.assertIn(previsit_second, {
            "question.abdominal_pain.severity",
            "question.abdominal_pain.duration",
            "question.abdominal_pain.location",
        })
        self.assertTrue(
            health_second.startswith("question.abdominal_pain."),
            health_second,
        )
        self.assertNotEqual(previsit_second, "question.abdominal_pain.collapse-shock")
        self.assertNotEqual(previsit_third, "question.abdominal_pain.collapse-shock")
        self.assertEqual(health_third, "question.abdominal_pain.collapse-shock")

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

    def test_llm_runtime_uses_chatbot_test_instructions_and_exact_objects(self):
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
            return (
                "**Q1.** 다친 뒤 시작했나요?\n\n1 예\n2 아니오\n\n"
                "출처: [공동 작업 지식] question.joint-limb.recent-injury "
                "· [AI 표현] 문장"
            )

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
            (ROOT / "docs/gpt/CHATBOT_TEST_RUNTIME_INSTRUCTIONS.md").read_text(
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
        self.assertEqual(messages[-2], {"role": "user", "content": "왼쪽 발목 통증"})
        self.assertIn("<host_next_turn_contract>", messages[-1]["content"])
        self.assertIn("question.joint-limb.recent-injury", messages[-1]["content"])
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
            or (
                "Q1. 다친 뒤 시작했나요?\n\n"
                "출처: [공동 작업 지식] question.joint-limb.recent-injury"
            ),
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

        def generation_transport(_provider, messages, _timeout):
            captured.append(messages)
            directive = messages[-1]["content"]
            if "question.joint-limb.recent-injury" in directive:
                return "Q1. 다친 뒤 시작했나요?"
            return "Q2. 현재 증상을 조금 더 알려주세요."

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
        runtime.respond(
            "rfe.joint_limb_complaint",
            [{"role": "user", "content": "왼쪽 발목 통증"}],
            selection,
        )
        self.assertIn('"question.joint-limb.recent-injury"', captured[0][1]["content"])
        self.assertNotIn('"question.joint-limb.primary-context"', captured[0][1]["content"])
        self.assertIn("<host_next_turn_contract>", captured[0][-1]["content"])
        self.assertIn("question.joint-limb.recent-injury", captured[0][-1]["content"])

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

    def test_positive_cough_gate_prioritizes_conditional_detail(self):
        runtime = LlmChatbotInterviewRuntime(enabled=False, repository_root=ROOT)
        package = runtime._load_package("rfe.cough")
        conversation = [
            {"role": "user", "content": "기침"},
            {
                "role": "assistant",
                "content": "Q1. 언제 시작했나요?\n출처: question.symptom_onset",
            },
            {"role": "user", "content": "어제"},
            {
                "role": "assistant",
                "content": (
                    "Q2. 갑자기 시작했나요?\n1 예\n2 아니오\n"
                    "출처: question.symptom_cough_sudden_onset"
                ),
            },
            {"role": "user", "content": "2"},
            {
                "role": "assistant",
                "content": (
                    "Q3. 가슴 통증이 있나요?\n1 예\n2 아니오\n"
                    "출처: question.symptom_chest_pain"
                ),
            },
            {"role": "user", "content": "1"},
        ]
        retrieval = runtime._compiled_candidate_retrieval(
            "rfe.cough", conversation, package
        )
        self.assertTrue(retrieval["question_ids"][0].startswith("question.cough.chest-pain"))

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
        self.assertIn("previous draft violated", captured[1][-1]["content"])
        self.assertIn("question.symptom_onset", captured[1][-1]["content"])
        self.assertEqual(captured[1][-2], {"role": "user", "content": "기침"})

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

    def test_identical_prior_question_stem_is_rejected_even_with_allowed_id(self):
        conversation = [
            {"role": "user", "content": "기침"},
            {
                "role": "assistant",
                "content": (
                    "Q1. 기침이 처음 시작된 시점은 언제입니까?\n\n"
                    "출처: question.symptom_onset"
                ),
            },
            {"role": "user", "content": "어제"},
        ]
        response = (
            "Q4. 기침이 처음 시작된 시점은 언제입니까?\n\n"
            "출처: question.symptom_duration"
        )
        self.assertTrue(_response_repeats_prior_question(response, conversation))

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
            (ROOT / "docs/gpt/CHATBOT_TEST_RUNTIME_INSTRUCTIONS.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn("linked_package_index", captured[0][1]["content"])
        self.assertIn("question.joint-limb.recent-injury", captured[0][1]["content"])


if __name__ == "__main__":
    unittest.main()
