# 20作品の観測から実装条件へ
今回は再視聴やUI評価ではなく、前段の実映像観測を条件・入出力・処理・試験へ変換する工程。VIDEO20_TO_RULES.jsonに20作品を1件も省かず掲載し、URL/作品内秒数/事実/導出ルールを対応付けた。作品秒数はReplayゲーム時刻ではない。
全体構成20/20は粗い断続観測。明示kill通知2件以上の根拠は14/20、保留6作品はV02/V03/V08/V15/V16/V24。音声20/20未実施。参照の見た目だけでカメラFOV、速度、FlashやBlurの処理方式、正確なキル時刻を確定しない。今回の人工/数理検証は参照映像の再現成功ではない。

## 実行の分離
1. 入力固定：Replay hash、patch、target player ID、verified kill/assist、ユーザーpre/post、cameraと素材のrevision/hashesを保存する。
2. イベント整理：stable IDで重複排除、同時刻の別victimは保持。競合ID/NaN/Inf/負時刻は拒否。assist/engageをkill Flashへ流用しない。engage専用イベントがない現在は未対応と記録する。
3. オフラインShotPlan：位置・遮蔽・続く戦闘が分かる場合だけ候補を生成。手動/未指定を優先し、BLUE/REDの安全性が未承認なら既存baselineを保持。候補は採用理由と拒否理由を両方残す。
4. take収録：既存camera/TargetLockにadapterで接続。計画値を直接新しいカメラ計算へ置き換えない。同じイベントを複数takeで撮る場合はReplay時刻で照合し、シーク直後の安定確認を別に記録。
5. 編集：確定TimeMapで速度、kill素材、FX、切替、音声をoutput時刻にそろえる。外部CG/人物切抜き/本当のdissolveは追加engineが必要。既存fadeを同等再現と呼ばない。
6. QA：構図・見切れ・輝度・時刻・AV・デコード・実機負荷を別判定。失敗を自動で修復/承認せず、baseline比較とログを残す。

## 12ルール
### R01 安全な自動構図
入力：verified replay ID/side/TargetLock、同時刻のgeometry
処理：manual/未指定は維持。side/geometry不明時はbaseline。検証済み可視率と遮蔽で候補を拒否。
既存/新規：旧10camera/制御3種/TargetLockをadapterから呼ぶ。geometry供給と候補検査は新規。
検査：CT01/CT02/CT09

### R02 複数キル・集団戦
入力：kill event IDs/actor ID/participants/fight end
処理：同一actorの重複IDを除外、別victimの同時killは保持。イベント列とfight推定を分離しwide候補を優先。
既存/新規：既存kill/scene/trim。fight segmentation・複数対象包含は新規。
検査：CT02/CT03

### R03 長射程の射線
入力：発射/命中ID・時刻/位置/遮蔽・capture時点
処理：発射者だけへの寄りを抑える。発射/弾道/到達先を含むtakeを別収録。両側位置不明ならbaseline。
既存/新規：既存camera収録を土台。projectile対応、2端点構図は新規。
検査：CT03

### R04 戦闘前後を残す
入力：user pre/post・最後のkill・次engageの既知/不明
処理：sceneは半開区間。user範囲を勝手に狭めない。次engage不明を安全な空白と解釈しない。
既存/新規：既存前後trimとscene保存。auto境界延長は新規で未既定。
検査：CT01/CT02

### R05 人物・武器の挿入
入力：fight終了確定/next-engage空白/take検査
処理：3条件を満たす時だけ任意cutaway。戦闘へ戻る位置とplayheadを保存。外部CGは別素材として扱う。
既存/新規：camera別takeは一部既存、planner/外部トラックは新規。
検査：CT04

### R06 FX・カラー
入力：processing revision/asset hashes/実イベント/色空間
処理：ゲーム発光・低HP縁・死亡灰色と編集FXを分離。入力→grade→FX→overlay→transitionの順をversion化。
既存/新規：既存grade/video effects/35overlayFX。背景人物別maskは新規。
検査：CT05/CT06

### R07 Flashのイベント同期
入力：replay→output TimeMap、CFR rateまたはVFR PTS
処理：eventごとの因果ゲートとmax合成。小数3桁丸めの先行漏れを拒否。V5 CFR tickは別revision。
既存/新規：legacy先頭event中心は保持。V4/V5は研究候補で未採用。
検査：CT05

### R08 Blurの輝度保持
入力：weights/scale/input color metadata/clip境界
処理：tmix正規化とズーム軌道を別検査。clip境界で履歴をリセット。正規化だけで空間radial blurとは呼ばない。
既存/新規：旧zoom_blur ID維持。新revision選択・履歴flushは実装前条件。
検査：CT06

### R09 切替・暗転・再提示
入力：scene boundary/transition kind/duration/前後take
処理：hard cut/fadeと本当の2映像dissolveを分離。意図的黒と広告/未読込/不良を区別。二重効果を防ぐ。
既存/新規：既存fade/cut。空間transition/任意split/逆再生は新規。
検査：CT04/CT10

### R10 素材・6登場
入力：catalog namespace/asset hash/status/geometry revision
処理：37/89/652/35を分離。6motion IDと既存pop横揺れを保存。確認用選択は承認ではない。
既存/新規：既存素材renderer。肖像境界確定と新座標契約は別実装。
検査：CT07/CT08

### R11 共通時刻・座標
入力：patch/replay hash、各段のPTS・viewport・DPI
処理：有理数TimeMap、seek gap補間禁止、outputの確定時刻で全レイヤーを同期。roundは最終pixel端で1回。
既存/新規：旧CPU/preview/GPUと比較して選択移行。rendererを本研究で変更しない。
検査：CT07/CT08/CT11

### R12 音声・負荷・合否
入力：許可済み音声/PTS/解析metadata/実機性能
処理：無音・飽和・左右差・AVdriftを分ける。音源なしはNOT_RUN。NVENC成功はGPU FX成功と別。
既存/新規：既存game/BGM/encoderを保持。beat同期と負荷予算は新規。
検査：CT11/CT12

## 複数キルの具体条件
eventの間隔だけをfight終了の根拠にしない。同一actor・既知combat IDを優先、combat IDなしのgap groupingは提案値をprojectへ明示して保持する。固定3秒を正式既定にしない。多人数/長射程なら広い構図候補、単体ならfollow候補を検査する。対象群・退路・弾道を検査できなければ既存wide/fixedへ戻す。
可視率95%/遮蔽5%/画面safe margin8%は暫定検討値。元映像から測定した値ではなく、実機でユーザー/ChatGPTが採用を判断する。固定自動はpose維持を優先、full_autoも可視性が不明なら動かさない。TargetLock解除やBLUE/RED反転を演出に利用しない。

## 6レシピの設定化
Cinematic：戦闘wide＋条件付き人物take、外部CG別扱い。Impact：確定killのみFlash/キル素材、連打時maxと因果性。Elegant：控えめgradeと低頻度挿入、人物mask新規。Competitive：HUD/射程/退路を保持し強いFXを抑える候補。Montage：章/再提示/外部挿入は任意、beat未検証。Low-load Cinema：旧camera＋最小FXを候補とし、低負荷の保証には実機測定が必要。どれも正式既定値にはしていない。
