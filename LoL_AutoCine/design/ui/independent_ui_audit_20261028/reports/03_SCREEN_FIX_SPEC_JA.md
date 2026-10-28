# 画面別の修正仕様

全座標は正本のネイティブpxのx,y,width,height。C3=1672×941、R1/R2=1920×1080。未提供サブ画面の矩形は正本上の復帰先であり、実画面を撮影・測定した値ではありません。手測りのアンカーは同寸法の重畳で調整してください。

## C3-01 / P0 / C3 T-A-M

対象領域：`[866, 777, 421, 158]`。根拠種別：CAPTURE_CONFIRMED。

4行の数値欄はあるが、原画の4スライダーとリセットがない。値950/170と原画900/420の違い自体は不具合としない。

修正：距離/高さ/回転角/回り込みの各スライダー＋数値を同じ行に復帰し、リセットを右上へ戻す。既存値・範囲・Undoと双方向同期。従来UI原本は編集せずUI3限定で追加する。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/ui3_baseline.css:80](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/ui3_baseline.css#L80)。

比較資料：crops/C3_numeric.png。

## C3-02 / P0 / C3 T-A-M

対象領域：`[1287, 735, 385, 203]`。根拠種別：CAPTURE_CONFIRMED。

演出素材欄が枠カード5枚だけになり、フレーム/エフェクト/アニメの3切替、なし枠、登場6種入口、一覧の状態要約がない。

修正：右下の3タブ、なしを含む5表示枠、図鑑と6アニメ入口を原画位置で復帰。実素材の絵柄差と承認状態は実カタログのまま。素材を原画の合成絵へ差し替える指示ではない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/audit29_client.js:935](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/audit29_client.js#L935)。

比較資料：crops/C3_materials.png。

## C3-03 / P1 / C3 T-A-M

対象領域：`[850, 0, 822, 49]`。根拠種別：CAPTURE_CONFIRMED。

上部操作が短い文言・狭い幅で極端に右へ寄った。リプレイ白面の左端は原画870、実画面1272で+402px。GPU/音声/HUDという設定の内容も見えない。

修正：上部操作を原画の幅と順序へ。リプレイ約[869,6,140,35]、準備[1017,6,80,35]、設定[1105,6,190,35]、ログ[1303,6,82,35]、作成[1394,6,150,35]を目標にする。版番号等の可変文言は固定しない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

比較資料：crops/C3_header.png。

## C3-04 / P1 / C3 T-A-M

対象領域：`[355, 611, 895, 46]`。根拠種別：CAPTURE_CONFIRMED。

4操作は存在するが中央寄せ・幅・文言・アイコンが原画と異なる。実画面の開始は約x549、原画はx465。

修正：ミラー開始[465,618,147,38]、ミラー停止[623,618,130,38]、演出再生[780,618,248,38]、プレビュー停止[1036,618,150,38]へ近づける。ミラー停止・プレビュー停止・録画停止を共用しない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

比較資料：comparisons/C3/overlay50.png。

## C3-05 / P1 / C3 T-A-M

対象領域：`[0, 773, 865, 162]`。根拠種別：CAPTURE_CONFIRMED。

カメラカードの選択印がなく、見出し/画像が小さく、説明が1行へ減っている。下段が約20px下へずれ、固定領域に不要な縦スクロールがある。

修正：原画の見出しy約780、カード上端y約798を目標に再配置。3カードにラジオ/選択枠、画像と2行説明を復帰。手計測のため原画重畳で最終調整し、古いy793の集約矩形だけを正解にしない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/ui3_baseline.css:64](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/ui3_baseline.css#L64)。

比較資料：crops/C3_camera.png。

## C3-06 / P1 / C3 T-A-M

対象領域：`[626, 778, 240, 147]`。根拠種別：CAPTURE_CONFIRMED。

原画のBLUE/RED 2ボタンに自動を加えた3ボタンで、注目対象のドロップダウンも表示されず未選択文だけになっている。

修正：原画位置にBLUE/REDと対象セレクタを維持。自動という既存機能は削除せず詳細設定へ移す。未接続時は対象セレクタを理由付き無効にして形を維持。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

比較資料：crops/C3_camera.png。

## C3-07 / P1 / C3 T-A-M

対象領域：`[1276, 270, 376, 299]`。根拠種別：CAPTURE_AND_BOUNDS。

12個の行要素は用意されるが行高27pxで12行目の大半がスクロール外。原画は12行を同時表示している。

修正：同じ枠に12行が収まる行高（原画目標22〜24px程度）/paddingへ調整し、10人・12シーンの明示した配置検査fixtureで確認。実未スキャン0件を12件の検出成功に捏造しない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

比較資料：crops/C3_scene-list.png, data/C3_EDGE_RECHECK.json。

## C3-08 / P1 / C3 T-A-M

対象領域：`[19, 553, 315, 96]`。根拠種別：CAPTURE_CONFIRMED。

左下プリセット選択が狭く、保存3操作が小さく離れており、原画の幅のある選択欄と均等な3ボタンの構成を失っている。

修正：プリセットをほぼ列幅で表示し、読み込み/保存/別名保存を約100pxずつの3等分で整列。保存対象がプロジェクトかプリセットかは既存U10の調査を踏まえる。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

比較資料：comparisons/C3/overlay50.png。

## C3-09 / P2 / C3 T-A-M

対象領域：`[1470, 706, 177, 33]`。根拠種別：CAPTURE_CONFIRMED。

原画の画像選択入口がなく、比較UIへの追加ボタンが下段タブの右を占有している。3UI切替の追加自体は必要な統合差分。

修正：比較UIの切替は共通メニュー等へ整理し、画像選択の場所を保持する。意味未確定U09なので別処理へ勝手に結線せず、未対応理由を明示する。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

比較資料：comparisons/C3/actual.png。

## C3-10 / P1 / C3 T-A-M

対象領域：`[1275, 212, 379, 35]`。根拠種別：CAPTURE_CONFIRMED。

原画はチェック付き4フィルター、実画面は細い4テキストボタン。選択状態・操作領域の視認性が弱い。

修正：原画相当のチェックとラベル間隔を復帰。既存フィルターAPIの複合条件を確認し、見た目だけのチェックや同じ処理の重複接続を作らない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

比較資料：crops/C3_scene-list.png。

## R-01 / P0 / R1,R2 detail,curve

対象領域：`[1580, 207, 310, 510]`。根拠種別：SOURCE_CONFIRMED_NO_VIEW_CAPTURE。

詳細/カーブは既存エディタを開くボタン＋カメラ数値に置換。選択キーの時刻/FOV/補間/追加削除/適用、直接カーブがこの画面内にない。

修正：右インスペクタへ原画のキー編集を復帰し、下部に秒ルーラー/選択点/再生ヘッドとキー・カーブの別描画を実装。既存キーアダプターを使用。自由XYZ/Bezierを勝手に実装済みにしない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:33](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L33)。

