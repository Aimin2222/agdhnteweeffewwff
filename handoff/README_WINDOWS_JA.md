# v5.10.3 一括作成・応答停止対策版をWindowsへ取得

GitHubの `codex/lol-autocine-v5103-hangfix-handoff` ブランチで **Code → Download ZIP**。元v5.10.3と別フォルダへ展開し、**LoL_AutoCine/START.bat**を起動してください。mainへのマージ・環境Publishは不要です。

`handoff/LoL_AutoCine_v5.10.3_HangFix_Windows_Full.zip`は起動用完全版で、GitHubの **Download raw file**でも取得できます。差分ZIPは元Codex v5.10.3基準で、単体起動用ではありません。番号5.10.3は維持しますが、ファイル名のHangFixで対策版と区別できます。

接続/GPU表示の応答待ちをUIから分離しました。録画側の通信ロックとFFmpeg確認の待機中でもUIイベントを処理し、確認スレッドは各1本に制限。接続タイマーを重複させず、確認失敗から再確認できます。終了後も確認スレッドはTkオブジェクトを保持しません。一括作成は開始前の二重起動防止・開始準備中の表示・ALL_STAGE診断・周期スタック採取を追加しています。

全259テスト成功。実TkでAPI/GPU確認を待機させても全5シーン/GPU方針/ゲーム音/モンタージュを既存ワーカーへ渡し、画面更新/中止/二重クリック防止を確認。実ReplayAPIロック競合も再現しました。core全ファイル/GPU/録画/カメラ/LoL専用音声/Native Helper/START.batは前回とバイト一致です。

Windowsで報告された異常終了の同一原因は未確定です。まずGPU優先でチェック1シーン、次に全検出シーンを試し、開始準備中と進捗・中止の応答、色/音声/同期/対象追従/fpsを確認してください。再び落ちる場合は再起動前に同フォルダのCOLLECT_DIAGNOSTICS.batで診断をPC上へ保存してください。ログや動画を自動送信する機能は追加していません。

ソース243ファイル/Python88・全35ブランチをbundleへ保存。完全版241/差分5ファイル、SHA256付き。全旧ZIP/bundle/manifest/ブランチを保持。個人設定/プロジェクト/ログ/録画/音声/cacheは配布しません。

## ローカルGit開発

保存先が存在しないことを確認して実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5103-hangfix-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_HangFix_Handoff
git clone --branch integration/v5.10.3-hangfix LoL_AutoCine_HangFix_Handoff/handoff/LoL_AutoCine_v5.10.3_HangFix_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git branch stable/v5.8.5 origin/stable/v5.8.5
git branch feature/gpu-engine origin/feature/gpu-engine
git branch feature/ui-dispatch-hangfix-v5103 origin/feature/ui-dispatch-hangfix-v5103
git branch integration/v5.10.3 origin/integration/v5.10.3
git status --short
git branch --all
```

全35ブランチをorigin/*へ復元します。cloneのoriginはPC上のbundleでGitHubではありません。UIはfeature/ui-dispatch-hangfix-v5103、GPUはfeature/gpu-engine。共有ガードにはdocs/CODEX_SHARED_API_REVIEW_v5.10.1.jsonを使います。元v5.10.3はintegration/v5.10.3として残しています。

詳細はLoL_AutoCine/docs/CODEX_ALL_SCENES_HANG_FIX_v5.10.3_JA.md、Git状態・実変更一覧はSOURCE_GIT_REPORT_JA.md、検証はVERIFICATION_v5.10.3_HangFix.jsonを参照してください。
