# 全89元画像のキルフレーム候補制作・検証レポート

基準: `22861a90c585c8b6b91263241d7437ccf956acc2`。作業ブランチ: `codex/killframes-all-89-candidates-20261014`。

全89枚を読み取り、元ファイル名・寸法・ファイルSHA-256・デコードRGBのSHA-256・各部品の座標を台帳へ記録した。最大8元画像の12バッチで処理し、デコードは1元画像ずつ。**素材は完成候補または要手直し候補であり、最終の見た目は未承認。**

## 成果物と確認の入口

- [31台帳テーマの弱・強・肖像入り一覧](../assets/kill_frames/all_sources/all31_overview.jpg)
- [全89枚の一覧CSV](../assets/kill_frames/all_sources/source_census.csv)
- [全部品の元ファイル・座標・PNG/マスクSHA-256対応CSV](../assets/kill_frames/all_sources/part_correspondence.csv)
- [全画像の切り出し定義JSON](../assets/kill_frames/all_sources/source_inventory.json)
- [既存31テーマの旧ファイル名と実ファイル名の対応](../assets/kill_frames/all_sources/theme_correspondence.json)
- [検証結果JSON](../assets/kill_frames/all_sources/verification_report.json) / [全成果物SHA-256一覧](../assets/kill_frames/all_sources/sha256_files.json)
- [要確認部品だけの一覧](../assets/kill_frames/all_sources/quality_issues.csv) / [全テーマ・設計別の品質一覧](../assets/kill_frames/all_sources/all_design_quality.csv) / [未対応・対象外の理由](../assets/kill_frames/all_sources/unsupported_parts.json)
- [各バッチの全素材・黒白比較](../assets/kill_frames/all_sources/batches/) / [保存場所と再現方法](../assets/kill_frames/all_sources/README_JA.md)

各 `s001`〜`s089` フォルダーで、`source_regions.jpg`（水色の切り出し範囲・赤色の肖像穴）、`review_*.jpg`（全素材をチェック柄/黒/白/実LoL背景/サンプル肖像/小サイズで比較）、`combinations_*.jpg`（その原画像に存在する全フレーム×明示された全ロールモチーフ）を確認する。比較文字は表示用で、素材や動画へ追加していない。Akali×Mordekaiserは既存公式キャッシュのデモであり、試合のキラー/被害者を示すものではない。

## 実数

| 項目 | 数 |
|---|---:|
| 元PNG（変更・改名なし） | 89 |
| 異なる元画像RGB | 88 |
| 部品レコード（参照を含む。独立デザイン数ではない） | 1255 |
| 新規透過PNG | 1225 |
| 新規独立アルファマスク | 1225 |
| 既存15点を含めたPNG実ファイル | 1240 |
| 全素材の背景別・肖像入り・縮小比較ページ | 196 |
| 実在部品の組合せ比較パターン | 2997 |
| 品質注意フラグ付き部品（自動承認しない） | 641 |
| 元画像の端で欠損した部分図 | 8 |
| 保護した既存キルフレーム | 37 |

s058 `image-gen-6(6).png` と s082 `image.png` は、PNGファイルのSHAは異なるがデコードRGBが完全一致した。同じデザインの符号化違いとして分類し、候補ファイルを共有した。既存3テーマ15点と15マスクは再加工せず参照する。部品数には一覧の別案、小型の色/効果参照、同画像の異なるモチーフ、重複元画像からの参照も含むため、テーマ数や独立した完成デザイン数に置き換えない。

## テスト・保護条件

- Windows/Python 3.14.7: pytest **796件合格**（81ファイルを分割実行）、旧式総合 **16/16合格**。
- 各バッチで元画像SHA、全RGB画素、独立マスク一致、指定肖像穴の内部アルファ0、非空の素材、背景比較の存在を検証した。新規の数理テストは、肖像が面積の大半を占める場合でも肖像を背景サンプルとして誤採用しないことを暗/明の両背景で確認する。
- 既存37素材、既存3テーマ候補、core/app/legacy_app等の保護対象153ファイルは基準SHAと一致。元PNG89枚も輸入台帳のSHAと全件一致。
- 初期の既存テスト3件はサンドボックスの既定一時ディレクトリに書けず実行エラーとなったが、作業領域内の新規一時ディレクトリで58件合格した。テスト/本体の安全チェックは削除していない。
- 数値検証は宣言した穴の透明性を確認する。残った髪/衣装の縁、全ての細線の保全、フリンジの見た目を保証するものではない。
- 本番カメラ/TargetLock/録画/GPU/音声/UIのコードは変更していない。LoLを終了したWindowsで合成・モック入力を使った回帰テストを実施し、実LoL録画・動画合成・UI選択・登場FXの新規統合は未実施。
- 一時テストコピーは既存ランナーが削除。検査用スクリプト・ログ・一時画像は無視対象の `diagnostics/local_dev` へ整理し、個人パスを含む生ログ/録画をGitHubへ保存していない。既存のユーザーデータは削除していない。

