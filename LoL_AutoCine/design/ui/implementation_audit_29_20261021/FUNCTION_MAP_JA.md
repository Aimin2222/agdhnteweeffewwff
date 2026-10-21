# 全案共通 AutoCine機能接続契約

参照：a7e1db5a205cb1dd2448f857c83ec7e53899835c（2026-10-21確認）。全29画面から同じ機能へ到達する契約。ここに名前があることは実装完了の証明ではない。

| ID | 機能 | 既存接続 | 必須動作・不足 |
|---|---|---|---|
| F01 | LoL接続・準備 | `on_quick_prepare / on_open_replay / on_play_recent` | 接続先・リプレイ状態と10人取得を実結果で表示。設定準備と実接続成功を分ける。 |
| F02 | TargetLock・選手 | `tree / locked / on_lock` | 選択プレイヤーIDを保持。BLUE/REDは実サイド。テーマ切替で解除しない。 |
| F03 | 試合全体スキャン | `on_scan / pb_scan / lbl_scan / _match_scan_cache` | 進捗・失敗・キャンセルを処理から購読。押下直後に成功を表示しない。 |
| F04 | キル・アシスト絞込 | `var_event_mode / var_scene_player_filter` | キル／アシスト／キル＋アシスト。絞込と出力チェックを別管理。 |
| F05 | エンゲージ選択 | `未確認・新規能力契約 events.engage` | 参照UIの対応モード・専用ハンドラーは確認できない。killへ偽装接続しない。能力がない時は「エンゲージ未対応」を説明付き表示。全案の受入は実能力追加後に別検証。 |
| F06 | シーン焦点・ジャンプ | `on_scene_selection / on_jump_selected / ReferenceStudio._select_scene` | 安定シーンIDを共有。行の選択と書き出しチェックを別にする。 |
| F07 | 出力チェック | `checked_kills / on_toggle_checked / on_check_all / on_uncheck_all` | 全選択・解除・件数を同じ集合から描画する。 |
| F08 | 実ミラープレビュー | `on_mirror_start / on_mirror_stop / var_live / var_preview_hz` | 既存WGCの同一セッションを表示。未接続は明示。静止イラストで実接続成功を装わない。目標Hzと実測FPSを分ける。 |
| F09 | 演出プレビュー再生・停止 | `on_preview_play / on_preview_stop` | 録画しない確認操作。stop_ev共用があるため録画中の停止競合を実装段階で検証する。 |
| F10 | カメラモード・サイド | `var_camera_control_mode / var_camera_side` | manual / fixed_auto / full_auto / 既存維持None。サイドは自動・BLUE・RED。 |
| F11 | 10カメラスタイル | `var_style / STYLES / ReferenceStudio._set_camera_style` | third_cinema, third, geo_aim, cinema, fps, orbit, lolnam_cinema, follow, cinema_top, top。カード文言と内部値を分離。 |
| F12 | 数値・動作・自動候補 | `sl / _slider_range / on_camera_safe_pose / director_work_controls` | 距離500〜1400、高さ0〜900、Yaw−180〜180、回り込み0〜45、ドリー0〜15。サイド別QA承認候補のみ、候補なしは既存固定へ。 |
| F13 | 37バッジ・89原本 | `kill_frame_gallery / var_kill_icon_style` | Work652候補と分離。89原本と37バッジの素材は変更禁止。 |
| F14 | フレーム652候補 | `var_work_frame / work_gallery / catalog.json` | 参照時点は正式合格No.083/a_simple_mainの1件、確認用651件。実装時はカタログ実値を表示。 |
| F15 | FX35・ペア・強度 | `var_work_effect / select_frame_with_effect / var_work_strength / var_work_review` | 35点はすべて確認用。枠合格を同名FXに継承しない。確認用使用チェックは承認ではない。 |
| F16 | 登場6種類 | `var_kill_icon_motion / MOTION_STYLES` | instant／slide_left／slide_right／slide_up／slide_down／pop。popは既存の横方向減衰位置ずれ。未実装の拡縮等を追加しない。 |
| F17 | タイムライン・前後トリム | `ReferenceStudio._timeline/_draw_timeline / SceneTimeline / var_pre / var_post` | イベント選択と前後トリム1〜15秒・0.5秒刻み。4トラックは自由な多重動画編集エンジンを意味しない。 |
| F18 | 保存・Undo・コピー・順序 | `on_save_scene / on_scene_undo/redo / on_clear_scene / on_copy_scene_settings / on_paste_scene_settings / on_apply_shot_to_checked / on_move_scene / on_reset_scene_order` | 簡単／詳細と候補切替で値を初期化しない。画像の分割／削除は既存機能との意味を明示して実装。 |
| F19 | キーフレーム・色・DOF | `on_keyframe_upsert/remove/preview/preset / kf_vars / scene_fx_vars / _focus_editor_zone` | CのグラフやFの3フェーズは既存モデルの表示層。新しいカメラ計算を暗黙追加しない。 |
| F20 | プロジェクト・テンプレート・参考 | `on_scene_export/import / SceneProject / apply_template / _open_template_gallery / _focus_reference` | 既存保存形式を保持。プリセット適用は明示操作。テーマや候補切替では適用しない。 |
| F21 | GPU/NVENC・録画 | `var_encoder_policy / 既存録画処理 / _refresh_runtime_status` | 設定方針と実際に使用したエンコーダを区別。NVENC成功は実ログ・出力で検証。 |
| F22 | LoLゲーム音声・BGM・HUD | `var_gaudio / var_hud_mode / 既存音量変数 / _show_legacy_settings` | ゲーム音・BGM・HUD全設定への導線を維持。テーマは映像の色設定から独立。 |
| F23 | 動画作成・出力・中止 | `on_make_selected / on_make_checked / on_make_clips / on_one_click / on_smart_one_click / on_stop / on_pick_out / var_fps_ui` | 対象1件／チェック分／全検出を明示。標準とスマートを選別。演出確認と録画を書き分ける。 |
| F24 | テスト・診断・ログ | `on_automatic_qa / on_dev_camera_qa / on_show_diagnostics` | 一括QAは動画・診断ZIPを作る。未実行・失敗・合格・要確認を実データで表示。 |
| F25 | テーマ・候補切替 | `新設UI契約 appearance.mode / candidateId / viewId` | light / dark / systemを保存。状態は同じモデルから購読し、バックエンド再生成をしない。 |

F05エンゲージは専用接続を確認できなかった。今回は処理追加をせず、能力未提供として明示する。すべての実接続試験はCodex実装時に実施する。
