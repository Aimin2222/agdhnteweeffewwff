# 29画面の比較資料

`index.json` と各画面の `result.json` に29画面の寸法・RGB差・検証状態を記録する。`MEASURED` は監査矩形との位置比較が済んだ意味で、外観合格を意味しない。LoL実機動作は全画面 `NOT_RUN`。

- 原画像：`../../../design/ui/implementation_audit_29_20261021/references/` の各監査画像
- 実装画像：旧10画面は `../live_legacy_offline/<ID>.png`、既存19画面は `../live_offline/<ID>.png`
- 旧10画面の50%重ね／絶対差分：このフォルダの `<ID>/overlay_50.png`／`<ID>/absolute_difference.png`
- 既存19画面の50%重ね／絶対差分：`../live_offline/review/<ID>/`

画面内のLoLプレビューはリプレイ未接続のため空欄で撮影した。撮影に開発用Edgeを用いたが、配布アプリの画面はWindows内蔵WebView2で表示する。最終の画像審査はWebView2アプリ実画面で再実行する。
