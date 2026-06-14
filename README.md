# MinaFox

MinaFox is a calm, private, kawaii Firefox wrapper for Arch/Hyprland. It gives the system Firefox binary a dedicated MinaFox profile, launcher, desktop identity, pink/purple glass UI, local-search start page, optional AI Den, and Android/LAN UX testing harness — without pretending to be a compiled Firefox fork.

![MinaFox logo](assets/minafox-logo-transparent.png)

## Status

**Current phase:** Standalone wrapper / profile distribution.

The roadmap is still: standalone wrapper now, packaged wrapper next, source fork later only after the wrapper distribution is reliable.

MinaFox currently ships:

- a `minafox` launcher around the distro `firefox` package;
- a dedicated Firefox profile namespace and profile prefs;
- `userChrome.css` / `userContent.css` theme files;
- a local MinaFox start page;
- optional localhost MinaFox SearXNG search;
- optional localhost Mina AI Den broker for local Ollama experiments;
- an Android/LAN harness for responsive UX testing without building a browser APK;
- Arch packaging and systemd user services.

It does **not** bundle, replace, or compile Firefox yet. A future Firefox ESR source-fork phase is tracked separately in the wiki and licensing notes.

## Quick install on Arch

### From a clone

```bash
git clone git@github.com:KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox
./scripts/install-minafox-arch.sh
minafox
```

### From the Arch package skeleton

```bash
cd ~/Minafox/packaging/arch/minafox-profile-git
makepkg -si
minafox
```

After package installation, update with:

```bash
minafox-update
```

`minafox-update` pulls the repo, rebuilds/reinstalls the package, reloads the systemd user manager, and restarts MinaFox user services that are already active or enabled. Use this when changing browser assets, search, AI broker, or harness code:

```bash
minafox-update --no-restart-services  # package update only
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

MinaFox includes a local SearXNG overlay for private search. The helper keeps generated runtime files under `~/.local/share/minafox/searxng`, binds the service to `127.0.0.1:8888`, and supports Docker Compose or Podman Compose.

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
```

See [MinaFox Search](../../wiki/MinaFox-Search) for full setup and troubleshooting.

## Telemetry removal

MinaFox disables telemetry/reporting through both enterprise policies and profile prefs. The policy layer includes `DisableTelemetry`, `DisableFirefoxStudies`, and related locked preferences; the profile layer disables toolkit telemetry, health reports, Normandy/Shield studies, sponsored new-tab content, search/urlbar event telemetry, and similar reporting paths.

Validate the telemetry gate with:

```bash
python3 scripts/validate-no-firefox-telemetry.py
```

Important limit: this configures the distro Firefox binary; it does not physically remove telemetry code paths from Firefox source.

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

The GitHub wiki is the main documentation hub. A versioned mirror is also kept under [`docs/wiki/`](docs/wiki/) so the docs remain reviewable from the repository checkout.

- [Home](../../wiki) / [`docs/wiki/Home.md`](docs/wiki/Home.md)
- [Getting Started](../../wiki/Getting-Started) / [`docs/wiki/Getting-Started.md`](docs/wiki/Getting-Started.md)
- [Architecture](../../wiki/Architecture) / [`docs/wiki/Architecture.md`](docs/wiki/Architecture.md)
- [Services](../../wiki/Services) / [`docs/wiki/Services.md`](docs/wiki/Services.md)
- [Android/LAN Testing](../../wiki/Android-LAN-Testing) / [`docs/wiki/Android-LAN-Testing.md`](docs/wiki/Android-LAN-Testing.md)
- [Mina AI Den](../../wiki/Mina-AI-Den) / [`docs/wiki/Mina-AI-Den.md`](docs/wiki/Mina-AI-Den.md)
- [MinaFox Search](../../wiki/MinaFox-Search) / [`docs/wiki/MinaFox-Search.md`](docs/wiki/MinaFox-Search.md)
- [Packaging and Updating](../../wiki/Packaging-and-Updating) / [`docs/wiki/Packaging-and-Updating.md`](docs/wiki/Packaging-and-Updating.md)
- [Development Guide](../../wiki/Development-Guide) / [`docs/wiki/Development-Guide.md`](docs/wiki/Development-Guide.md)
- [Troubleshooting](../../wiki/Troubleshooting) / [`docs/wiki/Troubleshooting.md`](docs/wiki/Troubleshooting.md)

In-repo docs remain available for versioned details:

- [`docs/brand-lore.md`](docs/brand-lore.md)
- [`docs/ai-provider-architecture.md`](docs/ai-provider-architecture.md)
- [`docs/licensing-and-source-fork.md`](docs/licensing-and-source-fork.md)
- [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md)

## License and third-party posture

MinaFox-owned code is licensed under **MPL-2.0**; see [`LICENSE`](LICENSE). The current distribution stays a wrapper around the distro Firefox package and uses separate MinaFox-owned assets/configuration. MinaFox is independent and is not affiliated with or endorsed by Mozilla; it does not ship a modified Firefox binary.

Brand-usage rules live in [`BRANDING.md`](BRANDING.md). Third-party notes live in [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md). Future Firefox source-fork guardrails live in [`docs/licensing-and-source-fork.md`](docs/licensing-and-source-fork.md).
