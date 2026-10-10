# v5.10.3 GPUFX Capture60 保存報告

ソース: /workspace/LoL_AutoCine（ローカルGit、remoteなし）。取得用: /workspace/agdhnteweeffewwff（origin https://github.com/Aimin2222/agdhnteweeffewwff.git）。
ソースHEAD: 2a7a538540cbce9c13aae49da4a156cfd7ff4671、ブランチ: integration/v5.10.3-capture60。取得用: codex/lol-autocine-v5103-capture60-handoff。mainへマージしない。
開始前の両Gitのstatusは空。最終コミット/push後の状態はVERIFICATIONにも記録。個人設定・録画・原診断ZIP・ログ・.venvは配布しない。

## git log -3 --oneline（ソース）

```
2a7a538 Integrate 60fps capture with preserved scene and mirror UI
954f55c Document 60fps intermediate policy and preserve parallel integration contract
5aefb57 Record and normalize 60fps exports at 60fps without changing camera cadence
```

## git remote -v

ソースは空。取得用:

```
origin	https://github.com/Aimin2222/agdhnteweeffewwff.git (fetch)
origin	https://github.com/Aimin2222/agdhnteweeffewwff.git (push)
```

## 前回ExportOptからの実変更

```
M	core/jobs.py
A	docs/CODEX_CAPTURE60_v5.10.3_JA.md
A	docs/CODEX_SHARED_API_REVIEW_CAPTURE60_v5.10.3.json
A	tests/test_gpu_capture60_v5103.py
M	tools/check_parallel_integration.py
A	tools/package_v5103_capture60.py
```

## 元v5.8.5からの実変更

