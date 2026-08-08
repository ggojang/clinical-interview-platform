import json
import unittest
from copy import deepcopy
from pathlib import Path

from preventive.package_recommendation import compare_add_on_packages
from preventive.national_screening import NationalScreeningSession
from runtime.questionnaire_prepopulation import prefill_questionnaire_response
from runtime.service_modes import ServiceModeRegistry, resolve_service_mode
from runtime.session import InterviewSession


ROOT = Path(__file__).resolve().parents[1]


def test_no_explicit_mode_preserves_legacy_rfe_first_chatbot():
    result = resolve_service_mode()
    assert result["compatibility_default"]
    assert result["mode"]["id"] == "clinical_adaptive"
    assert result["mode"]["entry"] == "reason_for_encounter"
    policy = ServiceModeRegistry().document["compatibility"]
    assert policy["legacy_entry_behavior_unchanged"]
    assert policy["existing_conversation_starters_unchanged"]
    config = json.loads(
        (ROOT / "docs/gpt/custom-gpt-config.json").read_text(encoding="utf-8")
    )
    assert config["conversation_starters"] == [
        "평가/설문 목록",
        "오늘 불편한 증상이나 상담받고 싶은 내용을 입력하겠습니다",
        "건강검진 문진을 시작하고 싶습니다",
        "환자경험평가",
    ]


def test_top_level_categories_require_submode_only_when_needed():
    clinical = resolve_service_mode("진료 준비")
    assert clinical["status"] == "selection_required"
    assert [item["id"] for item in clinical["options"]] == [
        "clinical_adaptive",
        "clinical_structured",
    ]
    screening = resolve_service_mode("추가 검진 추천받기")
    assert screening["status"] == "resolved"
    assert screening["mode"]["id"] == "screening_addon_recommendation"
    assert screening["next"]["workflow"] == "supplemental_adaptive_interview"
    assert screening["next"]["prompt_ko"] == "필요한 내용만 대화로 확인하겠습니다."
    assert screening["next"]["official_nhis_questionnaire"] == "offer_as_optional_choice"


def test_fixed_questionnaire_modes_preserve_source_authority():
    conversational = resolve_service_mode("대화로 설문하기")["mode"]
    structured = resolve_service_mode("정형 설문")["mode"]
    assert conversational["source_items_are_immutable"]
    assert structured["source_items_are_immutable"]
    assert not conversational["automatic_question_terminology_mapping"]
    assert not structured["automatic_question_terminology_mapping"]
    assert structured["sdc_extraction"] == "disabled"


def _questionnaire():
    return {
        "resourceType": "Questionnaire",
        "id": "synthetic-nhis-preview",
        "url": "https://example.test/fhir/Questionnaire/synthetic-nhis-preview",
        "version": "1",
        "status": "draft",
        "item": [
            {"linkId": "smoking-status", "type": "choice", "text": "흡연 상태"},
            {"linkId": "smoking-history", "type": "integer", "text": "흡연 기간"},
            {"linkId": "comment", "type": "string", "text": "추가 의견"},
        ],
    }


def _mapping():
    return {
        "id": "mapping.synthetic-nhis-preview",
        "version": "0.1.0",
        "provenance": {"source": "synthetic_regression_fixture"},
        "entries": [
            {
                "target_link_id": "smoking-status",
                "source_fact_ids": ["patient.smoking.status"],
                "relation": "equivalent",
            },
            {
                "target_link_id": "smoking-history",
                "source_fact_ids": [
                    "patient.smoking.cigarettes_per_day",
                    "patient.smoking.years",
                ],
                "value_fact_id": "patient.smoking.years",
                "relation": "exact",
            },
            {
                "target_link_id": "comment",
                "source_fact_ids": ["screening.additional_concern"],
                "relation": "partial",
            },
        ],
    }


