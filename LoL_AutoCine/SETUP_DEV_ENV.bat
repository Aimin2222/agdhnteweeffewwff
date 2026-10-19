@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "PY_VERSION=3.12"
if not "%~1"=="" set "PY_VERSION=%~1"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\bootstrap_python.ps1" -Mode Setup -RequestedVersion "%PY_VERSION%"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" echo Setup failed. Read the error above, then try again.
pause
exit /b %RC%
