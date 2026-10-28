# Codex向け Windows/WebView2実装仕様
## 1. 採用範囲
R1/R2は追加の表示層。現行混合7＋4、比較3/5/8、簡単編集未決定を保持。候補番号をR1/R2へ割り当て直さない。本体/カメラ/GPU/録音/素材承認は別工程。

## 2. 再現するUI
source of truthはdemo/app.cssとapp.js、SCREENSHOT_METRICS。1920×1080の18画面（各8画面＋dark main各1）と1366×768 main各1、計20枚。固定header66、nav54、status28、timeline270px（高さ820以下ではheader58/nav44/status26px）。高さ900以下は210、820以下は170へ縮小。R1 columns252/残り/344、gap12/padding12。幅1500以下210/残り/288。R2 rail82/残り/340、幅1500以下72/残り/288、gap16、shotstrip37（compactは縮小）。詳細値はLAYOUT_TOKENS。

previewはviewport内で16:9 contain。横幅=min(領域幅,領域高×16/9)。スクロールはscene列、inspector、shotstrip横、modal内、compact track名だけ。中央preview/transport/header/timeline/statusを親scrollへ入れない。1366×768の実測previewは約649×365（R1）と同等以上のR2。1180px未満は横scrollで明示し、モバイル対応としない。

button通常36px、small30px、compact24px、角丸7、panel角丸9。base15px、1500幅以下14px、title21/heading18、補助11〜13。細かい補助表示を主要操作ラベルへ転用しない。テーマはCSS tokenだけを交換し映像に適用しない。選択はcheck＋border＋ariaで示す。opaque主要色の実算比はCOLOR_TOKENS。全状態・高コントラストテーマ・screen reader適合の認証ではない。

## 3. 共通モデル
projectId/revision、stable sceneId、focusedSceneId、outputCheckedIds、sceneOverride、cameraMode/style/side、TargetLock playerId、sourcePTS/timelinePTS、selectedKeyId、outputPolicy、jobId/state、formalAssetStatusを単一storeに置く。view/variant/themeは外観state。切替でstore/backend/mirror sessionを再生成しない。再生中のlayout切替もtimeを保持する。output jobは開始時snapshotから処理し、編集中の設定を混入させない。

デモschema1は独立の研究形式で、製品保存形式と同一ではない。移植時はadapterで変換し、旧scene保存形式・Undo・個別overrideの意味を保持する。FOVのベース値とキー適用を明示。preview timeとrecord source timeを混同しない。実製品では前工程の整数tick/有理数・[start,end)契約を優先し、デモの12秒/float実装をそのまま録画時刻の基準にしない。

## 4. バックエンド境界（提案、今回未接続）
UI request例：{schema:1,id,type,args,projectRevision}。reply：{id,ok,result,error,revision}。event：{subscriptionId,event,data}。型・範囲・能力・対象sceneId・revisionをnative側でも検証する。

replay.prepare/status → on_quick_prepare/on_open_replay/on_play_recent
scene.scan/cancel → on_scan、scan progressを実処理から通知
scene.focus/check → on_scene_selection等、checked_killsとは別
camera.mode/style/side → 既存var/adapter、採用済みthird/third_cinemaを保持
mirror.start/stop → 既存WGC session。未接続時に合成図を実mirror成功と表示しない
preview.play/stop → 既存演出確認、recordと停止tokenを区別
scene.key/trim/grade → 既存scene/keyframeモデル。自由XYZ曲線がなければFOVデモから捏造しない
asset.select → catalogの実ID/承認状態を参照。研究図形IDを製品IDへ流用しない
job.start/cancel/retry/status → on_make_*等、実encoder/実音声/ファイルQAをeventで返す
diagnostic.run/report → on_automatic_qa/on_dev_camera_qa/on_show_diagnostics

全70のsource/handler/不足はFEATURE_COMPARISON_70.json。ENGAGE/BESTSHOT等の不足を接続済みに変えない。GPU/NVENCは方針と実使用encoderを区別。音声はLoL process treeだけが既定、他アプリ/desktop loopbackへ黙ってfallbackしない。

## 5. 今回のホスト
WinForms .NET Framework x64＋WebView2 SDK1.0.3856.49。既存Runtimeを検出し、local virtual hostへdemo/をmap。外部navigation/new window/permissionは拒否。HTML connect-src none。ブラウザーやWindowsのネットワーク/セキュリティ設定を変更しない。参照：[Microsoft local content](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/working-with-local-content)、[Runtime配布](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/distribution)。全WindowsにRuntimeがあるとは仮定しない。

実装済みbridgeはdemo-ready/state-snapshot/test-report/integration-report/save-json/capture-*のみ。LoLやshellの汎用実行handlerは無い。message source/sizeを検証し、capture名は固定regex、保存はOS dialog。診断dataは専用_sessionへ。SDK DLL3点のlicense/noticeを保持し、第三者UI画像/ブランド素材を同梱しない。

## 6. 受入条件
画面ID=LD/LN＋view＋theme＋sizeと原画像を対応させる。pane境界・余白・文字・固定/scrollを画像overlayで比較。全view切替でプロジェクト/カメラ/選択/チェック/time不変。drag中はpreviewが残り、pointer cancelで元へ戻る。dialogはEsc/close/焦点復帰と背景scrollを試験。保存JSONを再起動・別layoutへ読み込んで一致。native keyboard/IME、125/150/200%DPI、長い日本語path、クリーンPC、実mirror/scan/録画/音声/NVENCと異常復旧は別E2Eで行う。

色のCSS近似を製品gradeと同一視しない。真のBezier接線/位置XYZ/独立回転curve、LUT/mixer/wheels、実catalog一覧、実export progressは未実装。見た目のために既存設定を削除せず、能力がない箇所は説明と導線を残す。
