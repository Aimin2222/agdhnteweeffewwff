# FX・色・素材の統合仕様

基準：`bd93e2caf3bdb823d52b86fead0d71fc15c41327`。制作済み画像、エンジン処理、品質研究の限定PASS、正式承認を独立に管理します。原本・catalog承認・既存37バッジ/89原本/652候補/35FXを変更しません。

## 最新コードによる更新

Flash `causal_pts_v1`とZoom `normalized_tmix_v1`は既にcore/effects.pyに存在。PR #54/#55の通常BATはこれらを環境変数で選び、legacy引数で旧経路へ戻します。直接Python起動や環境未指定のfilter既定はlegacyのため、起動経路ごとの実revisionを記録します。古い研究の「候補未実装」をそのまま再開発指示に使いません。候補の正式採用や実LoL完走は別です。

これらrevisionは現在Templateの宣言fieldではなくgetattr/envで選択されるため、保存後に出力が変わり得ます。新規schemaでprocessing_revisionを型付き保存、起動envよりproject明示指定を優先するadapterを提案。旧projectは互換legacy/既存起動方針を明示し、silent migrationを禁止。D10の採用判断と分離します。

## Flash

現候補はeventごとgte(t,start)、exp減衰、max合成。先頭eventだけを中心にした旧経路と同時eventを加算して白飛びする経路を混同しません。9桁文字列は浮動丸めが残るため、厳密な「絶対に前へ出ない」はinteger ticks/time_baseで最終frameのactualPTSと比較します。CFRはceil(event_out×fps)、VFRは最初のactualPTS>=event_out。event IDとvictimを保持し同時別victimを捨てない。

強度kの既存amp=.18+.65k、exp減衰18は既存値。因果gate修正、強度/色保持、残光上限は別revision。headroom候補の3強度が同じ上限へ潰れた研究はREVIEWのままです。キル前の他FXは意図を別定義し、全FXを勝手に因果0へ変更しません。

試験：30/60/60000÷1001fps、単発/短間隔/連続/同時、通常/.5倍/2倍、イベント境界直前/直後、pause/seek/cut。FlashだけOFFの同一frameとの差分で、全event前の効果量0、後で非0を測る。RGB平均/飽和率/最大値を記録。CPU候補PASSをGPU成功へ流用しません。

## Zoom / Blur

現行zoom_blurはscale/cropと3frame tmix、weights1:2:1。legacy scale4とcandidate .25は異なる経路。正規化後のDC gainをFFmpegの実版本でパッチ実測し、白飛び/飽和/RGB保持を確認。履歴はclip/cut/seek/continuity ID変更時に破棄。GPUが同じ候補を実装していなければ正しいCPUへfallbackし理由を記録します。

`radial_blur`の現在名は時間tmixで空間放射blurではありません。真の空間radialは別effect ID：同じframeを中心(cx,cy)周りに複数scaleして非負weight合計1で合成、透明端/edge sampling/alpha/色空間を明示。中心は0..1映像content座標、対象追跡のconfidence不足なら中央固定またはOFFをユーザーへ表示。追跡器は研究画像の既知点と別実装です。scale数/最大zoomは品質負荷測定後の選択肢で、未実証値を正式既定化しません。

## 既存22 CoreFXと35 WorkFX

70台帳中FX_の22IDはTemplate.video_effects、0..1強度。WorkFX35枚はRGBA素材/peak時間カーブ、weak=.45/strong=1。1つのドロップダウンに名前だけで統合しません。素材カタログIDとfilter IDをnamespace分離。独立WorkFX選択API、なし、同名pair、review opt-inを追加し、原本承認は変えない。

camera_shake等は画像crop/scaleであり実3Dカメラ移動とは別。scene別任意CoreFXと時間envelopeは現行5FXのShot外なのでschema/adapter/CPU/GPU評価を拡張。時刻はキル相対Replay→TimeMapで出力へ。0は明確にOFF。時間envelopeの開始/hold/終了、補間、durationを持つ場合は新しい型として保存し、既存値はconstant envelopeへ互換変換。

## 画面切替

