# 正しい候補3の特定

正解は **候補3 → testA → T-A-M → 旧テストA 現行整理**。比較版の開始ルートは `/candidates/testA/T-A-M` です。「案3」という文字列だけで選択しないでください。

| 証拠 | 確認結果 |
|---|---|
| PR #51番号表 | 候補3=testA/T-A-M、候補2=legacy03/L03-N |
| comparison_labels.py | CANDIDATE_ORDERの3番目が(testA,T-A-M) |
| PR51 HTML | bodyのdata-screen=T-A-M、data-plan=testA |
| HTMLの領域順 | prepare → preview-panel → scene-list。下部timeline/materials/camera-detail/target-side/camera-numeric |
| 元画像 | A_main.png、1672×941、SHA256 `b05abe6a04732069729abd58fc4e7aca3b09c19e8d2703c5d9af3e5a5ed01a13` |
| C3改善資料 | C3-P/C3-Sとも旧テストAを参照。原画と同一画面・同一寸法ではない追加提案 |

PR51固定参照コミット：`ee700835efe25c1aa65670d73e57f1fd9373bac2`。原画像のGit blob `3a68a05c72f9f9c3c4f63e032cb6b227697938a0` は同コミットのツリー記録と一致しました。番号表・HTML・CSSの固定出典は `evidence/IDENTITY.json` へ記録しています。

注意：PR51のT-A-M.htmlは、画像から再構成した比較版のHTMLです。オリジナルのベクター/編集データが復元された証拠ではありません。原画の見た目の基準はPNG、既存比較版の実装構造の基準はHTML/CSSと分けます。HTMLはテキストとして調査しただけで実行・再配布していません。

## 実装取り違えを止める条件

実装ビルドの開発用情報にcandidateNumber=3、family=testA、sourceScreenId=T-A-M、referenceSha256を記録してください。C3-P/C3-Sの派生ビューは別IDを付け、T-A-M原本の判定を置き換えません。L03-N/R-A-mainを読み込んだら画像比較の前にFAILとします。

原本の基本構造は左準備・対象、中央ミラー、右スキャン・検出一覧、下部の簡単/詳細タブ＋タイムライン＋カメラ/素材です。R1の左シーン/右インスペクタへ丸ごと置換しないでください。

出典：[PR51番号表](https://github.com/Aimin2222/agdhnteweeffewwff/blob/ee700835efe25c1aa65670d73e57f1fd9373bac2/LoL_AutoCine/qa/ui7_20261026/NUMBERING_JA.md)、[ラベル対応](https://github.com/Aimin2222/agdhnteweeffewwff/blob/ee700835efe25c1aa65670d73e57f1fd9373bac2/LoL_AutoCine/ui/comparison_labels.py)、[元HTML](https://github.com/Aimin2222/agdhnteweeffewwff/blob/ee700835efe25c1aa65670d73e57f1fd9373bac2/LoL_AutoCine/design/ui/ui29_legacy/T-A-M.html)、[原画像](https://github.com/Aimin2222/agdhnteweeffewwff/blob/ee700835efe25c1aa65670d73e57f1fd9373bac2/LoL_AutoCine/design/ui/implementation_audit_29_20261021/references/legacy_test/A_main.png)。
