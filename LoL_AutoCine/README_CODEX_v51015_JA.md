# v5.10.15 Codex UI・スキャン・カメラ / GPU統合版

受領UIは原本ブランチに保存し、GPU/UI担当を分けて統合。スキャン操作の集約、独立5ページ、青チェック、DOF詳細、日本語素材/カラー名、実フレームの大きな比較と公式キラー画像を追加。画像照会/取得/加工は単一の最新要求ワーカーで、TkはUIスレッドだけ操作。

既存GPU Full/OpenCL・9切替演出・cut高速コピー・60fps・LoL専用音声/録画/同期・TargetLock・ミラー操作優先を保持。旧設定/素材ID/手動0°/180°を保持。RED通常/FPSだけ受領側の暫定構図を適用、Windows実映像の良否は未確認。

完全版を旧版と別フォルダへ展開しSTART_GPU.bat。詳細はdocs/CODEX_INTEGRATION_v51015_JA.md、まとめテストはdocs/WINDOWS_TEST_v51015_JA.md。mainへマージせず新ブランチのDraft PRで保存します。受領側テスト記録とCodex統合後の実行結果は区別してください。
