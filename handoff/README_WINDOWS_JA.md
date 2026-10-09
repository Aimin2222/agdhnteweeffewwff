# LoL AutoCine v5.9.9をWindowsへ取得する

保存先: [Draft PR #10](https://github.com/Aimin2222/agdhnteweeffewwff/pull/10)。mainへマージしていません。

GitHubの `codex/lol-autocine-v599-handoff` ブランチで **Code → Download ZIP**。旧版を別フォルダに保管し、新しいフォルダへ展開して **LoL_AutoCine/START.bat** を起動してください。LoL_AutoCine/は完全版です。添付の差分ZIP単体は起動用ではありません。
Windowsへの取得にmainのマージや環境Publishは不要です。チャットの生成ZIPリンクは使用しません。

`handoff/LoL_AutoCine_v5.9.9_Windows_Full.zip` は起動用の完全版ZIPです。GitHubでそのファイルを開いて **Download raw file** でも取得できます。`LoL_AutoCine_v5.9.9_Codex_MergeChanges.zip` は統合用差分なので、単体で起動しないでください。完全版ZIPは診断フォルダの説明・プレースホルダー2件を除く211ファイル、取得用LoL_AutoCine/は213ファイルです。SHA256SUMS.txtでZIPのハッシュを確認できます。

## Git履歴を含むローカル開発

保存先がまだ存在しないことを確認してPowerShell/Git Bashで実行:

```sh
git clone --single-branch --branch codex/lol-autocine-v599-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.9.9 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.9.9_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

全25ブランチがorigin/*へ復元されます。UIはfeature/ui-killbadges-v599、GPUはfeature/gpu-engine、統合はintegration/v5.9.9。このcloneのoriginはPC上のbundleです。GitHubへ開発内容を同期する場合はAutoCine用リポジトリを別途指定してください。ZIP取得後も同じbundleからcloneできます。

## 保存と確認

- 完全ソース213ファイルと全25ブランチの履歴。旧bundle/manifestも保持。コミット/SHA256はMANIFEST.json、元Git状態/log/remote/変更一覧はSOURCE_GIT_REPORT_JA.md。
- キル装飾4種、位置・大きさ・長さ・濃さ、シーン別上書き、任意のスマート構図、明示スマート時だけの自動選別を統合。通常計画と手動順序を保持。
- 共有camera/jobsは小さい差分をGPU担当でレビュー。追加設定を末尾に置いて旧位置引数互換を保持。録画中の既存playback観測からスロー再生を含む動画時刻を補間し、追加API呼出しなしで装飾・強調へ渡す。
- 受領PNGのshortest指定が映像・音声末尾を短くする問題を実出力で再現し、装飾入力で動画長を打ち切らないよう修正。
- pytest162件成功。実Tk/worker/モックAPIの対象固定・HUD復元・Undo/Redo・JSON保存・追加7設定の再起動復元、実Gitの旧承認拒否と新承認成功を確認。
- 実FFmpegで4装飾×4位置の1080p/60fps出力、通常版とのAAC完全一致、末尾長差0を確認。タイトル＋装飾＋ゲーム音＋BGM、GPU失敗を模擬したCPU再試行も成功。スマート/従来双方で2クリップ＋モンタージュを生成。
- 装飾overlayはCPU処理でありGPU高速化ではない。Windows/実LoL/GTX 1070 Ti/Native録音/実NVENCは未検証。合成音声・モック成功と区別する。

実機ではまず装飾OFF/構図OFFの通常編集、その後各装飾・スマート構図、通常への切替、手動順序・個別設定優先・Undo/Redo・保存復元、スロー時のキル表示時刻、カラー・LoLのみ音声・HUD・対象追従・fpsを確認してください。HUDの名前非表示はLoL側の設定が必要です。
詳細: LoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.9.9_JA.md。
個人設定・プロジェクト・ログ・録画・音声・.venvは含みません。
比較先はcodex/lol-autocine-v598-handoff。既存PRとmainを保持し、新しいDraft PRへ保存します。

## クラウド復元の確認

GitHubに保存したbundleから別フォルダへソース213ファイルと全25ローカルブランチを復元し、一致を確認しました。依存・構文・Tk/Xvfb・共有ガード、代表58テストが成功。既存フォルダへのセットアップ再実行も成功し、未コミットの変更はありません。新しいクラウドタスクの起動そのものは別の確認になります。

完全版/差分ZIPは保存済みソースに一致します。単体Git・GitHub取得用構成の双方でパッケージ作成を確認し、差分適用後の213ファイル一致も確認しました。受領パッチを記録したdocs/v599_changes.patchの文脈行には元の空白を保持しているため、外側のパッチ適用で17行の空白警告が出ます。適用検査と内容一致は成功し、アプリコードの空白検査も成功しています。
