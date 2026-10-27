# 候補3・特定と全機能配置 / UI実装受入準備

候補3は **比較版3 / testA / T-A-M / 旧テストA 現行整理** です。L03-N（候補2）、R-A-main（新A Studio）とは別です。

今回は新しいUI候補を増やさず、既存C3-P/C3-Sの差分と必要修正、監査70項目の全配置、初心者フロー、実装後の受入検査を整理しました。12画面原本は変更していません。正式採用はユーザーが決定します。

| 読む順 | 内容 |
|---|---|
| reports/01_IDENTITY_JA.md | PR51・HTML・原画像の一致と取り違え防止 |
| images/CANDIDATE3_C3P_C3S.png | 原本と2つの改善案を並べた比較 |
| reports/02_COMPARISON_JA.md | 維持する点、変更提案、競合する点 |
| reports/03_FUNCTION_PLACEMENT_JA.md | 70項目の主配置・簡単/詳細の導線 |
| reports/04_BEGINNER_FLOW_JA.md | リプレイ選択からMP4作成まで |
| reports/05_ACCEPTANCE_JA.md | 実装後の画像・操作検査手順 |
| reports/06_REQUIRED_REVISIONS_JA.md | 既存12枚への差分修正提案 |
| Codexへの追加依頼文.txt | コピペ用の引き継ぎ |

検査台帳は `specs/UI_ACCEPTANCE_CHECKLIST.json`。Codex実装に対する検査結果は全件NOT_RUNです。資料整合のPASS、旧PRが報告したPASS、ユーザーの好みのREVIEWを混同しません。

実行アプリ・HTML/JSデモは含めません。以前の配布停止デモは復元・再配布せず、本体・main・既存UI・正式素材・承認状態は変更していません。
