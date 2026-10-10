@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
py -3 -m core.auto_qa
if errorlevel 1 (
  echo.
  echo 自動診断で失敗が見つかりました。diagnostics\selftest_latest.json を確認してください。
)
pause
