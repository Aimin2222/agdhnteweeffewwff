# B2 ワンクリック・既存モンタージュとの接続
PR49 smart_montage/highlight_director/montage_fx原文を読み、既存choose_scenesをpure fixtureで実行した。新たな自動映像理解を実装済みとはしない。5eventのscore順はa1,k1,k4,k2,k3。独立候補は同actorで間隔<=3秒のkillを3/1/1へgroup化し前4/後3秒を仮付与。

4限定assertion PASS: 同じevent_id重複除去、同時刻の別victim保持、手動順序優先、同戦闘group。既存scoreが意図する見せ場順と時間groupを別目的として比較する。自動候補のFX同時数1/peak alpha.35は研究開始値で最適値ではない。

Codexへ: 既存標準とスマートの入口を保持。event identity→user override→group候補→既存score→trim→camera recipe→FX budget→job snapshot。推奨結果はユーザー確認で覆せる。wait/slowはevent local時刻でなくsource→timelineの区分写像を明示し、キル数を失わない。実engage検出/被写体スキン認識/ベスト映像理解/6レシピの新しい実映像成功はNOT_RUN。20参考動画の観測資料は継承のみで今回の再生0本。

PLAN_FIXTURESと合成plan_compare動画はイベントデータの可視化でゲーム出力ではない。1クリック完了の受入は実LoL接続→scan→選択→ゲーム音のみ録画→CPU/GPU出力→音声/画角QA→成功/失敗通知まで別E2Eで行う。再実行b_fixtures.py。
