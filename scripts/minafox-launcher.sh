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

merge_packaged_text_asset() {
  local src="$1"
  local dest="$2"
  local begin_marker="$3"
  local end_marker="$4"
  local rendered
  rendered="$(mktemp)"
  render_template "$src" "$rendered"
  python3 - "$dest" "$rendered" "$begin_marker" "$end_marker" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path


dest = Path(sys.argv[1])
rendered = Path(sys.argv[2])
begin = sys.argv[3]
end = sys.argv[4]
managed = rendered.read_text(encoding="utf-8")
existing = dest.read_text(encoding="utf-8") if dest.exists() else ""
managed_block = re.compile(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.DOTALL)

preserved = managed_block.sub("", existing).rstrip()
managed = managed.rstrip()
parts = []
if preserved:
    parts.append(preserved)
parts.append(f"{begin}\n{managed}\n{end}")
dest.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
PY
  rm -f "$rendered"
}

sync_packaged_assets() {
  [[ -d "$SHARE_DIR" ]] || return 0
  [[ ! -e "$SYNC_MARKER" ]] || return 0

  mkdir -p "$PROFILE_DIR/chrome" "$START_DIR" "$DESKTOP_DIR" "$ICON_DIR"

  if [[ -f "$SHARE_DIR/profile/user.js" ]]; then
    merge_packaged_text_asset \
      "$SHARE_DIR/profile/user.js" \
      "$PROFILE_DIR/user.js" \
      "// BEGIN MINAFOX PACKAGED ASSETS" \
      "// END MINAFOX PACKAGED ASSETS"
  fi
  if [[ -f "$SHARE_DIR/profile/userChrome.css" ]]; then
    merge_packaged_text_asset \
      "$SHARE_DIR/profile/userChrome.css" \
      "$PROFILE_DIR/chrome/userChrome.css" \
      "/* BEGIN MINAFOX PACKAGED ASSETS */" \
      "/* END MINAFOX PACKAGED ASSETS */"
  fi
  if [[ -f "$SHARE_DIR/profile/userContent.css" ]]; then
    merge_packaged_text_asset \
      "$SHARE_DIR/profile/userContent.css" \
      "$PROFILE_DIR/chrome/userContent.css" \
      "/* BEGIN MINAFOX PACKAGED ASSETS */" \
      "/* END MINAFOX PACKAGED ASSETS */"
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
