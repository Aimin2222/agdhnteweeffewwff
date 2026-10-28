# カメラ統合仕様

基準：`bd93e2caf3bdb823d52b86fead0d71fc15c41327`。三人称斜め後ろ・既存RED FPS/geo_aimを保護し、UI都合で計算を置き換えません。今回確認したのはコードと既存研究で、実LoLでの新しい成功判定はありません。

## 既存能力と入力

10style：third_cinema / third / geo_aim / cinema / fps / orbit / lolnam_cinema / follow / cinema_top / top。UIの「5geo aim」は既存geo_aimの表示別名として説明し、別の未知styleへ変換しません。manual / fixed_auto / full_autoはstyleと独立。TargetLockのplayer ID、camera_side、style、modeを別フィールドにし、BLUE/RED切替で対象playerを変えません。

thirdは通常斜め後ろ、third_cinemaは寄り・低角度・キルcue、lolnam_cinemaは回り込み/ドリー/FOV/multi補正、fpsは安全高さ/side別経路を持ちます。orbitは既存軌道です。全styleへ同じキー機能を架空適用せず、現行キーはTHIRD_STYLESに限定。UIで不適用の理由を表示します。

距離500..1400、cam_height0..900、third_yaw−180..180°、motion_arc0..45°、dolly0..15%。`cam_height`はFPS系高さ補正で、`third_elev`(仰角)とは別。SceneProject arcは0..75°を許すため、global45°へ縮めて保存し直さない。scope別rangeを明示します。third_elev等の専用APIがない数値は、既存Template/カメラ評価の有効域を確認して追加し、UIの希望rangeを既存型へ押し込みません。

現在R1/R2 `cameraControls`は入力値だけ`v.third_y`を読み、実状態は`third_yaw`を返します。読み取りを`v.third_yaw`へ変更し、32°→poll→R1/R2/C3→scene/theme往復で32°が残ることを確認。送信keyもthird_yawに統一。欠損を0で黙って表示せずunknown/errorにします。

## BLUE/REDと上下反転

ORDER=BLUE、CHAOS=RED。実APIのEulerは現在コードのcamera_tuningとcalibrationを正とし、研究図の軸をゲームへ代入しません。camera_position−target_positionからatan2で向きを計算する経路と、保護された既存経路を維持します。roll=0の経路へ180°rollを加えず、yaw回転は位置/視線へ一貫適用。pitch軸や符号が不明ならトップ/FPSのキャリブレーション結果を検査し、適当な反転を試して成功扱いしません。

side×style×modeの設定はdeep-copyした独立エントリー。BLUEの三人称修正がRED FPS/geo_aimや別styleへ伝播しないことを回帰条件にします。0/90/180/−180°、往復切替、seek前後、対象変更、接続断/再接続でroll/pitch/yaw・target ID・screen captureを取得。過去の古いpitch-sign cache、途中の軸取り違え、180°non-pitchジャンプを再現fixtureとして保持します。数式だけでキャラ可視をPASSにしません。

## キーの保存と評価

SceneProject v3：最大40点、time−15..15秒(キル相対)、yaw−70..70°、zoom−30..30%、fov−15..15°加算。validatorは同時刻の最後の値へ整理、2桁へ丸めます。UI確定時に差が出る値は正規化後の値を表示。精密FX時刻へこの2桁を流用しない。keyframe_upsert/remove/preview、scene_save/undo/redoを再利用し、安定したselected_key IDとscene revisionをadapterで補います。

0点はdelta0、1点は端点値、2点はsmoothstep、3点以上は形状保存Hermite。区間外は端点値。実評価器と同じ関数を曲線表示に使用し、別の見栄え用Bezierを描かない。横軸はキル相対秒、縦軸は選択channelの度/%、playhead/選択点/入力欄を同期。drag中は局所preview、確定時1Undo、Escで戻す。矢印はtime .01秒/valueの定義step、Shiftは10step、範囲外/キー重なりは検証。

linear/hold/freeBezierは現行にない。D03承認後にchannel/segmentごとのinterpolationをschema追加。linearは区間線形、holdは左値を右端直前まで保持、legacy_smoothは旧挙動。Bezierはtime軸単調・非交差ハンドルを検証してx(u)=timeを解きy(u)を評価、CPU/実カメラ/保存で共有。接線の単位はchannel/time、rollやXYZへ勝手に拡張しません。

## 絶対FOV

現行はtime-varying base+delta、通常キー適用時32..100°clamp、full-auto複数キルではさらにBASE_FOV下限。原画の手動48°/選択キー64°は同一入力ではありません。D02推奨は評価器のrawBaseとeffectiveFOVを公開し、delta=request−rawBaseが許容範囲内か検証、最終mode制限で達しない場合は理由表示。クランプ済み値から逆算して損失を隠さない。独立absolute trackにする場合は新schema/評価順序/互換試験が必要。決定前は現在値表示と相対編集を使い、絶対入力は理由付きdisabled。

## カメラプリセット

新しい型`camera-preset`を提案：schema_version / profile_id / side / style / control_mode / camera numeric / target-relative keyframes / optional processing revision。対象player/replay path、色/FX/LUT、素材、音声、出力先は含めない。global/focused-scene適用scopeを確認し、旧Templateとは識別子で区別。scene applyはdeep-copy、旧projectを直接上書きしません。

## 自動構図の拡張

現行smart_camera_directorはclip境界だけで、side別の明示QA許可と除外を使い、multiplicityからwide styleを優先します。敵位置や地形遮蔽をkill metadataから生成しません。新しい複数人包含/長射程2端点/遮蔽回避は別候補として、同時刻の参加者world位置・FOV投影・depth/visibility confidenceが必須。欠測時は既存baselineを保持して理由を記録。

候補評価は対象包含率、safe-frame、遮蔽confidence、速度/加速度/追従遅れ、切替不連続を個別scoreにする研究契約。閾値は実LoL正解付き検証で決め、未測定の値を正式最適値にしません。走行中のstyle変更は既定で禁止。手動指定/既存三人称が常に優先、候補追加で既存cache/accepted profileを共有変更しません。

根拠：[bd93e2c camera.py](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/camera.py)、[camera_tuning.py](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/camera_tuning.py)、[smart_camera_director.py](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/smart_camera_director.py)、[SceneProject](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/scene_project.py)。数値一覧/実装依存/テストIDは付属JSONを参照。
