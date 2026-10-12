@echo off
rem Keep this file strictly ASCII; only Python displays Japanese user text.
chcp 65001 >nul
setlocal DisableDelayedExpansion
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "RESULT=0"
cd /d "%~dp0"
title AutoCine - Reference Video Review
set "SOURCE=%~1"
set "LOG=%TEMP%\AutoCine_ReferenceReview_latest.log"
set "RUNPY=python"
if exist ".venv\Scripts\python.exe" set "RUNPY=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set "RUNPY=venv\Scripts\python.exe"
echo [AutoCine] Reference Video Review
echo [AutoCine] Log: "%LOG%"
if "%SOURCE%"=="" goto PICKER
if not exist "%SOURCE%" goto MISSING
if /I "%~x1"==".zip" goto ZIP_INPUT
set "OUTPUT=%~dp1_AutoCineReferenceReview_%~n1"
pushd "%SOURCE%" >nul 2>&1
if errorlevel 1 goto DIRECT_RUN
popd
set "OUTPUT=%SOURCE%\_AutoCineReferenceReview"
:DIRECT_RUN
echo [AutoCine] Input: "%SOURCE%"
echo [AutoCine] Output: "%OUTPUT%"
"%RUNPY%" -m tools.reference_video_review "%SOURCE%" --output "%OUTPUT%" > "%LOG%" 2>&1
goto CHECK_RESULT
:PICKER
echo [AutoCine] Opening video/folder picker. Cancel file selection to choose a folder.
"%RUNPY%" -m tools.reference_video_review > "%LOG%" 2>&1
goto CHECK_RESULT
:CHECK_RESULT
set "EXITCODE=%ERRORLEVEL%"
if exist "%LOG%" type "%LOG%"
if not "%EXITCODE%"=="0" goto FAILED
echo [AutoCine] Finished. Look for ReferenceReview_contact_sheets.zip.
goto DONE
:ZIP_INPUT
echo [ERROR] ZIP was dropped. Extract the ZIP first; then select MP4 or a folder.
echo [ERROR] Double-click this BAT to select a video without drag and drop.
set "RESULT=4"
goto DONE
:MISSING
echo [ERROR] The input path does not exist: "%SOURCE%"
set "RESULT=2"
goto DONE
:FAILED
echo [ERROR] Video review exited with code: %EXITCODE%
echo [ERROR] Please send the following log file:
echo "%LOG%"
set "RESULT=3"
if not defined CI if exist "%LOG%" start "" notepad.exe "%LOG%"
:DONE
echo.
echo [AutoCine] Press any key to close this window.
if not defined CI pause >nul
endlocal & exit /b %RESULT%
