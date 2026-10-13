# 元画素からの3テーマ透過試作（未承認・未実装）

対象は冬の祝祭/PROJECT/エルダウッドだけ。各テーマの弱フレーム/強フレームと近接/遠隔/ハイブリッド各1種類、計15点のRGBA PNG。15点の別ファイル *.alpha.png は編集可能なアルファマスク。

元ブランチはautocine/chatgpt-killframes-abcd-theme-assets-20261013、元commit ae73309d9066f5389cb443fd999dbe10239ad524。89枚の元PNGはsource_import_manifest.jsonの全SHAと一致。元絵は変更/改名しない。Issue #45の「画像未アップロード」は古い記述であり、今回のGit実体89枚を確認した。

## 実画像の対応

|テーマ|実在する元ファイル|寸法|
|---|---|---|
|冬の祝祭|assets/kill_concepts/image.png|1448×1086|
|PROJECT|assets/kill_concepts/image-gen-1(8).png|1448×1086|
|エルダウッド|assets/kill_concepts/image-gen-1(10).png|1448×1086|

core/kill_frame_themes.pyの30件のsource_fileは実ファイル名と全件不一致。冬の祝祭はカタログに未登録。今回そのコードは変更せず、実寸crop_boxとスプライト中心をmanifest、図示をqa/*_source_regions.pngに記録した。仮のmotif_centersを実装で採用せず、将来UI側でこの採寸を参照する。素材はまだアプリで選択・表示されない。

## 処理と検証

元画素を整数座標で切り出し、RGBは一切描き直し/再生成/色補正/縮小しない。全出力RGBが元cropと完全一致することをテスト。変更はアルファだけ。局所背景平面をRGBからロバスト推定し、色差をアルファへ変換。肖像穴は実寸の円/四角マスク、不要なボード罫線は除外マスクで透明化。全パラメータとSHAはpilot_extraction_spec.jsonとmanifest.json、*.alpha.pngに保存。

16件の数値テスト成功/失敗0。RGBA、全透明/全不透明でないこと、部分透過、ソースRGB完全一致、SHA、肖像中心20×20透明、4背景比較を検証。これは視覚品質の合格ではない。元絵上の顔と装飾が重なった箇所を新たに描いて埋めない。

比較はqa/<theme>_comparison.png。列はチェック柄・黒・白・実LoLゲーム画面、行は弱/強/近接/遠隔/ハイブリッド。LoL画面はユーザーが提供したHUDなし実機フレームを、今回明示依頼された比較用に使用。ユーザー名・パス・診断原本・動画はコミットしない。表示用だけ背景をパネル寸法へ縮小、抽出PNGは元画素サイズを保持。

## 未完成の点

全15点をneeds_manual_mask/試作として扱う。再生成/描き直しで見かけ上完成にしない。

- PROJECT: 白背景で黒下地由来の暗い縁、細かな破片/背景線が残る。暗い金属と暗い背景の区別が曖昧で、機械的な色抜きだけでは満足な最終品質ではない。
- 冬の祝祭: 淡い氷の発光、元の青い下地の縁、丸枠とボード罫線が接したところを再点検する。
- エルダウッド: 葉/花/枝の細い輪郭、白い紙下地上の発光、肖像/罫線と重なった丸枠の欠けを再点検する。

単一のRGBボードに焼き込まれた発光の「元のRGBと本来のalpha」は一意に復元できない。現在はRGB不変を優先し、マット色を消すための新しい色の合成や隠れた装飾の描き足しは行っていない。比較で問題がある素材を完成扱いにせず、マスクの修正対象として残す。ユーザー確認/承認前に残りテーマへ展開しない。

## 再現

Pillow/NumPy/pytestのあるPythonで、LoL_AutoCineフォルダーから:

```text
python tools/extract_killframe_original_alpha_pilot.py
python -m pytest tests/test_killframe_original_alpha_pilot.py -q
```

スクリプトは3テーマのPNG/alpha/比較/基本manifestを再構築する。初回の元89枚の照合とカタログ監査・視覚レビュー記録はqa/verification.json、qa/catalog_source_audit.json、このREADMEで保持する。再構築によって承認状態を合格へ変更しない。

既存assets/kill_badgesの37 PNG、core/以下・legacy_app.pyなどのアプリ本体、カメラ/録画/GPU/音声、main/PR29は今回変更なし。アプリ統合やA/B/C/D登場FX/UIの実装は含めない。ZIPは素材パッケージで、古いブランチのアプリ丸ごと更新ではない。
