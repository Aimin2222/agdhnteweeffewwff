# 全体統合仕様

目的：候補3 `testA / T-A-M`、R1 Track Desk、R2 Shot Canvasの独自配置を保持し、同じAutoCine機能を利用できる一括実装契約に統合する。新UI選定/製品統合/最終デザイン採点は行わない。

## 基準と矛盾の解消

PR #55先頭を読み取り確認し、指定`bd93e2caf3bdb823d52b86fead0d71fc15c41327`と一致。PR #54先頭`5feff820b8fd3ffe2b300adb17277e77d57aae91`も確認。PR55はこの機能基盤を引き継いでいるが、PR54/55の報告PASSを今回の独立操作PASSにしない。現在取得した74ファイルはbyte数/Git blob照合済みで、製品実行はしていない。

原画優先順はユーザー選択PNG→計測/必須役割→再構成HTMLの寸法参考→過去改善提案。C3はL03-N/新A Studio/C3-P/Sではない。正本画像21枚はreferencesへ保存、全sourceはコミット固定manifestで参照。配布停止した過去demoを実行/復元/同梱しない。

既存70機能は接続手段の29直接/35従来エディタ/4自動/2未実装を維持しつつ、3UI専用入口へ移す。全機能の実接続合格という意味ではない。追加16能力は別IDで、ENGAGE/BESTSHOTは既存70に含む未実装のため二重計上しない。

Flash/Zoom候補は現在実装済みで通常BATから選択される。古い研究の未実装記載を上書きするのはこの実装能力の点だけで、正式採用/素材承認/実LoL成功へ繰り上げない。既存露出/LUT/近似比較helperも存在し、新UI接続/scene schema不足とエンジン新規を区別する。

## 共通アーキテクチャ

1つのApp/Template/SceneProjectに3view adapterを接続。DOMの見た目/個別routeは別、状態と処理は共通。現行runtime.performのwhitelist/main threadを再利用。追加API名は提案で、既存endpointの存在を偽らない。

State revision/request ID/replay generationで遅い応答を排除、draftと確定stateを分離。画面/テーマだけの変更はrender/camera/scanの副作用なし。jobは開始時config/hashのimmutable snapshot、live編集が進行中jobへ混入しない。

詳細はSTATE_AND_SAVE_CONTRACT.json。現SceneProject v3はshots/sequenceだけで、全Template/Replay/check/UIを保存しない。ProjectBundleの追加を別schemaとして提案し、旧形式の読込と型区別を保持する。camera presetはside×style単位で色/音声/素材から独立。

## 受入済み部分と残件

差分監査26親IDは完了済み調査として再利用。静的解消6/改善継続18/追加修正1/仕様整理1。4スライダー、素材切替、比較誤接続除去、539px desktopなどの改善を再実装しない。1366の重なり、Yaw読取、キーcurve、原画詳細操作、色/LUT、比較/チェック/テーマを残件として画面/機能契約へ組み込む。

## 今回の確定範囲

36画面/子画面契約、数値/単位、状態/保存/エラー/両theme、70+16能力の処理境界、14曖昧点、26監査残件、依存DAG、単体/統合/実機計画を定義。11判断事項は選択肢と推奨を明記し未採用。原画にない子画面は追加仕様と表示し、存在しない原画像/寸法を出典として作らない。

未完了のP2素材523、651暫定肖像、原本制約19、実LoL/GPU/音声/DPIはそのまま保持。研究の数値fixture/限定描画を製品成功に変えない。権利不明の第三者画像/素材は同梱しない。

## 完了の定義

今回の完了は「実装前統合仕様の納品」。製品の完成ではない。Codexは仕様の必須既存接続を実装し、追加候補は判断/dataゲートのまま扱い、実行結果を同じIDへ証拠付きで返す。main/旧UI/原本/承認を保護し、正式採用やmergeを勝手に行わない。


## 全設定を落とさないための補助台帳

`specs/TEMPLATE_ALL_FIELDS.json`は基準版Templateの全宣言fieldを型/既定/元comment/現行source/3UI入口/保存scope付きで一覧化しています。`FEATURE_SECTIONS_70.json`は70専用sectionと画面IDを対応付けます。設定を削って見た目を簡略化しません。未確定rangeは明示し、Codexは既存validator/専用controlをbridgeで公開してから数値controlを有効化してください。新しい可変rangeや単位を推測しないでください。

専用APIは状態を返すqueryとvalidated commandを分離し、project/Template/sceneのscopeを明示。既存`perform`にないNEW名は提案です。既存handlerを検証したadapterを追加し、任意method名やOS commandをJSから実行する汎用APIへ変えません。保存はschema/typeの全検証後atomic replace、失敗時は旧stateを保持します。
