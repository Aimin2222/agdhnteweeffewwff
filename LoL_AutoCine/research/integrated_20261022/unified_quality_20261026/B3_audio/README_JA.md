# B3 ゲーム音声・同期の実行可能範囲
今回の新規実行は48kHz mono合成880Hz pulse(.5/1.5/2.5秒)と合成flash映像のAAC/MP4 encode/mux/full decode。音を再生せずファイル数値解析を実施。LoL/システム/他アプリ音声の収録0。

4診断assertion PASS: 通常3秒、映像2倍長＋atempo.5、意図的に映像だけ伸長、意図的に音声なし。最後2つのPASSは不良出力を診断できた意味で、出力合格ではない。通常の時間長差約8ms、正しいslow約14.7ms、誤ったslow約2.959秒。音声なしstreamを検出。AV_FIXTURE_RESULTSにactual PTSと全frame時刻、音声envelope onsetを保存。

slowの映像flashは.966667/2.966667/4.966667秒、音声onsetは.96/2.97/4.97秒。対映像onset最大約6.7ms（10ms envelope測定）。理想的な1/3/5秒に対しては映像が約33ms早い。duration許容.1秒PASSだけで同期全合格にはしない。atempo/時刻変換/encoder frame複製を含むevent同期はREVIEW。

最初の測定では自動選択された15fpsを30fpsと仮定してしまったため無効化した。現結果は-r30 -fps_mode cfrを明示、FFmpeg showinfoでPTSを取得し、passthrough全decode枚数と照合して修正済み。過去の測定ミスを製品不具合として扱わない。ffprobeは環境になく、インストールしなかった。

既定はLoLの対象PID＋子プロセスだけ。全デスクトップloopbackへ黙ってfallbackしない。ゲーム音必須か無音許可かをjob設定で分離し、helper未起動/streamなしは明示停止かユーザー許可済み方針へ。CPUとNVENC双方で同じ基準PTS、concatでは各segmentのvideo/audio開始とdurationを照合する。実ゲーム音、複数クリップconcat、長尺drift、GPU/CPU差、参考20本の実音源解析はNOT_RUN。音源と実Replay/録画環境が必要。

参考: [Microsoft process-loopback sample](https://learn.microsoft.com/en-us/samples/microsoft/windows-classic-samples/applicationloopbackaudio-sample/) は対象process treeのinclude/exclude取得設計を示す。既存helperがこの契約を実機で満たすかは別検証。再実行audio_fixtures.py。
