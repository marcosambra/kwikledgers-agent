#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$SCRIPT_DIR/mcp_servers/.venv/bin/python"
SYNC_SCRIPT="$SCRIPT_DIR/scripts/sync_project_agent_access.py"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "ERRO: runtime compartilhado nao encontrado em $PYTHON_BIN"
  echo "Rode primeiro: bash $SCRIPT_DIR/setup.sh"
  exit 1
fi

exec "$PYTHON_BIN" "$SYNC_SCRIPT"