# Packaging and Updating

MinaFox currently packages as `minafox-profile-git`, an Arch VCS package for the standalone wrapper phase.

## Package intent

The package installs MinaFox wrapper/profile assets while depending on the distro Firefox package. It does not compile Firefox or replace `/usr/bin/firefox`.

Installed pieces include:

- `/usr/bin/minafox`
- `/usr/bin/minafox-update`
- `/usr/bin/minafox-ai-broker`
- `/usr/share/applications/minafox.desktop`
- `/usr/share/icons/hicolor/.../apps/minafox.png`
- `/usr/share/minafox/`
- `/usr/share/doc/minafox/`
- `/usr/lib/systemd/user/minafox-searxng.service`
- `/usr/lib/systemd/user/minafox-ai-broker.service`
- `/usr/lib/systemd/user/minafox-mobile-harness.service`

## Build/install

```bash
cd ~/Minafox/packaging/arch/minafox-profile-git
makepkg -si
```

## First launch sync

On first launch, `/usr/bin/minafox` syncs packaged files into user-local paths:

```text
~/.mozilla/firefox/minafox
~/.local/share/minafox
~/.local/share/applications/minafox.desktop
~/.local/share/icons/hicolor
```

## Update command

```bash
minafox-update
```

Default behavior:

1. Use `~/Minafox` or `MINAFOX_REPO_DIR`.
2. Pull the repo unless `--no-pull` is passed.
3. Run `makepkg -si` from `packaging/arch/minafox-profile-git`.
4. Refresh installed profile/start-page assets from `/usr/share/minafox` into the current user's MinaFox paths.
5. Run `systemctl --user daemon-reload`.
6. Restart MinaFox services that are already active or enabled.

The asset refresh updates these files after package upgrades, so UI/profile changes do not wait for a fresh first launch marker:

```text
~/.mozilla/firefox/minafox/user.js
~/.mozilla/firefox/minafox/chrome/userChrome.css
~/.mozilla/firefox/minafox/chrome/userContent.css
~/.local/share/minafox/start.html
~/.local/share/applications/minafox.desktop
~/.local/share/icons/hicolor
```

Preserve local profile/start-page customizations:

```bash
minafox-update --no-sync-profile-assets
```

Skip service reload/restarts while still rebuilding/installing and syncing profile/start-page assets:

```bash
minafox-update --no-restart-services
```

Use another checkout:

```bash
minafox-update --repo /path/to/Minafox
MINAFOX_REPO_DIR=/path/to/Minafox minafox-update
```

## Service restart policy

The updater does not start inactive+disabled optional services. It only restarts services that are already active or enabled: `minafox-ai-broker.service`, `minafox-searxng.service`, and `minafox-mobile-harness.service`.

## Package validation

```bash
python3 scripts/validate-minafox-arch-package.py
python3 scripts/test-minafox-update.py
```

## Wrapper/source-fork boundary

The Arch package should keep `depends=('firefox' ...)`, avoid `provides=('firefox')` or `conflicts=('firefox')`, avoid bundled Firefox binaries, and remain honest as a standalone profile wrapper until a deliberate source-fork phase exists.
