# MinaFox — standalone Firefox distribution starter

This is a practical custom Firefox distribution/profile scaffold for an Arch + Hyprland desktop.

MinaFox is currently in its **Standalone wrapper** phase: installing the repo gives you a dedicated `minafox` launcher, desktop entry, icon identity, profile namespace, themed start page, and policy/profile hardening while using the system Firefox binary underneath.

It is **not** a full Firefox source fork yet. The plan is: Standalone wrapper now, Arch package next, source fork later after the wrapper distribution is reliable.

## Repository layout

The GitHub repo is organized around the installable pieces:

- `assets/` — MinaFox logo sources and generated app icons.
  - `assets/minafox-logo-transparent.png` — transparent master PNG.
  - `assets/minafox-logo.svg` — SVG-style logo wrapper.
  - `assets/icons/` — generated PNG/ICO app icons.
  - `assets/icons/hicolor/` — Linux icon-theme layout copied during install.
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
  - `scripts/install-minafox-searxng-arch.sh` — starts the local MinaFox SearXNG service with Docker/Podman Compose.
  - `scripts/validate-minafox-standalone.py` — validates the `minafox` launcher, desktop entry, installer wiring, and docs.
  - `scripts/validate-minafox-arch-package.py` — validates the Arch package skeleton and simulates the `package()` function without requiring an Arch host.
  - `scripts/validate-minafox-ui.py` — validates theme/start-page structure.
  - `scripts/validate-no-host-paths.py` — validates that source files do not contain author-machine paths like hardcoded home directories.
  - `scripts/validate-no-firefox-telemetry.py` — validates telemetry prefs/policies.
  - `scripts/validate-minafox-searxng.py` — validates the SearXNG overlay.
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

The package installs `minafox`, the desktop entry, icons, docs, and packaged assets under `/usr/share/minafox`. After package install, run this once as your user to sync the full profile/start-page assets:

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

MinaFox uses a cute pink/purple fox-browser logo.

- Transparent PNG master: `assets/minafox-logo-transparent.png`
- SVG-style vector version: `assets/minafox-logo.svg`
- Flat app icon PNGs: `assets/icons/minafox-{16,32,48,64,128,256,512,1024}.png`
- Multi-size ICO: `assets/icons/minafox.ico`
- Linux icon theme layout: `assets/icons/hicolor/<size>x<size>/apps/minafox.png`

The desktop launcher uses `Icon=minafox`, and the Arch installer copies the hicolor icons into `~/.local/share/icons/hicolor/`.

## Hybrid MinaFox UI theme

The current visual direction is a hybrid of calm Zen-like minimalism and Arc-like workspace structure, but with MinaFox’s own kawaii pink/purple identity.

Implemented theme files:

- `profile/userChrome.css` — Firefox chrome theme: dark lavender glass, rounded URL bar, soft tab pills, pink/violet active glow, and sidebar/bookmarks styling.
- `desktop/start.html` — cozy local start page with a centered MinaFox SearXNG search bar, workspace bubbles, and quick-link cards.
- `profile/userContent.css` — scoped support styling for `about:home`, `about:newtab`, and the local MinaFox start page only.
- `profile/user.js` — enables `toolkit.legacyUserProfileCustomizations.stylesheets` so Firefox loads `userChrome.css`.
- `scripts/validate-minafox-ui.py` — repeatable validation gate for the theme structure.

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
3. Confirm the browser chrome uses the lavender/pink theme and the selected tab has a soft glow.
4. Confirm the start page opens, the local SearXNG search form works, and quick links open.
5. Press `Tab` through the page; focus rings should be visible.
6. Resize the window narrow/wide; cards should collapse cleanly on small widths.
7. Open DevTools on the start page with `F12` or `Ctrl+Shift+I` and confirm no console errors.

Note: `userChrome.css` relies on Firefox internal selectors, so keep future chrome edits conservative and easy to revert when Firefox updates.

## MinaFox SearXNG search

MinaFox now includes a local SearXNG overlay that follows the same design philosophy as the browser shell: calm Zen-like minimalism, Arc-like glass panels, and a soft pink/purple MinaFox identity.

Implemented SearXNG files:

- `searxng/Dockerfile` — builds from upstream `searxng/searxng` and copies the MinaFox overlay.
- `searxng/docker-compose.yml` — runs the search service on localhost only: `127.0.0.1:8888:8080`.
- `searxng/settings.yml` — privacy-first local defaults, POST search submission, safe-search default, local base URL, and `simple_style: minafox`.
- `searxng/uwsgi.ini` — local container runtime config.
- `searxng/theme/minafox.css` — MinaFox theme for SearXNG’s Simple UI.
- `searxng/README.md` — run/update/manual verification notes.
- `scripts/install-minafox-searxng-arch.sh` — Arch-friendly helper using `docker compose` or `podman compose`.
- `scripts/validate-minafox-searxng.py` — repeatable validation gate for the SearXNG overlay.

Start local search:

```bash
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh
```

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

1. Make the packaged launcher auto-sync `/usr/share/minafox` assets into the dedicated user profile on first run.
2. Continue the cosmic Arc/Zen-inspired start-page and chrome polish.
3. Decide whether Sidebery should be force-installed by policy or documented as recommended.
4. Decide whether local SearXNG should remain optional or become a packaged user service.
5. After the wrapper and package are reliable, start the Firefox ESR source-fork proof-of-build.
6. Later: move proven branding/defaults into the source fork and only then attempt native workspace UI.

## Notes

- uBlock Origin is force-installed by policy.
- Telemetry/studies/Pocket are disabled.
- DRM stays enabled so streaming sites can work; change `media.eme.enabled` to `false` if you prefer stricter privacy.
- The profile uses Wayland-friendly portal prefs for Hyprland.
