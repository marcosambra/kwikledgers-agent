[CmdletBinding()]
param(
    [string]$TaskName = "KwikLedgers Daily Summary",
    [string]$Time = "09:00",
    [string]$WorkspaceRoot = "/home/ambra/Kwikledgers",
    [string]$WslDistro = ""
)

$ErrorActionPreference = "Stop"

function ConvertTo-ArgumentString {
    param([string[]]$Arguments)

    $parts = foreach ($item in $Arguments) {
        if ($item -match '[\s"]') {
            '"' + $item.Replace('"', '""') + '"'
        } else {
            $item
        }
    }

    return ($parts -join ' ')
}

$agentRoot = "$WorkspaceRoot/agent"
$runnerPath = "$agentRoot/scripts/run_daily_summary.py"
$pythonPath = "$agentRoot/mcp_servers/.venv/bin/python"
$envFilePath = "$agentRoot/.env"

$escapedAgentRoot = $agentRoot.Replace("'", "'\''")
$escapedPythonPath = $pythonPath.Replace("'", "'\''")
$escapedRunnerPath = $runnerPath.Replace("'", "'\''")
$escapedEnvFilePath = $envFilePath.Replace("'", "'\''")
$bashCommand = "cd '$escapedAgentRoot' && KWIKLEDGERS_ENV_FILE='$escapedEnvFilePath' '$escapedPythonPath' '$escapedRunnerPath' --source task-scheduler"

$wslArguments = @()
if ($WslDistro) {
    $wslArguments += "-d"
    $wslArguments += $WslDistro
}
$wslArguments += "bash"
$wslArguments += "-lc"
$wslArguments += $bashCommand

$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument (ConvertTo-ArgumentString $wslArguments)
$trigger = New-ScheduledTaskTrigger -Daily -At ([datetime]::ParseExact($Time, "HH:mm", [System.Globalization.CultureInfo]::InvariantCulture))
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$description = "Executa o resumo diario do KwikLedgers via WSL e envia notificacao quando estiver disponivel."

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description $description `
    -Force | Out-Null

Write-Output "Tarefa registrada: $TaskName"
Write-Output "Horario: $Time"
Write-Output "Workspace WSL: $WorkspaceRoot"
Write-Output "Comando: wsl.exe $(ConvertTo-ArgumentString $wslArguments)"