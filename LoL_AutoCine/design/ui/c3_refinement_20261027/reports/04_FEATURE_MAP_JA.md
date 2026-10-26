# 70機能の配置案

接続提案です。handlerは以前の監査から継承し、最新アプリでは未照合です。未実装研究機能の正式実装を意味しません。

| ID | 機能 | 両追加案での入口 |
|---|---|---|
| REPLAY | Replay API接続 | 左 準備・TargetLock |
| LAUNCH | ROFL起動・最近のリプレイ | 左 準備・TargetLock |
| PLAYER | 対象プレイヤー固定 | 左 準備・TargetLock |
| SCAN | 試合全体スキャン | 右 スキャン・検出シーン > 条件 |
| ASSIST | キル／アシスト／両方 | 右 スキャン・検出シーン > 条件 |
| MULTI | 連続キル判定 | 右 スキャン・検出シーン > 条件 |
| SCENE | シーン編集・保存 | 下部 シーン/タイムライン・カーブ |
| TIMELINE | シーンタイムライン | 下部 シーン/タイムライン・カーブ |
| KEYFRAME | 相対yaw/zoom/FOVキーフレーム | 下部 シーン/タイムライン・カーブ |
| HIGHLIGHT | 既存おまかせ演出 | 右 スキャン・検出シーン > 条件 |
| SMARTMONTAGE | 既存シーン採点・並べ替え | 下部 シーン/タイムライン・カーブ |
| HUD | HUD非表示・復元 | 上 基本設定 / 下 出力 > 作成内容確認 |
| MIRROR | ミラー・表示FPS | 中央ミラー > 再生 / 基本設定 |
| CAPTURE | WGC/共有メモリ取得 | 中央ミラー > 再生 / 基本設定 |
| RECORD | 録画・時刻整合 | 上 基本設定 / 下 出力 > 作成内容確認 |
| JOB | チェック済み・複数クリップ作成 | 上 基本設定 / 下 出力 > 作成内容確認 |
| AUDIO | LoLプロセス専用録音 | 上 基本設定 / 下 出力 > 作成内容確認 |
| AUDIOGUARD | 音声必須時の失敗伝播 | 上 基本設定 / 下 出力 > 作成内容確認 |
| BGM | BGMミックス・音量 | 上 基本設定 / 下 出力 > 作成内容確認 |
| NVENC | GPUエンコード・CPU代替 | 上 基本設定 / 下 出力 > 作成内容確認 |
| GPUFX | OpenCL全体FX経路 | 下部 色・FX > 詳細/基本設定GPU |
| GRADE | 16グレード・LUT・カーブ | 下部 色・FX > 詳細/基本設定GPU |
| FOG | ゲーム内Fog | 下部 色・FX > 詳細/基本設定GPU |
| DOF | ゲーム内DOFと後段焦点表現 | 下部 色・FX > 詳細/基本設定GPU |
| PULSE | キル時ハイライト | 下部 色・FX > 詳細/基本設定GPU |
| BADGE | 既存37キルバッジ | 下部素材カード > 素材ドロワー |
| WORKFRAME | Workフレーム候補 | 下部素材カード > 素材ドロワー |
| WORKFX | Workエフェクト候補 | 下部素材カード > 素材ドロワー |
| MOTION | 登場アニメ6種 | 下部素材カード > 素材ドロワー |
| REFERENCE | 参考映像の局所特徴抽出 | 下部素材カード > 素材ドロワー |
| PREVIEW | 近似プレビューと厳密静止画 | 中央ミラー > 再生 / 基本設定 |
| MONTAGEFX | 連結後の明暗トランジション | 下部 色・FX > 詳細/基本設定GPU |
| SELFQA | 既存自己診断 | 上 ログ > 診断 |
| DIAG | 性能診断・QAパッケージ | 上 ログ > 診断 |
| CAM_third_cinema | third_cinema | 下部カメラ > 詳細ドロワー |
| CAM_third | third | 下部カメラ > 詳細ドロワー |
| CAM_geo_aim | geo_aim | 下部カメラ > 詳細ドロワー |
| CAM_cinema | cinema | 下部カメラ > 詳細ドロワー |
| CAM_fps | fps | 下部カメラ > 詳細ドロワー |
| CAM_orbit | orbit | 下部カメラ > 詳細ドロワー |
| CAM_lolnam_cinema | lolnam_cinema | 下部カメラ > 詳細ドロワー |
| CAM_follow | follow | 下部カメラ > 詳細ドロワー |
| CAM_cinema_top | cinema_top | 下部カメラ > 詳細ドロワー |
| CAM_top | top | 下部カメラ > 詳細ドロワー |
| FIXED | 固定自動 | 下部カメラ > 詳細ドロワー |
| FULL | フルオートシネマ | 下部カメラ > 詳細ドロワー |
| FX_motion_camera | motion_camera | 下部 色・FX > 詳細/基本設定GPU |
| FX_radial_blur | radial_blur | 下部 色・FX > 詳細/基本設定GPU |
| FX_zoom_blur | zoom_blur | 下部 色・FX > 詳細/基本設定GPU |
| FX_glitch | glitch | 下部 色・FX > 詳細/基本設定GPU |
| FX_kaleidoscope | kaleidoscope | 下部 色・FX > 詳細/基本設定GPU |
| FX_vhs_damage | vhs_damage | 下部 色・FX > 詳細/基本設定GPU |
| FX_block_motion | block_motion | 下部 色・FX > 詳細/基本設定GPU |
| FX_spin_motion | spin_motion | 下部 色・FX > 詳細/基本設定GPU |
| FX_chroma_leak | chroma_leak | 下部 色・FX > 詳細/基本設定GPU |
| FX_flash | flash | 下部 色・FX > 詳細/基本設定GPU |
| FX_focus_blur | focus_blur | 下部 色・FX > 詳細/基本設定GPU |
| FX_vignette_fx | vignette_fx | 下部 色・FX > 詳細/基本設定GPU |
| FX_glint | glint | 下部 色・FX > 詳細/基本設定GPU |
| FX_camera_shake | camera_shake | 下部 色・FX > 詳細/基本設定GPU |
| FX_wiggle | wiggle | 下部 色・FX > 詳細/基本設定GPU |
| FX_vr_blur | vr_blur | 下部 色・FX > 詳細/基本設定GPU |
| FX_vr_light_leak | vr_light_leak | 下部 色・FX > 詳細/基本設定GPU |
| FX_sphere_blur | sphere_blur | 下部 色・FX > 詳細/基本設定GPU |
| FX_panel_wipe | panel_wipe | 下部 色・FX > 詳細/基本設定GPU |
| FX_stretch_wipe | stretch_wipe | 下部 色・FX > 詳細/基本設定GPU |
| FX_mirror | mirror | 下部 色・FX > 詳細/基本設定GPU |
| FX_slice | slice | 下部 色・FX > 詳細/基本設定GPU |
| ENGAGE | エンゲージ独立検出 | 右 スキャン・検出シーン > 条件 |
| BESTSHOT | 画像品質によるベストショット選択 | 右 スキャン・検出シーン > 条件 |
