# v5.6.1 音声修正版

## 最初に

1. 旧版を別フォルダに残したまま、このフォルダを新しく展開してください。
2. `START.bat` を実行して依存関係を更新してください。
3. LoLリプレイを再生して音が出ている状態で録画してください。
4. それでも音が取れない場合は `REPAIR_AUDIO.bat` を実行してから `START.bat` を再実行してください。

## 音声経路

1. Windows WASAPI Process Loopback で LoL プロセスだけを録音
2. Process Loopback が使えない場合は PyAudioWPatch + WASAPI loopback を使用
3. フォールバック時は録音中だけ LoL 以外のオーディオセッションをミュート
4. 録音WAVを映像レンダー後にAACとして最終MP4へmux
5. 完成MP4にAudioストリームが存在するか自動検証

## v5.6.1の修正

- 音声ワーカーの警告がSTARTプロトコルを壊さないよう修正
- Python warningを抑制し、START/ERRORまでプロトコル行を待つ方式に変更
- `return` in `finally` 警告を修正
- PyAudioWPatchをWindows依存関係へ追加
- `REPAIR_AUDIO.bat` を追加
- 新規追加エフェクトは初期状態を全てOFF
