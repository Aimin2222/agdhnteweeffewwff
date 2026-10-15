# v5.9.2 シーンキーフレーム接続の共有APIレビュー

UI側の提案は受領ZIPの `docs/CODEX_INTEGRATION_v592_JA.md`。
Codex側で差分・呼び出し契約・従来カメラとの互換性を確認し、次の変更に限定して取り込む。
GPU・共有APIの変更は `feature/gpu-engine`、UIは `feature/ui-keyframes-v592` に分ける。

- `Template.scene_keyframes`: デフォルトはシーンごとに独立した空リスト。既存フィールドと位置引数の順序を保つため、末尾へ追加する。FFmpegフィルター・エンコード処理は変更しない。
- `CameraPlan.scene_keyframes`: デフォルトは空タプル。既存の位置引数を保つため末尾へ追加する。検証済みのキル相対時刻・加算Yaw・距離比・加算FOVを受け取る。
- `core/jobs._setup_clip`: プレーンなTemplateのキーフレームをタプルにしてCameraPlanへ渡す1接続だけを追加する。`run_auto_edit` の公開署名・音声・録画処理は維持する。
- カメラ座標・キャラクター中心のOrbit・最低高さを維持する。キーフレームは三人称系のみ有効。空または非三人称なら従来のFOVをそのまま返す。

受領コードでは空キーフレームにもFOVの32〜100度制限がかかり、新フィールドが途中へ挿入されていた。
従来動作・位置引数を保つ上記の小修正をCodex側で加えた。UIのソースは受領パッチと一致させる。
キー値は `ui/scene_project.py` の検証を経てスナップショットになり、ワーカー内でTkを参照しない。

GPUエフェクトモジュールをASTで比較し、追加フィールド以外の実装がv5.9.0と同一であることを確認する。
従来カメラとの比較、および `tests/test_gpu_shared_camera_contract.py` と既存OrbitTargetLockテストで回帰を確認する。
Windows・実LoLの向き、対象ロスト、Native音声、GPU実行は別途実機テストが必要。

機械的な承認範囲は `CODEX_SHARED_API_REVIEW_v5.9.2.json` に保存する。
共通基準コミット、変更担当、ファイルモード、Git blobハッシュを指定し、確認した内容だけを承認する。
同じファイルの後続変更、他方ブランチの変更、新たな共有API変更、統合先の巻き戻しは承認しない。
レビュー指定なしのガードは引き続き共有API変更を検出して終了1にする。

```sh
python tools/check_parallel_integration.py --ui feature/ui-keyframes-v592 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.2.json
python tools/check_parallel_integration.py --ui feature/ui-keyframes-v592 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.9.2.json --integration integration/v5.9.2
```

ガードはコミット済みの先端を比較する。実行前に `git status --short` も確認する。
