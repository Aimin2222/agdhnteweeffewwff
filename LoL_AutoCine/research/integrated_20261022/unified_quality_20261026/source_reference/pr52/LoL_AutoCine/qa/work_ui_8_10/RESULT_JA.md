# Work新UI 候補8〜10 独立体験版の検証

## 正本と構成

- 正本: Work研究コミット `6ab57afee2e236e50833c6e15022484fb84b79e7` の `research/integrated_20261022/v4_continuation_20261026/ui/`
- 専用アプリ: `standalone/work_ui_8_10/`。アプリ内WebView2で動作し、外部ブラウザの操作は不要。
- 開発者向け対応: 候補8 = P1 Focus、候補9 = P2 Guided、候補10 = P3 Collection。利用者に見える切替・現在候補・比較画面は番号表示。
- 現行AutoCine、既存候補1〜7、PR #51のファイルと機能は変更していない。独立した起動ファイルと配布ZIPを使用する。

## Windows EXE画面と原画像の比較

配布用EXEからWork指定の24画面をWebView2で撮影した。全件で指定解像度、候補番号、ポップアップ表示、横方向のはみ出しを確認し、エラーは0件だった。撮影結果は `frozen_all_final/`、寸法・画素比較は `frozen_comparison/metrics.json` に保存した。主要画面の `reference.png`、`windows_app.png`、`overlay_50.png`、`absolute_difference.png` も同フォルダに保存した。

| 画面 | 平均RGB絶対差 | 差分20超の画素 |
|---|---:|---:|
| 候補8 main | 2.57 | 1.17% |
| 候補9 flow | 2.35 | 1.06% |
| 候補10 library | 2.69 | 1.23% |
| POP-compare | 2.31 | 0.85% |
| 候補8 small | 3.54 | 1.96% |
| 候補9 small | 3.54 | 2.05% |

24画面全体で差分20超の画素は平均1.09%、最大2.05%。差分には候補名を番号へ置換した文字列とWebView2の文字描画差が含まれる。画像の貼り付け表示ではなく、WorkのHTML/CSS構造を専用アプリで描画している。候補9・10の詳細編集画面は元画像がないため同じデザインで補完しており、画像一致の対象外。

## 体験操作

ソース起動、配布用EXE、配布ZIPを実際に展開したEXEで操作シナリオ11件が通過した。候補8→9→10切替、ライト/ダーク、簡単/詳細編集、カメラ画面、スライダーと数値入力、シーン選択と出力チェックの区別、素材選択、候補変更後の状態保持、出力モックの表示、Escで閉じる操作を確認した。記録は `interaction_source.json`、`interaction_frozen.json`、`interaction_zip_extracted.json`。

実装した操作はUI状態の比較・体験用である。LoL接続、実スキャン、録画、GPU/NVENC、音声、MP4出力、AutoCine本体の設定保存は**未実装**。ミラープレビューの映像・シーン・素材は見本であり、実処理に接続したとは表示しない。

## 配布と制限

`AutoCine_Work_UI_8_10_Portable.zip` を展開し、`AutoCine_Work_UI_8_10.exe` を起動する。同梱のWebView2 Fixed Runtime x64を使用する。ビルド元コードは `1834e5d`、ZIPのSHA-256は `bffa6666a6b76b89088dbdd567a1fc37c1de8240c8e69b8dcdae69046d51388b`。ZIPのCRCと展開後EXEの11操作を確認した。Windows x64以外、実LoL連携、125% DPIでの実機操作はこの検証の合格対象外。候補1〜7の配布ZIPやAutoCine本体とは別アプリである。
