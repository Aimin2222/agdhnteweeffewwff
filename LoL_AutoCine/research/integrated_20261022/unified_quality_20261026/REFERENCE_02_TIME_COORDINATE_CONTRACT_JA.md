# 時刻・座標・層の実装契約
## 時刻の型
Replay秒、capture wall clock、clip PTS、output PTS、音声sample indexを別フィールドにする。Float秒を小数3桁へ丸めて全段へ使わない。内部は整数ticks＋time_baseまたは有理数。可変速segmentはout=output_in+(replay_time−replay_in)/rate。区間は[replay_in,replay_out)、seek gap内イベントは無効・理由付き、外挿/補間禁止。rate<=0、overlap、output逆行、非有限値を拒否。
CFRでイベントの最初の可視フレームはceil(output_time×fps)。60000/1001等も有理数で計算。VFRは実際のPTS列で最初のPTS>=eventを探す。n/fpsをVFRへ流用しない。元作品のスローを断定してrateを作らない。
同一shot内で速度変更がある場合はcamera takeとbadge/FXをそれぞれ同じTimeMapで再標本化。音声は同じsource区間とoutput durationを使い、pitch変更とtempo変更を分離。pause/seek/取消で時計が飛んだらcontinuity_idを更新する。

## 座標
素材のnative canvas/alpha bbox/portrait hole、基準1920×1080、output video rect、preview viewport rect、DPI device pxを別管理。カメラ位置の3D座標とbadgeの2D pixelは混ぜない。
contain係数k=min(W/Rw,H/Rh)、offset=((W−Rw*k)/2,(H−Rh*k)/2)。reference→output→previewのアフィン変換を合成し、辺座標を最終pixelでhalf-up丸め。出力画像に合わせたpreviewを縮小表示し、各段で素材を再スケールして丸め誤差を累積しない。letterboxをoverlay座標の原点と混同しない。
RGBA合成のalpha型（straight/premultiplied）、transfer/primaries/range、resize filterを記録。RGB非ゼロ/alpha0だけで素材不良としないが、resample時の縁色は背景対照で調べる。形式変換でalpha二重適用を避ける。

## 既存の不一致
V4 CPU出力で1920のbboxは一致、1366でexport[973,84,1312,200]に対しmirror[1086,60,1328,142]、1280でも差があった。RGB/alphaのbboxは検出条件も異なり、完全な同一指標ではない。この結果は今回修正済みではない。
今回のCOORDINATE_CONTRACT_RESULTSは3output×3viewport×3DPI×6motion×3phase×3rect=1458条件。数理上の合成変換だけの検査で、製品rendererは呼んでいない。基準alpha/色/実frame比較による実機試験を別に行う。

## schema（提案）
Event：event_id/type/actor_id/victim_id/replay_time/time_base/evidence/source_hash。
ShotSegment：segment_id/replay_in/out/output_in/out/rate/continuity_id/camera_mode/style/side/target_id/manual_overrides/geometry_provenance/rejection_reasons。
Overlay：asset_namespace/id/hash/catalog_status/portrait_geometry_revision/motion_id/processing_revision/output_event_pts/reference_rect/alpha_mode/color_metadata。
QACase：case_id/input_hashes/commands/environment/expected/actual/status/evidence_paths。statusはPASS/FAIL/REVIEW/NOT_RUNを区別する。metadata不足は成功として扱わない。
