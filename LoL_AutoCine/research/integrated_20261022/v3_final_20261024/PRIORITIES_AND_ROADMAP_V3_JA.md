# 分類・優先順位・境界

A=既存不具合候補、B=UI互換、C=既存強化、D=新機能、E=低優先、F=Windowsで判定。A01は独立再現済みだが製品修正未実施、A02はhelper例外と通常到達性を区別する。採用済み項目は0。

|ID/分類|提案|難度|変更候補|試験|依存|GPU負荷|効果|
|---|---|---|---|---|---|---|---|
|A01/A|multi CPU flashの中心式|中|core/effects.py|T03/T09/T08|原文と独立再現、最新job追試|低|後続killにも正しいpulse|
|A02/A|空event helperとcall path防御|低|core/effects.py / core/jobs.py|T02/T09|通常fallback経路の到達性確認|低|異常入力の例外伝播明確化。通常crashとは未確定|
|B01/B|旧10cameraとTargetLockのUI接続|中|ui/controller / core/smart_camera_director.py（必要時のみ）|T01/T13|UI選定と旧設定fixture|不変|設定欠落・陣営取り違えを防ぐ|
|B02/B|旧FX ID/保存revision互換|中|core/templates.py / core/effects.py / ui|T08/T09/T13|旧project/golden output|低|旧templateを壊さず名称/処理を明示|
|B03/B|素材状態/顔形状/旧37の保持|中|ui/work_gallery.py / core/work_kill_assets.py（採用後）|T06/T07/T13|素材審査・portrait metadata|低|未承認の誤採用と顔形状不一致を防ぐ|
|B04/B|70機能adapterとtheme状態保持|高|ui29 runtime / controller / project model|T01–T14の既存該当範囲|ユーザーUI選定|低|view変更とproject/録画状態を分離|
|C01/C|event/capture/output時刻map統一|高|core/jobs.py / effects / compose|T02/T03/T08/T09/T11|録画時刻正解fixture|低|retime/複数event/音画同期の再現性|
|C02/C|preview modeと最終graph差の説明|中|core/preview.py / ui|T08|時間FX fixture|中|誤った静止合格を防ぐ|
|C03/C|frame/peak/HUD safe-area審査|中|kill_icons / work_kill_assets / ui|T06/T07|原寸審査と実顔/HUD|低〜中|装飾/顔の可読性|
|C04/C|GPU FX/encode別のfallback診断|中|jobs / gpu pipeline / diagnostics|T10/T11/T14|実device/LoL同時動作|経路依存|負荷と失敗の説明改善|
|D01/D|checkpoint/失敗clipだけretry|高|jobs / project persistence / ui|T14|settings/input/output hash設計|低|長尺失敗から安全に復旧|
|D02/D|group-aware shot list|高|新shot planner / camera adapter / jobs|T01/T03/T04/T12|旧機能Windows合格/ユーザー採用|中〜高|連戦の理解と決着後cutaway|
|D03/D|複数takeのbest shot採点|高|新candidate capture/scoring|T04/T10/T12|D02/可視性データ/正解annotation|高|撮影候補を根拠付き比較|
|D04/D|警告中心output QA|高|新qa analyzer / output manifest / ui|T05/T06/T10/T11/T14|負例annotation/metric由来|中|不良候補を時刻付きで提示|
|D05/D|6recipeのdraft適用/override保存|中|新recipe schema / project / ui adapter|T12/T13|ユーザー採用/C01/D02は任意|レシピ依存|初心者の操作と手動優先を両立|
|E01/E|本物のradial/glow/空間wipe|高|新FX IDs / CPU+GPU implementations|T08/T09/T10|互換revision/B02|高|名称どおりの新演出。既存修正とは別|
|E02/E|音楽beat同期/外部CG intro|高|新audio analysis / media editor|T11/T12|音源/映像素材と権利/長尺UX|中〜高|任意montage表現。音声未観察なので優先低|
|F01/F|BLUE/RED実動/LoL専用音声/長尺1080p60|中〜高|まず既存コードの試験、根拠後に限定修正|T01/T04/T10/T11/T14|ユーザーWindows Replay fixture|実測待ち|机上では判定不能の品質/安定性|
|F02/F|WebView2/PythonなしPC配布|中|packaging/runtime検出/配布manifest|T14|clean Windows/依存bundle|GPU能力に依存|配布先の起動と実出力を確認|

## 推奨順（ユーザーの開発順を優先）

1. UI29比較版→ユーザー選定。研究側は比較候補を削除/統合しない。
2. B01〜04と既存70機能の接続。A01/A02の製品追試を行い、既存不具合として限定修正する場合も同fixture回帰を添付。
3. F01/F02、T01〜14の既存範囲をWindowsで実施。GPU encodeとFX、音声、長尺、Pythonなし配布を個別に合格にする。
4. 研究レビュー後、採用されたC01時刻map、C02preview説明、C03素材審査、C04診断を小さく適用。
5. D01再開処理→D04警告QA→D05recipe→D02shot list→D03best shotの順を候補とする。D05はshot plannerなしの既存機能recipeだけ先に限定導入できる。
6. E01/E02は既存品質と互換が安定してから。旧演出IDの置換で実現済みと扱わない。

本体へcommitしていない。記載fileは実装時の影響候補であり確定patchではない。難度/負荷は設計見積り、fps/クレジット削減の実測効果ではない。
