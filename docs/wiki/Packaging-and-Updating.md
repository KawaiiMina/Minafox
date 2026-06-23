# Packaging and Updating

MinaFox currently packages as `minafox-profile-git`, an Arch VCS package for the standalone wrapper phase.

## Package intent

The package installs MinaFox wrapper/profile assets while depending on the distro Firefox package. It does not compile Firefox, bundle a Firefox binary, replace `/usr/bin/firefox`, or declare `provides=('firefox')` / `conflicts=('firefox')`.

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
git clone https://github.com/KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox/packaging/arch/minafox-profile-git
makepkg -si
```

If you already have the checkout, start from the existing `~/Minafox` path instead of cloning again.

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

If the repo was checked out directly at the `v0.1.0-rc2` tag for rc2 smoke testing, use `minafox-update --no-pull` because the default updater runs `git pull --ff-only`.

Default behavior:

1. Use `~/Minafox`, `MINAFOX_REPO_DIR`, or `--repo`.
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

The current release path has passed the package validator, updater smoke tests, and a disposable Arch pacman install/remove smoke for the wrapper package payload.

```bash
python3 scripts/validate-minafox-arch-package.py
python3 scripts/test-minafox-update.py
```

## Wrapper/source-fork boundary

The Arch package should keep `depends=('firefox' ...)`, avoid `provides=('firefox')` or `conflicts=('firefox')`, avoid installing `/usr/bin/firefox`, `/usr/lib/firefox`, or bundled Firefox binaries, and remain honest as a standalone profile wrapper until a deliberate source-fork phase exists. Package metadata and docs should not describe MinaFox as a Firefox replacement, rebranded Firefox binary, or compiled Firefox build during the wrapper phase.
