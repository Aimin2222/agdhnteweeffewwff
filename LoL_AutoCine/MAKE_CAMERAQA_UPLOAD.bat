@echo off
setlocal DisableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0"
title AutoCine Developer CameraQA 30MB Upload
set "SOURCE=%~1"
if not defined SOURCE set /p "SOURCE=CameraQA folder (contains results.json): "
if not defined SOURCE exit /b 2
set "RUNEXE="
set "RUNARG="
if exist ".venv\Scripts\python.exe" set "RUNEXE=.venv\Scripts\python.exe"
if not defined RUNEXE if exist "venv\Scripts\python.exe" set "RUNEXE=venv\Scripts\python.exe"
if not defined RUNEXE (
  python -c "import PIL, imageio_ffmpeg" >nul 2>&1
  if not errorlevel 1 set "RUNEXE=python"
)
if not defined RUNEXE (
  py -3 -c "import PIL, imageio_ffmpeg" >nul 2>&1
  if not errorlevel 1 (
    set "RUNEXE=py"
    set "RUNARG=-3"
  )
)
if not defined RUNEXE (
  echo [ERROR] Start AutoCine once to install Python dependencies, then retry.
  if not defined CI pause
  exit /b 4
)
"%RUNEXE%" %RUNARG% -m tools.make_cameraqa_upload "%SOURCE%"
set "RESULT=%ERRORLEVEL%"
echo [AutoCine] Originals and previous ZIPs are preserved. Exit code: %RESULT%
if not defined CI pause
endlocal & exit /b %RESULT%
