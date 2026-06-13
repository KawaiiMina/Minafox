# MinaFox — custom Firefox distribution starter

This is a practical custom Firefox distribution/profile scaffold for an Arch + Hyprland desktop.

It is **not** a full Firefox fork yet. It starts with the maintainable profile/distribution layer plus a local MinaFox SearXNG search overlay.

## Repository layout

The GitHub repo is organized around the installable pieces:

- `assets/` — MinaFox logo sources and generated app icons.
  - `assets/minafox-logo-transparent.png` — transparent master PNG.
  - `assets/minafox-logo.svg` — SVG-style logo wrapper.
  - `assets/icons/` — generated PNG/ICO app icons.
  - `assets/icons/hicolor/` — Linux icon-theme layout copied during install.
- `desktop/` — desktop-facing files.
  - `desktop/start.html` — local MinaFox start page that submits searches to local SearXNG.
  - `desktop/minafox.desktop` — Linux desktop launcher.
- `distribution/` — Firefox enterprise policy files.
  - `distribution/policies.json` — extension policy, telemetry/studies shutdown, locked prefs.
- `profile/` — files copied into the dedicated Firefox profile.
  - `profile/user.js` — Firefox profile prefs, privacy hardening, chrome CSS enablement.
  - `profile/userChrome.css` — MinaFox browser-chrome theme.
  - `profile/userContent.css` — scoped content styling for Firefox start surfaces and local MinaFox page.
- `scripts/` — install and validation helpers.
  - `scripts/install-minafox-arch.sh` — installs/updates the MinaFox Firefox profile assets.
  - `scripts/install-minafox-searxng-arch.sh` — starts the local MinaFox SearXNG service with Docker/Podman Compose.
  - `scripts/validate-minafox-ui.py` — validates theme/start-page structure.
  - `scripts/validate-no-firefox-telemetry.py` — validates telemetry prefs/policies.
  - `scripts/validate-minafox-searxng.py` — validates the SearXNG overlay.
- `searxng/` — local private search overlay.
  - `searxng/Dockerfile` — builds from upstream `searxng/searxng` and copies the MinaFox overlay.
  - `searxng/docker-compose.yml` — localhost-only service on `127.0.0.1:8888`.
  - `searxng/settings.yml` — privacy-first SearXNG settings.
  - `searxng/uwsgi.ini` — SearXNG container runtime config.
  - `searxng/theme/minafox.css` — MinaFox Simple-theme stylesheet.
  - `searxng/README.md` — SearXNG-specific run/update notes.

## What gets installed

- Firefox enterprise policies: `distribution/policies.json`
- Dedicated profile prefs: `profile/user.js`
- Optional UI CSS: `profile/userChrome.css` and `profile/userContent.css`
- Local quiet start page: `desktop/start.html`
- Desktop launcher: `desktop/minafox.desktop`
- MinaFox app icons and logo assets: `assets/`
- Local SearXNG overlay: `searxng/`
- Arch install helpers: `scripts/install-minafox-arch.sh` and `scripts/install-minafox-searxng-arch.sh`

## Install on Arch

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

Launch:

```bash
firefox --profile ~/.mozilla/firefox/minafox
```

The desktop app is named **MinaFox**.

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

Validate the theme files:

```bash
cd ~/Minafox
python3 scripts/validate-minafox-ui.py
```

Manual Firefox verification:

1. Run `./scripts/install-minafox-arch.sh` to copy the profile/start page assets.
2. Launch `firefox --profile ~/.mozilla/firefox/minafox`.
3. Confirm the browser chrome uses the lavender/pink theme and the selected tab has a soft glow.
4. Confirm the start page opens, the DuckDuckGo search form works, and quick links open.
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
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd("env MOZ_ENABLE_WAYLAND=1 firefox --name minafox --class MinaFox --profile /home/wilhelmina/.mozilla/firefox/minafox"))
```

For legacy hyprland.conf:

```ini
bind = $mod, B, exec, env MOZ_ENABLE_WAYLAND=1 firefox --name minafox --class MinaFox --profile ~/.mozilla/firefox/minafox
```

## Next steps

1. Pick the base: Firefox stable, Firefox ESR, or LibreWolf.
2. Decide branding/name/icon.
3. Add curated extensions.
4. Add custom search shortcuts.
5. Add vertical tabs / Sidebery if wanted.
6. Later: make an Arch `PKGBUILD` that packages this config as `minafox-profile`.

## Notes

- uBlock Origin is force-installed by policy.
- Telemetry/studies/Pocket are disabled.
- DRM stays enabled so streaming sites can work; change `media.eme.enabled` to `false` if you prefer stricter privacy.
- The profile uses Wayland-friendly portal prefs for Hyprland.
