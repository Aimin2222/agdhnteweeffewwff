# LoL AutoCine v5.9.6をWindowsへ取得する

GitHubの `codex/lol-autocine-v596-handoff` ブランチで **Code → Download ZIP** を選び、Windows PCへ展開してください。
その中の **LoL_AutoCineフォルダ** が完全なプロジェクトです。旧版は別フォルダに保管して、既存の `START.bat` で起動してください。
チャットの生成ZIPリンクは使用しません。mainへのマージやクラウド環境設定の操作は、Windowsでの取得には不要です。

## Git履歴と担当ブランチを復元する

Gitがある場合、以下をPowerShellまたはGit Bashで実行できます。保存先が既にある場合は別の名前を使ってください。

```sh
git clone --single-branch --branch codex/lol-autocine-v596-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.9.6 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.9.6_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

`LoL_AutoCine_Dev` が元の開発Gitです。全19ブランチがorigin/*にも復元されます。
UI担当はfeature/ui-hud-batch-v596、GPU担当はfeature/gpu-engine、統合版はintegration/v5.9.6です。
このcloneのoriginはPC上のbundleです。GitHubへ同期する場合はAutoCine用のリポジトリを別途指定してください。
ZIPを先に取得した場合も、展開フォルダの同じbundleからcloneできます。
取得用リポジトリ自体を開発する場合は、作業ディレクトリがLoL_AutoCine/になる点に注意してください。

## 保存内容と今回の確認

- 179ソースファイルと全19ブランチのbundleを保存。アップロードされた差分ZIP単体ではなく、こちらのLoL_AutoCine/が完全なプロジェクトです。
- 元のGit状態・変更一覧はSOURCE_GIT_REPORT_JA.md、コミット・SHA256はMANIFEST.json。過去bundle/manifestも保持。
- HUD3択の共通設定と再起動復元、チェックしたシーンへの未保存設定の一括適用を統合。一括変更は1 Undoで戻せます。
- 名前非表示そのものはLoL側の設定が必要。AutoCineが自動で消すものではありません。
- 100テスト成功。モックAPIでHPバー中心のフラグと終了時のHUD復元、一括対象限定・Undo/Redo・自動保存・実プレビューを確認。
- 共有jobsの変更は開始ログとコメントのみ。GPU・録音・カメラ・エンコード本体を維持。GPU高速化自体は未実装。
- 個人設定・プロジェクト・ログ・録画・音声・.venvは含めません。Windows/実LoL/GPU/Native録音は今回未検証。
- 今回はFFmpeg通し出力を再実行していません。以前の合成出力検証は過去記録を参照してください。

詳細はLoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.9.6_JA.mdへ保存。
前回のcodex/lol-autocine-v595-handoffとの比較用Draft PRを作成します。既存PR #1〜#5を保持し、mainへマージしません。
