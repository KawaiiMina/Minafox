#!/usr/bin/env python3
"""Validate the MinaFox SearXNG overlay.

This is intentionally stdlib-only so it can run on a fresh Arch install.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "searxng/Dockerfile",
    "searxng/docker-compose.yml",
    "searxng/settings.yml",
    "searxng/uwsgi.ini",
    "searxng/theme/minafox.css",
    "searxng/README.md",
    "scripts/install-minafox-searxng-arch.sh",
]

REQUIRED_THEME_TOKENS = [
    "--mf-bg",
    "--mf-ink",
    "--mf-muted",
    "--mf-lavender",
    "--mf-violet",
    "--mf-pink",
    "--mf-rose",
    "--mf-glass",
    "--mf-border",
    "--mf-glow",
]

REQUIRED_THEME_SELECTORS = [
    "#main_results",
    "#search",
    "#q",
    ".result",
    ".result h3",
    ".suggestions",
    ".infobox",
    "@media (max-width: 760px)",
    "@media (prefers-reduced-motion: reduce)",
    ":focus-visible",
]

REQUIRED_SETTINGS_SNIPPETS = [
    "instance_name: \"MinaFox Search\"",
    "default_theme: simple",
    "simple_style: minafox",
    "search_on_category_select: false",
    "method: POST",
    "safe_search: 1",
    "autocomplete: \"duckduckgo\"",
    "formats:",
    "- html",
]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.exists():
        raise AssertionError(f"missing required file: {rel}")
    return path.read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise AssertionError(f"{label} missing required snippet: {needle}")


def main() -> int:
    failures: list[str] = []

    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            failures.append(f"missing required file: {rel}")

    if failures:
        print("MinaFox SearXNG validation: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    theme = read("searxng/theme/minafox.css")
    settings = read("searxng/settings.yml")
    compose = read("searxng/docker-compose.yml")
    dockerfile = read("searxng/Dockerfile")
    installer = read("scripts/install-minafox-searxng-arch.sh")
    start_page = read("desktop/start.html")
    readme = read("README.md")
    overlay_readme = read("searxng/README.md")

    checks: list[tuple[str, str, str]] = []
    checks += [(theme, token, "theme") for token in REQUIRED_THEME_TOKENS]
    checks += [(theme, selector, "theme") for selector in REQUIRED_THEME_SELECTORS]
    checks += [(settings, snippet, "settings") for snippet in REQUIRED_SETTINGS_SNIPPETS]
    checks += [
        (compose, "127.0.0.1:8888:8080", "compose"),
        (compose, "no-new-privileges:true", "compose"),
        (compose, "cap_drop:", "compose"),
        (compose, "MinaFox SearXNG", "compose"),
        (dockerfile, "searxng/searxng", "Dockerfile"),
        (dockerfile, "minafox.min.css", "Dockerfile"),
        (installer, "docker compose", "installer"),
        (installer, "podman compose", "installer"),
        (installer, "grep -E '^SEARXNG_SECRET_KEY='", "installer"),
        (installer, "^[A-Za-z0-9._~+=:@-]{32,128}$", "installer"),
        (installer, "http://127.0.0.1:8888/", "installer"),
        (start_page, "method=\"post\"", "start page"),
        (start_page, "http://127.0.0.1:8888/search", "start page"),
        (start_page, "Search MinaFox SearXNG", "start page"),
        (readme, "## MinaFox SearXNG search", "README"),
        (overlay_readme, "docker compose", "searxng README"),
        (overlay_readme, "http://127.0.0.1:8888/", "searxng README"),
    ]

    for text, needle, label in checks:
        try:
            assert_contains(text, needle, label)
        except AssertionError as exc:
            failures.append(str(exc))

    if re.search(r"ports:\s*\n\s*-\s*[\"']?8888:8080", compose):
        failures.append("compose exposes SearXNG on all interfaces; bind to 127.0.0.1")

    if "source .env" in installer or ". .env" in installer:
        failures.append("installer must parse .env as data, not source it as shell code")

    if failures:
        print("MinaFox SearXNG validation: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("MinaFox SearXNG validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
