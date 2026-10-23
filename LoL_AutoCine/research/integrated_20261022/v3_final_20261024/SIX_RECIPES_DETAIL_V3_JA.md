# 6演出レシピの詳細仕様 V3

全数値は実装前の提案値。参考作品の実測FOV/距離/LUT/速度ではない。FOV degreesは新adapterの意味上の値であり、既存styleのzoom/距離へ直接代入しない。baseline距離の倍率は世界単位距離が取れる場合だけ変換し、取れなければcamera原設定を保持。旧template値は上書きしない。

## Cinematic

対象：単発/連戦の余韻。映像根拠：V06/V08/V21（動画報告の時刻参照）。

カメラ候補：cinema_top/top/follow。提案距離1.10×baseline、FOV55°、yaw差0°、pitchは承認済み基準のまま。単位変換未検証なら原値維持。

前：−4秒から相手/進路を残す。瞬間：wideを保持。後：最後のkill後.4〜1.4秒cutaway、次engage余白1.5秒未満は抑制。multiはgroup内でcamera/transitionを反復しない。

速度：1.0x基準。任意の最終kill±.25秒だけ0.75x。映像と音声は同じpiecewise mapで再配置。

global FX：neutral grade 0.15、全面flash off。frame：旧37または既存静止承認083を手動選択のまま。未承認651を自動採用しない。peak：初期off、任意選択時はreview表示と弱.45から比較。登場：instant（既存式を保持）。

負荷：低〜中、任意3takeは高。機器別の性能保証なし。fallbackは元scene/承認済みcamera、FXを減らす前にユーザーのfallback policyを確認。解像度/fpsの無断低下は禁止。

既存の土台：scene scan/selection, legacy10 camera/manual keys, HUD, frame/badge/motion selections, grade/basic FFmpeg, output encode/audio。新規：recipe adapter/schema, group-aware climax budget, shot planner/best shot (except low-load), time map contract, warning QA context。

保存/接続：schema_version, recipe_id, revision, explicit_overrides, target_id, team, scene_ids, camera_original_values, shot_plan, time_map, fx_ids_strength_revision, frame_id_hash_status, peak_id_hash_status, motion, hud, encoder, gpu_fx, audio_source_policy, fps, resolution, qa_policy。draft→validate→変更差分→適用→immutable job。手動指定をrecipeで上書きせず、再適用時もoverrideを維持。T01〜T14の該当試験とユーザー承認が必要。

## Impact

対象：単発/最終multiの決着。映像根拠：V22（白plateau約.3秒）/V06（動画報告の時刻参照）。

カメラ候補：cinema_top/top。提案距離1.15×baseline、FOV58°、yaw差0°、pitchは承認済み基準のまま。単位変換未検証なら原値維持。

前：−4秒から相手/進路を残す。瞬間：wideを保持。後：killごとに寄らずgroup最後のpulse後にwide復帰。multiはgroup内でcamera/transitionを反復しない。

速度：通常1.0x、任意climax .2秒0.75x。映像と音声は同じpiecewise mapで再配置。

global FX：corrected flash候補80〜160ms、強度.15〜.30、最後のみ。frame：旧37または既存静止承認083を手動選択のまま。未承認651を自動採用しない。peak：初期off、任意選択時はreview表示と弱.45から比較。登場：pop（既存式を保持）。

負荷：中。stack/flash重複は抑制。機器別の性能保証なし。fallbackは元scene/承認済みcamera、FXを減らす前にユーザーのfallback policyを確認。解像度/fpsの無断低下は禁止。

既存の土台：scene scan/selection, legacy10 camera/manual keys, HUD, frame/badge/motion selections, grade/basic FFmpeg, output encode/audio。新規：recipe adapter/schema, group-aware climax budget, shot planner/best shot (except low-load), time map contract, warning QA context。

