# Windowsローカル開発環境整備（2026-10-14）

> 過去の環境での実績記録です。2026-10-18のクリーンインストール後の状態・不足要件・再検証結果は [RECOVERY_20261018_JA.md](RECOVERY_20261018_JA.md) を参照してください。当時のPython／Helper／GPU成功を現在の実績とは扱いません。現行のテストrunnerはモジュール別、Windows GUIはケース別の子プロセスを使います。

対象版は5.10.26-test。元コミットae73309から作業ブランチ
`codex/windows-local-dev-setup-20261014`を作成した。
main、PR #29、3テーマ透過試作ブランチ、v5.10.27引き継ぎブランチの変更・マージ・pushは行わない。

## 導入した環境

- LoL_AutoCine/.venv: Python 3.14.7、グローバルPythonとは分離。
- requirements.txtの全依存とpytestを導入。pip check、主要import、GUI起動は成功。
- 主な導入版: numpy 2.5.4、Pillow 12.3.0、imageio-ffmpeg 0.6.0、windows-capture 2.0.1、yt-dlp 2026.10.10.233141.dev0、pycaw 20260927、PyAudioWPatch 0.2.12.9、psutil 7.2.2、pytest 9.1.1。
- Python 3.14だけが原因となる互換性障害は確認していない。現時点で3.12への切り替えは行っていない。
- Native Audio Helperは既存Visual Studio Build Tools 18.10.2とWindows SDK 10.0.26100.0でビルドし、tools/bin/lol_audio_helper.exeへ配置。引数なしのUsage表示・終了2を確認。音声キャプチャ本体は未検証。
- OS build 26200はHelperの要件20348以上を満たす。必要ヘッダーaudioclientactivationparams.hも存在。
- 追加の管理者インストール、専用GPU FFmpeg約200MBの取得は実施していない。Pythonの大きいwheelはローカルキャッシュから導入した。

## 起動とテスト

以下はLoL_AutoCineフォルダ内で実行する。バッチは自身のフォルダへ移動するので、ダブルクリックでもよい。

```powershell
# 初回または依存不足時（ネット接続が必要）
.\SETUP_DEV_ENV.bat

# 通常起動: .venv優先、なければ従来のpy -3
.\START.bat

# このPCの既存PATH FFmpegを検証して利用。ダウンロードなし。
.\START_LOCAL_GPU.bat

# 既存pytest全件を一時コピーで実行（LoLゲーム/リプレイは閉じる）
.\RUN_TESTS.bat --pytest-only

# pytestに加えて旧式総合テストも実行。旧テストの失敗を隠さない。
.\RUN_TESTS.bat

# GUI起動と合成素材1080p60/音声/GPU/CPUの検査
& .\.venv\Scripts\python.exe tools\run_local_smoke.py

# バッチを使わず起動
& .\.venv\Scripts\python.exe app.py
```

既存START_GPU.batは従来どおりチェックサム固定の専用FFmpegを導入する入口。
未導入時に約200MBを取得するため、今回の整備では実行していない。
新しいSTART_LOCAL_GPU.batは既存PATH FFmpegをセッション内のIMAGEIO_FFMPEG_EXEで明示選択し、OpenCL Fullプローブ成功時にだけ起動する。PATHや永続設定を書き換えない。

SETUP_DEV_ENV.bat -3.12は、.venvがまだ存在しない環境でのバージョン選択用。
既存.venvを削除・置換する機能はない。

## GPU実行結果

GTX 1070 Ti 8GB、ドライバー582.66。

| 使用FFmpeg | 実行結果 |
|---|---|
| imageio-ffmpeg付属7.1（通常起動） | h264_nvenc成功。OpenCLフィルターなし。エフェクトはCPUへフォールバック |
| 既存PATHの2026-05-31ビルド（ローカルGPU起動） | NV12 avgblur_opencl、RGBA program_opencl、Fullプローブ成功。1080p60/Bloomの実出力でgpu_effects_confirmed=true、h264_nvencを確認 |
| 明示CPU設定 | libx264、gpu_effects_confirmed=falseを確認 |

各出力の1920×1080、60fps、1秒、カラー保持、音声ストリーム、非無音を確認。
音声は試験用の合成WAVであり、LoL専用音声の実機合格ではない。
短い合成素材での結果であり、全エフェクトの画質、長時間安定性、ゲーム映像での速度は未検証。

## テスト結果と残る課題

