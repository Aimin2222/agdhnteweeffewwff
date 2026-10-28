# 不明機能14件の調査結果

ソース照合は14件すべて実施。操作の実証は全件NOT_RUNです。U09/U10などの役割は一意に決まらず、選択肢を残しました。推奨は正式採用決定ではありません。

## U01 FOV48°と選択キー64°

分類：部分対応・値モデルが異なる。既存Shotは相対fov±15°、baseはstyleと時刻で変動。camera.fov_atは制限も行う。現在UIは絶対FOV未接続を表示している。

実装：D02：選択キーの要求値/補正量/評価後現在値を別表示。実baseで逆変換可能範囲だけadapter。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/camera.py#L360)

## U02 なめらか補間とBezier

分類：既存評価あり／選択モード・自由接線は新規。2点はsmoothstep、3点以上は調和平均傾きの形状保存Hermite、端点傾き0。キー外は端点値。linear/hold/Bezierの選択APIはない。

実装：まず同じ評価器を曲線描画へ。D03後にmode/tangentをversion付き保存、CPU/実カメラで同じ評価。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/camera.py#L297)

## U03 XYZ/Yaw/Zoomの複数トラック

分類：既存3channel／XYZ新規。Yaw/Zoom/FOVはShot.keyframesで束ねて保存。XYZや自由姿勢trackはこのschemaにない。THIRD_STYLES以外はkeyframe delta0。

実装：既存3channelを表示・数値・drag同期。XYZはD04、geometryと軸/遮蔽検査なしでは無効。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/scene_project.py#L16)

## U04 露出/彩度/色温度/LUT

分類：既存エンジン＋UI/API/schema拡張。Template.exposure/vibrance/lut_path/temperature/grade/curveは実在。露出はeq brightnessへの係数、Kelvin/EVではない。既存scene APIはtemperature/bloom/focus_blur/dof_blur/highlight_pulseのみ。

実装：global接続とscene拡張を別work item。均一彩度とvibranceを区別。D07/D11。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/effects.py#L511)

## U05 Zoom Blur/放射状/時間混合

分類：既存候補コードあり／空間radialは新規。zoom_blurはscale/crop+tmix。normalized_tmix_v1は既に実装。radial_blur名の既存処理もtmixで空間radialではない。Flash causal_pts_v1も実装済み。

実装：再実装せずrevision/save/GPU互換/境界を検査。真のradialは別ID。D10。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/effects.py#L438)

## U06 ゲームFog/DOFと後処理

分類：類似非同一。Replay render環境とTemplate/FFmpeg/OpenCLの画像ぼかしは別経路。focus_blurとdof_blurも別入力。

実装：カメラ環境/映像FXの別section。影響scope/単位/実接続能力を表示、テーマへ連動しない。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/render_fx.py#L15)

## U07 Replay秒/クリップ秒/キー秒

分類：型変換が必要。現行キーはkill相対秒、scene_keyには2桁時刻を含む。UI表示丸めをFX因果判定へ流用できない。

実装：整数tick/time_baseとTimeMap、半開区間/continuity IDを導入。既存IDはmigration alias。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/scene_project.py#L45)

## U08 project/Template/ROFL保存

分類：既存型が異なる。project_export/importはon_scene_export/importからSceneProject v3のshots/sequenceを扱う。Template.to_dictやROFL準備とは別。全セッション丸ごと保存ではない。

実装：型表示と必要ならProjectBundle新schema。現行v1/2/3読み込みを保持。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/scene_project.py#L243)

## U09 画像選択

分類：原制作意図は推定・用途は未確定。A_main制作指示は素材視覚chooserと6アニメ入口。独立importの形式/保存効果は定義されていない。BのcaptionをAのAPI根拠にしない。

実装：D01推奨は既存図鑑。決定まで位置保持/disabled理由。自由画像取込へ勝手に接続しない。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/audit29_client.js#L1155)

## U10 プリセット読み込み/保存

分類：保存scope未確定。既存全体Template/参考映像TemplateとSceneProject/キーpresetは保存対象が違う。現在左下ボタンで同じものと見なせない。

実装：D05の型付き保存。camera-onlyをside/style単位で独立、FXプリセットと共有dictにしない。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/effects.py#L226)

## U11 ROFL/実スキャン入口

分類：既存actionあり・専用画面整理。R1/R2 prepareControlsはopen_replay/prepare/scan/target_lockを呼ぶ。ROFLを選んだだけではLoL接続やscan成功ではない。

実装：各UI設定→リプレイ準備の専用子画面と状態表示。未接続時に入口が消えない。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/reference_views_v2.js#L85)

## U12 保存/録画/テスト結果

