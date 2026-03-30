# Registers a Windows Scheduled Task: every Monday 6:00 AM (local time) - YouTube pipeline + report.
# Run once in PowerShell (no admin usually required for current-user tasks):
#   powershell -ExecutionPolicy Bypass -File ".\scripts\register_monday_6am_task.ps1"
#
# Remove task: Unregister-ScheduledTask -TaskName 'YouTubeNicheWeeklyReport' -Confirm:$false

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$RunScript = Join-Path $ProjectRoot "scripts\run_weekly_youtube_report.ps1"
$TaskName = "YouTubeNicheWeeklyReport"

if (-not (Test-Path $RunScript)) {
    Write-Error "Missing $RunScript"
    exit 1
}

$FullPathToRunScript = (Resolve-Path $RunScript).Path
$Arg = "-NoProfile -ExecutionPolicy Bypass -File `"$FullPathToRunScript`""

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $Arg -WorkingDirectory $ProjectRoot

# Every Monday at 06:00 local time
$Trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Monday -At "06:00"

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -WakeToRun `
    -MultipleInstances IgnoreNew

# Run as you, interactive session (needed for typical OAuth token refresh behavior)
$Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "YouTube ingest, metrics, charts, Slides + Gmail (Demo Project)" | Out-Null

Write-Output "Registered scheduled task '$TaskName' - Mondays 06:00, runs:"
Write-Output "  $FullPathToRunScript"
Write-Output "Logs append to: $(Join-Path $ProjectRoot '.tmp\weekly_youtube_schedule.log')"
Write-Output ""
Write-Output "Ensure this PC is on or wakes before 06:00, and you stay signed into Windows for this interactive task."
