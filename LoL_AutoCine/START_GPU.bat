@echo off
setlocal EnableExtensions
cd /d "%~dp0"
echo [GPU] Preparing OpenCL effects and NVENC...
py -3 tools\setup_gpu_ffmpeg.py
if errorlevel 1 (
  echo [GPU] Setup did not complete. Original START.bat is still available.
  pause
  exit /b 20
)
call START.bat
exit /b %ERRORLEVEL%
