param(
    [string]$Salam = 'salam',
    [string]$Compiler = 'gcc',
    [string]$Python = 'python'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $projectRoot
try {
    New-Item -ItemType Directory -Path build -Force | Out-Null
    & $Salam build src/main.salam --backend=c "--cc=$Compiler" --output=build/subtitle-check.exe --log-level=error
    if ($LASTEXITCODE -ne 0) { throw 'Application compilation failed.' }
    & $Salam build tests/unit.salam --backend=c "--cc=$Compiler" --output=build/unit.exe --log-level=error
    if ($LASTEXITCODE -ne 0) { throw 'Unit-test compilation failed.' }
    & ./build/unit.exe
    if ($LASTEXITCODE -ne 0) { throw 'Unit tests failed.' }
    & $Python tests/e2e.py build/subtitle-check.exe
    if ($LASTEXITCODE -ne 0) { throw 'End-to-end tests failed.' }
} finally {
    Pop-Location
}
