# 3UI忠実再現・独立監査取り込み結果（2026-10-28）

## 対象と基準

- 候補3は `testA / T-A-M`。元画像は `design/ui/implementation_audit_29_20261021/references/legacy_test/A_main.png`。PR #51原本は変更していない。
- R1はLeague Director参考 `LD_*.png`、R2はLolnam参考 `LN_*.png`。Work正本コミット `d0523f43d911eea781451b91c01098393bd69e6f`。
- 独立監査26件は固定コミット `8fa9050d64aaa77ee74cb604f8c1793fc9718c7c` の資料を読み、今の変更と照合した。個別状況は `qa/ui3_audit_20261028/RECONCILIATION_JA.md`。

## 実施した変更

候補3では原本HTMLと既存の7案比較版を変更せず、UI3 BAT起動時だけ4スライダー・数値・安全値リセット、フレーム/同名FX/6アニメ切替、素材「なし」、BLUE/REDとTargetLock選択、12シーン行の密度、ヘッダーと素材欄の配置を修正した。R1/R2では既存Appの相対キーフレーム直接編集、シーン別FX、実素材カード、出力設定、FPS/エンコーダ保持を追加。誤接続されていた「調整前と比較」は実装理由を表示して無効にした。R2のショット列を下段へ移し、出力対象ダイアログを追加した。

## Windows実画面と比較

| 対象 | 実画面 | 原画像比較 | 判定 |
|---|---|---|---|
| 候補3 | `qa/ui3_audit_20261028/c3_flow/T-A-M.png` | 同フォルダの `T-A-M_50percent_overlay.png` / `T-A-M_difference.png` / `T-A-M_comparison.json` | 寸法REVIEW、見た目REVIEW |
| R1 | `qa/ui3_fidelity_v2_20261028/ld/` の10状態 | 各状態の50% overlay/difference、一覧 `comparison_20.json` | 10状態すべてREVIEW |
| R2 | `qa/ui3_fidelity_v2_20261028/ln/` の10状態 | 同上 | 10状態すべてREVIEW |

20状態のUI領域平均チャネル差は10.03～18.54/255。これはゲーム映像と未取得シーンの可変領域を除外した測定で、全体の視覚合格点ではない。候補3の11領域はL/T/R/B辺で再判定し総合REVIEW。初回のR2映像面は533pxでWork原画539pxより6px短かった。その後、下段ショット列を維持したCSS調整で539pxとなった。再撮影は `qa/ui3_audit_20261028/r2_stage_refined/` に保存し、原画像との全体比較は引き続きREVIEW。

## 実操作・回帰テスト

- Windows WebView2 source hostで、候補3の4スライダー/リセット/素材なし/6アニメ入口、メイン→詳細→素材→メイン、カメラ・同名FX・設定保持を確認した。証拠は `qa/ui3_audit_20261028/c3_flow/index.json`。
- R1/R2のWindows WebView2で、比較ボタン無効、カメラ数値、実素材＋同名FX、144fps/GPUポリシーのタブ往復後保持、UI切替後の設定保持、入力中1.5秒のフォーカス保持を確認した。R2は下段ショット列と出力対象ダイアログ開閉も確認。証拠は各 `index.json`。
- 候補3の「画像選択」入口を原画位置へ復帰し、意味未確定のため理由付き無効とした。UI比較とR1/R2切替は全機能ドロワーへ移動。Windows再撮影・追加のDOM検査・同寸法重ね合わせを `qa/ui3_audit_20261028/c3_image_entry_refined/` に保存。画像選択の実処理は未接続。
- `pytest tests/test_ui3_integration.py tests/test_ui29_runtime.py tests/test_ui29_desktop.py -q`：30件＋24サブテスト通過。
- 実LoL接続、BLUE/RED実カメラ送信、GPU/NVENC、ゲーム音、録画、MP4書き出し、125% DPIはNOT_RUN。WindowsのUI撮影をそれらの合格と混同しない。

## 残る差・能力境界

- 候補3は元画像の情報配置へ近づけたが、未接続時の実ミラーは黒表示であり、文字・アイコン・カメラ画像・素材欄・フィルターに差が残る。架空のゲーム画面や検出シーンを貼っていない。
- R1/R2は20画面の骨格と直接操作を増やしたが、元画像の装飾、横カード、色ルック、時刻/再生倍率、原画の絶対FOV・自由Bezier・LUT/露出/彩度は未完成または既存処理と能力が違う。未接続操作は無効/説明表示にしている。
- 既存キーはキル相対秒、FOVは±15°の補正値。Workの絶対FOV64°などへ無断変換していない。
- Workの284件提案は画像/ソース監査の独立結果（PASS 0/FAIL 17/REVIEW 17/NOT_RUN 250）。Codexの従来台帳を上書きせず、今回のWindowsで確認した個別項目を別証拠として保持した。

本結果はWindows source hostのオフライン試験であり、完成版または実LoL総合合格を意味しない。
