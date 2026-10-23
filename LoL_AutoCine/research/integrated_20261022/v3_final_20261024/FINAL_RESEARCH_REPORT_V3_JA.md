# LoL AutoCine 総合研究 V3 — 2026年10月24日

研究資料・仕様・独立人工検証をまとめた引継ぎ版。本体への実装は0。依頼範囲すべての実機検査や素材承認が終わった意味の「全面完了」ではない。残件を一件台帳と試験仕様に分離し、できた範囲とできない範囲を明示する。

## V2からの増分

- 20作品すべてを追加実再生。明示キル通知2件以上は9→10作品。全編0、音声/BPM0。V22の114点だけdecode-readyな停止コマ送りを追加し、白plateau約0.3秒を概算。
- 全687の白暗thumbnail目視、35FX全画像の原寸確認、端74件の原寸部分＋原本crop比較、083×FX×強度×背景140合成を実施。652frame全体原寸/実HUD/動的承認は未完。
- 原本89の現物hash、旧37badgeのhash/最新blobとthumb、652候補の原本番号/部品対応を確認。全素材/承認状態は不変。
- 6motionの人工1080p60 MP4生成、132frame×6のdecode、3size式検査。popは左右振動。旧badgeとWorkでは開始時刻が異なる。
- CPU flash複数eventの中心式を人工FFmpegで独立再現。空event helperも例外再現したが通常到達性を断定しない。14FX/motion isolated case、別途14warning fixture。
- NVENC人工1秒1080p60 encode成功。人工AV retimeで約24.2msのpulse開始差を測定。LoL音/GPU FX/長尺/製品テストの代用ではない。
- camera shot planner/旧10保持、6recipe JSON、time map/job checkpoint/UI adapter契約、T01〜14、70機能接続台帳、A〜F分類19提案を詳細化。

## 最新コードと保護

原文基準`fb03e0390805125fc063f4599af6c2541a653abf`。UI観測head`9bb15e15d8057237515cc9bcf7e061a6d15d3369`。full tree比較で371file差分、core/assets差分0。UI側が継続開発中のため統合直前に再照合する。本研究は研究専用branch/prefixだけへ保存、V1/V2とUI29開発を変更しない。

素材正式状態は静止1件083 approved、651frame review、35FX reviewのまま。19件の原本制約（partial8/palette11）と651の仮portrait位置を正式採用と扱わない。ユーザーはUIをまだ選んでいない。

## 状態一覧

|作業|状態|実施|残り|
|---|---|---|---|
|映像20作品再確認|検査済み|20/20追加実再生、2通知10/20、全編/音声0|未確定10作品は通知/kill同期を特定できる素材と追加原映像/音声観察が必要|
|687機械検査|検査済み|687全件、V2immutable台帳継承|原寸の美術評価とは別|
|687白暗thumb|検査済み|687/687|652frame全体原寸・実顔/HUD・動的合成は要確認|
|FX原寸/140合成|検査済み|35/35、083との140/140|他frame/HUD/3stack/実動画は未実施|
|端接触74|要確認|74原寸部分＋74原本crop比較|欠け/光/意図と原本ROIを全体原寸で審査|
|原本/旧badge保護|検査済み|89/89hash、37/37hash+thumb、652ID対応|原本全体の美術検査ではない|
|6motion|一部検査済み|6本人工1080p60、全decode、3size式|全素材/30fps/他size実出力/LoL背景未実行|
|CPUflash|独立再現済み|255/127/127とgraph一致|製品job追試と修正は未実施|
|NVENC/AV|一部検査済み|人工1秒NVENC、人工retime AV|LoL音/GPUFX/長尺/製品同期/配布は未実行|
|warning QA|設計・人工検査済み|14fixture期待一致|独立LoL負例/誤警告率を実測|
|次世代camera/6recipe/UI接続|仕様完成・未実装|contract/70行/14tests/19提案|ユーザー採用後に実装|
|Windows製品T01〜14|要実機検証|完全PASS0|対応Replay/利用者の実機操作・clean PC・長尺試験が必要|

## 研究としての優先改善案

先に既存UI比較→ユーザー選定→70機能接続と既存不具合の追試→Windows全機能/配布検査。採用後は時刻mapと互換revision、素材/顔形状審査、warning QA、checkpoint/clip retryを先に整え、shot list/recipe/best shotを段階追加する。高度FX/beat/CGは低優先。低角度shotや強いFXを増やすことだけを完成品質の目標にしない。

主な資料はREADME/index.htmlから閲覧。公開成果物に第三者動画/再生スクリーンショット、素材原本キャッシュ、私的診断音声を含めない。比較シートはユーザー素材の派生研究資料、MP4は人工矩形・人工音源だけ。RTKによるWork全体のクレジット削減は測定しておらず主張しない。
