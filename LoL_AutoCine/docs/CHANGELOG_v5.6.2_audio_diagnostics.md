# v5.6.2 音声診断・ログ強化

## 変更

- `diagnostics/audio.log` を追加
- 音声方式、LoL PID、WASAPIデバイス、プロセスループバック開始/停止、フォールバック理由、WAV検証を記録
- クリップ作成時の音声開始/停止/検証もログへ記録
- `00_AUDIO_TEST.bat` を追加（初回に最初に実行する用）
- `SOUND_TEST.bat` を追加/強化
- 5秒間の実録音によるLoLゲーム音テスト
- `diagnostics/audio_test_result.json` に結果を保存
- `OPEN_AUDIO_LOG.bat` を追加
- `tools/sound_test.py` でPyAudioWPatch、LoL PID、WASAPI、実音声信号を診断
- サウンドテスト失敗時にAutoCineの本番出力へ進む前に原因を切り分けやすくした

## 基本フロー

`00_AUDIO_TEST.bat` → `[PASS]` → `START.bat` → AutoCine

ゲーム音ONなのに録音できない場合は、無音MP4を成功扱いせず、音声エラーと診断ログを残します。
