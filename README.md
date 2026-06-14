# MinaFox — standalone Firefox distribution starter

This is a practical custom Firefox distribution/profile scaffold for an Arch + Hyprland desktop.

MinaFox is currently in its **Standalone wrapper** phase: installing the repo gives you a dedicated `minafox` launcher, desktop entry, icon identity, profile namespace, themed start page, and policy/profile hardening while using the system Firefox binary underneath.

It is **not** a full Firefox source fork yet. The plan is: Standalone wrapper now, Arch package next, source fork later after the wrapper distribution is reliable.

## License and Mozilla/MPL posture

MinaFox-owned code is licensed under **MPL-2.0**; see [`LICENSE`](LICENSE). The current package intentionally stays a wrapper around the distro Firefox package:

- it does **not** bundle or install a modified Firefox binary;
- it does **not** copy Firefox source files into MinaFox-owned files;
- it depends on system `firefox`;
- it ships MinaFox-owned launcher/profile/CSS/start-page/policy/icon/helper files separately;
- it keeps optional SearXNG as a separate localhost service/container;
- it uses MinaFox branding and does not imply Mozilla endorsement.

Third-party notes are tracked in [`THIRD_PARTY_LICENSES.md`](THIRD_PARTY_LICENSES.md). Future Firefox ESR source-fork obligations are tracked in [`docs/licensing-and-source-fork.md`](docs/licensing-and-source-fork.md).

## Repository layout

The GitHub repo is organized around the installable pieces:

- `assets/` — MinaFox logo sources and generated app icons.
  - `assets/minafox-logo-transparent.png` — transparent master PNG.
  - `assets/minafox-logo.svg` — SVG-style logo wrapper.
  - `assets/icons/` — generated PNG/ICO app icons.
  - `assets/icons/hicolor/` — Linux icon-theme layout copied during install.
- `docs/` — project/brand documentation.
  - `docs/brand-lore.md` — Mina the mascot, logo story, voice, and future mascot-art direction.
  - `docs/ai-provider-architecture.md` — optional Mina AI Den provider, privacy, and Hermes Gateway architecture.
  - `docs/licensing-and-source-fork.md` — MPL, wrapper-package, and future Firefox source-fork guardrails.
- `LICENSE` — MinaFox MPL-2.0 license text.
- `THIRD_PARTY_LICENSES.md` — Firefox/SearXNG/provider notice tracker and compliance notes.
- `desktop/` — desktop-facing files.
  - `desktop/start.html` — local MinaFox start page that submits searches to local SearXNG.
  - `desktop/minafox.desktop` — Linux desktop launcher that calls `minafox`.
- `distribution/` — Firefox enterprise policy files.
  - `distribution/policies.json` — extension policy, telemetry/studies shutdown, locked prefs.
- `profile/` — files copied into the dedicated Firefox profile.
  - `profile/user.js` — Firefox profile prefs, privacy hardening, chrome CSS enablement.
  - `profile/userChrome.css` — MinaFox browser-chrome theme.
  - `profile/userContent.css` — scoped content styling for Firefox start surfaces and local MinaFox page.
- `scripts/` — install and validation helpers.
  - `scripts/install-minafox-arch.sh` — installs/updates the MinaFox Firefox profile assets and the user-local `minafox` launcher.
  - `scripts/minafox-launcher.sh` — Wayland-friendly standalone wrapper around the system Firefox binary.
  - `scripts/install-minafox-searxng-arch.sh` — prepares and starts the local MinaFox SearXNG service with Docker/Podman Compose, including the packaged systemd user-service path.
  - `scripts/minafox-update.sh` — updater installed as `minafox-update` for rebuilding/upgrading the Arch package.
  - `scripts/validate-minafox-standalone.py` — validates the `minafox` launcher, desktop entry, installer wiring, and docs.
  - `scripts/validate-minafox-arch-package.py` — validates the Arch package skeleton and simulates the `package()` function without requiring an Arch host.
  - `scripts/validate-minafox-ui.py` — validates theme/start-page structure.
  - `scripts/validate-no-host-paths.py` — validates that source files do not contain author-machine paths like hardcoded home directories.
  - `scripts/validate-no-firefox-telemetry.py` — validates telemetry prefs/policies.
  - `scripts/validate-minafox-searxng.py` — validates the SearXNG overlay.
  - `scripts/validate-minafox-ai.py` — validates the static AI Den UI and no-secrets architecture guardrails.
