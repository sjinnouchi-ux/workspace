$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

function Get-PythonExe {
    if ($env:PYTHON_EXE -and (Test-Path $env:PYTHON_EXE)) {
        return $env:PYTHON_EXE
    }

    $codexPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path $codexPython) {
        return $codexPython
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return $python.Source
    }

    throw "Python was not found. Install Python 3, then run this script again."
}

Set-Location $ProjectRoot

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating virtual environment..."
    $pythonExe = Get-PythonExe
    & $pythonExe -m venv ".venv"
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VenvPython)) {
        throw "Failed to create virtual environment."
    }
}

Write-Host "Installing dependencies..."
& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r "requirements.txt"

if (-not (Test-Path (Join-Path $ProjectRoot ".env"))) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot ".env.example") -Destination (Join-Path $ProjectRoot ".env")
    Write-Host "Created .env from .env.example. Add your API keys when needed."
}

Write-Host "Starting API Monitor..."
Write-Host "Open http://localhost:8501 in your browser."
& $VenvPython -m streamlit run "app.py" --server.address 127.0.0.1 --server.port 8501
