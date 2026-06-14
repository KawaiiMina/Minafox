# MinaFox Search

MinaFox Search is a local SearXNG overlay with MinaFox branding, privacy-first defaults, and a calm pink/purple glass style.

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
```

Open:

```text
http://127.0.0.1:8888/
```

## Start from package

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
```

## Runtime files

The helper keeps generated runtime config outside the repo:

```text
~/.local/share/minafox/searxng
```

It copies the overlay, chooses Docker or Podman Compose, creates a local `.env`, renders `settings.yml.local`, and starts the service.

## Stop/update

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh stop
systemctl --user restart minafox-searxng.service
```

## Manual verification

1. Open `http://127.0.0.1:8888/` in MinaFox.
2. Search for a harmless query.
3. Confirm result cards use the lavender glass/pink accent theme.
4. Press `Tab`; focus rings should be visible.
5. Resize below 760px; layout should remain readable.
6. Confirm the start page search form submits to `/search` on the configured SearXNG host.

## Validation

```bash
python3 scripts/validate-minafox-searxng.py
```
