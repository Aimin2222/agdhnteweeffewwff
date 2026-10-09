@echo off
cd /d "%~dp0"
py -3 tools\test_lol_audio.py
if errorlevel 1 (
  echo.
  echo [AUDIO TEST FAILED]
  pause
  exit /b 1
)
echo.
echo [AUDIO TEST PASSED]
pause
