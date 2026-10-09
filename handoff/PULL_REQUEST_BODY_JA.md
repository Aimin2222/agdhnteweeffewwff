NVENCでエンコードできてもBloomをCPUで処理しており、ユーザー診断では9秒/13秒の素材の最終効果処理に約81秒/122秒かかっていました。Bloomと円形DOFのぼかし・焦点マスク・合成をOpenCL GPUへ移し、両方有効なら同じGPUメモリで連続処理します。この区間のアップロード/ダウンロードは各1回。色補正/装飾/音声/UIなどCPU処理も残ります。

START_GPU.batで公式固定SHA256のWindows FFmpegを別途追加。元同梱版・START.bat・Native Audio Helperのフローは保持します。フィルター列挙だけでなくGPU種別を限定したRGBA実行プローブ後に採用し、CPU OpenCLを除外。実行失敗/不意なモノクロ化は同じイベント時刻・肖像・タイトル・音声マップ・fpsでCPU再描画し、診断を修正します。明示FFmpeg指定、既存NVENC失敗時のCPUエンコード再試行を保持。

検証: 全pytest268件成功（13.83秒）、新GPU9ケース。CPU PoCLで実OpenCLカーネルによる1080pのBloom/円形DOF/併用を実行し、RGB平均絶対誤差0.45〜0.69/255、色と円形焦点を確認。これはGPU実機成功や高速化の証拠ではありません。GPU専用プローブがCPU OpenCLを拒否することを確認。Windows/GTX 1070 Ti/実LoL/Native録音/Windows FFmpeg実行と速度は未検証。追加FFmpegの新NVENCとドライバー互換性も実機確認が必要です。

UI/HangFix/カメラ/録画/LoL専用録音/Native/元START.bat/共有API/依存宣言を保持し、担当・共有blob・統合一致ガード成功。250ソース/Python93・全36ブランチbundle、完全版248/差分11ファイル、SHA256、差分適用後の全ソース一致を確認。個人診断/設定/録画と200MBのFFmpegをGitへ入れません。前回HangFixを比較先にしたDraft PRで、mainへマージしません。

WindowsはこのブランチのCode→Download ZIP→LoL_AutoCine/START_GPU.bat。実行後の診断でgpu_effects_confirmed=trueとpipeline.gpu_blur_effectsのbloom/dof、NVENCはencoder=h264_nvencを別に確認し、同じ素材で速度を比較します。環境PublishはWindows取得に不要です。
