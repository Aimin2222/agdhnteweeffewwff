# GPUFX版をWindowsで使う

GitHubの `codex/lol-autocine-v5103-gpu-effects-handoff` ブランチで **Code → Download ZIP** を使い、前回版とは別フォルダへ展開します。**LoL_AutoCine/START_GPU.bat**を実行してください。初回だけOpenCL対応FFmpegを約184 MiBダウンロードし、公式固定SHA256とフィルター/エンコーダーを検査して追加します。元START.batとNative Audio Helperの構築フローは維持しています。

`handoff/LoL_AutoCine_v5.10.3_GPUFX_Windows_Full.zip` のGitHub **Download raw file**でも完全版を取得できます。チャットの架空ダウンロードリンクは使いません。差分ZIPはHangFix版基準で、単体起動用ではありません。Windows取得・起動にmainマージや環境Publishは不要です。

Bloomと円形DOFのぼかし/マスク/合成をGPUへ移しました。併用はGPUメモリで続けて計算し、この区間の転送はアップロード/ダウンロード各1回。GPUデバイスでRGBA実行を確認してから採用し、非対応・エラー・不意なモノクロ出力はCPUへ戻して理由を診断に記録します。既存Focus Blur等のOpenCL対応判定、NVENC→CPUエンコード再試行も維持。

CPUで動く部分もあります。Tk画面操作、軽量プレビュー、色補正/LUT、粒子、ビネット、字幕・肖像、音声、上下帯DOFはCPU。既存UI・カメラ・LoLだけのNative録音・実時間同期を変更していません。追加FFmpegは新しいGPUドライバーを必要とする場合があります。明示IMAGEIO_FFMPEG_EXEは優先されます。

まずGPU優先 + Bloomでチェック1シーンを作成してください。次に円形DOF単独/併用と全検出シーンを試し、色/LoLだけ音声/同期/fps/焦点/追従/中止の応答を旧版と比較します。COLLECT_DIAGNOSTICS.batの最終effects JSONで `returncode=0`、`error=null`、`gpu_effects_confirmed=true`、`pipeline.gpu_blur_effects` のbloom/dofを確認します。NVENCはencoder=h264_nvencで別に確認します。同じ素材・同じ設定で処理時間を比較してください。

全pytest268件成功。CPU PoCL上の実OpenCLで1080pのBloom/DOF/併用を実行し、色と円形焦点を確認しました。これはGPU速度/実機成功の検証ではありません。Windows/GTX 1070 Ti/実LoL/Native録音/追加Windows FFmpegの実行と速度は未検証です。

ソース250ファイル/Python93・全36ブランチ、完全版248/差分11ファイルを保存。差分を適用すると全ソースが一致することを検査し、未追跡の個人ファイルを除外。全旧版を保持。バージョン番号は5.10.3、配布名GPUFXで区別します。

## ローカルGit開発

保存先が存在しない状態で実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5103-gpu-effects-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_GPUFX_Handoff
git clone --branch integration/v5.10.3-gpu-effects LoL_AutoCine_GPUFX_Handoff/handoff/LoL_AutoCine_v5.10.3_GPUFX_all_branches.bundle LoL_AutoCine_GPUFX_Dev
cd LoL_AutoCine_GPUFX_Dev
git branch stable/v5.8.5 origin/stable/v5.8.5
git branch feature/gpu-engine origin/feature/gpu-engine
git branch feature/ui-dispatch-hangfix-v5103 origin/feature/ui-dispatch-hangfix-v5103
git branch integration/v5.10.3-hangfix origin/integration/v5.10.3-hangfix
git status --short
git branch --all
```

全36ブランチはorigin/*にも復元されます。このcloneのoriginはPC上のbundleでGitHubではありません。GPUはfeature/gpu-engine、UIはfeature/ui-dispatch-hangfix-v5103。衝突ガードと共有blob承認はLoL_AutoCine/docs/CODEX_GPU_EFFECTS_v5.10.3_JA.mdを参照。
