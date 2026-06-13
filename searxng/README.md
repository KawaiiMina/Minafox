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

From the repo root, prefer the helper so the local SearXNG secret is generated safely:

```bash
cd ~/Minafox
./scripts/install-minafox-searxng-arch.sh
```

Then open:

```text
http://127.0.0.1:8888/
```

### Manual Compose run

If you want to run Compose directly, create a local runtime settings file first so SearXNG does not use the checked-in placeholder secret:

```bash
cd ~/Minafox/searxng
printf 'SEARXNG_SECRET_KEY=%s\n' "$(openssl rand -hex 32)" > .env
sed "s/MINAFOX_CHANGE_ME_WITH_INSTALLER/$(cut -d= -f2- .env)/g" settings.yml > settings.yml.local
MINAFOX_SEARXNG_SETTINGS=./settings.yml.local docker compose up -d --build
```

For Podman Compose, replace the last command with:

```bash
MINAFOX_SEARXNG_SETTINGS=./settings.yml.local podman compose up -d --build
```

## Arch helper

From the repo root:

```bash
./scripts/install-minafox-searxng-arch.sh
```

The helper:

1. chooses `docker compose` or `podman compose`,
2. creates a local `.env` file with a generated secret when possible,
3. starts the local MinaFox SearXNG container,
4. prints the local URL.

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
cd ~/Minafox/searxng
docker compose down
# or: podman compose down

docker compose pull
docker compose up -d --build
```

## Notes

- The container is bound to localhost only; it is not a public SearXNG instance.
- The upstream SearXNG image supplies the Python app. MinaFox only overlays config and CSS.
- SearXNG theme internals may change upstream; keep custom CSS conservative and easy to remove.
