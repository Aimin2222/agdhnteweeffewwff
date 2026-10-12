# Windowsまとめてテスト v5.10.23-test

完全ZIPを旧版と別フォルダで展開しSTART_GPU.bat。設定/録画を保管しLoLリプレイを再生。

1. MAKE_REFERENCE_SHEETS.batをダブルクリック→日本語名のMP4選択。元動画の隣の_AutoCineReferenceReview_元の名前へ6時点比較ZIPが出るか。別の日本語名の動画でも別フォルダになるか。
2. ファイル選択をキャンセル→動画フォルダ選択で複数動画の比較、両方キャンセル時は比較出力を作らないか。
3. 単体MP4/フォルダをBATへドラッグ。ZIP指定は展開案内、不存在/Python不足は案内とpause。失敗時diagnostics/reference_review_latest.logとTEMP/AutoCine_ReferenceReview_latest.logを確認。候補はライブラリをimportできるPythonだけ。
4. 開発用接続→全体scan→動画・画像→500MB ZIPを未接続から1回。complete cache再利用/二重押し防止/partial・失敗・stop/旧結果と旧ZIP保持を確認。
5. RED2/4/5が前版と同じ構図か。RED1はZ傾き・上下反転なく中心へ、RED3 FPSはキル前後の主役/敵が見切れないか。FPS手動0/180と高さも確認。
6. BLUE6〜10の引き具合、特に以前良いBLUE7/9が悪化しないか。カメラ切替→戻す/seek/別リプレイでも確認。番号で傾き/遮蔽/対象ロストを区別。
7. QA10カメラ/RED・BLUE各review_all/時間割合3時点画像/従来3比較・空間6種・キル6動作/results/QA_Supportと全ZIPpart。参照BATの最新ログが存在すればsupportへ各1MB以下で入るか。ZIP内最終JSON一覧一致、空間確認だけ無音、通常LoL音声。
8. ミラーONで色/タブ/scroll/DOF/図鑑/A-B、自動ディレクター0/0.5/1、通常1シーン/全検出/チェック2シーン、1080p60/22FX/フレーム/LoL音声のみ・同期・ミラー復帰、TEST_GPU_RENDERを確認。GPU effectsとencoder/fallbackを別に見る。

返すもの: QA ZIP全partと必要なら診断ZIP/参照BATログ、カメラ番号のメモ。録画/診断をGitHubへ自動送信しない。Windows BAT・日本語パス・カメラ構図/NVIDIA速度は実機確認が必要。
