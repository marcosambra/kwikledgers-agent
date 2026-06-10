# KwikLedgers Dev Agent - Setup
# Execute este script UMA VEZ para instalar todas as dependencias

Write-Host "=== KwikLedgers Dev Agent Setup ===" -ForegroundColor Cyan

# 1. Python dependencies - Azure DevOps MCP
Write-Host "`n[1/3] Instalando dependencias do MCP Azure DevOps..." -ForegroundColor Yellow
pip install -r "$PSScriptRoot\mcp_servers\azure_devops\requirements.txt"

# 2. Python dependencies - Windows Calendar MCP
Write-Host "`n[2/3] Instalando dependencias do MCP Windows Calendar..." -ForegroundColor Yellow
pip install -r "$PSScriptRoot\mcp_servers\windows_calendar\requirements.txt"

# 3. Node.js - Postman e Puppeteer MCP (via npx, instalado sob demanda)
Write-Host "`n[3/3] Verificando Node.js para Postman e Puppeteer MCPs..." -ForegroundColor Yellow
node --version
npx --version

# 4. Instrucoes finais
Write-Host "`n=== Setup concluido! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Copie agent\.env.example para agent\.env e preencha as variaveis"
Write-Host "  2. Copie agent\.vscode\mcp.json para a pasta .vscode na raiz do seu workspace"
Write-Host "  3. Configure as variaveis de ambiente do sistema:"
Write-Host "     setx AZURE_ORG_URL https://dev.azure.com/kwikledgers"
Write-Host "     setx AZURE_PAT seu_pat_aqui"
Write-Host "     setx AZURE_PROJECT KwikLedgers"
Write-Host "     setx POSTMAN_API_KEY sua_key_aqui"
Write-Host "  4. Reinicie o VS Code"
Write-Host "  5. Abra o Chat do Copilot e selecione o agente: KwikLedgers Dev Agent"
Write-Host ""
Write-Host "Para gerar o Azure PAT:"
Write-Host "  https://dev.azure.com/kwikledgers/_usersSettings/tokens"
Write-Host "  Permissoes: Work Items (Read+Write), Code (Read), Pull Requests (Read)"
