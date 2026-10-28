# 未解決機能の意味と追加開発の分類

指定コミットの原文を読み取りで確認しました。古い資料に「無い」と書かれた処理も、現コードの存在/接続/単位/スコープを分けて再確認しています。実API送信・映像出力はNOT_RUNです。

## C3-10

現在「すべて」と「キル＋アシスト」は同じboth。対象プレイヤーのkill OR assistであり、両条件ANDや全プレイヤー全イベントではない。

分類：ALIAS / LABEL_SPECIFICATION。

付随/開発方針：現在の別名であることを説明。独立した意味が必要ならイベント型/対象範囲の追加仕様。架空のengage処理を割り当てない。

根拠：[LoL_AutoCine/ui/audit29_client.js:679](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/audit29_client.js#L679)、[LoL_AutoCine/core/scanner.py:169](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/scanner.py#L169)、[LoL_AutoCine/legacy_app.py:4022](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/legacy_app.py#L4022)。

## U09

A_mainの原制作指示は下段に枠/FX/アニメの視覚的chooserを置き、最終修正は6アニメを見る入口を指定。「画像選択」という独立した入力/保存操作は定義されていない。同系列Bのcaption指定をAのAPI仕様とは扱わない。

分類：SOURCE_INTENT_INFERRED / OPERATION_UNRESOLVED。

付随/開発方針：最も近いのは演出素材図鑑への視覚選択導線。ただし取込/参考画像抽出へ断定しない。既存work_galleryを使う役割と承認区分・適用対象を合意すれば表示層の接続で済む可能性。自由画像取込なら型/保存/承認等の新仕様が必要。disabledは未実装の正直な表示として維持。

根拠：outputs/test_ui_improvements_20261020/PROMPTS.json（保存JSONのsha参照）、[LoL_AutoCine/ui/audit29_client.js:1157](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/audit29_client.js#L1157)。

## COMPARE

調整前後比較は同一時刻のbefore/after表示。演出再生は時刻を進めて動きを見る処理。最新版は誤接続を除去しただけで実比較はない。

分類：MISBINDING_REMOVED / COMPARE_NEW_CONNECTION_REQUIRED。

付随/開発方針：同じフレーム/時刻・処理ON/OFFの画像を取得し分割/切替する表示経路が必要。実ミラー/preview/outputで同等性を検証。

根拠：[LoL_AutoCine/ui/reference_views.py:51](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/reference_views.py#L51)。

## FOV

SceneProjectはキル相対秒、fovは−15〜+15°の加算補正。実角度は時変base＋補正を制限範囲へclampし、モードによる追加制限もある。絶対64°とは同一でない。

分類：DIFFERENT_COORDINATE_AND_VALUE_MODEL。

付随/開発方針：補正量UIとして明記すれば既存機能に接続可能。絶対指定なら同時刻のbaseを評価/表示して逆算し、clamp/モード/対象styleを扱う新アダプターが必要。48から64は+16で補正限界超過の例になり得る。無断で64を補正欄へ送らない。

根拠：[LoL_AutoCine/ui/scene_project.py:16](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/scene_project.py#L16)、[LoL_AutoCine/core/camera.py:360](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/camera.py#L360)、[LoL_AutoCine/ui/audit29_runtime.py:437](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/audit29_runtime.py#L437)。

## COLOR

既存Templateにexposure/vibrance/lut_pathが存在し、color_filtersが露出由来brightness・grade saturation・lut3dを生成。新UIのscene_fx_numberはtemperature/bloom/focus_blur/dof_blur/highlight_pulseの5種のみ。

分類：EXISTING_ENGINE / ADAPTER_AND_SCOPE_GAPS。

付随/開発方針：既存の全体設定へ接続するなら新処理エンジンは不要な部分がある。シーン別露出/LUTなら保存schema/override追加が必要。exposureはbrightnessへ0.5係数で加算する既存量で、写真のEVではない。vibranceと一律彩度は別。独立saturationはプリセット内部値があるだけで専用保存パラメータの追加を要し得る。

根拠：[LoL_AutoCine/core/effects.py:511](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/effects.py#L511)、[LoL_AutoCine/core/effects.py:141](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/effects.py#L141)、[LoL_AutoCine/ui/audit29_runtime.py:472](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/ui/audit29_runtime.py#L472)、[LoL_AutoCine/legacy_app.py:3630](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/legacy_app.py#L3630)。

## INTERPOLATION

2キーはsmoothstep、3キー以上は内部勾配を調整した形状維持cubic Hermite。範囲外は端点値。キー/対象styleがなければゼロ補正。選べるlinear/hold/自由Bezierモードはない。

分類：EXISTING_DETERMINISTIC_SMOOTH_MODEL / NO_SELECTABLE_MODES。

付随/開発方針：グラフ表示は現行評価式をサンプルして描けばエンジンを変更せず一致可能。linear/hold/自由接線を追加するならモデル/保存/再生側の開発と試験が必要。ファイル冒頭の古い「smoothstepのみ」説明より実分岐を優先。

根拠：[LoL_AutoCine/core/camera.py:297](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/camera.py#L297)、[LoL_AutoCine/core/camera.py:323](https://github.com/Aimin2222/agdhnteweeffewwff/blob/bd93e2caf3bdb823d52b86fead0d71fc15c41327/LoL_AutoCine/core/camera.py#L323)。


「すべて」は現在表示する対象の対応済み種別全体という別名です。対象プレイヤーが固定された通常導線ではkill∪assistになります。scannerのplayer=Noneなら全体概要も扱えますが、4フィルターの「すべて」を押しただけで対象が全員へ変わる実装ではありません。

FOVの例は、同時刻のbaseが仮に48°なら絶対64°には+16°が必要という意味です。実際のbaseはstyle/時刻/モードで変わるため固定48とは置きません。補正±15とclampの制限を無視した逆算はできません。

露出を増やした画面と元画面を比較するために、未接続のbefore/after経路を実装する必要は残ります。既存のcolor_filtersやLUT読込があることは、その新UIで分割比較ができる証拠ではありません。写真のEV、一律彩度、自然な彩度、グレード強度も別の意味です。

補間は2キー時のsmoothstepと3キー以上の形状維持Hermiteを実際の分岐から確認しました。モード選択APIはありません。グラフの描画だけならこの評価式のサンプルで一致可能です。linear/hold/自由接線を追加する場合は保存・評価・移行まで必要で、表示ラベルを足すだけの修正ではありません。
