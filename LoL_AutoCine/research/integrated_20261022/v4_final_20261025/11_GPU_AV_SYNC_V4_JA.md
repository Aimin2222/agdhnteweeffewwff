# GPU・encode・AV同期
Windowsネイティブでlibx264/h264_nvenc各2秒・5秒1080p60をencode、全120/300frames decode、4/4成功。CPU約.362/.748秒、NVENC約.813/1.157秒。この短い人工入力/CQとCRF非同等条件で速度/画質の優勝は決めません。

GPU FXは元GPUFullStage runtime probe、代替OpenCL avgblur、sandbox外の同条件再試行でdevice creation -12 Cannot allocate memory。NVENC成功でGPU FX成功に置き換えません。driver変更・インストール・UI29への介入なし。CPU代替で他研究は継続。

人工AVは30/60fps×.5/1/2x×PCM/AAC=12。white映像pulseと1kHz音をsource.5秒に配置。atempo/時刻変換後をvideo showinfo PTS、audio ashowinfo block PTS+sample indexで測定。単純frame-order offsetはAAC先頭時刻を落とすため旧診断値として残し、PTS再評価を採用。

10/12は±50ms以内、30fps2x PCM−58.791ms/AAC−58.625msは要確認。閾値立上り、frame量子化、atempo過渡を含み、サンプル聴取やLoL captureではありません。再検証は複数pulse/相互相関/先頭末尾/長尺driftを追加し、LoL専用録音を別試験。LoL音声合格0。実製品で固定補正58msを勝手に追加しない。
