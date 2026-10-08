@echo off
setlocal
cd /d "%~dp0"
echo ================================================================
echo LoL AutoCine - Native Audio Helper Check
echo ================================================================
echo.
if exist "tools\bin\lol_audio_helper.exe" (
  echo [PASS] Helper exists:
  echo        %CD%\tools\bin\lol_audio_helper.exe
  echo.
  echo Run 00_AUDIO_TEST.bat to test LoL-only capture.
  pause
  exit /b 0
)
echo [MISSING] tools\bin\lol_audio_helper.exe
echo.
echo Run 00_AUDIO_TEST.bat. It will build the helper automatically.
echo If the build fails, see diagnostics\native_audio_build.log
pause
exit /b 1
