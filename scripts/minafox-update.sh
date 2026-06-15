#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${MINAFOX_REPO_URL:-https://github.com/KawaiiMina/Minafox.git}"
REPO_DIR="${MINAFOX_REPO_DIR:-$HOME/Minafox}"
PACKAGE_DIR="packaging/arch/minafox-profile-git"
SHARE_DIR="${MINAFOX_SHARE_DIR:-/usr/share/minafox}"
PROFILE_DIR="${MINAFOX_PROFILE_DIR:-$HOME/.mozilla/firefox/minafox}"
START_DIR="$HOME/.local/share/minafox"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"
SYNC_MARKER="$PROFILE_DIR/.minafox-packaged-sync.done"
DO_PULL=1
RESTART_SERVICES=1
SYNC_PROFILE_ASSETS=1
MINAFOX_SERVICES=(
  minafox-ai-broker.service
  minafox-searxng.service
  minafox-mobile-harness.service
)

usage() {
  cat <<'USAGE'
Usage: minafox-update [--repo DIR] [--no-pull] [--sync-profile-assets] [--no-sync-profile-assets] [--restart-services] [--no-restart-services] [--help]

Upgrade the installed MinaFox Arch package from the MinaFox git package skeleton.

Defaults:
  repo: ~/Minafox
  remote: https://github.com/KawaiiMina/Minafox.git
  share: /usr/share/minafox
  profile: ~/.mozilla/firefox/minafox

Examples:
  minafox-update
  minafox-update --repo ~/Minafox
  minafox-update --no-sync-profile-assets
  minafox-update --no-restart-services
  MINAFOX_REPO_DIR=~/src/Minafox minafox-update

After a successful package install, minafox-update refreshes MinaFox profile/start-page assets by default.
Use --no-sync-profile-assets if you intentionally keep local profile/start-page customizations.

Then it reloads the systemd user manager and restarts MinaFox user services by default:
  minafox-ai-broker.service, minafox-searxng.service, minafox-mobile-harness.service
Use --no-restart-services if you only want to rebuild/install the package and sync assets.
USAGE
}

render_template() {
  local src="$1"
  local dest="$2"
  local start_url
  start_url="$(python3 -c 'from pathlib import Path; print((Path.home() / ".local/share/minafox/start.html").as_uri())')"
  sed "s|__MINAFOX_START_URL__|$start_url|g" "$src" > "$dest"
}

merge_managed_text_asset() {
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

secret_name = re.compile(r"(?i)(api[_-]?key|token|password|passwd|secret|credential|connection[_-]?string)")
managed_block = re.compile(re.escape(begin) + r".*?" + re.escape(end) + r"\n?", re.DOTALL)
user_pref_secret = re.compile(
    r'(?i)(user_pref\(\s*"[^"]*(?:api[_-]?key|token|password|passwd|secret|credential|connection[_-]?string)[^"]*"\s*,\s*)"[^"]*"(\s*\)\s*;?)'
)
quoted_assignment_secret = re.compile(
    r'(?i)((?:api[_-]?key|token|password|passwd|secret|credential|connection[_-]?string)[^=:\n]*[=:]\s*)["\']?[^"\'\n;]+["\']?'
)


def redact_line(line: str) -> str:
    if not secret_name.search(line):
        return line
    line = user_pref_secret.sub(r'\1"[REDACTED]"\2', line)
    line = quoted_assignment_secret.sub(r'\1[REDACTED]', line)
    if secret_name.search(line) and "[REDACTED]" not in line:
        return "[REDACTED]\n" if line.endswith("\n") else "[REDACTED]"
    return line


def redact(text: str) -> str:
    return "".join(redact_line(line) for line in text.splitlines(keepends=True))


preserved = managed_block.sub("", existing)
preserved = redact(preserved).rstrip()
managed = redact(managed).rstrip()
parts = []
if preserved:
    parts.append(preserved)
parts.append(f"{begin}\n{managed}\n{end}")
dest.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
PY
  rm -f "$rendered"
}

