# Windowsまとめてテスト v5.10.22-test

完全ZIPを旧版と別フォルダに展開しSTART_GPU.bat。設定/録画を保管。LoLリプレイを再生状態にする。

1. アプリ内の接続/スキャンをまだしていない状態で「開発用：1回で接続→全体スキャン→動画・画像→500MB ZIP」を1回。接続→プレイヤー→全体スキャン→録画→比較→ZIPが進むか、途中もUIに応答があるか。二重押しで2録画が始まらないか。
2. 同じ試合でスキャン済みの状態からもう一度。再スキャンをせず再利用し、旧結果/旧ZIPを消さず別フォルダへ出るか。停止時は新たな録画/support/ZIPを開始しないか（現在のFFmpeg1本は終了待ち）。接続失敗/イベント不足は録画へ進まないか。
3. RED1引き構図とZ+3の見え方、RED3 FPSドアップ改善、RED5 geoの引きと中心を確認。RED2/RED4とBLUE7/BLUE9が前版の良い構図を維持するかを最重要比較。BLUE8 FPS距離を確認。上下反転/傾き/草岩遮蔽/対象ロストは番号で区別。
4. FPS手動blue0/red180と高さを変更して、位置と向き・高さ入力が一致するか。カメラを切替→戻す/seek/別リプレイでも確認。
5. QA10カメラ、sideごとのreview_all.mp4、時間割合3時点画像、従来3比較・空間6種・キル6動作、results.json/QA_Support/READ_ME_FIRST_JA.md/診断断片、全ZIPpartを確認。空間確認のみ無音、通常/side録画はLoL専用音声。ZIP内resultsのqa_archivesが最終一覧と一致するか。
6. 日本語フォルダ・日本語名の単体MP4をMAKE_REFERENCE_SHEETS.batへドラッグ。比較ZIPと6時点画像・元動画不変。失敗時は%TEMP%/AutoCine_ReferenceReview_latest.logを会話へ。RUN_AUTOTEST.batで自動診断JSONも確認。
7. ミラーONで色微調整/タブ/scroll/DOF/図鑑/A-B、自動ディレクター0/0.5/1.0、通常1シーン/全検出/チェック2シーン、1080p60/22FX/フレーム/LoL音声のみ・同期・ミラー復帰、TEST_GPU_RENDER実結果を確認。GPU effectsとencoder/fallbackは診断で別々に確認。

返してほしいもの: 作成されたQA ZIPを全part、この会話へ。必要ならAutoCine_Diagnostics.zip、RED3/BLUE8動画、番号付きメモ。診断断片や録画をGitHubへ自動送信しない。カメラ構図・BATと日本語パス・NVIDIA性能はWindowsでの確認が必要。
