# Windowsまとめてテスト v5.10.20-test

完全ZIPを旧版と別フォルダに展開してSTART_GPU.bat。設定/録画を保管。

1. ミラーONで色微調整ON。チェックの直下に4項目が出るか、OFF→ONで値を保持するか確認。かんたん/詳細のテンプレート/A/B/図鑑/DOF/スクロール/タブ切替の応答も確認。
2. 全体スキャン後に開発QAを1回。RED1通常thirdの中心/上下反転、RED2シネマの前版構図、RED3 FPSとRED4 Lolnam/RED5 geoの主役位置を確認。
3. BLUE6通常thirdの引き構図、BLUE7シネマ/BLUE9 Lolnamの草・岩による遮蔽、BLUE8 FPSの戦闘、BLUE10 geoの前版構図を確認。特にRED2/BLUE10は前版との比較。カメラを切替→戻す/seek/同対象再選択/別リプレイでも確認。
4. QAは10カメラ(RED/BLUE各5)、各side review_all.mp4、従来切替3種(cut/flash/dark)、空間6種、キル登場6種、3時点画像と500MB以下の直接ZIP。空間確認のみ無音、通常/side録画はLoL音声。中止は現在1本後に残り停止。3時点は時間割合サンプルで実キル時刻の自動特定ではない。
5. 通常1シーン/全検出/チェック2シーンで1080p60fps・色/全22FX・フレーム・LoL音声のみ/同期・録画後ミラー復帰。TEST_GPU_RENDERの結果を確認。診断で実GPU effectsと実encoder/fallback理由を別々に確認。
6. 任意: 参照MP4フォルダをMAKE_REFERENCE_SHEETS.batへドラッグ。_AutoCineReferenceReview/ReferenceReview_contact_sheets.zipに各動画6時点JPEGとJSON、元動画が残るか確認。これは動画の編集/アップロードではない。

返してほしいもの: QA直接ZIPとAutoCine_Diagnostics.zip、必要ならRED/BLUE review_all.mp4。「RED1正常、BLUE7岩、BLUE10以前と同じ」など番号付きメモ。ログ/録画はGitHubへ無断公開しない。実機構図とNVIDIA速度はクラウドでは未確認。
