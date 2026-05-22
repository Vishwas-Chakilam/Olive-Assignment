# Run backend without activating venv (avoids PowerShell execution policy issues)
$ErrorActionPreference = "Stop"
$BackendRoot = Join-Path $PSScriptRoot "..\backend"
$Python = Join-Path $BackendRoot ".venv\Scripts\python.exe"
$Pip = Join-Path $BackendRoot ".venv\Scripts\pip.exe"

if (-not (Test-Path $Python)) {
    Write-Host "Creating virtual environment..."
    python -m venv (Join-Path $BackendRoot ".venv")
}

Write-Host "Installing dependencies..."
& $Pip install -q -r (Join-Path $BackendRoot "requirements.txt")

$env:PYTHONPATH = $BackendRoot
# DATABASE_URL: set in repo root .env (MySQL recommended) or export before running
New-Item -ItemType Directory -Force -Path (Join-Path $BackendRoot "data") | Out-Null
$env:INGESTION_URL = if ($env:INGESTION_URL) { $env:INGESTION_URL } else { "http://localhost:8000/logs" }
$env:DEFAULT_PROVIDER = if ($env:DEFAULT_PROVIDER) { $env:DEFAULT_PROVIDER } else { "mock" }
$env:DEFAULT_MODEL = if ($env:DEFAULT_MODEL) { $env:DEFAULT_MODEL } else { "mock-gpt" }

Write-Host "Starting backend at http://127.0.0.1:8000"
Set-Location $BackendRoot
& $Python -m uvicorn app.main:app --reload --port 8000
