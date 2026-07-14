#!/usr/bin/env python3
"""Build the standalone Custom GPT Knowledge file for the fixed survey."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "fhir/r4/questionnaires/kr-patient-experience-evaluation-5th-2025.json"
OUTPUT = ROOT / "docs/gpt/knowledge-files/patient-experience-evaluation-5th-2025-chatbot.md"


def answer_lines(item: dict) -> list[str]:
    if item["type"] == "integer":
        return [
            "- 허용 응답: 0부터 10까지의 정수",
            "- 추가 응답: `11 잘 모르겠음`, `12 답변하지 않음`",
        ]

    choices = []
    for option in item.get("answerOption", []):
        coding = option["valueCoding"]
        choices.append(f"- `{coding['code']} {coding['display']}`")

    codes = {option["valueCoding"]["code"] for option in item.get("answerOption", [])}
    if item["linkId"] == "q24":
        choices.extend(["- `3 잘 모르겠음`", "- `5 답변하지 않음`"])
    elif item["linkId"] in {"q25", "q26"}:
        choices.extend(["- `6 잘 모르겠음`", "- `7 답변하지 않음`"])
    else:
        choices.extend(["- `5 잘 모르겠음`", "- `6 답변하지 않음`"])
    assert len(codes) == len(item.get("answerOption", []))
    return choices


def build() -> str:
    questionnaire = json.loads(SOURCE.read_text(encoding="utf-8"))
    lines = [
        "# 2025년(5차) 환자경험평가 — 챗봇 정형 설문",
        "",
        "- Questionnaire ID: `kr-patient-experience-evaluation-5th-2025`",
        f"- FHIR canonical: `{questionnaire['url']}`",
        f"- Questionnaire version: `{questionnaire['version']}`",
        "- 상태: `draft`, `unreviewed`, `research_only`",
        "- 구성: 8개 섹션, 26개 문항",
        "",
        "## 실행 계약",
        "",
        "이 파일은 동적 임상 질문 생성에 사용하지 않는다. 사용자가 환자경험평가 작성을 명확히 확인한 뒤에만 사용한다.",
        "확인 직후에는 설계 설명, 계획, 사과, 재확인 없이 `section-1`의 `q01`을 그대로 제시한다.",
        "한 번에 한 문항만 제시하고, 문항 문구·보기 코드·보기 문구·순서를 변경하지 않는다.",
        "각 답변은 해당 FHIR `linkId`에 연결한다. `잘 모르겠음`은 `asked-unknown`, `답변하지 않음`은 `asked-declined`로 유지한다.",
        "이 실행 계약 자체는 사용자에게 출력하지 않는다.",
        "",
    ]
    question_count = 0
    for section_number, section in enumerate(questionnaire["item"], 1):
        lines.extend([
            f"## 섹션 {section_number}/8 — {section['text']}",
            "",
        ])
        for item in section.get("item", []):
            if item["type"] == "display":
                lines.extend([f"> {item['text']}", ""])
                continue
            question_count += 1
            lines.extend([
                f"### `{item['linkId']}`",
                "",
                item["text"],
                "",
                *answer_lines(item),
                "",
            ])
    assert question_count == 26
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"Built {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
