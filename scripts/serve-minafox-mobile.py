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
from dataclasses import dataclass, replace
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
    harness_url: str | None = None
    mode: str = "desktop-local"

    def __post_init__(self) -> None:
        object.__setattr__(self, "ai_broker_url", normalize_http_url(self.ai_broker_url, label="ai broker URL"))
        object.__setattr__(self, "search_base_url", normalize_http_url(self.search_base_url, label="search base URL"))
        if self.search_action_url is not None:
            object.__setattr__(self, "search_action_url", normalize_http_url(self.search_action_url, label="search action URL", allow_query=True))
        if self.harness_url is not None:
            object.__setattr__(self, "harness_url", normalize_http_url(self.harness_url, label="harness URL"))
        mode = self.mode.strip() or "desktop-local"
        if mode not in {"desktop-local", "lan-test", "tailscale-test"}:
            raise ValueError("mode must be desktop-local, lan-test, or tailscale-test")
        object.__setattr__(self, "mode", mode)

    @property
    def effective_search_action_url(self) -> str:
        return self.search_action_url or f"{self.search_base_url}/search"

    @property
    def effective_harness_url(self) -> str:
        if self.harness_url:
            return self.harness_url
        if self.mode in {"lan-test", "tailscale-test"}:
            parsed = urllib.parse.urlparse(self.search_base_url)
            hostname = parsed.hostname or DEFAULT_HOST
            return f"{parsed.scheme}://{hostname}:{DEFAULT_PORT}"
        return f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"

    @property
    def health_url(self) -> str:
        return f"{self.effective_harness_url}/health"

    @property
    def android_checklist_url(self) -> str:
        return f"{self.effective_harness_url}/android-checklist"

    def as_dict(self) -> dict[str, str]:
        return {
            "mode": self.mode,
            "aiBrokerUrl": self.ai_broker_url,
            "searchBaseUrl": self.search_base_url,
            "searchActionUrl": self.effective_search_action_url,
            "harnessUrl": self.effective_harness_url,
            "healthUrl": self.health_url,
            "androidChecklistUrl": self.android_checklist_url,
        }


def config_script(config: RuntimeConfig) -> str:
    payload = json.dumps(config.as_dict(), ensure_ascii=False, sort_keys=True, indent=2)
    return f"  <script>\n    window.MINAFOX_RUNTIME_CONFIG = {payload};\n  </script>\n"


def request_host_from_header(host_header: str | None) -> tuple[str, str] | None:
    """Return (host header netloc, hostname) when a request Host is safe to reuse."""
    if not host_header:
        return None
    host = host_header.strip()
    allowed = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.-:[]"
    if not host or any(char not in allowed for char in host):
        return None
    parsed = urllib.parse.urlsplit(f"//{host}")
    if not parsed.hostname:
        return None
    return host, parsed.hostname


def url_with_request_host(url: str, request_hostname: str) -> str:
    """Keep a service URL's scheme, port, path, and query but use the request host."""
    parsed = urllib.parse.urlparse(url)
    hostname = f"[{request_hostname}]" if ":" in request_hostname and not request_hostname.startswith("[") else request_hostname
    netloc = f"{hostname}:{parsed.port}" if parsed.port else hostname
    return urllib.parse.urlunparse(parsed._replace(netloc=netloc))


def config_for_request(config: RuntimeConfig, host_header: str | None) -> RuntimeConfig:
    """Prefer the phone-visible Host header for LAN/Tailscale runtime links."""
    request_host = request_host_from_header(host_header)
    if request_host is None:
        return config
    host, hostname = request_host
    updates: dict[str, str] = {"harness_url": f"http://{host}"}
    if config.mode in {"lan-test", "tailscale-test"}:
        updates["ai_broker_url"] = url_with_request_host(config.ai_broker_url, hostname)
        updates["search_base_url"] = url_with_request_host(config.search_base_url, hostname)
        if config.search_action_url is not None:
            updates["search_action_url"] = url_with_request_host(config.search_action_url, hostname)
    if not updates:
        return config
    return replace(config, **updates)


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


def config_payload(config: RuntimeConfig) -> dict[str, Any]:
    return {
        "service": "minafox-mobile-harness",
        "config": config.as_dict(),
        "warning": "Use only on trusted LAN/Tailscale networks; never expose provider secrets through the harness.",
    }


def android_checklist_payload(config: RuntimeConfig) -> dict[str, Any]:
    return {
        "service": "minafox-mobile-harness",
        "mode": config.mode,
        "url": f"{config.effective_harness_url}/",
        "healthUrl": config.health_url,
        "configUrl": f"{config.effective_harness_url}/config",
        "checklist": [
            "Open the harness on Android and test 360 px, 390 px, 430 px, and tablet-width layouts.",
            "Confirm the page has no sideways panning and the workspace rail/tabs scroll calmly.",
            "Tap the search field and search-mode pills; the query input should stay readable and tappable.",
            "Confirm Search and AI Den endpoint copy mentions the desktop LAN/Tailscale host, not Android 127.0.0.1.",
            "Open /health and /config from the phone to confirm the harness is the reachable desktop service.",
            "Keep the harness on trusted LAN/Tailscale only; never expose port 8766 to the public internet.",
        ],
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
            request_config = config_for_request(config, self.headers.get("Host"))
            if path in {"/", "/index.html"}:
                self._send(render_start_page(request_config).encode("utf-8"), "text/html; charset=utf-8")
                return
            if path == "/health":
                body = json.dumps(health_payload(request_config), ensure_ascii=False, sort_keys=True).encode("utf-8")
                self._send(body, "application/json; charset=utf-8")
                return
            if path == "/config":
                body = json.dumps(config_payload(request_config), ensure_ascii=False, sort_keys=True).encode("utf-8")
                self._send(body, "application/json; charset=utf-8")
                return
            if path == "/android-checklist":
                body = json.dumps(android_checklist_payload(request_config), ensure_ascii=False, sort_keys=True).encode("utf-8")
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
    parser.add_argument("--harness-url", default=os.environ.get("MINAFOX_MOBILE_HARNESS_URL"), help="public URL Android should use for this harness; defaults to localhost or the search host in LAN/Tailscale mode")
    parser.add_argument("--mode", default=os.environ.get("MINAFOX_MOBILE_HARNESS_MODE", "desktop-local"), choices=("desktop-local", "lan-test", "tailscale-test"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not 1 <= args.port <= 65535:
        print(f"port must be between 1 and 65535, got {args.port}", file=sys.stderr)
        return 2
    try:
        config = RuntimeConfig(
            ai_broker_url=args.ai_broker_url,
            search_base_url=args.search_base_url,
            search_action_url=args.search_action_url,
            harness_url=args.harness_url,
            mode=args.mode,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    server = ThreadingHTTPServer((args.host, args.port), make_handler(config))
    print(f"MinaFox mobile harness listening on http://{args.host}:{args.port}", flush=True)
    print(f"  Android:   {config.effective_harness_url}/", flush=True)
    print(f"  Health:    {config.health_url}", flush=True)
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
