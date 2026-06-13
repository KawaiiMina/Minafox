#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SEARXNG_DIR="$ROOT_DIR/searxng"
LOCAL_URL="http://127.0.0.1:8888/"

if [[ ! -d "$SEARXNG_DIR" ]]; then
  echo "Missing MinaFox SearXNG directory: $SEARXNG_DIR" >&2
  exit 1
fi

compose_cmd=()
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  compose_cmd=(docker compose)
elif command -v podman >/dev/null 2>&1 && podman compose version >/dev/null 2>&1; then
  compose_cmd=(podman compose)
else
  cat >&2 <<'EOF'
Neither 'docker compose' nor 'podman compose' is available.

On Arch, install one of these first, for example:
  sudo pacman -S --needed docker docker-compose
  sudo systemctl enable --now docker

or for Podman:
  sudo pacman -S --needed podman podman-compose
EOF
  exit 1
fi

cd "$SEARXNG_DIR"

if [[ "${compose_cmd[0]}" == "docker" ]] && ! docker info >/dev/null 2>&1; then
  cat >&2 <<'EOF'
Docker is installed, but this user cannot talk to the Docker daemon.

On Arch, either run this helper with the right privileges, or add your user to
the docker group and re-login:
  sudo usermod -aG docker <your-user>

Then retry:
  ./scripts/install-minafox-searxng-arch.sh
EOF
  exit 1
fi

if [[ ! -f .env ]]; then
  if command -v openssl >/dev/null 2>&1; then
    secret_key="$(openssl rand -hex 32)"
  elif command -v python3 >/dev/null 2>&1; then
    secret_key="$(python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)"
  else
    secret_key="minafox-$(date +%s)-local-only-change-this-secret"
  fi
  umask 077
  printf 'SEARXNG_SECRET_KEY=%s\n' "$secret_key" > .env
  echo "Created local SearXNG .env with a generated secret key."
fi

if [[ -f .env ]]; then
  SEARXNG_SECRET_KEY="$(grep -E '^SEARXNG_SECRET_KEY=' .env | tail -n 1 | cut -d= -f2- || true)"
fi
if [[ -n "${SEARXNG_SECRET_KEY:-}" ]]; then
  if [[ ! "$SEARXNG_SECRET_KEY" =~ ^[A-Za-z0-9._~+=:@-]{32,128}$ ]]; then
    cat >&2 <<'EOF'
Invalid SEARXNG_SECRET_KEY in searxng/.env.
Use 32-128 characters from: letters, numbers, dot, underscore, tilde, plus, equals, colon, at, hyphen.
EOF
    exit 1
  fi
  tmp_settings="$(mktemp)"
  sed "s/MINAFOX_CHANGE_ME_WITH_INSTALLER/$SEARXNG_SECRET_KEY/g" settings.yml > "$tmp_settings"
  mv "$tmp_settings" settings.yml.local
  export MINAFOX_SEARXNG_SETTINGS=./settings.yml.local
fi

"${compose_cmd[@]}" up -d --build

echo "MinaFox SearXNG is starting at: $LOCAL_URL"
echo "Open it in MinaFox, or use the MinaFox start page search box."
