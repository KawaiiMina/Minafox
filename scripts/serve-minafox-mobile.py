#!/usr/bin/env python3
"""Serve MinaFox start page for Android/LAN UX testing.

This is a dev/test harness, not a production browser wrapper. It serves the
static MinaFox start page and injects runtime endpoint URLs so a phone can talk
to services running on the desktop/LAN host instead of phone-local 127.0.0.1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
START_PAGE = ROOT / "desktop" / "start.html"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
DEFAULT_AI_BROKER_URL = "http://127.0.0.1:8765"
DEFAULT_SEARCH_BASE_URL = "http://127.0.0.1:8888"
CONFIG_MARKER = "  <script>\n"


def normalize_http_url(value: str, *, label: str, allow_query: bool = False) -> str:
    raw = value.strip().rstrip("/")
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{label} must be an http(s) URL, got {value!r}")
    if (parsed.query and not allow_query) or parsed.fragment:
        raise ValueError(f"{label} must not include {'fragment' if allow_query else 'query or fragment'}, got {value!r}")
    return raw


@dataclass(frozen=True)
class RuntimeConfig:
    ai_broker_url: str = DEFAULT_AI_BROKER_URL
    search_base_url: str = DEFAULT_SEARCH_BASE_URL
    search_action_url: str | None = None
    mode: str = "desktop-local"

    def __post_init__(self) -> None:
        object.__setattr__(self, "ai_broker_url", normalize_http_url(self.ai_broker_url, label="ai broker URL"))
        object.__setattr__(self, "search_base_url", normalize_http_url(self.search_base_url, label="search base URL"))
        if self.search_action_url is not None:
            object.__setattr__(self, "search_action_url", normalize_http_url(self.search_action_url, label="search action URL", allow_query=True))
        mode = self.mode.strip() or "desktop-local"
        if mode not in {"desktop-local", "lan-test", "tailscale-test"}:
            raise ValueError("mode must be desktop-local, lan-test, or tailscale-test")
        object.__setattr__(self, "mode", mode)

    @property
    def effective_search_action_url(self) -> str:
        return self.search_action_url or f"{self.search_base_url}/search"

    def as_dict(self) -> dict[str, str]:
        return {
            "mode": self.mode,
            "aiBrokerUrl": self.ai_broker_url,
            "searchBaseUrl": self.search_base_url,
            "searchActionUrl": self.effective_search_action_url,
        }


def config_script(config: RuntimeConfig) -> str:
    payload = json.dumps(config.as_dict(), ensure_ascii=False, sort_keys=True, indent=2)
    return f"  <script>\n    window.MINAFOX_RUNTIME_CONFIG = {payload};\n  </script>\n"


def render_start_page(config: RuntimeConfig) -> str:
    html = START_PAGE.read_text(encoding="utf-8")
    if "window.MINAFOX_RUNTIME_CONFIG =" in html:
        return html
    if CONFIG_MARKER not in html:
        raise RuntimeError("desktop/start.html is missing the script marker for runtime config injection")
    return html.replace(CONFIG_MARKER, config_script(config) + CONFIG_MARKER, 1)


def health_payload(config: RuntimeConfig) -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "minafox-mobile-harness",
        "config": config.as_dict(),
        "warning": "LAN/Tailscale mode is for trusted local UX testing only; do not put provider secrets in static assets.",
    }


def make_handler(config: RuntimeConfig) -> type[BaseHTTPRequestHandler]:
    class MinaFoxMobileHarnessHandler(BaseHTTPRequestHandler):
        server_version = "MinaFoxMobileHarness/0.1"

        def log_message(self, format: str, *args: Any) -> None:
            if os.environ.get("MINAFOX_MOBILE_HARNESS_VERBOSE", "").strip().lower() in {"1", "true", "yes", "on"}:
                super().log_message(format, *args)

        def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            path = urllib.parse.urlsplit(self.path).path
            if path in {"/", "/index.html"}:
                self._send(render_start_page(config).encode("utf-8"), "text/html; charset=utf-8")
                return
            if path == "/health":
                body = json.dumps(health_payload(config), ensure_ascii=False, sort_keys=True).encode("utf-8")
                self._send(body, "application/json; charset=utf-8")
                return
            self._send(json.dumps({"error": "not_found", "path": path}).encode("utf-8"), "application/json; charset=utf-8", status=404)

    return MinaFoxMobileHarnessHandler


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve MinaFox for Android/LAN UX testing.")
    parser.add_argument("--host", default=os.environ.get("MINAFOX_MOBILE_HARNESS_HOST", DEFAULT_HOST), help="bind host; use 0.0.0.0 only on trusted LAN/Tailscale")
    parser.add_argument("--port", type=int, default=int(os.environ.get("MINAFOX_MOBILE_HARNESS_PORT", DEFAULT_PORT)), help="bind port")
    parser.add_argument("--ai-broker-url", default=os.environ.get("MINAFOX_MOBILE_AI_BROKER_URL", DEFAULT_AI_BROKER_URL), help="URL browsers should use for minafox-ai-broker")
    parser.add_argument("--search-base-url", default=os.environ.get("MINAFOX_MOBILE_SEARCH_BASE_URL", DEFAULT_SEARCH_BASE_URL), help="base URL browsers should use for MinaFox SearXNG")
    parser.add_argument("--search-action-url", default=os.environ.get("MINAFOX_MOBILE_SEARCH_ACTION_URL"), help="optional full SearXNG search form action URL; defaults to <search-base-url>/search")
    parser.add_argument("--mode", default=os.environ.get("MINAFOX_MOBILE_HARNESS_MODE", "desktop-local"), choices=("desktop-local", "lan-test", "tailscale-test"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not 1 <= args.port <= 65535:
        print(f"port must be between 1 and 65535, got {args.port}", file=sys.stderr)
        return 2
    try:
        config = RuntimeConfig(ai_broker_url=args.ai_broker_url, search_base_url=args.search_base_url, search_action_url=args.search_action_url, mode=args.mode)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    server = ThreadingHTTPServer((args.host, args.port), make_handler(config))
    print(f"MinaFox mobile harness listening on http://{args.host}:{args.port}", flush=True)
    print(f"  AI broker: {config.ai_broker_url}", flush=True)
    print(f"  Search:    {config.search_base_url}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nMinaFox mobile harness stopped", flush=True)
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
