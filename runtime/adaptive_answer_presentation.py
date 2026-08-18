"""Patient-facing answer presentation for adaptive Knowledge questions.

The Knowledge graph stores stable internal answer tokens.  Those tokens are
implementation identifiers, not patient labels.  This module derives labels
only from the authored Korean question and only for completion-policy selector
Facts, where the allowed-value order and the displayed choice order are the
same authored contract.  Ambiguous layouts have explicit reviewed overrides.

No fallback turns ``snake_case`` into a patient option.  If a label cannot be
resolved with this contract, the Runtime leaves the question open-text and the
client must not expose terminology-server implementation codes.
"""
from __future__ import annotations

import re
from typing import Any


LOCAL_ANSWER_SYSTEM = (
    "https://ggojang.github.io/clinical-interview-platform/fhir/"
    "CodeSystem/clinical-interview-answer"
)


_TERMINAL_LABELS = {
    "other_unclear": "기타·불명확",
    "other_or_unclear": "기타·불명확",
    "other": "기타",
    "unknown": "잘 모르겠음",
    "unclear": "잘 모르겠음",
    "not_applicable": "해당 없음",
}


# These questions cannot be recovered safely by comma-list parsing, or their
# authored wording groups choices differently from the stable internal values.
_LABEL_OVERRIDES: dict[str, list[str]] = {
    "diabetes.type_or_context": [
        "1형 당뇨병", "2형 당뇨병", "임신성 당뇨병", "기타 유형", "잘 모르겠음",
    ],
    "fatigue.primary_group": [
        "갑작스러운 피로 변화", "수면·낮 졸림 관련", "활동 후 악화",
        "기분·스트레스 관련", "감염·체중 변화 동반", "숨참·출혈 동반",
        "내분비·대사 증상 관련", "임신·산후", "약물·물질 관련",
        "소아·청소년", "기타·불명확",
    ],
    "encounter.result_follow_up.goal": [
        "의료기관 검사결과 확인", "검사결과 판독·설명", "둘 다", "잘 모르겠음",
    ],
    "lump.primary_group": [
        "림프절", "피부·피하", "깊은 연부조직", "유방·겨드랑이", "목",
        "서혜부·음낭", "복부·골반", "뼈", "기타·불명확",
    ],
    "movement.primary_group": [
        "떨림", "느려짐·경직 또는 파킨슨증 양상", "비틀림·이상 자세",
        "움찔거림·무도증·틱 등 불수의 운동", "약물·물질·대사 관련",
        "진단된 운동질환 추적", "기타·불명확",
    ],
    "patient.smoking.product_types": [
        "일반담배", "가열담배", "전자담배", "시가·파이프·물담배",
        "무연담배", "니코틴 파우치", "기타 제품",
    ],
    "patient.smoking.status": [
        "현재 사용", "과거 사용 후 중단", "평생 사용한 적 없음",
    ],
    "patient.alcohol.use_status": [
        "현재 음주", "과거 음주 후 금주", "평생 비음주",
    ],
    "pregnancy.primary_concern_group": [
        "임신 초기 통증·출혈", "임신 후기 태동·양수·진통",
        "임신 중 전신 증상", "산후 신체 회복", "산후 정신건강·수유",
        "기타·불명확",
    ],
    "resp_followup.condition_group": [
        "천식", "COPD", "천식·COPD 중복", "불확실한 호흡기 질환",
        "기타·불명확",
    ],
    "result.report.status": [
        "등록됨", "일부 결과", "예비", "최종", "수정됨", "정정됨",
        "추가됨", "취소됨", "오입력", "잘 모르겠음",
    ],
    "result.follow_up_action_status": [
        "아직 시작 전", "예약됨", "진행 중", "완료", "거절함",
        "해당 없음", "잘 모르겠음", "기타",
    ],
    "skin.primary_context": [
        "급성·빠르게 퍼지는 피부 변화", "국소 염증·상처",
        "약물·알레르기 시간관계", "반복 가려움·발진", "점·지속 병변",
        "소아·보호자 응답", "추적·결과 확인", "탈모·두피 변화",
        "기타·불명확",
    ],
}


def selector_fact_ids(completion_policy: dict[str, Any]) -> set[str]:
    """Return Facts that select a conditional completion branch."""
    return {
        item["selector_fact"]
        for item in completion_policy.get("conditional_required_facts", [])
        if isinstance(item, dict) and isinstance(item.get("selector_fact"), str)
    }


