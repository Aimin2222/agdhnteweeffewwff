# v5.10.10 保存報告

ソース保存先: /workspace/LoL_AutoCine、branch integration/v5.10.10、HEAD 3dc58a4558e6b7ccc72bddfae57edb995386d51c、remoteなし。
取得用: /workspace/agdhnteweeffewwff、branch codex/lol-autocine-v51010-real-scene-handoff、origin https://github.com/Aimin2222/agdhnteweeffewwff.git。
作業開始前の両git status --shortは空。完了時の状態はVERIFICATION_v5.10.10.jsonへ記録。mainにはマージしない。

## git log -3 --oneline（ソース）

```
3dc58a4 Merge validated gallery regression fixture correction
b704dbc Use package-qualified fixture import for gallery regression checks
550f0a0 Document received changes and preserve branch ownership and reproducible v5.10.10 packages
```

## git remote -v（取得用）

```
origin	https://github.com/Aimin2222/agdhnteweeffewwff.git (fetch)
origin	https://github.com/Aimin2222/agdhnteweeffewwff.git (push)
```

## 前回v5.10.7からの実際の追加・変更

```
A	README_v5.10.10_JA.md
A	README_v5.10.8_JA.md
A	README_v5.10.9_JA.md
A	TESTLIST_v5.10.10_JA.md
A	TESTLIST_v5.10.9_JA.md
M	VERSION.txt
A	assets/kill_badges/README_JA.txt
A	assets/kill_badges/cyberpunk.png
A	assets/kill_badges/inferno_gothic.png
A	assets/kill_badges/neon_crystal.png
A	assets/kill_badges/obsidian_gold.png
A	assets/kill_badges/premium_gold.png
A	assets/kill_badges/star_guardian.png
M	core/effects.py
M	core/gpu_full.py
M	core/kill_icons.py
A	docs/CODEX_INTEGRATION_v51010_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.10.10.json
A	docs/WINDOWS_TEST_v51010_JA.md
M	legacy_app.py
A	patches/history/RECEIVED_v51010_JA.txt
A	patches/history/RECEIVED_v5108_JA.txt
A	patches/history/RECEIVED_v5109_JA.txt
A	patches/history/v5.10.10_from_v5.10.9.patch
A	patches/history/v5.10.8_from_codex_v5.10.7.patch
M	tests/test_gpu_champion_pair_v599.py
M	tests/test_gpu_highlight_v598.py
M	tests/test_gpu_killbadges_v599.py
A	tests/test_gpu_material_v51010.py
M	tests/test_gpu_montage_v597.py
M	tests/test_gpu_shared_camera_contract.py
A	tests/test_v51010_gallery_responsiveness.py
A	tests/test_v51010_real_scene_material.py
M	tests/test_v5105_killfeed_glow_side_help.py
A	tests/test_v5108_premium_gallery.py
M	tests/test_v599_automontage_killbadges.py
M	tools/check_parallel_integration.py
A	tools/package_v51010.py
A	ui/template_gallery.py
```

## 元v5.8.5からの実際の追加・変更・移動

