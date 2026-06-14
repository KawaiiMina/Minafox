#!/usr/bin/env bash
set -euo pipefail

PROFILE_DIR="${MINAFOX_PROFILE_DIR:-$HOME/.mozilla/firefox/minafox}"
FIREFOX_BIN="${MINAFOX_FIREFOX_BIN:-firefox}"
SHARE_DIR="${MINAFOX_SHARE_DIR:-/usr/share/minafox}"
START_DIR="$HOME/.local/share/minafox"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"
SYNC_MARKER="$PROFILE_DIR/.minafox-packaged-sync.done"

export MOZ_ENABLE_WAYLAND=1

render_template() {
  local src="$1"
  local dest="$2"
  local start_url
  start_url="$(python3 -c 'from pathlib import Path; print((Path.home() / ".local/share/minafox/start.html").as_uri())')"
  sed "s|__MINAFOX_START_URL__|$start_url|g" "$src" > "$dest"
}

sync_packaged_assets() {
  [[ -d "$SHARE_DIR" ]] || return 0
  [[ ! -e "$SYNC_MARKER" ]] || return 0

  mkdir -p "$PROFILE_DIR/chrome" "$START_DIR" "$DESKTOP_DIR" "$ICON_DIR"

  if [[ -f "$SHARE_DIR/profile/user.js" ]]; then
    render_template "$SHARE_DIR/profile/user.js" "$PROFILE_DIR/user.js"
  fi
  if [[ -f "$SHARE_DIR/profile/userChrome.css" ]]; then
    cp "$SHARE_DIR/profile/userChrome.css" "$PROFILE_DIR/chrome/userChrome.css"
  fi
  if [[ -f "$SHARE_DIR/profile/userContent.css" ]]; then
    render_template "$SHARE_DIR/profile/userContent.css" "$PROFILE_DIR/chrome/userContent.css"
  fi
  if [[ -f "$SHARE_DIR/desktop/start.html" ]]; then
    cp "$SHARE_DIR/desktop/start.html" "$START_DIR/start.html"
  fi
  if [[ -f "$SHARE_DIR/desktop/minafox.desktop" ]]; then
    cp "$SHARE_DIR/desktop/minafox.desktop" "$DESKTOP_DIR/minafox.desktop"
  fi
  if [[ -d "$SHARE_DIR/assets/icons/hicolor" ]]; then
    shopt -s nullglob
    icon_sources=("$SHARE_DIR/assets/icons/hicolor/"*)
    shopt -u nullglob
    if (( ${#icon_sources[@]} > 0 )); then
      cp -R "${icon_sources[@]}" "$ICON_DIR/"
    fi
  fi

  update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
  gtk-update-icon-cache "$ICON_DIR" >/dev/null 2>&1 || true
  touch "$SYNC_MARKER"
}

if ! command -v "$FIREFOX_BIN" >/dev/null 2>&1; then
  echo "MinaFox launcher could not find Firefox binary: $FIREFOX_BIN" >&2
  echo "Install firefox or set MINAFOX_FIREFOX_BIN to a compatible Firefox binary." >&2
  exit 127
fi

if [[ ! -d "$PROFILE_DIR" ]]; then
  mkdir -p "$PROFILE_DIR"
  "$FIREFOX_BIN" --CreateProfile "minafox $PROFILE_DIR" >/dev/null 2>&1 || true
fi

sync_packaged_assets

exec "${MINAFOX_FIREFOX_BIN:-firefox}" --name minafox --class MinaFox --profile "$PROFILE_DIR" "$@"
