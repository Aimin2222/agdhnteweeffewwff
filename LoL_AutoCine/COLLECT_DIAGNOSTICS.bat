@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo Collecting ALL AutoCine diagnostics...
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\bootstrap_python.ps1" -Mode Diagnostics
set "RC=%ERRORLEVEL%"
echo.
pause
exit /b %RC%
