"""Ephemeral health-screening add-on package comparison workflow.

The source catalog is isolated test data, not Clinical Knowledge.  This
adapter performs deterministic local navigation over the current immutable
catalog version.  It never sends participant answers to a catalog Action and
never claims medical necessity, diagnosis, or current availability.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any


CATALOG_ROOT = (
    Path(__file__).resolve().parents[1]
    / "docs/gpt/test-catalogs/health-screening-packages"
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


def _normalized(value: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]+", "", value.casefold())


def _question(
    number: int,
    fact_id: str,
    text: str,
    options: tuple[tuple[str, str], ...] = (),
) -> dict[str, Any]:
    return {
        "question_ref": f"Q{number}",
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
    }


QUESTIONS = (
    _question(
        1,
        "screening.region",
        "추가 검진 패키지를 비교할 지역은 어디인가요?",
        REGIONS,
    ),
    _question(
        2,
        "screening.focus",
        "추가 검진에서 우선 비교하고 싶은 영역은 무엇인가요?",
        tuple((code, label) for code, label, _ in FOCUS_OPTIONS),
    ),
    _question(
        3,
        "screening.concern",
        "최근 이상 소견, 가족력 또는 특별히 확인하고 싶은 건강 문제가 있나요?",
    ),
    _question(
        4,
        "screening.budget_preference",
        "가격은 어떻게 비교할까요? 경제능력은 추정하지 않으며 선택하지 않아도 됩니다.",
        BUDGET_OPTIONS,
    ),
    _question(
        5,
        "screening.nhis_questionnaire_choice",
        "국가건강검진 문진은 어떻게 할까요? 패키지 비교의 필수 조건은 아닙니다.",
        NHIS_OPTIONS,
    ),
)


@dataclass
class ScreeningRecommendationSession:
    session_id: str
    catalog_root: Path = CATALOG_ROOT
    answers: dict[str, str] = field(default_factory=dict)
    next_question_index: int = 0
    latest_question: dict[str, Any] | None = None
    recommendation: dict[str, Any] | None = None
    closed: bool = False

    def process(self, message: str) -> dict[str, Any]:
        self._ensure_open()
        answer = message.strip()
        if not answer:
            raise ValueError("screening recommendation answer must not be empty")
        if self.recommendation is not None:
            return self._state(status="recommendation_ready", phase="recommendation")

        if self.next_question_index == 0:
            region = self._resolve_region(answer)
            if region is None:
                self.latest_question = deepcopy(QUESTIONS[0])
                return self._state(status="in-progress", phase="questioning")
            self.answers["screening.region"] = region
            self.next_question_index = 1
        else:
            current = QUESTIONS[self.next_question_index]
            self.answers[current["fact_id"]] = self._resolve_answer(current, answer)
            self.next_question_index += 1

        if self.next_question_index >= len(QUESTIONS):
            self.latest_question = None
            self.recommendation = self._build_recommendation()
            return self._state(status="recommendation_ready", phase="recommendation")

        self.latest_question = deepcopy(QUESTIONS[self.next_question_index])
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
            "answers_collected": len(self.answers),
            "response_storage": "memory_only",
        }

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
        concern_tokens = tuple(
            token for token in re.findall(r"[0-9a-z가-힣]+", self.answers.get("screening.concern", "").casefold())
            if len(token) >= 2 and token not in {"없음", "모름", "잘모르겠음"}
        )

        ranked: list[tuple[int, int, dict[str, Any]]] = []
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
            score = 3 * sum(_normalized(token) in haystack for token in focus_tokens)
            score += 2 * sum(_normalized(token) in haystack for token in concern_tokens)
            ranked.append((score, price, summary))
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
        deduplicated: list[tuple[int, int, dict[str, Any]]] = []
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
            self._candidate_detail(version_root, score, price, summary, summary is cheapest[2])
            for score, price, summary in deduplicated
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
                "budget_preference": preference,
                "lowest_price_candidate_always_included": True,
                "medical_necessity_inferred": False,
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
