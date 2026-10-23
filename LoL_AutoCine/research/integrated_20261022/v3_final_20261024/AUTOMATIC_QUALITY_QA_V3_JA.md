# 警告中心の完成動画QA仕様

最初は警告と証拠一覧のみ。自動修復/削除/再録画/処理停止へ直結しない。既存SELFQAの拡張案と、映像解析の新機能候補を混同しない。閾値は全てfixture用の提案で、LoL一般の誤検出率は未測定。

|対象|自動検出できる根拠|不足/人間の確認|
|---|---|---|
|黒画面|decode済み輝度、capture状態、継続frame数|intentional黒/ロード/暗いmapを区間文脈で除外|
|frame落ち/停止|PTS、期待frame数、記録drop counter、画像差|静止shotとfreezeを画像差だけで区別不可|
|音声なし|track存在、sample数、RMS、audio_expected|意図的無音と録音失敗はpolicyが必要|
|音ズレ|人工同期marker/eventと時刻map|戦闘音だけの意味的同期は人間/対応音源必要|
|overlay見切れ|描画canvas/alpha bbox/safe area|slide登場中の画面外は仕様、静止後の切断とは別|
|FX過剰点滅|viewport別輝度変化・頻度・envelope記録|teleport/ゲーム内発光とpostFXの由来。安全認証は行わない|
|主役画面外/target喪失|lock応答/追跡confidence/ROI|全champion3D/遮蔽は現行APIで保証されない|
|上下反転/急回転|render姿勢、roll/角速度と区間注釈|地形/エフェクトで画像推定が不確か。意図rollを除外|
|地形埋まり/遮蔽|低confidence検出と比較take|depth/geometryなしでは確定できない|
|不自然な継ぎ目|PTS/音声不連続/shot境界/flash envelope|意図hard cut/CG挿入の評価は人が行う|

## 人工検証結果

`WARNING_QA_SYNTHETIC_V3.json`に14fixture。黒capture、意図black、死亡gray、lowHPred、teleport明画面、動くはずのfreeze、意図still、音声missing/optional/silence、frame count不足、event offset、slide意図clip、静止overlay clipを実行。14/14で設計した期待warning集合と一致。これは設計どおり動く最小試験であり、独立データでのprecision/recall評価ではない。閾値30frame<5輝度/60frame差<.1/offset50ms等を製品推奨値と断定しない。

## 実データでの評価手順

最低各20正常/異常の匿名clipを用意し、death/lowHP/teleport/recall/transition/freeze/無音を重複tagする。2名が独立annotation→不一致を協議。rule別TP/FP/FN/TNとconfidence閾値、検査時間を集計。death等を異常正解に混ぜない。小規模データで「誤検出0だから高精度」としない。高い重要度でも根拠不明は要確認、ユーザーが原frameへjumpできる導線を残す。製品停止条件はdecode不能等の確実な処理不成立と、人の演出評価を分離して別承認する。

warningはoutput時刻/frame、元replay区間、対象匿名ID、rule/version、metric、threshold、context、confidence、画像hashと再現手順を持つ。画像/音声の公開は既定off。QA自身がprojectや素材承認を変更しない。
