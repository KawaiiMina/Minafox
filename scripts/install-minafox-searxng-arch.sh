#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_SEARXNG_DIR="/usr/share/minafox/searxng"
if [[ -d "$ROOT_DIR/searxng" ]]; then
  SOURCE_SEARXNG_DIR="$ROOT_DIR/searxng"
fi
DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
RUNTIME_SEARXNG_DIR="$DATA_HOME/minafox/searxng"
LOCAL_URL="http://127.0.0.1:8888/"
ACTION="${1:-start}"

usage() {
  cat <<'EOF'
Usage: install-minafox-searxng-arch.sh [start|service|stop|status|logs|install-service]

Actions:
  start           Prepare per-user config and run Docker/Podman Compose detached.
  service         Prepare per-user config and run Compose in the foreground for systemd --user.
  stop            Stop the Compose service from the per-user runtime directory.
  status          Show the systemd --user service status.
  logs            Follow the systemd --user service logs.
  install-service Enable and start minafox-searxng.service for this user.
EOF
}

find_compose() {
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
}

check_docker_daemon() {
  if [[ "${compose_cmd[0]}" == "docker" ]] && ! docker info >/dev/null 2>&1; then
    cat >&2 <<'EOF'
Docker is installed, but this user cannot talk to the Docker daemon.

On Arch, either run this helper with the right privileges, or add your user to
the docker group and re-login:
  sudo usermod -aG docker <your-user>

Then retry:
  /usr/share/minafox/scripts/install-minafox-searxng-arch.sh start
EOF
    exit 1
  fi
}

copy_overlay_file() {
  local rel="$1"
  install -Dm644 "$SOURCE_SEARXNG_DIR/$rel" "$RUNTIME_SEARXNG_DIR/$rel"
}

prepare_runtime_dir() {
  if [[ ! -d "$SOURCE_SEARXNG_DIR" ]]; then
    echo "Missing MinaFox SearXNG directory: $SOURCE_SEARXNG_DIR" >&2
    exit 1
  fi

  mkdir -p "$RUNTIME_SEARXNG_DIR"
  copy_overlay_file Dockerfile
  copy_overlay_file docker-compose.yml
  copy_overlay_file settings.yml
  copy_overlay_file uwsgi.ini
  copy_overlay_file README.md
  copy_overlay_file theme/minafox.css

  cd "$RUNTIME_SEARXNG_DIR"

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
      echo "Need openssl or python3 to generate a SearXNG secret key." >&2
      exit 1
    fi
    umask 077
    printf 'SEARXNG_SECRET_KEY=%s\n' "$secret_key" > .env
    echo "Created local SearXNG .env with a generated secret key at: $RUNTIME_SEARXNG_DIR/.env"
  fi

  SEARXNG_SECRET_KEY="$(grep -E '^SEARXNG_SECRET_KEY=' .env | tail -n 1 | cut -d= -f2- || true)"
  if [[ -z "${SEARXNG_SECRET_KEY:-}" ]]; then
    echo "Missing SEARXNG_SECRET_KEY in $RUNTIME_SEARXNG_DIR/.env" >&2
    exit 1
  fi
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
  chmod 600 .env settings.yml.local
  export MINAFOX_SEARXNG_SETTINGS=./settings.yml.local
}

install_user_service() {
  if [[ -f "$ROOT_DIR/systemd/user/minafox-searxng.service" && ! -f /usr/lib/systemd/user/minafox-searxng.service ]]; then
    mkdir -p "$HOME/.config/systemd/user"
    sed "s|/usr/share/minafox/scripts/install-minafox-searxng-arch.sh|$SCRIPT_DIR/install-minafox-searxng-arch.sh|g" \
      "$ROOT_DIR/systemd/user/minafox-searxng.service" > "$HOME/.config/systemd/user/minafox-searxng.service"
    echo "Installed user unit copy to: $HOME/.config/systemd/user/minafox-searxng.service"
  fi

  systemctl --user daemon-reload
  systemctl --user enable --now minafox-searxng.service
  echo "MinaFox SearXNG user service enabled."
  echo "Status: systemctl --user status minafox-searxng.service"
  echo "Logs:   journalctl --user -u minafox-searxng.service -f"
}

case "$ACTION" in
  start|up)
    prepare_runtime_dir
    find_compose
    check_docker_daemon
    "${compose_cmd[@]}" up -d --build
    echo "MinaFox SearXNG is starting at: $LOCAL_URL"
    echo "Runtime directory: $RUNTIME_SEARXNG_DIR"
    echo "Open it in MinaFox, or use the MinaFox start page search box."
    ;;
  service)
    prepare_runtime_dir
    find_compose
    check_docker_daemon
    exec "${compose_cmd[@]}" up --build
    ;;
  stop|down)
    prepare_runtime_dir
    find_compose
    "${compose_cmd[@]}" down
    ;;
  status)
    systemctl --user status minafox-searxng.service
    ;;
  logs)
    journalctl --user -u minafox-searxng.service -f
    ;;
  install-service)
    install_user_service
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "Unknown action: $ACTION" >&2
    usage >&2
    exit 2
    ;;
esac