保存/接続：schema_version, recipe_id, revision, explicit_overrides, target_id, team, scene_ids, camera_original_values, shot_plan, time_map, fx_ids_strength_revision, frame_id_hash_status, peak_id_hash_status, motion, hud, encoder, gpu_fx, audio_source_policy, fps, resolution, qa_policy。draft→validate→変更差分→適用→immutable job。手動指定をrecipeで上書きせず、再適用時もoverrideを維持。T01〜T14の該当試験とユーザー承認が必要。

## Elegant

対象：duel/小物の余韻。映像根拠：V03/V08（動画報告の時刻参照）。

カメラ候補：follow/cinema_top。提案距離1.05×baseline、FOV52°、yaw差8°、pitchは承認済み基準のまま。単位変換未検証なら原値維持。

前：−4秒から相手/進路を残す。瞬間：wideを保持。後：決着後1秒以内の任意shot、情報不足ならcutawayなし。multiはgroup内でcamera/transitionを反復しない。

速度：1.0x、任意cutawayだけ0.8x。映像と音声は同じpiecewise mapで再配置。

global FX：柔らかいgrade .10、flash/temporal blur off。frame：旧37または既存静止承認083を手動選択のまま。未承認651を自動採用しない。peak：初期off、任意選択時はreview表示と弱.45から比較。登場：instant（既存式を保持）。

負荷：低〜中、DOF/別takeは追加負荷。機器別の性能保証なし。fallbackは元scene/承認済みcamera、FXを減らす前にユーザーのfallback policyを確認。解像度/fpsの無断低下は禁止。

既存の土台：scene scan/selection, legacy10 camera/manual keys, HUD, frame/badge/motion selections, grade/basic FFmpeg, output encode/audio。新規：recipe adapter/schema, group-aware climax budget, shot planner/best shot (except low-load), time map contract, warning QA context。

保存/接続：schema_version, recipe_id, revision, explicit_overrides, target_id, team, scene_ids, camera_original_values, shot_plan, time_map, fx_ids_strength_revision, frame_id_hash_status, peak_id_hash_status, motion, hud, encoder, gpu_fx, audio_source_policy, fps, resolution, qa_policy。draft→validate→変更差分→適用→immutable job。手動指定をrecipeで上書きせず、再適用時もoverrideを維持。T01〜T14の該当試験とユーザー承認が必要。

## Competitive

対象：プレイ解説/HUD重視。映像根拠：V04/V09/V12/V13/V25（動画報告の時刻参照）。

カメラ候補：top/follow。提案距離1.15×baseline、FOV60°、yaw差0°、pitchは承認済み基準のまま。単位変換未検証なら原値維持。

前：−4秒から相手/進路を残す。瞬間：wideを保持。後：前4秒後2秒、fight中cutawayなし。multiはgroup内でcamera/transitionを反復しない。

速度：1.0x固定を初期値。映像と音声は同じpiecewise mapで再配置。

global FX：global FX off、HUD on。frame：旧37または既存静止承認083を手動選択のまま。未承認651を自動採用しない。peak：初期off、任意選択時はreview表示と弱.45から比較。登場：instant（既存式を保持）。

負荷：低、低負荷を実測した意味ではない。機器別の性能保証なし。fallbackは元scene/承認済みcamera、FXを減らす前にユーザーのfallback policyを確認。解像度/fpsの無断低下は禁止。

既存の土台：scene scan/selection, legacy10 camera/manual keys, HUD, frame/badge/motion selections, grade/basic FFmpeg, output encode/audio。新規：recipe adapter/schema, group-aware climax budget, shot planner/best shot (except low-load), time map contract, warning QA context。

保存/接続：schema_version, recipe_id, revision, explicit_overrides, target_id, team, scene_ids, camera_original_values, shot_plan, time_map, fx_ids_strength_revision, frame_id_hash_status, peak_id_hash_status, motion, hud, encoder, gpu_fx, audio_source_policy, fps, resolution, qa_policy。draft→validate→変更差分→適用→immutable job。手動指定をrecipeで上書きせず、再適用時もoverrideを維持。T01〜T14の該当試験とユーザー承認が必要。

