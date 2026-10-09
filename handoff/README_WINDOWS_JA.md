# v5.10.3 GPUFX CaptureFixをWindowsで試す

GitHubの `codex/lol-autocine-v5103-capturefix-handoff` ブランチで **Code → Download ZIP**。前回版とは別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat**を起動してください。元START.bat/Native Audio Helper/追加GPU FFmpegの手順を維持しています。初回のGPU FFmpeg取得は約184MiBです。

`handoff/LoL_AutoCine_v5.10.3_GPUFX_CaptureFix_Windows_Full.zip` のGitHub **Download raw file**でも完全版を取得できます。差分ZIPは前回GPUFX基準で、単体起動用ではありません。Windowsへの取得・起動にmainマージ/環境Publishは不要です。

今回の診断はチェック2シーンの開始後、Windowsの画面キャプチャ開始で35秒以上待機し、ユーザーが応答なしを手動終了したものです。GPUエフェクト/エンコードは開始した記録がなく、その失敗とは断定できません。原ZIP/ユーザー名/プレイヤー情報は配布していません。

WGCを独立Pythonプロセスで開始し、8秒以内に初フレームが来なければ子を終了してエラーに戻します。共有メモリの最新BGRAを親が所有する配列へ受信し、混在フレームと古いフレームの継続録画を避けます。停止・異常終了・再試行で子と共有メモリを回収し、Windowsでは可能ならJob Objectでも親終了時の子終了を保証します。LoLウィンドウだけを対象にし、デスクトップ録画は追加しません。

前回GPUFXのBloom/円形DOF/OpenCL/NVENC選択・CPUフォールバック、カメラ、LoL専用音声、UI、応答停止対策、録画時刻を維持。全pytest278件成功（22.03秒）、新しい実プロセス/共有メモリ試験10件成功。正常BGRA/メモリ所有/開始待ち/子異常終了/中断/再試行/回収/待機中の実Tk応答を確認。ただしネイティブWGCだけは合成実装で、Windows/実LoL/GPUドライバーでの修復成功は未検証です。

LoLリプレイを表示し、最小化を解除してチェック1シーン、次にチェック2シーンを試してください。開始できなければ8秒程度でエラーに戻り、同じアプリで再試行できるか確認します。COLLECT_DIAGNOSTICS.batで新しいcapture.log/capture_worker_*.log/last_errorを収集できます。初期化が成功したら、色/LoLだけ音声/同期/fps/対象追従/DOF/Bloomと最終effects JSONのGPU実行を確認してください。

ソース256/Python97/全38ブランチ、完全版254/差分8ファイルを保存。差分適用後全ソース一致・個人ファイル除外を確認。番号5.10.3を維持し、GPUFX_CaptureFixで区別します。

## ローカルGit開発

保存先が存在しないことを確認して実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5103-capturefix-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_CaptureFix_Handoff
git clone --branch integration/v5.10.3-capturefix LoL_AutoCine_CaptureFix_Handoff/handoff/LoL_AutoCine_v5.10.3_GPUFX_CaptureFix_all_branches.bundle LoL_AutoCine_CaptureFix_Dev
cd LoL_AutoCine_CaptureFix_Dev
git branch stable/v5.8.5 origin/stable/v5.8.5
git branch feature/gpu-engine origin/feature/gpu-engine
git branch feature/capture-startup-v5103 origin/feature/capture-startup-v5103
git branch feature/ui-dispatch-hangfix-v5103 origin/feature/ui-dispatch-hangfix-v5103
git branch integration/v5.10.3-gpu-effects origin/integration/v5.10.3-gpu-effects
git status --short
git branch --all
```

全38ブランチをorigin/*にも復元します。このcloneのoriginはPC上のbundleでGitHubではありません。GPUはfeature/gpu-engine（feature/capture-startup-v5103と同じ先端）、UIはfeature/ui-dispatch-hangfix-v5103。ガードはdocs/CODEX_SHARED_API_REVIEW_CAPTURE_v5.10.3.jsonを使います。詳細はLoL_AutoCine/docs/CODEX_CAPTURE_STARTUP_FIX_v5.10.3_JA.md、Git/実変更はSOURCE_GIT_REPORT_JA.md、検証はVERIFICATION_v5.10.3_CaptureFix.jsonを参照。
