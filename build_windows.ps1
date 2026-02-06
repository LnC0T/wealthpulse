$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$pythonCmd = "py"
if (-not (Get-Command $pythonCmd -ErrorAction SilentlyContinue)) {
    $pythonCmd = "python"
}

Write-Host "Creating venv..."
if (-not (Test-Path ".venv")) {
    & $pythonCmd -m venv .venv
}

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
Write-Host "Upgrading pip..."
& $venvPython -m pip install --upgrade pip

Write-Host "Installing dependencies..."
if (Test-Path "requirements.txt") {
    & $venvPython -m pip install -r requirements.txt
} else {
    & $venvPython -m pip install streamlit yfinance pandas requests plotly pillow
}
& $venvPython -m pip install pyinstaller

Write-Host "Cleaning previous builds..."
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }

$addData = @()
if (Test-Path "wealth_tracker.py") { $addData += @("--add-data", "wealth_tracker.py;.") }
if (Test-Path "supabase_community_schema.sql") { $addData += @("--add-data", "supabase_community_schema.sql;.") }
if (Test-Path "assets") { $addData += @("--add-data", "assets;assets") }

Write-Host "Building executable..."
& $venvPython -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --name "WealthPulse" `
    --collect-all "streamlit" `
    @addData `
    "win_launcher.py"

Write-Host ""
Write-Host "Build complete."
Write-Host "Run: dist\\WealthPulse\\WealthPulse.exe"
