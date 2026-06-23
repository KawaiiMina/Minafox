#!/usr/bin/env python3
"""Validate MinaFox standalone-wrapper install assets.

This gate checks the first standalone milestone: MinaFox should be launched as
`minafox`, keep its own profile/app identity, and avoid falling back to default
Firefox branding in the desktop entry.
"""
from __future__ import annotations

import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from configparser import ConfigParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "scripts" / "minafox-launcher.sh"
DESKTOP = ROOT / "desktop" / "minafox.desktop"
INSTALLER = ROOT / "scripts" / "install-minafox-arch.sh"
README = ROOT / "README.md"
BRANDING = ROOT / "BRANDING.md"
POLICIES = ROOT / "distribution" / "policies.json"


REQUIRED_LAUNCHER_SNIPPETS = (
    "MOZ_ENABLE_WAYLAND=1",
    "--name minafox",
    "--class MinaFox",
    'PROFILE_DIR="${MINAFOX_PROFILE_DIR:-$HOME/.mozilla/firefox/minafox}"',
    'SHARE_DIR="${MINAFOX_SHARE_DIR:-/usr/share/minafox}"',
    "sync_packaged_assets()",
    "merge_packaged_text_asset",
    "render_template",
    'SYNC_MARKER="$PROFILE_DIR/.minafox-packaged-sync.done"',
    'Path.home() / ".local/share/minafox/start.html"',
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
    "BRANDING.md",
    "not affiliated with or endorsed by Mozilla",
    "/android-checklist",
)

