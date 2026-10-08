# v5.9.2 元プロジェクトのGit状態

保存場所: `/workspace/LoL_AutoCine`

## git status --short

```text
（出力なし）
```

## git log -3 --oneline

```text
9724db1 Record v5.9.1 and v5.9.2 integration and regression evidence
f80f5ae Integrate v5.9.1 sequence and v5.9.2 scene editing UI
e04baaf Merge reviewed keyframe camera API bridge and integration guard
```

## git remote -v

```text
（出力なし）
```

## git diff --name-status integration/v5.9.0 HEAD

```text
A	README_v5.9.1_JA.md
A	README_v5.9.2_JA.md
M	VERSION.txt
M	core/camera.py
M	core/effects.py
M	core/jobs.py
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.2_JA.md
A	docs/CODEX_INTEGRATION_v592_JA.md
A	docs/CODEX_MERGE_v5.9.1_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.2.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.2_JA.md
A	docs/v592_ui_changes.patch
M	legacy_app.py
A	tests/test_gpu_shared_camera_contract.py
M	tests/test_parallel_integration.py
A	tests/test_scene_keyframes_v592.py
A	tests/test_scene_sequence.py
M	tests/test_scene_studio.py
M	tests/test_scene_studio_gui.py
M	tools/check_parallel_integration.py
M	ui/motion_graph.py
M	ui/scene_batch.py
M	ui/scene_project.py
A	ui_changes_v5.9.1.patch
```

未保存のソース変更はありません。ログ・録画・音声・個人プロジェクト・.venvは含めていません。
