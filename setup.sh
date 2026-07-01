#!/usr/bin/env bash
# KwikLedgers Dev Agent - Setup para Linux/WSL
set -e

echo "=== KwikLedgers Dev Agent Setup (Linux/WSL) ==="

# --- Verificacoes iniciais ---
command -v python3 >/dev/null 2>&1 || { echo "ERRO: python3 nao encontrado. Instale com: sudo apt install python3"; exit 1; }
command -v pip3   >/dev/null 2>&1 || { echo "ERRO: pip3 nao encontrado. Instale com: sudo apt install python3-pip"; exit 1; }
command -v node   >/dev/null 2>&1 || { echo "ERRO: node nao encontrado. Instale com: sudo apt install nodejs npm"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- 1. Dependencias Python - Azure DevOps MCP ---
echo ""
echo "[1/3] Instalando dependencias do MCP Azure DevOps..."
pip3 install -r "$SCRIPT_DIR/mcp_servers/azure_devops/requirements.txt"

# --- 2. Dependencias Python - Windows Calendar MCP ---
# No WSL o servidor Windows usa o PowerShell do host para notificacoes
echo ""
echo "[2/3] Instalando dependencias do MCP Windows Calendar (via WSL)..."
pip3 install -r "$SCRIPT_DIR/mcp_servers/windows_calendar/requirements.txt" || {
  echo "AVISO: pywin32 nao instalavel no Linux — sera usado fallback via PowerShell.exe para notificacoes."
  pip3 install mcp winotify 2>/dev/null || pip3 install mcp
}

# --- 3. Dependencias Python - Tracking local MCP ---
echo ""
echo "[3/3] Instalando dependencias do MCP Local Tracking..."
pip3 install -r "$SCRIPT_DIR/mcp_servers/local_tracking/requirements.txt"

# --- 4. Variaveis de ambiente ---
ENV_FILE="$SCRIPT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
  cp "$SCRIPT_DIR/.env.example" "$ENV_FILE"
  echo ""
  echo "Arquivo .env criado a partir do .env.example"
  echo "Edite o arquivo antes de usar: nano $ENV_FILE"
fi

# --- 5. Exportar variaveis no shell profile ---
# Detecta o shell atual pelo processo pai, nao pela variavel (mais confiavel)
CURRENT_SHELL=$(ps -p $PPID -o comm= 2>/dev/null || echo "bash")
if echo "$CURRENT_SHELL" | grep -q "zsh"; then
  PROFILE_FILE="$HOME/.zshrc"
elif echo "$CURRENT_SHELL" | grep -q "fish"; then
  PROFILE_FILE="$HOME/.config/fish/config.fish"
else
  PROFILE_FILE="$HOME/.bashrc"
fi

MARKER="# kwikledgers-agent"
if ! grep -q "$MARKER" "$PROFILE_FILE" 2>/dev/null; then
  echo "" >> "$PROFILE_FILE"
  echo "$MARKER" >> "$PROFILE_FILE"
  echo "set -a && [ -f $ENV_FILE ] && source $ENV_FILE && set +a" >> "$PROFILE_FILE"
  echo "Variaveis do .env configuradas em: $PROFILE_FILE"
fi

echo ""
echo "=== Setup concluido! ==="
echo ""
echo "Proximos passos:"
echo "  1. Preencha suas credenciais: nano $ENV_FILE"
echo "  2. Recarregue o shell:        source $PROFILE_FILE"
echo "  3. Copie o mcp.json para o workspace:"
echo "     cp $SCRIPT_DIR/.vscode/mcp.json /caminho/para/Kwikledgers/.vscode/mcp.json"
echo "  4. Reinicie o VS Code"
echo "  5. Use o resumo diario do Azure para gerar arquivos em AI_Tracking/"
echo ""
echo "Para gerar seu Azure PAT:"
echo "  https://dev.azure.com/viwaredevops/_usersSettings/tokens"
echo "  Permissoes: Work Items (Read+Write) | Code (Read) | Pull Request Threads (Read+Write)"