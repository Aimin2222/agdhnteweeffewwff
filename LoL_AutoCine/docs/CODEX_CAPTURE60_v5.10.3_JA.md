# v5.10.3 GPUFX Capture60

ユーザーの希望: 144fpsでの加工は不要で、最初から60fps加工でよい。既存UI・カメラ・LoL専用音声とGPU処理を維持し、小さい差分で60fps出力の中間工程も軽量化する。

## 今回のWindows診断で確認したこと

前回ExportOptのエフェクト4本すべてでeffects_fps=60、frame_rate_selection=before_effects。FFmpegグラフ先頭はfps=fps=60:round=near、GPU OpenCL Bloom/円形DOFとNVENCで成功（returncode=0、gpu_effects_confirmed=true）。加工時間53.489/55.422/56.296/49.413秒。runtimeは4本完了を記録し、モンタージュも成功。途中でInvalid shared capture frame headerによる子終了があったが、1回の映像入力復旧後に次の録画を開始できた。原因が完全に解消したという意味ではない。診断に個人パスが含まれるため原ZIPはGitへ入れない。

録画と時間補正だけはまだ144fps。新規映像の到着数は各237～246、書き込み枚数は626～688で、複製フレームを144fpsでスケール/エンコードしていた。時間補正は4.726～6.303秒。前回診断と効果設定が異なるため、今回の49～56秒から厳密な速度改善率は算出しない。

## 今回の変更

core/jobs.pyのClipRecorder開始時だけ、録画fpsをmin(capture_fps, fps)へ制限する。標準60fps出力なら原録画60fps→必要な時間補正60fps→加工60fps→出力60fps。前回の加工前fps選択はそのまま維持。録画と加工・出力のfpsをruntimeへ表示する。

Template.capture_fpsやTemplate.fpsの既存フィールド、UI変数/配置/選択肢、公開record_one_clipの引数/返却型を変えない。既存144fps出力を明示選択した場合は144fpsの機能を維持し、30/120fpsも選択値に対応。低いcapture_fpsを明示した呼び出し側の上限も守る。録画fpsとカメラの更新頻度は独立しており、CameraDirector内部144Hz/Replay API送信最大60Hzを変更しない。

core/recorder.pyは未変更。実時間に合わせる再生速度補正を省略せず、新しい録画fpsが元動画の時刻と補正出力へ伝わる。LoL専用Native音声/録音時刻/trim/mux、イベント時刻、TargetLock、WGCの安全停止・復旧、GPU Bloom/DOF/Focus Blur/CPUフォールバック、NVENC→CPU保護を維持。今回の変更後Windows実機での速度・音声同期は未検証。

## 検査・並行開発

GPUブランチ: feature/gpu-capture60-v5103、feature/gpu-engineもfast-forward。UIブランチ: feature/ui-mirror-targetfix-v5103を保持。統合: integration/v5.10.3-capture60。core/jobs.pyの正確なblobは新しい共有レビューへ記録し、旧capture/cameraの承認を保持する。mainへマージせず、全旧版を保存。

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-capture60-v5103 --ui feature/ui-mirror-targetfix-v5103 --shared-review docs/CODEX_SHARED_API_REVIEW_CAPTURE60_v5.10.3.json --integration integration/v5.10.3-capture60
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python -m pytest tests -q
```

追加テストは30/60/120/144fpsと低い録画上限のジョブ開始を検査し、テンプレート不変/カメラ144Hz/60Hzを確認。実FFmpegで60fpsのバックプレッシャー相当の短い原動画を実時間へ補正し、60fps/連続PTS/終端丸め1フレーム以内を検査。既存の録画・音声・エフェクト・カメラ・UI回帰も実行する。

## Windowsで取得・確認

取得ブランチcodex/lol-autocine-v5103-capture60-handoffのCode→Download ZIP。旧版とは別フォルダへ展開し、LoL_AutoCine/START_GPU.batで起動。標準60 FPSで同じ1シーン/同じ効果と音声の所要時間を比較し、次に4シーン連続を確認。録画・時間補正の診断output_fps=60、効果effects_fps=60、最終MP4の60fps、色/焦点/対象追従/イベント/LoLだけ音声/同期/再生速度を確認する。144 FPSを明示選択した場合は高fpsを維持する。

完全版/前回ExportOptからの差分/全ブランチbundleを保存し、tools/package_v5103_capture60.pyで再生成できる。配布名GPUFX_Capture60、VERSION5.10.3を維持。Windows取得/起動にmainマージ・環境Publishは不要。