- `packaging/` — distro packaging experiments.
  - `packaging/arch/minafox-profile-git/` — Arch VCS package skeleton for the standalone wrapper.
- `searxng/` — local private search overlay.
  - `searxng/Dockerfile` — builds from upstream `searxng/searxng` and copies the MinaFox overlay.
  - `searxng/docker-compose.yml` — localhost-only service on `127.0.0.1:8888`.
  - `searxng/settings.yml` — privacy-first SearXNG settings.
  - `searxng/uwsgi.ini` — SearXNG container runtime config.
  - `searxng/theme/minafox.css` — MinaFox Simple-theme stylesheet.
  - `searxng/README.md` — SearXNG-specific run/update notes.

## What gets installed

- User-local launcher: `~/.local/bin/minafox`
- Firefox enterprise policies: `distribution/policies.json`
- Dedicated profile prefs: `profile/user.js`
- Optional UI CSS: `profile/userChrome.css` and `profile/userContent.css`
- Local quiet start page: `desktop/start.html`
- Desktop launcher: `desktop/minafox.desktop`
- MinaFox app icons and logo assets: `assets/`
- Local SearXNG overlay: `searxng/`
- Packaged SearXNG user unit: `systemd/user/minafox-searxng.service`
- Arch install helpers: `scripts/install-minafox-arch.sh` and `scripts/install-minafox-searxng-arch.sh`

## Install on Arch

### User-local install from a clone

```bash
git clone git@github.com:KawaiiMina/Minafox.git ~/Minafox
cd ~/Minafox
./scripts/install-minafox-arch.sh
```

Or if this folder is already present:

```bash
cd ~/Minafox
./scripts/install-minafox-arch.sh
```

### Package install from the Arch skeleton

```bash
cd ~/Minafox/packaging/arch/minafox-profile-git
makepkg -si
```

The package installs `minafox`, the desktop entry, icons, docs, and packaged assets under `/usr/share/minafox`. On first launch, `/usr/bin/minafox` automatically syncs the packaged profile, start page, desktop entry, and icons into your user-local MinaFox paths before starting Firefox.

Upgrade an installed Arch package from the MinaFox git package skeleton:

```bash
minafox-update
```

The updater uses `~/Minafox` by default, pulls the repo, then runs `makepkg -si` from `packaging/arch/minafox-profile-git`. After a successful package install it also runs `systemctl --user daemon-reload` and restarts MinaFox user services that are already active or enabled: `minafox-ai-broker.service`, `minafox-searxng.service`, and `minafox-mobile-harness.service`. Use `minafox-update --no-restart-services` if you only want the package rebuild/install step. It does not store GitHub tokens; configure GitHub HTTPS auth with `gh` or git credentials first if the repo is private.

You can still run the full setup helper manually when you want an explicit refresh or want it to attempt enterprise-policy installation:

```bash
/usr/share/minafox/scripts/install-minafox-arch.sh
```

Validate the package skeleton from any Linux dev host:

```bash
python3 scripts/validate-minafox-arch-package.py
```

Launch:

```bash
minafox
```

