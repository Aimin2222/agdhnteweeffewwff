@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo LoL AutoCine - Audio Repair
echo ========================================
echo.
py -3 -m pip install --upgrade PyAudioWPatch pycaw
if errorlevel 1 (
  echo.
  echo [ERROR] Audio packages could not be installed.
  pause
  exit /b 1
)
echo.
echo [OK] Audio packages installed.
echo Run 00_AUDIO_TEST.bat again.
pause
exit /b 0
