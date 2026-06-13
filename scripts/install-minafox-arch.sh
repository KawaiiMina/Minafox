#!/usr/bin/env bash
set -euo pipefail

APP_NAME="minafox"
PROFILE_DIR="$HOME/.mozilla/firefox/$APP_NAME"
START_DIR="$HOME/.local/share/$APP_NAME"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v firefox >/dev/null 2>&1; then
  if command -v pacman >/dev/null 2>&1; then
    echo "Firefox is not installed. Installing via pacman..."
    sudo pacman -S --needed firefox
  else
    echo "Firefox not found and pacman is not available. Install Firefox first." >&2
    exit 1
  fi
fi

mkdir -p "$PROFILE_DIR/chrome" "$START_DIR" "$DESKTOP_DIR" "$ICON_DIR"
cp "$ROOT_DIR/profile/user.js" "$PROFILE_DIR/user.js"
cp "$ROOT_DIR/profile/userChrome.css" "$PROFILE_DIR/chrome/userChrome.css"
cp "$ROOT_DIR/profile/userContent.css" "$PROFILE_DIR/chrome/userContent.css"
cp "$ROOT_DIR/desktop/start.html" "$START_DIR/start.html"
cp "$ROOT_DIR/desktop/minafox.desktop" "$DESKTOP_DIR/minafox.desktop"
if [[ -d "$ROOT_DIR/assets/icons/hicolor" ]]; then
  cp -R "$ROOT_DIR/assets/icons/hicolor/"* "$ICON_DIR/"
fi

# Create/update profiles.ini entry if Firefox has not seen this profile yet.
if ! grep -R "Path=$PROFILE_DIR" "$HOME/.mozilla/firefox/profiles.ini" >/dev/null 2>&1; then
  firefox --CreateProfile "minafox $PROFILE_DIR" >/dev/null 2>&1 || true
fi

# Install enterprise policies for the Firefox package when possible.
if [[ -d /usr/lib/firefox ]]; then
  echo "Installing Firefox policies to /usr/lib/firefox/distribution (sudo required)."
  sudo mkdir -p /usr/lib/firefox/distribution
  sudo cp "$ROOT_DIR/distribution/policies.json" /usr/lib/firefox/distribution/policies.json
elif [[ -d /usr/lib64/firefox ]]; then
  echo "Installing Firefox policies to /usr/lib64/firefox/distribution (sudo required)."
  sudo mkdir -p /usr/lib64/firefox/distribution
  sudo cp "$ROOT_DIR/distribution/policies.json" /usr/lib64/firefox/distribution/policies.json
else
  echo "Could not find Firefox install dir; profile installed, policies skipped." >&2
fi

update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
gtk-update-icon-cache "$ICON_DIR" >/dev/null 2>&1 || true

echo "Installed MinaFox profile: $PROFILE_DIR"
echo "Launch with: firefox --profile '$PROFILE_DIR'"
echo "Desktop entry: $DESKTOP_DIR/minafox.desktop"
echo "Icons installed under: $ICON_DIR/*/apps/minafox.png"
