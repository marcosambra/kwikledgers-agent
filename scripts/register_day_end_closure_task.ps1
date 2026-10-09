[CmdletBinding()]
param(
    [string]$TaskName = "KwikLedgers Day End Closure",
    [string]$Time = "18:00",
    [string]$WorkspaceRoot = "/home/ambra/Kwikledgers",
    [string]$WslDistro = ""
)

$ErrorActionPreference = "Stop"

$projectRoot = "$WorkspaceRoot/kwikledgers_langgraph"
$bashCommand = "cd '$projectRoot' && .venv/bin/python -m kwikledgers_langgraph.day_end_closure_cli --trigger scheduled --notify"

$wslArguments = @()
if ($WslDistro) {
    $wslArguments += @("-d", $WslDistro)
}
$wslArguments += @("bash", "-lc", ('"' + $bashCommand + '"'))

$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument ($wslArguments -join ' ')
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At ([datetime]::ParseExact($Time, "HH:mm", [System.Globalization.CultureInfo]::InvariantCulture))
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$description = "Fechamento de fim de dia do KwikLedgers: lanca horas, fecha a task Active e abre a continuacao."

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description $description -Force | Out-Null

Write-Output "Tarefa registrada: $TaskName ($Time, seg-sex)"
Write-Output "Comando: wsl.exe $($wslArguments -join ' ')"
