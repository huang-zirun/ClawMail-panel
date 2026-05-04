$ErrorActionPreference = "Stop"

$projectDir = Split-Path -Parent $PSScriptRoot
Set-Location $projectDir

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    uv sync
}

Write-Host "Starting watcher..." -ForegroundColor Green
Start-Process -FilePath "uv" -ArgumentList "run", "python", "-m", "app.watcher" -NoNewWindow:$false

Write-Host "Starting web server..." -ForegroundColor Green
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
