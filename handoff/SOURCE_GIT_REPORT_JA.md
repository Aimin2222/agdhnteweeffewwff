# 元プロジェクトのGit状態

保存場所: `/workspace/LoL_AutoCine`

## git status --short

```text
（出力なし）
```

## git log -3 --oneline

```text
c271b60 Record v5.9.0 integration checks and Windows handoff plan
9ea22f0 Integrate v5.9.0 SceneStudio UI without changing GPU core
4deb9d4 Merge SceneStudio branch ownership guard
```

## git remote -v

```text
（出力なし）
```

## git diff --name-status baseline/v5.8.5 HEAD

```text
A	README_v5.8.6_JA.md
A	README_v5.9.0_JA.md
M	VERSION.txt
A	docs/CHANGELOG_v5.8.6_JA.md
A	docs/CODEX_ARCHITECTURE_JA.md
A	docs/CODEX_AUDIT_RESULTS_JA.md
A	docs/CODEX_GPU_ANALYSIS_JA.md
A	docs/CODEX_INTEGRATION_CONTRACT_JA.md
A	docs/CODEX_INTEGRATION_RESULTS_v5.9.0_JA.md
A	docs/CODEX_LOCAL_DEVELOPMENT_JA.md
A	docs/CODEX_MERGE_PROMPT_JA.md
A	docs/CODEX_MERGE_v5.9.0_JA.md
A	docs/CODEX_PARALLEL_INTEGRATION_JA.md
A	docs/DESIGN_SCENESTUDIO_JA.md
A	docs/REQUIREMENTS_SCENESTUDIO_JA.md
A	docs/TEST_PLAN_v5.9.0_JA.md
M	legacy_app.py
A	tests/test_editor_ui_contract.py
A	tests/test_parallel_integration.py
A	tests/test_scene_studio.py
A	tests/test_scene_studio_gui.py
A	tools/check_parallel_integration.py
A	ui/__init__.py
A	ui/motion_graph.py
A	ui/scene_batch.py
A	ui/scene_project.py
A	ui/scene_timeline.py
```

未コミットの追跡済み変更・未追跡ソースはありません。作業用.venv、キャッシュ、診断ログ等は除外されています。

受け渡し用GitHubリポジトリ: `Aimin2222/agdhnteweeffewwff`。元AutoCineのremoteとして設定したものではありません。
