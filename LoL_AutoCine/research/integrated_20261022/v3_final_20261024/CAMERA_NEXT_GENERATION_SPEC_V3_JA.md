# 次世代自動カメラ仕様（未実装の提案）

## 現行との境界

現行`full_auto`はclip境界で、陣営別に明示承認された旧style候補から一つ選ぶ。空の承認表は未検証を意味し、除外を尊重したfallbackを返す。戦闘中にshotを連続設計する機能ではない。`fixed_auto`/manual/旧10styleはそのまま保持する。自動プランナーは新しい任意モード候補として追加し、旧保存値を置換しない。

## 入力・出力と処理順

入力：replay hash/patch、target_id、BLUE/RED、ChampionKill/assist/engageの根拠、take範囲、手動camera/lock/scene境界、陣営別QA承認表、取得データとconfidence、素材状態、出力fps。出力：`ShotPlan`（schema_version、immutable settings hash、segments、candidate score、fallback reason、time map）、各segmentの収録ファイルとQA。未知情報を0や敵座標に置き換えない。

1. API/event重複排除、対象/陣営を確定。seek不連続で時刻segmentを分割。
2. 近いkillをgroup化。提案gap3.0秒、次engage/主役生存/画面状況も併用。gapは動画から測定した値ではない。対象不明はgroup演出を中止し元scene維持。
3. first kill−4秒〜last kill+2秒のwide基準takeを必ず先に確保。元設定を変更せずtarget lockを継続。
4. 最後のkill後0.4〜1.4秒の任意cutaway候補。次engageまで1.5秒未満、target死亡/喪失、陣営未承認、地形/視界不明、手動固定なら候補を作らない。将来イベントを使えるoffline replayで先読みし、live情報がない時は推測で次戦闘なしとしない。
5. 候補は最大3take、wide/follow/人物shot。余分な収録はコスト上限を設ける。まず全候補を取得して比較する方式を段階実装し、撮影中の視点切替は別段階。
6. hard gateを通った候補のみ採点。wide基準があれば不明/失敗時に戻す。全候補無効なら警告して手動確認、品質を捏造しない。

## 候補評価と安全条件

提案score=0.35*主役可視率+0.25*戦闘参加者の構図内率+0.20*動き安定性+0.10*画面余白+0.10*時間連続性。各0〜1、観測可能な項目だけを使い、欠測はconfidenceを下げる。metric3個未満または主役可視率不明なら自動bestの確定はしない。score差<.05は安定したwideを優先（提案閾値）。一般精度の実測はまだない。

hard gate：BLUE/RED一致、target_id一致、該当陣営のcamera QA承認、元イベント範囲とtake内時刻一致。上下反転、画面外継続、極端な角速度/地形埋まりを疑う映像は採用を保留。intentional roll/transitionには区間注釈を付ける。画像だけの疑義を衝突検出の確定値として扱わない。

TargetLockはjob開始時の対象snapshotに結び、別targetへのsilent fallback禁止。座標系はteam mirror変換を1箇所へ限定し、yaw/pitchを二重反転しない。BLUE/RED各2fixtureでT01、旧10style×2陣営で回帰。manual key/選択scene固定はplannerより優先。

## データの可用性

現行raw codeは127.0.0.1:2999のplayback/render、playerlist/eventdata等を利用。必要endpointがreplayで実際に応答するかはpatchごとに実測する。[Riot公式Replay API資料](https://developer.riotgames.com/docs/lol#replay-api)はcamera/render制御の根拠になるが、全actorの信頼できる3D位置、深度buffer、壁のocclusion、装備meshの任意target取得を保証していない。

取得できない場合：画面内2D追跡/手動ROI/録画メタデータは補助候補。ただしFX遮蔽、dash、死亡時に誤追跡し得る。3Dがないのに完全な衝突回避や本物のdolly/DOFを約束しない。顔/小物shotは任意で低confidenceならwideへ。API応答fieldと由来、欠測率、capture timestampを保存する。

## ShotPlan例と検査

schema例は`RESEARCH_CONTRACTS_V3.json`。同一groupでwide→任意cutaway→次scene、各segmentへreplay/take/output範囲、camera原値、target/team、confidence、採否理由、素材hash、音声track範囲を保存。cutawayは同一時間帯の別takeを選び、尺を増やす場合はtime mapを新たに作る。別takeでも音声を重複mixしない。T01/T03/T04/T08/T10/T11/T14の実機合格後、ユーザーが採用を決める。
