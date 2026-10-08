# LoL AutoCine v5.9.5をWindowsへ取得する

GitHubの `codex/lol-autocine-v595-handoff` ブランチで **Code → Download ZIP** を選び、Windows PCへ展開してください。
その中の **LoL_AutoCineフォルダ** が完全なプロジェクトです。旧版は別フォルダに保管して、既存の `START.bat` で起動してください。
チャットの生成ZIPリンクは使用しません。mainへのマージやクラウド環境設定の操作は、Windowsでの取得には不要です。

## Git履歴と担当ブランチを復元する

Gitがある場合、以下をPowerShellまたはGit Bashで実行できます。保存先が既にある場合は別の名前を使ってください。

```sh
git clone --single-branch --branch codex/lol-autocine-v595-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.9.5 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.9.5_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

`LoL_AutoCine_Dev` が元の開発Gitです。全17ブランチがorigin/*にも復元されます。
UI担当はfeature/ui-workspace-v595、GPU担当はfeature/gpu-engine、統合版はintegration/v5.9.5です。
このcloneのoriginはPC上のbundleです。GitHubへ同期する場合はAutoCine用のリポジトリを別途指定してください。
ZIPを先に取得した場合も、展開フォルダの同じbundleからcloneできます。
取得用リポジトリ自体を開発する場合は、作業ディレクトリがLoL_AutoCine/になる点に注意してください。

## 保存内容と今回の確認

- 元ソースの追跡済み169ファイルと全17ブランチを保存。Git状態と変更一覧はSOURCE_GIT_REPORT_JA.md、コミットとSHA256はMANIFEST.json。
- 過去のbundleとmanifestを保持。個人設定、ログ、録画、音声、.venvは含めません。
- UIワークスペースと未保存設定のコピー・貼り付けを統合。かんたん編集に戻る際の右側出力設定の表示漏れだけ3行修正。
- 93テスト成功。実Tkのコピー・貼り付け・Undo/Redo・自動保存・4区分切替と、モックAPIまでのプレビューを確認。
- core/とui/の27ファイル、録画/音声/GPU/カメラ処理を維持。GPU高速化そのものは未実装。
- 今回はFFmpeg通し出力を再実行せず、前回v5.9.4の結果を保持。Windows・実LoL・GPU・専用録音は今回未検証。
- ウィンドウタイトルも受領版でv5.9.5へ更新されています。

詳細はLoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.9.5_JA.mdを参照してください。
前回の取得用codex/lol-autocine-v594-handoffとの比較用に新しいDraft PRを作成します。
既存PR #1〜#4を保持し、mainへはマージしません。
