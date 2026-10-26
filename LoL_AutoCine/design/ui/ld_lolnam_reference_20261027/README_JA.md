# AutoCine｜League Director・Lolnam UI比較研究
2026-10-27。比較対象はこの2ソフトのみ。研究提案と製品実装を分離する。

## Windowsで試す
ZIPをすべて展開し、`体験版を起動.cmd` または `windows/AutoCine_UI_Reference_v1.exe` をダブルクリックする。Pythonは不要。既存のWebView2 Runtimeと.NET Framework 4.6.2以降が必要。自動インストールは行わない。Windows x64の現在環境で実行確認した。別のクリーンPCでの配布試験は未実施。

- R1 Track Desk：League Directorの数値・多段キーの俯瞰を参考に、固定3領域＋中央previewを設計。
- R2 Shot Canvas：Lolnamの映像中心・timeline/curve切替を参考に、tool rail＋shotstripを設計。
- 両案にメイン・かんたん・詳細・カメラ・カーブ・色・素材・出力を用意。ライト/ダーク/Windows追従。

操作できるのは研究UIの状態編集。合成preview、FOV/回転の表示、数値、FOVキー/補間、scene選択、出力チェック、色のCSS近似、図形素材、Undo/Redo、JSON保存/読込。LoL/TargetLock/scan/GPU/ゲーム音/録画/実動画出力は未接続。ゲーム画面や他社素材をプレビューとして流用していない。

## 成果物
- `index.html`：自作画面20枚・比較図2枚・資料を閲覧するローカルギャラリー。
- `research/実画面比較_JA.md` / `SOURCES.json`：公式画像4枚と原文の確認範囲・出典。第三者画像は公開物に含めない。
- `specs/70機能比較_JA.md` / JSON：既存70機能との照合・各案の導線・不足/残件。
- `specs/WINDOWS_IMPLEMENTATION_JA.md`：Windows/WebView2と既存処理を接続する仕様。
- `specs/LAYOUT_TOKENS.json` / `COLOR_TOKENS.json`：寸法・色・配置の基準。
- `tests/`：85モデル試験、19DOMイベント試験、10自己テスト、20画面の実測結果。
- `demo/` / `windows/`：操作可能なHTML/CSS/JSとWindowsホスト、ソース、SDKのlicense/notice。

## 現行候補を維持
混合案A＝候補7メイン＋候補4詳細/素材/枠、簡単編集未決定。候補3/5/8も維持。今回のR1/R2は追加参考案であり、旧UI・UI29・比較アプリを置換しない。全候補の採点・順位付け・正式採用はしていない。

## 検証の限界
公式画面を確認したが参照2アプリは起動していない。デモは既存70機能を実行できる製品版ではない。テストには重複するモデルassertionがあり、総数を「114件の独立した実機E2E合格」としない。native pointer/keyboard/IME、OSファイルダイアログ、複数DPI、別PC、実バックエンドはNOT_RUN。P2残523、651暫定肖像形状、19原本制約と前工程の実LoL/GPU/音声/DPI残件はそのまま保持した。

保存commitとZIP再取得・実展開・hashの結果は、封印後の `SAVE_RECEIPT.json` に記録する（ZIP外）。
