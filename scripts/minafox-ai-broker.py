#!/usr/bin/env python3
"""MinaFox local AI broker.

Endpoints:
- GET /health
- GET /providers
- GET /hermes/health
- POST /chat

The broker is intentionally localhost-only by default. It keeps Hermes and
future provider credentials out of the static MinaFox start page.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_HERMES_BASE_URL = "http://127.0.0.1:8642"
MAX_BODY_BYTES = 64 * 1024
ALLOWED_CORS_ORIGINS = {"null", "file://", "http://127.0.0.1:8765", "http://localhost:8765"}

PROVIDERS: list[dict[str, Any]] = [
    {
        "id": "ollama",
        "name": "Ollama",
        "label": "Ollama — Local",
        "privacy_mode": "local",
        "status": "planned",
        "enabled": False,
        "notes": "Local model provider; not wired in this broker sprint.",
    },
    {
        "id": "openai_compatible",
        "name": "OpenAI / ChatGPT-compatible",
        "label": "OpenAI / ChatGPT-compatible — Cloud",
        "privacy_mode": "cloud",
        "status": "planned",
        "enabled": False,
        "notes": "Cloud provider; keys must stay in local config/env/keyring, never the page.",
    },
    {
        "id": "gemini",
        "name": "Gemini",
        "label": "Gemini — Cloud",
        "privacy_mode": "cloud",
        "status": "planned",
        "enabled": False,
        "notes": "Cloud provider; not enabled until a secrets backend exists.",
    },
    {
        "id": "claude",
        "name": "Claude",
        "label": "Claude — Cloud",
        "privacy_mode": "cloud",
        "status": "planned",
        "enabled": False,
        "notes": "Cloud provider; not enabled until a secrets backend exists.",
    },
    {
        "id": "openrouter",
        "name": "OpenRouter",
        "label": "OpenRouter — Cloud",
        "privacy_mode": "cloud",
        "status": "planned",
        "enabled": False,
        "notes": "OpenAI-compatible cloud router; not enabled until a secrets backend exists.",
    },
    {
        "id": "hermes_gateway",
        "name": "Hermes Gateway",
        "label": "Hermes Gateway — LAN / advanced",
        "privacy_mode": "lan",
        "status": "detectable",
        "enabled": False,
        "notes": "Hermes Gateway can trigger tool-capable agents. Chat stays disabled until explicit safety wiring exists.",
    },
]


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def env_port(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        port = int(raw)
    except ValueError:
        raise SystemExit(f"{name} must be an integer, got {raw!r}") from None
    if not 1 <= port <= 65535:
        raise SystemExit(f"{name} must be between 1 and 65535, got {port}")
    return port


def assert_loopback_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Hermes API Server URL must be loopback-only by default")


def json_bytes(payload: dict[str, Any], status: int = 200) -> tuple[int, bytes]:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return status, body


def hermes_request(path: str, timeout: float = 2.0) -> dict[str, Any]:
    base_url = os.environ.get("HERMES_API_SERVER_URL", DEFAULT_HERMES_BASE_URL).rstrip("/")
    try:
        assert_loopback_url(base_url)
    except ValueError as exc:
        return {
            "available": False,
            "status_code": None,
            "elapsed_ms": 0,
            "base_url": base_url,
            "error": str(exc),
        }
    key = os.environ.get("HERMES_API_SERVER_KEY") or os.environ.get("API_SERVER_KEY")
    request = urllib.request.Request(base_url + path)
    request.add_header("Accept", "application/json")
    if key:
        request.add_header("Authorization", f"Bearer {key}")
    started = time.time()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(256 * 1024)
            try:
                data = json.loads(body.decode("utf-8")) if body else {}
            except json.JSONDecodeError:
                data = {"raw": body.decode("utf-8", errors="replace")[:1000]}
            return {
                "available": 200 <= response.status < 300,
                "status_code": response.status,
                "elapsed_ms": int((time.time() - started) * 1000),
                "base_url": base_url,
                "data": data,
            }
    except urllib.error.HTTPError as exc:
        return {
            "available": False,
            "status_code": exc.code,
            "elapsed_ms": int((time.time() - started) * 1000),
            "base_url": base_url,
            "error": exc.reason,
        }
    except Exception as exc:  # noqa: BLE001 - return health details, do not crash the broker
        return {
            "available": False,
            "status_code": None,
            "elapsed_ms": int((time.time() - started) * 1000),
            "base_url": base_url,
            "error": type(exc).__name__,
        }


class MinaFoxBrokerHandler(BaseHTTPRequestHandler):
    server_version = "MinaFoxAIBroker/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        if env_bool("MINAFOX_AI_BROKER_VERBOSE"):
            super().log_message(format, *args)

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        status_code, body = json_bytes(payload, status)
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        origin = self.headers.get("Origin")
        if origin in ALLOWED_CORS_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802 - stdlib handler API
        self._send_json({"ok": True})

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        path = urllib.parse.urlsplit(self.path).path
        if path == "/health":
            self._send_json({
                "status": "ok",
                "service": "minafox-ai-broker",
                "host": os.environ.get("MINAFOX_AI_BROKER_HOST", DEFAULT_HOST),
                "port": env_port("MINAFOX_AI_BROKER_PORT", DEFAULT_PORT),
            })
            return
        if path == "/providers":
            hermes = hermes_request("/health")
            providers = [dict(provider) for provider in PROVIDERS]
            for provider in providers:
                if provider["id"] == "hermes_gateway":
                    provider["available"] = hermes["available"]
                    provider["health"] = hermes
            self._send_json({
                "status": "ok",
                "broker": "minafox-ai-broker",
                "providers": providers,
                "safety": "No API keys live in the static page. Hermes Gateway can trigger tool-capable agents.",
            })
            return
        if path == "/hermes/health":
            self._send_json({"status": "ok", "hermes": hermes_request("/health")})
            return
        self._send_json({"error": "not_found", "path": path}, status=404)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        path = urllib.parse.urlsplit(self.path).path
        if path != "/chat":
            self._send_json({"error": "not_found", "path": path}, status=404)
            return
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except ValueError:
            self._send_json({"error": "invalid_content_length"}, status=400)
            return
        if length > MAX_BODY_BYTES:
            self._send_json({"error": "request_too_large", "max_body_bytes": MAX_BODY_BYTES}, status=413)
            return
        _ = self.rfile.read(length) if length else b""
        if not env_bool("MINAFOX_AI_BROKER_ENABLE_CHAT"):
            self._send_json({
                "error": "chat_disabled",
                "message": "MinaFox broker is running, but chat is disabled until explicit Hermes safety UX is implemented.",
                "safety": "Hermes Gateway can trigger tool-capable agents.",
            }, status=403)
            return
        self._send_json({
            "error": "not_implemented",
            "message": "Chat enablement is reserved for the next safety-reviewed sprint.",
        }, status=501)


def main() -> int:
    host = os.environ.get("MINAFOX_AI_BROKER_HOST", DEFAULT_HOST)
    port = env_port("MINAFOX_AI_BROKER_PORT", DEFAULT_PORT)
    if host not in {"127.0.0.1", "localhost", "::1"}:
        print(f"Refusing non-loopback bind: {host}", file=sys.stderr)
        return 2
    server = ThreadingHTTPServer((host, port), MinaFoxBrokerHandler)
    print(f"MinaFox AI broker listening on http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMinaFox AI broker stopped", flush=True)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
