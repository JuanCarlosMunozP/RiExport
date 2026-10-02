$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot
try {
    flutter run -d web-server --web-hostname 127.0.0.1 --web-port 8080
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
