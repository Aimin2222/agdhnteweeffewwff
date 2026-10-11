# v5.10.15 UI・スキャン・カメラ / GPU統合レビュー

GPU: feature/gpu-camera-v51015、UI: feature/ui-scan-v51015、統合: integration/v5.10.15。原本: archive/received-ui-v51015。旧76ブランチを保持し、前回Codex統合v5.10.14を配布の基準とする。

受領パッチ19パスは受領原本v14へ正確に適用して保存。現在のCodex修正と競合するcamera/montage/UI/テストは選択的に統合し、元GPUファイルの丸ごと置換は行わない。core/montage_fx.pyの受領追加は既存の旧日本語名互換処理と同等で、Codexの9演出GPU経路をそのまま保持する。

- UI: スキャン・表示プレイヤー・キル/アシストを右の検出シーンへ集約。既存の完全スキャンだけのキャッシュ、対象の同期、処理中の変更拒否、再接続後の破棄は保持。独立5作業領域、出力内の基本設定折りたたみ、明瞭な青チェック、DOF詳細の直下表示、素材/色の日本語名を統合。保存キー/素材37 PNGは不変。旧表示名も互換別名で読み込む。
- スクロール: ネイティブ候補一覧のホイールは背面へ転送しない。既存popdownだけ検知し、イベント毎に未使用メニューを生成しない。閉じたコンボで値を誤変更しない。UI内の旧Notebookテストは独立ページへ読み替え、ミラーの応答性テストを除外せず実行する。
- 比較: 大きい仕上がり比較のフレーム取得/色加工/縮小を既存LatestPreviewへ。最後のプリセット要求だけ表示し、設定・カメラを勝手に適用しない。閉じる/destroyで停止。従来の500msホバー/DOF比較と図鑑の非同期処理を保持する。
- 公式画像: チャンピオン画像のキャッシュ照会/ネット取得/画像読込/72px縮小はUI外の単一ワーカー。プレイヤーのplain snapshotのみ渡し、Tk呼出はUI側poll。イベント名の正規化、最後の選択とリプレイ世代の確認、取得失敗時の名前表示、終了時の停止。古い選択の画像を次の試合へ出さない。
- REDカメラ: 通常三人称の余分なpitch反転を撤廃し、校正済み符号を保持。±80°安全制限は従来のRED通常だけに限定しBLUE/シネマの数学を変更しない。通常三人称の自動RED yawは192→184°。手動blue/red 0/180°は8°補正を適用しない。FPSは実所属REDだけ既存offset量0.76倍、teamをCameraPlan末尾へ既定ORDERで追加。TargetLock、位置と視線の同じ基準、最終±55°、実キル時刻だけのnudgeは保持。

RED構図の改善は受領側の暫定調整であり、今回のWindows/LoL実映像の良否は未確認。三人称シネマ/FPS/Lolnam/BLUEの非対象モード、LoL専用音声/録画/同期、GPUエンジン、60fps時刻/フレーム数、NVENC/安全なCPUfallback、TEST_GPU_RENDERは維持する。CPU制御/静止画/ライブミラー近似表示は残る。

共有camera/jobsは正確なblobでレビュー、他6共有ファイルは前回と同じ。担当ガード:

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-camera-v51015 --ui feature/ui-scan-v51015 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.15.json --integration integration/v5.10.15
```

受領側507件成功・1ファイル除外の記録はdocs/RECEIVED_TEST_RESULTS_v5.10.15_JA.mdへ区別して保存。今回の統合テストの実結果はhandoff/VERIFICATION_v5.10.15.json。実機まとめテストはWINDOWS_TEST_v51015_JA.md。生診断/録画/個人設定はGitと配布ZIPへ含めない。
