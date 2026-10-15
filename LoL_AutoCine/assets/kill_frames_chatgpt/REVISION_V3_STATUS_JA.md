# 追加制作・再制作 v3 の現状

生成・再構成版を主方式として採用。No.013〜015の旧生成版は利用者の指摘により不採用として履歴を保持し、新規ファイルに再制作した。

**全件未完了。新しい生成候補は 33 点、対象は322点、最終合格は0点。**
新しい生成画像がないパーツを完成扱いしていない。方式の採用は、個々の画像の最終承認を意味しない。

|原本No.|対象パーツ|新しい生成候補|原本見切れ保留|最終合格|
|---|---:|---:|---:|---:|
|001|50|15|0|0|
|002|20|0|0|0|
|003|20|0|0|0|
|004|40|0|8|0|
|013|18|6|0|0|
|014|15|6|0|0|
|015|9|6|0|0|
|086|50|0|0|0|
|087|50|0|0|0|
|088|50|0|0|0|

## 品質上の未解決事項

27 点で画像外周にアルファの残留を検出した。RGBA形式・透明画素の存在だけでは完全透過合格にしない。新しいNo.013〜015では四角／円形の誤りと主要モチーフを修正したが、装飾の細部・線幅・位置の厳密一致は引き続きレビュー対象。

No.004の8パーツは原本自体が見切れており、見えない部分の忠実な再現は原本不足で保留。No.013のUI配置例は別デザインとして数えていない。

## 保存先

- `review_v3/production.json`: 全322パーツの状態、原本SHA、切り出し座標、生成プロンプト、生成PNGのSHA、透過検査。
- `review_v3/<No.>/*.generated.png`: 生成元のPNGをバイト変更せず保存したレビュー候補。
- `review_v3/<No.>/*.source_crop.png`: 原本比較用の切り出し。完成素材ではない。
- `downloads/revision_v3/AutoCine_原本比較一覧_v3.zip`: 展開してHTMLを開くだけの原本対新版の一覧。未生成・要修正も表示。
- `downloads/revision_v3/生成再構成_v3_part*.zip`: 新しい生成候補だけの画像ZIP。

既存の89原本、37バッジ、本体コード、過去のレビュー素材は変更していない。

## ダウンロード

- [原本と新版をまとめて見る一覧ZIP](https://github.com/Aimin2222/agdhnteweeffewwff/raw/refs/heads/chatgpt/killframes-source-numbering-20261014/LoL_AutoCine/assets/kill_frames_chatgpt/downloads/revision_v3/AutoCine_%E5%8E%9F%E6%9C%AC%E6%AF%94%E8%BC%83%E4%B8%80%E8%A6%A7_v3.zip)
- [今回の生成候補33点だけの画像ZIP](https://github.com/Aimin2222/agdhnteweeffewwff/raw/refs/heads/chatgpt/killframes-source-numbering-20261014/LoL_AutoCine/assets/kill_frames_chatgpt/downloads/revision_v3/%E7%94%9F%E6%88%90%E5%86%8D%E6%A7%8B%E6%88%90_v3_part01.zip)

一覧ZIPは展開後 `ここから見る.html` を開く。ブラウザでの実操作は未確認。HTML内スクリプトの構文とZIPの破損検査は合格。
透過修正の再生成は `review_v3/repair_attempts` に保存。外周アルファは0になったが、中心の青い輪郭が不自然なため主候補に採用していない。
