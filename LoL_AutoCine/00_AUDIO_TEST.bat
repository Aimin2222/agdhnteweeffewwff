@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo ================================================================
echo LoL AutoCine - Audio Test
echo ================================================================
echo.

if not exist "tools\bin\lol_audio_helper.exe" (
  echo [INFO] Native audio helper is not built yet.
  echo [INFO] Starting the helper build automatically...
  echo.
  call "%CD%\BUILD_AUDIO_HELPER.bat" /nopause
  if errorlevel 1 (
    echo.
    echo [FAIL] Native audio helper could not be built.
    echo See diagnostics\native_audio_build.log
    echo.
    pause
    exit /b 10
  )
)

if not exist "tools\bin\lol_audio_helper.exe" (
  echo [FAIL] Helper EXE is still missing after the build step.
  echo See diagnostics\native_audio_build.log
  pause
  exit /b 11
)

echo.
echo [OK] Native helper is ready.
echo.
echo [1] Start the LoL replay and make sure game audio is playing.
echo [2] Press ENTER here to start a 5-second capture.
echo [3] The result and detailed log will be saved in diagnostics.
echo.
pause
py -3 tools\sound_test.py
set "RC=%ERRORLEVEL%"
echo.
if "%RC%"=="0" (
  echo [PASS] Audio test succeeded. You can start AutoCine.
) else (
  echo [FAIL] Audio test failed.
  echo Open diagnostics\audio.log for details.
)
echo.
pause
exit /b %RC%
