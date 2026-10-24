# UI29候補切替の導線（2026-10-24）

- 変更コード: `de87eb1`。29画面の各画面の右端に「UI比較」タブを設置。押すと12候補グループ、全29個別画面、12候補一覧への入口が開く。従来の `Ctrl+Shift+U` も使える。候補変更は既存の単一AutoCine Appへの `screen` 操作であり、カメラ・シーンの再初期化処理は加えていない。
- 入口: 配布ZIPを展開し `LoL_AutoCine_UI29.exe` を起動。初回は12候補一覧が表示される。従来の `LoL_AutoCine.exe` は別の9案入口で、UI29の切替には使わない。
- Windows EXE実画面: `switching_webview2/R-B-main.png`。1920×1080、LoL未接続。右端タブが既存の上部メニューを隠さないことを画像で確認。画面操作の全項目およびLoL実接続は未検証。
- 検査: JavaScript構文チェック成功。UI29ランタイムとWebView2設定の対象テスト11件成功。ZIPビルダーのファイル検査、ZIP CRC、EXEバックエンドスモーク成功。
- ZIP: `builds/ui29-switch-20261024-de87eb1/LoL_AutoCine_UI_Comparison_Portable.zip`（作業フォルダ直下）。2,068,497,521バイト、SHA-256 `94130B553DCCAD5D4351A533278941F90F8E750E9BE0BC5E978ED6F408F5A11D`。Microsoft WebView2 Fixed Version x64を同梱。
- 残作業: 配置寸法の要修正9画面、旧11画面の外観、全29画面の目視受入、1366×768と125% DPIでの操作、LoL実機接続は未完了。このZIPは比較途中版であり、完成版ではない。

追記（2026-10-24）：右端「UI比較」パネルに配色選択（ライト／ダーク／Windows追従）を追加。配置寸法の旧9画面は次の凍結EXE一括撮影で許容内となった。最新の比較途中版ZIPは `L02_TOOLBAR_20261024_JA.md` を参照。旧11画面の外観と操作は引き続き作業中。

最新追記（`423e7a5`）：上記ZIPは履歴。現在の比較途中版は `builds/ui29-layout-20261024-423e7a5/LoL_AutoCine_UI_Comparison_Portable.zip`。Windows EXEで29画面を再撮影し、監査矩形は29/29許容内。外観合格・LoL実機合格ではない。詳細とSHA-256は `FROZEN_INCREMENT_423e7a5_JA.md` を参照。

現在の比較途中版は `builds/ui29-layout-20261024-c5ae7e1/LoL_AutoCine_UI_Comparison_Portable.zip`。Windows EXEで29画面を再撮影。旧案3を更新。詳細とSHA-256は `L03_FROZEN_20261024_JA.md`。右端「UI比較」から12候補／29画面を選ぶ操作は同じ。

最新の比較途中版は `builds/ui29-layout-20261024-3966401/LoL_AutoCine_UI_Comparison_Portable.zip`。旧案5を更新。詳細とSHA-256は `L05_FROZEN_20261024_JA.md`。初回の12候補一覧、右端「UI比較」、`Ctrl+Shift+U` の操作は維持。

現在の比較途中版は `builds/ui29-layout-20261024-47dbc95/LoL_AutoCine_UI_Comparison_Portable.zip`。旧案6のライブラリ／編集を更新し、実素材を選択したまま切替可能。Windows EXE全29画面の新しい検査とSHA-256は `L06_FROZEN_20261024_JA.md`。上記ZIPは履歴。

最新の比較途中版は `builds/ui29-layout-20261024-027b000/LoL_AutoCine_UI_Comparison_Portable.zip`。旧テストB主画面を更新。初回の12候補一覧、右端「UI比較」、`Ctrl+Shift+U` は同じ。検証証拠とSHA-256は `TEST_B_FROZEN_20261024_JA.md`。

現在の比較途中版は `builds/ui29-layout-20261024-46c4dbe/LoL_AutoCine_UI_Comparison_Portable.zip`。旧テストBカメラ設定画面を更新。初回の12候補一覧、右端「UI比較」、`Ctrl+Shift+U` は同じ。検証証拠とSHA-256は `TEST_B_CAMERA_FROZEN_20261024_JA.md`。上記ZIPは履歴。

最新の比較途中版は `builds/ui29-layout-20261024-c13500a/LoL_AutoCine_UI_Comparison_Portable.zip`。旧テストBキル演出画面を更新。初回の12候補一覧、右端「UI比較」、`Ctrl+Shift+U` は同じ。実カタログ素材とmotionを操作可能だが、LoL実機での合成は未検証。検証証拠とSHA-256は `TEST_B_EFFECT_FROZEN_20261024_JA.md`。上記ZIPは履歴。
