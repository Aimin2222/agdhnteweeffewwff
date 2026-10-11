# v5.10.15 PortraitCrashFix 統合記録

受領パッチをraw UI archiveへ適用し、同梱の完成ファイルとバイト一致を確認。GPU担当feature/gpu-portraitfix-v51015へ小さいコミットをcherry-pickし、integration/v5.10.15-portraitfixへ統合。UI担当feature/ui-scan-v51015は変更なし。VERSIONは5.10.15のまま、配布名にPortraitCrashFixを付けて前回配布物を保持。

修正前、Playerを画像ID取得APIへ直接渡すとAttributeErrorを再現（受領テスト4失敗・1成功）。修正後5成功。辞書とPlayerの両形式に対応し、既存の識別子検証・旧素材名互換・キャッシュ利用・画像取得方法は不変。現在のUIは既に辞書スナップショットを渡すため、Windowsの同じ画面クラッシュをここで再現したとは説明しない。

共有8ファイルは前回レビューのGitオブジェクトをそのまま保持。GPUエンジン、60fps、音声、録画、TargetLock、カメラ、全UIファイルと37PNGを前回統合版とバイト比較する。新テストをGPU所有として登録し、UIからの古いkill_icons上書きを衝突ガードで検出する。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-portraitfix-v51015 --ui feature/ui-scan-v51015 --integration integration/v5.10.15-portraitfix --shared-review docs/CODEX_SHARED_API_REVIEW_PORTRAITFIX_v5.10.15.json
```

全pytestは除外なしで実行する。実結果は配布handoff/VERIFICATION_v5.10.15_PortraitCrashFix.json。物理GPU/NVIDIA/Windows/LoL実機の今回の動作は未検証。Draft PRのみ、mainへマージしない。
