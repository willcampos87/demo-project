# Weekly YouTube niche pipeline + Slides + Gmail (see Task Scheduler registration script).
# Project root = parent of scripts/
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$LogDir = Join-Path $ProjectRoot ".tmp"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
$LogFile = Join-Path $LogDir "weekly_youtube_schedule.log"

function Write-LogLine {
    param([string]$Message)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    Add-Content -Path $LogFile -Value $line -Encoding utf8
    Write-Output $line
}

$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-LogLine "ERROR: Missing venv Python at $Python"
    exit 1
}

Write-LogLine "----- run start -----"

try {
    & $Python "tools\run_pipeline.py"
    if ($LASTEXITCODE -ne 0) {
        Write-LogLine "ERROR: run_pipeline.py exited $LASTEXITCODE"
        exit $LASTEXITCODE
    }
    Write-LogLine "OK: run_pipeline.py"

    & $Python "tools\complete_youtube_report.py"
    if ($LASTEXITCODE -ne 0) {
        Write-LogLine "ERROR: complete_youtube_report.py exited $LASTEXITCODE"
        exit $LASTEXITCODE
    }
    Write-LogLine "OK: complete_youtube_report.py"
}
catch {
    Write-LogLine "ERROR: $($_.Exception.Message)"
    exit 1
}

Write-LogLine "----- run end (success) -----"
exit 0
