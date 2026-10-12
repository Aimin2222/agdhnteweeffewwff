@echo off
chcp 65001 >nul
setlocal DisableDelayedExpansion
cd /d "%~dp0"
title AutoCine Reference Video Review
set "SOURCE=%~1"
set "LOG=%TEMP%\AutoCine_ReferenceReview_latest.log"
if "%SOURCE%"=="" goto USAGE
if not exist "%SOURCE%" goto MISSING
set "OUTPUT=%~dp1_AutoCineReferenceReview_%~n1"
if exist "%SOURCE%\NUL" set "OUTPUT=%SOURCE%\_AutoCineReferenceReview"
set "RUNPY=python"
if exist ".venv\Scripts\python.exe" set "RUNPY=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set "RUNPY=venv\Scripts\python.exe"
echo [AutoCine] 参照動画の解析を開始します。
echo [AutoCine] 入力: "%SOURCE%"
echo [AutoCine] 出力: "%OUTPUT%"
echo [AutoCine] 詳細ログ: "%LOG%"
"%RUNPY%" -m tools.reference_video_review "%SOURCE%" --output "%OUTPUT%" > "%LOG%" 2>&1
set "EXITCODE=%ERRORLEVEL%"
type "%LOG%"
if not "%EXITCODE%"=="0" goto FAILED
echo.
echo [AutoCine] 完了:
echo "%OUTPUT%\ReferenceReview_contact_sheets.zip"
goto DONE
:USAGE
echo [使い方] MP4などの動画ファイル、または動画を含むフォルダーを、このBATの上にドラッグしてください。
echo [注意] ZIPを渡す場合は、先に展開してから動画かフォルダーを指定してください。
goto DONE
:MISSING
echo [ERROR] 指定されたファイル／フォルダーが見つかりません。
echo "%SOURCE%"
goto DONE
:FAILED
echo.
echo [ERROR] 参照動画の処理中にエラーが発生しました。終了コード: %EXITCODE%
echo [ERROR] 次のログファイルをそのまま送ってください:
echo "%LOG%"
echo [ERROR] Python／ffmpeg／Pillowや入力形式を確認してください。
:DONE
echo.
pause
endlocal
