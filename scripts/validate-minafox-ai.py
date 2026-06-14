#!/usr/bin/env python3
"""Validate MinaFox optional AI Den, local broker, and privacy architecture."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START_HTML = ROOT / "desktop" / "start.html"
DOC = ROOT / "docs" / "ai-provider-architecture.md"
README = ROOT / "README.md"
BROKER = ROOT / "scripts" / "minafox-ai-broker.py"
BROKER_WRAPPER = ROOT / "scripts" / "minafox-ai-broker.sh"
BROKER_TEST = ROOT / "scripts" / "test-minafox-ai-broker.py"
BROKER_SERVICE = ROOT / "systemd" / "user" / "minafox-ai-broker.service"

PROVIDERS = (
    "Ollama",
    "OpenAI",
    "ChatGPT-compatible",
    "Gemini",
    "Claude",
    "OpenRouter",
    "Hermes Gateway",
)

START_SNIPPETS = (
    "Mina AI Den",
    "ai-den-card",
    "ai-provider-select",
    "ai-prompt-input",
    "ai-send-button",
    "ai-status-text",
    "data-privacy-mode=\"local\"",
    "data-privacy-mode=\"cloud\"",
    "data-privacy-mode=\"lan\"",
    "127.0.0.1",
    "No API keys live in this static page",
    "Hermes Gateway can trigger tool-capable agents",
    "minafox-ai-broker",
    "http://127.0.0.1:8765",
    "/providers",
    "/hermes/health",
    "data-ai-response",
    "data-ai-chat-state",
    "POST",
    "/chat",
)

DOC_SNIPPETS = (
    "# MinaFox AI Provider Architecture",
    "localhost-only broker",
    "127.0.0.1",
    "~/.config/minafox/ai.yaml",
    "secrets must not be committed",
    "environment variables",
    "Local / Cloud / LAN",
    "Hermes Gateway can trigger tool-capable agents",
    "http://127.0.0.1:8765",
    "http://127.0.0.1:8642",
    "API_SERVER_KEY",
)

BROKER_SNIPPETS = (
    "GET /health",
    "GET /providers",
    "GET /hermes/health",
    "POST /chat",
    "POST /test-provider",
    "HERMES_API_SERVER_KEY",
    "Ollama chat can be enabled",
    "MINAFOX_AI_ENABLE_OLLAMA_CHAT",
    "http://127.0.0.1:8642",
    "ThreadingHTTPServer",
    "127.0.0.1",
    "8765",
    "ALLOWED_CORS_ORIGINS",
    "assert_loopback_url",
)

WRAPPER_SNIPPETS = (
    "minafox-ai-broker.py",
    "MINAFOX_AI_BROKER_HOST=127.0.0.1",
)

SERVICE_SNIPPETS = (
    "Description=MinaFox local AI broker",
    "ExecStart=/usr/bin/minafox-ai-broker",
    "Environment=MINAFOX_AI_BROKER_HOST=127.0.0.1",
)

FORBIDDEN_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"ANTHROPIC_API_KEY\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"OPENAI_API_KEY\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"API_SERVER_KEY\s*[:=]\s*['\"][^'\"]+['\"]"),
)

FORBIDDEN_STATIC_NETWORK_TOKENS = (
    "XMLHttpRequest",
    "WebSocket",
    "sendBeacon",
    "api.openai.com",
    "generativelanguage.googleapis.com",
    "api.anthropic.com",
    "openrouter.ai/api",
    "http://127.0.0.1:8642",
)


def read(path: Path, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require(label: str, text: str, snippets: tuple[str, ...], failures: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            failures.append(f"{label}: missing {snippet!r}")


def main() -> int:
    failures: list[str] = []
    start = read(START_HTML, failures)
    doc = read(DOC, failures)
    readme = read(README, failures)
    broker = read(BROKER, failures)
    broker_test = read(BROKER_TEST, failures)
    wrapper = read(BROKER_WRAPPER, failures)
    service = read(BROKER_SERVICE, failures)

    require("desktop/start.html", start, START_SNIPPETS, failures)
    require("docs/ai-provider-architecture.md", doc, DOC_SNIPPETS, failures)
    require("scripts/minafox-ai-broker.py", broker, BROKER_SNIPPETS, failures)
    require("scripts/test-minafox-ai-broker.py", broker_test, ("handle_chat_payload", "ollama_request", "provider_disabled"), failures)
    require("scripts/minafox-ai-broker.sh", wrapper, WRAPPER_SNIPPETS, failures)
    require("systemd/user/minafox-ai-broker.service", service, SERVICE_SNIPPETS, failures)
    require("README.md", readme, ("## Mina AI Den", "scripts/validate-minafox-ai.py", "minafox-update", "minafox-ai-broker"), failures)

    for provider in PROVIDERS:
        if provider not in start:
            failures.append(f"desktop/start.html: missing provider {provider!r}")
        if provider not in doc:
            failures.append(f"docs/ai-provider-architecture.md: missing provider {provider!r}")
        if provider not in broker:
            failures.append(f"scripts/minafox-ai-broker.py: missing provider {provider!r}")

    for token in FORBIDDEN_STATIC_NETWORK_TOKENS:
        if token in start:
            failures.append(f"desktop/start.html: static AI surface contains forbidden direct network token {token!r}")
    if "fetch(\"http://127.0.0.1:8765" not in start and "fetch('http://127.0.0.1:8765" not in start:
        failures.append("desktop/start.html: AI surface should only fetch the MinaFox local broker on 127.0.0.1:8765")
    if 'Access-Control-Allow-Origin", "*"' in broker or "Access-Control-Allow-Origin', '*'" in broker:
        failures.append("scripts/minafox-ai-broker.py: must not use wildcard CORS")

    combined = {
        "desktop/start.html": start,
        "docs/ai-provider-architecture.md": doc,
        "README.md": readme,
        "scripts/minafox-ai-broker.py": broker,
        "scripts/test-minafox-ai-broker.py": broker_test,
        "scripts/minafox-ai-broker.sh": wrapper,
        "systemd/user/minafox-ai-broker.service": service,
    }
    for label, text in combined.items():
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                failures.append(f"{label}: contains likely committed API key/token pattern {pattern.pattern}")
        if re.search(r"/home/[A-Za-z0-9_.-]+", text):
            failures.append(f"{label}: contains an author-machine /home/<user> path")

    if failures:
        print("MinaFox AI validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("MinaFox AI validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
