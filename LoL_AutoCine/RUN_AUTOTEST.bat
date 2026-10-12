@echo off
rem ASCII-only launcher to avoid mojibake in Windows cmd.exe.
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
py -3 -m core.auto_qa
set "STATUS=%ERRORLEVEL%"
if not "%STATUS%"=="0" (
  echo [ERROR] Automatic diagnostics reported a failure.
  echo [ERROR] See diagnostics\selftest_latest.json
)
echo.
if not defined CI pause
endlocal & exit /b %STATUS%
