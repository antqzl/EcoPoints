# Start FastAPI locally. / 在本地启动 FastAPI。
$ErrorActionPreference = "Stop"
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = "D:\my_env\Project_ecopoint_venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { throw "Virtual environment not found. Run setup_venv.ps1 first." }
Set-Location $projectPath
& $venvPython -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
