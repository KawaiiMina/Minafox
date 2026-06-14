#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${MINAFOX_REPO_URL:-https://github.com/KawaiiMina/Minafox.git}"
REPO_DIR="${MINAFOX_REPO_DIR:-$HOME/Minafox}"
PACKAGE_DIR="packaging/arch/minafox-profile-git"
DO_PULL=1

usage() {
  cat <<'USAGE'
Usage: minafox-update [--repo DIR] [--no-pull] [--help]

Upgrade the installed MinaFox Arch package from the MinaFox git package skeleton.

Defaults:
  repo: ~/Minafox
  remote: https://github.com/KawaiiMina/Minafox.git

Examples:
  minafox-update
  minafox-update --repo ~/Minafox
  MINAFOX_REPO_DIR=~/src/Minafox minafox-update

This script does not store GitHub tokens. Configure GitHub HTTPS auth with gh or git credentials first if the repository is private.
USAGE
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

echo "MinaFox package update complete. Launch with: minafox"
