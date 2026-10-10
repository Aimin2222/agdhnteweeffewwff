# LoL AutoCine v5.6.2 音声診断

## 初回にやること

1. LoLリプレイを再生する
2. ゲーム音が鳴る状態にする
3. `00_AUDIO_TEST.bat` を実行
4. 5秒間の実録音テストを行う
5. `[PASS]` なら `START.bat` でAutoCineを起動

## ログ

- `diagnostics/audio.log` : 音声方式、LoL PID、WASAPI、フォールバック理由、録音開始/停止、WAV検証
- `diagnostics/audio_test_result.json` : 最後のサウンドテスト結果
- `diagnostics/lol_audio_test.wav` : テスト録音

## 失敗時

1. `REPAIR_AUDIO.bat`
2. PCの再起動（WASAPI/デバイス状態が怪しい場合）
3. `00_AUDIO_TEST.bat`
4. `OPEN_AUDIO_LOG.bat` で `audio.log` を確認

## 重要

プロセスループバックを第一優先にし、利用できない場合のみフォールバックします。
フォールバック時はログに理由を残します。

ゲーム音がONなのに録音できない場合、AutoCineは無音MP4を成功扱いせず、クリップを失敗として明示します。
