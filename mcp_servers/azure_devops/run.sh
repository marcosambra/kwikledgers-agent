#!/usr/bin/env bash
# Bootstrap: instala dependencias e inicia o servidor
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../../.env"

# Cria .env a partir do exemplo se ainda nao existir
if [ ! -f "$ENV_FILE" ]; then
  cp "$SCRIPT_DIR/../../.env.example" "$ENV_FILE"
fi

# Instala dependencias silenciosamente se necessario
pip3 install -q -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null

# Inicia o servidor
exec python3 "$SCRIPT_DIR/server.py"