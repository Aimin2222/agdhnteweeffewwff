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
if not exist "diagnostics" mkdir "diagnostics" >nul 2>&1
set "RUNEXE=py"
set "RUNARG=-3"
if exist ".venv\Scripts\python.exe" (
  set "RUNEXE=.venv\Scripts\python.exe"
  set "RUNARG="
) else if exist "venv\Scripts\python.exe" (
  set "RUNEXE=venv\Scripts\python.exe"
  set "RUNARG="
) else (
  where py >nul 2>&1
  if errorlevel 1 (
    set "RUNEXE=python"
    set "RUNARG="
  )
)
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
goto CHECK_RESULT
:PICK_SOURCE
echo [AutoCine] No file dropped. Opening MP4/folder picker.
"%RUNEXE%" %RUNARG% -m tools.reference_video_review > "%LOG%" 2>&1
goto CHECK_RESULT
:CHECK_RESULT
set "EXITCODE=%ERRORLEVEL%"
if exist "%LOG%" (
  type "%LOG%"
  copy /y "%LOG%" "diagnostics\reference_review_latest.log" >nul 2>&1
)
if not "%EXITCODE%"=="0" goto FAILED
echo [AutoCine] COMPLETE. The contact sheet ZIP is in the output folder.
goto DONE
:ZIP_INPUT
echo [ERROR] Do not drop a ZIP archive. Extract it first, then drop an MP4 or folder.
set "RESULT=2"
goto DONE
:MISSING
echo [ERROR] Input path not found: "%SOURCE%"
set "RESULT=2"
goto DONE
:FAILED
echo [ERROR] Reference video processing failed. Exit code: %EXITCODE%
echo [ERROR] Please send diagnostics\reference_review_latest.log
echo [ERROR] Fallback copy: "%LOG%"
set "RESULT=3"
:DONE
echo.
if not defined CI pause
endlocal & exit /b %RESULT%
