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
    "searxng/theme/minafox-categories.js",
    "searxng/patch-base-template.py",
    "searxng/README.md",
    "scripts/install-minafox-searxng-arch.sh",
    "systemd/user/minafox-searxng.service",
]

REQUIRED_THEME_TOKENS = [
    "--mf-bg",
    "--mf-cosmic-bg",
    "--mf-ink",
    "--mf-muted",
    "--mf-lavender",
    "--mf-violet",
    "--mf-pink",
    "--mf-rose",
    "--mf-glass",
    "--mf-border",
    "--mf-glow",
    "cosmic fox",
    "privacy-minded",
    "gentle",
    "MinaFox",
    "Calm local metasearch",
    "body::before",
    "body::after",
    ".title h1::before",
    ".title h1::after",
]

REQUIRED_THEME_SELECTORS = [
    "#main_results",
    "#search",
    "#main_results #search",
    "#main_results #search_header",
    "flex-wrap: wrap",
    "#main_results #search_view",
    "#main_results .search_box",
    "#main_results #categories",
    "--mf-results-logo-width: 64px",
    "--mf-results-search-indent",
    "--mf-results-search-rail",
    "box-sizing: border-box",
    "margin: 14px 0 12px var(--mf-results-search-indent)",
    "overflow-x: hidden",
    "justify-content: space-between",
    "#categories_container .category_checkbox",
    "flex: 1 1 0",
    "min-width: 0",
    "#categories .category_name",
    "clip-path: inset(50%)",
    "#categories label",
    "min-width: 34px",
    ".autocomplete .help",
    "display: none",
    "order: 3",
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
    "instance_name: \"MinaFox\"",
    "default_theme: simple",
    "simple_style: dark",
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


def validate_no_direct_browser_search_providers(browser_assets: dict[str, str], failures: list[str]) -> None:
    forbidden_patterns = [
        r"(?i)(?:https?:)?//(?:www\.)?google\.",
        r"(?i)(?:https?:)?//scholar\.google\.",
        r"(?i)(?:https?:)?//(?:www\.)?duckduckgo\.com(?:/|$)",
        r"(?i)(?:https?:)?//search\.brave\.com(?:/|$)",
        r"(?i)(?:https?:)?//(?:www\.)?startpage\.com(?:/|$)",
        r"(?i)(?:https?:)?//(?:www\.)?bing\.com(?:/|$)",
        r"(?i)(?:https?:)?//search\.yahoo\.com(?:/|$)",
    ]
    for label, text in browser_assets.items():
        for forbidden in forbidden_patterns:
            if re.search(forbidden, text):
                failures.append(
                    f"{label}: browser-facing search must route through local SearXNG, "
                    f"not direct external endpoint matching: {forbidden}"
                )


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
    categories_js = read("searxng/theme/minafox-categories.js")
    settings = read("searxng/settings.yml")
    compose = read("searxng/docker-compose.yml")
    dockerfile = read("searxng/Dockerfile")
    patcher = read("searxng/patch-base-template.py")
    installer = read("scripts/install-minafox-searxng-arch.sh")
    systemd_unit = read("systemd/user/minafox-searxng.service")
    start_page = read("desktop/start.html")
    user_js = read("profile/user.js")
    user_content_css = read("profile/userContent.css")
    mobile_harness = read("scripts/serve-minafox-mobile.py")
    policies = read("distribution/policies.json")
    readme = read("README.md")
    overlay_readme = read("searxng/README.md")
    search_wiki = read("docs/wiki/MinaFox-Search.md")
    repository_map = read("docs/wiki/Repository-Map.md")
    pkgbuild = read("packaging/arch/minafox-profile-git/PKGBUILD")

    checks: list[tuple[str, str, str]] = []
    checks += [(theme, token, "theme") for token in REQUIRED_THEME_TOKENS]
    checks += [(theme, selector, "theme") for selector in REQUIRED_THEME_SELECTORS]
    checks += [(settings, snippet, "settings") for snippet in REQUIRED_SETTINGS_SNIPPETS]
    checks += [
        (compose, "127.0.0.1:8888:8080", "compose"),
        (compose, "./etc:/etc/searxng:ro", "compose"),
        (compose, "no-new-privileges:true", "compose"),
        (compose, "cap_drop:", "compose"),
        (compose, "INSTANCE_NAME=MinaFox", "compose"),
        (dockerfile, "searxng/searxng", "Dockerfile"),
        (dockerfile, "minafox.min.css", "Dockerfile"),
        (dockerfile, "dark.min.css", "Dockerfile"),
        (dockerfile, "sxng-ltr.min.css", "Dockerfile"),
        (dockerfile, "sxng-rtl.min.css", "Dockerfile"),
        (dockerfile, "bundled stylesheet files", "Dockerfile"),
        (dockerfile, "patch-base-template.py", "Dockerfile"),
        (dockerfile, "base.html", "Dockerfile"),
        (dockerfile, "themes/simple/css/minafox.min.css", "Dockerfile"),
        (dockerfile, "theme/minafox-categories.js", "Dockerfile"),
        (dockerfile, "themes/simple/js/minafox-categories.js", "Dockerfile"),
        (patcher, "expected limiter/client CSS anchor not found", "base template patcher"),
        (patcher, "themes/simple/css/minafox.min.css", "base template patcher"),
        (patcher, "themes/simple/js/minafox-categories.js", "base template patcher"),
        (patcher, "MINAFOX_SCRIPT", "base template patcher"),
        (patcher, "CATEGORIES_TEMPLATE", "base template patcher"),
        (patcher, "CATEGORY_HELP_LINE", "base template patcher"),
        (patcher, "patch_categories_template", "base template patcher"),
        (patcher, "if MINAFOX_LINK not in text", "base template patcher"),
        (patcher, "if MINAFOX_SCRIPT not in text", "base template patcher"),
        (categories_js, "categoryInputs", "category script"),
        (categories_js, "checked = false", "category script"),
        (categories_js, "At least one MinaFox category stays selected", "category script"),
        (categories_js, "submitCategorySearch", "category script"),
        (categories_js, "requestSubmit", "category script"),
        (categories_js, "selected.form", "category script"),
        (categories_js, "change", "category script"),
        (dockerfile, "Use the upstream-compatible dark style name", "Dockerfile"),
        (installer, "docker compose", "installer"),
        (installer, "podman compose", "installer"),
        (installer, "grep -E '^SEARXNG_SECRET_KEY='", "installer"),
        (installer, "^[A-Za-z0-9._~+=:@-]{32,128}$", "installer"),
        (installer, "copy_overlay_file patch-base-template.py", "installer"),
        (installer, "copy_overlay_file theme/minafox-categories.js", "installer"),
        (installer, "cp settings.yml.local etc/settings.yml", "installer"),
        (installer, "chmod 644 settings.yml.local etc/settings.yml etc/uwsgi.ini", "installer"),
        (installer, "http://127.0.0.1:8888/", "installer"),
        (installer, "SOURCE_SEARXNG_DIR=\"/usr/share/minafox/searxng\"", "installer"),
        (installer, "DATA_HOME=\"${XDG_DATA_HOME:-$HOME/.local/share}\"", "installer"),
        (installer, "RUNTIME_SEARXNG_DIR=\"$DATA_HOME/minafox/searxng\"", "installer"),
        (installer, "install-service", "installer"),
        (installer, "escaped_script_path", "installer"),
        (installer, "${escaped_script_path//&/", "installer"),
        (installer, "${escaped_script_path//|/", "installer"),
        (installer, "sed \"s|/usr/share/minafox/scripts/install-minafox-searxng-arch.sh|$escaped_script_path|g\"", "installer"),
        (installer, "Installed user unit override", "installer"),
        (installer, "systemctl --user enable --now minafox-searxng.service", "installer"),
        (installer, "service)", "installer"),
        (installer, "\"${compose_cmd[@]}\" up --build", "installer"),
        (installer, "stop|down)", "installer"),
        (installer, "\"${compose_cmd[@]}\" down", "installer"),
        (installer, "logs)", "installer"),
        (installer, "journalctl --user -u minafox-searxng.service", "installer"),
        (systemd_unit, "[Unit]", "systemd unit"),
        (systemd_unit, "Description=MinaFox local SearXNG search service", "systemd unit"),
        (systemd_unit, "ExecStart=/usr/share/minafox/scripts/install-minafox-searxng-arch.sh service", "systemd unit"),
        (systemd_unit, "ExecStop=/usr/share/minafox/scripts/install-minafox-searxng-arch.sh stop", "systemd unit"),
        (systemd_unit, "WantedBy=default.target", "systemd unit"),
        (start_page, "method=\"post\"", "start page"),
        (start_page, "http://127.0.0.1:8888/search", "start page"),
        (start_page, "Search MinaFox SearXNG", "start page"),
        (start_page, "data-search-category=\"images\"", "start page"),
        (start_page, "data-search-category=\"videos\"", "start page"),
        (start_page, "data-search-status", "start page"),
        (start_page, "systemctl --user status minafox-searxng.service", "start page"),
        (start_page, "journalctl --user -u minafox-searxng.service -f", "start page"),
        (start_page, "setSearchCategory", "start page"),
        (start_page, "category_${category}", "start page"),
        (start_page, "Default search: MinaFox SearXNG", "start page"),
        (start_page, "Engines are managed through SearXNG", "start page"),
        (theme, "Results polish", "theme"),
        (theme, "#main_results #results.only_template_images #urls", "theme"),
        (theme, "#categories .category_checkbox input:checked + label", "theme"),
        (theme, "grid-template-columns: minmax(160px, 240px) minmax(0, 1fr)", "theme"),
        (pkgbuild, "desktop/start.html", "PKGBUILD"),
        (pkgbuild, "searxng/theme/minafox.css", "PKGBUILD"),
        (pkgbuild, "searxng/theme/minafox-categories.js", "PKGBUILD"),
        (pkgbuild, "searxng/patch-base-template.py", "PKGBUILD"),
        (pkgbuild, "docker-compose", "PKGBUILD"),
        (pkgbuild, "podman-compose", "PKGBUILD"),
        (readme, "## MinaFox SearXNG search", "README"),
        (readme, "MinaFox uses local SearXNG as the default MinaFox search layer", "README"),
        (readme, "Future search-engine support is configured through SearXNG", "README"),
        (readme, "install-service", "README"),
        (readme, "systemctl --user status minafox-searxng.service", "README"),
        (search_wiki, "# MinaFox Search", "Search wiki"),
        (search_wiki, "MinaFox uses local SearXNG as the default MinaFox search layer", "Search wiki"),
        (search_wiki, "MinaFox UI → local SearXNG → upstream engines", "Search wiki"),
        (search_wiki, "Future search-engine support is configured through SearXNG", "Search wiki"),
        (search_wiki, "Do not add direct browser-side search integrations", "Search wiki"),
        (repository_map, "MinaFox-Search.md", "Repository map"),
        (overlay_readme, "docker compose", "searxng README"),
        (overlay_readme, "default MinaFox search layer", "searxng README"),
        (overlay_readme, "engines are managed through SearXNG", "searxng README"),
        (overlay_readme, "http://127.0.0.1:8888/", "searxng README"),
        (overlay_readme, "~/.local/share/minafox/searxng", "searxng README"),
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

    validate_no_direct_browser_search_providers(
        {
            "desktop/start.html": start_page,
            "profile/user.js": user_js,
            "profile/userContent.css": user_content_css,
            "scripts/serve-minafox-mobile.py": mobile_harness,
        },
        failures,
    )
    if '"SearchEngines"' in policies:
        failures.append("distribution/policies.json must not set browser-side search engines; keep upstream selection in SearXNG")

    if re.search(r"(?m)^#search,\s*\n\s*\.search_box\s*\{", theme):
        failures.append("theme must not style the whole results-page #search form as a glass card; style #main_index #search and .search_box separately")

    if "#main_results #search {" in theme and "background: transparent" not in theme:
        failures.append("results-page #search must reset to a transparent layout container")

    if failures:
        print("MinaFox SearXNG validation: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("MinaFox SearXNG validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
