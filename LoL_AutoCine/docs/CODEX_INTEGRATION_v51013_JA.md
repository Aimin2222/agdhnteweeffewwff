# v5.10.11〜v5.10.13 GPU/UI統合レビュー

GPU担当はfeature/gpu-shared-v51013、UI担当はfeature/ui-player-filter-v51013、統合はintegration/v5.10.13。受領原本はarchive/received-ui-v51011〜13。以前のブランチ先端・配布物は保持する。

共有camera/jobs/scannerは担当ブランチの正確なblobでレビュー。CameraPlanの追加pitch_complementは既定False、ScanResult.eventsは末尾既定値付き。Template、run_auto_edit、LoL音声録音の呼出契約は維持。

- カメラ：俯角の2種類の表現を判定し、不明時は安全なトップへ。BLUE -12°/RED192°は受領版の自動構図。REDは暫定で実機映像の確認が必要。手動blue/redの0°/180°を維持し、スマート構図が基準角まで55°に丸めないよう修正。Lolnam軌道の位置と視線も同じ制限値を使う。ReplayFXは実際のCameraPlan距離を渡す。
- スキャン：試合全体の正規化イベントを一度集め、APIへの再要求なしで対象/キル/アシストを抽出。連続キルはキラー別・キルのみで計算。UIは完全終了時のみキャッシュし、再接続・リプレイ起動で対象と一覧を消去。処理中の表示プレイヤー変更は拒否し、表示を実際の対象へ戻す。
- 素材：既存6+v11追加15+v13追加16=37 PNGスタイルを保持。プレビュー385×116、書き出し素材770×232。CPU/GPU合成とも素材だけ倍率を半分にして同じ画面サイズ/行間を保つ。PNGは受領版と同一。装飾生成はキルごとにCPU、動画の合成は従来のGPU Fullで処理。
- UI：旧GPUファイルの丸ごと置換を避け、legacy_appは3-way統合。操作優先ミラー、設定変更時だけのsnapshot、図鑑・拡大画像の単一ワーカーと最新要求制限を維持。CPU/Pillowの近似ミラーをGPU処理済みと表示しない。
- QA：同時起動を防ぎ、エラーもキュー配送。選択中のFFmpegを確認し、VERSIONを正しく記録。NVENC列挙とGPU実処理を区別する。

音声/録画/GPU検出/60fpsのタイムスタンプ・フレーム数・CPUフォールバック・TEST_GPU_RENDERは以前の修正を保持。共有8ファイルの正確なblobをJSONで確認する。

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-shared-v51013 --ui feature/ui-player-filter-v51013 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.13.json --integration integration/v5.10.13
```

配布はCodex統合v5.10.10からのGit差分と完全版。UI単独版にGPUファイルを上書きしない。診断ログ・キャッシュを含む元のv13パッチはGit外に保持し、履歴にはソースのみの再生成差分を保存。WindowsまとめテストはWINDOWS_TEST_v51013_JA.md。
