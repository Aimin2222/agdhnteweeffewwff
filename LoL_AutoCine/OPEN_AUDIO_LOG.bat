@echo off
setlocal
cd /d "%~dp0"
if not exist diagnostics\audio.log (
  echo No audio.log exists yet.
  echo Run 00_AUDIO_TEST.bat first.
  pause
  exit /b 0
)
start "" notepad.exe "%~dp0diagnostics\audio.log"
exit /b 0
