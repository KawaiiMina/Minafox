# Repository Map

## Top-level files

- `README.md` — concise repo landing page.
- `LICENSE` — MinaFox-owned code license, MPL-2.0.
- `THIRD_PARTY_LICENSES.md` — Firefox/SearXNG/provider notice tracker.

## `assets/`

Logo and icon assets:

- `assets/minafox-logo-transparent.png`
- `assets/minafox-logo.svg`
- `assets/icons/minafox-*.png`
- `assets/icons/minafox.ico`
- `assets/icons/hicolor/.../apps/minafox.png`

## `desktop/`

- `desktop/start.html` — MinaFox local start page.
- `desktop/minafox.desktop` — Linux desktop launcher entry.

## `profile/`

- `profile/user.js` — Firefox prefs, privacy hardening, chrome CSS enablement.
- `profile/userChrome.css` — browser chrome theme.
- `profile/userContent.css` — scoped content styling.

## `scripts/`

- `install-minafox-arch.sh` — user-local setup and refresh helper.
- `minafox-launcher.sh` — Wayland-friendly launcher around Firefox.
- `minafox-update.sh` — package update/restart helper.
- `install-minafox-searxng-arch.sh` — local SearXNG runtime/service helper.
- `minafox-ai-broker.py` / `.sh` — local AI broker.
- `serve-minafox-mobile.py` — Android/LAN UX harness.
- `test-*.py` — unit/smoke tests.
- `validate-*.py` — project validation gates.

## `searxng/`

- `Dockerfile` — upstream SearXNG image with MinaFox overlay.
- `docker-compose.yml` — local-only service binding.
- `settings.yml` — privacy-first settings template.
- `uwsgi.ini` — container runtime config.
- `theme/minafox.css` — MinaFox search styling.
- `README.md` — SearXNG-specific notes.

## `systemd/user/`

- `minafox-ai-broker.service`
- `minafox-searxng.service`
- `minafox-mobile-harness.service`

## `packaging/arch/minafox-profile-git/`

Arch VCS package skeleton for the wrapper phase. It depends on the system `firefox` package and installs MinaFox assets separately.

## `docs/`

Versioned reference docs that should stay in the repo:

- `brand-lore.md`
- `ai-provider-architecture.md`
- `licensing-and-source-fork.md`
