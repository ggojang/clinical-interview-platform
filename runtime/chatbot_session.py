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
from typing import Any, Callable, Optional


ChatbotTurn = Callable[[str, list[dict[str, str]]], str]
SafetyAssessor = Callable[[str, Optional[dict[str, Any]]], dict[str, Any]]

DEFAULT_PREVISIT_QUESTION_BUDGET = 8
DEFAULT_HEALTH_INFORMATION_QUESTION_BUDGET = 6

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
    interaction_purpose: str = "clinical_adaptive"
    question_budget: int = DEFAULT_PREVISIT_QUESTION_BUDGET
    safety_assessor: SafetyAssessor | None = None
    conversation: list[dict[str, str]] = field(default_factory=list)
    closed: bool = False
    latest_question: dict[str, Any] | None = None
    review_pending: bool = False
    information_ready: bool = False
    latest_safety_status: dict[str, Any] | None = None

    def process(self, message: str) -> dict[str, Any]:
        self._ensure_open()
        text = message.strip()
        if not text:
            raise ValueError("message must not be empty")
        self.conversation.append({"role": "user", "content": text})

        if self.safety_assessor is not None:
            self.latest_safety_status = self.safety_assessor(
                text,
                deepcopy(self.latest_question),
            )
            if self.latest_safety_status.get("level") in {
                "emergency_suspected",
                "urgent_assessment_suggested",
            }:
                assistant = str(self.latest_safety_status.get("action_ko", "")).strip()
                self.conversation.append({"role": "assistant", "content": assistant})
                self.latest_question = None
                return self._state(
                    assistant,
                    status="triage_handoff",
                    phase="safety_notification",
                )

        if self.review_pending and text == "종료 확인":
            assistant = (
                "설문이 종료되었습니다. 현재 응답은 이 종료 시점을 기준으로 "
                "확정되었습니다."
            )
            self.conversation.append({"role": "assistant", "content": assistant})
            self.latest_question = None
            return self._state(assistant, status="completed", phase="completed")

        if self._question_count() >= self.question_budget:
            self.latest_question = None
            if self.interaction_purpose == "health_information":
                self.information_ready = True
                return self._state(None, status="information_ready", phase="advice")
            assistant = _previsit_review_message(self.conversation)
            self.conversation.append({"role": "assistant", "content": assistant})
            self.review_pending = True
            return self._state(assistant, status="review", phase="review")

        assistant = self.chatbot_turn(
            self.reason_for_encounter,
            deepcopy(self.conversation),
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
        return self._state(
            assistant,
            status="completed" if completed else "stopped" if stopped else "in-progress",
            phase="questioning",
        )

    def _state(
        self,
        assistant: str | None,
        *,
        status: str,
        phase: str,
    ) -> dict[str, Any]:
        return {
            "runtime": "custom_gpt_conversation",
            "reason_for_encounter": self.reason_for_encounter,
            "interaction_purpose": self.interaction_purpose,
            "assistant_message": assistant,
            "selected_question": deepcopy(self.latest_question),
            "interview_flow": {
                "status": status,
                "phase": phase,
                "question_selection": "llm_with_exact_repository_knowledge",
                "question_budget": self.question_budget,
                "questions_asked": self._question_count(),
                "legacy_deterministic_fallback": False,
            },
            "turn_count": len(self.conversation),
            "conversation": deepcopy(self.conversation),
            "safety_status": deepcopy(self.latest_safety_status),
        }

    def result(self) -> dict[str, Any]:
        self._ensure_open()
        return {
            "status": (
                "information_ready"
                if self.information_ready
                else "review_pending"
                if self.review_pending
                else "in_progress"
            ),
            "reason_for_encounter": self.reason_for_encounter,
            "interaction_purpose": self.interaction_purpose,
            "questions_asked": self._question_count(),
            "latest_safety_status": deepcopy(self.latest_safety_status),
            "response_storage": "memory_only",
        }

    def _question_count(self) -> int:
        return sum(
            _parse_question(item.get("content", "")) is not None
            for item in self.conversation
            if item.get("role") == "assistant"
        )

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
        self.latest_safety_status = None
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
    stem = re.sub(
        r"\s*\*{0,2}\s*\[(?:공동 작업 지식|AI 표현|AI 자체 생성|"
        r"STOM 용어 조회|사용자 제공|첨부자료)\].*$",
        "",
        stem,
    ).strip().strip("*").strip()
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
    provenance = re.search(
        r"출처:\s*\[공동 작업 지식\]\s*([A-Za-z0-9_.-]+)",
        message,
    )
    if provenance is None:
        provenance = re.search(r"\b(question\.[A-Za-z0-9_.-]+)\b", message)
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
        "source_question_id": provenance.group(1) if provenance else None,
    }


def _previsit_review_message(conversation: list[dict[str, str]]) -> str:
    rows: list[str] = []
    question_ref = ""
    question_text = ""
    for item in conversation:
        if item.get("role") == "assistant":
            parsed = _parse_question(item.get("content", ""))
            if parsed is not None:
                question_ref = parsed["question_ref"]
                question_text = parsed["text"]
        elif item.get("role") == "user" and question_ref:
            rows.append(
                f"{len(rows) + 1}. [{question_ref}] {question_text}: {item.get('content', '').strip()}"
            )
            question_ref = ""
            question_text = ""
    body = "\n".join(rows) if rows else "확인된 응답이 없습니다."
    return (
        "응답 검토\n\n"
        f"{body}\n\n"
        "내용을 확인한 뒤 화면의 '문진 완료'를 누르거나 "
        "'종료 확인'이라고 입력해 주세요."
    )
