# LoL AutoCine v5.10.0をWindowsへ取得

GitHubの `codex/lol-autocine-v5100-handoff` ブランチで **Code → Download ZIP**。旧版は別フォルダへ保管し、新フォルダへ展開して **LoL_AutoCine/START.bat** を起動する。

`handoff/LoL_AutoCine_v5.10.0_Windows_Full.zip` は起動用完全版。GitHubでこのファイルを開いて **Download raw file** でも取得できる。`Codex_MergeChanges.zip` は前回v5.9.9 ChampionPairFix基準の統合用差分で単体起動用ではない。Windows取得にmainマージ・環境Publishは不要。

## ローカルGit開発

保存先がまだ存在しないことを確認して実行:

```sh
git clone --single-branch --branch codex/lol-autocine-v5100-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.10.0 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.10.0_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

全29ブランチがorigin/*へ復元される。UIはfeature/ui-killframe-v5100、GPUはfeature/gpu-engine。このcloneのoriginはPC上のbundleでGitHubではない。

## 保存と検証

- ソース226ファイル/Python78ファイル・全29ブランチ、完全版224ファイルと差分25ファイルのZIP、旧版bundle/manifest/ZIP/ハッシュを保存。差分適用後の全226ファイル一致を確認。
- ホイール誤操作防止、左端シーンチェック、実ナビ/参考URL、枠色/発光/枠幅/6マーク、エンコード選択/実績表示/設定保存を統合。
- 受領GPUファイルの古い版への上書きを避け、effect_eventsの実時間補正、shortest=0、曖昧な名前の省略、Fiddlesticks正式ID、取得重複防止、同時キルの最新ペアを保持。共有jobsはエンコード方針受け渡しのみ。camera/音声/Native Helper/GPUフィルター本体は前回とバイト一致。
- NVENC録画は開始前プローブ、完成素材のNVENC失敗はlibx264へ一度再試行。途中録画失敗は中断。失敗/タイムアウトを成功・GPU実行確認済みと表示しない。
- pytest209件、実Tk再起動の14設定、UI→worker→モックAPI、実FFmpegの4装飾/4位置・2ペア・AAC完全一致・AV末尾差0を確認。スマートON/OFF各2クリップ＋モンタージュは1080p/60fps・音声あり。実NVENC拒否→CPU録画/時間補正/FX再試行も確認。
- Linux CPU・合成肖像・モックAPIでの試験。Windows/実LoL/実GPU/NVENC成功/Native録音は未確認。公式Data Dragonの実取得は現在のクラウドプロキシ403で未確認。Bloom/DOFのGPU高速化は未実装。

## Windowsで確認すること

10人取得→対象固定→スキャン。装飾OFF/4装飾、異なる敵の連続キル、スロー時表示、色/発光/枠幅/マークと保存再起動、ホイール/シーンチェック/ナビ、色・LoLのみ音声・同期・HUD・対象追従・fpsを確認。CPU優先と自動/GPU優先を比べ、実エンコーダとエフェクト経路を別々に確認する。

初回肖像取得は `ddragon.leagueoflegends.com` への接続が必要。キャッシュは `%LOCALAPPDATA%/LoL_AutoCine/champion_icons`。ネットなしでは `assets/champion_icons/<ChampionID>.png` へ公式PNGを置ける。情報/画像欠落時は装飾を省略する。

詳細はLoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.10.0_JA.md。Git状態/実差分はSOURCE_GIT_REPORT_JA.md、ハッシュ/枝一覧はMANIFEST.jsonとSHA256SUMS.txt。比較先は前回codex/lol-autocine-v599-champion-pair-handoff。mainへマージしない。
