# v5.10.6 GPU Full — Windowsでまとめて確認する

## 取得・起動

GitHubの `codex/lol-autocine-v5106-gpu-full-handoff` ブランチで **Code → Download ZIP**。旧版と別フォルダへ展開し、`LoL_AutoCine/START_GPU.bat` を実行します。設定を引き継ぐ場合は旧設定をコピーし、録画/プロジェクトの原本は残してください。mainのマージやクラウド環境Publishは不要です。

初回はFFmpeg準備とGPU実行プローブに時間がかかります。CPU経路への切替理由を診断へ保存します。「NVENC使用」はGPUエフェクト実行の証明にはなりません。

## 一度のテストでお願いしたい操作

1. **UI**：ミラーON、簡易FX反映ON。色/露出/DOFのスライダーを続けて動かし、タブ・スクロールを操作。「？」の1秒ホバーとクリック説明、ミラーON/OFFも確認。
2. **同じ1シーンを60fpsで書き出し**：まず普段の色、Sphere Blur、Vignette、DOF、Bloom、粒子を使う。実時間の長さ、正常なカラー、中心の焦点、三人称TargetLock、LoLだけの音声とキル瞬間の同期を確認。書き出し後のミラーが地中や真っ暗にならないことも確認。
3. **録画済み素材の一括比較**：アプリを閉じて `TEST_GPU_RENDER.bat` を実行。2で作った `raw` のMP4を選択（完成済みの加工MP4は選ばない）。同じ先頭6秒で6本を自動生成し、再録画のばらつきを除いて比較します。ゲーム音声なしの加工専用テストで、元ファイルは変えません。
4. **複数シーン**：アプリを再起動し、チェック2〜3シーン→全検出シーン、モンタージュflash/darkを確認。日本語タイトル・実チャンピオンのキル画像/複数行、枠/発光、カメラのブルー/レッド向き、ゲーム音声/BGMを確認。二重クリック防止とキャンセルも試す。
5. **診断を送る**：`COLLECT_DIAGNOSTICS.bat` で作る `AutoCine_Diagnostics.zip` と、見た目/所要時間/問題があった操作を送ってください。映像を全て送る必要はありません。

## 一括比較の6本

| ファイル | 確認すること |
| --- | --- |
| 01_clean_gpu | 色補正なし、カラー・60fps・速度が正常 |
| 02_standard_gpu | 普段の重い色/温度/彩度＋DOF/Bloom/Sphere/Vignette/粒子をGPU加工 |
| 03_standard_cpu | 02と同じ設定をCPU加工（エンコーダー条件は同じ） |
| 04_curve_title_band_gpu | カーブ・日本語タイトル・帯DOF・黒枠 |
| 05_temporal_transform_gpu | Radial/Zoom時間ブラー、Shake/Mirror、キル時の色ずれ/Flash |
| 06_fog_grain_glint_gpu | フォグ・粒子・Glint/Glitch・Film Burn・BPM/キルアクセント |

結果は `output/gpu_render_tests/日時/`。MP4と `RESULTS.json`、同じ比較結果が診断ZIPにも入ります。GPU対応時には `GPU confirmed`、切替時には `CPU/hybrid fallback` と実際の経路を表示します。成功しただけでGPU実行扱いにはしません。

02と03の `wall_time_s` と、実際の加工 `elapsed_s` を比較します。初回にはプローブ/コンパイルが含まれるため、必要なら同じテストをもう一度実行し2回目を比較します。速度の合格倍率は決め打ちしません。**同じエンコーダー、GPU成功、画質/時間/音声維持**を確認してから速さを判定します。GPU失敗/CPU切替ならドライバ・形式・シェーダーの理由を診断で特定します。

新経路が問題を起こす場合は `START_GPU_HYBRID.bat` で前版の部分GPU経路、`START_CPU_EFFECTS_COMPARE.bat` でCPUエフェクトを選べます。どちらも既存の録画・LoL専用音声・UI設定を維持します。

## 診断で見る項目

- `gpu_effects_confirmed=true`、`pipeline.full_gpu_pipeline=true`、`gpu_effects_selected` にcolor_grade、vignette、grain、dof、bloomなど。
- 実際の `encoder=h264_nvenc`、デコード実証時は `pipeline.video_decoder=NVDEC`。利用不可理由と再試行は別項目。
- `effects_fps=60`、`frame_rate_selection=before_effects`、主映像のOpenCL転送各1回。
- `ffmpeg_cpu_pc_pct` はPC全体に対するFFmpegの占有率。`ffmpeg_cpu_pct` は全CPUコアの合計なので100%超も正常。旧 `cpu_pct` はPC全体。最初の測定値は0になり短い実行では参考値です。

UI、音声、ファイルI/O、GPU入口の形式変換とミラー簡易合成はCPUを使います。すべてのCPU負荷がなくなる仕様ではありません。LinuxのPoCL検証はCPU上でOpenCLシェーダーを確認するもので、NVIDIA実機性能の証明には使いません。
