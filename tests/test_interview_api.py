from __future__ import annotations

import json
from io import BytesIO
import unittest
from http.client import HTTPMessage

from services.interview_api.server import ServerConfig, build_handler
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
        self.assertEqual(capabilities["implemented_mode_ids"], ["clinical_adaptive"])
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
    ):
        headers = HTTPMessage()
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
        payload = json.loads(raw_payload) if raw_payload else {}
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

    def test_origin_is_denied_by_default(self):
        status, _, body = self._request(
            "GET",
            "/healthz",
            authorized=False,
            origin="https://untrusted.example",
        )
        self.assertEqual(status, 403)
        self.assertEqual(body["error"]["code"], "origin_not_allowed")


class InterviewApiRuntimeIntegrationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
