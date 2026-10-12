# Windowsまとめてテスト v5.10.25-test

完全ZIPをv5.10.24と別フォルダへ展開、START_GPU.bat、旧設定/録画は保管。

1. 未接続から開発用ワンクリックQAを1回。接続→全体scan→10カメラ・画像→切替3種/空間6種/キル6登場→500MBまでの直接ZIP。complete cache再利用・二重押し防止・partial/失敗/停止・旧結果保持。
2. BLUE6通常thirdのPRE/KILL/POSTで主役/敵が上端に切れず中央付近か、前版と比較。位置/距離は同じ、角度だけ候補。BLUE7〜10とRED全5を回帰、特にRED1/3中心補正・RED2/4/5良好構図。切替→戻す、seek/別リプレイ、手動0/180・高さも確認。
3. 切替3種/空間6種の実MP4で動きの違い、各side集約reel/3時点画像/最終JSON/QA_Support/全part再結合。静止画だけで動画の動きやAI主役認識を断定しない。
4. 日本語動画・ZIP・folderをMAKE_REFERENCE_SHEETS.batへdrag、ダブルクリック選択/cancel、6時点JPEG/JSONと元名map、原本不変・保存先Explorer/ログ。破損/動画なしZIPは理由・pause・最新log、cancelは出力/Explorerなし。
5. 参考演出メモは資料として追加、通常template/QAに新効果が勝手に入っていないか。部分カラーmaskは未実装でnoirとは別。
6. ミラーON色/tab/scroll/DOF/図鑑37素材/A-B/強さ0/0.5/1、通常1シーン/全検出/チェック2シーン1080p60・22FXカラー/LoL音のみ/同期・ミラー復帰。TEST_GPU_RENDERでGPU effectsとencoder/fallbackを別に確認。

返すもの: CameraQA全part・results.json、必要な診断ZIP/参照logとカメラ番号メモ。ユーザー動画/診断の無断GitHub公開なし。Windows/BAT日本語パス/Explorer・LoL構図・NVIDIA速度は実機未確認。
