"""Ephemeral health-screening add-on package comparison workflow.

The source catalog is isolated test data, not Clinical Knowledge.  This
adapter performs deterministic local navigation over the current immutable
catalog version.  It never sends participant answers to a catalog Action and
never claims medical necessity, diagnosis, or current availability.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any

from runtime.session import extract, extract_atomic_social_history


CATALOG_ROOT = (
    Path(__file__).resolve().parents[1]
    / "docs/gpt/test-catalogs/health-screening-packages"
)
COMPILED_SCREENING_KNOWLEDGE = (
    Path(__file__).resolve().parents[1] / "docs/gpt/screening-kr.json"
)
COMPILED_CLINICIAN_CONTEXT = (
    Path(__file__).resolve().parents[1] / "docs/gpt/clinician-submission-context.json"
)

REGIONS = (
    ("seoul", "서울"), ("gyeonggi", "경기"), ("incheon", "인천"),
    ("busan", "부산"), ("daegu", "대구"), ("gwangju", "광주"),
    ("daejeon", "대전"), ("ulsan", "울산"), ("sejong", "세종"),
    ("gangwon", "강원"), ("chungbuk", "충북"), ("chungnam", "충남"),
    ("jeonbuk", "전북"), ("jeonnam", "전남"), ("gyeongbuk", "경북"),
    ("gyeongnam", "경남"), ("jeju", "제주"),
)

FOCUS_OPTIONS = (
    ("basic", "기본·종합 검진", ("기본", "베이직", "종합")),
    ("cancer", "암 검진", ("암", "종양")),
    ("cardiovascular", "뇌·심혈관", ("뇌", "심장", "심혈관", "혈관")),
    ("digestive", "위·대장·소화기", ("위", "대장", "소화", "내시경")),
    ("lung", "폐·호흡기", ("폐", "흉부", "호흡")),
    ("women", "여성 건강", ("여성", "유방", "부인")),
    ("men", "남성 건강", ("남성", "전립선")),
    ("senior", "고령·노년 건강", ("고령", "노인", "시니어")),
    ("precision", "정밀·프리미엄", ("정밀", "프리미엄", "vip")),
    ("unsure", "정하지 못함", ()),
)

BUDGET_OPTIONS = (
    ("lowest", "가장 저렴한 후보 우선"),
    ("balanced", "관심 영역과 가격을 함께 비교"),
    ("no_preference", "가격 선호 없음"),
    ("declined", "답변하지 않음"),
)

NHIS_OPTIONS = (
    ("not_now", "지금은 추가 문진만 진행"),
    ("after", "추천 후 국가건강검진 문진도 작성"),
    ("already_completed", "이미 국가건강검진 문진을 작성함"),
    ("unsure", "잘 모르겠음"),
)

OPERATIONAL_FACT_IDS = frozenset({
    "screening.focus",
    "screening.region",
    "screening.budget_preference",
    "screening.nhis_questionnaire_choice",
})

# Only relationships already allowed by the compiled
# ``history.family.relationship`` Fact receive a coded value. More distant
# relatives are still preserved in the existing narrative family-history
# Facts without inventing a new relationship code.
FAMILY_RELATIONSHIP_TERMS = {
    "어머니": "mother", "어머님": "mother", "엄마": "mother",
    "아버지": "father", "아버님": "father", "아빠": "father",
    "부모": "parent", "형제": "sibling", "자매": "sibling",
    "남매": "sibling", "할머니": "grandparent", "할아버지": "grandparent",
    "자녀": "child", "아들": "son", "딸": "daughter",
    "배우자": "spouse",
}
EXTENDED_FAMILY_CONTEXT_TERMS = (
    "가족", "가족력", "이모", "이모부", "고모", "고모부", "삼촌",
    "외삼촌", "외숙모", "숙모", "큰아버지", "작은아버지",
    "큰어머니", "작은어머니", "조부", "조모", "외조부", "외조모",
    "사촌", "조카",
)
SEX_RELEVANT_SCREENING_TERMS = (
    "유방", "유방암", "자궁", "자궁경부", "난소", "부인과", "전립선",
    "고환", "여성검진", "남성검진",
)


def _normalized(value: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]+", "", value.casefold())


def _question(
    fact_id: str,
    text: str,
    options: tuple[tuple[str, str], ...] = (),
) -> dict[str, Any]:
    return {
        "fact_id": fact_id,
        "text": text,
        "stem_text": text,
        "answer_options": [
            {
                "input": str(index),
                "display_ko": label,
                "internal_value": code,
            }
            for index, (code, label) in enumerate(options, 1)
        ],
        "allow_free_text": True,
        "response_instruction_ko": (
            "번호로 답하거나 내용을 직접 입력해 주세요."
            if options else "필요한 내용만 간단히 입력해 주세요. 없으면 '없음'이라고 답할 수 있습니다."
        ),
        "source": "screening_recommendation_workflow",
        "source_kind": "operational_comparison_condition",
    }


OPERATIONAL_QUESTIONS = (
    _question(
        "screening.focus",
        "추가 검진에서 우선 비교하고 싶은 영역은 무엇인가요?",
        tuple((code, label) for code, label, _ in FOCUS_OPTIONS),
    ),
    _question(
        "screening.region",
        "추가 검진 패키지를 비교할 지역은 어디인가요?",
        REGIONS,
    ),
    _question(
        "screening.budget_preference",
        "가격은 어떻게 비교할까요? 경제능력은 추정하지 않으며 선택하지 않아도 됩니다.",
        BUDGET_OPTIONS,
    ),
    _question(
        "screening.nhis_questionnaire_choice",
        "국가건강검진 문진은 어떻게 할까요? 패키지 비교의 필수 조건은 아닙니다.",
        NHIS_OPTIONS,
    ),
)


@lru_cache(maxsize=1)
def _compiled_question_catalog() -> dict[str, Any]:
    """Index existing compiled questions without creating parallel clinical content."""
    screening = json.loads(COMPILED_SCREENING_KNOWLEDGE.read_text(encoding="utf-8"))
    clinician = json.loads(COMPILED_CLINICIAN_CONTEXT.read_text(encoding="utf-8"))
    screening_by_id: dict[str, dict[str, Any]] = {}
    screening_by_fact: dict[str, list[dict[str, Any]]] = {}
    for group in screening.get("question_groups", []):
        for item in group.get("questions", []):
            indexed = {**deepcopy(item), "group_id": group.get("id")}
            screening_by_id[str(item["id"])] = indexed
            screening_by_fact.setdefault(str(item["fact_id"]), []).append(indexed)
    clinician_by_id = {
        str(item["template_id"]): deepcopy(item)
        for item in clinician.get("questions", [])
    }
    clinician_by_fact: dict[str, list[dict[str, Any]]] = {}
    for item in clinician.get("questions", []):
        clinician_by_fact.setdefault(str(item["fact_id"]), []).append(deepcopy(item))

    # The screening workflow may reuse an explicitly stated Fact from any
    # compiled package.  It still asks follow-up questions only from the two
    # compiled documents indexed above.  This separates reusable clinical
    # memory from the small set of workflow-only comparison conditions.
    fact_sources: dict[str, set[str]] = {}

    def index_facts(document: dict[str, Any], source: str) -> None:
        for item in document.get("facts", document.get("items", [])):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                continue
            fact_sources.setdefault(item["id"], set()).add(source)

    index_facts(screening, str(COMPILED_SCREENING_KNOWLEDGE.relative_to(
        COMPILED_SCREENING_KNOWLEDGE.parents[2]
    )))
    index_facts(clinician, str(COMPILED_CLINICIAN_CONTEXT.relative_to(
        COMPILED_CLINICIAN_CONTEXT.parents[2]
    )))
    gpt_root = COMPILED_SCREENING_KNOWLEDGE.parent
    for path in [gpt_root / "common-facts.json", *sorted(gpt_root.glob("rfe/*/facts.json"))]:
        if not path.is_file():
            continue
        index_facts(
            json.loads(path.read_text(encoding="utf-8")),
            str(path.relative_to(gpt_root.parents[1])),
        )
    return {
        "screening_document_id": screening["id"],
        "clinician_document_id": clinician["id"],
        "screening_by_id": screening_by_id,
        "screening_by_fact": screening_by_fact,
        "clinician_by_id": clinician_by_id,
        "clinician_by_fact": clinician_by_fact,
        "compiled_fact_ids": frozenset(fact_sources),
        "fact_sources": {
            fact_id: tuple(sorted(sources))
            for fact_id, sources in fact_sources.items()
        },
    }


def _explicit_existing_fact_candidates(text: str) -> dict[str, Any]:
    """Capture only explicitly stated values for already compiled Facts.

    The shared Runtime extractors provide the first pass.  The small context
    adapters below project unstructured demographic and history statements to
    existing common Facts; they do not define screening-specific clinical
    concepts or infer a diagnosis from a symptom.
    """
    candidates = {
        fact_id: candidate.get("value")
        for fact_id, candidate in {
            **extract(text, 0),
            **extract_atomic_social_history(text, 0),
        }.items()
        if isinstance(candidate, dict) and "value" in candidate
    }
    normalized = _normalized(text)
    family_relationship = next(
        (
            relationship
            for term, relationship in FAMILY_RELATIONSHIP_TERMS.items()
            if _normalized(term) in normalized
        ),
        None,
    )
    family_context = family_relationship is not None or any(
        _normalized(term) in normalized for term in EXTENDED_FAMILY_CONTEXT_TERMS
    )
    family_positions = [
        text.find(term)
        for term in (*FAMILY_RELATIONSHIP_TERMS, *EXTENDED_FAMILY_CONTEXT_TERMS)
        if text.find(term) >= 0
    ]
    first_family_position = min(family_positions) if family_positions else len(text)
    self_context = bool(re.search(
        r"(?:^|[\s,])(저는|나는|제가|본인|수검자|환자)(?:[\s,은는이가]|$)",
        text,
    )) or bool(re.search(
        r"^\s*(?:만\s*)?\d{1,3}\s*세\s*(?:남성|여성|남자|여자)",
        text,
    ))
    family_only_context = family_context and not self_context

    # A relative's age, sex, symptoms, diagnoses, or medication must never be
    # silently projected onto the participant.
    if family_context:
        # Symptom extraction cannot safely assign a mixed sentence to the
        # participant once a relative is mentioned. A later targeted compiled
        # question can collect it without making that attribution error.
        candidates.pop("patient.age_years", None)
        candidates = {
            fact_id: value
            for fact_id, value in candidates.items()
            if not fact_id.startswith("symptom.")
        }
        if self_context:
            age = extract(text[:first_family_position], 0).get("patient.age_years")
            if isinstance(age, dict) and "value" in age:
                candidates["patient.age_years"] = age["value"]

        for prefix, cues in (
            ("patient.smoking.", ("흡연", "담배", "vape", "smok")),
            ("patient.alcohol.", ("음주", "술", "alcohol")),
        ):
            cue_positions = [
                text.casefold().find(cue)
                for cue in cues
                if text.casefold().find(cue) >= 0
            ]
            participant_statement = bool(
                self_context
                and cue_positions
                and min(cue_positions) < first_family_position
            )
            if not participant_statement:
                candidates = {
                    fact_id: value
                    for fact_id, value in candidates.items()
                    if not fact_id.startswith(prefix)
                }

    if not family_only_context:
        participant_segment = (
            text[:first_family_position] if family_context else text
        )
        participant_normalized = _normalized(participant_segment)
        if re.search(
            r"(?:^|[\s,])(남성|남자)(?=$|[\s,]|이고|이며|입니다)",
            participant_segment,
        ):
            candidates["patient.sex_for_clinical_care"] = "male"
        elif re.search(
            r"(?:^|[\s,])(여성|여자)(?=$|[\s,]|이고|이며|입니다)",
            participant_segment,
        ):
            candidates["patient.sex_for_clinical_care"] = "female"

        condition_markers = (
            "진단받", "진단을받", "진단되어", "앓고", "기저질환",
            "만성질환", "치료중", "치료를받",
        )
        medication_markers = (
            "복용중", "복용하고", "복용함", "먹는약", "처방약",
            "투약중", "약을먹", "약복용",
        )
        condition_positions = [
            normalized.find(marker)
            for marker in condition_markers
            if normalized.find(marker) >= 0
        ]
        medication_positions = [
            normalized.find(marker)
            for marker in medication_markers
            if normalized.find(marker) >= 0
        ]
        normalized_family_positions = [
            normalized.find(_normalized(term))
            for term in (*FAMILY_RELATIONSHIP_TERMS, *EXTENDED_FAMILY_CONTEXT_TERMS)
            if normalized.find(_normalized(term)) >= 0
        ]
        normalized_family_position = (
            min(normalized_family_positions)
            if normalized_family_positions else len(normalized)
        )
        participant_condition = bool(condition_positions) and (
            not family_context
            or (self_context and min(condition_positions) < normalized_family_position)
        )
        participant_medication = bool(medication_positions) and (
            not family_context
            or (self_context and min(medication_positions) < normalized_family_position)
        )
        if participant_condition:
            candidates["history.condition.current"] = text.strip()
        if participant_medication:
            candidates["medication.current"] = text.strip()
        if "알레르기" in participant_normalized and any(
            marker in participant_normalized for marker in ("있", "없", "반응", "알러지")
        ):
            candidates["allergy.current"] = text.strip()

    if family_context:
        candidates["history.family"] = text.strip()
        if family_relationship is not None:
            candidates["history.family.relationship"] = family_relationship
        if "암" in normalized:
            candidates["history.cancer.family"] = text.strip()

    # Preserve an explicit symptom statement in the existing screening Fact
    # while retaining each more specific compiled symptom Fact as well.
    symptom_values = [
        value
        for fact_id, value in candidates.items()
        if fact_id.startswith("symptom.")
        and value is not False
        and value is not None
        and value != "none"
    ]
    if symptom_values and not family_only_context:
        candidates["screening.current_symptom"] = text.strip()

    allowed = _compiled_question_catalog()["compiled_fact_ids"]
    return {
        fact_id: value
        for fact_id, value in candidates.items()
        if fact_id in allowed
    }


def _labels_from_numbered_wording(
    wording: str, answer_code_map: dict[str, str]
) -> tuple[tuple[str, str], ...]:
    labels: list[tuple[str, str]] = []
    positions = list(re.finditer(r"(?:^|[,.?]\s*)?(\d+)\s+", wording))
    for index, match in enumerate(positions):
        number = match.group(1)
        if number not in answer_code_map:
            continue
        end = positions[index + 1].start() if index + 1 < len(positions) else len(wording)
        label = wording[match.end():end].strip(" ,.?·")
        if label:
            labels.append((str(answer_code_map[number]), label))
    return tuple(labels)


def _knowledge_question(
    fact_id: str,
    *,
    question_id: str | None = None,
    template_id: str | None = None,
) -> dict[str, Any]:
    catalog = _compiled_question_catalog()
    if template_id:
        authored = catalog["clinician_by_id"][template_id]
        wording = str(authored["wording"])
        options = _labels_from_numbered_wording(
            wording, authored.get("answer_code_map", {})
        )
        question = _question(fact_id, wording, options)
        question.update({
            "template_id": authored["template_id"],
            "knowledge_source_id": catalog["clinician_document_id"],
            "source": "compiled_knowledge",
            "source_kind": "reused_compiled_question_template",
            "allow_free_text": authored.get("accept_free_text", True),
        })
        return question

    if question_id:
        authored = catalog["screening_by_id"][question_id]
    else:
        authored = catalog["screening_by_fact"][fact_id][0]
    text = authored.get("text", {})
    wording = text.get("ko") if isinstance(text, dict) else text
    question = _question(fact_id, str(wording))
    question.update({
        "template_id": authored["id"],
        "knowledge_source_id": catalog["screening_document_id"],
        "question_group_id": authored.get("group_id"),
        "source": "compiled_knowledge",
        "source_kind": "reused_compiled_question",
        "allow_free_text": authored.get("accept_free_text", True),
    })
    return question


INITIAL_CONCERN_QUESTION = _knowledge_question(
    "screening.additional_concern",
    question_id="kr.nhis.general.common.additional_concern",
)


@dataclass
class ScreeningRecommendationSession:
    session_id: str
    catalog_root: Path = CATALOG_ROOT
    answers: dict[str, Any] = field(default_factory=dict)
    question_queue: list[dict[str, Any]] = field(default_factory=list)
    question_cursor: int = 0
    latest_question: dict[str, Any] | None = None
    recommendation: dict[str, Any] | None = None
    uploaded_health_contexts: list[str] = field(default_factory=list)
    inferred_fact_ids: set[str] = field(default_factory=set)
    reused_fact_sources: dict[str, set[str]] = field(default_factory=dict)
    inferred_focus_from_concern: str | None = None
    closed: bool = False

    def __post_init__(self) -> None:
        self._append_questions([deepcopy(INITIAL_CONCERN_QUESTION)])
        self.latest_question = deepcopy(self.question_queue[0])

    def add_uploaded_health_context(self, text: str) -> None:
        """Add locally extracted text without treating it as a questionnaire answer."""
        self._ensure_open()
        if self.recommendation is not None:
            raise RuntimeError("screening recommendation is already ready")
        normalized = text.strip()
        if not normalized:
            return
        if len(self.uploaded_health_contexts) >= 5:
            raise ValueError("uploaded health context limit has been reached")
        self.uploaded_health_contexts.append(normalized[:20_000])
        self._capture_reusable_facts_from_text(
            normalized[:20_000], source_kind="uploaded_health_context"
        )

    def process(self, message: str) -> dict[str, Any]:
        self._ensure_open()
        answer = message.strip()
        if not answer:
            raise ValueError("screening recommendation answer must not be empty")
        if self.recommendation is not None:
            return self._state(status="recommendation_ready", phase="recommendation")

        if self.latest_question is None:
            raise RuntimeError("screening recommendation has no pending question")
        current = self.latest_question
        if current["fact_id"] == "screening.region":
            region = self._resolve_region(answer)
            if region is None:
                self.latest_question = deepcopy(current)
                return self._state(status="in-progress", phase="questioning")
            self.answers["screening.region"] = region
        else:
            self.answers[current["fact_id"]] = self._resolve_fact_answer(current, answer)
        self._capture_reusable_facts_from_text(
            answer, source_kind="question_answer"
        )
        self._extend_questionnaire_after(current)
        self.question_cursor += 1

        if self.question_cursor >= len(self.question_queue):
            self.latest_question = None
            self.recommendation = self._build_recommendation()
            return self._state(status="recommendation_ready", phase="recommendation")

        self.latest_question = deepcopy(self.question_queue[self.question_cursor])
        return self._state(status="in-progress", phase="questioning")

    def result(self) -> dict[str, Any]:
        self._ensure_open()
        return {
            "status": "recommendation_ready" if self.recommendation else "in_progress",
            "answers": deepcopy(self.answers),
            "recommendation": deepcopy(self.recommendation),
            "response_storage": "memory_only",
        }

    def close(self) -> dict[str, Any]:
        self.answers.clear()
        self.uploaded_health_contexts.clear()
        self.inferred_fact_ids.clear()
        self.reused_fact_sources.clear()
        self.inferred_focus_from_concern = None
        self.question_queue.clear()
        self.latest_question = None
        self.recommendation = None
        self.closed = True
        return {"status": "closed", "response_state_purged": True}

    def _state(self, *, status: str, phase: str) -> dict[str, Any]:
        return {
            "runtime": "screening_recommendation_workflow",
            "status": status,
            "phase": phase,
            "selected_question": deepcopy(self.latest_question),
            "recommendation": deepcopy(self.recommendation),
            "answers_collected": sum(
                item["fact_id"] in self.answers
                for item in self.question_queue[:self.question_cursor]
            ),
            "response_storage": "memory_only",
        }

    def _append_questions(self, questions: list[dict[str, Any]]) -> None:
        existing = {item["fact_id"] for item in self.question_queue}
        for question in questions:
            fact_id = question["fact_id"]
            source = question.get("source")
            if source == "screening_recommendation_workflow":
                if fact_id not in OPERATIONAL_FACT_IDS:
                    raise RuntimeError(
                        f"non-operational screening question is prohibited: {fact_id}"
                    )
            elif source == "compiled_knowledge":
                if fact_id not in _compiled_question_catalog()["compiled_fact_ids"]:
                    raise RuntimeError(
                        f"question Fact is absent from compiled Knowledge: {fact_id}"
                    )
            else:
                raise RuntimeError(f"unsupported screening question source: {source}")
            if question["fact_id"] in existing or question["fact_id"] in self.answers:
                continue
            authored = deepcopy(question)
            authored["question_ref"] = f"Q{len(self.question_queue) + 1}"
            self.question_queue.append(authored)
            existing.add(authored["fact_id"])

    def _extend_questionnaire_after(self, current: dict[str, Any]) -> None:
        fact_id = current["fact_id"]
        if fact_id == "screening.additional_concern":
            concern = self.answers[fact_id]
            self._append_questions(self._concern_questions(concern))
            inferred_focus = self._infer_focus_from_concern(concern)
            if inferred_focus is None:
                self._append_questions([deepcopy(OPERATIONAL_QUESTIONS[0])])
            else:
                self.inferred_focus_from_concern = inferred_focus
                self._append_questions([
                    self._personalized_focus_question(inferred_focus)
                ])
            return
        if fact_id == "screening.focus":
            focus = self.answers[fact_id]
            self._append_questions(self._focus_questions(focus))
            self._append_questions([deepcopy(item) for item in OPERATIONAL_QUESTIONS[1:]])

    @staticmethod
    def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
        normalized = _normalized(text)
        return any(_normalized(term) in normalized for term in terms)

    def _concern_questions(self, concern: str) -> list[dict[str, Any]]:
        # Chatbot-test screening selection uses age, sex-related context, and
        # reported risks before choosing a candidate group. Reuse the existing
        # clinician-context questions and let ``_append_questions`` suppress
        # either one when the opening or an upload already supplied its Fact.
        questions = (
            self._sex_and_age_questions()
            if self._contains_any(concern, SEX_RELEVANT_SCREENING_TERMS)
            else self._age_and_sex_questions()
        )
        normalized_concern = _normalized(concern)
        if "암" in normalized_concern and self._contains_any(
            concern,
            tuple(FAMILY_RELATIONSHIP_TERMS) + EXTENDED_FAMILY_CONTEXT_TERMS,
        ):
            questions.append(_knowledge_question(
                "history.cancer.family",
                question_id="kr.nhis.cancer.common.family_history",
            ))
        elif self._contains_any(concern, ("가족력", "유전", "가족 질환")):
            questions.append(_knowledge_question(
                "history.family", template_id="question.clinician-context.family-history"
            ))
        if self._contains_any(concern, ("만성질환", "기저질환", "진단받", "치료받")):
            questions.append(_knowledge_question(
                "history.condition.current",
                question_id="kr.nhis.general.common.medical_history",
            ))
        if self._contains_any(concern, ("복용약", "먹는 약", "약물", "처방약")):
            questions.append(_knowledge_question(
                "medication.current",
                question_id="kr.nhis.general.common.medication",
            ))
        if self._contains_any(concern, ("흡연", "담배", "폐", "호흡기")):
            questions.append(_knowledge_question(
                "patient.smoking.status",
                template_id="question.clinician-context.smoking-status",
            ))
        return questions

    def _capture_reusable_facts_from_text(
        self, text: str, *, source_kind: str
    ) -> None:
        """Reuse explicit compiled Facts from any local in-session input."""
        current_fact_ids = set(self.answers)
        for fact_id, value in _explicit_existing_fact_candidates(text).items():
            if fact_id in OPERATIONAL_FACT_IDS:
                continue
            self.answers.setdefault(fact_id, value)
            if fact_id not in current_fact_ids:
                self.inferred_fact_ids.add(fact_id)
                self.reused_fact_sources.setdefault(fact_id, set()).add(source_kind)

    def _infer_focus_from_concern(self, concern: str) -> str | None:
        mappings: tuple[tuple[str, tuple[str, ...]], ...] = (
            ("cardiovascular", (
                "뇌출혈", "지주막하출혈", "sah", "뇌동맥류", "뇌졸중",
                "중풍", "심근경색", "협심증", "심혈관", "심장", "뇌혈관",
            )),
            ("cancer", ("암", "종양", "악성")),
            ("digestive", (
                "위암", "대장암", "위장", "대장", "소화기", "내시경",
                "복통", "혈변",
            )),
            ("lung", ("폐암", "폐", "호흡기", "기침", "숨참", "흡연", "담배")),
            ("women", ("유방", "자궁", "난소", "부인과", "여성검진")),
            ("men", ("전립선", "남성검진")),
            ("senior", ("고령", "노년", "노인", "시니어")),
        )
        for focus, terms in mappings:
            if self._contains_any(concern, terms):
                return focus
        return None

    @staticmethod
    def _personalized_focus_question(focus: str) -> dict[str, Any]:
        question = deepcopy(OPERATIONAL_QUESTIONS[0])
        options = question["answer_options"]
        preferred = [item for item in options if item["internal_value"] == focus]
        ordered_options = preferred + [
            item for item in options if item["internal_value"] != focus
        ]
        # The preferred option moves to the top, so its visible shortcut must
        # also be 1. Keeping the old input tokens made the first button start at
        # 2 and diverged from the Chatbot-test one-question contract.
        question["answer_options"] = [
            {**item, "input": str(index)}
            for index, item in enumerate(ordered_options, 1)
        ]
        label = preferred[0]["display_ko"] if preferred else "선택한"
        text = (
            f"말씀하신 내용은 {label} 영역과 관련해 비교할 수 있습니다. "
            "이 영역을 우선할까요? 다른 영역을 선택할 수도 있습니다."
        )
        question["text"] = text
        question["stem_text"] = text
        question["suggested_from_concern"] = focus
        return question

    @staticmethod
    def _age_and_sex_questions() -> list[dict[str, Any]]:
        return [
            _knowledge_question(
                "patient.age_years", template_id="question.clinician-context.age"
            ),
            _knowledge_question(
                "patient.sex_for_clinical_care",
                template_id="question.clinician-context.sex",
            ),
        ]

    @staticmethod
    def _sex_and_age_questions() -> list[dict[str, Any]]:
        return [
            _knowledge_question(
                "patient.sex_for_clinical_care",
                template_id="question.clinician-context.sex",
            ),
            _knowledge_question(
                "patient.age_years", template_id="question.clinician-context.age"
            ),
        ]

    def _focus_questions(self, focus: str) -> list[dict[str, Any]]:
        questions = self._age_and_sex_questions()
        if focus in {"basic", "precision", "unsure"}:
            questions.extend([
                _knowledge_question(
                    "history.condition.current",
                    question_id="kr.nhis.general.common.medical_history",
                ),
                _knowledge_question(
                    "medication.current",
                    question_id="kr.nhis.general.common.medication",
                ),
                _knowledge_question(
                    "history.family",
                    template_id="question.clinician-context.family-history",
                ),
            ])
        elif focus == "cancer":
            questions.extend([
                _knowledge_question(
                    "screening.current_symptom",
                    question_id="kr.nhis.cancer.common.current_symptom",
                ),
                _knowledge_question(
                    "history.cancer.family",
                    question_id="kr.nhis.cancer.common.family_history",
                ),
            ])
        elif focus == "cardiovascular":
            questions.extend([
                _knowledge_question(
                    "history.condition.current",
                    question_id="kr.nhis.general.common.medical_history",
                ),
                _knowledge_question(
                    "medication.current",
                    question_id="kr.nhis.general.common.medication",
                ),
                _knowledge_question(
                    "history.family",
                    template_id="question.clinician-context.family-history",
                ),
                _knowledge_question(
                    "patient.smoking.status",
                    template_id="question.clinician-context.smoking-status",
                ),
            ])
        elif focus == "digestive":
            questions.extend([
                _knowledge_question(
                    "history.condition.current",
                    question_id="kr.nhis.general.common.medical_history",
                ),
                _knowledge_question(
                    "history.cancer.family",
                    question_id="kr.nhis.cancer.common.family_history",
                ),
            ])
            age = self._age_years()
            if age is not None and age >= 40:
                questions.extend([
                    _knowledge_question(
                        "screening.gastric.last_test",
                        question_id="kr.nhis.cancer.gastric.last_test",
                    ),
                    _knowledge_question(
                        "screening.gastric.last_result",
                        question_id="kr.nhis.cancer.gastric.last_result",
                    ),
                ])
            if age is not None and age >= 50:
                questions.extend([
                    _knowledge_question(
                        "screening.colorectal.last_test",
                        question_id="kr.nhis.cancer.colorectal.last_test",
                    ),
                    _knowledge_question(
                        "screening.colorectal.last_result",
                        question_id="kr.nhis.cancer.colorectal.last_result",
                    ),
                ])
        elif focus == "lung":
            questions.extend([
                _knowledge_question(
                    "patient.smoking.status",
                    template_id="question.clinician-context.smoking-status",
                ),
                _knowledge_question(
                    "patient.smoking.pack_years",
                    question_id="kr.nhis.cancer.lung.pack_years",
                ),
                _knowledge_question(
                    "screening.current_symptom",
                    question_id="kr.nhis.cancer.common.current_symptom",
                ),
            ])
        elif focus == "women":
            questions.extend([
                _knowledge_question(
                    "screening.breast.last_mammography",
                    question_id="kr.nhis.cancer.breast.last_mammography",
                ),
                _knowledge_question(
                    "screening.cervical.last_cytology",
                    question_id="kr.nhis.cancer.cervical.last_cytology",
                ),
                _knowledge_question(
                    "history.condition.current",
                    question_id="kr.nhis.general.common.medical_history",
                ),
            ])
        elif focus == "men":
            questions.extend([
                _knowledge_question(
                    "history.condition.current",
                    question_id="kr.nhis.general.common.medical_history",
                ),
                _knowledge_question(
                    "history.family",
                    template_id="question.clinician-context.family-history",
                ),
                _knowledge_question(
                    "patient.smoking.status",
                    template_id="question.clinician-context.smoking-status",
                ),
            ])
        elif focus == "senior":
            questions.extend([
                _knowledge_question(
                    "history.condition.current",
                    question_id="kr.nhis.general.common.medical_history",
                ),
                _knowledge_question(
                    "medication.current",
                    question_id="kr.nhis.general.common.medication",
                ),
            ])
            if self._age_years() == 66:
                questions.extend([
                    _knowledge_question(
                        "screening.cognition.concern",
                        question_id="kr.nhis.general.age66.additional.cognition",
                    ),
                    _knowledge_question(
                        "screening.fall.last_year",
                        question_id="kr.nhis.general.age66.additional.fall",
                    ),
                ])
        return questions

    def _resolve_region(self, answer: str) -> str | None:
        normalized = _normalized(answer)
        for index, (code, display) in enumerate(REGIONS, 1):
            if normalized in {str(index), _normalized(code), _normalized(display)}:
                return code
        return None

    @staticmethod
    def _resolve_answer(question: dict[str, Any], answer: str) -> str:
        normalized = _normalized(answer)
        for option in question.get("answer_options", []):
            if normalized in {
                _normalized(option["input"]),
                _normalized(option["display_ko"]),
                _normalized(option["internal_value"]),
            }:
                return str(option["internal_value"])
        return answer

    def _resolve_fact_answer(self, question: dict[str, Any], answer: str) -> str:
        resolved = self._resolve_answer(question, answer)
        if question["fact_id"] == "patient.age_years":
            match = re.search(r"(?<!\d)(\d{1,3})(?!\d)", resolved)
            if match and 0 <= int(match.group(1)) <= 120:
                return match.group(1)
        return resolved

    def _age_years(self) -> int | None:
        raw = self.answers.get("patient.age_years", "")
        if isinstance(raw, int) and 0 <= raw <= 120:
            return raw
        return (
            int(raw)
            if isinstance(raw, str) and raw.isdigit() and 0 <= int(raw) <= 120
            else None
        )

    @staticmethod
    def _profile_catalog_score(
        summary: dict[str, Any], age: int | None, sex: str | None
    ) -> tuple[int, list[str]]:
        target = " ".join(str(item) for item in summary.get("target_texts", []))
        name = str(summary.get("package_name", ""))
        combined = f"{target} {name}"
        score = 0
        reasons: list[str] = []

        if sex in {"female", "male"}:
            female_marked = "여성" in combined
            male_marked = "남성" in combined
            if sex == "female" and female_marked:
                score += 2
                reasons.append("표기 대상의 여성 조건과 일치")
            elif sex == "male" and male_marked:
                score += 2
                reasons.append("표기 대상의 남성 조건과 일치")
            elif female_marked != male_marked:
                score -= 4

        if age is not None:
            matched_age = False
            for upper in re.findall(r"(\d{1,3})세\s*이하", combined):
                matched_age = matched_age or age <= int(upper)
            for lower in re.findall(r"(\d{1,3})세\s*이상", combined):
                matched_age = matched_age or age >= int(lower)
            for low, high in re.findall(r"(\d{1,3})\s*[-~]\s*(\d{1,3})세", combined):
                matched_age = matched_age or int(low) <= age <= int(high)
            for low, high in re.findall(r"(\d)0\s*[-~]\s*(\d)0대", combined):
                matched_age = matched_age or int(low) * 10 <= age <= int(high) * 10 + 9
            if matched_age:
                score += 3
                reasons.append("표기 연령 조건과 일치")
        return score, reasons

    def _build_recommendation(self) -> dict[str, Any]:
        registry_path = self.catalog_root / "registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        version = registry.get("current_version")
        if not isinstance(version, str) or not version:
            return self._blocked("current catalog version is unavailable")
        version_root = self.catalog_root / "versions" / version
        metadata_path = version_root / "metadata.json"
        if not metadata_path.is_file():
            return self._blocked("current catalog metadata is unavailable")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        region_id = self.answers["screening.region"]
        region = next(
            (item for item in metadata.get("regions", []) if item.get("id") == region_id),
            None,
        )
        if region is None:
            return self._blocked("selected catalog region is unavailable")

        summaries: list[dict[str, Any]] = []
        region_root = version_root / "regions" / region_id
        index = json.loads((region_root / "index.json").read_text(encoding="utf-8"))
        for page in index.get("pages", []):
            page_number = page.get("page")
            if not isinstance(page_number, int):
                continue
            document = json.loads(
                (region_root / "pages" / f"{page_number}.json").read_text(encoding="utf-8")
            )
            summaries.extend(document.get("packages", []))

        focus = self.answers.get("screening.focus", "unsure")
        focus_tokens = next(
            (tokens for code, _, tokens in FOCUS_OPTIONS if code == focus),
            (),
        )
        clinical_answer_texts = [
            str(value)
            for fact_id, value in self.answers.items()
            if fact_id not in {
                "screening.focus",
                "screening.region",
                "screening.budget_preference",
                "screening.nhis_questionnaire_choice",
                "patient.sex_for_clinical_care",
            }
        ]
        combined_concern = " ".join([
            *clinical_answer_texts,
            *self.uploaded_health_contexts,
        ])
        concern_tokens = tuple(dict.fromkeys(
            token for token in re.findall(r"[0-9a-z가-힣]+", combined_concern.casefold())
            if len(token) >= 2 and token not in {"없음", "모름", "잘모르겠음"}
        ))[:60]

        age = self._age_years()
        sex = self.answers.get("patient.sex_for_clinical_care")
        ranked: list[tuple[int, int, dict[str, Any], list[str]]] = []
        for summary in summaries:
            price = summary.get("price_summary", {}).get("minimum_krw")
            if not isinstance(price, int) or price < 0:
                continue
            haystack = _normalized(" ".join([
                str(summary.get("package_name", "")),
                str(summary.get("institution", "")),
                " ".join(str(item) for item in summary.get("lexical_tags", [])),
                " ".join(str(item) for item in summary.get("target_texts", [])),
            ]))
            focus_hits = sum(_normalized(token) in haystack for token in focus_tokens)
            concern_hits = sum(_normalized(token) in haystack for token in concern_tokens)
            score = 3 * focus_hits + 2 * concern_hits
            reasons: list[str] = []
            if focus_hits:
                reasons.append("선택한 비교 영역과 카탈로그 표기가 일치")
            if concern_hits:
                reasons.append("입력한 건강 관심 내용과 카탈로그 표기가 일치")
            profile_score, profile_reasons = self._profile_catalog_score(summary, age, sex)
            score += profile_score
            reasons.extend(profile_reasons)
            ranked.append((score, price, summary, reasons))
        if not ranked:
            return self._blocked("priced package candidates are unavailable")

        cheapest = min(ranked, key=lambda item: (item[1], item[2].get("package_name", "")))
        preference = self.answers.get("screening.budget_preference", "no_preference")
        if preference == "lowest":
            ordered = sorted(ranked, key=lambda item: (item[1], -item[0]))
        else:
            matched = [item for item in ranked if item[0] > 0]
            ordered = sorted(matched or ranked, key=lambda item: (-item[0], item[1]))
        selected = [cheapest, *ordered]
        deduplicated: list[tuple[int, int, dict[str, Any], list[str]]] = []
        seen: set[str] = set()
        for item in selected:
            package_id = str(item[2].get("package_id", ""))
            if not package_id or package_id in seen:
                continue
            seen.add(package_id)
            deduplicated.append(item)
            if len(deduplicated) == 4:
                break

        candidates = [
            self._candidate_detail(
                version_root, score, price, summary, summary is cheapest[2], reasons
            )
            for score, price, summary, reasons in deduplicated
        ]
        nhis_choice = self.answers.get("screening.nhis_questionnaire_choice", "not_now")
        result = {
            "status": "candidate_comparison_ready",
            "catalog_id": registry.get("catalog_id"),
            "catalog_version": version,
            "region": deepcopy(region),
            "selection_basis": {
                "focus": focus,
                "concern_terms_used_locally": list(concern_tokens),
                "reused_fact_ids": sorted(
                    fact_id
                    for fact_id in self.answers
                    if fact_id not in {
                        "screening.focus",
                        "screening.region",
                        "screening.budget_preference",
                        "screening.nhis_questionnaire_choice",
                    }
                ),
                "knowledge_sources": sorted({
                    item["knowledge_source_id"]
                    for item in self.question_queue
                    if item.get("knowledge_source_id")
                }),
                "age_used_locally": age is not None,
                "sex_context_used_locally": sex in {"female", "male"},
                "adaptive_question_count": sum(
                    item.get("source") == "compiled_knowledge"
                    for item in self.question_queue
                ),
                "inferred_fact_ids": sorted(self.inferred_fact_ids),
                "reused_fact_sources": {
                    fact_id: sorted(sources)
                    for fact_id, sources in sorted(self.reused_fact_sources.items())
                },
                "focus_suggested_from_concern": self.inferred_focus_from_concern,
                "uploaded_text_context_count": len(self.uploaded_health_contexts),
                "budget_preference": preference,
                "lowest_price_candidate_always_included": True,
                "medical_necessity_inferred": False,
                "patient_profile_transmitted_to_catalog_action": False,
            },
            "official_nhis_questionnaire": {
                "choice": nhis_choice,
                "separate_questionnaire_response_required": True,
                "next_step": (
                    "정형 대화의 국민건강검진 문진(시험용)에서 별도로 작성하세요."
                    if nhis_choice == "after" else None
                ),
            },
            "candidates": candidates,
            "limitations_ko": (
                "시험용·미검토 공개 카탈로그의 비교 후보입니다. 국가검진과의 항목 중복, "
                "의학적 필요성, 실제 가격·구성·대상·예약 가능 여부는 자동 확정하지 않으며 "
                "선택 전 해당 기관에 직접 확인해야 합니다."
            ),
        }
        result["summary_ko"] = self._summary(result)
        return result

    def _candidate_detail(
        self,
        version_root: Path,
        score: int,
        price: int,
        summary: dict[str, Any],
        is_lowest: bool,
        match_reasons: list[str],
    ) -> dict[str, Any]:
        detail_path = version_root / "packages" / f"{summary['package_id']}.json"
        detail = json.loads(detail_path.read_text(encoding="utf-8"))
        variants = detail.get("variants", [])
        first = variants[0] if variants else {}
        urls = detail.get("source", {}).get("urls", [])
        return {
            "package_id": summary.get("package_id"),
            "institution": summary.get("institution"),
            "package_name": summary.get("package_name"),
            "minimum_price_krw": price,
            "price_raw": first.get("price", {}).get("raw"),
            "items_text": first.get("items_text"),
            "source_url": urls[0] if urls else None,
            "match_score": score,
            "match_reasons": match_reasons or ["가격 비교 후보"],
            "lowest_price_candidate": is_lowest,
            "listing_statuses": deepcopy(summary.get("listing_statuses", [])),
        }

    @staticmethod
    def _summary(result: dict[str, Any]) -> str:
        lines = [
            f"{result['region']['display_ko']} 지역 추가 검진 패키지 비교 후보입니다.",
            "가장 저렴한 확인 가능 후보를 포함했으며, 현재 카탈로그의 표기만 비교했습니다.",
        ]
        for index, candidate in enumerate(result["candidates"], 1):
            marker = " · 지역 내 최저가 확인 후보" if candidate["lowest_price_candidate"] else ""
            price = f"{candidate['minimum_price_krw']:,}원부터"
            lines.append(
                f"{index}. {candidate['institution']} · {candidate['package_name']} · {price}{marker}"
            )
            if candidate.get("items_text"):
                lines.append(f"   주요 표기 항목: {candidate['items_text']}")
            if candidate.get("match_reasons"):
                lines.append(f"   비교 근거: {', '.join(candidate['match_reasons'])}")
            if candidate.get("source_url"):
                lines.append(f"   확인: {candidate['source_url']}")
        lines.append(result["limitations_ko"])
        next_step = result["official_nhis_questionnaire"].get("next_step")
        if next_step:
            lines.append(next_step)
        return "\n".join(lines)

    @staticmethod
    def _blocked(reason: str) -> dict[str, Any]:
        return {
            "status": "recommendation_blocked",
            "reason": reason,
            "candidates": [],
            "summary_ko": (
                "현재 버전의 시험용 검진센터 카탈로그를 확인할 수 없어 패키지 후보를 "
                "만들지 않았습니다. 카탈로그가 복구된 뒤 다시 시도해 주세요."
            ),
        }

    def _ensure_open(self) -> None:
        if self.closed:
            raise RuntimeError("screening recommendation session is closed")
