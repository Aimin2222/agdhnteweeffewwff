# Windowsまとめてテスト v5.10.18-test

完全版ZIPを旧版と別フォルダへ展開しSTART_GPU.bat。個人設定/録画/プロジェクトは保管。

1. 新規起動でカラーが「無補正（LoL本来の色）」か確認。テンプレートや色を選ぶと選択値が適用されるか、旧設定/素材ID/動き/DOF値が読み込めるか確認。無補正はカラーだけで、他エフェクトは個別設定。
2. ミラーONのまま図鑑を開いてwheel。図鑑だけが動き、背景パネルが動かないか確認。閉じるとメインスクロールが復帰するか。タブ/スライダー/素材連続選択/DOF円帯/チェックhoverの応答も確認。
3. 試合全体スキャン後、「開発用：指定テストを一括作成・500MB ZIPに保存」を実行。通常はRED/BLUE各5視点（従来4＋geo_aim実験）で計10本、10切替と6モーションを出力。後半で再録画しないことを確認。計画取得失敗なら付属JSONへ戻りUIが固まらないか確認。
4. camera_comparison.jpg/transition_comparison.jpg/JSONを確認。RED/BLUEの水平線反転・対象ロスト・地形めり込みを区別してメモ。geo_aimは実験で、既存の通常三人称等と比較。geometry_validationや画像差分は参考値で、自動合格判定ではない。
5. QAフォルダの直接ZIPが各500MB以下で、ZIP内にZIPがなく、results.jsonにqa_archives/カメラ数値/実FX経路/実encoderが入るか確認。元MP4も残っているか。巨大ファイルのpartはRESTORE_OVERSIZED_FILES.txtの順でバイナリ結合。
6. モーション6本を再生して60fps/3秒以下/音声/方向を確認。通常1シーン・全検出・チェック2シーンで1080p60fps、色、LoL音声のみ/同期、TargetLock、ミラー復帰を確認。TEST_GPU_RENDERも実行しGPU confirmedとNVENCを別に確認。
7. QA中止は現在の1本終了後に残り停止、比較表/ZIPを追加開始しないか確認。

この会話へQA直接ZIP（必要なパート）とAutoCine_Diagnostics.zipを添付。比較表とJSON、必要ならRED1本/BLUE1本で構図を確認する。設定・操作・何秒後かをメモ。個人ログ/映像をGitHubへ無断公開しない。
