# GPUフォールバック分析と段階計画

対象: LoL AutoCine v5.8.5。監査日: 2026-10-08。アプリ本体の変更なし。手元のGTX 1070 Tiの実機診断ZIPは同梱されていないため、ユーザーのWindows環境の原因はまだ確定できない。

## 現在の選択条件

`core/gpu_pipeline.py:48`の検査は、アプリが実際に使用するFFmpegに`avgblur_opencl`があり、`opencl=ocl:0.0`でNV12 upload → avgblur → NV12 downloadを1フレーム通せた場合だけ成功する。単にNVENCや`scale_cuda`があるだけではOpenCL効果を選ばない。

`selected_gpu_effects`の対象は`focus_blur`、`vr_blur`、`sphere_blur`、`glint`のみ。OpenCL検査に失敗、対象効果がOFF、対応フィルターがない場合はCPUへ進む。Bloom、DOF、色補正、LUT、その他の多くの効果はCPUグラフである。ゲーム内DOFはReplay APIによる別経路で、FFmpegのOpenCL DOFではない。

GPUレンダーに失敗すると`effects.py:652`以降で元のCPU効果を復元して再試行する。NV12を維持する経路になっており、過去の不適合な直接yuv420pダウンロードは再導入していない。

## 原因候補と確度

| 原因 | 確認結果・検査方法 | 確度 |
|---|---|---|
| アプリ使用FFmpegにavgblur_openclがない | imageio-ffmpegの実バイナリを確認する。PATHの別FFmpegを調べても判定対象と一致しないことがある。 | 引き継ぎ資料で最有力。Linux同梱7.0.2では実際に欠落。Windowsは未確認。 |
| OpenCLランタイム/ドライバー/デバイス初期化失敗 | フィルター搭載の次にNV12の実行プローブを確認。 | LinuxのシステムFFmpeg 7.1.5ではOpenCL平台なし(-1001)で失敗を再現。Windowsは未確認。 |
| 0.0固定が目的のGPUを選んでいない | 複数プラットフォーム、CPU OpenCLデバイス、NVIDIAの登録順を調べる。 | ソースで選択固定を確認。GTX 1070 Tiでの並びは未確認。 |
| Bloom/DOFだけを有効化している | `video_effects`の対象4効果と`pipeline.gpu_effects_selected`を確認。 | ソースで確認。現行Bloom/DOFはCPUなので正常な設計上の経路。 |
| 1フレーム検査は成功したが本処理は失敗 | GPU試行のFFmpeg stderrと続くCPU試行JSONを比較。 | フォールバック実装あり。Windowsでの発生有無は未確認。 |

## 能力・実行結果・表示の整合性

次は修正候補。今回の監査で本体や既存テストは変更していない。

1. **NVENCは搭載の有無だけで判定。** `detect()`と`gpu_encoder_available()`は`-encoders`の文字列を見ており、実際のエンコード検査はない。LinuxのシステムFFmpegではNVENC搭載と表示されるが、1フレームの実行は`Cannot load libcuda.so.1`で失敗した。それでも`backend_name()`は`NVIDIA NVENC + CPU Effects fallback`となった。UI表示は利用可能性を過大評価する。GPU効果のCPU再試行も同じ`encoder_args()`を使うため、NVENC自体の失敗をlibx264へ切り替える実装にはなっていない。
2. **OpenCL実行検査の詳細が消える。** `_opencl_probe()`は終了コード/エラーをboolへ潰す。フィルター欠落と実行検査失敗はJSONで区別するが、平台、デバイス、フォーマット、タイムアウトの原因までは保存しない。`gblur_opencl`というフィールド名は実際にはavgblur_openclの搭載を指す。
3. **OpenCL成功はNVIDIA GPUの証明ではない。** 選んだOpenCLデバイスの種類/名前を検証していない。CPU OpenCLデバイスで通ってもGPUと表現できてしまう。glintの`unsharp_opencl`は搭載を確認するが、専用の実行検査はなくavgblurの検査を共有する。
4. **再試行JSONに能力ラベルが残る。** GPU失敗時に`gpu_effects_selected`は空へ直す一方、`gpu_backend`や`gpu_effects_unavailable_reason`は元の情報を引き継ぐ。`fallback_reason`と`filter_graph`、各試行の成否を合わせて読む必要がある。
5. **色保持再試行のcpu_video_effectsが更新されない。** 通常GPU失敗経路ではCPU効果リストを更新するが、色保持再試行ではGPUで消費した効果がCPUリストに戻らない。さらにタイトルPNGを再試行より前に削除するため、タイトル付きの色保持再試行にはファイル不存在の可能性がある。ソース上の問題で、GPUなしの今回の実行ではこの条件を再現していない。
6. **gpu_effects_confirmedはレンダー試行単位。** `run_render`はGPU効果指定あり＋FFmpeg終了0でtrueにする。その後のファイル検査、色検査、音声mux、最終MP4検査より前なので、最終クリップ成功とは別。最新ZIPは1試行分なので、全試行は`COLLECT_DIAGNOSTICS.bat`の集約ZIPで比較する。
7. **GPU/CPUで見え方が同一とは限らない。** GPU blurはNV12の輝度のみ平均ぼかし、CPUは低解像度gblur。glintもGPUのunsharpとCPUのunsharp＋eqで処理が異なる。単に速くなるだけの置換と扱わず、色と効果強度を同一素材で比較する。

