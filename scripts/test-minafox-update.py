#!/usr/bin/env python3
"""Smoke tests for the MinaFox updater script.

These tests use fake git/makepkg/systemctl binaries so they can run on non-Arch
CI/dev hosts without touching the real user systemd manager.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UPDATER = ROOT / "scripts" / "minafox-update.sh"


def write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def make_fake_repo(base: Path) -> Path:
    repo = base / "Minafox"
    pkg = repo / "packaging" / "arch" / "minafox-profile-git"
    (repo / ".git").mkdir(parents=True)
    pkg.mkdir(parents=True)
    return repo


def make_fake_share(base: Path) -> Path:
    share = base / "share" / "minafox"
    (share / "profile").mkdir(parents=True)
    (share / "desktop").mkdir(parents=True)
    (share / "assets" / "icons" / "hicolor" / "16x16" / "apps").mkdir(parents=True)
    (share / "profile" / "user.js").write_text(
        'user_pref("browser.startup.homepage", "__MINAFOX_START_URL__");\n',
        encoding="utf-8",
    )
    (share / "profile" / "userChrome.css").write_text("/* packaged chrome css */\n", encoding="utf-8")
    (share / "profile" / "userContent.css").write_text(
        '@-moz-document url("__MINAFOX_START_URL__") { body { color: #f7a8ff; } }\n',
        encoding="utf-8",
    )
    (share / "desktop" / "start.html").write_text("<main>MinaFox packaged start page</main>\n", encoding="utf-8")
    (share / "desktop" / "minafox.desktop").write_text("[Desktop Entry]\nName=MinaFox\n", encoding="utf-8")
    (share / "assets" / "icons" / "hicolor" / "16x16" / "apps" / "minafox.png").write_bytes(b"fakepng")
    return share


def run_updater(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(UPDATER), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        timeout=30,
    )


def test_update_reloads_and_restarts_minafox_user_services_by_default() -> None:
    with tempfile.TemporaryDirectory(prefix="minafox-update-test-") as tmp_s:
        tmp = Path(tmp_s)
        fakebin = tmp / "bin"
        fakebin.mkdir()
        repo = make_fake_repo(tmp)
        log = tmp / "commands.log"

        write_executable(fakebin / "git", f"""#!/usr/bin/env bash
printf 'git %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "makepkg", f"""#!/usr/bin/env bash
printf 'makepkg %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "systemctl", f"""#!/usr/bin/env bash
printf 'systemctl %s\n' "$*" >> {log}
exit 0
""")

        env = os.environ.copy()
        env.update({"PATH": f"{fakebin}:{env['PATH']}", "MINAFOX_REPO_DIR": str(repo)})
        result = run_updater([], env)

        assert result.returncode == 0, result.stdout
        calls = log.read_text(encoding="utf-8")
        assert "git pull --ff-only" in calls
        assert "makepkg -si" in calls
        assert "systemctl --user daemon-reload" in calls
        assert "systemctl --user restart minafox-ai-broker.service" in calls
        assert "systemctl --user restart minafox-searxng.service" in calls
        assert "systemctl --user restart minafox-mobile-harness.service" in calls


def test_update_can_skip_service_restarts() -> None:
    with tempfile.TemporaryDirectory(prefix="minafox-update-test-") as tmp_s:
        tmp = Path(tmp_s)
        fakebin = tmp / "bin"
        fakebin.mkdir()
        repo = make_fake_repo(tmp)
        log = tmp / "commands.log"

        write_executable(fakebin / "git", f"""#!/usr/bin/env bash
printf 'git %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "makepkg", f"""#!/usr/bin/env bash
printf 'makepkg %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "systemctl", f"""#!/usr/bin/env bash
printf 'systemctl %s\n' "$*" >> {log}
exit 0
""")

        env = os.environ.copy()
        env.update({"PATH": f"{fakebin}:{env['PATH']}", "MINAFOX_REPO_DIR": str(repo)})
        result = run_updater(["--no-restart-services"], env)

        assert result.returncode == 0, result.stdout
        calls = log.read_text(encoding="utf-8")
        assert "makepkg -si" in calls
        assert "systemctl" not in calls


def test_update_does_not_start_inactive_disabled_optional_services() -> None:
    with tempfile.TemporaryDirectory(prefix="minafox-update-test-") as tmp_s:
        tmp = Path(tmp_s)
        fakebin = tmp / "bin"
        fakebin.mkdir()
        repo = make_fake_repo(tmp)
        log = tmp / "commands.log"

        write_executable(fakebin / "git", f"""#!/usr/bin/env bash
