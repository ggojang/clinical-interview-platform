"""Dependency-free HTTP adapter for the interview application service."""
from __future__ import annotations

from dataclasses import dataclass
import hmac
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import threading
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from services.interview_api.service import InterviewApi, ServiceError


MAX_JSON_BODY_BYTES = 65_536
SESSION_PATH = re.compile(r"^/v1/sessions/([^/]+)$")
MESSAGE_PATH = re.compile(r"^/v1/sessions/([^/]+)/messages$")
RESULT_PATH = re.compile(r"^/v1/sessions/([^/]+)/result$")
COMPLETE_PATH = re.compile(r"^/v1/sessions/([^/]+)/complete$")
DEMO_RESOURCE_PATH = re.compile(r"^/v1/demo/resources/([^/]+)$")
STATIC_ROOT = Path(__file__).resolve().parent / "static"
STATIC_FILES = {
    "/": ("demo.html", "text/html; charset=utf-8"),
    "/demo": ("demo.html", "text/html; charset=utf-8"),
    "/demo/": ("demo.html", "text/html; charset=utf-8"),
    "/demo/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/demo/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


@dataclass(frozen=True)
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 8000
    api_key: str | None = None
    allowed_origins: tuple[str, ...] = ()
    session_ttl_seconds: int = 1_800
    max_sessions: int = 1_000
    execution_mode: str = "research_test"

    @classmethod
    def from_env(cls) -> "ServerConfig":
        origins = tuple(
            item.strip()
            for item in os.getenv("CLINICAL_API_ALLOWED_ORIGINS", "").split(",")
            if item.strip()
        )
        return cls(
            host=os.getenv("CLINICAL_API_HOST", "127.0.0.1"),
            port=int(os.getenv("CLINICAL_API_PORT", "8000")),
            api_key=os.getenv("CLINICAL_API_KEY") or None,
            allowed_origins=origins,
            session_ttl_seconds=int(os.getenv("CLINICAL_API_SESSION_TTL", "1800")),
            max_sessions=int(os.getenv("CLINICAL_API_MAX_SESSIONS", "1000")),
            execution_mode=os.getenv("CLINICAL_API_EXECUTION_MODE", "research_test"),
        )

    def validate(self) -> None:
        local_hosts = {"127.0.0.1", "localhost", "::1"}
        if self.host not in local_hosts and not self.api_key:
            raise ValueError("CLINICAL_API_KEY is required for a non-loopback bind address")
        if not 1 <= self.port <= 65_535:
            raise ValueError("CLINICAL_API_PORT must be between 1 and 65535")


def build_handler(api: InterviewApi, config: ServerConfig) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "ClinicalInterviewAPI"
        sys_version = ""

        def do_OPTIONS(self) -> None:  # noqa: N802
            if not self._origin_allowed():
                return
            self.send_response(HTTPStatus.NO_CONTENT)
            self._security_headers()
            self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Request-ID")
            self.send_header("Access-Control-Max-Age", "600")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            self._dispatch("GET")

        def do_POST(self) -> None:  # noqa: N802
            self._dispatch("POST")

        def do_DELETE(self) -> None:  # noqa: N802
            self._dispatch("DELETE")

        def _dispatch(self, method: str) -> None:
            request_id = self.headers.get("X-Request-ID", "").strip() or str(uuid4())
            if len(request_id) > 128:
                request_id = str(uuid4())
            try:
                if not self._origin_allowed(request_id):
                    return
                path = urlsplit(self.path).path
                if path == "/healthz" and method == "GET":
                    self._json(HTTPStatus.OK, api.health(), request_id)
                    return
                if path in STATIC_FILES and method == "GET":
                    filename, content_type = STATIC_FILES[path]
                    self._static(filename, content_type, request_id)
                    return
                self._authenticate()
                if path == "/v1/catalog" and method == "GET":
                    self._json(HTTPStatus.OK, api.catalog(), request_id)
                    return
                if path == "/v1/llm/providers" and method == "GET":
                    self._json(HTTPStatus.OK, api.llm_providers(), request_id)
                    return
                if path == "/v1/demo/resources" and method == "GET":
                    self._json(HTTPStatus.OK, api.demo_resources(), request_id)
                    return
                if match := DEMO_RESOURCE_PATH.fullmatch(path):
                    if method == "GET":
                        self._json(HTTPStatus.OK, api.demo_resource(match.group(1)), request_id)
                        return
                if path == "/v1/sessions" and method == "POST":
                    self._json(HTTPStatus.CREATED, api.create_session(self._body()), request_id)
                    return
                if match := MESSAGE_PATH.fullmatch(path):
                    if method == "POST":
                        self._json(HTTPStatus.OK, api.send_message(match.group(1), self._body()), request_id)
                        return
                if match := RESULT_PATH.fullmatch(path):
                    if method == "GET":
                        self._json(HTTPStatus.OK, api.result(match.group(1)), request_id)
                        return
                if match := COMPLETE_PATH.fullmatch(path):
                    if method == "POST":
                        self._json(HTTPStatus.OK, api.complete(match.group(1)), request_id)
                        return
                if match := SESSION_PATH.fullmatch(path):
                    if method == "GET":
                        self._json(HTTPStatus.OK, api.get_session(match.group(1)), request_id)
                        return
                    if method == "DELETE":
                        self._json(HTTPStatus.OK, api.delete_session(match.group(1)), request_id)
                        return
                raise ServiceError(404, "route_not_found", "route was not found")
            except ServiceError as exc:
                self._json(exc.status, exc.as_dict(request_id), request_id)
            except (ValueError, json.JSONDecodeError) as exc:
                error = ServiceError(400, "invalid_request", str(exc))
                self._json(error.status, error.as_dict(request_id), request_id)
            except Exception:
                error = ServiceError(500, "internal_error", "the request could not be completed")
                self._json(error.status, error.as_dict(request_id), request_id)

        def _authenticate(self) -> None:
            if not config.api_key:
                return
            supplied = self.headers.get("Authorization", "")
            expected = f"Bearer {config.api_key}"
            if not hmac.compare_digest(supplied, expected):
                raise ServiceError(401, "unauthorized", "a valid bearer API key is required")

        def _origin_allowed(self, request_id: str | None = None) -> bool:
            origin = self.headers.get("Origin")
            if origin is None or origin in config.allowed_origins:
                return True
            if request_id is not None:
                error = ServiceError(403, "origin_not_allowed", "request origin is not allowed")
                self._json(error.status, error.as_dict(request_id), request_id)
            else:
                self.send_response(HTTPStatus.FORBIDDEN)
                self._security_headers()
                self.end_headers()
            return False

        def _body(self) -> dict[str, Any]:
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
            if content_type != "application/json":
                raise ServiceError(415, "unsupported_media_type", "Content-Type must be application/json")
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                raise ServiceError(411, "content_length_required", "Content-Length is required")
            try:
                length = int(raw_length)
            except ValueError as exc:
                raise ServiceError(400, "invalid_request", "Content-Length is invalid") from exc
            if length < 0 or length > MAX_JSON_BODY_BYTES:
                raise ServiceError(413, "input_too_large", "JSON body exceeds 65536 bytes")
            raw = self.rfile.read(length)
            if not raw:
                return {}
            try:
                body = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ServiceError(400, "invalid_json", "request body is not valid UTF-8 JSON") from exc
            if not isinstance(body, dict):
                raise ServiceError(400, "invalid_request", "request body must be an object")
            return body

        def _json(self, status: int, payload: dict[str, Any], request_id: str) -> None:
            body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self._security_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Request-ID", request_id)
            if status == HTTPStatus.UNAUTHORIZED:
                self.send_header("WWW-Authenticate", "Bearer")
            self.end_headers()
            self.wfile.write(body)

        def _static(self, filename: str, content_type: str, request_id: str) -> None:
            try:
                body = (STATIC_ROOT / filename).read_bytes()
            except OSError as exc:
                raise ServiceError(404, "static_resource_not_found", "static resource was not found") from exc
            self.send_response(HTTPStatus.OK)
            self._security_headers()
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Security-Policy", (
                "default-src 'self'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; img-src 'self' data: blob:; object-src 'none'; "
                "base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
            ))
            self.send_header("X-Request-ID", request_id)
            self.end_headers()
            self.wfile.write(body)

        def _security_headers(self) -> None:
            self.send_header("Cache-Control", "no-store")
            self.send_header("Pragma", "no-cache")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            origin = self.headers.get("Origin")
            if origin and origin in config.allowed_origins:
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")

        def log_message(self, format: str, *args: Any) -> None:
            # Do not emit request paths, query strings, addresses, or bodies.
            return

    return Handler


def serve(config: ServerConfig | None = None) -> None:
    config = config or ServerConfig.from_env()
    config.validate()
    api = InterviewApi(
        session_ttl_seconds=config.session_ttl_seconds,
        max_sessions=config.max_sessions,
        execution_mode=config.execution_mode,
    )
    server = ThreadingHTTPServer((config.host, config.port), build_handler(api, config))
    stop_janitor = threading.Event()
    janitor_interval = min(30.0, max(1.0, config.session_ttl_seconds / 4))

    def purge_expired_sessions() -> None:
        while not stop_janitor.wait(janitor_interval):
            api.purge_expired()

    janitor = threading.Thread(
        target=purge_expired_sessions,
        name="interview-session-janitor",
        daemon=True,
    )
    janitor.start()
    print(f"clinical-interview-api listening on http://{config.host}:{config.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_janitor.set()
        janitor.join(timeout=2)
        api.purge_all()
        server.server_close()


if __name__ == "__main__":
    serve()
