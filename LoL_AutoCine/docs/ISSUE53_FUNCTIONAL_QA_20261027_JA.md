# Issue #53 機能試験版：2026-10-27 検証記録

**2026-10-27追記：開発用の配布入口はBAT版に変更。** この文書にあるEXE起動スモークとEXE用ZIPの結果は旧試作の履歴であり、新しい開発用BAT版の実LoL一括QA合格を意味しない。v5.10.31-testと同じくアプリ内の「開発用：カメラ＋Work素材一括QA・30MB ZIP」を使う。`ISSUE53_WINDOWS_TEST_JA.md`を現行手順とする。旧EXEは友人向けUI比較EXEや現行AutoCineを置き換えるものではない。

## 判定の範囲

基準は従来AutoCine `v5.10.32-test`、PR #49 の `feb895491ca4bc780da4aab91990f25177cd35ab`。Issue #53 の独立ブランチと別EXEで調査した。PR #51 の7案比較版、PR #52 の候補8〜10、既存配布EXE、`main` は変更していない。FlashとZoomは試験EXEだけで既定ONとなる研究候補で、環境変数 `AUTOCINE_RESEARCH_FLASH=legacy`、`AUTOCINE_RESEARCH_ZOOM=legacy` により従来処理へ戻せる。正式採用は未決定。

## 実施結果

| 項目 | 判定 | 根拠・残る範囲 |
| --- | --- | --- |
| UI差替え境界 | PASS（契約試験） | `core/ui_bridge.py` のイベント→従来`App`ハンドラ、共有状態、UIスレッド条件の試験。候補画面の接続完了を意味しない。 |
| Flashのイベント時刻 | PASS（短尺FFmpeg） | 旧処理の小数3桁丸めでイベント前に発光する条件を再現。試験候補は実PTSで発光開始を制御し、30/60/60000÷1001fps、VFR等の個別試験を通した。長尺実リプレイはNOT_RUN。 |
| Zoom `tmix` | PASS（短尺FFmpeg） | 旧経路の過度な明るさと候補の正規化をピクセル測定。これは時間混合の修正であり、空間的な放射ブラー完成ではない。 |
| 保存済み実ゲーム映像の再合成 | PASS（限定） | 1920×1080・60fps・120フレームを従来／候補で再合成。旧経路のフレーム30は平均輝度211.33、250以上の画素66.67%。候補フレーム30は58.52／0.05%、発光開始フレーム31は167.34／1.42%。同一設定のライブReplay比較ではない。 |
| NVENCによる映像出力 | PASS（オフライン） | 1080p60の120フレームMP4をNVIDIA NVENCで出力し、デコード・寸法・フレーム数を確認。GPU FXは診断値`gpu_effects_attempted=false`で、CPU FX fallback。GPU FX実使用はNOT_RUN。 |
| 保存済みゲーム音声の合成 | PASS（オフライン） | 過去QAの可聴WAVを使用し、NVENC映像とMP4へ合成。デコード後RMS 0.010518、ピーク0.056263。LoLプロセス専用のライブ録音や長時間AV driftはNOT_RUN。 |
| ポータブルEXE | PASS（起動スモーク） | 旧配布物と別フォルダにビルドし、ZIP展開後に起動して`v5.10.32-test - Scene Studio`のウィンドウを確認。frozen子プロセスのcapture worker／yt-dlpも終了コード0。GUI全ボタンの操作検証ではない。 |
| 実LoLリプレイ、スキャン、ミラー、録画 | NOT_RUN | この実行環境では`LeagueClient.exe`起動と`.rofl`関連付け起動がWinError 5で拒否された。LoL画面上の試験は未実施。 |
| BLUE/RED全カメラ、TargetLock、全素材・35FX・6motion | REVIEW | コードと既存試験を棚卸しした。実Replayでの各視点、見た目、ミラー対出力の一致は未合格。正式素材はNo.083 Aのみ、残りは確認用。 |
| 125% DPI、144HzミラーFPS、長時間安定性 | NOT_RUN | 操作可能なLoLセッションを得られず、条件を満たす測定を実施できなかった。 |

