@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run START.bat once first.
  pause
  goto :eof
)
".venv\Scripts\python.exe" tests\run_tests.py
pause
