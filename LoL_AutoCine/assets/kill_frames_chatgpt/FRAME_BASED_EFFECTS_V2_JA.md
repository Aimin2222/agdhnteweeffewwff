# キルフレーム画像を元にしたエフェクト v2

元のキルフレームの配色・装飾・素材感から、新しい「キル瞬間」のエフェクト画像を制作した。キルフレーム本体の制作は再開していない。既存PNGと本体コードは変更していない。

新規制作: 35 / 35種類（A/B/C/D 4案 + Dスキンテーマ31種）。各1枚のピーク用透過RGBA PNG。発光・光跡・飛散する小片を含む1枚のエフェクトで、個々の粒子を独立操作する画像パーツではない。

## ダウンロード

- [元フレーム・単体エフェクト・動きの一覧ZIP](https://github.com/Aimin2222/agdhnteweeffewwff/raw/refs/heads/chatgpt/killframes-source-numbering-20261014/LoL_AutoCine/assets/kill_frames_chatgpt/downloads/frame_effects_v2/AutoCine_%E3%82%A8%E3%83%95%E3%82%A7%E3%82%AF%E3%83%88%E4%B8%80%E8%A6%A7_v2.zip)
- [エフェクトPNGだけの画像ZIP](https://github.com/Aimin2222/agdhnteweeffewwff/raw/refs/heads/chatgpt/killframes-source-numbering-20261014/LoL_AutoCine/assets/kill_frames_chatgpt/downloads/frame_effects_v2/AutoCine_%E3%82%A8%E3%83%95%E3%82%A7%E3%82%AF%E3%83%88%E7%94%BB%E5%83%8F_v2_part01.zip)

一覧ZIPは展開後 `ここから見る.html` を開く。元フレーム、エフェクト単体、簡易的な動き、重ねた見え方を同じ画面で比較できる。プレビューは縮小画像を使う。原寸PNGは画像ZIP。

## 対応と品質

|テーマ／案|参照原本No.|素材ID|状態|
|---|---|---|---|
|PROJECT|013|D_project|外周アルファ残留・レビュー待ち|
|スターガーディアン|028|D_star_guardian|外周アルファ残留・レビュー待ち|
|スピリットブロッサム|050|D_spirit_blossom|外周アルファ残留・レビュー待ち|
|シンプル|083|A|基本透過検査通過・レビュー待ち|
|高級感|083|B|外周アルファ残留・レビュー待ち|
|シネマ|083|C|外周アルファ残留・レビュー待ち|
|スキン・地域テーマ|083|D|外周アルファ残留・レビュー待ち|
|アーケード|066|D_arcade|外周アルファ残留・レビュー待ち|
|バトルキャスト|019|D_battlecast|外周アルファ残留・レビュー待ち|
|ビウィッチング|073|D_bewitching|外周アルファ残留・レビュー待ち|
|血月|071|D_blood_moon|外周アルファ残留・レビュー待ち|
|Broken Covenant|022|D_broken_covenant|外周アルファ残留・レビュー待ち|
|コズミック|021|D_cosmic|外周アルファ残留・レビュー待ち|
|ダークコズミック|030|D_dark_cosmic|外周アルファ残留・レビュー待ち|
|ダークスター|057|D_dark_star|外周アルファ残留・レビュー待ち|
|ドーンブリンガー|045|D_dawnbringer|外周アルファ残留・レビュー待ち|
|Dragonmancer|067|D_dragonmancer|外周アルファ残留・レビュー待ち|
|エルダウッド|006|D_elderwood|外周アルファ残留・レビュー待ち|
|Faerie Court|031|D_faerie_court|外周アルファ残留・レビュー待ち|
|ハートスティール|043|D_heartsteel|外周アルファ残留・レビュー待ち|
|ハイヌーン|064|D_high_noon|外周アルファ残留・レビュー待ち|
|インフェルナル|059|D_infernal|外周アルファ残留・レビュー待ち|
|K/DA|037|D_kda|外周アルファ残留・レビュー待ち|
|メカ|080|D_mecha|外周アルファ残留・レビュー待ち|
|Mecha Kingdoms|060|D_mecha_kingdoms|外周アルファ残留・レビュー待ち|
|ナイトブリンガー|052|D_nightbringer|外周アルファ残留・レビュー待ち|
|Ocean Song|053|D_ocean_song|外周アルファ残留・レビュー待ち|
|プールパーティー|017|D_pool_party|外周アルファ残留・レビュー待ち|
|磁器|079|D_porcelain|外周アルファ残留・レビュー待ち|
|PsyOps|018|D_psyops|外周アルファ残留・レビュー待ち|
|Shan Hai Scrolls|074|D_shan_hai_scrolls|外周アルファ残留・レビュー待ち|
|Space Groove|046|D_space_groove|外周アルファ残留・レビュー待ち|
|Steel Valkyries|007|D_steel_valkyries|外周アルファ残留・レビュー待ち|
|覇王|077|D_warring_kingdoms|外周アルファ残留・レビュー待ち|
|冬の祝祭|082|D_winter_festival|外周アルファ残留・レビュー待ち|

全画像は生成元のRGBA PNGをバイト変更せず保存した。参照したキルフレームのファイルとSHA、制作プロンプト、新画像のSHA、透明画素・外周アルファの検査は `effect_assets/frame_based_review_v2/production.json` に記録。

**レビュー候補であり、最終合格・本体への組み込み完了ではない。34 点で画像外周のアルファ残留を検出している。** 顔・文字・顔枠の混入、見切れ、背景の板状残り、元フレームとの配色・装飾の対応を比較画像で確認する。極小アルファの残留も合格に読み替えない。

前回利用者が不採用としたNo.013の旧生成版は参照せず、新しい四角いPROJECTフレームを参照した。各入力フレームもレビュー候補であり、参照したことをフレームの最終承認とは扱わない。

## 保存先

[参照画像・生成プロンプト・SHAの管理表](effect_assets/frame_based_review_v2/production.json) ／ [Codex向け実装仕様書](effect_specs/frame_based_review_v2/IMPLEMENTATION_JA.md)

生成は組み込みのimagegenを使用した。35点すべてを白・黒背景の比較シートで確認し、修正前2点は履歴として保持した。HTML内スクリプト全体の構文、ZIP破損検査は通過。ブラウザ実操作と本体への実装・実LoL映像での確認は未実施。

- `effect_assets/frame_based_review_v2/<ID>/impact_rgba.png`: 新しいピーク用画像。
- `effect_assets/frame_based_review_v2/production.json`: 原本・参照フレーム・生成PNGの対応と品質。
- `effect_specs/frame_based_review_v2/<ID>.json`: 表示位置、時間、強度、弱／強の倍率、合成契約。
- `effect_specs/frame_based_review_v2/IMPLEMENTATION_JA.md`: 実装引継ぎ。
- `downloads/frame_effects_v2/`: 画像だけのZIPと一覧ZIP。

既存の311点のエフェクトレイヤーと35件のアニメーション仕様・確認用WebPは `review_v1` に保持している。今回の新画像は追加素材であり、過去のglowや断片粒子を上書きしていない。