## 未完成・未対応・品質課題

- **s004の右端8部分図**: ターゴン/ヴォイド、覇王/プールパーティー、ビースト/カフェ、機械仕掛け/深海の恐怖の掲載図は原画像端で欠ける。完全な二者フレームは復元できない。部分候補として残し、描き足していない。
- **s005**: テーマ名が表示されない低解像度のゲーム背景付き参考画像。名称未確認として登録。背景と金属が似た画素色のため境界は要マスク確認。
- **s017**: 水滴・発光・隣のモチーフが接する。全9案の実画像を切り出したが、接触部の正確な分離・役割見出しの色の残りは要手直し候補。
- **s028**: 明るい紙面/紺の下地の混在を元画像のサンプル画素で抑制。星/金属の暗部、白い発光と背景が同色になる所は未承認。
- **s003 KDA、s066 Arcade、s078 Soul Fighter**: 元デザイン中の文字/数値と装飾が重なる。測定した文字領域をアルファで除外した候補だが、背後にない絵を復元できず欠けが生じる。残字・デザインとしての可否は最終目視で判断する。
- **小型一覧/パレット/構造参照**: 低解像度の原画を高精細な素材と誤認しない。拡大時の画質・細い輪郭・肖像の周辺は要確認。部品CSVで該当点を識別できる。
- **全テーマ共通のRGB制約**: 背景と発光が混ざったRGBのアンマット、黒/白フリンジの色修正、肖像で隠れた装飾、原図から欠けた線はアルファだけで一意に復元できない。RGBの補色・描画・再生成はせず、課題として残した。
- 原画像に弱/強や3ロールの指定・パーツがなければ `unspecified` または `unsupported` に記録。A/B/C/D主図の説明アニメーション途中・拡大図、背景人物、操作部品、見出し/文章/罫線は独立した追加デザインとして数えない。全体の別案・実在する色/形状見本は別途保存した。
- **旧ChatGPT画像の不足**: 旧チャットの画像一覧と原本が参照不能なため、89枚以外に不足があるか確認不能。台帳の旧ファイル名不一致は実画像対応へ解決し、「未取得の画像がある」とは推測で断定しない。

## 全89枚の処理一覧

