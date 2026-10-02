$ErrorActionPreference = 'Stop'

$python = Join-Path $PSScriptRoot 'venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    throw 'No existe el entorno virtual. Créalo con py -3.12 -m venv venv y sincroniza con uv.'
}

Push-Location $PSScriptRoot
try {
    & $python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
