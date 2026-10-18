@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run SETUP_DEV_ENV.bat first.
  pause
  exit /b 2
)
rem Explicit session-only override. No download and no machine-wide settings.
set "IMAGEIO_FFMPEG_EXE="
for /f "delims=" %%F in ('where ffmpeg.exe 2^>nul') do if not defined IMAGEIO_FFMPEG_EXE set "IMAGEIO_FFMPEG_EXE=%%F"
if not defined IMAGEIO_FFMPEG_EXE (
  echo No local FFmpeg on PATH. Use START.bat or explicitly set up START_GPU.bat.
  pause
  exit /b 3
)
set "AUTOCINE_GPU_EFFECTS=full"
".venv\Scripts\python.exe" tools\check_local_gpu.py
if errorlevel 1 (
  echo Local OpenCL validation failed. START.bat remains available with CPU effects.
  pause
  exit /b 4
)
call START.bat
exit /b %ERRORLEVEL%
