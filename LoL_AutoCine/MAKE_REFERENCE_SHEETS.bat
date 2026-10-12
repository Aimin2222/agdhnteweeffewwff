@echo off
rem ASCII-only Windows CMD launcher. Source media remains UTF-8/Unicode.
setlocal DisableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONUNBUFFERED=1"
set "RESULT=0"
cd /d "%~dp0"
title AutoCine Reference Video Review
set "SOURCE=%~1"
set "LOG=%TEMP%\AutoCine_ReferenceReview_latest.log"
> "%LOG%" echo [AutoCine] Starting reference video review.
if not exist "diagnostics" mkdir "diagnostics" >nul 2>&1
set "RUNEXE="
set "RUNARG="
rem Interpreter selection must verify PIL/imageio. The Windows py launcher
rem can point to a different Python from one installed by setup-python.
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import PIL, imageio_ffmpeg" >nul 2>&1
  if not errorlevel 1 set "RUNEXE=.venv\Scripts\python.exe"
)
if not defined RUNEXE (
  if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" -c "import PIL, imageio_ffmpeg" >nul 2>&1
    if not errorlevel 1 set "RUNEXE=venv\Scripts\python.exe"
  )
)
if not defined RUNEXE (
  where python >nul 2>&1
  if not errorlevel 1 (
    python -c "import PIL, imageio_ffmpeg" >nul 2>&1
    if not errorlevel 1 set "RUNEXE=python"
  )
)
if not defined RUNEXE (
  where py >nul 2>&1
  if not errorlevel 1 (
    py -3 -c "import PIL, imageio_ffmpeg" >nul 2>&1
    if not errorlevel 1 (
      set "RUNEXE=py"
      set "RUNARG=-3"
    )
  )
)
if not defined RUNEXE goto PY_MISSING
if "%SOURCE%"=="" goto PICK_SOURCE
if /I "%~x1"==".zip" goto ZIP_INPUT
if not exist "%SOURCE%" goto MISSING
set "OUTPUT=%~dp1_AutoCineReferenceReview_%~n1"
pushd "%SOURCE%" >nul 2>&1
if errorlevel 1 goto SOURCE_READY
popd
set "OUTPUT=%SOURCE%\_AutoCineReferenceReview"
:SOURCE_READY
echo [AutoCine] Input: "%SOURCE%"
echo [AutoCine] Output: "%OUTPUT%"
echo [AutoCine] Log: "%LOG%"
"%RUNEXE%" %RUNARG% -m tools.reference_video_review "%SOURCE%" --output "%OUTPUT%" > "%LOG%" 2>&1
set "EXITCODE=%ERRORLEVEL%"
goto CHECK_RESULT
:PICK_SOURCE
echo [AutoCine] No file dropped. Opening MP4/folder picker.
"%RUNEXE%" %RUNARG% -m tools.reference_video_review > "%LOG%" 2>&1
set "EXITCODE=%ERRORLEVEL%"
goto CHECK_RESULT
:CHECK_RESULT
if exist "%LOG%" (
  type "%LOG%"
  copy /y "%LOG%" "diagnostics\reference_review_latest.log" >nul 2>&1
)
if not "%EXITCODE%"=="0" goto FAILED
echo [AutoCine] COMPLETE. The contact sheet ZIP is in the output folder.
goto DONE
:PY_MISSING
>> "%LOG%" echo [ERROR] Python with Pillow and imageio-ffmpeg was not found.
echo [ERROR] Python with Pillow and imageio-ffmpeg was not found.
echo [ERROR] Run: py -3 -m pip install pillow imageio-ffmpeg
echo [ERROR] Then retry the MP4 or folder drop.
set "RESULT=4"
goto DONE
:ZIP_INPUT
>> "%LOG%" echo [ERROR] Extract the ZIP first, then select a video or folder.
echo [ERROR] Do not drop a ZIP archive. Extract it first, then drop an MP4 or folder.
set "RESULT=2"
goto DONE
:MISSING
>> "%LOG%" echo [ERROR] Input path not found: "%SOURCE%"
echo [ERROR] Input path not found: "%SOURCE%"
set "RESULT=2"
goto DONE
:FAILED
echo [ERROR] Reference video processing failed. Exit code: %EXITCODE%
echo [ERROR] Please send diagnostics\reference_review_latest.log
echo [ERROR] Fallback copy: "%LOG%"
set "RESULT=3"
:DONE
if exist "%LOG%" copy /y "%LOG%" "diagnostics\reference_review_latest.log" >nul 2>&1
echo.
if not defined CI pause
endlocal & exit /b %RESULT%