| ID | 元PNG（そのままの名前） | 寸法 | 部品 | 品質注意 | 比較 |
|---|---|---|---:|---:|---|
| s001 | [10テーマの幻想的キルアイコン集.png](../assets/kill_concepts/10%E3%83%86%E3%83%BC%E3%83%9E%E3%81%AE%E5%B9%BB%E6%83%B3%E7%9A%84%E3%82%AD%E3%83%AB%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3%E9%9B%86.png) | 1448x1086 | 50 | 28 | [比較](../assets/kill_frames/all_sources/s001/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s001/manifest.json) |
| s002 | [10種の勝利バナー・デザイン集.png](../assets/kill_concepts/10%E7%A8%AE%E3%81%AE%E5%8B%9D%E5%88%A9%E3%83%90%E3%83%8A%E3%83%BC%E3%83%BB%E3%83%87%E3%82%B6%E3%82%A4%E3%83%B3%E9%9B%86.png) | 1536x1024 | 20 | 0 | [比較](../assets/kill_frames/all_sources/s002/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s002/manifest.json) |
| s003 | [20テーマのキャラクター対決UIギャラリー.png](../assets/kill_concepts/20%E3%83%86%E3%83%BC%E3%83%9E%E3%81%AE%E3%82%AD%E3%83%A3%E3%83%A9%E3%82%AF%E3%82%BF%E3%83%BC%E5%AF%BE%E6%B1%BAUI%E3%82%AE%E3%83%A3%E3%83%A9%E3%83%AA%E3%83%BC.png) | 1536x1024 | 20 | 1 | [比較](../assets/kill_frames/all_sources/s003/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s003/manifest.json) |
| s004 | [40テーマの対決アイコンギャラリー.png](../assets/kill_concepts/40%E3%83%86%E3%83%BC%E3%83%9E%E3%81%AE%E5%AF%BE%E6%B1%BA%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3%E3%82%AE%E3%83%A3%E3%83%A9%E3%83%AA%E3%83%BC.png) | 1536x1024 | 40 | 8 | [比較](../assets/kill_frames/all_sources/s004/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s004/manifest.json) |
| s005 | [image(20261013-062433).png](../assets/kill_concepts/image%2820261013-062433%29.png) | 310x372 | 3 | 3 | [比較](../assets/kill_frames/all_sources/s005/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s005/manifest.json) |
| s006 | [image-gen-1(10).png](../assets/kill_concepts/image-gen-1%2810%29.png) | 1448x1086 | 15 | 6 | [比較](../assets/kill_frames/all_sources/s006/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s006/manifest.json) |
| s007 | [image-gen-1(20261013-075555).png](../assets/kill_concepts/image-gen-1%2820261013-075555%29.png) | 1448x1086 | 15 | 4 | [比較](../assets/kill_frames/all_sources/s007/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s007/manifest.json) |
| s008 | [image-gen-1(3).png](../assets/kill_concepts/image-gen-1%283%29.png) | 1448x1086 | 1 | 1 | [比較](../assets/kill_frames/all_sources/s008/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s008/manifest.json) |
| s009 | [image-gen-1(4).png](../assets/kill_concepts/image-gen-1%284%29.png) | 1448x1086 | 6 | 6 | [比較](../assets/kill_frames/all_sources/s009/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s009/manifest.json) |
| s010 | [image-gen-1(5).png](../assets/kill_concepts/image-gen-1%285%29.png) | 1448x1086 | 9 | 9 | [比較](../assets/kill_frames/all_sources/s010/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s010/manifest.json) |
| s011 | [image-gen-1(6).png](../assets/kill_concepts/image-gen-1%286%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s011/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s011/manifest.json) |
| s012 | [image-gen-1(7).png](../assets/kill_concepts/image-gen-1%287%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s012/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s012/manifest.json) |
| s013 | [image-gen-1(8).png](../assets/kill_concepts/image-gen-1%288%29.png) | 1448x1086 | 19 | 10 | [比較](../assets/kill_frames/all_sources/s013/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s013/manifest.json) |
| s014 | [image-gen-1(9).png](../assets/kill_concepts/image-gen-1%289%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s014/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s014/manifest.json) |
| s015 | [image-gen-10(1).png](../assets/kill_concepts/image-gen-10%281%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s015/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s015/manifest.json) |
| s016 | [image-gen-10(2).png](../assets/kill_concepts/image-gen-10%282%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s016/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s016/manifest.json) |
| s017 | [image-gen-10(3).png](../assets/kill_concepts/image-gen-10%283%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s017/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s017/manifest.json) |
| s018 | [image-gen-10(4).png](../assets/kill_concepts/image-gen-10%284%29.png) | 1448x1086 | 15 | 2 | [比較](../assets/kill_frames/all_sources/s018/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s018/manifest.json) |
| s019 | [image-gen-10(5).png](../assets/kill_concepts/image-gen-10%285%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s019/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s019/manifest.json) |
| s020 | [image-gen-10.png](../assets/kill_concepts/image-gen-10.png) | 1448x1086 | 6 | 6 | [比較](../assets/kill_frames/all_sources/s020/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s020/manifest.json) |
| s021 | [image-gen-2(10).png](../assets/kill_concepts/image-gen-2%2810%29.png) | 1448x1086 | 15 | 6 | [比較](../assets/kill_frames/all_sources/s021/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s021/manifest.json) |
| s022 | [image-gen-2(20261013-075559).png](../assets/kill_concepts/image-gen-2%2820261013-075559%29.png) | 1448x1086 | 15 | 4 | [比較](../assets/kill_frames/all_sources/s022/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s022/manifest.json) |
| s023 | [image-gen-2(3).png](../assets/kill_concepts/image-gen-2%283%29.png) | 1448x1086 | 1 | 1 | [比較](../assets/kill_frames/all_sources/s023/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s023/manifest.json) |
| s024 | [image-gen-2(4).png](../assets/kill_concepts/image-gen-2%284%29.png) | 1448x1086 | 6 | 5 | [比較](../assets/kill_frames/all_sources/s024/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s024/manifest.json) |
| s025 | [image-gen-2(5).png](../assets/kill_concepts/image-gen-2%285%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s025/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s025/manifest.json) |
| s026 | [image-gen-2(6).png](../assets/kill_concepts/image-gen-2%286%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s026/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s026/manifest.json) |
| s027 | [image-gen-2(7).png](../assets/kill_concepts/image-gen-2%287%29.png) | 1448x1086 | 9 | 6 | [比較](../assets/kill_frames/all_sources/s027/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s027/manifest.json) |
| s028 | [image-gen-2(8).png](../assets/kill_concepts/image-gen-2%288%29.png) | 1448x1086 | 15 | 13 | [比較](../assets/kill_frames/all_sources/s028/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s028/manifest.json) |
| s029 | [image-gen-2(9).png](../assets/kill_concepts/image-gen-2%289%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s029/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s029/manifest.json) |
| s030 | [image-gen-3(10).png](../assets/kill_concepts/image-gen-3%2810%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s030/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s030/manifest.json) |
| s031 | [image-gen-3(20261013-075602).png](../assets/kill_concepts/image-gen-3%2820261013-075602%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s031/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s031/manifest.json) |
| s032 | [image-gen-3(3).png](../assets/kill_concepts/image-gen-3%283%29.png) | 1448x1086 | 1 | 1 | [比較](../assets/kill_frames/all_sources/s032/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s032/manifest.json) |
| s033 | [image-gen-3(4).png](../assets/kill_concepts/image-gen-3%284%29.png) | 1448x1086 | 6 | 2 | [比較](../assets/kill_frames/all_sources/s033/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s033/manifest.json) |
| s034 | [image-gen-3(5).png](../assets/kill_concepts/image-gen-3%285%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s034/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s034/manifest.json) |
| s035 | [image-gen-3(6).png](../assets/kill_concepts/image-gen-3%286%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s035/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s035/manifest.json) |
| s036 | [image-gen-3(7).png](../assets/kill_concepts/image-gen-3%287%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s036/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s036/manifest.json) |
| s037 | [image-gen-3(8).png](../assets/kill_concepts/image-gen-3%288%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s037/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s037/manifest.json) |
| s038 | [image-gen-3(9).png](../assets/kill_concepts/image-gen-3%289%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s038/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s038/manifest.json) |
| s039 | [image-gen-4(2).png](../assets/kill_concepts/image-gen-4%282%29.png) | 1448x1086 | 8 | 8 | [比較](../assets/kill_frames/all_sources/s039/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s039/manifest.json) |
| s040 | [image-gen-4(3).png](../assets/kill_concepts/image-gen-4%283%29.png) | 1448x1086 | 6 | 3 | [比較](../assets/kill_frames/all_sources/s040/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s040/manifest.json) |
| s041 | [image-gen-4(4).png](../assets/kill_concepts/image-gen-4%284%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s041/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s041/manifest.json) |
| s042 | [image-gen-4(5).png](../assets/kill_concepts/image-gen-4%285%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s042/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s042/manifest.json) |
| s043 | [image-gen-4(6).png](../assets/kill_concepts/image-gen-4%286%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s043/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s043/manifest.json) |
| s044 | [image-gen-4(7).png](../assets/kill_concepts/image-gen-4%287%29.png) | 1448x1086 | 15 | 8 | [比較](../assets/kill_frames/all_sources/s044/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s044/manifest.json) |
| s045 | [image-gen-4(8).png](../assets/kill_concepts/image-gen-4%288%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s045/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s045/manifest.json) |
| s046 | [image-gen-4(9).png](../assets/kill_concepts/image-gen-4%289%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s046/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s046/manifest.json) |
| s047 | [image-gen-5(2).png](../assets/kill_concepts/image-gen-5%282%29.png) | 1448x1086 | 8 | 8 | [比較](../assets/kill_frames/all_sources/s047/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s047/manifest.json) |
| s048 | [image-gen-5(3).png](../assets/kill_concepts/image-gen-5%283%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s048/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s048/manifest.json) |
| s049 | [image-gen-5(4).png](../assets/kill_concepts/image-gen-5%284%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s049/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s049/manifest.json) |
| s050 | [image-gen-5(5).png](../assets/kill_concepts/image-gen-5%285%29.png) | 1448x1086 | 15 | 7 | [比較](../assets/kill_frames/all_sources/s050/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s050/manifest.json) |
| s051 | [image-gen-5(6).png](../assets/kill_concepts/image-gen-5%286%29.png) | 1448x1086 | 24 | 24 | [比較](../assets/kill_frames/all_sources/s051/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s051/manifest.json) |
| s052 | [image-gen-5(7).png](../assets/kill_concepts/image-gen-5%287%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s052/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s052/manifest.json) |
| s053 | [image-gen-5(8).png](../assets/kill_concepts/image-gen-5%288%29.png) | 1448x1086 | 15 | 5 | [比較](../assets/kill_frames/all_sources/s053/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s053/manifest.json) |
| s054 | [image-gen-6(2).png](../assets/kill_concepts/image-gen-6%282%29.png) | 1448x1086 | 4 | 4 | [比較](../assets/kill_frames/all_sources/s054/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s054/manifest.json) |
| s055 | [image-gen-6(3).png](../assets/kill_concepts/image-gen-6%283%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s055/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s055/manifest.json) |
| s056 | [image-gen-6(4).png](../assets/kill_concepts/image-gen-6%284%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s056/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s056/manifest.json) |
| s057 | [image-gen-6(5).png](../assets/kill_concepts/image-gen-6%285%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s057/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s057/manifest.json) |
| s058 | [image-gen-6(6).png](../assets/kill_concepts/image-gen-6%286%29.png) | 1448x1086 | 15 | 4 | [比較](../assets/kill_frames/all_sources/s058/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s058/manifest.json) |
| s059 | [image-gen-6(7).png](../assets/kill_concepts/image-gen-6%287%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s059/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s059/manifest.json) |
| s060 | [image-gen-6(8).png](../assets/kill_concepts/image-gen-6%288%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s060/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s060/manifest.json) |
| s061 | [image-gen-7(1).png](../assets/kill_concepts/image-gen-7%281%29.png) | 1448x1086 | 8 | 8 | [比較](../assets/kill_frames/all_sources/s061/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s061/manifest.json) |
| s062 | [image-gen-7(2).png](../assets/kill_concepts/image-gen-7%282%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s062/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s062/manifest.json) |
| s063 | [image-gen-7(3).png](../assets/kill_concepts/image-gen-7%283%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s063/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s063/manifest.json) |
| s064 | [image-gen-7(4).png](../assets/kill_concepts/image-gen-7%284%29.png) | 1448x1086 | 15 | 8 | [比較](../assets/kill_frames/all_sources/s064/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s064/manifest.json) |
| s065 | [image-gen-7(5).png](../assets/kill_concepts/image-gen-7%285%29.png) | 1448x1086 | 21 | 15 | [比較](../assets/kill_frames/all_sources/s065/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s065/manifest.json) |
| s066 | [image-gen-7(6).png](../assets/kill_concepts/image-gen-7%286%29.png) | 1448x1086 | 15 | 10 | [比較](../assets/kill_frames/all_sources/s066/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s066/manifest.json) |
| s067 | [image-gen-7(7).png](../assets/kill_concepts/image-gen-7%287%29.png) | 1448x1086 | 15 | 8 | [比較](../assets/kill_frames/all_sources/s067/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s067/manifest.json) |
| s068 | [image-gen-8(1).png](../assets/kill_concepts/image-gen-8%281%29.png) | 1448x1086 | 7 | 7 | [比較](../assets/kill_frames/all_sources/s068/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s068/manifest.json) |
| s069 | [image-gen-8(2).png](../assets/kill_concepts/image-gen-8%282%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s069/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s069/manifest.json) |
| s070 | [image-gen-8(3).png](../assets/kill_concepts/image-gen-8%283%29.png) | 1448x1086 | 9 | 9 | [比較](../assets/kill_frames/all_sources/s070/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s070/manifest.json) |
| s071 | [image-gen-8(4).png](../assets/kill_concepts/image-gen-8%284%29.png) | 1448x1086 | 18 | 12 | [比較](../assets/kill_frames/all_sources/s071/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s071/manifest.json) |
| s072 | [image-gen-8(5).png](../assets/kill_concepts/image-gen-8%285%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s072/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s072/manifest.json) |
| s073 | [image-gen-8(6).png](../assets/kill_concepts/image-gen-8%286%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s073/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s073/manifest.json) |
| s074 | [image-gen-8(7).png](../assets/kill_concepts/image-gen-8%287%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s074/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s074/manifest.json) |
| s075 | [image-gen-9(1).png](../assets/kill_concepts/image-gen-9%281%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s075/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s075/manifest.json) |
| s076 | [image-gen-9(2).png](../assets/kill_concepts/image-gen-9%282%29.png) | 1448x1086 | 9 | 3 | [比較](../assets/kill_frames/all_sources/s076/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s076/manifest.json) |
| s077 | [image-gen-9(3).png](../assets/kill_concepts/image-gen-9%283%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s077/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s077/manifest.json) |
| s078 | [image-gen-9(4).png](../assets/kill_concepts/image-gen-9%284%29.png) | 1448x1086 | 24 | 21 | [比較](../assets/kill_frames/all_sources/s078/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s078/manifest.json) |
| s079 | [image-gen-9(5).png](../assets/kill_concepts/image-gen-9%285%29.png) | 1448x1086 | 15 | 8 | [比較](../assets/kill_frames/all_sources/s079/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s079/manifest.json) |
| s080 | [image-gen-9(6).png](../assets/kill_concepts/image-gen-9%286%29.png) | 1448x1086 | 15 | 9 | [比較](../assets/kill_frames/all_sources/s080/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s080/manifest.json) |
| s081 | [image-gen-9.png](../assets/kill_concepts/image-gen-9.png) | 1448x1086 | 7 | 7 | [比較](../assets/kill_frames/all_sources/s081/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s081/manifest.json) |
| s082 | [image.png](../assets/kill_concepts/image.png) | 1448x1086 | 15 | 0 | [比較](../assets/kill_frames/all_sources/s082/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s082/manifest.json) |
| s083 | [ゲームUIキルアイコン四案比較シート.png](../assets/kill_concepts/%E3%82%B2%E3%83%BC%E3%83%A0UI%E3%82%AD%E3%83%AB%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3%E5%9B%9B%E6%A1%88%E6%AF%94%E8%BC%83%E3%82%B7%E3%83%BC%E3%83%88.png) | 1536x1024 | 11 | 11 | [比較](../assets/kill_frames/all_sources/s083/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s083/manifest.json) |
| s084 | [リーグテーマ別装飾フレーム図鑑.png](../assets/kill_concepts/%E3%83%AA%E3%83%BC%E3%82%B0%E3%83%86%E3%83%BC%E3%83%9E%E5%88%A5%E8%A3%85%E9%A3%BE%E3%83%95%E3%83%AC%E3%83%BC%E3%83%A0%E5%9B%B3%E9%91%91.png) | 1536x1024 | 20 | 0 | [比較](../assets/kill_frames/all_sources/s084/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s084/manifest.json) |
| s085 | [リーグ風地域別対戦アイコンギャラリー.png](../assets/kill_concepts/%E3%83%AA%E3%83%BC%E3%82%B0%E9%A2%A8%E5%9C%B0%E5%9F%9F%E5%88%A5%E5%AF%BE%E6%88%A6%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3%E3%82%AE%E3%83%A3%E3%83%A9%E3%83%AA%E3%83%BC.png) | 1536x1024 | 30 | 0 | [比較](../assets/kill_frames/all_sources/s085/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s085/manifest.json) |
| s086 | [幻想と機械のキルアイコン大全.png](../assets/kill_concepts/%E5%B9%BB%E6%83%B3%E3%81%A8%E6%A9%9F%E6%A2%B0%E3%81%AE%E3%82%AD%E3%83%AB%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3%E5%A4%A7%E5%85%A8.png) | 1536x1024 | 50 | 26 | [比較](../assets/kill_frames/all_sources/s086/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s086/manifest.json) |
| s087 | [幻想ゲームUIデザイン大全 61–70.png](../assets/kill_concepts/%E5%B9%BB%E6%83%B3%E3%82%B2%E3%83%BC%E3%83%A0UI%E3%83%87%E3%82%B6%E3%82%A4%E3%83%B3%E5%A4%A7%E5%85%A8%2061%E2%80%9370.png) | 1536x1024 | 50 | 30 | [比較](../assets/kill_frames/all_sources/s087/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s087/manifest.json) |
| s088 | [幻想テーマ別キルアイコン大全.png](../assets/kill_concepts/%E5%B9%BB%E6%83%B3%E3%83%86%E3%83%BC%E3%83%9E%E5%88%A5%E3%82%AD%E3%83%AB%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3%E5%A4%A7%E5%85%A8.png) | 1536x1024 | 50 | 30 | [比較](../assets/kill_frames/all_sources/s088/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s088/manifest.json) |
| s089 | [第4弾 キルアイコン装飾テンプレート集.png](../assets/kill_concepts/%E7%AC%AC4%E5%BC%BE%20%E3%82%AD%E3%83%AB%E3%82%A2%E3%82%A4%E3%82%B3%E3%83%B3%E8%A3%85%E9%A3%BE%E3%83%86%E3%83%B3%E3%83%97%E3%83%AC%E3%83%BC%E3%83%88%E9%9B%86.png) | 1536x1024 | 10 | 10 | [比較](../assets/kill_frames/all_sources/s089/review_01.jpg) / [台帳](../assets/kill_frames/all_sources/s089/manifest.json) |

