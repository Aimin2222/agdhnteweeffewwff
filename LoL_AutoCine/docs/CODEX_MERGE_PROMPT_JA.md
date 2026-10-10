# Codexへ貼る統合依頼文

以下はChatGPT側で開発した v5.8.6 UIブランチです。あなたが進めているGPU実装と統合してください。

最初に `docs/CODEX_INTEGRATION_CONTRACT_JA.md` を読んでください。
このUIブランチは v5.8.5 を起点に作られており、GPU側の変更を上書きしないでください。

対象:
- `legacy_app.py` の編集UI変更（タイムライン、自動ディレクター、カメラ簡単設定）
- `ui/scene_timeline.py` 新規
- `tests/test_editor_ui_contract.py` 新規
- docs以下の統合方針

絶対に `core/effects.py`、`core/gpu_pipeline.py` や `core/audio.py` を古いものに戻さないでください。
既にGPU側ブランチでUIにも変更がある場合は、 `legacy_app.py` を丸ごと上書きせず、差分をレビューして適用してください。

統合後に `python -m pytest tests/test_editor_ui_contract.py tests/test_feature_preservation.py tests/test_orbit_target_lock.py -q` と `python tests/test_checked_dispatch.py` を実行してください（GUIテストはXvfbかWindowsで）。
Windows上でLoL音声、NVENC、GPUエフェクト、キル作成を実測し、結果を報告してください。
