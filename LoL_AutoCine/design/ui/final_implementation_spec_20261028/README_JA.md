# LoL AutoCine 一括実装用・最終統合仕様

これは実装前の研究・設計の納品です。製品完成/最終UI採用の宣言ではありません。基準PR55 bd93e2c、PR54 5feff82、完了した差分監査71df643を統合しました。

まずCODEX_FINAL_HANDOFF_JA.mdをCodexへ渡してください。指定9成果物をrootへ配置、各仕様の機械可読台帳/単位/36画面/全操作/状態/依存/テストはspecs、原画像21枚と前回資料はreferencesへ保存しました。新しいデザイン画像や実行demoは制作していません。

既存70機能+追加16能力、14曖昧点、26監査親ID、11判断事項を対応付けました。判断待ちは未採用、製品操作テストは全件NOT_RUN。P2素材523/暫定肖像651/原本制約19/実LoL・GPU・音声・DPIの未完了状態は保持しています。

参照コミット・pathはspecs/SOURCE_PROVENANCE.json、現行74ファイルのGit blob/サイズはBASELINE_SOURCE_FILES.json。既存本体/旧UI/main/Codexブランチ/正式素材は変更しません。配布停止研究demoは含みません。

## 資料一覧

- MASTER_INTEGRATION_SPEC_JA.md
- UI3_COMPLETE_SPEC_JA.md
- CAMERA_FINAL_SPEC_JA.md
- FX_COLOR_MATERIAL_FINAL_JA.md
- UNKNOWN_FUNCTION_DECISIONS_JA.md
- IMPLEMENTATION_ORDER_JA.md
- TEST_MASTER_PLAN_JA.md
- CODEX_FINAL_HANDOFF_JA.md
- FUNCTION_IMPLEMENTATION_MATRIX.json

その他：reports/03_70機能実装台帳_JA.md、reports/07_監査26件残件_JA.md、specs/TEST_CASES.json、specs/DECISION_REGISTER.json。
