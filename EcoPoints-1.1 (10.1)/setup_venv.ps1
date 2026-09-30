# Create the requested virtual environment. / 创建用户指定位置的虚拟环境。
$ErrorActionPreference = "Stop"
$venvPath = "D:\my_env\Project_ecopoint_venv"
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python was not found. Install Python 3.11+ and enable Add python.exe to PATH."
}
if (-not (Test-Path $venvPath)) { python -m venv $venvPath }
$venvPython = Join-Path $venvPath "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $projectPath "backend\requirements.txt")
Write-Host "Virtual environment ready: $venvPath"
Write-Host "Activate with: & '$venvPath\Scripts\Activate.ps1'"
