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
import re
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
UPDATER = ROOT / "scripts" / "minafox-update.sh"
LICENSE = ROOT / "LICENSE"
BRANDING = ROOT / "BRANDING.md"
THIRD_PARTY = ROOT / "THIRD_PARTY_LICENSES.md"
LICENSING_DOC = ROOT / "docs" / "licensing-and-source-fork.md"

REQUIRED_PKGBUILD_SNIPPETS = (
    "pkgname=minafox-profile-git",
    "license=('MPL-2.0')",
    "depends=('firefox' 'desktop-file-utils' 'hicolor-icon-theme' 'python')",
    "makedepends=('git')",
    "source=('git+https://github.com/KawaiiMina/Minafox.git')",
    "install -Dm755 scripts/minafox-launcher.sh \"$pkgdir/usr/bin/minafox\"",
    "install -Dm755 scripts/minafox-update.sh \"$pkgdir/usr/bin/minafox-update\"",
    "install -Dm755 scripts/minafox-ai-broker.sh \"$pkgdir/usr/bin/minafox-ai-broker\"",
    "install -Dm644 desktop/minafox.desktop \"$pkgdir/usr/share/applications/minafox.desktop\"",
    "install -Dm644 README.md \"$pkgdir/usr/share/doc/minafox/README.md\"",
    "install -Dm644 LICENSE \"$pkgdir/usr/share/licenses/$pkgname/LICENSE\"",
    "install -Dm644 BRANDING.md \"$pkgdir/usr/share/doc/minafox/BRANDING.md\"",
    "install -Dm644 THIRD_PARTY_LICENSES.md \"$pkgdir/usr/share/doc/minafox/THIRD_PARTY_LICENSES.md\"",
    "install -Dm644 docs/brand-lore.md \"$pkgdir/usr/share/doc/minafox/brand-lore.md\"",
    "install -Dm644 docs/ai-provider-architecture.md \"$pkgdir/usr/share/doc/minafox/ai-provider-architecture.md\"",
    "install -Dm644 docs/licensing-and-source-fork.md \"$pkgdir/usr/share/doc/minafox/licensing-and-source-fork.md\"",
    "cp -a assets \"$pkgdir/usr/share/minafox/\"",
    "install -Dm644 desktop/minafox.desktop \"$pkgdir/usr/share/minafox/desktop/minafox.desktop\"",
    "install -Dm644 profile/user.js \"$pkgdir/usr/share/minafox/profile/user.js\"",
    "install -Dm755 scripts/install-minafox-arch.sh \"$pkgdir/usr/share/minafox/scripts/install-minafox-arch.sh\"",
    "install -Dm755 scripts/install-minafox-searxng-arch.sh \"$pkgdir/usr/share/minafox/scripts/install-minafox-searxng-arch.sh\"",
    "install -Dm755 scripts/minafox-update.sh \"$pkgdir/usr/share/minafox/scripts/minafox-update.sh\"",
    "install -Dm755 scripts/minafox-ai-broker.py \"$pkgdir/usr/share/minafox/scripts/minafox-ai-broker.py\"",
    "install -Dm755 scripts/serve-minafox-mobile.py \"$pkgdir/usr/share/minafox/scripts/serve-minafox-mobile.py\"",
    "install -Dm755 scripts/minafox-ai-broker.sh \"$pkgdir/usr/share/minafox/scripts/minafox-ai-broker.sh\"",
    "install -Dm644 systemd/user/minafox-searxng.service \"$pkgdir/usr/lib/systemd/user/minafox-searxng.service\"",
    "install -Dm644 systemd/user/minafox-ai-broker.service \"$pkgdir/usr/lib/systemd/user/minafox-ai-broker.service\"",
    "install -Dm644 systemd/user/minafox-mobile-harness.service \"$pkgdir/usr/lib/systemd/user/minafox-mobile-harness.service\"",
)

