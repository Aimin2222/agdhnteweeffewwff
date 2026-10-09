# v5.7.3 - Native Audio Helper Build Flow

## 目的

前版では `lol_audio_helper.exe` が存在しない場合に Python 側でエラー終了し、ビルド失敗の原因が分かりにくかったため、ヘルパー生成と音声テストの入口を整理した。

## 変更点

- `00_AUDIO_TEST.bat` が helper EXE の存在を自動確認。
- EXE が無い場合は `BUILD_AUDIO_HELPER.bat` を自動実行。
- ビルドログを `diagnostics/native_audio_build.log` に保存。
- コンパイラ未検出、コンパイル失敗、EXE未生成を個別に判定。
- ビルド成功後に helper EXE の存在を再確認。
- `CHECK_AUDIO_HELPER.bat` を追加。
- 手動ビルド用 README を追加。

## 注意

この変更はビルドフローの改善であり、Windows 上の Process Loopback 音声取得がこの環境で実機確認済みという意味ではない。実際の LoL 音声取得テストはユーザー環境で `00_AUDIO_TEST.bat` を実行して確認する。