If your shell does not find it yet, ensure your user-local bin directory is on `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

The desktop app is named **MinaFox** and its desktop entry also launches `minafox`.

## Branding assets

MinaFox uses a cute pink/purple fox-browser logo. The mascot behind the mark is **Mina**, a cozy cosmic fox guide who represents calm navigation, privacy, and gentle help when the web gets noisy.

- Brand lore and mascot direction: `docs/brand-lore.md`

- Transparent PNG master: `assets/minafox-logo-transparent.png`
- SVG-style vector version: `assets/minafox-logo.svg`
- Flat app icon PNGs: `assets/icons/minafox-{16,32,48,64,128,256,512,1024}.png`
- Multi-size ICO: `assets/icons/minafox.ico`
- Linux icon theme layout: `assets/icons/hicolor/<size>x<size>/apps/minafox.png`

The desktop launcher uses `Icon=minafox`, and the Arch installer copies the hicolor icons into `~/.local/share/icons/hicolor/`.

## Hybrid MinaFox UI theme

The current visual direction is a hybrid of calm Zen-like minimalism and Arc-like workspace structure, but with MinaFox’s own kawaii pink/purple identity.

Implemented theme files:

- `profile/userChrome.css` — Firefox chrome theme: dark lavender glass, a more centered command-bar-like URL bar with pink/violet focus glow, rounded soft tab pills, named design tokens for rail/pill/glow surfaces, and conservative sidebar/panel styling.
- `desktop/start.html` — cosmic Arc/Zen-inspired local start page with a floating workspace rail, soft tab preview, centered MinaFox SearXNG command/search bar, quick app cards, safe Settings/Profile action buttons, focus/notes/lofi widgets, a first-screen Mina AI Den card, roadmap card, and design-system palette card.
- `profile/userContent.css` — scoped support styling for `about:home`, `about:newtab`, and the local MinaFox start page only.
- `profile/user.js` — enables `toolkit.legacyUserProfileCustomizations.stylesheets` so Firefox loads `userChrome.css`.
- `scripts/validate-minafox-ui.py` — repeatable validation gate for the theme structure.

## Mina AI Den

MinaFox includes the first **Mina AI Den** surface on the start page. It stays privacy-first: browser JavaScript only calls the localhost `minafox-ai-broker` at `http://127.0.0.1:8765`, makes no direct cloud-provider or Hermes Gateway calls, and stores no secrets in static files.

Provider placeholders shown in the UI:

- Local: Ollama
- Cloud: OpenAI / ChatGPT-compatible APIs, Gemini, Claude, and OpenRouter
- LAN / advanced: Hermes Gateway

The future architecture is a localhost-only broker bound to `127.0.0.1`, with user-local config at `~/.config/minafox/ai.yaml` and provider keys read from environment variables or a future keyring integration. Hermes Gateway is labeled separately because it may connect to tool-capable Hermes agents and will require explicit pairing/auth before implementation.

Run the local broker from a checkout:

```bash
cd ~/Minafox
./scripts/minafox-ai-broker.sh
```

Run the broker from the installed Arch package:

```bash
minafox-ai-broker
systemctl --user enable --now minafox-ai-broker.service
```

The broker exposes:

- `GET /health`
- `GET /providers`
- `GET /hermes/health`
- `POST /chat` — local Ollama only, disabled unless `MINAFOX_AI_ENABLE_OLLAMA_CHAT=1` is set.
- `POST /test-provider` — local Ollama health check.

To try local Ollama chat after starting Ollama:

```bash
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 ./scripts/minafox-ai-broker.sh
```

Cloud providers remain metadata-only until a secrets backend exists. Hermes Gateway remains detection-only until explicit pairing/auth and tool-safety UX exists.

Hermes API Server should stay on loopback at `http://127.0.0.1:8642`. Store `API_SERVER_KEY` or `HERMES_API_SERVER_KEY` only in local env/secret files, not in MinaFox.

Architecture notes: `docs/ai-provider-architecture.md`

## Android/LAN UX harness

For Android responsiveness and touch/UX testing, use the lightweight harness instead of compiling a full browser APK. It serves `desktop/start.html` and injects runtime endpoint URLs so the phone does not accidentally call phone-local `127.0.0.1`.

Trusted LAN/Tailscale harness example:

