# Issue #3 数値入力の限定回帰（2026-10-29）

## 対象と変更

- 基準: PR #55 の `7cc6986565ef74973dc235aae4ff1d6d6d899eb0`、Workの管理Issue #1コメント `6477657691`、優先Issue #3。
- R1/R2の数値欄、候補3の数値欄で空欄を `Number('') === 0` として送信し得た経路を修正。空欄、`badInput`、非有限、範囲外、step不一致を送信前に拒否し、実Appの既存値を欄へ戻す。エラー文、赤枠、`aria-invalid` を表示する。明示的な0は有効値として送信する。
- R1/R2の再描画後もエラー表示を保持。候補3の前後トリム欄は実App状態と同期する。
- キーフレームの追加・更新で空欄や無効な数値を0として送らない。実シーンなしでのキーフレーム操作は未検証。

## 今回実行した検証

| 対象 | 結果 | 証拠・範囲 |
|---|---|---|
| R1 League Director | PASS | Windows WebView2で露出0.12→空欄確定、無効文字代入、範囲外9を拒否。実App値0.12保持。明示0と画面切替後の0保持、カメラYaw32→空欄保持→0を確認。`webview/index.json`、`issue3_reference-ld_*.png`。 |
| R2 Lolnam | PASS | 同上。`webview/index.json`、`issue3_reference-ln_*.png`。 |
| 候補3 T-A-M | PASS | 同上。メイン→詳細→メインの切替後の0保持、前トリム6→空欄→定期更新後も6を確認。`webview/index.json`、`issue3_T-A-M_*.png`。 |
| 既存R1操作フロー | PASS | `reference_regression/index.json`。カメラ・素材と同名FX・色・FPS/encoder設定の限定的な実App操作。実GPUエンコードは未実施。 |
| 既存候補3操作フロー | PASS | `candidate3_regression/index.json`。候補3の限定操作と設定保持。 |
| 対象pytest | PASS | `tests/test_ui3_integration.py`、`tests/test_ui29_runtime.py`、`tests/test_ui29_desktop.py` は34 passed、24 subtests passed。 |

WebView2試験は実Windowsの埋め込みWebView2で数値欄へ `input`/`change` イベントを送った。無効文字 `abc` はChromiumの `type=number` が空欄へ正規化したため、**実キーボードによる `badInput` 状態と物理Tab操作はNOT_RUN**。`validity.badInput` のコード経路は防御を入れたが、実操作PASSには含めない。初回実行でR1の定期再描画が赤枠を消す問題を検出し、修正後の再試験でPASS。テストのボタン探索ミスも修正し、最終 `index.json` は3画面とも成功。

## 残件

- Work M02: 実Appの `_replay_generation` とUI `action_revision` を状態応答に追加し、R1/R2/候補3のクライアントで古い世代・改訂の応答を採用しない。候補・テーマ保存失敗時の選択復元を追加し、単体テストと既存Windows操作フローで限定PASS。リプレイAの遅延応答→Bの競合試験、Project/Template/Sceneの型付き保存と失敗復元、Undo/Redo一般化、旧schema移行は未完了。M02全体PASSではない。
- Work M03: 70既存＋16追加能力のC3/R1/R2全画面での入力→状態→保存→出力の追跡は未完了。キーフレーム実シーン操作、LUT、scene色overrideなどは未接続またはNOT_RUN。
- 実LoL、GPU/NVENC、音声、録画、MP4、125/150% DPI、239件の完全受入はNOT_RUN。21画面の画像忠実度はREVIEWのまま。
- PR #55はDraftを維持し、mainへのマージは行っていない。