最終pytestは77ファイル・652件すべて成功。失敗/skip/除外なし。7バッチ合計222.66秒（コピー準備等を除く）。
構文検査は171 Pythonファイル成功。依存セットアップの再実行とpip checkも成功。
GUI起動・イベント処理・終了、既定FFmpeg/ローカルFFmpegでの合成素材スモークも成功。
起動バッチ4種類は一時フォルダのスタブで.venv選択、引数転送、非ゼロ終了コードの保持を検証した。

ログは次のローカル除外フォルダに保持する（ユーザーパスを含むためコミットしない）。

- diagnostics/local_dev/20261014_015055_967613/: 最終pytest全件とsummary.json
- diagnostics/local_dev/smoke_20261014_014219_967754/: 起動・1080p60・音声・GPU/CPU出力
- diagnostics/local_dev/20261014_012729_199244/legacy.log: 旧式総合テストの成功/失敗詳細

初回pytestは634成功/18失敗。Windows向け検査を修正後、再実行で共有メモリ解放直後の1件が失敗した。
確認用ハンドルを閉じつつ最大3秒待つ検査へ直し、該当12件と最終全652件の成功を確認した。

旧式tests/run_tests.pyは16件中9成功・7失敗（t06/t07/t10/t11/t12/t13/t16）。
失敗を通すためのエンジン変更や保護処理の無効化は行っていない。

- t06/t10/t11/t13: ゲーム音ONのケースに必要なWAV/音声factoryを渡さない。t13の先行音声ミックスケースは実行されたが、その後の音声なしケースで失敗。
- t07: Windows/LoL不在時のCaptureError文言をLinux前提の文言で検査する。
- t12: 現在のカメラログへの旧テストの期待と不一致。座標・TargetLockは変更していない。
- t16: 正確静止画のPNG出力に失敗。先行監査にも静止画Bloomのサイズ混在が記録されている。今回の環境整備ではcore/preview.pyを変更しない。
- PillowのImage.getdata非推奨警告あり。現時点のテストを停止するエラーではない。

Windows用に修正した既存pytestの検査は、FFmpegグラフ中のドライブ文字エスケープ、モックへのNVIDIA監視混入、禁止文字を含むダミー画像名、区切り文字依存、共有メモリ解放直後のOSハンドル寿命。検査をskip/除外せず、エンジンや描画結果の期待は維持した。

## LoL実機で残る確認

実リプレイ接続、BLUE/RED各カメラの構図、TargetLockの実対象追従、HUD非表示、WGCのゲーム画面録画、LoLプロセスだけの音声（他アプリ音声の除外）、実時間同期、長時間1080p60、停止・再実行、全37素材の実動画は未検証。
合成テスト/モック成功を実機合格として扱わない。

## 保存とデータ保護

- 自動テストと起動スモークは一時ソースコピーで実施し、元settings.json、録画、テンプレート、診断を保護。
- テストの一時コピーと合成MP4/WAVは終了後削除。pytestの一時データもコピー内へ集約。
- 結果・診断はdiagnostics/local_dev/<実行日時>/へ保存し、Gitから除外。失敗ログも保持。
- .venv、Helper exe、obj、診断ログはコミットしない。
- core/、legacy_app.py、既存UI、37キルフレーム、元画像89枚は変更しない。
- 次の素材/カメラ統合作業には進まず、環境整備結果を報告して区切る。

最終確認で元89 PNGのSHA-256は台帳と全件一致。既存37 PNGも維持。
core/、legacy_app.py、ui/、assets/のGit差分はゼロ。

## 変更したファイル（LoL_AutoCine/以下）

| 範囲 | ファイル |
|---|---|
| 既存起動/テストバッチ | START.bat、START_GPU.bat、RUN_TESTS.bat |
| 新しい環境整備/GPU起動 | SETUP_DEV_ENV.bat、START_LOCAL_GPU.bat、requirements-dev.txt |
| ローカル検証ツール | tools/run_local_tests.py、tools/run_local_smoke.py、tools/check_local_gpu.py |
| Windows向けテスト修正 | tests/test_gpu_capture_isolation.py、tests/test_gpu_full_pipeline.py、tests/test_gpu_montage_v51014.py、tests/test_gpu_montage_v597.py、tests/test_gpu_opencl_bloom.py、tests/test_v51010_gallery_responsiveness.py、tests/test_v51019_camera_ui_reliability.py |
| 除外/報告 | .gitignore、本書 |