```bash
cd ~/Minafox
python3 scripts/serve-minafox-mobile.py \
  --host 0.0.0.0 \
  --mode lan-test \
  --search-base-url http://<desktop-lan-ip>:8888 \
  --search-action-url http://<desktop-lan-ip>:8888/search \
  --ai-broker-url http://<desktop-lan-ip>:8765
```

Then open this on Android:

```text
http://<desktop-lan-ip>:8766/
```

Installed package service option:

```bash
systemctl --user enable --now minafox-mobile-harness.service
systemctl --user status minafox-mobile-harness.service
```

The packaged harness service defaults to `0.0.0.0:8766` for trusted LAN testing. Only enable it on a trusted LAN/Tailscale network, and keep your firewall/router from exposing port `8766` to untrusted networks. Override `MINAFOX_MOBILE_SEARCH_BASE_URL`, `MINAFOX_MOBILE_SEARCH_ACTION_URL`, and `MINAFOX_MOBILE_AI_BROKER_URL` with a user-service override if Android should point at a specific LAN/Tailscale hostname instead of loopback.

If you also want AI Den status/chat from Android, the broker must be exposed explicitly for trusted local testing only:

```bash
MINAFOX_AI_BROKER_ALLOW_LAN=1 \
MINAFOX_AI_BROKER_ALLOWED_ORIGINS=http://<desktop-lan-ip>:8766 \
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 \
MINAFOX_AI_BROKER_HOST=0.0.0.0 \
./scripts/minafox-ai-broker.sh
```

Safety notes:

- Loopback remains the default for desktop/private mode.
- Never use wildcard CORS; list the harness origin with `MINAFOX_AI_BROKER_ALLOWED_ORIGINS`.
- Do not put cloud provider keys in the harness, start page, localStorage, or static files.
- Check 360px, 390px, 430px, and 768px widths for readable search, AI status, and touch targets.

Validate the AI surface and privacy guardrails:

```bash
python3 scripts/validate-minafox-ai.py
```

Validate the theme, standalone wrapper, package skeleton, and host-path checks:

```bash
cd ~/Minafox
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-minafox-standalone.py
python3 scripts/validate-minafox-arch-package.py
python3 scripts/validate-no-host-paths.py
```

Manual Firefox verification:

1. Run `./scripts/install-minafox-arch.sh` to copy the profile/start page assets and install `~/.local/bin/minafox`.
2. Launch `minafox`.
3. Confirm the browser chrome uses the lavender/pink theme, the URL bar reads as a centered command bar with a stronger focus glow, and the selected tab has a soft pink/violet pill glow.
4. Confirm the start page opens, Mina AI Den is visible on the first screen, the local SearXNG search form works, and quick links open.
5. Click Settings or Profiles. Firefox blocks privileged `about:` pages from static start pages, so MinaFox should copy/show the relevant address (`about:preferences` or `about:profiles`) instead of using dead links.
6. Press `Tab` through the page; focus rings should be visible.
7. Resize the window narrow/wide; cards should collapse cleanly on small widths.
8. Open DevTools on the start page with `F12` or `Ctrl+Shift+I` and confirm no console errors.

Note: `userChrome.css` relies on Firefox internal selectors, so keep future chrome edits conservative and easy to revert when Firefox updates.

## MinaFox SearXNG search

MinaFox now includes a local SearXNG overlay that says **MinaFox** first and follows the same design philosophy as the browser shell: calm Zen-like minimalism, Arc-like glass panels, soft pink/purple identity, privacy-minded defaults, and gentle focus states instead of noisy search chrome.

Implemented SearXNG files:

- `searxng/Dockerfile` — builds from upstream `searxng/searxng` and copies the MinaFox overlay.
- `searxng/docker-compose.yml` — runs the search service on localhost only: `127.0.0.1:8888:8080`.
- `searxng/settings.yml` — privacy-first local defaults, POST search submission, safe-search default, local base URL, and upstream-compatible `simple_style: dark` with MinaFox CSS installed over the active dark stylesheet.
- `searxng/uwsgi.ini` — local container runtime config.
- `searxng/theme/minafox.css` — MinaFox theme for SearXNG’s Simple UI.
- `searxng/README.md` — run/update/manual verification notes.
- `scripts/install-minafox-searxng-arch.sh` — Arch-friendly helper using `docker compose` or `podman compose`.
- `scripts/validate-minafox-searxng.py` — repeatable validation gate for the SearXNG overlay.

