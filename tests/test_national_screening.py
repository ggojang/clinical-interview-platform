from preventive.consent import ConsentLedger
from preventive.export import DAR_EXTENSION, to_api_payload, to_fhir_bundle, to_report
from preventive.national_screening import NationalScreeningSession, load_knowledge
from preventive.self_simulation import run as run_self_simulation
from preventive.guidance import build_post_interview_guidance


def male_54_context():
    return {
        "subject_ref": "Patient/example",
        "age": 54,
        "administrative_gender": "male",
        "sex_at_birth": "male",
        "smoking": {"status": "current", "pack_years": 15},
    }


def test_knowledge_is_unreviewed_research_only():
    knowledge = load_knowledge()
    assert knowledge["status"] == "research_only"
    assert knowledge["review_status"] == "unreviewed"
    assert all(item["id"] for item in knowledge["facts"])


def test_age_sex_and_risk_eligibility_is_advisory():
    session = NationalScreeningSession("male54", male_54_context())
    eligible = session.eligible_group_ids()
    assert "kr.nhis.general.common" in eligible
    assert "kr.nhis.cancer.gastric" in eligible
    assert "kr.nhis.cancer.colorectal" in eligible
    assert "kr.nhis.cancer.common" in eligible
    assert "kr.nhis.cancer.lung" not in eligible
    assert "kr.nhis.cancer.breast" not in eligible
    assert all(item["official_entitlement_confirmation"] == "required" for item in session.offers())


def test_question_group_never_activates_without_explicit_consent():
    session = NationalScreeningSession("consent-gate", male_54_context())
    assert session.active_questions() == []
    decision = session.decide("kr.nhis.cancer.gastric", 1)
    assert decision["decision"] == "accepted"
    assert decision["consent_id"]
    assert session.active_questions()
    session.decide("kr.nhis.cancer.gastric", 2)
    assert session.active_questions() == []


def test_answer_keeps_raw_input_and_data_absent_reason():
    session = NationalScreeningSession("dar", male_54_context())
    session.decide("kr.nhis.cancer.gastric", "예")
    question_id = "kr.nhis.cancer.gastric.last_test"
    record = session.answer(question_id, 3)
    assert record["raw_input"] == "3"
    assert record["value"] is None
    assert record["dataAbsentReason"]["code"] == "asked-unknown"


def test_consent_is_independent_and_withdrawable():
    ledger = ConsentLedger("ledger", "Patient/example")
    consent = ledger.capture(
        scope="api-delivery:screening-result",
        purpose="deliver-screening-result",
        decision="accepted",
        raw_input="1",
        policy_uri="https://example/policy",
        policy_version="1",
    )
    withdrawn = ledger.withdraw(consent["consent_id"], raw_input="철회")
    assert withdrawn["lifecycle_status"] == "withdrawn"
    assert withdrawn["withdrawal_raw_input"] == "철회"


def test_age_66_female_and_liver_risk_activates_expected_candidates():
    session = NationalScreeningSession("female66", {
        "age": 66,
        "sex_at_birth": "female",
        "liver_risk": {"hbv": True, "hcv": False, "cirrhosis": False},
        "smoking": {"status": "never", "pack_years": 0},
    })
    eligible = session.eligible_group_ids()
    assert "kr.nhis.general.age66.additional" in eligible
    assert "kr.nhis.cancer.liver" in eligible
    assert "kr.nhis.cancer.breast" in eligible
    assert "kr.nhis.cancer.cervical" in eligible


def test_report_api_and_fhir_are_projections_of_same_response():
    session = NationalScreeningSession("export", male_54_context())
    session.decide("kr.nhis.cancer.gastric", 1)
    session.answer("kr.nhis.cancer.gastric.last_test", "3")
    response = session.snapshot(completed=True)
    report = to_report(response)
    api = to_api_payload(response)
    bundle = to_fhir_bundle(response)
    assert report["session_id"] == api["idempotency_key"] == "export"
    assert bundle["resourceType"] == "Bundle"
    resources = [item["resource"] for item in bundle["entry"]]
    assert {item["resourceType"] for item in resources} >= {"Patient", "QuestionnaireResponse", "Consent"}
    qr = next(item for item in resources if item["resourceType"] == "QuestionnaireResponse")
    assert qr["item"][0]["extension"][0]["url"] == DAR_EXTENSION
    consent = next(item for item in resources if item["resourceType"] == "Consent")
    assert consent["status"] == "active"


def test_exploratory_self_simulation_exposes_candidate_fact_gaps():
    report = run_self_simulation()
    assert report["passed"]
    assert report["case_count"] == 3
    candidate_ids = {item["candidate_fact_id"] for item in report["candidate_fact_gaps"]}
    assert "patient.anatomy.cervix_present" in candidate_ids
    assert "eligibility.nhis.confirmed_items" in candidate_ids


def test_post_interview_guidance_separates_ddx_tests_drugs_and_explanation():
    session = NationalScreeningSession("guidance", male_54_context())
    session.decide("kr.nhis.general.common", 1)
    session.answer("kr.nhis.general.common.current_symptom", "없음", value="none")
    session.answer("kr.nhis.general.common.medication", "암로디핀 5mg")
    guidance = build_post_interview_guidance(session.snapshot(completed=True))
    sections = guidance["sections"]
    assert sections["possible_differential_considerations"]["status"] == "not_applicable"
    labels = {item["label_ko"] for item in sections["screening_tests_to_confirm"]["items"]}
    assert {"위암검진", "대장암검진"} <= labels
    assert sections["medication_information"]["current_medication"] == "암로디핀 5mg"
    assert sections["questionnaire_explanation"]["consent_is_separate"]
