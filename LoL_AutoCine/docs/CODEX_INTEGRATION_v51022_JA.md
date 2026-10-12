# v5.10.22-test ワンクリックQA・ASCII起動・限定診断ZIP・モード別引き構図

受領ZIPのCRC/パス/リンクと全README/差分/7新規テストを確認。指定GitHub0e8e8f65362fd10a3ab9509c3fcbb4580b72691dへ独立checkoutでapply --check/適用、単体テストとpatch内はバイト一致。受領v21からの15パス差分を現行Codex v21 dadb48884538158ae21351a618e278e3c64c06bcへ機能別統合。core/camera_tuningとjobs/UIなどは前回Codex補正と競合、全ファイル上書きせず有限値・手動向き・高さ・ディレクター接続・UIを保持して個別解決。原ZIPはGit外、原コードはarchive/received-ui-v51022とhistory。添付のWindows実行/画像評価/CI612件/Release記述は受領側の説明で、Codex実測・Release作成ではない。

ワンクリックQAはUIでTemplate/出力先snapshot、同じ1ワーカーで未接続ならconnect→全体scan→camera QA。既存complete cacheは再利用、partial scan/接続失敗/イベント不足/停止時は録画しない。busyは押した時点で立つ従来機構、二重押しを抑制。snapshot不正値は開始前UIエラー、worker冒頭のstopも追加。既存_connect/_scanはplain data/queueのみ、Tk読みはUI上。旧開発bundleボタン・通常出力・ミラー/図鑑/DOFを保持。

MAKE_REFERENCE_SHEETS.batとRUN_AUTOTEST.batをASCII、Python UTF8フラグと失敗終了コードを保持。前者の単体動画/フォルダ/ログ/pause、後者のpy -3 -m core.auto_qaを保持。全root BATはASCII。新auditはGit rootを正しく取得してtracked sourceだけ確認し、単体Git/配布内LoL_AutoCine両方で動作。受領のroot.parent基準では単体Gitから外れてrglobで個人ファイルまで読む問題を補正。非Gitフォルダのテストではfallback、symlink・diagnostics・buildは対象外。コードを勝手に再エンコードせず不正UTF8を検出。Windows cmd/日本語ファイル名の実機実行は未確認。

QA_Supportに読み方と指定6診断ファイルの末尾各最大1MB。seek後のreadにも固定上限、元バイトのままコピーしUTF8へ再変換しない、元ログを変更しない。symlink/外部参照を除外、書込失敗は診断情報を記録して成功録画を無効にしない。中止時にはsupport/ZIPを開始しない。受領のキル前・瞬間・後という表現を時間割合サンプルへ訂正、AI主役/キル認識ではない。

既存ZIPは.logを除外していたため、実ZIPテストが初回63成功/1失敗。QA_Support直下の既知名かつ1MB以下のログのみ許可して補正（追加後関連65成功）。任意ログ/巨大ログは除外。1MBstream・最大500MB・元動画/JSON/既存ZIP/再出力別名/part再結合/最終JSON一致は維持。qa_supportと最終ZIP一覧をresults.jsonへ反映後に出力。診断や動画をGitHubへ自動送信しない。

カメラは受領の小幅試験値。RED通常third距離1.13/Z+3度、RED FPS back1.60/X-4/Y+4、RED geo距離1.12/X-4、BLUE FPS back1.22。RED2シネマ距離0.96/追加角度なし、RED4 Lolnam/BLUE7シネマ/BLUE9 Lolnamの数値は維持。一般距離0.87〜1.30、fps_back1.0〜1.65、角度±8と有限値検証。FPSでは相対poseだけ倍率を掛け高さを別加算、手動0/180は同じ位置/回転headingを保ち自動角度biasは適用しない（診断へapplied_angle_bias）。前回のキャッシュ/安定回転のチーム・モード分離、TargetLock/forced Y pitch metadata/安全俯瞰/seek/reset、実ディレクターgain・旧API/Template任意Noneを保持。実画角・Z角の見え方・主役中心の改善はWindows未確認。

GPU feature/gpu-cameraqa-v51022、UI feature/ui-cameraqa-v51022、統合 integration/v5.10.22、受領 archive/received-ui-v51022。旧111先端/202旧配布物/37PNGを保持、全115refs bundle、共有8blobレビュー。

```sh
python tools/check_parallel_integration.py --gpu feature/gpu-cameraqa-v51022 --ui feature/ui-cameraqa-v51022 --integration integration/v5.10.22 --shared-review docs/CODEX_SHARED_API_REVIEW_v5.10.22.json
python tools/check_text_encoding.py
```

statusも確認。GPU Full全22FX/OpenCL/NVENC/60fps時刻・フレーム数/LoL Native Loopback/Helper/WGC/encoder policy・実FXとencoder別診断/安全CPUfallback/LatestPreview/Tk所有/ミラー応答/6空間・6キルQA/付属3比較と通常10演出を保持。今回はエフェクト/録画/音声の本体はbyte不変。CPU制御/音声/I/O/静止比較は残る。過去native139/132は原因未確定、今回成功を恒久修正と扱わない。Windows/LoL/NVIDIA速度は未確認。結果はhandoff/VERIFICATION_v5.10.22.json。mainへマージしない。
