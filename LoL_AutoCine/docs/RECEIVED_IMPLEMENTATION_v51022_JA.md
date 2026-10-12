# 受領側資料（Codex実機確認・CI実測・Release作成ではない）

現在仕様はCODEX_INTEGRATION_v51022_JA.md参照。以下は原資料。

# LoL AutoCine v5.10.22 開発仕様書・Windowsテスト手順

## 目的
日本語WindowsでのBAT文字化けを防止。開発用テストボタン1回で接続→全体スキャン→RED/BLUE別カメラ動画→キル前/中/後の画像→切替演出比較→キルフレーム比較→診断ログ→最大500MB単位ZIP作成まで行う。既存のGPU/NVENC/LoL専用音声/HUD/TargetLock/1080p60/キルフレームは変更しない。

## 文字化け対策
- `MAKE_REFERENCE_SHEETS.bat` と `RUN_AUTOTEST.bat` をASCIIのみのソースへ変更。日本語はPythonのUTF-8処理経由で表示。
- BAT実行前に `chcp 65001`、`PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8` を適用。
- `tools/check_text_encoding.py` でgit追跡中のソーステキストがUTF-8、BAT/CMDがASCIIであることをCI検証。
- GitHub Actions実Windowsで日本語フォルダ/MP4名を使い、比較画像ZIPまで検査。
- 元MP4や診断ログを黙って他エンコーディングへ再変換しない。処理失敗は `%TEMP%\AutoCine_ReferenceReview_latest.log` に記録する。

## 開発用ワンクリック
`on_dev_camera_qa` はGUIスレッドでテンプレートと出力先を確定し、1つのワーカーを起動。既存の試合全体キャッシュがあれば再利用、なければReplay API接続と試合全体スキャンを完了させてから録画する。二重クリックはbusy制御で停止。キルのない試合や接続失敗時は無理な録画に進まず、診断ログへエラーを残す。

QA計画は毎回GitHub上のJSONを3秒のタイムアウトで取得し、通信できない場合はZIP内の同一JSONへフォールバック。Pythonコードを外部から取り込んで実行しない。今回指定の5つのカメラモードをRED/BLUE別に録画し、切替・登場動作などは可能な範囲で既存録画を再利用する。

生成される `CameraQA_日時` には、カメラ10本、RED/BLUE連結MP4、3時点比較画像、Transition動画、KillFrames動画、results.json、QA_Support（読み方/最新診断ログ）を含める。part ZIPは各500MB以下、**二重ZIPなし**。共有時は全partをアップロードする。

## カメラ独立性
現状、リプレイAPIへの送信/追従エンジンは共通だが、`SHOT_TUNING[(side, style)]` がモード×チーム別の距離/角度を独立して保持し、clipごとに新しい`CameraPlan`インスタンスを作成する。キャリブレーションキャッシュは(対象キャラ, チーム, スタイル)別。共通エンジンの変更には回帰テストが必須で、*10本のプログラムが完全独立*していると誤解させない。

v5.10.21比較画像への今回の小幅な補正:
- RED #1: 0.94倍から1.13倍へ撮影距離を増やし、角度Z+3°の試験値を追加。
- RED #2: 視認性が完成判定。距離0.96倍、角度補正なしを維持。
- RED #3: FPS向けの独立距離倍率1.60倍、向きX-4°/Y+4°の試験値。ドアップ・右上寄りを抑える。
- RED #4: 現在の良い構図を厳守。距離/角度の変更なし。
- RED #5: 1.12倍に引き、X方向を-1°だけ変更（-3°→-4°）。
- BLUE #7/#9: 良好なカメラの数値を維持。BLUE #8は距離を1.22倍へ引く。
- 既存のTargetLock/ゲーム音/エンコード機能のコードは変更しない。

## GitHubエラーの整理
以前のv5.10.21で出た主な失敗は、Windowsのフォルダ出力先名の期待値不一致、従来FPSの`side_yaw` API互換性チェック違反、テストが存在しないファイルに例外を期待するミス、CI依存関係導入の遅延である。これらは最終v5.10.21でWindows BATテストと612件の回帰テストが通過している。今回のBAT文字化けとは原因が異なる。
このチャット側でユーザー添付の分割MP4 ZIPを読むと`InvalidArgumentError`が発生する場合がある。GitHubリポジトリ容量が足りないという根拠は確認されていない。Githubへの動画アップロードは必要ない。ChatGPT側の実行環境が復旧しない間は、比較画像とJSON、BATで作るコンタクトシートを送る。

## Windowsで確認してほしいこと
1. [ ] Windows版ZIPを前版と別フォルダーに展開し`START.bat`で起動する。
2. [ ] 一度も接続・スキャンせず**開発用テスト**を1回押す。接続→10人→スキャン→撮影→画像→ZIPまで止まらず進むか。
3. [ ] 全体スキャン済みの状態でも同じボタンを1回押し、再スキャンせず録画されるか。
4. [ ] RED #2と#4が以前と変わらず、RED #1が少し引いて中央に近づくか。
5. [ ] RED #3でキャラのドアップが解消し、RED #5で遠くから中央寄りに映るか。
6. [ ] BLUE #8の引き具合が改善し、BLUE #7/#9が悪くなっていないか。
7. [ ] `QA_Support/READ_ME_FIRST_JA.md`、比較画像、RED/BLUEのまとめ動画、全part ZIPが出るか。
8. [ ] 日本語のMP4名や日本語フォルダーを`MAKE_REFERENCE_SHEETS.bat`にドラッグして文字化けせず成功するか。
9. [ ] 1080p/60fps、GPU/NVENC、ゲーム音、HUDとミラーの挙動に回帰がないか。

ファイル読み込みやBAT失敗時は`%TEMP%\AutoCine_ReferenceReview_latest.log` と `diagnostics/last_error.txt`、`results.json`を送る。これらは個人環境のファイルパスなどを含む可能性があるため、第三者への公開には注意する。

## 配布
GitHub Releaseの`LoL_AutoCine_v5.10.22_Windows_Test_Full.zip`と`LoL_AutoCine_v5.10.22_Codex_MergeChanges.zip`を直接配布（それぞれ独立したZIP）。Codex差分は既存Codex v5.10.15に対する累積差分、main/統合ブランチの上書きやPRマージを自動実行しない。
