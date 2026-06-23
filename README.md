# MinaFox

MinaFox is a calm, private, kawaii Firefox wrapper for Arch/Hyprland. It gives the system Firefox binary a dedicated MinaFox profile, launcher, desktop identity, pink/purple glass UI, local-search start page, optional AI Den, and Android/LAN UX testing harness — without pretending to be a compiled Firefox fork.

![MinaFox logo](assets/minafox-logo-transparent.png)

## Status

**Current phase:** Standalone wrapper / profile distribution.

The next public release candidate is `v0.1.0-rc2`. Treat it as a release candidate for the wrapper/profile package, not as a bundled browser binary. The public package install path depends on the Git tag `v0.1.0-rc2` existing before users run `makepkg -si`.

The roadmap is still: standalone wrapper now, release-channel hardening next, source fork later only after the wrapper distribution is reliable.

MinaFox currently ships:

- a `minafox` launcher around the distro `firefox` package;
- a dedicated Firefox profile namespace and profile prefs;
- `userChrome.css` / `userContent.css` theme files;
- a local MinaFox start page;
- default localhost MinaFox SearXNG search;
- optional localhost Mina AI Den broker for local Ollama experiments;
- an Android/LAN harness for responsive UX testing without building a browser APK;
- Arch packaging and systemd user services.

It does **not** bundle, replace, or compile Firefox yet. A future Firefox ESR source-fork phase is tracked separately in the wiki and licensing notes.

## Quick install on Arch

### From a clone

```bash
git clone https://github.com/KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox
git checkout v0.1.0-rc2
./scripts/install-minafox-arch.sh
minafox
```

### From the Arch package skeleton

```bash
git clone https://github.com/KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox
git checkout v0.1.0-rc2
cd packaging/arch/minafox-profile-git
makepkg -si
minafox
```

For rc2, the package skeleton is pinned to `Minafox::git+https://github.com/KawaiiMina/Minafox.git#tag=v0.1.0-rc2` with `pkgver=0.1.0rc2` and `pkgrel=1`. That tag must be created before publishing these commands; once it exists, the package source does not drift when `main` advances. The GitHub pre-release is useful for release notes, tag provenance, and reviewed state. Install commands remain source/package based until a separately approved package channel exists.

After package installation, update with:

```bash
minafox-update
```

If `~/Minafox` is checked out directly at the `v0.1.0-rc2` tag for release-candidate smoke testing, use `minafox-update --no-pull` so the updater does not try to pull from a detached tag checkout.

`minafox-update` pulls the repo, rebuilds/reinstalls the package, refreshes the installed profile/start-page assets from `/usr/share/minafox`, reloads the systemd user manager, and restarts MinaFox user services that are already active or enabled. Use this when changing browser assets, search, AI broker, or harness code:

```bash
minafox-update --no-sync-profile-assets  # preserve local profile/start-page customizations
minafox-update --no-restart-services     # package update + asset sync only
```

## Optional services

### Local search

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
```

Local URL: `http://127.0.0.1:8888/`

### Mina AI Den broker

```bash
systemctl --user enable --now minafox-ai-broker.service
systemctl --user status minafox-ai-broker.service
```

Broker URL: `http://127.0.0.1:8765/`

Ollama chat remains disabled unless explicitly enabled with `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1`. Cloud providers and Hermes Gateway are metadata/detection-only until a secrets backend and safety UX exist.

### Android/LAN UX harness

Use this to test MinaFox responsiveness and touch UX on Android without compiling a full browser APK:

```bash
systemctl --user enable --now minafox-mobile-harness.service
systemctl --user status minafox-mobile-harness.service
```

Harness URL: `http://<desktop-lan-ip>:8766/`

Diagnostics from Android: `/health`, `/config`, and `/android-checklist` on the same harness host. The start page includes an Android/LAN test companion card that shows the active endpoints and touch checklist.

Only enable the LAN harness on trusted LAN/Tailscale networks. Keep port `8766` blocked from untrusted networks.

## Repository map

- `assets/` — logo and icon assets.
- `desktop/` — desktop entry and MinaFox start page.
- `distribution/` — Firefox enterprise policies.
- `docs/` — focused reference documents kept in-repo.
- `packaging/arch/minafox-profile-git/` — Arch package skeleton.
- `profile/` — Firefox profile prefs and chrome/content CSS.
- `scripts/` — installer, launcher, update, services, tests, and validators.
- `searxng/` — local SearXNG overlay and Compose config.
- `systemd/user/` — optional user services.

## MinaFox SearXNG search

