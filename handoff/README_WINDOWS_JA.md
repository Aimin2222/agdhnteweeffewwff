# v5.10.3 GPUFX Capture60をWindowsで試す

GitHubの `codex/lol-autocine-v5103-capture60-handoff` ブランチで **Code → Download ZIP**。前回版とは別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat**を起動してください。mainマージ/クラウド環境Publishは不要です。

GitHubの `handoff/LoL_AutoCine_v5.10.3_GPUFX_Capture60_Windows_Full.zip` の **Download raw file**でも取得できます。差分ZIPは前回ExportOpt基準で単体起動用ではありません。VERSION5.10.3を維持し、GPUFX_Capture60で区別します。

今回の診断では前回版の加工はすでに60fps/GPU Bloom・円形DOF + NVENC、4本完了、加工49～56秒でした。ただし原録画/時間補正が144fpsだったため、標準60 FPSなら録画60fps→必要な時間補正60fps→加工60fps→出力60fpsに揃えました。CameraDirector内部144Hz/Replay API送信最大60Hzを維持。UIやカメラ、GPU効果/CPU保護、LoL専用音声/時間軸は変更しません。144 FPSを明示選択した機能も維持します。

全pytest303件成功（27.86秒、失敗/skipなし）。追加6件で30/60/120/144fpsと低い録画上限、カメラ時計とテンプレート不変を検査し、実FFmpegで60fpsの時間補正/連続PTS/終端丸め1フレーム以内を確認。新しいCapture60版のWindows実機速度と音声同期は未検証です。

同じリプレイ/同じ1シーン/60 FPS/同じ効果・音声で前回版と所要時間を比較し、4シーン連続を確認。完成MP4の色/焦点/カメラ/LoLだけ音声/同期/再生速度を確認。COLLECT_DIAGNOSTICS.batでcapture.output_fps=60、timing_normalization.output_fps=60（補正が必要な場合）、effects_fps=60、gpu_effects_confirmed、encoderを確認できます。runtimeには録画/加工・出力fpsを表示。

完全版266/差分6、差分適用後全268ソース一致、個人ファイル除外。Git報告はSOURCE_GIT_REPORT_JA.md、検証はVERIFICATION_v5.10.3_Capture60.json、詳細はLoL_AutoCine/docs/CODEX_CAPTURE60_v5.10.3_JA.md。

## ローカルGit開発

既存フォルダを上書きしない新しい保存先で実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5103-capture60-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_Capture60_Handoff
git clone --branch integration/v5.10.3-capture60 LoL_AutoCine_Capture60_Handoff/handoff/LoL_AutoCine_v5.10.3_GPUFX_Capture60_all_branches.bundle LoL_AutoCine_Capture60_Dev
cd LoL_AutoCine_Capture60_Dev
git branch feature/gpu-capture60-v5103 origin/feature/gpu-capture60-v5103
git branch feature/ui-mirror-targetfix-v5103 origin/feature/ui-mirror-targetfix-v5103
git branch integration/v5.10.3-exportopt origin/integration/v5.10.3-exportopt
git status --short
git branch --all
```

全45ブランチをorigin/*へ復元。このcloneのoriginはPC上のbundleです。担当/共有レビュー/統合ガードは上記開発文書のコマンドを使用。旧版/旧ブランチ/旧ZIP/bundleを保存しています。