全行が処理済み。除外対象・未対応理由は89行CSV/JSONで確認できる。欠損図や品質注意の部品は正式に使用できる素材として承認していない。

## 既存31テーマの対応と品質判定

| テーマ | 実ファイル | 主図 | 同名の掲載/別案画像 | 判定 |
|---|---|---|---|---|
| 冬の祝祭 (`winter_festival`) | image.png | [s082](../assets/kill_frames/all_sources/s082/review_01.jpg) | s002, s004, s058, s082 | 数値検証合格・目視未承認 |
| PROJECT (`project`) | image-gen-1(8).png | [s013](../assets/kill_frames/all_sources/s013/review_01.jpg) | s003, s004, s013, s086 | 数値検証合格・目視未承認 / 品質注意10点 |
| スターガーディアン (`star_guardian`) | image-gen-2(8).png | [s028](../assets/kill_frames/all_sources/s028/review_01.jpg) | s003, s004, s028, s086 | 数値検証合格・目視未承認 / 品質注意13点 |
| K/DA (`kda`) | image-gen-3(8).png | [s037](../assets/kill_frames/all_sources/s037/review_01.jpg) | s003, s004, s037, s062 | 数値検証合格・目視未承認 / 品質注意9点 |
| ハートスティール (`heartsteel`) | image-gen-4(6).png | [s043](../assets/kill_frames/all_sources/s043/review_01.jpg) | s003, s004, s043, s069 | 数値検証合格・目視未承認 / 品質注意9点 |
| スピリットブロッサム (`spirit_blossom`) | image-gen-5(5).png | [s050](../assets/kill_frames/all_sources/s050/review_01.jpg) | s003, s004, s050, s055 | 数値検証合格・目視未承認 / 品質注意7点 |
| ダークスター (`dark_star`) | image-gen-6(5).png | [s057](../assets/kill_frames/all_sources/s057/review_01.jpg) | s003, s004, s057, s075 | 数値検証合格・目視未承認 / 品質注意9点 |
| ハイヌーン (`high_noon`) | image-gen-7(4).png | [s064](../assets/kill_frames/all_sources/s064/review_01.jpg) | s003, s004, s048, s064 | 数値検証合格・目視未承認 / 品質注意8点 |
| 血月 (`blood_moon`) | image-gen-8(4).png | [s071](../assets/kill_frames/all_sources/s071/review_01.jpg) | s003, s004, s071 | 数値検証合格・目視未承認 / 品質注意12点 |
| 覇王 (`warring_kingdoms`) | image-gen-9(3).png | [s077](../assets/kill_frames/all_sources/s077/review_01.jpg) | s003, s004, s077 | 数値検証合格・目視未承認 / 品質注意9点 |
| プールパーティー (`pool_party`) | image-gen-10(3).png | [s017](../assets/kill_frames/all_sources/s017/review_01.jpg) | s003, s004, s017 | 数値検証合格・目視未承認 / 品質注意9点 |
| エルダウッド (`elderwood`) | image-gen-1(10).png | [s006](../assets/kill_frames/all_sources/s006/review_01.jpg) | s001, s006, s088 | 数値検証合格・目視未承認 / 品質注意6点 |
| コズミック (`cosmic`) | image-gen-2(10).png | [s021](../assets/kill_frames/all_sources/s021/review_01.jpg) | s001, s021, s088 | 数値検証合格・目視未承認 / 品質注意6点 |
| ダークコズミック (`dark_cosmic`) | image-gen-3(10).png | [s030](../assets/kill_frames/all_sources/s030/review_01.jpg) | s001, s030, s088 | 数値検証合格・目視未承認 / 品質注意9点 |
| ドーンブリンガー (`dawnbringer`) | image-gen-4(8).png | [s045](../assets/kill_frames/all_sources/s045/review_01.jpg) | s001, s045, s088 | 数値検証合格・目視未承認 / 品質注意9点 |
| ナイトブリンガー (`nightbringer`) | image-gen-5(7).png | [s052](../assets/kill_frames/all_sources/s052/review_01.jpg) | s001, s052, s088 | 数値検証合格・目視未承認 / 品質注意9点 |
| インフェルナル (`infernal`) | image-gen-6(7).png | [s059](../assets/kill_frames/all_sources/s059/review_01.jpg) | s001, s002, s004, s059, s088, s089 | 数値検証合格・目視未承認 / 品質注意9点 |
| アーケード (`arcade`) | image-gen-7(6).png | [s066](../assets/kill_frames/all_sources/s066/review_01.jpg) | s001, s002, s004, s066, s088, s089 | 数値検証合格・目視未承認 / 品質注意10点 |
| ビウィッチング (`bewitching`) | image-gen-8(6).png | [s073](../assets/kill_frames/all_sources/s073/review_01.jpg) | s001, s073, s088 | 数値検証合格・目視未承認 / 品質注意9点 |
| 磁器 (`porcelain`) | image-gen-9(5).png | [s079](../assets/kill_frames/all_sources/s079/review_01.jpg) | s001, s079, s088 | 数値検証合格・目視未承認 / 品質注意8点 |
| PsyOps (`psyops`) | image-gen-10(4).png | [s018](../assets/kill_frames/all_sources/s018/review_01.jpg) | s001, s018, s088 | 数値検証合格・目視未承認 / 品質注意2点 |
| Steel Valkyries (`steel_valkyries`) | image-gen-1(20261013-075555).png | [s007](../assets/kill_frames/all_sources/s007/review_01.jpg) | s007, s087 | 数値検証合格・目視未承認 / 品質注意4点 |
| Broken Covenant (`broken_covenant`) | image-gen-2(20261013-075559).png | [s022](../assets/kill_frames/all_sources/s022/review_01.jpg) | s022, s087 | 数値検証合格・目視未承認 / 品質注意4点 |
| Faerie Court (`faerie_court`) | image-gen-3(20261013-075602).png | [s031](../assets/kill_frames/all_sources/s031/review_01.jpg) | s002, s004, s031, s086, s087 | 数値検証合格・目視未承認 / 品質注意9点 |
| Space Groove (`space_groove`) | image-gen-4(9).png | [s046](../assets/kill_frames/all_sources/s046/review_01.jpg) | s046, s086, s087 | 数値検証合格・目視未承認 / 品質注意9点 |
| Ocean Song (`ocean_song`) | image-gen-5(8).png | [s053](../assets/kill_frames/all_sources/s053/review_01.jpg) | s053, s086, s087 | 数値検証合格・目視未承認 / 品質注意5点 |
| Mecha Kingdoms (`mecha_kingdoms`) | image-gen-6(8).png | [s060](../assets/kill_frames/all_sources/s060/review_01.jpg) | s060, s086, s087 | 数値検証合格・目視未承認 / 品質注意9点 |
| Dragonmancer (`dragonmancer`) | image-gen-7(7).png | [s067](../assets/kill_frames/all_sources/s067/review_01.jpg) | s067, s086, s087 | 数値検証合格・目視未承認 / 品質注意8点 |
| Shan Hai Scrolls (`shan_hai_scrolls`) | image-gen-8(7).png | [s074](../assets/kill_frames/all_sources/s074/review_01.jpg) | s074, s086, s087 | 数値検証合格・目視未承認 / 品質注意9点 |
| メカ (`mecha`) | image-gen-9(6).png | [s080](../assets/kill_frames/all_sources/s080/review_01.jpg) | s080, s086, s087 | 数値検証合格・目視未承認 / 品質注意9点 |
| バトルキャスト (`battlecast`) | image-gen-10(5).png | [s019](../assets/kill_frames/all_sources/s019/review_01.jpg) | s019, s086, s087 | 数値検証合格・目視未承認 / 品質注意9点 |

台帳31件以外にも、地域案、A/B/C/D案、名称未表示、共通パレット等の追加分類IDが56件ある。これを公式のテーマ数と断定せず、[対応JSON](../assets/kill_frames/all_sources/theme_correspondence.json)と全部品CSVで実画の掲載位置を追えるようにした。

## Git保存・次の工程

12バッチをそれぞれ検証後に専用ブランチへコミット・Pushした。追加参照図と測定の仕上げも同じ専用ブランチに保存する。main・PR #29・カメラv5.10.27・素材試作ブランチを変更/マージしていない。コミット一覧は `batch_commits.json` とブランチ履歴で確認できる。

次はChatGPTとユーザーが背景別/肖像入り/縮小比較で正式な見た目を判定する。要手直しだけを分離して、承認した部品ID・許容する欠け・必要な解像度を台帳へ記録する。ChatGPTがA/B/C/D UI・視覚設計・登場FXを担当し、Codexが元画素/Windows検証と共有エンジンの接続を担当する分担を維持する。**本報告を区切りとして、正式UI・動画・FX統合を開始せず停止する。**