比較資料：data/R1_R2_COVERAGE_20.json。

## R-02 / P0 / R1,R2 main,color,all preview headers

対象領域：`[1440, 140, 100, 32]`。根拠種別：CAPTURE_AND_SOURCE。

原画の「調整前と比較」に相当する#compare-viewは、現コードでpreview_playを呼ぶ演出再生ボタンになっている。

修正：比較ボタンの役割と位置を復帰し、調整前後の表示stateへ接続する。演出再生はtransportから。比較能力未接続なら理由付き無効とし、別処理へ偽装しない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.py:42](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.py#L42)。

比較資料：comparisons/R1/actual.png, comparisons/R2/actual.png。

## R2-01 / P0 / R2 reference-ln / main

対象領域：`[98, 175, 1454, 539]`。根拠種別：CAPTURE_AND_SOURCE。

ショット列を.center内に入れ、270pxの全幅timelineを別に足している。映像面の高さ539→485（-54px）、timeline左端12（原画98）、timeline上端約779（原画819）。

修正：#shot-stripを中心映像から分離し、下段をx98からのshotstrip y782/h37＋timeline y819/h233、全体270pxの構造へ。中央映像面y175/h539を復帰する。画面の一括拡大縮小で直さない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.py:45](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.py#L45)。

比較資料：data/STAGE_SPANS.json, crops/R2_lower-stack.png。

## R2-02 / P0 / R2 main / shot strip

対象領域：`[730, 786, 95, 30]`。根拠種別：SOURCE_CONFIRMED_NO_POPUP_CAPTURE。

原画の対象チェック入口がない。ショット列はselect_sceneボタンだけで、チェックボックスはR2で非表示の.scene-pane内にしかない。

修正：ショット列末尾へ対象チェックを復帰し、焦点とは独立のチェック集合を選択するダイアログへ接続。他UIでチェックしてから戻ることを前提にしない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:37](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L37)。

