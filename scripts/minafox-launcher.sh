#!/usr/bin/env bash
set -euo pipefail

PROFILE_DIR="${MINAFOX_PROFILE_DIR:-$HOME/.mozilla/firefox/minafox}"
FIREFOX_BIN="${MINAFOX_FIREFOX_BIN:-firefox}"

export MOZ_ENABLE_WAYLAND=1

if ! command -v "$FIREFOX_BIN" >/dev/null 2>&1; then
  echo "MinaFox launcher could not find Firefox binary: $FIREFOX_BIN" >&2
  echo "Install firefox or set MINAFOX_FIREFOX_BIN to a compatible Firefox binary." >&2
  exit 127
fi

if [[ ! -d "$PROFILE_DIR" ]]; then
  mkdir -p "$PROFILE_DIR"
  "$FIREFOX_BIN" --CreateProfile "minafox $PROFILE_DIR" >/dev/null 2>&1 || true
fi

exec "${MINAFOX_FIREFOX_BIN:-firefox}" --name minafox --class MinaFox --profile "$PROFILE_DIR" "$@"