def _labels_from_authored_wording(wording: str, allowed_values: list[Any]) -> list[str]:
    text = wording.strip().rstrip(".?")
    # ``중`` is matched as a standalone postposition.  Matching it inside
    # words such as 체중, 집중 or 진행 중 corrupts option labels.
    text = re.sub(r"\s+중\s+(?:무엇|어디|어느|가장)[^,.?]*$", "", text)
    text = text.split("?", 1)[0]
    labels = [part.strip() for part in text.split(",") if part.strip()]
    if labels:
        for marker in (
            "상황은 ", "목적은 ", "문제는 ", "불편은 ", "증상은 ",
            "부위는 ", "곳은 ", "변화는 ", "유형은 ", "상태는 ",
            "양상은 ",
        ):
            if marker in labels[0]:
                labels[0] = labels[0].split(marker, 1)[1]
                break
        else:
            # Remove only the leading topic clause (for example ``이번 복통은``
            # or ``오늘 추적관리하려는 질환은``), never text inside a choice.
            labels[0] = re.sub(r"^.{1,80}?(?:은|는)\s+", "", labels[0], count=1)
        labels[0] = re.sub(
            r"^현재 피로와 가장 관련 있어 보이는 상황은 무엇인가요\?\s*",
            "",
            labels[0],
        )
    labels = [
        re.sub(r"^(?:또는|아니면)\s+", "", re.sub(r"\s+중\s+.*$", "", label)).strip()
        for label in labels
    ]
    while (
        len(labels) < len(allowed_values)
        and str(allowed_values[len(labels)]) in _TERMINAL_LABELS
    ):
        labels.append(_TERMINAL_LABELS[str(allowed_values[len(labels)])])
    return labels


def patient_answer_options(
    fact_id: str,
    fact_node: dict[str, Any],
    question_template: dict[str, Any],
    completion_policy: dict[str, Any],
    local_answer_system: str | None = None,
) -> list[dict[str, Any]]:
    """Return localized options only when the authored mapping is complete."""
    allowed_values = list(fact_node.get("allowed_values") or [])
    if not allowed_values or fact_id not in selector_fact_ids(completion_policy):
        return []
    labels = _LABEL_OVERRIDES.get(fact_id) or _labels_from_authored_wording(
        str(question_template.get("wording") or ""), allowed_values
    )
    if len(labels) != len(allowed_values) or any(not label for label in labels):
        return []

    binding = fact_node.get("answer_semantic_binding", {})
    mapped = binding.get("internal_value_mappings", {})
    system = local_answer_system or LOCAL_ANSWER_SYSTEM
    complete_local = binding.get("value_set_strategy") == "complete_local"
    options = []
    for index, (internal_value, display_ko) in enumerate(
        zip(allowed_values, labels), start=1
    ):
        option: dict[str, Any] = {
            "input": str(index),
            "internal_value": internal_value,
            "display_ko": display_ko,
        }
        mapping = mapped.get(str(internal_value))
        if mapping:
            option["coding"] = {
                key: mapping[key]
                for key in ("system", "code", "display")
                if key in mapping
            }
        elif complete_local:
            option["coding"] = {
                "system": system,
                "code": f"{fact_id}--{internal_value}",
                # Coding.display is the localized human-readable rendering for
                # this response.  Stable identity remains in system + code.
                "display": display_ko,
            }
        options.append(option)
    return options


def selector_stem_ko(fact_id: str) -> str:
    """Return a concise single-answer prompt for a selector question."""
    if fact_id == "abdominal_pain.primary_group":
        return "이번 복통은 어떤 상황에 가장 가깝나요?"
    if fact_id.endswith((".primary_group", ".primary_context")):
        return "이번 방문에서 현재 상황과 가장 가까운 항목을 선택해 주세요."
    return "현재 상황과 가장 가까운 항목을 선택해 주세요."


def resolve_patient_option(
    options: list[dict[str, Any]], answer: str
) -> dict[str, Any] | None:
    """Resolve a number, internal value or localized label to one option."""
    normalized = answer.strip().lower().rstrip(".!?")
    for option in options:
        aliases = {
            str(option.get("input", "")).lower(),
            str(option.get("internal_value", "")).lower(),
            str(option.get("display_ko", "")).lower(),
        }
        if normalized in aliases:
            return option
    return None
