# Release Notes

## v0.1.0-rc2

**Status:** Draft GitHub pre-release body. Do not publish until the Git tag `v0.1.0-rc2` exists.

**Release URL:** https://github.com/KawaiiMina/Minafox/releases/tag/v0.1.0-rc2

This release candidate is an Arch-first wrapper/profile release for MinaFox. It uses the operating-system `firefox` package underneath and does not bundle or compile Firefox.

### What is included

- `minafox` launcher for the distro Firefox binary.
- Dedicated MinaFox profile namespace and profile prefs.
- MinaFox chrome/content theme files and local start page.
- Local SearXNG search integration.
- Optional Mina AI Den broker for local Ollama experiments.
- Optional Android/LAN UX testing harness.
- Arch `minafox-profile-git` package skeleton and `minafox-update` workflow.
- Rc2 package source pin: `Minafox::git+https://github.com/KawaiiMina/Minafox.git#tag=v0.1.0-rc2`.
- Static rc2 package version: `pkgver=0.1.0rc2`, `pkgrel=1`.
- Validation scripts for wrapper, package, search, AI, mobile harness, telemetry prefs, and host-path checks.

### What is not included

- No bundled Firefox executable.
- No compiled or modified Firefox binary.
- No replacement for `/usr/bin/firefox`.
- No AUR upload or distro package repository.
- No cloud AI chat provider support in the browser surface.
- No live GitHub Wiki sync unless Mina approves that channel separately.

### Install posture

Create the Git tag `v0.1.0-rc2` before publishing the public package path. The rc2 `PKGBUILD` is tag-pinned so `makepkg -si` installs the reviewed rc2 source instead of drifting with `main`.

Public source/package install commands:

```bash
git clone https://github.com/KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox
git checkout v0.1.0-rc2
cd packaging/arch/minafox-profile-git
makepkg -si
minafox
```

The GitHub pre-release is for release notes, tag provenance, and reviewed public state; it is not a binary installer channel.

### Source-fork boundary

A future Firefox ESR source fork is a later phase with separate source, licensing, packaging, and release obligations. Until then, MinaFox should be described as a Firefox wrapper, profile distribution, or standalone wrapper.
