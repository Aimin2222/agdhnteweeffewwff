@echo off
rem Issue #53 developer launcher. Keep one persistent console, as in v5.10.31.
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

if /I "%~1"=="legacy" (
  set "AUTOCINE_RESEARCH_FLASH=legacy"
  set "AUTOCINE_RESEARCH_ZOOM=legacy"
  echo [Issue53] Legacy Flash and Zoom selected.
) else (
  set "AUTOCINE_RESEARCH_FLASH=causal_pts_v1"
  set "AUTOCINE_RESEARCH_ZOOM=normalized_tmix_v1"
  echo [Issue53] Trial Flash and Zoom selected.
)

if /I "%~1"=="--check" (
  echo [Issue53] Launcher is ready. Open a LoL replay, then click the in-app developer one-click QA button.
  endlocal & exit /b 0
)
if /I "%~2"=="--check" (
  echo [Issue53] Launcher is ready. Open a LoL replay, then click the in-app developer one-click QA button.
  endlocal & exit /b 0
)
if not exist "%~dp0START.bat" (
  echo [Issue53] START.bat is missing from this folder.
  endlocal & exit /b 2
)

rem Keep first-run Python/pip temporary files inside this test copy.
set "TEMP=%~dp0qa_tmp\bootstrap_temp"
set "TMP=%TEMP%"
set "PIP_CACHE_DIR=%~dp0qa_tmp\pip_cache"
if not exist "%TEMP%" mkdir "%TEMP%"
if not exist "%TEMP%" (
  echo [Issue53] Cannot create a writable temporary folder.
  endlocal & exit /b 3
)

rem Reuse an already prepared v5.10.31-style Python environment when supplied.
if defined AUTOCINE_ISSUE53_PYTHON goto RunPrepared

echo [Issue53] One console stays open for diagnostics. No separate EXE is used.
echo [Issue53] In the app, click the developer camera + Work assets one-click QA button.
call "%~dp0START.bat"
set "RC=%ERRORLEVEL%"
endlocal & exit /b %RC%

:RunPrepared
if not exist "%AUTOCINE_ISSUE53_PYTHON%" (
  echo [Issue53] AUTOCINE_ISSUE53_PYTHON does not exist.
  endlocal & exit /b 4
)
"%AUTOCINE_ISSUE53_PYTHON%" -c "import numpy,PIL,imageio_ffmpeg,windows_capture,yt_dlp,pycaw,pyaudiowpatch,psutil"
if errorlevel 1 (
  echo [Issue53] The supplied Python environment is missing AutoCine dependencies.
  endlocal & exit /b 5
)
if not exist "%~dp0tools\bin\lol_audio_helper.exe" (
  echo [Issue53] Native LoL audio helper is missing.
  endlocal & exit /b 6
)
echo [Issue53] Starting with an existing Python environment in this console.
"%AUTOCINE_ISSUE53_PYTHON%" "%~dp0app.py"
set "RC=%ERRORLEVEL%"
echo [Issue53] AutoCine exited with code %RC%.
if not defined CI pause
endlocal & exit /b %RC%
