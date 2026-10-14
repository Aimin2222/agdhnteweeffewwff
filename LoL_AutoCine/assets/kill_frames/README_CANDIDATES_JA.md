# 3テーマの透過完成候補 — 正式承認待ち

冬の祝祭・PROJECT・エルダウッドだけを対象にした素材候補です。アプリの選択UI・動画合成・登場FXにはまだ統合していません。
元PNGは改名/再生成/描き直し/色補正せず、15点のRGBは透明部分も含め元cropと完全一致。変更はアルファだけです。

## 比較を見る

[18通りの一覧（LoL背景・肖像入り）](qa/three_theme_overview.png)

| テーマ | 15素材のうち各5点×4背景 | 試作からの前後比較 | 肖像入り・弱/強×近接/遠隔/ハイブリッド |
|---|---|---|---|
| 冬の祝祭 | [背景比較](qa/winter_festival_comparison.png) | [前後](qa/winter_festival_before_after.png) | [肖像・組合せ](qa/winter_festival_portraits.png) |
| PROJECT | [背景比較](qa/project_comparison.png) | [前後](qa/project_before_after.png) | [肖像・組合せ](qa/project_portraits.png) |
| エルダウッド | [背景比較](qa/elderwood_comparison.png) | [前後](qa/elderwood_before_after.png) | [肖像・組合せ](qa/elderwood_portraits.png) |

各列は透明状態を示すチェック柄・黒・白・LoL実ゲーム背景。素材単体は実際のRGBA PNGです。比較用背景は素材へ焼き込んでいません。
比較画像は素材を原寸で配置。肖像と表示用ゲーム背景だけをパネルへ縮小します。
肖像はPCにキャッシュされていた公式Riotチャンピオン画像のAkali（左/キラー役）×Mordekaiser（右/被害者役）。128×128、キャッシュ版記録16.20.1。
実試合のキラー/被害者の指定ではありません。中心モチーフを重ねた組合せも確認用の合成見本で、正式な描画仕様/配置/FXではありません。

## 主な変更

- 暗い背景の残りと白い紙背景の縁を、元RGBへの距離と紙色判定からアルファへ反映。
- 切り出し内のボード罫線/関係しない破片を実測した局所マスクで除外。
- 1〜2画素の孤立ノイズだけを除去。輪郭全体の一律erosion/blurは使わず、枝・葉・細い接続を保護。
- エルダウッド強の上部枝/葉を元画像拡大で再採寸。罫線除外と装飾保持を両立する局所ROIへ調整。
- PROJECT/エルダウッドの誤ったファイル対応を実ファイルへ修正し、冬の祝祭を台帳へ追加。3テーマの元寸法・各5crop・3中央座標・肖像穴を登録。
- 旧試作の15マスク/manifest/specはqa/pilot_*で保持。旧抽出コマンドで候補を上書きする操作は拒否する。

`themes/<theme>/` にframe_weak/strongとcenter_melee/ranged/hybridの5 RGBA、対応5 alphaマスク。
詳細な台帳は [source_mapping.json](source_mapping.json)、抽出設定は [candidate_extraction_spec.json](candidate_extraction_spec.json)、現行SHAは [manifest.json](manifest.json)。
元ファイルはwinter=image.png、project=image-gen-1(8).png、elderwood=image-gen-1(10).pngで、いずれも1448×1086です。

## 検証と承認の区別

[candidate_verification.json](qa/candidate_verification.json) は15点のRGB一致、マスク一致、SHA、原89枚、alpha変化量の数値記録。
116,838画素のalphaを抑制、孤立ノイズ180画素を除去、エルダウッド強277画素のalphaを復元。alpha総量は試作の67.6〜91.7%を維持。
これは画質スコアでも全画素の背景識別の正しさでもありません。visual_approval=false、全素材candidate_pending_visual_approvalです。
旧qa/verification.jsonは取り込み元試作の過去記録で、現在のテスト/承認状態ではありません。
現行catalog_source_auditは31登録のうち3解決・28未解決。残りの画像対応は推測で埋めず、素材化もしていません。

黒/白背景で残るマット色、細い発光、元絵の肖像や罫線と重なる欠けは目視の確認事項です。
単一RGBへ焼き込まれた背景と発光を完全に分離するにはRGB変更が必要な場合があります。今回はRGB不変を優先し、色を塗り替えたり隠れた絵を描き足したりしません。
薄い発光の透明度は低下しているため、消しすぎていないかも確認してください。完全フリンジ除去・全欠け復元を保証しません。

正式承認では、各テーマの弱/強、中央3種について「黒・白・ゲーム背景での縁」「肖像穴」「小サイズでの見やすさ」「消しすぎ/不要線」を比較してください。
承認前に残テーマへ展開せず、UI・実動画・GPU登場FXの統合は次工程へ残します。

## 再生成/検証

LoL_AutoCine内で、専用.venvを使います（アプリ起動不要）。

```powershell
& .\.venv\Scripts\python.exe -B tools/build_killframe_candidates.py
& .\.venv\Scripts\python.exe -B tools/verify_killframe_candidates.py
.\RUN_TESTS.bat --pytest-only --test-file tests/test_kill_frame_themes.py --test-file tests/test_killframe_original_alpha_pilot.py --test-file tests/test_killframe_candidate_quality.py
```

元画像、spec、参照マスク、参照背景と肖像画像から再現できます。builderは対象3テーマだけを処理し、元PNGや既存37素材には書き込みません。
Riotチャンピオン画像は確認用の公式ゲーム素材です。元コンセプト作者の素材と混同せず、独自に生成した肖像とは案内しません。
