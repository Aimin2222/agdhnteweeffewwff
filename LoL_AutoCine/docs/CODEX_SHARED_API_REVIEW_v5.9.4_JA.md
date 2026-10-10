# v5.9.4 共有APIレビュー

受領パッチはv5.9.3統合版への `git apply --check` が成功。
全ファイルではなくパッチの共有差分だけを `feature/gpu-engine` へ取り込んだ。
同梱camera.py全体には旧位置引数・キーなしFOVの互換性修正がないため、上書きしない。
UIと新規UIテストは別の `feature/ui-preview-v594` へ保存する。

## 接続点

- `CameraDirector._run` の経過時間上限を80msから250msへ変更。
- `SmoothReplayClock.advance` の上限を100msから250msへ変更。
- `preview_clip` は終了時に既存Directorの成功render回数・遅延・時刻ずれをログへ記録する。
- 上記の関数署名、CameraPlanとTemplateの旧位置引数、キーなしFOV、TargetLock座標・校正を維持。
- UIは未保存のShotをUIスレッドで取得し、deep copyしたTemplateと選択Killを既存プレビューworkerへ渡す。
  保存済みプロジェクトを変更せず、レンダラへTk値を持ち込まない。

通常の105〜180ms待ちを時計へ反映する一方、250msを超える停止では依然上限が働く。
HTTP呼出しそのものの高速化や非同期化は含まない。プレビューは録画せずLoLの再生位置・カメラを操作する。
終了後の停止、HUD・ゲーム内FX復元は既存経路を使う。
診断回数と待ち時間は成功したset_renderが対象で、すべてのGET/失敗した呼出しを計測した値ではない。

## 検証

共有カメラ回帰とGitガード45テスト成功。
模擬時計を用いDirectorの実ループで105msのrender待ちが切り捨てられないことを確認。
250msの停止上限と一時停止中の非進行、旧API位置引数・FOVも確認。
cameraのAST比較で変更がDirectorのrunだけに限定されることを確認した。
保護されたGPU・録音等の実行ファイル12個はv5.9.3とバイト単位で同一。

共有レビューJSONは基準コミットとこの3ファイルのmode/blobだけを承認する。
後続変更、他方担当の変更、巻き戻しは再レビューが必要。
Windows・実LoL・GPU・Native録音の実機成功は主張しない。
