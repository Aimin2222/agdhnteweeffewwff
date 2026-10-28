# Work最終統合仕様の取り込み状況（2026-10-29）

## 基準と保護

- PR #55 のHEAD `bd93e2caf3bdb823d52b86fead0d71fc15c41327` を確認してから作業。main、PR #49/#51/#52/#54、既存素材の承認状態は変更していない。
- Work正本 `34c8cab1910fa979299b9457b846a760f6f208b2` の `design/ui/final_implementation_spec_20261028/` を原本のまま取り込んだ。9主要資料、36画面仕様、70機能台帳、16追加能力、239テスト計画、D01〜D11判断台帳を確認した。
- 本記録は段階的な実装証拠であり、3UI・36画面・70機能の完成判定ではない。

## 今回の実装

| 項目 | 状態 | 根拠・限界 |
|---|---|---|
| R1/R2回転角 `third_yaw` | 修正・Windows操作PASS | 32°を既存Appへ送信し、1.1秒pollとR1/R2切替後も保持。10スタイル×両サイドの実LoL確認はNOT_RUN。 |
| 遅延状態応答 | UI側対策済み | 操作中の古いsnapshot破棄、操作の順序化、入力中の再描画抑制。server側revision、replay generation、保存契約は未実装。 |
| R2 1366×768 | 対象条件PASS | Windows WebView2でpreview下端529px、timeline上端566px、footer上端740px、scrollHeight768px。125/150% DPIはNOT_RUN。1920版stage539pxは維持。 |
| R1/R2ダークテーマの文字 | 部分確認PASS | 数値入力・選択中タブ・候補切替タブをWindows WebView2のcomputed styleで測定。R2のコントラストは11.75/7.63/6.29。全コントロールとポップアップのテーマ検査はNOT_RUN。 |
| 3UI共通色設定 | 一部直接接続・Windows操作PASS | 既存Templateのgrade/strength/temperature/contrast/exposure/vibranceへ検証付き接続。候補3の全機能パネルからも露出0.12を操作確認。露出はEVではない。LUT選択、曲線、scene色override、GPU/CPU出力一致は未接続・NOT_RUN。 |
| 3UI原画像比較 | 21/21画像作成・REVIEW | `comparisons/index.json` に参照画像、Windows撮影、50%重ね、差分、寸法を記録。元画像には見本ゲーム映像があり、全画像RGB差をUI合格に使わない。文字、アイコン、素材欄には差が残る。 |

## 実行した検証

- `pytest tests/test_ui3_integration.py tests/test_ui29_runtime.py tests/test_ui29_desktop.py -q --tb=short`: **31 passed, 24 subtests passed**。対象外の機能を合格に繰り上げない。
- Windows WebView2 `--reference ln --reference-all`、`--reference ld --reference-all`、`--ui3-flow` はオフラインで完了。各 `index.json` に操作結果と撮影を保存。
- R1/R2で実Appへカメラ距離920・回転角32・フレームと同名FX・共通露出0.12・出力FPS144/encoder GPU設定を送信し、UI切替後の保持を確認。GPUによる実エンコード成功は確認していない。
- Workの239ケースは**個別の完全手順をまだ実行していないため239件ともNOT_RUN**。今回の部分実証はYAW-32、COMPACT-NO-OVERLAP、COLOR-ROUNDTRIP、STATE-SWITCHの将来判定の根拠として別管理する。既存284受入結果と26件独立監査結果は上書きしていない。
- `SCREEN_STATUS_36.json` は36画面の部分表示／入口のみを区別し、`FEATURE_STATUS_86.json` は70既存＋16追加能力の現在の入口と未完了条件を記録する。`TEST_EXECUTION_239.json` は239件すべてのNOT_RUNと4件の部分証拠を記録する。

## 残件とゲート

- 共通Project/Template/Sceneの型付き保存、Undo/Redo一般化、replay generation、server revision、旧schema移行。
- 3UIの36画面の内部配置・装飾・入力と全70機能の直接操作。従来エディタ経由の項目は直接接続完了と数えない。
- 絶対FOV、linear/hold/Bezier、scene色/LUTなどの判断待ちD01〜D11は推奨を承認とみなさず、適用していない。
- 実LoL、BLUE/RED全カメラ、GPU/NVENC、LoL音声、録画、MP4、125/150% DPI、プレビューと出力の一致はNOT_RUN。
- 比較画像は全21画面REVIEW。元画像との忠実度合格には、文字・素材・内部レイアウトの差分修正と再撮影が必要。

## 証拠

- `ln_capture/index.json`、`ld_capture/index.json`、`c3_capture/index.json`: Windowsソースホストの実画面と操作。
- `comparisons/index.json`: 正本21画像と実画面の重ね合わせ・差分。
- `design/ui/final_implementation_spec_20261028/specs/TEST_CASES.json`: 239件の未実行計画。
- 従来の `qa/ui3_audit_20261028/` と `qa/ui3_three_views_20261028/` は別台帳として保持。
