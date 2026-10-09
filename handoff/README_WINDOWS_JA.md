# v5.10.3 GPUFX MirrorFixをWindowsで試す

GitHubの `codex/lol-autocine-v5103-mirrorfix-handoff` ブランチで **Code → Download ZIP**。前回版とは別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat**を起動してください。

`handoff/LoL_AutoCine_v5.10.3_GPUFX_MirrorFix_Windows_Full.zip` のGitHub **Download raw file**でも完全版を取得できます。差分ZIPは前回CaptureFix基準で、単体起動用ではありません。Windowsへの取得・起動にmainマージ/環境Publishは不要です。

今回の原因は前回workerがwindow_nameとwindow_hwndを同時指定した不具合。14回ともキャプチャのコンストラクターでエラー終了。GPU処理を始める前に失敗していました。HWND対応版はHWNDのみ、旧版はLoLタイトルのみを渡します。子の具体的エラーをUIに表示し、準備中の表示を失敗後に残しません。

ミラー開始/停止は画面を止めず非同期で処理。準備中の再クリックで中止し、遅れて戻る古い結果は無効化します。録画中の切替は案内して拒否。既存UIの配置、GPU Bloom/円形DOF/OpenCL/NVENC/CPUフォールバック、カメラ、LoL専用音声、録画時刻、START/Native Audio Helper/FFmpeg導入を維持します。

全pytest283件成功（22.60秒、失敗/skipなし）。公式ライブラリ4版のPythonラッパーで対象の指定も検査しましたが、native Windowsと実GPUは代替で、Windows/LoL/GPUの修復成功は未検証です。

LoLリプレイを表示/最小化解除し、ミラーON→OFF→ON、チェック1シーン→2シーンを試してください。8秒初フレーム上限を維持し、失敗なら具体的エラーへ戻ります。COLLECT_DIAGNOSTICS.batでcapture.log/capture_worker_*.log/last_errorを収集。開始できたら色/LoLだけ音声/同期/fps/対象追従/Bloom/DOFと診断の実GPU実行を確認してください。

ソース260/Python99/全41ブランチ、完全版258/差分10を保存。差分適用後全ソース一致、個人ファイル除外を確認。番号5.10.3を維持し、GPUFX_MirrorFixで区別します。

## ローカルGit開発

既存フォルダを上書きしない新しい保存先で実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5103-mirrorfix-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_MirrorFix_Handoff
git clone --branch integration/v5.10.3-mirrorfix LoL_AutoCine_MirrorFix_Handoff/handoff/LoL_AutoCine_v5.10.3_GPUFX_MirrorFix_all_branches.bundle LoL_AutoCine_MirrorFix_Dev
cd LoL_AutoCine_MirrorFix_Dev
git branch feature/capture-targetfix-v5103 origin/feature/capture-targetfix-v5103
git branch feature/ui-mirror-targetfix-v5103 origin/feature/ui-mirror-targetfix-v5103
git branch integration/v5.10.3-capturefix origin/integration/v5.10.3-capturefix
git status --short
git branch --all
```

全41ブランチがorigin/*にも復元されます。このcloneのoriginはPC上のbundleでGitHubではありません。UI/GPU統合検査のコマンドはLoL_AutoCine/docs/CODEX_MIRROR_TARGET_FIX_v5.10.3_JA.mdを参照。Git/実変更はSOURCE_GIT_REPORT_JA.md、検証はVERIFICATION_v5.10.3_MirrorFix.json。
