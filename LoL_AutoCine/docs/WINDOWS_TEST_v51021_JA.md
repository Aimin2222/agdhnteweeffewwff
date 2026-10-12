# Windowsまとめてテスト v5.10.21-test

完全ZIPを旧版と別フォルダに展開しSTART_GPU.bat。設定/録画を保管。

1. ミラーONで色微調整ON→OFF→ON。チェック直下の4項目・値保持、タブ/スクロール/スライダー/DOF/図鑑/A-Bの応答を確認。
2. 自動ディレクターONで直下の強さ欄が開くか。0.5を入力して自動作成、1.0より回り込み/接近が弱いか確認。0も試す（固有のFOV/スロー/ローアングル/手動keyframeは残る）。OFF時に従来設定を優先するか。文字/NaN等の不正値は開始前エラー。
3. 全体スキャン後に開発QAを1回。RED1/2の距離、特にRED2の前版構図を確認。RED3 FPSに主役/キル、RED4 Lolnam/RED5 geoで中心位置を確認。
4. BLUE6の対象/敵、BLUE7の良い構図が維持されるか、BLUE8 FPSに戦闘、BLUE9/10の俯角と主役を確認。上下反転/地形めり込み/草岩遮蔽を分け、番号でメモ。
5. FPS手動blue0/red180と高さ入力を変更し、位置と向きが食い違わないか。カメラを切替→戻す/seek/同対象再選択/別リプレイも確認。
6. QA10カメラ/RED・BLUE各review_all.mp4、従来3切替、空間6種、キル登場6種、3時点画像、500MB以下直接ZIP。空間確認のみ無音、通常録画とside確認にはLoL音声。中止は現在1本後に残り停止。3時点は時間割合サンプル。
7. 単体MP4をMAKE_REFERENCE_SHEETS.batへドラッグ、同じく動画フォルダも試す。比較ZIPと6時点JPEG/JSON・元動画不変を確認。失敗時は%TEMP%/AutoCine_ReferenceReview_latest.logを会話へ。ZIPは先に展開。
8. 通常1シーン/全検出/チェック2シーンで1080p60・色/22FX・フレーム・LoL音声のみ/同期・ミラー復帰。TEST_GPU_RENDERの実結果でGPU effectsとencoder/fallbackを別々に確認。

返してほしいもの: QA直接ZIP、AutoCine_Diagnostics.zip、必要ならRED3/BLUE8動画と番号付きメモ。個人ログ/録画はGitHubへ無断公開しない。Windows BAT/カメラ構図/NVIDIA速度はクラウドで未確認。