Start local search from a repo checkout:

```bash
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh start
```

Start and enable local search from the Arch package as a systemd user service:

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
```

The packaged helper copies the read-only overlay into the writable runtime directory `~/.local/share/minafox/searxng`, generates a private `.env`, renders `settings.yml.local`, then runs Compose locally. Install either `docker` + `docker-compose` or `podman` + `podman-compose`. The service stays bound to `127.0.0.1:8888`.

Then open:

```text
http://127.0.0.1:8888/
```

Validate the SearXNG overlay:

```bash
cd ~/Minafox
python3 scripts/validate-minafox-searxng.py
```

Manual Firefox verification:

1. Start local MinaFox SearXNG.
2. Open `http://127.0.0.1:8888/` in MinaFox.
3. Run a harmless test search.
4. Confirm result cards use the lavender glass/pink accent theme.
5. Press `Tab`; focus rings should be visible.
6. Resize below 760px; layout should stay readable.
7. Open DevTools with `F12` or `Ctrl+Shift+I` and confirm no uncaught console errors.
8. Confirm the MinaFox start page search form submits to `http://127.0.0.1:8888/search`.

## Telemetry removal

MinaFox now disables Firefox telemetry/reporting at both layers:

- **Enterprise policies** in `distribution/policies.json`:
  - `DisableTelemetry`
  - `DisableFirefoxStudies`
  - `DisableDefaultBrowserAgent`
  - Firefox Accounts disabled by policy for this profile scaffold
  - Feedback/screenshot/background desktop integrations disabled where policy-supported
  - Key telemetry prefs also locked through the `Preferences` policy block
- **Profile prefs** in `profile/user.js`:
  - Toolkit telemetry upload/archive/new-profile/update/shutdown/BHR/coverage pings disabled
  - Health report and data submission disabled
  - Crash report checks and automatic submission disabled
  - Normandy, Shield studies, experiments, and discovery disabled
  - Activity Stream/new-tab telemetry and sponsored content disabled
  - Browser ping-centre telemetry disabled
  - Search/urlbar event telemetry and Quick Suggest data collection disabled
  - Captive portal, connectivity probe, and private attribution submission services disabled

Validate the telemetry removal gate:

```bash
cd ~/Minafox
python3 scripts/validate-no-firefox-telemetry.py
```

Important limit: this removes/disables telemetry at the profile and enterprise-policy level. It does not recompile Firefox source code to physically remove telemetry code paths from the Firefox binary.

## Hyprland bind idea

For Hyprland Lua configs, adapt to your existing style:

```lua
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("minafox"))
```

For legacy hyprland.conf:

```ini
bind = $mod, B, exec, minafox
```

## Next steps

1. Package installs now work immediately: `minafox` auto-syncs `/usr/share/minafox` assets into the dedicated user profile/local share paths on first launch.
2. Continue the cosmic Arc/Zen-inspired start-page and chrome polish.
3. Decide whether Sidebery should be force-installed by policy or documented as recommended.
4. Decide whether local SearXNG should remain optional or become a packaged user service.
5. After the wrapper and package are reliable, start the Firefox ESR source-fork proof-of-build.
6. Later: move proven branding/defaults into the source fork and only then attempt native workspace UI.

## Notes

- Extension installs are allowed, but MinaFox does not force-install add-ons by policy.
- Telemetry/studies/Pocket are disabled.
- DRM stays enabled so streaming sites can work; change `media.eme.enabled` to `false` if you prefer stricter privacy.
- The profile uses Wayland-friendly portal prefs for Hyprland.
