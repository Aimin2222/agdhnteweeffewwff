# AutoCine 保存元のGit状態と差分

保存場所: `/workspace/LoL_AutoCine`

取得用コピー: `/workspace/agdhnteweeffewwff/LoL_AutoCine`

ソースブランチ: `integration/v5.9.5`

## git status --short

```text
(未コミット変更なし)
```

## git log -3 --oneline

```text
d2ecc50 Record v5.9.5 workspace integration and regression evidence
4d87b86 Integrate v5.9.5 UI while retaining GPU audio and camera code
2368c81 Merge v5.9.5 ownership guard update
```

## git remote -v

```text
(remoteなし: ローカルGit)
```

取得用origin: https://github.com/Aimin2222/agdhnteweeffewwff.git 。mainへマージしない。

## 元v5.8.5から実際に追加・変更したファイル

A=追加、M=変更。

```text
A	README_v5.8.6_JA.md
A	README_v5.9.0_JA.md
A	README_v5.9.1_JA.md
A	README_v5.9.2_JA.md
A	README_v5.9.3_JA.md
A	README_v5.9.4_JA.md
A	README_v5.9.5_JA.md
M	VERSION.txt
M	core/camera.py
A	core/camera_clock.py
M	core/effects.py
M	core/jobs.py
A	docs/CHANGELOG_v5.8.6_JA.md
A	docs/CHANGELOG_v5.9.4_JA.md
A	docs/CHANGELOG_v5.9.5_JA.md
A	docs/CODEX_ARCHITECTURE_JA.md
A	docs/CODEX_AUDIT_RESULTS_JA.md
A	docs/CODEX_GPU_ANALYSIS_JA.md
A	docs/CODEX_INTEGRATION_CONTRACT_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.0_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.2_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.3_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.4_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.5_JA.md
A	docs/CODEX_INTEGRATION_v592_JA.md
A	docs/CODEX_INTEGRATION_v593_JA.md
A	docs/CODEX_INTEGRATION_v595_JA.md
A	docs/CODEX_LOCAL_DEVELOPMENT_JA.md
A	docs/CODEX_MERGE_NOTICE_v5.9.4_JA.md
A	docs/CODEX_MERGE_PROMPT_JA.md
A	docs/CODEX_MERGE_v5.9.0_JA.md
A	docs/CODEX_MERGE_v5.9.1_JA.md
A	docs/CODEX_PARALLEL_INTEGRATION_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.2.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.2_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.3.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.3_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.4.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.4_JA.md
A	docs/DESIGN_SCENESTUDIO_JA.md
A	docs/DIAGNOSTIC_FINDINGS_v5.9.4_JA.md
A	docs/REQUIREMENTS_SCENESTUDIO_JA.md
A	docs/TEST_PLAN_v5.9.0_JA.md
A	docs/changes_v5.9.4.patch
A	docs/v592_ui_changes.patch
A	docs/v593_ui_camera_changes.patch
M	legacy_app.py
A	patches/v594_to_v595.patch
A	tests/test_editor_ui_contract.py
A	tests/test_gpu_shared_camera_contract.py
A	tests/test_gpu_shared_camera_v593.py
A	tests/test_gpu_shared_camera_v594.py
A	tests/test_parallel_integration.py
A	tests/test_scene_keyframes_v592.py
A	tests/test_scene_sequence.py
A	tests/test_scene_studio.py
A	tests/test_scene_studio_gui.py
A	tests/test_v593_mode_camera.py
A	tests/test_v594_live_preview.py
A	tests/test_v595_workspace.py
A	tools/check_parallel_integration.py
A	ui/__init__.py
A	ui/motion_graph.py
A	ui/scene_batch.py
A	ui/scene_project.py
A	ui/scene_timeline.py
A	ui_changes_v5.9.1.patch
```

## 前回v5.9.4からの差分

A=追加、M=変更。

```text
A	README_v5.9.5_JA.md
M	VERSION.txt
A	docs/CHANGELOG_v5.9.5_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.5_JA.md
A	docs/CODEX_INTEGRATION_v595_JA.md
M	legacy_app.py
A	patches/v594_to_v595.patch
M	tests/test_parallel_integration.py
M	tests/test_v593_mode_camera.py
A	tests/test_v595_workspace.py
M	tools/check_parallel_integration.py
```

全17ブランチのコミットとbundleのSHA256はMANIFEST.jsonに保存。旧bundle/manifestを保持。