オフライン比較用の計測器は`tools/issue53_compare_render.py`。上記動画、比較コンタクトシート、原診断ログは個人録画・ローカルパスを含むためGitHubに追加しない。研究の数理fixtureを実レンダラの合格へ読み替えない。

## 回帰試験と従来版比較

`tools/run_issue53_regression.py`は各`test_*.py`を別Pythonプロセスで実行し、native/Tcl crash後も残りを継続する。全110モジュールを実行し、短い一時パスとUTF-8を使って再試験した最良の結果は**96 PASS、7 FAIL、4 CRASH、3 NO_TESTS、計1055 passing cases**。`NO_TESTS`の3ファイルは試験関数を持たない補助ファイルである。単一プロセスの全pytestはWindows native終了コードで途中停止したため、「全件通過」ではない。

残る7 FAILのうち、3件はlocalhost socketのWinError 10013、3件はTcl初期化の不安定さ、1件はv5.10.32より古いUI文言を要求するsource-string試験。4 CRASHはTk/nativeプロセス終了。これらの多くは無変更の基準worktreeでも再現した。基準側の問題を今回の修正で新規発生したと断定できない一方、候補側のTcl失敗が基準で通った例もあり、環境依存の未解決として残す。ログは圧縮せずローカルに保存し、エラー原文を確認した。

Flash/Zoom候補のFFmpegフレーム試験、UI bridge試験、CameraQAの版数を合わせた対象試験は通過。`core/camera_qa.py`の旧`5.10.30-test`表記だけを実配布`5.10.32-test`に合わせ、該当17件を再試験した。カメラ計算、録画、音声、素材IDは変更していない。

## Issue #53 の作業状態

- **A：準備**：従来機能台帳、イベント接続表、共有状態境界、UI選定後の接続手順を`ISSUE53_BASELINE_AND_UI_BRIDGE_JA.md`に保存。候補1〜10への実接続はUI選定後。
- **B：研究試験**：FlashとZoomのみlegacy切替付きで実装。座標1458条件、カメラ12新ルール、Work652素材の品質承認、音声研究案は本体処理へ無断採用していない。
- **C：Windows QA**：EXE起動・ZIP展開・保存済み素材のNVENC/音声合成を確認。実LoLセッション、WGC、LoL専用音声、全カメラと全UI操作はユーザー実機試験待ち。手順は`ISSUE53_WINDOWS_TEST_JA.md`。
- **現行BAT版の追加判定**：通常候補と`legacy`のBAT`--check`は終了コード0。既存一括QA・Work素材・30MBアップロード・CameraQA版数の対象4モジュール37件はPASS。ZIPのCRC・展開・音声helper同梱を確認。準備済みPython環境を指定したBAT経由では展開先アプリの起動ログを確認した。新規環境の初回セットアップはサンドボックス一時フォルダの権限エラーをBAT内TEMP指定で解消したが、pipの外部DNSが拒否され完了できなかった。アプリ内一括QAのライブ完走、コマンド画面の点滅解消は実機試験待ち。旧EXEの起動結果をBAT版の動作合格へ流用しない。

## 配布と追試

ビルド元コミットはZIP内`BUILD_INFO.json`、ZIPのSHA256は同じビルドフォルダの`SHA256SUMS.txt`を参照する。ZIPを空の新規フォルダへ展開し、`TEST_GUIDE_JA.md`の順で検証する。失敗時は時刻、選択シーン、BLUE/RED、試験EXEのrevision、動画、診断ZIPを記録する。既存フォルダは上書きしない。実Replayに接続できた後、同一シーン・同一設定で従来版と試験版を比較し、FAILは元ログを確認してから修正する。
