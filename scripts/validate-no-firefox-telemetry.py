#!/usr/bin/env python3
"""Validate that MinaFox disables Firefox telemetry/reporting surfaces.

This is a profile/policy validation gate. It verifies prefs and enterprise
policies that disable telemetry, studies, crash submission, Normandy/Shield,
Activity Stream telemetry, ping-centre, and Mozilla probe/reporting endpoints.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
USER_JS = ROOT / "profile" / "user.js"
POLICIES_JSON = ROOT / "distribution" / "policies.json"
README = ROOT / "README.md"

EXPECTED_PREFS: dict[str, bool | str | int] = {
    # Core telemetry collection/upload/archive.
    "toolkit.telemetry.enabled": False,
    "toolkit.telemetry.unified": False,
    "toolkit.telemetry.server": "",
    "toolkit.telemetry.archive.enabled": False,
    "toolkit.telemetry.newProfilePing.enabled": False,
    "toolkit.telemetry.shutdownPingSender.enabled": False,
    "toolkit.telemetry.updatePing.enabled": False,
    "toolkit.telemetry.bhrPing.enabled": False,
    "toolkit.telemetry.firstShutdownPing.enabled": False,
    "toolkit.telemetry.coverage.opt-out": True,
    "toolkit.coverage.opt-out": True,
    "toolkit.coverage.endpoint.base": "",
    # Health report / data reporting.
    "datareporting.healthreport.uploadEnabled": False,
    "datareporting.healthreport.service.enabled": False,
    "datareporting.policy.dataSubmissionEnabled": False,
    "datareporting.policy.firstRunURL": "",
    "datareporting.sessions.current.clean": True,
    # Crash reporting / automated submission.
    "browser.crashReports.unsubmittedCheck.enabled": False,
    "browser.crashReports.unsubmittedCheck.autoSubmit2": False,
    "browser.crashReports.unsubmittedCheck.autoSubmit": False,
    "breakpad.reportURL": "",
    "browser.tabs.crashReporting.sendReport": False,
    # Normandy / Shield / studies / experiments.
    "app.shield.optoutstudies.enabled": False,
    "app.normandy.enabled": False,
    "app.normandy.api_url": "",
    "messaging-system.rsexperimentloader.enabled": False,
    "browser.discovery.enabled": False,
    # Activity Stream / new-tab telemetry and sponsored content.
    "browser.newtabpage.activity-stream.telemetry": False,
    "browser.newtabpage.activity-stream.feeds.telemetry": False,
    "browser.newtabpage.activity-stream.showSponsored": False,
    "browser.newtabpage.activity-stream.showSponsoredTopSites": False,
    "browser.newtabpage.activity-stream.feeds.section.topstories": False,
    "browser.newtabpage.activity-stream.feeds.snippets": False,
    "browser.urlbar.eventTelemetry.enabled": False,
    "browser.search.serpEventTelemetry.enabled": False,
    "browser.search.serpEventTelemetryCategorization.enabled": False,
    "browser.search.serpEventTelemetryCategorization.regionEnabled": False,
    "browser.urlbar.quicksuggest.dataCollection.enabled": False,
    "browser.urlbar.quicksuggest.enabled": False,
    # Browser ping centre / background probes.
    "browser.ping-centre.telemetry": False,
    "network.captive-portal-service.enabled": False,
    "network.connectivity-service.enabled": False,
    "default-browser-agent.enabled": False,
    "dom.private-attribution.submission.enabled": False,
}

EXPECTED_POLICIES: dict[str, Any] = {
    "DisableTelemetry": True,
    "DisableFirefoxStudies": True,
    "DisableFirefoxAccounts": True,
    "DisableAccounts": True,
    "DisablePocket": True,
    "DisableDefaultBrowserAgent": True,
    "DisableFeedbackCommands": True,
    "DisableFirefoxScreenshots": True,
    "DisableSetDesktopBackground": True,
    "DontCheckDefaultBrowser": True,
    "NoDefaultBookmarks": True,
}

README_MARKERS = [
    "## Telemetry removal",
    "validate-no-firefox-telemetry.py",
    "DisableTelemetry",
]

SCAFFOLD_RE = re.compile(r"\b(?:TODO|FIXME|XXX|LOREM IPSUM)\b", re.IGNORECASE)
USER_PREF_RE = re.compile(
    r"user_pref\(\s*(?P<quote>[\"'])(?P<name>.*?)(?P=quote)\s*,\s*(?P<value>.*?)\s*\)\s*;"
)


def parse_user_js(text: str) -> dict[str, Any]:
    prefs: dict[str, Any] = {}
    for match in USER_PREF_RE.finditer(text):
        raw = match.group("value").strip()
        if raw == "true":
            value: Any = True
        elif raw == "false":
            value = False
        elif (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
            value = raw[1:-1]
        else:
            try:
                value = int(raw)
            except ValueError:
                value = raw
        prefs[match.group("name")] = value
    return prefs


def check_scaffold(label: str, text: str, failures: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if SCAFFOLD_RE.search(line):
            failures.append(f"{label}:{line_number}: leftover scaffold marker: {line.strip()}")


def main() -> int:
    failures: list[str] = []

    user_js = USER_JS.read_text(encoding="utf-8") if USER_JS.exists() else ""
    if not user_js:
        failures.append("missing profile/user.js")
    prefs = parse_user_js(user_js)
    for name, expected in EXPECTED_PREFS.items():
        actual = prefs.get(name, "<missing>")
        if actual != expected:
            failures.append(f"profile/user.js: {name} expected {expected!r}, got {actual!r}")

    try:
        policies = json.loads(POLICIES_JSON.read_text(encoding="utf-8"))["policies"]
    except Exception as exc:
        failures.append(f"distribution/policies.json: could not parse policies: {exc}")
        policies = {}
    for name, expected in EXPECTED_POLICIES.items():
        actual = policies.get(name, "<missing>")
        if actual != expected:
            failures.append(f"distribution/policies.json: {name} expected {expected!r}, got {actual!r}")
    if policies.get("OfferToSaveLogins") is not False:
        failures.append("distribution/policies.json: OfferToSaveLogins should remain false")

    locked_preferences = policies.get("Preferences", {})
    if not isinstance(locked_preferences, dict):
        failures.append("distribution/policies.json: Preferences policy block must be an object")
        locked_preferences = {}
    for name, expected in EXPECTED_PREFS.items():
        entry = locked_preferences.get(name, "<missing>")
        if not isinstance(entry, dict):
            failures.append(f"distribution/policies.json: Preferences.{name} expected locked entry, got {entry!r}")
            continue
        if entry.get("Value") != expected:
            failures.append(
                f"distribution/policies.json: Preferences.{name}.Value expected {expected!r}, got {entry.get('Value')!r}"
            )
        if entry.get("Status") != "locked":
            failures.append(
                f"distribution/policies.json: Preferences.{name}.Status expected 'locked', got {entry.get('Status')!r}"
            )

    readme = README.read_text(encoding="utf-8") if README.exists() else ""
    for marker in README_MARKERS:
        if marker not in readme:
            failures.append(f"README.md: missing {marker!r}")

    check_scaffold("profile/user.js", user_js, failures)
    if POLICIES_JSON.exists():
        check_scaffold("distribution/policies.json", POLICIES_JSON.read_text(encoding="utf-8"), failures)
    check_scaffold("README.md", readme, failures)

    if failures:
        print("MinaFox telemetry validation: FAIL")
        print(f"Repository: {ROOT}")
        print(f"Failures: {len(failures)}")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("MinaFox telemetry validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
