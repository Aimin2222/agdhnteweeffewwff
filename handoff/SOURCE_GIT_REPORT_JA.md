# GPUFX版の保存・実変更

ソース保存先: /workspace/LoL_AutoCine。ローカルGit、remoteなし。
取得用保存先: /workspace/agdhnteweeffewwff。origin https://github.com/Aimin2222/agdhnteweeffewwff.git。
ソースHEAD: 16074dc72bce28cfc5daeb93ad34fdd073fa6beb。ブランチ: integration/v5.10.3-gpu-effects。
取得用ブランチ: codex/lol-autocine-v5103-gpu-effects-handoff。mainへマージしない。

開始時の両Gitのgit status --shortは空。最終コミット/push後の状態はVERIFICATION_v5.10.3_GPUFX.jsonに記録する。無視ファイル（.venv/個人設定/診断/録画/生成dist）をローカルに保持し配布しない。

## ソースgit log -3 --oneline

```
16074dc Record separate DOF-only and combined OpenCL reference measurements
dacf009 Integrate GPU Bloom and DOF while preserving v5.10.3 HangFix UI
eb8cb75 Add GPU-only OpenCL Bloom and circular DOF with verified Windows FFmpeg setup
```

## git remote -v

ソース: 空。取得用:

```
origin	https://github.com/Aimin2222/agdhnteweeffewwff.git (fetch)
origin	https://github.com/Aimin2222/agdhnteweeffewwff.git (push)
```

## 前回HangFix版からの追加・変更

```
M	.gitignore
A	START_GPU.bat
M	core/effects.py
A	core/gpu_binary.py
A	core/gpu_bloom.py
M	core/gpu_pipeline.py
A	docs/CODEX_GPU_EFFECTS_v5.10.3_JA.md
A	tests/test_gpu_opencl_bloom.py
M	tools/check_parallel_integration.py
A	tools/package_v5103_gpu.py
A	tools/setup_gpu_ffmpeg.py
```

## 元v5.8.5からの追加・変更

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
A	docs/CODEX_CHAMPION_PAIR_RESULTS_v5.9.9_JA.md
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
A	docs/CODEX_PARALLEL_INTEGRATION_JA.md
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
A	tests/test_gpu_champion_pair_v599.py
A	tests/test_gpu_circle_focus_v5103.py
A	tests/test_gpu_dof_only_v5103.py
A	tests/test_gpu_encoding_safety_v510.py
A	tests/test_gpu_encoding_v510.py
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
A	tools/package_v5103_gpu.py
A	tools/package_v5103_hangfix.py
A	tools/package_v599.py
A	tools/setup_gpu_ffmpeg.py
A	ui/__init__.py
A	ui/highlight_director.py
A	ui/hud_presets.py
A	ui/motion_graph.py
A	ui/scene_batch.py
A	ui/scene_project.py
A	ui/scene_timeline.py
A	ui/smart_montage.py
A	ui/studio_localization.py
A	ui_changes_v5.9.1.patch
```

250ソースファイル/Python93、全36ブランチをbundle保存。UI/カメラ/録画/LoL専用録音/Native Helper/元START.bat/依存宣言はHangFix版とバイト一致。全旧ブランチ・ZIP・bundleを保持。
