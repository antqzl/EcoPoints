# Always serve the frontend beside this script, regardless of the shell's directory.
$ErrorActionPreference = "Stop"
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = "D:\my_env\Project_ecopoint_venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { (Get-Command python -ErrorAction Stop).Source }
& $python (Join-Path $projectPath "serve_frontend.py")
