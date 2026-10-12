# Windowsまとめてテスト v5.10.19-test

完全ZIPを旧版と別フォルダで展開しSTART_GPU.bat。設定/録画は保管。

1. 起動直後の無加工プリセットで四隅が暗くならず、粒子/Bloom/フラッシュが勝手に付かないか確認。別プリセット/効果を選べば反映するか確認。
2. かんたん編集でテンプレートA/Bと図鑑が使えるか、詳細編集でも同じ選択になるか確認。色微調整ONで4項目を表示、OFF→ONで値保持。ミラーONのスクロール/タブ/スライダー/DOF/チェック/図鑑の応答を確認。
3. 通常三人称のRED/BLUEとRED geoの上下反転・対象ロストを確認。REDシネマ/Lolnamの寄りすぎ、BLUEシネマ/Lolnam/geoの従来構図も確認。水平線反転・地形めり込み・対象見切れを区別してメモ。手動0・180度/TargetLock/seek/再選択/別リプレイも確認。
4. 全体スキャン後に開発QAボタン1回。通常はRED/BLUE各5カメラ、sideごとのreview_all.mp4、10切替、6空間切替、6キル登場、3時点比較画像、500MB以下の直接ZIPを確認。後半の切替/比較では新たなLoL録画が始まらないことを確認。
5. spatial_*.mp4の6種類を比較。空間確認動画は無音、通常録画/side reviewはLoL音声を確認。results.jsonのspatial_transition_tests[].renderでGPU effectsと実encoderを別に確認。GPU不可時はCPU fallback理由。60fps/長さ/色と切替前後の素材を確認。
6. 通常1シーン/全検出/チェック2シーンで1080p60fps・カラー・LoL音声のみ/同期・録画後ミラー復帰。TEST_GPU_RENDERも実行。QA中止は現在の1本後に残り停止。

この会話へQA直接ZIPとAutoCine_Diagnostics.zip。特にRED/BLUE review_all.mp4、RED/BLUE_camera_3frames.jpg、transition_3frames.jpg、JSON、良い/悪いカメラ番号を共有。個人ログ/録画はGitHubへ無断公開しない。カメラ補正の実機成功とNVIDIA速度はクラウドで保証しない。