REQUIRED_SRCINFO_SNIPPETS = (
    "pkgbase = minafox-profile-git",
    "pkgname = minafox-profile-git",
    "license = MPL-2.0",
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
    "usr/bin/minafox-update",
    "usr/bin/minafox-ai-broker",
    "usr/share/applications/minafox.desktop",
    "usr/share/icons/hicolor/16x16/apps/minafox.png",
    "usr/share/icons/hicolor/1024x1024/apps/minafox.png",
    "usr/share/minafox/assets/icons/hicolor/16x16/apps/minafox.png",
    "usr/share/minafox/assets/icons/hicolor/1024x1024/apps/minafox.png",
    "usr/share/minafox/desktop/start.html",
    "usr/share/minafox/desktop/minafox.desktop",
    "usr/share/minafox/distribution/policies.json",
    "usr/share/minafox/profile/user.js",
    "usr/share/minafox/profile/userChrome.css",
    "usr/share/minafox/profile/userContent.css",
    "usr/share/minafox/scripts/install-minafox-arch.sh",
    "usr/share/minafox/scripts/install-minafox-searxng-arch.sh",
    "usr/share/minafox/scripts/minafox-launcher.sh",
    "usr/share/minafox/scripts/minafox-update.sh",
    "usr/share/minafox/scripts/minafox-ai-broker.py",
    "usr/share/minafox/scripts/serve-minafox-mobile.py",
    "usr/share/minafox/scripts/minafox-ai-broker.sh",
    "usr/lib/systemd/user/minafox-searxng.service",
    "usr/lib/systemd/user/minafox-ai-broker.service",
    "usr/lib/systemd/user/minafox-mobile-harness.service",
    "usr/share/minafox/searxng/docker-compose.yml",
    "usr/share/minafox/searxng/theme/minafox.css",
    "usr/share/doc/minafox/README.md",
    "usr/share/licenses/minafox-profile-git/LICENSE",
    "usr/share/doc/minafox/BRANDING.md",
    "usr/share/doc/minafox/THIRD_PARTY_LICENSES.md",
    "usr/share/doc/minafox/brand-lore.md",
    "usr/share/doc/minafox/ai-provider-architecture.md",
    "usr/share/doc/minafox/licensing-and-source-fork.md",
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
    updater = read(UPDATER, failures)

    require("PKGBUILD", pkgbuild, REQUIRED_PKGBUILD_SNIPPETS, failures)
    require(".SRCINFO", srcinfo, REQUIRED_SRCINFO_SNIPPETS, failures)

    if "pkgver()" not in pkgbuild:
        failures.append("PKGBUILD: missing VCS pkgver() function")
    if "post_install()" not in install or "/usr/share/minafox/scripts/install-minafox-arch.sh" not in install:
        failures.append("minafox-profile-git.install: missing user setup post-install guidance")
    if "makepkg -si" not in readme or "python3 scripts/validate-minafox-arch-package.py" not in readme:
        failures.append("packaging README: missing build or validation command")
    require(
        "packaging README",
        readme,
        (
            "It does **not** compile Firefox or turn MinaFox into a source fork yet.",
            "/usr/share/licenses/minafox-profile-git/LICENSE",
            "/usr/share/doc/minafox/THIRD_PARTY_LICENSES.md",
            "/usr/share/doc/minafox/licensing-and-source-fork.md",
            "MINAFOX_MOBILE_HARNESS_URL",
            "/android-checklist",
            "minafox-update --no-sync-profile-assets",
            "refreshes the installed profile/start-page assets from `/usr/share/minafox`",
        ),
        failures,
    )
    require(
        "minafox-update",
        updater,
        (
            "SYNC_PROFILE_ASSETS=1",
            "MINAFOX_SHARE_DIR",
            "MINAFOX_PROFILE_DIR",
            "--no-sync-profile-assets",
            "sync_profile_assets()",
            "render_template",
            'Path.home() / ".local/share/minafox/start.html"',
            "Syncing MinaFox profile and start-page assets",
        ),
        failures,
    )


def arch_relation_is_token(value: str, token: str) -> bool:
    value = value.strip(" \t\r\n'\"")
    if value == token:
        return True
    return bool(re.match(rf"^{re.escape(token)}(?:[<>=]|<=|>=).+", value))


def pkbuild_array_has_token(pkgbuild: str, name: str, token: str) -> bool:
    """Return True if a bash array assignment contains token as an item.

    This intentionally handles common PKGBUILD forms such as:
    provides=('foo' 'firefox'), provides=("firefox"), and multiline arrays.
    It is a guardrail, not a full bash parser.
    """
    pattern = re.compile(rf"(?m)^\s*{re.escape(name)}\s*=\s*\((.*?)\)", re.DOTALL)
    for match in pattern.finditer(pkgbuild):
        body = re.sub(r"#.*", "", match.group(1))
        items = [part.strip(" \t\r\n'\"") for part in re.split(r"\s+", body) if part.strip()]
        if any(arch_relation_is_token(item, token) for item in items):
            return True
    return False


def srcinfo_has_relation(srcinfo: str, key: str, token: str) -> bool:
    pattern = re.compile(rf"(?m)^\s*{re.escape(key)}\s*=\s*(\S+)\s*$")
    return any(arch_relation_is_token(match.group(1), token) for match in pattern.finditer(srcinfo))


def scalar_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*['\"]?([^'\"\n]+)['\"]?\s*$", text)
    return match.group(1).strip() if match else None


def validate_pkgbuild_srcinfo_consistency(pkgbuild: str, srcinfo: str, failures: list[str]) -> None:
    for key in ("pkgver", "pkgrel", "pkgdesc", "url"):
        pkgbuild_value = scalar_value(pkgbuild, key)
        srcinfo_value = scalar_value(srcinfo, key)
        if pkgbuild_value and srcinfo_value and pkgbuild_value != srcinfo_value:
            failures.append(f"PKGBUILD/.SRCINFO: {key} mismatch ({pkgbuild_value!r} != {srcinfo_value!r})")

    pkgname = scalar_value(pkgbuild, "pkgname")
    pkgbase = scalar_value(srcinfo, "pkgbase")
    srcinfo_pkgname = scalar_value(srcinfo, "pkgname")
    if pkgname and pkgbase and pkgname != pkgbase:
        failures.append(f"PKGBUILD/.SRCINFO: pkgname/pkgbase mismatch ({pkgname!r} != {pkgbase!r})")
    if pkgname and srcinfo_pkgname and pkgname != srcinfo_pkgname:
        failures.append(f"PKGBUILD/.SRCINFO: pkgname mismatch ({pkgname!r} != {srcinfo_pkgname!r})")


def validate_license_guardrails(failures: list[str]) -> None:
    pkgbuild = read(PKGBUILD, failures)
    srcinfo = read(SRCINFO, failures)
    license_text = read(LICENSE, failures)
    branding = read(BRANDING, failures)
    third_party = read(THIRD_PARTY, failures)
    licensing_doc = read(LICENSING_DOC, failures)

    validate_pkgbuild_srcinfo_consistency(pkgbuild, srcinfo, failures)

    require("LICENSE", license_text, ("Mozilla Public License Version 2.0", "3.1. Distribution of Source Form"), failures)
    require(
        "BRANDING.md",
        branding,
        (
            "MinaFox",
            "logo",
            "mascot",
            "official MinaFox builds",
            "not affiliated with or endorsed by Mozilla",
            "Firefox is a trademark of Mozilla Foundation",
            "does not grant permission to use MinaFox brand assets",
        ),
        failures,
    )
    require(
        "THIRD_PARTY_LICENSES.md",
        third_party,
        (
            "System Firefox",
            "does not bundle a Firefox executable",
            "does not copy Firefox source files into MinaFox-owned files",
            "SearXNG is AGPL-3.0-or-later upstream",
            "does not claim Mozilla endorsement",
        ),
        failures,
    )
    require(
        "docs/licensing-and-source-fork.md",
        licensing_doc,
        (
            "does **not** bundle or install a modified Firefox binary",
            "does **not** copy Firefox source files into MinaFox-owned files",
            "depends on the distro/system Firefox package",
            "ships MinaFox-owned launcher, profile, CSS, start page, policy, icon, helper, and documentation files separately",
            "avoid adding GPL-only or AGPL code directly into Firefox product source",
            "avoid Mozilla/Firefox trademarks unless permission exists",
        ),
        failures,
    )
    for array_name in ("provides", "conflicts"):
        if pkbuild_array_has_token(pkgbuild, array_name, "firefox"):
            failures.append(f"PKGBUILD: wrapper package must not list firefox in {array_name}()")
    for key in ("provides", "conflicts"):
        if srcinfo_has_relation(srcinfo, key, "firefox"):
            failures.append(f".SRCINFO: wrapper package must not list firefox as {key}")
    for marker in ("/usr/bin/firefox", "/usr/lib/firefox", "firefox-source", "firefox-esr"):
        if marker in pkgbuild:
            failures.append(f"PKGBUILD: wrapper package must not contain {marker!r}")
    if "license = MPL-2.0" not in srcinfo:
        failures.append(".SRCINFO: missing MPL-2.0 license")


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

        forbidden_staged_prefixes = (
            "usr/bin/firefox",
            "usr/lib/firefox",
            "usr/share/firefox",
            "usr/share/minafox/firefox-source",
            "usr/share/minafox/mozilla-central",
        )
        for staged_path in pkgdir.rglob("*"):
            if not staged_path.is_file() and not staged_path.is_dir():
                continue
            rel = staged_path.relative_to(pkgdir).as_posix()
            if any(rel == marker or rel.startswith(marker + "/") for marker in forbidden_staged_prefixes):
                failures.append(f"staged package contains Firefox binary/source-like path: {rel}")

        for rel in (
            "usr/bin/minafox",
            "usr/bin/minafox-update",
            "usr/bin/minafox-ai-broker",
            "usr/share/minafox/scripts/install-minafox-arch.sh",
            "usr/share/minafox/scripts/install-minafox-searxng-arch.sh",
            "usr/share/minafox/scripts/minafox-launcher.sh",
            "usr/share/minafox/scripts/minafox-update.sh",
            "usr/share/minafox/scripts/minafox-ai-broker.py",
            "usr/share/minafox/scripts/minafox-ai-broker.sh",
        ):
            path = pkgdir / rel
            if path.exists() and not os.access(path, os.X_OK):
                failures.append(f"staged executable is not executable: {rel}")

        launcher = pkgdir / "usr/bin/minafox"
        source_launcher = ROOT / "scripts" / "minafox-launcher.sh"
        if launcher.exists() and source_launcher.exists():
            if launcher.read_text(encoding="utf-8") != source_launcher.read_text(encoding="utf-8"):
                failures.append("staged /usr/bin/minafox differs from scripts/minafox-launcher.sh")

        updater = pkgdir / "usr/bin/minafox-update"
        source_updater = ROOT / "scripts" / "minafox-update.sh"
        if updater.exists() and source_updater.exists():
            if updater.read_text(encoding="utf-8") != source_updater.read_text(encoding="utf-8"):
                failures.append("staged /usr/bin/minafox-update differs from scripts/minafox-update.sh")


def shlex_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def main() -> int:
    failures: list[str] = []
    if not shutil.which("bash"):
        print("MinaFox Arch package validation: FAIL")
        print("- bash is required")
        return 1

    validate_static(failures)
    validate_license_guardrails(failures)
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
