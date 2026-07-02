# KwikLedgers Dev Agent - Setup
# Execute este script UMA VEZ para instalar todas as dependencias

Write-Host "=== KwikLedgers Dev Agent Setup ===" -ForegroundColor Cyan

$VenvDir = Join-Path $PSScriptRoot "mcp_servers/.venv"
$PythonBin = Join-Path $VenvDir "Scripts/python.exe"
$StampDir = Join-Path $VenvDir ".requirements"

if (!(Test-Path $PythonBin)) {
	python -m venv $VenvDir
}

if (!(Test-Path $StampDir)) {
	New-Item -ItemType Directory -Path $StampDir | Out-Null
}

function Write-RequirementsStamp {
	param(
		[string]$ServerName
	)

	$RequirementsFile = Join-Path $PSScriptRoot "mcp_servers/$ServerName/requirements.txt"
	$StampFile = Join-Path $StampDir "$ServerName.sha256"
	$Hash = (Get-FileHash -Algorithm SHA256 $RequirementsFile).Hash.ToLower()
	Set-Content -NoNewline -Path $StampFile -Value $Hash
}

# 1. Python dependencies - Azure DevOps MCP
Write-Host "`n[1/4] Instalando dependencias do MCP Azure DevOps..." -ForegroundColor Yellow
& $PythonBin -m pip install -r "$PSScriptRoot\mcp_servers\azure_devops\requirements.txt"
Write-RequirementsStamp "azure_devops"

# 2. Python dependencies - Windows Calendar MCP
Write-Host "`n[2/4] Instalando dependencias do MCP Windows Calendar..." -ForegroundColor Yellow
& $PythonBin -m pip install -r "$PSScriptRoot\mcp_servers\windows_calendar\requirements.txt"
Write-RequirementsStamp "windows_calendar"

# 3. Python dependencies - Local Tracking MCP
Write-Host "`n[3/4] Instalando dependencias do MCP Local Tracking..." -ForegroundColor Yellow
& $PythonBin -m pip install -r "$PSScriptRoot\mcp_servers\local_tracking\requirements.txt"
Write-RequirementsStamp "local_tracking"

# 4. Sincronizar agente compartilhado nos repositorios de projects/
Write-Host "`n[4/4] Sincronizando o agente e os MCPs nos repositorios de projects/..." -ForegroundColor Yellow
& $PythonBin "$PSScriptRoot\scripts\sync_project_agent_access.py"

# 4. Arquivo .env
$EnvFile = Join-Path $PSScriptRoot ".env"
$EnvExample = Join-Path $PSScriptRoot ".env.example"
if (!(Test-Path $EnvFile)) {
	Copy-Item $EnvExample $EnvFile
	Write-Host "`nArquivo .env criado a partir do .env.example" -ForegroundColor Yellow
}

# 5. Instrucoes finais
Write-Host "`n=== Setup concluido! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Cyan
Write-Host "  1. Preencha as variaveis em: $EnvFile"
Write-Host "     AZURE_ORG_URL=https://dev.azure.com/viwaredevops"
Write-Host "     AZURE_PAT=seu_pat_aqui"
Write-Host "     AZURE_PROJECT=Kwik Ledgers"
Write-Host "     AZURE_USER_EMAIL=seu_email@empresa.com"
Write-Host "  2. O setup ja sincronizou o agente e os MCPs nos repositorios em projects/"
Write-Host "  3. Copie agent\.vscode\mcp.json para a pasta .vscode na raiz do seu workspace, se necessario"
Write-Host "  4. Reinicie o VS Code"
Write-Host "  5. Abra o Chat do Copilot e selecione o agente: KwikLedgers Dev Agent"
Write-Host "  6. Gere os arquivos em AI_Tracking/ via resumo diario do Azure"
Write-Host ""
Write-Host "Para gerar o Azure PAT:"
Write-Host "  https://dev.azure.com/viwaredevops/_usersSettings/tokens"
Write-Host "  Permissoes: Work Items (Read+Write), Code (Read), Pull Requests (Read)"
