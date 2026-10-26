# UI29 Windowsデスクトップ化の進捗（2026-10-24）

## 実装した起動経路

- `LoL_AutoCine_UI29.exe` はWebView2をアプリ内のウィンドウとして起動する。利用者がChrome、Edge、localhostを開く操作は不要。
- 内部では同じEXEの子プロセスに既存の `legacy_app.App` を1個起動し、ランダムトークン付き127.0.0.1の通信でUIから操作する。カメラ、FX、録画、音声の計算は従来のAppに委ねる。
- TkとWebView2のGUIループを別プロセスに置いた。ウィンドウを閉じるとAppの既存終了処理を呼ぶ。
- 従来の `LoL_AutoCine.exe` とBAT起動経路は維持。UI29用EXEは比較版として別名で同梱する。
- 表示前に隠れたTkキャンバスのレイアウト寸法を確定し、1×1扱いによるミラーの低解像度化を避ける。実際のLoL映像の画質・FPSは未測定。
- UI29の映像取得を固定100ms間隔から選択中の60/144Hz目標に連動する更新へ変更。Tk側の同一フレームはJPEGを再エンコードせず、ETag/304で重複転送を避ける。UIで実際に表示できた新規フレームFPSと、既存Tkミラーの合成表示FPSを別表示する。これは実機で144fpsを達成した証拠ではない。

## 検証済みと未検証を分ける

- ソース版WebView2の非表示ウィンドウで12候補の選択画面を確認。
- 凍結版UI29 EXEのバックエンド起動、29画面インベントリ読込、WebView2の12候補描画を確認。
- 実Appブリッジで全29画面のURLを開き、画面切替を一周した後もカメラ側・距離・登場アニメ・素材・テーマ設定が保持されることを確認（`local_bridge_probe.json`）。LoL実機操作は含まない。
- 2026-10-24の途中版EXE/ZIPを作成し、現行EXE、UI29バックエンド、Captureワーカー、非表示WebView2起動のスモークテストを通した。先行する29画面キャプチャは開発用Edgeで取得した。
- WindowsのWebView2撮影APIを使い、ソース版と凍結EXEの両方で全29画面の画像とDOM寸法を取得した。凍結版は `qa/ui29/frozen_webview2_offline/` に撮影結果、`comparison_frozen_webview2/` に原画像との差分・50%重ね・寸法結果を保存。スクロールバー起因の幅ずれ修正後、20画面は矩形許容内、9画面は要修正。矩形許容内は外観合格ではない。125% DPI確認は未実施。
- Microsoft公式ページからWebView2 Fixed Version 156.0.4314.42 x64 CABを取得し、CABのSHA-256 `CB4612CE79A62A0BE094301A72F73CF91BB250F5E83DC51886F66A083FC0694F` と展開した `msedgewebview2.exe` のMicrosoft署名を確認。Fixed Runtime同梱ZIPを制作し、展開後のウィンドウ起動が通った。実際のブラウザ子プロセスの実行パスがZIP同梱の `WebView2Fixed/msedgewebview2.exe` であることを確認。Runtime未導入PCでの起動は未検証。
- ポータブルZIPのファイル検査、EXEのバックエンド起動、Captureワーカー起動はビルドスクリプトで確認する。
- 29画面のうち新18画面と旧テストAの計19画面は部分実装。旧10画面は監査矩形に基づく編集可能なHTML/CSSとして再構成し、12候補すべてを選択可能にした。各候補は同じApp操作へ接続するが、外観と全操作は未合格。
- オフラインの原画像・実装画像・50%重ね・差分・寸法比較を29画面で取得。旧10画面はすべて矩形許容内だが、RGB差が大きい。`MEASURED` は画像合格ではない。
- LoL実接続、BLUE/RED、TargetLock、FX、WGC、GPU/NVENC、ゲーム音、MP4書き出し、125% DPI、他PCのWebView2 Runtimeは未検証。友達への完成版としての配布判定は保留。

## 配布物

ビルドコマンドは `tools/build_portable_ui.py --audio-helper <既存MSVC製ヘルパー> --output <出力先>`。ZIPに現行9画面のEXE、UI29比較EXE、キャプチャワーカー、アセット、UI29のHTML/CSS/JS、監査インベントリを入れる。公式Fixed Versionを展開済みなら `--webview2-fixed-folder <msedgewebview2.exeを含むフォルダ>` で同梱する。2026-10-24に同梱版ZIPを作り、展開後の3つのEXEスモークテストを通した。サイズ・SHA-256・再現手順は `PORTABLE_FIXED_JA.md`。Fixed Version v120以降のWindows 10ではフォルダのApp Container用読み取り・実行権限も要確認。Runtime未導入PCでのインストール不要性は未検証。

監査の全29画面・12候補という目標、原画像の比較結果、未完成箇所は `STATUS_JA.md` に維持する。最終採用UIは未選定。
