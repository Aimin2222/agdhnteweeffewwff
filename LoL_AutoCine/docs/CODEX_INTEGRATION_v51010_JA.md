# v5.10.10 実シーン図鑑・キルログ素材とGPU Fullの統合

受領順はv5.10.7→v5.10.8→v5.10.9→v5.10.10。v5.10.8の原パッチが現在の7cd5b1へ適用可能なこと、v5.10.10原パッチがv5.10.9受領版へ適用可能なことを隔離cloneで確認した。原本はarchive/received-ui-v5108、v5109、v51010へコミット。全ファイル上書き指示は採用せず、GPUファイルをレビューして担当ブランチへ分けた。

- UI: feature/ui-real-scenes-v51010。実シーンのキル/アシストを選択・移動して実フレームを保存し、図鑑で同じ元映像と補正後を比較する。画像未保存時は案内のみ表示。静止画はカメラ/時間演出の再現をしない。
- GPU: feature/gpu-material-v51010。素材PNG6種、追加カラー、末尾に追加したTemplate.kill_sparkle_intensity/kill_stack_gapと新しい発光処理をレビュー。素材の顔部分には実際のキラー/犠牲者アイコンを合成し、385x116へ縮小する。動的発光OFFでも素材に描き込まれた装飾自体は残る。
- 統合: integration/v5.10.10。新しい間隔がCPUだけに届く問題をGPU Fullの配置にも接続し、両経路でround(116*scale+gap)の行送りに統一。入力不正/NaN/無限大の間隔と素材の発光値を共通検証。
- 図鑑の読込・色/2D FX比較は単一のLatestPreviewワーカーへ移動。Tkには設定のplain snapshotを渡す。最新要求だけ保持し、旧結果はgenerationで破棄、閉じるとworkerを停止。カードのPhotoImageはTkスレッドで順に表示する。同じ検出件数で内容が変わった再スキャンも選択肢を更新する。
- ミラーの受領変更は常時表示サイズ加工へ戻すため、品質選択にした。初期値「操作優先」は操作中640x360/約6fps、操作後960x540の既存対策を保持。「表示サイズで確認」は表示サイズで加工。設定保存対応。いずれもライブはCPU/Pillowの近似表示、書き出しはGPU Full/60fpsを保持。

core/gpu_pipeline、gpu_binary、gpu_bloom、recorder、capture、preview、camera/TargetLock、音声本体/Native Helperは前回と同一。gpu_fullの差分はキルログの行間のみ。effectsの差分は追加カラー/プリセット、Template末尾2項目、バッジ生成/行間の接続のみ。前回のGPUフレーム時刻・60fpsの修正を維持した。NVENCだけとGPUエフェクト実行の区別、非対応時のフォールバックも維持。

担当ガードへ新UIテストとGPU素材の所有を追加。stable/v5.8.5からの共有8ファイルは前回レビューした同じblobで、共有API変更なし。

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-material-v51010 --ui feature/ui-real-scenes-v51010 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.10.json --integration integration/v5.10.10
```

Linux/Tkの全回帰、素材の実アイコン/発光差分/行間、図鑑処理中のTk応答、再スキャン、ミラー品質選択を検証する。NVIDIA/Windows/LoLでの今回の新機能は未実機検証。ユーザーの診断ZIP、録画、生ログ、個人設定/プロジェクトはGitへ追加しない。旧57ブランチ先端と旧配布物を保持する。
