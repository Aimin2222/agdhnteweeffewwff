# Codex向け段階別依頼書（コピー用）

## 依頼1：UI比較の完了と選定待ち

UI29画面/12候補の独自layout/遷移を維持してください。ユーザーはUI未選定です。画像再現の結果と不足を報告し、制作側推薦を採用決定にしないでください。研究の新機能は実装しないでください。

## 依頼2：採用UIへ既存機能の統合（選定後のみ）

採用UI：ユーザーが明示するIDを記入。作業前に最新headと研究のLATEST_DEVELOPMENT_DELTA_V3を比較し、変更原文/関係テストを再確認してください。ALL_70_FEATURE_INTEGRATION_V3を1行ずつ接続/未接続/対象外理由/実行証拠で埋めてください。旧10camera、TargetLock、全scan、timeline、固定mirror、旧37badge、Work素材の状態、6motion、FX、GPUFXとencode、LoL専用音声、1080p60出力を削除しないでください。既存の部分/未実装項目を動作済みとして接続欄に記入しないでください。

ライト/ダーク/Windows追従はview設定のみ更新し、project/scene/camera/previewを初期化しないでください。preview再生/停止/実動画作成/取消を区別してください。未知保存fieldとmanual overrideを維持してください。

## 依頼3：既存不具合とWindows回帰

FX-FLASH-MULTIは人工入力でfirst-event-onlyを再現済みです。最新job経路で追試後、必要範囲だけ修正してください。空[]helper例外は通常no-kill経路のcrashと断定しないでください。T01〜T14のうち既存範囲を実機で実施し、未実行をPASSにせず、入力/ログ/出力hash/expected/observedを提出してください。GPU encodeだけの成功でGPUFXやLoL録音を合格にしないでください。旧templateの処理互換を確認してください。

## 依頼4：実行/配布確認

長尺/大量clip/cancel/失敗時音声/CPUfallback、Pythonなしclean Windows、Runtime依存、標準権限、日本語pathを確認し、portable EXE/ZIPの中身/sha256/起動/実出力を報告してください。未実装checkpointを再開対応済みと扱わないでください。診断は匿名化しユーザーlogを無断送信しないでください。

## 依頼5：研究採用後の新機能

採用する提案IDをユーザーが明示してから着手してください。先にRESEARCH_CONTRACTS_V3、6recipe、camera/QA/FX仕様を確認し、1提案ずつ別変更/回帰結果/rollback条件を提出してください。UI選定・素材承認の判断は代行しないでください。

## 完了報告の必須項目

本体commit、UI ID、接続70行の実績、不具合再現/修正、T01〜14の結果と未実行理由、BLUE/RED/音声/GPU/出力証拠、素材/原本/承認のbefore-after、配布SHA256、残件。画面が表示されたこととLoL実動の合格を分けて報告してください。
