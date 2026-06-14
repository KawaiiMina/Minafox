#!/usr/bin/env python3
"""Validate the MinaFox Arch package skeleton.

The CI/dev host for this repo may not be Arch and may not have makepkg. This
script therefore performs two portable checks:

1. Static metadata checks for PKGBUILD, .SRCINFO, and install script content.
2. A package() simulation by sourcing PKGBUILD in bash with temporary srcdir and
   pkgdir values, then checking the staged package tree.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG_DIR = ROOT / "packaging" / "arch" / "minafox-profile-git"
PKGBUILD = PKG_DIR / "PKGBUILD"
SRCINFO = PKG_DIR / ".SRCINFO"
INSTALL = PKG_DIR / "minafox-profile-git.install"
PKG_README = PKG_DIR / "README.md"

REQUIRED_PKGBUILD_SNIPPETS = (
    "pkgname=minafox-profile-git",
    "depends=('firefox' 'desktop-file-utils' 'hicolor-icon-theme' 'python')",
    "makedepends=('git')",
    "source=('git+https://github.com/KawaiiMina/Minafox.git')",
    "install -Dm755 scripts/minafox-launcher.sh \"$pkgdir/usr/bin/minafox\"",
    "install -Dm644 desktop/minafox.desktop \"$pkgdir/usr/share/applications/minafox.desktop\"",
    "cp -a assets/icons/hicolor \"$pkgdir/usr/share/icons/\"",
    "cp -a assets \"$pkgdir/usr/share/minafox/\"",
    "install -Dm644 profile/user.js \"$pkgdir/usr/share/minafox/profile/user.js\"",
    "install -Dm755 scripts/install-minafox-arch.sh \"$pkgdir/usr/share/minafox/scripts/install-minafox-arch.sh\"",
    "install -Dm755 scripts/install-minafox-searxng-arch.sh \"$pkgdir/usr/share/minafox/scripts/install-minafox-searxng-arch.sh\"",
    "install -Dm644 systemd/user/minafox-searxng.service \"$pkgdir/usr/lib/systemd/user/minafox-searxng.service\"",
)

REQUIRED_SRCINFO_SNIPPETS = (
    "pkgbase = minafox-profile-git",
    "pkgname = minafox-profile-git",
    "depends = firefox",
    "depends = desktop-file-utils",
    "depends = hicolor-icon-theme",
    "depends = python",
    "makedepends = git",
    "optdepends = docker-compose: provide Docker Compose for the optional local MinaFox SearXNG service",
    "optdepends = podman-compose: provide Podman Compose for the optional local MinaFox SearXNG service",
    "source = git+https://github.com/KawaiiMina/Minafox.git",
)

REQUIRED_STAGED_FILES = (
    "usr/bin/minafox",
    "usr/share/applications/minafox.desktop",
    "usr/share/icons/hicolor/16x16/apps/minafox.png",
    "usr/share/icons/hicolor/1024x1024/apps/minafox.png",
    "usr/share/minafox/assets/icons/hicolor/16x16/apps/minafox.png",
    "usr/share/minafox/assets/icons/hicolor/1024x1024/apps/minafox.png",
    "usr/share/minafox/desktop/start.html",
    "usr/share/minafox/distribution/policies.json",
    "usr/share/minafox/profile/user.js",
    "usr/share/minafox/profile/userChrome.css",
    "usr/share/minafox/profile/userContent.css",
    "usr/share/minafox/scripts/install-minafox-arch.sh",
    "usr/share/minafox/scripts/install-minafox-searxng-arch.sh",
    "usr/share/minafox/scripts/minafox-launcher.sh",
    "usr/lib/systemd/user/minafox-searxng.service",
    "usr/share/minafox/searxng/docker-compose.yml",
    "usr/share/minafox/searxng/theme/minafox.css",
    "usr/share/doc/minafox/README.md",
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


def validate_static(failures: list[str]) -> None:
    pkgbuild = read(PKGBUILD, failures)
    srcinfo = read(SRCINFO, failures)
    install = read(INSTALL, failures)
    readme = read(PKG_README, failures)

    require("PKGBUILD", pkgbuild, REQUIRED_PKGBUILD_SNIPPETS, failures)
    require(".SRCINFO", srcinfo, REQUIRED_SRCINFO_SNIPPETS, failures)

    if "pkgver()" not in pkgbuild:
        failures.append("PKGBUILD: missing VCS pkgver() function")
    if "post_install()" not in install or "/usr/share/minafox/scripts/install-minafox-arch.sh" not in install:
        failures.append("minafox-profile-git.install: missing user setup post-install guidance")
    if "makepkg -si" not in readme or "python3 scripts/validate-minafox-arch-package.py" not in readme:
        failures.append("packaging README: missing build or validation command")


def validate_package_simulation(failures: list[str]) -> None:
    with tempfile.TemporaryDirectory(prefix="minafox-pkg-") as tmp_s:
        tmp = Path(tmp_s)
        srcdir = tmp / "src"
        pkgdir = tmp / "pkg"
        srcdir.mkdir()
        pkgdir.mkdir()
        os.symlink(ROOT, srcdir / "Minafox", target_is_directory=True)

        command = (
            "set -euo pipefail; "
            f"srcdir={shlex_quote(str(srcdir))}; "
            f"pkgdir={shlex_quote(str(pkgdir))}; "
            f"source {shlex_quote(str(PKGBUILD))}; "
            "package"
        )
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=PKG_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
        )
        if result.returncode != 0:
            failures.append("PKGBUILD package() simulation failed:\n" + result.stdout.strip())
            return

        for rel in REQUIRED_STAGED_FILES:
            path = pkgdir / rel
            if not path.exists():
                failures.append(f"staged package missing: {rel}")

        for rel in (
            "usr/bin/minafox",
            "usr/share/minafox/scripts/install-minafox-arch.sh",
            "usr/share/minafox/scripts/install-minafox-searxng-arch.sh",
            "usr/share/minafox/scripts/minafox-launcher.sh",
        ):
            path = pkgdir / rel
            if path.exists() and not os.access(path, os.X_OK):
                failures.append(f"staged executable is not executable: {rel}")

        launcher = pkgdir / "usr/bin/minafox"
        source_launcher = ROOT / "scripts" / "minafox-launcher.sh"
        if launcher.exists() and source_launcher.exists():
            if launcher.read_text(encoding="utf-8") != source_launcher.read_text(encoding="utf-8"):
                failures.append("staged /usr/bin/minafox differs from scripts/minafox-launcher.sh")


def shlex_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def main() -> int:
    failures: list[str] = []
    if not shutil.which("bash"):
        print("MinaFox Arch package validation: FAIL")
        print("- bash is required")
        return 1

    validate_static(failures)
    if not failures:
        validate_package_simulation(failures)

    if failures:
        print("MinaFox Arch package validation: FAIL")
        print(f"Repository: {ROOT}")
        print(f"Failures: {len(failures)}")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("MinaFox Arch package validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
