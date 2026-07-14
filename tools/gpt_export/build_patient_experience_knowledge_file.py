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
        return ["- 허용 응답: 0부터 10까지의 정수"]

    choices = []
    for option in item.get("answerOption", []):
        coding = option["valueCoding"]
        choices.append(f"- `{coding['code']} {coding['display']}`")

    codes = {option["valueCoding"]["code"] for option in item.get("answerOption", [])}
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
        "각 답변은 해당 FHIR `linkId`에 연결한다. 화면에는 원본 `answerOption` 또는 선언된 정수 범위만 표시하며, 원문에 없는 `잘 모르겠음`이나 `답변하지 않음` 보기를 추가하지 않는다.",
        "사용자가 보기 밖의 자유 입력으로 모름이나 응답 거부를 명시한 경우에만 각각 `asked-unknown`, `asked-declined`로 내부 기록하고 동일 문항의 숫자 보기로 만들지 않는다.",
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
