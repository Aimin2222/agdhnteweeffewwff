# v5.10.3 GPUFX ExportOpt

## 確認した問題と原因の確度

ユーザーはMirrorFixでミラー正常起動を確認。新しいWindows診断もnative開始/初フレーム取得を示し、Python3.14.7 / windows-capture2.0.1で動いた。各バッチ4シーン中3本成功/1本失敗。前半3本は旧imageio FFmpegにprogram_openclがなくCPUエフェクト、後半3本は検証済み追加FFmpegでOpenCL Bloom/円形DOF/Focus Blur + NVENCを完了（returncode=0）。後半は約9秒素材/1080p60で138～143秒、システム全体CPU平均約89%/GPU32～35%。アプリ単独CPU値とは区別する。設定が異なるため前半/後半からGPU対CPUの速度差は算出しない。

遅さ: 原録画と時間補正は144fps、最終出力は60fps。従来はCPU/GPUの重いエフェクトに全144fpsを通し、エンコーダー段階で60fpsへ間引いていた。これはソース/FFmpegコマンドで確定した余分な処理である。CPUの色補正/VHS/粒子/合成なども残っている。NVENC使用率が低くてもエンコーダーだけが遅いとは判断しない。

第4シーン: シーク後に新しい映像を確認できず停止した。途中のcapture.logに子プロセス停止もあるが、旧ログだけでは停止を呼んだ箇所を特定できない。また停止中リプレイはフレームを一度だけ届け、その後更新しない場合があり、カメラ設定後に新たなフレームを要求すると拒否される。これらはコード上の再現試験で確認した失敗経路であり、実機の唯一の根因と断定しない。反復35秒監視スタックは通常エフェクト処理待ち/Tk mainloopで、クラッシュの証拠とはしない。

## 修正

1. 完成fpsの選択を重いエフェクトより前へ移す。CPU/GPU/失敗時CPU再試行/色保持再試行の全経路でfpsを揃える。内部144fps録画とCameraDirectorの更新頻度、最終30/60/120/144fps設定を維持。出力解像度/エフェクトの強度を下げない。時間ベースの演出/イベント/タイトル/肖像/音声mapとtrimを維持。フレームごとの粒子や時間方向の効果は完成fpsのサンプル上で評価する。
2. BGRAの毎フレームtobytesコピーを除去。親が所有する配列のmemoryviewをFFmpegへ渡し、非連続配列だけ連続化。新しい到着数/複製を含む録画枚数/補正前の動画長を診断へ残す。録画の速度補正/失敗時保護/NVENC選択は維持。
3. OpenCL Gaussianの重みをテンプレートごとに事前計算し、画素ごとのexp/正規化計算を除去。ぼかし半径/540p処理/円形焦点/DOF→Bloom順/アップロードとダウンロード/カラーを維持する。
4. 録画後はFFmpegの終了・時間補正を待つ前にLoLを一時停止し、ゲームの無駄な再生を減らす。LoL専用音声方式/時間軸は変えない。
5. シーク後の映像更新失敗は録画/録音前に1回だけ復旧。健康なミラーは再利用し、終了したキャプチャだけ同じWGCWindowSourceで再開始。自動前再生でReplay時刻の進行と新規フレームを両方確認し、指定の開始時刻へ再シーク/同じカメラ設定、さらに新しいフレームを確認してから録画する。静止した古い映像で成功にしない。中止/復旧失敗は安全停止し無限再試行しない。子の停止要求元スレッド名も診断に残す。

UIレイアウト/変数/ミラー操作/UI各種機能、カメラ座標/TargetLock/時計、Native LoL専用音声、START/FFmpeg導入/依存宣言を変更しない。共有core/jobs.pyとcore/capture_process.pyは内部変更のみで既存公開関数の引数/返却型とBGRAを維持する。正確なblobレビューを新JSONに記録し、旧camera/camera_clock/capture/workerの承認を保持する。

## 検証結果

- 全pytest297件成功（25.44秒、失敗/skipなし）。従来283+新14。実FFmpegで30/60/144fpsの枚数/時刻連続性、GPU転送前のfps選択、buffer同一性/非連続入力、係数の数式一致、停止後の第4シーン相当の復旧・死んだworker再開始・中止・古い画面で録画しない・FFmpeg終了待ち前のゲーム停止を検査。既存GPU失敗→CPU/色保持/音声/イベント/カメラ/実Tk/子プロセス/共有メモリの回帰も通過。
- 1080p・144fps入力→60fps・1秒素材、同じCPU色補正/VHS/Bloom/DOF等のFFmpegグラフを比較。従来11.805秒→先行fps選択5.070秒（約57%短縮）。FFmpegのthread数を減らす案はこの比較で速くならず採用しない。これはクラウドCPUの合成素材測定で、Windows実GPUの短縮率ではない。
- CPU PoCLによる実OpenCLで1080p色/焦点を再検証。Bloom/DOF単独は修正前画像と完全一致、併用は平均RGB誤差0.0000084/255、最大差2/255。色パッチと円形焦点は維持。Bloom/DOF併用3フレームの温まった比較は3.983→3.033秒だがCPU OpenCL値で実GPU性能の証拠ではない。製品のGPUプローブがCPU OpenCLを拒否することも確認。
- 診断ZIP/個人設定/パス/録画/音声/FFmpegバイナリー/PoCL依存はGitへ入れない。

## ブランチ・取得・再測定

GPU/録画: feature/gpu-export-optimization-v5103（feature/gpu-engineもここへfast-forward）。UI: feature/ui-mirror-targetfix-v5103を変更しない。統合: integration/v5.10.3-exportopt。全旧版/旧ブランチ/旧配布物を保存し、mainへマージしない。

```sh
.venv/bin/python tools/check_parallel_integration.py --gpu feature/gpu-export-optimization-v5103 --ui feature/ui-mirror-targetfix-v5103 --shared-review docs/CODEX_SHARED_API_REVIEW_EXPORT_v5.10.3.json --integration integration/v5.10.3-exportopt
.venv/bin/python -m compileall -q app.py legacy_app.py ui_phase1_prototype.py core ui tests tools
/workspace/.onboarding-tools/autocine/with-xvfb.sh .venv/bin/python -m pytest tests -q
```

取得用codex/lol-autocine-v5103-exportopt-handoffのCode → Download ZIP、別フォルダへ展開してLoL_AutoCine/START_GPU.bat。旧MirrorFixからの差分/完全版/全ブランチbundleをtools/package_v5103_exportopt.pyで生成。配布名GPUFX_ExportOpt、VERSION5.10.3を維持。Windows取得/起動にmainマージや環境Publishは不要。

実機では同じリプレイ/同じ選択1シーン/1080p60/同じBloom・DOF・VHS・音声等で前回版と所要時間を比較。次に4シーン連続で試し、4番目が復旧して録画できるか、失敗しても再試行可能かを確認。完成動画の色/ぼけ/焦点/イベント時刻/対象追従/LoLだけ音声/同期/再生速度を確認。COLLECT_DIAGNOSTICSのeffects_fps/frame_rate_selection/encoder/gpu_effects_confirmedとcaptureのframes/fresh_frames/captured_media_duration_s、復旧ログ/stop_requestedを照合。Windows/実LoLの復旧成功と速度改善はこの版では未検証であり、上記クラウドの数値で保証しない。
