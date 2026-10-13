@echo off
setlocal EnableExtensions
cd /d "%~dp0"
rem Optional launcher version, e.g. SETUP_DEV_ENV.bat -3.12
set "PY_VERSION=-3"
if not "%~1"=="" set "PY_VERSION=%~1"
if not exist ".venv\Scripts\python.exe" (
  py %PY_VERSION% -m venv .venv
  if errorlevel 1 exit /b 2
)
echo Installing development dependencies into .venv only...
".venv\Scripts\python.exe" -m pip install -r requirements-dev.txt
if errorlevel 1 exit /b 3
".venv\Scripts\python.exe" -m pip check
exit /b %ERRORLEVEL%
