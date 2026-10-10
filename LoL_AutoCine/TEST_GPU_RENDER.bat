@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run START_GPU.bat once to prepare Python and GPU FFmpeg first.
  pause
  exit /b 2
)
".venv\Scripts\python.exe" tools\gpu_render_test.py %*
set "test_result=%ERRORLEVEL%"
pause
exit /b %test_result%
