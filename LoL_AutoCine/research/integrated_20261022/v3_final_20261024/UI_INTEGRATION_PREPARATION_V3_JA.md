# 採用UI決定後の全機能統合準備

ユーザーはUI未選定。29画面/12候補を比較できる状態を先に完成し、ユーザー選定→採用UIへ既存全機能→Windows検証→研究採用→新機能、の順序を固定する。E Flow/A Studioの制作側推薦を採用決定と扱わない。

70行の`ALL_70_FEATURE_INTEGRATION_V3.csv/json`へV1の全ID・状態・証拠リンクを保持した。既存70は「70全機能が実動合格」の意味ではなく、部分/未実装（engage独立検出、best shot等）を含む監査項目。UI接続/Windows実行欄はすべて未実行を初期値にした。source側状態を勝手に格上げしない。

## 失われやすい設定と接続

|領域|保持項目|確認操作|
|---|---|---|
|Replay/scene|patch/対象/陣営、kill/assist/multi、範囲、チェック、順序、前後秒|scan→timeline選択→保存再開→同scene|
|camera|旧10ID、manual/fixed/full、TargetLock、yaw/pitch/FOV/zoom単位、keyframe、除外/陣営承認|各styleへ切替→戻す→原値照合|
|素材|旧37ID、frame/peakID/hash/status、弱強、位置/scale/stack、6motion|未承認表示維持→preview→final同snapshot|
|FX|既存ID/強度/revision、grade/LUT、時刻map、HUD/DOF/Fog|簡単↔詳細で隠れた値を初期化しない|
|GPU/音声|encoderとGPU FX別、CPUfallback、LoL音/BGM/gain/必須policy|GPU失敗と音声失敗を別に試す|
|出力/job|1920×1080/60、path/container、品質、cancel、結果/log|preview停止とrender取消を区別|
|view/theme|light/dark/system、サイズ、panel/tab、固定preview|themeでproject/target/preview/captureを再生成しない|

新UIの各layoutは同じProjectState/command adapterを使う。widget→command→validation→model→snapshot→jobの方向、engine結果→model→viewの方向を分け、viewのサンプル値を実LoL結果に見せない。ミラープレビューを固定し、右panelとscene一覧だけをscroll。ライト/ダークはview preferenceに保存し、画像previewのRGBへ色補正をかけない。テーマ切替の実動保持はT13が必要。

## 最新差分を更新する方式

最終観測UI head `9bb15e15d8057237515cc9bcf7e061a6d15d3369`、基準`fb03e0390805125fc063f4599af6c2541a653abf`。再帰tree全件で371file差分、core0/assets0。前回c7c506fからの26fileはUI CSSと比較画像/QA記録が中心。API compareの300file上限を避けfull treeで照合した。詳細は`LATEST_DEVELOPMENT_DELTA_V3.json`。新headが出たら統合前に同じ方法で差分取得し、changed codeの原文と該当T試験を更新する。hash不変はコード同一性の根拠であり、新UI経由の実機合格ではない。

## Windowsで利用者が確認する順

1. Pythonなし環境で起動、依存Runtime/FFmpeg、標準ユーザー、日本語path、表示倍率100/125/150%。
2. 同patchのReplayに接続し対象とBLUE/REDを確認。全scan、kill/assist、timeline、seek、ミラー常時表示。
3. 旧10camera/TargetLock、簡単/詳細の設定往復、未承認cameraの表示とfallback。
4. 旧37とWork選択/状態、6motion、global FX、previewと実動画の差。
5. LoL音と別app音を同時に流して専用captureを確認。GPU encode/GPU FX/CPU fallbackを別々に記録。
6. 1080p60出力を最後までdecode、30clip/長尺/cancel、保存再起動、テーマ切替、失敗表示を確認。

変更前後の同fixtureを残し、実機で未実行欄を埋める。UI screenshot一致の試験と、既存機能/Replay接続の試験を別に合否判定する。
