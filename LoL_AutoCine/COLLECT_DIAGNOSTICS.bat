@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo Collecting ALL AutoCine diagnostics...
py -3 "tools\collect_diagnostics.py"
if errorlevel 1 (
    python "tools\collect_diagnostics.py"
)
echo.
pause
