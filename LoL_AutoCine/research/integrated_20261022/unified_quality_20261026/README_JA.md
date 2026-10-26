# LoL AutoCine 統合品質研究・素材類似整理
研究期間2026-10-26〜27。前回成果991f107857ee789b90f9fb5c24d2224a7addb4dfを引継いだ追加実証。実行可能なCPU/合成fixtureの研究納品を整理した。製品修正・正式素材承認・実LoL成功は未完である。

index.htmlを開くと9分野の資料、比較画像、手動再生動画を見られる。自動再生なし。B3動画だけ合成pulse音声を含み、初期muted。研究結果と正式採用を分ける。

|分野|今回の追加|残件|
|---|---|---|
|A1 類似|1464枠候補再計測、FX595組、同族1047組、AI比較38組|全人間選別・1450既存候補組の新規目視|
|A2 品質|P2新規24素材AI審査、652肖像候補数値|P2残523、651正式形状、19原本制約|
|A3 FX|Flash4clock列、他FX16＋組合せ4、移動中心blur比較|実Replay/GPU/色・負荷/最適強度|
|A4 位置|108条件・全時間3240frame、旧84FAIL、共有RGBA108PASS|nativeDPI/GUI/独立planner/全素材|
|B1 カメラ|切替4方式の軌跡・遅れ比較|BLUE/RED/TargetLock/地形の実機確認|
|B2 一括|既存処理対group候補、4assertion|実戦闘・録画E2E|
|B3 音声|合成AV4動画のactual PTS/音声decode|ゲーム音/concat/長尺/GPU|
|B4 機能|混合7＋4と比較3/5/8の70機能対応、15状態fixture|製品GUI実行|
|B5 配布|注入異常6種・日本語journal・CRLF text|Python無しPC/EXE/実異常系|

素材AI審査は継承P0/P1 140＋新規P2 24＝164/687。今回の比較組数を素材件数に二重加算しない。機械PASS/AI REVIEW/人間正式承認は別。ユーザー不採用5点を再推薦しない。

詳しい条件/再実行手順/実装指示は各分野READMEとCODEX_HANDOFF_JA.md。VALIDATION_REPORTは限定試験の合否で、総合製品PASS表ではない。SOURCE_REFERENCES/SOURCE_COMPARISON_7は照会した原文の固定コミット、PROTECTIONは原本保護、CONTENT_MANIFESTはZIP内hash一覧。

League Director／Lolnam Editor UI追加研究は未着手。現在の保存・完了報告より先に開始しない。今回UI候補評価・順位付け・新UI画像/プロトタイプは制作していない。

封印ZIPのGitHub再取得・実展開・全hash結果と保存SHAは、循環hashを避けZIP外のSAVE_RECEIPT.jsonに記録する。
