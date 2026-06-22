# Troubleshooting

This page covers the current standalone wrapper/profile release. MinaFox uses the distro Firefox binary, optional local services, and static start-page fallbacks; it is not a compiled Firefox fork.

## `minafox` command not found

For user-local installs, ensure `~/.local/bin` is on `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

For package installs, verify package files:

```bash
pacman -Ql minafox-profile-git | grep /usr/bin/minafox
```

If the package is installed but the shell still cannot find `minafox`, refresh the shell command cache or open a new terminal:

```bash
hash -r
command -v minafox
```

See [Getting Started](Getting-Started) and [Packaging and Updating](Packaging-and-Updating) for the expected install paths.

## Firefox binary is missing

MinaFox launches the system Firefox package. It does not bundle or replace Firefox.

```bash
command -v firefox
pacman -Q firefox
```

On Arch, install the distro package:

```bash
sudo pacman -S --needed firefox
```

If you intentionally use another compatible Firefox binary, point the launcher at it:

```bash
MINAFOX_FIREFOX_BIN=/path/to/firefox minafox
```

## Profile path or assets are missing

The expected profile path is `~/.mozilla/firefox/minafox`. For package installs, first launch syncs packaged assets from `/usr/share/minafox` into user-local paths.

```bash
ls ~/.mozilla/firefox/minafox
ls ~/.mozilla/firefox/minafox/chrome
ls ~/.local/share/minafox/start.html
```

If the profile does not exist, run `minafox` once. If packaged assets did not sync, check the share directory:

```bash
ls /usr/share/minafox
```

Then refresh assets from an installed package:

```bash
minafox-update
```

Use `minafox-update --no-sync-profile-assets` only when you intentionally want to preserve local profile/start-page customizations.

## Browser opens but theme is missing

Run the installer/sync again:

```bash
cd ~/Minafox
./scripts/install-minafox-arch.sh
```

Check that `toolkit.legacyUserProfileCustomizations.stylesheets` is enabled in `profile/user.js`.

If the theme partly applies but some chrome details look different after a Firefox update, treat it as a chrome-polish compatibility issue. MinaFox's `userChrome.css` is version-sensitive; the fallback expectation is that Firefox still runs with the MinaFox profile and start page even if a tab, toolbar, or sidebar detail needs CSS follow-up.

```bash
firefox --version
minafox --version
```

Run the UI validator before making chrome CSS changes:

```bash
python3 scripts/validate-minafox-ui.py
```

See [Known Limitations](Known-Limitations) for the release boundary.

## Package install fails

The Arch package skeleton needs `base-devel`, `git`, and the distro `firefox` dependency.

```bash
sudo pacman -S --needed base-devel git firefox
cd ~/Minafox/packaging/arch/minafox-profile-git
makepkg -si
```

If validation fails, run:

```bash
python3 scripts/validate-minafox-arch-package.py
git diff --check
bash -n scripts/*.sh
```

The package should remain a wrapper/profile package around distro Firefox. It should not provide, conflict with, bundle, replace, or compile Firefox.

## `minafox-update` fails

`minafox-update` uses `~/Minafox` by default, runs `git pull --ff-only`, builds from `packaging/arch/minafox-profile-git`, then syncs installed assets from `/usr/share/minafox`.

Check the repo path:

```bash
ls ~/Minafox/packaging/arch/minafox-profile-git
minafox-update --repo /path/to/Minafox
MINAFOX_REPO_DIR=/path/to/Minafox minafox-update
```

Common causes:

- `git` is missing.
- `makepkg` is missing because `base-devel` is not installed.
- The checkout has local commits or edits that prevent `git pull --ff-only`.
- `/usr/share/minafox` is missing because the package install did not complete.

If you only need to rebuild/install without touching local browser customizations:

```bash
minafox-update --no-sync-profile-assets
```

If a service restart is getting in the way while debugging the package update:

```bash
minafox-update --no-restart-services
```

## SearXNG search is offline

```bash
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh start
```

Open `http://127.0.0.1:8888/`.

The service is optional and not auto-enabled by the package. It also needs Docker Compose or Podman Compose available to start the local SearXNG container.

```bash
command -v docker || command -v podman
docker compose version || podman compose version
```

Keep SearXNG loopback-local by default. For Android testing, route it over a trusted LAN/Tailscale path rather than publishing it publicly. See [MinaFox Search](MinaFox-Search).

## AI Den says broker is offline

```bash
systemctl --user status minafox-ai-broker.service
curl http://127.0.0.1:8765/health
curl http://127.0.0.1:8765/providers
```

Start manually:

```bash
cd ~/Minafox
./scripts/minafox-ai-broker.sh
```

From an installed package, enable the optional user service explicitly:

```bash
systemctl --user enable --now minafox-ai-broker.service
```

The broker binds to `127.0.0.1:8765` by default and refuses non-loopback binds unless LAN mode is explicitly allowed. See [Mina AI Den](Mina-AI-Den).

## Ollama chat does not enable

Make sure Ollama is running and the broker is explicitly allowed to chat:

```bash
curl http://127.0.0.1:11434/api/tags
MINAFOX_AI_ENABLE_OLLAMA_CHAT=1 ./scripts/minafox-ai-broker.sh
```

Cloud providers are metadata-only in this release, and Hermes Gateway is detection-only. If the UI says cloud or Hermes chat is unavailable, that is the expected conservative behavior.

## Android page loads but search/AI points to the phone

On Android, `127.0.0.1` means the phone. Use the mobile harness and configure desktop/LAN URLs:

```bash
python3 scripts/serve-minafox-mobile.py \
  --host 0.0.0.0 \
  --mode lan-test \
  --harness-url http://<desktop-lan-ip>:8766 \
  --search-base-url http://<desktop-lan-ip>:8888 \
  --search-action-url http://<desktop-lan-ip>:8888/search \
  --ai-broker-url http://<desktop-lan-ip>:8765
```

Open `http://<desktop-lan-ip>:8766/`. If the page loads but the companion card shows a bad harness URL, set `MINAFOX_MOBILE_HARNESS_URL=http://<desktop-lan-ip>:8766` in the user-service override or pass `--harness-url` manually.

Diagnostics:

```bash
curl http://<desktop-lan-ip>:8766/health
curl http://<desktop-lan-ip>:8766/config
curl http://<desktop-lan-ip>:8766/android-checklist
```

If Android cannot reach the harness:

- confirm the desktop and phone are on the same trusted LAN/Tailscale network;
- check the desktop firewall for port `8766`;
- use the desktop LAN/Tailscale IP or hostname, not `127.0.0.1`;
- stop testing rather than exposing the harness through a public router or reverse proxy.

See [Android/LAN Testing](Android-LAN-Testing).

## LAN broker refuses to start

For trusted LAN testing you need both the LAN flag and explicit origins:

```bash
MINAFOX_AI_BROKER_ALLOW_LAN=1 \
MINAFOX_AI_BROKER_ALLOWED_ORIGINS=http://<desktop-lan-ip>:8766 \
MINAFOX_AI_BROKER_HOST=0.0.0.0 \
./scripts/minafox-ai-broker.sh
```

Do not use wildcard CORS.

## `minafox-update` did not restart a service

`minafox-update` restarts services only when they are already active or enabled. Enable the service first:

```bash
systemctl --user enable --now minafox-ai-broker.service
systemctl --user enable --now minafox-searxng.service
systemctl --user enable --now minafox-mobile-harness.service
```

Then run `minafox-update`.

## Start-page Settings/Profile buttons copy text

This is expected. Firefox blocks static local pages from directly opening privileged `about:` pages such as `about:preferences` and `about:profiles` in some contexts. MinaFox copies or displays those commands instead of pretending the button can always navigate there.

Paste the copied command into the address bar, or open the page manually:

```text
about:preferences
about:profiles
```

## UI polish looks degraded

MinaFox's chrome polish is CSS layered over distro Firefox. Firefox updates can change internal selectors and spacing. The release fallback is conservative:

- Firefox should still launch with the MinaFox profile.
- The local start page should remain usable.
- Focus rings and readable mobile layouts should remain intact.
- Minor chrome mismatches should be tracked as follow-up CSS work, not treated as a source-fork feature.

Validate the current UI files:

```bash
python3 scripts/validate-minafox-ui.py
python3 scripts/validate-minafox-standalone.py
```

## Validation commands

```bash
python3 scripts/test-serve-minafox-mobile.py
python3 scripts/test-minafox-ai-broker.py
python3 scripts/validate-minafox-searxng.py
python3 scripts/validate-minafox-ai.py
python3 scripts/validate-minafox-arch-package.py
git diff --check
tick validate
```
