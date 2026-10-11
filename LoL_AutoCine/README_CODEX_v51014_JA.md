# v5.10.14 Codex Studio / GPU統合版

受領UIはarchive/received-ui-v51014へ保存し、GPU/UI担当ブランチを分けて統合。5作業領域・折りたたみ・図鑑・ホバー/DOF比較を追加し、画像加工はUI外ワーカーへ移動。切替演出9種類は既存OpenCLへ接続、cutは高速コピー。旧設定/手動カメラ角度の互換性を保持。

音声・録画・ミラー操作優先・TargetLock・60fps映像時刻とフレーム数・GPU失敗時の安全なフォールバックは保持。CPUゼロではなく、動画エフェクトをGPU優先とし、静止画/ミラー近似表示はCPU。NVIDIA/LoL実機は未確認です。

詳細はdocs/CODEX_INTEGRATION_v51014_JA.md、まとめテストはdocs/WINDOWS_TEST_v51014_JA.md。完全版を旧版と別フォルダへ展開しSTART_GPU.bat。mainへマージせず新ブランチのDraft PRで保存します。
