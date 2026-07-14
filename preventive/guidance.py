"""Post-questionnaire guidance kept separate from captured responses."""
from __future__ import annotations

from copy import deepcopy
from typing import Any


SCREENING_METHODS = {
    "kr.nhis.cancer.gastric": {
        "label_ko": "위암검진",
        "method_ko": "위내시경(시행이 어려운 경우 위장조영검사)",
        "source_ref": "source.kr.ncc.national-cancer-screening",
    },
    "kr.nhis.cancer.colorectal": {
        "label_ko": "대장암검진",
        "method_ko": "분변잠혈검사, 양성인 경우 대장내시경 평가",
        "source_ref": "source.kr.ncc.national-cancer-screening",
    },
    "kr.nhis.cancer.liver": {
        "label_ko": "간암검진",
        "method_ko": "간초음파와 혈청 알파태아단백 검사",
        "source_ref": "source.kr.ncc.national-cancer-screening",
    },
    "kr.nhis.cancer.lung": {
        "label_ko": "폐암검진",
        "method_ko": "저선량 흉부 CT",
        "source_ref": "source.kr.ncc.national-cancer-screening",
    },
    "kr.nhis.cancer.breast": {
        "label_ko": "유방암검진",
        "method_ko": "유방촬영술",
        "source_ref": "source.kr.ncc.national-cancer-screening",
    },
    "kr.nhis.cancer.cervical": {
        "label_ko": "자궁경부암검진",
        "method_ko": "자궁경부세포검사",
        "source_ref": "source.kr.ncc.national-cancer-screening",
    },
}


def _known_answer(response: dict[str, Any], fact_id: str) -> Any:
    for item in response.get("answers", {}).values():
        if item.get("fact_id") == fact_id and item.get("status") == "known":
            return item.get("value")
    return None


def build_post_interview_guidance(response: dict[str, Any]) -> dict[str, Any]:
    symptom = _known_answer(response, "screening.current_symptom")
    symptom_absent = symptom in {None, False, "no", "none", "없음", "2"}
    if symptom_absent:
        ddx = {
            "status": "not_applicable",
            "items": [],
            "explanation_ko": "현재 평가할 증상이 보고되지 않아 감별진단을 생성하지 않았습니다.",
        }
    else:
        ddx = {
            "status": "requires_symptom_specific_follow_up",
            "items": [],
            "explanation_ko": "증상별 추가 문진과 안전평가 전에는 감별진단 후보를 생성하지 않습니다.",
        }

    screening_items = []
    for group_id in response.get("eligible_question_groups", []):
        if group_id in SCREENING_METHODS:
            item = deepcopy(SCREENING_METHODS[group_id])
            item.update({
                "question_group_id": group_id,
                "eligibility": "candidate",
                "official_confirmation": "NHIS required",
                "certainty": "program-rule-match",
            })
            screening_items.append(item)

    medication = _known_answer(response, "medication.current")
    medication_section = {
        "status": "available" if medication else "not_captured",
        "current_medication": medication,
        "explanation_ko": (
            "복용약은 검진기관에 제시하고 임의로 중단하지 않습니다. 제품·성분·용량이 불명확하면 약 봉투나 처방전으로 확인합니다."
            if medication else
            "현재 설문 응답에서 확인된 약물 정보가 없습니다."
        ),
    }

    return {
        "resource_type": "PostInterviewGuidance",
        "session_id": response["session_id"],
        "status": "research_only",
        "review_status": "unreviewed",
        "not_a_diagnosis": True,
        "sections": {
            "urgency_and_next_action": {
                "level": "routine" if symptom_absent else "reassess_symptom_safety",
                "explanation_ko": "현재 응답만으로 응급 신호는 확인되지 않았습니다." if symptom_absent else "새 증상에 대한 안전 질문이 먼저 필요합니다.",
            },
            "possible_differential_considerations": ddx,
            "screening_tests_to_confirm": {
                "items": screening_items,
                "explanation_ko": "아래 항목은 연령·성별·위험조건으로 계산한 후보이며 실제 공단 검진 항목은 별도로 확인해야 합니다.",
            },
            "treatment_and_lifestyle_discussion": {
                "items": [],
                "explanation_ko": "검진 설문만으로 치료나 처방을 결정하지 않습니다. 결과와 위험요인을 바탕으로 의료진과 논의합니다.",
            },
            "medication_information": medication_section,
            "questionnaire_explanation": {
                "program": "Korean NHIS national health screening",
                "official_entitlement": response.get("official_entitlement", "unverified"),
                "consent_is_separate": True,
                "report_api_fhir_are_projections": True,
            },
            "missing_or_uncertain_information": [
                {
                    "fact_id": item["fact_id"],
                    "dataAbsentReason": deepcopy(item["dataAbsentReason"]),
                }
                for item in response.get("answers", {}).values()
                if item.get("dataAbsentReason")
            ],
        },
        "source_refs": sorted({item["source_ref"] for item in screening_items}),
    }
