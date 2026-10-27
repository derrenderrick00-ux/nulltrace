$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$python = if (Get-Command py -ErrorAction SilentlyContinue) { 'py' } else { 'python' }
& $python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Cannot create Python virtual environment' }
& .\.venv\Scripts\python.exe -m pip install --retries 1 --timeout 15 -e '.[dev]'
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& .\.venv\Scripts\python.exe -m nulltrace --strict
if ($LASTEXITCODE -ne 0) { throw 'Environment checks failed' }
& .\.venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
Write-Host 'NULLTRACE v1.5.0-rc1 Python tests passed. Windows GUI acceptance remains pending.'
