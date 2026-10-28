# 一括実装の依存順

一度の依頼内で以下の作業群に分けて実装・証拠保存します。別UIへの統一/正式採用はしません。既存修正を先に保持し、新規候補を理由なく必須化しません。判断待ちだけを最後にまとめ、既存接続の完成を止めない方針です。

|順|ID|依存|実装内容|ゲート|
|---|---|---|---|---|
|1|STATE|なし|共通App状態/型/保存契約・stale応答対策|必須|
|2|CAPABILITY|STATE|既存/接続不足/新規/実機未検証の能力表示|必須|
|3|THEME_LAYOUT|STATE|3UI構造・dark token・R2compact重なり|必須|
|4|CAMERA_BINDING|STATE, CAPABILITY|third_yaw/side/style/既存数値を正しく接続|必須|
|5|KEY_ADAPTER|CAMERA_BINDING|既存キー編集/保存/実評価器のcurve描画|必須|
|6|N01|KEY_ADAPTER|絶対FOV adapter。D02後|判断ゲート|
|7|N02|KEY_ADAPTER|値軸/曲線/ドラッグ/キーボード|必須|
|8|N03|N02|linear/hold schemaと評価。D03後|判断ゲート|
|9|N04|N03|自由接線。D03後|追加候補|
|10|N06|STATE, CAPABILITY|既存global色とLUTのUI接続|必須|
|11|N07|N06|scene色override/均一彩度。D07/D11後|判断ゲート|
|12|N08|N06, TIME_MAP|同じframe before/after比較|必須・scope D06|
|13|N09|CAMERA_BINDING|独立カメラpreset。D05後|判断ゲート|
|14|TIME_MAP|STATE|Replay/capture/output/音声の明示時刻写像|必須|
|15|N12|TIME_MAP|Flash/Zoom実revision永続化・境界試験|必須・既定変更D10|
|16|OVERLAY_PLAN|TIME_MAP|共有配置/activation/6motion/alpha契約|必須|
|17|N11|OVERLAY_PLAN|CPU/preview/GPUへ同planを接続|必須|
|18|N14|CAPABILITY, THEME_LAYOUT|素材/FX/6motion図鑑を実catalogへ接続|必須・U09のみD01|
|19|N10|TIME_MAP, N12|真の空間radialを別IDで実装|追加候補|
|20|EXPORT|STATE, TIME_MAP, CAPABILITY|実job/出力/音声/encoder/結果を3UIへ|必須|
|21|N13|EXPORT, N06, KEY_ADAPTER, N14|初心者の一貫した作成フロー|必須|
|22|N16|STATE, N12|ProjectBundle/旧schema移行|判断ゲートD05|
|23|CAMERA_QA|CAMERA_BINDING, KEY_ADAPTER|BLUE/RED×style×mode/反転回帰を実LoL確認|実機ゲート|
|24|N05|CAMERA_QA|XYZ姿勢data供給・track|追加候補|
|25|ENGAGE|CAPABILITY, TIME_MAP|combat data取得実証→区間推定|追加候補D09|
|26|BESTSHOT|EXPORT, CAPABILITY|実frame/target quality取得→候補比較|追加候補D09|
|27|N15|CAMERA_QA, ENGAGE|複数対象/長射程/遮蔽の新camera候補|追加候補・geometry必須|
|28|FINAL_QA|THEME_LAYOUT, N02, N06, N08, N11, N12, N13, CAMERA_QA|70機能×3UIの実操作・実LoL/AV/GPU・29/旧UI回帰|実機ゲート|

表は作業群の表示順で、機械的な実行順はJSONの依存からtopological sortします。TIME_MAPが必要な比較を先に実行しない。新camera/ENGAGE/BESTSHOTはデータ取得/採用判断が必要で、データ不足ならNOT_RUNとして既存機能の納品と区別します。
