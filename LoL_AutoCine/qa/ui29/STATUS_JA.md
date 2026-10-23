# 全29画面 UI進捗・テスト結果

監査元：`design/ui/implementation_audit_29_20261021/`。全12候補を最終対象として維持。最終UIは未選定。

## 今回確認したこと

- 原画像・個別仕様・SHA-256・寸法：29画面を照合。
- Windowsソース版デスクトップホストのWebView2実描画を29画面撮影し、原画像との50%重ね・絶対差分・DOM矩形を保存。16画面は矩形許容内、13画面は矩形要修正。画像の合格判定とは別。
- 新18画面・旧テストA・旧10画面：既存AutoCine Appに接続したUI経由で、LoL未接続のEdge画像・DOM矩形・50%重ね・差分を保存。最終審査はWindowsアプリ実画面で再実施する。
- Appブリッジ（候補切替、テーマ、カメラ側・距離、登場アニメ、監査済み素材）：PASS。
- LoLリプレイ接続、WGCミラー、カメラ実映像、GPU/NVENC、ゲーム音、録画、MP4出力：**このブランチでは未実施**。
- 旧11画面：旧10画面も原画像の領域座標から編集可能なHTML/CSSへ再構成し、12候補の切替と共通App操作へ接続を開始。外観・全操作は未合格。原画像をUI背景には使用しない。

`MEASURED` は寸法比較を実行した意味。目視審査・機能合格ではない。`REVIEW` は矩形差が許容外。

## 29画面一覧

| ID | 候補 | 実装 | オフライン視覚 | 映像外RGB差/255 | 矩形許容内 | LoL実機 |
|---|---|---|---|---:|---:|---|
| L02-M | 旧案2 標準編集 | 再構成中 | MEASURED | 43.0546 | 9/9 | NOT_RUN |
| L03-D | 旧案3 ハイブリッド | 再構成中 | MEASURED | 37.9396 | 11/11 | NOT_RUN |
| L03-N | 旧案3 ハイブリッド | 再構成中 | MEASURED | 34.9851 | 11/11 | NOT_RUN |
| L05-M | 旧案5 ウィザード | 再構成中 | MEASURED | 34.0998 | 13/13 | NOT_RUN |
| L06-E | 旧案6 ライブラリ／編集 | 再構成中 | MEASURED | 36.3415 | 9/9 | NOT_RUN |
| L06-L | 旧案6 ライブラリ／編集 | 再構成中 | MEASURED | 54.1886 | 10/10 | NOT_RUN |
| T-A-M | 旧テストA 現行整理 | 部分実装 | MEASURED | 31.6168 | 12/12 | NOT_RUN |
| T-B-S | 旧テストB カメラ・FX | 再構成中 | MEASURED | 40.2014 | 13/13 | NOT_RUN |
| T-B-C | 旧テストB カメラ・FX | 再構成中 | MEASURED | 36.4433 | 14/14 | NOT_RUN |
| T-B-F | 旧テストB カメラ・FX | 再構成中 | MEASURED | 38.1603 | 13/13 | NOT_RUN |
| T-B-M | 旧テストB カメラ・FX | 再構成中 | MEASURED | 36.5588 | 14/14 | NOT_RUN |
| R-A-main | 新A Studio | 部分実装 | REVIEW | 10.8672 | 12/23 | NOT_RUN |
| R-B-main | 新B Creator | 部分実装 | MEASURED | 0.7547 | 15/15 | NOT_RUN |
| R-C-main | 新C Director | 部分実装 | REVIEW | 1.7096 | 14/15 | NOT_RUN |
| R-D-main | 新D Highlights | 部分実装 | MEASURED | 1.2005 | 12/12 | NOT_RUN |
| R-E-main | 新E Flow | 部分実装 | MEASURED | 0.4192 | 13/13 | NOT_RUN |
| R-F-main | 新F Killbeat | 部分実装 | REVIEW | 2.8097 | 11/18 | NOT_RUN |
| R-A-main-dark | 新A Studio | 部分実装 | REVIEW | 9.605 | 12/23 | NOT_RUN |
| R-E-main-dark | 新E Flow | 部分実装 | MEASURED | 0.4213 | 13/13 | NOT_RUN |
| R-A-camera | 新A Studio | 部分実装 | REVIEW | 4.7928 | 13/25 | NOT_RUN |
| R-A-frames | 新A Studio | 部分実装 | REVIEW | 3.5416 | 11/16 | NOT_RUN |
| R-E-studio | 新E Flow | 部分実装 | REVIEW | 5.7241 | 13/23 | NOT_RUN |
| R-E-frames | 新E Flow | 部分実装 | REVIEW | 3.5418 | 11/16 | NOT_RUN |
| R-A-main-1366x768 | 新A Studio | 部分実装 | REVIEW | 5.846 | 13/23 | NOT_RUN |
| R-B-main-1366x768 | 新B Creator | 部分実装 | REVIEW | 1.1387 | 11/15 | NOT_RUN |
| R-C-main-1366x768 | 新C Director | 部分実装 | REVIEW | 2.7029 | 11/15 | NOT_RUN |
| R-D-main-1366x768 | 新D Highlights | 部分実装 | MEASURED | 1.2067 | 12/12 | NOT_RUN |
| R-E-main-1366x768 | 新E Flow | 部分実装 | REVIEW | 0.6021 | 12/13 | NOT_RUN |
| R-F-main-1366x768 | 新F Killbeat | 部分実装 | REVIEW | 3.7881 | 11/18 | NOT_RUN |

## 残る合格条件

1. 旧10画面の部品・文字・色・操作順を原画像に合わせて詰め、再構成を完成させる。大きなRGB差を寸法一致だけで合格扱いしない。
2. 新18画面を含む全操作部品を監査F01〜F25へ接続し、表示例を実データへ置換する。エンゲージは専用実装ができるまで未対応と表示する。
3. 全29画面の比較画像を修正後に再撮影し、Windowsアプリの実画面と表示倍率125%も確認する。
4. 実際のLoLリプレイでスキャン、TargetLock、BLUE/RED、固定自動・フルオート、FX、WGC、GPU/NVENC、LoL音声、MP4出力を機能別に合否記録する。
5. 合格したコミットからポータブルEXE/ZIPを作り、起動・操作・保存・書き出しを実機で確認する。mainへのマージはユーザー承認待ち。
