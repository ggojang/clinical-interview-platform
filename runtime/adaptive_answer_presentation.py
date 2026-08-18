"""Patient-facing answer presentation for adaptive Knowledge questions.

The Knowledge graph stores stable internal answer tokens.  Those tokens are
implementation identifiers, not patient labels.  This module derives labels
only from an audited draft patient-presentation contract: shared atomic answer-domain
bindings, exact reusable value axes, or the authored selector wording.  The
same internal token is never translated in isolation because its patient label
can differ by clinical context.  Ambiguous layouts have explicit overrides.

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


# Draft patient-facing labels for reusable *exact* answer axes. A tuple must match
# the complete authored allowed-value sequence; individual snake_case tokens
# are never translated independently.  This is presentation metadata only:
# stable semantic identity remains the compiled system + code, and absent
# states are projected through dataAbsentReason rather than coded here.
_EXACT_AXIS_LABELS: dict[tuple[str, ...], dict[str, str]] = {
    ("none", "mild", "moderate", "severe"): {
        "none": "없음", "mild": "가벼움", "moderate": "중간", "severe": "심함",
    },
    ("mild", "moderate", "severe"): {
        "mild": "가벼움", "moderate": "중간", "severe": "심함",
    },
    ("none", "some_days", "often", "nearly_every_day"): {
        "none": "없음", "some_days": "가끔", "often": "자주",
        "nearly_every_day": "거의 매일",
    },
    ("not_tried", "improved", "unchanged", "worsened"): {
        "not_tried": "해보지 않음", "improved": "좋아짐",
        "unchanged": "변화 없음", "worsened": "악화됨",
    },
    ("improving", "unchanged", "worsening", "fluctuating", "resolved", "uncertain", "other"): {
        "improving": "좋아지는 중", "unchanged": "변화 없음",
        "worsening": "악화되는 중", "fluctuating": "좋아졌다 나빠졌다 함",
        "resolved": "회복됨", "uncertain": "판단하기 어려움", "other": "기타",
    },
    ("left", "right", "bilateral", "unclear"): {
        "left": "왼쪽", "right": "오른쪽", "bilateral": "양쪽",
        "unclear": "잘 모르겠음",
    },
    ("none", "less_than_daily", "daily"): {
        "none": "없음", "less_than_daily": "매일은 아님", "daily": "매일",
    },
    ("current", "former", "never"): {
        "current": "현재", "former": "과거", "never": "한 번도 없음",
    },
    ("current", "former", "never", "unknown", "other"): {
        "current": "현재 사용", "former": "과거 사용", "never": "사용한 적 없음",
        "unknown": "잘 모르겠음", "other": "기타 사용 상태",
    },
    ("sudden", "gradual", "unclear"): {
        "sudden": "갑자기 시작", "gradual": "서서히 시작",
        "unclear": "잘 모르겠음",
    },
    ("sudden", "gradual"): {
        "sudden": "갑자기 시작", "gradual": "서서히 시작",
    },
    ("pregnant", "postpartum_within_one_year", "not_pregnant_or_postpartum", "not_applicable", "unknown"): {
        "pregnant": "임신 중", "postpartum_within_one_year": "출산 후 1년 이내",
        "not_pregnant_or_postpartum": "임신·산후에 해당하지 않음",
        "not_applicable": "해당 없음", "unknown": "잘 모르겠음",
    },
    ("pregnant", "postpartum_6_weeks", "not_pregnant_or_postpartum", "not_applicable", "unknown"): {
        "pregnant": "임신 중", "postpartum_6_weeks": "출산 후 6주 이내",
        "not_pregnant_or_postpartum": "임신·산후에 해당하지 않음",
        "not_applicable": "해당 없음", "unknown": "잘 모르겠음",
    },
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
    """Return localized options only when the audited draft mapping is complete."""
    allowed_values = list(fact_node.get("allowed_values") or [])
    if not allowed_values:
        return []

    binding = fact_node.get("answer_semantic_binding", {})
    absent_values = set(binding.get("data_absent_reason_mappings", {}))
    clinical_values = [
        value for value in allowed_values if str(value) not in absent_values
    ]
    if not clinical_values:
        return []

    shared_mappings = binding.get("internal_value_mappings", {})
    labels_by_value: dict[str, str] = {}
    if fact_id in selector_fact_ids(completion_policy):
        labels = _LABEL_OVERRIDES.get(fact_id) or _labels_from_authored_wording(
            str(question_template.get("wording") or ""), allowed_values
        )
        if len(labels) == len(allowed_values) and all(labels):
            labels_by_value = {
                str(value): label for value, label in zip(allowed_values, labels)
            }
    elif all(
        shared_mappings.get(str(value), {}).get("display_ko")
        for value in clinical_values
    ):
        labels_by_value = {
            str(value): shared_mappings[str(value)]["display_ko"]
            for value in clinical_values
        }
    else:
        labels_by_value = _EXACT_AXIS_LABELS.get(
            tuple(str(value) for value in allowed_values), {}
        )
    if any(not labels_by_value.get(str(value)) for value in clinical_values):
        return []

    mapped = {
        **binding.get("snomed_mappings", {}),
        **binding.get("fhir_bound_answer_mappings", {}),
        **shared_mappings,
    }
    system = local_answer_system or LOCAL_ANSWER_SYSTEM
    options = []
    for index, internal_value in enumerate(clinical_values, start=1):
        display_ko = labels_by_value[str(internal_value)]
        option: dict[str, Any] = {
            "input": str(index),
            "internal_value": internal_value,
            "display_ko": display_ko,
        }
        mapping = mapped.get(str(internal_value))
        if mapping:
            option["coding"] = {
                key: mapping[key]
                for key in ("system", "code")
                if key in mapping
            }
            # display is the current patient-language rendition. The stable
            # identity remains system + code; source terminology display stays
            # available in the compiled binding for audit.
            option["coding"]["display"] = display_ko
        else:
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
