# LoL AutoCine v5.9.9 ChampionPairFixをWindowsへ取得

保存先: [Draft PR #11](https://github.com/Aimin2222/agdhnteweeffewwff/pull/11)。mainへマージしていません。

GitHubの `codex/lol-autocine-v599-champion-pair-handoff` ブランチで **Code → Download ZIP**。旧版は別フォルダへ保管し、新しいフォルダへ展開して **LoL_AutoCine/START.bat** を起動してください。

`handoff/LoL_AutoCine_v5.9.9_ChampionPairFix_Windows_Full.zip` は起動用完全版です。GitHubでこのファイルを開いて **Download raw file** でも取得できます。`ChampionPairFix_Codex_MergeChanges.zip` は前回v5.9.9基準の統合用差分で単体起動用ではありません。Windows取得にmainマージ・環境Publishは不要です。

## ローカルGit開発

保存先がまだ存在しないことを確認して実行:

```sh
git clone --single-branch --branch codex/lol-autocine-v599-champion-pair-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.9.9-champion-pair LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.9.9_ChampionPairFix_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

全27ブランチがorigin/*へ復元されます。UIはfeature/ui-champion-pair-v599、GPUはfeature/gpu-engine。このcloneのoriginはPC上のbundleでGitHubではありません。

## 保存と検証

- ソース218ファイル・全27ブランチ、検査済み完全版/差分ZIP、旧版bundle/manifest/ZIP/チェックサムを保持。完全版ZIPは診断説明/placeholder2件を除く216ファイル。
- 文字付き装飾をチャンピオン2肖像へ変更し、キルごとに相手画像を切り替える。画像/情報欠落・同名曖昧時は装飾を省略し、推測しない。
- 受領フルファイルは上書きせず、前回のスロー時イベント実時間補正、PNGで動画末尾を打ち切らない修正、v5.9.9表示、旧位置引数互換を保持。camera/jobs/音声/録画/GPU経路/Native Helperは前回とバイト一致。
- pytest182件成功。実Tk/worker/モックAPIの対象固定・HUD復元・Undo/Redo・保存・一覧スナップショット、実Gitガードを確認。
- 実FFmpegで4装飾/4位置・2キルの相手色切替、1080p/60fps、通常版とのAAC完全一致・AV末尾差0。タイトル/BGMと複数PNG、GPU失敗模擬CPU再試行も確認。肖像はテスト用合成画像です。
- 公式Data Dragonへの実取得はクラウドのプロキシで403となり未検証。模擬通信/ローカルPNG/オフラインキャッシュは確認。Windows/実LoL/実GPU/Native録音/実NVENCは未検証。装飾はCPU処理でGPU高速化ではありません。

## Windowsで確認すること

10人取得→対象固定→スキャン後に通常OFFと4装飾、異なる敵の連続キル、スロー時表示、位置/サイズ/秒数/濃さと保存復元、カラー・LoLのみ音声・HUD・対象追従・fpsを確認してください。
画像の初回取得は `ddragon.leagueoflegends.com` への接続が必要です。キャッシュは `%LOCALAPPDATA%/LoL_AutoCine/champion_icons`。ネットなしでは `assets/champion_icons/<ChampionID>.png` に公式PNGを置けます。未取得時は該当装飾を省略します。

詳細はLoL_AutoCine/docs/CODEX_CHAMPION_PAIR_RESULTS_v5.9.9_JA.md。Git状態・実差分はSOURCE_GIT_REPORT_JA.md、ハッシュ/枝一覧はMANIFEST.jsonとSHA256SUMS.txt。比較先は前回codex/lol-autocine-v599-handoff。mainへマージしません。

## クラウド復元の確認

GitHub保存済みbundleから別フォルダへソース218ファイルと全27ローカルブランチを復元し、一致を確認しました。依存・構文・Tk/Xvfb・共有ガード、代表76テストが成功。既存フォルダへのinstaller再実行も成功し、未コミットの変更はありません。新しいクラウドタスクの起動そのものは別の確認になります。

完全版/差分ZIPは保存済みソースに一致します。単体GitとGitHub取得用構成の双方でパッケージ作成を確認し、差分パッチ適用後の218ソース一致も確認しました。

公式画像の接続許可は環境設定ドラフトへddragon.leagueoflegends.comを追加します。設定保存は現在の403解消や実取得成功を意味しません。Windowsの取得/使用に環境Publishは不要です。
