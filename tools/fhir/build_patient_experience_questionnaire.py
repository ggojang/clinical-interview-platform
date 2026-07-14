#!/usr/bin/env python3
"""Build the 2025 fifth Korean patient-experience survey as FHIR R4 Questionnaire."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "fhir/r4/questionnaires/kr-patient-experience-evaluation-5th-2025.json"
CANONICAL = "https://ggojang.github.io/clinical-interview-platform/fhir"
QUESTION_SYSTEM = f"{CANONICAL}/CodeSystem/kr-patient-experience-question"
ANSWER_SYSTEM = f"{CANONICAL}/CodeSystem/kr-patient-experience-answer"
SECTION_SYSTEM = f"{CANONICAL}/CodeSystem/kr-patient-experience-section"


LIKERT = [
    ("1", "전혀 그렇지 않았다"),
    ("2", "그렇지 않았다"),
    ("3", "그랬다"),
    ("4", "항상 그랬다"),
]


def options(values: list[tuple[str, str]]) -> list[dict[str, Any]]:
    return [
        {"valueCoding": {"system": ANSWER_SYSTEM, "code": code, "display": display}}
        for code, display in values
    ]


def choice(number: int, text: str, values: list[tuple[str, str]] = LIKERT) -> dict[str, Any]:
    return {
        "linkId": f"q{number:02d}",
        "code": [{"system": QUESTION_SYSTEM, "code": f"Q{number:02d}", "display": text}],
        "prefix": f"문{number})",
        "text": text,
        "type": "choice",
        "required": False,
        "repeats": False,
        "answerOption": options(values),
    }


def score(number: int, text: str) -> dict[str, Any]:
    return {
        "linkId": f"q{number:02d}",
        "extension": [
            {"url": "http://hl7.org/fhir/StructureDefinition/minValue", "valueInteger": 0},
            {"url": "http://hl7.org/fhir/StructureDefinition/maxValue", "valueInteger": 10},
        ],
        "code": [{"system": QUESTION_SYSTEM, "code": f"Q{number:02d}", "display": text}],
        "prefix": f"문{number})",
        "text": text,
        "type": "integer",
        "required": False,
        "repeats": False,
    }


def group(number: int, title: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    roman = {1: "Ⅰ", 2: "Ⅱ", 3: "Ⅲ", 4: "Ⅳ", 5: "Ⅴ", 6: "Ⅵ", 7: "Ⅶ", 8: "Ⅷ"}
    return {
        "linkId": f"section-{number}",
        "code": [{"system": SECTION_SYSTEM, "code": f"S{number}", "display": title}],
        "prefix": f"{roman[number]}.",
        "text": title,
        "type": "group",
        "repeats": False,
        "item": items,
    }


def build() -> dict[str, Any]:
    q11 = LIKERT + [("0", "해당 없음 (통증이 없었다)")]
    q12 = LIKERT[:3] + [("4", "매우 그랬다")]
    q19 = LIKERT + [("0", "해당 없음 (불만이 없었다)")]
    q21 = LIKERT + [("0", "해당 없음 (신체노출 등의 상황이 없었다)")]
    document: dict[str, Any] = {
        "resourceType": "Questionnaire",
        "id": "kr-patient-experience-evaluation-5th-2025",
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/Questionnaire"],
            "tag": [
                {"system": f"{CANONICAL}/CodeSystem/content-status", "code": "research-only", "display": "Research only"},
                {"system": f"{CANONICAL}/CodeSystem/review-status", "code": "unreviewed", "display": "Unreviewed"},
            ],
        },
        "language": "ko-KR",
        "url": f"{CANONICAL}/Questionnaire/kr-patient-experience-evaluation-5th-2025",
        "identifier": [{"system": f"{CANONICAL}/identifier/questionnaire", "value": "KR-PEE-5-2025"}],
        "version": "5.0.0-draft",
        "name": "KrPatientExperienceEvaluation5th2025",
        "title": "2025년(5차) 환자경험평가 설문지",
        "status": "draft",
        "experimental": True,
        "subjectType": ["Patient"],
        "date": "2025-04",
        "publisher": "평가관리실 평가관리부",
        "description": "2025년(5차) 환자경험평가 세부시행계획 별첨의 입원 환자경험 평가도구 문항 1~26을 FHIR R4 Questionnaire로 구조화한 연구용 미검토 변환본.",
        "purpose": "원 설문 문항과 응답 코드를 보존하여 QuestionnaireResponse 수집, 결과 출력 및 후속 FHIR 변환 시험을 지원한다.",
        "copyright": "원문: 2025년(5차) 환자경험평가 세부시행계획, 별첨 환자경험 평가도구(설문지). 본 변환본은 unreviewed/research_only 상태이며 원 발행기관의 공식 FHIR 배포본이 아니다.",
        "jurisdiction": [{"coding": [{"system": "urn:iso:std:iso:3166", "code": "KR", "display": "Republic of Korea"}]}],
        "item": [
            group(1, "입원 중 간호사 영역", [
                choice(1, "담당 간호사는 귀하를 존중하고 예의를 갖추어 대하였습니까?"),
                choice(2, "담당 간호사는 귀하의 이야기를 주의 깊게 들어 주었습니까?"),
                choice(3, "담당 간호사는 병원생활에 대해 알기 쉽게 설명해 주었습니까?"),
                choice(4, "담당 간호사는 귀하가 도움을 필요로 할 때, 귀하의 요구를 처리하기 위하여 노력하였습니까?"),
            ]),
            group(2, "입원 중 의사 영역", [
                choice(5, "담당 의사는 귀하를 존중하고 예의를 갖추어 대하였습니까?"),
                choice(6, "담당 의사는 귀하의 이야기를 주의 깊게 들어 주었습니까?"),
                choice(7, "귀하나 보호자가 원할 때 담당 의사를 만나 이야기할 기회를 가지셨습니까?"),
                choice(8, "귀하는 담당 의사의 회진시간 또는 회진시간 변경에 대한 정보를 제공 받으셨습니까?"),
            ]),
            group(3, "투약 및 치료과정", [
                {"linkId": "section-3-note", "text": "투약·검사·처치 등 투약 및 치료과정에 관련된 모든 병원 직원(의사, 간호사, 약사, 방사선사, 임상병리사 등)에 대한 설문내용입니다.", "type": "display"},
                choice(9, "투약이나 검사, 처치 전에 그에 대한 이유를 알기 쉽게 설명해 주었습니까?"),
                choice(10, "투약이나 검사, 처치 후에 생길 수 있는 부작용에 대해 알기 쉽게 설명해 주었습니까?"),
                choice(11, "귀하의 통증을 줄이기 위하여 적절한 조치를 취하였습니까?", q11),
                choice(12, "퇴원 후 주의사항과 치료계획에 대한 정보를 적절히 제공받았습니까?", q12),
                choice(13, "귀하가 보기에 병원 부서 간(의사, 간호사, 검사실, 원무과 등)의 의사소통이 원활하게 이루어졌습니까?"),
            ]),
            group(4, "정서적 지지", [
                choice(14, "귀하의 질환에 대하여 의료진과 직원들로부터 위로와 공감을 받았습니까?"),
            ]),
            group(5, "환자 안전과 병원 환경", [
                choice(15, "투약, 검사, 수술 등을 시행할 때, 의료진과 직원은 환자 본인확인을 하였습니까?"),
                choice(16, "병원 환경은 안전하였습니까? (예: 안전손잡이, 실내등과 야간등의 밝기 등 낙상위험 방지, 소화기 등 화재예방)"),
                choice(17, "병실, 복도, 화장실 등 병원 내 시설은 깨끗하였습니까?"),
            ]),
            group(6, "환자권리보장", [
                choice(18, "귀하가 입원해 있을 때, 다른 환자들과 비교하여, 의료진과 직원들로부터 받은 대우가 공평하였습니까?"),
                choice(19, "입원 기간 동안 의료진과 직원에게 궁금한 내용을 말하거나 설명이 부족한 내용을 다시 물어보기가 쉬웠습니까?", q19),
                choice(20, "검사나 치료 방법의 결정 과정에서 귀하가 가지고 있는 질문이나 의견을 의료진과 직원이 고려해 주었습니까?"),
                choice(21, "귀하가 진료나 검사를 받을 때, 신체 노출 등으로 수치감을 느끼지 않을 수 있도록, 의료진과 직원이 배려하였습니까?", q21),
            ]),
            group(7, "전반적 평가", [
                score(22, "이 병원에서의 입원 경험을 0점에서 10점 사이의 점수로 평가한다면 몇 점을 주시겠습니까? (0점은 ‘가장 나쁜 경우’이고, 10점은 ‘가장 좋은 경우’입니다.)"),
                score(23, "만약 가족이나 친구 중에 입원할 일이 생긴다면, 이 병원을 이용하도록 추천하시겠습니까? (0점은 ‘절대로 추천 안함’이고, 10점은 ‘매우 추천하는 경우’입니다.)"),
            ]),
            group(8, "개인 특성", [
                choice(24, "귀하는 응급실을 통해 입원하셨습니까?", [("1", "예"), ("2", "아니오")]),
                choice(25, "현재 귀하의 건강은 어떻다고 생각하십니까?", [("1", "매우 좋다"), ("2", "좋다"), ("3", "보통이다"), ("4", "나쁘다"), ("5", "매우 나쁘다")]),
                choice(26, "귀하의 최종 학력은 어떻게 되십니까?", [("1", "중졸 이하"), ("2", "고졸"), ("3", "대학 재학"), ("4", "대학 졸업"), ("5", "대학원 재학 또는 졸업")]),
            ]),
        ],
    }
    return document


def validate(document: dict[str, Any]) -> None:
    if document.get("resourceType") != "Questionnaire" or document.get("status") not in {"draft", "active", "retired", "unknown"}:
        raise ValueError("invalid Questionnaire resourceType or status")
    identifiers: list[str] = []
    question_count = 0

    def walk(items: list[dict[str, Any]]) -> None:
        nonlocal question_count
        for item in items:
            link_id = item.get("linkId")
            if not link_id or link_id in identifiers:
                raise ValueError(f"missing or duplicate linkId: {link_id}")
            identifiers.append(link_id)
            item_type = item.get("type")
            children = item.get("item", [])
            if item_type == "group" and not children:
                raise ValueError(f"group without children: {link_id}")
            if item_type == "display" and (children or "code" in item or "required" in item or "repeats" in item):
                raise ValueError(f"invalid display item: {link_id}")
            if item_type == "choice":
                question_count += 1
                if not item.get("answerOption") or any("valueCoding" not in option for option in item["answerOption"]):
                    raise ValueError(f"choice without valueCoding options: {link_id}")
            elif item_type == "integer":
                question_count += 1
            walk(children)

    walk(document["item"])
    if question_count != 26:
        raise ValueError(f"expected 26 questions, found {question_count}")


def main() -> None:
    document = build()
    validate(document)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {OUTPUT.relative_to(ROOT)} with 8 sections and 26 questions")


if __name__ == "__main__":
    main()
