# LoL AutoCine キルフレーム・元画像置き場

> 状態: **画像PNG本体のアップロードは未完了**（2026-10-13）。このREADMEの存在は画像が置かれた証拠ではありません。

## 目的
このChatGPTで既に作成した「1テーマ＝1枚」のコンセプトボードPNGを**画素そのまま**保存し、Codexがそこから透過素材を切り出す。画像を見て似た模様を描き直すことはしない。

## 入力（元画像・変更禁止）
- フォルダー: `LoL_AutoCine/assets/kill_concepts/`
- 配置: 例 `エルダウッド_キルアイコンデザイン案.png`、`冬の祝祭_*.png`、`PROJECT_*.png`
- `core/kill_frame_themes.py` の `THEMES[*].source_file` と実際のファイル名が一致するよう対応表を作る。
- 元画像の名前が違う場合は、元名とSHA-256を記録し、元画像自体を上書きしない。
- このフォルダーには**オリジナルの画像だけ**を保存。透過作業・改変画像を混在させない。

## 出力（Codexが作る）
- `LoL_AutoCine/assets/kill_frames/themes/<theme_id>/frame_weak.png`
- `LoL_AutoCine/assets/kill_frames/themes/<theme_id>/frame_strong.png`
- `LoL_AutoCine/assets/kill_frames/themes/<theme_id>/center_melee.png`
- `LoL_AutoCine/assets/kill_frames/themes/<theme_id>/center_ranged.png`
- `LoL_AutoCine/assets/kill_frames/themes/<theme_id>/center_hybrid.png`
- `LoL_AutoCine/assets/kill_frames/themes/<theme_id>/fx/`（エフェクト素材が必要な場合）
- `LoL_AutoCine/assets/kill_frames/qa/`（黒・白・透明チェッカー・ゲーム画面での比較）
- `LoL_AutoCine/assets/kill_frames/manifest.json`（元画像のファイル名とSHA-256、各派生素材のパスと品質結果）

## 絶対ルール
1. 元画像は加工前のままGitで追跡する。デザインの「再生成」は禁止。
2. 肖像イラスト・文字・背景を出力素材に含めない。後からゲームの実チャンピオン肖像をはめ込む穴は透明。
3. 発光・髪の毛状の細線・模様を維持。境界は黒縁・白縁が残らないようにQAする。
4. まず冬の祝祭・PROJECT・エルダウッドの3種類を試作し、ユーザー承認を得てから全テーマ展開。
5. 既存 `assets/kill_badges/` の37種類は上書きしない。
6. 公開リポジトリなので、ユーザーの診断ZIP・私的スクリーンショット・ゲームアカウント情報を追加しない。

作業の詳細: `LoL_AutoCine/docs/CODEX_KILLFRAME_ORIGINAL_ALPHA_PIPELINE_20261013_JA.md`
