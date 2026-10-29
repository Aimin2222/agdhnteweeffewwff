# UI候補3・カメラ・FX 差分検証（2026-10-29）

対象ブランチ: `codex/ui3-camera-fx-regression-20261029`。起点はDraft PR #55の`e3bb364327f4a2a1e2f3826aafc2417c8c7d6250`。PR #55、#54、mainを変更しない。

## 変更

- R2 Shot Canvasの1366×768表示で、右のツールボタンの最小高さが中央プレビューの操作列を押し下げ、ショット列と重なっていた。820px以下の画面高でツール列を縮め、中央の操作列とショット列を分離した。
- Windows WebView2撮影の寸法検査に、中央操作列、ショット列、タイムライン見出しの順序を追加した。以前の検査はプレビュー本体とタイムライン外枠しか測っておらず、この重なりを見逃していた。

## 実測結果

| 項目 | 結果 | 証拠 |
|---|---|---|
| R2 1366×768、操作列とショット列の重なり | PASS | [修正前](ln_before/LN_main_light_1366x768.png)、[修正後](ln_after/LN_main_light_1366x768.png)。操作列bottom=558、ショット列top=567、タイムライン見出しtop=604。文書高さ=768。 |
| R2 1920×1080の中央プレビュー高さ | PASS | [修正後](ln_after/LN_main_light_1920x1080.png)、撮影データで539px。 |
| R2カメラ回転角のUI→設定→再表示 | PASS | Windows WebView2撮影フローの`camera_yaw_roundtrip`。画面は`third_yaw`を使用し、ランタイムの同じキーに送る。 |
| カメラ・FX・UI3対象回帰 | PASS | Windowsで75件PASS。対象はcamera axes、mode isolation、BLUE6、Orbit TargetLock、Flash、Zoom、UI3 integration。 |
| UI29既存回帰 | PASS | Windowsで23件PASS、24 subtests PASS。 |
| 候補3の4スライダー・リセット・素材3切替・比較ボタン | REVIEW | PR #55起点に実装がある。今回の差分では変更せず、個々の実機受入は未完了。比較ボタンは真の比較が未接続のため理由付き無効化を維持。 |
| Work素材 | REVIEW | `AUDIT_20261019.json`で静止フレーム正式合格1/652、FX35件は確認用。正式承認状態は変更していない。 |
| LoL接続・GPU/NVENC・音声・録画・MP4・125% DPI | NOT_RUN | 今回の対象外。 |

最初のサンドボックス内テストでは一時フォルダ作成とlocalhostソケットが拒否された。Windows権限で同じ対象を再実行し、上記98件＋24 subtestsを確認した。エラー原文はローカルのみ保存し、GitHubには載せない。

## 保護・残課題

- `third_cinema`、TargetLock座標計算、Flash/Zoom演算、正式素材は変更していない。
- 284件受入台帳の過去判定を上書きしていない。各項目のWindows実操作とLoL総合試験は別途必要。
- 試験版配布前に、BAT起動、ミラー、LoL、録画、音声、出力先、MP4を実機で確認する。
