# 全29画面 UI進捗・テスト結果

監査元：`design/ui/implementation_audit_29_20261021/`。全12候補を最終対象として維持。最終UIは未選定。

## 今回確認したこと

- 原画像・個別仕様・SHA-256・寸法：29画面を照合。
- 新18画面：既存AutoCine Appに接続したローカルUI経由で、LoL未接続のEdge画像・DOM矩形・50%重ね・差分を保存。
- Appブリッジ（候補切替、テーマ、カメラ側・距離、登場アニメ、監査済み素材）：PASS。
- LoLリプレイ接続、WGCミラー、カメラ実映像、GPU/NVENC、ゲーム音、録画、MP4出力：**このブランチでは未実施**。
- 旧11画面：編集可能な原HTMLがないため、コードとしての忠実な再構成は未実装。原画像を押せるだけの画面として扱わない。

`MEASURED` は寸法比較を実行した意味。目視審査・機能合格ではない。`REVIEW` は矩形差が許容外。

## 29画面一覧

| ID | 候補 | 実装 | オフライン視覚 | 映像外RGB差/255 | 矩形 ±2px | LoL実機 |
|---|---|---|---|---:|---:|---|
| L02-M | 旧案2 標準編集 | 未実装 | NOT_RUN | — | — | NOT_RUN |
| L03-D | 旧案3 ハイブリッド | 未実装 | NOT_RUN | — | — | NOT_RUN |
| L03-N | 旧案3 ハイブリッド | 未実装 | NOT_RUN | — | — | NOT_RUN |
| L05-M | 旧案5 ウィザード | 未実装 | NOT_RUN | — | — | NOT_RUN |
| L06-E | 旧案6 ライブラリ／編集 | 未実装 | NOT_RUN | — | — | NOT_RUN |
| L06-L | 旧案6 ライブラリ／編集 | 未実装 | NOT_RUN | — | — | NOT_RUN |
| T-A-M | 旧テストA 現行整理 | 未実装 | NOT_RUN | — | — | NOT_RUN |
| T-B-S | 旧テストB カメラ・FX | 未実装 | NOT_RUN | — | — | NOT_RUN |
| T-B-C | 旧テストB カメラ・FX | 未実装 | NOT_RUN | — | — | NOT_RUN |
| T-B-F | 旧テストB カメラ・FX | 未実装 | NOT_RUN | — | — | NOT_RUN |
| T-B-M | 旧テストB カメラ・FX | 未実装 | NOT_RUN | — | — | NOT_RUN |
| R-A-main | 新A Studio | 部分実装 | REVIEW | 9.7284 | 12/23 | NOT_RUN |
| R-B-main | 新B Creator | 部分実装 | MEASURED | 0.7406 | 15/15 | NOT_RUN |
| R-C-main | 新C Director | 部分実装 | REVIEW | 0.4395 | 14/15 | NOT_RUN |
| R-D-main | 新D Highlights | 部分実装 | MEASURED | 1.056 | 12/12 | NOT_RUN |
| R-E-main | 新E Flow | 部分実装 | MEASURED | 0.4049 | 13/13 | NOT_RUN |
| R-F-main | 新F Killbeat | 部分実装 | REVIEW | 2.7946 | 11/18 | NOT_RUN |
| R-A-main-dark | 新A Studio | 部分実装 | REVIEW | 8.188 | 12/23 | NOT_RUN |
| R-E-main-dark | 新E Flow | 部分実装 | MEASURED | 0.406 | 13/13 | NOT_RUN |
| R-A-camera | 新A Studio | 部分実装 | REVIEW | 4.7227 | 13/25 | NOT_RUN |
| R-A-frames | 新A Studio | 部分実装 | REVIEW | 3.5286 | 11/16 | NOT_RUN |
| R-E-studio | 新E Flow | 部分実装 | REVIEW | 4.2912 | 13/23 | NOT_RUN |
| R-E-frames | 新E Flow | 部分実装 | REVIEW | 3.5288 | 11/16 | NOT_RUN |
| R-A-main-1366x768 | 新A Studio | 部分実装 | REVIEW | 3.7992 | 13/23 | NOT_RUN |
| R-B-main-1366x768 | 新B Creator | 部分実装 | REVIEW | 1.1127 | 11/15 | NOT_RUN |
| R-C-main-1366x768 | 新C Director | 部分実装 | REVIEW | 0.7225 | 11/15 | NOT_RUN |
| R-D-main-1366x768 | 新D Highlights | 部分実装 | MEASURED | 0.933 | 12/12 | NOT_RUN |
| R-E-main-1366x768 | 新E Flow | 部分実装 | REVIEW | 0.5753 | 12/13 | NOT_RUN |
| R-F-main-1366x768 | 新F Killbeat | 部分実装 | REVIEW | 3.7609 | 11/18 | NOT_RUN |

## 残る合格条件

1. 旧11画面を原画像の配置・操作順でコードから再構成し、12候補すべてを同じAppで切り替える。
2. 新18画面を含む全操作部品を監査F01〜F25へ接続し、表示例を実データへ置換する。エンゲージは専用実装ができるまで未対応と表示する。
3. 全29画面で実装画像・重ね合わせ・差分・寸法を審査し、表示倍率125%も確認する。
4. 実際のLoLリプレイでスキャン、TargetLock、BLUE/RED、固定自動・フルオート、FX、WGC、GPU/NVENC、LoL音声、MP4出力を機能別に合否記録する。
5. 合格したコミットからポータブルEXE/ZIPを作り、起動・操作・保存・書き出しを実機で確認する。mainへのマージはユーザー承認待ち。
