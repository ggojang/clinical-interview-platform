from __future__ import annotations

import json
from io import BytesIO
import os
import unittest
from http.client import HTTPMessage
from unittest.mock import patch

from services.interview_api.llm import (
    LlmClinicalInterpreter,
    LlmHealthInformationAdvisor,
    LlmInterviewPlanner,
    LlmProvider,
    LlmProviderRegistry,
    LlmQuestionPresenter,
    LlmSelectionError,
    _is_single_question_presentation,
    _openai_compatible_completion,
)
from services.interview_api.server import AnonymousDemoGate, ServerConfig, build_handler
from services.interview_api.service import InterviewApi, ServiceError


class _FakeAdapter:
    def clinician_handoff(self):
        return {
            "format": "non_fhir_structured_summary",
            "lifecycle_status": "draft",
            "review_status": "unreviewed",
            "clinical_use_status": "limited",
        }


class _FakeCore:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.mode_id = None
        self.adapter = None
        self.closed = False

    def start(self):
        return {"status": "purpose_required"}

    def process(self, message: str):
        if self.closed:
            raise RuntimeError("closed")
        if self.mode_id is None:
            self.mode_id = "clinical_adaptive"
            self.adapter = _FakeAdapter()
        return {"status": "active", "echo_length": len(message)}

    def close(self):
        self.closed = True
        self.adapter = None
        self.mode_id = None
        return {"status": "closed", "response_state_purged": True}


class InterviewApiServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = [1_800_000_000.0]
        self.api = InterviewApi(
            session_ttl_seconds=60,
            max_sessions=2,
            clock=lambda: self.now[0],
            session_factory=_FakeCore,
        )

    def test_session_lifecycle_returns_result_then_purges(self):
        created = self.api.create_session({"initial_message": "기침이 나요"})
        session_id = created["session_id"]
        self.assertEqual(created["retention"]["storage"], "memory_only")
        self.assertNotIn("기침이 나요", json.dumps(created, ensure_ascii=False))

        updated = self.api.send_message(session_id, {"message": "3일 전부터요"})
        self.assertEqual(updated["state"]["status"], "active")
        result = self.api.result(session_id)
        self.assertEqual(result["lifecycle_status"], "draft")
        self.assertFalse(result["independent_diagnosis_or_treatment"])
        self.assertEqual(result["fhir"]["status"], "not_implemented")

        completed = self.api.complete(session_id)
        self.assertTrue(completed["response_state_purged"])
        with self.assertRaises(ServiceError) as context:
            self.api.get_session(session_id)
        self.assertEqual(context.exception.status, 404)

    def test_expiry_closes_and_removes_session(self):
        created = self.api.create_session()
        session_id = created["session_id"]
        self.now[0] += 61
        self.assertEqual(self.api.purge_expired(), 1)
        with self.assertRaises(ServiceError) as context:
            self.api.get_session(session_id)
        self.assertEqual(context.exception.code, "session_not_found")

    def test_catalog_does_not_overstate_unimplemented_adapters(self):
        capabilities = self.api.catalog()["api_capabilities"]
        self.assertEqual(
            capabilities["implemented_mode_ids"],
            ["clinical_adaptive", "health_information"],
        )
        self.assertEqual(
            capabilities["result_formats"]["fhir_questionnaire_response"],
            "not_implemented",
        )

    def test_purge_all_closes_every_live_session(self):
        self.api.create_session()
        self.api.create_session()
        self.assertEqual(self.api.purge_all(), 2)
        self.assertEqual(self.api.health()["active_sessions"], 0)

    def test_capacity_and_input_boundaries(self):
        self.api.create_session()
        self.api.create_session()
        with self.assertRaises(ServiceError) as context:
            self.api.create_session()
        self.assertEqual(context.exception.status, 503)
        with self.assertRaises(ServiceError) as context:
            self.api.send_message("not-a-uuid", {"message": "hello"})
        self.assertEqual(context.exception.code, "invalid_session_id")

    def test_production_mode_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "research_test"):
            InterviewApi(execution_mode="production")

    def test_default_session_uses_local_llm_without_clinical_authority(self):
        created = self.api.create_session()
        self.assertEqual(created["llm"]["provider_id"], "local_vllm")
        self.assertEqual(created["llm"]["selected_by"], "platform_default")
        self.assertFalse(created["llm"]["external_processing"])
        self.assertFalse(created["llm"]["clinical_authority"])

    def test_request_body_cannot_supply_llm_credentials(self):
        with self.assertRaises(ServiceError) as context:
            self.api.create_session(
                {"llm_selection": {"provider_id": "local_vllm", "api_key": "no"}}
            )
        self.assertEqual(context.exception.code, "invalid_llm_selection")

    def test_demo_resources_are_allowlisted_and_response_free(self):
        catalog = self.api.demo_resources()
        self.assertFalse(catalog["contains_patient_responses"])
        self.assertEqual(catalog["response_storage"], "none")
        questionnaire = self.api.demo_resource("patient-experience-5th-2025")
        self.assertEqual(questionnaire["resourceType"], "Questionnaire")
        screening = self.api.demo_resource("national-health-screening-form-1-2025")
        self.assertEqual(screening["resourceType"], "Questionnaire")
        self.assertEqual(screening["title"], "건강검진 문진표")
        additional = self.api.demo_resource("national-health-screening-form-2-2025")
        self.assertEqual(additional["resourceType"], "Questionnaire")
        with self.assertRaises(ServiceError) as context:
            self.api.demo_resource("../../private")
        self.assertEqual(context.exception.code, "demo_resource_not_found")

    def test_anonymous_demo_is_local_only_scoped_and_short_lived(self):
        configuration = self.api.anonymous_demo_configuration()
        self.assertFalse(configuration["authentication_required"])
        self.assertTrue(configuration["synthetic_test_information_required"])
        self.assertFalse(configuration["providers"][0]["external_processing"])

        created = self.api.create_anonymous_demo_session(
            {"mode_selection": "문진 시작", "initial_message": "가상 기침 사례"}
        )
        self.assertEqual(created["access_scope"], "anonymous_demo")
        self.assertEqual(created["retention"]["ttl_seconds"], 60)
        self.assertTrue(
            created["retention"]["delete_endpoint"].startswith(
                "/demo-api/sessions/"
            )
        )
        session_id = created["session_id"]
        updated = self.api.send_anonymous_demo_message(
            session_id, {"message": "가상 답변"}
        )
        self.assertEqual(updated["access_scope"], "anonymous_demo")
        completed = self.api.complete_anonymous_demo_session(session_id)
        self.assertTrue(completed["response_state_purged"])

    def test_anonymous_demo_rejects_provider_override_and_authenticated_session(self):
        with self.assertRaises(ServiceError) as context:
            self.api.create_anonymous_demo_session(
                {"llm_selection": {"provider_id": "local_vllm"}}
            )
        self.assertEqual(context.exception.code, "invalid_request")

        authenticated = self.api.create_session({"initial_message": "test"})
        with self.assertRaises(ServiceError) as context:
            self.api.send_anonymous_demo_message(
                authenticated["session_id"], {"message": "test"}
            )
        self.assertEqual(context.exception.code, "session_not_found")


