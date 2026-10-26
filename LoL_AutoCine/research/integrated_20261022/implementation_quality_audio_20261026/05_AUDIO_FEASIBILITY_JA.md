# 音声分析の実行可能性と今回の実行結果
## 結論の修正
聴取用ツールがないことと信号解析が不可能なことは別。既存FFmpegとNumPyのみで、音声fileのdecode/peak/RMS/DC/無音候補/左右相関/LUFS・true peak計測を実行できた。新しいソフトのinstallや音声再生、OS音量変更はしていない。
現在のFFmpegの版・hash・filter可否はAUDIO_ENVIRONMENT。研究フォルダー2か所の既存media120件をprobeし、44件にaudio streamがあったが、すべて既存の人工AV試験素材。参考20作品の実音源は対象範囲で0件。PC全体の私的ファイルは探索していない。

## 実行した解析
48kHz/stereo/3秒の人工WAV7件（無音、440Hz左右音量差、逆相、clipped plateau、DC、4pulse、右30ms delay）を生成し、FFmpeg astats/ebur128/silencedetectとNumPyで測定。7件の既知入力oracleに合格。左右30msをFFT相関で検出。pulse候補は0.5/1.0/1.5/2.0秒を10ms窓で検出。逆相を単純monoへ足すと消えることも確認した。
RMS dBFSはLUFSではなく、sample peakとtrue peakも別。無音の−∞はJSONでnull＋silence状態として表現。信号検出のonsetを音楽のbeat/小節/キル効果音と断定しない。ラウドネス値の0への自動正規化やmono合成は実施していない。
公式：[astats](https://ffmpeg.org/ffmpeg-filters.html#astats-1)、[ebur128](https://ffmpeg.org/ffmpeg-filters.html#ebur128-1)。全実測ログはaudio_lab/*_ffmpeg.log、WAVの生成器とhash、数値結果を同梱。

## 20作品の状態
20件すべてNOT_RUNのまま。今回は映像を再生せず、新規の参照音声も取得していない。音楽/ゲーム音/声の内容や同期を聴いたと報告しない。字幕や映像Flashを音声の代用にしない。未観測のダウンロードURLや保護回避による取得はしない。

## 必要条件と後続手順
1. ユーザーが共有できる音声付き動画/音源、またはサービスが正規に提供する利用可能な取得手段。作品ID/URL、許可範囲、元sample rate/channels、全体のoffsetを付ける。
2. 1本ずつsource hash/PTSをprobe。元音源を読み取り専用で保持し、解析用PCMを別に生成。可逆圧縮/低音量再生を使い、Windows全体音量は変えない。
3. fullworkのpeak/RMS/LUFS/truepeak/無音区間、channel別onset/相関、短時間スペクトルの候補を測定。48kHzへのresampleやmonoの前後を区別する。
4. 映像eventとの同期は通常速度・同一PTSで確認。倍速の印象で判定しない。冒頭だけでなく中盤/終端のdriftを分離。AAC delay/encoder priming/間欠frameを記録する。
5. 音楽beat候補・sfx候補を人手で聴取確認。聴取手段がなければ信号候補まで。source separation/ASRは今回未導入で、音量の急変や音楽の意味は自動で確定しない。
合格は実素材入力・手段・解析範囲を伴う場合のみ。人工7件の成功で20本の音声分析を完了にしない。
