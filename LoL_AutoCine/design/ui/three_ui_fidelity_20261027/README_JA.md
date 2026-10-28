# 候補3忠実再現 / R1・R2の実装支援基準

今回は候補3のユーザー指定画像を基準に固定し、R1 League Director参考版・R2 Lolnam参考版も別UIとして実装できる資料を整理しました。新しいUI案・画面画像は制作せず、既存画像を参照しています。

最初に **SOURCE_OF_TRUTH_JA.md** を読んでください。LD_はR1 Track Desk、LN_はR2 Shot Canvasです。候補3はtestA/T-A-Mで、L03-N/R-A-main/C3-P/C3-Sではありません。

1. reports/01_C3_FIDELITY_JA.md：候補3と認める/認めない条件
2. reports/02_C3_MUST_KEEP_JA.md：維持必須領域、ボタン、密度
3. reports/03_R2_LOLNAM_MAP_JA.md：Lolnam参考版の画面別機能
4. reports/04_R1_LEAGUE_DIRECTOR_MAP_JA.md：League Director参考版の画面別機能
5. reports/05_UNKNOWN_FUNCTION_RESEARCH_JA.md：不明機能の調査ルール
6. reports/06_ATTACHMENT_POLICY_JA.md：既存/類似/新規機能の付随方針
7. reports/07_ACCEPTANCE_JA.md：3UIの受入検査と証拠の取り方
8. reports/08_REPORT_JA.md：完了範囲と未検証事項

各機能と画面の対応は `specs/FUNCTION_MAP_210.json`、画面単位の役割は `specs/SCREEN_FUNCTION_MAP.json`、全検査台帳は `specs/ACCEPTANCE_CHECKLIST.json`。実装版を試験した結果は全件NOT_RUNです。

現在のBAT版の劣化はユーザー報告として記録しました。今回そのBAT/EXEは起動・改変していません。候補3の画像を簡略化版へ置換する方針にはしません。本体・main・旧原本・正式素材・承認状態・Windows設定・停止デモは変更対象外です。
