# LoL AutoCine 全29画面・実装前整理

**ユーザーはまだ採用案を決めていません。全29枚・12候補ファミリーを保持しています。** このパッケージはデザイン監査と実装準備。本体コードを変更していません。

最初に [比較一覧](index.html) を開くと、29原本と寸法線の切替、各画面仕様を確認できます。SVG寸法線は原本の上に別レイヤーで置き、原本PNGを変更していません。

- [全29対象表](INVENTORY_JA.md) / [CSV対応表](SCREEN_MAP.csv)
- [画面遷移](NAVIGATION_JA.md) / [候補ルートJSON](NAVIGATION.json)
- [画面別の仕様29件](screens/L02-M.md)（各画面は対象表から）
- [色・寸法・テーマ・スクロール](COMPONENTS_AND_THEMES_JA.md) / [共通部品の内訳](COMPONENT_DECOMPOSITION_JA.md)
- [AutoCine機能対応](FUNCTION_MAP_JA.md)
- [Codex実装指示](CODEX_INSTRUCTIONS_JA.md)
- [画像／実接続の合格条件](ACCEPTANCE_JA.md) / [未実施の審査表](REVIEW_CHECKLIST.csv)
- [監査結果・不足](AUDIT_FINDINGS_JA.md)
- SCREENS_29.json（全29座標／部品／ハッシュ）、RESEARCH_MEASURED.json（新18の実測590部品）、LEGACY_RECONSTRUCTION.json（旧11の再構成）、COLOR_TOKENS.json

新18の元HTML/CSS/JSONと素材は同じブランチの `../ui_rethink_20261021/` に保存済み。旧11の原本もreferences配下へ複製し、新旧同名ファイルを分離しました。

旧原本に編集可能なソースはなく、正確なフォント値は復元不能です。旧矩形は原画を測った再構成契約であり、完全なゼロ差分を保証するものではありません。実画素と実装目標解像度を分け、誤差と未確定部分を明記しました。エンゲージの既存接続は確認できず、追加能力が必要な要件として残しています。

本資料の整備完了は、29画面のアプリ実装やLoL実接続試験の完了を意味しません。後から全件比較してユーザーが採用案を決定します。


検査補助：`tools/compare_ui.py` は原本と実装画面の寸法確認、50%オーバーレイ、絶対差分、マスク付きRGB差を出力します。実装画面の検査を自動で合格にはしません。
