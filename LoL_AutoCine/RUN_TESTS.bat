@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run SETUP_DEV_ENV.bat first to create the development environment.
  pause
  exit /b 2
)
".venv\Scripts\python.exe" tools\run_local_tests.py %*
set "RC=%ERRORLEVEL%"
pause
exit /b %RC%
