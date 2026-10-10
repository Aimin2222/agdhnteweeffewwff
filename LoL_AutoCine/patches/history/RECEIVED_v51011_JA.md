# Codex統合用 v5.10.11

基準は v5.10.10 Windowsフル版（同等のCodexブランチ）。

1. `patches/v51011_from_v51010.patch` をプロジェクトの1階層上から `git apply --check` / `git apply` で適用。
2. 同梱の `LoL_AutoCine/` 内の新しいファイル・追加PNGを作業ツリーの同じ場所へコピー。
3. `core/camera.py`,`legacy_app.py`,`core/kill_icons.py` についてCodex側のGPU変更が先行していたら無条件上書きしないで差分マージ。
4. `python -m pytest -q tests/test_v51011_gallery_camera_qa.py` と `RUN_AUTOTEST.bat` を実行。

GPU書き出し本体、音声の実装ファイルには今回変更を加えていません。
実LoLリプレイ視点の構図はWindowsで確認。Replay API校正失敗時は安全俯瞰へフォールバックします。
