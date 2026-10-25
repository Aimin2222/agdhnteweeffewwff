# 自動カメラと6recipe
CAMERA_SOURCE_MATH48/48：旧10style×BLUE/REDの7時点、heading20条件、slowguard8条件でfinite/FOV/speed/dt・copy isolationを確認。値が有限でも画角が正しい保証ではありません。既存top/third等を削除しません。auto headingのORDER−12/CHAOS192、手動0/180は原文の暫定値であり、BLUE/RED実映像未合格。

独立ルール133/133：旧manual/fixed/full選択、approved不足fallback、除外/全除外例外、unknownmode、重複ID/assist除外、group間隔境界、manual/次戦闘不明/target死亡/visibility不足/side未承認でcutaway抑制、6recipe保存復元/手動保持。gap.5/1.5/3/5秒×4event列の感度例16。gap3秒・次戦闘余白1.5秒・可視性.9・最大3takeは提案値で製品既定ではありません。

設計：手動設定を最優先、戦闘group中wide、最後のkill後.4〜1.4秒の寄りは空白が検証できた場合だけ。unknownは高得点とせずnull、未承認side/対象逸失/地形外/強遮蔽/時刻map不正は候補不採用。全部不採用ならverified baseline。旧camera/TargetLock snapshotをtakeごとに保存・復元。fallbackで除外styleを復活させない。

ShotPlanはRESEARCH_CONTRACTS_V4.json。source patch/replay/event/target/team、legacy値、manual override、2段TimeMap、score/confidence/rejection、asset hash、revisionを保存。takeは最大3、同一入力/seed/costを記録。信頼度を画像品質の実証済み確率と表示しない。

SIX_RECIPES_V4.jsonに6案の既存/新規/保存/例外/差分を全件保持。Cinematic=wide＋最後だけ余韻、Impact=最後だけ任意pulse、Elegant=弱演出、Competitive=情報維持、Montage=groupと遷移、Low-load=単一take。V06/V21の連戦を根拠に、途中の寄り連発を抑える。適用はdraft→validate→差分表示→明示適用→immutable job snapshot。theme/view切替でcamera/project/previewを再生成しない。

レシピ比較は同一Replay・対象・scene・設定seedでbaseline+6出力、イベント前4/後2秒、速度map/kill/HUD/camera/FX/CPU/GPU/audioを保存し、T01/03/08/09/10/11/12を実機で審査。明確な入力不足は勝手に補わずfallback理由を表示。
