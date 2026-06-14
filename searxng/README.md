# MinaFox SearXNG

A local MinaFox-flavoured SearXNG overlay for private search.

Design goals:

- calm Zen-like minimalism
- Arc-like glass panels and workspace structure
- MinaFox pink/purple kawaii identity
- privacy-first local deployment on `http://127.0.0.1:8888/`

## Files

- `Dockerfile` — builds from upstream `searxng/searxng` and copies the MinaFox overlay.
- `docker-compose.yml` — runs only on localhost: `127.0.0.1:8888:8080`.
- `settings.yml` — MinaFox privacy/UI defaults.
- `uwsgi.ini` — local container runtime config.
- `theme/minafox.css` — custom Simple theme stylesheet copied as `minafox.min.css`.

## Run locally

From the repo root or from the packaged install, prefer the helper so the local SearXNG secret is generated safely and the writable runtime files live under `~/.local/share/minafox/searxng`:

```bash
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh start
```

After installing the Arch package, the same helper is available at:

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh start
```

Then open:

```text
http://127.0.0.1:8888/
```

### Manual Compose run

If you want to run Compose directly, still keep generated runtime files outside the repo checkout:

```bash
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh start
cd ~/.local/share/minafox/searxng
# inspect or manage the generated runtime files here
```

Or, after the helper has prepared `~/.local/share/minafox/searxng/settings.yml.local`, run Compose manually from the runtime directory:

```bash
cd ~/.local/share/minafox/searxng
MINAFOX_SEARXNG_SETTINGS=./settings.yml.local docker compose up -d --build
```

For Podman Compose, replace the last command with:

```bash
MINAFOX_SEARXNG_SETTINGS=./settings.yml.local podman compose up -d --build
```

## Arch helper and user service

From the repo root:

```bash
./scripts/install-minafox-searxng-arch.sh start
```

From the Arch package:

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh install-service
systemctl --user status minafox-searxng.service
journalctl --user -u minafox-searxng.service -f
```

The helper:

1. copies the read-only overlay into the writable user runtime directory `~/.local/share/minafox/searxng`,
2. chooses `docker compose` or `podman compose`,
3. creates a local `.env` file with a generated secret when possible,
4. renders `settings.yml.local` without committing secrets,
5. starts the local MinaFox SearXNG container or runs it in the foreground for the systemd user service,
6. prints the local URL.

## Firefox / MinaFox manual verification

1. Start the service with `./scripts/install-minafox-searxng-arch.sh`.
2. Open `http://127.0.0.1:8888/` in MinaFox.
3. Search for a harmless query such as `arch linux video editor`.
4. Confirm result cards use the lavender glass/pink accent theme.
5. Press `Tab`; focus rings should be visible.
6. Resize the window below 760px; panels should remain readable and rounded.
7. Open DevTools (`F12` or `Ctrl+Shift+I`) and confirm no uncaught console errors.
8. Confirm the MinaFox start page search form submits to `http://127.0.0.1:8888/search`.

## Stop / update

```bash
/usr/share/minafox/scripts/install-minafox-searxng-arch.sh stop
# or from a repo checkout:
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh stop

cd ~/.local/share/minafox/searxng
docker compose pull
docker compose up -d --build
```

If you installed the user service, prefer:

```bash
systemctl --user restart minafox-searxng.service
```

## Notes

- The container is bound to localhost only; it is not a public SearXNG instance.
- The upstream SearXNG image supplies the Python app. MinaFox only overlays config and CSS.
- SearXNG theme internals may change upstream; keep custom CSS conservative and easy to remove.