比較資料：comparisons/R2/actual.png。

## R-03 / P1 / R1,R2 easy

対象領域：`[1580, 207, 310, 540]`。根拠種別：SOURCE_CONFIRMED_NO_VIEW_CAPTURE。

簡単編集の原画はカメラ/雰囲気/キル演出の3群カード。現body(easy)は縦モードボタンと素材画面へのリンクだけ。

修正：3群の横カードと細かく調整する入口を復帰。カード選択は既存プリセットのドラフトへ、適用範囲/Undoを明示し、録画を自動開始しない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:28](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L28)。

比較資料：data/R1_R2_COVERAGE_20.json。

## R-04 / P1 / R1,R2 camera

対象領域：`[1580, 207, 310, 540]`。根拠種別：SOURCE_CONFIRMED_NO_VIEW_CAPTURE。

モードが縦3ボタン、数値はnumberのみでFOVスライダー/数値がない。原画のモード横3カード、FOV/Yaw等のスライダー＋数値と異なる。

修正：モードを横3カードへ戻し、FOVを含む数値を対応スライダーと併設。サイド/スタイル/TargetLockと実能力の説明は維持。既存パラメータ範囲をUI都合で変えない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:19](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L19)。

比較資料：data/R1_R2_COVERAGE_20.json。

## R-05 / P1 / R1,R2 color

対象領域：`[1580, 207, 310, 540]`。根拠種別：SOURCE_CONFIRMED_NO_VIEW_CAPTURE。

色調整が既存色/FX設定へ飛ぶ3ボタン＋frameControlsになり、ルック3枚・露出/彩度/暖かさ・分割比較がない。素材の設定が色タブへ混入。

修正：色インスペクタを原画の役割へ復帰し、素材選択は素材タブに置く。実グレード能力/単位へアダプター接続し、CSS近似を実LUT/GPU処理の成功としない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:32](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L32)。

比較資料：data/R1_R2_COVERAGE_20.json。

## R-06 / P1 / R1,R2 material

対象領域：`[1580, 207, 310, 540]`。根拠種別：SOURCE_CONFIRMED_NO_VIEW_CAPTURE。

frameControlsは文字/状態のみのボタンで素材画像がなく、登場6種も2列。原画の大きな画像カード、FXの見た目/強度、登場3列×2行と違う。

修正：実カタログのサムネイル・選択枠・状態を画像カードへ。6アニメは3列×2行で視覚選択。原画の自作見本を正式素材IDへ転用しない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:21](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L21)。

比較資料：data/R1_R2_COVERAGE_20.json。

## R-07 / P1 / R1,R2 export

対象領域：`[1580, 207, 310, 540]`。根拠種別：SOURCE_CONFIRMED_NO_VIEW_CAPTURE。

出力内に原画の解像度選択/HUD欄がなく、項目順と作成前の確認パネルも変わっている。

修正：解像度→fps→エンコーダ→LoL音/HUD→作成前確認の情報階層を復帰。出力先や実ジョブ情報の追加は同じインスペクタ内で整理し、JSON保存とMP4を混同しない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:23](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L23)。

比較資料：data/R1_R2_COVERAGE_20.json。

## R-08 / P1 / R1,R2 main

対象領域：`[1564, 132, 344, 638]`。根拠種別：CAPTURE_AND_SOURCE。

概要カードのFOVがカメラ名に、ゲーム音のみが出力FPSに置き換わった。初心者パネル/主ボタンも小さくなり、原画の全幅ボタンと背景のまとまりがない。

修正：概要4枠をサイド/FOV/出力対象/音声へ戻し、状態が無ければ—を表示。原画の幅一杯の主操作とまとまりを再現。カメラスタイル/fpsは専用画面に保持する。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:27](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L27)。

