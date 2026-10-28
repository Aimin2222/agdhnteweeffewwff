# 7候補の番号表示（開発者向け）

この対応表は開発・検証用です。友達に渡すZIPには同梱しません。比較版の画面には番号だけを表示します。

| 表示 | 内部グループ | 開始画面ID | 元の候補名 |
|---|---|---|---|
| 候補1 | `testB` | `T-B-M` | 旧テストB カメラ・FX |
| 候補2 | `legacy03` | `L03-N` | 旧案3 ハイブリッド |
| 候補3 | `testA` | `T-A-M` | 旧テストA 現行整理 |
| 候補4 | `legacy06` | `L06-L` | 旧案6 ライブラリ・編集 |
| 候補5 | `researchE` | `R-E-main` | 新E Flow |
| 候補6 | `legacy02` | `L02-M` | 旧案2 標準編集 |
| 候補7 | `legacy05` | `L05-M` | 旧案5 ウィザード |

## 検証

- UI/APIの対象テスト: 22件、追加のサブテスト24件が通過。
- Windows WebView2のソース実画面: 起動時候補一覧と対象16画面を撮影。各画面の右端タブ、Ctrl+Shift+Uの切替一覧、現在候補、ページタイトル、画面本文で旧候補名が表示されないことを検査。証拠は `numbered_source_all_v2/`。
- 最終配布EXE: `numbered_frozen_all_final/` の16画面すべてで番号表示を検査。`numbered_frozen_flow_final/` では7候補すべてのメイン→詳細→素材→メインと設定保持が通過。
- 元画像のない補完画面: `numbered_frozen_derived/` の詳細3画面・素材4画面も最終配布EXEで撮影し、番号表示と戻る操作を確認。旧案3の詳細画面は元画像のある `L03-D` として16画面の検査に含まれます。
- ZIP内の `README_TEST_JA.txt` と `TEST_GUIDE_JA.md` には候補1〜7のみを掲載し、旧候補名の一致件数は0。開発者向けのこの対応表はZIPに同梱していません。
- 内部ID、元デザイン原本、他のAutoCine処理は変更していません。
- LoL接続、録画、GPU/NVENC、音声、MP4出力は今回の表示名変更では再検証していません。

## 配布物

- WindowsポータブルZIP: `builds/ui7-numbered-20261026-439482f/LoL_AutoCine_UI_Comparison_Portable.zip`
- 起動: 展開後に `LoL_AutoCine/LoL_AutoCine_UI29.exe` を実行。
- ZIP容量: 1,704,280,528 bytes。
- ZIP SHA-256: `99328C9EB4F462E08B46359DAF67B3B681C05585F2B931DBA5A7AEC395B63318`
- 実装・ビルド元コミット: `439482f`。


取得元：https://github.com/Aimin2222/agdhnteweeffewwff/blob/ee700835efe25c1aa65670d73e57f1fd9373bac2/LoL_AutoCine/qa/ui7_20261026/NUMBERING_JA.md
これはPR側の過去の試験報告です。今回のWork再試験結果ではありません。
