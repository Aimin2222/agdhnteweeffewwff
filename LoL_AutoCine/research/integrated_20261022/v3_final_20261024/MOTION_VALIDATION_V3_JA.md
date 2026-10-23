# 6motionの式・実動画検査

基準core/kill_icons.pyのASTからnormalize_motion/badge_motion_xy/badge_planだけを研究環境へ読み込んだ。本体moduleの起動・本体変更なし。FFmpeg7.1、1920×1080、60fps、2.2秒、blue480×160矩形の登場0.4〜1.8秒の6本を実生成。各132frameを実デコードし、6枚のdecoded contact sheetも全て閲覧した。`*_SEQUENCE.jpg`は別途083を用いた式の描画であり、MP4の実素材合成を表すものではない。

|motion|既存式・開始|静止/退場|確認の限界|
|---|---|---|---|
|instant|直ちに定位置|終了時に消える|fadeなし|
|slide_left|左からW+20pxぶん移動|0.260秒smoothstep後停止|途中の画面外は意図した登場|
|slide_right|右からW+20px|同上|実rect動画と式の位置確認|
|slide_up|下からH+20px（上向きに移動）|同上|上端clipは登場区間と静止区間を分ける|
|slide_down|上からH+20px（下向きに移動）|同上|下端のHUD重なりは実素材未検証|
|pop|x方向16*exp(-18e)*cos(28e)|左右振動が減衰|拡大縮小バウンドではない|

smoothstepはu=clamp((t-start)/.260,0,1)、s=3u²−2u³。平常位置は右W−w−32/左32、top62/bottom H−h−62−row_step。motion式自体にはalpha fade/exit curveはない。動画の1.8秒は有効、次の1.8167秒は非表示。30fpsでは.260秒が約8frame、60fpsでは約16frameだが30fps実書き出しは今回未実行。

旧badge_planはkill−.10秒に開始。Work layer_planは+0.10秒ずらして渡すのでWork側はkill時開始になる。両者を同じタイミングと記載しない。ピークのopacity envelopeは別機能で、0/.04/.08/.20/.8秒に0/.8/1/.65/0（既存値）。これは参考動画のflash測定ではない。

連続5event(.5,.6,.7,.8,1.0)を既存badge_planで計算し最大同時3件を確認。4件目以降は最古の終了を早める。実game映像での3段HUD遮蔽、すべてのframeの動的見切れ、GPU layer同期は未実行。pair全体を一枚にした旧badgeは同一x/yで動くが、Workのornament/peak/portraits各layerのCPU/GPU一致は別試験。

1920/1366/1280の3サイズの式の位置はJSONへ保存。実MP4は1920のみ。各sizeで同じ端margin32/62が適切か、scale/card size/stack spacingはT07で実測する。6motionと既存IDを保持し、後から本当のscale-pop/exit-fadeを追加するなら別ID/新revisionで提案する。
