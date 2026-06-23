# MinaFox Search

MinaFox uses local SearXNG as the default MinaFox search layer. The Arch package installs the service unit and helper, but it does not auto-enable the service.

```text
MinaFox UI → local SearXNG → upstream engines
```

The browser/start page sends searches to the local MinaFox SearXNG service at `http://127.0.0.1:8888/search` using POST. SearXNG then handles upstream engine selection, categories, autocomplete, safe-search defaults, result rendering, and privacy behavior.

## Default architecture

- **Browser UI:** `desktop/start.html` owns the search box and category shortcuts.
- **Local search layer:** `searxng/` provides the MinaFox-flavoured SearXNG overlay.
- **Runtime service:** `minafox-searxng.service` starts the local SearXNG container through `scripts/install-minafox-searxng-arch.sh`.
- **Writable config/runtime:** generated files live under `~/.local/share/minafox/searxng`, not in the repo checkout or `/usr/share`.

## Engine support plan

Future search-engine support is configured through SearXNG engine settings. Support for DuckDuckGo, Brave, Startpage, Google, Wikipedia, or other engines should be added by changing SearXNG settings/categories, not by adding direct browser-side search integrations.

Do not add direct browser-side search integrations for upstream engines. MinaFox should not grow separate hardcoded form actions or JavaScript fetch paths for Google, DuckDuckGo, Brave, Startpage, Bing, or similar engines. Keep the browser UI pointed at local SearXNG so search privacy and engine behavior stay centralized.

## Files

- `searxng/Dockerfile` — builds from upstream `searxng/searxng` and copies the MinaFox overlay.
- `searxng/docker-compose.yml` — local-only service on `127.0.0.1:8888`.
- `searxng/settings.yml` — privacy-first SearXNG settings.
- `searxng/uwsgi.ini` — container runtime config.
- `searxng/theme/minafox.css` — MinaFox Simple theme stylesheet.
- `scripts/install-minafox-searxng-arch.sh` — Docker/Podman Compose helper.

## Start from checkout

```bash
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh start
curl -fsS http://127.0.0.1:8888/
```

Open:

```text
http://127.0.0.1:8888/
```

## Start from package

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh status
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
```

## Runtime files

The helper keeps generated runtime config outside the repo:

```text
~/.local/share/minafox/searxng
```

It copies the overlay, chooses Docker or Podman Compose, creates a local `.env`, renders `settings.yml.local`, and starts the service.

## Where to configure engines

Primary files:

- `searxng/settings.yml` — checked-in privacy and UI defaults.
- `scripts/install-minafox-searxng-arch.sh` — renders runtime settings and generated secrets.
- `~/.local/share/minafox/searxng/settings.yml.local` — generated runtime settings on a user machine.

When adding engine customization later, prefer documenting the desired SearXNG settings in this page and validating the checked-in template with `scripts/validate-minafox-searxng.py`.

## Privacy rules

- Keep the SearXNG service bound to `127.0.0.1:8888` by default.
- Keep the start page search form using POST.
- Manage upstream engines through SearXNG settings, not browser-side provider integrations.
- Do not commit generated SearXNG secrets.
- Do not place upstream search API keys or provider credentials in static browser assets.
- If LAN/mobile testing needs search, route through trusted local/Tailscale access rather than exposing SearXNG publicly.

## Stop/update

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh stop
systemctl --user disable minafox-searxng.service
```

Refresh a running installed service after package or overlay changes:

```bash
systemctl --user restart minafox-searxng.service
```

## Manual verification

1. Open `http://127.0.0.1:8888/` in MinaFox.
2. Search for a harmless query.
3. Confirm result cards use the lavender glass/pink accent theme.
4. Press `Tab`; focus rings should be visible.
5. Resize below 760px; layout should remain readable.
6. Confirm the start page search form submits to `/search` on the configured SearXNG host.

Runtime smoke checks, when Docker/Podman is available:

```bash
curl -fsS http://127.0.0.1:8888/
curl -fsS http://127.0.0.1:8888/search -d 'q=minafox'
```

## Validation

```bash
python3 scripts/validate-minafox-searxng.py
python3 scripts/validate-minafox-ui.py
```

For offline service triage and LAN boundaries, see [Troubleshooting](Troubleshooting) and [Known Limitations](Known-Limitations).
