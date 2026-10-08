# v5.7.2 Native Process Loopback Audio

## 変更

v5.7.0までのPython ctypesによるProcess Loopback実装を録音経路から外し、WindowsネイティブのC++ヘルパーへ切り替えました。

### 音声

- `tools/native_audio/lol_audio_helper.cpp` を追加
- `BUILD_AUDIO_HELPER.bat` を追加
- `tools/bin/lol_audio_helper.exe` が生成されるとPython側が自動使用
- `ActivateAudioInterfaceAsync` を使用
- `AUDIOCLIENT_ACTIVATION_TYPE_PROCESS_LOOPBACK` を使用
- `PROCESS_LOOPBACK_MODE_INCLUDE_TARGET_PROCESS_TREE` を使用
- LoL PIDと子プロセスのレンダー音声だけを対象
- デスクトップ全体ループバックへのフォールバックは禁止
- 他アプリのミュートは禁止
- WAVはPCM16として出力

## 初回セットアップ

`BUILD_AUDIO_HELPER.bat` を一度実行してください。

Visual Studio Build Toolsが未導入の場合は、C++デスクトップ開発とWindows SDKが必要です。

## 注意

この環境ではWindows上のMSVC実機ビルド・LoL実機録音までは実行できないため、配布物にはソースとビルドスクリプトを同梱しています。
