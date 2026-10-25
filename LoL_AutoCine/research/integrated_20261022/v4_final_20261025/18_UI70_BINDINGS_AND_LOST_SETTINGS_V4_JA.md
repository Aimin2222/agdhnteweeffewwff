# 70機能・設定フィールド・旧操作の保持

core/effects.pyのTemplate宣言をASTで読み、型/既定式/行番号/注釈を全保存。ui/audit29_runtime.pyの宣言actionと70監査項目を対応付けました。専用操作がない項目をnative_settingsへ案内することと、専用操作が実装済みであることを混同しません。ENGAGE/BESTSHOTは未実装提案を維持。

|ID|既存Templateキー|宣言済みaction（実動未検証）|
|---|---|---|
|REPLAY||connect|
|LAUNCH||open_replay,prepare|
|PLAYER||target_lock|
|SCAN|pre,post,merge_multikill|scan|
|ASSIST||event_mode|
|MULTI|merge_multikill,pre,post|scan|
|SCENE|scene_keyframes,pre,post|scene_save,scene_undo,scene_redo,project_export,project_import|
|TIMELINE|pre,post,scene_keyframes|select_scene,jump_selected,check_scene|
|KEYFRAME|scene_keyframes|native_editor_zone|
|HIGHLIGHT|smart_highlight_enabled,smart_highlight_style,smart_composition,highlight_pulse|export_smart|
|SMARTMONTAGE|smart_montage|export_smart|
|HUD|hide_hud,keep_champion_bars|hud|
|MIRROR|capture_fps|mirror_start,mirror_stop|
|CAPTURE|capture_fps|mirror_start,export_selected|
|RECORD|capture_fps,fps,game_audio|export_selected,cancel_job|
|JOB|fps,encoder_policy|export_checked,export_all,cancel_job,output_folder|
|AUDIO|game_audio,game_volume|game_audio,native_settings|
|AUDIOGUARD|game_audio|native_settings|
|BGM|bgm_path,bgm_volume,bpm|native_editor_zone|
|NVENC|encoder_policy|encoder_policy|
|GPUFX||native_settings|
|GRADE|grade,grade_strength,temperature,contrast,vignette,grain,bloom,bars,exposure,vibrance,lut_path,curve_enabled,curve_points|native_editor_zone|
|FOG|fog_enabled,fog_preset,fog_strength|native_editor_zone|
|DOF|dof_enabled,dof_preview,dof_blur,dof_focus_distance,dof_near_distance,dof_far_distance,dof_shape,dof_center_x,dof_center_y,dof_radius,dof_feather|native_editor_zone|
|PULSE|highlight_pulse|native_editor_zone|
|BADGE|kill_icon_style,kill_icon_position,kill_icon_scale,kill_icon_duration,kill_icon_opacity,kill_icon_players,kill_frame_color,kill_glow_color,kill_glow_enabled,kill_glow_strength,kill_frame_width,kill_mark_style,kill_sparkle_intensity,kill_stack_gap,kill_icon_motion|frame,native_settings|
|WORKFRAME|work_kill_frame_id,work_kill_review,kill_icon_position,kill_icon_scale,kill_icon_duration,kill_icon_opacity,kill_stack_gap|frame,work_gallery,work_settings|
|WORKFX|work_kill_effect_id,work_kill_review,work_kill_strength|work_settings,effect_strength|
|MOTION|kill_icon_motion|motion|
|REFERENCE|reference_dna,reference_sources,template_origin|native_settings|
|PREVIEW|video_effects|fx_enabled,preview_play,preview_stop,native_settings|
|MONTAGEFX|montage_fx,transition|native_editor_zone|
|SELFQA||native_settings|
|DIAG||native_settings|
|CAM_third_cinema|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_third|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_geo_aim|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_cinema|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_fps|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_orbit|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_lolnam_cinema|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_follow|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_cinema_top|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|CAM_top|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_style,camera_mode,camera_side,camera_number|
|FIXED|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_mode,camera_side,camera_style,camera_number|
|FULL|style,intensity,camera_side,cam_height,dist_scale,third_elev,third_dist,third_yaw,motion_arc,motion_dolly,motion_profile,auto_director_strength,camera_control_mode,camera_auto_excluded,camera_auto_qa_approved|camera_mode,camera_side,camera_style,camera_number|
|FX_motion_camera|video_effects|native_editor_zone|
|FX_radial_blur|video_effects|native_editor_zone|
|FX_zoom_blur|video_effects|native_editor_zone|
|FX_glitch|video_effects|native_editor_zone|
|FX_kaleidoscope|video_effects|native_editor_zone|
|FX_vhs_damage|video_effects|native_editor_zone|
|FX_block_motion|video_effects|native_editor_zone|
|FX_spin_motion|video_effects|native_editor_zone|
|FX_chroma_leak|video_effects|native_editor_zone|
|FX_flash|video_effects|native_editor_zone|
|FX_focus_blur|video_effects|native_editor_zone|
|FX_vignette_fx|video_effects|native_editor_zone|
|FX_glint|video_effects|native_editor_zone|
|FX_camera_shake|video_effects|native_editor_zone|
|FX_wiggle|video_effects|native_editor_zone|
|FX_vr_blur|video_effects|native_editor_zone|
|FX_vr_light_leak|video_effects|native_editor_zone|
|FX_sphere_blur|video_effects|native_editor_zone|
|FX_panel_wipe|video_effects|native_editor_zone|
|FX_stretch_wipe|video_effects|native_editor_zone|
|FX_mirror|video_effects|native_editor_zone|
|FX_slice|video_effects|native_editor_zone|
|ENGAGE|||
|BESTSHOT|||

## UIから失われやすい項目

scene_keyframes/merge_multikill/対象slot/checked scene順序、manual yaw/zoom/FOV単位とcamera_side、旧10style・除外・陣営QA、game_audio requiredとgame/BGM volume、encoder_policyとGPUFXの別状態、curve_points/LUT/fog/DOF形状と半径/feather、旧37色/glow/mark/sparkle、kill_stack_gap/位置/scale/秒/opacity/motion、Work frame/effect/review/strength、reference metadata、montage_fxとtransition、capture_fpsと最終fps。簡単↔詳細、タブ/theme/画面ID変更、保存再起動で値を消さない。

## 接続検査

各70行で、元設定→新画面表示→変更→model→保存→再開→job snapshot→最終出力→ログを往復照合。declared dispatcherだけで接続合格にしない。current adapterのoutput_fpsは60/144許可であり、研究の30fps人工試験をUI30fps対応済みとはしない。camera_numberは有限値/範囲も原文どおり追試。旧Templateのcenter_mosaic退役処理など、既存移行例外まで未知field一般論で復活させない。

Templateの実際の位置はcore/effects.pyです。V3提案のcore/templates.py等は想定変更先に過ぎず、存在確認済み実装先ではないことを訂正します。採用直前に最新headの変更原文を再確認してください。
