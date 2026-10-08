# Codex向け v5.9.0 ChatGPT/UIブランチ統合手順

対象: Codexがv5.8.5ベースのGPUエンジンを開発中である一方、ChatGPT側でv5.8.6→v5.9.0を追加。

1. `LoL_AutoCine_v5.9.0_SceneStudio_UIOnly.zip` に含まれる **変更差分だけ**を統合する。`core/effects.py` / `core/gpu_pipeline.py` / `core/audio.py` / `core/camera.py` / `core/jobs.py` はこのUI差分に含めない。
2. `legacy_app.py` は既存UIとの競合をレビューして適用。カメラの固定・音声・TargetLock・GPUフォールバックを変えない。
3. `ui/scene_project.py`, `ui/scene_batch.py`, `ui/motion_graph.py` は新規モジュール。`ui/scene_timeline.py` はv5.8.6と同じ。
4. Worker関数の引数を `scene_mode, shots, auto` で増やしている。UIの値をWorker内で読み取ってはいけない。
5. `render_scenes` は `run_auto_edit` を1シーンずつ呼び出すため、シーン別モードON時はマルチキル重複がグループ化されず別クリップになる。GPUの一括処理と競合する場合、出力APIを変更する前に相談する。
6. 既存モードOFFなら従来の `run_auto_edit` を呼び出す。常にこの経路でも回帰テストする。
7. テスト：`python -m pytest tests/test_scene_studio.py -q`、GUI環境で`python -m pytest tests/test_scene_studio_gui.py -q`、`tests/test_editor_ui_contract.py`、`tests/test_checked_dispatch.py`。Windowsでは音声・カラー・複数クリップを実機確認する。
8. Git：安定版タグを保持し、UIブランチとGPUブランチを`git merge`、衝突は手動レビュー。単にファイル一式を上書きしない。

未実装：任意キーフレーム/曲線編集によるフレームごとのカメラ駆動、クリップ並べ替え、シーンサムネイル等。これらは機能完成と誤認しないこと。
