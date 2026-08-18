#!/usr/bin/env python3
"""Build source-defined Korean national health-screening Questionnaire drafts.

The wording, answer choices, and order follow the Ministry of Health and Welfare
health-screening forms.  The source is fixed, so this builder deliberately does
not infer clinical terminology mappings or scoring rules.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "fhir/r4/questionnaires"
CANONICAL = "https://ggojang.github.io/clinical-interview-platform/fhir/Questionnaire"
UNIT_URL = "http://hl7.org/fhir/StructureDefinition/questionnaire-unit"
UNIT_OPTION_URL = "http://hl7.org/fhir/StructureDefinition/questionnaire-unitOption"

FORM_1_SOURCE = (
    "https://www.law.go.kr/LSW/flDownload.do?bylClsCd=200203&"
    "flNm=%5B%EB%B3%84%EC%A7%80+1%5D+%EA%B1%B4%EA%B0%95%EA%B2%80%EC%A7%84+"
    "%EB%AC%B8%EC%A7%84%ED%91%9C&flSeq=148392179"
)
FORM_2_SOURCE = (
    "https://www.law.go.kr/LSW/flDownload.do?flNm=%5B%EB%B3%84%EC%A7%80+2%5D+"
    "%EA%B1%B4%EA%B0%95%EA%B2%80%EC%A7%84+%EC%B6%94%EA%B0%80+"
    "%EB%AC%B8%EC%A7%84%ED%91%9C&flSeq=136957935"
)


def option(value: str) -> dict:
    return {"valueString": value}


def display(link_id: str, text: str, prefix: str | None = None) -> dict:
    item = {"linkId": link_id, "text": text, "type": "display"}
    if prefix:
        item["prefix"] = prefix
    return item


def text_item(
    link_id: str,
    text: str,
    prefix: str | None = None,
    item_type: str = "string",
    required: bool = False,
    enable_when: list[dict] | None = None,
) -> dict:
    item = {
        "linkId": link_id,
        "text": text,
        "type": item_type,
        "required": required,
        "repeats": False,
    }
    if prefix:
        item["prefix"] = prefix
    if enable_when:
        item["enableWhen"] = enable_when
        item["enableBehavior"] = "all"
    return item


def choice(
    link_id: str,
    text: str,
    choices: list[str],
    prefix: str | None = None,
    required: bool = False,
    enable_when: list[dict] | None = None,
) -> dict:
    item = text_item(link_id, text, prefix, "choice", required, enable_when)
    item["answerOption"] = [option(value) for value in choices]
    return item


def group(
    link_id: str,
    text: str,
    items: list[dict],
    prefix: str | None = None,
    enable_when: list[dict] | None = None,
    enable_behavior: str = "all",
) -> dict:
    item = {"linkId": link_id, "text": text, "type": "group", "repeats": False, "item": items}
    if prefix:
        item["prefix"] = prefix
    if enable_when:
        item["enableWhen"] = enable_when
        item["enableBehavior"] = enable_behavior
    return item


def quantity(
    link_id: str,
    text: str,
    unit: str | None = None,
    units: list[str] | None = None,
    prefix: str | None = None,
    enable_when: list[dict] | None = None,
) -> dict:
    item = text_item(link_id, text, prefix, "quantity", enable_when=enable_when)
    extensions = []
    if unit:
        extensions.append({"url": UNIT_URL, "valueCoding": {"code": unit, "display": unit}})
    for candidate in units or []:
        extensions.append({"url": UNIT_OPTION_URL, "valueCoding": {"code": candidate, "display": candidate}})
    if extensions:
        item["extension"] = extensions
    return item


def enabled(question: str, answer: str) -> list[dict]:
    return [{"question": question, "operator": "=", "answerString": answer}]


def enabled_quantity_unless(question: str, value: float, unit: str) -> list[dict]:
    return [{
        "question": question,
        "operator": "!=",
        "answerQuantity": {"value": value, "unit": unit, "code": unit},
    }]


def metadata(resource_id: str, version: str, title: str, description: str, source: str) -> dict:
    return {
        "resourceType": "Questionnaire",
        "id": resource_id,
        "meta": {
            "profile": ["http://hl7.org/fhir/StructureDefinition/Questionnaire"],
            "tag": [
                {
                    "system": "https://ggojang.github.io/clinical-interview-platform/fhir/CodeSystem/content-status",
                    "code": "draft-limited-use",
                    "display": "Draft; limited use",
                },
                {
                    "system": "https://ggojang.github.io/clinical-interview-platform/fhir/CodeSystem/review-status",
                    "code": "unreviewed",
                    "display": "Unreviewed",
                },
                {
                    "system": "https://ggojang.github.io/clinical-interview-platform/fhir/CodeSystem/questionnaire-origin",
                    "code": "source-defined-fixed",
                    "display": "Source-defined fixed questionnaire",
                },
            ],
        },
        "language": "ko-KR",
        "url": f"{CANONICAL}/{resource_id}",
        "version": version,
        "status": "draft",
        "experimental": True,
        "subjectType": ["Patient"],
        "date": "2026-08-18",
        "publisher": "보건복지부 (연구용 FHIR 구조화: Clinical Interview AI Platform)",
        "title": title,
        "description": description,
        "purpose": "공식 서식의 문항·보기·순서를 보존하여 내부 대화형 입력 및 QuestionnaireResponse 생성 시험을 지원한다.",
        "copyright": "원문: 국가법령정보센터 건강검진 실시기준 별지 서식. 이 리소스는 미검토 연구용 구조화본이며 공식 FHIR 배포본이 아니다.",
        "derivedFrom": [source],
    }


def disease_history_items() -> list[dict]:
    diseases = [
        "뇌졸중(중풍)",
        "심근경색/협심증",
        "고혈압",
        "당뇨병",
        "이상지질혈증",
        "폐결핵",
        "우울증",
        "조기정신증",
        "C형간염",
        "기타(암포함)",
    ]
    rows = []
    for index, disease in enumerate(diseases, 1):
        rows.append(group(
            f"q1-row-{index}",
            disease,
            [
                choice(f"q1-{index}-diagnosis", f"{disease} — 진단", ["예", "아니요"]),
                choice(f"q1-{index}-medication", f"{disease} — 약물치료", ["예", "아니요"]),
            ],
        ))
    return rows


def family_history_items() -> list[dict]:
    diseases = ["뇌졸중(중풍)", "심근경색/협심증", "고혈압", "당뇨병", "기타(암포함)"]
    return [choice(f"q2-{index}", disease, ["예", "아니요"]) for index, disease in enumerate(diseases, 1)]


def smoking_current_details(prefix: str, selector: str, noun: str = "흡연") -> list[dict]:
    return [
        group(
            f"{prefix}-current",
            "현재 피움",
            [
                quantity(f"{prefix}-current-years", f"총 {noun}기간", "년"),
                quantity(f"{prefix}-current-daily", f"하루 평균 {noun}량", "개비"),
            ],
            enable_when=enabled(selector, "현재 피움"),
        ),
        group(
            f"{prefix}-former",
            "과거에는 피웠으나 현재 피우지 않음",
            [
                quantity(f"{prefix}-former-years", f"과거 총 {noun}기간", "년"),
                quantity(f"{prefix}-former-daily", f"{noun}했을 때 하루 평균 {noun}량", "개비"),
                quantity(f"{prefix}-quit-years", "끊은 지", "년"),
            ],
            enable_when=enabled(selector, "과거에는 피웠으나 현재 피우지 않음"),
        ),
    ]


def alcohol_amount_group(link_id: str, text: str, prefix: str) -> dict:
    beverage_types = ["소주", "맥주", "양주", "막걸리", "와인"]
    return group(
        link_id,
        text,
        [
            display(
                f"{link_id}-instruction",
                "잔 또는 병 또는 캔 또는 cc 중 한 곳에만 작성해 주십시오. (술 종류는 복수응답 가능, 하루에 마신 총 양으로 합산, 기타 술 종류는 비슷한 술 종류에 표기)",
            ),
            *[
                quantity(f"{link_id}-{index}", beverage, units=["잔", "병", "캔", "cc"])
                for index, beverage in enumerate(beverage_types, 1)
            ],
        ],
        prefix,
        [
            *enabled("q7-frequency", "일주일에 ( )번"),
            *enabled("q7-frequency", "한 달에 ( )번"),
            *enabled("q7-frequency", "1년에 ( )번"),
        ],
        "any",
    )


def form_1() -> dict:
    resource = metadata(
        "kr-national-health-screening-form-1-2025",
        "2025-01-01-draft",
        "건강검진 문진표",
        "건강검진 실시기준 [별지 제1호 서식] <개정 2025. 1. 1.>을 FHIR R4 Questionnaire로 구조화한 미검토 시험용 리소스.",
        FORM_1_SOURCE,
    )
    resource["name"] = "KrNationalHealthScreeningForm1_2025"
    resource["item"] = [
        display(
            "notice-cvd-risk",
            "검진대상자는 문진문항을 빠짐없이 작성하여야만 심뇌혈관질환 위험평가 결과를 통보 받으실 수 있습니다.",
        ),
        display("notice-current-state", "아래 문항을 읽고 자신의 현재 상태에 해당되는 내용을 작성하여 주십시오."),
        group(
            "respondent-information",
            "수검자 정보",
            [
                text_item("respondent-name", "수검자 성명"),
                text_item("resident-registration-number", "주민등록번호"),
                text_item("telephone-home", "전화번호(자택)"),
                text_item("telephone-mobile", "전화번호(핸드폰)"),
                text_item("address", "주소", item_type="text"),
                text_item("email", "E-mail"),
                choice("result-delivery-method", "결과통보 수령방법", ["우편", "E-mail", "모바일"]),
            ],
        ),
        group(
            "q1",
            "다음과 같은 질병으로 진단을 받았거나, 현재 약물 치료 중이십니까?",
            disease_history_items(),
            "1.",
        ),
        group(
            "q2",
            "부모, 형제, 자매 중에 다음 질환을 앓았거나 해당 질환으로 사망한 경우가 있으십니까?",
            family_history_items(),
            "2.",
        ),
        choice("q3", "B형간염 바이러스 보유자입니까?", ["예", "아니요", "모름"], "3."),
        choice(
            "q4-ever-cigarettes",
            "지금까지 평생 총 5갑(100개비) 이상의 일반담배(궐련)를 피운 적이 있습니까?",
            ["아니요", "예"],
            "4.",
        ),
        group(
            "q4-1",
            "현재 일반담배(궐련)를 피우십니까?",
            [
                choice(
                    "q4-1-status",
                    "현재 일반담배(궐련) 흡연 상태",
                    ["현재 피움", "과거에는 피웠으나 현재 피우지 않음"],
                ),
                *smoking_current_details("q4-1", "q4-1-status"),
            ],
            "4-1.",
            enabled("q4-ever-cigarettes", "예"),
        ),
        choice(
            "q5-ever-heated-tobacco",
            "지금까지 궐련형 전자담배(가열담배, 예: 아이코스, 글로, 릴 등)를 사용한 적 있습니까?",
            ["아니요", "예"],
            "5.",
        ),
        group(
            "q5-1",
            "현재 궐련형 전자담배(가열담배) 사용하십니까?",
            [
                choice(
                    "q5-1-status",
                    "현재 궐련형 전자담배 사용 상태",
                    ["현재 피움", "과거에는 피웠으나 현재 피우지 않음"],
                ),
                *smoking_current_details("q5-1", "q5-1-status", "담배사용"),
            ],
            "5-1.",
            enabled("q5-ever-heated-tobacco", "예"),
        ),
        choice(
            "q6-ever-liquid-ecigarette",
            "액상형 전자담배를 사용한 경험이 있습니까?",
            ["아니요", "예"],
            "6.",
        ),
        choice(
            "q6-1-recent-liquid-ecigarette",
            "최근 한 달 동안 액상형 전자담배를 사용한 경험이 있습니까?",
            ["아니요", "월 1-2일", "월 3-9일", "월 10-29일", "매일"],
            "6-1.",
            enable_when=enabled("q6-ever-liquid-ecigarette", "예"),
        ),
        choice(
            "q7-frequency",
            "술을 마시는 횟수는 어느 정도입니까? (1개만 응답)",
            ["일주일에 ( )번", "한 달에 ( )번", "1년에 ( )번", "술을 마시지 않는다."],
            "7.",
        ),
        quantity("q7-count-week", "일주일에 마신 횟수", "회", enable_when=enabled("q7-frequency", "일주일에 ( )번")),
        quantity("q7-count-month", "한 달에 마신 횟수", "회", enable_when=enabled("q7-frequency", "한 달에 ( )번")),
        quantity("q7-count-year", "1년에 마신 횟수", "회", enable_when=enabled("q7-frequency", "1년에 ( )번")),
        alcohol_amount_group("q7-1-usual", "술을 마시는 날은 보통 어느 정도 마십니까?", "7-1."),
        alcohol_amount_group("q7-2-maximum", "하루 동안 가장 많이 마셨던 음주량은 어느 정도입니까?", "7-2."),
        group(
            "physical-activity",
            "신체활동",
            [
                quantity(
                    "q8-1-vigorous-days",
                    "평소 1주일간, 숨이 많이 차게 만드는 고강도 신체활동을 며칠 하십니까?",
                    "일",
                    prefix="8-1.",
                ),
                display("q8-1-example", "고강도 신체활동의 예> 달리기, 에어로빅, 빠른 속도로 자전거 타기, 건설 현장 노동, 계단으로 물건 나르기 등"),
                quantity(
                    "q8-2-vigorous-hours",
                    "평소 하루에 숨이 많이 차게 만드는 고강도 신체활동을 몇 시간 하십니까? — 시간",
                    "시간",
                    prefix="8-2.",
                    enable_when=enabled_quantity_unless("q8-1-vigorous-days", 0, "일"),
                ),
                quantity(
                    "q8-2-vigorous-minutes",
                    "평소 하루에 숨이 많이 차게 만드는 고강도 신체활동을 몇 시간 하십니까? — 분",
                    "분",
                    enable_when=enabled_quantity_unless("q8-1-vigorous-days", 0, "일"),
                ),
                quantity(
                    "q9-1-moderate-days",
                    "평소 1주일간, 숨이 약간 차게 만드는 중강도 신체활동을 며칠 하십니까?",
                    "일",
                    prefix="9-1.",
                ),
                display("q9-1-exclusion", "8번 응답에 관련된 신체활동은 제외하고 답해주십시오."),
                display("q9-1-example", "중강도 신체활동의 예> 빠르게 걷기, 복식 테니스, 보통 속도로 자전거 타기, 가벼운 물건 나르기, 청소 등"),
                quantity(
                    "q9-2-moderate-hours",
                    "평소 하루에 숨이 약간 차게 만드는 중강도 신체활동을 몇 시간 하십니까? — 시간",
                    "시간",
                    prefix="9-2.",
                    enable_when=enabled_quantity_unless("q9-1-moderate-days", 0, "일"),
                ),
                quantity(
                    "q9-2-moderate-minutes",
                    "평소 하루에 숨이 약간 차게 만드는 중강도 신체활동을 몇 시간 하십니까? — 분",
                    "분",
                    enable_when=enabled_quantity_unless("q9-1-moderate-days", 0, "일"),
                ),
                quantity(
                    "q10-strength-days",
                    "최근 1주일 동안 팔굽혀펴기, 윗몸일으키기, 아령, 역기, 철봉 등 근력 운동을 한 날은 며칠입니까?",
                    "일",
                    prefix="10.",
                ),
            ],
        ),
    ]
    return resource


def form_2() -> dict:
    resource = metadata(
        "kr-national-health-screening-form-2-2025",
        "2025-source-draft",
        "건강검진 추가 문진표",
        "건강검진 실시기준 [별지 제2호 서식]의 만 66세, 70세, 80세 대상 추가 문진을 FHIR R4 Questionnaire로 구조화한 미검토 시험용 리소스.",
        FORM_2_SOURCE,
    )
    resource["name"] = "KrNationalHealthScreeningForm2_2025"
    resource["item"] = [
        display("eligibility", "추가 문진표는 해당 수검자만 작성해주십시오."),
        display("age-scope", "노인기능평가 관련 문항(66세, 70세, 80세 해당)"),
        group(
            "respondent-information",
            "수검자 정보",
            [
                text_item("respondent-name", "수검자 성명"),
                text_item("resident-registration-number", "주민등록번호"),
            ],
        ),
        choice("q1-influenza", "인플루엔자(독감) 예방접종을 매년 하십니까?", ["예", "아니요"], "1."),
        choice("q2-pneumococcal", "폐렴예방접종을 받으셨습니까?", ["예", "아니요"], "2."),
        group(
            "q3-adl",
            "다음은 일상생활 수행능력에 대한 질문입니다. 아래 문항을 읽고 현재 상태에 해당하는 답에 O 표시를 해주십시오.",
            [
                choice("q3-1-eating", "음식을 차려주면 남의 도움 없이 혼자서 식사하십니까?", ["예", "아니요"], "1)"),
                choice("q3-2-dressing", "옷을 챙겨 입을 때 남의 도움 없이 혼자서 하십니까?", ["예", "아니요"], "2)"),
                choice("q3-3-toilet", "대소변을 보기 위해 화장실 출입할 때 남의 도움 없이 혼자서 하십니까?", ["예", "아니요"], "3)"),
                choice("q3-4-bathing", "목욕하실 때 남의 도움 없이 혼자서 하십니까?", ["예", "아니요"], "4)"),
                choice("q3-5-meal-preparation", "식사 준비를 다른 사람의 도움 없이 혼자서 하십니까?", ["예", "아니요"], "5)"),
                choice("q3-6-going-out", "상점, 이웃, 병원, 관공서 등 걸어서 갔다 올 수 있는 곳의 외출을 다른 사람의 도움 없이 혼자서 하십니까?", ["예", "아니요"], "6)"),
            ],
            "3.",
        ),
        choice("q4-fall", "낙상에 관한 질문입니다. 지난 6개월간 넘어진 적이 있습니까?", ["예", "아니요"], "4."),
        choice("q5-urination", "배뇨장애에 관한 질문입니다. 소변을 보는 데 장애가 있거나 소변을 지릴 경우가 있습니까?", ["예", "아니요"], "5."),
    ]
    return resource


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for resource in (form_1(), form_2()):
        path = OUTPUT / f"{resource['id']}.json"
        path.write_text(json.dumps(resource, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
