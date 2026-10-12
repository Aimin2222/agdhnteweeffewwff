@echo off
rem This batch file is deliberately 7-bit ASCII to avoid CP932/UTF-8 cmd.exe parsing corruption.
chcp 65001 >nul
setlocal DisableDelayedExpansion
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "RESULT=0"
cd /d "%~dp0"
title AutoCine - Reference Video Review
set "SOURCE=%~1"
set "LOG=%TEMP%\AutoCine_ReferenceReview_latest.log"
if "%SOURCE%"=="" goto USAGE
if not exist "%SOURCE%" goto MISSING
set "OUTPUT=%~dp1_AutoCineReferenceReview_%~n1"
pushd "%SOURCE%" >nul 2>&1
if errorlevel 1 goto SOURCE_READY
popd
set "OUTPUT=%SOURCE%\_AutoCineReferenceReview"
:SOURCE_READY
set "RUNPY=python"
if exist ".venv\Scripts\python.exe" set "RUNPY=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set "RUNPY=venv\Scripts\python.exe"
echo [AutoCine] Starting reference video review.
echo [AutoCine] Input: "%SOURCE%"
echo [AutoCine] Output: "%OUTPUT%"
echo [AutoCine] Log: "%LOG%"
"%RUNPY%" -m tools.reference_video_review "%SOURCE%" --output "%OUTPUT%" > "%LOG%" 2>&1
set "EXITCODE=%ERRORLEVEL%"
if exist "%LOG%" type "%LOG%"
if not "%EXITCODE%"=="0" goto FAILED
echo [AutoCine] COMPLETE: "%OUTPUT%\ReferenceReview_contact_sheets.zip"
goto DONE
:USAGE
echo [USAGE] Drag a video file (MP4/MOV/MKV/WEBM) or a folder onto this BAT.
echo [USAGE] Unzip archives before dropping videos or folders.
set "RESULT=1"
goto DONE
:MISSING
echo [ERROR] Input path does not exist: "%SOURCE%"
set "RESULT=2"
goto DONE
:FAILED
echo [ERROR] Reference-video review failed. Exit code: %EXITCODE%
echo [ERROR] Please attach this log file:
echo "%LOG%"
set "RESULT=3"
:DONE
echo.
if not defined CI pause
endlocal & exit /b %RESULT%
