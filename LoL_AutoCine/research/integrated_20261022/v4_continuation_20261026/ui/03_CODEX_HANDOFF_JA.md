# Codex実装引継ぎ（採用前の研究提案）
本体コードを本研究で変更しない。候補を勝手に正式採用せず、ユーザー/ChatGPTが比較して決定するまで旧案の忠実実装と本提案を別ルートにする。

## 画像再現の正本
SCREENS.json（24画像ID/params/解像度）、screens/*.png（比較基準）、ui.css/ui.js/index.html（配置・状態見本）、MEASURED_LAYOUT.json（各画面のregionと全button/input/selectの矩形）。寸法はCSS論理px、撮影DPR1。1920×1080を基本、P1/P2は1366×768も固定画像。125/150%DPIは未検証。

通常1920：上部60、nav52、下timeline192、footer38、各行gap10。workspace x16–1904、P1左260/右358/列gap12/中央可変。P2左230/右340。P3左410/右330。panel角丸10、境界1、間隔12、padding16、button40、本文16/副文14/見出し19、checkbox22、数値78×38。詳細数値はMEASURED_LAYOUTを優先。
1366：header52/nav48/timeline154/footer32、gap7、左212/右282、列gap9、文字15、button36、quick64。previewの映像表示最小は480×270（今回通常最小は約508×286）。スクリーン領域とobject-fit:contain後の実映像矩形を別に比較。
1920ドロワー：右16/top132/bottom250/幅550、preview領域を再配置して重なり0。モーダル幅660/maxheight80vh、背景dim。timeline詳細は高さ300。各固定/scrollは実測JSONとCSSのoverflowを参照。

## 維持する共有状態
App/coreは1インスタンス。projectId/replaySessionId/targetPlayerId/selectedSceneId/checkedSceneIds/playhead/sceneSettings/cameraMode/cameraSide/cameraStyle/cameraValues/TargetLock/frameId/effectId/motionId/outputSettings/mirrorSessionId/activeJobIdをUIの外へ置く。テーマとレイアウト切替はこれらを再初期化せず、job/previewを再生成しない。
appearance.mode=light|dark|systemをユーザー設定へ保存、Windowsテーマ変更はsystem選択時のみ反映。UI色の更新で映像にfilter/LUTをかけない。カメラ/素材/レシピの変更は同じmodelへ明示commit。ウィザード戻りでも保持。
本HTMLは画像制作のための試作で、ページ遷移をまたぐ全編集状態の保存やsystem自動追従は未実装。テーマのライト/ダーク切替はDOM更新のみ、現在の数値を保持することを実操作で確認した。

## 機能対応
FUNCTION_BINDINGS_REFERENCE.jsonにF01–F25の既存接続を前監査から継承。今回latest reference_studio.pyとcomparison_detail.pyも読み、実App共有・派生画面の明示方針を確認。旧baselineと最新コードは別のcommit。接続名だけで動作合格にしない。

|提案UI|接続候補|実装時の注意|
|---|---|---|
|リプレイ/Target|on_quick_prepare/on_open_replay/on_play_recent/on_lock|接続済み表示は実測。選択player IDとBLUE/REDを混同しない|
|試合全体scan|on_scan/pb_scan/lbl_scan/_match_scan_cache|非同期進捗/失敗/取消、未接続や未実行を空の成功にしない|
|scene/チェック|on_scene_selection/on_jump_selected/checked_kills/on_toggle_checked|行選択と出力対象を分離、同一IDで参照|
|assist/engage|var_event_mode/var_scene_player_filter|engage専用検出は未対応のまま無効/説明。新規の実イベント契約が必要|
|ミラー|on_mirror_start/on_mirror_stop/var_preview_hz|1セッションを固定previewへ、実FPSと目標Hzを区別|
|演出プレビュー|on_preview_play/on_preview_stop|録画なし確認。stop_ev共有によるrecordへの影響は製品試験|
|カメラ|var_camera_control_mode/var_camera_side/var_style/sl/director_work_controls|manual/fixed_auto/full_autoと旧10IDを維持、未知side時安全側。BLUE/RED試験を分離|
|フレーム|kill_frame_gallery/var_kill_icon_style/var_work_frame/work_gallery|37バッジ、89原本、Work652の別カタログ。1承認記録と651確認用を明示|
|FX/登場|var_work_effect/select_frame_with_effect/var_work_strength/var_work_review/var_kill_icon_motion|35FXの確認用を表示、6motion IDを維持。同名承認を伝播しない|
|timeline/trim|SceneTimeline/var_pre/var_post|1–15s/0.5sの既存契約。図の多段帯は自由な多重動画合成engineの追加ではない|
|詳細編集|on_save_scene/on_scene_undo/redo/on_copy_scene_settings/on_paste_scene_settings/on_keyframe_* /scene_fx_vars|シーンdraftと確定値を分離、Undoの範囲を説明|
|GPU/音声/HUD|var_encoder_policy/var_gaudio/var_hud_mode/_show_legacy_settings|方針と実使用encoderを区別。OS音量・ネットワーク設定は変更しない|
|実録画/出力|on_make_selected/on_make_checked/on_make_clips/on_one_click/on_smart_one_click/on_stop/on_pick_out|選択対象と保存先を明示、通常/スマートの既存差を維持|
|診断/結果|on_automatic_qa/on_dev_camera_qa/on_show_diagnostics|未実施/成功/要確認/失敗の実状態。ログZIPの内容確認、誤って成功表示しない|

## 新規提案として扱うもの
P1/P2/P3レイアウト、右ドロワー、状態をまたぐ比較器、通知履歴、draft/commit統一、theme/system保存の統一adapter、構図種類別の自動条件、発射/着弾イベント契約。現機能の呼出しだけで新規提案の全てが存在するとはしない。

## 画像・操作審査
1. SCREENSのID/解像度を固定し同じsample state/DPR/フォントで撮影。previewを実映像からmaskしてUI差分を別測定。旧原画像との一致審査と本提案の審査を混ぜない。
2. panel境界±2論理px、control位置/大きさ±2、fontsize±1、gap±2、色は指定token。閾値は提案。差分の大きい場所をoverlay/heatmapで人が確認し「寸法一致だけで外観合格」にしない。
3. 1920/1366、light/dark/system、100/125/150%DPI。preview最小480×270、全体水平scroll0、panel内scrollのみ。大きな文字/Windows高コントラストも別検証。
4. 10カメラ/BLUE/RED/数値、素材1/651/35、6登場、各設定への到達、scene選択・出力チェック・Undo/redo・保存を各案から確認。
5. UI/theme/簡単詳細切替の前後で共有状態digest一致、mirrorSession/job ID一致。外観だけでなくPlay/Stopが録画を意図せず止めないか確認。
6. キーボードのみで開く→選ぶ→適用/取消→閉じる、Esc、focus復帰、modal背景無効、drawer非trap。ネストdialogは原則避ける。
7. 実Replay、BLUE/RED、TargetLock、GPU、LoL音、AV同期、実MP4は別の実機合否表。オフラインmock/画像一致でPASSにしない。
