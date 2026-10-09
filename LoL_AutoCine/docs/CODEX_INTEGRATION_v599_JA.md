# v5.9.9 Codex統合用差分

- 基準: `codex/lol-autocine-v598-handoff`（v5.9.8）
- 変更ファイル: このZIPに含まれる `LoL_AutoCine/` 以下
- Git推奨: 既存変更をコミットしてから `git apply --check CHANGES_v5.9.9.patch` → `git apply CHANGES_v5.9.9.patch`
- Gitを使わない場合: 一覧を比較してから各ファイルをマージ（自動上書きは推奨しない）
- Codexが別途編集した `core/effects.py`、`core/gpu_pipeline.py`、`core/jobs.py`、`core/camera.py` 等はコンフリクト確認必須
- 音声のProcess Loopback、NVENC、TargetLock、UI設定の回帰テストを実施
- Windows/LoL/NVIDIA実機テストは配布前のLinux CIとは別に行う
