@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ================================================================
echo LoL AutoCine
echo ================================================================

echo [Audio] Checking native LoL audio helper...
if not exist "tools\bin\lol_audio_helper.exe" (
  echo [Audio] Helper is missing. Preparing C++ Build Tools automatically...
  call "%CD%\BUILD_AUDIO_HELPER.bat"
  if errorlevel 1 (
    echo.
    echo [Audio] Native helper setup failed.
    echo You can run BUILD_AUDIO_HELPER.bat manually after approving UAC.
    pause
    exit /b 10
  )
)

if not exist "tools\bin\lol_audio_helper.exe" (
  echo [Audio] Helper is still missing.
  pause
  exit /b 11
)

echo [Audio] Native LoL audio helper is ready.
echo [App] Starting LoL AutoCine...
py -3 app.py
set "RC=%ERRORLEVEL%"
echo.
echo LoL AutoCine exited with code %RC%.
pause
exit /b %RC%
