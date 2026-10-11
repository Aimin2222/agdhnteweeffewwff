# v5.10.15 ScanFix 統合レビュー

基準integration/v5.10.15-portraitfix。受領6ソースをarchive/received-scanfix-v51015へ保存、GPU担当feature/gpu-scanfix-v51015 / UI担当feature/ui-scanfix-v51015 / 統合integration/v5.10.15-scanfix。raw受領との差分は旧表示名の追加互換、既存非同期UI維持、DOF中央のモード排他、チェック画像のstate優先順、一括テストの中止/失敗表示/入力解放。原パッチ内の生ログ/cache/pycはGitへ含めず、historyは6ソースだけの再生成Gitパッチ。受領側89成功の記録は独自の検証結果と区別。

共同レビューcore/camera.pyはキャッシュ消去関数を追加するだけ。selection_name指定時は該当キー、無指定は全件クリア。UI選択/プレビュー/開発一括ケースから呼ぶ。座標/heading/pitch/TargetLock/CameraPlanと録画共有APIは変更なし。8共有blobのうちcameraだけ更新、残り7一致。kill_iconsは表示名/互換aliasだけ、PortraitCrashFixのPlayer対応は保持。全GPUエンジン/60fps/音声/37PNGは前回と同じ。

冷開始のスキャンはUIで設定snapshot→単一worker→接続→プレイヤー取得→完全スキャン。キャッシュ再利用/リプレイ世代を保持。DOFの2種類は中央/右側とも排他表示で値を保持。チェックはselected+disabled / selected+activeを一般stateより先に評価。一括録画は既存run_auto_edit/LoL専用音声でBLUE/RED4カメラと全切替、workerで実行、中止で次のケースを開始せず入力をfinally解放。Windowsの反転防止効果と録画結果は実機未確認。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-scanfix-v51015 --ui feature/ui-scanfix-v51015 --integration integration/v5.10.15-scanfix --shared-review docs/CODEX_SHARED_API_REVIEW_SCANFIX_v5.10.15.json
```

実テスト/ZIP/復元結果はhandoff/VERIFICATION_v5.10.15_ScanFix.json。旧83refs/配布物/個人設定を保持。Draft PRのみ、mainへマージしない。