```
M	.gitignore
A	README_v5.10.0_JA.md
A	README_v5.10.1_JA.md
A	README_v5.10.3_JA.md
A	README_v5.8.6_JA.md
A	README_v5.9.0_JA.md
A	README_v5.9.1_JA.md
A	README_v5.9.2_JA.md
A	README_v5.9.3_JA.md
A	README_v5.9.4_JA.md
A	README_v5.9.5_JA.md
A	README_v5.9.6_JA.md
A	README_v5.9.7_JA.md
A	README_v5.9.8_JA.md
A	README_v5.9.9_ChampionPairFix_JA.md
A	README_v5.9.9_JA.md
A	START_GPU.bat
M	VERSION.txt
A	assets/champion_icons/README_JA.txt
M	core/camera.py
A	core/camera_clock.py
M	core/capture.py
A	core/capture_process.py
A	core/capture_worker.py
M	core/effects.py
A	core/focus_fx.py
A	core/gpu_binary.py
A	core/gpu_bloom.py
M	core/gpu_pipeline.py
A	core/highlight_pulse.py
M	core/jobs.py
A	core/kill_icons.py
A	core/montage_fx.py
M	core/performance_diagnostics.py
M	core/preview.py
M	core/recorder.py
A	docs/CHANGELOG_v5.8.6_JA.md
A	docs/CHANGELOG_v5.9.4_JA.md
A	docs/CHANGELOG_v5.9.5_JA.md
A	docs/CHANGELOG_v5.9.6_JA.md
A	docs/CHANGELOG_v5.9.7_JA.md
A	docs/CODEX_ALL_SCENES_HANG_FIX_v5.10.3_JA.md
A	docs/CODEX_ARCHITECTURE_JA.md
A	docs/CODEX_AUDIT_RESULTS_JA.md
A	docs/CODEX_CAPTURE60_v5.10.3_JA.md
A	docs/CODEX_CAPTURE_STARTUP_FIX_v5.10.3_JA.md
A	docs/CODEX_CHAMPION_PAIR_RESULTS_v5.9.9_JA.md
A	docs/CODEX_EXPORT_OPTIMIZATION_v5.10.3_JA.md
A	docs/CODEX_GPU_ANALYSIS_JA.md
A	docs/CODEX_GPU_EFFECTS_v5.10.3_JA.md
A	docs/CODEX_GPU_REVIEW_v5.9.8_JA.md
A	docs/CODEX_INTEGRATION_CONTRACT_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.10.0_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.10.1_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.10.3_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.0_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.2_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.3_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.4_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.5_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.6_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.7_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.8_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.9_JA.md
A	docs/CODEX_INTEGRATION_v592_JA.md
A	docs/CODEX_INTEGRATION_v593_JA.md
A	docs/CODEX_INTEGRATION_v595_JA.md
A	docs/CODEX_INTEGRATION_v596_JA.md
A	docs/CODEX_INTEGRATION_v597_JA.md
A	docs/CODEX_INTEGRATION_v598_JA.md
A	docs/CODEX_INTEGRATION_v599_JA.md
A	docs/CODEX_LOCAL_DEVELOPMENT_JA.md
A	docs/CODEX_MERGE_NOTICE_v5.9.4_JA.md
A	docs/CODEX_MERGE_PROMPT_JA.md
A	docs/CODEX_MERGE_v5.9.0_JA.md
A	docs/CODEX_MERGE_v5.9.1_JA.md
A	docs/CODEX_MIRROR_TARGET_FIX_v5.10.3_JA.md
A	docs/CODEX_PARALLEL_INTEGRATION_JA.md
A	docs/CODEX_SHARED_API_REVIEW_CAPTURE60_v5.10.3.json
A	docs/CODEX_SHARED_API_REVIEW_CAPTURE_v5.10.3.json
A	docs/CODEX_SHARED_API_REVIEW_EXPORT_v5.10.3.json
A	docs/CODEX_SHARED_API_REVIEW_MIRROR_v5.10.3.json
A	docs/CODEX_SHARED_API_REVIEW_v5.10.0.json
A	docs/CODEX_SHARED_API_REVIEW_v5.10.0_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.10.1.json
A	docs/CODEX_SHARED_API_REVIEW_v5.10.1_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.2.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.2_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.3.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.3_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.4.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.4_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.6.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.6_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.7.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.7_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.9.9.json
A	docs/CODEX_SHARED_API_REVIEW_v5.9.9_JA.md
A	docs/DESIGN_SCENESTUDIO_JA.md
A	docs/DIAGNOSTIC_FINDINGS_v5.9.4_JA.md
A	docs/HANDOFF_MASTER_2026-10-09_JA.md
A	docs/REQUIREMENTS_SCENESTUDIO_JA.md
A	docs/TEST_PLAN_v5.9.0_JA.md
A	docs/changes_v5.9.4.patch
A	docs/v5.9.5_to_v5.9.6.patch
A	docs/v592_ui_changes.patch
A	docs/v593_ui_camera_changes.patch
A	docs/v596_base_sha256.json
A	docs/v597_CHANGED_FILES.txt
A	docs/v597_changes.patch
A	docs/v598_CHANGED_FILES.txt
A	docs/v598_changes.patch
A	docs/v599_changes.patch
M	legacy_app.py
A	patches/v594_to_v595.patch
A	tests/test_editor_ui_contract.py
A	tests/test_gpu_capture60_v5103.py
A	tests/test_gpu_capture_isolation.py
A	tests/test_gpu_champion_pair_v599.py
A	tests/test_gpu_circle_focus_v5103.py
A	tests/test_gpu_dof_only_v5103.py
A	tests/test_gpu_encoding_safety_v510.py
A	tests/test_gpu_encoding_v510.py
A	tests/test_gpu_export_optimization.py
A	tests/test_gpu_highlight_v598.py
A	tests/test_gpu_killbadges_v599.py
A	tests/test_gpu_montage_v597.py
A	tests/test_gpu_opencl_bloom.py
A	tests/test_gpu_replay_warmup_v5101.py
A	tests/test_gpu_shared_camera_contract.py
A	tests/test_gpu_shared_camera_v593.py
A	tests/test_gpu_shared_camera_v594.py
A	tests/test_parallel_integration.py
A	tests/test_scene_keyframes_v592.py
A	tests/test_scene_sequence.py
A	tests/test_scene_studio.py
A	tests/test_scene_studio_gui.py
A	tests/test_v5101_scroll_check_warmup.py
A	tests/test_v5102_circle_focus_preset.py
A	tests/test_v5103_nonblocking_dispatch.py
A	tests/test_v510_ui_gpu_killframe.py
A	tests/test_v593_mode_camera.py
A	tests/test_v594_live_preview.py
A	tests/test_v595_workspace.py
A	tests/test_v596_hud_batch.py
A	tests/test_v597_studio.py
A	tests/test_v598_highlight_director.py
A	tests/test_v5991_portrait_pairs.py
A	tests/test_v599_automontage_killbadges.py
A	tools/check_parallel_integration.py
A	tools/package_v5100.py
A	tools/package_v5101.py
A	tools/package_v5103.py
A	tools/package_v5103_capture60.py
A	tools/package_v5103_capturefix.py
A	tools/package_v5103_exportopt.py
A	tools/package_v5103_gpu.py
A	tools/package_v5103_hangfix.py
A	tools/package_v5103_mirrorfix.py
A	tools/package_v599.py
A	tools/setup_gpu_ffmpeg.py
A	ui/__init__.py
A	ui/highlight_director.py
A	ui/hud_presets.py
A	ui/mirror_capture.py
A	ui/motion_graph.py
A	ui/scene_batch.py
A	ui/scene_project.py
A	ui/scene_timeline.py
A	ui/smart_montage.py
A	ui/studio_localization.py
A	ui_changes_v5.9.1.patch
```

ソース268/Python103、全45ブランチをbundle保存。前回版の全配布物を残す。今回のアプリ変更はcore/jobs.pyの録画fps制限とログのみ。GPUエフェクト/recorder/カメラ/時計/LoL音声/Native/START/UIはバイト一致。共有jobsの正確なblobはCODEX_SHARED_API_REVIEW_CAPTURE60_v5.10.3.jsonへ記録。詳細はCODEX_CAPTURE60_v5.10.3_JA.md。
