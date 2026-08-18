"""Deterministic presentation metadata for adaptive interview questions.

These shortcuts are not clinical answer codes and must never be exported as a
Questionnaire ``answerOption`` or included in an answer ValueSet.  They only
make an otherwise free-text question easier to answer.  The Runtime owns this
contract so every client presents the same choices without asking an LLM to
invent them.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any


PRESENTATION_CONTRACT_VERSION = "0.4.0"


_FACT_SUGGESTIONS: dict[str, list[dict[str, str]]] = {
    "symptom.duration": [
        {
            "input": "1",
            "display_ko": "오늘부터",
            "answer_text": "1일",
        },
        {
            "input": "2",
            "display_ko": "3일 정도",
            "answer_text": "3일",
        },
        {
            "input": "3",
            "display_ko": "1주일 정도",
            "answer_text": "1주",
        },
        {
            "input": "4",
            "display_ko": "1개월 정도",
            "answer_text": "1개월",
        },
    ],
}


DATA_ABSENT_ACTIONS = [
    {
        "input": "5",
        "display_ko": "잘 모르겠음",
        "dataAbsentReason": "asked-unknown",
        "answer_text": "잘 모르겠습니다",
    },
    {
        "input": "6",
        "display_ko": "답변하지 않음",
        "dataAbsentReason": "asked-declined",
        "answer_text": "답변하지 않음",
    },
]


def data_absent_actions(start_input: int = 5) -> list[dict[str, str]]:
    """Return separately numbered absence actions for the visible question."""
    actions = deepcopy(DATA_ABSENT_ACTIONS)
    for offset, action in enumerate(actions):
        action["input"] = str(start_input + offset)
    return actions


def resolve_data_absent_input(
    answer: str, actions: list[dict[str, str]]
) -> dict[str, Any] | None:
    """Resolve a visible absence action without treating it as an answer code."""
    normalized = answer.strip().lower().rstrip(".!?")
    for action in actions:
        aliases = {
            action["input"].lower(),
            action["display_ko"].lower(),
            action["answer_text"].lower(),
        }
        if normalized in aliases:
            return {
                "kind": "data_absent",
                "answer_text": action["answer_text"],
                "dataAbsentReason": action["dataAbsentReason"],
            }
    return None


def display_suggestions(
    fact_id: str, *, chatbot: bool = False
) -> list[dict[str, str]]:
    """Return input-only shortcuts for a Fact, never coded answer options."""
    explicit = _FACT_SUGGESTIONS.get(fact_id)
    if explicit is not None:
        return deepcopy(explicit)
    if not chatbot:
        return []
    labels = _chatbot_example_labels(fact_id)
    return [
        {
            "input": str(index),
            "display_ko": label,
            "answer_text": label,
        }
        for index, label in enumerate(labels[:4], start=1)
    ]


def chatbot_stem_ko(fact_id: str, wording: str) -> str | None:
    """Return the concise patient question used by the Chatbot-test Runtime.

    Compiled authoring questions intentionally preserve every clinician handoff
    dimension.  They are therefore often too long to show directly to a
    patient.  This presentation layer selects one answer-bearing axis without
    changing the immutable Knowledge object or pretending that a partial
    answer resolves every clause in the authoring text.
    """
    low = fact_id.casefold()
    exact = {
        "symptom.headache.location": "머리에서 가장 아픈 곳은 어디인가요?",
        "headache.side_site_radiation_and_laterality": "두통이 한쪽인가요, 양쪽인가요? 다른 부위로 퍼지면 함께 알려주세요.",
        "neck.exact_site_laterality_and_extent": "목에서 가장 아픈 곳은 어디인가요?",
        "neck.current_pain_nrs": "현재 목 통증은 0~10 중 몇 점인가요?",
        "neck.worst_pain_nrs": "가장 심했을 때 목 통증은 0~10 중 몇 점이었나요?",
        "neck.pain_quality_and_stiffness": "목 통증은 어떤 느낌인가요?",
        "neck.range_of_motion_and_torticollis": "목 움직임은 얼마나 제한되나요?",
        "neck.night_rest_pain_and_sleep_interruption": "가만히 있거나 밤에 목 통증이 더 심해지나요?",
        "neck.headache_dizziness_visual_speech_or_facial_symptoms": "두통·어지럼·시야·말·얼굴 증상이 함께 있나요?",
        "headache.current_nrs_peak_nrs_and_peak_time": "현재 두통은 0~10 중 몇 점인가요?",
        "headache.patient_concern_goal_expectation_and_additional_comment": "이번 진료에서 가장 확인하고 싶은 점은 무엇인가요?",
        "neck.patient_concern_goal_and_other_detail": "이번 진료에서 가장 확인하고 싶은 점은 무엇인가요?",
    }
    if fact_id in exact:
        return exact[fact_id]
    if any(token in low for token in ("exact_site", ".location", "pain_site")):
        return "불편하거나 아픈 부위는 어디인가요?"
    if any(token in low for token in ("onset_date", "date_time", "started_at")):
        return "증상은 언제 처음 시작됐나요?"
    if low.endswith(".onset_mode") or "onset_speed" in low:
        return "증상은 갑자기 시작했나요, 서서히 시작했나요?"
    if "duration_course_frequency" in low or "continuous_episodic" in low:
        return "증상이 나타나는 양상은 어떤가요?"
    if low == "symptom.duration" or low.endswith(".duration"):
        return "증상은 언제부터 있었나요?"
    if any(token in low for token in ("current_pain_nrs", "current_nrs")):
        return "현재 통증은 0~10 중 몇 점인가요?"
    if any(token in low for token in ("worst_pain_nrs", "peak_nrs")):
        return "가장 심했을 때 통증은 0~10 중 몇 점이었나요?"
    if any(token in low for token in ("pain_quality", ".quality", ".character")):
        return "통증이나 불편감은 어떤 느낌인가요?"
    if any(token in low for token in ("radiation", "spread", "migration")):
        return "통증이나 이상감각이 다른 부위로 퍼지나요?"
    if any(token in low for token in ("trigger", "aggravat", "provok", "movement_posture")):
        return "어떤 움직임이나 상황에서 더 심해지나요?"
    if any(token in low for token in ("relief", "alleviat")):
        return "무엇을 하면 증상이 나아지나요?"
    if any(token in low for token in ("range_of_motion", "movement_limit")):
        return "움직임은 얼마나 제한되나요?"
    if any(token in low for token in ("numbness", "tingling", "sensory")):
        return "저림이나 감각 둔함이 있나요? 있다면 어디인가요?"
    if any(token in low for token in ("weakness", "grip", "dexterity")):
        return "힘이 빠지거나 손동작이 달라졌나요?"
    if any(token in low for token in ("gait", "balance", "falls")):
        return "걷기나 균형에 변화가 있나요?"
    if any(token in low for token in ("fever", "chills", "systemic")):
        return "열·오한 같은 전신 증상이 함께 있나요?"
    if any(token in low for token in ("injury", "trauma", "whiplash")):
        return "증상 시작 전에 다치거나 무리한 일이 있었나요?"
    if any(token in low for token in ("infection", "dental", "ent", "recent_procedure")):
        return "최근 감염이나 관련 시술·수술이 있었나요?"
    if any(token in low for token in ("occupation", "ergonomic", "work_exposure")):
        return "직업·학업이나 반복 자세가 증상에 영향을 주나요?"
    if any(token in low for token in ("function", "activity_impact", "selfcare")):
        return "증상 때문에 일상생활이 얼마나 불편한가요?"
    if any(token in low for token in ("prior_treatment", "treatment_response")):
        return "지금까지 해본 치료와 그 효과는 어땠나요?"
    if any(token in low for token in ("prior_imaging", "prior_labs", "prior_bp")):
        return "이 증상으로 받은 검사와 결과가 있나요?"
    if any(token in low for token in ("current_medicine", "medication")):
        return "현재 복용하거나 사용하는 약이 있나요?"
    if "allerg" in low:
        return "알레르기나 약물 부작용이 있나요?"
    if any(token in low for token in ("patient_concern", "goal", "expectation")):
        return "이번 진료에서 가장 확인하고 싶은 점은 무엇인가요?"
    if any(token in low for token in ("prior_examination", "prior_diagnosis", "specialist")):
        return "이 증상으로 이전에 진료받은 적이 있나요?"
    if any(token in low for token in ("family", "familial")):
        return "가족 중 비슷하거나 관련된 질환이 있나요?"
    if any(token in low for token in ("smoking", "alcohol", "substance")):
        return "흡연·음주 등 증상과 관련될 수 있는 생활 요인이 있나요?"
    if any(token in low for token in ("age", "demographic", "life_stage")):
        return "증상 판단에 필요한 나이·임신·산후 정보가 있나요?"
    if any(token in low for token in ("information_source", "proxy", "reliability")):
        return "이 답변은 본인 경험인가요, 보호자나 기록에 따른 내용인가요?"
    if any(token in low for token in ("accessibility", "communication_need")):
        return "문진이나 진료에 필요한 의사소통 지원이 있나요?"
    # Local import avoids a module cycle: adaptive_answer_presentation imports
    # no patient-question composer and remains the audited answer-code layer.
    from runtime.adaptive_answer_presentation import concise_stem_ko

    concise = concise_stem_ko(fact_id, wording)
    if concise:
        return concise
    if wording and len(wording) <= 72:
        return wording
    return "이 증상과 관련해 의료진에게 전달할 다른 중요한 내용이 있나요?"


def _chatbot_example_labels(fact_id: str) -> list[str]:
    low = fact_id.casefold()
    if fact_id == "symptom.headache.location":
        return ["이마·눈 주위", "관자놀이", "정수리", "뒤통수·목 위쪽"]
    if fact_id == "neck.exact_site_laterality_and_extent":
        return ["왼쪽 목덜미", "오른쪽 목덜미", "목 중앙", "목과 어깨 사이"]
    if any(token in low for token in ("pain_quality", ".quality", ".character")):
        return ["뻐근함·묵직함", "쑤심·욱신거림", "찌르는 느낌", "타거나 전기 오는 느낌"]
    if "duration_course_frequency" in low or "continuous_episodic" in low:
        return ["계속됨", "간헐적으로 반복", "좋아지는 중", "점점 심해짐"]
    if any(token in low for token in ("radiation", "spread", "migration")):
        return ["퍼지지 않음", "머리·뒤통수로", "어깨·날개뼈로", "팔·손으로"]
    if any(token in low for token in ("trigger", "aggravat", "provok", "movement_posture")):
        return ["움직일 때", "오래 같은 자세일 때", "기침·힘줄 때", "특별한 유발 상황 없음"]
    if any(token in low for token in ("relief", "alleviat")):
        return ["쉬면 나아짐", "자세를 바꾸면 나아짐", "찜질·약으로 나아짐", "나아지는 방법 없음"]
    if any(token in low for token in ("range_of_motion", "movement_limit")):
        return ["제한 없음", "조금 제한됨", "한 방향이 많이 제한됨", "거의 움직이기 어려움"]
    if any(token in low for token in ("numbness", "tingling", "sensory")):
        return ["없음", "왼쪽 팔·손", "오른쪽 팔·손", "양쪽 팔·손"]
    if any(token in low for token in ("weakness", "grip", "dexterity")):
        return ["없음", "팔 들기 어려움", "손아귀 힘이 약해짐", "물건을 자주 떨어뜨림"]
    if any(token in low for token in ("gait", "balance", "falls")):
        return ["없음", "걷기가 불안정함", "계단이 어려움", "넘어졌거나 넘어질 뻔함"]
    if any(token in low for token in ("fever", "chills", "systemic")):
        return ["없음", "열·오한", "심한 피로·식은땀", "체중 감소·발진"]
    if any(token in low for token in ("injury", "trauma", "whiplash")):
        return ["관련 없음", "넘어짐·충돌", "운동·무거운 물건", "자고 일어난 뒤"]
    if any(token in low for token in ("function", "activity_impact", "selfcare")):
        return ["거의 영향 없음", "일부 활동이 불편", "일·수면에 큰 영향", "도움이 필요함"]
    return []


def resolve_presentation_input(
    fact_id: str,
    answer: str,
    *,
    chatbot: bool = False,
) -> dict[str, Any] | None:
    """Resolve a shortcut label/number without confusing it with a code."""
    normalized = answer.strip().lower().rstrip(".!?")
    suggestions = display_suggestions(fact_id, chatbot=chatbot)
    for suggestion in suggestions:
        aliases = {
            suggestion["input"].lower(),
            suggestion["display_ko"].lower(),
            suggestion["answer_text"].lower(),
        }
        if normalized in aliases:
            return {
                "kind": "display_suggestion",
                "answer_text": suggestion["answer_text"],
            }
    # Inputs 5 and 6 are reserved only in the shortcut presentation.  Treating
    # them globally would corrupt legitimate numeric answers such as NRS 5.
    return resolve_data_absent_input(answer, DATA_ABSENT_ACTIONS) if suggestions else None
