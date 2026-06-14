#!/usr/bin/env python3
"""Validate MinaFox optional AI Den UI and privacy architecture docs."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
START_HTML = ROOT / "desktop" / "start.html"
DOC = ROOT / "docs" / "ai-provider-architecture.md"
README = ROOT / "README.md"

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
)

DISABLED_CONTROL_SNIPPETS = (
    "class=\"ai-provider-select\" disabled",
    "class=\"ai-prompt-input\" disabled",
    "class=\"ai-send-button\" type=\"button\" disabled",
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
)

FORBIDDEN_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"ANTHROPIC_API_KEY\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"OPENAI_API_KEY\s*[:=]\s*['\"][^'\"]+['\"]"),
)

FORBIDDEN_STATIC_NETWORK_TOKENS = (
    "fetch(",
    "XMLHttpRequest",
    "WebSocket",
    "sendBeacon",
    "api.openai.com",
    "generativelanguage.googleapis.com",
    "api.anthropic.com",
    "openrouter.ai/api",
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

    require("desktop/start.html", start, START_SNIPPETS, failures)
    require("desktop/start.html", start, DISABLED_CONTROL_SNIPPETS, failures)
    require("docs/ai-provider-architecture.md", doc, DOC_SNIPPETS, failures)
    require("README.md", readme, ("## Mina AI Den", "scripts/validate-minafox-ai.py", "minafox-update"), failures)

    for provider in PROVIDERS:
        if provider not in start:
            failures.append(f"desktop/start.html: missing provider {provider!r}")
        if provider not in doc:
            failures.append(f"docs/ai-provider-architecture.md: missing provider {provider!r}")

    for token in FORBIDDEN_STATIC_NETWORK_TOKENS:
        if token in start:
            failures.append(f"desktop/start.html: static AI surface contains direct network token {token!r}")

    combined = {
        "desktop/start.html": start,
        "docs/ai-provider-architecture.md": doc,
        "README.md": readme,
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
