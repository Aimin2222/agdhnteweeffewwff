# AutoCine v5.10.26 — バージョン判定・空/マップ外の検知・ZIP CI復旧

## 根拠と重要な発見
- ユーザーが送った `results(20261012-175926).json` の実行版は **5.10.23-test**。同時に送った比較画像でBLUE8/9/10が空やマップ外を映していたが、**5.10.25実行の証拠としては利用できない**。異なるビルドを比較すると角度が良くなったカメラを再び壊すリスクがある。
- 失敗した `autocine/v5.10.25-blue6-vertical-frame-qa` のGitHub Actionsでは、Codex差分ZIPを作る際、`with zipfile.ZipFile(diff, ...)` の外側に2行の `z.write` があり、`ValueError: Attempt to write to ZIP archive that was already closed` を引き起こした。該当ブランチにインデント修正済み。
- 同じ失敗ブランチの以前のテストではBLUE6の補正がX=-4.0なのに過去X=3.0を期待して失敗。該当ブランチのコードにはX=-4.0を期待する更新済みのテストがある。ただし、この値の実機での優位性は不明。
- **v5.10.26は前回成功済みブランチ** `autocine/v5.10.25-blue6-framing-reference-handoff` に基づく。BLUE6の角度はX=-2.0のまま、その他9カメラも変更しない。壊れた実行履歴や誤ったビルドの比較画像を根拠に直感的な角度変更を重ねない。

## 今回追加した機能
1. `core/camera_qa.py` の results.jsonに `version=5.10.26-test`、実際の `VERSION.txt` の内容 `installed_version`、`camera.py + camera_tuning.py` の内容をSHA256化した `camera_code_fingerprint`、バージョン不一致フラグ `version_mismatch` を保存。QA_Support/READ_ME_FIRST_JA.mdにも版と識別子を書き込む。
2. `core/qa_visual.py` の `flat_upper_background_ratio` で実MP4から抽出した **PRE/KILL/POSTの3枚**について、画面上部55%に似た色の広い領域がないかを数値化。2/3以上のフレームで上部の約50%が単色に近ければ`suspected_sky_or_empty_frame`、その他の疑わしい項目は`framing_needs_human_review`へ保存する。
3. この単色判定は **AIによるキル視認判定ではない**。空以外の平坦地形、壁、暗所でも反応するかもしれないため、危険と判定したケースを人間が比較映像で確認する補助情報に限る。既存のQA自動録画、GPU/NVENC、ゲーム音、HUD、全10カメラの動作値は変更しない。
4. GitHub ActionsのWindows日本語MP4/動画ZIPとLinux回帰全件、Codexパッチの適用確認、ZIPのCRC/SHAを通過してから配布する。

## Windowsでしてほしいテスト
1. [ ] v5.10.26 WindowsフルZIPを**前の版とは別の新しいフォルダー**へ解凍。`VERSION.txt` が`5.10.26-test`と表示されるか。
2. [ ] 開発用一括QAボタンを押し、接続→試合全体スキャン→RED/BLUEそれぞれ5モード→切替比較→画像→500MB分割ZIPを自動生成。
3. [ ] 新しく出た`results.json`に `version` と `installed_version` が両方 `5.10.26-test` とあるか。もし違うなら古い起動プログラムやフォルダー違いを疑う。
4. [ ] BLUE 8/9/10の**PRE・KILL・POST**で空やマップ外が映っていないか、`visual_qa.camera` の `flat_upper_background_ratio` / `suspected_sky_or_empty_frame` と比較する。
5. [ ] RED 1・3、RED 2・4・5の良い構図が維持されているか。
6. [ ] BLUE6のPREで主役と敵が見えるか。問題があるときは新しい座標・画像を添付する。
7. [ ] xMedia動画ZIPを `MAKE_REFERENCE_SHEETS.bat` へドラッグし、比較画像ZIPの場所が表示されるか。
8. [ ] LoLゲーム音、1080p60、NVENC、HUD非表示/ミラー、37種のキルフレームで回帰がないか。
9. [ ] 生成された全CameraQA part ZIP、results.json、比較画像、diagnostics ZIPを送る。**ユーザーが『完了』と言うまでは次の修正を始めない。**

## 配布とCodex
- Windows用フル版ZIPとCodex v5.10.15からの累積差分ZIPを別々に配布、二重ZIPなし。
- Codex本家のGPU Full/録画/LoLゲーム音/非同期プレビューは旧版で上書きしない。
- PR #29はdraft/open、mainやCodex側へ自動でマージしない。
- Python/コンテナが`InvalidArgumentError`で生MP4を直接開けない場合はそのまま申告し、動画を見たと偽らない。
