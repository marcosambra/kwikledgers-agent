#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../.env"

if [ ! -f "$ENV_FILE" ]; then
  cp "$SCRIPT_DIR/../../.env.example" "$ENV_FILE"
fi

pip3 install -q mcp winotify 2>/dev/null

exec python3 "$SCRIPT_DIR/server.py"