## Montage

対象：複数fightの連結。映像根拠：V04/V16/V20/V23/V24（動画報告の時刻参照）。

カメラ候補：cinema_top/third/follow。提案距離1.10×baseline、FOV55°、yaw差8°、pitchは承認済み基準のまま。単位変換未検証なら原値維持。

前：−4秒から相手/進路を残す。瞬間：wideを保持。後：group内は連続、group境界でのみtransition。CG挿入は外部素材必要。multiはgroup内でcamera/transitionを反復しない。

速度：1.0x基準、別承認の速度curveのみ。映像と音声は同じpiecewise mapで再配置。

global FX：初期hard cut、任意transition .2秒、flash off。frame：旧37または既存静止承認083を手動選択のまま。未承認651を自動採用しない。peak：初期off、任意選択時はreview表示と弱.45から比較。登場：slide_right（既存式を保持）。

負荷：中〜高、最大3take/group。機器別の性能保証なし。fallbackは元scene/承認済みcamera、FXを減らす前にユーザーのfallback policyを確認。解像度/fpsの無断低下は禁止。

既存の土台：scene scan/selection, legacy10 camera/manual keys, HUD, frame/badge/motion selections, grade/basic FFmpeg, output encode/audio。新規：recipe adapter/schema, group-aware climax budget, shot planner/best shot (except low-load), time map contract, warning QA context。

保存/接続：schema_version, recipe_id, revision, explicit_overrides, target_id, team, scene_ids, camera_original_values, shot_plan, time_map, fx_ids_strength_revision, frame_id_hash_status, peak_id_hash_status, motion, hud, encoder, gpu_fx, audio_source_policy, fps, resolution, qa_policy。draft→validate→変更差分→適用→immutable job。手動指定をrecipeで上書きせず、再適用時もoverrideを維持。T01〜T14の該当試験とユーザー承認が必要。

## Low-load Cinema

対象：長尺/負荷制限。映像根拠：V12/V25のwideを応用した設計推論（動画報告の時刻参照）。

カメラ候補：top/follow。提案距離1.10×baseline、FOV58°、yaw差0°、pitchは承認済み基準のまま。単位変換未検証なら原値維持。

前：−4秒から相手/進路を残す。瞬間：wideを保持。後：1takeのみ、cutaway off、動的顔追跡off。multiはgroup内でcamera/transitionを反復しない。

速度：1.0x、retime off。映像と音声は同じpiecewise mapで再配置。

global FX：grade .08まで、temporal blur/DOF/全画面flash off。frame：旧37または既存静止承認083を手動選択のまま。未承認651を自動採用しない。peak：初期off、任意選択時はreview表示と弱.45から比較。登場：instant（既存式を保持）。

負荷：提案上低。製品のfps/メモリ効果は未実測。機器別の性能保証なし。fallbackは元scene/承認済みcamera、FXを減らす前にユーザーのfallback policyを確認。解像度/fpsの無断低下は禁止。

既存の土台：scene scan/selection, legacy10 camera/manual keys, HUD, frame/badge/motion selections, grade/basic FFmpeg, output encode/audio。新規：recipe adapter/schema, group-aware climax budget, shot planner/best shot (except low-load), time map contract, warning QA context。

保存/接続：schema_version, recipe_id, revision, explicit_overrides, target_id, team, scene_ids, camera_original_values, shot_plan, time_map, fx_ids_strength_revision, frame_id_hash_status, peak_id_hash_status, motion, hud, encoder, gpu_fx, audio_source_policy, fps, resolution, qa_policy。draft→validate→変更差分→適用→immutable job。手動指定をrecipeで上書きせず、再適用時もoverrideを維持。T01〜T14の該当試験とユーザー承認が必要。
