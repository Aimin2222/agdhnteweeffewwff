# Codex作業指示 — キルフレーム元画像の保管と正確な透過素材化
更新日: 2026-10-13 / 現行アプリ: v5.10.26-test
**この文書はCodexに渡す作業指示書。書いただけで画像アップロードや透過が完了するわけではありません。**

## 作業ブランチ・取得先
- リポジトリ: `Aimin2222/agdhnteweeffewwff`（**public**）
- 元ブランチ: `autocine/chatgpt-killframes-abcd-theme-assets-20261013`
- 作業する際はこのブランチからCodex専用の新規ブランチを作り、Codex側で行ったバイナリPNG追加と処理コードをコミットする。
- `main` や未マージPR #29は変更・マージしない。
- 元画像格納先: `LoL_AutoCine/assets/kill_concepts/`
- 抽出PNG格納先: `LoL_AutoCine/assets/kill_frames/themes/<theme_id>/`
- QA比較画像: `LoL_AutoCine/assets/kill_frames/qa/`
- 素材台帳: `LoL_AutoCine/assets/kill_frames/manifest.json`

## 最重要: 「本当の元画像」を使う
元画像はChatGPT会話内の完成コンセプトボード。装飾を生成し直して似せてはいけない。
PNG**実ピクセル**から中央の×、飾り枠、プレート、弱/強、近接/遠隔/ハイブリッドを切り分ける。
除外するのは、サンプル人物顔、説明文章、見出し、風景などの背景。抽出不能な部品は捏造せず `needs_manual_mask` と記録すること。
元画像そのものは無改変で残し、元のSHA-256・寸法・テーマ・参照ボード内の位置をmanifestで記録する。

## 最初の3テーマと受け入れ条件
1. 冬の祝祭 (winter_festival)
2. PROJECT (project)
3. エルダウッド (elderwood)

先にこの3つで、元画像を保管→実画像の顔円盤と中央モチーフを分離→透明PNGの品質確認→比較シート生成。
**3テーマの比較画像をユーザーに提出し、承認を得るまでは残りを一括処理しない。**

## テーマ別の出力
```
LoL_AutoCine/assets/kill_concepts/<original_filename>.png
LoL_AutoCine/assets/kill_frames/themes/<theme_id>/
  frame_weak.png           # 実画像から切り出した、人物や文字なし・肖像穴は透明
  frame_strong.png         # 同上・装飾強
  center_melee.png         # 近接中央モチーフ
  center_ranged.png        # 遠隔中央モチーフ
  center_hybrid.png        # ハイブリッド中央モチーフ
  fx/                      # 登場エフェクト用に元画像から実抽出した装飾がある場合
LoL_AutoCine/assets/kill_frames/qa/<theme_id>_comparison.png
LoL_AutoCine/assets/kill_frames/manifest.json
```
同一の元絵・装飾を保存しつつ、アイコン領域はゲーム本来のキラー/ビクティムの公式アイコンを後から合成できる穴とする。
Dテーマの登場FXは「この元画像から抽出可能なパーツ」と「プログラムで動かすパラメータ」を区別して定義。
A/B/Cもここまで作成された参考画像を確認して追加。既存37種類の `assets/kill_badges/` は保持。

## 品質ゲート（必須）
- PNGが実際にRGBAであること。全ピクセルalpha=255またはalpha=0のような全不透明/全透明は失格。
- 肖像穴の中央が完全透明で、文字や元のチャンピオン顔が残らない。
- 透明のチェッカー・黒背景・白背景・任意のLoLゲーム背景の4種類の比較画像を生成。
- ライトブルームの外周や宝石・金属模様の色欠け、白/黒のフリンジを検査。
- オリジナルと抽出物が視覚的に対応し、実ピクセル由来であることをユーザーに説明。
- 個別の切り出し領域 `crop_box` と、使用したmask/調整値/手作業の要否を台帳に残す。
- 現在の `core/kill_frame_themes.py` の `motif_centers` は仮値。必ず元画像の実寸を採寸して調整。
- ソースコードにまだ組み込んでいない素材は「透過素材のみ完成」と明示する。
- 全件自動処理の前に3テーマの承認を求める。

## Codex実行順
1. 作業開始前に上記専用ブランチの HEAD と既存ファイルを確認。
2. `assets/kill_concepts/` 配下の元画像PNGを列挙。元ファイルが未配置なら**絶対に「取得済み」と言わず**ユーザーへアップロードを依頼する。
3. 元画像名と `core/kill_frame_themes.py` の `THEMES.source_file` を照合し、食い違いの一覧を報告。
4. 3テーマの元画像を人手でも画像確認し、切り出し位置・透過/セグメンテーション方法を決める。
5. できた透過PNGと4種類のQA比較シート、manifest、ツール・テストを**Codexの専用ブランチ**へ保存・コミット。
6. GitHub上のファイルURLと検証結果を提示し、ユーザー承認を待つ。
7. 承認後は残りの実在するコンセプトボードを対象に繰り返す。チャット内の過去画像すべてが自動転送済みとは仮定しない。
8. 必要ならChatGPTと相談して UI/UX・D専用登場FX の独立差分を統合。録画、音声、NVENC、カメラには手を加えない。

## 役割
ChatGPT: A/B/C/Dの見た目、キルフレーム選択UI、スキンテーマ別登場FXのデザイン・仕様/独立実装。
Codex: 今回の**実画像の透過・品質試験・GitへのPNG保存**、共有エンジンへの安全な最終統合。

## 誤認防止
この文書がGitHubへ保存されていても、画像実体のアップロード済み・透過実行済み・CI成功を意味しない。証拠は Gitのバイナリファイル名とそのSHA-256、比較PNG、manifest、テストログで示すこと。
