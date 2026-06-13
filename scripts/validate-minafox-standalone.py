#!/usr/bin/env python3
"""Validate MinaFox standalone-wrapper install assets.

This gate checks the first standalone milestone: MinaFox should be launched as
`minafox`, keep its own profile/app identity, and avoid falling back to default
Firefox branding in the desktop entry.
"""
from __future__ import annotations

import os
import re
import stat
import sys
from configparser import ConfigParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "minafox-launcher.sh"
DESKTOP = ROOT / "desktop" / "minafox.desktop"
INSTALLER = ROOT / "scripts" / "install-minafox-arch.sh"
README = ROOT / "README.md"


REQUIRED_LAUNCHER_SNIPPETS = (
    "MOZ_ENABLE_WAYLAND=1",
    "--name minafox",
    "--class MinaFox",
    'PROFILE_DIR="${MINAFOX_PROFILE_DIR:-$HOME/.mozilla/firefox/minafox}"',
    'exec "${MINAFOX_FIREFOX_BIN:-firefox}"',
)

REQUIRED_INSTALLER_SNIPPETS = (
    "BIN_DIR=\"$HOME/.local/bin\"",
    "install -m 0755 \"$ROOT_DIR/scripts/minafox-launcher.sh\" \"$BIN_DIR/minafox\"",
    "Launch with: minafox",
)

REQUIRED_README_SNIPPETS = (
    "minafox",
    "Standalone wrapper",
    "source fork later",
    "scripts/validate-minafox-standalone.py",
)


class DesktopParser(ConfigParser):
    def optionxform(self, optionstr: str) -> str:  # preserve desktop key case
        return optionstr


def read_text(path: Path, failures: list[str]) -> str:
    if not path.exists():
        failures.append(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8")


def require_contains(label: str, haystack: str, snippets: tuple[str, ...], failures: list[str]) -> None:
    for snippet in snippets:
        if snippet not in haystack:
            failures.append(f"{label}: missing {snippet!r}")


def validate_launcher(failures: list[str]) -> str:
    text = read_text(LAUNCHER, failures)
    if not text:
        return text

    mode = LAUNCHER.stat().st_mode
    if not (mode & stat.S_IXUSR):
        failures.append("scripts/minafox-launcher.sh: not executable by owner")

    if not text.startswith("#!/usr/bin/env bash\nset -euo pipefail"):
        failures.append("scripts/minafox-launcher.sh: missing bash shebang plus set -euo pipefail")

    require_contains("scripts/minafox-launcher.sh", text, REQUIRED_LAUNCHER_SNIPPETS, failures)

    if re.search(r"firefox\s+--profile\s+\$HOME", text):
        failures.append("scripts/minafox-launcher.sh: profile path should be configurable via MINAFOX_PROFILE_DIR")

    return text


def validate_desktop(failures: list[str]) -> str:
    text = read_text(DESKTOP, failures)
    if not text:
        return text

    parser = DesktopParser(interpolation=None)
    try:
        parser.read_string(text)
    except Exception as exc:
        failures.append(f"desktop/minafox.desktop: parse error: {exc}")
        return text

    if "Desktop Entry" not in parser:
        failures.append("desktop/minafox.desktop: missing [Desktop Entry] section")
        return text

    entry = parser["Desktop Entry"]
    expected = {
        "Name": "MinaFox",
        "Exec": "minafox %u",
        "Icon": "minafox",
        "StartupWMClass": "MinaFox",
    }
    for key, expected_value in expected.items():
        actual = entry.get(key)
        if actual != expected_value:
            failures.append(f"desktop/minafox.desktop: expected {key}={expected_value!r}, got {actual!r}")

    if "firefox" in entry.get("Exec", "").lower():
        failures.append("desktop/minafox.desktop: Exec should call minafox, not firefox directly")

    return text


def validate_installer(failures: list[str]) -> str:
    text = read_text(INSTALLER, failures)
    if not text:
        return text
    require_contains("scripts/install-minafox-arch.sh", text, REQUIRED_INSTALLER_SNIPPETS, failures)
    return text


def validate_readme(failures: list[str]) -> str:
    text = read_text(README, failures)
    if not text:
        return text
    require_contains("README.md", text, REQUIRED_README_SNIPPETS, failures)
    return text


def validate_no_placeholders_or_host_paths(contents: dict[str, str], failures: list[str]) -> None:
    forbidden = ("/" + "home" + "/" + "hermes", "/" + "hermes" + "/" + "home")
    for label, text in contents.items():
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "__MINAFOX_START_URL__" in line and label not in {
                "profile/user.js",
                "profile/userContent.css",
                "distribution/policies.json",
                "scripts/install-minafox-arch.sh",
            }:
                failures.append(f"{label}:{line_no}: unexpected MinaFox template placeholder")
            for marker in forbidden:
                if marker in line:
                    failures.append(f"{label}:{line_no}: contains author-machine path {marker!r}")


def main() -> int:
    failures: list[str] = []
    contents = {
        "scripts/minafox-launcher.sh": validate_launcher(failures),
        "desktop/minafox.desktop": validate_desktop(failures),
        "scripts/install-minafox-arch.sh": validate_installer(failures),
        "README.md": validate_readme(failures),
    }
    validate_no_placeholders_or_host_paths(contents, failures)

    if failures:
        print("MinaFox standalone validation: FAIL")
        print(f"Repository: {ROOT}")
        print(f"Failures: {len(failures)}")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("MinaFox standalone validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
