# LoL AutoCine v5.7.7 - Native Helper Capture Client Fix

## 修正

- `IAudioCaptureClient` の取得処理を追加。
- `IAudioClient::Initialize()` 後に `client.As(&captureClient)` を実行し、Process Loopback のキャプチャループで使用する `captureClient` を正しく初期化。
- これにより `captureClient` 未定義による MSVC C2065 ビルドエラーを解消。
- `ComPtr` でライフタイムを管理し、手動 Release を不要にした。

## 対象

- `tools/native_audio/lol_audio_helper.cpp`

## 注意

Windows/MSVC 実環境でのコンパイル・LoL Process Loopback の実機動作はこの環境から直接検証できないため、今回の修正はユーザー環境のビルドログで確認された C2065 に対するソース修正です。
