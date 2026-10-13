# v5.10.26-test 実機調査・修正前後比較（合格未判定）

旧版と別フォルダへ完全ZIP展開、VERSION確認、START_GPU.bat。旧設定/録画を保管。

1. まず指定元ビルドbec275d/9e8b67454cb10e33の既存results.json・CameraQA part001〜003・診断ZIP・PRE/KILL/POST画像をこの会話へ添付。同じ日付/シーンのものを揃える。古い診断ZIPで代用しない。
2. 候補版で同じリプレイ・対象・イベント時刻・設定・1080p60を使い一括QA1回。version/installed_version/qa_build_versionが5.10.26-test、不一致false。camera_code_sha256/fingerprintは今回コードの別IDで、元9e8b...と区別する。
3. BLUE9/10優先: 実MP4のPRE/KILL/POST、空/地形外・暗い領域の面積、主役/敵の位置、baseline_readsのtarget/camera worldposition・rotation・offset・mode/selection、POSE FOV/note/fell_backを照合。角度の勘による変更なし。
4. BLUE6 X=-2のままPRE/KILL/POST上端見切れ、stale基準。BLUE8大幅変更なし。RED1/3TargetLock/Z=0とstale警告、RED2/4/5・BLUE7の良い構図を保護。RED4fallback理由も確認。切替→復帰/seek/別replay/手動0・180/高さ。
5. recording_timingのevent_replay_timesとevent_video_seconds、visual_qaのevent_video_seconds/sample_seconds/kill_sample_basisを確認。recording_event_observationだけ実イベント補間。fallbackはMID時間割合で実KILLと呼ばない。単独KILL>0.5も目視警告、撮影失敗と断定しない。
6. oneclick接続→全体scan→10カメラ/side reels/3切替/6空間/6登場→画像/全500MBpart、stop/二重押し/cache/ミラー復帰、LoL音のみ/同期/60fps/GPU22FX・NVENCとfallback。旧設定/UI/図鑑37素材/参照ZIPも回帰。

返すもの: 元ビルドの全資料と候補版の全part/results/診断、同一シーン比較・カメラ番号メモ。録画/個人ログをGitHubへ無断公開しない。自動テスト/Windows CIだけで実機構図の合格を宣言しない。
