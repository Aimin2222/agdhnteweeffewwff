@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
if errorlevel 1 (
  echo [UI3] 起動フォルダへ移動できませんでした。
  goto Fail
)

rem Candidate 3 is a provisional integration target; keep all other launchers.
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "AUTOCINE_UI3_LAUNCH=1"
set "AUTOCINE_UI_COMPARE_PREFS=%~dp0ui3_data\workspace.json"
set "AUTOCINE_UI3_OUTPUT_DEFAULT=%~dp0ui3_data\exports"
set "TEMP=%~dp0ui3_data\temp"
set "TMP=%TEMP%"
set "PIP_CACHE_DIR=%~dp0ui3_data\pip_cache"
if not exist "%TEMP%" mkdir "%TEMP%"
if not exist "%AUTOCINE_UI3_OUTPUT_DEFAULT%" mkdir "%AUTOCINE_UI3_OUTPUT_DEFAULT%"
if not exist "%TEMP%" (
  echo [UI3] テスト用フォルダを作成できません。ZIPを展開し、書き込み可能な場所から起動してください。
  goto Fail
)

if /I "%~1"=="legacy" (
  set "AUTOCINE_RESEARCH_FLASH=legacy"
  set "AUTOCINE_RESEARCH_ZOOM=legacy"
) else (
  set "AUTOCINE_RESEARCH_FLASH=causal_pts_v1"
  set "AUTOCINE_RESEARCH_ZOOM=normalized_tmix_v1"
)

if defined AUTOCINE_UI3_PYTHON (
  set "UI3_PYTHON=%AUTOCINE_UI3_PYTHON%"
) else if exist "%~dp0.venv\Scripts\python.exe" (
  set "UI3_PYTHON=%~dp0.venv\Scripts\python.exe"
) else (
  set "UI3_PYTHON=python"
)

"%UI3_PYTHON%" -c "import numpy,PIL,imageio_ffmpeg,windows_capture,yt_dlp,pycaw,pyaudiowpatch,psutil,webview" >nul 2>&1
if errorlevel 1 (
  echo [UI3] Python または依存パッケージが不足しています。
  echo [UI3] Python 3.12 x64 の既存環境を優先し、requirements.txt をインストールしてください。
  echo [UI3] 例: python -m pip install -r requirements.txt
  echo [UI3] 準備済み環境がある場合: set AUTOCINE_UI3_PYTHON=...\Scripts\python.exe
  goto Fail
)
if not exist "%~dp0tools\bin\lol_audio_helper.exe" (
  echo [UI3] LoL専用音声ヘルパーがありません。BUILD_AUDIO_HELPER.bat で準備してください。
  goto Fail
)
if /I "%~1"=="--check" (
  echo [UI3] Python・依存パッケージ・音声ヘルパーを確認しました。
  endlocal & exit /b 0
)
if /I "%~2"=="--check" (
  echo [UI3] Python・依存パッケージ・音声ヘルパーを確認しました。
  endlocal & exit /b 0
)

echo [UI3] 候補3をWindowsアプリ内で起動します。Flash/Zoomの旧方式は引数 legacy で選択できます。
echo [UI3] このコマンド画面は診断用に1つだけ維持します。
"%UI3_PYTHON%" "%~dp0app.py" --ui3
set "UI3_RC=%ERRORLEVEL%"
echo [UI3] AutoCineの終了コード: %UI3_RC%
if not defined CI pause
endlocal & exit /b %UI3_RC%

:Fail
echo [UI3] 起動できませんでした。上の原因を確認してください。
if not defined CI pause
endlocal & exit /b 1
