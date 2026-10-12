# Windowsまとめてテスト v5.10.24-test

完全ZIPを旧版と別フォルダで展開しSTART_GPU.bat。既存設定/録画は保管。

1. リプレイ再生中、未接続から開発用ワンクリックQAを1回。接続→全体scan→RED/BLUE動画・画像→500MBまでの直接ZIP。complete cache再利用/二重押し防止/partial・失敗・停止/旧結果保持を確認。
2. RED1通常thirdとRED3 FPSのPRE/KILL/POSTで主役が中央付近、Z傾き・上下反転・右端の欠けがないか。数式改善と実画面の見た目を区別。RED2/4/5は前版と同じ構図、BLUE6 PRE優先・BLUE7〜10回帰。モード切替→戻す、seek/別リプレイ、手動0/180/高さも確認。
3. MAKE_REFERENCE_SHEETS.batダブルクリック→日本語MP4/動画ZIP。6時点比較ZIPの実フルパス表示と保存先Explorer。ファイルcancel→フォルダ選択、両cancelは比較出力なし/Explorerなし。別の日本語名は別フォルダか。
4. 単体動画/動画フォルダ/動画ZIPをBATへdrag。日本語・重複名の対応reference_archive_names.json、6時点画像、元動画/ZIP不変を確認。29本など多数動画も試す。結果ZIPはJPEG/JSONのみで元動画ZIPを含まない。
5. 壊れたZIP/動画なしZIP/不存在は理由とpause/最新diagnostics/reference_review_latest.log、既存成功ZIPを成功扱いしない。Python不足時の案内・ログ。CI環境ではExplorer/pauseを抑制。
6. QA10カメラ/RED・BLUEreview_all/3時間割合画像/従来3比較・6空間・6キル登場/最終results/QA_Support/全ZIPpartと再結合。静止比較はAI主役判定ではない。supportは最新参照ログなど指定各1MB末尾のみ。
7. ミラーONで色・tab・scroll・DOF・図鑑37素材・A-B・ディレクター0/0.5/1、通常1シーン/全検出/チェック2シーン1080p60。22FXのカラー・時間・LoL音声だけ/同期・ミラー復帰。TEST_GPU_RENDERでGPU effectsとencoder/fallbackを別に確認。

返すもの: QA ZIP全part・必要な診断ZIP/参照ログとカメラ番号のメモ。ユーザー動画やログをGitHubへ無断アップロードしない。Windows BAT/日本語パス/Explorer、LoL構図、NVIDIA性能は実機確認が必要。
