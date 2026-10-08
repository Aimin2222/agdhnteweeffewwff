# LoL AutoCine v5.9.7をWindowsへ取得する

GitHubの `codex/lol-autocine-v597-handoff` ブランチで **Code → Download ZIP**。新しいフォルダへ展開し、**LoL_AutoCine/START.bat**で起動してください。このフォルダは完全版です。添付の差分ZIP単体は起動用ではありません。旧版は別フォルダに保管してください。
Windowsへの取得にmainのマージや環境Publishは不要です。チャットの生成ZIPリンクは使用しません。

## Git履歴を含むローカル開発

Gitがある場合、保存先が存在しないことを確認して次をPowerShellまたはGit Bashで実行:

```sh
git clone --single-branch --branch codex/lol-autocine-v597-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.9.7 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.9.7_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

元の開発Gitの全21ブランチがorigin/*へ復元されます。UIはfeature/ui-studio-v597、GPUはfeature/gpu-engine、統合はintegration/v5.9.7。このcloneのoriginはPC上のbundleです。GitHubへ開発内容を同期する場合はAutoCine用リポジトリを別途指定してください。ZIP取得後も同じbundleからcloneできます。

## 保存・確認

- 191ソースファイルと全21ブランチの完全履歴。旧bundle/manifestも保持。SHA256とコミットはMANIFEST.json、元Gitのstatus/log/remote/実差分一覧はSOURCE_GIT_REPORT_JA.md。
- 上段3ペイン＋下段全幅エディタ、日本語表示、カメラグラフ・DOF概念図、通常/白い閃光/暗転のモンタージュ設定を統合。
- GPU側既存修正・位置引数互換性を維持。通常連結は従来経路。追加演出はCPUフィルター＋映像再エンコードで、音声はcopy、失敗時は元連結に復旧。GPU効果の高速化は未実装。
- pytest115件成功。実FFmpegの1080p/60fpsと640x360/144fpsでカラー、元fps、音声AAC完全一致を確認。モックReplay APIの既存通常/シーン別経路でも1080p/60fpsの2クリップ＋モンタージュを生成。
- UI実プレビュー、HUD指定・復元、チェックした2シーンだけ一括適用、Undo/Redo、自動保存も確認。
- Windows/実LoL/GTX 1070 Ti/Native録音/実NVENCは未検証。合成音声の成功とは区別する。旧版を残して実機で上記項目を確認してください。

詳細: LoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.9.7_JA.md。
個人設定・プロジェクト・録画・音声・.venvは含みません。HUDの名前非表示はLoL側設定が必要です。
取得用比較ブランチはcodex/lol-autocine-v596-handoff。既存PRとmainを保持し、Draft PR #7へ保存しました。
https://github.com/Aimin2222/agdhnteweeffewwff/pull/7

GitHubから別フォルダへ復元し、191ファイルと全21ブランチの一致、GUIと新モンタージュ回帰41テスト、共有変更ガードの成功を確認しました。