## Windows / GTX 1070 Tiでの診断コマンド

プロジェクトフォルダでPowerShellを開く。以下は診断用の1フレーム処理で、LoL録音やカメラを変更しない。`.venv`の準備は`CODEX_LOCAL_DEVELOPMENT_JA.md`を参照。

```powershell
$ff = (& .\.venv\Scripts\python.exe -c "from core.effects import FFMPEG; print(FFMPEG)").Trim()
& $ff -version
& $ff -hide_banner -filters | Select-String 'avgblur_opencl|unsharp_opencl|scale_cuda|hwupload'
& $ff -hide_banner -encoders | Select-String 'h264_nvenc|libx264'
& $ff -hide_banner -hwaccels
nvidia-smi
& .\.venv\Scripts\python.exe -c "import json; from core.effects import gpu_capabilities,gpu_pipeline_status; print(json.dumps(gpu_capabilities())); print(gpu_pipeline_status())"
New-Item -ItemType Directory -Force diagnostics\ffmpeg | Out-Null

$oclLog = & $ff -hide_banner -loglevel verbose -init_hw_device opencl=ocl:0.0 -filter_hw_device ocl -f lavfi -i 'color=c=0x4080c0:s=64x64:d=0.1' -vf 'format=nv12,hwupload,avgblur_opencl=sizeX=3:sizeY=3:planes=1,hwdownload,format=nv12' -frames:v 1 -f null - 2>&1
$oclRC = $LASTEXITCODE
$oclLog | Set-Content -Encoding utf8 diagnostics\ffmpeg\codex_opencl_probe.log
"OpenCL probe exit=$oclRC"

$nvLog = & $ff -hide_banner -loglevel verbose -f lavfi -i 'color=c=0x4080c0:s=128x128:d=0.1' -frames:v 1 -c:v h264_nvenc -pix_fmt yuv420p -f null - 2>&1
$nvRC = $LASTEXITCODE
$nvLog | Set-Content -Encoding utf8 diagnostics\ffmpeg\codex_nvenc_probe.log
"NVENC probe exit=$nvRC"
```

`$ff`の選択を明示することが重要。外部FFmpegへ比較切替する場合は、信用できる配布元・署名/チェックサムを確認したバイナリを用い、同じPowerShellセッションで`$env:IMAGEIO_FFMPEG_EXE = '検証済みFFmpegの絶対パス'`を設定して新しいPythonプロセスで確認する。CUDA経路や他のGPU処理を一緒に変更しない。

OpenCLログでデバイスを確認し、0.0がNVIDIA GPUでない場合のみ、実際に列挙された番号で同じプローブを再実行する。番号を推測してコードへ固定しない。`unsharp_opencl`採用前には同じNV12経路でそのフィルターも個別に試す。

その後、同じリプレイ・カメラ・解像度・FPS・クリップ区間で、全効果OFF / Focus Blurのみ / Bloomのみ / DOFのみを個別に比較。1シーンと2シーン、LoLのみ音声、同期、カラー、対象ロスト、二重実行防止を確認する。`COLLECT_DIAGNOSTICS.bat`のZIPをローカル保管し、Gitへ追加しない。

## 次の小さな開発順序

1. **診断の正確性。** FFmpeg実パス/バージョン、搭載能力、各フィルターの実行検査、デバイス名/種類、終了コード/stderr、実際に選択・完了したエフェクト/エンコーダーを分ける。再試行ログとタイトルPNG寿命の問題を、それぞれ独立した小差分と失敗注入テストで扱う。UIレイアウト・カメラ・音声処理は触らない。
2. **Windows実機の経路確認。** 現行バイナリと検証済みOpenCL搭載バイナリを同一条件で比較。GTX 1070 Tiが選ばれていることとNV12往復の成功を確認。NVENCの実行可否と効果の実行可否は別の結果にする。
3. **Focus Blurの限定導入。** 既存CPU版との差、カラー・時間・効果強度・VRAM・エラー時の復元を確認し、通ったものだけ採用。CPUフォールバックを維持。
4. **Bloom、DOFを個別評価。** 現行CPU版を比較基準に、まず小さい検証グラフを作る。深度代理マスクや色の合成を維持し、計測結果なしにGPU化完了や速度向上を主張しない。
5. **回帰テストの整備。** 既存テストと現行音声/HUD/1080pプレビュー仕様の不一致を整理。Orbitの180/270度、左右サイド、音声分離/同期、GPU失敗後のCPU成功、キャンセルを増やす。UI整理やexe配布はこの後。

各修正は`codex/initial-audit`から機能別ブランチを作り、検証後にレビューする。v5.8.4はユーザー手元の実機比較基準として保存し、今回のZIPが含んでいないv5.8.4を復元済みとは扱わない。
