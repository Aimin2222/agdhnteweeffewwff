# v5.10.7 ミラー設定操作・GPUテスト起動修正版

GitHubの `codex/lol-autocine-v5107-mirror-test-handoff` ブランチで **Code → Download ZIP**。旧版と別フォルダへ展開し、**LoL_AutoCine/START_GPU.bat** を実行してください。mainのマージやクラウド環境PublishはWindowsの取得/起動に不要です。

完全版ZIPを `handoff/LoL_AutoCine_v5.10.7_MirrorFix_Windows_Full.zip` で開いて **Download raw file** でも取得できます。MergeChangesは前回GPU Full v5.10.6基準のGitパッチです。古いGPUファイルを上書きしないでください。

今回の受領診断では16回すべて、OpenCL GPUによる映像加工・NVDEC・NVENC・1080p/60fpsで成功しています。GPUテスト6ケースの実行結果は診断に含まれませんでした。ミラー表示はCPU合成です。

ミラー用の縮小を高速化し、画面サイズへの拡大をワーカーへ移動。Canvas描画itemを再利用し、テンプレートは値変更時に再取得。スライダー/色/タブ/スクロール操作中はミラーだけ約6fpsへ抑え、操作後に通常頻度へ戻します。書き出し品質/FPS、三人称TargetLock、LoL専用音声、GPU Full処理は維持しています。

TEST_GPU_RENDERは通常アプリと同じpy -3を優先し、存在しないWindows用.venvを必須にしません。Python選択/終了コード、エンジンimportより前の起動状態、例外/キャンセル/完了を診断へ保存してコンソールに表示し、最後はpauseします。受領UI差分からRED側Orbitの向き、キル＋アシスト、ガラス斬撃/中央なし、準備失敗時のミラー復帰を統合。既存のホバー/クリック説明とGPUエンジンを保持しました。

全pytest369件成功、失敗/skipなし。実Tkで大きなミラー、設定変更、タブ/スクロール、ワーカー処理を確認。Linuxの合成1080p画像の準備時間中央値は60.18ms→29.81ms。これはTk画素転送やWindows実機の測定を含まず、実機のラグ解消を保証する数値ではありません。

**今回のテスト手順**: LoL_AutoCine/docs/WINDOWS_TEST_v5107_JA.md。
1. ミラーONで設定エリアのスライダー/色/タブ/スクロールを操作。ライブFX ON/OFFを比較。
2. アプリを閉じて **TEST_GPU_RENDER.bat** →同じraw MP4を選択。6ケースの進行と終了コードが表示され、最後の画面が残るか確認。
3. 通常アプリで1080p/60fpsの1シーン/複数シーン、LoL音声/同期、三人称、RED/BLUE、キル＋アシストを確認。
4. **COLLECT_DIAGNOSTICS.bat** の診断ZIPを送る。

起動失敗でもdiagnostics/gpu_test_launcher.logとgpu_test_startup_日時.json/.logに記録します。成功ならoutput/gpu_render_tests/日時/RESULTS.jsonとgpu_batch記録も生成。加工テスト自体は無音で、カメラやLoL音声は通常アプリで確認します。

## ローカルGitへ戻す場合

```sh
git clone --single-branch --branch codex/lol-autocine-v5107-mirror-test-handoff https://github.com/Aimin2222/agdhnteweeffewwff.git LoL_AutoCine_v5107_Handoff
git clone --branch integration/v5.10.7 LoL_AutoCine_v5107_Handoff/handoff/LoL_AutoCine_v5.10.7_MirrorFix_all_branches.bundle LoL_AutoCine_v5107_Dev
cd LoL_AutoCine_v5107_Dev
git branch feature/gpu-test-launch-v5107 origin/feature/gpu-test-launch-v5107
git branch feature/ui-mirror-v5107 origin/feature/ui-mirror-v5107
git status --short
```

全57ブランチはorigin/*へ復元されます。originはローカルbundleです。担当ガードはdocs/CODEX_INTEGRATION_v5107_JA.md。旧配布物96件と旧54ブランチを保存しています。
