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


if __name__ == "__main__":
    test_update_reloads_and_restarts_minafox_user_services_by_default()
    test_update_can_skip_service_restarts()
    test_update_does_not_start_inactive_disabled_optional_services()
    print("minafox-update smoke tests: PASS")
