# Arch package skeleton: `minafox-profile-git`

This directory is the first Arch packaging sprint for MinaFox's standalone-wrapper phase.

## Package intent

`minafox-profile-git` packages the current Git checkout as a user-friendly Arch package while MinaFox still uses the system Firefox binary underneath.

It installs:

- `/usr/bin/minafox` — Wayland-friendly standalone launcher.
- `/usr/share/applications/minafox.desktop` — desktop app entry.
- `/usr/share/icons/hicolor/.../apps/minafox.png` — icon-theme assets.
- `/usr/share/minafox/` — profile, start page, branding assets, policy, SearXNG overlay, and helper scripts.
- `/usr/share/doc/minafox/README.md` — project documentation.

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

## Local validation from this repo

From the repo root:

```bash
python3 scripts/validate-minafox-arch-package.py
```

The validator checks the packaging metadata and simulates the `package()` function with a temporary `pkgdir`, so it can run on non-Arch CI/dev machines that do not have `makepkg`.
