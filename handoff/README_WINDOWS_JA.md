# LoL AutoCine v5.10.1をWindowsへ取得

GitHubの `codex/lol-autocine-v5101-handoff` ブランチで **Code → Download ZIP**。旧v5.10.0は別フォルダへ保管し、新フォルダへ展開して **LoL_AutoCine/START.bat** を起動する。Windows取得にmainマージ・環境Publishは不要。

`handoff/LoL_AutoCine_v5.10.1_Windows_Full.zip` は起動用完全版。GitHubで開いて **Download raw file** でも取得できる。Codex_MergeChanges.zipは前回v5.10.0基準の統合用差分で単体起動用ではない。

## 保存した変更と確認

- ホイールの値変更防止を動的コントロールへ拡張し、シーンのチェック/全選択/全解除でもスクロール位置・選択を保持する。
- WGCの最初の録画に自動プレロールを追加。API時刻の進行とフレーム更新を確認し、カメラ反映後の新フレームを待つ。失敗/停止では録画前に中断、新リプレイ/再接続は再準備する。
- 受領jobsフルファイルを上書きせず、effect_events実時間補正とsmart_highlight_enabled条件、NVENC/CPU方針、LoL専用音声/TargetLockを保持。GPU処理/エンコード/カメラ/音声/Native Helperは前回とバイト一致。
- pytest229件成功。実Tkのホイール・実パネルスクロール・ネイティブドロップダウン選択・シーン位置・新起動/再接続と、停止/失敗/古いフレームの防止を確認。
- 実FFmpeg・模擬WGC・モックHTTP Replay APIで初回だけ準備し、スマートON/OFF各2クリップ＋モンタージュへ1080p/60fps・カラー/音声ありで出力。手動逆順/対象/Template/録画時刻転送を保持。Windows Native Captureを実行した試験ではない。
- ソース233ファイル/Python81ファイル・全31ブランチ、完全版231/差分13ファイルのZIPとSHA256を保持。差分適用後233ソースの一致、未追跡個人ファイル除外を確認。旧ZIP/bundle/manifest/ハッシュは残す。

## Windowsで確認すること

スキャン後、手動プレビューを一度も再生せず、チェックした最初の1クリップを作成する。冒頭がネクサスでなく現場か、対象追従/キル時刻/色/LoLのみ音声/同期/fpsを確認。続けて2クリップ/モンタージュ、ホイール、シーンチェック位置、準備中の停止、再接続/新リプレイを確認する。

フレーム更新とAPI時刻はゲーム映像内容の画像認識ではない。Windows/実LoLのネクサス問題解消、実GPU/NVENC成功、Native音声は未確認。Bloom/DOFのGPU高速化は未実装。公式画像の実取得は現在クラウドプロキシ403で未確認。未取得時はペア装飾を省略する。Windows公式画像キャッシュは `%LOCALAPPDATA%/LoL_AutoCine/champion_icons`。手動 `assets/champion_icons/<ChampionID>.png` も使える。

## ローカルGit開発

保存先が存在しないことを確認して実行:

```sh
git clone --single-branch --branch codex/lol-autocine-v5101-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Handoff
git clone --branch integration/v5.10.1 LoL_AutoCine_Handoff/handoff/LoL_AutoCine_v5.10.1_all_branches.bundle LoL_AutoCine_Dev
cd LoL_AutoCine_Dev
git status --short
git branch --all
```

全31ブランチがorigin/*へ復元される。UIはfeature/ui-scroll-v5101、GPUはfeature/gpu-engine。このcloneのoriginはPC上のbundleでGitHubではない。

詳細はLoL_AutoCine/docs/CODEX_INTEGRATION_RESULTS_v5.10.1_JA.md。Git状態と元v5.8.5/前回v5.10.0からの実変更一覧はSOURCE_GIT_REPORT_JA.md。mainへマージしない。
