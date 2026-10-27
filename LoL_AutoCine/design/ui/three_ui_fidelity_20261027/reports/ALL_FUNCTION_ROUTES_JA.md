# 3UI×70項目の付随先

過去監査の67実装確認/1部分実装(FULL)/2未実装(ENGAGE/BESTSHOT)を継承。最新本体の再監査や接続成功ではありません。

| UI | ID | 機能 | 主画面/タブ | 入口 | 詳細 |
|---|---|---|---|---|---|
| C3 | REPLAY | Replay API接続 | C3.main | 左準備・TargetLock / 上部リプレイ/準備 | C3.camera > 対象詳細 |
| C3 | LAUNCH | ROFL起動・最近のリプレイ | C3.main | 左準備・TargetLock / 上部リプレイ/準備 | C3.camera > 対象詳細 |
| C3 | PLAYER | 対象プレイヤー固定 | C3.main | 左準備・TargetLock / 上部リプレイ/準備 | C3.camera > 対象詳細 |
| C3 | SCAN | 試合全体スキャン | C3.scene | 右スキャン/一覧 > 下段シーン | C3.scene > 条件/連続キル/並び順 |
| C3 | ASSIST | キル／アシスト／両方 | C3.scene | 右スキャン/一覧 > 下段シーン | C3.scene > 条件/連続キル/並び順 |
| C3 | MULTI | 連続キル判定 | C3.scene | 右スキャン/一覧 > 下段シーン | C3.scene > 条件/連続キル/並び順 |
| C3 | SCENE | シーン編集・保存 | C3.scene | 右スキャン/一覧 > 下段シーン | C3.scene > 条件/連続キル/並び順 |
| C3 | TIMELINE | シーンタイムライン | C3.scene | 下段の常設シーンタイムライン | C3.camera > キー/カーブ詳細（追加ペイン） |
| C3 | KEYFRAME | 相対yaw/zoom/FOVキーフレーム | C3.scene | 下段の常設シーンタイムライン | C3.camera > キー/カーブ詳細（追加ペイン） |
| C3 | HIGHLIGHT | 既存おまかせ演出 | C3.scene | 右スキャン/一覧 > 下段シーン | C3.scene > 条件/連続キル/並び順 |
| C3 | SMARTMONTAGE | 既存シーン採点・並べ替え | C3.scene | 右スキャン/一覧 > 下段シーン | C3.scene > 条件/連続キル/並び順 |
| C3 | HUD | HUD非表示・復元 | C3.settings | 上部 GPU・音声・HUD設定 | C3.settings > 対象項目（下段出力からも到達） |
| C3 | MIRROR | ミラー・表示FPS | C3.main | 中央ミラー直下の4操作 | C3.settings > 映像取得/実測 |
| C3 | CAPTURE | WGC/共有メモリ取得 | C3.settings | 上部 GPU・音声・HUD設定 | C3.settings > 対象項目（下段出力からも到達） |
| C3 | RECORD | 録画・時刻整合 | C3.export | 上部作成/右下チェック作成/下段出力 | C3.export > 音声/GPU/出力ジョブ |
| C3 | JOB | チェック済み・複数クリップ作成 | C3.export | 上部作成/右下チェック作成/下段出力 | C3.export > 音声/GPU/出力ジョブ |
| C3 | AUDIO | LoLプロセス専用録音 | C3.export | 上部作成/右下チェック作成/下段出力 | C3.export > 音声/GPU/出力ジョブ |
| C3 | AUDIOGUARD | 音声必須時の失敗伝播 | C3.export | 上部作成/右下チェック作成/下段出力 | C3.export > 音声/GPU/出力ジョブ |
| C3 | BGM | BGMミックス・音量 | C3.settings | 上部 GPU・音声・HUD設定 | C3.settings > 対象項目（下段出力からも到達） |
| C3 | NVENC | GPUエンコード・CPU代替 | C3.export | 上部作成/右下チェック作成/下段出力 | C3.export > 音声/GPU/出力ジョブ |
| C3 | GPUFX | OpenCL全体FX経路 | C3.settings | 上部 GPU・音声・HUD設定 | C3.settings > 対象項目（下段出力からも到達） |
| C3 | GRADE | 16グレード・LUT・カーブ | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FOG | ゲーム内Fog | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | DOF | ゲーム内DOFと後段焦点表現 | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | PULSE | キル時ハイライト | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | BADGE | 既存37キルバッジ | C3.material | 下段右の素材/図鑑 | C3.material > カタログ/参考・抽出 |
| C3 | WORKFRAME | Workフレーム候補 | C3.material | 下段右の素材/図鑑 | C3.material > カタログ/参考・抽出 |
| C3 | WORKFX | Workエフェクト候補 | C3.material | 下段右の素材/図鑑 | C3.material > カタログ/参考・抽出 |
| C3 | MOTION | 登場アニメ6種 | C3.material | 下段右の素材/図鑑 | C3.material > カタログ/参考・抽出 |
| C3 | REFERENCE | 参考映像の局所特徴抽出 | C3.material | 下段右の素材/図鑑 | C3.material > カタログ/参考・抽出 |
| C3 | PREVIEW | 近似プレビューと厳密静止画 | C3.main | 中央ミラー直下の4操作 | C3.settings > 映像取得/実測 |
| C3 | MONTAGEFX | 連結後の明暗トランジション | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | SELFQA | 既存自己診断 | C3.test-results | 下段テスト結果 / 上部ログ | C3.test-results > 診断/未対応説明 |
| C3 | DIAG | 性能診断・QAパッケージ | C3.test-results | 下段テスト結果 / 上部ログ | C3.test-results > 診断/未対応説明 |
| C3 | CAM_third_cinema | third_cinema | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_third | third | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_geo_aim | geo_aim | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_cinema | cinema | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_fps | fps | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_orbit | orbit | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_lolnam_cinema | lolnam_cinema | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_follow | follow | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_cinema_top | cinema_top | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | CAM_top | top | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | FIXED | 固定自動 | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | FULL | フルオートシネマ | C3.camera | 下段カメラカード/対象/数値 | C3.camera > スタイル/環境/詳細 |
| C3 | FX_motion_camera | motion_camera | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_radial_blur | radial_blur | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_zoom_blur | zoom_blur | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_glitch | glitch | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_kaleidoscope | kaleidoscope | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_vhs_damage | vhs_damage | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_block_motion | block_motion | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_spin_motion | spin_motion | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_chroma_leak | chroma_leak | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_flash | flash | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_focus_blur | focus_blur | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_vignette_fx | vignette_fx | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_glint | glint | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_camera_shake | camera_shake | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_wiggle | wiggle | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_vr_blur | vr_blur | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_vr_light_leak | vr_light_leak | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_sphere_blur | sphere_blur | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_panel_wipe | panel_wipe | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_stretch_wipe | stretch_wipe | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_mirror | mirror | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | FX_slice | slice | C3.color-fx | 下段 色・FX | C3.color-fx > CoreFXパラメータ/グレード |
| C3 | ENGAGE | エンゲージ独立検出 | C3.test-results | 下段テスト結果 / 上部ログ | C3.test-results > 診断/未対応説明 |
| C3 | BESTSHOT | 画像品質によるベストショット選択 | C3.test-results | 下段テスト結果 / 上部ログ | C3.test-results > 診断/未対応説明 |
| R2 | REPLAY | Replay API接続 | R2.main | 右上設定 > リプレイ準備/対象（追加接続） | R2.camera > TargetLock/対象詳細 |
| R2 | LAUNCH | ROFL起動・最近のリプレイ | R2.main | 右上設定 > リプレイ準備/対象（追加接続） | R2.camera > TargetLock/対象詳細 |
| R2 | PLAYER | 対象プレイヤー固定 | R2.main | 右上設定 > リプレイ準備/対象（追加接続） | R2.camera > TargetLock/対象詳細 |
| R2 | SCAN | 試合全体スキャン | R2.main | 右上設定 > スキャン（追加接続）/下部ショット列・対象チェック | R2.detail > シーン/前後トリム/連続処理 |
| R2 | ASSIST | キル／アシスト／両方 | R2.main | 右上設定 > スキャン（追加接続）/下部ショット列・対象チェック | R2.detail > シーン/前後トリム/連続処理 |
| R2 | MULTI | 連続キル判定 | R2.main | 右上設定 > スキャン（追加接続）/下部ショット列・対象チェック | R2.detail > シーン/前後トリム/連続処理 |
| R2 | SCENE | シーン編集・保存 | R2.main | 右上設定 > スキャン（追加接続）/下部ショット列・対象チェック | R2.detail > シーン/前後トリム/連続処理 |
| R2 | TIMELINE | シーンタイムライン | R2.detail | 下部常設トラック / 詳細編集・カーブ | R2.curve > 選択キーの時刻/値/補間 |
| R2 | KEYFRAME | 相対yaw/zoom/FOVキーフレーム | R2.detail | 下部常設トラック / 詳細編集・カーブ | R2.curve > 選択キーの時刻/値/補間 |
| R2 | HIGHLIGHT | 既存おまかせ演出 | R2.main | 右上設定 > スキャン（追加接続）/下部ショット列・対象チェック | R2.detail > シーン/前後トリム/連続処理 |
| R2 | SMARTMONTAGE | 既存シーン採点・並べ替え | R2.main | 右上設定 > スキャン（追加接続）/下部ショット列・対象チェック | R2.detail > シーン/前後トリム/連続処理 |
| R2 | HUD | HUD非表示・復元 | R2.export | 右上設定 > 映像取得/GPU/音声/HUD（追加接続） | R2.export > 対応する基本設定へのリンク |
| R2 | MIRROR | ミラー・表示FPS | R2.main | 中央映像と直下の再生/停止 | R2.main > ミラーセッション/演出確認の切替（追加接続） |
| R2 | CAPTURE | WGC/共有メモリ取得 | R2.export | 右上設定 > 映像取得/GPU/音声/HUD（追加接続） | R2.export > 対応する基本設定へのリンク |
| R2 | RECORD | 録画・時刻整合 | R2.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R2.export > 結果・実ファイル/ログ |
| R2 | JOB | チェック済み・複数クリップ作成 | R2.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R2.export > 結果・実ファイル/ログ |
| R2 | AUDIO | LoLプロセス専用録音 | R2.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R2.export > 結果・実ファイル/ログ |
| R2 | AUDIOGUARD | 音声必須時の失敗伝播 | R2.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R2.export > 結果・実ファイル/ログ |
| R2 | BGM | BGMミックス・音量 | R2.export | 右上設定 > 映像取得/GPU/音声/HUD（追加接続） | R2.export > 対応する基本設定へのリンク |
| R2 | NVENC | GPUエンコード・CPU代替 | R2.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R2.export > 結果・実ファイル/ログ |
| R2 | GPUFX | OpenCL全体FX経路 | R2.export | 右上設定 > 映像取得/GPU/音声/HUD（追加接続） | R2.export > 対応する基本設定へのリンク |
| R2 | GRADE | 16グレード・LUT・カーブ | R2.color | 色調整 > ルック/数値/比較 | R2.color > 実LUT/対応パラメータ（能力照合後） |
| R2 | FOG | ゲーム内Fog | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | DOF | ゲーム内DOFと後段焦点表現 | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | PULSE | キル時ハイライト | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | BADGE | 既存37キルバッジ | R2.material | 素材 > 枠/WorkFX/登場/実カタログ | R2.material > 図鑑/承認区分/参考抽出 |
| R2 | WORKFRAME | Workフレーム候補 | R2.material | 素材 > 枠/WorkFX/登場/実カタログ | R2.material > 図鑑/承認区分/参考抽出 |
| R2 | WORKFX | Workエフェクト候補 | R2.material | 素材 > 枠/WorkFX/登場/実カタログ | R2.material > 図鑑/承認区分/参考抽出 |
| R2 | MOTION | 登場アニメ6種 | R2.material | 素材 > 枠/WorkFX/登場/実カタログ | R2.material > 図鑑/承認区分/参考抽出 |
| R2 | REFERENCE | 参考映像の局所特徴抽出 | R2.material | 素材 > 枠/WorkFX/登場/実カタログ | R2.material > 図鑑/承認区分/参考抽出 |
| R2 | PREVIEW | 近似プレビューと厳密静止画 | R2.main | 中央映像と直下の再生/停止 | R2.main > ミラーセッション/演出確認の切替（追加接続） |
| R2 | MONTAGEFX | 連結後の明暗トランジション | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | SELFQA | 既存自己診断 | R2.export | 出力 > 結果/テスト / 設定 > 診断（追加接続） | R2.export > 実ジョブログ/未対応説明 |
| R2 | DIAG | 性能診断・QAパッケージ | R2.export | 出力 > 結果/テスト / 設定 > 診断（追加接続） | R2.export > 実ジョブログ/未対応説明 |
| R2 | CAM_third_cinema | third_cinema | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_third | third | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_geo_aim | geo_aim | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_cinema | cinema | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_fps | fps | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_orbit | orbit | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_lolnam_cinema | lolnam_cinema | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_follow | follow | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_cinema_top | cinema_top | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | CAM_top | top | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | FIXED | 固定自動 | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | FULL | フルオートシネマ | R2.camera | カメラ > モード/スタイル/サイド/数値 | R2.camera > 既存スタイル/ゲーム内環境 |
| R2 | FX_motion_camera | motion_camera | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_radial_blur | radial_blur | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_zoom_blur | zoom_blur | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_glitch | glitch | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_kaleidoscope | kaleidoscope | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_vhs_damage | vhs_damage | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_block_motion | block_motion | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_spin_motion | spin_motion | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_chroma_leak | chroma_leak | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_flash | flash | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_focus_blur | focus_blur | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_vignette_fx | vignette_fx | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_glint | glint | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_camera_shake | camera_shake | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_wiggle | wiggle | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_vr_blur | vr_blur | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_vr_light_leak | vr_light_leak | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_sphere_blur | sphere_blur | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_panel_wipe | panel_wipe | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_stretch_wipe | stretch_wipe | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_mirror | mirror | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | FX_slice | slice | R2.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R2.material > WorkFX選択とは別のCoreFX設定 |
| R2 | ENGAGE | エンゲージ独立検出 | R2.export | 出力 > 結果/テスト / 設定 > 診断（追加接続） | R2.export > 実ジョブログ/未対応説明 |
| R2 | BESTSHOT | 画像品質によるベストショット選択 | R2.export | 出力 > 結果/テスト / 設定 > 診断（追加接続） | R2.export > 実ジョブログ/未対応説明 |
| R1 | REPLAY | Replay API接続 | R1.main | 右上設定 > リプレイ準備/対象（追加接続） | R1.camera > TargetLock/対象詳細 |
| R1 | LAUNCH | ROFL起動・最近のリプレイ | R1.main | 右上設定 > リプレイ準備/対象（追加接続） | R1.camera > TargetLock/対象詳細 |
| R1 | PLAYER | 対象プレイヤー固定 | R1.main | 右上設定 > リプレイ準備/対象（追加接続） | R1.camera > TargetLock/対象詳細 |
| R1 | SCAN | 試合全体スキャン | R1.main | 左スキャン・シーン列 | R1.detail > シーン/前後トリム/連続処理 |
| R1 | ASSIST | キル／アシスト／両方 | R1.main | 左スキャン・シーン列 | R1.detail > シーン/前後トリム/連続処理 |
| R1 | MULTI | 連続キル判定 | R1.main | 左スキャン・シーン列 | R1.detail > シーン/前後トリム/連続処理 |
| R1 | SCENE | シーン編集・保存 | R1.main | 左スキャン・シーン列 | R1.detail > シーン/前後トリム/連続処理 |
| R1 | TIMELINE | シーンタイムライン | R1.detail | 下部常設トラック / 詳細編集・カーブ | R1.curve > 選択キーの時刻/値/補間 |
| R1 | KEYFRAME | 相対yaw/zoom/FOVキーフレーム | R1.detail | 下部常設トラック / 詳細編集・カーブ | R1.curve > 選択キーの時刻/値/補間 |
| R1 | HIGHLIGHT | 既存おまかせ演出 | R1.main | 左スキャン・シーン列 | R1.detail > シーン/前後トリム/連続処理 |
| R1 | SMARTMONTAGE | 既存シーン採点・並べ替え | R1.main | 左スキャン・シーン列 | R1.detail > シーン/前後トリム/連続処理 |
| R1 | HUD | HUD非表示・復元 | R1.export | 右上設定 > 映像取得/GPU/音声/HUD（追加接続） | R1.export > 対応する基本設定へのリンク |
| R1 | MIRROR | ミラー・表示FPS | R1.main | 中央映像と直下の再生/停止 | R1.main > ミラーセッション/演出確認の切替（追加接続） |
| R1 | CAPTURE | WGC/共有メモリ取得 | R1.export | 右上設定 > 映像取得/GPU/音声/HUD（追加接続） | R1.export > 対応する基本設定へのリンク |
| R1 | RECORD | 録画・時刻整合 | R1.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R1.export > 結果・実ファイル/ログ |
| R1 | JOB | チェック済み・複数クリップ作成 | R1.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R1.export > 結果・実ファイル/ログ |
| R1 | AUDIO | LoLプロセス専用録音 | R1.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R1.export > 結果・実ファイル/ログ |
| R1 | AUDIOGUARD | 音声必須時の失敗伝播 | R1.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R1.export > 結果・実ファイル/ログ |
| R1 | BGM | BGMミックス・音量 | R1.export | 右上設定 > 映像取得/GPU/音声/HUD（追加接続） | R1.export > 対応する基本設定へのリンク |
| R1 | NVENC | GPUエンコード・CPU代替 | R1.export | 出力 > 対象/解像度/fps/encoder/音声/実作成 | R1.export > 結果・実ファイル/ログ |
| R1 | GPUFX | OpenCL全体FX経路 | R1.export | 右上設定 > 映像取得/GPU/音声/HUD（追加接続） | R1.export > 対応する基本設定へのリンク |
| R1 | GRADE | 16グレード・LUT・カーブ | R1.color | 色調整 > ルック/数値/比較 | R1.color > 実LUT/対応パラメータ（能力照合後） |
| R1 | FOG | ゲーム内Fog | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | DOF | ゲーム内DOFと後段焦点表現 | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | PULSE | キル時ハイライト | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | BADGE | 既存37キルバッジ | R1.material | 素材 > 枠/WorkFX/登場/実カタログ | R1.material > 図鑑/承認区分/参考抽出 |
| R1 | WORKFRAME | Workフレーム候補 | R1.material | 素材 > 枠/WorkFX/登場/実カタログ | R1.material > 図鑑/承認区分/参考抽出 |
| R1 | WORKFX | Workエフェクト候補 | R1.material | 素材 > 枠/WorkFX/登場/実カタログ | R1.material > 図鑑/承認区分/参考抽出 |
| R1 | MOTION | 登場アニメ6種 | R1.material | 素材 > 枠/WorkFX/登場/実カタログ | R1.material > 図鑑/承認区分/参考抽出 |
| R1 | REFERENCE | 参考映像の局所特徴抽出 | R1.material | 素材 > 枠/WorkFX/登場/実カタログ | R1.material > 図鑑/承認区分/参考抽出 |
| R1 | PREVIEW | 近似プレビューと厳密静止画 | R1.main | 中央映像と直下の再生/停止 | R1.main > ミラーセッション/演出確認の切替（追加接続） |
| R1 | MONTAGEFX | 連結後の明暗トランジション | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | SELFQA | 既存自己診断 | R1.export | 出力 > 結果/テスト / 設定 > 診断（追加接続） | R1.export > 実ジョブログ/未対応説明 |
| R1 | DIAG | 性能診断・QAパッケージ | R1.export | 出力 > 結果/テスト / 設定 > 診断（追加接続） | R1.export > 実ジョブログ/未対応説明 |
| R1 | CAM_third_cinema | third_cinema | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_third | third | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_geo_aim | geo_aim | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_cinema | cinema | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_fps | fps | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_orbit | orbit | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_lolnam_cinema | lolnam_cinema | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_follow | follow | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_cinema_top | cinema_top | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | CAM_top | top | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | FIXED | 固定自動 | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | FULL | フルオートシネマ | R1.camera | カメラ > モード/スタイル/サイド/数値 | R1.camera > 既存スタイル/ゲーム内環境 |
| R1 | FX_motion_camera | motion_camera | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_radial_blur | radial_blur | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_zoom_blur | zoom_blur | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_glitch | glitch | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_kaleidoscope | kaleidoscope | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_vhs_damage | vhs_damage | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_block_motion | block_motion | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_spin_motion | spin_motion | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_chroma_leak | chroma_leak | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_flash | flash | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_focus_blur | focus_blur | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_vignette_fx | vignette_fx | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_glint | glint | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_camera_shake | camera_shake | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_wiggle | wiggle | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_vr_blur | vr_blur | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_vr_light_leak | vr_light_leak | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_sphere_blur | sphere_blur | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_panel_wipe | panel_wipe | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_stretch_wipe | stretch_wipe | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_mirror | mirror | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | FX_slice | slice | R1.detail | 詳細編集 > FX・キル演出（詳細セクション追加） | R1.material > WorkFX選択とは別のCoreFX設定 |
| R1 | ENGAGE | エンゲージ独立検出 | R1.export | 出力 > 結果/テスト / 設定 > 診断（追加接続） | R1.export > 実ジョブログ/未対応説明 |
| R1 | BESTSHOT | 画像品質によるベストショット選択 | R1.export | 出力 > 結果/テスト / 設定 > 診断（追加接続） | R1.export > 実ジョブログ/未対応説明 |