比較資料：crops/R1_inspector.png。

## R2-03 / P1 / R2 main / all tool rail

対象領域：`[0, 120, 82, 650]`。根拠種別：CAPTURE_AND_SOURCE。

左レールは原画の7項目＋アイコンに対し、メインを加えた8項目の文字のみ。レール開始も原画y120に対し約132。

修正：7つのツール/アイコン/順序へ戻し、メインは上部タブから。同じviewId同期を維持し、レール上端をnav下に揃える。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.py:41](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.py#L41)。

比較資料：crops/R2_rail.png。

## R-09 / P1 / R1,R2 main / transport

対象領域：`[290, 714, 1250, 56]`。根拠種別：CAPTURE_AND_SOURCE。

原画の現在/総時刻と再生倍率の表示・操作がtransportにない。ミラー4操作を置いたことは接続要件上の追加だが、元の時間確認が失われている。

修正：現在時刻/総時間・倍率をtransportに復帰。Replay時刻とclip局所時刻を区別し、取得できなければ—と理由。ミラー/プレビューの独立操作は補助群として整理し録画と混同しない。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.py:44](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.py#L44)。

比較資料：comparisons/R1/actual.png, comparisons/R2/actual.png。

## R-10 / P2 / R1,R2 main / header

対象領域：`[0, 0, 1920, 132]`。根拠種別：CAPTURE_AND_SOURCE。

ヘッダーのUndo/Redo/操作ガイド、ツールのアイコンがなく、body14px/見出し19px等で原画より小さい。3UI切替の追加は統合差分として分ける。

修正：原画の15px基調・タイトル21px・見出し18px等と同じ見え方へ。Undo/Redo/ヘルプを既存状態へ結び付け、ラベルを消して収めない。3UI切替は合意した追加差分に記録。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.css:4](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.css#L4)。

比較資料：comparisons/R1/overlay50.png, comparisons/R2/overlay50.png。

## R-11 / P1 / R1,R2 all inputs

対象領域：`[1564, 132, 344, 638]`。根拠種別：SOURCE_RISK_RUNTIME_NOT_RUN。

1100msごとのsnapshot→renderがinspector-body.innerHTMLを置換するため、入力中のフォーカス/未確定文字/選択が失われるリスクがある。実Windows操作は未再試験。

修正：差分更新と編集中のローカルドラフトを使い、フォーカス中のDOMを置換しない。1.1秒をまたぐ数値入力・IME・スクロール位置の実試験を追加。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:38](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L38)。

## R-12 / P1 / R1,R2 export / fps and encoder

対象領域：`[1580, 207, 310, 540]`。根拠種別：SOURCE_RISK_RUNTIME_NOT_RUN。

fps/encoderのselect生成でstateに対応するselectedがなく、render後は先頭の60/autoを表示する疑い。theme/trim以外は後段代入もない。実操作再現は未試験。

修正：o.fps/encoder方針へ明示的にvalueを反映し、144やGPUを選択→poll→タブ往復して表示と実設定が一致するか確認。実NVENC使用成否とは別検査。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/ui/reference_views.js:23](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/ui/reference_views.js#L23)。

## QA-01 / P1 / C3 measurement script

対象領域：`[0, 0, 1672, 941]`。根拠種別：JSON_AND_SOURCE_CONFIRMED。

xywh個別差の最大値で判定しており、位置差と幅差が合算する右辺ずれを見落とす。独立再計算は11領域中6 PASS/5 REVIEW。

修正：比較を[L,T,R,B]=[x,y,x+w,y+h]で実行し、幅/高さ差も別記録。細部の見た目や固定動作の合格へ拡大しない。古い手計測領域の限界も明記。

確認：same-size capture/overlay plus focused control test; do not fake data or bypass capability checks。

接続/描画箇所：[LoL_AutoCine/tools/compare_ui3_baseline.py:52](https://github.com/Aimin2222/agdhnteweeffewwff/blob/4a00871f3009475dbdd1586e5bf05f78117b8907/LoL_AutoCine/tools/compare_ui3_baseline.py#L52)。

比較資料：data/C3_EDGE_RECHECK.json。
