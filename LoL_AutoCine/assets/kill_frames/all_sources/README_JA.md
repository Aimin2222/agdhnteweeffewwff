# 全89元画像の透過素材候補

このフォルダーはオフラインの素材・台帳・比較画像専用です。アプリのUI、動画合成、登場FXへの接続は行っていません。基準は `22861a90c585c8b6b91263241d7437ccf956acc2`。最終の見た目は未承認です。

## 確認する順序

1. `source_inventory.json`: 全89枚の元ファイル名、SHA-256、寸法、テーマ、各部品のピクセル座標、肖像穴、除外領域、未対応理由。
2. `theme_correspondence.json`: 既存31テーマの旧台帳名と実ファイル名、および一覧・別案の対応。台帳の旧名を元PNGへ適用せず、対応表だけで解決。
3. `s001`〜`s089` の `source_regions.jpg`: 水色の切り出し範囲と赤色の肖像穴。画像を見て台帳と対応させるための図。
4. 各フォルダーの `review_*.jpg`: **全部品**のチェック柄・黒・白・LoL背景・Akali×Mordekaiserのデモ・幅160px以下の縮小比較。説明文字は素材の外側。
5. `combinations_*.jpg`: その画像に明示された全フレーム×全ロールモチーフの組合せ。弱/強・近接/遠隔/ハイブリッドの別案も対象。役割のない部品には架空の役割を付けない。
6. `manifest.json`: PNG/独立アルファマスクのSHA-256、数値検証、品質課題、比較画像一覧。

## 素材の扱い

- PNGのRGBは**元画像の同座標の切り出しと全画素一致**。透明画素のRGBも保持する。サイズ変更は比較用の表示だけ。
- `*.alpha.png` は独立したLモードのアルファ。肖像穴の内側はゼロ。元PNG89枚、既存37素材、既存3テーマ15素材と15マスクは読み取り専用。
- 元画像にない部品・色を生成しない。復元、描き足し、RGBのデフリンジ/アンマットはしない。
- 画像に装飾の弱/強やロール指定がなければ `unspecified`。説明用アニメーションの途中状態・拡大図・背景人物・操作UIは部品に混ぜず、対象外理由を記録。
- 一覧画像の小型図、文字が重なった図、原本から欠けた図は承認対象から切り分けて品質課題を記載。数値検証合格は、目視合格ではない。
- AkaliとMordekaiserは既存の公式キャッシュを使った配置例。実試合のキラー/被害者を意味しない。
- LoL背景は既存のQA参照画像。動画・音声は出力しない。比較画像の文字は、将来の動画に焼き込む素材ではない。

## 再現・検証（Windows）

リポジトリ直下で実行:

```powershell
LoL_AutoCine\.venv\Scripts\python.exe LoL_AutoCine/tools/build_all_killframe_candidates.py --batch 1
LoL_AutoCine\.venv\Scripts\python.exe LoL_AutoCine/tools/build_all_killframe_candidates.py --batch 1 --verify-only
$env:AUTOCINE_KILLFRAME_BATCH = '1'
Set-Location LoL_AutoCine
.venv\Scripts\python.exe -m pytest -q tests/test_all_killframe_candidates.py
```

バッチは1〜12、最大8元画像、デコードは1元画像ずつ。途中のバッチ検査後は環境変数を解除すると全89枚が必須になる。全件アプリ回帰は、LoLのゲーム/リプレイを終了して既存 `tools/run_local_tests.py` を使う。

平坦化済みの元絵では、黒/白/カラー背景と発光が混ざったRGB、肖像で隠れた装飾、元から欠損した輪郭はアルファだけでは復元できない。要手直しを承認済みや完全な素材と誤認しないこと。
