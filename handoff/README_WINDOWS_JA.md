# LoL AutoCine v5.9.8をWindowsへ取得する

GitHubの `codex/lol-autocine-v598-handoff` ブランチで **Code → Download ZIP**。旧版を別フォルダに保管し、新しいフォルダへ展開して **LoL_AutoCine/START.bat** を起動してください。LoL_AutoCine/は完全版です。添付の差分ZIP単体は起動用ではありません。
Windowsへの取得にmainのマージや環境Publishは不要です。チャットの生成ZIPリンクは使用しません。

## Git履歴を含むローカル開発

保存先がまだ存在しないことを確認してPowerShell/Git Bashで実行:

```sh
git clone --single-branch --branch codex/lol-autocine-v598-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.9.8 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.9.8_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

全23ブランチがorigin/*へ復元されます。UIはfeature/ui-highlight-v598、GPUはfeature/gpu-engine、統合はintegration/v5.9.8。このcloneのoriginはPC上のbundleです。GitHubへ開発内容を同期する場合はAutoCine用リポジトリを別途指定してください。ZIP取得後も同じbundleからcloneできます。

## 保存と確認

- 完全ソース201ファイルと全23ブランチの履歴。旧bundle/manifestも保持。コミット/SHA256はMANIFEST.json、元Git状態/log/remote/変更一覧はSOURCE_GIT_REPORT_JA.md。
- スマート演出4種、5点カメラキー、短いキル強調、強度スライダー、全シーン推薦、旧JSON互換を統合。
- 既存GPU修正と位置引数互換性を保持。通常編集へのスマート計画の持越しを修正。個別保存済み設定を保持し、明示的な全シーン推薦はUndoで復元できます。
- pytest133件成功。モックAPIで実プレビュー・HUD復元・対象固定、一括適用、推薦Undo/Redo、強調値保存を確認。
- 実FFmpegの1080p/60fpsで2イベントの短い強調、カラー、通常版とのAAC完全一致を確認。スマート/従来の双方で2クリップ＋モンタージュを生成。
- 新アクセントはCPUフィルターでありGPU高速化ではありません。Windows/実LoL/GTX 1070 Ti/Native録音/実NVENCは未検証。合成音声の成功と区別します。

実機では通常→スマート4種→通常の切替、個別設定優先、全推薦Undo/Redo、保存復元、チェック2シーンのカラー・LoLのみ音声・HUD・対象追従・fpsを確認してください。HUDの名前非表示はLoL側の設定が必要です。
詳細: LoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.9.8_JA.md。
個人設定・プロジェクト・ログ・録画・音声・.venvは含みません。
比較先はcodex/lol-autocine-v597-handoff。既存PRとmainを保持し、Draft PR #8へ保存しました。
https://github.com/Aimin2222/agdhnteweeffewwff/pull/8

GitHubから別フォルダへ復元し、201ファイルと全23ブランチの一致、GUI/新旧演出56テスト、共有変更ガードの成功を確認しました。
