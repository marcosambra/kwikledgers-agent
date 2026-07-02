$VenvPython = Join-Path $PSScriptRoot "mcp_servers/.venv/Scripts/python.exe"
$SyncScript = Join-Path $PSScriptRoot "scripts/sync_project_agent_access.py"

if (!(Test-Path $VenvPython)) {
	Write-Error "Runtime compartilhado nao encontrado em $VenvPython"
	Write-Host "Rode primeiro: .\setup.ps1"
	exit 1
}

& $VenvPython $SyncScript
exit $LASTEXITCODE