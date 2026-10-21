# LoL AutoCine — UI/UX全面再調査・新6案
制作日：2026-10-21。過去の9案とは別の比較用デザイン。AutoCine本体を変更していない。

**推奨：E Flowを初回入口、A Studioを詳細編集にする構成。** 初心者は準備後の自動作成へ進み、必要な時に同じ編集状態のままStudioへ移る。

## 開く順序
1. [比較一覧](index.html)：6案、上位2案のライト／ダーク、追加設定画面、1366版を比較。
2. [比較・推奨順位](COMPARISON_AND_RECOMMENDATION_JA.md)：8観点の設計評価と長所・短所。
3. [調査報告](RESEARCH_JA.md)：10アプリの公式UI・手順、テーマ、参考にする点。
4. [現行UI分析](CURRENT_UI_ANALYSIS_JA.md)：最新UI比較ブランチ、過去2報告との照合。
5. [実装ガイド](IMPLEMENTATION_GUIDE_JA.md)、[機能対応表](FEATURE_MAP_JA.md)、[テーマ仕様](THEME_SPEC_JA.md)。

## 画像一覧
- 1920×1080のメイン6枚：A Studio、B Creator、C Director、D Highlights、E Flow、F Killbeat。
- 同じ配置のダーク2枚：A_main_dark、E_main_dark。
- 上位2案の追加4枚：A_camera、A_frames、E_studio、E_frames。
- 1366×768の縮小対応6枚：各案の*_main_1366x768.png。全体画像を縮小したものではなく再配置した出力。
- 主要UI部品16枚：components/に8部品×ライト／ダーク。

合計：画面画像18枚＋UI部品16枚。画面は正確に1920×1080または1366×768。UIを数値指定のHTML/CSSから出力している。過去の生成画像の原寸サイズとは異なる。

## 再現・検査データ
- ui.css / ui.jsと各HTML：寸法と色を再現する閲覧用の設計データ。本体のコードではなく、LoL接続・録画は行わない。
- LAYOUT_CONTRACT.json：配置、共通寸法、スクロール、最小映像面の条件。
- RENDERED_LAYOUT.json：18画面の主パネル境界・寸法の実測。
- ELEMENT_METRICS.json：主要ボタン、カード、入力等の位置・サイズ・文字・色。
- COLOR_TOKENS.json / CONTRAST_AUDIT.csv：両テーマの指定色と60組の計算。
- LAYOUT_QA.json / CONTRAST_QA.json / PREVIEW_THEME_PIXEL_QA.json：配置・配色・状態・映像の確認結果。
- SOURCE_PROVENANCE.json：参照したAutoCineのコミットと素材の元のハッシュ。
- PREVIEW_GENERATION_PROMPT.txt：組み込み画像生成への指示。生成は映像配置例1枚のみ。UIはHTML/CSSから出力。

## 境界
公式資料と画面を調べた設計レビューであり、他社10アプリを実機で同一課題テストしたものではない。利用者の疲労軽減、操作時間、誤操作率を測定した評価ではない。

HTMLでのテーマ切替・入力保持・再配置は確認したが、WindowsネイティブDPI、実LoL、WGC、カメラ、GPU、録画、音声、書き出しは今回検証していない。採用後にCodexが実装・実機検証するための資料。

枠・FXはカタログ原本の参照コピー。既存37バッジ、89原本、652候補、エフェクトの原本・品質台帳を変更していない。枠の合格をFXへ継承しない。新しい配置、テーマ保存、Flowの仕事場分離、Killbeatの3段階はUI設計提案。

## 保存
UI専用ブランチ：work/ui-ux-research-20261021
保存フォルダ：LoL_AutoCine/design/ui/ui_rethink_20261021/
GITHUB_RECEIPT.jsonにコミットと読み戻し結果を別添する。ZIPは画像・仕様・閲覧用UIの一式で、保存後の確認記録は別添。

