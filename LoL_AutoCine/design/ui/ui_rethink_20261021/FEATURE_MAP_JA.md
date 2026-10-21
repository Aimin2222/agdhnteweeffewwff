# UI部品と既存AutoCine機能の対応
参照コミット：a7e1db5a205cb1dd2448f857c83ec7e53899835c。今回、以下への接続・変更はしていない。全案は同じ編集モデルと既存処理を使う想定。

| UIの役割・部品ID | 既存の表示・処理・変数 | 新設／維持の境界 |
|---|---|---|
| ヘッダー・基本設定 | legacy_app.App、ReferenceStudio._header、_show_legacy_settings、_focus_settings | 新しい主経路を設計。旧設定を削除しない |
| Eの準備段階・リプレイ | on_quick_prepare、on_fix_cfg、on_open_replay、on_play_recent | 既存。準備済みと接続成功を混同しない |
| 対象選手・TargetLock | tree、locked、on_lock | 既存。ワークスペース／テーマで解除しない |
| 試合スキャン | on_scan、pb_scan、lbl_scan、_match_scan_cache | 既存。手順を整理する表示案 |
| scene-list / scene-wall / kill-ribbon | lb_kills、kills、checked_kills、on_scene_selection、ReferenceStudio._render_scenes/_select_scene | 同じシーンキーを共有する3種類の見せ方 |
| キル・アシスト・プレイヤー絞込 | var_event_mode、var_scene_player_filter、_on_scene_player_filter_changed | 既存。絞り込みで出力チェックを失わない |
| 出力チェック／全選択／解除 | on_toggle_checked、on_check_all、on_uncheck_all | 既存。プレビューのフォーカスと別状態 |
| 選択シーンへ移動 | on_jump_selected | 既存 |
| one-click：Eのおすすめ自動作成 | on_one_clickを標準、on_smart_one_clickは演出重視の明示選択 | 既存2処理を勝手に統合しない。Eの既定は確認用FXを使わない標準 |
| export：A/C/Fの動画作成 | on_make_checked、必要に応じon_make_selected／on_make_clipsへの選択UI | 既存。対象件数と範囲を表示 |
| Bのプリセット | templates、var_tpl、apply_template、_open_template_gallery、_choose_easy_preset | 既存テンプレートの画像選択表示案。模擬サムネイルを実出力比較と扱わない |
| 参考動画 | _focus_reference、既存URL／ローカル参照・テンプレート作成 | 既存。B入口と基本設定に残す |
| preview-panel / preview-controls | on_mirror_start、on_mirror_stop、var_preview_quality、var_preview_hz、var_live | 既存WGCとGPU表示。見た目のために再起動・再初期化しない |
| 演出確認／停止 | on_preview_play、on_preview_stop | 既存、録画なし。stop_ev共有の録画中競合は実装時に確認 |
| 目標Hzと実測・録画状態 | var_preview_hz、var_encoder_policy、var_gaudio、var_hud_mode、ReferenceStudio._refresh_runtime_status | 設定方針と実行実績は別。未取得値は—。成功の固定文言は使わない |
| timeline | ReferenceStudio._timeline/_draw_timelineと_select_scene | 試合イベント選択はすでに存在。トラックの自由編集ではない |
| trim | SceneTimeline、var_pre、var_post、Template.pre/post | 既存、1〜15秒、0.5秒刻み。数値と図を共有 |
| camera-modes | var_camera_control_mode、director_work_controls.build、CONTROL_MODES | manual／fixed_auto／full_auto／既存維持None。UI名を内部モードに追加しない |
| サイド選択 | var_camera_side、CAMERA_SIDE_CHOICES | 自動／BLUE／RED。BLUE＝常に味方という表現にしない |
| style-tiles | var_style、STYLES、ReferenceStudio._set_camera_style | 既存10種。画像は配置例。実装では既存QAの実画像等に置換 |
| slider-third_dist / cam_height / third_yaw | sl、sl_labels、_slider_range、on_camera_safe_pose | 既存値・範囲を維持。三人称距離500〜1400、高さ0〜900、Yaw−180〜180 |
| slider-motion_arc / motion_dolly | motion_arc、motion_dolly、_set_camera_motion | 既存。回り込み0〜45、ドリー0〜15 |
| 自動カメラ候補・QA | camera_auto_qa_approved、camera_auto_excluded、decide_camera、director_work_controls.open_settings | 既存の手動承認とサイド別判定を保つ。未確認候補は自動合格させない |
| material-library | work_gallery、ReferenceStudio._library、catalog.json、_open_work_gallery | 検索・状態・分類・ページ送りは既存。固定ミラーと一体に見せる新しい表示層 |
| 既存37バッジ | kill_frame_gallery、var_kill_icon_style | Work枠と区別して維持 |
| frame / FX選択 | var_work_frame、var_work_effect、select_frame_with_effect、ReferenceStudio._apply_asset/_apply_effect | 同名ペア選択を維持。枠とFXの合否を共有しない |
| 確認用の使用・弱強 | var_work_review、var_work_strength | 既存。使用許可は承認操作ではない |
| motion-grid | var_kill_icon_motion、MOTION_STYLES | instant、slide_left、slide_right、slide_up、slide_down、popの既存6種 |
| C動作表示・F phase-0/1/2 | on_keyframe_upsert/remove/preview/preset、kf_vars、シーン別設定、var_pre/post、ショット設定 | 新しい表示整理。自由な新カメラ／別動画エンジンは作らない |
| シーンの保存・元戻す | on_save_scene、on_scene_undo、on_scene_redo、on_clear_scene | 既存 |
| コピー・貼付・一括適用 | on_copy_scene_settings、on_paste_scene_settings、on_apply_shot_to_checked | 既存詳細から維持 |
| プロジェクト・順序 | on_scene_export/import、on_move_scene、on_reset_scene_order、SceneProject | 既存JSONとUndoを維持 |
| 色・DOF・FX | _focus_editor_zone、既存のsl／scene_fx_vars等 | 選択シーンか全体かを明示。テーマの色と映像の色を混ぜない |
| GPU・録画・音声・HUD | var_encoder_policy、var_gaudio、var_hud_mode、ゲーム音/BGM各変数と既存詳細 | 内部処理は変更対象外。原設定画面への導線を残す |
| 出力先／FPS／中止 | var_fps_ui、on_pick_out、on_open_out、on_stop、pb_job、lbl_job | 既存。ミラーHzと出力FPSを分離 |
| テスト結果・ログ・警告 | on_automatic_qa、on_show_diagnostics、on_dev_camera_qa | 既存。一括QAは動画・診断ZIPを作る。合否をUIが捏造しない |
| theme-switch | 現行の表示色から独立したappearance.modeを新設する提案 | **新規UI機能**。ライト／ダーク／Windows追従を保存。カメラ変数等には触らない |

## 接続時の注意
Eの「おすすめで自動作成」にon_smart_one_clickを無条件で結び付けると、標準より演出が強い処理へ変わる。採用時は標準／スマートを明示して既存の意図を保つ。モックの説明用のデータや選択状態を実プロジェクトの既定値としてコピーしない。

本文に挙げたハンドラーは参照時点のもの。将来の変更に追従する際は、名前だけでなく実際の変数と処理内容を読み直す。今後の本体コード変更や既存テストのスキップを認める資料ではない。


新規プロジェクトの標準例と、既存プロジェクトの値は分ける。Eへ戻った時にFXや詳細値を標準例へ戻さず、現在のモデル値と確認用素材の有効状態を要約表示する。
