"""Conversation-native adaptive interview runtime.

The Custom GPT conversation is the behavioral contract.  This session keeps
the original user and assistant turns intact and delegates the next clinical
turn to the selected LLM with the repository's GPT instructions and selected
Knowledge package.  It deliberately does not choose, rewrite, or replace a
question with a deterministic Fact planner.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import re
from typing import Any, Callable


ChatbotTurn = Callable[[str, list[dict[str, str]]], str]

_QUESTION_RE = re.compile(
    r"(?im)^(?:\*\*)?\s*(?:\[)?Q(?P<number>[1-9]\d*)(?:\])?[.)：:]?"
    r"(?:\*\*)?\s*(?P<stem>.+?)\s*$"
)
_OPTION_RE = re.compile(r"^\s*(?P<number>\d+)[.)]?\s+(?P<label>\S.*)$")


@dataclass
class ChatbotInterviewSession:
    session_id: str
    reason_for_encounter: str
    chatbot_turn: ChatbotTurn
    conversation: list[dict[str, str]] = field(default_factory=list)
    closed: bool = False
    latest_question: dict[str, Any] | None = None

    def process(self, message: str) -> dict[str, Any]:
        self._ensure_open()
        text = message.strip()
        if not text:
            raise ValueError("message must not be empty")
        self.conversation.append({"role": "user", "content": text})
        assistant = self.chatbot_turn(
            self.reason_for_encounter, deepcopy(self.conversation)
        )
        if not isinstance(assistant, str) or not assistant.strip():
            raise RuntimeError("chatbot LLM returned no usable interview turn")
        assistant = assistant.strip()
        self.conversation.append({"role": "assistant", "content": assistant})
        self.latest_question = _parse_question(assistant)
        completed = text == "종료 확인" or "설문이 종료되었습니다" in assistant
        stopped = any(
            marker in assistant
            for marker in ("설문을 중단", "문진을 중단", "상태: stopped")
        )
        return {
            "runtime": "custom_gpt_conversation",
            "reason_for_encounter": self.reason_for_encounter,
            "assistant_message": assistant,
            "selected_question": deepcopy(self.latest_question),
            "interview_flow": {
                "status": "completed" if completed else "stopped" if stopped else "in-progress",
                "question_selection": "llm_with_exact_repository_knowledge",
                "legacy_deterministic_fallback": False,
            },
            "turn_count": len(self.conversation),
        }

    def clinician_handoff(self) -> dict[str, Any]:
        self._ensure_open()
        return {
            "session_id": self.session_id,
            "reason_for_encounter": self.reason_for_encounter,
            "status": "draft",
            "lifecycle_status": "draft",
            "review_status": "unreviewed",
            "clinical_use_status": "limited",
            "independent_diagnosis_or_treatment": False,
            "runtime": "custom_gpt_conversation",
            "conversation": deepcopy(self.conversation),
            "latest_question": deepcopy(self.latest_question),
            "note": (
                "대화 원문은 현재 프로세스 메모리에만 있으며, 최종 임상 요약은 "
                "정확한 '종료 확인' 뒤 LLM이 생성한 완료 응답을 기준으로 검토해야 합니다."
            ),
        }

    def close(self) -> dict[str, Any]:
        self.conversation.clear()
        self.latest_question = None
        self.closed = True
        return {
            "status": "closed",
            "response_state_purged": True,
            "runtime": "custom_gpt_conversation",
        }

    def _ensure_open(self) -> None:
        if self.closed:
            raise RuntimeError("chatbot interview session is closed")


def _parse_question(message: str) -> dict[str, Any] | None:
    """Parse the visible Q reference and shortcuts without changing the text."""
    match = _QUESTION_RE.search(message)
    if match is None:
        return None
    question_ref = f"Q{match.group('number')}"
    stem = match.group("stem").strip().strip("*").strip()
    suffix = message[match.end():]
    options: list[dict[str, Any]] = []
    for line in suffix.splitlines():
        stripped = line.strip().strip("-•").strip()
        option = _OPTION_RE.match(stripped)
        if option is None:
            continue
        label = option.group("label").strip().strip("*").strip()
        if label.startswith(("출처:", "응답 안내:", "번호로 답")):
            continue
        options.append(
            {
                "input": option.group("number"),
                "display_ko": label,
                "internal_value": label,
            }
        )
    return {
        "question_ref": question_ref,
        "fact_id": f"chatbot.{question_ref.lower()}",
        "text": stem,
        "stem_text": stem,
        "answer_options": options,
        "allow_free_text": True,
        "response_instruction_ko": (
            "번호로 답하거나, 보기에 없으면 내용을 직접 입력해 주세요."
            if options else "내용을 자유롭게 입력해 주세요."
        ),
        "source": "custom_gpt_llm_turn",
    }
