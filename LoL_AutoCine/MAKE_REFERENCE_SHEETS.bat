@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if "%~1"=="" (
  echo.
  echo [AutoCine] xMedia / LoL MP4 フォルダーをこのBATへドラッグしてください。
  echo フォルダー内の全MP4から6時点の比較画像をまとめて作成します。
  echo.
  pause
  exit /b 1
)
set "SOURCE=%~1"
if not exist "%SOURCE%\" (
  echo [ERROR] 指定されたフォルダーがありません: %SOURCE%
  pause
  exit /b 2
)
set "RUNPY=python"
if exist ".venv\Scripts\python.exe" set "RUNPY=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set "RUNPY=venv\Scripts\python.exe"
echo [AutoCine] 参照動画の比較シートを作成中...
"%RUNPY%" -m tools.reference_video_review "%SOURCE%" --output "%SOURCE%\_AutoCineReferenceReview"
if errorlevel 1 (
  echo [ERROR] 処理失敗。先にAutoCineの依存ライブラリをインストールしてください。
  pause
  exit /b 3
)
echo 完了: %SOURCE%\_AutoCineReferenceReview\ReferenceReview_contact_sheets.zip
pause
endlocal
