#!/usr/bin/env bash
set -euo pipefail

# Default bind: MINAFOX_AI_BROKER_HOST=127.0.0.1
export MINAFOX_AI_BROKER_HOST="${MINAFOX_AI_BROKER_HOST:-127.0.0.1}"
export MINAFOX_AI_BROKER_PORT="${MINAFOX_AI_BROKER_PORT:-8765}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/minafox-ai-broker.py"

if [[ ! -f "$SCRIPT_PATH" && -f /usr/share/minafox/scripts/minafox-ai-broker.py ]]; then
  SCRIPT_PATH=/usr/share/minafox/scripts/minafox-ai-broker.py
fi

exec python3 "$SCRIPT_PATH" "$@"
