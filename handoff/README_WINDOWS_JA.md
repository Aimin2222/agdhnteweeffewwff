# v5.10.6 GPU FullをWindowsで取得する

GitHubの `codex/lol-autocine-v5106-gpu-full-handoff` ブランチで **Code → Download ZIP**。旧版と別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat** を実行してください。mainのマージやクラウド環境PublishはWindowsの取得/起動に不要です。

完全版ZIPを `handoff/LoL_AutoCine_v5.10.6_GPUFull_Windows_Full.zip` で開いて **Download raw file** でも取得できます。MergeChangesは前回v5.10.5基準のGitパッチです。古いGPUファイルを上書きしないでください。

色/LUT/カーブ・全22演出・時間ブラー・DOF（円/帯）・Bloom・周辺減光・粒子・枠/フォグ・BPM/キルアクセント・タイトル/キル画像合成をOpenCL GPUへ対応。加工前60fps選択、主映像のOpenCL転送各1回、PNGのGPU再利用、対応素材のNVDEC、NVENCへのRGBA入力を追加しました。GPU/形式/色保持に問題があれば同じCPU経路へ再試行します。

受領ホットフィックスの録画後カメラ復帰とホバーを統合。滑らかなミラーUI、クリック説明、三人称TargetLock、LoL専用音声、カメラ144Hz/動画60fpsは維持。CPUは音声・UI・制御・ファイル・GPU入口の形式変換・ミラー簡易合成に残ります。全CPU負荷を0にするものではありません。

全pytest348件成功、失敗/skipなし。CPU PoCL上のシェーダーで色の平均誤差0.52～1.10/255、時間履歴誤差最大1.5/255、60fpsフレーム数、装飾表示/消去時刻、全演出を確認。実FFmpegで144fps→加工60fps、音声offset/mux、GPUモンタージュと音声copyを確認。これはLinuxでの検証で、Windows/NVIDIA実機の速度・ドライバ相性は未検証です。

**まとめて試す手順**: LoL_AutoCine/docs/WINDOWS_TEST_v5106_JA.md。
1. ミラーONでスライダー/色/タブ/スクロール、ホバー/クリックを確認。
2. 普段の設定で同じ1シーンを60fps出力し、色/焦点/TargetLock/LoL音声/同期を確認。
3. アプリを閉じて **TEST_GPU_RENDER.bat** →そのraw MP4を選択。6本を自動加工し、02_GPUと03_CPUを比較（加工テスト自体は無音）。
4. アプリで2～3シーン/全シーンとflash/darkモンタージュ、タイトル/キル画像を確認。
5. **COLLECT_DIAGNOSTICS.bat** の診断ZIPと所要時間・見た目・問題操作を送る。

比較結果はoutput/gpu_render_tests/日時/RESULTS.jsonと診断ZIP。GPU成功とfallbackを区別します。問題時はSTART_GPU_HYBRID.bat（旧部分GPU）、START_CPU_EFFECTS_COMPARE.bat（CPUエフェクト）で比較できます。詳細はVERIFICATION_v5.10.6.json、SHA256SUMS.txt、SOURCE_GIT_REPORT_JA.md。

## ローカルGitで開発する場合

新しい保存先で実行します。

```sh
git clone --single-branch --branch codex/lol-autocine-v5106-gpu-full-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v5106_Handoff
git clone --branch integration/v5.10.6 LoL_AutoCine_v5106_Handoff/handoff/LoL_AutoCine_v5.10.6_GPUFull_all_branches.bundle LoL_AutoCine_v5106_Dev
cd LoL_AutoCine_v5106_Dev
git branch feature/gpu-full-v5106 origin/feature/gpu-full-v5106
git branch feature/ui-hover-v5106 origin/feature/ui-hover-v5106
git branch stable/v5.8.5 origin/stable/v5.8.5
git status --short
git branch --all
```

全54ブランチはorigin/*へ復元されます。originはローカルbundleです。担当ガードはdocs/CODEX_INTEGRATION_v5106_JA.md。旧配布物90件と旧51ブランチを保存しています。
