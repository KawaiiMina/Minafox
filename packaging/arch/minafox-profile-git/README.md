# Arch package skeleton: `minafox-profile-git`

This directory is the first Arch packaging sprint for MinaFox's standalone-wrapper phase.

## Package intent

`minafox-profile-git` packages the current Git checkout as a user-friendly Arch package while MinaFox still uses the system Firefox binary underneath.

It installs:

- `/usr/bin/minafox` — Wayland-friendly standalone launcher.
- `/usr/bin/minafox-update` — rebuild and upgrade the installed package from the git package skeleton.
- `/usr/bin/minafox-ai-broker` — localhost-only Mina AI Den broker.
- `/usr/share/applications/minafox.desktop` — desktop app entry.
- `/usr/share/icons/hicolor/.../apps/minafox.png` — icon-theme assets.
- `/usr/share/minafox/` — profile, start page, branding assets, policy, SearXNG overlay, and helper scripts.
- `/usr/lib/systemd/user/minafox-searxng.service` — optional local search user service.
- `/usr/lib/systemd/user/minafox-ai-broker.service` — optional local AI broker user service.
- `/usr/share/doc/minafox/README.md` and `/usr/share/doc/minafox/brand-lore.md` — project documentation and Mina mascot lore.
- `/usr/share/doc/minafox/ai-provider-architecture.md` — Mina AI Den provider and privacy architecture notes.

It does **not** compile Firefox or turn MinaFox into a source fork yet.

## Build on Arch

```bash
cd packaging/arch/minafox-profile-git
makepkg -si
```

## User setup after install

The package installs the launcher system-wide, so this should work immediately:

```bash
minafox
```

On first launch, `/usr/bin/minafox` auto-syncs packaged assets from `/usr/share/minafox` into the current user's MinaFox paths:

```text
~/.mozilla/firefox/minafox
~/.local/share/minafox
~/.local/share/applications/minafox.desktop
~/.local/share/icons/hicolor
```

To force a full refresh, or to attempt installing Firefox enterprise policies, run:

```bash
/usr/share/minafox/scripts/install-minafox-arch.sh
```

Note: the user setup script may ask for `sudo` when it tries to install Firefox enterprise policies under `/usr/lib/firefox/distribution`. The launcher's automatic first-run sync is user-local only and does not use `sudo`.

## Updating the installed package

After installing the package, upgrade from the MinaFox git package skeleton with:

```bash
minafox-update
```

By default this uses `~/Minafox`, pulls the repo, and runs `makepkg -si` from this package directory. Use `minafox-update --repo /path/to/Minafox` or `MINAFOX_REPO_DIR=/path/to/Minafox minafox-update` for another checkout.

## Optional Mina AI Den broker

The package installs the broker command and unit file, but does not enable it
automatically. To run it once:

```bash
minafox-ai-broker
```

To keep it running as a user service:

```bash
systemctl --user enable --now minafox-ai-broker.service
systemctl --user status minafox-ai-broker.service
```

It binds to `127.0.0.1:8765`, exposes `/health`, `/providers`, and
`/hermes/health`, and leaves `/chat` disabled until the Hermes safety UX is
implemented.

## Optional local SearXNG user service

The package installs the unit file, but it does not automatically start containers. To enable local private search for your user:

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
```

The helper copies the packaged read-only overlay into `~/.local/share/minafox/searxng`, generates the local secret/config there, and keeps SearXNG bound to `127.0.0.1:8888`. Install either the Docker stack (`docker` + `docker-compose`) or the Podman stack (`podman` + `podman-compose`) first.

## Local validation from this repo

From the repo root:

```bash
python3 scripts/validate-minafox-arch-package.py
```

The validator checks the packaging metadata and simulates the `package()` function with a temporary `pkgdir`, so it can run on non-Arch CI/dev machines that do not have `makepkg`.
