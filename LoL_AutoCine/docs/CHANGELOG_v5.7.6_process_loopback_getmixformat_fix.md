# LoL AutoCine v5.7.6 – Process Loopback GetMixFormat 修正

## 修正内容

- Windows の `VIRTUAL_AUDIO_DEVICE_PROCESS_LOOPBACK` で `IAudioClient::GetMixFormat()` が `0x80004001 (E_NOTIMPL)` を返すケースに対応。
- Microsoft の Application Loopback サンプルと同じく、キャプチャ形式を PCM 16-bit / 2ch / 44100 Hz に固定。
- `AUDCLNT_STREAMFLAGS_AUTOCONVERTPCM` により Process Loopback 側から指定形式へ変換。
- `_wfopen` を `_wfopen_s` に変更。
- これにより今回の `GetMixFormat failed: 0x80004001` で録音開始前に停止する問題を回避する。

## 参考

Microsoft の Application Loopback サンプルでは、Process Loopback 用 `IAudioClient` に対して `GetMixFormat` を使わず、PCM 16-bit / 2ch / 44100 Hz を指定して `Initialize` している。

## 注意

この環境では Windows/MSVC と LoL の実音声を実機テストできないため、Windows 上でのビルド・録音成功そのものは未確認。
