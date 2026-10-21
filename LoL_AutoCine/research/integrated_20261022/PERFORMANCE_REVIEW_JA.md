# GPU・録画・音声・出力性能の監査

> 調査日：2026-10-22 JST。コード基準：`fb03e0390805125fc063f4599af6c2541a653abf`。今回の作業は調査・設計のみ。実装、LoL実機操作、録画、既存テストの再実行は行っていません。提案値は未実測です。

## 4種類のFPS・GPU結果を分離する

1. カメラ制御の送信/更新Hz。
2. ミラーUIの表示FPS。
3. WGC等が取得した新しいframeの実効FPS/fresh ratio。
4. 出力containerのFPSと重複/補間を除いた実映像情報。

NVENCは圧縮、OpenCLは映像加工。CPU合成＋NVENCでも動画ファイルはGPU encoderを使用できる。[NVIDIA Video Codec SDK](https://docs.nvidia.com/video-technologies/video-codec-sdk/13.0/)はencode/decodeの仕組みを提供するが、AutoCineの全処理GPU化の証明にはならない。

## 過去ログの解釈

10/20文書には61出力exit0/NVENC、GPU FX confirmed=false全61、12件ffmpeg_missing_program_opencl、fresh ratio62–68%/実効約39fps等が記録される。その後の計測33.12fps、41.42fps、144Hz目標改善という異なるrunがある。別runの数値を1条件の速度向上率へまとめない。OpenCLgrainの688×387オフライン中央値22.24ms/p95 24.9msも1080p全処理60fps合格ではない。

今回これらの録画・計測は再実行していない。最新UI headにあるcapture_process変更を含め、実効改善の断定には新しい同条件の記録が必要。

## 計測計画

| 項目 | 記録値 | 判定上の注意 |
| --- | --- | --- |
| capture | frame_id/QPC, delivered/fresh/duplicate, p50/p95待ち | 同一画面で画素一致しても新規取得の場合がある |
| mirror | 描画回数/実frame回数、UI遅延p95 | 高い目標値だけを成果にしない |
| camera | API latency/slow call/drift/pose | 送信Hzを上げてもfresh映像が増えるとは限らない |
| FX | requested/supported/actual path、filter名、fallback理由 | GPU利用率だけで個別filter成功を証明しない |
| encoder | 実encoder、driver、FFmpeg hash、encode時間 | 列挙と3秒実encode成功を分離 |
| audio | LoL PID/tree、WAV長、start offset、peak/RMS、AVずれ | 他アプリ音が入らない対照試験が必要 |
| 全体 | wall time/映像秒、CPU/GPU/VRAM/RAM、temp disk | warmup・capture・FX・muxを分ける |


## 音声の環境条件

[core/audio.py:1](https://github.com/Aimin2222/agdhnteweeffewwff/blob/fb03e0390805125fc063f4599af6c2541a653abf/LoL_AutoCine/core/audio.py#L1)はnative helperを使う。legacy endpoint loopbackが残っていても自動代替として使用しない。[Microsoft application loopback sample](https://learn.microsoft.com/en-us/samples/microsoft/windows-classic-samples/applicationloopbackaudio-sample/)の最小条件はWindows build20348で、すべてのWindows10が対応する意味ではない。実際のOS機能probeを優先。LoLが無音の時はloopbackも無音になり得る。

## 性能改善の推薦

A：重複待ち・clock drift・frame queueを先に計測。bounded queueと古い表示frame破棄はmirrorに有効でも、録画frameを勝手に落として無記録にしない。B：grain/blur等の重いFXを単独最適化、LUTと合成順の共通化。C：ゼロコピーと複数GPU対応は転送コストを証明してから。GPU非対応時CPUは出力品質を守り、遅くなる理由を表示する。1080p60方針を黙って30fpsへ変更しない。