Template.transitionのcut/fade/flash、montage_fxのcut/flash/dark/white/soft/gold/cool/pulse/cinema/shadowは別処理。現montageは連結後eq明暗変化等でframe数を増減せず音声copy、softも真の2映像cross-dissolveではありません。真のdissolve/別take/reverseは新規filter+音声TimeMapが必要。clip端transitionとmontage境界を二重適用しない。実durationから境界を計算、失敗fallbackは通常cutと明示。

## 色処理

既存Template：16grade/strength0..1.4、temperature−1..1、contrast.6..1.6、exposure−.3..+.3、vibrance−1..1.5、lut_path .cube、curve_points。`color_filters`の順序はeq→colorbalance→vibrance→lut3d→curve。露出はgrade brightness+.5*exposureでEVではなく、temperatureはKelvinではありません。均一彩度はgradeの係数にあり独立Template scalarは未実装。D07で新fieldを追加する場合、1中立の乗算・合成順・CPU/GPU LUT bakeを同じrevisionにします。

新UIはまず既存globalへのvalidated APIを追加。scene別はShotに任意override mapとinherit/null semanticsをversion付き追加し、global→scene→評価の順を固定。clear overrideはglobalを参照、resetは値0と同じではありません。LUTはpath/hash/存在/構文を確認し、欠損時に動画が成功した体裁で黙って無効化しない。scene別LUT/露出はglobal処理のUI接続だけでは完成しません。

比較は既存preview.compose_compare(近似)とrender_exact_still(時間FXを除く静止)を利用可能。R1/R2比較ボタンは今はdisabledで、preview_playへの誤接続だけ解消済み。同じrawframe/PTSをbefore/afterへ分岐しsplit0..1、タイムライン停止中に比較。近似と厳密は明示し、時間FXは同じhistory/連続区間が必要。全カメラbefore/afterは別take収録の新契約で、静止比較成功へ混ぜません。

## DOF/Fog

Replay環境、後処理focus blur、circle/band DOFとゲームレンズの距離値を別管理。DOFの画像中心/半径は正規化座標でDPIに依存させない。GPU/CPUの形状/feather/alphaを比較。depth bufferが無ければ真の奥行き被写界深度とは表示しません。

## フレーム/6登場/重なり

instant / slide_left / slide_right / slide_up / slide_down / popを維持。slideは.260秒のsmoothstep、popは横方向16exp(−18t)cos(28t)で、scale-popへ変更しません。frame/肖像/ornament/FXを同一transformで移動。原本のcanvas、alpha bbox、portrait hole、参照1920、output、viewport、DPIを別型にします。

共通OverlayPlanにeventID/row/activation[start,end)/elapsed/motion/anchor/scale/mask/opacity/FX layer/clip/geometry revisionを保持。previewとexportが別のrow/size計算をしない。同じ準備RGBA合成器の一致は独立plannerの正しさの証明ではないので、両段を別テスト。raw RGBAのbbox辺差<=2px、RGB差<=2階調を初期検査契約、missing bboxは理由必須。圧縮H264の許容差は別測定。1920/1366/1280×6motion×1/2/3段で全frame比較、letterbox/DPIは最後のview変換。

素材研究は機械検査687、AI画像審査累計164/687、P2残523。651暫定肖像形状、No004見切れ8+palette11の19原本制約を残す。geometry候補652は作者確定maskではありません。original/derived、formal status、research review、userExcludedを別属性にし、明暗/実映像/動作の未検査を残します。除外5件はrecommendationから外しても原本削除/承認変更をしません。

## GPUと音声

NVENCはencoding、OpenCLはFX、WGCはcaptureで別能力。processing revision対応を実測してからGPU有効と表示。CPU fallbackは適用FX/実encoder/理由をlogへ。LoLプロセス音声のみ、取得不能時のデスクトップ全音声への黙ったfallbackは禁止。可変速とconcatは同一TimeMap/実PTS/sample countで同期を測り、音源なしはNOT_RUN。Windows全体音量やネットワーク設定を変更して試験を通しません。

根拠：[effects.py](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/effects.py)、[preview.py](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/preview.py)、[work_kill_assets.py](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/work_kill_assets.py)、[kill_icons.py](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/kill_icons.py)、[montage_fx.py](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/montage_fx.py)。過去限定実証のcommit/pathはSOURCE_PROVENANCEに保存。
