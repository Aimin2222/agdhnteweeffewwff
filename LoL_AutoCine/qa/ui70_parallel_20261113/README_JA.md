# AutoCine LoL動画編集 — 70機能 / UI候補3 (testA/T-A-M) 独立オフラインQA

2026-11-13 JST。管理工程5 OS受入14件・Phase1B OS受入10件・D11B Owner結果は**Work専属**。本ブランチはこれらに一切触れない。LoLアプリ本体の本番変更や正式受入も行わない。

## GitHub / 完了したもの

- 開発元：保護Draft PR #56 の`b4f8b0af7633da5f362ab84b901b5cde69c8adc0`から**新規独立ブランチ**`chat/ui70-readonly-qa-20261113`を作成。動画main・Draft #54/#55/#56を改変しない。管理main、Work/coordinationブランチ、Windows設定・モデル自動起動も不変更。
- `audit_ui70_core.mjs`：UI3 3系統(C3/R1/R2)・70 ID/70 section・70配置/70 binding・36 screen・86 control・239 test specs・210 route・固定原画identityを**照合する純関数**。実アプリに触れず、差異時はBLOCKED。
- `run_offline_audit.mjs`：node標準ライブラリのみ、固定8仕様ファイルのGit blob SHAを確認。symbolic link/親フォルダ遡り/入力改変は拒否、存在するbackend source pathsだけ照合。実行時JSONを標準出力に表示し**何も書き込まない**。ローカルNode上でのこの新ランナー自体は**まだ実行していない**。
- `test_ui70_contract.mjs`：仕様を意図的に破壊する30異常系を定義。独立V8 JS実行環境では同じ30変異を全て拒否できた。Nodeランナーを実際に動かしたとの証明ではない。
- `FEATURE_ROUTE_MATRIX_70x3.json`：全70機能とC3/R1/R2の提案210入口、元source path、単体/WindowsテストID、**NOT_RUN**を記録。*クリック可能・動作合格の主張ではない*。
- `QA_RESULTS.json`：今回のオフライン実証・固定ソースSHA・正式NOT_RUNを分離して記録。

## ソース仕様に基づく現状

| 指標 | 仕様照合 | 実動作証明 |
|---|---:|---|
| 70機能 / 210入口 | **70/70・210/210 整合** | **NOT_RUN** |
| 36 screen / 86 control | **36/36・86/86 仕様参照整合** | **NOT_RUN** |
| 239件の製品テストケース | **239件定義** | **0/239実行** |
| 30件の仕様破損・偽装の拒否 | **30/30 オフラインPASS** | Node/Windows現地試験は未 |
| C3候補3 原画「testA/T-A-M」 | **同一性契約保持** | Windowsピクセル比較やアプリ表示は未 |

入口クラス：**29 DIRECT_UI3、35 NATIVE_EDITOR、4 BACKEND_AUTOMATIC、2 UNIMPLEMENTED**。配置分類はMAIN8/EASY4/DETAIL2/SETTINGS12/SPECIAL39/LIBRARY5。

未実装の**ENGAGE（エンゲージ独立検出）**と**BESTSHOT（画像品質に基づくベストショット選択）**は引き続き`UNIMPLEMENTED`。既存のキル/アシスト判定・メタデータスコアとは区別して実LoL時系列/フレーム証拠が必要。今回実装済と主張しない。

## 読み取り専用の再現手順（将来の安全なQA）

動画の独立ブランチを通常Git checkoutした後、リポジトリ最上位から：

```bash
node LoL_AutoCine/qa/ui70_parallel_20261113/run_offline_audit.mjs
node LoL_AutoCine/qa/ui70_parallel_20261113/test_ui70_contract.mjs
```

Node 18以上の標準APIのみを使用。既存のNode/ローカルGit checkoutを前提とする。**ユーザーに今これを実行させる必要はない**。元JSONのGit blob SHAが変更されたら意図的にBLOCKEDになり、勝手に既存受入を更新しない。テスト結果を記録するなら標準出力から別途非機密部分だけ収集。

**注意**：`run_offline_audit.mjs`は入力SHAが全て一致したときだけ仕様整合PASSを出す。実装の機能動作や自動QAの通過・LoL実ゲーム・NVENC・音声同期・Windowsピクセル一致・実成果MP4は確認しない。本番アプリの起動も新しいモデル起動も行わない。

## 次に進む内容と分担

1. このチャット担当：70機能の実装Gapを優先度別に棚卸し、C3/T-A-M原画保全、R1/R2誤結線を防ぐオフライン型チェック、入力バリデーションやシーン状態/保存の純粋関数fixture試験を独立ブランチで追加する。
2. Work担当：管理工程5(14)、Phase1B(10)、D11B既存Owner結果とOS復旧。一方の成果物は相互に上書きしない。
3. 管理M1〜M7 0/7の正式受入後、またはユーザーの明示した優先順位変更後に、本体UI・実LoL/GPU/音声機能の正式統合/Windows E2Eを検討する。現在はあくまで隔離開発準備。

**残停止点**：239製品テストの実動作0件、2機能未実装、OS実証なし、UI動作/エンコードの本番受入なし。対応は独立テスト→安全な統合レビュー→最後にWindows一括実測。ユーザー操作**今なし**。追加費用**0円**。