def test_prepopulation_is_exact_equivalent_only_and_never_completes():
    questionnaire = _questionnaire()
    original = deepcopy(questionnaire)
    facts = {
        "patient.smoking.status": {
            "status": "known",
            "value": {
                "system": "http://snomed.info/sct",
                "code": "77176002",
                "display": "Smoker",
            },
        },
        "patient.smoking.cigarettes_per_day": {"status": "not_provided"},
        "patient.smoking.years": {"status": "known", "value": 20},
        "screening.additional_concern": {"status": "known", "value": "합성 의견"},
    }
    result = prefill_questionnaire_response(questionnaire, facts, _mapping())
    response = result["questionnaire_response"]
    assert questionnaire == original
    assert response["status"] == "in-progress"
    assert response["questionnaire"].endswith("|1")
    assert [item["linkId"] for item in response["item"]] == ["smoking-status"]
    report = result["prepopulation_report"]
    assert report["requires_user_review"]
    assert not report["automatic_completed_status"]
    skipped = {item["target_link_id"]: item["reason"] for item in report["skipped"]}
    assert skipped == {
        "smoking-history": "source_fact_not_known",
        "comment": "relation_not_automatic",
    }


def test_prepopulation_rejects_mapping_without_provenance():
    mapping = _mapping()
    mapping.pop("provenance")
    try:
        prefill_questionnaire_response(_questionnaire(), {}, mapping)
    except ValueError as exc:
        assert "version and provenance" in str(exc)
    else:
        raise AssertionError("missing provenance must be rejected")


def test_package_comparison_always_includes_lowest_cost_suitable_option():
    packages = [
        {
            "id": "center.basic-addon",
            "display_ko": "기본 추가형",
            "price_krw": 100000,
            "item_ids": ["nhis.lipid", "center.eye"],
            "need_tags": ["eye", "cardiovascular"],
        },
        {
            "id": "center.premium-addon",
            "display_ko": "정밀 추가형",
            "price_krw": 400000,
            "item_ids": ["nhis.lipid", "center.eye", "center.retina"],
            "need_tags": ["eye", "retina"],
        },
    ]
    result = compare_add_on_packages(
        packages,
        {"eye", "retina"},
        national_baseline_items={"nhis.lipid"},
    )
    assert result["lowest_cost_suitable_package_id"] == "center.basic-addon"
    assert result["best_match_package_id"] == "center.premium-addon"
    assert result["presented_candidate_ids"] == [
        "center.basic-addon",
        "center.premium-addon",
    ]
    assert not result["economic_capacity_inferred"]
    assert all(
        item["duplicate_national_item_ids"] == ["nhis.lipid"]
        for item in result["evaluated_packages"]
    )


def test_service_mode_simulation_fixture_is_synthetic_and_covers_compatibility():
    fixture = json.loads(
        (ROOT / "simulation/workflows/service-mode-compatibility-cases.json").read_text(
            encoding="utf-8"
        )
    )
    assert fixture["synthetic"]
    assert not fixture["contains_real_patient_data"]
    case_ids = {item["id"] for item in fixture["cases"]}
    assert {
        "legacy-chatbot-no-mode-selection",
        "screening-default-supplemental-interview",
        "fixed-survey-source-authority",
        "nhis-prefill-compound-fact-gap",
    } <= case_ids


def test_legacy_interview_session_can_purge_ephemeral_response_state():
    session = InterviewSession("ephemeral-close")
    state = session.process("기침이 4일 전부터 있어요")
    assert state["facts"]
    assert state["events"]
    closed = session.close()
    assert closed["response_state_purged"]
    assert session.memory.facts == {}
    assert session.memory.events == []
    assert session.encounter_context["care_setting"] == "primary_care"
    try:
        session.process("다시 입력")
    except RuntimeError as exc:
        assert "closed" in str(exc)
    else:
        raise AssertionError("closed session must reject new answers")


def test_screening_session_can_purge_ephemeral_response_state():
    session = NationalScreeningSession("ephemeral-screening", {
        "subject_ref": "Patient/synthetic",
        "age": 54,
        "administrative_gender": "male",
        "sex_at_birth": "male",
        "smoking": {"status": "current", "pack_years": 15},
    })
    session.decide("kr.nhis.general.common", 1)
    session.answer("kr.nhis.general.common.current_symptom", "없음", value="none")
    result = session.close()
    assert result["response_state_purged"]
    assert session.patient_context == {}
    assert session.answers == {}
    assert session.events == []
    assert session.consent_ledger.records == []
    try:
        session.snapshot()
    except RuntimeError as exc:
        assert "closed" in str(exc)
    else:
        raise AssertionError("closed screening session must reject snapshots")


def load_tests(loader, tests, pattern):
    """Run function-style regressions under the repository's unittest gate."""
    suite = unittest.TestSuite()
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            suite.addTest(unittest.FunctionTestCase(value, description=name))
    return suite
