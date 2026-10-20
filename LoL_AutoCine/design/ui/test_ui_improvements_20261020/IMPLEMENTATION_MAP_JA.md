# Codex向けUI実装対応表
対象ソースは固定コミット feb895491ca4bc780da4aab91990f25177cd35ab。行番号は参照時点、実装時は関数名・変数名で照合する。今回はこの表と画像のみを納品し、実装は行わない。

| UI部品 | 現行接続先 | 種別・保持事項 |
|---|---|---|
| 全体レイアウト | legacy_app.py App._build、topdeck、center_preview_host、center_edit_scroll、ScrollFrame | Aは既存配置の整理。B/Cは親フレーム再配置案。中央をスクロールの子にしない |
| 簡単／詳細 | var_edit_mode、_apply_edit_mode | 既存。変数を共有し、切替で値を破棄しない |
| リプレイ／準備 | on_open_replay、on_play_recent、on_quick_prepare、on_fix_cfg | 既存。ショートカットと補助設定を残す |
| 対象選手 | tree、on_lock、locked、var_camera_side | 既存TargetLockの処理を変更しない |
| 試合全体スキャン | on_scan、pb_scan、lbl_scan | 既存。接続・10人取得を重複実行する新処理は作らない |
| シーン一覧 | lb_kills、on_scene_selection、_on_kill_list_click、var_event_mode、var_scene_player_filter | 既存。選択行とチェック状態を分ける |
| シーンへ移動 | on_jump_selected | 既存 |
| 全選択／解除 | on_check_all、on_uncheck_all、on_toggle_checked | 既存 |
| 動画作成 | on_make_selected、on_make_checked、on_make_clips | 既存。プレビュー操作から呼ばない |
| 簡単自動作成 | on_one_click、on_smart_one_click | 既存。Cでも詳細メニュー等に残す |
| ミラー開始／停止 | on_mirror_start、on_mirror_stop、var_preview_hz、var_preview_quality、var_live | 既存。表示目標Hzと実測表示FPSを混同しない |
| 演出プレビュー | on_preview_play、on_preview_stop | 既存。LoL上でカメラ等を再生、録画しない。停止は既存stop_evを共用するため録画中の競合確認が必要 |
| 前後トリム | ui/scene_timeline.py SceneTimeline、var_pre、var_post | 既存。1〜15秒、0.5秒刻み、Template.pre/postを共有 |
| キル選択タイムライン | 新しいCanvas行 → on_scene_selection相当の共通選択処理、on_jump_selected | **新規UI案**。同じkillsとscene_keyを用い、独立したイベント台帳を作らない |
| モードカード | ui/director_work_controls.py build、var_camera_control_mode、MODE_LABELS、core/smart_camera_director.py CONTROL_MODES | 既存値manual/fixed_auto/full_auto/None。カードUIは新規表示案 |
| サイド選択 | var_camera_side、CAMERA_SIDE_CHOICES | 既存。対象選手から自動判定と明示BLUE/REDを区別 |
| 10スタイル | var_style、core/camera.py STYLES | 既存スタイルを使用。画像ボタンは新規UI。ボタン文言で内部キーを新設しない |
| 数値・スライダー | sl、sl_labels、_slider_range、_set_camera_motion、on_camera_safe_pose | 既存変数と範囲。距離・高さ・Yawのみ戻す既存安全設定も残す |
| 自動選択QA候補 | camera_auto_qa_approved、camera_auto_excluded、director_work_controls.open_settings | 既存手動承認。BLUE/RED別の候補を勝手に合格させない |
| フルオート判断 | core/smart_camera_director.py decide_camera | 内部ロジック変更対象外。承認済み候補なしの固定視点フォールバックを維持 |
| 既存37バッジ | _open_kill_frame_gallery、ui/kill_frame_gallery.py、var_kill_icon_style、core/kill_icons.py STYLES | 既存。Work素材と別名前空間、表示サムネイルのみ改善 |
| Work枠／FX図鑑 | _open_work_gallery、ui/work_gallery.py、assets/work_kill_assets/catalog.json | 既存検索・状態・分類・ページ送り・レスポンシブを流用。埋込みインスペクタは新規UI |
| 枠＋同名FX選択 | director_work_controls.select_frame_with_effect、var_work_frame、var_work_effect | 既存IDと同名ペア判定を流用。枠承認とFX承認は別 |
| 未合格素材／強さ | var_work_review、var_work_strength | 既存。review使用は品質台帳を更新しない |
| 登場アニメ | var_kill_icon_motion、core/kill_icons.py MOTION_STYLES | 既存6種。画像カードは新規UI |
| シーン設定 | on_save_scene、on_scene_undo、on_scene_redo、on_copy_scene_settings、on_paste_scene_settings、on_apply_shot_to_checked | 既存。設定の保存先と適用範囲を維持 |
| キーフレーム | on_keyframe_upsert、on_keyframe_remove、on_keyframe_preview、on_keyframe_preset | 既存詳細への導線を維持 |
| プロジェクト／順序 | on_scene_export、on_scene_import、on_move_scene、on_reset_scene_order | 既存。新タイムラインで非対応の編集を追加しない |
| テンプレート／参考 | _open_template_gallery、apply_template、_focus_reference | 既存。B/Cのヘッダー／準備メニューに残す |
| 出力 | var_fps_ui、on_pick_out、on_open_out、on_stop、pb_job、lbl_job | 既存出力設定・中止を保つ。ミラーHzと出力FPSは別 |
| 基本設定 | _focus_settings、_focus_editor_zone | 既存GPU・音声・HUD・色・出力等への導線。各詳細設定を削除しない |
| 一括QA | on_dev_camera_qa | 既存。カメラ動画・Work整合性・図鑑・GPUミラー計測・診断ZIP。録画なしではない |
| 自動診断／ログ | on_automatic_qa、on_show_diagnostics | 既存。ログ原文と出力物への経路を維持 |
| テスト結果パネル | 既存ログ・ジョブ状態・QA成果物を参照する集約ビュー | **新規UI案**。新しい合否判定エンジンは作らない。未実行を既定表示 |
| 1366×768 | root.minsize現行1280×780、PanedWindow比率、右／下タブ切替 | **新規UI案**。最小高さ変更とDPI実機確認が別途必要 |

## 実装時の確認項目
- 左右のスクロール、カメラカード切替、簡単／詳細、素材選択でミラーが隠れないこと。
- 同じIDのシーンが一覧と新規タイムラインで同期し、チェック状態とフォーカスが独立していること。
- 既存スライダーの範囲・変数・プロジェクトJSON・Undo/Redoが保持されること。
- プレビュー停止・録画ジョブ中止の共有stop_evを確認し、既存処理を無断変更しないこと。
- フルオートに未承認候補が混入せず、BLUE/RED別の承認が維持されること。
- フレーム合格をFXへ継承せず、確認用素材の出力にも状態表示を残すこと。
- 1366×768、1920×1080とWindowsのDPI倍率で操作領域を確認すること。

この一覧は将来のUI実装担当向け。上記の実機確認は今回の静止画像納品では実施していない。