```
M	.gitignore
M	README.md
A	README_v5.10.10_JA.md
A	README_v5.10.5_JA.md
A	README_v5.10.8_JA.md
A	README_v5.10.9_JA.md
A	START_CPU_EFFECTS_COMPARE.bat
A	START_GPU.bat
A	START_GPU_HYBRID.bat
M	START_HERE.txt
A	TESTLIST_v5.10.10_JA.md
A	TESTLIST_v5.10.9_JA.md
A	TEST_GPU_RENDER.bat
M	VERSION.txt
A	assets/champion_icons/README_JA.txt
A	assets/kill_badges/README_JA.txt
A	assets/kill_badges/cyberpunk.png
A	assets/kill_badges/inferno_gothic.png
A	assets/kill_badges/neon_crystal.png
A	assets/kill_badges/obsidian_gold.png
A	assets/kill_badges/premium_gold.png
A	assets/kill_badges/star_guardian.png
M	core/camera.py
A	core/camera_clock.py
M	core/capture.py
A	core/capture_process.py
A	core/capture_worker.py
M	core/effects.py
A	core/focus_fx.py
A	core/gpu_binary.py
A	core/gpu_bloom.py
A	core/gpu_full.py
M	core/gpu_pipeline.py
A	core/highlight_pulse.py
M	core/jobs.py
A	core/kill_icons.py
A	core/montage_fx.py
M	core/performance_diagnostics.py
M	core/preview.py
M	core/recorder.py
M	core/replay_api.py
M	core/scanner.py
A	docs/APP_PACKAGING_PLAN_JA.md
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
A	docs/CODEX_INTEGRATION_v51010_JA.md
A	docs/CODEX_INTEGRATION_v5104_JA.md
A	docs/CODEX_INTEGRATION_v5105_JA.md
A	docs/CODEX_INTEGRATION_v5106_JA.md
A	docs/CODEX_INTEGRATION_v5107_JA.md
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
A	docs/CODEX_SHARED_API_REVIEW_v5.10.10.json
A	docs/CODEX_SHARED_API_REVIEW_v5.10.1_JA.md
A	docs/CODEX_SHARED_API_REVIEW_v5.10.4.json
A	docs/CODEX_SHARED_API_REVIEW_v5.10.5.json
A	docs/CODEX_SHARED_API_REVIEW_v5.10.6.json
A	docs/CODEX_SHARED_API_REVIEW_v5.10.7.json
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
A	docs/WINDOWS_TEST_v51010_JA.md
A	docs/WINDOWS_TEST_v5105_JA.md
A	docs/WINDOWS_TEST_v5106_JA.md
A	docs/WINDOWS_TEST_v5107_JA.md
A	docs/changes_v5.9.4.patch
A	docs/history/README.md
R100	README_AUDIO_DIAGNOSTICS_v5.6.2.md	docs/history/README_AUDIO_DIAGNOSTICS_v5.6.2.md
R100	README_AUDIO_FIX_v5.6.1.md	docs/history/README_AUDIO_FIX_v5.6.1.md
A	docs/history/README_before_v5105.md
A	docs/history/README_v5.10.0_JA.md
A	docs/history/README_v5.10.1_JA.md
A	docs/history/README_v5.10.3_JA.md
A	docs/history/README_v5.10.4_JA.md
R100	README_v5.4.md	docs/history/README_v5.4.md
R100	README_v5.7.2.md	docs/history/README_v5.7.2.md
R100	README_v5.8.2_DIAGNOSTICS.md	docs/history/README_v5.8.2_DIAGNOSTICS.md
R100	README_v5.8.5_JA.md	docs/history/README_v5.8.5_JA.md
A	docs/history/README_v5.8.6_JA.md
A	docs/history/README_v5.9.0_JA.md
A	docs/history/README_v5.9.1_JA.md
A	docs/history/README_v5.9.2_JA.md
A	docs/history/README_v5.9.3_JA.md
A	docs/history/README_v5.9.4_JA.md
A	docs/history/README_v5.9.5_JA.md
A	docs/history/README_v5.9.6_JA.md
A	docs/history/README_v5.9.7_JA.md
A	docs/history/README_v5.9.8_JA.md
A	docs/history/README_v5.9.9_ChampionPairFix_JA.md
A	docs/history/README_v5.9.9_JA.md
A	docs/history/START_HERE_before_v5105.txt
R100	START_HERE_v5.7.2.txt	docs/history/START_HERE_v5.7.2.txt
R100	START_HERE_v5.7.3.txt	docs/history/START_HERE_v5.7.3.txt
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
A	patches/history/RECEIVED_v51010_JA.txt
A	patches/history/RECEIVED_v5108_JA.txt
A	patches/history/RECEIVED_v5109_JA.txt
A	patches/history/ui_changes_v5.9.1.patch
A	patches/history/v5.10.10_from_v5.10.9.patch
A	patches/history/v5.10.8_from_codex_v5.10.7.patch
A	patches/history/v5106_from_codex_v5105.patch
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
A	tests/test_gpu_full_pipeline.py
A	tests/test_gpu_highlight_v598.py
A	tests/test_gpu_killbadges_v599.py
A	tests/test_gpu_material_v51010.py
A	tests/test_gpu_montage_v597.py
A	tests/test_gpu_opencl_bloom.py
A	tests/test_gpu_replay_warmup_v5101.py
A	tests/test_gpu_restore_mirror_v5106.py
A	tests/test_gpu_shared_camera_contract.py
A	tests/test_gpu_shared_camera_v593.py
A	tests/test_gpu_shared_camera_v594.py
A	tests/test_gpu_shared_replay_v5104.py
A	tests/test_gpu_shared_ui5106.py
A	tests/test_gpu_test_launcher.py
A	tests/test_parallel_integration.py
A	tests/test_scene_keyframes_v592.py
A	tests/test_scene_sequence.py
A	tests/test_scene_studio.py
A	tests/test_scene_studio_gui.py
A	tests/test_v51010_gallery_responsiveness.py
A	tests/test_v51010_real_scene_material.py
A	tests/test_v5101_scroll_check_warmup.py
A	tests/test_v5102_circle_focus_preset.py
A	tests/test_v5103_nonblocking_dispatch.py
A	tests/test_v5104_notebook_livefx_camera.py
A	tests/test_v5105_killfeed_glow_side_help.py
A	tests/test_v5105_preview_responsiveness.py
A	tests/test_v5106_hover_help.py
A	tests/test_v5107_mirror_controls.py
A	tests/test_v5108_premium_gallery.py
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
A	tools/gpu_render_test.py
A	tools/package_v5100.py
A	tools/package_v5101.py
A	tools/package_v51010.py
A	tools/package_v5103.py
A	tools/package_v5103_capture60.py
A	tools/package_v5103_capturefix.py
A	tools/package_v5103_exportopt.py
A	tools/package_v5103_gpu.py
A	tools/package_v5103_hangfix.py
A	tools/package_v5103_mirrorfix.py
A	tools/package_v5104.py
A	tools/package_v5105.py
A	tools/package_v5106.py
A	tools/package_v5107.py
A	tools/package_v599.py
A	tools/setup_gpu_ffmpeg.py
A	ui/__init__.py
A	ui/highlight_director.py
A	ui/hud_presets.py
A	ui/live_preview.py
A	ui/mirror_capture.py
A	ui/motion_graph.py
A	ui/redraw.py
A	ui/scene_batch.py
A	ui/scene_project.py
A	ui/scene_timeline.py
A	ui/smart_montage.py
A	ui/studio_localization.py
A	ui/template_gallery.py
```

全333ソース/Python127、全63ブランチをbundleへ保存。旧57ブランチ先端、GPUエンジン・カメラ・録画・LoL音声など23ファイル、受領PNG6種の一致を確認。GPU Fullの差分はキル行間、effectsはカラー/プリセット/末尾設定/バッジ設定接続のみ。個人設定/プロジェクト/原診断ZIP/録画/生ログは配布しない。旧版配布物102件をバイト単位で保持。
