# 単体・統合・総合テスト計画

計239ケースを定義、製品での実行は全件NOT_RUN。今回は仕様整合性の検査だけを実行します。以前のCodexのテスト結果や研究限定PASSは、今回の実機成功へ繰り上げません。各ケースの具体的入力/操作/期待値/前提/証拠はTEST_CASES.jsonを参照。

## 段階

1. Unit：70機能の状態変換・validation・旧schema・補間・型をfixtureで確認。
2. Integration：3UIの入口→同じApp→保存→再表示、実jobとログの結び付きを確認。
3. Windows：1366/1920、DPI100/125/150%、light/dark/system、popup/キーボード/scroll/route/draft。
4. Media：Flash/Zoom/Overlay全frame比較、CPUとGPU、A/V actualPTS/sample count。
5. Real LoL：side/style/mode/TargetLock/反転/録画/音声/MP4を同一Replayで実証。未取得dataを架空sceneで補わない。
6. Optional new：判断/data取得が済んだ能力だけ、ENGAGE/BESTSHOT/Bezier/XYZ等を実証。

## 重点ケース

|ID|入力|操作|合格条件|
|---|---|---|---|
|THEME-ALL|全3UI・全control・light/dark/system|paletteの文字/背景、selected/hover/focus/disabled/native select/popupを実測、Windows設定は変更しない|通常文字>=4.5、主要UI境界>=3を目安。previewRGB不変。computed styleと画像を保存|
|STATE-SWITCH|2sceneに異なるkeys/FX、focus A/check B、未確定draft|3UI/12画面/theme往復→保存→再起動/再読込|focus/check/draft/Templateの適切なscopeが保持、camera無命令|
|COMPACT-NO-OVERLAP|1366×768/1920×1080 content viewport、DPI100/125/150%|preview/transport/shotstrip/timeline bboxとscroll、input focusを測定|重なり面積0、transport全表示。native outer windowとcontent viewportを別記|
|YAW-32|state.third_yaw=32、他数値非0|poll→camera→R1/R2/C3→theme→scene復帰|32表示/送信一致。欠損はunknownで0偽装しない|
|KEY-INTERPOLATION|0/1/2/3/40keysと非均一間隔、極値|実評価器の端点/中間/キー外をcurve samplingと比較|legacy2点smoothstep/3点Hermite一致。style非適用時delta0|
|FOV-SEMANTICS|複数style/時刻/baseとrequested64°/delta±15|raw base/effective clamp/fullauto multi下限を比較|絶対/相対を区別、到達不能を拒否、変更なし|
|COMPARE-SAME-FRAME|1rawframe+PTS+Template+processing revision|before/after splitと近似/厳密を別生成。playhead監視|比較で時刻が進まず、左右同じinput、時間FX未対応を表示|
|SCENE-CHECK|2実scene、focus A/checked B|Bチェック→A選択→対象dialog→scan再読込→export_checked|export Bのみ。選択変更でcheck不変。0件は明示|
|FLASH-CAUSAL|30/60/60000÷1001fps×単/連/同時×.5/1/2rate|revision別全frameRGB/PTSを比較、seek/pause/cutを含む|event前Flash差0、event後非0、全ID保持。輝度/飽和は別REVIEW|
|ZOOM-NORMALIZE|明暗/RGBパッチ・動き×弱/中/強|legacy/candidate時間tmix/spatial別にDC gain/残像を測定|時間候補のgain正常、cut/seek後履歴なし。空間blurと混同しない|
|OVERLAY-FRAMES|3解像度×6motion×1/2/3段×FXoff/on|全frameのactiveID/alpha/bbox/RGB差、独立plannerと共通rasterを分け比較|raw bbox<=2px/RGB<=2階調の契約、missingbboxは理由。圧縮は別測定|
|CAMERA-SIDES|BLUE/RED×10style×manual/fixed/full×0/90/180°|キャリブレーション/seek/target変更/切替を録画・姿勢log|TargetLock維持/反転なし、保護RED経路不変。可視性は実画像で判定|
|COLOR-ROUNDTRIP|global/scene exposure/temp/vibrance/LUTとoverride解除|3UI入力→保存再読込→CPU/GPU/厳密比較|値・scope・処理順一致。EV/Kelvin/均一彩度の誤表示なし|
|ASSET-IMMUTABLE|37/89/652/35の既存manifest|選択/適用/取消/図鑑/書出し前後hashとformal status照合|原本/承認不変。P2残523/暫定651/制約19を保持|
|AV-GPU-E2E|許可済み実LoL replay/音声、CPU/NVENC/OpenCL機|実録画→可変速→concat→decode/actualPTS/sample count測定|LoL音声だけ、必須失敗伝播。実encoderとFX経路別表示。A/V drift基準は用途別明記|
|PROJECT-TYPES|SceneProject v1/2/3、Template、camera-preset、bundle、不正JSON|import/save/取消/失敗/日本語pathを実行|型違い拒否・atomic保存・旧読込保持・MP4と別結果|
|POPUP-FOCUS|設定/図鑑/出力確認/エラーpopup|Tab/ShiftTab/Esc/Enter/閉じる/背景wheelを操作|focus trap/復帰、背景誤操作なし、取消は未適用|
|ONECLICK-REAL|実Replay・既存target・手動overrideあり|選択→scan→check→おまかせ→preview→MP4→検証|全段実結果、手動値保護、失敗段で再試行可能。出力QA後に成功|
|OLD-REGRESSION|旧UI29/候補1〜10/元C3/従来カメラ|変更file範囲と旧入口/テンプレート保存/起動を回帰|既存導線・原本不変。配布停止研究demoは復元/再配布しない|

## 判定と証拠

PASSは期待assertionを実行し証拠がある場合のみ。FAILは条件不一致、REVIEWは品質や採用の判断待ち、NOT_RUNは実行なし/前提不足。元画像との数値差・機能の動作・美的な好み・実LoL未接続を別列に記録します。black previewや0scene自体はデザイン不合格にしません。

284受入台帳の既存IDと9FAIL/29REVIEW/246NOT_RUNを基準案として保持。新testとの対応はrelated IDで結び、同じ操作を重複合格として数えません。最終合格は差分修正後の実装build SHA、入力hash、環境、raw結果・画面・ログを付して更新します。

A/V driftや品質scoreの全用途共通閾値は確定していません。測定精度・許容フレーム/サンプル誤差・想定尺を明記して合意し、durationだけで合格にしない。テスト不能のためにWindows/セキュリティ設定を変更しません。
