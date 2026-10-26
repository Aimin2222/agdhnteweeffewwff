# B1 自動構図・切替の研究候補
採用済みthird/third_cinemaを変更せず、前回36条件の既存数値/BLUE・RED/90・180度可視化を継承。今回120frameの既知2D対象位置がn30/n75で切替わるfixtureを4方式で比較した。実LoL座標軸校正・TargetLock追従・地形遮蔽の実機成功ではない。

raw最大step626.498、速度制限14units/frame、速度＋加速度制限14units/frame/1800units/s²。速度だけは加速度最大12600で段差が残る。加速度制限は滑らかだが平均追従遅れ189.435units。hold-then-cutは切断として626.498の跳びを残す。小さなstepだけで採用せず、対象が構図から外れる遅れと意図したcutを同時評価する。

既存固定自動/フルオートは別モードのまま。提案条件: 既存三人称の斜め後ろanchorを初期値、manual override最優先、実サイドと座標変換のrevisionを明示、接続中の対象IDを維持。視点切替にはspeed/accel制約、追従遅れ上限、遮蔽confidence、hysteresis、cut許可区間を別管理。90/180回転は最短角のwrap規則とサイド別期待方向を実機で照合し、REDを画面の左右だけで反転しない。

複数キルは生存対象/直近victim/着弾先のscreen-space hullへ余白を取り、FOV上限と距離上限に達したらcut候補へ。長射程は発射/飛翔/着弾phaseで対象集合を切替える。地形meshやvisibilityが無いfixtureでは遮蔽成功と呼ばず、最後の安定姿勢へfallback。固定＋小補正と自由回り込みを同じスイッチに混ぜない。

METHOD_COMPARISON.json/png/mp4が新規証拠。研究座標にゲームunit換算の保証なし。LoL実機、遮蔽物、長射程、複数人実録画、回転酔い・視認性、API低速化はNOT_RUN。再実行b_fixtures.py。
