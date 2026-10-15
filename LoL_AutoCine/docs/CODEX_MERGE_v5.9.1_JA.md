# Codex統合 — v5.9.1 ChatGPT UI差分

## 基準

- GitHub `Aimin2222/agdhnteweeffewwff` ブランチ `codex/lol-autocine-v590-handoff` の `LoL_AutoCine` サブフォルダ。
- 変更対象は `legacy_app.py`, `ui/scene_project.py`, `ui/scene_batch.py`, `tests/test_scene_studio.py`, `tests/test_scene_studio_gui.py`, `tests/test_scene_sequence.py` とUI向けdocs、`VERSION.txt`。
- `core/**`, `tools/native_audio/**`, `core/effects.py`, `core/gpu_pipeline.py` は**変更していない**。

## 推奨手順

1. 最新GPUブランチからUI用ブランチを切る。
2. `ui_changes_v5.9.1.patch` の適用前に `git apply --check ui_changes_v5.9.1.patch`。
3. 問題なければ `git apply ui_changes_v5.9.1.patch`。競合がある場合はソース丸ごと上書きせず、差分内容を手動で統合。
4. `python -m pytest -q tests`、必要に応じて `xvfb-run` の仮想表示でTkテストを実施。
5. Windowsでクリップ音声、カラー、カメラTargetLock、シーン順序を実機テスト。

### 呼び出し契約

- シーンON時だけ `SceneProject.sequence` のスナップショットが `render_scenes(...,order=...)` へ渡る。
- OFFの経路は従来の `core.jobs.run_auto_edit` を無変更で呼ぶ。
- プロジェクトJSON schema 2。schema 1もロード可。
- GUIのTk値はUIスレッドでスナップショットを取得しワーカーへ渡す。

**注意**：Codex側が別途 `legacy_app.py` を変更している場合、Git側で差分統合すること。GPU側変更があるならビデオ生成の実機テストを必須とする。