printf 'git %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "makepkg", f"""#!/usr/bin/env bash
printf 'makepkg %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "systemctl", f"""#!/usr/bin/env bash
printf 'systemctl %s\n' "$*" >> {log}
if [[ "$1" == "--user" && "$2" == "is-active" ]]; then exit 3; fi
if [[ "$1" == "--user" && "$2" == "is-enabled" ]]; then exit 1; fi
exit 0
""")

        env = os.environ.copy()
        env.update({"PATH": f"{fakebin}:{env['PATH']}", "MINAFOX_REPO_DIR": str(repo)})
        result = run_updater([], env)

        assert result.returncode == 0, result.stdout
        calls = log.read_text(encoding="utf-8")
        assert "systemctl --user daemon-reload" in calls
        assert "systemctl --user restart minafox-ai-broker.service" not in calls
        assert "systemctl --user restart minafox-searxng.service" not in calls
        assert "systemctl --user restart minafox-mobile-harness.service" not in calls


def test_update_syncs_profile_and_start_page_assets_by_default() -> None:
    with tempfile.TemporaryDirectory(prefix="minafox-update-test-") as tmp_s:
        tmp = Path(tmp_s)
        fakebin = tmp / "bin"
        fakebin.mkdir()
        repo = make_fake_repo(tmp)
        share = make_fake_share(tmp)
        home = tmp / "home"
        profile = home / ".mozilla" / "firefox" / "minafox"
        log = tmp / "commands.log"

        write_executable(fakebin / "git", f"""#!/usr/bin/env bash
printf 'git %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "makepkg", f"""#!/usr/bin/env bash
printf 'makepkg %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "systemctl", f"""#!/usr/bin/env bash
printf 'systemctl %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "update-desktop-database", "#!/usr/bin/env bash\nexit 0\n")
        write_executable(fakebin / "gtk-update-icon-cache", "#!/usr/bin/env bash\nexit 0\n")

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fakebin}:{env['PATH']}",
                "HOME": str(home),
                "MINAFOX_REPO_DIR": str(repo),
                "MINAFOX_SHARE_DIR": str(share),
                "MINAFOX_PROFILE_DIR": str(profile),
            }
        )
        result = run_updater([], env)

        assert result.returncode == 0, result.stdout
        user_js = profile / "user.js"
        user_content = profile / "chrome" / "userContent.css"
        assert user_js.exists()
        assert user_content.exists()
        assert "__MINAFOX_START_URL__" not in user_js.read_text(encoding="utf-8")
        assert "file://" in user_js.read_text(encoding="utf-8")
        assert "__MINAFOX_START_URL__" not in user_content.read_text(encoding="utf-8")
        assert (profile / "chrome" / "userChrome.css").read_text(encoding="utf-8") == "/* packaged chrome css */\n"
        assert (home / ".local" / "share" / "minafox" / "start.html").read_text(encoding="utf-8") == "<main>MinaFox packaged start page</main>\n"
        assert (home / ".local" / "share" / "applications" / "minafox.desktop").exists()
        assert (home / ".local" / "share" / "icons" / "hicolor" / "16x16" / "apps" / "minafox.png").exists()
        assert (profile / ".minafox-packaged-sync.done").exists()
        assert "Syncing MinaFox profile and start-page assets" in result.stdout


def test_update_can_skip_profile_asset_sync() -> None:
    with tempfile.TemporaryDirectory(prefix="minafox-update-test-") as tmp_s:
        tmp = Path(tmp_s)
        fakebin = tmp / "bin"
        fakebin.mkdir()
        repo = make_fake_repo(tmp)
        share = make_fake_share(tmp)
        home = tmp / "home"
        profile = home / ".mozilla" / "firefox" / "minafox"
        log = tmp / "commands.log"

        write_executable(fakebin / "git", f"""#!/usr/bin/env bash
printf 'git %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "makepkg", f"""#!/usr/bin/env bash
printf 'makepkg %s\n' "$*" >> {log}
exit 0
""")
        write_executable(fakebin / "systemctl", f"""#!/usr/bin/env bash
printf 'systemctl %s\n' "$*" >> {log}
exit 0
""")

        env = os.environ.copy()
        env.update(
            {
                "PATH": f"{fakebin}:{env['PATH']}",
                "HOME": str(home),
                "MINAFOX_REPO_DIR": str(repo),
                "MINAFOX_SHARE_DIR": str(share),
                "MINAFOX_PROFILE_DIR": str(profile),
            }
        )
        result = run_updater(["--no-sync-profile-assets"], env)

        assert result.returncode == 0, result.stdout
        assert not (profile / "user.js").exists()
        assert not (home / ".local" / "share" / "minafox" / "start.html").exists()
        assert "Skipping MinaFox profile/start-page asset sync" in result.stdout


if __name__ == "__main__":
    test_update_reloads_and_restarts_minafox_user_services_by_default()
    test_update_can_skip_service_restarts()
    test_update_does_not_start_inactive_disabled_optional_services()
    test_update_syncs_profile_and_start_page_assets_by_default()
    test_update_can_skip_profile_asset_sync()
    print("minafox-update smoke tests: PASS")