分類：既存処理別系統。project_exportはJSON、export_checked/selectedは実job、diagnostics/automatic_qaは別処理。UI3の結果は自動QA概要が中心。

実装：job_id/実encoder/audio source/出力/失敗理由を表示。MP4成功はdecode/PTS/音声QA後、JSON保存で動画成功にしない。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/audit29_runtime.py#L553)

## U13 固定＋自動構図/フルオート

分類：既存部分実装・承認gateあり。smart_camera_directorはclip境界でstyle決定し、side別approved/excludedを使う。enemy geometryは推定しない。full modeのmulti wide補正はあるが遮蔽最適化の証明ではない。

実装：既存thirdを保護。mode/side/style別preset。geometryが無ければ安全baselineと理由。自動切替はclip境界。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/smart_camera_director.py#L27)

## U14 BAT版の劣化

分類：差分監査へ置換済み／live受入は未実施。初期台帳の画面不足は20画面と差分監査により解消。26親IDの差分結果は完了。原画基準は維持し、製品操作はNOT_RUN。

実装：同じ監査を再実施しない。26残件と284更新案を今回の実装完了条件へ継承。

根拠：[固定ソース](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/reference_views.css#L11)

## C3-10

現在の「すべて」「キル＋アシスト」は同じbothで、対象のkill OR assist。UIの4部品は保持し、選択説明にaliasを明示。全プレイヤーへのscope変更やENGAGEへの拡張は別判断D08です。

## 判断待ちの選択肢

### D01 画像選択の入力対象

A：素材図鑑を開き現在のframe/FX/animationタブに適用

B：自由PNG取込／参考映像特徴抽出への入口

推奨は既存素材図鑑。原制作指示に独立import仕様がなく、正式決定まではdisabled。

### D02 原画の絶対FOV

A：既存相対モデルを保持し、計算後の絶対値表示＋到達可能範囲内の逆変換adapter

B：独立absoluteFOV trackを新schemaで追加

推奨はadapter。rawBase評価を提供し、requested−baseが±15を超える/最終clamp/多キル制限なら理由を表示して拒否。64°を+64へ送らない。

### D03 追加補間モード

A：既存2点smoothstep/3点以上Hermiteを既定として明示。linear/holdをversion付き任意追加

B：自由Bezierを同時追加／既存だけに限定

推奨は既存表示→linear/hold拡張→自由接線の順。原画の選択肢は能力が出るまで理由付き無効。

### D04 自由XYZ/カメラ軌道

A：既存yaw/zoom/FOVのみを初期接続

B：検証済み世界座標供給＋XYZ姿勢trackを新設

推奨は前者。Replay world軸・target追従と独立座標の意味・地形検査なしにXYZ成功を作らない。

### D05 候補3プリセットの保存範囲

A：型選択つきcamera-only / effect-only / 全体Templateを明示

B：左下をSceneProject専用にする

推奨は型付き。既存画像の文言だけで型を断定しない。camera-onlyは色/FX/音声/対象IDを変えない。

### D06 調整前後比較の範囲

A：近似色比較と厳密静止画比較を段階別に明示

B：時系列FX/カメラ変更を含む同期2take比較

推奨は静止/色の接続から。時間系はbuffer/historyを揃えた別能力。カメラを動かし直した2画像は同一rawframe比較ではない。

### D07 色の単位と範囲

A：既存露出係数−.3..+.3と自然な彩度を正しい名前で接続、均一彩度は別field

B：EV露出を新しいlinear-light処理として追加

推奨は既存互換。均一彩度0..2(1中立)は追加案で、gradeの彩度へ乗算する場合はCPU/GPU/保存のrevisionが必要。

### D08 すべての意味

A：現行both aliasとして注記し機能保持

B：全プレイヤーのkill/assistやENGAGE等を含む全イベントへ拡張

推奨は現行alias維持。別意味は対象scopeとevent typesを別設定として承認後に導入。

### D09 ENGAGE/BESTSHOTの今回の開発範囲

A：データ契約・取得可否を実証してから任意追加

B：今回必須として収集/推定/評価まで新規実装

推奨は段階ゲート。正解付き入力と実フレームが無ければschema/検証器まででNOT_RUN。kill数採点を代用しない。

### D10 研究FX revisionの正式既定化

A：BATの現行candidate/legacy切替を保持し永続revisionの設計だけ追加

B：合格後に新revisionを新規projectの既定へ

推奨は現行維持。過去projectの出力を黙って変えない。正式採用判断はユーザー。

### D11 シーン別色設定の範囲

A：既存5項目を維持し、露出/LUT/彩度のoverride schemaを追加

B：グローバル色だけ接続して個別は従来エディタへ

推奨は個別拡張。ただしglobal inheritance/clear/reset/undo/importを同時実装。
