# Getting Started

This page gets MinaFox installed and running on Arch/Hyprland.

## Prerequisites

- Arch Linux or Arch-like environment.
- `firefox` installed from the distro package.
- `python3` for helper scripts and validators.
- `base-devel` for `makepkg` if you install with the Arch package skeleton.
- Optional for local search: Docker Compose or Podman Compose.
- Optional for local AI: Ollama on `127.0.0.1:11434`.
- Optional for GitHub publishing: GitHub SSH key or HTTPS credentials.

## Install from a clone

```bash
git clone https://github.com/KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox
git checkout v0.1.0-rc2
./scripts/install-minafox-arch.sh
minafox
```

If the repo already exists:

```bash
cd ~/Minafox
git fetch --tags
git checkout v0.1.0-rc2
./scripts/install-minafox-arch.sh
minafox
```

## Install with the Arch package skeleton

MinaFox's package is a wrapper/profile package around the distro `firefox` package. It does not install a Firefox binary, replace `/usr/bin/firefox`, or declare itself as Firefox.

```bash
git clone https://github.com/KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox/packaging/arch/minafox-profile-git
makepkg -si
minafox
```

The package installs `/usr/bin/minafox`, `/usr/bin/minafox-update`, `/usr/bin/minafox-ai-broker`, the desktop entry, icons, docs, assets, and optional systemd user units.

On first launch, `/usr/bin/minafox` syncs packaged assets into user-local paths. Later `minafox-update` refreshes the same profile/start-page assets after package upgrades unless you pass `--no-sync-profile-assets`:

```text
~/.mozilla/firefox/minafox
~/.local/share/minafox
~/.local/share/applications/minafox.desktop
~/.local/share/icons/hicolor
```

Update the installed package with:

```bash
minafox-update
```

By default, `minafox-update` uses `~/Minafox`, pulls the repo, runs `makepkg -si`, syncs current packaged assets from `/usr/share/minafox`, reloads the systemd user manager, and restarts only MinaFox services that are already active or enabled.

Useful update variants:

```bash
minafox-update --no-sync-profile-assets
minafox-update --no-restart-services
minafox-update --repo /path/to/Minafox
MINAFOX_REPO_DIR=/path/to/Minafox minafox-update
```

## Launch

```bash
minafox
```

If the command is not found after a user-local install:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## First checks

1. `minafox` opens Firefox with the MinaFox profile.
2. The browser chrome uses the dark lavender/pink theme.
3. The start page says MinaFox and shows the search box, quick links, widgets, AI Den, and search status.
4. Settings/Profile buttons copy or show `about:` commands rather than dead-linking.
5. Tab focus rings are visible.
6. Resizing to narrow widths keeps cards readable.

## Optional next steps

- Enable local search: [MinaFox Search](MinaFox-Search).
- Enable AI broker: [Mina AI Den](Mina-AI-Den).
- Test on Android: [Android/LAN Testing](Android-LAN-Testing).
- Package/update workflow: [Packaging and Updating](Packaging-and-Updating).
- Troubleshoot command, profile, service, and chrome-polish failures: [Troubleshooting](Troubleshooting).
- Review release boundaries: [Known Limitations](Known-Limitations).
