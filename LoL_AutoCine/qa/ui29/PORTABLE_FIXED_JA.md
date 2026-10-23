# UI29ポータブルZIP（WebView2 Fixed Version同梱）

- 作成日: 2026-10-24
- AutoCineソースコミット: `c7c506f05502213cfb41a88bf08401f189fac076`
- ローカルZIP: `builds/ui29-desktop-20261024-e9ab91f/LoL_AutoCine_UI_Comparison_Portable.zip`（このリポジトリの親作業フォルダ内）
- ZIPサイズ: 2,061,502,309バイト
- ZIP SHA-256: `AC34722C54D199C0EE548C0620EF43E3749EB50EDAB7CF2863FD96FA2D78D0E3`
- ZIP内の `BUILD_INFO.json` にソースコミット、画面数、同梱Runtimeとネイティブ音声ヘルパーのハッシュを記録した。

## 同梱したMicrosoft Runtime

- 公式配布元: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
- Fixed Version: `156.0.4314.42`、x64
- 配布元ページに埋め込まれたCABのURLから取得。CAB SHA-256: `CB4612CE79A62A0BE094301A72F73CF91BB250F5E83DC51886F66A083FC0694F`
- CAB形式を確認し、Windowsの `expand.exe` で257ファイルを展開。`msedgewebview2.exe` のAuthenticodeは有効なMicrosoft Corporation署名。
- 同梱先: `LoL_AutoCine/WebView2Fixed/`。pywebview 6.2.1の `WEBVIEW2_RUNTIME_PATH` にこのフォルダを指定する。
- Microsoft Defender SmartScreenとMicrosoftプライバシーへの案内をZIP内 `README_TEST_JA.txt` に記載。Fixed Versionの更新は自動ではない。

## 今回の確認

- ビルドスクリプトのZIP CRC、必要ファイル検査、現行EXE・UI29バックエンド・キャプチャワーカーのスモーク: PASS。
- ZIPを新規フォルダへ展開後、現行EXE、UI29の12候補選択ウィンドウ、キャプチャワーカーのスモーク: すべて終了コード0。
- 同梱版でWebView2を起動し、子プロセスの実行パスが `WebView2Fixed/msedgewebview2.exe` であることを確認。
- 凍結EXEの全29画面撮影・原画像との差分: `FROZEN_REVIEW_JA.md`。矩形許容内16、要修正13。外観合格0。
- LoLリプレイ実接続、WGCミラー実測FPS、GPU/NVENC、ゲーム音声、MP4書き出し、およびWebView2 Runtime未導入PC: **未検証**。このZIPは完成合格版ではない。

巨大なZIPとMicrosoftのCABはGitにはコミットしていない。コード・29画面の証跡・再現手順をUI専用ブランチへ保存し、PR #51はドラフトのまま維持する。
