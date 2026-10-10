@echo off
setlocal
cd /d "%~dp0"
echo ================================================
echo LoL AutoCine - Audio Test
echo ================================================
echo.
py -3 tools\sound_test.py
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo [PASS] Audio test succeeded.
) else (
  echo [FAIL] Audio test failed.
  echo Open diagnostics\audio.log for details.
)
echo.
pause
exit /b %RC%
