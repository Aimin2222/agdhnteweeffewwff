# v5.10.3 GPUFX ExportOptをWindowsで試す

GitHubの `codex/lol-autocine-v5103-exportopt-handoff` ブランチで **Code → Download ZIP**。前回版とは別フォルダへ展開して **LoL_AutoCine/START_GPU.bat** を起動してください。mainマージ・クラウド環境Publishは取得や起動に不要です。

`handoff/LoL_AutoCine_v5.10.3_GPUFX_ExportOpt_Windows_Full.zip` のGitHub **Download raw file**でも取得できます。差分ZIPは前回MirrorFix基準で、単体起動用ではありません。番号5.10.3を維持し、GPUFX_ExportOptで区別します。

録画144fpsの全フレームへ重いエフェクトをかけてから60fpsへ間引いていたため、完成fpsの選択をエフェクトより前へ移しました。毎フレームBGRAコピーを減らし、OpenCL Gaussian係数を事前計算。FFmpeg終了待ちより前にLoLを停止します。シーク後の映像更新失敗は録画/録音前に一度だけ再準備し、新しい映像を確認できなければ安全停止します。

UI/カメラ/LoL専用音声方式/内部144fps/録画時間補正/解像度/エフェクト強度/既存GPU→CPU保護を維持。すべてのエフェクトがGPUになったという変更ではなく、CPU色補正・VHS・粒子などは残ります。

全pytest297件成功（25.44秒、失敗/skipなし）。クラウドCPUの1080p合成素材・同一効果で11.805→5.070秒（約57%短縮）。これはWindows実GPUの短縮率ではありません。CPU OpenCLで修正前後の色/焦点も検証。Windows/LoL実機でこの版の速度と第4シーンの復旧は未検証です。

同じリプレイ・同じ1シーン・1080p60・同じ効果/音声設定で前回版と時間を比較し、次に4シーン連続を確認してください。完成動画の色/焦点/カメラ/イベント/LoLだけ音声/同期を確認。COLLECT_DIAGNOSTICS.batでeffects_fps、frame_rate_selection、gpu_effects_confirmed、encoder、frames/fresh_frames、復旧/stop_requestedログを確認できます。

完全版262/差分11、差分適用後全264ソース一致、個人ファイル除外を確認。詳細はLoL_AutoCine/docs/CODEX_EXPORT_OPTIMIZATION_v5.10.3_JA.md、検証はVERIFICATION_v5.10.3_ExportOpt.json。

## ローカルGit開発

既存フォルダを上書きしない新しい保存先で実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5103-exportopt-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_ExportOpt_Handoff
git clone --branch integration/v5.10.3-exportopt LoL_AutoCine_ExportOpt_Handoff/handoff/LoL_AutoCine_v5.10.3_GPUFX_ExportOpt_all_branches.bundle LoL_AutoCine_ExportOpt_Dev
cd LoL_AutoCine_ExportOpt_Dev
git branch feature/gpu-export-optimization-v5103 origin/feature/gpu-export-optimization-v5103
git branch feature/ui-mirror-targetfix-v5103 origin/feature/ui-mirror-targetfix-v5103
git branch integration/v5.10.3-mirrorfix origin/integration/v5.10.3-mirrorfix
git status --short
git branch --all
```

全43ブランチがorigin/*に復元されます。このcloneのoriginはPC上のbundleです。GPU/UIを分離した検査コマンドは上記開発文書に記載。旧版/旧ブランチ/旧ZIP/bundleも保存しています。
