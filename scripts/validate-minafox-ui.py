#!/usr/bin/env python3
"""Validate the MinaFox hybrid UI assets.

This is the repeatable UI test gate. It checks the MinaFox browser-chrome
tokens/selectors, start-page structure, required Firefox custom-CSS preference,
scoped content CSS, and leftover scaffold markers.
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
USER_CHROME = ROOT / "profile" / "userChrome.css"
START_HTML = ROOT / "desktop" / "start.html"
USER_JS = ROOT / "profile" / "user.js"
USER_CONTENT = ROOT / "profile" / "userContent.css"
BRAND_LORE = ROOT / "docs" / "brand-lore.md"


class StartPageParser(HTMLParser):
    """Small HTML collector sufficient for this validation script."""

    def __init__(self) -> None:
        super().__init__()
        self.classes: set[str] = set()
        self.ids: set[str] = set()
        self.forms: list[dict[str, str]] = []
        self.inputs: list[dict[str, str]] = []
        self.anchors: list[dict[str, str]] = []
        self.buttons: list[dict[str, str]] = []
        self.text_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        if attr_map.get("class"):
            self.classes.update(attr_map["class"].split())
        if attr_map.get("id"):
            self.ids.add(attr_map["id"])
        if tag == "form":
            self.forms.append(attr_map)
        if tag == "input":
            self.inputs.append(attr_map)
        if tag == "a":
            self.anchors.append(attr_map)
        if tag == "button":
            self.buttons.append(attr_map)

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text_chunks.append(data.strip())

    @property
    def text(self) -> str:
        return " ".join(self.text_chunks)


def read_text(path: Path, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require_contains(label: str, haystack: str, needles: Iterable[str], failures: list[str]) -> None:
    for needle in needles:
        if needle not in haystack:
            failures.append(f"{label}: missing {needle!r}")


def require_regex(label: str, haystack: str, pattern: str, description: str, failures: list[str]) -> None:
    if not re.search(pattern, haystack, re.MULTILINE):
        failures.append(f"{label}: missing {description}")


def validate_user_chrome(failures: list[str]) -> str:
    css = read_text(USER_CHROME, failures)
    if not css:
        return css

    require_contains(
        "profile/userChrome.css",
        css,
        [
            "--mf-lavender",
            "--mf-glass",
            "--mf-pink",
            "--mf-command-glow",
            "--mf-rail-bg",
            "--mf-pill-active",
            "#navigator-toolbox",
            "#sidebar-box",
            "#urlbar-container",
            "#urlbar-background",
            '#urlbar[focused="true"]',
            ".tabbrowser-tab[selected]",
            "menupopup",
        ],
        failures,
    )
    require_regex(
        "profile/userChrome.css",
        css,
        r"#sidebar-box|sidebar",
        "sidebar styling selector (#sidebar-box or another sidebar selector)",
        failures,
    )
    return css


def validate_start_html(failures: list[str]) -> str:
    html = read_text(START_HTML, failures)
    if not html:
        return html

    parser = StartPageParser()
    try:
        parser.feed(html)
    except Exception as exc:  # HTMLParser is forgiving; this catches unexpected parser errors.
        failures.append(f"desktop/start.html: parser error: {exc}")
        return html

    if "minafox-shell" not in parser.classes and "minafox-shell" not in parser.ids:
        failures.append("desktop/start.html: missing minafox-shell class or id")

    has_search_form = any(
        form.get("method", "").lower() == "post"
        and form.get("action") == "http://127.0.0.1:8888/search"
        and (form.get("role") == "search" or "search" in form.get("class", "").lower())
        for form in parser.forms
    )
    has_query_input = any(input_attrs.get("name") == "q" and input_attrs.get("type") == "search" for input_attrs in parser.inputs)
    if not (has_search_form and has_query_input):
        failures.append("desktop/start.html: missing local SearXNG POST search form with search query input")

    required_classes = {
        "minafox-desktop",
        "workspace-rail",
        "workspace-bubbles",
        "workspace-bubble",
        "soft-tabs",
        "soft-tab-list",
        "command-bar",
        "quick-card",
        "dashboard-grid",
        "widget-grid",
        "focus-timer-card",
        "notes-card",
        "lofi-card",
        "roadmap-card",
        "design-system-card",
    }
    for class_name in sorted(required_classes - parser.classes):
        failures.append(f"desktop/start.html: missing required class {class_name!r}")

    expected_links = {
        "ChatGPT": "https://chat.openai.com/",
        "GitHub": "https://github.com/",
        "YouTube": "https://youtube.com/",
    }
    hrefs = {anchor.get("href", "") for anchor in parser.anchors}
    for label, href in expected_links.items():
        if href not in hrefs:
            failures.append(f"desktop/start.html: missing preserved quick link {label} ({href})")

    action_targets = {button.get("data-about-target", "") for button in parser.buttons}
    for label, target in {"New Tab": "about:blank", "Settings": "about:preferences", "Profiles": "about:profiles"}.items():
        if target not in action_targets:
            failures.append(f"desktop/start.html: missing safe start-page action button for {label} ({target})")
    for blocked in {"about:newtab", "about:preferences", "about:profiles"}:
        if blocked in hrefs:
            failures.append(f"desktop/start.html: privileged about URL should not be a direct href: {blocked}")
    if 0 <= html.find("MinaFox roadmap") < html.find("Mina AI Den"):
        failures.append("desktop/start.html: Mina AI Den should appear before roadmap so it is visible on the first screen")
    require_contains(
        "desktop/start.html",
        html,
        ["data-action-status", "copyAboutCommand", "data-about-target"],
        failures,
    )

    require_contains(
        "desktop/start.html",
        html,
        [":focus-visible", "@media (max-width", "@media (prefers-reduced-motion"],
        failures,
    )

    if "MinaFox" not in parser.text:
        failures.append("desktop/start.html: missing MinaFox brand text")
    return html


def validate_user_js(failures: list[str]) -> str:
    prefs = read_text(USER_JS, failures)
    if not prefs:
        return prefs

    require_regex(
        "profile/user.js",
        prefs,
        r'user_pref\(\s*["\']toolkit\.legacyUserProfileCustomizations\.stylesheets["\']\s*,\s*true\s*\)\s*;',
        "toolkit.legacyUserProfileCustomizations.stylesheets=true",
        failures,
    )
    return prefs


def validate_user_content(failures: list[str]) -> str:
    css = read_text(USER_CONTENT, failures)
    if not css:
        return css

    require_contains(
        "profile/userContent.css",
        css,
        [
            "@-moz-document",
            'url("about:home")',
            'url("about:newtab")',
            'url-prefix("__MINAFOX_START_URL__")',
            ":focus-visible",
        ],
        failures,
    )

    before_scope = css.split("@-moz-document", 1)[0]
    if "body" in before_scope or ":root" in before_scope:
        failures.append("profile/userContent.css: contains global body/:root styling before @-moz-document scope")

    return css


def validate_brand_lore(failures: list[str]) -> str:
    lore = read_text(BRAND_LORE, failures)
    if not lore:
        return lore

    require_contains(
        "docs/brand-lore.md",
        lore,
        [
            "# MinaFox Brand Lore",
            "Mascot name: Mina",
            "Mina is",
            "Logo/mascot direction",
            "Voice and personality",
            "Accessibility and privacy",
        ],
        failures,
    )
    return lore


def validate_no_scaffold_markers(files: dict[str, str], failures: list[str]) -> None:
    scaffold_markers = re.compile(r"\b(?:TODO|FIXME|XXX|LOREM IPSUM)\b", re.IGNORECASE)
    for label, content in files.items():
        for line_number, line in enumerate(content.splitlines(), start=1):
            if scaffold_markers.search(line):
                failures.append(f"{label}:{line_number}: leftover scaffold marker: {line.strip()}")


def main() -> int:
    failures: list[str] = []
    contents = {
        "profile/userChrome.css": validate_user_chrome(failures),
        "desktop/start.html": validate_start_html(failures),
        "profile/user.js": validate_user_js(failures),
        "profile/userContent.css": validate_user_content(failures),
        "docs/brand-lore.md": validate_brand_lore(failures),
    }
    validate_no_scaffold_markers(contents, failures)

    if failures:
        print("MinaFox UI validation: FAIL")
        print(f"Repository: {ROOT}")
        print(f"Failures: {len(failures)}")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("MinaFox UI validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