MinaFox uses local SearXNG as the default MinaFox search layer. The browser UI sends searches to `http://127.0.0.1:8888/search` with POST, and SearXNG handles upstream engine selection, categories, privacy settings, and result rendering. Future search-engine support is configured through SearXNG engine settings instead of adding direct browser-side Google/DuckDuckGo/Brave/Startpage integrations.

The helper keeps generated runtime files under `~/.local/share/minafox/searxng`, binds the service to `127.0.0.1:8888`, and supports Docker Compose or Podman Compose.

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
```

See [MinaFox Search](../../wiki/MinaFox-Search) for full setup and troubleshooting.

## Telemetry removal

MinaFox disables known Firefox telemetry/reporting surfaces through both enterprise policies and profile prefs. The policy layer includes `DisableTelemetry`, `DisableFirefoxStudies`, and related locked preferences; the profile layer disables toolkit telemetry, health reports, Normandy/Shield studies, sponsored new-tab content, search/urlbar event telemetry, and similar reporting paths.

Validate the telemetry gate with:

```bash
python3 scripts/validate-no-firefox-telemetry.py
```

Important limit: this configures the distro Firefox binary; it does not physically remove telemetry code paths from Firefox source, and it is not a claim that all possible Firefox network activity has been removed. Re-run the validator when Firefox or MinaFox prefs change.

## Validation

Run the full local gate before publishing changes:

```bash
python3 scripts/test-serve-minafox-mobile.py
python3 scripts/test-minafox-ai-broker.py
python3 scripts/test-minafox-update.py
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-minafox-standalone.py
python3 scripts/validate-minafox-arch-package.py
python3 scripts/validate-no-host-paths.py
python3 scripts/validate-no-firefox-telemetry.py
python3 scripts/validate-minafox-searxng.py
python3 scripts/validate-minafox-ai.py
```

## Documentation

The versioned docs mirror under [`docs/wiki/`](docs/wiki/) is the reviewed source for this release candidate. GitHub Wiki sync is a separate approval-gated channel, so live wiki pages may lag the repository mirror.

- [Home](../../wiki) / [`docs/wiki/Home.md`](docs/wiki/Home.md)
- [Getting Started](../../wiki/Getting-Started) / [`docs/wiki/Getting-Started.md`](docs/wiki/Getting-Started.md)
- [Architecture](../../wiki/Architecture) / [`docs/wiki/Architecture.md`](docs/wiki/Architecture.md)
- [Services](../../wiki/Services) / [`docs/wiki/Services.md`](docs/wiki/Services.md)
- [Android/LAN Testing](../../wiki/Android-LAN-Testing) / [`docs/wiki/Android-LAN-Testing.md`](docs/wiki/Android-LAN-Testing.md)
- [Mina AI Den](../../wiki/Mina-AI-Den) / [`docs/wiki/Mina-AI-Den.md`](docs/wiki/Mina-AI-Den.md)
- [MinaFox Search](../../wiki/MinaFox-Search) / [`docs/wiki/MinaFox-Search.md`](docs/wiki/MinaFox-Search.md)
- [Packaging and Updating](../../wiki/Packaging-and-Updating) / [`docs/wiki/Packaging-and-Updating.md`](docs/wiki/Packaging-and-Updating.md)
- [`docs/wiki/Release-Notes.md`](docs/wiki/Release-Notes.md)
- [`docs/wiki/Publishing-Checklist.md`](docs/wiki/Publishing-Checklist.md)
- [`docs/wiki/Known-Limitations.md`](docs/wiki/Known-Limitations.md)
- [Development Guide](../../wiki/Development-Guide) / [`docs/wiki/Development-Guide.md`](docs/wiki/Development-Guide.md)
- [Troubleshooting](../../wiki/Troubleshooting) / [`docs/wiki/Troubleshooting.md`](docs/wiki/Troubleshooting.md)

In-repo docs remain available for versioned details:

- [`docs/brand-lore.md`](docs/brand-lore.md)
- [`docs/ai-provider-architecture.md`](docs/ai-provider-architecture.md)
- [`docs/licensing-and-source-fork.md`](docs/licensing-and-source-fork.md)
- [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)

## License and third-party posture

MinaFox-owned code and assets in this repository are licensed under **MPL-2.0** where applicable; see [`LICENSE`](LICENSE). The current distribution stays a wrapper around the distro Firefox package and uses separate MinaFox-owned assets/configuration. It does not relicense Firefox, ship Firefox source, or ship a modified Firefox binary. MinaFox is independent and is not affiliated with or endorsed by Mozilla.

Brand-usage rules live in [`BRANDING.md`](BRANDING.md). Third-party notes live in [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md). Future Firefox source-fork guardrails live in [`docs/licensing-and-source-fork.md`](docs/licensing-and-source-fork.md).
