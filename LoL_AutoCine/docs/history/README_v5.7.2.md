# LoL AutoCine v5.7.2

## 音声方式変更

v5.7.2では、LoLゲーム音の録音をPython ctypes/WASAPIワーカーから、WindowsネイティブのProcess Loopbackヘルパーへ変更しました。

- LoL PIDを指定
- 対象プロセスと子プロセスのレンダー音声だけを取得
- デスクトップ全体ループバックは使用しない
- 他アプリのミュート処理は行わない
- WAVを既存のクリップ生成・MP4 muxへ渡す

MicrosoftのApplication Loopback APIと同じProcess Loopback APIを使用する設計です。

## 初回セットアップ

1. Visual Studio Build Tools / Visual Studio のC++デスクトップ開発環境を入れる
2. `BUILD_AUDIO_HELPER.bat` を実行
3. `00_AUDIO_TEST.bat` を実行
4. `[PASS] Audio test succeeded` を確認
5. AutoCineを起動

`tools/bin/lol_audio_helper.exe` が生成されれば、Python側は自動的にそれを使用します。