sync_profile_assets() {
  if [[ ! -d "$SHARE_DIR" ]]; then
    echo "Warning: MinaFox packaged share directory missing: $SHARE_DIR" >&2
    echo "Profile/start-page assets were not synced." >&2
    return 0
  fi

  echo "Syncing MinaFox profile and start-page assets from $SHARE_DIR ..."
  mkdir -p "$PROFILE_DIR/chrome" "$START_DIR" "$DESKTOP_DIR" "$ICON_DIR"

  if [[ -f "$SHARE_DIR/profile/user.js" ]]; then
    merge_managed_text_asset \
      "$SHARE_DIR/profile/user.js" \
      "$PROFILE_DIR/user.js" \
      "// BEGIN MINAFOX PACKAGED ASSETS" \
      "// END MINAFOX PACKAGED ASSETS"
  fi
  if [[ -f "$SHARE_DIR/profile/userChrome.css" ]]; then
    merge_managed_text_asset \
      "$SHARE_DIR/profile/userChrome.css" \
      "$PROFILE_DIR/chrome/userChrome.css" \
      "/* BEGIN MINAFOX PACKAGED ASSETS */" \
      "/* END MINAFOX PACKAGED ASSETS */"
  fi
  if [[ -f "$SHARE_DIR/profile/userContent.css" ]]; then
    merge_managed_text_asset \
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
    local icon_sources=("$SHARE_DIR/assets/icons/hicolor/"*)
    shopt -u nullglob
    if (( ${#icon_sources[@]} > 0 )); then
      cp -R "${icon_sources[@]}" "$ICON_DIR/"
    fi
  fi

  update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
  gtk-update-icon-cache "$ICON_DIR" >/dev/null 2>&1 || true
  touch "$SYNC_MARKER"
}

while (($#)); do
  case "$1" in
    --repo)
      [[ $# -ge 2 ]] || { echo "--repo requires a directory" >&2; exit 2; }
      REPO_DIR="$2"
      shift 2
      ;;
    --no-pull)
      DO_PULL=0
      shift
      ;;
    --restart-services)
      RESTART_SERVICES=1
      shift
      ;;
    --no-restart-services)
      RESTART_SERVICES=0
      shift
      ;;
    --sync-profile-assets)
      SYNC_PROFILE_ASSETS=1
      shift
      ;;
    --no-sync-profile-assets)
      SYNC_PROFILE_ASSETS=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! command -v git >/dev/null 2>&1; then
  echo "minafox-update needs git installed." >&2
  exit 127
fi
if ! command -v makepkg >/dev/null 2>&1; then
  echo "minafox-update needs makepkg. On Arch, install base-devel." >&2
  exit 127
fi

if [[ "$REPO_URL" == -* ]]; then
  echo "Refusing MINAFOX_REPO_URL that begins with '-': $REPO_URL" >&2
  exit 2
fi

REPO_DIR="$(python3 -c 'import os,sys; print(os.path.abspath(os.path.expanduser(sys.argv[1])))' "$REPO_DIR")"

if [[ ! -d "$REPO_DIR/.git" ]]; then
  echo "MinaFox repo not found at: $REPO_DIR"
  echo "Cloning $REPO_URL ..."
  mkdir -p "$(dirname "$REPO_DIR")"
  git clone -- "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

if (( DO_PULL )); then
  echo "Updating MinaFox repo in $REPO_DIR ..."
  git pull --ff-only
fi

if [[ ! -d "$PACKAGE_DIR" ]]; then
  echo "Package directory missing: $REPO_DIR/$PACKAGE_DIR" >&2
  exit 1
fi

cd "$PACKAGE_DIR"
echo "Building and installing minafox-profile-git ..."
echo "makepkg may ask for your password through pacman when installing."
makepkg -si

if (( SYNC_PROFILE_ASSETS )); then
  sync_profile_assets
else
  echo "Skipping MinaFox profile/start-page asset sync (--no-sync-profile-assets)."
fi

if (( RESTART_SERVICES )); then
  if command -v systemctl >/dev/null 2>&1; then
    echo "Reloading MinaFox user services ..."
    systemctl --user daemon-reload || echo "Warning: systemctl --user daemon-reload failed; services may need a manual reload." >&2
    for service in "${MINAFOX_SERVICES[@]}"; do
      if systemctl --user is-active --quiet "$service" || systemctl --user is-enabled --quiet "$service"; then
        echo "Restarting $service ..."
        systemctl --user restart "$service" || echo "Warning: could not restart $service. Check with: systemctl --user status $service" >&2
      else
        echo "Skipping $service because it is not active or enabled."
      fi
    done
  else
    echo "systemctl not found; skipping MinaFox user service restarts."
  fi
else
  echo "Skipping MinaFox user service restarts (--no-restart-services)."
fi

echo "MinaFox package update complete. Launch with: minafox"
