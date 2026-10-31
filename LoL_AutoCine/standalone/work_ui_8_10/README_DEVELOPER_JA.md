# Work新UI 3案の独立体験版

このフォルダだけで起動・ビルドするWindowsデスクトップアプリです。AutoCine本体や候補1〜7比較版をimportせず、LoL API、録画、GPU、音声、MP4出力も呼びません。`launcher.py` が127.0.0.1の一時ポートで同梱Web素材を配信し、アプリ内のWebView2に表示します。外部ブラウザは不要です。

## 開発者向け対応表

| 友達向け表示 | Work内部名 | レイアウト |
|---|---|---|
| 候補8 | P1 Focus | `hybrid` |
| 候補9 | P2 Guided | `flow` |
| 候補10 | P3 Collection | `library` |

Work正本はコミット `6ab57afee2e236e50833c6e15022484fb84b79e7` の `research/integrated_20261022/v4_continuation_20261026/ui/` です。`web/ui.css`・`web/ui.js`・画像assetsは正本の複製です。`web/experience.js` と `web/experience.css` は番号表示と体験版の操作性だけを追加します。正本ファイルは変更しません。

## 起動・検査

```powershell
python standalone/work_ui_8_10/launcher.py
python standalone/work_ui_8_10/launcher.py --qa-interaction --output qa/work_ui_8_10/interaction.json
python standalone/work_ui_8_10/launcher.py --capture-all --output qa/work_ui_8_10/windows_captures
python standalone/work_ui_8_10/compare_images.py --captures qa/work_ui_8_10/windows_captures --output qa/work_ui_8_10/comparison
```

配布物は `build_portable.py` で生成します。公式WebView2 Fixed Runtime x64を同梱し、EXEと同じフォルダに配置します。画面は見本データで動き、実LoL機能へ接続されたようには表示しません。

元画像があるのは候補8の主要8画面、候補9の3画面、候補10のライブラリ画面、ポップアップ12画面の計24画面です。候補9・10の詳細編集画面は原画像がなく、体験用に同じデザイン言語で補完しました。