REQUIRED_BRANDING_SNIPPETS = (
    "MinaFox",
    "logo",
    "mascot",
    "official MinaFox builds",
    "not affiliated with or endorsed by Mozilla",
    "Firefox is a trademark of Mozilla Foundation",
    "does not grant permission to use MinaFox brand assets",
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


def validate_branding(failures: list[str]) -> str:
    text = read_text(BRANDING, failures)
    if not text:
        return text
    require_contains("BRANDING.md", text, REQUIRED_BRANDING_SNIPPETS, failures)
    return text


def validate_no_forced_ublock_install(contents: dict[str, str], failures: list[str]) -> None:
    forbidden_markers = (
        "uBlock0@raymondhill.net",
        "ublock-origin/latest.xpi",
        "uBlock Origin is force-installed",
    )
    for label, text in contents.items():
        for marker in forbidden_markers:
            if marker in text:
                failures.append(f"{label}: remove forced uBlock Origin install marker {marker!r}")


def validate_no_placeholders_or_host_paths(contents: dict[str, str], failures: list[str]) -> None:
    forbidden = ("/" + "home" + "/" + "hermes", "/" + "hermes" + "/" + "home")
    for label, text in contents.items():
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "__MINAFOX_START_URL__" in line and label not in {
                "profile/user.js",
                "profile/userContent.css",
                "distribution/policies.json",
                "scripts/install-minafox-arch.sh",
                "scripts/minafox-launcher.sh",
            }:
                failures.append(f"{label}:{line_no}: unexpected MinaFox template placeholder")
            for marker in forbidden:
                if marker in line:
                    failures.append(f"{label}:{line_no}: contains author-machine path {marker!r}")


def validate_packaged_first_run_smoke(failures: list[str]) -> None:
    """Run the launcher against temp HOME/share/fake Firefox to prove first-run sync."""
    with tempfile.TemporaryDirectory(prefix="minafox-home-") as home_s, tempfile.TemporaryDirectory(
        prefix="minafox-share-"
    ) as share_s, tempfile.TemporaryDirectory(prefix="minafox-bin-") as bin_s:
        home = Path(home_s)
        share = Path(share_s)
        fake_bin = Path(bin_s) / "fakefox"
        fake_bin.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ \"${1:-}\" == \"--CreateProfile\" ]]; then "
            "printf 'CreateProfile %s\\n' \"$*\" >> \"$HOME/fakefox.log\"; exit 0; fi\n"
            "printf 'fakefox %s\\n' \"$*\" >> \"$HOME/fakefox.log\"\n"
            "printf 'fakefox %s\\n' \"$*\"\n",
            encoding="utf-8",
        )
        fake_bin.chmod(0o755)

        shutil.copytree(ROOT / "profile", share / "profile")
        shutil.copytree(ROOT / "desktop", share / "desktop")
        shutil.copytree(ROOT / "assets", share / "assets")

        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "PATH": f"{bin_s}:{env.get('PATH', '')}",
                "MINAFOX_FIREFOX_BIN": "fakefox",
                "MINAFOX_SHARE_DIR": str(share),
            }
        )
        result = subprocess.run(
            [str(LAUNCHER), "--version"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
        if result.returncode != 0:
            failures.append("packaged first-run smoke failed:\n" + result.stdout.strip())
            return

        expected_files = (
            home / ".mozilla/firefox/minafox/user.js",
            home / ".mozilla/firefox/minafox/chrome/userChrome.css",
            home / ".mozilla/firefox/minafox/chrome/userContent.css",
            home / ".local/share/minafox/start.html",
            home / ".local/share/applications/minafox.desktop",
            home / ".local/share/icons/hicolor/16x16/apps/minafox.png",
        )
        for path in expected_files:
            if not path.exists():
                failures.append(f"packaged first-run smoke: missing {path.relative_to(home)}")

        for rel in (
            ".mozilla/firefox/minafox/user.js",
            ".mozilla/firefox/minafox/chrome/userContent.css",
        ):
            path = home / rel
            text = path.read_text(encoding="utf-8") if path.exists() else ""
            if "__MINAFOX_START_URL__" in text:
                failures.append(f"packaged first-run smoke: placeholder not rendered in {rel}")
            if "file://" not in text:
                failures.append(f"packaged first-run smoke: missing file:// start URL in {rel}")

        fake_log = (home / "fakefox.log").read_text(encoding="utf-8") if (home / "fakefox.log").exists() else ""
        if "CreateProfile" not in fake_log:
            failures.append("packaged first-run smoke: launcher did not call --CreateProfile for fresh profile")
        if "fakefox --name minafox --class MinaFox --profile" not in fake_log:
            failures.append("packaged first-run smoke: launcher did not exec MINAFOX_FIREFOX_BIN with MinaFox identity")

        marker = home / ".mozilla/firefox/minafox/.minafox-packaged-sync.done"
        if not marker.exists():
            failures.append("packaged first-run smoke: missing packaged-sync marker")

        user_js = home / ".mozilla/firefox/minafox/user.js"
        if user_js.exists():
            user_js.write_text(user_js.read_text(encoding="utf-8") + "\n// local customization sentinel\n", encoding="utf-8")
            second = subprocess.run(
                [str(LAUNCHER), "--version"],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=30,
            )
            if second.returncode != 0:
                failures.append("packaged second-run smoke failed:\n" + second.stdout.strip())
            elif "local customization sentinel" not in user_js.read_text(encoding="utf-8"):
                failures.append("packaged second-run smoke: first-run sync overwrote user.js on second launch")


def validate_packaged_existing_profile_smoke(failures: list[str]) -> None:
    """Existing profiles should get packaged assets without losing local edits."""
    with tempfile.TemporaryDirectory(prefix="minafox-home-") as home_s, tempfile.TemporaryDirectory(
        prefix="minafox-share-"
    ) as share_s, tempfile.TemporaryDirectory(prefix="minafox-bin-") as bin_s:
        home = Path(home_s)
        share = Path(share_s)
        profile = home / ".mozilla/firefox/minafox"
        chrome = profile / "chrome"
        chrome.mkdir(parents=True)
        fake_bin = Path(bin_s) / "fakefox"
        fake_bin.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ \"${1:-}\" == \"--CreateProfile\" ]]; then "
            "printf 'CreateProfile %s\\n' \"$*\" >> \"$HOME/fakefox.log\"; exit 0; fi\n"
            "printf 'fakefox %s\\n' \"$*\" >> \"$HOME/fakefox.log\"\n",
            encoding="utf-8",
        )
        fake_bin.chmod(0o755)

        (profile / "user.js").write_text('user_pref("minafox.local.existing", true);\n', encoding="utf-8")
        (chrome / "userChrome.css").write_text("/* existing chrome customization */\n", encoding="utf-8")
        (chrome / "userContent.css").write_text("/* existing content customization */\n", encoding="utf-8")

        shutil.copytree(ROOT / "profile", share / "profile")
        shutil.copytree(ROOT / "desktop", share / "desktop")
        shutil.copytree(ROOT / "assets", share / "assets")

        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "PATH": f"{bin_s}:{env.get('PATH', '')}",
                "MINAFOX_FIREFOX_BIN": "fakefox",
                "MINAFOX_SHARE_DIR": str(share),
            }
        )
        result = subprocess.run(
            [str(LAUNCHER), "--version"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
        if result.returncode != 0:
            failures.append("packaged existing-profile smoke failed:\n" + result.stdout.strip())
            return

        user_js = (profile / "user.js").read_text(encoding="utf-8")
        user_chrome = (chrome / "userChrome.css").read_text(encoding="utf-8")
        user_content = (chrome / "userContent.css").read_text(encoding="utf-8")
        fake_log = (home / "fakefox.log").read_text(encoding="utf-8") if (home / "fakefox.log").exists() else ""

        if "CreateProfile" in fake_log:
            failures.append("packaged existing-profile smoke: launcher called --CreateProfile for existing profile")
        if 'user_pref("minafox.local.existing", true);' not in user_js:
            failures.append("packaged existing-profile smoke: user.js customization was not preserved")
        if "browser.startup.homepage" not in user_js:
            failures.append("packaged existing-profile smoke: packaged user.js prefs were not merged")
        if "/* existing chrome customization */" not in user_chrome:
            failures.append("packaged existing-profile smoke: userChrome.css customization was not preserved")
        if "--mf-bg" not in user_chrome:
            failures.append("packaged existing-profile smoke: packaged userChrome.css was not merged")
        if "/* existing content customization */" not in user_content:
            failures.append("packaged existing-profile smoke: userContent.css customization was not preserved")
        if "__MINAFOX_START_URL__" in user_js or "__MINAFOX_START_URL__" in user_content:
            failures.append("packaged existing-profile smoke: start URL placeholder was not rendered")
        if not (profile / ".minafox-packaged-sync.done").exists():
            failures.append("packaged existing-profile smoke: missing packaged-sync marker")


def validate_launcher_missing_firefox_smoke(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="minafox-home-") as home_s, tempfile.TemporaryDirectory(
        prefix="minafox-share-"
    ) as share_s:
        home = Path(home_s)
        env = os.environ.copy()
        env.update(
            {
                "HOME": str(home),
                "PATH": "/usr/bin:/bin",
                "MINAFOX_FIREFOX_BIN": "definitely-missing-minafox-firefox",
                "MINAFOX_SHARE_DIR": str(Path(share_s)),
            }
        )
        result = subprocess.run(
            [str(LAUNCHER), "--version"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
        if result.returncode != 127:
            failures.append(f"missing Firefox smoke: expected exit 127, got {result.returncode}\n{result.stdout.strip()}")
        if "could not find Firefox binary: definitely-missing-minafox-firefox" not in result.stdout:
            failures.append("missing Firefox smoke: missing actionable error message")
        if (home / ".mozilla/firefox/minafox").exists():
            failures.append("missing Firefox smoke: launcher created a profile before validating Firefox binary")


def main() -> int:
    failures: list[str] = []
    contents = {
        "scripts/minafox-launcher.sh": validate_launcher(failures),
        "desktop/minafox.desktop": validate_desktop(failures),
        "scripts/install-minafox-arch.sh": validate_installer(failures),
        "README.md": validate_readme(failures),
        "BRANDING.md": validate_branding(failures),
        "distribution/policies.json": read_text(POLICIES, failures),
    }
    validate_no_placeholders_or_host_paths(contents, failures)
    validate_no_forced_ublock_install(contents, failures)
    validate_packaged_first_run_smoke(failures)
    validate_packaged_existing_profile_smoke(failures)
    validate_launcher_missing_firefox_smoke(failures)

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
