# Codex統合ガイド — v5.9.3

ベース: ChatGPT v5.9.2 / CodexのGPU最適化は引き続き別ブランチで管理

## 編集対象（変更あり）

- `legacy_app.py`：編集画面のモード切替、かんたんプリセット、キーフレーム型、三人称設定リセット。UIと動画生成の呼出し条件のみ。
- `core/camera.py`：再生時刻の連続補間・キーフレームの速度連続性・診断カウンター。既存TargetLock座標系には変更なし。
- `core/camera_clock.py`：新規。純Python・依存なしの時刻同期モデル。
- `core/jobs.py`：録画終了時のカメラ診断ログ1行追加。
- `tests/test_v593_mode_camera.py`：新規。
- `VERSION.txt`, `README_v5.9.3_JA.md`, `docs/CODEX_INTEGRATION_v593_JA.md`：更新資料。

## 編集していないファイル

`core/effects.py`, `core/gpu_pipeline.py`, `core/audio*.py`, `core/procloop.py`, `core/capture.py`, Native Audio Helperなど。

## 統合の推奨方法

1. 最新のCodexブランチを元に統合用ブランチを切る。
2. `docs/v593_ui_camera_changes.patch` のパッチを `LoL_AutoCine` ディレクトリから `git apply --check` で検査する。
3. 問題がなければ `git apply`。Codex側で `legacy_app.py` や `core/camera.py` への変更がある場合は手動で差分統合し、GPU/音声実装を温存。
4. Windows Replay APIの実機録画と既存テストを必ず実行する。

注意: **全ZIPをまるごと上書きしないこと。** 既存のCodex側GPU最適化パッチを失う可能性があります。
