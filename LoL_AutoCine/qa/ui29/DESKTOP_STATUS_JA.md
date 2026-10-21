# UI29 Windowsデスクトップ化の進捗（2026-10-22）

## 実装した起動経路

- `LoL_AutoCine_UI29.exe` はWebView2をアプリ内のウィンドウとして起動する。利用者がChrome、Edge、localhostを開く操作は不要。
- 内部では同じEXEの子プロセスに既存の `legacy_app.App` を1個起動し、ランダムトークン付き127.0.0.1の通信でUIから操作する。カメラ、FX、録画、音声の計算は従来のAppに委ねる。
- TkとWebView2のGUIループを別プロセスに置いた。ウィンドウを閉じるとAppの既存終了処理を呼ぶ。
- 従来の `LoL_AutoCine.exe` とBAT起動経路は維持。UI29用EXEは比較版として別名で同梱する。
- 表示前に隠れたTkキャンバスのレイアウト寸法を確定し、1×1扱いによるミラーの低解像度化を避ける。実際のLoL映像の画質・FPSは未測定。

## 検証済みと未検証を分ける

- ソース版WebView2の非表示ウィンドウで12候補の選択画面を確認。
- 凍結版UI29 EXEのバックエンド起動、29画面インベントリ読込、WebView2の12候補描画を確認。
- ポータブルZIPのファイル検査、EXEのバックエンド起動、Captureワーカー起動はビルドスクリプトで確認する。
- 29画面のうち新18画面と旧テストAの計19画面は部分実装。旧10画面は未実装のまま選択画面に明示し、押せる画像だけの画面として合格扱いしない。
- LoL実接続、BLUE/RED、TargetLock、FX、WGC、GPU/NVENC、ゲーム音、MP4書き出し、125% DPI、他PCのWebView2 Runtimeは未検証。友達への完成版としての配布判定は保留。

## 配布物

ビルドコマンドは `tools/build_portable_ui.py --audio-helper <既存MSVC製ヘルパー> --output <出力先>`。ZIPに現行9画面のEXE、UI29比較EXE、キャプチャワーカー、アセット、UI29のHTML/CSS/JS、監査インベントリを入れる。Microsoft Edge WebView2 Runtimeを必要とし、現時点では固定版ランタイムをZIPに同梱していない。WebView2がない友達のPCへのインストール不要性は未達。

監査の全29画面・12候補という目標、原画像の比較結果、未完成箇所は `STATUS_JA.md` に維持する。最終採用UIは未選定。
