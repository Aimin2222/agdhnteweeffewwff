# ワンクリック制作の成功率設計

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 成功の定義

「ボタン処理が終了」「MP4が存在」「FFmpeg exit0」「映像とLoL音声が正しい」を分離する。成功率を実測していないため今回の数値は出さない。分母は開始要求数、互換環境で開始できた数、clip試行数をそれぞれ保存し、途中キャンセルを除外するなら定義を添える。

|段階|確認と現在の入口|失敗時の設計案|
|---|---|---|
|1 接続|Replay API、ゲーム/ROFL版|原因分類、接続だけ再試行|
|2 対象固定|Player snapshot|別対象へ自動切替しない|
|3 全体scan|completeフラグ、元イベント|中断scanを完全扱いしない|
|4 シーン選択|チェック・pin・並び|選択状態保存、再scanで無言リセットなし|
|5 設定確定|template/素材ID/hash|入力を凍結しジョブfingerprint作成|
|6 環境事前検査|空容量・出力権限・helper・NVENC|書出し前に検出、CPU代替理由を表示|
|7 seek/warmup|新規frameとreplay進行|既存の制御された復旧を活用、無限再試行なし|
|8 camera/HUD/FX|適用readback・元状態|失敗時復元、未承認自動cameraは代替明示|
|9 音声開始|LoL helperと実WAV|game_audio必須なら失敗。全体録音禁止|
|10 録画|wall/replay/frame clock|停止・キャンセルで資源解放と状態復元|
|11 FX/合成|actual path、色、asset hash|CPU代替の品質確認、失敗raw保持方針|
|12 結合/検査|clip成功集合、AV/黒/fresh等|一部失敗を完全成功表示しない|
|13 保存/報告|manifestと出力hash|atomic確定、成功clipを使って失敗分だけ再開|

## 既存の保護

[core/jobs.py:442](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/jobs.py#L442)は音声開始失敗・空/短/完全無音WAVを失敗にし、HUD/FX/mirrorを復元する。[core/jobs.py:618](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/jobs.py#L618)はclip単位例外をres.failedへ記録して継続する。スキャン停止、録画停止、結合失敗を同じエラーに丸めない。

## 追加する永続job台帳案

job_id、source replay識別子、patch、player、scene interval、settings hash、asset hash、工程、attempt、output hash、error class、取消理由。出力はtmp→検査→renameで確定。途中再起動で同一入力の成功clipを二重生成せず、入力が変わった場合は旧結果を再利用しない。録画・API POSTは副作用があるので単純retry decoratorを付けない。

## Windows実機試験

正常2scene、1scene音声失敗、2scene目GPU FX失敗、容量不足、LoL閉じる、seek停止、キャンセル、再起動再開を試験。音声失敗で無音成功しない、成功済みclipが残る、設定/HUD/camera復元、再試行は失敗clipのみを合格条件にする。現状で全項目が実装済みという意味ではない。
