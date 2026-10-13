@echo off
setlocal
chcp 65001 >nul
set "ZIP_PATH=%~1"
if not defined ZIP_PATH (
  echo キルフレーム.zip のフルパスを貼り付けて Enter を押してください。
  echo または ZIP ファイルをこのBATファイルへドラッグしても実行できます。
  set /p "ZIP_PATH=ZIP path: "
)
if not defined ZIP_PATH (
  echo ZIP が指定されていません。
  pause
  exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0upload_original_killframes_from_zip.ps1" -ZipPath "%ZIP_PATH%"
if errorlevel 1 (
  echo.
  echo 取り込みに失敗しました。上のエラーメッセージを ChatGPT に送ってください。
) else (
  echo.
  echo 完了: GitHub Desktop の Changes 画面で Commit, Push origin を押してください。
)
echo.
pause
