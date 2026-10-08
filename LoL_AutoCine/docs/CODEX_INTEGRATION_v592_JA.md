# v5.9.2 Codex統合ガイド

## 共通基準

ChatGPT側 v5.9.1 Scene Sequence / Codex handoffを起点に、今回の**差分だけ**を取り込んでください。Codex側で別途変更されたGPUエフェクトを失わないよう、フル版ZIPを上書きしないでください。

## 変更したファイル

- `legacy_app.py` UI: キーフレーム編集、シーン別FX、ミラーからサムネイル保存
- `ui/scene_project.py` schema v3: Shot項目、検証、適用、v1/v2読込
- `ui/motion_graph.py` 実際のCameraPlanを使ったキーフレーム可視化
- `core/camera.py` Keyframe smoothstep補間、TargetLock座標系を変えず追加Orbit/Zoom/FOVの適用
- `core/jobs.py` Scene TemplateのキーフレームをCameraPlanへ渡すだけ
- `core/effects.py` Template.scene_keyframesフィールド追加のみ（FFmpegフィルタ本体は未変更）
- `tests/test_scene_keyframes_v592.py` 新規テスト
- `tests/test_scene_sequence.py`, `tests/test_scene_studio.py` schema v3による期待値更新

## Codexへの依頼

1. 手持ちのCodexブランチで変更をコミット/バックアップする。
2. パッチ `docs/v592_ui_changes.patch` を `git apply --check` で確認。Codexで変更済みの core/effects.py と衝突する場合は **1フィールド追加だけ**を手動でマージし、既存GPU処理のコードを優先する。
3. `legacy_app.py` は現在のUIを保持し、場面編集部分を統合。
4. `python -m pytest -q tests` を実行。GUIテストはLinuxなら `xvfb-run -a python -m pytest -q tests`。
5. Windows実機でカメラの向き/キャラクター追従、音声、カラーを確認。

## 既存機能は必ず維持

- camera TargetLockのキャラ中心Orbit、実際の座標系
- Native Process LoopbackによるLoL音声録音
- NVENC優先/CPU fallback
- モンタージュ並べ替え、チェック済みシーン出力

パッチはUTF-8。`git apply --check` に失敗したら強制適用せず衝突行を確認してください。