class InterviewApiHttpTests(unittest.TestCase):
    def setUp(self) -> None:
        api = InterviewApi(session_factory=_FakeCore)
        config = ServerConfig(api_key="test-secret")
        self.handler_class = build_handler(api, config)

    def _request(
        self,
        method: str,
        path: str,
        body=None,
        *,
        authorized=True,
        origin=None,
        host="demo.example",
    ):
        headers = HTTPMessage()
        headers.add_header("Host", host)
        raw_body = b""
        if authorized:
            headers.add_header("Authorization", "Bearer test-secret")
        if origin:
            headers.add_header("Origin", origin)
        if body is not None:
            raw_body = json.dumps(body).encode("utf-8")
            headers.add_header("Content-Type", "application/json")
            headers.add_header("Content-Length", str(len(raw_body)))
        handler = self.handler_class.__new__(self.handler_class)
        handler.command = method
        handler.path = path
        handler.request_version = "HTTP/1.1"
        handler.requestline = f"{method} {path} HTTP/1.1"
        handler.client_address = ("127.0.0.1", 12345)
        handler.headers = headers
        handler.rfile = BytesIO(raw_body)
        handler.wfile = BytesIO()
        getattr(handler, f"do_{method}")()
        response = handler.wfile.getvalue()
        raw_headers, raw_payload = response.split(b"\r\n\r\n", 1)
        header_lines = raw_headers.decode("iso-8859-1").split("\r\n")
        status = int(header_lines[0].split()[1])
        response_headers = {
            key.strip(): value.strip()
            for line in header_lines[1:]
            if ":" in line
            for key, value in [line.split(":", 1)]
        }
        content_type = response_headers.get("Content-Type", "")
        if raw_payload and content_type.startswith("application/json"):
            payload = json.loads(raw_payload)
        elif raw_payload:
            payload = raw_payload.decode("utf-8")
        else:
            payload = {}
        return status, response_headers, payload

    def test_health_does_not_require_auth_and_disables_cache(self):
        status, headers, body = self._request("GET", "/healthz", authorized=False)
        self.assertEqual(status, 200)
        self.assertEqual(body["response_storage"], "memory_only")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_bearer_auth_and_session_routes(self):
        status, _, body = self._request("GET", "/v1/catalog", authorized=False)
        self.assertEqual(status, 401)
        self.assertEqual(body["error"]["code"], "unauthorized")

        status, _, created = self._request(
            "POST", "/v1/sessions", {"initial_message": "문진 시작"}
        )
        self.assertEqual(status, 201)
        session_id = created["session_id"]
        status, _, result = self._request("GET", f"/v1/sessions/{session_id}/result")
        self.assertEqual(status, 200)
        self.assertEqual(result["clinical_handoff"]["lifecycle_status"], "draft")

        status, _, completed = self._request(
            "POST", f"/v1/sessions/{session_id}/complete", {}
        )
        self.assertEqual(status, 200)
        self.assertTrue(completed["response_state_purged"])
        status, _, missing = self._request("GET", f"/v1/sessions/{session_id}")
        self.assertEqual(status, 404)
        self.assertEqual(missing["error"]["code"], "session_not_found")

        status, _, providers = self._request("GET", "/v1/llm/providers")
        self.assertEqual(status, 200)
        self.assertEqual(providers["default_provider_id"], "local_vllm")
        self.assertEqual(providers["credentials_in_request_body"], "prohibited")

    def test_origin_is_denied_by_default(self):
        status, _, body = self._request(
            "GET",
            "/healthz",
            authorized=False,
            origin="https://untrusted.example",
        )
        self.assertEqual(status, 403)
        self.assertEqual(body["error"]["code"], "origin_not_allowed")

    def test_same_origin_browser_request_is_allowed(self):
        status, _, body = self._request(
            "GET",
            "/healthz",
            authorized=False,
            origin="https://demo.example",
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_demo_shell_is_public_but_resources_require_auth(self):
        status, headers, body = self._request("GET", "/demo", authorized=False)
        self.assertEqual(status, 200)
        self.assertIn("Clinical Interactive AI Platform", body)
        self.assertIn("1 · 설문 유형", body)
        self.assertIn("응답 완료·결과 생성", body)
        self.assertIn("결과 확인", body)
        self.assertIn("id=\"responseForm\"", body)
        self.assertIn("id=\"terminologyState\"", body)
        self.assertIn("id=\"displayLocale\"", body)
        self.assertIn("국민건강검진 문진(시험용)", body)
        self.assertIn("id=\"adaptivePurposeHelp\"", body)
        self.assertIn("<details class=\"api-key-panel\" open>", body)
        self.assertIn("<strong>비정형 대화</strong>", body)
        self.assertIn("id=\"adaptiveProcessing\"", body)
        self.assertIn("플랫폼 API key (상용 LLM key 아님)", body)
        self.assertIn("Key만으로 제공자·모델을 판별할 수 없으므로", body)
        self.assertIn("id=\"fixedRevision\"", body)
        self.assertIn("환자 답변은 질문 표현 요청에 포함하지 않습니다.", body)
        self.assertNotIn("id=\"screeningDate\"", body)
        self.assertIn("검진 예정일은 공식 문항 선택에 필요하지 않아 묻지 않습니다.", body)
        self.assertNotIn("class=\"connection-card\"", body)
        self.assertNotIn("API key 없이 자동 연결", body)
        self.assertIn("연계 산출물 상태", body)
        self.assertNotIn("data-output=\"preview\"", body)
        self.assertNotIn("id=\"startAdaptive\"", body)
        self.assertNotIn("id=\"anonymousConnectButton\"", body)
        self.assertIn("default-src 'self'", headers["Content-Security-Policy"])
        self.assertEqual(headers["Cache-Control"], "no-store")

        status, _, stylesheet = self._request("GET", "/demo/styles.css", authorized=False)
        self.assertEqual(status, 200)
        self.assertIn("[hidden] { display: none !important; }", stylesheet)

        status, _, body = self._request(
            "GET", "/v1/demo/resources", authorized=False
        )
        self.assertEqual(status, 401)
        self.assertEqual(body["error"]["code"], "unauthorized")

        status, _, body = self._request("GET", "/v1/demo/resources")
        self.assertEqual(status, 200)
        self.assertFalse(body["contains_patient_responses"])

    def test_demo_javascript_does_not_use_browser_persistence(self):
        status, _, body = self._request("GET", "/demo/app.js", authorized=False)
        self.assertEqual(status, 200)
        self.assertIn("completeStructuredResponse", body)
        self.assertIn("structuredAnswers", body)
        self.assertIn("isItemEnabled", body)
        self.assertIn("loadQuestionnaireValueSets", body)
        self.assertIn("syntheticGuidanceFor", body)
        self.assertIn("async function resetAdaptiveConversation", body)
        self.assertIn("setAdaptiveBusy(true", body)
        self.assertIn("adaptiveRequestSerial", body)
        self.assertIn("numericControlConfig", body)
        self.assertIn("hasRenderableQuestionnaireContent", body)
        self.assertIn("shouldSubmitOnEnter", body)
        self.assertIn("editFixedAnswer", body)
        self.assertIn("refreshFixedQuestions();\n  renderFixedRevisionList();\n  syncRunnerVisibility();", body)
        self.assertIn("valueDate", body)
        self.assertNotIn("localStorage", body)
        self.assertNotIn("sessionStorage", body)
        self.assertNotIn("document.cookie", body)

    def test_terminology_routes_are_authenticated_and_report_configuration(self):
        status, _, body = self._request(
            "GET", "/v1/terminology/status", authorized=False
        )
        self.assertEqual(status, 401)
        self.assertEqual(body["error"]["code"], "unauthorized")

        status, _, body = self._request("GET", "/v1/terminology/status")
        self.assertEqual(status, 200)
        self.assertFalse(body["configured"])
        self.assertFalse(body["patient_data_transmitted"])


class AnonymousDemoHttpTests(InterviewApiHttpTests):
    def setUp(self) -> None:
        api = InterviewApi(session_factory=_FakeCore)
        config = ServerConfig(
            api_key="test-secret",
            anonymous_demo_enabled=True,
            anonymous_demo_requests_per_minute=30,
        )
        self.handler_class = build_handler(api, config)

    def test_anonymous_demo_lifecycle_needs_no_api_key(self):
        status, _, configuration = self._request(
            "GET", "/demo-api/config", authorized=False
        )
        self.assertEqual(status, 200)
        self.assertTrue(configuration["synthetic_test_information_required"])

        status, _, created = self._request(
            "POST",
            "/demo-api/sessions",
            {"mode_selection": "문진 시작", "initial_message": "가상 기침 사례"},
            authorized=False,
            origin="https://demo.example",
        )
        self.assertEqual(status, 201)
        self.assertEqual(created["access_scope"], "anonymous_demo")
        session_id = created["session_id"]

        status, _, updated = self._request(
            "POST",
            f"/demo-api/sessions/{session_id}/messages",
            {"message": "가상 답변"},
            authorized=False,
            origin="https://demo.example",
        )
        self.assertEqual(status, 200)
        self.assertEqual(updated["access_scope"], "anonymous_demo")

        status, _, completed = self._request(
            "POST",
            f"/demo-api/sessions/{session_id}/complete",
            {},
            authorized=False,
            origin="https://demo.example",
        )
        self.assertEqual(status, 200)
        self.assertTrue(completed["response_state_purged"])

        status, _, protected = self._request(
            "GET", "/v1/catalog", authorized=False
        )
        self.assertEqual(status, 401)
        self.assertEqual(protected["error"]["code"], "unauthorized")

    def test_anonymous_demo_gate_does_not_store_client_identity(self):
        gate = AnonymousDemoGate(2)
        self.assertTrue(gate.allow())
        self.assertTrue(gate.allow())
        self.assertFalse(gate.allow())
        self.assertFalse(hasattr(gate, "client_addresses"))

    def test_anonymous_terminology_status_needs_no_api_key(self):
        status, _, body = self._request(
            "GET", "/demo-api/terminology/status", authorized=False
        )
        self.assertEqual(status, 200)
        self.assertFalse(body["configured"])


class InterviewApiRuntimeIntegrationTests(unittest.TestCase):
    def test_real_api_routes_colloquial_rfe_then_uses_bounded_plan(self):
        local = LlmProvider(
            provider_id="local_vllm",
            display_name="Local",
            adapter="openai_compatible_chat",
            base_url="http://127.0.0.1:8000/v1",
            model="qwen3-27b",
            external_processing=False,
        )
        api = InterviewApi(
            max_sessions=1,
            llm_registry=LlmProviderRegistry([local]),
            llm_presenter=LlmQuestionPresenter(enabled=False),
            clinical_interpreter=LlmClinicalInterpreter(
                enabled=True,
                transport=lambda *_args: json.dumps({
                    "status": "resolved",
                    "rfe_id": "rfe.abdominal_pain",
                    "confidence": 0.94,
                    "candidates": [],
                }),
            ),
            interview_planner=LlmInterviewPlanner(
                enabled=True,
                transport=lambda *_args: json.dumps({
                    "fact_id": "symptom.abdominal_pain.severity",
                }),
            ),
        )

        created = api.create_session({
            "mode_selection": "문진 시작",
            "initial_message": "아랫배 통증",
        })

        self.assertEqual(created["mode_id"], "clinical_adaptive")
        self.assertEqual(created["state"]["adapter_state"]["turn"], 1)
        self.assertEqual(
            created["state"]["adapter_state"]["package"]["id"],
            "package.primary-care-abdominal-pain",
        )
        self.assertEqual(
            created["state"]["adapter_state"]["selected_question"]["fact_id"],
            "symptom.abdominal_pain.severity",
        )
        self.assertEqual(
            created["state"]["adapter_state"]["selected_question"]["planner"],
            "bounded_llm_candidate_selection",
        )
        api.delete_session(created["session_id"])

    def test_real_core_exposes_draft_handoff_without_fhir_claim(self):
        api = InterviewApi(max_sessions=1)
        created = api.create_session(
            {
                "mode_selection": "문진 시작",
                "initial_message": "기침이 나요",
            }
        )
        self.assertEqual(created["mode_id"], "clinical_adaptive")
        result = api.result(created["session_id"])
        self.assertIsNotNone(result["clinical_handoff"])
        self.assertEqual(result["clinical_handoff"]["lifecycle_status"], "draft")
        self.assertEqual(result["fhir"]["status"], "not_implemented")
        api.delete_session(created["session_id"])

    def test_health_information_adapter_generates_information_and_completes(self):
        captured = []

        def transport(provider, messages, timeout):
            captured.append(messages)
            return "일반적인 원인과 확인할 점을 설명합니다. 텍스트만으로 진단할 수는 없습니다."

        advisor = LlmHealthInformationAdvisor(enabled=True, transport=transport)
        api = InterviewApi(max_sessions=1, health_information_advisor=advisor)
        created = api.create_session(
            {
                "mode_selection": "일반 건강상담",
                "initial_message": "가상 사용자의 두통이 궁금합니다",
            }
        )
        self.assertEqual(created["mode_id"], "health_information")
        self.assertEqual(created["presentation"]["purpose"], "health_information")
        self.assertTrue(created["presentation"]["patient_input_transmitted"])
        self.assertFalse(created["presentation"]["clinical_authority"])
        self.assertIn("가상 사용자의 두통", json.dumps(captured[0], ensure_ascii=False))

        result = api.result(created["session_id"])
        self.assertEqual(result["available_formats"], ["health_information_json"])
        self.assertFalse(result["independent_diagnosis_or_treatment"])
        completed = api.complete(created["session_id"])
        self.assertTrue(completed["response_state_purged"])

    def test_health_information_red_flag_precedes_llm_and_is_not_diagnosis(self):
        advisor = LlmHealthInformationAdvisor(
            enabled=True,
            transport=lambda provider, messages, timeout: "즉시 안전 안내를 따라야 합니다.",
        )
        api = InterviewApi(max_sessions=1, health_information_advisor=advisor)
        created = api.create_session(
            {
                "mode_selection": "일반 건강상담",
                "initial_message": "갑자기 한쪽 마비가 있고 말이 어눌합니다",
            }
        )
        safety = created["state"]["adapter_state"]["safety_status"]
        self.assertEqual(safety["level"], "emergency_suspected")
        self.assertIsNone(safety["diagnosis"])
        self.assertIn("119", safety["action_ko"])
        api.delete_session(created["session_id"])


class InterviewApiLlmPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.local = LlmProvider(
            provider_id="local_vllm",
            display_name="Local",
            adapter="openai_compatible_chat",
            base_url="http://127.0.0.1:8000/v1",
            model="qwen3-27b",
            external_processing=False,
        )
        self.external = LlmProvider(
            provider_id="commercial_test",
            display_name="Commercial test",
            adapter="openai_compatible_chat",
            base_url="https://llm.example/v1",
            model="approved-model",
            external_processing=True,
            api_key_env="COMMERCIAL_TEST_KEY",
        )

    def test_external_provider_requires_server_secret_and_explicit_consent(self):
        with patch.dict(os.environ, {"COMMERCIAL_TEST_KEY": "secret"}):
            registry = LlmProviderRegistry([self.local, self.external])
            with self.assertRaises(LlmSelectionError) as context:
                registry.select(
                    {"allowed_provider_ids": ["local_vllm", "commercial_test"]},
                    {"provider_id": "commercial_test", "selected_by": "participant"},
                )
            self.assertEqual(
                context.exception.code, "external_processing_consent_required"
            )
            selected = registry.select(
                {"allowed_provider_ids": ["local_vllm", "commercial_test"]},
                {
                    "provider_id": "commercial_test",
                    "selected_by": "participant",
                    "external_processing_consent": True,
                },
            )
            self.assertEqual(selected.provider.provider_id, "commercial_test")

    def test_requester_can_disable_participant_provider_choice(self):
        registry = LlmProviderRegistry([self.local])
        with self.assertRaises(LlmSelectionError) as context:
            registry.select(
                {
                    "allowed_provider_ids": ["local_vllm"],
                    "participant_may_choose": False,
                },
                {"provider_id": "local_vllm", "selected_by": "participant"},
            )
        self.assertEqual(context.exception.code, "participant_llm_selection_disabled")

        requester_default = registry.select(
            {
                "allowed_provider_ids": ["local_vllm"],
                "default_provider_id": "local_vllm",
                "participant_may_choose": False,
            },
            None,
        )
        self.assertEqual(requester_default.selected_by, "requester")

    def test_presenter_transmits_only_compiled_question(self):
        captured = []

        def transport(provider, messages, timeout):
            captured.append((provider, messages, timeout))
            return "기침은 얼마나 오래되었나요?"

        registry = LlmProviderRegistry([self.local])
        selected = registry.select(None, None)
        presenter = LlmQuestionPresenter(enabled=True, transport=transport)
        state = {
            "adapter_state": {
                "facts": {"patient.secret": "must-not-leave"},
                "selected_question": {"text": "How long have you had the cough?"},
            }
        }
        result = presenter.present(state, selected)
        self.assertEqual(result["status"], "generated")
        self.assertEqual(result["text"], "기침은 얼마나 오래되었나요?")
        transmitted = json.dumps(captured[0][1], ensure_ascii=False)
        self.assertIn("How long have you had the cough?", transmitted)
        self.assertNotIn("must-not-leave", transmitted)
        self.assertIn("advice is reserved for the finalized result", transmitted)
        self.assertFalse(result["patient_response_transmitted"])

    def test_clinical_interpreter_accepts_only_allowlisted_rfe_json(self):
        captured = []

        def transport(provider, messages, timeout):
            captured.append(messages)
            return json.dumps({
                "status": "resolved",
                "rfe_id": "rfe.abdominal_pain",
                "confidence": 0.93,
                "candidates": [],
            })

        registry = LlmProviderRegistry([self.local])
        selected = registry.select(None, None)
        interpreter = LlmClinicalInterpreter(enabled=True, transport=transport)
        result = interpreter.interpret(
            "아랫배 통증",
            [
                {"id": "rfe.abdominal_pain", "display_ko": "복통", "aliases": ["복통"]},
                {"id": "rfe.urinary_symptoms", "display_ko": "배뇨 증상", "aliases": ["소변"]},
            ],
            selected,
        )
        self.assertEqual(result["rfe_id"], "rfe.abdominal_pain")
        self.assertFalse(result["clinical_authority"])
        transmitted = json.dumps(captured[0], ensure_ascii=False)
        self.assertIn("아랫배 통증", transmitted)
        self.assertIn("rfe.abdominal_pain", transmitted)

        invalid = LlmClinicalInterpreter(
            enabled=True,
            transport=lambda *_args: json.dumps({
                "status": "resolved",
                "rfe_id": "rfe.invented_diagnosis",
                "confidence": 0.99,
            }),
        ).interpret(
            "아랫배 통증",
            [{"id": "rfe.abdominal_pain", "display_ko": "복통", "aliases": []}],
            selected,
        )
        self.assertNotEqual(invalid["status"], "resolved")

        non_finite = LlmClinicalInterpreter(
            enabled=True,
            transport=lambda *_args: (
                '{"status":"resolved","rfe_id":"rfe.abdominal_pain",'
                '"confidence":NaN}'
            ),
        ).interpret(
            "아랫배 통증",
            [{"id": "rfe.abdominal_pain", "display_ko": "복통", "aliases": []}],
            selected,
        )
        self.assertEqual(non_finite["status"], "unavailable")
        self.assertTrue(non_finite["patient_input_transmitted"])

    def test_interview_planner_rejects_non_candidate_fact(self):
        registry = LlmProviderRegistry([self.local])
        selected = registry.select(None, None)
        candidates = [
            {"fact_id": "symptom.location", "text": "어디가 아픈가요?", "score": 10},
            {"fact_id": "symptom.severity", "text": "얼마나 심한가요?", "score": 9},
        ]
        valid = LlmInterviewPlanner(
            enabled=True,
            transport=lambda *_args: '{"fact_id":"symptom.location"}',
        )
        self.assertEqual(valid.choose({}, candidates, selected), "symptom.location")
        invalid = LlmInterviewPlanner(
            enabled=True,
            transport=lambda *_args: '{"fact_id":"diagnosis.appendicitis"}',
        )
        self.assertIsNone(invalid.choose({}, candidates, selected))

    def test_presenter_uses_compiled_stem_without_repeating_inline_choices(self):
        captured = []

        def transport(provider, messages, timeout):
            captured.append(messages)
            return "현재 흡연 상태는 무엇인가요?"

        registry = LlmProviderRegistry([self.local])
        selected = registry.select(None, None)
        presenter = LlmQuestionPresenter(enabled=True, transport=transport)
        presenter.present(
            {
                "adapter_state": {
                    "selected_question": {
                        "text": "현재 흡연 상태는 무엇인가요? 1 현재 흡연, 2 과거 흡연",
                        "stem_text": "현재 흡연 상태는 무엇인가요?",
                    }
                }
            },
            selected,
        )
        self.assertEqual(captured[0][1]["content"], "현재 흡연 상태는 무엇인가요?")

    def test_question_presenter_rejects_answer_commentary_before_question(self):
        self.assertTrue(_is_single_question_presentation("기침은 언제 시작되었나요?"))
        self.assertFalse(
            _is_single_question_presentation(
                "말씀하신 답변은 중요합니다. 기침은 언제 시작되었나요?"
            )
        )
        self.assertFalse(
            _is_single_question_presentation("기침은 언제 시작되었나요? 열도 있나요?")
        )

    def test_qwen3_completion_disables_reasoning_only_output(self):
        captured = []

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _limit):
                return json.dumps(
                    {"choices": [{"message": {"content": "간결한 안내입니다."}}]}
                ).encode()

        def fake_urlopen(request, timeout):
            captured.append((request, timeout))
            return Response()

        provider = LlmProvider(
            provider_id="local_vllm",
            display_name="Banttas AI local LLM",
            adapter="openai_compatible",
            base_url="http://127.0.0.1:8000/v1",
            model="qwen3-27b",
            external_processing=False,
        )
        with patch("services.interview_api.llm.urlopen", side_effect=fake_urlopen):
            result = _openai_compatible_completion(
                provider, [{"role": "user", "content": "질문"}], 30
            )
        payload = json.loads(captured[0][0].data.decode())
        self.assertEqual(result, "간결한 안내입니다.")
        self.assertEqual(
            payload["chat_template_kwargs"], {"enable_thinking": False}
        )


if __name__ == "__main__":
    unittest.main()
