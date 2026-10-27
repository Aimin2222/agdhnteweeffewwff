# 候補3の正体と統合作業の監査（2026-10-27）

## 結論

友達向け比較版の「候補3」は `testA / T-A-M / 旧テストA 現行整理`。`legacy03 / L03-N` は「候補2」。現在の独立作業ブランチの起動画面も `T-A-M` であり、番号の取り違えは確認されなかった。

## 照合した証拠

- PR #51由来の `qa/ui7_20261026/NUMBERING_JA.md` は候補3を `testA / T-A-M` と明記する。
- `ui/comparison_labels.py` の `CANDIDATE_ORDER` は3番目が `(testA, T-A-M)`、2番目が `(legacy03, L03-N)`。
- `ui/audit29_runtime.py` の起動選択は `AUTOCINE_UI3_LAUNCH=1` の場合 `self.screen_id = "T-A-M"`。原本を提供する対応は `LEGACY_RECONSTRUCTIONS = {"T-A-M": "T-A-M.html"}`。
- 原HTMLは `design/ui/ui29_legacy/T-A-M.html`。Workの原本画像は `design/ui/implementation_audit_29_20261021/references/legacy_test/A_main.png`。
- PR #51の実画面 `qa/ui7_20261026/numbered_frozen_all_final/T-A-M.png` と今回の `qa/ui3_20261027/T-A-M.png` は、左準備・中央固定ミラー・右シーン・下編集の同じ構成。両方1672×941。現在画像には右端の「全機能」入口が加わる。LoL未接続の撮影のため映像領域は黒く、原本画像との総画素差を外観合格判定に使わない。

## ベースと修正対象

- ベース: PR #54の `5feff820b8fd3ffe2b300adb17277e77d57aae91` とPR #51の `ee700835efe25c1aa65670d73e57f1fd9373bac2` を、独立ブランチ `codex/ui3-full-function-integration-20261027` の統合コミット `88ce3ad02470ff681ca7b8cdc9f72a07ed4eee4d` で結合した。
- 候補の取り違えによる修正対象はない。現在の暫定入口は `ui/audit29_client.js`、操作アダプターは `ui/audit29_runtime.py`、起動は `app.py` と `START_AUTOCINE_UI3.bat`。これらをC3-P/C3-Sの比較入口へ拡張するが、原本 `T-A-M.html` は上書きしない。
- 既存の候補1〜10、PR #49/#51/#52/#54、従来アプリ、37バッジ・89原本および承認状態は変更しない。R1/R2の配布停止済み実行コードは流用しない。

## C3-P/C3-Sと70機能の扱い

Work保存コミット `2053ab4b983a1b663490fded2ed7bf603213579b` の `design/ui/c3_refinement_20261027` は画像・静的SVG・寸法・接続提案であり、動作アプリではない。C3-Pは下部の詳細編集、数値・トラック・キー操作の提案、C3-Sは下部のかんたん編集、カードと素材選択の提案として、元の候補3と並べて比較する。候補3の左/中央/右/下の構造を維持する。

70機能の現状は `UI3_FEATURE70_CONNECTION_20261027.csv` に全行記録した。29件は候補3から直接操作、35件は既存の実動作エディタへの入口、4件はバックエンド内の自動処理、2件（ENGAGE、BESTSHOT）は未実装。これは到達経路の分類で、実LoLやGPUの動作合格ではない。Workの `FEATURE_BINDINGS_70.json` のhandler名も提案であり最新実装保証ではない。接続後のテスト結果は機能ごとにPASS/FAIL/REVIEW/NOT_RUNで別管理する。

## 復旧方法と試験順序

本ブランチの作業は別worktreeで行い、PR #51/#54とmainには書き込まない。統合開始前の復旧点は `88ce3ad02470ff681ca7b8cdc9f72a07ed4eee4d`。以後の作業を分離コミットし、必要な変更だけ `git revert` できるようにする。PR #54の総合QA結果とログは元ブランチに保持する。

順番はC3比較と操作接続、BATによる起動・小規模回帰、BAT ZIPの検査、最後に実LoL総合QA。未実施項目はNOT_RUNと明記する。
