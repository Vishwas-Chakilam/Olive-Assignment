$ErrorActionPreference = "Stop"
$FrontendRoot = Join-Path $PSScriptRoot "..\frontend"

if (-not $env:NEXT_PUBLIC_API_URL) {
    $env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
}

Set-Location $FrontendRoot
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..."
    npm install
}

Write-Host "Starting frontend at http://localhost:3000"
npm run dev
